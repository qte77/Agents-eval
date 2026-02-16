#!/bin/bash
# Live monitoring for Ralph loop execution.
#
# Usage:
#   ./ralph/scripts/watch.sh          # Live tail + process tree
#   ./ralph/scripts/watch.sh status   # Process tree only
#   ./ralph/scripts/watch.sh log      # Show latest log
#   ./ralph/scripts/watch.sh log FILE # Show specific log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

LOG_DIR="logs/ralph"

show_process_tree() {
    echo "=== Ralph Process Tree ==="

    if command -v pstree &> /dev/null; then
        local ralph_pids
        ralph_pids=$(pgrep -f "ralph/scripts/ralph.sh" 2>/dev/null || true)
        ralph_pids=$(echo "$ralph_pids" | grep -v "^$$\$" | grep -v "^$" || true)

        if [ -n "$ralph_pids" ]; then
            echo "$ralph_pids" | while read -r pid; do
                [ -z "$pid" ] && continue
                local pname
                pname=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                echo "--- PID $pid ($pname) ---"
                pstree -a -p "$pid" 2>/dev/null || true
            done
        else
            echo "No active Ralph loop processes found"
        fi
    else
        # Fallback: plain ps
        local ralph_procs
        ralph_procs=$(ps aux | grep -E "ralph/scripts/ralph.sh" | grep -v grep | grep -v "watch.sh" || true)
        local claude_procs
        claude_procs=$(ps aux | grep "claude -p.*dangerously-skip-permissions" | grep -v grep || true)

        if [ -n "$ralph_procs" ] || [ -n "$claude_procs" ]; then
            [ -n "$ralph_procs" ] && echo "$ralph_procs"
            [ -n "$claude_procs" ] && echo "$claude_procs"
        else
            echo "No active Ralph loop processes found"
        fi
    fi
    echo ""
}

get_latest_log() {
    if [ -d "$LOG_DIR" ]; then
        ls -t "$LOG_DIR"/*.log 2>/dev/null | sed -n '1p'
    fi
}

show_log() {
    local log_file="${1:-}"
    if [ -z "$log_file" ]; then
        log_file=$(get_latest_log)
    fi

    if [ -z "$log_file" ] || [ ! -f "$log_file" ]; then
        log_error "No Ralph log files found in $LOG_DIR/"
        exit 1
    fi

    echo "=== Log: $log_file ==="
    cat "$log_file"
}

watch_live() {
    show_process_tree

    local log_file
    log_file=$(get_latest_log)

    if [ -z "$log_file" ] || [ ! -f "$log_file" ]; then
        log_warn "No log files found in $LOG_DIR/"
        log_info "Waiting for Ralph to start..."
        while true; do
            log_file=$(get_latest_log)
            [ -n "$log_file" ] && [ -f "$log_file" ] && break
            sleep 2
        done
    fi

    log_info "Tailing: $log_file (Ctrl+C to exit)"
    tail -f "$log_file"
}

case "${1:-watch}" in
    watch)  watch_live ;;
    status) show_process_tree ;;
    log)    show_log "${2:-}" ;;
    *)
        echo "Usage: $0 [watch|status|log [file]]"
        exit 1
        ;;
esac
