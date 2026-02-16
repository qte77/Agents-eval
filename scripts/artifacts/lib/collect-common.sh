#!/bin/bash
#
# Shared utilities for CC artifact collection scripts.
# Source this file: source "$(dirname "${BASH_SOURCE[0]}")/../lib/collect-common.sh"
#

# Parse --name and --output-dir from arguments.
# Sets NAME and OUTPUT_DIR variables. Passes unknown args back via EXTRA_ARGS.
# Exits 2 on missing required arguments.
#
# Args:
#   "$@" - all script arguments
#
# Usage:
#   parse_collect_args "$@"
#   set -- "${EXTRA_ARGS[@]}"  # remaining args for script-specific parsing
parse_collect_args() {
    NAME=""
    OUTPUT_DIR=""
    EXTRA_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            --name)
                NAME="$2"
                shift 2
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            *)
                EXTRA_ARGS+=("$1")
                shift
                ;;
        esac
    done

    if [[ -z "$NAME" ]] || [[ -z "$OUTPUT_DIR" ]]; then
        echo "Error: --name and --output-dir are required" >&2
        return 2
    fi
}

# Validate a file contains valid JSON. Exits 1 on failure.
#
# Args:
#   $1 - path to JSON file
validate_json() {
    local file="$1"
    if ! jq empty "$file" 2>/dev/null; then
        echo "Error: Invalid JSON in $(basename "$file")" >&2
        return 1
    fi
}

# Verify a file exists. Exits 1 if missing.
#
# Args:
#   $1 - path to file
require_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "Error: $(basename "$file") not created" >&2
        return 1
    fi
}
