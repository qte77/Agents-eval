#!/bin/bash
#
# Baseline-aware test validation for Ralph Loop
#
# Captures pre-existing test failures at loop start, then only blocks
# story advancement on NEW failures (regressions). This prevents
# unrelated failures from blocking story progress.
#
# ANTI-CONTAMINATION: Baseline is automatically refreshed after successful
# validation to prevent failures from leaking between stories.
#
# ANTI-ABSORPTION: Baselines are persisted per story ID. On restart, the
# original pre-story baseline is reused so a story's own failures from a
# prior attempt cannot be laundered into the baseline.
#
# STORY-SCOPED LINT: Phase 1 test linting only checks files changed by
# the current story (git diff + untracked). Pre-existing lint violations
# in untouched test files do not block story progress.
#
# Source this file: source "$SCRIPT_DIR/lib/baseline.sh"
#
# Functions:
#   get_story_base_commit          - Find pre-story commit for scoped diffs
#   capture_test_baseline          - Snapshot current failing tests (per-story persistent)
#   refresh_baseline_on_success    - Update baseline after clean validation
#   compare_test_failures          - Diff current failures against baseline
#   run_quality_checks_baseline    - Lint/type/test with baseline comparison
#   get_baseline_age               - Check baseline freshness
#

# Freshness threshold for pytest cache (seconds)
BASELINE_CACHE_MAX_AGE=${BASELINE_CACHE_MAX_AGE:-300}

# Auto-refresh baseline after successful validation (prevents contamination)
RALPH_AUTO_REFRESH_BASELINE=${RALPH_AUTO_REFRESH_BASELINE:-true}

# Persistent per-story baseline storage (prevents absorption across restarts)
BASELINE_STORE_DIR="${BASELINE_STORE_DIR:-/tmp/claude/ralph_baselines}"

# Find the commit before a story's first commit.
# Used to scope lint checks and baseline captures to story-changed files.
# Returns HEAD if no story commits exist yet.
#
# Args:
#   $1 - Story ID (e.g., STORY-014)
get_story_base_commit() {
    local story_id="$1"
    local first
    first=$(git log --format="%H" --grep="$story_id" --reverse | sed -n '1p')
    if [ -n "$first" ]; then
        git rev-parse "${first}^" 2>/dev/null || git rev-parse HEAD
    else
        git rev-parse HEAD
    fi
}

# Capture current test failures as baseline.
# Uses pytest cache if fresh, falls back to full test run.
#
# Args:
#   $1 - Path to baseline file
#   $2 - Optional story ID for tracking (default: "loop-init")
capture_test_baseline() {
    local baseline_file="$1"
    local story_id="${2:-loop-init}"
    local cache_file=".pytest_cache/v/cache/lastfailed"

    log_info "Capturing test baseline for $story_id..."
    mkdir -p "$(dirname "$baseline_file")"
    mkdir -p "$BASELINE_STORE_DIR"

    # Reuse persisted baseline if it exists for this story (prevents absorption
    # of story's own failures across restarts)
    local stored="${BASELINE_STORE_DIR}/${story_id}.txt"
    if [ "$story_id" != "loop-init" ] && [ -f "$stored" ]; then
        # Staleness check: invalidate if codebase changed since capture
        local stored_commit
        stored_commit=$(grep "^# Base-commit:" "$stored" 2>/dev/null | sed -n '1p' | sed 's/^# Base-commit: //' || true)
        local current_base
        current_base=$(get_story_base_commit "$story_id")

        if [ -n "$stored_commit" ] && [ "$stored_commit" != "$current_base" ]; then
            log_warn "Persisted baseline stale (base ${stored_commit:0:8} != current ${current_base:0:8}) — re-capturing"
            rm -f "$stored"
            # Fall through to fresh capture below
        else
            log_info "Reusing persisted baseline for $story_id (prevents absorption)"
            cp "$stored" "$baseline_file"
            local count
            count=$(grep -v "^#" "$baseline_file" | grep -c . || true)
            log_info "Persisted baseline: $count pre-existing failure(s)"
            return 0
        fi
    fi

    # Try pytest cache first (instant, no test execution)
    if [ -f "$cache_file" ]; then
        local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
        if [ "$cache_age" -lt "$BASELINE_CACHE_MAX_AGE" ]; then
            log_info "Using pytest cache (${cache_age}s old, threshold: ${BASELINE_CACHE_MAX_AGE}s)"

            local failures_temp=$(mktemp)
            jq -r 'keys[]' "$cache_file" | sort > "$failures_temp"

            # Add metadata header
            {
                echo "# Baseline captured: $(date --iso-8601=seconds)"
                echo "# Story: $story_id"
                echo "# Source: pytest-cache"
                echo "# Base-commit: $(git rev-parse HEAD)"
                cat "$failures_temp"
            } > "$baseline_file"
            rm "$failures_temp"

            local count
            count=$(grep -v "^#" "$baseline_file" | grep -c . || true)
            if [ "$count" -eq 0 ]; then
                log_info "Baseline captured: all tests passing (cached)"
            else
                log_warn "Baseline captured: $count pre-existing failure(s) (cached)"
            fi
            return 0
        else
            log_warn "Pytest cache stale (${cache_age}s old) — running fresh baseline"
        fi
    else
        log_info "No pytest cache found — running fresh baseline"
    fi

    # Fallback: full test run
    local test_output
    test_output=$(uv run pytest --tb=no -q 2>&1) || true

    # Extract FAILED lines, strip "FAILED " prefix, sort
    # Reason: grep returns 1 when no matches; || true prevents set -e abort
    local failures_temp=$(mktemp)
    echo "$test_output" \
        | { grep "^FAILED " || true; } \
        | sed 's/^FAILED //' \
        | sort > "$failures_temp"

    # Add metadata header
    {
        echo "# Baseline captured: $(date --iso-8601=seconds)"
        echo "# Story: $story_id"
        echo "# Source: full-test-run"
        echo "# Base-commit: $(git rev-parse HEAD)"
        cat "$failures_temp"
    } > "$baseline_file"
    rm "$failures_temp"

    local count
    count=$(grep -v "^#" "$baseline_file" | grep -c . || true)

    if [ "$count" -eq 0 ]; then
        log_info "Baseline captured: all tests passing"
    else
        log_warn "Baseline captured: $count pre-existing failure(s)"
    fi

    # Persist for this story (reused on restart to prevent absorption)
    if [ "$story_id" != "loop-init" ]; then
        cp "$baseline_file" "${BASELINE_STORE_DIR}/${story_id}.txt"
        log_info "Baseline persisted for $story_id"
    fi
}

