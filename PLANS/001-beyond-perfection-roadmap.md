# 001 — Beyond-Perfection Roadmap: Questerix + Student App

> **Type:** [ARCH] · **Status:** ACTIVE · **Owner:** Architect (Claude) · **Created:** 2026-04-17
> **Scope:** `Questerix/` (bugfix-only admin, full-range `packages/core/` + shared infra) and `questerix-student-app/`.
> **Explicitly out of scope:** `questerix-help-docs/`, `questerix-landing-pages/`.

---

## Purpose & North Star

"Beyond perfection" means the two products stop being scored against a checklist of best practices and start being scored against their own telemetry — every regression is caught before users see it, every slow frame is budgeted, every failure mode has a tested recovery path, and every piece of AI behavior is observable, replayable, and bounded. Concretely, this roadmap drives the Questerix student app and the shared Questerix backend from "passing 457/457 tests at 59% coverage" to a system where p99 cold-start is under 1.5s, offline sync is eventually-consistent under 90s on flaky networks, AI calls are cached/mocked/bounded with a published cost ceiling per DAU, WCAG 2.2 AA is enforced in CI, and a 10× user/content scale test runs nightly. The north-star metric is **Weekly Excellent Sessions (WES)** — a session that completes without error, meets p95 frame budget, succeeds at sync, and has no a11y violations — tracked per build and used to gate releases. Every phase below raises a specific, measurable dimension of that metric.

## Scope Lock

- **IN**
  - `Questerix/` for: `packages/core/` (types, utils, constants), `supabase/` (new migrations, edge functions, RLS, seeds, tests), `questerix-cortex/` (planning/verification tooling), shared CI/CD, observability wiring, and bugfix-only work in `admin-panel/`.
  - `questerix-student-app/` for: `lib/src/core/*`, `lib/src/features/*`, `test/`, `integration_test/`, `l10n/`, `scripts/`, platform channels under `android/` and `ios/` as needed for performance/a11y work.
