# AI Workflow Setup & Configuration

> **Last Updated:** 2026-03-29  
> **Applies To:** All AI coding agents (Cursor, Windsurf, Antigravity, VS Code Copilot)  
> **Scope:** QuesterixFull workspace (4 projects)

---

## Overview

This document describes the complete AI tooling setup for the QuesterixFull workspace. All configurations are designed to work across **4 IDEs**: Cursor AI, Windsurf, Antigravity IDE, and VS Code Copilot.

### Goals

1. **Token Efficiency** — Reduce AI context window usage by 80-95% through structured MCP tools
2. **Persistent Context** — Share memories and project knowledge across all IDEs and sessions
3. **Automation** — Eliminate manual prompts for tool selection and memory storage
4. **Consistency** — Same rules and tooling apply regardless of which IDE is used

---

## Architecture

### The 4 Projects

| Project | Location | Tech Stack | Purpose |
|---------|----------|------------|---------|
| **Questerix** | `Questerix/` | React 18 + TypeScript + Vite + Supabase | Admin Panel + Backend |
| **Student App** | `questerix-student-app/` | Flutter + Riverpod + Drift | iOS/Android Mobile App |
| **Help Docs** | `questerix-help-docs/` | VitePress + Cloudflare Pages | User Documentation |
| **Landing Pages** | `questerix-landing-pages/` | React 18 + Vite + Cloudflare Pages | Marketing Site |

### The 4 IDEs

All IDEs are configured with identical MCP tools and ignore patterns:

1. **Cursor AI** — Primary IDE with `.cursor/mcp.json` and `.cursor/rules/`
2. **Windsurf** — Uses `.codeium/windsurf/mcp_config.json` and `.codeiumignore`
3. **Antigravity IDE** — Uses `.gemini/antigravity/mcp_config.json` and `.antigravityignore`
4. **VS Code Copilot** — Uses user `mcp.json` and per-project `.vscode/mcp.json`

---

## MCP Tools Configuration

### Global IDE Configs

Each IDE has a **global config** that applies to all projects:

| IDE | Config Location | Key |
|-----|-----------------|-----|
| Cursor | `~/.cursor/mcp.json` | `mcpServers` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` |
| Antigravity | `~/.gemini/antigravity/mcp_config.json` | `mcpServers` |
| VS Code | `~/AppData/Roaming/Code/User/mcp.json` | `servers` |

### Installed MCP Tools

| Tool | Purpose | Token Reduction | Command |
|------|---------|-----------------|---------|
| **LEARNING_LOG** | Prevention rules from past bugs | N/A | Check `docs/LEARNING_LOG.md` |
| **pare-git** | Structured git operations | ~92% | `pare-git_status`, `pare-git_log`, `pare-git_diff` |
| **pare-npm** | Structured npm operations | ~83% | `pare-npm_install`, `pare-npm_list`, `pare-npm_run` |
| **pare-test** | Structured test output | ~80% | `pare-test_run`, `pare-test_coverage` |
| **pare-typescript** | Structured TypeScript errors | Significant | `pare-typescript_check` |

### Project-Level Configs

Each project also has `.vscode/mcp.json` for VS Code Copilot and `.mcp_config.json` for reference:

- `Questerix/.vscode/mcp.json`
- `questerix-student-app/.vscode/mcp.json`
- `questerix-help-docs/.vscode/mcp.json`
- `questerix-landing-pages/.vscode/mcp.json`

---

## Ignore Files (Token Savings)

Every project has 3 ignore files with **tailored patterns**:

### File Locations

```
<project-root>/
├── .cursorignore       → Cursor AI indexing exclusion
├── .codeiumignore      → Windsurf indexing exclusion  
├── .antigravityignore  → Antigravity IDE exclusion
└── .vscode/
    └── settings.json   → VS Code search.exclude
```

### Patterns by Project

#### Questerix (Admin Panel)
```gitignore
# Dependencies
**/node_modules/

# Lock files (massive, zero AI value)
**/package-lock.json
**/yarn.lock

# Build output
**/dist/
**/build/
admin-panel/dist/

# Supabase generated types (~2k lines each)
admin-panel/src/lib/database.types.utf8.ts

# Test artifacts
**/playwright-report/
**/test-results/
**/coverage/

# Cortex outputs
questerix-cortex/outputs/
questerix-cortex/dist/

# Secrets
**/.env
**/.env.*
.mcp_config.json

# Legacy (don't index dead code)
landing-pages/
student-app/
```

#### Student App (Flutter)
```gitignore
# Dart/Flutter
**/.dart_tool/
**/.pub-cache/
**/.pub/

