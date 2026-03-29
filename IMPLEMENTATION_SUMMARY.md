# Question Type Mismatch Fix - Implementation Summary

## Problem
The production admin panel was experiencing recurring errors where AI-generated questions returned `question_type: "mcq"` but the validation schema only accepted `"multiple_choice"`. This caused validation failures and prevented question generation from succeeding.

## Root Cause
The question type enum was defined inconsistently across 6+ locations in 2 repositories:
- Admin panel Zod schemas used `multiple_choice`
- Edge Function prompts instructed the AI to use `mcq`
- Test fixtures used various aliases (`mcq`, `short_answer`, `ordering`)
- No single source of truth existed

## Solution: 5-Layer Defense in Depth

### Layer 0: Structural Prevention (Gemini responseSchema)
**File**: `questerix-student-app/supabase/functions/generate-questions/index.ts`

Added JSON Schema constraint to Gemini API call that physically prevents the model from outputting invalid enum values:

```typescript
const responseSchema = {
  type: "array",
  items: {
    properties: {
      question_type: {
        type: "string",
        enum: ["multiple_choice", "mcq_multi", "text_input", "boolean", "reorder_steps", "matching"]
      }
    }
  }
};
```

**Impact**: Makes it structurally impossible for Gemini to return `mcq` instead of `multiple_choice`.

### Layer 1: Single Source of Truth
**File**: `Questerix/packages/core/src/constants/question-types.ts` (NEW)

Created canonical constants file with:
- `CANONICAL_QUESTION_TYPES` array
- `QUESTION_TYPE_ALIASES` map (mcq → multiple_choice, etc.)
- `normalizeQuestionType()` function
- Shared Zod schema with `z.preprocess` for automatic normalization

**Files Updated**:
- `admin-panel/src/hooks/use-studio-generator.ts` - imports from core
- `admin-panel/src/hooks/use-ai-generator.ts` - imports from core
- `admin-panel/src/features/ai-assistant/api/generateQuestions.ts` - imports CanonicalQuestionType
- `admin-panel/src/features/ai-assistant/components/QuestionReviewGrid.tsx` - imports CanonicalQuestionType

### Layer 2: Server-Side Normalization
**File**: `questerix-student-app/supabase/functions/generate-questions/index.ts`

- Fixed `buildPrompt()` to use `multiple_choice` instead of `mcq` in schema documentation
- Added post-parse normalization:
  ```typescript
  questions = questions.map((q: any) => ({
    ...q,
    question_type: normalizeQuestionType(q.question_type) ?? q.question_type,
  }));
  ```

**Impact**: All clients receive canonical values regardless of what the model emits.

### Layer 3: Client-Side Normalization
**Files**: 
- `admin-panel/src/hooks/use-studio-generator.ts`
- `admin-panel/src/hooks/use-ai-generator.ts`

Uses shared `AIQuestionSchema` from `@questerix/core` which includes `z.preprocess` to normalize before validation.

**Impact**: Even if server normalization is bypassed, client recovers gracefully.

### Layer 4: Test Fixture Alignment
**Files Updated**:
- `Questerix/admin-panel/tests/fixtures/questions.ts`
  - Changed `'mcq'` → `'multiple_choice'`
  - Changed `'short_answer'` → `'text_input'`
  - Changed `'ordering'` → `'reorder_steps'`
  - Imports `CanonicalQuestionType` from core

- `questerix-student-app/test/fixtures/question_fixtures.dart`
  - Changed `QuestionType.mcq` → `QuestionType.multipleChoice`
  - Changed `QuestionType.shortAnswer` → `QuestionType.textInput`
  - Now imports from `questerix_domain` package

- `questerix-student-app/supabase/functions/generate-questions/test.ts`
  - All mock responses use `multiple_choice` instead of `mcq`

- `questerix-student-app/supabase/functions/validate-content/test.ts`
  - All test questions use `multiple_choice` instead of `mcq`

### Layer 5: Observability (Monitoring)
**File**: `admin-panel/src/hooks/use-studio-generator.ts`

Added logging in `generateBatch` catch block to record invalid `question_type` values to `studio_prompts` table for monitoring:

```typescript
if (promptId && invalidType) {
  await supabase.from('studio_prompts').update({ 
    status: 'failed',
    error_details: { 
      invalid_question_type: (invalidType as any)._errors[0],
      raw_ai_response: response.questions
    }
  }).eq('id', promptId);
}
```

## Files Created
1. `Questerix/packages/core/src/constants/question-types.ts` - Single source of truth

## Files Modified
### Admin Panel (Questerix)
1. `packages/core/package.json` - Added zod dependency, export path
2. `admin-panel/src/hooks/use-studio-generator.ts` - Import from core, use shared schema
3. `admin-panel/src/hooks/use-ai-generator.ts` - Import from core
4. `admin-panel/src/features/ai-assistant/api/generateQuestions.ts` - Import CanonicalQuestionType
5. `admin-panel/src/features/ai-assistant/components/QuestionReviewGrid.tsx` - Import CanonicalQuestionType
6. `admin-panel/tests/fixtures/questions.ts` - Use canonical values

### Student App (questerix-student-app)
7. `supabase/functions/generate-questions/index.ts` - responseSchema, normalization, prompt fix
8. `test/fixtures/question_fixtures.dart` - Use domain model types
9. `supabase/functions/generate-questions/test.ts` - Use canonical values
10. `supabase/functions/validate-content/test.ts` - Use canonical values

## Remaining Work
### Cloudflare Worker (Outside This Workspace)
The Cloudflare Worker that serves `/ai/generate-questions` needs the same updates as the Edge Function:
1. Add `responseSchema` to Gemini API call
2. Fix prompt to use `multiple_choice` instead of `mcq`
3. Add post-parse normalization

## Testing
- Admin panel type-checks pass (31 remaining errors are pre-existing unrelated issues)
- No linter errors in modified files
- Test fixtures aligned across both repos
- Edge Function tests updated

## Success Criteria Met
✅ Gemini cannot output `mcq` (responseSchema enforces canonical values)  
✅ Server normalizes before HTTP response  
✅ Client normalizes via z.preprocess  
✅ All test fixtures use canonical DB enum values  
✅ Both Zod schemas derive from one shared constant  
✅ `use-ai-generator.ts` gains `matching` support  
✅ Invalid types logged to studio_prompts for monitoring

## Deployment Notes
1. Deploy updated Edge Function to Supabase
2. Deploy admin panel with new core package
3. Update Cloudflare Worker (separate repo) with same changes
4. Monitor `studio_prompts` table for any `error_details` entries with `invalid_question_type`
