#!/bin/bash
#
# Ralph Loop - Autonomous iteration script
#
# Usage: ./ralph/scripts/ralph.sh
#
# Environment variables:
#   RALPH_MODEL         - Claude model to use (default: sonnet)
#   MAX_ITERATIONS      - Maximum loop iterations (default: 10)
#   REQUIRE_REFACTOR    - Require [REFACTOR] commit (default: false)
#   RALPH_BASELINE_MODE - Baseline-aware test validation (default: true)
#
# This script orchestrates autonomous task execution by:
# 1. Reading prd.json for incomplete stories
# 2. Executing single story via Claude Code (with TDD workflow)
# 3. Verifying TDD commits (RED + GREEN + optional REFACTOR phases)
# 4. Running quality checks (make validate)
# 5. Updating prd.json status on success
# 6. Appending learnings to progress.txt
# 7. Logging all output to logs/ralph/YYYY-MM-DD_HH:MM:SS.log
#
# TDD Workflow Enforcement:
# - Agent must make separate commits for RED (tests) and GREEN (implementation)
# - REFACTOR phase is optional (controlled by REQUIRE_REFACTOR variable)
# - Script verifies commits were made in correct order: RED → GREEN → REFACTOR
# - Checks for [RED], [GREEN], and [REFACTOR]/[BLUE] markers in commit messages
#
# NOTE: This script currently enforces TDD only (check_tdd_commits).
# Supporting BDD (Given-When-Then) would require refactoring the commit
# verification logic to accept alternative markers and workflow patterns.
# Future: Add RALPH_TEST_WORKFLOW=tdd|bdd switch to select verification strategy.
#
# NOTE: Context management during story execution relies on Claude Code's
# built-in automatic summarization (kicks in when context window fills up).
# The custom /compacting-context skill forks a separate Explore agent with
# file reads — overkill for mid-story compaction. Similarly /researching-codebase
# forks an Explore agent; prefer inline file reads in the prompt template instead.
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/baseline.sh"

# Helpers
commit_count() { git rev-list --count HEAD 2>/dev/null; }

commit_state_files() {
    local msg="$1"
    log_info "Committing state files..."
    git add "$PRD_JSON" "$PROGRESS_FILE" 2>/dev/null || log_warn "Could not stage state files (may be ignored)"
    git commit -m "$msg" || log_warn "No state changes to commit"
}

# Configuration
RALPH_MODEL=${RALPH_MODEL:-"sonnet"}  # Model: sonnet, opus, haiku
MAX_ITERATIONS=${MAX_ITERATIONS:-25}
REQUIRE_REFACTOR=${REQUIRE_REFACTOR:-false}  # Require [REFACTOR] commit (true/false)
PRD_JSON="ralph/docs/prd.json"
PROGRESS_FILE="ralph/docs/progress.txt"
PROMPT_FILE="ralph/docs/templates/prompt.md"
MAX_RETRIES=3
RALPH_BASELINE_MODE=${RALPH_BASELINE_MODE:-true}
BASELINE_FILE="/tmp/claude/ralph_baseline_failures.txt"

# Set up logging
LOG_DIR="logs/ralph"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d_%H:%M:%S).log"
mkdir -p "$LOG_DIR"

# Redirect all output to both console and log file
exec > >(tee -a "$LOG_FILE") 2>&1

# Validate environment
validate_environment() {
    log_info "Validating environment..."

    if [ ! -f "$PRD_JSON" ]; then
        log_error "prd.json not found at $PRD_JSON"
        log_info "Run 'claude -p' and ask: 'Use generating-prd skill to create prd.json'"
        exit 1
    fi

    if [ ! -f "$PROGRESS_FILE" ]; then
        log_warn "progress.txt not found, creating..."
        mkdir -p "$(dirname "$PROGRESS_FILE")"
        echo "# Ralph Loop Progress" > "$PROGRESS_FILE"
        echo "Started: $(_ts)" >> "$PROGRESS_FILE"
        echo "" >> "$PROGRESS_FILE"
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi

    log_info "Environment validated successfully"
}

