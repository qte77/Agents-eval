# CC Trace Collection Scripts

Scripts for collecting Claude Code execution artifacts into `CCTraceAdapter`-compatible directory structures for evaluation pipeline integration.

## Scripts

### `collect-cc-solo.sh`

Collects Claude Code solo session data into adapter-expected format.

**Usage:**

```bash
./scripts/collect-cc-traces/collect-cc-solo.sh --name <session-name> --output-dir <path>
```

**Arguments:**

- `--name` (required): Session name identifier
- `--output-dir` (required): Output directory path for collected artifacts

**Output Structure:**

```text
<output-dir>/
├── metadata.json       # Session ID, timestamps, model info
└── tool_calls.jsonl    # Tool usage events (empty placeholder; populated when parsing real sessions)
```

**Example:**

```bash
./scripts/collect-cc-traces/collect-cc-solo.sh --name my-session --output-dir ./artifacts/solo-run
```

### `collect-cc-teams.sh`

Collects Claude Code teams mode artifacts from `~/.claude/teams/` and `~/.claude/tasks/`.

**Usage:**

```bash
./scripts/collect-cc-traces/collect-cc-teams.sh --name <team-name> --output-dir <path> \
  [--teams-source <path>] [--tasks-source <path>]
```

**Arguments:**

- `--name` (required): Team name identifier
- `--output-dir` (required): Output directory path for collected artifacts
- `--teams-source` (optional): Custom path to teams directory (default: `~/.claude/teams`)
- `--tasks-source` (optional): Custom path to tasks directory (default: `~/.claude/tasks`)

**Output Structure:**

```text
<output-dir>/
├── config.json         # Team configuration with members array
├── tasks/              # Task files preserving directory structure
│   ├── task-001.json
│   └── subtasks/
│       └── subtask-001.json
└── inboxes/            # Agent message files (if present)
    └── message-001.json
```

**Example:**

```bash
./scripts/collect-cc-traces/collect-cc-teams.sh --name review-team --output-dir ./artifacts/teams-run
```

**Example with custom source paths:**

```bash
./scripts/collect-cc-traces/collect-cc-teams.sh --name review-team --output-dir ./artifacts/teams-run \
  --teams-source /tmp/mock-teams --tasks-source /tmp/mock-tasks
```

## Exit Codes

All scripts use consistent exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | Artifacts collected successfully |
| `1` | Validation failure | Malformed artifacts or output structure verification failed |
| `2` | Usage error | Missing required parameters or invalid arguments |

## Dependencies

- `bash` (with `set -euo pipefail`)
- `jq` (for JSON validation)

## Integration with CCTraceAdapter

These scripts produce output compatible with `CCTraceAdapter` from `src/app/judge/cc_trace_adapter.py`:

**Solo mode:** `CCTraceAdapter(artifacts_dir=Path("output/"))`

**Teams mode:** `CCTraceAdapter(artifacts_dir=Path("output/"), tasks_dir=Path("output/tasks"))`

## Testing

Tests are in `tests/scripts/test_collect_cc_scripts.py`:

```bash
# Run all script tests
uv run pytest tests/scripts/test_collect_cc_scripts.py -v

# Run specific test
uv run pytest tests/scripts/test_collect_cc_scripts.py::TestCollectCCSolo::test_creates_metadata_json_with_session_info -v
```

## Notes

- **Solo mode**: Creates valid artifact structure even without real CC session data (useful for testing)
- **Teams mode**: Requires source directories to exist (`~/.claude/teams/{name}/` and optionally `~/.claude/tasks/{name}/`)
- **Directory structure**: Teams script preserves nested directory structure when copying task files
- **Validation**: Both scripts validate output structure (required files exist, valid JSON) before exiting with code 0
