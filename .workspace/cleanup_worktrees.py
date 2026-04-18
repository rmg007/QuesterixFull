#!/usr/bin/env python3
"""Worktree cleanup for /implement pipeline.

Usage:
    python3 .workspace/cleanup_worktrees.py --check      # report only
    python3 .workspace/cleanup_worktrees.py --force      # remove all phase worktrees
    python3 .workspace/cleanup_worktrees.py --phase N    # remove one phase worktree
"""
import argparse
import subprocess
import sys
from pathlib import Path

PHASE_DIR = Path(".workspace/phases")


def list_phase_worktrees() -> list[str]:
    """Return list of worktree paths under .workspace/phases/."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    paths = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree ") and ".workspace/phases/" in line:
            paths.append(line.removeprefix("worktree ").strip())
    return paths


def remove_worktree(path: str) -> bool:
    """Remove one worktree. Returns True on success."""
    result = subprocess.run(
        ["git", "worktree", "remove", "--force", path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"FAIL: {path} — {result.stderr.strip()}", file=sys.stderr)
        return False
    print(f"removed: {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="list phase worktrees, exit non-zero if any exist")
    group.add_argument("--force", action="store_true", help="remove ALL phase worktrees")
    group.add_argument("--phase", type=int, help="remove only phase-N worktree")
    args = parser.parse_args()

    worktrees = list_phase_worktrees()

    if args.check:
        if not worktrees:
            print("no phase worktrees found")
            return 0
        print(f"STALE: {len(worktrees)} phase worktree(s) still present:")
        for wt in worktrees:
            print(f"  {wt}")
        print("\nrun --force to remove, or --phase N to remove one")
        return 1

    if args.phase is not None:
        target = str(PHASE_DIR / f"phase-{args.phase}")
        matches = [wt for wt in worktrees if wt.replace("\\", "/").endswith(f"phase-{args.phase}")]
        if not matches:
            print(f"no worktree found for phase {args.phase}")
            return 1
        return 0 if all(remove_worktree(wt) for wt in matches) else 1

    if args.force:
        if not worktrees:
            print("nothing to clean")
            return 0
        ok = all(remove_worktree(wt) for wt in worktrees)
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
