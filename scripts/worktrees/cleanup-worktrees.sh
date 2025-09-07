#!/bin/bash
# Cleanup Git Worktrees after Development
# Usage: ./scripts/cleanup-worktrees.sh [--force]

set -e

FORCE_CLEANUP=false
if [[ "$1" == "--force" ]]; then
    FORCE_CLEANUP=true
fi

echo "🧹 Cleaning up Git Worktrees"

# Function to safely remove worktree
cleanup_worktree() {
    local worktree_path="$1"
    local branch_name="$2"
    
    if [[ -d "$worktree_path" ]]; then
        echo "  → Checking worktree: $worktree_path"
        
        # Check for uncommitted changes
        cd "$worktree_path"
        if ! git diff --quiet || ! git diff --cached --quiet; then
            if [[ "$FORCE_CLEANUP" == "true" ]]; then
                echo "    ⚠️  Discarding uncommitted changes in $worktree_path"
                git reset --hard HEAD
                git clean -fd
            else
                echo "    ❌ Uncommitted changes in $worktree_path"
                echo "       Use --force to discard or commit changes first"
                return 1
            fi
        fi
        
        # Return to main directory
        cd "/workspaces/Agents-eval"
        
        # Remove worktree
        echo "    🗑️  Removing worktree: $worktree_path"
        git worktree remove "$worktree_path"
        
        # Delete branch if it exists
        if git branch --list | grep -q "$branch_name"; then
            echo "    🗑️  Deleting branch: $branch_name"
            git branch -D "$branch_name"
        fi
        
        echo "    ✅ Cleaned up: $worktree_path"
    else
        echo "  ℹ️  Worktree not found: $worktree_path"
    fi
}

echo "📋 Current worktrees:"
git worktree list

echo ""
echo "🧹 Starting cleanup..."

# Cleanup each worktree
cleanup_worktree "../Agents-eval-metrics" "feat/traditional-metrics"
cleanup_worktree "../Agents-eval-llm-context" "feat/large-context-llm"  
cleanup_worktree "../Agents-eval-sweep" "feat/metrics-sweep"
cleanup_worktree "../Agents-eval-integration" "feat/integration-test"

echo ""
echo "📋 Remaining worktrees:"
git worktree list

echo ""
echo "✅ Worktree cleanup complete!"