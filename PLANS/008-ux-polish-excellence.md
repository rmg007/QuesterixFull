# 008 — UX Polish Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 7
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

UX polish excellence means interaction fidelity is complete: haptics on intent, transitions are smooth and purpose-driven, every screen has skeleton/empty/error/offline states, and there are no "dead" or unresponsive UI states. Beyond perfection = sub-300ms tap feedback, 60fps transitions, every route has all five states tested, haptics scoped to confirmed intent, and offline state is a feature (not a failure mode).

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/ (all UI, interactions, animations, feedback, states); Questerix/packages/core/ (shared design tokens, animation utilities)
- **OUT:** help-docs, landing-pages, admin-specific UX work
- **Respects:** R5 (targeted test paths), R7 (theme tokens), R9 (master only)

## Phases & Workstreams

### Workstream 6.3 (from Phase 6) — Five-state audit per screen (link to dimension 7)
- **Goal:** Every route has loaded, skeleton, empty, error, offline visual states.
- **Target files:** questerix-student-app/test/widget/<feature>/states_test.dart (per feature)
- **Key deliverables:**
  - Golden tests for all five states per route
  - 100% route coverage with tests
  - No placeholder UI; each state is intentional design
  - Offline state shows cached data or graceful fallback
  - Error state shows actionable message + retry
  - Empty state shows helpful guidance
  - Loading skeleton matches final layout to prevent jank
- **Acceptance gate:** 100% route coverage; zero routes skip a state without waiver

### Workstream PS-1 — Tap feedback & haptic polish
- **Goal:** <300ms feedback on user action; haptics confirm intent.
- **Target files:** questerix-student-app/lib/src/core/feedback/ (new folder: haptic_manager.dart, feedback_provider.dart)
- **Key deliverables:**
  - Tap feedback: visual (highlight), haptic (light impact), and optional sound
  - Tap-to-feedback latency measured and budgeted at <300ms
  - Haptics scoped to high-intent actions (form submit, correct answer, confirmation)
  - Avoid haptics on hover or casual navigation
  - Platform-specific haptics (iOS pattern, Android pattern)
  - Test: force 500ms delay, verify UI feedback appears within 300ms
- **Acceptance gate:** <300ms tap-to-feedback on Pixel 4a + iPhone 12; test green

### Workstream PS-2 — Transition & animation audit
- **Goal:** Smooth, purposeful transitions; no jank.
- **Target files:** questerix-student-app/lib/src/core/theme/animations.dart (shared), lib/src/features/<feature>/presentation/screens/*
- **Key deliverables:**
  - Route transitions: 300-400ms Curves.easeOutCubic
  - List item animations: staggered fade-in (100ms apart)
  - Micro-interactions: success checkmark (500ms), error shake (300ms)
  - All animations 60fps on mid-tier Android
  - Audit document: every animation mapped to intent
  - Reduce-motion: decorative animations disabled
- **Acceptance gate:** All transitions 60fps on Pixel 4a in CI; animation audit merged

### Workstream PS-3 — Empty state experiences
- **Goal:** Empty states guide user to next action.
- **Target files:** questerix-student-app/lib/src/core/widgets/empty_state.dart (shared), per-screen overrides
- **Key deliverables:**
  - Empty state design language: icon, message, CTA
  - 100% of list/grid routes have empty state
  - Messages are friendly and actionable
  - CTA links to relevant feature (e.g., "Start your first quest")
- **Acceptance gate:** 100% route coverage; UX review of copy/icon/CTA

### Workstream PS-4 — Error state experiences
- **Goal:** Users understand what went wrong and how to recover.
- **Target files:** questerix-student-app/lib/src/core/widgets/error_state.dart (shared), per-screen overrides
- **Key deliverables:**
  - Error state design: icon, user-friendly message (not stack trace), retry CTA
  - 100% of network/DB/AI operations have error state
  - Messages explain what happened (not technical jargon)
  - Retry is always available
  - Test: force error, verify state rendered correctly
- **Acceptance gate:** 100% operation coverage; UX review of messages

### Workstream PS-5 — Offline state experiences
- **Goal:** Offline is a feature, not a failure mode.
- **Target files:** questerix-student-app/lib/src/core/connectivity/ (connectivity provider), per-screen implementations
- **Key deliverables:**
  - Offline banner: subtle, informative, non-blocking
  - Offline data: show cached data with "last updated X hours ago"
  - Offline write: queue operations; show "syncing" status on successful local write
  - Offline read: graceful degradation (e.g., show 20 recent items instead of paginating)
  - Test: toggle connectivity, verify states transition smoothly
- **Acceptance gate:** All routes handle offline gracefully; connectivity test green

### Workstream PS-6 — Loading skeleton design
- **Goal:** Loading skeletons match final layout; no jank on complete.
- **Target files:** questerix-student-app/lib/src/core/widgets/skeleton.dart (shared), per-route implementations
- **Key deliverables:**
  - Skeleton layout matches data layout exactly
  - 200-400ms animation (shimmer or fade)
  - Skeleton duration bounded: max 2s before showing error/empty
  - Smooth transition from skeleton to data (no layout shift)
- **Acceptance gate:** Skeletons match final layout; <0 layout shift CLS on animation

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Tap-to-feedback latency (p95) | n/a | <400ms | <300ms |
| Transition smoothness (fps) | unknown | 60fps | 60fps sustained, 0 jank |
| Five-state coverage per route | unknown | 80% | 100% |
| Route transition duration | n/a | 300-500ms | 300-400ms target |
| Animation audit coverage | 0% | 100% | 100% + intent mapping |
| Offline state coverage | unknown | 100% | 100% + sync status shown |
| Empty state message quality | n/a | reviewed | reviewed + A/B tested |
| Skeleton-to-content layout shift | n/a | <0.1 CLS | 0 CLS |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Animations cause jank on older devices | Med | Test on Pixel 4a (2019 baseline); profile with DevTools |
| Haptic feedback inconsistent across platforms | Low | Platform-specific implementation tested on both iOS + Android CI |
| Offline state confuses users (cached data stale) | Med | Always show "last updated X time ago" on cached data |
| Loading skeleton duration unbounded | Med | Max 2s skeleton before error/empty; measured per route |
| Tap feedback latency regresses with feature bloat | Med | Budget tracked in golden-paths; perf gate enforces |

## Dependencies & Sequencing

- **Must complete Phase 2** (Architecture) first — clean code enables UX work
- **Can run in parallel** with Phase 5 (AI), Phase 8 (Scale)
- **Builds on Phase 6** (Accessibility) — five-state audit (6.3) is shared

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS PS-1 (tap feedback):** Create questerix-student-app/lib/src/core/feedback/haptic_manager.dart with haptic feedback for high-intent actions. Test <300ms feedback latency on Pixel 4a emulator and add to perf gate.
