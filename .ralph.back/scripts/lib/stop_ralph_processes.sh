#!/bin/bash
# Stop all Ralph processes without deleting state or data.
# Can be sourced as a library or called directly.

_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v log_info &> /dev/null; then
    source "$_LIB_DIR/common.sh"
fi

stop_ralph_processes() {
    log_info "Stopping Ralph loops..."

    # Phase 1: Kill Ralph script processes
    local ralph_pids
    ralph_pids=$(ps aux | grep "ralph/scripts/ralph.sh" | grep -v grep | awk '{print $2}' || true)
    if [ -n "$ralph_pids" ]; then
        log_info "Found Ralph processes: $ralph_pids"
        kill $ralph_pids 2>/dev/null || true
        sleep 1
        kill -9 $ralph_pids 2>/dev/null || true
        log_info "Ralph loops terminated"
    else
        log_info "No running Ralph loops found"
    fi

    # Phase 2: Kill orphaned Claude processes spawned by Ralph
    local claude_pids
    claude_pids=$(ps aux | grep "claude -p.*dangerously-skip-permissions" | grep -v grep | awk '{print $2}' || true)
    if [ -n "$claude_pids" ]; then
        log_info "Cleaning up orphaned Claude processes: $claude_pids"
        kill $claude_pids 2>/dev/null || true
        sleep 1
        kill -9 $claude_pids 2>/dev/null || true
    fi

    log_info "Stop complete"
}

# Run directly if not sourced
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    stop_ralph_processes
fi
