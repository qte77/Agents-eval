#!/usr/bin/env bash
# Create a git worktree for a Ralph branch and cd into it.
# Usage: make ralph_worktree BRANCH=ralph/sprint-name
set -euo pipefail

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
    echo "Usage: $0 BRANCH"
    echo ""
    echo "  BRANCH   Git branch name (required)"
    echo ""
    echo "Creates a git worktree and symlinks the source repo's .venv."
    echo "Preferred: make ralph_worktree BRANCH=ralph/sprint-name"
    exit 0
fi

BRANCH="${1:?Usage: $0 BRANCH. Try --help.}"
WORKTREE_DIR="../$(basename "$BRANCH")"
SOURCE_VENV="$PWD/.venv"

# Reuse existing worktree, or set up branch + worktree
WORKTREE_EXISTS=false
if git worktree list --porcelain | grep -q "branch refs/heads/${BRANCH}$"; then
    WORKTREE_EXISTS=true
fi

if [ "$WORKTREE_EXISTS" = true ]; then
    echo "Worktree already exists: $(realpath "$WORKTREE_DIR") ($(git log -1 --format='%h %s' "$BRANCH"))"
elif git rev-parse --verify "$BRANCH" &>/dev/null; then
    # Branch exists but no worktree — confirm before creating one
    echo "Branch '$BRANCH' exists but has no worktree ($(git log -1 --format='%h %s' "$BRANCH"))."
    read -rp "Create worktree and continue? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }
    git worktree add "$WORKTREE_DIR" "$BRANCH"
    echo "Worktree created: $(realpath "$WORKTREE_DIR")"
else
    git branch "$BRANCH"
    echo "Created branch: $BRANCH"
    git worktree add "$WORKTREE_DIR" "$BRANCH"
    echo "Worktree created: $(realpath "$WORKTREE_DIR")"
fi

cd "$WORKTREE_DIR"

# Symlink source repo's .venv — both repos share one venv in real time.
if [ -d "$SOURCE_VENV" ] && [ ! -e .venv ]; then
    ln -s "$SOURCE_VENV" .venv
    echo "Linked .venv from source repo"
fi

echo ""
echo "cd $(realpath .)"
