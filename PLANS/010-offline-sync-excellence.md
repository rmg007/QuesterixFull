# 010 — Offline & Sync Robustness Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 9
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Offline & sync robustness excellence means the system is eventually-consistent under loss, reorder, duplicate, and clock-skew, with deterministic conflict resolution and tests for every resolver. Beyond perfection = 1000-run Monte Carlo sync test proves 100% convergence in ≤90s under chaos, every Drift table has a versioned conflict resolver, sync invariants are formally documented, and offline state is transparent to users (data syncs silently).

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/lib/src/core/sync/, lib/src/core/database/; Questerix/supabase/ (sync edge functions, migrations)
- **OUT:** help-docs, landing-pages, admin-only offline features
- **Respects:** R2 (additive Drift migrations), R3 (RLS required), R6 (no live tests), R9 (master only), R10 (integration tests on real DB)

## Phases & Workstreams

### Workstream 4.1 — Sync invariants doc
- **Goal:** Formalize the guarantees sync must maintain.
- **Target files:** questerix-student-app/docs/sync/INVARIANTS.md (new)
- **Key deliverables:**
  - Monotonic timestamps: server time always increases
  - Idempotent replay: replaying same event produces same result
  - Deterministic conflict resolution: same conflict always resolves the same way
  - Per-entity vector clock: tracks causal ordering per entity
  - Formal proof sketch: invariants imply eventual consistency
- **Acceptance gate:** Doc merged; referenced by all resolver tests

### Workstream 4.2 — Conflict resolvers per table
- **Goal:** Every syncing Drift table has a resolver + unit test.
- **Target files:** questerix-student-app/lib/src/core/sync/resolvers/ (new folder, one file per table)
- **Key deliverables:**
  - Resolver for each syncing table (quest_attempt, question_answer, progress, etc.)
  - Unit test per resolver: deterministic, no flakes, 100% coverage
  - Versioned resolvers for schema evolution
  - Conflict examples documented (e.g., "user answered Q1 offline, then online; pick latest timestamp")
- **Acceptance gate:** Every syncing table has a resolver; all tests passing

### Workstream 4.3 — Property-based sync tests
- **Goal:** Prove 1000 runs converge 100%.
- **Target files:** questerix-student-app/test/sync/property_test.dart (new)
- **Key deliverables:**
  - Property-based test using glados or similar
  - Generates random event sequences: local writes, remote writes, merges
  - Verifies deterministic conflict resolution
  - 1000 runs minimum
  - All pass without flake
- **Acceptance gate:** 1000 runs, 100% converge, zero flakes across 30 runs

### Workstream 4.4 — Chaos harness
- **Goal:** Inject failures; prove convergence under all conditions.
- **Target files:** questerix-student-app/integration_test/chaos/ (new folder)
- **Key deliverables:**
  - Network drop injector (random packet loss)
  - Reorder injector (shuffle event order)
  - Duplicate injector (replay events)
  - Clock-skew injector (timestamp drift ±5s)
  - Nightly CI run; 0 divergence tolerated
- **Acceptance gate:** Nightly chaos harness green; zero divergence cases

### Workstream 4.5 — Circuit breakers for external deps
- **Goal:** Graceful fallback when sync service unavailable.
- **Target files:** questerix-student-app/lib/src/core/network/circuit_breaker.dart (new)
- **Key deliverables:**
  - Circuit breaker for Supabase sync endpoint
  - Trip on 5 consecutive failures
  - Half-open after exponential backoff
  - Offline state transparent: local writes queue, UI shows "syncing..."
  - Test forces 500s error; verifies fallback within 1s
- **Acceptance gate:** Forced 500s trip breaker; offline state shows within 1s

### Workstream 4.6 — Retry-with-jitter policy
- **Goal:** Avoid thundering herd during outages.
- **Target files:** questerix-student-app/lib/src/core/sync/sync_manager.dart (update existing)
- **Key deliverables:**
  - Exponential backoff: 100ms, 200ms, 400ms, 800ms, cap 30s
  - Jitter: ±20% randomization
  - Max 5 retries per sync attempt
  - Tested under simulated load spike
- **Acceptance gate:** p99 retry storms capped; backoff verified under load

### Workstream 4.7 — Idempotency keys on writes
- **Goal:** Duplicate POST → single row.
- **Target files:** Questerix/supabase/functions/*/index.ts (update edge functions), new migration for idempotency_keys table
- **Key deliverables:**
  - idempotency_keys table: (request_id, response_hash, created_at, user_id)
  - Edge function middleware checks key before processing
  - Retry returns cached response
  - Test: POST twice with same request_id → single row + same response
- **Acceptance gate:** Duplicate POST returns 200 with same response; single row in DB

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Sync convergence (chaos, 1000 runs) | n/a | 95% @ ≤180s | 100% @ ≤90s |
| Conflict resolver coverage | unknown | 95% | 100% per table |
| Property-based sync flakes | n/a | 0 / month | 0 sustained |
| Offline state latency (trip to fallback) | n/a | ≤2s | ≤1s |
| Retry jitter compliance | n/a | 100% | 100% + <5% deviation |
| Idempotency coverage (write endpoints) | n/a | 100% | 100% + audit log |
| Sync push latency (50 events) | unknown | ≤2s | ≤1.5s |
| Sync pull latency (1MB delta) | unknown | ≤5s | ≤3s |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Sync property tests reveal deep schema issue | Med | Phase 4 budgets 25% buffer; schema fixes land as new migrations (R2) |
| Chaos harness masks real bugs by being too deterministic | Low | Seeded + random modes; both must pass |
| Retry storms during production incident | Med | Backoff tested under load; hard cap of 5 retries |
| Clock-skew in chaos harness doesn't reflect real-world drift | Low | Real-world drift capped by NTP; chaos uses ±5s as upper bound |
| Offline state confuses users (out-of-date data) | Med | Always show "last synced X minutes ago"; sync status visible |

## Dependencies & Sequencing

- **Must complete Phase 2** (Architecture) first — clean boundaries required
- **Must complete Phase 3** (Performance) first — perf budgets inform sync timeouts
- **Can run in parallel** with Phase 5 (AI)
- **Must complete before Phase 8** (Scale) — resilience is prerequisite

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 4.1 (invariants doc):** Create questerix-student-app/docs/sync/INVARIANTS.md documenting the 4 core guarantees with examples. Reference real sync implementation (Drift, Supabase edge functions) once implementation exists.
