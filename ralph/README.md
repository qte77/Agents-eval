# Ralph Loop - Autonomous TDD Development with Claude Code

> "Ralph makes the agent earn every commit — red, green, refactor, verify, repeat."

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
  1. Read prd.json, pick next story (status: "pending"/"failed")
  1b. Generate story context snapshot (AC, files, tests)
  2. Mark story "in_progress", implement (TDD: red → green → refactor)
  3. Run typecheck + tests
  4. If passing: mark "passed", commit, log learnings
  5. On max retries: mark "failed"
  6. In teams mode: verify teammate stories in same wave
  7. Repeat until all pass (or context limit)
```

**Memory persists only through:**

- `prd.json` - Task status and acceptance criteria
- `progress.txt` - Learnings, patterns, and failure mode tables
- Git commits - Code changes
- `codebase-map.md` - Source tree + function signatures (refreshed per wave)

**Usage:**

```bash
make ralph_run MAX_ITERATIONS=25              # Run autonomous development
make ralph_run MAX_ITERATIONS=25 TEAMS=true   # EXPERIMENTAL: parallel story delegation
make ralph_worktree BRANCH=ralph/sprintN      # Run in isolated git worktree
make ralph_status                             # Check progress
```

**Configuration** (environment variables):

- `RALPH_MODEL` - Model selection: sonnet (default), opus, haiku
- `MAX_ITERATIONS` - Loop limit (default: 25)
- `REQUIRE_REFACTOR` - Enforce REFACTOR phase (default: false)
- `TEAMS` - EXPERIMENTAL: Enable parallel story delegation via agent teams (default: false). Known failure modes documented below — cross-story interference causes false rejections.
- `SNAPSHOT_SIG_LIMIT` - Max signature lines per file in codebase map (default: 100)
- `DOMAIN_RETRY_THRESHOLD` - Failures before suggesting skill creation (default: 3)

**Monitoring** (interactive sessions):

```bash
claude remote-control --name "Ralph"
```

Run before an interactive session to monitor and steer Ralph from another device.

## Design Principles

- **TDD Enforcement** — Red (`[RED]`) → Green (`[GREEN]`) → Refactor (`[REFACTOR]`) commit markers
- **[Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** — Incremental boundaries, state management, checkpointing, error recovery, human-in-the-loop
- **[Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)** — Plan → Work → Assess → Compound
- **[Context Engineering (ACE-FCA)](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)** — Context window management (see `.claude/rules/context-management.md`)

## Workflow

```text
PRD.md → prd.json → Ralph Loop → src/ + tests/ → progress.txt
```

### Sprint-Specific PRD Management

Each sprint gets its own PRD file. Ralph reads only `prd.json` —
the PRD markdown is human-facing input to `generate_prd_json.py`.

```text
docs/PRD.md                    # Parser input (or symlink to active sprint)
ralph/docs/prd.json            # Ralph reads this
```

Optionally, symlink `docs/PRD.md` to the active sprint file so the
parser always reads the right one without arguments:

```bash
cd docs && ln -sf sprints/PRD-SprintN.md PRD.md
```

**Switching sprints:**

```bash
# Archive current sprint
git tag sprint-N-complete -a -m "Sprint N complete"
mkdir -p ralph/archive/sprintN/
cp ralph/docs/{prd.json,progress.txt} ralph/archive/sprintN/

# Point parser at next sprint and regenerate
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

### Git Worktree Workflow

Run Ralph in an isolated worktree to keep the source branch clean.

**Setup and run:**

```bash
make ralph_worktree BRANCH=ralph/<branch-name>
```

This creates a sibling worktree at `../<branch-basename>`, symlinks
`.venv` from the source repo, and starts Ralph. Reuses an existing
branch and worktree if one exists.

**Directory layout** (sibling pattern):

```text
parent-dir/
├── your-project/                   # Source repo (working branch)
│   ├── .venv/                      # Shared virtual environment
│   └── ralph/docs/prd.json
└── <branch-basename>/              # Worktree (ralph branch)
    ├── .venv → ../your-project/.venv   # Symlinked, not copied
    └── ralph/docs/prd.json
```

**Key practices:**

- **One worktree per sprint branch** — keeps TDD noise off the source branch
- **`.venv` is symlinked**, not duplicated — never run `uv sync` in the worktree
- **Don't edit overlapping files** in the source repo while Ralph runs —
  files listed in `prd.json` `files` arrays belong to the worktree
- **Clean up when done** — use `git worktree remove`, not `rm -rf`

**Configuration** (same env vars as `ralph_run`):

```bash
make ralph_worktree BRANCH=ralph/<name> TEAMS=true MAX_ITERATIONS=50 MODEL=opus
```

**Sandbox note:** If your environment restricts writes outside the repo
directory (e.g., DevContainers), add the parent directory to the sandbox
write allowlist so worktrees can be created as siblings.

### Merging Back

Squash merge from source repo (not worktree). TDD commits are implementation noise — final state is what matters.

```bash
git merge --squash ralph/<branch>
git commit -m "feat(sprintN): implement stories via Ralph"
git worktree remove ../<worktree-dir>
git branch -d ralph/<branch>
```

**Conflict prevention**: Don't edit files in `prd.json` `files` arrays on the source branch while Ralph runs.

For conflict resolution, `-X ours`/`-X theirs` strategies, GPG re-signing, and edge cases, see [LEARNINGS.md](docs/LEARNINGS.md) section 4.

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
│   ├── FAILURE_MODES.md       # Teams mode failure analysis
│   ├── LEARNINGS.md           # Patterns and lessons
│   ├── prd.json               # Story tracking (committed)
│   ├── codebase-map.md        # Source tree + signatures (AST-based)
│   ├── .codebase-map.sha      # Content hash (gitignored)
│   ├── story-context.md       # Per-story context (gitignored)
│   ├── progress.txt           # Execution log (committed)
│   ├── TEMPLATE_USAGE.md      # Setup guide
│   └── templates/             # Project templates
│       ├── prd.json.template
│       ├── prd.md.template
│       ├── progress.txt.template
│       ├── prompt.md
│       └── userstory.md.template
└── scripts/
    ├── ralph.sh               # Main orchestration
    ├── ralph-in-worktree.sh   # Git worktree launcher
    ├── generate_prd_json.py   # PRD.md → prd.json parser
    ├── init.sh                # Environment validation
    ├── setup_project.sh       # Interactive setup
    └── lib/
        ├── common.sh              # Shared utilities
        ├── snapshot.sh            # Codebase snapshot generation
        ├── baseline.sh            # Baseline-aware test validation
        ├── extract_signatures.py  # AST-based Python signature extraction
        └── stop_ralph_processes.sh # Process cleanup
```

## Known Failure Modes

See [FAILURE_MODES.md](docs/FAILURE_MODES.md) for Sprint 7 root cause analysis of teams mode cross-story interference (6 failure modes with recommended solutions).

## TODO / Future Work

See [TODO.md](TODO.md) for the consolidated backlog (bugs, enhancements, deferred items, and done).

## Sources

- [Ralph Wiggum technique](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)
- [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

---

See [CHANGELOG.md](CHANGELOG.md) for version history.
