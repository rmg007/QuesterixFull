# Supabase Alert Thresholds - Question Studio

Run these SQL queries in your Supabase SQL Editor to monitor the health of the AI generation system.

## 1. Monitor Critical AI Format Errors (Last Hour)
If this returns > 5 rows in 10 minutes, alert the engineering team.
```sql
SELECT 
  COUNT(*) as error_count,
  error_details->>'invalid_question_type' as type_found
FROM studio_prompts
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '1 hour'
  AND error_details->>'invalid_question_type' IS NOT NULL
GROUP BY type_found;
```

## 2. Overall Success Rate Check
If `success_rate` drops below 95%, investigate AI provider latency or quota issues.
```sql
WITH stats AS (
  SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'generated') as success
  FROM studio_prompts
  WHERE created_at > NOW() - INTERVAL '24 hours'
)
SELECT 
  total,
  success,
  ROUND(100.0 * success / NULLIF(total, 0), 2) as success_rate
FROM stats;
```

## 3. Database Cleanup (Optional)
Recommended weekly cleanup for old debug/failed prompts to save storage.
```sql
DELETE FROM studio_prompts
WHERE created_at < NOW() - INTERVAL '30 days'
  AND status = 'failed';
```
