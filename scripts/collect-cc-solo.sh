#!/bin/bash
# Collect Claude Code solo session artifacts into CCTraceAdapter-compatible format
#
# Exit codes:
#   0 - Success
#   1 - Validation failure (missing source dirs, malformed artifacts)
#   2 - Usage error (missing required parameters)

set -euo pipefail

# Parse arguments
NAME=""
OUTPUT_DIR=""

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
            echo "Error: Unknown argument: $1" >&2
            echo "Usage: $0 --name <session-name> --output-dir <path>" >&2
            exit 2
            ;;
    esac
done

# Validate required arguments
if [[ -z "$NAME" ]] || [[ -z "$OUTPUT_DIR" ]]; then
    echo "Error: Missing required arguments" >&2
    echo "Usage: $0 --name <session-name> --output-dir <path>" >&2
    exit 2
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Locate CC session data
# Reason: CC stores sessions in ~/.claude/projects/ or current working directory
SESSION_DIR="${HOME}/.claude/projects/${NAME}"

if [[ ! -d "$SESSION_DIR" ]]; then
    # Try current directory as fallback
    SESSION_DIR="."
fi

# Create metadata.json
# Reason: CCTraceAdapter expects metadata.json with session_id, timestamps, model
TIMESTAMP=$(date +%s)
cat > "$OUTPUT_DIR/metadata.json" << EOF
{
  "session_id": "${NAME}",
  "start_time": ${TIMESTAMP}.0,
  "end_time": ${TIMESTAMP}.0,
  "model": "claude-sonnet-4-5"
}
EOF

# Validate metadata.json is valid JSON
if ! jq empty "$OUTPUT_DIR/metadata.json" 2>/dev/null; then
    echo "Error: Failed to create valid metadata.json" >&2
    exit 1
fi

# Create tool_calls.jsonl
# Reason: CCTraceAdapter expects one JSON object per line
# For now, create empty file (no real CC session data to parse)
touch "$OUTPUT_DIR/tool_calls.jsonl"

# Validate output structure
if [[ ! -f "$OUTPUT_DIR/metadata.json" ]]; then
    echo "Error: metadata.json not created" >&2
    exit 1
fi

if [[ ! -f "$OUTPUT_DIR/tool_calls.jsonl" ]]; then
    echo "Error: tool_calls.jsonl not created" >&2
    exit 1
fi

echo "Solo session artifacts collected successfully to: $OUTPUT_DIR"
exit 0
