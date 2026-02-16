#!/bin/bash
# Collect Claude Code teams mode artifacts into CCTraceAdapter-compatible format
#
# Exit codes:
#   0 - Success
#   1 - Validation failure (missing source dirs, malformed artifacts)
#   2 - Usage error (missing required parameters)

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/lib/collect-common.sh"

# Defaults for optional args
TEAMS_SOURCE="${HOME}/.claude/teams"
TASKS_SOURCE="${HOME}/.claude/tasks"

parse_collect_args "$@"
set -- "${EXTRA_ARGS[@]}"

# Parse script-specific arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --teams-source)
            TEAMS_SOURCE="$2"
            shift 2
            ;;
        --tasks-source)
            TASKS_SOURCE="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown argument: $1" >&2
            echo "Usage: $0 --name <team-name> --output-dir <path> [--teams-source <path>] [--tasks-source <path>]" >&2
            exit 2
            ;;
    esac
done

# Construct source paths
TEAM_DIR="${TEAMS_SOURCE}/${NAME}"
TASKS_DIR="${TASKS_SOURCE}/${NAME}"

# Validate source directories exist
if [[ ! -d "$TEAM_DIR" ]]; then
    echo "Error: Team directory does not exist: $TEAM_DIR" >&2
    exit 1
fi

# Validate config.json exists
if [[ ! -f "$TEAM_DIR/config.json" ]]; then
    echo "Error: config.json not found in: $TEAM_DIR" >&2
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Copy config.json
cp "$TEAM_DIR/config.json" "$OUTPUT_DIR/config.json"
validate_json "$OUTPUT_DIR/config.json"

# Copy task files if tasks directory exists
if [[ -d "$TASKS_DIR" ]] && [[ -n "$(ls -A "$TASKS_DIR" 2>/dev/null)" ]]; then
    mkdir -p "$OUTPUT_DIR/tasks"
    cp -r "$TASKS_DIR"/* "$OUTPUT_DIR/tasks/" 2>/dev/null || true
fi

# Copy inboxes if they exist (optional)
if [[ -d "$TEAM_DIR/inboxes" ]]; then
    mkdir -p "$OUTPUT_DIR/inboxes"
    cp -r "$TEAM_DIR/inboxes"/* "$OUTPUT_DIR/inboxes/" 2>/dev/null || true
fi

# Validate output structure
require_file "$OUTPUT_DIR/config.json"

echo "Teams mode artifacts collected successfully to: $OUTPUT_DIR"
exit 0
