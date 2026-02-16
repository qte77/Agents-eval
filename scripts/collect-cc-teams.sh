#!/bin/bash
# Collect Claude Code teams mode artifacts into CCTraceAdapter-compatible format
#
# Exit codes:
#   0 - Success
#   1 - Validation failure (missing source dirs, malformed artifacts)
#   2 - Usage error (missing required parameters)

set -euo pipefail

# Parse arguments
NAME=""
OUTPUT_DIR=""
TEAMS_SOURCE="${HOME}/.claude/teams"
TASKS_SOURCE="${HOME}/.claude/tasks"

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

# Validate required arguments
if [[ -z "$NAME" ]] || [[ -z "$OUTPUT_DIR" ]]; then
    echo "Error: Missing required arguments" >&2
    echo "Usage: $0 --name <team-name> --output-dir <path> [--teams-source <path>] [--tasks-source <path>]" >&2
    exit 2
fi

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

# Validate copied config.json is valid JSON
if ! jq empty "$OUTPUT_DIR/config.json" 2>/dev/null; then
    echo "Error: Invalid JSON in config.json" >&2
    exit 1
fi

# Copy task files if tasks directory exists
if [[ -d "$TASKS_DIR" ]]; then
    # Create tasks subdirectory in output
    mkdir -p "$OUTPUT_DIR/tasks"

    # Copy all JSON files preserving directory structure
    # Reason: CCTraceAdapter expects tasks/ subdirectory with preserved structure
    if [[ -n "$(ls -A "$TASKS_DIR" 2>/dev/null)" ]]; then
        # Use rsync to preserve structure, or fall back to cp -r
        if command -v rsync &> /dev/null; then
            rsync -av --include='*/' --include='*.json' --exclude='*' "$TASKS_DIR/" "$OUTPUT_DIR/tasks/"
        else
            cp -r "$TASKS_DIR"/* "$OUTPUT_DIR/tasks/" 2>/dev/null || true
        fi
    fi
fi

# Copy inboxes if they exist (optional)
if [[ -d "$TEAM_DIR/inboxes" ]]; then
    mkdir -p "$OUTPUT_DIR/inboxes"
    cp -r "$TEAM_DIR/inboxes"/* "$OUTPUT_DIR/inboxes/" 2>/dev/null || true
fi

# Validate output structure
if [[ ! -f "$OUTPUT_DIR/config.json" ]]; then
    echo "Error: config.json not created in output" >&2
    exit 1
fi

echo "Teams mode artifacts collected successfully to: $OUTPUT_DIR"
exit 0
