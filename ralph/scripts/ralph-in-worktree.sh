#!/usr/bin/env bash
# Create a git worktree for a Ralph branch and cd into it.
# Usage: make ralph_worktree BRANCH=ralph/sprint-name
set -euo pipefail

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
    echo "Usage: $0 BRANCH"
    echo ""
    echo "  BRANCH   Git branch name (required)"
    echo ""
    echo "Creates a git worktree and symlinks dependency dirs from source repo."
    echo "Set RALPH_WORKTREE_SYMLINKS to override (default: .venv)."
    echo "Preferred: make ralph_worktree BRANCH=ralph/sprint-name"
    exit 0
fi

BRANCH="${1:?Usage: $0 BRANCH. Try --help.}"
WORKTREE_DIR="../$(basename "$BRANCH")"
SOURCE_DIR="$PWD"
# Directories to symlink from source repo into worktree (space-separated).
# Default: .venv (Python). Override for other stacks, e.g. "node_modules .venv"
RALPH_WORKTREE_SYMLINKS="${RALPH_WORKTREE_SYMLINKS:-.venv}"

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

# Symlink dependency directories from source repo into worktree.
# Reason: Re-link if symlink is broken (source moved) or missing entirely
for dir_name in $RALPH_WORKTREE_SYMLINKS; do
    local_source="$SOURCE_DIR/$dir_name"
    if [ -d "$local_source" ]; then
        if [ -L "$dir_name" ] && [ ! -e "$dir_name" ]; then
            rm -f "$dir_name"
            echo "Removed broken $dir_name symlink"
        fi
        if [ ! -e "$dir_name" ]; then
            ln -s "$local_source" "$dir_name"
            echo "Linked $dir_name from source repo"
        elif [ -L "$dir_name" ]; then
            echo "$dir_name symlink exists: $(readlink "$dir_name")"
        fi
    fi
done

echo ""
echo "cd $(realpath .)"
