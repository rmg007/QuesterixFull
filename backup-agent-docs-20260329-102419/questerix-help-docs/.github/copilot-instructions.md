# GitHub Copilot Instructions for Questerix Help Docs

> **Documentation**: `../AI_WORKFLOW_SETUP.md`, `../MCP_TOOLS_REFERENCE.md`, `../QUICK_REFERENCE.md`

## Required: Check Prevention Rules First

**Before starting any work, check for known issues:**
- Read `../Questerix/docs/LEARNING_LOG.md` for cross-project prevention rules

## Tool Preferences (MANDATORY)

## 1. Git Operations
- **ALWAYS** use `pare-git` MCP tools instead of direct `git` terminal commands.

## 2. Node/npm
- **ALWAYS** use `pare-npm` and `pare-test` MCP tools.
- NEVER run `npm install` or `npm test` directly in the terminal.

## 3. Learning Log
- **ALWAYS** document issues in the main project's LEARNING_LOG after fixing bugs.
