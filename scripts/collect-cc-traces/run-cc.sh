#!/bin/bash
# Run Claude Code and collect artifacts into CCTraceAdapter-compatible format.
#
# Supports two modes:
#   Solo mode (default): Single CC session, no orchestration
#   Teams mode (--teams): CC with Agent Teams orchestration enabled
#
# Usage:
#   ./collect-cc-solo.sh --paper-id <id> [--output-dir <path>] [--timeout <s>] [--model <m>] [--teams]
#
# Output (solo):
#   <output-dir>/metadata.json      - Session ID, timestamps, model, cost
#   <output-dir>/tool_calls.jsonl   - Tool usage events from CC session
#   <output-dir>/raw_stream.jsonl   - Raw stream-json capture (for debugging)
#
# Output (teams, in addition to solo artifacts):
#   <output-dir>/config.json        - Team config (copied from ~/.claude/teams/)
#   <output-dir>/inboxes/           - Agent mailboxes (copied from ~/.claude/teams/)
#   <output-dir>/tasks/             - Task files (copied from ~/.claude/tasks/)
#
# Exit codes:
#   0 - Success
#   1 - CC execution or validation failure
#   2 - Usage error (missing params or claude CLI not found)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/collect-common.sh"

# Defaults
PAPER_ID=""
OUTPUT_DIR=""
TIMEOUT=300
CC_MODEL=""
TEAMS_MODE=false
TEAMS_SOURCE="${HOME}/.claude/teams"
TASKS_SOURCE="${HOME}/.claude/tasks"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --paper-id)  PAPER_ID="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --timeout)   TIMEOUT="$2"; shift 2 ;;
        --model)     CC_MODEL="$2"; shift 2 ;;
        --teams)     TEAMS_MODE=true; shift ;;
        --teams-source) TEAMS_SOURCE="$2"; shift 2 ;;
        --tasks-source) TASKS_SOURCE="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 --paper-id <id> [--output-dir <path>] [--timeout <s>] [--model <m>] [--teams]"
            echo ""
            echo "Arguments:"
            echo "  --paper-id      Paper ID for PeerRead review (required)"
            echo "  --output-dir    Output directory (default: logs/cc/{solo|teams}/<id>_<ts>)"
            echo "  --timeout       CC execution timeout in seconds (default: 300)"
            echo "  --model         Claude model override (e.g., sonnet, opus, haiku)"
            echo "  --teams         Enable Agent Teams orchestration mode"
            echo "  --teams-source  Custom ~/.claude/teams path (default: ~/.claude/teams)"
            echo "  --tasks-source  Custom ~/.claude/tasks path (default: ~/.claude/tasks)"
            exit 0
            ;;
        *) echo "Error: Unknown argument: $1" >&2; exit 2 ;;
    esac
done

# Validate required args
if [[ -z "$PAPER_ID" ]]; then
    echo "Error: --paper-id is required" >&2
    echo "Usage: $0 --paper-id <id> [--output-dir <path>] [--timeout <s>] [--model <m>] [--teams]" >&2
    exit 2
fi

# Check claude CLI
if ! command -v claude &>/dev/null; then
    echo "Error: claude CLI not found. Install: curl -fsSL https://claude.ai/install.sh | bash" >&2
    exit 2
fi

# Derive defaults
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MODE_LABEL="solo"
if [[ "$TEAMS_MODE" == "true" ]]; then
    MODE_LABEL="teams"
fi
OUTPUT_DIR="${OUTPUT_DIR:-logs/cc/${MODE_LABEL}/${PAPER_ID}_${TIMESTAMP}}"

echo "=== CC ${MODE_LABEL} artifact collection ==="
echo "Paper:   $PAPER_ID"
echo "Output:  $OUTPUT_DIR"
echo "Timeout: ${TIMEOUT}s"
[[ -n "$CC_MODEL" ]] && echo "Model:   $CC_MODEL"
echo ""

mkdir -p "$OUTPUT_DIR"

