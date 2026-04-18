# 002 — Architecture Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 1
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Architecture excellence means boundaries are enforced by the build, not by convention—a new engineer cannot violate a layer or dependency rule accidentally; the compiler or CI blocks it. Beyond perfection = zero god-files (≤400 lines per file), zero inter-feature imports without explicit barrel exports, zero core-to-feature imports, and a cycle-free provider dependency graph committed to every PR.

## Scope Lock (inherited from master)

- **IN:** Questerix/ (packages/core/, shared infra), questerix-student-app/ (all features, core modules, tests)
- **OUT:** help-docs, landing-pages, new admin features
- **Respects:** R1 (admin bugfix-only), R2 (additive Drift migrations), R4 (QueryBuilder immutability), R9 (master only)

## Phases & Workstreams

### Workstream 2.1 — God-file decomposition (9 → ≤4)
- **Goal:** No file is both data model and orchestration; no feature's rules live in one place.
- **Target files:** questerix-student-app/lib/src/features/ and lib/src/core/services/
- **Key deliverables:**
  - Split top-5 god-files (>500 lines) into data/domain/presentation layers
  - Pure-function extraction; public API preserved
  - Widget/snapshot tests on affected features pass unchanged
  - Analyzer still 0 errors
- **Acceptance gate:** God-file count ≤4; zero behavior regression; analyzer green

### Workstream 2.2 — Import-boundary lint
- **Goal:** Enforce layering by the build, not convention.
- **Target files:** questerix-student-app/analysis_options.yaml (dart_code_metrics), Questerix/packages/core/.eslintrc.cjs
- **Key deliverables:**
  - features/A cannot import features/B except via explicit features/A/public/ barrel
  - core/* cannot import features/*
  - CI lint runs on every PR
- **Acceptance gate:** Zero violations on master; lint enforced in CI

### Workstream 2.3 — packages/core shared-type extraction + codegen
- **Goal:** One source of truth for cross-app types; no hand-sync drift.
- **Target files:** Questerix/packages/core/src/types/, tools/codegen/ (new TS → Dart generator)
- **Key deliverables:**
  - Generator emits Dart classes + JSON codecs from Zod schemas
  - Generated files committed; CI verifies re-run produces no diff
  - One shared enum (e.g. QuestionType) and one shared DTO (e.g. QuestAttempt) flow through codegen
- **Acceptance gate:** CI step `generated-is-fresh` green; zero codegen drift

### Workstream 2.4 — Riverpod provider dependency graph
- **Goal:** Make provider graph visible, cycle-free, and diff-able in PRs.
- **Target files:** questerix-student-app/scripts/provider_graph.dart (new), outputs docs/provider-graph.svg
- **Key deliverables:**
  - Static analysis walks provider definitions, renders a DAG
  - Fails if a cycle is found
  - PRs show graph diff as CI artifact
- **Acceptance gate:** Zero cycles; graph rendered on every PR

### Workstream 2.5 — QueryBuilder immutability lint (R4)
- **Goal:** Make the rule machine-enforced, not memorized.
- **Target files:** Questerix/packages/core/tools/eslint-rules/supabase-query-immutable.js (new)
- **Key deliverables:**
  - Custom ESLint rule flags query.eq(), query.in_(), query.filter(), etc., when return value is discarded
  - Enabled in admin-panel and edge functions
- **Acceptance gate:** CI fails on violation; existing codebase passes

### Workstream 2.6 — packages/core test suite + publishing model
- **Goal:** Core shared code is tested and versioned.
- **Target files:** Questerix/packages/core/src/**/*.test.ts, package.json
- **Key deliverables:**
  - 90% line coverage on shared code
  - Versioned releases via workspace protocol
  - Core tests run separately in CI
- **Acceptance gate:** Core tests pass; consumers pin to a version

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| God-files (>500 lines) | 9 | 4 | 0 |
| Import-boundary violations | n/a (measured in Phase 2) | 0 | 0 sustained |
| Provider cycles | unknown | 0 | 0 + DAG visible per PR |
| Shared-type codegen drift | n/a | 0 | 0 + CI enforced |
| packages/core coverage | n/a | 75% | 90% |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Codegen (TS → Dart) introduces drift | High | CI step fails if generated files aren't checked in or don't match |
| God-file split reveals behavior bugs | Med | Property tests added **before** the split; PR is split-only |
| Import-lint false-positives on shared utilities | Med | Start with warnings, escalate to errors after Phase 2 complete |
| Provider graph regression on new providers | Low | CI check enforces graph regeneration on every PR |

## Dependencies & Sequencing

- **Must complete Phase 0** (Foundation & Instrumentation) first
- **Can run in parallel** with Phase 3 (Performance)
- **Must complete before Phase 4** (Resilience) — clean boundaries required for resilience patterns

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 2.1 (god-file decomposition):** Run `flutter analyze` on questerix-student-app and identify the top-5 files >500 lines via `baseline.sh`. Create a PR that splits the largest one into data/domain/presentation layers, preserving the public API with property tests added **before** the split.
