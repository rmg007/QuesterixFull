# 003 — Performance Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 2
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Performance excellence means every user-visible interaction has a measured budget (frame, route, network, DB, AI), and p99 (not p50) is the target. Beyond perfection = p95 cold-start ≤2.0s, p99 ≤3.0s on mid-tier Android; dropped-frame ratio <1%; every golden path CI-gated; sync push <2s per 50 events; AI cached calls ≤1200ms p95.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/lib/src/core/observability/, lib/main.dart, app.dart; Questerix/supabase/functions/
- **OUT:** help-docs, landing-pages, admin-only features (R1 measurement only, no perf work)
- **Respects:** R1 (admin bugfix), R3 (RLS on new tables), R5 (targeted test paths), R6 (no live AI calls), R9 (master only)

## Phases & Workstreams

### Workstream 3.1 — Define the 10 golden paths with explicit budgets
- **Goal:** Codify the critical user flows and their latency budgets.
- **Target files:** questerix-student-app/docs/perf/golden-paths.md (new)
- **Key deliverables:**
  - 10 paths documented with budgets: cold start, login, start quest, answer question, submit answer, open progress, sync pull, sync push, AI hint, offline→online
  - Each budget wired to CI assertion
  - Baseline measurements captured
- **Acceptance gate:** Doc merged; CI assertions for all 10 paths green

### Workstream 3.2 — Frame-budget instrumentation
- **Goal:** Measure dropped-frame ratio per route; emit to WES.
- **Target files:** questerix-student-app/lib/src/core/observability/frame_profiler.dart (new)
- **Key deliverables:**
  - SchedulerBinding hook capturing dropped-frame ratio
  - Emitted to WES with route name
  - Per-route panels on perf dashboard
  - <1% dropped-frame ratio on mid-tier Android
- **Acceptance gate:** Dropped-frame ratio <1% on Pixel 4a emulator baseline in CI for 5-minute scripted session

### Workstream 3.3 — Cold-start optimization
- **Goal:** Reduce startup time by deferring non-critical init.
- **Target files:** questerix-student-app/lib/main.dart, lib/src/app.dart, lib/src/core/database/app_database.dart
- **Key deliverables:**
  - Defer non-critical provider initialization until first frame
  - Open Drift connection lazily behind a provider
  - Audit platform channel calls on boot
  - Pre-inflate hero widgets
- **Acceptance gate:** p95 cold-start ≤2.0s, p99 ≤3.0s measured via CI benchmark harness over 20 runs

### Workstream 3.4 — DB query budgets
- **Goal:** Log and monitor slow queries; tune to <50ms p95.
- **Target files:** Questerix/supabase/migrations/<date>_query_budget_log.sql (new)
- **Key deliverables:**
  - slow_queries table (RLS per R3); queries >50ms logged with plan, RPC name, tenant, correlation-id
  - Dashboard view of top-20 slow queries
  - Tuning recommendations per query
- **Acceptance gate:** Top-20 queries <50ms p95 after two weeks of tuning

### Workstream 3.5 — Bundle & asset budget (admin measurement, R1-safe)
- **Goal:** Track admin-panel bundle size without adding features.
- **Target files:** Questerix/admin-panel/scripts/bundle-budget.js (new)
- **Key deliverables:**
  - JSON output with per-chunk gzipped size
  - CI alarm if main chunk grows >10% vs. rolling median
  - Current size recorded in baseline
- **Acceptance gate:** Current size measured; alarm wired

### Workstream 3.6 — CI perf gate
- **Goal:** Block regressions on any of the 10 golden paths.
- **Target files:** Questerix/.github/workflows/perf.yml (new)
- **Key deliverables:**
  - Runs benchmark harness on PR
  - Fails if any golden-path p95 regresses by >10% vs. rolling 7-day median
  - Gate stable for 7 days before becoming required
- **Acceptance gate:** Gate stable for 7 days; zero false-positives

### Workstream 3.7 — Image & asset pipeline
- **Goal:** Compress images; ensure all variants present.
- **Target files:** questerix-student-app/scripts/asset_pipeline.dart (new), pubspec.yaml
- **Key deliverables:**
  - All PNGs converted to WebP where supported
  - 1x/2x/3x variants present
  - Lint blocks missing variants
  - Asset size down ≥30%
- **Acceptance gate:** App size reduced ≥30%; asset lint passes

### Workstream 3.8 — Supabase edge function cold-start audit
- **Goal:** Profile and optimize edge function boot time.
- **Target files:** Questerix/supabase/functions/*/index.ts
- **Key deliverables:**
  - Profile cold start of each function
  - Remove unused deps
  - Shared imports hoisted
  - Lazy init for optional features
- **Acceptance gate:** p95 edge cold-start ≤400ms

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| p95 cold-start (mid Android) | n/a | ≤3.0s | ≤2.0s |
| p99 cold-start | n/a | ≤5.0s | ≤3.0s |
| Dropped-frame ratio | n/a | <2% | <1% |
| Top-20 query p95 latency | n/a | <50ms | <30ms |
| Admin bundle (main chunk) growth | n/a | no >10% regressions | <5% / quarter |
| Golden-path regression frequency | n/a | ≤1 / month | 0 / month |
| Asset pipeline coverage | n/a | 100% | 100% + <0.1s encode time |
| Edge function p95 cold-start | n/a | ≤500ms | ≤400ms |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Perf budgets regress on older devices not in CI | Med | Add low-tier emulator (2019 spec) to perf CI matrix |
| Frame profiler overhead skews results | Med | Profile hook disabled by default; enabled only in CI runs |
| Asset pipeline breaks image quality | Low | Manual review of compressed images before commit |
| Cold-start deferral races on first-frame UI | Med | Add explicit `ensureReady()` boundary with test |

## Dependencies & Sequencing

- **Must complete Phase 0** (Foundation & Instrumentation) first
- **Can run in parallel** with Phase 2 (Architecture)
- **Must complete before Phase 7** (Observability) — perf metrics feed dashboards

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 3.1 (golden paths doc):** Create questerix-student-app/docs/perf/golden-paths.md with the 10 critical paths and their budgets. Measure current median latency on each path using the baseline harness and record.
