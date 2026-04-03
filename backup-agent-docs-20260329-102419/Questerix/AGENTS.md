# Agent Rules & Conventions

> These rules apply to **all AI coding agents** working on Questerix, in any IDE.
> **Governance Model (2-file SSoT)**:
>
> - `AGENTS.md` (this file) — **Universal**: applies to all agents
> - `GEMINI.md` (user memory) — **Antigravity-specific**: execution permissions

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
