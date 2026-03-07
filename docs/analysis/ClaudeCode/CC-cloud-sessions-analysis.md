---
title: CC Cloud Sessions (Claude Code on the Web) Analysis
source: https://code.claude.com/docs/en/claude-code-on-the-web
purpose: Analysis of Claude Code cloud execution for parallel baseline collection, remote task offloading, and CI-like autonomous runs within Agents-eval workflows.
created: 2026-03-07
---

**Status**: Research preview

## What Claude Code on the Web Is

Run Claude Code tasks on Anthropic-managed cloud VMs via `claude.ai/code` or the Claude mobile app ([source][cc-cloud]). Each session clones a GitHub repo into an isolated VM, runs a setup script, executes the task, and pushes results to a branch for PR creation. No local machine needed.

### Key Mechanics

- **GitHub-only**: Requires GitHub-hosted repository with Claude GitHub app installed ([source][cc-cloud])
- **Isolated VMs**: Each session runs in its own Anthropic-managed VM ([source][cc-cloud])
- **Default image**: Pre-installed Python, Node.js, Ruby, PHP, Java, Go, Rust, C++, PostgreSQL 16, Redis 7.0 ([source][cc-cloud])
- **Setup scripts**: Bash scripts run before Claude Code launches (install deps, configure tools) ([source][cc-cloud])
- **Network policy**: Limited by default (allowlisted domains), configurable to "No internet" or "Full" ([source][cc-cloud])
- **Diff view**: Review changes inline before creating PR, iterate with comments ([source][cc-cloud])
- **Session sharing**: Team visibility (Enterprise/Teams) or Public (Max/Pro) ([source][cc-cloud])

### Starting Sessions

```bash
# From terminal — creates new cloud session
claude --remote "Fix the authentication bug in src/auth/login.ts"

# Parallel tasks
claude --remote "Fix flaky test in auth.spec.ts"
claude --remote "Update API documentation"
claude --remote "Refactor logger to structured output"

# Monitor
/tasks
```

### Terminal-to-Web-to-Terminal Flow

<!-- markdownlint-disable MD013 -->

| Direction | Method | Details |
| --------- | ------ | ------- |
| Terminal -> Web | `claude --remote "prompt"` | Creates new cloud session; runs independently |
| Web -> Terminal | `/teleport` or `claude --teleport` | Fetches branch, loads conversation history into terminal |
| Plan -> Execute | `claude --permission-mode plan` then `claude --remote "Execute plan"` | Plan locally (read-only), execute remotely |

<!-- markdownlint-enable MD013 -->

**Teleport requirements**: Clean git state, correct repository (not fork), branch pushed to remote, same Claude.ai account ([source][cc-cloud]).

### Environment Configuration

```bash
# Setup script (runs before Claude Code launches)
#!/bin/bash
apt update && apt install -y gh
npm install
pip install -r requirements.txt
```

- **Setup scripts**: Run only on new sessions (not resume). Non-zero exit = session fails ([source][cc-cloud])
- **SessionStart hooks**: Run on every session start (local + cloud). Use `CLAUDE_CODE_REMOTE` env var to scope ([source][cc-hooks])
- **Environment variables**: Configured in UI as `.env` format key-value pairs ([source][cc-cloud])

### Network Access Levels

| Level | Behavior |
| ----- | -------- |
| Limited (default) | Allowlisted domains only (GitHub, npm, PyPI, Docker, cloud providers, etc.) |
| No internet | Only Anthropic API communication |
| Full | Unrestricted outbound access |

### Security Model

- **GitHub proxy**: Scoped credentials; push restricted to current working branch ([source][cc-cloud])
- **HTTP/HTTPS proxy**: All outbound traffic through security proxy (rate limiting, content filtering) ([source][cc-cloud])
- **Credential isolation**: Git credentials and signing keys never inside sandbox ([source][cc-cloud])

### Pricing

Shares rate limits with all Claude/Claude Code usage. Parallel tasks consume proportionally more ([source][cc-cloud]).

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Workflow | Fit | Rationale |
| -------- | --- | --------- |
| Parallel CC baseline collection | Strong | `claude --remote` can run N tasks simultaneously on cloud VMs; no local resource contention |
| Ralph loop execution | Moderate | Could run `claude --remote "Execute stories from prd.json"` but loses local state files and MCP servers |
| CI/CD integration (PR review) | Strong | Kick off cloud session for automated review; results appear as PR |
| Interactive development | Weak | Latency to clone + setup; better to use local CC or Remote Control |
| Writeup generation | Weak | Needs local LaTeX toolchain, pandoc, custom scripts — cloud VM setup would be complex |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**Use cloud sessions for parallel, independent tasks that only need GitHub repo access. Use local CC (+ Remote Control) for workflows requiring local MCP servers, state files, or custom toolchains.** See [CC-remote-control-analysis.md](CC-remote-control-analysis.md#remote-control-vs-claude-code-on-the-web) for detailed comparison.

### Potential Integration

```makefile
# Example (NOT implemented — YAGNI until measured need)
CC_REMOTE_TASKS ?=
cc_run_cloud:
    @for task in $(CC_REMOTE_TASKS); do \
        claude --remote "$$task"; \
    done
    @echo "Monitor with: /tasks"
```

**Recommendation**: Worth exploring for CC baseline collection where local resources are constrained. Key blockers for deeper adoption:

1. **GitHub-only** — project must be on GitHub (already is)
2. **No local MCP servers** — Context7, Exa, and IDE MCP servers unavailable in cloud
3. **No persistent state** — `~/.claude/teams/` and Ralph state files not available
4. **Setup script complexity** — Would need to install uv, project deps, and configure env
5. **Research preview** — pricing and availability may change

Revisit when:

1. Cloud sessions support custom Docker images or snapshots
2. MCP server forwarding becomes available
3. Baseline collection needs more parallelism than local machine can provide

## References

- [CC Cloud Sessions docs][cc-cloud]
- [CC Remote Control docs][cc-rc]
- [CC Hooks docs][cc-hooks]
- [CC Settings docs][cc-settings]

[cc-cloud]: https://code.claude.com/docs/en/claude-code-on-the-web
[cc-rc]: https://code.claude.com/docs/en/remote-control
[cc-hooks]: https://code.claude.com/docs/en/hooks
[cc-settings]: https://code.claude.com/docs/en/settings
