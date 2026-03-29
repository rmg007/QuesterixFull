# QuesterixFull — Monorepo

> **AI Agents:** Read `AI_WORKFLOW_SETUP.md` first. Run `supermemory_recall(query="project context")` before starting work.

This is the root workspace containing all four Questerix projects. Each project is an independent repository with its own stack, deployment, and agent rules.

---

## Projects

| Directory | Product | Stack | Deployed To |
|-----------|---------|-------|-------------|
| [`Questerix/`](Questerix/) | Admin Panel + Backend | React 18 · TypeScript · Vite · Supabase · Playwright | Cloudflare Pages + Supabase |
| [`questerix-student-app/`](questerix-student-app/) | iOS/Android Student App | Flutter · Riverpod · Drift | App Store / Google Play |
| [`questerix-help-docs/`](questerix-help-docs/) | User Help Center | VitePress · Cloudflare Pages | `help.questerix.com` |
| [`questerix-landing-pages/`](questerix-landing-pages/) | Marketing Site | React 18 · Vite · Cloudflare Pages | `questerix.com` |

---

## Quick Start

Each project has its own `QUICKSTART.md`. Start there for local dev setup.

| Project | Quick Start |
|---------|-------------|
| Admin Panel | [`Questerix/QUICKSTART.md`](Questerix/QUICKSTART.md) |
| Student App | [`questerix-student-app/QUICKSTART.md`](questerix-student-app/QUICKSTART.md) |
| Help Docs | [`questerix-help-docs/QUICKSTART.md`](questerix-help-docs/QUICKSTART.md) |
| Landing Pages | [`questerix-landing-pages/QUICKSTART.md`](questerix-landing-pages/QUICKSTART.md) |

---

## AI Agent Setup

This workspace is fully configured for AI-assisted development across **4 IDEs** (Cursor, Windsurf, Antigravity, VS Code Copilot).

| Document | Purpose |
|----------|---------|
| [`AI_WORKFLOW_SETUP.md`](AI_WORKFLOW_SETUP.md) | Complete IDE/MCP configuration guide |
| [`MCP_TOOLS_REFERENCE.md`](MCP_TOOLS_REFERENCE.md) | Structured MCP tools (80-95% token savings) |
| [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Daily cheat sheet — task tiers, constraints, file locations |

### MCP Tools (configured in all 4 IDEs)

| Tool | Purpose |
|------|---------|
| `supermemory` | Persistent cross-session memory |
| `pare-git` | Structured git output (92% smaller than raw) |
| `pare-npm` | Structured npm output (83% smaller) |
| `pare-test` | Structured test results (80% smaller) |
| `pare-typescript` | Structured TypeScript errors |

### Scoped Rules

Rules auto-load based on the file you're editing:

| Rule | Activates When Editing |
|------|------------------------|
| `.cursor/rules/react-typescript.mdc` | React/TS files in Questerix or Landing Pages |
| `.cursor/rules/flutter.mdc` | Dart files in Student App |
| `.cursor/rules/supabase.mdc` | SQL migrations and DB types |
| `.cursor/rules/playwright.mdc` | E2E test files |
| `.cursor/rules/vitepress.mdc` | Help docs markdown |

---

## Critical Constraints

These apply across all projects — violating them causes real damage:

| # | Rule | Project |
|---|------|---------|
| 1 | **Admin panel is FEATURE FROZEN** — bug fixes only | Questerix |
| 2 | **Never run full `flutter test` locally** — use targeted paths | Student App |
| 3 | **Never modify existing Drift migrations** — always add new steps | Student App |
| 4 | **Never hardcode colors** — use design tokens | All |
| 5 | **Never hit Gemini API in tests** — always mock | All |
| 6 | **Never commit secrets** — `.env`, `.mcp_config.json` are gitignored | All |
| 7 | **Never connect prod domains** without explicit instruction | Help/Landing |
| 8 | **Supabase QueryBuilder is immutable** — always reassign on `.eq()` | Questerix |
| 9 | **All new DB tables need RLS** — SELECT/INSERT/UPDATE/DELETE policies | Questerix |
| 10 | **No backend libs in docs/marketing** | Help/Landing |

---

## Project Architecture

```
QuesterixFull/
│
├── Questerix/                    # Admin Panel + Backend (feature frozen)
│   ├── admin-panel/              # React SPA
│   ├── supabase/                 # Migrations, edge functions
│   ├── questerix-cortex/         # AI planning & verification tools
│   ├── docs/                     # Architecture, learning log, time log
│   ├── AGENTS.md                 # Universal agent rules
│   └── GEMINI.md                 # Antigravity execution permissions
│
├── questerix-student-app/        # Flutter mobile app
│   ├── lib/                      # Dart source (Riverpod + Drift)
│   ├── test/                     # Unit + widget tests
│   ├── docs/                     # Architecture, learning log
│   ├── AGENTS.md
│   └── GEMINI.md
│
├── questerix-help-docs/          # VitePress help center
│   ├── admins/                   # Admin-facing guides
│   ├── teachers/                 # Teacher-facing guides
│   ├── parents/                  # Parent-facing guides
│   ├── .vitepress/               # Config and theme
│   ├── _incoming/                # Feature Snapshot drop zone
│   ├── AGENTS.md
│   └── GEMINI.md
│
├── questerix-landing-pages/      # React marketing site
│   ├── src/                      # React components
│   ├── public/                   # Static assets
│   ├── AGENTS.md
│   └── GEMINI.md
│
├── .cursor/rules/                # Glob-scoped Cursor rules (8 rules)
├── .windsurf/rules/              # Glob-scoped Windsurf rules (8 rules)
├── .cursorignore                 # Root-level Cursor index exclusions
├── .codeiumignore                # Root-level Windsurf exclusions
├── .antigravityignore            # Root-level Antigravity exclusions
│
├── AI_WORKFLOW_SETUP.md          # ← Read this first (AI agents)
├── MCP_TOOLS_REFERENCE.md        # MCP tool reference
├── QUICK_REFERENCE.md            # Daily cheat sheet
└── README.md                     # This file
```

---

## Deployment Overview

| Project | Platform | Domain | Deploy Command |
|---------|----------|--------|----------------|
| Admin Panel | Cloudflare Pages | `app.questerix.com` | `npm run deploy` in `admin-panel/` |
| Student App | App Store / Play Store | N/A | CI pipeline |
| Help Docs | Cloudflare Pages | `help.questerix.com` | `npm run deploy` in `questerix-help-docs/` |
| Landing Pages | Cloudflare Pages | `questerix.com` | `npm run deploy` in `questerix-landing-pages/` |

> **Warning:** Never connect production domains without explicit instruction.

---

## Session Workflow

### Task Tiers (add to any message)

```
// quick    → Skip all overhead (micro-tasks, quick fixes)
// full     → Full bootstrap, plan/verify, session close checklist
(default)   → Read README only, batch session close
```

### Session Close Checklist (default + full)

- [ ] Add row to `docs/TIME_LOG.md`
- [ ] Delete temp/scratch files
- [ ] Update `tasks.md` — mark done, add sub-tasks
- [ ] Append to `docs/LEARNING_LOG.md` if meaningful
