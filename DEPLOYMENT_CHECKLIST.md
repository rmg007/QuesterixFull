# Deployment Checklist - Question Type Fix

## Toolchain Versions (Pinned for Stability)
To ensure consistent build artifacts, use these exact versions:
- **Node.js**: `v22.18.x`
- **npm**: `10.9.x`
- **Supabase CLI**: `v2.76.x`
- **Flutter**: `3.38.x` (Channel stable)
- **Dart**: `3.10.x`
- **Deno**: `2.7.x`

## Pre-Deployment

### 0. Contract Verification
- [ ] Run contract tests: `npx vitest run packages/core/src/constants/question-type-contract.test.ts --config admin-panel/vite.config.ts --root .`
- [ ] ✅ All tests passed (ensures code enums match DB schema)

### 1. Code Review
- [ ] Review `packages/core/src/constants/question-types.ts`
- [ ] Review changes to `use-studio-generator.ts` and `use-ai-generator.ts`
- [ ] Review Edge Function changes in `generate-questions/index.ts`
- [ ] Review test fixture updates

### 2. Local Testing
- [ ] Run admin panel: `cd Questerix/admin-panel && npm run dev`
- [ ] Test Question Studio generation with multiple types
- [ ] Verify no console errors
- [ ] Check Network tab for canonical `question_type` values

### 3. Build Verification
```bash
# Admin Panel
cd Questerix/admin-panel
npm run build

# Verify build succeeds
```

## Deployment Steps

### Step 1: Deploy Core Package
```bash
cd Questerix/packages/core
npm install
# No build step needed - TypeScript source is consumed directly
```

### Step 2: Deploy Admin Panel
```bash
cd Questerix/admin-panel
npm install
npm run build
# Deploy dist/ to your hosting (Vercel/Netlify/etc.)
```

### Step 3: Deploy Edge Function
```bash
cd questerix-student-app
supabase functions deploy generate-questions
```

**Verify**:
```bash
# Test the deployed function
curl -X POST https://[your-project].supabase.co/functions/v1/generate-questions \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test","difficulty_distribution":{"easy":1,"medium":0,"hard":0}}'
```

### Step 4: Deploy Cloudflare Worker (Separate Repo)
**Location**: Your Cloudflare Worker repository (outside this workspace)

**Changes to apply**:
1. Add `responseSchema` to Gemini API call (copy from Edge Function)
2. Update prompt: change `mcq` to `multiple_choice`
3. Add post-parse normalization (copy `normalizeQuestionType` function)

```bash
cd [your-worker-repo]
npm run deploy
```

## Post-Deployment Verification

### Immediate Checks (First 10 minutes)

1. **Generate a test question batch**:
   - Log into admin panel
   - Go to Question Studio
   - Generate 5 questions
   - ✅ Should succeed without errors

2. **Check console**:
   - Open DevTools
   - Generate questions
   - ✅ No `AI returned invalid question format` errors
   - ✅ No `Validation failed` errors with `question_type`

3. **Verify database**:
   ```sql
   SELECT * FROM studio_prompts 
   WHERE created_at > NOW() - INTERVAL '10 minutes'
   ORDER BY created_at DESC 
   LIMIT 5;
   ```
   - ✅ All should have `status = 'generated'` (not `'failed'`)

### Extended Monitoring (First 24 hours)

1. **Check error rate**:
   ```sql
   SELECT 
     DATE_TRUNC('hour', created_at) as hour,
     COUNT(*) FILTER (WHERE status = 'failed') as failed,
     COUNT(*) FILTER (WHERE status = 'generated') as success,
     ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'failed') / COUNT(*), 2) as failure_rate
   FROM studio_prompts
   WHERE created_at > NOW() - INTERVAL '24 hours'
   GROUP BY hour
   ORDER BY hour DESC;
   ```
   - ✅ Failure rate should be < 5%

2. **Check for unknown types**:
   ```sql
   SELECT 
     error_details->>'invalid_question_type' as invalid_type,
     COUNT(*) as occurrences
   FROM studio_prompts
   WHERE created_at > NOW() - INTERVAL '24 hours'
     AND error_details->>'invalid_question_type' IS NOT NULL
   GROUP BY invalid_type;
   ```
   - ✅ Should return 0 rows

3. **User feedback**:
   - Monitor support channels for generation issues
   - Check application logs for `[Studio] Generation error`

## Rollback Procedure

If critical issues occur:

### 1. Rollback Edge Function
```bash
cd questerix-student-app
supabase functions deploy generate-questions --no-verify-jwt
# Or restore from previous deployment
```

### 2. Rollback Admin Panel
Redeploy the previous version from git:
```bash
git revert [commit-hash]
npm run build
# Deploy
```

### 3. Rollback Cloudflare Worker
```bash
cd [worker-repo]
wrangler rollback
```

## Success Criteria

After 7 days in production:
- ✅ Zero `invalid question format` errors
- ✅ Question generation success rate > 95%
- ✅ No reports of generation failures from users
- ✅ All question types (including `matching`) work correctly

## Notes

- The fix is **backward compatible** - old data in the database is unaffected
- Client-side normalization ensures resilience even if server changes are delayed
- Test fixtures now use canonical values, preventing regression