# Codegen (regenerated, not hand-written)
**/*.g.dart
**/*.freezed.dart
**/*.mocks.dart
**/*.gr.dart

# Build
**/build/
android/app/debug/
android/app/profile/
android/app/release/

# iOS
**/ios/Flutter/.last_build_id
**/app.*.symbols
**/app.*.map.json
```

#### Help Docs (VitePress)
```gitignore
# VitePress cache & output
.vitepress/dist/
.vitepress/cache/

# Playwright
.playwright/
playwright-report/
```

#### Landing Pages
```gitignore
# Generated assets
public/assets/generated/

# Build
dist/
```

### Common Patterns (All Projects)

```gitignore
# Dependencies
**/node_modules/

# Lock files (massive JSON, no AI value)
**/package-lock.json
**/yarn.lock
**/pnpm-lock.yaml
**/pubspec.lock

# Media & binary (no code value)
**/*.png
**/*.jpg
**/*.jpeg
**/*.gif
**/*.svg
**/*.ico
**/*.mp4
**/*.woff
**/*.woff2

# Minified bundles (unreadable)
**/*.min.js
**/*.min.css
**/*.chunk.js

# Secrets (security)
**/.env
**/.env.*
**/.secrets*
temp-secrets-*.json

# Logs
**/*.log
**/*_output.txt
**/*_error.txt

# IDE noise
**/.idea/
**/.DS_Store
**/Thumbs.db
```

---

## Automation Rules (Glob-Scoped)

All rules use **strict glob targeting** to minimize token usage. Rules only load when editing matching files.

### Cursor Rules (`.cursor/rules/`)

#### Global Rules (Lightweight - All Files)

| Rule | globs | alwaysApply | Purpose |
|------|-------|-------------|---------|
| `tool-preference.mdc` | `**/*` | `true` | Quick reminder to use MCP tools |

These are **lean** (20 lines each) — just triggers with quick examples.

#### Scoped Rules (Tech-Specific)

| Rule | globs | When Active | Size |
|------|-------|-------------|------|
| `react-typescript.mdc` | `Questerix/admin-panel/src/**/*.{tsx,ts}`<br>`questerix-landing-pages/src/**/*.{tsx,ts}` | Editing React/TS | ~60 lines |
| `flutter.mdc` | `questerix-student-app/lib/**/*.dart` | Editing Flutter | ~50 lines |
| `vitepress.mdc` | `questerix-help-docs/docs/**/*.md` | Editing docs | ~40 lines |
| `supabase.mdc` | `**/supabase/**/*.sql`<br>`**/database.types*.ts` | DB work | ~50 lines |
| `playwright.mdc` | `**/e2e/**/*.spec.ts`<br>`**/playwright.config.ts` | E2E tests | ~40 lines |
| `cortex.mdc` | `**/questerix-cortex/**/*.md`<br>`**/*plan*.md` | AI workflow | ~40 lines |

**Token Savings:** Scoped rules save **thousands of tokens per prompt** by not loading irrelevant tech rules.

Example: When editing a Flutter file:
- ✅ Loads: `tool-preference.mdc` (20 lines) + `flutter.mdc` (50 lines)
- ❌ Ignores: `react-typescript.mdc`, `vitepress.mdc`, `supabase.mdc` (150+ lines saved)

### Windsurf Rules (`.windsurf/rules/`)

Same glob-scoped architecture for Windsurf IDE:

| Rule | globs | When Active |
|------|-------|-------------|
| `tool-preference.md` | `**/*` | All files |
| `react-typescript.md` | React/TS paths | Questerix/Landing |
| `flutter.md` | Dart paths | Student app |
| `vitepress.md` | Docs paths | Help docs |
| `supabase.md` | SQL paths | DB work |
| `playwright.md` | Test paths | E2E tests |
| `cortex.md` | Plan paths | AI workflow |

### AGENTS.md (All 4 Projects)

Each project's `AGENTS.md` includes the full tool preference rules (redundancy for non-Cursor IDEs).

### AGENTS.md (All 4 Projects)

Each project's `AGENTS.md` includes:

```markdown
## Tool Selection & Token Savings (MANDATORY)

To optimize token usage and ensure structured output, all agents MUST follow these preferences:

1.  **Git Operations**: NEVER use direct shell commands like `git status`, `git log`, or `git diff`. ALWAYS use the `pare-git` MCP tools (e.g., `pare-git_status`, `pare-git_log`).
2.  **Node/npm**: NEVER use direct shell commands like `npm install` or `npm test`. ALWAYS use `pare-npm` and `pare-test` MCP tools.
3.  **TypeScript**: ALWAYS use `pare-typescript_check` instead of direct `tsc` shell commands.
4.  **Learning Log**: After fixing bugs, add prevention rules to `docs/LEARNING_LOG.md` to prevent recurrence.

