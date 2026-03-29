# Quick Reference Card

> **Printable one-page reference for daily use**

---

## Task Tiers (Add to Any Message)

```
// quick    → Skip overhead, fast micro-task
// full     → Full bootstrap, plan/verify, close checklist
```

**Default:** TIER M (read README.md only, batch close)

---

## Session Close Checklist

Runs after every daily work period (TIER M & L):

- [ ] **TIME_LOG** — Add row to `docs/TIME_LOG.md`
- [ ] **Temp Files** — Delete scratch and `/tmp/` files
- [ ] **tasks.md** — Mark completed `[x]`, add sub-tasks
- [ ] **LEARNING_LOG** — Weekly prevention rules (if meaningful)

---

## MCP Tools (Use These, Not Raw CLI)

| Instead of... | Use This | Saves |
|---------------|----------|-------|
| `git status/log/diff` | `pare-git_status`, `pare-git_log`, `pare-git_diff` | 92% |
| `npm install` | `pare-npm_install` | 83% |
| `npm test` | `pare-test_run` | 80% |
| `tsc` | `pare-typescript_check` | Significant |
| Manual context | `supermemory_memory`, `supermemory_recall` | 100% |

---

## Scoped Rules (Auto-Load by File Type)

Rules only load when editing matching files — saves thousands of tokens:

| Rule | Applies When Editing |
|------|---------------------|
| `.cursor/rules/react-typescript.mdc` | React/TS files |
| `.cursor/rules/flutter.mdc` | Dart files |
| `.cursor/rules/supabase.mdc` | SQL migrations |
| `.cursor/rules/playwright.mdc` | E2E test files |
| `.cursor/rules/vitepress.mdc` | Help docs |

Global rules (`supermemory.mdc`, `tool-preference.mdc`) stay lean (~20 lines each).

---

## Critical Constraints (Never Violate)

| # | Constraint | Applies To |
|---|-----------|------------|
| 1 | **admin-panel: BUG FIXES ONLY** | Questerix |
| 2 | **Never run full `flutter test`** | Student App |
| 3 | **Never modify Drift migrations** | Student App |
| 4 | **Never hardcode colors** | All projects |
| 5 | **Never hit Gemini API in tests** | All projects |
| 6 | **Never commit secrets** | All projects |
| 7 | **Never connect prod domains** | Help/Landing |
| 8 | **QueryBuilder is immutable** | Supabase queries |
| 9 | **All tables need RLS** | New migrations |
| 10 | **No backend libs in docs/marketing** | Help/Landing |

---

## File Locations

| Purpose | File |
|---------|------|
| Active backlog | `tasks.md` |
| Time tracking | `docs/TIME_LOG.md` |
| Learnings | `docs/LEARNING_LOG.md` |
| Agent rules | `AGENTS.md` |
| Full setup | `AI_WORKFLOW_SETUP.md` |
| MCP tools | `MCP_TOOLS_REFERENCE.md` |
| This reference | `QUICK_REFERENCE.md` |

---

## Project Tech Stacks

| Project | Stack | Persona |
|---------|-------|---------|
| **Questerix** | React + TS + Vite + Supabase | Admin Panel Engineer |
| **Student App** | Flutter + Riverpod + Drift | Mobile Engineer |
| **Help Docs** | VitePress + Cloudflare Pages | Technical Writer |
| **Landing Pages** | React + Vite + Cloudflare Pages | Marketing/Creative |

---

## IDE Configs

All 4 IDEs have identical MCP setups:

- **Cursor:** `~/.cursor/mcp.json`
- **Windsurf:** `~/.codeium/windsurf/mcp_config.json`
- **Antigravity:** `~/.gemini/antigravity/mcp_config.json`
- **VS Code:** `~/AppData/Roaming/Code/User/mcp.json`

---

## Ignore Files (Token Savings)

Every project has:

- `.cursorignore` → Cursor AI
- `.codeiumignore` → Windsurf
- `.antigravityignore` → Antigravity
- `.vscode/settings.json` → VS Code search.exclude

Biggest exclusions: `node_modules`, `package-lock.json`, `*.g.dart`, `*.freezed.dart`

---

## Emergency Contacts

- **Can't find MCP tools?** Restart IDE
- **SuperMemory recall empty?** Wait 2-3 min for indexing
- **Forgot constraints?** Check `supermemory_recall(query="critical constraints")`
- **Need full docs?** Read `AI_WORKFLOW_SETUP.md`

---

**Version:** 2026-03-29  
**Workspace:** C:\dev\QuesterixFull
