#!/usr/bin/env python3
"""
Phase 4.5 — Evidence Validator
Validate that rule evidence is still valid (code hasn't drifted away from rule).

Usage:
    python3 .workspace/evidence_validator.py
    python3 .workspace/evidence_validator.py --dry-run
    python3 .workspace/evidence_validator.py --fix-stale
    python3 .workspace/evidence_validator.py --stale-threshold 0.7
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

STATE_DB = _HERE / "state.db"
VECTOR_DB = _HERE / "state_vectors.db"

STALE_THRESHOLD_DEFAULT = 0.7


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D float32 vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def load_embedding(raw) -> np.ndarray | None:
    """Deserialise a stored embedding (binary blob or JSON string)."""
    if raw is None:
        return None
    try:
        if isinstance(raw, (bytes, bytearray, memoryview)):
            return np.frombuffer(raw, dtype=np.float32)
        return np.array(json.loads(raw), dtype=np.float32)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def embed_text(text: str) -> np.ndarray:
    """
    Embed a text string using the same backend as indexer/search.
    Falls back to deterministic hash embedding if no API key.
    """
    import hashlib
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import httpx
            resp = httpx.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "content-type": "application/json",
                },
                json={"model": "voyage-3-lite", "input": text[:4096]},
                timeout=10,
            )
            if resp.status_code == 200:
                vec = resp.json()["data"][0]["embedding"]
                return np.array(vec, dtype=np.float32)
        except Exception:
            pass

    # Fallback: deterministic hash pseudo-embedding (offline/CI)
    digest = hashlib.sha256(text.encode()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vec = rng.standard_normal(1536).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


def validate_evidence(
    stale_threshold: float = STALE_THRESHOLD_DEFAULT,
    dry_run: bool = False,
    fix_stale: bool = False,
) -> dict:
    """
    Load rule_evidence pairs, re-embed current chunk content, compare to stored
    rule embedding, and flag evidence whose similarity has dropped below threshold.

    Returns a summary dict.
    """
    state_conn = sqlite3.connect(str(STATE_DB))
    state_conn.row_factory = sqlite3.Row
    vec_conn = sqlite3.connect(str(VECTOR_DB))
    vec_conn.row_factory = sqlite3.Row

    evidence_pairs = state_conn.execute(
        "SELECT re.id, re.rule_id, re.chunk_id, re.confidence, r.text AS rule_text "
        "FROM rule_evidence re JOIN rules r ON re.rule_id = r.id"
    ).fetchall()

    if not evidence_pairs:
        print("[INFO] No evidence pairs found in rule_evidence — nothing to validate.")
        state_conn.close()
        vec_conn.close()
        return {"total": 0, "valid": 0, "stale": 0, "missing": 0}

    valid_count = 0
    stale_count = 0
    missing_count = 0
    stale_ids: list[int] = []  # rule_evidence.id values that are stale

    for pair in evidence_pairs:
        ev_id = pair["id"]
        rule_id = pair["rule_id"]
        chunk_id = pair["chunk_id"]
        rule_text = pair["rule_text"]

        # Fetch current chunk from vector store
        chunk_row = vec_conn.execute(
            "SELECT content, embedding FROM chunks WHERE id=?", (chunk_id,)
        ).fetchone()

        if chunk_row is None:
            print(f"  Rule #{rule_id} chunk #{chunk_id} -> MISSING (chunk deleted)")
            missing_count += 1
            stale_ids.append(ev_id)
            continue

        # Re-embed current chunk content
        chunk_content = chunk_row["content"]
        stored_embedding = load_embedding(chunk_row["embedding"])

        # Re-embed the rule text to get fresh query vector
        rule_vec = embed_text(rule_text)

        if stored_embedding is None:
            print(f"  Rule #{rule_id} chunk #{chunk_id} -> STALE (no embedding in chunk)")
            stale_count += 1
            stale_ids.append(ev_id)
            continue

        # Compare: how similar is the current chunk to the rule?
        sim = cosine_similarity(rule_vec, stored_embedding)

        if sim < stale_threshold:
            print(
                f"  Rule #{rule_id} ({rule_text[:60]!r}) chunk #{chunk_id} "
                f"-> STALE (similarity {sim:.3f} < {stale_threshold})"
            )
            stale_count += 1
            stale_ids.append(ev_id)
        else:
            print(
                f"  Rule #{rule_id} ({rule_text[:60]!r}) chunk #{chunk_id} "
                f"-> VALID (similarity {sim:.3f})"
            )
            valid_count += 1

    total = len(evidence_pairs)
    print(f"\n[VALIDATION SUMMARY] {valid_count}/{total} valid, {stale_count} stale, {missing_count} missing")

    if fix_stale and stale_ids and not dry_run:
        print(f"\n[FIX-STALE] Re-linking {len(stale_ids)} stale evidence pairs...")
        # Import and run the linker for affected rules
        from link_rules_to_evidence import link_rules_to_evidence

        # Get stale rule_ids
        stale_rule_ids = [
            p["rule_id"]
            for p in evidence_pairs
            if p["id"] in stale_ids
        ]

        # Delete stale evidence rows so they can be re-inserted
        for ev_id in stale_ids:
            state_conn.execute("DELETE FROM rule_evidence WHERE id=?", (ev_id,))
        state_conn.commit()
        print(f"  Deleted {len(stale_ids)} stale evidence rows.")

        # Re-run linker (will re-process all confirmed rules; stale ones now have no entry)
        link_rules_to_evidence(limit=50, dry_run=False)
        print("[FIX-STALE] Re-linking complete.")
    elif dry_run and stale_ids:
        print(f"[DRY-RUN] Would re-link {len(stale_ids)} stale evidence pairs.")

    state_conn.close()
    vec_conn.close()

    return {
        "total": total,
        "valid": valid_count,
        "stale": stale_count,
        "missing": missing_count,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate rule evidence freshness")
    parser.add_argument("--dry-run", action="store_true", help="Preview without modifying DB")
    parser.add_argument("--fix-stale", action="store_true", help="Re-link stale evidence automatically")
    parser.add_argument(
        "--stale-threshold",
        type=float,
        default=STALE_THRESHOLD_DEFAULT,
        help=f"Cosine similarity below which evidence is considered stale (default: {STALE_THRESHOLD_DEFAULT})",
    )
    args = parser.parse_args()

    summary = validate_evidence(
        stale_threshold=args.stale_threshold,
        dry_run=args.dry_run,
        fix_stale=args.fix_stale,
    )

    pct_valid = (summary["valid"] / summary["total"] * 100) if summary["total"] > 0 else 0
    print(
        f"\n[RESULT] {summary['valid']}/{summary['total']} evidence pairs valid "
        f"({pct_valid:.0f}%) | {summary['stale']} stale | {summary['missing']} missing"
    )


if __name__ == "__main__":
    main()