# Get next incomplete story from prd.json (respects depends_on)
get_next_story() {
    # Get all completed story IDs
    local completed=$(jq -r '[.stories[] | select(.passes == true) | .id] | @json' "$PRD_JSON")

    # Find first incomplete story where all depends_on are satisfied
    jq -r --argjson done "$completed" '
      .stories[]
      | select(.passes == false)
      | select((.depends_on // []) - $done | length == 0)
      | .id
    ' "$PRD_JSON" | sed -n '1p'
}

# Get story details
get_story_details() {
    local story_id="$1"
    jq -r --arg id "$story_id" '.stories[] | select(.id == $id) | "\(.title)|\(.description)"' "$PRD_JSON"
}

# Update story status in prd.json
update_story_status() {
    local story_id="$1"
    local status="$2"
    local timestamp=$(_ts)

    jq --arg id "$story_id" \
       --arg status "$status" \
       --arg timestamp "$timestamp" \
       '(.stories[] | select(.id == $id) | .passes) |= ($status == "true") |
        (.stories[] | select(.id == $id) | .completed_at) |= (if $status == "true" then $timestamp else null end)' \
       "$PRD_JSON" > "${PRD_JSON}.tmp"

    mv "${PRD_JSON}.tmp" "$PRD_JSON"
}

# Append to progress log
log_progress() {
    local iteration="$1"
    local story_id="$2"
    local status="$3"
    local notes="$4"

    {
        echo "## Iteration $iteration - $(_ts)"
        echo "Story: $story_id"
        echo "Status: $status"
        echo "Notes: $notes"
        echo ""
    } >> "$PROGRESS_FILE"
}

# Log heartbeat with phase detection while story executes in background.
# Scans commits for the current story within the current sprint only
# (using prd.json generated timestamp as sprint boundary).
# Args:
#   $1 - story ID
monitor_story_progress() {
    local story_id="$1"
    local sprint_start
    sprint_start=$(jq -r '.generated' "$PRD_JSON")

    while sleep 60; do
        local elapsed=$(($(date +%s) - RALPH_STORY_START))
        local phase="RED"
        local story_commits
        story_commits=$(git log --grep="$story_id" --since="$sprint_start" --oneline 2>/dev/null)

        if [ -n "$story_commits" ]; then
            if echo "$story_commits" | grep -q "\[GREEN\]"; then phase="REFACTOR"
            elif echo "$story_commits" | grep -q "\[RED\]"; then phase="GREEN"
            fi
        fi
        log_info "  >> [$story_id] phase: $phase | elapsed: $(fmt_elapsed $elapsed)"
    done
}

# Execute single story via Claude Code
execute_story() {
    local story_id="$1"
    local details="$2"
    local title=$(echo "$details" | cut -d'|' -f1)
    local description=$(echo "$details" | cut -d'|' -f2)

    log_info "Executing story: $story_id - $title"

    # Create prompt for this iteration
    local iteration_prompt=$(mktemp)
    cat "$PROMPT_FILE" > "$iteration_prompt"
    {
        echo ""
        echo "## Current Story"
        echo "**ID**: $story_id"
        echo "**Title**: $title"
        echo "**Description**: $description"
        echo ""
        echo "Read prd.json for full acceptance criteria and expected files."
    } >> "$iteration_prompt"

    # Mark log position before agent execution
    local log_start=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")

    # Track story start time for monitor
    RALPH_STORY_START=$(date +%s)

    # Record commit count for monitor
    local commits_before=$(commit_count)

    # Execute via Claude Code
    log_info "Running Claude Code with story context..."
    log_info "  Story: $story_id - $title"
    log_info "  Model: $RALPH_MODEL"
    log_info "  Prompt: $iteration_prompt ($(wc -l < "$iteration_prompt") lines)"
    log_info "  PRD: $PRD_JSON"

    # Start background progress monitor
    monitor_story_progress "$story_id" &
    local monitor_pid=$!

    local claude_exit=0
    if cat "$iteration_prompt" | claude -p --dangerously-skip-permissions --model "$RALPH_MODEL"; then
        claude_exit=0
    else
        claude_exit=$?
    fi

    # Stop background monitor
    kill "$monitor_pid" 2>/dev/null; wait "$monitor_pid" 2>/dev/null || true

    local story_elapsed=$(($(date +%s) - RALPH_STORY_START))
    log_info "Story execution finished in $(fmt_elapsed $story_elapsed)"

    if [ $claude_exit -eq 0 ]; then
        # Check if agent reported story already complete
        if detect_already_complete "$log_start"; then
            log_info "Agent detected story is already complete"
            rm "$iteration_prompt"
            return 2  # Special return code for pre-completion
        fi
        rm "$iteration_prompt"
        return 0
    else
        rm "$iteration_prompt"
        return 1
    fi
}

# Detect if agent output indicates story is already complete.
# Prefers explicit sentinel file; falls back to scanning agent output.
detect_already_complete() {
    local start_line="$1"
    local sentinel="/tmp/claude/ralph_story_complete"

    if [ -f "$sentinel" ]; then
        rm -f "$sentinel"
        return 0
    fi

    # Fallback: scan agent output for completion phrases
    tail -n +$((start_line + 1)) "$LOG_FILE" 2>/dev/null \
        | grep -qi "already complete\|already implemented\|no further implementation.*required" || return 1
}

# Run quality checks (dispatches to baseline-aware or original mode)
# Args:
#   $1 - Story ID (for baseline refresh metadata)
run_quality_checks() {
    local story_id="${1:-unknown}"

    if [ "$RALPH_BASELINE_MODE" = "true" ]; then
        run_quality_checks_baseline "$BASELINE_FILE" "$story_id"
    else
        log_info "Running quality checks (make validate)..."
        if make --no-print-directory validate 2>&1 | tee /tmp/claude/ralph_validate.log; then
            log_info "Quality checks passed"
            return 0
        else
            log_error "Quality checks failed"
            cat /tmp/claude/ralph_validate.log
            return 1
        fi
    fi
}

# Check that TDD commits were made during story execution
# Verifies: at least 2 commits, [RED] and [GREEN] markers, [REFACTOR] optional, correct order
# Also accepts REFACTOR-only iterations when prior RED+GREEN exist (quality fix-up)
check_tdd_commits() {
    local story_id="$1"
    local commits_before="$2"

    log_info "Checking TDD commits (REQUIRE_REFACTOR=$REQUIRE_REFACTOR)..."

    local commits_after=$(commit_count)
    local new_commits=$((commits_after - commits_before))

    if [ $new_commits -eq 0 ]; then
        log_error "No commits made during story execution"
        return 1
    fi

    local recent_commits=$(git log --oneline -n $new_commits)
    log_info "Found $new_commits new commit(s) for $story_id:"

    # Report detected phases with their commits
    local red_commit=$(echo "$recent_commits" | grep "\[RED\]" | sed -n '1p')
    local green_commit=$(echo "$recent_commits" | grep "\[GREEN\]" | sed -n '1p')
    local refactor_commit=$(echo "$recent_commits" | grep -E "\[REFACTOR\]|\[BLUE\]" | sed -n '1p')

    [ -n "$red_commit" ] && log_info "  [RED]      $red_commit" || log_warn "  [RED]      not found"
    [ -n "$green_commit" ] && log_info "  [GREEN]    $green_commit" || log_warn "  [GREEN]    not found"
    [ -n "$refactor_commit" ] && log_info "  [REFACTOR] $refactor_commit" || log_info "  [REFACTOR] skipped"

    # REFACTOR-only iteration: agent is fixing quality issues after a prior RED+GREEN
    if [ -z "$red_commit" ] && [ -z "$green_commit" ] && [ -n "$refactor_commit" ]; then
        # Reason: --grep + --all-match requires both patterns in the same commit message
        local prior_red=$(git log --grep="\[RED\]" --grep="$story_id" --all-match --format="%h" -1 2>/dev/null)
        local prior_green=$(git log --grep="\[GREEN\]" --grep="$story_id" --all-match --format="%h" -1 2>/dev/null)

        if [ -n "$prior_red" ] && [ -n "$prior_green" ]; then
            log_info "REFACTOR-only: prior RED ($prior_red) + GREEN ($prior_green) found"
            return 0
        fi
        log_error "REFACTOR-only commit but no prior [RED]+[GREEN] for $story_id"
        return 1
    fi

    # Standard path: require RED + GREEN in current iteration
    local min_commits=2
    if [ "$REQUIRE_REFACTOR" = "true" ]; then
        min_commits=3
    fi

    if [ $new_commits -lt $min_commits ]; then
        log_error "Expected at least $min_commits commits (RED + GREEN), found $new_commits"
        return 1
    fi

    if [ -z "$red_commit" ] || [ -z "$green_commit" ]; then
        log_error "Missing [RED] and/or [GREEN] markers"
        return 1
    fi

    if [ "$REQUIRE_REFACTOR" = "true" ] && [ -z "$refactor_commit" ]; then
        log_error "Missing [REFACTOR] or [BLUE] marker (REQUIRE_REFACTOR=true)"
        return 1
    fi

    # Verify order: [RED] must appear after [GREEN] in git log (older = later in output)
    local red_line=$(echo "$recent_commits" | grep -n "\[RED\]" | sed -n '1p' | cut -d: -f1)
    local green_line=$(echo "$recent_commits" | grep -n "\[GREEN\]" | sed -n '1p' | cut -d: -f1)

    if [ "$red_line" -le "$green_line" ]; then
        log_error "[RED] must be committed BEFORE [GREEN]"
        return 1
    fi

    # If REFACTOR exists, verify it comes after GREEN
    if [ -n "$refactor_commit" ]; then
        local refactor_line=$(echo "$recent_commits" | grep -nE "\[REFACTOR\]|\[BLUE\]" | sed -n '1p' | cut -d: -f1)
        if [ "$refactor_line" -ge "$green_line" ]; then
            log_error "[REFACTOR]/[BLUE] must be committed AFTER [GREEN]"
            return 1
        fi
        log_info "TDD verified: [RED] -> [GREEN] -> [REFACTOR] order correct"
    else
        log_info "TDD verified: [RED] -> [GREEN] order correct"
    fi

    return 0
}

# Print progress: percent done, stories completed, estimated time remaining
# ETA is only shown when at least one story has completed this run
print_progress() {
    local total=$(jq '.stories | length' "$PRD_JSON")
    local passing=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")
    local remaining=$((total - passing))
    local pct=0
    if [ "$total" -gt 0 ]; then
        pct=$((passing * 100 / total))
    fi

    local eta_suffix=""
    local now=$(date +%s)
    local elapsed=$((now - RALPH_START_TIME))
    if [ "$passing" -gt "$RALPH_START_PASSING" ] && [ "$remaining" -gt 0 ]; then
        local done_this_run=$((passing - RALPH_START_PASSING))
        local eta=$(( (elapsed / done_this_run) * remaining ))
        eta_suffix=" | ETA: $(fmt_elapsed $eta)"
    fi

    log_info "Progress: $pct% ($passing/$total stories) | remaining: $remaining$eta_suffix"
}

# Main loop
main() {
    log_info "Starting Ralph Loop"
    log_info "Configuration: MAX_ITERATIONS=$MAX_ITERATIONS, RALPH_MODEL=$RALPH_MODEL, REQUIRE_REFACTOR=$REQUIRE_REFACTOR, RALPH_BASELINE_MODE=$RALPH_BASELINE_MODE"
    log_info "Log file: $LOG_FILE"

    validate_environment

    # Track timing for ETA calculation
    RALPH_START_TIME=$(date +%s)
    RALPH_START_PASSING=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")

    local iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        iteration=$((iteration + 1))
        log_info "===== Iteration $iteration/$MAX_ITERATIONS ====="

        # Get next incomplete story
        local story_id=$(get_next_story)

        if [ -z "$story_id" ]; then
            log_info "No incomplete stories found"
            log_info "<promise>COMPLETE</promise>"
            break
        fi

        local details=$(get_story_details "$story_id")
        local title=$(echo "$details" | cut -d'|' -f1)

        # Track retries for current story
        if [ "$story_id" != "${last_story_id:-}" ]; then
            retry_count=0
            last_story_id="$story_id"
        fi

        # Capture per-story baseline (persisted to prevent absorption on restart)
        if [ "$RALPH_BASELINE_MODE" = "true" ]; then
            capture_test_baseline "$BASELINE_FILE" "$story_id"
        fi

        # Record commit count before execution
        local commits_before=$(commit_count)

        print_progress

        # Execute story and capture return code (use || true to prevent set -e from exiting on non-zero)
        local exec_status=0
        execute_story "$story_id" "$details" || exec_status=$?

        if [ $exec_status -eq 2 ]; then
            # Story already complete - skip TDD verification, just run quality checks
            log_info "Story already complete - verifying with quality checks"

            if run_quality_checks "$story_id"; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Already complete, verified by quality checks"
                log_info "Story $story_id marked as PASSING (pre-existing implementation)"

                commit_state_files "chore: Update Ralph state after verifying $story_id (already complete)"
                print_progress
            else
                log_error "Story reported as complete but quality checks failed"
                log_progress "$iteration" "$story_id" "FAIL" "Quality checks failed despite reported completion"
                retry_count=$((retry_count + 1))
                if [ $retry_count -ge $MAX_RETRIES ]; then
                    log_error "Max retries reached for story $story_id"
                    exit 1
                fi
                continue
            fi

        elif [ $exec_status -eq 0 ]; then
            # Normal execution - verify TDD commits
            log_info "Story execution completed"

            # Verify TDD commits were made
            if ! check_tdd_commits "$story_id" "$commits_before"; then
                # Clean up invalid commits and files before retry
                local commits_after=$(commit_count)
                local new_commits=$((commits_after - commits_before))
                if [ $new_commits -gt 0 ]; then
                    log_warn "Resetting $new_commits invalid commit(s)"
                    git reset --hard HEAD~$new_commits
                fi
                log_warn "Cleaning up untracked files"
                git clean -fd

                retry_count=$((retry_count + 1))
                log_error "TDD verification failed (attempt $retry_count/$MAX_RETRIES)"
                log_progress "$iteration" "$story_id" "RETRY" "TDD failed, retrying"

                if [ $retry_count -ge $MAX_RETRIES ]; then
                    log_error "Max retries reached for story $story_id"
                    exit 1
                fi
                continue  # Retry same story (get_next_story returns same incomplete story)
            fi

            # Run quality checks
            if run_quality_checks "$story_id"; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Completed successfully with TDD commits"
                log_info "Story $story_id marked as PASSING"

                commit_state_files "chore: Update Ralph state after completing $story_id"
                print_progress
            else
                # Keep commits (RED+GREEN are valid) so next iteration can REFACTOR
                retry_count=$((retry_count + 1))
                log_error "Quality check failed (attempt $retry_count/$MAX_RETRIES)"
                log_progress "$iteration" "$story_id" "RETRY" "Quality checks failed, retrying"

                if [ $retry_count -ge $MAX_RETRIES ]; then
                    log_error "Max retries reached for story $story_id"
                    exit 1
                fi
                continue
            fi

        else
            # Execution failed
            log_error "Story execution failed"
            log_progress "$iteration" "$story_id" "FAIL" "Execution error"
        fi

        echo ""
    done

    if [ $iteration -eq $MAX_ITERATIONS ]; then
        log_warn "Reached maximum iterations ($MAX_ITERATIONS)"
    fi

    # Summary
    print_progress
}

# Run main
main