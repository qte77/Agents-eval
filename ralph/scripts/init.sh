#!/bin/bash
#
# Ralph Loop Initialization Script
#
# Validates environment and sets up required state files for Ralph loop execution
#

set -euo pipefail

# Get script directory and source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

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
        ".claude/skills/generating-prd-json-from-prd-md/SKILL.md"
        "ralph/scripts/ralph.sh"
        "ralph/docs/templates/prompt.md"
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

# Initialize progress.txt from template if it doesn't exist
initialize_progress() {
    local project="${RALPH_PROJECT:-$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")}"

    if [ ! -f "ralph/docs/progress.txt" ]; then
        log_info "Initializing progress.txt from template..."
        log_info "Project: $project"

        if [ -f "ralph/docs/templates/progress.txt.template" ]; then
            # Copy from template and replace {{DATE}} and {{PROJECT}} placeholders
            sed -e "s/{{DATE}}/$(date)/" -e "s/{{PROJECT}}/$project/" \
                ralph/docs/templates/progress.txt.template > ralph/docs/progress.txt
            log_success "progress.txt initialized from template"
        else
            log_warn "Template not found, creating default progress.txt..."
            cat > ralph/docs/progress.txt <<EOF
# Ralph Loop Progress Log

Started: $(date)
Project: $project

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
    local project="${RALPH_PROJECT:-$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")}"

    if [ ! -f "ralph/docs/prd.json" ]; then
        log_warn "prd.json not found"

        if [ -f "ralph/docs/templates/prd.json.template" ]; then
            log_info "Creating prd.json from template..."
            # Copy template and substitute placeholders
            sed -e "s/{{PROJECT}}/$project/" \
                -e "s/\"TEMPLATE\"/\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"/" \
                ralph/docs/templates/prd.json.template > ralph/docs/prd.json
            log_success "prd.json created from template"
        fi

        log_info ""
        log_info "To populate prd.json with real stories, run:"
        log_info "  make ralph_prd_json"
        log_info ""
        return 1
    else
        log_success "prd.json found"

        # Validate JSON format
        if jq empty ralph/docs/prd.json 2>/dev/null; then
            local total=$(jq '.stories | length' ralph/docs/prd.json)
            local passing=$(jq '[.stories[] | select(.passes == true)] | length' ralph/docs/prd.json)
            log_info "Status: $passing/$total stories completed"
        else
            log_error "prd.json is invalid JSON"
            return 1
        fi
    fi
}

# Verify scripts are executable (commit as 755, don't chmod at runtime)
check_executable() {
    local missing=0
    for script in ralph/scripts/ralph.sh ralph/scripts/init.sh; do
        if [ ! -x "$script" ]; then
            log_warn "$script is not executable — run: chmod +x $script"
            missing=1
        fi
    done
    [ $missing -eq 0 ] && log_success "Scripts are executable"
}

# Main
main() {
    check_prerequisites
    check_project_structure
    initialize_progress
    check_executable

    echo ""
    log_success "Ralph Loop environment initialized!"
    echo ""

    if ! check_prd_json; then
        log_warn "Run prd.json generation before starting Ralph loop"
        exit 1
    fi

    echo ""
    log_info "Ready to run Ralph loop:"
    log_info "  make ralph_run [ITERATIONS=25]"
    log_info "  or"
    log_info "  ./ralph/scripts/ralph.sh 5"
    echo ""
}

main