- **OUT**
  - `questerix-help-docs/` (separate ownership, VitePress)
  - `questerix-landing-pages/` (marketing, separate deploy)
  - Any **new** admin-panel feature (freeze — Rule #1). Admin work in this plan is strictly: security patches, vulnerability remediation, dead-code removal, test coverage raises, and observability hooks that do not alter user-facing behavior.
- **Respects (cited by number; hard non-negotiable):**
  - **R1** Admin freeze — bugfix only in `Questerix/admin-panel/`.
  - **R2** Never modify existing Drift migrations — additive only.
  - **R3** All new DB tables require RLS (S/I/U/D + audit).
  - **R4** Supabase QueryBuilder is immutable — `query = query.eq(...)`.
  - **R5** No full `flutter test` runs — targeted paths only.
  - **R6** No live Gemini/AI API calls in tests — mocks only.
  - **R7** Theme tokens only, no hardcoded colors.
  - **R8** No committed secrets.
  - **R9** All work on master — no branches.
  - **R10** No mock DB where integration is the point.

## Excellence Dimensions (the axes we push past production-ready)

The plan advances these twelve dimensions. Every workstream in every phase must cite at least one.

1. **Architecture** — Boundaries are enforced by the build (dependency rules, layer lints). "Beyond perfection" = a new engineer cannot violate a boundary accidentally; the compiler or CI blocks it.
2. **Performance** — Not just "fast enough." Every user-visible interaction has a budget (frame, route, network, DB, AI) and a CI gate. p99, not p50, is the target.
3. **Resilience** — Every external dependency (Supabase, AI, storage) has a circuit breaker, a retry policy with jitter, and a fallback. Chaos drills run in CI.
4. **Observability** — Structured traces, metrics, and logs correlated by a single request ID across app → Supabase → edge functions. No "what happened to this user" question takes >5 minutes to answer.
5. **Security** — Zero known CVEs at HIGH or CRITICAL. RLS policies fuzz-tested. Secrets rotated quarterly. Threat model documented per feature.
6. **Accessibility** — WCAG 2.2 AA enforced by CI (contrast, touch targets, screen-reader labels, focus order). No regression ships.
7. **UX polish** — Interaction fidelity: haptics, transitions, skeletons, empty states, error states, and offline states for every screen. No "dead" state.
8. **AI capability depth** — Every AI path is typed, cached, bounded by a token/cost budget, replayable from a captured transcript, and has a deterministic fallback.
9. **Offline & sync robustness** — Eventually-consistent under loss, reorder, duplicate, and clock-skew. Deterministic conflict resolution with tests for every resolver.
10. **Test quality** — Not a coverage number. Mutation score ≥60% on critical paths, property-based tests on sync and scoring, contract tests at every boundary.
11. **Developer experience** — From clean clone to running app in <10 minutes. One command for each of: lint, targeted test, build, deploy, rollback.
12. **Scale horizon** — A 10× and 100× synthetic load test runs weekly; results gate schema/index changes.

---

## Phase Map

| # | Phase | Intent | Size | Dimensions | Entry Criteria | Exit Gate (measurable) |
|---|-------|--------|------|------------|---------------|------------------------|
| 0 | **Foundation & Instrumentation** | Make excellence measurable before changing anything. | M | 4, 10, 11 | Current HEAD on master, baseline metrics captured. | WES metric emits per build. Dashboards live for perf, a11y, AI cost, sync lag. Baseline JSON committed at `PLANS/001-baseline.json`. |
| 1 | **Security & Dependency Hardening** | Close CVEs, tighten RLS, rotate secrets, unify supply chain. | M | 5, 11 | Phase 0 dashboards green. | Admin npm vulns ≤0 HIGH/CRIT (from 11). RLS fuzz harness passes 100%. Dependabot + `renovate.json` merged. SBOM generated per build. |
| 2 | **Architecture Boundary Lock-in** | Make god-files and layer violations impossible to add. | M | 1, 10, 11 | Phase 0. | God-files ≤4 (from 9). Import-boundary lint passes on both projects in CI. `packages/core/` extracted shared types adopted by student app. |
| 3 | **Performance Budgets & Golden Paths** | Instrument and enforce budgets on the 10 most-used flows. | L | 2, 4, 7 | Phase 0. | p95 cold-start ≤2.0s, p99 ≤3.0s on mid-tier Android. Route transitions ≤16ms dropped-frame-rate <1%. Perf CI gate green 7 days. |
| 4 | **Resilience & Offline/Sync Correctness** | Prove sync convergence under adversarial conditions. | XL | 3, 9, 10 | Phase 2 (boundaries), Phase 3 (perf). | Chaos harness: 1000-run Monte Carlo sync test 100% convergence in ≤90s simulated. Every Drift table has a conflict resolver + property test. |
| 5 | **AI Depth, Safety & Cost Controls** | Every AI path is typed, cached, budgeted, replayable. | L | 3, 5, 8, 10 | Phase 4 (sync stable). | AI cost/DAU published; p95 latency ≤1200ms cached / ≤3500ms cold. Replay harness loads any prod failure as a fixture. Cost ceiling alarm wired. |
| 6 | **Accessibility & UX Polish to WCAG 2.2 AA** | A11y enforced in CI; every screen has all five states. | L | 6, 7, 10 | Phase 2. | 0 a11y violations in CI. Every route has skeleton/empty/error/offline/loaded states with tests. Haptic/transition audit complete. |
| 7 | **Observability & Closed-Loop Telemetry** | Every session is traceable end-to-end; alerts self-heal simple cases. | M | 4, 5 | Phase 0 (dashboards), Phase 3 (perf). | Single correlation ID spans app→edge→DB. Error budget policy published. 3 automated remediations wired (e.g., stuck-sync auto-reset). |
| 8 | **Scale Horizon (10× / 100×)** | Prove the schema and indexes survive 10× content and users. | L | 2, 12 | Phase 1 (security), Phase 4 (sync). | Synthetic load at 10× DAU sustains p95 budgets. 100× smoke test identifies exactly which index/schema items break. Capacity plan committed. |
| 9 | **Release Engineering & Rollback** | Shipping becomes routine, boring, and instantly reversible. | M | 3, 11 | Phase 7. | One-command release for both projects. Rollback tested monthly (drill in CI). Release notes auto-generated from conventional commits. |
| 10 | **Docs, DX, & Onboarding Excellence** | Clean clone → running app in ≤10 minutes for both projects. | S | 11 | All prior phases landed work to document. | New-dev onboarding timer ≤10 min measured in CI. Decision log complete. Runbooks cover top-10 alerts. |

---

## Phase Details

### Phase 0 — Foundation & Instrumentation

Before we change anything, we make excellence measurable. Every later phase spends this phase's currency.

- **WS 0.1 — Baseline freeze.**
  - *Goal:* a tamper-evident snapshot of current state, re-runnable nightly to detect drift.
  - *Target files:* `PLANS/001-baseline.json` (new), `Questerix/scripts/baseline.sh` (new), `questerix-student-app/scripts/baseline.sh` (new).
  - *Deliverables:* JSON with `vulns=11`, `admin_coverage=0.34`, `student_coverage=0.59`, `god_files=9`, `deps_behind=19`, `tests=457/457`, `analyzer_errors=0`, bundle sizes, route transition medians, cold-start median, AI call volume (last 7 days), WCAG violation count from a first automated scan.
  - *Acceptance gate:* file committed, checksum posted in `PLANS/INDEX.md` footer, nightly CI job re-captures and diff-alerts on >5% drift.
  - *Risks/mitigations:* stale baseline → script is idempotent; partial metric capture → `baseline.sh` exits non-zero if any field is null.

- **WS 0.2 — WES metric emitter.**
  - *Goal:* make "Weekly Excellent Session" a first-class, typed metric emitted from both app and backend.
  - *Target files:* `questerix-student-app/lib/src/core/observability/wes_emitter.dart` (new), `questerix-student-app/lib/src/core/observability/wes_schema.dart` (new), edge function `Questerix/supabase/functions/wes-ingest/index.ts` (new).
  - *Deliverables:* event schema (session_id, correlation_id, dropped_frames, sync_success, a11y_flags, ai_calls, ai_cost_est, errors[], duration_ms); Supabase table `telemetry_wes` added via new migration (**R3** — full S/I/U/D RLS + audit); typed Dart struct; typed Zod in `packages/core`.
  - *Acceptance gate:* first real event lands within 24h of merge; dashboard shows WES rate.
  - *Risks/mitigations:* PII leakage → schema reviewed against data-classification doc; high-volume cost → sampling at 10% with full-capture on error.

- **WS 0.3 — Performance dashboards (4).**
  - *Goal:* live visibility into cold-start, route transitions, AI latency, and sync lag.
  - *Target files:* `Questerix/supabase/migrations/<date>_telemetry_views.sql` (new — never edit per **R2**), `Questerix/docs/dashboards/perf-*.json` (4 files).
  - *Deliverables:* 4 materialized views refreshed every 5 min; dashboards render p50/p95/p99 over 7/30/90 days.
  - *Acceptance gate:* 72h of live data; alert rules committed.
  - *Risks/mitigations:* view refresh cost → concurrent refresh + partial indexes; missing data → fallback to raw event query below a data-density threshold.

- **WS 0.4 — A11y, AI-cost, and sync-lag dashboards (3).**
  - *Goal:* close the remaining measurement gaps for dimensions 6, 8, and 9.
  - *Target files:* same pattern as 0.3 — new migration, new dashboard JSON.
  - *Deliverables:* a11y violations/session, AI cost/DAU, sync lag p95 per platform, with alarms wired to the `#quality` channel.
  - *Acceptance gate:* each dashboard has at least one alarm fired in drills.
  - *Risks/mitigations:* alarm fatigue → alarms require 3 consecutive breaches before firing.

- **WS 0.5 — Critical-rules CI evidence.**
  - *Goal:* the 10 rules are not aspirational — every PR proves them.
  - *Target files:* `Questerix/scripts/rules-check/` and `questerix-student-app/scripts/rules-check/` (R1 admin diff analyzer, R2 Drift migration edit detector, R3 RLS-presence checker, R4 QueryBuilder lint, R5 full-test invocation blocker, R6 AI-call-in-test scanner, R7 hardcoded-color lint, R8 gitleaks, R9 branch-is-master check, R10 "real-DB required" marker).
  - *Deliverables:* `rules-report.json` artifact per CI run, human-readable summary in PR comment.
  - *Acceptance gate:* CI fails the PR if any rule regresses; current master passes all 10.

- **WS 0.6 — Correlation-ID plumbing.**
  - *Goal:* every request carries an ID; every emitted event, log line, and DB query references it.
  - *Target files:* `questerix-student-app/lib/src/core/observability/correlation.dart` (new); all Supabase client wrappers in `lib/src/core/services/`; edge functions.
  - *Deliverables:* header `x-correlation-id` injected at client, forwarded through edge functions, logged in pg via `set_config`.
  - *Acceptance gate:* a captured test session's ID appears in client logs, edge function logs, and DB query logs.

**Exit criteria for Phase 0:** Baseline committed; WES emitting at ≥90% of active sessions; 7 dashboards live; rules-report green; correlation ID visible end-to-end in a captured trace.

---

### Phase 1 — Security & Dependency Hardening

- **WS 1.1 — Admin-panel CVE remediation (strict bugfix per R1).**
  - *Goal:* 11 → 0 HIGH/CRIT vulnerabilities without adding features.
  - *Target files:* `Questerix/admin-panel/package.json`, `Questerix/admin-panel/package-lock.json`; patch-level bumps; `npm audit --audit-level=high` must return zero.
  - *Deliverables:* upgrade PRs with only lockfile + package.json diffs, each accompanied by `rules-report.json` proving R1 respected (zero source-file diffs unless the dep requires a call-site change, in which case the change is annotated as a bugfix).
  - *Acceptance gate:* `npm audit --audit-level=high` returns 0 for 14 consecutive days; coverage doesn't regress.
  - *Risks/mitigations:* transitive break → every bump runs Playwright smoke; breaking change requires a separate plan.

- **WS 1.2 — Supabase RLS fuzz harness.**
  - *Goal:* empirically prove every policy on every table for every role.
  - *Target files:* `Questerix/supabase/tests/rls_fuzz/generator.py`, `.../runner.py`, `.../expected.yaml` (new folder).
  - *Deliverables:* pgTAP + Python test that enumerates (table × operation × role × tenant × deleted_at) and asserts expected allow/deny against a seeded DB.
  - *Acceptance gate:* 100% of existing tables pass; a new table without policies fails CI (per **R3**).
  - *Risks/mitigations:* combinatorial explosion → filter by role relevance, run full matrix nightly.

- **WS 1.3 — Renovate + Dependabot unification.**
  - *Goal:* one dependency policy across both projects with tiered auto-merge.
  - *Target files:* `renovate.json` at root (extend existing), per-project `.github/dependabot.yml`.
  - *Deliverables:* grouped minor PRs weekly, security PRs daily, auto-merge for patch-level with green CI and passing rules-report.
  - *Acceptance gate:* `deps_behind` in the baseline drops from 19 to ≤5 within 30 days and stays ≤5.

- **WS 1.4 — SBOM + signed builds.**
  - *Goal:* every release has a machine-readable bill of materials.
  - *Target files:* `Questerix/scripts/sbom.sh` (new), `questerix-student-app/scripts/sbom.sh` (new), CI release workflow.
  - *Deliverables:* CycloneDX SBOM uploaded as a build artifact; signed with a project key.
  - *Acceptance gate:* SBOM present and verifiable on three consecutive releases.

- **WS 1.5 — Secret rotation runbook + CI scan.**
  - *Target files:* `Questerix/docs/runbooks/secret-rotation.md` (new), gitleaks in CI, calendar-driven GitHub Issue template.
  - *Deliverables:* quarterly rotation drill, last-verified date in the runbook frontmatter that CI asserts is ≤90 days old.
  - *Acceptance gate:* gitleaks scan clean on history; drill runs successfully once.

- **WS 1.6 — Student app certificate pinning + MITM replay test.**
  - *Target files:* `questerix-student-app/lib/src/core/network/pinned_client.dart` (new), `integration_test/security_pinning_test.dart` (new).
  - *Deliverables:* pinned HTTP client used by every outbound call; integration test uses a local proxy with a rogue cert and asserts rejection.
  - *Acceptance gate:* test green on Android + iOS CI.

- **WS 1.7 — Threat model doc per feature area.**
  - *Target files:* `Questerix/docs/threat-model/<area>.md` (auth, sync, AI, storage, rate-limit).
  - *Deliverables:* STRIDE-style doc, mitigations mapped to code, links to fuzz tests.
  - *Acceptance gate:* five docs merged; each new feature PR references the relevant area or creates a new one.

---

### Phase 2 — Architecture Boundary Lock-in

- **WS 2.1 — God-file decomposition (9 → ≤4).**
  - *Goal:* no file is both the data model and the orchestration point; no file is the only place a feature's rules live.
  - *Target files:* identified via `baseline.sh` — top-5 largest under `questerix-student-app/lib/src/features/` and `lib/src/core/services/`.
  - *Deliverables:* each god-file split into `<feature>/data/`, `<feature>/domain/`, `<feature>/presentation/`; new files ≤400 lines; pure-function extraction where possible; public API preserved.
  - *Acceptance gate:* god-file count drops to ≤4; widget/snapshot tests on affected features pass unchanged; analyzer still 0 errors.
  - *Risks/mitigations:* behavior regression → property tests added **before** the split; PR is split-only, behavior changes are separate PRs.

- **WS 2.2 — Import-boundary lint.**
  - *Goal:* enforce layering by the build, not by convention.
  - *Target files:* `questerix-student-app/analysis_options.yaml` (custom lints via `dart_code_metrics`), `Questerix/packages/core/.eslintrc.cjs` (custom ESLint boundary rules).
  - *Deliverables:* `features/A` cannot import `features/B` except via an explicit `features/A/public/` barrel; `core/*` cannot import `features/*`; admin panel can't import student-app internals and vice versa.
  - *Acceptance gate:* lint runs in CI on every PR; zero violations on master.

- **WS 2.3 — `packages/core` shared-type extraction + codegen.**
  - *Goal:* one source of truth for cross-app types; no hand-sync drift.
  - *Target files:* `Questerix/packages/core/src/types/` (authoritative Zod), `Questerix/packages/core/tools/codegen/` (new TS → Dart generator), output to `questerix-student-app/lib/src/core/types/generated/`.
  - *Deliverables:* generator emits Dart classes + JSON codecs from Zod schemas; generated files committed; CI verifies re-run produces no diff.
  - *Acceptance gate:* one shared enum (e.g. `QuestionType`) and one shared DTO (e.g. `QuestAttempt`) flow through codegen; CI step `generated-is-fresh` green.

- **WS 2.4 — Riverpod provider dependency graph.**
  - *Goal:* make provider graph visible, cycle-free, and diff-able in PRs.
  - *Target files:* `questerix-student-app/scripts/provider_graph.dart` (new), outputs `docs/provider-graph.svg`.
  - *Deliverables:* static analysis walks provider definitions, renders a DAG, fails if a cycle is found; PRs show graph diff.
  - *Acceptance gate:* zero cycles; graph rendered on every PR as CI artifact.

- **WS 2.5 — QueryBuilder immutability lint (R4).**
  - *Goal:* make the rule machine-enforced, not memorized.
  - *Target files:* `Questerix/packages/core/tools/eslint-rules/supabase-query-immutable.js` (new), enabled in admin-panel and edge functions.
  - *Deliverables:* custom ESLint rule flags `query.eq(...)`, `query.in_(...)`, `query.filter(...)`, etc., when the return value is discarded.
  - *Acceptance gate:* CI fails on violation; existing codebase passes.

- **WS 2.6 — `packages/core` test suite + publishing model.**
  - *Target files:* `Questerix/packages/core/src/**/*.test.ts`, `Questerix/packages/core/package.json`.
  - *Deliverables:* 90% line coverage on shared code; versioned releases via workspace protocol.
  - *Acceptance gate:* core tests run separately in CI; consumers pin to a version.

---

### Phase 3 — Performance Budgets & Golden Paths

- **WS 3.1 — Define the 10 golden paths with explicit budgets.**
  - *Target file:* `questerix-student-app/docs/perf/golden-paths.md` (new).
  - *Paths & budgets (draft; tuned in WS 3.2):* (1) cold start → home ≤2.0s p95; (2) login ≤1.2s server-side, ≤2.5s total; (3) start quest ≤600ms; (4) answer question interaction ≤80ms tap-to-feedback; (5) submit answer ≤400ms local, ≤2s sync; (6) open progress ≤500ms; (7) sync pull ≤5s for 1MB delta; (8) sync push ≤2s per 50 events; (9) AI hint ≤1200ms p95 cached, ≤3500ms cold; (10) offline→online reconnect ≤10s to green.
  - *Acceptance gate:* doc merged, each budget wired to a CI assertion (see 3.6).

- **WS 3.2 — Frame-budget instrumentation.**
  - *Target file:* `questerix-student-app/lib/src/core/observability/frame_profiler.dart` (new).
  - *Deliverables:* `SchedulerBinding` hook capturing dropped-frame ratio per route; emitted to WES with route name; per-route panels on perf dashboard.
  - *Acceptance gate:* dropped-frame ratio <1% on Pixel 4a emulator baseline in CI for a 5-minute scripted session.

- **WS 3.3 — Cold-start optimization.**
  - *Target files:* `questerix-student-app/lib/main.dart`, `lib/src/app.dart`, `lib/src/core/database/app_database.dart`.
  - *Deliverables:* defer non-critical provider initialization until first frame; open Drift connection lazily behind a provider; audit platform channel calls on boot; pre-inflate hero widgets.
  - *Acceptance gate:* p95 cold-start ≤2.0s, p99 ≤3.0s measured via CI benchmark harness over 20 runs.
  - *Risks/mitigations:* deferred init races → add explicit `ensureReady()` boundary with a test.

- **WS 3.4 — DB query budgets.**
  - *Target files:* new migration `<date>_query_budget_log.sql` creating `slow_queries` table (RLS-compliant per **R3**); trigger function using `pg_stat_statements`.
  - *Deliverables:* queries exceeding 50ms logged with plan, RPC name, tenant, correlation-id.
  - *Acceptance gate:* top-20 queries <50ms p95 after two weeks of tuning.

- **WS 3.5 — Bundle & asset budget (admin — measurement only, R1-safe).**
  - *Target file:* `Questerix/admin-panel/scripts/bundle-budget.js` (new — measurement only; does not modify source).
  - *Deliverables:* JSON output with per-chunk gzipped size; CI alarm if main chunk grows >10% vs. rolling median.
  - *Acceptance gate:* current size recorded in baseline; alarm wired; no behavior change committed.

- **WS 3.6 — CI perf gate.**
  - *Target file:* `Questerix/.github/workflows/perf.yml` (new — applies to student app too).
  - *Deliverables:* runs the benchmark harness on PR; fails if any golden-path p95 regresses by >10% vs. rolling 7-day median.
  - *Acceptance gate:* gate stable for 7 days before becoming required.

- **WS 3.7 — Image & asset pipeline.**
  - *Target files:* `questerix-student-app/scripts/asset_pipeline.dart` (new), `pubspec.yaml` asset declarations.
  - *Deliverables:* all PNGs converted to WebP where supported; 1x/2x/3x variants present; lint blocks missing variants.
  - *Acceptance gate:* asset size down ≥30%; app size reduced accordingly.

- **WS 3.8 — Supabase edge function cold-start audit.**
  - *Target files:* `Questerix/supabase/functions/*/index.ts`.
  - *Deliverables:* profile cold start of each function; remove unused deps; shared imports hoisted; lazy init for optional features.
  - *Acceptance gate:* p95 edge cold-start ≤400ms.

---

### Phase 4 — Resilience & Offline/Sync Correctness

- **WS 4.1 — Sync invariants doc.** Target: `questerix-student-app/docs/sync/INVARIANTS.md`. Deliverables: formal list — monotonic timestamps, idempotent replay, deterministic conflict resolution, per-entity vector clock.
- **WS 4.2 — Conflict resolvers per table.** Target: `questerix-student-app/lib/src/core/sync/resolvers/`. Each Drift table that syncs needs a resolver + unit test. **Per R2**, we add new Drift migration files only — never edit existing.
- **WS 4.3 — Property-based sync tests.** Target: `questerix-student-app/test/sync/property_test.dart` using `glados` or similar. Gate: 1000 runs, 100% converge.
- **WS 4.4 — Chaos harness.** Target: `questerix-student-app/integration_test/chaos/`. Deliverables: network drop, reorder, duplicate, clock-skew injectors. Gate: nightly CI run, 0 divergence tolerated.
- **WS 4.5 — Circuit breakers for external deps.** Target: `questerix-student-app/lib/src/core/network/circuit_breaker.dart`; Supabase + Gemini wrappers. Gate: forced 500s trip breaker, UI shows offline fallback within 1s.
- **WS 4.6 — Retry-with-jitter policy.** Target: same module. Gate: p99 retry storms capped; backoff verified under load.
- **WS 4.7 — Idempotency keys on writes.** Target: Supabase edge functions + edge function tests. Schema addition via new migration. Gate: duplicate POST → single row.

---

### Phase 5 — AI Depth, Safety & Cost Controls

- **WS 5.1 — Typed AI contracts.** Target: `Questerix/packages/core/src/types/ai/` — Zod schemas for every AI call, propagated to Dart via codegen (Phase 2 plumbing). Gate: no `any` or `dynamic` at AI boundaries.
- **WS 5.2 — Replay harness.** Target: `questerix-student-app/test/ai/replay/` + fixture dir. Deliverables: every prod AI failure (sampled) becomes a fixture; harness reruns it offline. Honors **R6** — no live API calls. Gate: 50 fixtures passing.
- **WS 5.3 — Cost ceiling + alarm.** Target: Supabase edge function middleware that tags every AI call with `estimated_tokens`, `user_id`, `feature`. View: `ai_cost_per_dau`. Gate: alarm when rolling 7-day cost/DAU exceeds published budget.
- **WS 5.4 — Cache layer.** Target: `Questerix/supabase/functions/ai-cache/`. Deliverables: content-addressed cache keyed by (prompt-hash, model, params). Gate: ≥30% hit rate for hint/feedback calls within 14 days.
- **WS 5.5 — Deterministic fallback.** Target: when AI unavailable, a rules-based fallback returns a valid (if less rich) response. Gate: chaos test in Phase 4 forces AI-down for 1h; no user-visible error.
- **WS 5.6 — Prompt-injection & safety tests.** Target: `Questerix/supabase/tests/ai_safety/`. 100 adversarial fixtures. Gate: 100% blocked or sanitized.

---

### Phase 6 — Accessibility & UX Polish to WCAG 2.2 AA

- **WS 6.1 — A11y lint in CI.**
  - *Target files:* `questerix-student-app/scripts/a11y_lint.dart` (new) + golden tests under `test/accessibility/`.
  - *Deliverables:* contrast checker on every theme token combination, 48dp minimum touch target asserted per widget, semantic-label presence asserted for every `GestureDetector`/`InkWell`/`IconButton`.
  - *Acceptance gate:* zero violations on CI; existing violations fixed via a staged warnings-first rollout.
  - *Risks/mitigations:* false positives in contrast for decorative elements → opt-out marker documented.

- **WS 6.2 — Screen-reader semantics tests.**
  - *Target file:* `questerix-student-app/test/accessibility/semantics_test.dart` (new).
  - *Deliverables:* every route walked with `SemanticsHandle`; focus order validated; dynamic announcements (e.g., "correct answer") verified.
  - *Acceptance gate:* passes on all routes in student app.

- **WS 6.3 — Five-state audit per screen.**
  - *Target files:* `questerix-student-app/test/widget/<feature>/states_test.dart` (per feature).
  - *Deliverables:* every route has golden tests for loaded, loading skeleton, empty, error, offline.
  - *Acceptance gate:* 100% route coverage; skipping a state requires a documented waiver.

- **WS 6.4 — Theme-token enforcement (R7).**
  - *Target files:* custom analyzer rule in `analysis_options.yaml`; a11y-aware theme tokens in `lib/src/core/theme/`.
  - *Deliverables:* hex literals outside theme folder fail CI; all colors referenced via `Theme.of(context).extension<AppColors>()` or equivalent.
  - *Acceptance gate:* zero violations.

- **WS 6.5 — Haptic & motion audit.**
  - *Target files:* `questerix-student-app/docs/ux/motion-audit.md` (new); reduced-motion provider.
  - *Deliverables:* map of every animation to intent (essential vs. decorative); reduce-motion OS setting disables decorative; haptics scoped to confirmed-intent actions only.
  - *Acceptance gate:* toggling reduce-motion eliminates all non-essential animation verified by widget test.

- **WS 6.6 — Dynamic type & RTL pass.**
  - *Target files:* locale goldens under `test/l10n/`.
  - *Deliverables:* app renders correctly at text-scale 2.0×; RTL Arabic locale smoke test.
  - *Acceptance gate:* no overflow or clipped UI in golden diffs.

- **WS 6.7 — Copy review & tone consistency.**
  - *Target files:* `questerix-student-app/lib/l10n/app_en.arb` + any UX copy constants.
  - *Deliverables:* consistent voice, grade-level reading score target, error-message tone audit.
  - *Acceptance gate:* copy review checklist committed; automated reading-level check on new strings.

---

### Phase 7 — Observability & Closed-Loop Telemetry

- **WS 7.1 — Correlation ID end-to-end.** Target: app header injection → edge function → DB logs. Module: `questerix-student-app/lib/src/core/observability/correlation.dart`. Gate: a single ID threads through a captured session.
- **WS 7.2 — Error budget policy.** Target: `docs/error-budget.md` committed in both repos. Gate: breach pauses feature work until green (automated via CI label).
- **WS 7.3 — Three automated remediations.** Examples: (a) stuck sync auto-reset after 5 failed pushes; (b) AI cache warmup on cache-miss spike; (c) forced client refresh on schema-version mismatch. Gate: each has a test, a runbook, and a "times fired" counter.
- **WS 7.4 — Session replay (privacy-safe).** Target: WES session IDs link to structured event timelines (not pixel replay). Gate: any user report resolvable in ≤5 minutes via replay.
- **WS 7.5 — On-call runbooks for top 10 alerts.** Target: `Questerix/docs/runbooks/`. Gate: every alert in Phase 0 dashboards has a runbook.

---

### Phase 8 — Scale Horizon (10× / 100×)

- **WS 8.1 — Synthetic load harness.** Target: `Questerix/supabase/tests/load/` + k6 or Artillery scripts. Gate: 10× DAU load run nightly, p95 budgets hold.
- **WS 8.2 — Index & query-plan audit.** Target: `Questerix/supabase/scripts/audit-plans.sql`. Gate: top-20 queries have sensible plans at 10× row counts; regressions block merges.
- **WS 8.3 — Partitioning plan for high-churn tables.** Target: `Questerix/docs/scale/partitioning.md` + new migrations (per **R2**, additive only). Gate: test env shows the partitioned design holds at 100× volumes; rollout phased.
- **WS 8.4 — Client-side scale.** Target: paginate every list; virtualize long lists in student app. Gate: 10k-item quest log scrolls at 60fps on mid-tier Android.
- **WS 8.5 — Capacity plan.** Target: `Questerix/docs/scale/capacity-plan.md`. Gate: published headroom at DB (CPU/IOPS), edge fn (invocations/mo), storage (GB).

---

### Phase 9 — Release Engineering & Rollback

- **WS 9.1 — One-command release.**
  - *Target files:* `Questerix/scripts/release.sh` (new), `questerix-student-app/scripts/release.sh` (new).
  - *Deliverables:* single command runs `lint → test → build → sign → publish → notify`; idempotent; dry-run mode for rehearsal.
  - *Acceptance gate:* three consecutive releases shipped via the command with zero manual fallback.

- **WS 9.2 — Automated rollback drill.**
  - *Target files:* `Questerix/.github/workflows/rollback-drill.yml` (new).
  - *Deliverables:* monthly cron deploys N-1 to staging, runs smoke, asserts WES rate matches N baseline within tolerance.
  - *Acceptance gate:* drill green for three consecutive months; MTTR ≤15 min.

- **WS 9.3 — Conventional commits → auto changelog.**
  - *Target files:* `CHANGELOG.md` in both repos (generated), `commit-msg` git hook, CI linter.
  - *Deliverables:* changelog generated on release; PR title lint enforces conventional format.
  - *Acceptance gate:* two releases with fully auto-generated, accurate changelogs.

- **WS 9.4 — Canary / staged rollout for mobile.**
  - *Target files:* `questerix-student-app/docs/release/rollout-policy.md` (new); CI webhook that pauses rollout on WES regression >5%.
  - *Deliverables:* 1% → 10% → 50% → 100% progression with 24h soak each; automated halt on regression.
  - *Acceptance gate:* one full staged rollout completed without incident.

- **WS 9.5 — Environment parity check.**
  - *Target file:* `Questerix/scripts/env-parity.sh` (new).
  - *Deliverables:* diffs dev/staging/prod Supabase config (auth settings, RLS presence, function deploys) and app env vars; produces a structured report.
  - *Acceptance gate:* CI fails on drift except for an explicit allow-list.

- **WS 9.6 — Release retro cadence.**
  - *Target files:* `docs/release-retros/<date>.md` (per release).
  - *Deliverables:* 5-line structured retro per release (shipped, regressed, MTTR, lessons, next action).
  - *Acceptance gate:* four consecutive releases have retros.

---

### Phase 10 — Docs, DX, & Onboarding Excellence

- **WS 10.1 — `make bootstrap`** (or equivalent on Windows via `orchestrator.ps1`). Target: one command to install deps, generate types, seed DB, run the app. Gate: timed onboarding ≤10 minutes on clean clone in CI.
- **WS 10.2 — ADRs for every major decision.** Target: `Questerix/docs/adr/` and `questerix-student-app/docs/adr/`. Gate: every Phase exit produces at least one ADR.
- **WS 10.3 — Living architecture diagram.** Target: auto-generated from code (provider graph + boundary graph). Gate: diagram updated in CI, not by hand.
- **WS 10.4 — Decision log rolled up.** Target: `PLANS/001-decision-log.md` pulled into this plan's Decision Log section.
- **WS 10.5 — "Day in the life" runbook.** Target: `docs/DEV_DAY.md`. Gate: a new dev completes one real bug-fix PR end-to-end on day 2.

---

## Cross-Cutting Tracks

These run in parallel with all phases and have their own cadence.

- **T-OBS (Observability) — weekly.** Dashboards reviewed every Friday; any red line is a P1 task on Monday.
- **T-SEC (Security) — biweekly.** SBOM review, dependency triage, RLS fuzz results. Quarterly: threat model refresh.
- **T-CI/CD — continuous.** New gates added as phases complete. Gate inventory: `Questerix/.github/GATE_INVENTORY.md`.
- **T-DOCS — per-merge.** If a PR changes behavior visible to another team, it updates docs in the same PR.
- **T-RELEASE — monthly.** Rollback drill + release retro + deploy-frequency metric reviewed.
- **T-A11Y — per-PR (after Phase 6).** A11y CI gate; per-quarter manual screen-reader audit.

---

## Sequencing & Dependencies

```
Phase 0 (Foundation) ──▶ Phase 1 (Security) ──▶ Phase 8 (Scale)
           │                   │                    ▲
           ├──▶ Phase 2 (Arch) ─┼──▶ Phase 4 (Resilience) ─┤
           │                   │                    ▲
           ├──▶ Phase 3 (Perf) ─┘                    │
           │                                         │
           ├──▶ Phase 6 (A11y) ◀── Phase 2           │
           │                                         │
           ├──▶ Phase 7 (Observability) ◀── Phase 3  │
           │                                         │
           └──▶ Phase 5 (AI) ◀── Phase 4 ────────────┘

Phase 9 (Release Eng) ◀── Phase 7
Phase 10 (Docs) ◀── all prior phases have landed artifacts
```

- **Must be serial:** 0 → 1, 0 → 2, 2 → 4, 4 → 5, 3 → 7, 7 → 9.
- **Can run in parallel:** 2 ∥ 3, 5 ∥ 6, 6 ∥ 8 (a11y work is independent of load work).
- **Phase 10 is continuous but only "closable" at the end.**

---

## Success Metrics (Beyond-Perfection Scorecard)

| # | Metric | Baseline (2026-04-17) | Production-Ready Target | Beyond-Perfection Target | Leading / Lagging |
|---|--------|----------------------|------------------------|-------------------------|-------------------|
| 1 | Admin npm HIGH/CRIT vulns | 11 | 0 | 0 (sustained 90 days) | Leading |
| 2 | Admin coverage | 34% | 60% (bugfix-only; no new features) | 75% on changed lines | Lagging |
| 3 | Student coverage | 59% | 75% | 85% line, 70% branch | Lagging |
| 4 | Student tests passing | 457/457 | 457/457 | 457/457 **+ mutation score ≥60% on critical paths** | Lagging |
| 5 | God-files (>500 lines) | 9 | 4 | 0 | Leading |
| 6 | Dependencies behind | 19 | 5 | 0 critical, ≤5 minor | Leading |
| 7 | Analyzer errors (student) | 0 | 0 | 0 + ≤10 warnings | Leading |
| 8 | p95 cold start (mid Android) | n/a (measure in P0) | ≤3.0s | ≤2.0s | Leading |
| 9 | p99 cold start | n/a | ≤5.0s | ≤3.0s | Leading |
| 10 | Dropped-frame ratio | n/a | <2% | <1% | Leading |
| 11 | Sync convergence (chaos) | n/a | 95% @ ≤180s | 100% @ ≤90s | Lagging |
| 12 | AI p95 latency (cached) | n/a | ≤2000ms | ≤1200ms | Leading |
| 13 | AI cost/DAU | n/a | published + alarmed | within published budget 30 days | Lagging |
| 14 | WCAG 2.2 AA violations | n/a | 0 new in CI | 0 app-wide | Leading |
| 15 | Five-state coverage per route | unknown | 80% | 100% | Lagging |
| 16 | Correlation-ID end-to-end | no | yes | 100% of WES sessions | Leading |
| 17 | Error-budget breach frequency | n/a | ≤1 / quarter | 0 / quarter | Lagging |
| 18 | Rollback drill MTTR | n/a | ≤60 min | ≤15 min | Lagging |
| 19 | Onboarding time (clean clone → running) | n/a | ≤30 min | ≤10 min | Leading |
| 20 | Weekly Excellent Sessions (WES) | n/a | 70% of sessions | 90% of sessions | Lagging |

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Owner-slot |
|---|------|------------|--------|------------|-----------|
| R-01 | Admin freeze tempts "just one feature" drift while fixing CVEs. | Med | High | Rules-check CI (WS 0.5) flags any non-bugfix diff in `admin-panel/`. Reviewer must cite R1. | Reviewer |
| R-02 | Sync property tests reveal deep schema issue. | Med | High | Phase 4 budgets 25% buffer; schema fixes land as new Drift migrations (**R2**). | Architect |
| R-03 | Perf budgets regress on older devices not in CI. | Med | Med | Add a low-tier emulator (2019 spec) to the perf CI matrix. | Perf WS owner |
| R-04 | AI cost/DAU overruns budget during replay harness dev. | Low | Med | All replay is offline (**R6**); live cost gated by alarm before release. | AI WS owner |
| R-05 | RLS fuzz false-positives block migrations. | Med | Med | Fuzz harness is advisory for first 14 days, then enforcing; triage queue in `tasks.md`. | Security |
| R-06 | Codegen (TS → Dart) introduces drift. | High | Med | CI step fails if generated files aren't checked in or don't match. | Arch WS owner |
| R-07 | 100× synthetic load costs real money. | Low | Med | Scale tests scoped to a budgeted env; hard monthly cap. | Scale WS owner |
| R-08 | A11y CI is noisy, teams learn to ignore. | Med | Med | Start with warnings, promote to errors at Phase 6 exit; every failure linked to a fix playbook. | A11y WS owner |
| R-09 | Chaos harness masks real bugs by being too deterministic. | Low | High | Seeded + random modes; both must pass. | Resilience WS owner |
| R-10 | Secret rotation runbook goes stale. | Med | High | Rotation is calendarized and the runbook itself has a "last verified" field CI checks. | Security |
| R-11 | Branch-discipline drift (R9 violated). | Low | High | Pre-push hook blocks non-master pushes from local; CI rejects non-master PRs. | DX |
| R-12 | "Beyond perfection" scope-creep into help-docs/landing-pages. | Med | Low | This plan's Scope Lock section is reviewed on every phase exit; out-of-scope items filed as their own plans. | Architect |

---

## Out of Scope (explicit)

- **`questerix-help-docs/`** — any VitePress/content-tooling work belongs in its own plan.
- **`questerix-landing-pages/`** — any marketing-site work belongs in its own plan.
- **New admin-panel features** — R1 freeze. If a need surfaces, it becomes a separate plan for future post-freeze work; this plan explicitly does not reopen the freeze.
- **Edits to existing Drift migrations** — R2. All DB schema evolution in this plan is additive.
- **Full `flutter test` invocations in CI or scripts** — R5. Targeted paths only.
- **Live AI API calls in any test suite** — R6. Replay + fixtures only.
- **Any hardcoded color / theme token bypass** — R7.
- **Branches for this work** — R9. All commits go directly to master.
- **Mock Supabase in integration tests** — R10. Integration-level tests run against a seeded ephemeral Supabase instance.

---

## Decision Log

Format for each entry:
`YYYY-MM-DD · [PHASE#/WS#] · Decision · One-line rationale · Alternatives considered (1 line).`

*(Empty — populated during execution.)*

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

---

## Next Action

Create `PLANS/001-baseline.json` by running the baseline-capture script (WS 0.1) and committing it to master. This single artifact unlocks every subsequent measurement gate in the plan.