# Build prompt
# Reason: solo uses direct review prompt; teams uses a prompt that triggers team creation
if [[ "$TEAMS_MODE" == "true" ]]; then
    PROMPT="Create a team to review paper ${PAPER_ID} from PeerRead. \
Assign a researcher to analyze methodology, an analyst to evaluate technical claims, \
and a synthesizer to compile the final structured peer review with ratings. \
Coordinate via task list. The review must cover strengths, weaknesses, technical \
soundness, and provide recommendation scores (1-5)."
else
    PROMPT="Review paper ${PAPER_ID} from the PeerRead dataset. \
Provide a structured peer review covering: summary, strengths, weaknesses, \
technical assessment, clarity, and a recommendation score (1-5)."
fi

# Build claude command
# Reason: stream-json requires --verbose in print mode
CLAUDE_CMD=(claude -p "$PROMPT" --output-format stream-json --verbose)
if [[ -n "$CC_MODEL" ]]; then
    CLAUDE_CMD+=(--model "$CC_MODEL")
fi

# Reason: teams mode requires experimental env flag
if [[ "$TEAMS_MODE" == "true" ]]; then
    export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
fi

# Run CC and capture stream-json output
RAW_OUTPUT="$OUTPUT_DIR/raw_stream.jsonl"
echo "Running: claude -p --output-format stream-json ..."

CC_EXIT=0
if timeout "$TIMEOUT" "${CLAUDE_CMD[@]}" > "$RAW_OUTPUT" 2>"$OUTPUT_DIR/stderr.log"; then
    CC_EXIT=0
else
    CC_EXIT=$?
fi

if [[ $CC_EXIT -ne 0 ]]; then
    if [[ $CC_EXIT -eq 124 ]]; then
        echo "Error: Claude Code timed out after ${TIMEOUT}s" >&2
    else
        echo "Error: Claude Code exited with code $CC_EXIT" >&2
        [[ -s "$OUTPUT_DIR/stderr.log" ]] && cat "$OUTPUT_DIR/stderr.log" >&2
    fi
    exit 1
fi

echo "Claude Code completed successfully"
echo ""

# ---- Extract metadata from stream-json ----

# Reason: init message has session_id + model; result message has timing + cost
SESSION_ID=$(jq -r 'select(.type == "system" and .subtype == "init") | .session_id // empty' < "$RAW_OUTPUT" 2>/dev/null | head -1)
MODEL=$(jq -r 'select(.type == "system" and .subtype == "init") | .model // empty' < "$RAW_OUTPUT" 2>/dev/null | head -1)
DURATION_MS=$(jq -r 'select(.type == "result") | .duration_ms // 0' < "$RAW_OUTPUT" 2>/dev/null | head -1)
COST_USD=$(jq -r 'select(.type == "result") | .total_cost_usd // 0' < "$RAW_OUTPUT" 2>/dev/null | head -1)
NUM_TURNS=$(jq -r 'select(.type == "result") | .num_turns // 0' < "$RAW_OUTPUT" 2>/dev/null | head -1)

# Fallbacks
SESSION_ID="${SESSION_ID:-cc-${MODE_LABEL}-${PAPER_ID}}"
MODEL="${MODEL:-unknown}"
DURATION_MS="${DURATION_MS:-0}"
COST_USD="${COST_USD:-0}"
NUM_TURNS="${NUM_TURNS:-0}"

# Compute timestamps
END_TS=$(date +%s)
# Reason: derive start from end minus duration
START_TS=$(echo "$END_TS $DURATION_MS" | awk '{printf "%.3f", $1 - ($2 / 1000)}')

# Write metadata.json (CCTraceAdapter solo format)
cat > "$OUTPUT_DIR/metadata.json" << EOF
{
  "session_id": "${SESSION_ID}",
  "start_time": ${START_TS},
  "end_time": ${END_TS}.0,
  "model": "${MODEL}",
  "duration_ms": ${DURATION_MS},
  "total_cost_usd": ${COST_USD},
  "num_turns": ${NUM_TURNS},
  "paper_id": "${PAPER_ID}",
  "mode": "${MODE_LABEL}"
}
EOF

