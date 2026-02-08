---
name: committing-staged-with-message
description: Generate commit message for staged changes, pause for approval, then commit. Stage files first with `git add`, then run this skill.
compatibility: Designed for Claude Code
metadata:
  model: haiku
  argument-hint: (no arguments needed)
  disable-model-invocation: true
  allowed-tools: Bash, Read, Glob, Grep
---

# Commit staged with Generated Message

## Step 1: Analyze Staged Changes

Run these commands using the Bash tool to gather context:

- `git diff --staged --name-only` - List staged files
- `git diff --staged --stat` - Diff stats summary
- `git log --oneline -5` - Recent commit style
- `git diff --staged` - Review detailed staged changes

## Step 2: Generate Commit Message

Use the Read tool to check `.gitmessage` for commit message format and syntax.

## Step 3: Pause for Approval

**Please review the commit message.**

- **Approve**: "yes", "y", "commit", "go ahead"
- **Edit**: Provide your preferred message
- **Cancel**: "no", "cancel", "stop"

## Step 4: Commit

Once approved:

- `git commit -m "[message]"` - Commit staged changes with approved message
- `git status` - Verify success
