# 006 — Security Excellence Plan

> **Type:** [FEATURE] · **Status:** ACTIVE · **Dimension:** 5
> **Scope:** Questerix/ + questerix-student-app/ only; respects all 10 Critical Rules
> **Linked to master plan:** PLANS/001-beyond-perfection-roadmap.md

## Purpose & North Star

Security excellence means zero HIGH/CRITICAL CVEs, RLS policies are fuzz-tested and empirically proven for every role, secrets are rotated quarterly and drift-audited, and every feature has a documented threat model. Beyond perfection = 0 CVEs sustained for 90 days, 100% of RLS policies pass fuzz harness, SBOM is signed and verifiable per build, and threat models are linked from every new feature PR.

## Scope Lock (inherited from master)

- **IN:** Questerix/ (admin-panel CVE remediation per R1, packages/core/, supabase/ RLS + migrations); questerix-student-app/ (certificate pinning, client security)
- **OUT:** help-docs, landing-pages, admin-feature work (R1 freeze applies)
- **Respects:** R1 (admin bugfix-only), R2 (additive migrations), R3 (RLS required), R8 (no secrets), R9 (master only)

## Phases & Workstreams

### Workstream 1.1 — Admin-panel CVE remediation (R1)
- **Goal:** 11 → 0 HIGH/CRIT vulns; no new features.
- **Target files:** Questerix/admin-panel/package.json, package-lock.json; npm audit must return 0 for 14 consecutive days
- **Key deliverables:**
  - Patch-level bumps only
  - rules-report.json proves R1 respected (zero source-file diffs unless bugfix required)
  - Playwright smoke test per bump
- **Acceptance gate:** npm audit --audit-level=high returns 0 for 14 consecutive days; coverage doesn't regress

### Workstream 1.2 — Supabase RLS fuzz harness
- **Goal:** Empirically prove every policy for every role.
- **Target files:** Questerix/supabase/tests/rls_fuzz/ (new folder: generator.py, runner.py, expected.yaml)
- **Key deliverables:**
  - pgTAP + Python test enumerating (table × operation × role × tenant × deleted_at)
  - Assert expected allow/deny against seeded DB
  - 100% of existing tables pass
  - New table without policies fails CI (R3 enforced)
- **Acceptance gate:** 100% of tables pass; CI enforces on every migration

### Workstream 1.3 — Renovate + Dependabot unification
- **Goal:** One policy; tiered auto-merge.
- **Target files:** renovate.json (root), .github/dependabot.yml (per-project)
- **Key deliverables:**
  - Grouped minor PRs weekly
  - Security PRs daily
  - Auto-merge patch-level with green CI + rules-report
  - deps_behind drops from 19 to ≤5 within 30 days
- **Acceptance gate:** deps_behind ≤5 within 30 days; sustained ≤5

### Workstream 1.4 — SBOM + signed builds
- **Goal:** Every release has a machine-readable bill of materials, signed.
- **Target files:** Questerix/scripts/sbom.sh (new), questerix-student-app/scripts/sbom.sh (new), CI release workflow
- **Key deliverables:**
  - CycloneDX SBOM generated per build
  - Uploaded as build artifact
  - Signed with project key
  - SBOM verifiable on three consecutive releases
- **Acceptance gate:** SBOM present and verifiable on three releases

### Workstream 1.5 — Secret rotation runbook + CI scan
- **Goal:** Quarterly rotations; gitleaks ensures no leaks.
- **Target files:** Questerix/docs/runbooks/secret-rotation.md (new); gitleaks in CI
- **Key deliverables:**
  - Quarterly rotation drill with documented steps
  - Last-verified date in runbook frontmatter
  - CI asserts date ≤90 days old
  - gitleaks scan clean on entire history
  - Calendar-driven GitHub Issue template for next rotation
- **Acceptance gate:** gitleaks scan clean; drill runs successfully once

### Workstream 1.6 — Student app certificate pinning + MITM replay test
- **Goal:** Prevent MITM attacks; verify pinning works.
- **Target files:** questerix-student-app/lib/src/core/network/pinned_client.dart (new), integration_test/security_pinning_test.dart (new)
- **Key deliverables:**
  - Pinned HTTP client used by every outbound call
  - Integration test uses local proxy with rogue cert
  - Test asserts rejection
  - Test green on Android + iOS CI
- **Acceptance gate:** Test green on both platforms; pinning enforced in all network calls

### Workstream 1.7 — Threat model doc per feature area
- **Goal:** STRIDE-style threat model per feature; mitigations mapped.
- **Target files:** Questerix/docs/threat-model/ (new folder: auth.md, sync.md, ai.md, storage.md, rate-limit.md)
- **Key deliverables:**
  - 5 threat model docs (auth, sync, AI, storage, rate-limit)
  - Each: assets, threats, mitigations, links to fuzz tests
  - New feature PRs reference relevant area or create new doc
  - Reviewed quarterly
- **Acceptance gate:** 5 docs merged; every new feature PR references threat model

## Dimension-Specific Success Metrics

| Metric | Baseline | Production-Ready | Beyond-Perfection |
|--------|----------|------------------|-------------------|
| Admin npm HIGH/CRIT vulns | 11 | 0 | 0 sustained 90 days |
| RLS fuzz coverage | n/a | 100% | 100% + annual triage |
| Dependencies behind | 19 | ≤5 | 0 critical, ≤5 minor |
| SBOM verifiability | no | yes | 100% of releases |
| Secret rotation cadence | n/a | quarterly | quarterly + audit log |
| Certificate pinning coverage | 0% | 100% | 100% + MITM drill quarterly |
| Threat model coverage | n/a | 5 areas | 5+ areas + annual review |

## Dimension-Specific Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| CVE fix requires call-site change breaking R1 | Med | Separate plan for architectural fixes; Phase 1 handles only compatible patches |
| RLS fuzz false-positives block migrations | Med | Fuzz harness advisory for first 14 days, then enforcing; triage queue |
| Transitive dependency break on minor bump | Med | Every bump runs Playwright smoke; breaking change → separate plan |
| Secret rotation runbook goes stale | Med | Rotation is calendarized; runbook has "last verified" field CI checks ≤90 days |
| Certificate pinning breaks on cert rotation | Low | Pinning includes backup cert; rotation drilled quarterly |

## Dependencies & Sequencing

- **Must complete Phase 0** (Foundation & Instrumentation) first — baseline metrics required
- **Can run in parallel** with Phase 2 (Architecture), Phase 3 (Performance)
- **Must complete before Phase 8** (Scale) — security baseline required

## Decision Log

Format: `YYYY-MM-DD · [WS#] · Decision · Rationale · Alternatives`

| Date | Phase/WS | Decision | Rationale | Alternatives |
|------|----------|----------|-----------|--------------|
| — | — | — | — | — |

## Next Action

**WS 1.1 (CVE remediation):** Run `npm audit --audit-level=high` in Questerix/admin-panel/. Identify the 11 HIGH/CRIT vulns and create a PR that upgrades packages to patch versions that fix them. Verify no source-file changes required via rules-report.
