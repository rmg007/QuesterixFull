#!/usr/bin/env python3
"""
Phase 4.3 — Link Tasks to Code Files
Auto-populate task affected_files and evidence_chunk_ids columns.

Usage:
    python3 .workspace/link_tasks_to_code.py
    python3 .workspace/link_tasks_to_code.py --limit 20
    python3 .workspace/link_tasks_to_code.py --dry-run
    python3 .workspace/link_tasks_to_code.py --status open
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

STATE_DB = _HERE / "state.db"
VECTOR_DB = _HERE / "state_vectors.db"
REPO_ROOT = Path("C:/dev/QuesterixFull")

# Regex: match file references in task text (e.g. CurriculumService.ts, lib/src/foo.dart)
# tsx and yaml must come before ts/js to avoid partial matches (alternation is ordered)
FILE_PATH_RE = re.compile(r"[A-Za-z0-9_/.-]+\.(?:tsx|ts|dart|js|py|sql|yaml|json)(?!\w)")

TOP_K_DEFAULT = 3


def extract_file_paths(text: str) -> list[str]:
    """Extract file path references from free text using regex."""
    if not text:
        return []
    matches = FILE_PATH_RE.findall(text)
    # De-duplicate while preserving order
    seen: set[str] = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def get_impact_files(file_path: str) -> list[str]:
    """
    Call impact.py to get affected files for a given source file.
    Returns list of affected file paths (directly + transitively).
    """
    try:
        result = subprocess.run(
            [sys.executable, str(_HERE / "impact.py"), file_path],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(REPO_ROOT),
        )
        affected: list[str] = []
        # Parse impact.py output lines that start with label pattern [xxx]
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("[") and "]" in stripped:
                # Extract path after label: "[admin-panel] path/to/file.ts"
                parts = stripped.split("]", 1)
                if len(parts) == 2:
                    fp = parts[1].strip()
                    if fp:
                        affected.append(fp)
        return affected
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def get_chunk_ids_for_result(
    vec_conn: sqlite3.Connection, results: list[dict]
) -> list[int]:
    """Look up chunk IDs in state_vectors.db matching search results."""
    chunk_ids = []
    for res in results:
        row = vec_conn.execute(
            "SELECT id FROM chunks WHERE file_path=? AND start_line=? AND end_line=?",
            (res["file_path"], res["start_line"], res["end_line"]),
        ).fetchone()
        if row:
            chunk_ids.append(row[0])
    return chunk_ids


def link_tasks_to_code(
    limit: int = 20,
    dry_run: bool = False,
    status: str = "open",
    top_k: int = TOP_K_DEFAULT,
) -> dict:
    """
    For each task with the given status, extract file references from title/notes,
    call impact.py for affected files, and search vector store for evidence chunks.

    Returns a summary dict.
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

    tasks = state_conn.execute(
        "SELECT id, title, status, notes, hypothesis FROM tasks WHERE status=? ORDER BY id LIMIT ?",
        (status, limit),
    ).fetchall()

    if not tasks:
        print(f"[INFO] No tasks with status='{status}' found — nothing to link.")
        state_conn.close()
        vec_conn.close()
        return {"tasks_processed": 0, "tasks_with_files": 0, "tasks_with_evidence": 0}

    tasks_with_files = 0
    tasks_with_evidence = 0

    for task in tasks:
        task_id = task["id"]
        title = task["title"] or ""
        notes = task["notes"] or ""
        hypothesis = task["hypothesis"] or ""

        # Combine all text fields for extraction
        combined_text = f"{title} {notes} {hypothesis}"

        # 1. Extract file paths from task text
        raw_files = extract_file_paths(combined_text)

        # 2. Get impact analysis for each found file
        all_affected: list[str] = list(raw_files)  # start with directly mentioned files
        for fp in raw_files:
            impacted = get_impact_files(fp)
            for f in impacted:
                if f not in all_affected:
                    all_affected.append(f)

        # 3. Search vector store for task description evidence
        search_query = title[:500]  # limit query length
        results = searcher.search(search_query, top_k=top_k)
        chunk_ids = get_chunk_ids_for_result(vec_conn, results)

        label = "[DRY-RUN] " if dry_run else ""
        print(
            f"  {label}Task #{task_id} ({title[:60]!r}) -> "
            f"affects {len(all_affected)} files, "
            f"evidence in {len(chunk_ids)} chunks"
        )
        if all_affected:
            for fp in all_affected[:5]:
                print(f"    file: {fp}")
            if len(all_affected) > 5:
                print(f"    ... and {len(all_affected) - 5} more")

        if not dry_run:
            state_conn.execute(
                "UPDATE tasks SET affected_files=?, evidence_chunk_ids=? WHERE id=?",
                (
                    json.dumps(all_affected) if all_affected else None,
                    json.dumps(chunk_ids) if chunk_ids else None,
                    task_id,
                ),
            )

        if all_affected:
            tasks_with_files += 1
        if chunk_ids:
            tasks_with_evidence += 1

    if not dry_run:
        state_conn.commit()
        print(
            f"\n[DONE] Processed {len(tasks)} tasks: "
            f"{tasks_with_files} with files, {tasks_with_evidence} with evidence chunks."
        )
    else:
        print(
            f"\n[DRY-RUN] Would update {len(tasks)} tasks: "
            f"{tasks_with_files} with files, {tasks_with_evidence} with evidence chunks."
        )

    state_conn.close()
    vec_conn.close()
    searcher.close()

    return {
        "tasks_processed": len(tasks),
        "tasks_with_files": tasks_with_files,
        "tasks_with_evidence": tasks_with_evidence,
    }


def main():
    parser = argparse.ArgumentParser(description="Link tasks to code files and vector evidence")
    parser.add_argument("--limit", type=int, default=20, help="Max tasks to process (default: 20)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    parser.add_argument(
        "--status",
        default="open",
        choices=["open", "in_progress", "closed"],
        help="Task status filter (default: open)",
    )
    parser.add_argument("--top-k", type=int, default=TOP_K_DEFAULT, help="Top-k search results per task (default: 3)")
    args = parser.parse_args()

    summary = link_tasks_to_code(
        limit=args.limit,
        dry_run=args.dry_run,
        status=args.status,
        top_k=args.top_k,
    )

    print(
        f"[SUMMARY] tasks_processed={summary['tasks_processed']} "
        f"tasks_with_files={summary['tasks_with_files']} "
        f"tasks_with_evidence={summary['tasks_with_evidence']}"
    )


if __name__ == "__main__":
    main()
