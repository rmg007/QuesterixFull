# 005 — Observability Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 4
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Observability excellence means structured traces, metrics, and logs are correlated by a single request ID across app → Supabase → edge functions, and no "what happened to this user?" question takes >5 minutes to answer. Beyond perfection = correlation ID threads through 100% of WES sessions, error-budget policy is published and enforced, 3 automated remediations are wired (stuck-sync auto-reset, cache-miss spike warmup, schema-version mismatch refresh), and session replay (privacy-safe) links event timelines for every user report.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/lib/src/core/observability/; Questerix/supabase/functions/ (correlation plumbing); dashboards and alerting
- **OUT:** help-docs, landing-pages, admin-specific observability
- **Respects:** R1 (admin bugfix), R3 (RLS on new tables), R6 (no live AI in tests), R8 (no secrets), R9 (master only)

## Phases & Workstreams

### Workstream 7.1 — Correlation ID end-to-end
- **Goal:** Single ID threads through app → edge → DB logs.
- **Target files:** questerix-student-app/lib/src/core/observability/correlation.dart (new); all Supabase client wrappers; edge functions
- **Key deliverables:**
  - Header x-correlation-id injected at client
  - Forwarded through edge functions
  - Logged in pg via set_config
  - Visible in all WES event logs
  - Test session's ID appears in client + edge + DB logs
- **Acceptance gate:** Single ID visible end-to-end in a captured trace for 100% of WES sessions

### Workstream 7.2 — Error budget policy
- **Goal:** Publish and enforce error budgets; breach pauses feature work.
- **Target files:** Questerix/docs/error-budget.md, questerix-student-app/docs/error-budget.md (new)
- **Key deliverables:**
  - Error budget policy (e.g., 99.5% uptime = 3.6h / month downtime)
  - WES error rate as primary metric
  - Breach defined: WES rate drops below threshold for 2 consecutive days
  - Breach pauses feature work automatically via CI label
  - Weekly review of budget burn
- **Acceptance gate:** Policy docs merged; CI integration tested

### Workstream 7.3 — Three automated remediations
- **Goal:** Self-healing for common failure modes.
- **Target files:** Questerix/supabase/functions/ (remediation functions), questerix-student-app/lib/src/core/observability/remediations.dart
- **Key deliverables:**
  - (a) Stuck-sync auto-reset: after 5 failed pushes, force full re-sync + alert
  - (b) AI cache-miss spike warmup: detect spike in cache misses, pre-warm cache
  - (c) Schema-version mismatch: detect mismatch, force client refresh
  - Each has: test, runbook, "times fired" counter
- **Acceptance gate:** Each remediation has test + runbook; log entry per fire

### Workstream 7.4 — Session replay (privacy-safe)
- **Goal:** Any user report resolvable in ≤5 minutes via replay.
- **Target files:** Questerix/supabase/migrations/<date>_session_events.sql (new), event schema, replay viewer
- **Key deliverables:**
  - WES session IDs link to structured event timelines (not pixel replay)
  - Session events: navigation, sync events, AI calls, errors, performance markers
  - Replay viewer: play event timeline with time scrubbing
  - Integration with user-report flow: "view session" button
- **Acceptance gate:** 50 sessions with complete event timelines; <5 min to reproduce reported issue

### Workstream 7.5 — On-call runbooks for top 10 alerts
- **Goal:** Every alert in Phase 0 dashboards has a runbook.
- **Target files:** Questerix/docs/runbooks/alert-*.md (10 files)
- **Key deliverables:**
  - Runbook per alert: symptoms, root-cause queries, mitigation steps, escalation path
  - Examples: high error rate, sync lag spike, AI cost spike, cold-start regression
  - Runbooks linked from dashboard alert definitions
  - Updated quarterly or on incident
- **Acceptance gate:** 10 runbooks merged; every dashboard alert links to one

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Correlation-ID end-to-end coverage | no | yes | 100% of WES sessions |
| Error-budget compliance | n/a | 99.5% uptime / month | 0 breaches / quarter |
| Automated remediation coverage | 0 | 3 types | 5+ types |
| Session-replay latency (issue → root cause) | n/a | ≤15 min | ≤5 min |
| Alert runbook coverage | n/a | 100% | 100% + annual audit |
| MTTR (mean time to resolution) | n/a | ≤30 min | ≤15 min |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Correlation ID generation overhead on perf | Low | UUID4 generation is <1μs; minimal impact |
| Error budget breach due to transient spike | Med | Breach requires 2 consecutive days; transients <1 day exempt |
| Remediation false-positives auto-fire | Med | Each remediation has threshold (e.g., 5 consecutive failures); test under load |
| Session replay reveals sensitive data | High | Event schema reviewed against data-classification doc; PII redacted |
| Runbook escalation chains go stale | Med | Runbooks have "last verified" date; CI checks ≤90 days old |

## Dependencies & Sequencing

- **Must complete Phase 0** (Foundation & Instrumentation) first — dashboards and WES metric required
- **Must complete Phase 3** (Performance Budgets) first — perf metrics feed observability
- **Can run in parallel** with Phase 5 (AI), Phase 6 (A11y)
- **Must complete before Phase 9** (Release Engineering) — observability gates releases

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 7.1 (correlation ID):** Add x-correlation-id header injection to questerix-student-app/lib/src/core/observability/correlation.dart. Wire it into all Supabase client wrappers (lib/src/core/services/) and test that it flows through to WES events.
