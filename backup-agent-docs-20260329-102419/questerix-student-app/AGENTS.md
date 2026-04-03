# Agent Rules & Conventions — Mobile Engineer

> These rules inherit from the universal rules in `Questerix/AGENTS.md`.

## 📚 Documentation (Read First)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `../AI_WORKFLOW_SETUP.md` | Complete IDE/MCP setup guide | Onboarding, troubleshooting |
| `../MCP_TOOLS_REFERENCE.md` | All MCP tools with examples | When using git/npm/test/tools |
| `../QUICK_REFERENCE.md` | One-page daily reference | Quick lookups, print it out |

**All AI agents MUST read `docs/LEARNING_LOG.md` for prevention rules before making changes.**

## Task Tiers (Read First)
if message contains `// quick` or `// light`: TIER S — skip all bootstrap, Cortex, and close checklist
if message contains `// full` or `// sprint`: TIER L — full bootstrap, Cortex plan/verify, full session close
default: TIER M — read SKELETON_SUMMARY.md only, update local tasks.md, batch session close

## Tool Selection & Token Savings (MANDATORY)

To optimize token usage and ensure structured output, all agents MUST follow these preferences:

1.  **Git Operations**: NEVER use direct shell commands like `git status`, `git log`, or `git diff`. ALWAYS use the `pare-git` MCP tools (e.g., `pare-git_status`, `pare-git_log`).
2.  **Node/npm**: NEVER use direct shell commands like `npm install` or `npm test`. ALWAYS use `pare-npm` and `pare-test` MCP tools.
3.  **Learning Log**: After fixing bugs, add prevention rules to `docs/LEARNING_LOG.md` to prevent recurrence.

These tools reduce token consumption by 80-95% compared to raw terminal output.

## Primary Stack
- Flutter (Stable) + Riverpod (AsyncNotifier) + Drift (Offline-First Tombstone Sync) + Atomic UI Tokens.

## Core Rules
1. **Pixel Perfection**: Use `app_theme` tokens. Never hardcode raw HEX values.
2. **Offline-First**: All user actions must work offline. Use Drift; Sync Service handles prop.
3. **Immutability**: Use `freezed` for models.
4. **Clean Code**: Zero warnings in `analysis_options.yaml`.
5. **RTL Support**: Arabic and Hebrew locales exist; maintain as needed.
6. **No dynamic variables**: Use `final`.

## Testing & Operations
- Never run full `flutter test` suite locally (to prevent crashes). Use targeted file paths: `flutter test test/path/to/specific_test.dart`
- Always run `dart run build_runner build --delete-conflicting-outputs` after changing `@freezed` or `@DriftDatabase` classes.
- **Drift Migrations**: NEVER modify existing `MigrationStrategy` steps. Always increment `schemaVersion` and add new logic in `onUpgrade`.
- **English-only strings**: No hardcoded translations in source.
- **Supabase QueryBuilder**: IMMUTABLE — always chain `.eq()`. Never call on stored variable without reassigning.
