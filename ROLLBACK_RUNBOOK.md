# Rollback Runbook - Questerix

Use this runbook if a production deployment of the **Question Type Fix** (canonical enum migration) fails or causes regressions.

## Emergency Response Phase (Immediate)

### 1. Revert Supabase Migrations
If the DB schema change (`matching` enum) caused errors in existing code:

1.  **Identify the migration version**:
    `npx supabase migration list --password [db-password]`
2.  **Mark the migration as reverted**:
    `npx supabase migration repair --status reverted 20260328180000`
3.  **Manually remove the value (if necessary and possible)**:
    Note: Postgres doesn't easily allow removing enum values. If needed, you must drop and recreate the type (WARNING: this requires dropping all columns using it first).
    **Recommendation**: Only revert the code if the enum value itself isn't causing DB crashes.

### 2. Rollback Cloudflare Worker
The Worker is the entry point for AI generation.

1.  Navigate to your worker repository.
2.  `wrangler rollback`
3.  Verify the previous version is active in the Cloudflare Dashboard.

### 3. Revert Edge Function
1.  Navigate to `questerix-student-app`.
2.  Check the `supabase/functions/generate-questions` folder.
3.  If you have a backup of the previous `index.ts`, restore it.
4.  `supabase functions deploy generate-questions --no-verify-jwt`

## Stabilization Phase (Recovery)

### 1. Revert Admin Panel
1.  Go to the `Questerix/admin-panel` repo.
2.  `git checkout [last-known-stable-commit-hash]`
3.  `npm run build`
4.  Redeploy the `dist/` folder to your hosting provider.

### 2. Verify Client Compatibility
1.  Open the Student App (Flutter).
2.  Perform a test session.
3.  Check if older questions are still rendering correctly.
4.  ✅ The normalization logic in `packages/core` is backward compatible, so this should remain stable.

## Post-Mortem Phase (Analysis)

1.  Export the `studio_prompts` failure logs:
    `SELECT * FROM studio_prompts WHERE status = 'failed' AND created_at > [incident-start];`
2.  Identify which "Layer" failed (Layer 0, 1, 2, 3, or 4).
3.  Update the `AIQuestionSchema` in `packages/core` to include any missed edge cases.
4.  Update the contract tests in `question-type-contract.test.ts`.

## Contacts
- **Database Admin**: @[Name]
- **AI Infrastructure**: @[Name]
- **Frontend Lead**: @[Name]
