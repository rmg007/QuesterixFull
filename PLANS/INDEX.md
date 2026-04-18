# Active Plans Index

| # | Name | Type | Status | Tokens | Created | Completed |
|---|------|------|--------|--------|---------|-----------|
| — | *No active plans* | — | — | — | — | — |

## Plan Status Key
- **ACTIVE** — In progress, can be resumed
- **COMPLETED** — Finished and executed
- **ARCHIVED** — Superseded or abandoned

## Naming Convention
Plans are numbered sequentially (001, 002, 003...). File: `PLANS/NNN-slug.md`

**Type Tags:**
- `[ARCH]` — Architecture/design decisions
- `[FEATURE]` — New feature implementation
- `[BUGFIX]` — Bug fix
- `[REFACTOR]` — Code refactoring
- `[ROUTINE]` — Reusable routine (can be called multiple times)

## How Agents Use This

1. **Before starting work:** Check this index for active plans
2. **Creating a plan:** Use `/plan <slug> <problem>` → agent writes plan, logs entry here
3. **Resuming a plan:** Open `PLANS/NNN-slug.md`, review scope, continue
4. **Completing:** Update status → COMPLETED, add date, don't delete

---

*Last updated: 2026-04-17*
