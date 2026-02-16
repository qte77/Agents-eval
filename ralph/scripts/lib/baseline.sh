#!/bin/bash
#
# Baseline-aware test validation for Ralph Loop
#
# Captures pre-existing test failures at loop start, then only blocks
# story advancement on NEW failures (regressions). This prevents
# unrelated failures from blocking story progress.
#
# Source this file: source "$SCRIPT_DIR/lib/baseline.sh"
#
# Functions:
#   capture_test_baseline   - Snapshot current failing tests
#   compare_test_failures   - Diff current failures against baseline
#   run_quality_checks_baseline - Lint/type/test with baseline comparison
#

# Capture current test failures as baseline.
# Creates a sorted list of FAILED test IDs for later comparison.
#
# Args:
#   $1 - Path to baseline file
capture_test_baseline() {
    local baseline_file="$1"

    log_info "Capturing test baseline..."
    mkdir -p "$(dirname "$baseline_file")"

    local test_output
    test_output=$(uv run pytest --tb=no -q 2>&1) || true

    # Extract FAILED lines, strip "FAILED " prefix, sort
    # Reason: grep returns 1 when no matches; || true prevents set -e abort
    echo "$test_output" \
        | { grep "^FAILED " || true; } \
        | sed 's/^FAILED //' \
        | sort > "$baseline_file"

    local count
    count=$(wc -l < "$baseline_file" | tr -d ' ')

    if [ "$count" -eq 0 ]; then
        log_info "Baseline captured: all tests passing"
    else
        log_warn "Baseline captured: $count pre-existing failure(s)"
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

    # Extract current FAILED lines into sorted temp file
    local current_failures
    current_failures=$(mktemp /tmp/claude/ralph_current_failures.XXXXXX)
    # Reason: grep returns 1 when no matches; || true prevents set -e abort
    { grep "^FAILED " "$current_log" || true; } \
        | sed 's/^FAILED //' \
        | sort > "$current_failures"

    # Find new failures (in current but not in baseline)
    local new_failures
    new_failures=$(comm -13 "$baseline_file" "$current_failures")

    # Find resolved failures (in baseline but not in current)
    local resolved_failures
    resolved_failures=$(comm -23 "$baseline_file" "$current_failures")

    local baseline_count current_count new_count resolved_count
    baseline_count=$(wc -l < "$baseline_file" | tr -d ' ')
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
        rm "$current_failures"
        return 1
    fi

    local preexisting=$((current_count - new_count))
    if [ "$preexisting" -gt 0 ]; then
        log_warn "$preexisting pre-existing test failure(s) (from baseline, not blocking)"
    fi

    log_success "No new test failures — baseline-aware validation passed"
    rm "$current_failures"
    return 0
}

# Run quality checks with baseline-aware test comparison.
# Lint/type/complexity checks fail-fast. Test failures are compared
# against the baseline to distinguish regressions from pre-existing issues.
#
# Args:
#   $1 - Path to baseline file
run_quality_checks_baseline() {
    local baseline_file="$1"
    local current_log="/tmp/claude/ralph_current_tests.log"

    log_info "Running quality checks (baseline-aware)..."
    mkdir -p "$(dirname "$current_log")"

    # Phase 1: Lint/type/complexity (fail-fast)
    log_info "Phase 1: Lint/type/complexity checks..."

    if ! make ruff 2>&1; then
        log_error "Ruff formatting/linting failed"
        return 1
    fi

    if ! make ruff_tests 2>&1; then
        log_error "Ruff test linting failed"
        return 1
    fi

    if ! make type_check 2>&1; then
        log_error "Type checking failed"
        return 1
    fi

    if ! make complexity 2>&1; then
        log_error "Complexity check failed"
        return 1
    fi

    log_info "Phase 1 passed"

    # Phase 2: Tests with baseline comparison
    log_info "Phase 2: Tests with baseline comparison..."

    local test_exit=0
    uv run pytest --tb=no -q 2>&1 | tee "$current_log" || test_exit=$?

    if [ "$test_exit" -eq 0 ]; then
        log_info "All tests passed"
        return 0
    fi

    # Tests failed — check if failures are only pre-existing
    compare_test_failures "$baseline_file" "$current_log"
}
