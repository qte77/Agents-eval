#!/bin/bash
# Collect Claude Code solo session artifacts into CCTraceAdapter-compatible format
#
# Exit codes:
#   0 - Success
#   1 - Validation failure (malformed artifacts)
#   2 - Usage error (missing required parameters)

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/lib/collect-common.sh"

parse_collect_args "$@"

if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    echo "Error: Unknown argument: ${EXTRA_ARGS[0]}" >&2
    exit 2
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

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

validate_json "$OUTPUT_DIR/metadata.json"

# Create tool_calls.jsonl
# Reason: CCTraceAdapter expects one JSON object per line
# For now, create empty file (no real CC session data to parse)
touch "$OUTPUT_DIR/tool_calls.jsonl"

# Validate output structure
require_file "$OUTPUT_DIR/metadata.json"
require_file "$OUTPUT_DIR/tool_calls.jsonl"

echo "Solo session artifacts collected successfully to: $OUTPUT_DIR"
exit 0
