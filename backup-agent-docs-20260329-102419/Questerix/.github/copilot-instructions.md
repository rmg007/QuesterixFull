# GitHub Copilot Instructions for Questerix

> **Documentation**: `AI_WORKFLOW_SETUP.md`, `MCP_TOOLS_REFERENCE.md`, `QUICK_REFERENCE.md`

## Required: Check Prevention Rules First

**Before starting any work, check for known issues:**

- Read `docs/LEARNING_LOG.md` for prevention rules related to your task

## Tool Preferences (MANDATORY)

## 1. Git Operations

- **ALWAYS** use `pare-git` MCP tools instead of direct `git` terminal commands.
- Use `pare-git_status`, `pare-git_log`, `pare-git_diff`, etc.

## 2. Node/npm & Testing

- **ALWAYS** use `pare-npm` and `pare-test` MCP tools.
- NEVER run `npm install` or `npm test` directly in the terminal if the MCP tools are available.

## 3. TypeScript

- **ALWAYS** use `pare-typescript_check` for type-checking.

## 4. Learning Log

- **ALWAYS** add prevention rules to `docs/LEARNING_LOG.md` after fixing bugs.

These tools provide structured output that is significantly more token-efficient than raw terminal text.
