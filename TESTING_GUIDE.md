# Testing Guide for Question Type Fix

## Pre-Deployment Testing

### 1. Admin Panel - Unit Tests
```bash
cd Questerix/admin-panel
npm test -- use-studio-generator
npm test -- use-ai-generator
```

**Expected**: All tests pass, including the new test case that verifies `mcq` is normalized to `multiple_choice`.

### 2. Admin Panel - Type Check
```bash
cd Questerix/admin-panel
npm run typecheck
```

**Expected**: No errors related to `question_type` or `CanonicalQuestionType`.

### 3. Edge Function - Unit Tests
```bash
cd questerix-student-app/supabase/functions/generate-questions
deno test --allow-all test.ts
```

**Expected**: All tests pass, mock responses use `multiple_choice`.

### 4. Flutter - Static Analysis
```bash
cd questerix-student-app
flutter analyze
```

**Expected**: No errors in `question_fixtures.dart` or domain models.

## Manual Testing (Critical Path)

### Test Case 1: Question Studio Generation
1. Log into admin panel
2. Navigate to Question Studio
3. Configure:
   - Domain: "Math"
   - Topics: "Fractions"
   - Count: 5
   - Types: Select "Multiple Choice"
4. Click "Generate"

**Expected**: 
- ✅ Generation succeeds
- ✅ No console errors about invalid question format
- ✅ Questions appear in review cards
- ✅ All questions have `question_type: "multiple_choice"` (check network tab)

### Test Case 2: Legacy Alias Handling
**Purpose**: Verify normalization works if the AI somehow returns `mcq`.

1. Open browser DevTools > Network tab
2. Generate questions as in Test Case 1
3. Inspect the response from `/ai/generate-questions`
4. If you see `question_type: "mcq"` in the raw response, verify:
   - ✅ No validation error appears
   - ✅ Questions are accepted and displayed
   - ✅ Client-side normalization converted it to `multiple_choice`

**Note**: With Layer 0 (responseSchema), you should NEVER see `mcq` in the response. If you do, the Gemini API configuration didn't take effect.

### Test Case 3: All Question Types
Generate a batch with ALL types selected:
- Multiple Choice
- Multiple Select
- Text Input
- True/False
- Reorder Steps
- Matching

**Expected**: All types generate successfully without validation errors.

## Monitoring (Post-Deployment)

### Check for Invalid Types
Query the `studio_prompts` table for failed generations:

```sql
SELECT 
  id,
  created_at,
  domain_name,
  topics,
  status,
  error_details
FROM studio_prompts
WHERE status = 'failed'
  AND error_details->>'invalid_question_type' IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

**Expected**: After deployment, this query should return 0 rows (or only old pre-fix failures).

### Check AI Response Patterns
If you want to verify the AI is consistently using canonical types:

```sql
SELECT 
  question_types,
  COUNT(*) as generation_count,
  AVG(questions_generated) as avg_questions
FROM studio_prompts
WHERE created_at > NOW() - INTERVAL '7 days'
  AND status = 'generated'
GROUP BY question_types;
```

## Rollback Plan

If issues occur after deployment:

1. **Immediate**: Revert the Edge Function deployment
2. **Client-side**: The admin panel changes are backward-compatible (normalization handles both old and new formats)
3. **Database**: No schema changes were made, so no migration rollback needed

## Known Limitations

1. **Cloudflare Worker**: Changes must be manually applied to the Worker repo (outside this workspace)
2. **Pre-existing lint errors**: 2 unrelated lint errors remain in the admin panel (not introduced by this fix)
3. **Test fixtures**: Some E2E mocks may need updating if they assert on exact error messages

## Success Metrics

After 1 week in production:
- Zero `AI returned invalid question format` errors in logs
- Zero failed `studio_prompts` with `invalid_question_type` in `error_details`
- Question generation success rate > 95%