# Get baseline age in seconds.
# Returns age, or -1 if baseline doesn't exist or has no metadata.
#
# Args:
#   $1 - Path to baseline file
get_baseline_age() {
    local baseline_file="$1"

    if [ ! -f "$baseline_file" ]; then
        echo "-1"
        return
    fi

    # Extract timestamp from metadata header
    local baseline_ts
    baseline_ts=$(grep "^# Baseline captured:" "$baseline_file" 2>/dev/null | sed -n '1p' | sed 's/^# Baseline captured: //' || true)

    if [ -z "$baseline_ts" ]; then
        # No metadata, fall back to file modification time
        local file_age=$(($(date +%s) - $(stat -c %Y "$baseline_file")))
        echo "$file_age"
        return
    fi

    local baseline_epoch
    baseline_epoch=$(date -d "$baseline_ts" +%s 2>/dev/null || echo "-1")

    if [ "$baseline_epoch" -eq -1 ]; then
        echo "-1"
        return
    fi

    local age=$(($(date +%s) - baseline_epoch))
    echo "$age"
}

# Refresh baseline after successful validation.
# This prevents contamination: if validation passes, the current state
# becomes the new baseline for the next story.
#
# Args:
#   $1 - Path to baseline file
#   $2 - Story ID that just passed
#   $3 - Current failures count (default: 0)
refresh_baseline_on_success() {
    local baseline_file="$1"
    local story_id="$2"
    local current_failures="${3:-0}"

    log_info "Refreshing baseline after successful validation of $story_id"

    # Clean up persisted baseline (story completed, no restart protection needed)
    rm -f "${BASELINE_STORE_DIR}/${story_id}.txt"

    if [ "$current_failures" -eq 0 ]; then
        log_success "Clean state: all tests passing — baseline cleared"
        {
            echo "# Baseline refreshed: $(date --iso-8601=seconds)"
            echo "# Story: $story_id"
            echo "# Status: all-tests-passing"
            echo "# Base-commit: $(git rev-parse HEAD)"
        } > "$baseline_file"
    else
        log_info "State has $current_failures pre-existing failure(s) — baseline updated"
        # Reason: "loop-refresh" skips per-story persistence (story already completed)
        capture_test_baseline "$baseline_file" "loop-refresh"
    fi
}

