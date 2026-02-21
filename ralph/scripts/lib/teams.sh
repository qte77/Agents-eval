#!/bin/bash
#
# Teams-mode orchestration for Ralph Loop
#
# Provides wave-based parallel story execution: delegation prompt
# construction, hybrid commit attribution, selective revert, and
# teammate verification.
#
# Source order: common.sh → baseline.sh → teams.sh
# Requires globals from ralph.sh: PRD_JSON
# Requires functions from baseline.sh: run_ruff_scoped, run_complexity_scoped, run_tests_scoped
# Requires functions from ralph.sh: get_story_details, update_story_status, check_tdd_commits

# Return all unblocked incomplete story IDs (the current wave frontier).
get_unblocked_stories() {
    local completed=$(jq -r '[.stories[] | select(.status == "passed") | .id] | @json' "$PRD_JSON")

    # Reason: "in_progress" included so Ralph resumes interrupted stories after a crash
    jq -r --argjson completed "$completed" '
      .stories[]
      | select(.status == "pending" or .status == "failed" or .status == "in_progress")
      | select((.depends_on // []) - $completed | length == 0)
      | .id
    ' "$PRD_JSON"
}

# Run full make validate at wave boundary (non-blocking).
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

# Return wave peer story IDs (all unblocked stories except the primary).
# Args: $1 - primary story ID to exclude
teams_get_wave_peers() {
    local story_id="$1"
    get_unblocked_stories | grep -v "^${story_id}$" || true
}

# Append delegation prompt section for wave peer stories.
# Args:
#   $1 - Primary story ID (excluded from delegation list)
#   $2 - Path to iteration prompt file
# Outputs: number of delegated stories on stdout
teams_append_delegation_prompt() {
    local story_id="$1"
    local iteration_prompt="$2"

    local other_stories
    other_stories=$(teams_get_wave_peers "$story_id")
    if [ -z "$other_stories" ]; then
        echo 0
        return 0
    fi

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
    echo "$delegate_count"
}

# Filter commits to those attributed to a story (hybrid attribution).
# A commit matches if its message contains the story ID OR it touches
# a file listed in the story's files array in prd.json.
# Args:
#   $1 - Story ID
#   $2 - Newline-separated recent commits (hash + message per line)
#   $3 - Path to prd.json
# Outputs: filtered commit lines on stdout (empty if no match)
teams_filter_commits_for_story() {
    local story_id="$1"
    local recent_commits="$2"
    local prd_json="$3"

    local story_files
    story_files=$(jq -r --arg id "$story_id" \
        '.stories[] | select(.id == $id) | .files // [] | .[]' "$prd_json" 2>/dev/null || true)

    local filtered_commits=""
    local line commit_hash match changed_files sf

    while IFS= read -r line; do
        commit_hash=$(echo "$line" | cut -d' ' -f1)
        match=false

        # Check 1: commit message mentions story ID
        if echo "$line" | grep -qF "$story_id"; then
            match=true
        fi

        # Check 2: commit touches a file in the story's files array
        if [ "$match" = "false" ] && [ -n "$story_files" ]; then
            changed_files=$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null || true)
            while IFS= read -r sf; do
                if echo "$changed_files" | grep -qF "$sf"; then
                    match=true
                    break
                fi
            done <<< "$story_files"
        fi

        if [ "$match" = "true" ]; then
            filtered_commits="${filtered_commits:+$filtered_commits
}$line"
        fi
    done <<< "$recent_commits"

    echo "$filtered_commits"
}

# Selectively revert commits attributed to a primary story, preserving
# teammate commits. Uses the same hybrid attribution as teams_filter_commits_for_story.
# Args:
#   $1 - Story ID
#   $2 - Number of recent commits to examine
#   $3 - Path to prd.json
# Outputs: number of reverted commits on stdout
teams_revert_primary_commits() {
    local story_id="$1"
    local new_commits="$2"
    local prd_json="$3"

    local story_files
    story_files=$(jq -r --arg id "$story_id" \
        '.stories[] | select(.id == $id) | .files // [] | .[]' "$prd_json" 2>/dev/null || true)

    local reverted=0
    local hash msg is_primary changed sf

    for hash in $(git log --format="%h" -n "$new_commits"); do
        msg=$(git log --format="%s" -1 "$hash")
        is_primary=false

        if echo "$msg" | grep -qF "$story_id"; then
            is_primary=true
        elif [ -n "$story_files" ]; then
            changed=$(git diff-tree --no-commit-id --name-only -r "$hash" 2>/dev/null || true)
            while IFS= read -r sf; do
                if echo "$changed" | grep -qF "$sf"; then
                    is_primary=true
                    break
                fi
            done <<< "$story_files"
        fi

        if [ "$is_primary" = "true" ]; then
            git revert --no-edit "$hash" >/dev/null 2>&1 || true
            reverted=$((reverted + 1))
        fi
    done

    echo "$reverted"
}

# Verify teammate stories after primary story passes.
# Runs TDD commit check + scoped quality (ruff, complexity, tests) for each
# wave peer, then a single type_check for the whole batch.
# Args:
#   $1 - Primary story ID (excluded from verification)
#   $2 - commits_before count (passed to check_tdd_commits)
#   $3 - Newline-separated teammate story IDs (from delegation time).
#        Reason: must use the list captured at delegation time, not re-query
#        get_unblocked_stories, because the primary story is already "passed"
#        by this point — which unblocks Wave N+1 stories that were never delegated.
verify_teammate_stories() {
    local primary_id="$1"
    local commits_before="$2"
    local teammate_stories="${3:-}"

    # Fallback for callers that don't pass an explicit list
    if [ -z "$teammate_stories" ]; then
        teammate_stories=$(teams_get_wave_peers "$primary_id")
    fi

    if [ -z "$teammate_stories" ]; then
        return 0
    fi

    log_info "===== Verifying Teammate Stories ====="

    local type_check_needed=false
    local sid

    for sid in $teammate_stories; do
        log_info "Verifying teammate story: $sid"

        # TDD commit check (hybrid attribution)
        if ! check_tdd_commits "$sid" "$commits_before"; then
            log_warn "Teammate story $sid: TDD verification failed"
            update_story_status "$sid" "failed"
            continue
        fi

        # Scoped quality checks (ruff, complexity, tests)
        local sid_failed=false

        if ! run_ruff_scoped "$sid" "$PRD_JSON"; then
            log_warn "Teammate story $sid: ruff check failed"
            sid_failed=true
        fi

        if ! run_complexity_scoped "$sid" "$PRD_JSON"; then
            log_warn "Teammate story $sid: complexity check failed"
            sid_failed=true
        fi

        local teammate_test_log="/tmp/claude/ralph_teammate_${sid}_tests.log"
        if ! run_tests_scoped "$sid" "$PRD_JSON" "$teammate_test_log"; then
            log_warn "Teammate story $sid: tests failed"
            sid_failed=true
        fi

        if [ "$sid_failed" = "true" ]; then
            update_story_status "$sid" "failed"
        else
            update_story_status "$sid" "passed"
            log_info "Teammate story $sid marked as PASSED"
            type_check_needed=true
        fi
    done

    # Run type_check once for the whole batch (not per-story)
    if [ "$type_check_needed" = "true" ]; then
        log_info "Running type check for teammate batch..."
        if ! make --no-print-directory type_check 2>&1; then
            log_warn "Type check failed for teammate batch (non-blocking)"
        fi
    fi

    log_info "===== Teammate Verification Complete ====="
}
