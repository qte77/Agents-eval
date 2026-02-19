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
    echo "The worktree shares the source repo's .venv via symlink."
    echo "Ralph should never run uv sync — changes to .venv belong in the source repo."
    echo ""
    echo "Preferred: make ralph_worktree BRANCH=ralph/sprint8-name TEAMS=true"
    exit 0
fi

BRANCH="${1:?Usage: $0 BRANCH. Try --help.}"
WORKTREE_DIR="../$(basename "$BRANCH")"
SOURCE_VENV="$PWD/.venv"
RALPH_SCRIPT="ralph/scripts/ralph.sh"

# Reuse existing worktree, or set up branch + worktree
WORKTREE_EXISTS=false
if git worktree list --porcelain | grep -q "branch refs/heads/${BRANCH}$"; then
    WORKTREE_EXISTS=true
fi

if [ "$WORKTREE_EXISTS" = true ]; then
    echo "Resuming worktree: $(realpath "$WORKTREE_DIR") ($(git log -1 --format='%h %s' "$BRANCH"))"
elif git rev-parse --verify "$BRANCH" &>/dev/null; then
    # Branch exists but no worktree — confirm before creating one
    echo "Branch '$BRANCH' exists but has no worktree ($(git log -1 --format='%h %s' "$BRANCH"))."
    read -rp "Create worktree and continue? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }
    git worktree add "$WORKTREE_DIR" "$BRANCH"
    echo "Worktree: $(realpath "$WORKTREE_DIR")"
else
    git branch "$BRANCH"
    echo "Created branch: $BRANCH"
    git worktree add "$WORKTREE_DIR" "$BRANCH"
    echo "Worktree: $(realpath "$WORKTREE_DIR")"
fi

# Init and run Ralph inside the worktree (env vars inherited from caller)
cd "$WORKTREE_DIR"

# Symlink source repo's .venv — both repos share one venv in real time.
# Ralph should never run uv sync.
if [ -d "$SOURCE_VENV" ] && [ ! -e .venv ]; then
    ln -s "$SOURCE_VENV" .venv
fi
env -u VIRTUAL_ENV bash "$RALPH_SCRIPT"
