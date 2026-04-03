# Questerix Agent Rules - Single Source of Truth

> **This is the MASTER file for ALL AI agent rules across all 4 projects and all IDEs.**
> **All project AGENTS.md files inherit from this file.**

## 🎯 Scope

These rules apply to **all AI coding agents** working on any Questerix project:
- Questerix (Admin Panel) - React/TypeScript/Supabase
- questerix-student-app - Flutter/Dart/Drift
- questerix-help-docs - VitePress/Markdown
- questerix-landing-pages - React/Vite

**Supported IDEs**: Cursor, Windsurf, Antigravity IDE, VS Code with GitHub Copilot

---

# Universal Agent Rules & Conventions

> These rules apply to **all AI coding agents** in **any IDE**.

## 📚 Documentation (Read First)

| Document                 | Purpose                      | When to Read                  |
| ------------------------ | ---------------------------- | ----------------------------- |
| `AI_WORKFLOW_SETUP.md`   | Complete IDE/MCP setup guide | Onboarding, troubleshooting   |
| `MCP_TOOLS_REFERENCE.md` | All MCP tools with examples  | When using git/npm/test/tools |
| `QUICK_REFERENCE.md`     | One-page daily reference     | Quick lookups, print it out   |
| `../QUICK_REFERENCE.md`  | Multi-project quick ref      | Working across multiple apps  |

**All AI agents MUST read `docs/LEARNING_LOG.md` for prevention rules before making changes.**

## Task Tiers (Read First)

if message contains `// quick` or `// light`: TIER S — skip all bootstrap, Cortex, and close checklist
if message contains `// full` or `// sprint`: TIER L — full bootstrap, Cortex plan/verify, full session close
default: TIER M — read README.md only, batch session close

## Tool Selection & Token Savings (MANDATORY)

To optimize token usage and ensure structured output, all agents MUST follow these preferences:

1.  **Git Operations**: NEVER use direct shell commands like `git status`, `git log`, or `git diff`. ALWAYS use the `pare-git` MCP tools (e.g., `pare-git_status`, `pare-git_log`).
2.  **Node/npm**: NEVER use direct shell commands like `npm install` or `npm test`. ALWAYS use `pare-npm` and `pare-test` MCP tools.
3.  **TypeScript**: ALWAYS use `pare-typescript_check` instead of direct `tsc` shell commands.
4.  **Learning Log**: After fixing bugs, add prevention rules to `docs/LEARNING_LOG.md` to prevent recurrence.

These tools reduce token consumption by 80-95% compared to raw terminal output.

## 🔴 MANDATORY SESSION CLOSE CHECKLIST

> **This runs after EVERY session (daily work period), not per micro-task.**

- [ ] **1. TIME_LOG** — Add a row to `docs/TIME_LOG.md` with: date, hours, app(s), work type, description.
- [ ] **2. Temp Files** — Delete any scratch files or `/tmp/` files.
- [ ] **3. tasks.md** — Mark completed tasks `[x]`, add any new sub-tasks.
- [ ] **4. LEARNING_LOG** — Append weekly summary of prevention rules (only if meaningful).

## Core Rules

1. **No TODO/FIXME/HACK in code.** All work items go in `tasks.md`.
2. **Tasks only in `tasks.md`.** No rules, docs, or history in that file.
3. **DO NOT add any new features to `admin-panel/`.** Bug fixes only.
4. **Deployment allowlist (absolute): ONLY deploy `questerix` and `questerix-student-app`.**
5. **NEVER deploy any other app/repo/surface** (including `landing-pages` / `questerix-landing*`) from automation, scripts, or manual agent actions.
6. **If a workflow/script includes deployment for non-allowlisted apps, remove or disable that deploy path immediately.**
7. **Use Premium UI Components.** e.g., `ColumnToggle`, `BulkActionBar`.
8. **Every P0/P1 bug requires a test.** Opt-in for P2/P3.
9. **MANDATORY: Use `cortex_search`.** Use it for symbol lookup and discovery.
10. **Flag manual actions.** Explicitly highlight required user interventions.
11. **Automate over document.** Prefer CLIs and CI/CD over written guides.

## Discovery (The Faster Way)

- **Primary**: `Grep` or `SemanticSearch`
- **Codebase Orientation**: Read `README.md`

## RLS Checklist

For any migration creating a table, define SELECT/INSERT/UPDATE/DELETE policies or explicitly document omission. Run `psql $DATABASE_URL -f supabase/scripts/audit-rls.sql` after.

## Testing Standards

- **Tier 1 (E2E)**: Playwright (desktop only). Auth, CRUD, navigation.
- **Tier 2 (Visual)**: Playwright baselines.
- **Tier 3 (Unit)**: Vitest (Admin) / Deno (Edge) / Pytest (Content).
- **Conventions**: Use `TEST_USERS.SUPER_ADMIN`. Mock real APIs (never hit Gemini API in tests). Validate with Zod before RPC.

## File Placement

| What              | Where                  |
| ----------------- | ---------------------- |
| Active backlog    | `tasks.md`             |
| Developer time    | `docs/TIME_LOG.md`     |
| Session learnings | `docs/LEARNING_LOG.md` |
| Agent rules       | `AGENTS.md`            |

---

# IDE-Specific Rules

## 🔥 Antigravity IDE (GEMINI.md equivalent)

> **These rules apply ONLY when using Antigravity IDE**

### Autonomous Execution Rules

1. **Turbo Mode is ON**. All commands are pre-authorized via `// turbo-all`.
2. **Use `SafeToAutoRun: true`** for every `run_command` call.
3. If IDE gates a command, use the `ops_runner.py` workaround. Write `{ "description": "...", "command": "...", "cwd": "..." }` array to `tasks.json` in root, then run `python ops_runner.py tasks.json`.

### Watchdog Circuit Breakers

**CRITICAL**: These are hard limits to prevent infinite loops.

- **5 consecutive failures** on the same sub-task → STOP and escalate
- **3 consecutive identical errors** → You're in a loop. STOP.
- **25 total iterations** per session → Checkpoint progress and STOP
- **60 second test timeout** → Kill the test, investigate the hang
- **15 minutes with no progress** → Checkpoint and escalate

## 🐙 GitHub Copilot (VS Code)

> **These rules apply ONLY when using GitHub Copilot in VS Code**

### Core Development Principles

1. **Quality First**: Write tests for all new features and bug fixes
2. **Documentation**: Update relevant docs when making changes
3. **Consistency**: Follow existing patterns and conventions
4. **Security**: Never commit secrets or sensitive data
5. **Performance**: Consider token usage and efficiency

### File Organization

- Active tasks: `tasks.md`
- Time tracking: `docs/TIME_LOG.md`
- Prevention rules: `docs/LEARNING_LOG.md`
- Agent rules: `AGENTS.md` (this file)

## 🎯 Cursor & Windsurf

> **These IDEs use the universal rules above without additional IDE-specific requirements**

Standard behavior: Follow all universal rules, task tiers, and tool preferences listed above.

---

# Quick IDE Reference

| IDE | File to Read | Special Rules |
|-----|-------------|---------------|
| **Cursor** | This file only | Universal rules |
| **Windsurf** | This file only | Universal rules |
| **Antigravity** | This file only | + Autonomous Execution + Watchdog |
| **VS Code/Copilot** | This file only | + Development Principles |

---

> **Migration Note**: This consolidated file replaces the previous `AGENTS.md`, `GEMINI.md`, and `copilot-instructions.md` files. All IDEs now use this single source of truth.