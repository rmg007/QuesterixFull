"""
Workspace query helper — used by skills and agents to read/write state.db
Usage:
  python3 .workspace/query.py status
  python3 .workspace/query.py p0
  python3 .workspace/query.py open [project]
  python3 .workspace/query.py rules
  python3 .workspace/query.py patterns
  python3 .workspace/query.py close <task_id>
  python3 .workspace/query.py add-task <title> <priority> <project> <category>
  python3 .workspace/query.py add-outcome <task_id> <hypothesis> <result>
  python3 .workspace/query.py add-pattern <name> <description>
"""
import sqlite3
import sys
from datetime import datetime

DB = "C:/dev/QuesterixFull/.workspace/state.db"

def conn():
    return sqlite3.connect(DB)

def status():
    c = conn().cursor()
    c.execute("SELECT priority, COUNT(*) FROM tasks WHERE status='open' GROUP BY priority ORDER BY priority")
    rows = c.fetchall()
    print("=== OPEN TASKS BY PRIORITY ===")
    for p, n in rows:
        print(f"  {p}: {n} tasks")
    c.execute("SELECT COUNT(*) FROM tasks WHERE status='open'")
    print(f"  TOTAL open: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM tasks WHERE status='in_progress'")
    print(f"  In progress: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM outcomes WHERE result IS NULL")
    print(f"  Unverified outcomes: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM rules WHERE confidence < 0.7")
    print(f"  Low-confidence rules: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM patterns WHERE status='observing'")
    print(f"  Patterns under observation: {c.fetchone()[0]}")

def p0():
    c = conn().cursor()
    c.execute("SELECT id, title, project, status FROM tasks WHERE priority='P0' AND status='open'")
    rows = c.fetchall()
    print("=== P0 TASKS (OPEN) ===")
    for id, title, project, status in rows:
        print(f"  [{id}] [{project}] {title}")

def open_tasks(project=None):
    c = conn().cursor()
    if project:
        c.execute("SELECT id, priority, project, category, title FROM tasks WHERE status='open' AND project=? ORDER BY priority, id", (project,))
    else:
        c.execute("SELECT id, priority, project, category, title FROM tasks WHERE status='open' ORDER BY priority, id")
    rows = c.fetchall()
    print(f"=== OPEN TASKS{' ['+project+']' if project else ''} ===")
    for id, priority, proj, cat, title in rows:
        print(f"  [{id}] {priority} [{proj}][{cat}] {title}")

def rules():
    c = conn().cursor()
    c.execute("SELECT id, confidence, evidence_count, violation_count, text FROM rules ORDER BY confidence DESC")
    rows = c.fetchall()
    print("=== RULES ===")
    for id, conf, ev, viol, text in rows:
        flag = " ⚠️" if conf < 0.7 else ""
        print(f"  [{id}] conf={conf:.1f} ev={ev} viol={viol}{flag} | {text[:80]}")

def patterns():
    c = conn().cursor()
    c.execute("SELECT id, occurrences, status, name, description FROM patterns ORDER BY occurrences DESC")
    rows = c.fetchall()
    print("=== PATTERNS ===")
    for id, occ, status, name, desc in rows:
        flag = " → PROMOTE?" if occ >= 3 and status == 'observing' else ""
        print(f"  [{id}] x{occ} [{status}] {name}{flag}")
        print(f"       {desc[:100]}")

def close_task(task_id):
    c = conn()
    cur = c.cursor()
    cur.execute("UPDATE tasks SET status='closed', closed_at=datetime('now') WHERE id=?", (task_id,))
    c.commit()
    print(f"Task {task_id} closed.")

def add_task(title, priority, project, category):
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT INTO tasks (title, priority, project, category) VALUES (?,?,?,?)",
                (title, priority, project, category))
    c.commit()
    print(f"Task added with id={cur.lastrowid}")

def add_outcome(task_id, hypothesis, result):
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT INTO outcomes (task_id, hypothesis, result, verified_at) VALUES (?,?,?,datetime('now'))",
                (task_id, hypothesis, result))
    c.commit()
    print(f"Outcome logged for task {task_id}: {result}")

def add_pattern(name, description):
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT id, occurrences FROM patterns WHERE name=?", (name,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE patterns SET occurrences=occurrences+1, last_seen=datetime('now') WHERE id=?", (row[0],))
        print(f"Pattern '{name}' incremented to {row[1]+1} occurrences.")
        if row[1]+1 >= 3:
            print(f"  ⚠️  PROMOTE? Pattern hit 3 occurrences — consider adding as rule.")
    else:
        cur.execute("INSERT INTO patterns (name, description) VALUES (?,?)", (name, description))
        print(f"New pattern '{name}' added.")
    c.commit()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status": status()
    elif cmd == "p0": p0()
    elif cmd == "open": open_tasks(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "rules": rules()
    elif cmd == "patterns": patterns()
    elif cmd == "close": close_task(int(sys.argv[2]))
    elif cmd == "add-task": add_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "add-outcome": add_outcome(int(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif cmd == "add-pattern": add_pattern(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
