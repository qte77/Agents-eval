#!/bin/bash
# Git Worktree Setup for Parallel Subagent Development
# Usage: ./scripts/setup-worktrees.sh

set -e

echo "🔄 Setting up Git Worktrees for Parallel Development"

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d ".git" ]]; then
    echo "❌ Must be run from the root of Agents-eval repository"
    exit 1
fi

# Get current branch as base
BASE_BRANCH=$(git branch --show-current)
echo "📍 Using base branch: $BASE_BRANCH"

# Create worktrees for parallel development
echo "🌳 Creating worktrees..."

# Traditional Metrics Refactoring
if [[ ! -d "../Agents-eval-metrics" ]]; then
    echo "  → Creating traditional-metrics worktree..."
    git worktree add --track -b feat/traditional-metrics ../Agents-eval-metrics $BASE_BRANCH
    echo "    ✅ Created: /workspaces/Agents-eval-metrics (feat/traditional-metrics)"
else
    echo "  ⚠️  Worktree already exists: ../Agents-eval-metrics"
fi

# Large Context LLM Integration  
if [[ ! -d "../Agents-eval-llm-context" ]]; then
    echo "  → Creating large-context-llm worktree..."
    git worktree add --track -b feat/large-context-llm ../Agents-eval-llm-context $BASE_BRANCH
    echo "    ✅ Created: /workspaces/Agents-eval-llm-context (feat/large-context-llm)"
else
    echo "  ⚠️  Worktree already exists: ../Agents-eval-llm-context"
fi

# Metrics Sweep Engine
if [[ ! -d "../Agents-eval-sweep" ]]; then
    echo "  → Creating metrics-sweep worktree..."
    git worktree add --track -b feat/metrics-sweep ../Agents-eval-sweep $BASE_BRANCH  
    echo "    ✅ Created: /workspaces/Agents-eval-sweep (feat/metrics-sweep)"
else
    echo "  ⚠️  Worktree already exists: ../Agents-eval-sweep"
fi

# Integration Testing Worktree
if [[ ! -d "../Agents-eval-integration" ]]; then
    echo "  → Creating integration-test worktree..."
    git worktree add --track -b feat/integration-test ../Agents-eval-integration $BASE_BRANCH
    echo "    ✅ Created: /workspaces/Agents-eval-integration (feat/integration-test)"
else
    echo "  ⚠️  Worktree already exists: ../Agents-eval-integration"
fi

echo ""
echo "📋 Worktree Summary:"
git worktree list

echo ""
echo "🎯 Next Steps:"
echo "1. Start parallel development:"
echo "   cd /workspaces/Agents-eval-metrics     # Traditional metrics"
echo "   cd /workspaces/Agents-eval-llm-context # Large context LLM"  
echo "   cd /workspaces/Agents-eval-sweep       # Metrics sweep engine"
echo ""
echo "2. Use subagents in each worktree:"
echo "   claude --print 'Task(\"[description]\", subagent_type=\"[agent-type]\")'"
echo ""
echo "3. Test integration:"
echo "   ./scripts/integration-workflow.sh test-all"
echo ""
echo "4. Clean up when done:"
echo "   ./scripts/cleanup-worktrees.sh"

echo ""
echo "✅ Worktree setup complete!"