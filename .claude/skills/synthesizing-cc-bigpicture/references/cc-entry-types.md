# Claude Code JSONL Entry Types

Reference for parsing `~/.claude/projects/<path>/<session-uuid>.jsonl` files.

Source: `randlee/claude-history` entry type taxonomy + CC filesystem documentation.

## Session Transcript Entries

Each line in a session `.jsonl` file is a JSON object with a `type` field:

| Type | Description | Key Fields |
|------|-------------|------------|
| `user` | User messages (prompts or tool results) | `uuid`, `parentUuid`, `timestamp`, `message` |
| `assistant` | Claude responses with text and tool_use | `uuid`, `parentUuid`, `timestamp`, `message` |
| `system` | System events and hook summaries | `timestamp`, `event` |
| `queue-operation` | Subagent spawn triggers | `agentId`, `sessionId` |
| `progress` | Status updates during processing | `timestamp`, `status` |
| `file-history-snapshot` | Git state captured at session start | `staged`, `unstaged`, `untracked` |
| `summary` | Conversation summaries (from auto-compaction) | `timestamp`, `content` |
| `result` | Session completion markers | `timestamp`, `status` |

## Global History

`~/.claude/history.jsonl` — global prompt log, one entry per user message:

```json
{
  "display": "the user prompt text",
  "timestamp": "2026-03-20T14:30:00Z",
  "project": "/workspaces/my-project",
  "sessionId": "uuid"
}
```

Use for session discovery (unique `sessionId` values), timeline reconstruction,
and prompt topic analysis. Preferred over globbing `.jsonl` files when
`sessions-index.json` is unavailable.

## Stats Cache

`~/.claude/stats-cache.json` — daily activity aggregates:

```json
{
  "2026-03-20": {
    "messageCount": 42,
    "sessionCount": 5,
    "toolCallCount": 128
  }
}
```

Use for trajectory signal (active vs. stale days, trend detection).

## Plans

`~/.claude/plans/*.md` — plain markdown files with plan names as filenames
(often auto-generated whimsical names like `tingly-weaving-kite.md`).

## Tasks

`~/.claude/tasks/<session-or-team-name>/<N>.json` — structured objects:

```json
{
  "id": "3",
  "subject": "Task title",
  "description": "Task details",
  "status": "in_progress",
  "activeForm": "agent-form",
  "owner": "member-name",
  "blocks": ["4", "5"],
  "blockedBy": ["1"]
}
```

The `blocks`/`blockedBy` arrays create a dependency graph within a task list.
Task directories also contain `.lock` and `.highwatermark` state files (skip these).

## Teams

`~/.claude/teams/<team-name>/` — directory per team:

- `config.json` — team configuration:

  ```json
  {
    "name": "team-name",
    "description": "Team purpose",
    "members": [
      {
        "name": "member-name",
        "model": "claude-sonnet-4-6",
        "prompt": "system prompt",
        "role": "developer"
      }
    ]
  }
  ```

- `inboxes/<member-name>.json` — agent-to-agent messages:

  ```json
  [
    {
      "from": "other-member",
      "text": "Full message content",
      "summary": "Brief summary",
      "timestamp": "2026-03-20T14:30:00Z"
    }
  ]
  ```

## Subagent Transcripts

`~/.claude/projects/<path>/<session-uuid>/subagents/agent-<id>.jsonl` — full
transcripts of subagent sessions spawned within a parent session. Same entry
format as session `.jsonl` files.

## Project Memory

`~/.claude/projects/<path>/memory/MEMORY.md` — persistent per-project knowledge
loaded at conversation start.

## Path Encoding

Project paths are URL-encoded with dashes:
- `/home/user/myapp` → `-home-user-myapp`
- `/workspaces/Agents-eval` → `-workspaces-Agents-eval`
- `C:\Users\name\project` → `C--Users-name-project`
