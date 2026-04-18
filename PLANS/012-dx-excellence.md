# 012 — Developer Experience Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 11
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Developer experience excellence means from clean clone to running app in ≤10 minutes, and one command for each of: lint, targeted test, build, deploy, rollback. Beyond perfection = onboarding timer <10 min measured in CI, every phase exit produces an ADR, living architecture diagrams are auto-generated, decision log is rolled up, and a new dev completes a real bug-fix PR end-to-end on day 2.

## Scope Lock (inherited from master)

- **IN:** Questerix/ (scripts/, docs/), questerix-student-app/ (scripts/, docs/), CI/CD, onboarding materials
- **OUT:** help-docs, landing-pages, admin-only DX work
- **Respects:** R1 (admin bugfix), R9 (master only)

## Phases & Workstreams

### Workstream 10.1 — make bootstrap (one-command setup)
- **Goal:** Clean clone → running app in <10 minutes.
- **Target files:** Questerix/Makefile (or orchestrator.ps1 on Windows), questerix-student-app/Makefile; .envrc.example
- **Key deliverables:**
  - `make bootstrap` installs deps (flutter pub get, npm install), generates types, seeds DB, runs app
  - Includes pre-flight checks (Dart version, Node version, Supabase CLI)
  - Clear error messages if step fails
  - Windows support via orchestrator.ps1 or bash
  - Timed in CI: must complete in ≤10 minutes on clean clone
- **Acceptance gate:** Timed onboarding ≤10 min on clean clone in CI

### Workstream 10.2 — ADRs for every major decision
- **Goal:** Decisions are recorded and accessible.
- **Target files:** Questerix/docs/adr/ (new folder), questerix-student-app/docs/adr/
- **Key deliverables:**
  - ADR template (title, context, decision, consequences, alternatives)
  - Every phase exit produces ≥1 ADR (e.g., Phase 1 → "why did we fuzz RLS?")
  - ADRs linked from code (e.g., complex function has comment linking to ADR)
  - Indexed: docs/adr/INDEX.md with links to all ADRs
- **Acceptance gate:** 10+ ADRs merged; every phase has ≥1

### Workstream 10.3 — Living architecture diagram
- **Goal:** Architecture diagram auto-generated from code; always up-to-date.
- **Target files:** Questerix/docs/architecture.svg (generated), scripts/generate-arch.dart (new)
- **Key deliverables:**
  - Script walks provider graph (Riverpod) + feature imports
  - Renders directed graph: features, core modules, external deps
  - CI regenerates on every PR; commit if diff
  - Links from diagram to source files
- **Acceptance gate:** Diagram renders on every PR; zero manual edits

### Workstream 10.4 — Decision log rolled up
- **Goal:** All decisions recorded in one place; history visible.
- **Target files:** PLANS/001-decision-log.md (new, summary of all phase decisions)
- **Key deliverables:**
  - Decision log pulled from each phase plan's Decision Log section
  - Rolled up to PLANS/001-decision-log.md
  - Format: date, phase, decision, rationale, alternatives
  - Searchable; indexed by dimension
- **Acceptance gate:** PLANS/001-decision-log.md linked from README; updated per phase exit

### Workstream 10.5 — Day-in-the-life runbook
- **Goal:** New dev completes a real bug-fix PR by day 2.
- **Target files:** docs/DEV_DAY.md (new), example task (GitHub issue), example PR (merged)
- **Key deliverables:**
  - Runbook: read issue → run app → reproduce bug → fix → test → submit PR → review feedback
  - Links to: how to run tests, how to read logs, how to commit, how to push
  - Example issue (e.g., "fix button color mismatch") + example PR
  - Checklist: clone, bootstrap, find issue, fix, test, push
- **Acceptance gate:** New dev (external contributor) completes checklist by day 2

### Workstream 10.6 — Onboarding docs per area
- **Goal:** Step-by-step setup for: mobile dev, backend dev, full-stack dev.
- **Target files:** docs/onboarding/<role>.md (3 files: mobile, backend, full-stack)
- **Key deliverables:**
  - Mobile dev: Flutter setup, Riverpod, testing
  - Backend dev: Supabase setup, edge functions, migrations
  - Full-stack dev: both + architecture overview
  - Each: 30-min checklist, links to deep dives
- **Acceptance gate:** All 3 docs merged; peer-reviewed

### Workstream 10.7 — Command inventory (lint, test, build, deploy, rollback)
- **Goal:** One command for each standard operation.
- **Target files:** Questerix/scripts/ and questerix-student-app/scripts/ (standardize existing)
- **Key deliverables:**
  - `make lint` or `dart analyze` + `flutter analyze` (student app) + `eslint` (Questerix)
  - `make test` or `flutter test lib/src/core` (targeted) + npm test (Questerix)
  - `make build` (Flutter build apk/ipa + admin build)
  - `make deploy` (one-command release for both projects)
  - `make rollback` (rollback to previous release)
  - All commands idempotent and documented
- **Acceptance gate:** All 5 commands working; zero manual fallback required on 3 consecutive releases

### Workstream 10.8 — Runbook index
- **Goal:** All runbooks discoverable from one place.
- **Target files:** Questerix/docs/runbooks/INDEX.md (new)
- **Key deliverables:**
  - Index of all runbooks: secret rotation, secret-rotation, incident response, release, rollback, etc.
  - Per-runbook: title, owner, last-verified date, link
  - Runbooks linked from relevant alerts, dashboards, PRs
  - Quarterly review: mark stale runbooks for update
- **Acceptance gate:** INDEX.md merged; every runbook listed + linked

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Onboarding time (clean clone → running) | unknown | ≤30 min | ≤10 min |
| ADR coverage (decisions documented) | 0% | 90% | 100% |
| Architecture diagram auto-generation | no | yes (daily) | yes (per PR) |
| Command-inventory coverage (lint/test/build/deploy/rollback) | 50% | 100% | 100% + idempotent |
| Day-in-the-life completion time (new dev) | n/a | 8h | 4h (by day 2) |
| Runbook count (top areas covered) | n/a | 10+ | 15+ + annual audit |
| Onboarding docs completeness | 0 | all 3 roles | 3+ roles + tutorial videos |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Bootstrap script breaks on env variations (Python version, Node version) | Med | Pre-flight checks; clear error messages; alternative setup instructions |
| Architecture diagram generation fails on graph changes | Low | Script is tested on every PR; CI gates on generation success |
| ADRs become stale (decisions change) | Med | ADRs have "status" field (Active, Superseded, Deprecated); quarterly review |
| Command inventory drifts (lint command changes, not documented) | Med | Commands in Makefile/scripts; README links to source of truth |
| Day-in-the-life runbook assumes IDE setup (VS Code); other IDEs fail | Low | Runbook is CLI-first; optional IDE sections |

## Dependencies & Sequencing

- **Can run in parallel** with all phases — DX is foundational
- **Phase 10 is continuous** — DX work happens per-phase, rolled up at end

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 10.1 (bootstrap):** Create Questerix/Makefile (or Windows equivalent) with a `bootstrap` target that: installs Flutter deps (pub get), Node deps (npm install in admin-panel), generates types (from Zod), seeds local Supabase, and runs `flutter run`. Time it: must complete ≤10 min on clean clone.
