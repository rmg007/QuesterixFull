#!/usr/bin/env python3
"""
Phase 4.2 — Link Rules to Code Evidence
Auto-populate rule_evidence table by semantic search against the vector store.

Usage:
    python3 .workspace/link_rules_to_evidence.py
    python3 .workspace/link_rules_to_evidence.py --limit 50
    python3 .workspace/link_rules_to_evidence.py --dry-run
    python3 .workspace/link_rules_to_evidence.py --min-confidence 0.7
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

STATE_DB = _HERE / "state.db"
VECTOR_DB = _HERE / "state_vectors.db"

HIGH_CONFIDENCE_THRESHOLD = 0.8
MIN_CONFIDENCE_DEFAULT = 0.0


def get_chunk_id_for_result(vec_conn: sqlite3.Connection, file_path: str, start_line: int, end_line: int) -> int | None:
    """Look up the chunk id in state_vectors.db by file/line coordinates."""
    row = vec_conn.execute(
        "SELECT id FROM chunks WHERE file_path=? AND start_line=? AND end_line=?",
        (file_path, start_line, end_line),
    ).fetchone()
    return row[0] if row else None


def link_rules_to_evidence(
    limit: int = 50,
    dry_run: bool = False,
    top_k: int = 3,
    min_confidence: float = MIN_CONFIDENCE_DEFAULT,
) -> dict:
    """
    For each confirmed rule, perform a semantic search and populate rule_evidence.

    Returns a summary dict with counts.
    """
    from search import VectorSearch

    state_conn = sqlite3.connect(str(STATE_DB))
    state_conn.row_factory = sqlite3.Row
    vec_conn = sqlite3.connect(str(VECTOR_DB))

    try:
        searcher = VectorSearch(db_path=VECTOR_DB)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        state_conn.close()
        vec_conn.close()
        sys.exit(1)

    rules = state_conn.execute(
        "SELECT id, text, status FROM rules WHERE status='confirmed' ORDER BY id LIMIT ?",
        (limit,),
    ).fetchall()

    if not rules:
        print("[INFO] No confirmed rules found — nothing to link.")
        state_conn.close()
        vec_conn.close()
        return {"rules_processed": 0, "rules_linked": 0, "evidence_rows": 0}

    rules_linked = 0
    evidence_rows = 0

    for rule in rules:
        rule_id = rule["id"]
        rule_text = rule["text"]

        results = searcher.search(rule_text, top_k=top_k, min_similarity=min_confidence)

        chunk_ids = []
        best_result = None
        best_confidence = 0.0

        for res in results:
            cid = get_chunk_id_for_result(
                vec_conn, res["file_path"], res["start_line"], res["end_line"]
            )
            if cid is None:
                continue
            sim = res["similarity"]
            chunk_ids.append(cid)
            if sim > best_confidence:
                best_confidence = sim
                best_result = (cid, sim, res["file_path"])

        if not chunk_ids:
            print(f"  Rule #{rule_id} ({rule_text[:60]!r}) -> no evidence found")
            continue

        label = "[DRY-RUN] " if dry_run else ""
        print(
            f"  {label}Rule #{rule_id} ({rule_text[:60]!r}) -> "
            f"evidence chunks {chunk_ids} "
            f"(best: chunk#{best_result[0]} sim={best_result[1]:.3f} "
            f"from {best_result[2]})"
        )

        if not dry_run:
            # Upsert rule_evidence (UNIQUE on rule_id, so replace on conflict)
            state_conn.execute(
                """INSERT INTO rule_evidence(rule_id, chunk_id, confidence)
                   VALUES (?, ?, ?)
                   ON CONFLICT(rule_id) DO UPDATE SET
                       chunk_id=excluded.chunk_id,
                       confidence=excluded.confidence,
                       added_at=datetime('now')""",
                (rule_id, best_result[0], best_result[1]),
            )

            # Update rules.evidence_chunk_ids with all top-k chunk ids
            state_conn.execute(
                "UPDATE rules SET evidence_chunk_ids=? WHERE id=?",
                (json.dumps(chunk_ids), rule_id),
            )

            evidence_rows += 1

        rules_linked += 1

    if not dry_run:
        state_conn.commit()
        print(f"\n[DONE] Linked {rules_linked}/{len(rules)} rules to evidence ({evidence_rows} evidence rows inserted/updated).")
    else:
        print(f"\n[DRY-RUN] Would link {rules_linked}/{len(rules)} rules to evidence.")

    state_conn.close()
    vec_conn.close()
    searcher.close()

    return {
        "rules_processed": len(rules),
        "rules_linked": rules_linked,
        "evidence_rows": evidence_rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Link rules to code evidence via vector search")
    parser.add_argument("--limit", type=int, default=50, help="Max rules to process (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k search results per rule (default: 3)")
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=MIN_CONFIDENCE_DEFAULT,
        help=f"Minimum similarity score to include (default: {MIN_CONFIDENCE_DEFAULT})",
    )
    args = parser.parse_args()

    summary = link_rules_to_evidence(
        limit=args.limit,
        dry_run=args.dry_run,
        top_k=args.top_k,
        min_confidence=args.min_confidence,
    )

    if args.dry_run:
        print(f"[SUMMARY] rules_processed={summary['rules_processed']} rules_would_link={summary['rules_linked']}")
    else:
        print(
            f"[SUMMARY] rules_processed={summary['rules_processed']} "
            f"rules_linked={summary['rules_linked']} "
            f"evidence_rows={summary['evidence_rows']}"
        )


if __name__ == "__main__":
    main()
