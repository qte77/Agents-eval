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
  1. Read prd.json, pick next story (status: "pending"/"failed")
  2. Mark story "in_progress", implement (TDD: red → green → refactor)
  3. Run typecheck + tests
  4. If passing: mark "passed", commit, log learnings
  5. On max retries: mark "failed"
  6. In teams mode: verify teammate stories in same wave
  7. Repeat until all pass (or context limit)
```

**Memory persists only through:**

- `prd.json` - Task status and acceptance criteria
- `progress.txt` - Learnings and patterns
- Git commits - Code changes

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

Each sprint gets its own PRD file. Ralph reads only `prd.json` —
the PRD markdown is human-facing input to `generate_prd_json.py`.

```
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

**Conflict resolution**: Especially relevant for worktree branches that diverge from the source branch during long-running Ralph sessions. `-X ours`/`-X theirs` is relative to the checked-out branch (`ours` = branch you're on, `theirs` = branch being merged in):

- On main, merging Ralph in: `-X theirs` keeps Ralph's version
- On feat branch, merging main in: `-X ours` keeps feat's version

**Protected main with conflicting PR** (only valid when feat branch is the single source of truth and main's conflicting changes are already incorporated or superseded):

```bash
# Merge main into feat, resolve conflicts keeping ours
git fetch origin
git checkout <branch>
git merge -X ours origin/main
git push origin <branch>
gh pr merge <pr-number> --squash
```

If the feat branch itself is blocked, create a new one as fallback:

```bash
git checkout -b <branch>-v2 origin/<branch>
git merge -X ours origin/main
git push -u origin <branch>-v2
gh pr close <old-number> -c "Superseded by new PR"
gh pr create --title "feat: ..." --body "Supersedes #<old>."
gh pr merge --squash
```

**`modify/delete` conflicts**: `-X ours` won't auto-resolve when ours deleted a file that theirs modified. Fix with `git rm <files>` then commit — ours (delete) wins. Untracked files blocking merge need `rm -rf` before `git merge`.

**`-X ours` does NOT delete files added by theirs**: Files that exist only on the branch being merged in (e.g., `main` added files that `feat` never had) are not conflicts — git auto-merges them as additions. After `git merge -X ours origin/main`, diff against the pre-merge feat branch and `git rm` any files that shouldn't be there:

```bash
# After merge, find files main added that feat didn't have
git diff HEAD <feat-branch-pre-merge-sha> --name-only --diff-filter=A
# Delete them
git diff HEAD <feat-branch-pre-merge-sha> --name-only --diff-filter=A | xargs git rm
git commit --amend --no-edit
```

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
    ├── ralph-in-worktree.sh   # Git worktree launcher
    ├── generate_prd_json.py   # PRD.md → prd.json parser
    ├── init.sh                # Environment validation
    ├── setup_project.sh       # Interactive setup
    └── lib/
        ├── common.sh              # Shared utilities
        ├── baseline.sh            # Baseline-aware test validation
        └── stop_ralph_processes.sh # Process cleanup
```

## Known Failure Modes (Sprint 7 Research)

Root cause analysis from Sprint 7 log forensics (`logs/ralph/2026-02-17_19:32:09.log`,
`logs/ralph/2026-02-18_00:00:14.log`). STORY-009/010/011 implemented correctly but
Ralph rejected them repeatedly.

### 1. TDD commit counter doesn't survive reset (Sisyphean loop)

RED+GREEN commits made in iteration N pass TDD but fail complexity. Ralph runs
`git reset --hard HEAD~N`, erasing them. In iteration N+1 the agent sees work already
exists in reflog/history, makes only a REFACTOR commit. `check_tdd_commits` (line 404)
searches `git log --grep="[RED]" --grep="STORY-ID" --all-match` but reset commits are
gone from the log. Ralph rejects for missing RED+GREEN. Repeats until max retries.

**Root cause in code**: `ralph.sh:571-577` resets commits on TDD failure, and
`ralph.sh:553` resets on quality failure. Neither persists which TDD phases passed.
The `RETRY_CONTEXT_FILE` (line 567-570) only works for quality retries after TDD
already passed — not for TDD failures that require re-verification.

**Solutions (pick one):**

- **A. Persist verified phases to state file** (recommended): After `check_tdd_commits`
  passes but quality fails, write `RED=<hash> GREEN=<hash>` to
  `/tmp/claude/ralph_tdd_verified_{story_id}`. On retry, `check_tdd_commits` reads this
  file and skips phase requirements already satisfied. Clear file on story completion.

  ```bash
  # In quality-failure handler (after line 553):
  echo "RED=$red_commit GREEN=$green_commit" > "/tmp/claude/ralph_tdd_verified_${story_id}"

  # In check_tdd_commits (before line 418):
  local verified_file="/tmp/claude/ralph_tdd_verified_${story_id}"
  if [ -f "$verified_file" ]; then
      log_info "Prior TDD phases verified — accepting REFACTOR-only"
      return 0
  fi
  ```

- **B. Don't reset on quality failure** (simpler, less clean): Keep the commits when
  only complexity/tests fail. Append retry context. Agent adds a REFACTOR commit on top.
  Quality re-runs on the full stack. Avoids the reset-then-redo cycle entirely.

- **C. Cherry-pick surviving commits**: After reset, if prior RED+GREEN are in reflog,
  `git cherry-pick` them back before re-running quality. More fragile (merge conflicts).

### 2. Teams mode cross-contamination

When Ralph delegates multiple stories in one batch, the agent combines work across
stories. `check_tdd_commits` (line 378-386) filters by `grep "$story_id"` but if the
agent makes a single commit covering multiple stories, or uses a different story ID in
the message, the filter finds nothing.

**Root cause in code**: `ralph.sh:379` uses simple grep on commit messages. A commit
message like `feat(STORY-009,STORY-010): implement features [GREEN]` matches both
stories, while `feat: implement paper selection and settings [GREEN]` matches neither.

**Solutions (pick one):**

- **A. File-scoped commit attribution** (recommended): Instead of matching story ID in
  commit messages, check which files each commit touches against the story's `files`
  array from prd.json. A commit that modifies `src/gui/pages/settings.py` belongs to
  STORY-010 regardless of its message.

  ```bash
  # Replace grep-based filtering (line 379-381):
  story_files=$(jq -r ".stories[] | select(.id==\"$story_id\") | .files[]" "$PRD_FILE")
  story_commits=""
  for commit in $(git log --format="%h" -n $new_commits); do
      changed=$(git diff-tree --no-commit-id --name-only -r "$commit")
      if echo "$changed" | grep -qFf <(echo "$story_files"); then
          story_commits="$story_commits $commit"
      fi
  done
  ```

- **B. Sequential execution with shared baseline**: Don't batch stories. Execute one at
  a time. Slower but eliminates cross-contamination entirely. Use `TEAMS=false`.

- **C. Require story-scoped commits in prompt**: Add to the agent prompt:
  "Each commit must reference exactly one story ID. Never combine stories in one commit."
  Fragile (depends on agent compliance) but zero harness changes.

### 3. Complexity gate catches cross-story changes

STORY-013's `--engine` flag raised `parse_args` complexity from 10 to 11, which failed
STORY-009's quality gate. `run_quality_checks` (line 338) runs `make complexity` against
the entire `src/` tree, not just story-scoped files.

**Root cause in code**: `baseline.sh` compares test results before/after but the
complexity check has no baseline — it's a global pass/fail on the whole codebase.

**Solutions (pick one):**

- **A. Complexity baseline with delta scoping** (recommended): Before story execution,
  snapshot complexity results per function. After execution, only fail if functions in
  the story's `files` list have increased complexity. Cross-story increases are
  permitted (they'll be caught when that story is verified).

  ```bash
  # Capture complexity baseline:
  make complexity 2>&1 | grep "FAILED" > "/tmp/claude/ralph_complexity_baseline_${story_id}"

  # After execution, diff:
  make complexity 2>&1 | grep "FAILED" > "/tmp/claude/ralph_complexity_after"
  new_failures=$(comm -13 "$baseline" "$after" | grep -F "$story_files")
  ```

- **B. Per-file complexity check**: Run complexipy only on files changed by the current
  story's commits: `complexipy $(git diff --name-only HEAD~N) --max-complexity 10`.
  Requires complexipy to accept file arguments (it does via positional args).

- **C. Complexity allowlist in prd.json**: Add an optional `complexity_exceptions` field
  per story for known cross-story impacts. Heavy-handed but explicit.

### 4. Stale snapshot tests from other stories

STORY-010/013 changes created new test regressions (snapshot counts, new default args).
`baseline.sh` captures failing tests BEFORE the batch, so new failures from other
stories in the same batch appear as regressions introduced by the current story.

**Root cause in code**: `capture_test_baseline` (baseline.sh) runs once per story
start, but in teams mode all stories share the same codebase state. Story A's baseline
doesn't account for story B's changes that were applied in the same batch.

**Solutions (pick one):**

- **A. Rolling baseline per story** (recommended): After each story's commits are
  verified and kept, re-capture the baseline before verifying the next story. This way
  story B's baseline includes story A's changes.

  ```bash
  # After successful story completion (after line 546 or 620):
  capture_test_baseline "$BASELINE_FILE" "post-${story_id}"
  ```

- **B. Test-to-source mapping**: Map each failing test to the source files it imports.
  Only flag a failure as a regression if it imports a file from the current story's
  `files` list. Requires parsing Python imports (brittle) or using a naming convention
  (`tests/gui/` ↔ `src/gui/`).

- **C. Accept known cross-story failures**: In teams mode, after detecting new failures,
  check if those failures exist in ANY story's test file list from the batch. If yes,
  log a warning but don't block. Only block on truly orphaned regressions.

### 5. File-conflict dependencies not tracked

Ralph's `depends_on` tracks logical dependencies (STORY-006 needs STORY-005's
`cc_engine.py` to exist) but not file-overlap conflicts. In sequential mode this is
harmless — stories never run simultaneously. In teams mode, two unrelated stories editing
the same file (e.g., STORY-006 and STORY-009 both editing `run_cli.py`) produce merge
conflicts or silently overwrite each other's changes.

**Root cause in code**: `get_unblocked_stories` (line 121) checks only `depends_on` — it
has no file-overlap awareness. Two stories with `depends_on: []` and overlapping `files`
arrays both appear unblocked and get delegated to different teammates.

**Solutions (pick one):**

- **A. File-conflict deps in prd.json** (recommended): Add file-overlap dependencies
  during PRD generation or in the Story Breakdown. The `generate_prd_json.py` parser can
  detect overlapping `files` arrays and auto-inject `depends_on` edges. These deps are
  only needed for teams mode — sequential mode ignores them harmlessly.

  Sprint 8 PRD demonstrates this pattern with `[file: run_cli.py]` annotations:
  `STORY-009 (depends: STORY-008, STORY-006 [file: run_cli.py])`.

- **B. Runtime file-lock check**: Before delegating a story, check if any in-progress
  story shares files. Skip overlapping stories until the conflicting story completes.
  Requires tracking which stories are currently being executed (new state in ralph.sh).

### 6. Incomplete PRD file lists (Sprint 8 post-mortem)

Three stories passed quality checks but left stale tests because the PRD `files`
arrays missed secondary consumers of renamed interfaces. All three failures were
from tests *outside* the story's scope.

**Mitigations implemented:**

- Impact scan prompt instruction: agent greps test tree for old symbol names before implementation
- Wave checkpoint: full `make validate` runs at wave boundaries to catch cross-story breakage
- Killed-process detection: exit 137/143 is a hard failure, not a silent pass
- Scoped ruff/tests: teams mode only checks story files, preventing cross-story false positives
- Pycache cleanup: removes stale `.pyc` files before test runs

### Key Structural Issue

The fundamental problem is **cross-story interference in teams mode**: quality gates for
story X catch regressions introduced by stories Y and Z. The validation checks the
entire test suite against a baseline that predates all stories in the batch.

**Recommended combined approach**: Implement solutions 1A + 2A + 3B + 4A + 5A. This gives:

- Phase persistence across resets (1A) — eliminates Sisyphean loops
- File-scoped commit attribution (2A) — correct story ownership
- Per-file complexity (3B) — scoped complexity checks
- Rolling baseline (4A) — simplest baseline fix
- File-conflict deps in prd.json (5A) — prevents parallel edits to same file

All five are backward-compatible with single-story mode (`TEAMS=false`).

## TODO / Future Work

- [ ] **Agent Teams for parallel story execution**: Enable with `make ralph_run TEAMS=true` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Lead agent orchestrates teammates with skill-specific delegation. See [CC Agent Teams Orchestration](../docs/analysis/CC-agent-teams-orchestration.md) for architecture and tracing. **Terminology**: a **wave** is the set of currently unblocked stories (all `depends_on` satisfied) — i.e., the frontier of the dependency graph. Stories within a wave run in parallel (one teammate each); the next wave starts after the current one completes.
  - [ ] **CC Agent Teams as alternative orchestrator**: Instead of Ralph's bash loop driving `claude -p` with bolted-on teams support, the CC main orchestrator agent directly spawns a team via `TeamCreate` + `Task` tool. Each story becomes a `TaskCreate` entry with `blockedBy` dependencies (both logical and file-conflict). Addresses Ralph failure modes structurally: isolated teammate contexts prevent cross-contamination (#2), `blockedBy` prevents stale snapshots (#4), no external reset eliminates Sisyphean loops (#1), lead-scoped validation prevents cross-story complexity failures (#3), and file-conflict deps in `blockedBy` prevent parallel edits to the same file (#5). Requires self-contained story descriptions in the PRD Story Breakdown (usable as `TaskCreate(description=...)`). See Sprint 8 PRD "Notes for CC Agent Teams" section for orchestration waves, file-conflict dependency table, and teammate prompt template.

- [ ] **Consolidate split test directories**: `tests/gui/` vs `tests/test_gui/` directly caused 2 of 3 Sprint 8 failures. Story authors found and updated tests in one directory but missed the other. Merging into a single `tests/gui/` eliminates the ambiguity. Independent of ralph — codebase hygiene.

- [ ] **Ad-hoc steering instructions**: Accept a free-text `INSTRUCTION` parameter via CLI/Make to inject user guidance into the prompt without editing PRD or progress files. Usage: `make ralph_run INSTRUCTION="focus on error handling"`. The instruction would be appended to the story prompt so the agent factors it in during implementation. Useful for nudging behavior (e.g., "prefer small commits", "skip Tier 2 tests") without modifying tracked files.

- [ ] **Rewrite Ralph engine in Rust or similar**: The bash script engine (`ralph.sh` + `baseline.sh` + `common.sh`) is brittle, hard to test, and growing in complexity. Rewrite the orchestration core in Rust (or another low-weight, testable language) to get proper unit tests, type safety, and maintainable control flow. Keep the Claude Code invocation via subprocess. Shell scripts become a thin CLI wrapper.

- [ ] **Multi-instance worktree orchestration**: Run up to N independent Ralph instances (solo or teams) in separate git worktrees simultaneously. Each worktree gets its own branch, prd.json, and progress.txt. Merge results back at completion. See [ralph-loop-cc-tdd-wt-vibe-kanban-template](https://github.com/qte77/ralph-loop-cc-tdd-wt-vibe-kanban-template) for reference implementation. Supersedes the single-worktree "Git worktrees for teams isolation" TODO above.

- [ ] **Merge with ralph-loop template**: Evaluate and port features from [ralph-loop-cc-tdd-wt-vibe-kanban-template](https://github.com/qte77/ralph-loop-cc-tdd-wt-vibe-kanban-template) into this project, or merge both projects altogether. The template repo has diverged with its own worktree management, kanban tracking, and vibe coding workflow. Consolidate to avoid maintaining two separate Ralph implementations.

### Deferred

- [ ] **Intra-story teams**: Multiple agents on one story (e.g., test writer + implementer). Requires shared-file coordination, merge conflict handling, and split TDD ownership. Deferred until inter-story mode is validated.

- [ ] **Git worktrees for teams isolation**: True filesystem isolation eliminates all cross-contamination (`__pycache__`, ruff/test cross-pollution). Each story in a wave gets its own `git worktree`. Merge at wave boundaries via `git merge --squash`. Deferred until scoped checks + wave checkpoints are validated.

- [ ] **Automated impact-scope analysis**: Post-story function that diffs removed identifiers in `src/`, filters to renamed-only (removed but not re-added), and greps `tests/` for out-of-scope consumers. Currently handled by the agent via prompt instruction. Automate if a second incident occurs where the prompt instruction is insufficient.

- [ ] **Inline snapshot drift detection**: Run `uv run pytest --inline-snapshot=review` after clean test passes to surface stale snapshots. Deferred until `--inline-snapshot=review` output format is confirmed stable for non-interactive use. Snapshot mismatches already show up as normal test failures.

- [ ] **Cross-directory test warning**: Flag when a source module has tests in multiple directories (e.g., `tests/gui/` and `tests/test_gui/`). Symptom of poor test directory hygiene — consolidating test dirs (above) is the structural fix. Deferred as YAGNI.

### Done

- [x] **Intermediate progress visibility** — Monitor now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors, alongside existing phase detection from git log.
  - [x] **CC monitor log nesting** — `monitor_story_progress` now tracks byte offset (`wc -c`) between 30s cycles and reads only new log content via `tail -c +$offset`, preventing `[CC] [INFO] [CC] [INFO] ...` nesting chains.
- [x] **Agent Teams inter-story** — `ralph.sh` appends unblocked independent stories to the prompt; `check_tdd_commits` filters by story ID in teams mode to prevent cross-story marker false positives. Completed stories caught by existing `detect_already_complete` path.
- [x] **Scoped reset on red-green validation failure** — Untracked files are snapshot before story execution; on TDD failure, only story-created files are removed. Additionally, quality-failure retries skip TDD verification entirely (prior RED+GREEN already verified), and `check_tdd_commits` has a fallback that detects `refactor(` prefix when `[REFACTOR]` bracket marker is missing.
- [x] **Deduplicate log level in CC monitor output** — `monitor_story_progress` strips leading `[INFO]`/`[WARN]`/`[ERROR]` prefix from CC agent output before wrapping with `log_cc*`, preventing `[INFO] ... [CC] [INFO]` duplication.

## Sources

- [Ralph Wiggum technique](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)
- [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

---

See [CHANGELOG.md](CHANGELOG.md) for version history.
