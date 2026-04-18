# 013 — Scale Horizon Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 12
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Scale horizon excellence means a 10× and 100× synthetic load test runs nightly, results gate schema/index changes, and the system's headroom is published. Beyond perfection = 10× DAU sustains p95 perf budgets, 100× smoke test identifies exactly which index/schema items break, and a capacity plan is committed to docs with quarterly reviews.

## Scope Lock (inherited from master)

- **IN:** Questerix/supabase/ (load tests, query audit, partitioning), questerix-student-app/ (client-side scale: pagination, virtualization)
- **OUT:** help-docs, landing-pages, admin-only scale work
- **Respects:** R2 (additive migrations), R3 (RLS required), R5 (targeted test paths), R9 (master only), R10 (integration tests on real DB)

## Phases & Workstreams

### Workstream 8.1 — Synthetic load harness
- **Goal:** 10× DAU load runs nightly; p95 budgets hold.
- **Target files:** Questerix/supabase/tests/load/ (new folder: k6 or Artillery scripts)
- **Key deliverables:**
  - Load test scripts: simulate 10× active users doing golden-path flows (login, start quest, answer, submit, sync)
  - Nightly CI run against staging DB (or ephemeral prod-equivalent)
  - Metrics: p50/p95/p99 latency per endpoint, error rate, connection pool exhaustion
  - Results published to dashboards; alert if any metric degrades
- **Acceptance gate:** 10× DAU load runs nightly; p95 budgets hold 7 days

### Workstream 8.2 — Index & query-plan audit
- **Goal:** Top-20 queries have sensible plans at 10× volumes.
- **Target files:** Questerix/supabase/scripts/audit-plans.sql (new)
- **Key deliverables:**
  - Audit script runs EXPLAIN ANALYZE on top-20 queries at 10× row counts
  - Identifies missing indexes; flags full scans
  - Query plan stored in CI artifacts
  - New schema/index changes gate on plan audit passing
- **Acceptance gate:** Top-20 queries have index-backed plans; regressions block merges

### Workstream 8.3 — Partitioning plan for high-churn tables
- **Goal:** High-churn tables (e.g., events, logs) don't degrade at 100× volumes.
- **Target files:** Questerix/docs/scale/partitioning.md (new), new migrations (per R2, additive only)
- **Key deliverables:**
  - Identify high-churn tables (e.g., telemetry_wes, sync_events, slow_queries)
  - Partitioning strategy: time-based (monthly), range-based (user_id), or hash
  - Test env partitioned design holds at 100× volumes
  - Rollout phased: staging first, prod via canary
- **Acceptance gate:** Test env at 100× shows no performance degradation with partitioning

### Workstream 8.4 — Client-side scale
- **Goal:** Large lists (10k items) scroll smoothly on mid-tier Android.
- **Target files:** questerix-student-app/lib/src/core/widgets/ (pagination, virtualization)
- **Key deliverables:**
  - Pagination: all list endpoints paginate by default (20-50 items per page)
  - Virtualization: long lists use ListView.builder or SliverList with caching
  - Test: quest log with 10k entries scrolls at 60fps on Pixel 4a emulator
  - Benchmark: render 1000 items in <500ms
- **Acceptance gate:** 10k-item list scrolls 60fps on Pixel 4a; benchmark <500ms

### Workstream 8.5 — Capacity plan
- **Goal:** Published headroom at DB (CPU/IOPS), edge functions (invocations/mo), storage (GB).
- **Target files:** Questerix/docs/scale/capacity-plan.md (new)
- **Key deliverables:**
  - Current baseline: DB CPU/IOPS/connections, edge invocations/month, storage GB
  - 10× extrapolation: estimated CPU/IOPS needed at 10× DAU
  - 100× extrapolation: estimated CPU/IOPS at 100× DAU (smoke test)
  - Headroom targets: CPU <70%, IOPS <80%, connections <80% of limit
  - Quarterly review: update with real metrics
- **Acceptance gate:** Plan merged; baselines recorded; next review date set

### Workstream 8.6 — Schema / index change gate
- **Goal:** No schema/index change merges without scale test approval.
- **Target files:** .github/workflows/ (scale-test gate), Questerix/scripts/schema-change-detect.sh (new)
- **Key deliverables:**
  - CI detects schema changes (migrations, index additions/removals)
  - Triggers load test + audit-plans.sql on staging
  - Merge blocked if any metric regresses
  - Bypass requires approval from architect + two reviewers (rare)
- **Acceptance gate:** Gate enforced; zero regressions on 3 consecutive scale tests

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Synthetic load (10× DAU) p95 latency hold | n/a | ±10% vs. 1× | ±5% vs. 1× |
| Top-20 query execution plans | unknown (measure P8) | 100% index-backed | 100% + <50ms p95 |
| High-churn table scale (100× volumes) | unknown | degrades <20% | degrades <5% |
| Client-side scale (10k items) fps | n/a | 60fps | 60fps sustained, 0 jank |
| Capacity headroom (CPU/IOPS) | unknown | 50-70% | 30-50% |
| Headroom buffer (months to scale limit) | n/a | 6 months | 12+ months |
| Schema/index change gate coverage | 0% | 100% | 100% + zero regressions |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Synthetic load doesn't reflect real-world access patterns | Med | Load test designed from golden paths + real prod logs sampling |
| 100× test costs real money (ephemeral DB expensive) | Low | Scale tests scoped to a budgeted env; hard monthly cap on costs |
| Partitioning breaks rollback process | Low | Rollback tested quarterly; undo script included in migration |
| Client-side pagination introduces new loading states (UX churn) | Med | Loading state designed alongside pagination; golden tests added |
| Capacity plan becomes stale (never updated) | Med | Plan has "last verified" date; CI checks ≤90 days old quarterly |

## Dependencies & Sequencing

- **Must complete Phase 1** (Security) first — stable baseline required
- **Must complete Phase 4** (Resilience) first — resilience patterns are prerequisite
- **Can run in parallel** with Phase 7 (Observability)
- **Phase 8 is pre-requisite for Phase 9** (Release Engineering) — scale confidence required before shipping

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 8.1 (synthetic load):** Create Questerix/supabase/tests/load/ folder with k6 or Artillery scripts for 10× DAU load test. Test: simulate 1000 concurrent users doing golden-path flows (login, start quest, answer question, submit, sync). Run nightly and publish results to dashboards.
