---
name: reviewing-code
description: Provides concise, focused code reviews matching exact task complexity requirements. Use when reviewing code quality, security, or when the user asks for code review.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [file-or-directory]
  allowed-tools: Read, Grep, Glob, WebFetch, WebSearch
---

# Review Context

- Changed files: !`git diff --name-only HEAD~1 2>/dev/null || echo "No recent commits"`
- Staged files: !`git diff --staged --name-only`

## Code Review

**Scope**: $ARGUMENTS

Delivers **focused, streamlined** code reviews matching stated task
requirements exactly. No over-analysis.

## Python Standards

See `docs/best-practices/python-best-practices.md` for comprehensive Python guidelines.

## Workflow

1. **Read task requirements** to understand expected scope
2. **Check `make validate`** passes before detailed review
3. **Match review depth** to task complexity (simple vs complex)
4. **Validate requirements** - does implementation match task scope exactly?
5. **Issue focused feedback** with specific file paths and line numbers

## Review Strategy

**Simple Tasks (100-200 lines)**: Security, compliance, requirements match,
basic quality

**Complex Tasks (500+ lines)**: Above plus architecture, performance,
comprehensive testing

**Always**: Use existing project patterns, immediate use after implementation

## Review Checklist

**Security & Compliance**:

- [ ] No security vulnerabilities (injection, XSS, etc.)
- [ ] Follows @AGENTS.md mandatory requirements
- [ ] Passes `make validate`

**Requirements Match**:

- [ ] Implements exactly what was requested
- [ ] No over-engineering or scope creep
- [ ] Appropriate complexity level

**Code Quality**:

- [ ] Follows project patterns in `src/`
- [ ] Proper type hints and docstrings
- [ ] Tests cover stated functionality

**Structural Health**:

- [ ] No function exceeds cognitive complexity threshold (suggested default: 15 per function, overridable per-project)
- [ ] No copy-paste duplication across methods (watch for repeated dispatch chains)
- [ ] File aggregate complexity — flag if trending above project norms (suggested default: 50 per file, overridable per-project)

## Output Standards

**Simple Tasks**: CRITICAL issues only, clear approval when requirements met
**Complex Tasks**: CRITICAL/WARNINGS/SUGGESTIONS with specific fixes
**All reviews**: Concise, streamlined, no unnecessary complexity analysis
