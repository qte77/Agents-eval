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

# Persist TDD phase verification across git resets (Solution 1A).
# After check_tdd_commits passes, save RED+GREEN hashes so a quality-failure
# reset doesn't erase proof that TDD phases were completed.
persist_tdd_verified() {
    local story_id="$1"
    local red_hash="$2"
    local green_hash="$3"
    mkdir -p "$TDD_VERIFIED_DIR"
    echo "RED=$red_hash GREEN=$green_hash" > "$TDD_VERIFIED_DIR/$story_id"
    log_info "TDD phases persisted for $story_id (RED=$red_hash GREEN=$green_hash)"
}

# Clear persisted TDD verification (on story completion or story change).
clear_tdd_verified() {
    local story_id="$1"
    if [ -f "$TDD_VERIFIED_DIR/$story_id" ]; then
        rm -f "$TDD_VERIFIED_DIR/$story_id"
        log_info "Cleared TDD verification for $story_id"
    fi
}

# Configuration
RALPH_MODEL=${RALPH_MODEL:-"sonnet"}  # Model: sonnet, opus, haiku
MAX_ITERATIONS=${MAX_ITERATIONS:-25}
REQUIRE_REFACTOR=${REQUIRE_REFACTOR:-false}  # Require [REFACTOR] commit (true/false)
PRD_JSON="ralph/docs/prd.json"
PROGRESS_FILE="ralph/docs/progress.txt"
PROMPT_FILE="ralph/docs/templates/prompt.md"
MAX_RETRIES=3
RALPH_TEAMS=${RALPH_TEAMS:-false}  # EXPERIMENTAL: cross-story interference causes false rejections (see ralph/README.md)
RALPH_BASELINE_MODE=${RALPH_BASELINE_MODE:-true}
BASELINE_FILE="/tmp/claude/ralph_baseline_failures.txt"
RETRY_CONTEXT_FILE="/tmp/claude/ralph_retry_context.txt"
TDD_VERIFIED_DIR="/tmp/claude/ralph_tdd_verified"

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
    jq -r --argjson completed "$completed" '
      .stories[]
      | select(.passes == false)
      | select((.depends_on // []) - $completed | length == 0)
      | .id
    ' "$PRD_JSON" | sed -n '1p'
}

# Get all unblocked incomplete story IDs (for teams mode delegation).
# A "wave" is the set of unblocked stories at a given point — the frontier
# of the dependency graph defined by each story's depends_on array.
# Within a wave, stories run in parallel (one teammate each); the next
# wave starts after the current one completes.
get_unblocked_stories() {
    local completed=$(jq -r '[.stories[] | select(.passes == true) | .id] | @json' "$PRD_JSON")

    jq -r --argjson completed "$completed" '
      .stories[]
      | select(.passes == false)
      | select((.depends_on // []) - $completed | length == 0)
      | .id
    ' "$PRD_JSON"
}

# Print dependency wave plan and blocking tree for remaining stories.
# Uses iterative BFS: each wave is the frontier of unblocked incomplete stories.
# Output goes to both log and progress file for visibility.
print_dependency_tree() {
    local completed_ids
    completed_ids=$(jq -r '[.stories[] | select(.passes == true) | .id]' "$PRD_JSON")
    local completed_count
    completed_count=$(echo "$completed_ids" | jq 'length')

    # Get all incomplete stories as JSON array of {id, depends_on}
    local incomplete
    incomplete=$(jq '[.stories[] | select(.passes == false) | {id, depends_on: (.depends_on // [])}]' "$PRD_JSON")
    local incomplete_count
    incomplete_count=$(echo "$incomplete" | jq 'length')

    if [ "$incomplete_count" -eq 0 ]; then
        log_info "All stories complete — no dependency tree to show"
        return 0
    fi

    local total_count
    total_count=$(jq '.stories | length' "$PRD_JSON")

    # BFS wave computation
    local placed="$completed_ids"
    local wave_num=0
    local tree_output=""
    local blocking_output=""

    while true; do
        wave_num=$((wave_num + 1))
        # Find frontier: incomplete stories whose depends_on is subset of placed
        local frontier
        frontier=$(echo "$incomplete" | jq -r --argjson placed "$placed" '
            [.[] | select(
                .depends_on as $deps |
                ($deps | length == 0) or ($deps - ($placed | [.[]]) | length == 0)
            ) | .id] | .[]
        ')

        if [ -z "$frontier" ]; then
            break
        fi

        # Build wave label with dependency annotation
        local wave_ids
        wave_ids=$(echo "$frontier" | paste -sd', ' -)
        local dep_annotation=""
        if [ "$wave_num" -gt 1 ]; then
            # Collect unique dependencies of this wave's stories from placed set
            local wave_deps=""
            local fid
            for fid in $frontier; do
                local story_deps
                story_deps=$(echo "$incomplete" | jq -r --arg id "$fid" \
                    '.[] | select(.id == $id) | .depends_on[]' 2>/dev/null || true)
                for sd in $story_deps; do
                    # Only include deps that were placed in a previous wave (not pre-completed)
                    if echo "$completed_ids" | jq -e --arg d "$sd" 'any(.[]; . == $d)' >/dev/null 2>&1; then
                        continue  # skip pre-completed deps
                    fi
                    wave_deps="${wave_deps:+$wave_deps }$sd"
                done
            done
            # Deduplicate and sort
            if [ -n "$wave_deps" ]; then
                local unique_deps
                unique_deps=$(echo "$wave_deps" | tr ' ' '\n' | sort -u | paste -sd', ' -)
                dep_annotation=" (after $unique_deps)"
            fi
        fi
        tree_output="${tree_output}  Wave $wave_num${dep_annotation}: $wave_ids
"

        # Add frontier to placed, remove from incomplete
        for fid in $frontier; do
            placed=$(echo "$placed" | jq --arg id "$fid" '. + [$id]')
            incomplete=$(echo "$incomplete" | jq --arg id "$fid" '[.[] | select(.id != $id)]')
        done

        local remaining_incomplete
        remaining_incomplete=$(echo "$incomplete" | jq 'length')
        if [ "$remaining_incomplete" -eq 0 ]; then
            break
        fi
    done

    # Build blocking relationships (reverse depends_on)
    local all_incomplete
    all_incomplete=$(jq '[.stories[] | select(.passes == false) | {id, depends_on: (.depends_on // [])}]' "$PRD_JSON")
    local blocker_ids
    blocker_ids=$(echo "$all_incomplete" | jq -r '[.[].depends_on[]] | unique | .[]' 2>/dev/null || true)

    for bid in $blocker_ids; do
        # Skip if blocker is already completed
        if echo "$completed_ids" | jq -e --arg d "$bid" 'any(.[]; . == $d)' >/dev/null 2>&1; then
            continue
        fi
        local blocked_by_this
        blocked_by_this=$(echo "$all_incomplete" | jq -r --arg bid "$bid" \
            '[.[] | select(.depends_on | any(. == $bid)) | .id] | join(", ")')
        if [ -n "$blocked_by_this" ]; then
            blocking_output="${blocking_output}    $bid -> $blocked_by_this
"
        fi
    done

    # Output
    local header="===== Dependency Wave Plan ====="
    local footer=""
    if [ "$completed_count" -gt 0 ]; then
        footer="  (Note: $completed_count/$total_count stories already complete and excluded from waves)"
    fi
    local separator="============================="

    log_info "$header"
    echo "$tree_output" | while IFS= read -r line; do
        [ -n "$line" ] && log_info "$line" || true
    done

    if [ -n "$blocking_output" ]; then
        log_info ""
        log_info "  Blocking relationships:"
        echo "$blocking_output" | while IFS= read -r line; do
            [ -n "$line" ] && log_info "$line" || true
        done
    fi

    [ -n "$footer" ] && log_info "$footer"
    log_info "$separator"

    # Also append to progress file
    {
        echo ""
        echo "$header"
        echo "$tree_output"
        if [ -n "$blocking_output" ]; then
            echo "  Blocking relationships:"
            echo "$blocking_output"
        fi
        [ -n "$footer" ] && echo "$footer"
        echo "$separator"
        echo ""
    } >> "$PROGRESS_FILE"
}

# Run full validation at wave boundaries (teams mode only).
# Non-blocking: cross-story issues are logged but don't halt the pipeline.
# The next wave's stories will address any issues found here.
run_wave_checkpoint() {
    log_info "===== Wave Checkpoint: Full Validation ====="
    if make --no-print-directory validate 2>&1 | tee /tmp/claude/ralph_wave_checkpoint.log; then
        log_info "Wave checkpoint PASSED"
        return 0
    else
        log_warn "Wave checkpoint found cross-story issues (non-blocking, logged for next wave)"
        return 0  # Non-blocking — issues logged, next wave's stories will fix them
    fi
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

# Log heartbeat with phase detection and agent activity while story executes
# in background. Scans commits for phase and tails log file for recent output
# (agent output streams to LOG_FILE via tee on line 76).
# Args:
#   $1 - story ID
monitor_story_progress() {
    local story_id="$1"
    local sprint_start
    sprint_start=$(jq -r '.generated' "$PRD_JSON")
    # Reason: Track byte offset to read only new log content per cycle,
    # preventing [CC] prefix nesting when monitor re-reads its own output.
    local log_offset
    log_offset=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)

    while sleep 30; do
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
        # Show recent agent activity from log (new content only, via byte offset)
        local activity=""
        local current_size
        current_size=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
        if [ "$current_size" -gt "$log_offset" ]; then
            activity=$(tail -c +"$((log_offset + 1))" "$LOG_FILE" 2>/dev/null \
                | grep -v "^$\|^\[\|  >>" | tail -1 | cut -c1-120)
            log_offset=$current_size
        fi
        if [ -n "$activity" ]; then
            if echo "$activity" | grep -qi "error\|fail\|traceback"; then
                log_cc_error "$activity"
            else
                log_cc "$activity"
            fi
        fi
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

    # Append retry context if retrying after quality failure (#4: pass failure reason)
    if [ -f "$RETRY_CONTEXT_FILE" ]; then
        local failed_check
        failed_check=$(cat "$RETRY_CONTEXT_FILE")
        {
            echo ""
            echo "## RETRY: Previous quality check failed"
            echo "The \`$failed_check\` check failed on the previous attempt."
            echo "Your prior [RED] and [GREEN] commits already exist. Fix the issue and commit with \`[REFACTOR]\` marker."
        } >> "$iteration_prompt"
        log_info "Retry context appended to prompt (failed check: $failed_check)"
    fi

    # Teams mode: append current wave (independent unblocked stories) for delegation
    if [ "$RALPH_TEAMS" = "true" ]; then
        local other_stories
        other_stories=$(get_unblocked_stories | grep -v "^${story_id}$" || true)
        if [ -n "$other_stories" ]; then
            {
                echo ""
                echo "## Team Mode: Delegate Independent Stories"
                echo "Spawn one teammate per story using the Task tool."
                echo "Each follows TDD: RED [RED] → GREEN [GREEN] → REFACTOR [REFACTOR]."
                echo "Skills: \`testing-python\`, \`implementing-python\`, \`reviewing-code\`."
                echo ""
            } >> "$iteration_prompt"
            local sid
            for sid in $other_stories; do
                local sdetails
                sdetails=$(get_story_details "$sid")
                local stitle
                stitle=$(echo "$sdetails" | cut -d'|' -f1)
                local sdesc
                sdesc=$(echo "$sdetails" | cut -d'|' -f2)
                {
                    echo "### $sid: $stitle"
                    echo "$sdesc"
                    echo ""
                } >> "$iteration_prompt"
            done
            local delegate_count
            delegate_count=$(echo "$other_stories" | wc -l)
            log_info "Team mode: delegating $delegate_count additional story(ies)"
        fi
    fi

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
        run_quality_checks_baseline "$BASELINE_FILE" "$story_id" "$PRD_JSON"
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

    # Solution 1A: If TDD phases were persisted from a prior iteration
    # (before quality-failure reset), accept REFACTOR-only commits.
    if [ -f "$TDD_VERIFIED_DIR/$story_id" ]; then
        log_info "TDD phases already verified (persisted): $(cat "$TDD_VERIFIED_DIR/$story_id")"
        log_info "Accepting REFACTOR-only iteration (prior RED+GREEN persisted)"
        return 0
    fi

    local commits_after=$(commit_count)
    local new_commits=$((commits_after - commits_before))

    if [ $new_commits -eq 0 ]; then
        log_error "No commits made during story execution"
        return 1
    fi

    local recent_commits=$(git log --oneline -n $new_commits)

    # Teams mode (Solution 2A): file-scoped commit attribution.
    # Instead of grepping commit messages for story ID (fragile — agents write
    # generic messages), check which files each commit touches against the
    # story's files array from prd.json. Falls back to message grep if no
    # files array exists.
    if [ "$RALPH_TEAMS" = "true" ]; then
        local story_files
        story_files=$(jq -r --arg id "$story_id" \
            '.stories[] | select(.id == $id) | .files // [] | .[]' "$PRD_JSON" 2>/dev/null || true)

        if [ -n "$story_files" ]; then
            # File-scoped attribution: keep commits that touch at least one story file
            local filtered_commits=""
            local commit_hash
            while IFS= read -r line; do
                commit_hash=$(echo "$line" | cut -d' ' -f1)
                local changed_files
                changed_files=$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null || true)
                local match=false
                local sf
                while IFS= read -r sf; do
                    if echo "$changed_files" | grep -qF "$sf"; then
                        match=true
                        break
                    fi
                done <<< "$story_files"
                if [ "$match" = "true" ]; then
                    filtered_commits="${filtered_commits:+$filtered_commits
}$line"
                fi
            done <<< "$recent_commits"
            recent_commits="$filtered_commits"
        else
            # Fallback: no files array in prd.json, use original message grep
            log_warn "No files array for $story_id — falling back to message grep"
            recent_commits=$(echo "$recent_commits" | grep "$story_id" || true)
        fi

        new_commits=$(echo "$recent_commits" | grep -c . || true)
        if [ "$new_commits" -eq 0 ]; then
            log_error "No commits for $story_id in team batch (file-scoped)"
            return 1
        fi
    fi

    log_info "Found $new_commits new commit(s) for $story_id:"

    # Report detected phases with their commits
    local red_commit=$(echo "$recent_commits" | grep "\[RED\]" | sed -n '1p')
    local green_commit=$(echo "$recent_commits" | grep "\[GREEN\]" | sed -n '1p')
    local refactor_commit=$(echo "$recent_commits" | grep -E "\[REFACTOR\]|\[BLUE\]" | sed -n '1p')
    # Fallback: detect conventional commit prefix "refactor(" when bracket marker is missing
    if [ -z "$refactor_commit" ]; then
        refactor_commit=$(echo "$recent_commits" | grep -E "^[a-f0-9]+ refactor\(" | sed -n '1p')
        [ -n "$refactor_commit" ] && log_warn "  [REFACTOR] detected via prefix fallback: $refactor_commit"
    fi

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
    log_info "Configuration: MAX_ITERATIONS=$MAX_ITERATIONS, RALPH_MODEL=$RALPH_MODEL, REQUIRE_REFACTOR=$REQUIRE_REFACTOR, RALPH_BASELINE_MODE=$RALPH_BASELINE_MODE, RALPH_TEAMS=$RALPH_TEAMS"
    log_info "Log file: $LOG_FILE"

    validate_environment

    # Show dependency wave plan before starting
    print_dependency_tree

    # Track timing for ETA calculation
    RALPH_START_TIME=$(date +%s)
    RALPH_START_PASSING=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")

    local iteration=0

    # Wave tracking for teams mode checkpoint validation
    local last_wave_stories
    last_wave_stories=$(get_unblocked_stories)

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
            # Clear persisted TDD state from previous story
            [ -n "${last_story_id:-}" ] && clear_tdd_verified "$last_story_id"
            retry_count=0
            last_story_id="$story_id"
            rm -f "$RETRY_CONTEXT_FILE"
        fi

        # Capture per-story baseline (persisted to prevent absorption on restart)
        if [ "$RALPH_BASELINE_MODE" = "true" ]; then
            capture_test_baseline "$BASELINE_FILE" "$story_id"
        fi

        # Record commit count and untracked files before execution
        local commits_before=$(commit_count)
        local untracked_before
        untracked_before=$(mktemp /tmp/claude/ralph_untracked.XXXXXX)
        git ls-files --others --exclude-standard | sort > "$untracked_before"

        print_progress

        # Execute story and capture return code (use || true to prevent set -e from exiting on non-zero)
        local exec_status=0
        execute_story "$story_id" "$details" || exec_status=$?

        local story_passed=false

        if [ $exec_status -eq 2 ]; then
            # Story already complete - skip TDD verification, just run quality checks
            log_info "Story already complete - verifying with quality checks"

            if run_quality_checks "$story_id"; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Already complete, verified by quality checks"
                log_info "Story $story_id marked as PASSING (pre-existing implementation)"

                commit_state_files "chore: Update Ralph state after verifying $story_id (already complete)"
                story_passed=true
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

            # Skip TDD verification on quality retry (prior RED+GREEN already verified)
            if [ -f "$RETRY_CONTEXT_FILE" ]; then
                log_info "Quality retry — skipping TDD verification (prior RED+GREEN exist)"
                rm -f "$RETRY_CONTEXT_FILE"
            elif ! check_tdd_commits "$story_id" "$commits_before"; then
                # Clean up invalid commits and files before retry
                local commits_after=$(commit_count)
                local new_commits=$((commits_after - commits_before))
                if [ $new_commits -gt 0 ]; then
                    log_warn "Resetting $new_commits invalid commit(s)"
                    git reset --hard HEAD~$new_commits
                fi
                # Scoped clean: only remove files created during story execution
                local untracked_after
                untracked_after=$(mktemp /tmp/claude/ralph_untracked.XXXXXX)
                git ls-files --others --exclude-standard | sort > "$untracked_after"
                local story_untracked
                story_untracked=$(comm -13 "$untracked_before" "$untracked_after")
                if [ -n "$story_untracked" ]; then
                    local file_count
                    file_count=$(echo "$story_untracked" | wc -l)
                    log_warn "Cleaning $file_count story-created file(s)"
                    echo "$story_untracked" | xargs rm -f
                else
                    log_info "No story-created untracked files to clean"
                fi
                rm -f "$untracked_after"

                retry_count=$((retry_count + 1))
                log_error "TDD verification failed (attempt $retry_count/$MAX_RETRIES)"
                log_progress "$iteration" "$story_id" "RETRY" "TDD failed, retrying"

                if [ $retry_count -ge $MAX_RETRIES ]; then
                    log_error "Max retries reached for story $story_id"
                    exit 1
                fi
                continue  # Retry same story (get_next_story returns same incomplete story)
            fi

            # Persist TDD phases so quality-failure reset doesn't lose them (Solution 1A)
            local red_hash green_hash
            red_hash=$(git log --oneline -n $(($(commit_count) - commits_before)) \
                | grep "\[RED\]" | sed -n '1p' | cut -d' ' -f1)
            green_hash=$(git log --oneline -n $(($(commit_count) - commits_before)) \
                | grep "\[GREEN\]" | sed -n '1p' | cut -d' ' -f1)
            if [ -n "$red_hash" ] && [ -n "$green_hash" ]; then
                persist_tdd_verified "$story_id" "$red_hash" "$green_hash"
            fi

            # Run quality checks
            if run_quality_checks "$story_id"; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Completed successfully with TDD commits"
                log_info "Story $story_id marked as PASSING"
                rm -f "$RETRY_CONTEXT_FILE"
                clear_tdd_verified "$story_id"

                commit_state_files "chore: Update Ralph state after completing $story_id"
                story_passed=true
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

        # Wave boundary detection (teams mode only)
        if [ "$story_passed" = "true" ] && [ "$RALPH_TEAMS" = "true" ]; then
            local next_story
            next_story=$(get_next_story)
            if [ -n "$next_story" ] && ! echo "$last_wave_stories" | grep -qx "$next_story"; then
                run_wave_checkpoint
                last_wave_stories=$(get_unblocked_stories)
            fi
        fi

        rm -f "$untracked_before"
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