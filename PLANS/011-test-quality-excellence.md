# 011 — Test Quality Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 10
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Test quality excellence is not a coverage number—it's mutation score ≥60% on critical paths, property-based tests on sync and scoring, and contract tests at every boundary. Beyond perfection = mutation score ≥70% on core features, every public API has contract tests, every sync resolver has property-based tests, and test flakes are zero.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/test/, integration_test/, lib/src/core (core logic); Questerix/packages/core/ (shared code tests), supabase/tests/
- **OUT:** help-docs, landing-pages, admin-specific test work
- **Respects:** R5 (targeted test paths, no full `flutter test`), R6 (no live AI in tests), R10 (integration tests on real DB)

## Phases & Workstreams

### Workstream Phase-0 — Mutation score baseline
- **Goal:** Measure mutation score on critical paths; set targets.
- **Target files:** questerix-student-app/scripts/mutation_test.dart (new), packages/core/ mutation tests
- **Key deliverables:**
  - Run mutation testing on core/ and critical features
  - Generate mutation report (survived mutations = test gaps)
  - Baseline recorded: mutation score on each module
  - Targets set: ≥60% on critical paths, ≥50% on others
- **Acceptance gate:** Baseline recorded in baseline.json; targets committed

### Workstream TQ-1 — Contract tests for public APIs
- **Goal:** Every public API (Dart, TS) has contract tests.
- **Target files:** questerix-student-app/test/contracts/; Questerix/packages/core/src/**/*.contract.test.ts (new)
- **Key deliverables:**
  - Contract test per public function/class
  - Test: input examples → assert output shape + invariants
  - Examples include: happy path, empty input, boundary values
  - 100% coverage of public APIs
  - Test failures block merges
- **Acceptance gate:** 100% of public APIs have contract tests; all passing

### Workstream TQ-2 — Property-based tests on core logic
- **Goal:** Test invariants hold across random inputs.
- **Target files:** questerix-student-app/test/properties/ (new), Questerix/packages/core/src/**/*.property.test.ts (new)
- **Key deliverables:**
  - Property-based tests for: sync resolvers, scoring algorithms, offline-first logic
  - Generators for: valid quest states, user answers, timestamps
  - 100+ runs per property
  - All pass without flake
- **Acceptance gate:** 100+ runs per property; zero flakes

### Workstream TQ-3 — Fuzz tests for parser/validator logic
- **Goal:** Test robustness against malformed input.
- **Target files:** Questerix/supabase/tests/fuzz/ (new for RLS/edge-function inputs)
- **Key deliverables:**
  - Fuzz test for: Zod schema parsing, AI prompt sanitization, RLS edge cases
  - 1000+ random inputs per fuzz target
  - Assert no panics or uncaught errors
- **Acceptance gate:** 1000+ fuzzing runs; zero crashes

### Workstream TQ-4 — Widget & golden tests (5-state audit)
- **Goal:** Every route's 5 states (loaded, skeleton, empty, error, offline) are golden-tested.
- **Target files:** questerix-student-app/test/widget/<feature>/states_test.dart (per feature)
- **Key deliverables:**
  - Golden tests for all 5 states per route
  - 100% route coverage
  - No layout shift on state transition
  - Golden diffs caught by CI
- **Acceptance gate:** 100% route coverage; zero regressions in goldens

### Workstream TQ-5 — Integration tests with seeded ephemeral DB
- **Goal:** Test app against real Supabase instance (ephemeral per test run).
- **Target files:** questerix-student-app/integration_test/; Questerix/supabase/migrations/ (seeded)
- **Key deliverables:**
  - Integration test harness: spin up ephemeral Supabase, seed with test data, run app flow
  - Test flows: full sync loop, offline→online, AI hint request, scoring
  - All tests pass on both platforms (Android + iOS CI)
  - No mocks; real DB interaction (R10)
- **Acceptance gate:** Integration tests green on Android + iOS CI

### Workstream TQ-6 — Performance regression tests
- **Goal:** Catch perf regressions on golden paths.
- **Target files:** questerix-student-app/test/performance/ (new), linked to WS 3.6 perf gate
- **Key deliverables:**
  - Benchmark test for each golden path (cold-start, login, sync, AI hint, etc.)
  - Measure: latency p50/p95/p99, memory, CPU
  - CI gate: fails if p95 regresses >10% vs. rolling 7-day median
  - Results published to dashboards
- **Acceptance gate:** Perf gate stable for 7 days; zero false-positives

### Workstream TQ-7 — Mutation testing on critical paths
- **Goal:** Mutation score ≥60% on core logic.
- **Target files:** questerix-student-app/test/ (mutation tests added per module)
- **Key deliverables:**
  - Run mutation testing: flip conditionals, remove statements, change constants
  - Assert test suite kills mutations (detects the change)
  - Survived mutations indicate test gaps
  - Mutation report per PR: highlighted modules below threshold
- **Acceptance gate:** Core modules ≥60% mutation score; improvement tracked quarterly

### Workstream TQ-8 — Test flake elimination
- **Goal:** Zero test flakes; all tests deterministic.
- **Target files:** test infrastructure, CI config (.github/workflows/)
- **Key deliverables:**
  - Identify flaky tests (rerun detection)
  - Root cause: timing, randomness, shared state, network
  - Fix or quarantine; new flakes block merges
  - Nightly flake-check: run all tests 3× in parallel
  - Flake-free streak tracked
- **Acceptance gate:** 30-day flake-free streak; zero new flakes per month

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Mutation score (core) | unknown (measure P0) | ≥50% | ≥60% |
| Mutation score (critical paths) | unknown | ≥55% | ≥70% |
| Public API contract coverage | 0% | 100% | 100% + audit |
| Property-based test count | 0 | 20+ | 50+ |
| Test flake frequency | unknown | 0 / month | 0 / quarter |
| Integration test coverage (flows) | n/a | ≥5 | ≥10 |
| Golden test route coverage | unknown | 80% | 100% |
| Perf regression catch rate | n/a | 100% | 100% + <5% false-positive |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Mutation testing tools slow down CI significantly | Med | Run on subset of critical paths during PR; nightly full run |
| Property-based tests generate unbounded inputs (timeout) | Med | Generators have size limits; timeout per test = 5s |
| Golden test diffs are brittle (flake on minor rendering changes) | Med | Golden diffs use pixel-match with ±5px tolerance; review before commit |
| Ephemeral DB per integration test is slow | Med | Parallel test execution with independent DB instances |
| Mutation score targets too high, cause burnout | Low | Targets set per module; critical paths prioritized; quarterly reviews |

## Dependencies & Sequencing

- **Must complete Phase 0** (Foundation) first — baselines required
- **Can run in parallel** with all other phases — test infrastructure enables them
- **Per-phase dependencies:** each phase's tests inform its metrics

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**Workstream Phase-0 (mutation baseline):** Create questerix-student-app/scripts/mutation_test.dart that runs mutation testing on questerix-student-app/lib/src/core/ and records baseline mutation score per module. Commit baseline to baseline.json.
