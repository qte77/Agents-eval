---
title: Commit all changes with a generated Message
name: commit-with-message
description: Generate commit message, pause for approval, then commit all changes. This slash command automates the commit workflow while giving you control over the commit message.
argument-hint: (no arguments needed)
tools: Bash, Read, Glob, Grep, MultiEdit
---

I'll help you commit all your changes with a generated commit message. Here's what I'll do:

1. **Generate a commit message** by analyzing all uncommitted changes
2. **Pause for your approval** - you can review and edit the message
3. **Commit all changes** with the approved message
4. **Confirm completion**

Let me start by analyzing your uncommitted changes to generate an appropriate commit message.

## Step 1: Comprehensive Change Analysis and Commit Message Generation

I'll use Claude Code's native tools to analyze your changes:

**Git Analysis using Bash tool:**

- `git status --porcelain` - Get all changed files with status indicators
- `git diff --staged` - Show detailed diff of staged changes
- `git diff` - Show detailed diff of unstaged changes
- `git log --oneline -10` - Show recent commit messages for context

**File Analysis Process:**

For each file type, I will use these Claude Code native tools:

1. **Modified Files (M)**:
   - **Bash** tool: `git diff <file>` to see specific changes
   - **Read** tool: Examine current file content if needed for context
   - Identify modifications (features, fixes, refactoring)

2. **Untracked Files (??)**:
   - **Read** tool: Examine file content and purpose
   - **Glob** tool: Find related files by pattern if needed
   - Categorize as: scripts, configs, docs, agents, tests, etc.

3. **Deleted Files (D)**:
   - **Bash** tool: `git show --name-status HEAD` to see what was removed
   - Note deletion context and reasoning

4. **Pattern Recognition using native tools**:
   - **Grep** tool: Search for related patterns across the codebase
   - **Glob** tool: Identify file types by pattern matching
   - Analyze change patterns and relationships

Based on the comprehensive analysis above, here's my suggested commit message:

## Step 2: Pause for Approval

**Please review the commit message above.**

- **Approve**: Type "yes", "y", "commit", or "go ahead" to proceed
- **Edit**: Provide your preferred commit message
- **Cancel**: Type "no", "cancel", or "stop" to abort

**Your response:** _[Waiting for your input]_

## Step 3: Commit Changes

Once approved, I'll run:

**Using Bash tool for git operations:**

- `git add .` - Add all changes to staging
- `git commit -m "[approved message]"` with automated footer:
  - Co-Authored-By: Claude <noreply@anthropic.com>
- `git status` - Confirm commit success

## Step 4: Completion

**Done!** All changes have been committed successfully.

**Next steps you might want:**

- `git push` to push to remote
- `git log --oneline -1` to verify the commit
- Continue with your next development task
