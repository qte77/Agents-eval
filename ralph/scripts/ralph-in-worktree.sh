#!/usr/bin/env bash
# Setup git worktree branch, then run ralph.sh (env vars inherited from Make).
# Usage: make ralph_worktree BRANCH=ralph/sprint8-name [TEAMS=true MAX_ITERATIONS=50 MODEL=opus]
#   or:  RALPH_MODEL=opus MAX_ITERATIONS=50 bash ralph/scripts/ralph-in-worktree.sh BRANCH
set -euo pipefail

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
    echo "Usage: $0 BRANCH"
    echo ""
    echo "  BRANCH   Git branch name (required)"
    echo ""
    echo "Env vars (set by Make or caller):"
    echo "  RALPH_MODEL, MAX_ITERATIONS, RALPH_TEAMS, CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
    echo ""
    echo "Preferred: make ralph_worktree BRANCH=ralph/sprint8-name TEAMS=true"
    exit 0
fi

BRANCH="${1:?Usage: $0 BRANCH. Try --help.}"
WORKTREE_DIR="../$(basename "$BRANCH")"

# Create branch or confirm reuse
if git rev-parse --verify "$BRANCH" &>/dev/null; then
    echo "Branch '$BRANCH' already exists ($(git log -1 --format='%h %s' "$BRANCH"))."
    read -rp "Continue with existing branch? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }
else
    git branch "$BRANCH"
    echo "Created branch: $BRANCH"
fi

# Add worktree (skip if already linked)
if git worktree list --porcelain | grep -q "branch refs/heads/${BRANCH}$"; then
    echo "Worktree already exists: $(realpath "$WORKTREE_DIR")"
else
    git worktree add "$WORKTREE_DIR" "$BRANCH"
    echo "Worktree: $(realpath "$WORKTREE_DIR")"
fi

# Init and run Ralph inside the worktree (env vars inherited from caller)
cd "$WORKTREE_DIR"
bash ralph/scripts/init.sh
bash ralph/scripts/ralph.sh
