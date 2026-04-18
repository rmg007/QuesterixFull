import sqlite3
from datetime import datetime

db_path = "C:/dev/QuesterixFull/.workspace/state.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'P2',
    project TEXT DEFAULT 'shared',
    category TEXT,
    depends_on TEXT,
    hypothesis TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    closed_at TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    source TEXT,
    confidence REAL DEFAULT 0.5,
    evidence_count INTEGER DEFAULT 0,
    violation_count INTEGER DEFAULT 0,
    last_verified TEXT,
    status TEXT DEFAULT 'confirmed',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT DEFAULT (datetime('now')),
    title TEXT NOT NULL,
    context TEXT,
    options_considered TEXT,
    chosen TEXT,
    rationale TEXT
);

CREATE TABLE IF NOT EXISTS outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_sha TEXT,
    task_id INTEGER,
    hypothesis TEXT NOT NULL,
    result TEXT,
    notes TEXT,
    committed_at TEXT DEFAULT (datetime('now')),
    verified_at TEXT
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    occurrences INTEGER DEFAULT 1,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    promoted_to_rule_id INTEGER,
    status TEXT DEFAULT 'observing'
);

CREATE TABLE IF NOT EXISTS agents_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT NOT NULL,
    invoked_at TEXT DEFAULT (datetime('now')),
    task_context TEXT,
    verdict TEXT,
    correct INTEGER,
    notes TEXT
);
""")

rules = [
    ("Admin panel is FEATURE FROZEN — bug fixes only in Questerix/admin-panel/", "critical_rules.md", 1.0, 10),
    ("Never run full flutter test locally — use targeted paths only", "critical_rules.md", 1.0, 8),
    ("Never modify existing Drift migrations — always add new migration steps", "critical_rules.md", 1.0, 5),
    ("Never hardcode colors — use design tokens (Theme.of(context).colorScheme.*)", "critical_rules.md", 1.0, 6),
    ("Never hit Gemini/AI APIs in tests — always mock", "critical_rules.md", 1.0, 4),
    ("Never commit secrets — .env and .mcp_config.json are gitignored", "critical_rules.md", 1.0, 7),
    ("Never connect prod domains without explicit user instruction", "critical_rules.md", 1.0, 3),
    ("Supabase QueryBuilder is immutable — always reassign on .eq()", "critical_rules.md", 1.0, 9),
    ("All new DB tables need RLS — SELECT/INSERT/UPDATE/DELETE policies", "critical_rules.md", 1.0, 6),
    ("No backend libs in docs/marketing — help-docs and landing-pages stay lightweight", "critical_rules.md", 1.0, 3),
]
for text, source, confidence, evidence in rules:
    c.execute(
        "INSERT INTO rules (text, source, confidence, evidence_count, status, last_verified) VALUES (?,?,?,?,'confirmed', datetime('now'))",
        (text, source, confidence, evidence)
    )

tasks = [
    ("Fix 11 npm vulnerabilities in admin-panel (1 critical axios SSRF, 6 high, 4 moderate)", "open", "P0", "admin-panel", "security",
     "npm audit fix will resolve all without breaking changes"),
    ("Delete 43 stray .log/.txt files committed at admin-panel root", "open", "P0", "admin-panel", "hygiene",
     "git rm will cleanly remove all, no code affected"),
    ("Consolidate database types to packages/core — remove database.types.utf8.ts duplicate", "open", "P0", "admin-panel", "architecture",
     "Moving types and updating 12 import paths eliminates type drift risk"),
    ("Migrate Flutter build chain off discontinued packages (build_resolvers, build_runner_core)", "open", "P1", "student-app", "dependencies",
     "Migrating keeps codegen working on next Dart update"),
    ("Fix broken test coverage measurement — Cortex reporting 0% across all features", "open", "P1", "shared", "testing",
     "Reconfiguring coverage output will surface real numbers"),
    ("Resolve 169 type-safety violations (any/ts-ignore) in admin-panel", "open", "P1", "admin-panel", "quality",
     "Eliminating any types will surface latent bugs"),
    ("Retire or regenerate stale AGENT_CONTEXT.md (6 weeks old, false metrics)", "open", "P1", "shared", "docs", None),
    ("Verify Edge Function test coverage — SEC-P0-04 claimed done but unverified", "open", "P1", "admin-panel", "testing", None),
    ("Decompose question_widgets.dart — 950 lines", "open", "P2", "student-app", "godfile", None),
    ("Decompose progress_screen.dart — 772 lines", "open", "P2", "student-app", "godfile", None),
    ("Decompose UserManagementPage.tsx — 791 lines", "open", "P2", "admin-panel", "godfile", None),
    ("Decompose rich-text-editor.tsx — 701 lines", "open", "P2", "admin-panel", "godfile", None),
    ("Decompose InvitationCodesPage.tsx — 672 lines", "open", "P2", "admin-panel", "godfile", None),
    ("Decompose question-studio-page.tsx — 625 lines", "open", "P2", "admin-panel", "godfile", None),
    ("Plan and execute 19 major version upgrades (React 19, Vite 8, Tailwind 4, Zod 4, Router 7)", "open", "P2", "admin-panel", "dependencies", None),
    ("Consolidate duplicate migrations from both repos into shared/ canonical location", "open", "P2", "shared", "architecture", None),
    ("Consolidate duplicate lessons-learned folders into shared/ canonical location", "open", "P2", "shared", "architecture", None),
    ("P19-06b: Add mistake-type classification to SelfRatingDialog", "open", "P3", "student-app", "feature", None),
    ("P19-07: Widget tests for QuestionMap, PracticeBottomBar, SelfRatingDialog, HelpContentCard", "open", "P3", "student-app", "testing", None),
    ("QUAL-S06.2: Deep-link verification from push notifications", "open", "P3", "student-app", "testing", None),
]
for title, status, priority, project, category, hypothesis in tasks:
    c.execute(
        "INSERT INTO tasks (title, status, priority, project, category, hypothesis) VALUES (?,?,?,?,?,?)",
        (title, status, priority, project, category, hypothesis)
    )

patterns = [
    ("rls-column-mismatch", "SECURITY DEFINER functions silently reference wrong columns — causes total outage. Test with anon key first to isolate RLS.", 1),
    ("jwt-claims-unreliable", "JWT claim-based RLS is fragile; prefer direct DB query in helper functions. Simpler and more debuggable.", 1),
    ("supabase-order-by-explicit", "Always pass explicit ascending:true to .order() — implicit default is unreliable across versions.", 2),
    ("vi-mock-hoisting", "Variables inside vi.mock() factories must use vi.hoisted() — bare const causes ReferenceError at hoist time.", 4),
]
for name, desc, occ in patterns:
    c.execute(
        "INSERT INTO patterns (name, description, occurrences, status) VALUES (?,?,?,'promoted')",
        (name, desc, occ)
    )

c.execute("""INSERT INTO decisions (title, context, chosen, rationale)
             VALUES (
               'Adopt minimal self-growing agent system',
               'Setting up Claude Code environment for QuesterixFull monorepo',
               '3 agents + 2 skills + SQLite state + emergent growth pattern',
               'Start minimal, grow from real work friction. No upfront god-folder. Prune aggressively. Distill every session.'
             )""")

conn.commit()

c.execute("SELECT COUNT(*) FROM tasks"); print(f"Tasks inserted: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM rules"); print(f"Rules inserted: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM patterns"); print(f"Patterns inserted: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM decisions"); print(f"Decisions inserted: {c.fetchone()[0]}")
conn.close()
print("state.db ready.")