validate_json "$OUTPUT_DIR/metadata.json"

# ---- Extract tool calls from assistant messages ----

# Reason: tool_use content blocks in assistant messages represent CC tool invocations
jq -c '
  select(.type == "assistant")
  | .message.content[]?
  | select(.type == "tool_use")
  | {
      tool_name: .name,
      agent_id: "claude",
      timestamp: now,
      duration: 0,
      success: true,
      context: (.input | tostring | .[0:200])
    }
' < "$RAW_OUTPUT" > "$OUTPUT_DIR/tool_calls.jsonl" 2>/dev/null || touch "$OUTPUT_DIR/tool_calls.jsonl"

# ---- Teams mode: collect team artifacts from ~/.claude/ ----

if [[ "$TEAMS_MODE" == "true" ]]; then
    echo "Collecting teams artifacts..."

    # Reason: find the most recent team directory created during this session
    # CC writes to ~/.claude/teams/{team-name}/ — find by most recent mtime
    LATEST_TEAM=""
    if [[ -d "$TEAMS_SOURCE" ]]; then
        LATEST_TEAM=$(find "$TEAMS_SOURCE" -maxdepth 1 -mindepth 1 -type d \
            -newer "$RAW_OUTPUT" -printf '%T@ %p\n' 2>/dev/null \
            | sort -rn | head -1 | awk '{print $2}')

        # Fallback: if no team newer than raw_output, take the most recent one
        if [[ -z "$LATEST_TEAM" ]]; then
            LATEST_TEAM=$(find "$TEAMS_SOURCE" -maxdepth 1 -mindepth 1 -type d \
                -printf '%T@ %p\n' 2>/dev/null \
                | sort -rn | head -1 | awk '{print $2}')
        fi
    fi

    if [[ -n "$LATEST_TEAM" ]] && [[ -f "$LATEST_TEAM/config.json" ]]; then
        TEAM_NAME=$(basename "$LATEST_TEAM")
        echo "  Found team: $TEAM_NAME"

        # Copy config.json
        cp "$LATEST_TEAM/config.json" "$OUTPUT_DIR/config.json"
        validate_json "$OUTPUT_DIR/config.json"

        # Copy inboxes
        if [[ -d "$LATEST_TEAM/inboxes" ]]; then
            mkdir -p "$OUTPUT_DIR/inboxes"
            cp -r "$LATEST_TEAM/inboxes"/* "$OUTPUT_DIR/inboxes/" 2>/dev/null || true
        fi

        # Copy tasks from sibling tasks directory
        TEAM_TASKS_DIR="${TASKS_SOURCE}/${TEAM_NAME}"
        if [[ -d "$TEAM_TASKS_DIR" ]] && [[ -n "$(ls -A "$TEAM_TASKS_DIR" 2>/dev/null)" ]]; then
            mkdir -p "$OUTPUT_DIR/tasks"
            cp -r "$TEAM_TASKS_DIR"/* "$OUTPUT_DIR/tasks/" 2>/dev/null || true
        fi
    else
        echo "  Warning: No CC teams artifacts found in $TEAMS_SOURCE"
        echo "  (CC may not have created a team for this prompt)"
    fi
fi

# ---- Summary ----

require_file "$OUTPUT_DIR/metadata.json"
require_file "$OUTPUT_DIR/tool_calls.jsonl"

TOOL_COUNT=$(wc -l < "$OUTPUT_DIR/tool_calls.jsonl" | tr -d ' ')

echo ""
echo "Artifacts collected:"
echo "  Session:  $SESSION_ID"
echo "  Model:    $MODEL"
echo "  Duration: ${DURATION_MS}ms"
echo "  Cost:     \$${COST_USD}"
echo "  Turns:    $NUM_TURNS"
echo "  Tools:    $TOOL_COUNT tool calls"
echo "  Output:   $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  make run_cli ARGS=\"--paper-number=$PAPER_ID --cc-${MODE_LABEL/teams/teams}-dir=$OUTPUT_DIR\""
