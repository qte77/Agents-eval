# Ralph Contributing

Command reference for the Ralph autonomous development loop.
For project-level development workflows, see the root [CONTRIBUTING.md](../CONTRIBUTING.md).

## Command Reference

| Command | Purpose | Flags |
|---------|---------|-------|
| `make ralph_userstory` | Create UserStory.md interactively via Claude | |
| `make ralph_prd_md` | Generate PRD.md from UserStory.md | |
| `make ralph_prd_json` | Generate prd.json from PRD.md | `DRY_RUN=1` parse-only |
| `make ralph_init` | Initialize Ralph loop environment | `RALPH_PROJECT=name` |
| `make ralph_run` | Run Ralph loop | `MODEL=`, `MAX_ITERATIONS=`, `RALPH_TIMEOUT=`, `TEAMS=` |
| `make ralph_worktree` | Create git worktree for a branch | `BRANCH=` (required) |
| `make ralph_run_worktree` | Create worktree + run Ralph in it | `BRANCH=` (required), `MODEL=`, `MAX_ITERATIONS=`, `RALPH_TIMEOUT=`, `TEAMS=` |
| `make ralph_stop` | Stop all running Ralph loops | |
| `make ralph_status` | Show story progress from prd.json | |
| `make ralph_watch` | Live-watch Ralph log output with process tree | |
| `make ralph_get_log` | Show latest Ralph log | `LOG=path/to/file.log` |
| `make ralph_clean` | Reset Ralph state (removes prd.json, progress.txt) | |

## Common Flags

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `MODEL` | `sonnet`, `opus`, `haiku` | `sonnet` | Claude model |
| `MAX_ITERATIONS` | integer | `25` | Max loop iterations |
| `RALPH_TIMEOUT` | seconds | (none) | Kill after N seconds |
| `TEAMS` | `true`, `false` | `false` | CC Agent Teams mode (experimental) |
| `BRANCH` | branch name | (required) | Git branch for worktree recipes |
| `DRY_RUN` | `1` | (none) | Parse-only for prd_json |

## Typical Workflows

### Run in current directory

```bash
make ralph_init
make ralph_run MODEL=opus
```

### Run in isolated worktree

```bash
make ralph_run_worktree BRANCH=ralph/sprint9-name TEAMS=true MODEL=opus
```

### Monitor and inspect

```bash
make ralph_watch          # live output
make ralph_status         # story progress
make ralph_get_log        # latest log
```
