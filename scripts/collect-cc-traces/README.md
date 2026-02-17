# CC Trace Collection Scripts

Scripts for collecting Claude Code execution artifacts into `CCTraceAdapter`-compatible directory structures for evaluation pipeline integration.

## Quick Start

```bash
# CC Solo: run CC and collect artifacts
make cc_solo PAPER_ID=1105.1072

# CC Teams: run CC with Agent Teams orchestration
make cc_teams_run PAPER_ID=1105.1072 CC_TIMEOUT=600

# CC Teams: collect artifacts from an existing team
make cc_teams_collect TEAM_NAME=my-review-team

# Then compare against MAS
make run_cli ARGS="--paper-number=1105.1072 --cc-solo-dir=logs/cc/solo/1105.1072_<timestamp>"
```

## Default Output Paths

| Mode | Default output | Contents |
|------|---------------|----------|
| Solo | `logs/cc/solo/<paper-id>_<timestamp>/` | `metadata.json`, `tool_calls.jsonl`, `raw_stream.jsonl` |
| Teams | `logs/cc/teams/<paper-id>_<timestamp>/` | Above + `config.json`, `inboxes/`, `tasks/` |

## CC Default Artifact Locations

Claude Code writes artifacts to these paths automatically:

| Artifact | Path | Description |
|----------|------|-------------|
| Team config | `~/.claude/teams/{team-name}/config.json` | Team metadata, member roster |
| Agent mailboxes | `~/.claude/teams/{team-name}/inboxes/{agent}.json` | Per-agent message arrays |
| Task files | `~/.claude/tasks/{team-name}/{task-id}.json` | Task status and ownership |
| Session transcripts | `~/.claude/transcripts/{session-id}.jsonl` | Full session log (when enabled) |

## Scripts

### `collect-cc-solo.sh`

Runs Claude Code and collects artifacts into CCTraceAdapter format. Supports both solo and teams mode via `--teams` flag.

**Usage:**

```bash
# Solo mode (default)
./scripts/collect-cc-traces/collect-cc-solo.sh --paper-id 1105.1072

# Teams mode
./scripts/collect-cc-traces/collect-cc-solo.sh --paper-id 1105.1072 --teams

# With options
./scripts/collect-cc-traces/collect-cc-solo.sh \
  --paper-id 1105.1072 \
  --output-dir ./artifacts/solo-run \
  --timeout 300 \
  --model sonnet
```

**Arguments:**

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-id` | Yes | - | Paper ID for PeerRead review |
| `--output-dir` | No | `logs/cc/{mode}/<id>_<ts>` | Output directory |
| `--timeout` | No | `300` | CC execution timeout (seconds) |
| `--model` | No | CC default | Claude model (sonnet, opus, haiku) |
| `--teams` | No | `false` | Enable Agent Teams orchestration |
| `--teams-source` | No | `~/.claude/teams` | Custom teams artifact source |
| `--tasks-source` | No | `~/.claude/tasks` | Custom tasks artifact source |

**How it works:**

1. Invokes `claude -p "<review prompt>" --output-format stream-json`
2. Captures raw JSONL output (init, assistant, tool_use, result messages)
3. Extracts `metadata.json` from init + result messages (session_id, model, duration, cost)
4. Extracts `tool_calls.jsonl` from tool_use content blocks in assistant messages
5. (Teams mode) Copies `config.json`, `inboxes/`, `tasks/` from `~/.claude/`

### `collect-cc-teams.sh`

Collects existing Claude Code teams artifacts from `~/.claude/teams/` and `~/.claude/tasks/` (no CC invocation).

**Usage:**

```bash
./scripts/collect-cc-traces/collect-cc-teams.sh --name review-team --output-dir ./artifacts/teams-run
```

**Arguments:**

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--name` | Yes | - | Team name identifier |
| `--output-dir` | Yes | - | Output directory |
| `--teams-source` | No | `~/.claude/teams` | Custom teams source |
| `--tasks-source` | No | `~/.claude/tasks` | Custom tasks source |

## CC stream-json Output Format

`claude -p --output-format stream-json` emits one JSON object per line:

```text
{"type":"system","subtype":"init","session_id":"abc","model":"claude-sonnet-4-5-20250929",...}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{...}},...]},...}
{"type":"result","session_id":"abc","duration_ms":1234,"total_cost_usd":0.003,"num_turns":6,...}
```

The collection script extracts:
- **metadata.json**: `session_id`, `model`, timestamps, `duration_ms`, `total_cost_usd` from init + result
- **tool_calls.jsonl**: `tool_name`, `agent_id`, `timestamp` from `tool_use` blocks in assistant messages

## Integration with CCTraceAdapter

These scripts produce output compatible with `CCTraceAdapter` from `src/app/judge/cc_trace_adapter.py`:

```python
# Solo mode
adapter = CCTraceAdapter(artifacts_dir=Path("logs/cc/solo/1105.1072_20260217/"))
trace = adapter.parse()  # -> GraphTraceData

# Teams mode
adapter = CCTraceAdapter(
    artifacts_dir=Path("logs/cc/teams/1105.1072_20260217/"),
    tasks_dir=Path("logs/cc/teams/1105.1072_20260217/tasks"),
)
trace = adapter.parse()  # -> GraphTraceData
```

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | Artifacts collected successfully |
| `1` | Failure | CC execution error, timeout, or validation failure |
| `2` | Usage error | Missing required parameters or `claude` CLI not found |

## Dependencies

- `claude` CLI (Claude Code)
- `bash` (with `set -euo pipefail`)
- `jq` (for JSON extraction and validation)
- `timeout` (coreutils)
