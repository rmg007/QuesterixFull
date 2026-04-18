#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Maintenance & Cleanup
Provides full re-index, stale chunk cleanup, and embedding coverage validation.

Usage:
    python3 .workspace/maintenance.py --validate
    python3 .workspace/maintenance.py --cleanup
    python3 .workspace/maintenance.py --full-reindex
    python3 .workspace/maintenance.py --full-reindex --cleanup --validate
    python3 .workspace/maintenance.py --cleanup --dry-run
"""

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_WORKSPACE = Path(__file__).parent
_REPO_ROOT  = _WORKSPACE.parent
DB_PATH     = _WORKSPACE / "state_vectors.db"

COVERAGE_WARN_THRESHOLD = 95.0  # warn if coverage < 95%

# ---------------------------------------------------------------------------
# Import shared engine
# ---------------------------------------------------------------------------

sys.path.insert(0, str(_WORKSPACE))
from indexer import ChunkingEngine, EXTENSIONS, SKIP_DIRS, SKIP_PATTERNS  # noqa: E402
import re as _re

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found: {DB_PATH}", file=sys.stderr)
        print("        Run: python3 .workspace/init_vector_store.py", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _count_source_files() -> int:
    """Count actual source files in the repo (mirrors indexer._iter_files logic)."""
    skip_re = [_re.compile(p) for p in SKIP_PATTERNS]
    count = 0
    for dirpath_str, dirnames, filenames in os.walk(str(_REPO_ROOT)):
        dirpath = Path(dirpath_str)
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]
        for fname in filenames:
            fpath = dirpath / fname
            if fpath.suffix not in EXTENSIONS:
                continue
            if any(pat.search(fname) for pat in skip_re):
                continue
            count += 1
    return count


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def op_full_reindex(dry_run: bool = False) -> None:
    """Re-embed the entire codebase (monthly safety check)."""
    print("[maintenance] Starting full re-index...")
    start = time.time()

    if dry_run:
        print("[maintenance] DRY RUN — would call ChunkingEngine.run_indexing()")
        engine = ChunkingEngine(root=_REPO_ROOT, db_path=DB_PATH)
        files = engine._iter_files()
        engine.close()
        print(f"[maintenance] DRY RUN — would process {len(files)} files.")
        return

    engine = ChunkingEngine(root=_REPO_ROOT, db_path=DB_PATH)
    new_chunks = engine.run_indexing(dry_run=False)
    engine.close()

    elapsed = time.time() - start
    print(f"[maintenance] Full re-index complete in {elapsed:.1f}s. New chunks: {new_chunks}")


def op_cleanup(dry_run: bool = False) -> int:
    """Delete chunks for files that no longer exist in the repo."""
    print("[maintenance] Scanning for stale chunks...")
    db = _open_db()

    cur = db.execute("SELECT DISTINCT file_path FROM chunks")
    indexed_paths = [row[0] for row in cur.fetchall()]

    stale = []
    for rel in indexed_paths:
        abs_path = _REPO_ROOT / rel
        if not abs_path.exists():
            stale.append(rel)

    if not stale:
        print("[maintenance] No stale chunks found.")
        db.close()
        return 0

    total_deleted = 0
    for rel in stale:
        cur = db.execute("SELECT COUNT(*) FROM chunks WHERE file_path = ?", (rel,))
        count = cur.fetchone()[0]
        if not dry_run:
            db.execute("DELETE FROM chunks WHERE file_path = ?", (rel,))
        total_deleted += count
        tag = "[DRY]" if dry_run else "[DEL]"
        print(f"[maintenance] {tag} {rel}: {count} stale chunk(s)")

    if not dry_run:
        db.commit()
    db.close()

    action = "Would delete" if dry_run else "Deleted"
    print(f"[maintenance] {action} {total_deleted} stale chunk(s) from {len(stale)} missing file(s).")
    return total_deleted


def op_validate() -> bool:
    """Report embedding coverage and warn if below threshold."""
    print("[maintenance] Validating embedding coverage...")
    db = _open_db()

    cur = db.execute("SELECT COUNT(DISTINCT file_path) FROM chunks")
    indexed_file_count = cur.fetchone()[0]

    cur = db.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
    embedded_chunk_count = cur.fetchone()[0]

    cur = db.execute("SELECT COUNT(*) FROM chunks")
    total_chunk_count = cur.fetchone()[0]

    db.close()

    actual_file_count = _count_source_files()

    if actual_file_count == 0:
        print("[maintenance] No source files found in repo.")
        return True

    coverage_pct = (indexed_file_count / actual_file_count) * 100.0

    embed_pct = (
        (embedded_chunk_count / total_chunk_count * 100.0)
        if total_chunk_count > 0 else 0.0
    )

    print(f"[maintenance] Indexed files:    {indexed_file_count}/{actual_file_count} ({coverage_pct:.1f}%)")
    print(f"[maintenance] Total chunks:     {total_chunk_count}")
    print(f"[maintenance] Embedded chunks:  {embedded_chunk_count}/{total_chunk_count} ({embed_pct:.1f}%)")

    ok = True
    if coverage_pct < COVERAGE_WARN_THRESHOLD:
        print(
            f"[maintenance] WARNING: Coverage {coverage_pct:.1f}% is below the "
            f"{COVERAGE_WARN_THRESHOLD:.0f}% threshold. "
            f"Run: python3 .workspace/indexer.py --root {_REPO_ROOT}"
        )
        ok = False
    else:
        print(f"[maintenance] Coverage OK ({coverage_pct:.1f}% >= {COVERAGE_WARN_THRESHOLD:.0f}%)")

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Maintenance and cleanup for the QuesterixFull vector store."
    )
    parser.add_argument(
        "--full-reindex",
        action="store_true",
        help="Re-embed the entire codebase (monthly safety check).",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete chunks for files that no longer exist in the repo.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Report embedding coverage; warn if below 95%%.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making DB changes.",
    )
    args = parser.parse_args()

    if not any([args.full_reindex, args.cleanup, args.validate]):
        parser.print_help()
        sys.exit(0)

    overall_ok = True
    start = time.time()

    if args.full_reindex:
        op_full_reindex(dry_run=args.dry_run)
        print()

    if args.cleanup:
        op_cleanup(dry_run=args.dry_run)
        print()

    if args.validate:
        ok = op_validate()
        overall_ok = overall_ok and ok
        print()

    elapsed = time.time() - start
    print(f"[maintenance] All operations complete in {elapsed:.1f}s.")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