These tools reduce token consumption by 80-95% compared to raw terminal output.
```

### VS Code Copilot (`.github/copilot-instructions.md`)

Each project has copilot instructions mandating the same tool preferences.

---

## Task Tiers

All projects use a **3-tier task system**:

| Tier | Trigger | Behavior |
|------|---------|----------|
| **S (Quick)** | `// quick` or `// light` | Skip bootstrap, skip session close checklist |
| **M (Default)** | *(no trigger)* | Read README.md, batch session close |
| **L (Full)** | `// full` or `// sprint` | Full bootstrap, Cortex plan/verify, full session close |

### Session Close Checklist (TIER M & L)

Runs after every daily work period:

- [ ] **TIME_LOG** — Add row to `docs/TIME_LOG.md` with date, hours, app(s), work type, description
- [ ] **Temp Files** — Delete scratch files and `/tmp/` files
- [ ] **tasks.md** — Mark completed tasks `[x]`, add new sub-tasks
- [ ] **LEARNING_LOG** — Append weekly summary of prevention rules (if meaningful)

---

## Critical Constraints

### Cross-Project Anti-Patterns

| # | Constraint | Violation |
|---|-----------|-----------|
| 1 | **admin-panel is FEATURE FROZEN** | Adding new features instead of bug fixes |
| 2 | **Never run full `flutter test` locally** | Running `flutter test` without targeting specific files |
| 3 | **Never modify Drift MigrationStrategy** | Editing existing migration steps instead of adding new ones |
| 4 | **Never hardcode colors** | Using raw HEX in Flutter or hardcoded values in landing pages |
| 5 | **Never hit Gemini API in tests** | Calling real APIs instead of mocking |
| 6 | **Never commit secrets** | Committing `.env`, `.mcp_config.json`, or temp-secrets files |
| 7 | **Never connect prod domains** | Connecting `questerix.com` or `help.questerix.com` without instruction |
| 8 | **Supabase QueryBuilder is immutable** | Storing QueryBuilder in variable and reusing without reassigning |
| 9 | **All new tables need RLS** | Creating tables without SELECT/INSERT/UPDATE/DELETE policies |
| 10 | **Help/Landing: no backend libs** | Installing Supabase or backend libraries in docs/marketing repos |

---

## Prevention Rules

### What's Stored in LEARNING_LOG

The following critical knowledge is stored in `docs/LEARNING_LOG.md`:

1. **Bug Prevention Rules** — Patterns that caused bugs and how to avoid them
2. **IDE & MCP Setup** — All configured tools and ignore files
3. **Questerix Admin Panel** — Stack, feature freeze rule, testing tiers
4. **Student App** — Flutter rules, offline-first, Drift migrations
5. **Help Docs** — VitePress stack, writing persona, Feature Snapshot workflow
6. **Landing Pages** — React/Vite stack, design tokens, SEO rules
7. **Developer Workflow** — Task tiers, session close checklist
8. **Critical Constraints** — 11 anti-patterns that apply across all projects
9. **Supabase & Backend** — Cortex tools, RLS audit, edge functions
10. **Deployment Architecture** — Cloudflare Pages setup for all 4 projects
11. **Developer Preferences** — Automation preference, task tiers usage

### How to Retrieve

Any AI in any IDE can recall this context:

```
# Check LEARNING_LOG for relevant prevention rules
grep -i "flutter" docs/LEARNING_LOG.md
grep -i "migration" docs/LEARNING_LOG.md
grep -i "offline" docs/LEARNING_LOG.md
```

---

## File Reference

### Configuration Files Matrix

