# 007 — Accessibility Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 6
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Accessibility excellence means WCAG 2.2 AA is enforced in CI (contrast, touch targets, screen-reader labels, focus order), and zero regression ships. Beyond perfection = every route has all five states (loaded, skeleton, empty, error, offline) with tests, haptics are scoped to intent-confirmed actions only, dynamic type at 2.0× scales without overflow, RTL is functional, and copy is grade-level appropriate.

## Scope Lock (inherited from master)

- **IN:** questerix-student-app/ (all UI, l10n, theme, tests); Questerix/packages/core/ (shared theme tokens)
- **OUT:** help-docs, landing-pages, admin-specific a11y work (R1 scope limited)
- **Respects:** R5 (targeted test paths), R7 (theme tokens only), R9 (master only)

## Phases & Workstreams

### Workstream 6.1 — A11y lint in CI
- **Goal:** Enforce contrast, touch targets, semantic labels.
- **Target files:** questerix-student-app/scripts/a11y_lint.dart (new), test/accessibility/ (new folder)
- **Key deliverables:**
  - Contrast checker on every theme token combination
  - 48dp minimum touch target asserted per widget
  - Semantic-label presence asserted for every GestureDetector/InkWell/IconButton
  - Zero violations on CI
  - Staged warnings-first rollout for existing violations
  - Opt-out marker documented for decorative elements
- **Acceptance gate:** Zero violations on CI; all existing violations fixed

### Workstream 6.2 — Screen-reader semantics tests
- **Goal:** Every route has correct focus order and dynamic announcements.
- **Target files:** questerix-student-app/test/accessibility/semantics_test.dart (new)
- **Key deliverables:**
  - Every route walked with SemanticsHandle
  - Focus order validated per design spec
  - Dynamic announcements (e.g., "correct answer") verified
  - Integration with screen reader (accessibility inspector)
- **Acceptance gate:** Passes on all routes in student app

### Workstream 6.3 — Five-state audit per screen
- **Goal:** Every route has loaded, skeleton, empty, error, offline states with golden tests.
- **Target files:** questerix-student-app/test/widget/<feature>/states_test.dart (per feature)
- **Key deliverables:**
  - Golden tests for all five states
  - 100% route coverage
  - Waiver required to skip a state (documented)
  - No overflow or clipped UI in golden diffs
- **Acceptance gate:** 100% route coverage; zero waivers without justification

### Workstream 6.4 — Theme-token enforcement (R7)
- **Goal:** No hardcoded colors; all colors via theme.
- **Target files:** Custom analyzer rule in analysis_options.yaml; lib/src/core/theme/ (tokens)
- **Key deliverables:**
  - Hex literals outside theme folder fail CI
  - All colors referenced via Theme.of(context).extension<AppColors>() or equivalent
  - A11y-aware theme tokens (contrast-compliant)
- **Acceptance gate:** Zero violations; theme audit tool passes

### Workstream 6.5 — Haptic & motion audit
- **Goal:** Haptics intentional; decorative animations respect reduce-motion.
- **Target files:** questerix-student-app/docs/ux/motion-audit.md (new), lib/src/core/theme/ (reduced-motion provider)
- **Key deliverables:**
  - Map of every animation: essential vs. decorative
  - Reduce-motion OS setting disables decorative animations
  - Haptics scoped to confirmed-intent actions only (e.g., form submission, not hover)
  - Widget test: toggling reduce-motion eliminates non-essential animation
- **Acceptance gate:** Toggling reduce-motion eliminates all non-essential animation

### Workstream 6.6 — Dynamic type & RTL pass
- **Goal:** App renders correctly at 2.0× text scale; RTL Arabic works.
- **Target files:** test/l10n/ (locale goldens)
- **Key deliverables:**
  - Goldens at text-scale 1.0×, 1.5×, 2.0× for each locale
  - RTL Arabic locale smoke test
  - No overflow or clipped UI
  - RTL-safe layout (Directionality wrappers)
- **Acceptance gate:** No overflow in golden diffs; RTL test passes

### Workstream 6.7 — Copy review & tone consistency
- **Goal:** Grade-level appropriate copy; consistent voice.
- **Target files:** questerix-student-app/lib/l10n/app_en.arb, UX copy constants
- **Key deliverables:**
  - Copy review checklist (tone, reading level, clarity)
  - Automated reading-level check on new strings
  - Error messages use supportive tone
  - Consistent voice across features
- **Acceptance gate:** Copy review checklist merged; reading-level CI check enforced

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| WCAG 2.2 AA violations | n/a | 0 new in CI | 0 app-wide |
| Touch target minimum (48dp) compliance | unknown | 100% | 100% + audit log |
| Screen-reader label coverage | n/a | 100% | 100% + focus order tests |
| Five-state coverage per route | unknown | 80% | 100% |
| Theme-token compliance (R7) | 0% | 100% | 100% sustained |
| Dynamic type render correctness | n/a | 100% @ 2.0× | 100% @ 3.0× |
| Reduce-motion compliance | unknown | 100% | 100% + haptic audit |
| RTL locale support | none | Arabic + 1 other | 3+ locales tested |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| A11y CI noisy, teams learn to ignore | Med | Start with warnings, promote to errors at Phase 6 exit; every failure linked to fix playbook |
| False-positives in contrast for decorative elements | Med | Opt-out marker documented; reviewer trains team on usage |
| Dynamic type overflow on dense screens | Med | Pre-test at 2.0× during design review; golden diffs catch regressions |
| RTL layout breaks on legacy screens | Low | RTL test runs on all platforms; smoke test required |
| Reading-level check rejects valid domain terms | Med | Allow-list for domain vocabulary; updated quarterly |

## Dependencies & Sequencing

- **Must complete Phase 2** (Architecture Boundaries) first — clean code structure eases a11y work
- **Can run in parallel** with Phase 5 (AI), Phase 8 (Scale)
- **Must complete before Phase 9** (Release Engineering) — a11y gate releases

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 6.1 (a11y lint):** Create questerix-student-app/scripts/a11y_lint.dart using custom analyzer rules to check contrast on all theme token combinations and minimum touch target sizes. Run it on the student app and report violations.
