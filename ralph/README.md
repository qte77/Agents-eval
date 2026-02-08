# Ralph Loop - Autonomous TDD development loop with Claude Code

Autonomous AI development loop that iteratively implements stories until all acceptance criteria pass.

## What is Ralph?

Named after Ralph Wiggum from The Simpsons, this technique by Geoffrey Huntley implements self-referential AI development loops. The agent sees its own previous work in files and git history, iteratively improving until completion.

**Core Loop:**

```text
while stories remain:
  1. Read prd.json, pick next story (passes: false)
  2. Implement story
  3. Run typecheck + tests (TDD: red → green → refactor)
  4. If passing: commit, mark done, log learnings
  5. Repeat until all pass (or context limit)
```

**Memory persists only through:**

- `prd.json` - Task status and acceptance criteria
- `progress.txt` - Learnings and patterns
- Git commits - Code changes

**Usage:**

```bash
make ralph_run MAX_ITERATIONS=25    # Run autonomous development
make ralph_status                   # Check progress
```

**Configuration:**

Environment variables control Ralph behavior:

- `RALPH_MODEL` - Model selection: sonnet (default), opus, haiku
- `MAX_ITERATIONS` - Loop limit (default: 25)
- `REQUIRE_REFACTOR` - Enforce REFACTOR phase (default: false)

**Sources:**

- [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [ralph-loop@claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop)

---

## Extended Functionality

### TDD Enforcement (Red-Green-Refactor)

Stories require verifiable acceptance criteria with TDD workflow:

1. **Red** - Write failing test (commit with `[RED]` marker)
2. **Green** - Implement until tests pass (commit with `[GREEN]` marker)
3. **Refactor** - Clean up, optimize (optional: commit with `[REFACTOR]` marker)

The Ralph script enforces chronological commit verification and checks for proper phase markers.

### Compound Engineering

Learnings compound over time: **Plan** → **Work** → **Assess** → **Compound**

Sources: [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)

### ACE-FCA (Context Engineering)

Context window management for quality output. See `.claude/rules/context-management.md`

Source: [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

### Claude Code Sandbox

OS-level isolation for safer autonomous execution.

**Why:** Reduces approval fatigue and enables autonomy. Instead of approving every bash command, sandboxing creates defined boundaries where Claude can work freely.

**How:** Uses OS primitives (bubblewrap on Linux/WSL2, Seatbelt on macOS) for:

- **Filesystem isolation** - Write access limited to working directory; system files protected
- **Network isolation** - Only approved domains accessible; blocks data exfiltration

**What it protects against:**

- Prompt injection attacks
- Malicious dependencies (npm packages with harmful code)
- Compromised build scripts
- Unauthorized API calls or data exfiltration

```bash
make setup_sandbox  # Install bubblewrap + socat (Linux/WSL2)
```

Enable via `/sandbox` command in Claude Code. Configure in `settings.json`.

Source: [Claude Code Sandboxing](https://code.claude.com/docs/en/sandboxing)

### Skills and Rules

- `.claude/skills/` - Agent capabilities (generating-prd, researching-codebase)
- `.claude/rules/` - Behavioral guidelines (core-principles, context-management)

**Skills vs Commands:** Custom slash commands have been merged into skills. A file at `.claude/commands/review.md` and a skill at `.claude/skills/review/SKILL.md` both create `/review` and work the same way. Existing `.claude/commands/` files keep working. Skills add optional features:

- Directory for supporting files (templates, examples, scripts)
- Frontmatter to control invocation (`disable-model-invocation`, `user-invocable`)
- Ability for Claude to auto-load when relevant
- `context: fork` for subagent execution

### Advanced Skill Patterns

Skills support dynamic context injection via shell command preprocessing:

```yaml
---
name: pr-summary
context: fork
agent: Explore
---
## Context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`

Summarize this pull request...
```

**Dynamic content:** The `!`command`` syntax executes before Claude receives the prompt, replacing placeholders with live output. Useful for injecting git status, test results, or API responses.

**Subagent execution:** Use `context: fork` to run skills in isolated subagent context. Available built-in agents:

| Agent | Model | Tools | Use Case |
| ------- | ------- | ------- | ---------- |
| `Explore` | Haiku (fast) | Read-only | Codebase search, file discovery |
| `Plan` | Inherited | Read-only | Research for planning |
| `general-purpose` | Inherited | All | Complex multi-step tasks |

Source: [Claude Code Skills](https://code.claude.com/docs/en/skills#advanced-patterns), [Subagents](https://code.claude.com/docs/en/sub-agents#built-in-subagents)

---

## Quick Start

See [TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md) for setup and commands reference.

## Security

**Ralph runs with `--dangerously-skip-permissions`** - all operations execute without approval.

**Only use in:** Isolated environments (DevContainers, VMs).

### Devcontainer Firewall (Optional)

For enhanced network security, adopt Claude Code's [reference devcontainer](https://github.com/anthropics/claude-code/tree/main/.devcontainer) which includes an iptables firewall with default-deny policy. Requires custom Dockerfile with `NET_ADMIN`/`NET_RAW` capabilities. See [devcontainer docs](https://code.claude.com/docs/en/devcontainer).

## Workflow

```text
PRD.md → prd.json → Ralph Loop → src/ + tests/ → progress.txt
```

### Phase-Specific PRD Management

**Project uses phase-specific PRDs:**

- `docs/GreenAgent-PRD.md` - Phase 1 (Green Agent benchmark)
- `docs/PurpleAgent-PRD.md` - Phase 2 (Purple Agent competition)

**Ralph tooling expects `docs/PRD.md`:**

- `docs/PRD.md` is a **symlink** to the currently active phase PRD
- `generate_prd_json.py` parses only `PRD.md` (no changes needed)

**Switching phases:**

```bash
# Switch to Phase 1 (Green Agent)
cd docs && ln -sf GreenAgent-PRD.md PRD.md

# Switch to Phase 2 (Purple Agent)
cd docs && ln -sf PurpleAgent-PRD.md PRD.md
```

**Current:** `PRD.md` → `GreenAgent-PRD.md` (Phase 1 active)

## Structure

```text
ralph/
├── CHANGELOG.md            # Ralph Loop version history
├── README.md               # Methodology (this file)
├── docs/
│   ├── LEARNINGS.md        # Patterns and lessons learned
│   ├── prd.json            # Story tracking (gitignored)
│   ├── progress.txt        # Execution log (gitignored)
│   ├── TEMPLATE_USAGE.md       # Setup and usage guide
│   └── templates/          # Project templates
│       ├── prd.json.template
│       ├── prd.md.template
│       ├── progress.txt.template
│       ├── prompt.md
│       └── userstory.md.template
└── scripts/
    ├── ralph.sh            # Main orchestration script
    ├── generate_prd_json.py # PRD.md → prd.json parser
    ├── init.sh             # Environment validation
    ├── reorganize_prd.sh   # Archive and iterate
    ├── setup_project.sh    # Interactive project setup
    └── lib/
        └── common.sh       # Shared utilities
```

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for Ralph Loop version history and changes.
