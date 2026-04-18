# 004 — Resilience Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 3
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Resilience excellence means every external dependency (Supabase, AI, storage) has a circuit breaker, retry policy with jitter, and fallback. Beyond perfection = chaos harness proves 100% sync convergence in ≤90s under adversarial conditions (loss, reorder, duplicate, clock-skew), every Drift table has a conflict resolver with property-based tests, and deterministic fallbacks survive 1-hour AI outages.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/lib/src/core/sync/, lib/src/core/network/; Questerix/supabase/ (RLS, edge functions, migrations)
- **OUT:** help-docs, landing-pages, admin-specific resilience work
- **Respects:** R2 (additive Drift migrations), R3 (RLS required), R4 (immutable QueryBuilder), R6 (no live API in tests), R9 (master only), R10 (integration tests on real DB)

## Phases & Workstreams

### Workstream 4.1 — Sync invariants doc
- **Goal:** Formalize the guarantees that sync must maintain.
- **Target files:** questerix-student-app/docs/sync/INVARIANTS.md (new)
- **Key deliverables:**
  - Monotonic timestamps
  - Idempotent replay
  - Deterministic conflict resolution
  - Per-entity vector clock semantics
  - Formal proof sketch
- **Acceptance gate:** Doc merged; cited by all conflict resolver tests

### Workstream 4.2 — Conflict resolvers per table
- **Goal:** Every syncing Drift table has a resolver + unit test.
- **Target files:** questerix-student-app/lib/src/core/sync/resolvers/ (new folder per table)
- **Key deliverables:**
  - Resolver for each Drift table that syncs
  - Unit test per resolver (deterministic logic, no flakes)
  - Versioned resolvers for schema evolution
  - All tests passing
- **Acceptance gate:** Every syncing table has a resolver; 100% test coverage on resolver code

### Workstream 4.3 — Property-based sync tests
- **Goal:** Prove 1000 runs of sync converge 100%.
- **Target files:** questerix-student-app/test/sync/property_test.dart (new) using glados or similar
- **Key deliverables:**
  - Property-based test generating random event sequences
  - Verifies deterministic conflict resolution
  - 1000 runs minimum per test
  - All pass without flake
- **Acceptance gate:** 1000 runs, 100% converge, zero flakes across 30 runs

### Workstream 4.4 — Chaos harness
- **Goal:** Inject failures (network drop, reorder, duplicate, clock-skew); prove convergence.
- **Target files:** questerix-student-app/integration_test/chaos/ (new folder)
- **Key deliverables:**
  - Network drop injector (random packet loss)
  - Reorder injector (shuffle event order)
  - Duplicate injector (replay events)
  - Clock-skew injector (timestamp drift)
  - Nightly CI run with 0 divergence tolerated
- **Acceptance gate:** Nightly chaos harness green; zero divergence cases

### Workstream 4.5 — Circuit breakers for external deps
- **Goal:** Trip breaker on repeated failures; show offline state.
- **Target files:** questerix-student-app/lib/src/core/network/circuit_breaker.dart (new)
- **Key deliverables:**
  - Circuit breaker for Supabase + Gemini
  - Trip on 5 consecutive failures
  - Half-open state after exponential backoff
  - UI shows offline fallback within 1s of trip
  - Test forces 500s, verifies fallback
- **Acceptance gate:** Forced 500s trip breaker; UI shows offline state within 1s

### Workstream 4.6 — Retry-with-jitter policy
- **Goal:** Cap retry storms; avoid thundering herd.
- **Target files:** Same module as 4.5; RPC wrappers
- **Key deliverables:**
  - Exponential backoff: 100ms, 200ms, 400ms, 800ms, cap 30s
  - Jitter: ±20% randomization
  - Max 5 retries per call
  - Tested under simulated load spike
- **Acceptance gate:** p99 retry storms capped; backoff verified under load

### Workstream 4.7 — Idempotency keys on writes
- **Goal:** Duplicate POST → single row (exactly-once semantics).
- **Target files:** Questerix/supabase/functions/*/index.ts + new migration for idempotency_keys table
- **Key deliverables:**
  - Idempotency_keys table with (request_id, response_hash, created_at)
  - Edge function middleware checks key before processing
  - Retry of same request returns cached response
  - Integration test: POST twice with same request_id → single row
- **Acceptance gate:** Duplicate POST returns 200 with same response; single row in DB

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Sync convergence (chaos, 1000 runs) | n/a | 95% @ ≤180s | 100% @ ≤90s |
| Conflict resolver coverage | unknown | 95% | 100% |
| Property-based sync flakes | n/a | 0 / month | 0 sustained |
| Circuit breaker trip-to-offline latency | n/a | ≤2s | ≤1s |
| Retry backoff jitter compliance | n/a | 100% | 100% + <5% deviation |
| Idempotency coverage (write endpoints) | n/a | 100% | 100% + audit log |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Sync property tests reveal deep schema issue | Med | Phase 4 budgets 25% buffer; schema fixes land as new migrations (R2) |
| Chaos harness masks real bugs by being too deterministic | Low | Seeded + random modes; both must pass |
| Retry storms during production incident | Med | Backoff tested under load; hard cap of 5 retries |
| Idempotency key collisions on distributed clients | Low | Use UUID4 request IDs; collision impossible at scale |

## Dependencies & Sequencing

- **Must complete Phase 2** (Architecture Boundaries) first — clean boundaries required for resilience patterns
- **Must complete Phase 3** (Performance Budgets) first — perf data informs retry budgets
- **Can run in parallel** with Phase 5 (AI) — independent systems
- **Must complete before Phase 8** (Scale) — scale testing requires resilience baseline

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 4.1 (invariants doc):** Create questerix-student-app/docs/sync/INVARIANTS.md documenting the 4 core guarantees (monotonic timestamps, idempotent replay, deterministic conflict resolution, vector clocks). Reference the actual sync implementation once it exists.