| File Type | Questerix | Student App | Help Docs | Landing Pages | Root |
|-----------|-----------|-------------|-----------|---------------|------|
| `.cursorignore` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.codeiumignore` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.antigravityignore` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.vscode/mcp.json` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.vscode/settings.json` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.mcp_config.json` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `AGENTS.md` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `.github/copilot-instructions.md` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `.cursor/rules/*.mdc` | ❌ | ❌ | ❌ | ❌ | ✅ (8 scoped rules) |
| `.windsurf/rules/*.md` | ❌ | ❌ | ❌ | ❌ | ✅ (8 scoped rules) |

### Scoped Rules Reference

**Cursor** (`.cursor/rules/`):
| Rule | globs | Lines | Purpose |
|------|-------|-------|---------|
| `tool-preference.mdc` | `**/*` | ~20 | MCP tools trigger |
| `react-typescript.mdc` | React paths | ~60 | React/TS rules |
| `flutter.mdc` | Dart paths | ~50 | Flutter rules |
| `vitepress.mdc` | Docs paths | ~40 | VitePress rules |
| `supabase.mdc` | SQL paths | ~50 | DB rules |
| `playwright.mdc` | Test paths | ~40 | E2E rules |
| `cortex.mdc` | Plan paths | ~40 | AI workflow |

**Windsurf** (`.windsurf/rules/`) — Same 8 rules in `.md` format

### IDE Global Configs

| IDE | Config Path | Status |
|-----|-------------|--------|
| Cursor | `~/.cursor/mcp.json` | ✅ All tools configured |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | ✅ All tools configured |
| Antigravity | `~/.gemini/antigravity/mcp_config.json` | ✅ All tools configured |
| VS Code | `~/AppData/Roaming/Code/User/mcp.json` | ✅ All tools configured |

---

## Troubleshooting

### Issue: MCP tools not appearing in IDE

**Solution:** Restart the IDE. MCP servers are loaded at startup.

### Issue: Can't find prevention rules

**Cause:** LEARNING_LOG might not have relevant entries yet.

**Solution:** Wait 2-3 minutes after storing memories before attempting recall.

### Issue: `.mcp_config.json` not readable

**Cause:** File is gitignored and Cursor respects `.gitignore` as exclusion list.

**Solution:** This is intentional — the file contains tokens. Shell commands can still read/write it.

### Issue: Old OneDrive paths still referenced

**Solution:** All paths have been updated to `C:	emp\QuesterixFull️️`. If you find stale paths, update them.

---

## Quick Reference

### Essential Commands

```bash
# Check MCP status (in any IDE)
# Look for: pare-git, pare-npm, pare-test, pare-typescript

# Use structured git (instead of `git log`)
pare-git_log

# Use structured npm (instead of `npm install`)
pare-npm_install

# Use structured tests (instead of `npm test`)
pare-test_run

# Check prevention rules before making changes
# Read docs/LEARNING_LOG.md for relevant patterns
```

### Task Tier Shortcuts

```
// quick    → TIER S: Skip all overhead, fast micro-task
// full     → TIER L: Full bootstrap, plan/verify, session close
```

### File Locations

| Purpose | File |
|---------|------|
| Active backlog | `tasks.md` |
| Time tracking | `docs/TIME_LOG.md` |
| Session learnings | `docs/LEARNING_LOG.md` |
| Agent rules | `AGENTS.md` |
| IDE setup | `AI_WORKFLOW_SETUP.md` (this file) |

---

## Maintenance

### When Adding a New IDE

1. Add 4 Pare tools to its global MCP config
2. Copy `.cursorignore` → IDE's ignore format
3. Add reference to `AGENTS.md` and `.github/copilot-instructions.md`

### When Adding a New Project

1. Create `.cursorignore`, `.codeiumignore`, `.antigravityignore` with tailored patterns
2. Create `.vscode/mcp.json` with all 5 MCP tools
3. Create `.vscode/settings.json` with `search.exclude`
4. Create `AGENTS.md` with Tool Selection section
5. Create `.github/copilot-instructions.md`
6. Document project-specific rules in LEARNING_LOG

### When Updating MCP Tools

1. Update all 4 global IDE configs
2. Update all 4 per-project `.vscode/mcp.json` files
3. Update this documentation
4. Document in LEARNING_LOG if relevant

### When Adding a New Tech Stack

1. Create scoped rule in `.cursor/rules/{tech}.mdc`
2. Create equivalent in `.windsurf/rules/{tech}.md`
3. Define precise `globs` pattern (test with file globs)
4. Set `alwaysApply: false`
5. Keep rule under 60 lines (tech-specific details only)
6. Reference full docs in `AGENTS.md`
7. Document any prevention rules in LEARNING_LOG

### Glob Scoping Best Practices

| Practice | Why |
|----------|-----|
| **Keep global rules lean** | `**/*` rules load on every file — minimize tokens |
| **Specific globs** | `src/components/**/*.tsx` better than `**/*.tsx` |
| **alwaysApply: false** | Scoped rules only load when editing matching files |
| **Cross-reference AGENTS.md** | Don't duplicate — scoped rules are triggers |
| **Test globs** | Use IDE's rule tester to verify patterns match |

**Token Savings Calculation:**
- Old: 2 global rules × 80 lines = 160 lines on every file
- New: 2 global (40 lines) + 1 scoped (60 lines) = 100 lines on tech files
- **Savings:** 60 lines (37% reduction) per tech-specific prompt

---

## Contact & Updates

- **Documentation Owner:** AI Workflow Setup  
- **Last Full Review:** 2026-03-29  
- **Next Review:** When adding new MCP tools or projects

For questions about this setup, read this document and check `docs/LEARNING_LOG.md` for prevention rules.
