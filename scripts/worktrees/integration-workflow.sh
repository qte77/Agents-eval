#!/bin/bash
# Git Worktree + Subagent Integration Testing Workflow
# Usage: ./scripts/integration-workflow.sh [test-all|test-specific]

set -e

INTEGRATION_DIR="../Agents-eval-integration"
MAIN_DIR="/workspaces/Agents-eval"

echo "🔄 Starting Integration Testing Workflow"

# Function to test integration without committing
test_integration() {
    echo "📍 Switching to integration worktree..."
    cd "$INTEGRATION_DIR"
    
    echo "🔄 Pulling latest changes from main branch..."
    git fetch --all
    git reset --hard feat-evals
    
    echo "🔀 Merging branches without committing..."
    
    # Merge all feature branches without committing
    echo "  → Merging traditional-metrics..."
    git merge --no-commit --no-ff feat/traditional-metrics || {
        echo "❌ Merge conflict in traditional-metrics"
        git merge --abort
        return 1
    }
    
    echo "  → Merging large-context-llm..."
    git merge --no-commit --no-ff feat/large-context-llm || {
        echo "❌ Merge conflict in large-context-llm" 
        git merge --abort
        return 1
    }
    
    echo "  → Merging metrics-sweep..."
    git merge --no-commit --no-ff feat/metrics-sweep || {
        echo "❌ Merge conflict in metrics-sweep"
        git merge --abort
        return 1
    }
    
    echo "✅ All merges successful - testing integrated system..."
    
    # Run comprehensive tests
    echo "🧪 Running integration tests..."
    make validate || {
        echo "❌ Integration tests failed"
        git reset --hard HEAD
        return 1
    }
    
    # Test specific integration points
    echo "🔍 Testing cross-feature integration..."
    uv run pytest tests/integration/ -v || {
        echo "❌ Cross-feature integration tests failed"
        git reset --hard HEAD
        return 1
    }
    
    echo "✅ Integration tests passed!"
    
    # Reset to clean state (no commits made)
    echo "🔄 Resetting integration worktree to clean state..."
    git reset --hard HEAD
    
    echo "✅ Integration testing complete - ready for production merge"
    
    cd "$MAIN_DIR"
}

# Function to test specific feature combination
test_specific() {
    local features=("$@")
    cd "$INTEGRATION_DIR"
    
    echo "🔄 Testing specific feature combination: ${features[*]}"
    git reset --hard feat-evals
    
    for feature in "${features[@]}"; do
        echo "  → Merging $feature..."
        git merge --no-commit --no-ff "feat/$feature" || {
            echo "❌ Merge conflict in $feature"
            git merge --abort
            cd "$MAIN_DIR"
            return 1
        }
    done
    
    make quick_validate
    git reset --hard HEAD
    cd "$MAIN_DIR"
}

# Main execution
case "${1:-test-all}" in
    "test-all")
        test_integration
        ;;
    "test-specific")
        shift
        test_specific "$@"
        ;;
    *)
        echo "Usage: $0 [test-all|test-specific feature1 feature2 ...]"
        echo "Available features: traditional-metrics, large-context-llm, metrics-sweep"
        exit 1
        ;;
esac