# Compare current test failures against baseline.
# Returns 0 if no NEW failures, 1 if regressions detected.
#
# Args:
#   $1 - Path to baseline file
#   $2 - Path to current test output log
compare_test_failures() {
    local baseline_file="$1"
    local current_log="$2"

    # If no baseline file, treat all failures as new (safe default)
    if [ ! -f "$baseline_file" ]; then
        log_warn "No baseline file found — treating all failures as new"
        return 1
    fi

    # Extract baseline failures (skip metadata lines starting with #)
    local baseline_failures
    baseline_failures=$(mktemp /tmp/claude/ralph_baseline_failures.XXXXXX)
    grep -v "^#" "$baseline_file" | sort > "$baseline_failures"

    # Extract current FAILED lines into sorted temp file
    local current_failures
    current_failures=$(mktemp /tmp/claude/ralph_current_failures.XXXXXX)
    # Reason: grep returns 1 when no matches; || true prevents set -e abort
    { grep "^FAILED " "$current_log" || true; } \
        | sed 's/^FAILED //' \
        | sort > "$current_failures"

    # Find new failures (in current but not in baseline)
    local new_failures
    new_failures=$(comm -13 "$baseline_failures" "$current_failures")

    # Find resolved failures (in baseline but not in current)
    local resolved_failures
    resolved_failures=$(comm -23 "$baseline_failures" "$current_failures")

    local baseline_count current_count new_count resolved_count
    baseline_count=$(wc -l < "$baseline_failures" | tr -d ' ')
    current_count=$(wc -l < "$current_failures" | tr -d ' ')
    new_count=$(echo "$new_failures" | grep -c . || true)
    resolved_count=$(echo "$resolved_failures" | grep -c . || true)

    # Handle empty string giving count of 0 vs 1
    [ -z "$new_failures" ] && new_count=0
    [ -z "$resolved_failures" ] && resolved_count=0

    log_info "Test Results: baseline=$baseline_count, current=$current_count, new=$new_count, resolved=$resolved_count"

    # Log details
    if [ "$resolved_count" -gt 0 ]; then
        log_success "$resolved_count pre-existing failure(s) resolved:"
        echo "$resolved_failures" | while read -r line; do
            [ -n "$line" ] && log_success "  Fixed: $line"
        done
    fi

    if [ "$new_count" -gt 0 ]; then
        log_error "$new_count NEW test failure(s) (regressions):"
        echo "$new_failures" | while read -r line; do
            [ -n "$line" ] && log_error "  New: $line"
        done
        rm "$baseline_failures" "$current_failures"
        return 1
    fi

    local preexisting=$((current_count - new_count))
    if [ "$preexisting" -gt 0 ]; then
        log_warn "$preexisting pre-existing test failure(s) (from baseline, not blocking)"
    fi

    log_success "No new test failures — baseline-aware validation passed"

    # Export current failure count for caller (used by refresh function)
    export RALPH_CURRENT_FAILURE_COUNT="$current_count"

    rm "$baseline_failures" "$current_failures"
    return 0
}

# Run quality checks with baseline-aware test comparison.
# Lint/type/complexity checks fail-fast. Test failures are compared
# against the baseline to distinguish regressions from pre-existing issues.
#
# ANTI-CONTAMINATION: Automatically refreshes baseline after successful
# validation (controlled by RALPH_AUTO_REFRESH_BASELINE env var).
#
# Args:
#   $1 - Path to baseline file
#   $2 - Optional story ID (for baseline refresh metadata)
run_quality_checks_baseline() {
    local baseline_file="$1"
    local story_id="${2:-unknown}"
    local current_log="/tmp/claude/ralph_current_tests.log"

    log_info "Running quality checks (baseline-aware)..."

    mkdir -p "$(dirname "$current_log")"

    # Phase 1: Lint/type/complexity (fail-fast)
    log_info "Phase 1: Lint/type/complexity checks..."

    for check in ruff type_check complexity; do
        if ! make --no-print-directory "$check" 2>&1; then
            log_error "$check failed"
            return 1
        fi
    done

    log_info "Phase 1 passed"

    # Phase 2: Tests with baseline comparison
    log_info "Phase 2: Tests with baseline comparison..."

    local test_exit=0
    uv run pytest --tb=no -q 2>&1 | tee "$current_log" || test_exit=$?

    if [ "$test_exit" -eq 0 ]; then
        log_info "All tests passed"

        # Auto-refresh baseline on clean success
        if [ "$RALPH_AUTO_REFRESH_BASELINE" = "true" ]; then
            refresh_baseline_on_success "$baseline_file" "$story_id" 0
        fi

        return 0
    fi

    # Tests failed — check if failures are only pre-existing
    if compare_test_failures "$baseline_file" "$current_log"; then
        # No new failures — validation passed with pre-existing issues

        # Auto-refresh baseline to current state (prevents contamination)
        if [ "$RALPH_AUTO_REFRESH_BASELINE" = "true" ]; then
            refresh_baseline_on_success "$baseline_file" "$story_id" "$RALPH_CURRENT_FAILURE_COUNT"
        fi

        return 0
    else
        # New failures detected
        return 1
    fi
}
