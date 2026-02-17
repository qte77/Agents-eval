# Ralph Loop - Autonomous TDD Development with Claude Code

Autonomous AI development loop that iteratively implements stories
until all acceptance criteria pass.

## What is Ralph?

Named after Ralph Wiggum from The Simpsons, this technique by
Geoffrey Huntley implements self-referential AI development loops.
The agent sees its own previous work in files and git history,
iteratively improving until completion.

**Core Loop:**

```text
while stories remain:
  1. Read prd.json, pick next story (passes: false)
  2. Implement story (TDD: red → green → refactor)
  3. Run typecheck + tests
  4. If passing: commit, mark done, log learnings
  5. Repeat until all pass (or context limit)
```

**Memory persists only through:**

- `prd.json` - Task status and acceptance criteria
- `progress.txt` - Learnings and patterns
- Git commits - Code changes

**Usage:**

```bash
make ralph_run MAX_ITERATIONS=25              # Run autonomous development
make ralph_run MAX_ITERATIONS=25 TEAMS=true   # Run with parallel story delegation
make ralph_status                             # Check progress
```

**Configuration** (environment variables):

- `RALPH_MODEL` - Model selection: sonnet (default), opus, haiku
- `MAX_ITERATIONS` - Loop limit (default: 25)
- `REQUIRE_REFACTOR` - Enforce REFACTOR phase (default: false)
- `TEAMS` - Enable parallel story delegation via agent teams (default: false)

## Design Principles

### TDD Enforcement (Red-Green-Refactor)

1. **Red** - Write failing test (commit with `[RED]` marker)
2. **Green** - Implement until tests pass (commit with `[GREEN]` marker)
3. **Refactor** - Clean up (optional, commit with `[REFACTOR]` marker)

### Effective Agent Harnesses

Follows [Anthropic's production harness patterns](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):

1. **Incremental Boundaries** - Story-by-story execution; one feature per
   session, commit before moving on
2. **State Management** - prd.json (task status) + progress.txt (learnings) +
   git history (code); each session reads prior context before acting
3. **Checkpointing** - Git commits per story enable resumption from
   known-good states
4. **Error Recovery** - `git reset --hard` recovers failed stories without
   manual intervention
5. **Human-in-the-Loop** - Structured prompts: read progress → select story →
   implement → test → commit

### Compound Engineering

Learnings compound over time: **Plan** → **Work** → **Assess** → **Compound**

Source: [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)

### Context Engineering (ACE-FCA)

Context window management for quality output.
See `.claude/rules/context-management.md`.

Source: [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

## Workflow

```text
PRD.md → prd.json → Ralph Loop → src/ + tests/ → progress.txt
```

### Sprint-Specific PRD Management

Each sprint gets its own PRD file. Ralph reads `docs/PRD.md`, which
symlinks to the active sprint:

```
docs/
├── PRD.md → PRD-Sprint2.md   # Symlink (active)
├── PRD-Sprint1.md             # Completed
├── PRD-Sprint2.md             # Active
└── PRD-Sprint3.md             # Planned
```

**Switching sprints:**

```bash
# Archive current sprint
git tag sprint-2-complete -a -m "Sprint 2 complete"
mkdir -p docs/archive/sprint2/
cp ralph/docs/{prd.json,progress.txt} ralph/archive/sprint2/

# Activate next sprint
cd docs && ln -sf PRD-Sprint3.md PRD.md
make ralph_prd_json
make ralph_run MAX_ITERATIONS=25
```

**Why separate files?**

- Single PRD with 50+ stories across sprints overwhelms Ralph's context
- Completed sprint details pollute active sprint focus
- Each sprint PRD stays at 10-20 stories (manageable scope)
- Historical PRDs preserved as immutable records

**Story IDs**: Sequential across sprints (STORY-001... STORY-011 in Sprint 2,
STORY-012... in Sprint 3). Unique IDs across project lifetime.

**prd.json**: Fresh start per sprint. Archive before transition.

## Security

**Ralph runs with `--dangerously-skip-permissions`** - all operations
execute without approval.

**Only use in:** Isolated environments (DevContainers, VMs).

For network isolation, see Claude Code's
[reference devcontainer](https://github.com/anthropics/claude-code/tree/main/.devcontainer)
with iptables firewall.

## Quick Start

See [TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md) for setup and commands.

## Structure

```text
ralph/
├── CHANGELOG.md               # Version history
├── README.md                  # This file
├── docs/
│   ├── LEARNINGS.md           # Patterns and lessons
│   ├── prd.json               # Story tracking (gitignored)
│   ├── progress.txt           # Execution log (gitignored)
│   ├── TEMPLATE_USAGE.md      # Setup guide
│   └── templates/             # Project templates
│       ├── prd.json.template
│       ├── prd.md.template
│       ├── progress.txt.template
│       ├── prompt.md
│       └── userstory.md.template
└── scripts/
    ├── ralph.sh               # Main orchestration
    ├── generate_prd_json.py   # PRD.md → prd.json parser
    ├── init.sh                # Environment validation
    ├── setup_project.sh       # Interactive setup
    └── lib/
        ├── common.sh              # Shared utilities
        ├── baseline.sh            # Baseline-aware test validation
        └── stop_ralph_processes.sh # Process cleanup
```

## TODO / Future Work

- ~~**Intermediate progress visibility**~~: **DONE** — Monitor now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors, alongside existing phase detection from git log.

- **Agent Teams for parallel story execution**: Enable with `make ralph_run TEAMS=true` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Lead agent orchestrates teammates with skill-specific delegation. See [CC Agent Teams Orchestration](../docs/analysis/CC-agent-teams-orchestration.md) for architecture and tracing.
  - ~~**Inter-story**~~: **DONE** — `ralph.sh` appends unblocked independent stories to the prompt; `check_tdd_commits` filters by story ID in teams mode to prevent cross-story marker false positives. Completed stories caught by existing `detect_already_complete` path.
  - **Intra-story** (**TODO**): Multiple agents on one story (e.g., test writer + implementer). Requires shared-file coordination, merge conflict handling, and split TDD ownership. Deferred until inter-story mode is validated.

- ~~**Scoped reset on red-green validation failure**~~: **DONE** — Untracked files are snapshot before story execution; on TDD failure, only story-created files are removed. Additionally, quality-failure retries skip TDD verification entirely (prior RED+GREEN already verified), and `check_tdd_commits` has a fallback that detects `refactor(` prefix when `[REFACTOR]` bracket marker is missing.

## Sources

- [Ralph Wiggum technique](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)
- [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

---

See [CHANGELOG.md](CHANGELOG.md) for version history.
