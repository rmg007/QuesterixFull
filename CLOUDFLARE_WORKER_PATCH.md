# Cloudflare Worker Patch Instructions

## Overview
Your Cloudflare Worker that serves `/ai/generate-questions` needs the same fixes as the Supabase Edge Function to prevent the `mcq` vs `multiple_choice` mismatch.

## Required Changes

### 1. Add Canonical Types and Normalizer

Add this at the top of your worker file (after imports):

```typescript
// Canonical question types
const CANONICAL_QUESTION_TYPES = [
  'multiple_choice',
  'mcq_multi',
  'text_input',
  'boolean',
  'reorder_steps',
  'matching',
] as const;

const QUESTION_TYPE_ALIASES: Record<string, typeof CANONICAL_QUESTION_TYPES[number]> = {
  mcq: 'multiple_choice',
  single_choice: 'multiple_choice',
  radio: 'multiple_choice',
  multi_select: 'mcq_multi',
  multiple_select: 'mcq_multi',
  select_all_that_apply: 'mcq_multi',
  true_false: 'boolean',
  tf: 'boolean',
  short_answer: 'text_input',
  fill_in_blank: 'text_input',
  fill_blank: 'text_input',
  reorder: 'reorder_steps',
  ordering: 'reorder_steps',
  sequence: 'reorder_steps',
};

function normalizeQuestionType(raw: string): typeof CANONICAL_QUESTION_TYPES[number] | null {
  const normalized = raw.toLowerCase().replace(/\s/g, '_');
  return QUESTION_TYPE_ALIASES[normalized] || CANONICAL_QUESTION_TYPES.find(type => type === normalized) || null;
}
```

### 2. Add Gemini responseSchema

If using Gemini, add this schema:

```typescript
const responseSchema = {
  type: "array",
  items: {
    type: "object",
    properties: {
      text: { type: "string" },
      question_type: {
        type: "string",
        enum: CANONICAL_QUESTION_TYPES
      },
      difficulty: { type: "string", enum: ["easy", "medium", "hard"] },
      metadata: {
        type: "object",
        properties: {
          options: { type: "array", items: { type: "string" } },
          correct_answer: {},
          explanation: { type: "string" },
          terms: { type: "array", items: { type: "string" } },
          definitions: { type: "array", items: { type: "string" } }
        }
      }
    },
    required: ["text", "question_type", "difficulty", "metadata"]
  }
};
```

Then pass it to the model config:

```typescript
const model = genAI.getGenerativeModel({ 
  model: 'gemini-1.5-flash',
  generationConfig: {
    responseMimeType: "application/json",
    temperature: 0.1,
    responseSchema, // Add this
  },
});
```

### 3. Fix the Prompt

Find your `buildPrompt` function and update:

**Before**:
```typescript
const schema = {
  question_type: 'enum: mcq | mcq_multi | text_input | boolean | reorder_steps',
  // ...
};

// Requirements:
// - Mix question types (mcq, mcq_multi, text_input, boolean, reorder_steps)
```

**After**:
```typescript
const schema = {
  question_type: `enum: ${CANONICAL_QUESTION_TYPES.join(' | ')}`,
  // ...
};

// Requirements:
// - Mix question types (${CANONICAL_QUESTION_TYPES.filter(t => t !== 'matching').join(', ')})
```

### 4. Add Post-Parse Normalization

After parsing the AI response, normalize before returning:

```typescript
let questions = JSON.parse(aiResponse);

// Normalize question types
questions = questions.map((q: any) => ({
  ...q,
  question_type: normalizeQuestionType(q.question_type) ?? q.question_type,
}));

return new Response(JSON.stringify({ questions, metadata }), {
  headers: { 'Content-Type': 'application/json' },
});
```

## Testing the Worker

### Local Testing
```bash
npm run dev
# Or: wrangler dev
```

Test with curl:
```bash
curl -X POST http://localhost:8787/ai/generate-questions \
  -H "Authorization: Bearer [test-token]" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test content about fractions",
    "difficulty_distribution": {"easy": 2, "medium": 1, "hard": 0}
  }'
```

**Verify**:
- Response contains `question_type: "multiple_choice"` (NOT `"mcq"`)
- No validation errors

### Production Testing
After deploying:
```bash
curl -X POST https://[your-worker].workers.dev/ai/generate-questions \
  -H "Authorization: Bearer [prod-token]" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test content",
    "difficulty_distribution": {"easy": 1, "medium": 0, "hard": 0}
  }'
```

## Alternative: If Not Using Gemini

If your Worker uses a different AI provider (OpenAI, Anthropic, etc.):

1. **Skip responseSchema** (provider-specific)
2. **Keep the prompt fix** (change `mcq` to `multiple_choice`)
3. **Keep the normalization** (essential for any provider)

For OpenAI with Structured Outputs:
```typescript
const completion = await openai.chat.completions.create({
  model: "gpt-4o-2024-08-06",
  messages: [...],
  response_format: {
    type: "json_schema",
    json_schema: {
      name: "questions",
      schema: {
        type: "object",
        properties: {
          questions: {
            type: "array",
            items: {
              properties: {
                question_type: {
                  type: "string",
                  enum: CANONICAL_QUESTION_TYPES
                }
              }
            }
          }
        }
      }
    }
  }
});
```

## Verification Checklist

After deploying the Worker:
- [ ] Worker responds successfully to generation requests
- [ ] Response contains canonical `question_type` values
- [ ] Admin panel can consume the response without validation errors
- [ ] No `mcq` appears in any response
- [ ] Monitor Worker logs for errors in first hour
