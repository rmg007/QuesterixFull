# MCP Tools Quick Reference

> **One-page reference for all configured MCP tools**

---

## Learning Log (Prevention Rules)

**Purpose:** Prevent repeated bugs by documenting patterns and solutions

### Tools

| Action | Use When | Location |
|--------|----------|----------|
| Read LEARNING_LOG | Before making changes | `docs/LEARNING_LOG.md` |
| Add prevention rule | After fixing a bug | `docs/LEARNING_LOG.md` |
| Check cross-project rules | Working on shared patterns | `Questerix/docs/LEARNING_LOG.md` |

### Examples

```markdown
# Before making changes, check for relevant prevention rules:
# Read docs/LEARNING_LOG.md and search for related patterns

# After fixing a bug, add a prevention rule:
## [2026-03-29] SQLite Migration Fix
- **Root Cause**: Missing default value for non-nullable column
- **Prevention Rule**: ALWAYS use withDefault() for non-nullable columns in Drift migrations
```

---

## Pare Git

**Purpose:** Structured git operations (92% token reduction vs `git log`)

### Tools

| Tool | Replaces | Output |
|------|----------|--------|
| `pare-git_status` | `git status` | Working tree status with branch, staged, modified, untracked |
| `pare-git_log` | `git log` | Commit history as structured data |
| `pare-git_diff` | `git diff` | File-level diff stats with optional full patch |
| `pare-git_branch` | `git branch` | List, create, or delete branches |
| `pare-git_show` | `git show` | Commit details and diff stats |
| `pare-git_add` | `git add` | Stage files |
| `pare-git_commit` | `git commit` | Create commits |
| `pare-git_push` | `git push` | Push to remote |
| `pare-git_pull` | `git pull` | Pull from remote |
| `pare-git_checkout` | `git checkout` | Switch branches |

### Examples

```javascript
// Get last 5 commits (structured, not walls of text)
pare-git_log({ args: ["-n", "5"] })

// Check what's modified
pare-git_status()

// See diff stats
pare-git_diff({ args: ["--stat"] })
```

---

## Pare NPM

**Purpose:** Structured npm operations (83% token reduction vs `npm install` output)

### Tools

| Tool | Replaces | Use For |
|------|----------|---------|
| `pare-npm_install` | `npm install` | Installing dependencies cleanly |
| `pare-npm_list` | `npm list` | Listing installed packages |
| `pare-npm_outdated` | `npm outdated` | Checking for updates |
| `pare-npm_info` | `npm info` | Package information |
| `pare-npm_run` | `npm run` | Running scripts |

### Examples

```javascript
// Install packages (clean output)
pare-npm_install({ args: ["--save", "lodash"] })

// Check for outdated packages
pare-npm_outdated()

// Run build script
pare-npm_run({ args: ["build"] })
```

---

## Pare Test

**Purpose:** Structured test output (80% token reduction vs test runner output)

### Tools

| Tool | Replaces | Use For |
|------|----------|---------|
| `pare-test_run` | `npm test`, `vitest`, `jest`, `pytest` | Running tests |
| `pare-test_coverage` | Test coverage reports | Getting coverage data |

**Auto-detection:** Supports vitest, jest, pytest, and more automatically.

### Examples

```javascript
// Run all tests (structured output)
pare-test_run()

// Run specific test file
pare-test_run({ args: ["src/components/Button.test.tsx"] })

// Get coverage
pare-test_coverage()
```

**Note for Flutter:** The student app uses `flutter test` directly (not pare-test). Never run full suite locally — use targeted paths:
```bash
flutter test test/path/to/specific_test.dart
```

---

## Pare TypeScript

**Purpose:** Structured TypeScript errors (significant reduction vs `tsc` output)

### Tools

| Tool | Replaces | Use For |
|------|----------|---------|
| `pare-typescript_check` | `tsc` | Type-checking with clean output |

### Examples

```javascript
// Check TypeScript (structured errors)
pare-typescript_check()
```

---

## Comparison: Raw CLI vs Pare MCP

### Git Log Example

**Raw CLI (`git log --stat`):**
```
commit a1b2c3d4 (HEAD -> main, origin/main)
Author: Developer <dev@example.com>
Date:   Mon Mar 29 10:00:00 2026

    Fix navigation bug

 admin-panel/src/components/Nav.tsx | 12 +++++++++++-
 1 file changed, 11 insertions(+), 1 deletion(-)

commit b2c3d4e5
Author: Developer <dev@example.com>
Date:   Mon Mar 29 09:00:00 2026

    Add user profile

 admin-panel/src/pages/Profile.tsx | 45 +++++++++++++++++++++++++++++
 1 file changed, 45 insertions(+)

[... hundreds more lines ...]
```

**Pare MCP (`pare-git_log`):**
```json
{
  "commits": [
    {
      "hash": "a1b2c3d4",
      "message": "Fix navigation bug",
      "author": "Developer",
      "date": "2026-03-29",
      "filesChanged": 1,
      "insertions": 11,
      "deletions": 1
    },
    {
      "hash": "b2c3d4e5",
      "message": "Add user profile",
      "author": "Developer",
      "date": "2026-03-29",
      "filesChanged": 1,
      "insertions": 45,
      "deletions": 0
    }
  ]
}
```

**Token savings:** ~92% (4,992 tokens → 382 tokens)

---

## When to Use Which

### Always Use Pare MCP

| Situation | Use | Never Use |
|-----------|-----|-----------|
| Check git status | `pare-git_status` | `git status` |
| View commit history | `pare-git_log` | `git log` |
| See what changed | `pare-git_diff` | `git diff` |
| Install packages | `pare-npm_install` | `npm install` |
| Run tests | `pare-test_run` | `npm test` |
| Check types | `pare-typescript_check` | `tsc` |
| Prevention rules | `LEARNING_LOG.md` | (no equivalent) |

### Still Use Raw CLI

| Situation | Use | Why |
|-----------|-----|-----|
| Complex git operations | `git rebase -i` | Interactive, not structured |
| One-off commands | `git stash` | Not worth MCP overhead |
| Flutter testing | `flutter test` | Pare doesn't support Flutter |
| Build commands | `npm run build` | If not supported by pare-npm |

---

## IDE-Specific Notes

### Cursor AI

- All tools appear in MCP panel
- Rules in `.cursor/rules/` enforce tool usage automatically

### Windsurf

- Tools appear in Cascade panel
- Respects `.codeiumignore` for indexing

### Antigravity IDE

- Tools available via Gemini integration
- Respects `.antigravityignore` for focus control

### VS Code Copilot

- Tools in `.vscode/mcp.json` loaded per-project
- Also reads from global `~/AppData/Roaming/Code/User/mcp.json`

---

## Automation Reminder

**You don't need to remember this.** All `AGENTS.md` files and Cursor rules enforce:

```markdown
## Tool Selection & Token Savings (MANDATORY)

1. **Git Operations**: NEVER use direct shell commands... ALWAYS use `pare-git`
2. **Node/npm**: NEVER use direct shell commands... ALWAYS use `pare-npm` and `pare-test`
3. **TypeScript**: ALWAYS use `pare-typescript_check`
4. **Learning Log**: Check `docs/LEARNING_LOG.md` before changes, add rules after fixes
```

---

## See Also

- Full setup: `AI_WORKFLOW_SETUP.md`
- Project rules: `AGENTS.md` (per-project)
- Quick commands: `QUICK_REFERENCE.md`
