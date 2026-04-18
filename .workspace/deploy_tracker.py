#!/usr/bin/env python3
"""Deploy tracker — records deployment lifecycle to state.db.

Usage:
  python3 deploy_tracker.py init <slug> [--plan <plan-slug>] [--target <env>]
  python3 deploy_tracker.py phase <slug> <pre|deploy|post|done|failed|rolled_back> <running|passed|failed|skipped>
  python3 deploy_tracker.py set <slug> <field> <value>
  python3 deploy_tracker.py log <slug> <pre|deploy|post> <output-text>
  python3 deploy_tracker.py finish <slug> <done|failed|rolled_back>
  python3 deploy_tracker.py status <slug>
  python3 deploy_tracker.py list [--limit N]
  python3 deploy_tracker.py latest [<slug>]
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

DB = Path(__file__).parent / "state.db"

ALLOWED_PHASES = {"pre", "deploy", "post", "done", "failed", "rolled_back"}
ALLOWED_STATUS = {"pending", "running", "passed", "failed", "skipped"}
SETTABLE = {"version", "git_sha", "artifact", "target", "plan_slug", "error"}


def conn():
    return sqlite3.connect(DB)


def init(slug, plan_slug=None, target=None):
    with conn() as c:
        cur = c.execute(
            "INSERT INTO deployments (slug, plan_slug, phase, status, target) VALUES (?, ?, 'pre', 'pending', ?)",
            (slug, plan_slug, target),
        )
        return cur.lastrowid


def _latest_id(c, slug):
    row = c.execute(
        "SELECT id FROM deployments WHERE slug=? ORDER BY id DESC LIMIT 1", (slug,)
    ).fetchone()
    if not row:
        raise SystemExit(f"no deployment found for slug={slug}")
    return row[0]


def phase(slug, ph, status):
    if ph not in ALLOWED_PHASES:
        raise SystemExit(f"bad phase: {ph}")
    if status not in ALLOWED_STATUS:
        raise SystemExit(f"bad status: {status}")
    with conn() as c:
        did = _latest_id(c, slug)
        c.execute(
            "UPDATE deployments SET phase=?, status=? WHERE id=?", (ph, status, did)
        )


def set_field(slug, field, value):
    if field not in SETTABLE:
        raise SystemExit(f"field not settable: {field}")
    with conn() as c:
        did = _latest_id(c, slug)
        c.execute(f"UPDATE deployments SET {field}=? WHERE id=?", (value, did))


def log(slug, ph, text):
    col = {"pre": "pre_output", "deploy": "deploy_output", "post": "post_output"}.get(ph)
    if not col:
        raise SystemExit(f"bad phase for log: {ph}")
    with conn() as c:
        did = _latest_id(c, slug)
        existing = c.execute(f"SELECT {col} FROM deployments WHERE id=?", (did,)).fetchone()[0]
        combined = (existing or "") + ("\n" if existing else "") + text
        c.execute(f"UPDATE deployments SET {col}=? WHERE id=?", (combined, did))


def finish(slug, outcome):
    if outcome not in {"done", "failed", "rolled_back"}:
        raise SystemExit(f"bad outcome: {outcome}")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with conn() as c:
        did = _latest_id(c, slug)
        c.execute(
            "UPDATE deployments SET phase=?, finished_at=? WHERE id=?", (outcome, now, did)
        )


def status(slug):
    with conn() as c:
        row = c.execute(
            """SELECT id, slug, plan_slug, phase, status, target, version, git_sha,
                      artifact, started_at, finished_at, error
               FROM deployments WHERE slug=? ORDER BY id DESC LIMIT 1""",
            (slug,),
        ).fetchone()
        if not row:
            print(f"no deployment for {slug}")
            return
        keys = ["id", "slug", "plan_slug", "phase", "status", "target", "version",
                "git_sha", "artifact", "started_at", "finished_at", "error"]
        print(json.dumps(dict(zip(keys, row)), indent=2, default=str))


def list_deploys(limit=10):
    with conn() as c:
        rows = c.execute(
            """SELECT id, slug, phase, status, target, version, started_at, finished_at
               FROM deployments ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    for r in rows:
        print(f"#{r[0]:>4}  {r[1]:<24} phase={r[2]:<12} status={r[3]:<8} "
              f"target={r[4] or '-':<10} v={r[5] or '-'}  started={r[6]}")


def latest(slug=None):
    with conn() as c:
        if slug:
            row = c.execute(
                "SELECT phase, status FROM deployments WHERE slug=? ORDER BY id DESC LIMIT 1",
                (slug,),
            ).fetchone()
        else:
            row = c.execute(
                "SELECT slug, phase, status FROM deployments ORDER BY id DESC LIMIT 1"
            ).fetchone()
    if not row:
        print("none")
        return
    print(" ".join(str(x) for x in row))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "init":
        slug = args[0]
        plan_slug = None
        target = None
        i = 1
        while i < len(args):
            if args[i] == "--plan":
                plan_slug = args[i + 1]; i += 2
            elif args[i] == "--target":
                target = args[i + 1]; i += 2
            else:
                i += 1
        did = init(slug, plan_slug, target)
        print(f"deployment #{did} initialized: slug={slug} target={target or '-'}")
    elif cmd == "phase":
        phase(args[0], args[1], args[2])
    elif cmd == "set":
        set_field(args[0], args[1], args[2])
    elif cmd == "log":
        log(args[0], args[1], args[2])
    elif cmd == "finish":
        finish(args[0], args[1])
    elif cmd == "status":
        status(args[0])
    elif cmd == "list":
        limit = 10
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        list_deploys(limit)
    elif cmd == "latest":
        latest(args[0] if args else None)
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
