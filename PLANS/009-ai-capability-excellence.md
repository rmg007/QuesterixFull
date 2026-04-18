# 009 — AI Capability Depth Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 8
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

AI capability depth excellence means every AI path is typed, cached, budgeted by token/cost, replayable from a captured transcript, and has a deterministic fallback. Beyond perfection = AI cost/DAU published with a ceiling alarm, p95 latency ≤1200ms cached / ≤3500ms cold, every prod failure becomes a fixture for offline replay, prompt injection is fuzz-tested with 100 adversarial fixtures, and AI unavailability triggers a rules-based fallback that returns valid (if less rich) responses.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/ (AI hint/feedback features), Questerix/supabase/functions/ (AI edge functions), packages/core/ (AI types + contracts)
- **OUT:** help-docs, landing-pages, admin-specific AI features
- **Respects:** R3 (RLS on new tables), R5 (targeted test paths), R6 (no live AI calls in tests), R8 (no secrets), R9 (master only)

## Phases & Workstreams

### Workstream 5.1 — Typed AI contracts
- **Goal:** Every AI call has a Zod schema; no `any` or `dynamic` at boundaries.
- **Target files:** Questerix/packages/core/src/types/ai/ (new folder), Zod schemas; Dart codegen via Phase 2 plumbing
- **Key deliverables:**
  - Zod schemas for: hint request/response, feedback request/response, explanation request/response, etc.
  - Propagated to Dart via codegen (Phase 2 WS 2.3)
  - Generated files committed; CI verifies re-run produces no diff
  - Every AI call validated against schema on input + output
- **Acceptance gate:** No `any` or `dynamic` in AI boundary types; codegen audit passes

### Workstream 5.2 — Replay harness
- **Goal:** Every prod AI failure (sampled) becomes a fixture; reruns offline.
- **Target files:** questerix-student-app/test/ai/replay/ (new folder), fixture dir (AI call + response pairs)
- **Key deliverables:**
  - Fixture format: request JSON, response JSON, expected latency, cost tokens
  - 50+ fixtures (sampled from last 30 days of prod logs)
  - Harness reruns each fixture; asserts response matches expected shape
  - All fixtures passing (no live API calls per R6)
  - Captured on errors and edge cases
- **Acceptance gate:** 50 fixtures passing; zero fixture flakes

### Workstream 5.3 — Cost ceiling + alarm
- **Goal:** Published budget per DAU; alarm on breach.
- **Target files:** Questerix/supabase/functions/ (cost-tracking middleware), AI cost view, alerts
- **Key deliverables:**
  - Every AI call tagged: user_id, feature, estimated_tokens, model
  - View: ai_cost_per_dau (7-day rolling average)
  - Published budget (e.g., $0.02 / DAU / day)
  - Alarm fires if rolling 7-day cost/DAU exceeds budget
  - Cost ceiling alarm wired to #quality Slack channel
- **Acceptance gate:** Cost/DAU published in docs; alarm tested in drill

### Workstream 5.4 — Cache layer
- **Goal:** Content-addressed cache; ≥30% hit rate within 14 days.
- **Target files:** Questerix/supabase/functions/ai-cache/ (new folder), cache store (Supabase table), test
- **Key deliverables:**
  - Cache key: hash(prompt, model, params)
  - Cache store: request_hash, response, created_at, hit_count
  - Hit-count tracking per cache entry
  - 30-day TTL; old entries pruned
  - Test: warm cache, assert ≥30% hit rate on repeated hints
- **Acceptance gate:** ≥30% hit rate for hint/feedback calls within 14 days; latency <500ms on cache hit

### Workstream 5.5 — Deterministic fallback
- **Goal:** When AI unavailable, rules-based fallback returns valid response.
- **Target files:** questerix-student-app/lib/src/features/<feature>/domain/ai_fallback.dart (new, per feature)
- **Key deliverables:**
  - Hint fallback: return N random example solutions from DB
  - Feedback fallback: return template feedback (e.g., "Try reviewing step X")
  - Explanation fallback: return definition of key term from curriculum
  - No user-visible error when AI down (chaos test forces AI-down for 1h)
  - Test: chaos forces AI unavailable, verifies fallback returned
- **Acceptance gate:** Chaos test in Phase 4 forces AI-down for 1h; no user-visible error

### Workstream 5.6 — Prompt-injection & safety tests
- **Goal:** 100 adversarial fixtures; all blocked or sanitized.
- **Target files:** Questerix/supabase/tests/ai_safety/ (new folder), fixtures.yaml
- **Key deliverables:**
  - 100 adversarial prompts (injection, jailbreak, extraction attempts)
  - Prompt sanitization: check for prompt keywords, filter HTML tags, truncate length
  - Guard: check response for suspicious patterns (API keys, instructions, mode switches)
  - All 100 fixtures pass (blocked or sanitized)
  - Nightly CI run
- **Acceptance gate:** 100 fixtures passing; zero false-positives in production

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| AI boundary type coverage | n/a (no typed AI) | 100% | 100% + codegen audit |
| Replay fixture count | 0 | 50 | 100+ from last 30 days prod |
| Cache hit rate | n/a | 20% | ≥30% |
| AI p95 latency (cached) | n/a | ≤2000ms | ≤1200ms |
| AI p95 latency (cold) | n/a | ≤5000ms | ≤3500ms |
| AI cost/DAU trending | unpublished | published + alarmed | within published budget 30 days |
| Fallback coverage (features) | 0% | 100% | 100% + chaos-tested |
| Prompt-injection fuzz coverage | 0 | 50 fixtures | 100 fixtures |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| AI cost/DAU overruns budget during replay harness dev | Low | All replay is offline (R6); live cost gated by alarm before release |
| Cache invalidation misses stale data | Med | Cache keys include model version; manual cache-clear procedure on model upgrade |
| Fallback is too different from real AI (confuses users) | Med | A/B test fallback before full launch; monitor user completion rate difference |
| Prompt injection test becomes false-positive factory | Med | Start with sampling; escalate to 100% only when validated |
| Codegen (TS → Dart) AI types introduce drift | High | CI step fails if generated files aren't checked in; compare on every PR |

## Dependencies & Sequencing

- **Must complete Phase 4** (Resilience & Offline/Sync) first — sync stability required before adding AI complexity
- **Can run in parallel** with Phase 6 (Accessibility), Phase 7 (Observability)
- **Must complete before Phase 8** (Scale) — cost controls required before scale testing

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 5.1 (typed AI contracts):** Create Questerix/packages/core/src/types/ai/ folder with Zod schemas for hint request/response and feedback request/response. Generate Dart codecs via Phase 2 codegen plumbing and verify no drift.
