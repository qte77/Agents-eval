#!/bin/bash
#
# Ralph Loop Initialization Script
#
# Validates environment and sets up required state files for Ralph loop execution
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

log_info "Initializing Ralph Loop environment..."

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=0

    # Check for claude command
    if ! command -v claude &> /dev/null; then
        log_error "claude command not found (Claude Code required)"
        missing=1
    else
        log_success "Claude Code CLI found"
    fi

    # Check for jq
    if ! command -v jq &> /dev/null; then
        log_error "jq not found (required for JSON processing)"
        log_info "Install: apt-get install jq (or brew install jq)"
        missing=1
    else
        log_success "jq found"
    fi

    # Check for git
    if ! command -v git &> /dev/null; then
        log_error "git not found"
        missing=1
    else
        log_success "git found"
    fi

    # Check for make
    if ! command -v make &> /dev/null; then
        log_error "make not found"
        missing=1
    else
        log_success "make found"
    fi

    if [ $missing -eq 1 ]; then
        log_error "Missing required dependencies"
        exit 1
    fi
}

# Verify project structure
check_project_structure() {
    log_info "Verifying project structure..."

    # Check for required files
    local required_files=(
        "AGENTS.md"
        "CONTRIBUTING.md"
        "docs/PRD.md"
        "Makefile"
        ".claude/skills/generating-prd/SKILL.md"
        ".claude/scripts/ralph/ralph.sh"
        ".claude/scripts/ralph/prompt.md"
    )

    local missing=0
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            missing=1
        fi
    done

    if [ $missing -eq 1 ]; then
        log_error "Project structure incomplete"
        exit 1
    fi

    log_success "Project structure validated"
}

# Create state directories
create_state_dirs() {
    log_info "Creating state directories..."

    mkdir -p docs/ralph

    log_success "State directories created"
}

# Initialize progress.txt from template if it doesn't exist
initialize_progress() {
    if [ ! -f "docs/ralph/progress.txt" ]; then
        log_info "Initializing progress.txt from template..."

        if [ -f ".claude/templates/ralph/progress.txt.template" ]; then
            # Copy from template and replace {{DATE}} placeholder
            sed "s/{{DATE}}/$(date)/" .claude/templates/ralph/progress.txt.template > docs/ralph/progress.txt
            log_success "progress.txt initialized from template"
        else
            log_warn "Template not found, creating default progress.txt..."
            cat > docs/ralph/progress.txt <<EOF
# Ralph Loop Progress Log

Started: $(date)
Project: Agents-eval

This file tracks the progress of Ralph loop autonomous execution.
Each iteration appends its results here.

---

EOF
            log_success "progress.txt initialized (default)"
        fi
    else
        log_info "progress.txt already exists"
    fi
}

# Check if prd.json exists, create from template if not
check_prd_json() {
    if [ ! -f "docs/ralph/prd.json" ]; then
        log_warn "prd.json not found"

        if [ -f ".claude/templates/ralph/prd.json.template" ]; then
            log_info "Creating prd.json from template..."
            cp .claude/templates/ralph/prd.json.template docs/ralph/prd.json
            # Update timestamp
            sed -i "s/\"TEMPLATE\"/\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"/" docs/ralph/prd.json
            log_success "prd.json created from template"
        fi

        log_info ""
        log_info "To populate prd.json with real stories, run:"
        log_info "  claude -p"
        log_info "  Then ask: 'Use generating-prd skill to create prd.json from PRD.md'"
        log_info ""
        return 1
    else
        log_success "prd.json found"

        # Validate JSON format
        if jq empty docs/ralph/prd.json 2>/dev/null; then
            local total=$(jq '.stories | length' docs/ralph/prd.json)
            local passing=$(jq '[.stories[] | select(.passes == true)] | length' docs/ralph/prd.json)
            log_info "Status: $passing/$total stories completed"
        else
            log_error "prd.json is invalid JSON"
            return 1
        fi
    fi
}

# Make scripts executable
make_executable() {
    log_info "Making scripts executable..."
    chmod +x .claude/scripts/ralph/ralph.sh
    chmod +x .claude/scripts/ralph/init.sh
    log_success "Scripts are executable"
}

# Main
main() {
    check_prerequisites
    check_project_structure
    create_state_dirs
    initialize_progress
    make_executable

    echo ""
    log_success "Ralph Loop environment initialized!"
    echo ""

    if ! check_prd_json; then
        log_warn "Run prd.json generation before starting Ralph loop"
        exit 1
    fi

    echo ""
    log_info "Ready to run Ralph loop:"
    log_info "  make ralph ITERATIONS=5"
    log_info "  or"
    log_info "  ./.claude/scripts/ralph/ralph.sh 5"
    echo ""
}

main
