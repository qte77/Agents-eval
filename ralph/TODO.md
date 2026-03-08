---
title: Ralph TODO
purpose: Consolidated backlog for Ralph loop — bugs, enhancements, and deferred items from README.md and CC feature research.
created: 2026-03-07
---

## Adopt Now (zero cost)

None.

## Backlog

<!-- markdownlint-disable MD013 -->

- [ ] **AST-based signature extraction**: Replace `grep -nE '^(class |def |    def |async def )'` in `lib/snapshot.sh` with a Python `ast` helper script. AST captures return types, decorators (`@tool`), and full arg annotations that grep misses. Speed difference negligible (0.42s vs 0.36s for 103 files). Complexipy is a separate tool (quality gate, not mapping).
- [ ] **Multi-instance worktree orchestration**: Run up to N independent Ralph instances in separate git worktrees simultaneously. Each worktree gets its own branch, prd.json, and progress.txt. See [ralph-loop-cc-tdd-wt-vibe-kanban-template](https://github.com/qte77/ralph-loop-cc-tdd-wt-vibe-kanban-template) for reference.
- [ ] **Merge with ralph-loop template**: Evaluate and port features from [ralph-loop-cc-tdd-wt-vibe-kanban-template](https://github.com/qte77/ralph-loop-cc-tdd-wt-vibe-kanban-template) into this project, or merge both projects altogether.
- [ ] **Symptom-cause-fix tables in progress.txt**: Structured failure mode tables instead of free-text learnings. Agents avoid repeating known mistakes. Source: [2602.20478] §3.3
- [ ] **Context drift detector**: Session-start hook warning when src/ files changed without codebase-map.md update. Extends content-hash check. Source: [2602.20478] §5
- [ ] **Agent creation heuristic**: Track retry counts per-domain; suggest new skill when a domain repeatedly fails. Source: [2602.20478] §3.2

<!-- markdownlint-enable MD013 -->

## Future Work

<!-- markdownlint-disable MD013 -->

- [ ] **Agent Teams for parallel story execution**: Enable with `make ralph_run TEAMS=true` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Lead agent orchestrates teammates with skill-specific delegation. See [CC Agent Teams Orchestration](https://github.com/qte77/claude-code-research/blob/main/docs/agent-orchestration/CC-agent-teams-orchestration.md) for architecture and tracing. **Terminology**: a **wave** is the set of currently unblocked stories (all `depends_on` satisfied) — i.e., the frontier of the dependency graph. Stories within a wave run in parallel (one teammate each); the next wave starts after the current one completes.
  - [ ] **CC Agent Teams as alternative orchestrator**: Instead of Ralph's bash loop driving `claude -p` with bolted-on teams support, the CC main orchestrator agent directly spawns a team via `TeamCreate` + `Task` tool. Each story becomes a `TaskCreate` entry with `blockedBy` dependencies (both logical and file-conflict). Addresses Ralph failure modes structurally: isolated teammate contexts prevent cross-contamination (#2), `blockedBy` prevents stale snapshots (#4), no external reset eliminates Sisyphean loops (#1), lead-scoped validation prevents cross-story complexity failures (#3), and file-conflict deps in `blockedBy` prevent parallel edits to the same file (#5). Requires self-contained story descriptions in the PRD Story Breakdown (usable as `TaskCreate(description=...)`). See Sprint 8 PRD "Notes for CC Agent Teams" section for orchestration waves, file-conflict dependency table, and teammate prompt template.

<!-- markdownlint-enable MD013 -->

## Monitor (revisit on trigger)

<!-- markdownlint-disable MD013 -->

| Item | Current Blocker | Trigger to Revisit |
| ---- | --------------- | ------------------ |
| **Fast mode for Ralph loop** | 2x+ cost increase; autonomous execution doesn't benefit from latency reduction | Pricing drops or Ralph becomes interactive |
| **Omnara cloud sandbox failover** | Startup risk (pivoted once); no E2E encryption; CC Remote Control may be sufficient | Ralph runs regularly stall because laptop sleeps — measured, not assumed |
| **Cloud Sessions for Ralph loop** | No local MCP servers or persistent state in cloud VMs; setup script complexity | Cloud sessions support custom images or MCP forwarding |
| **BDD workflow support** | Only TDD `[RED]/[GREEN]/[REFACTOR]` accepted | A BDD project needs Ralph |
| **Cross-layer validation commands** | Single-layer Python project | Project becomes multi-layer |
| **CLI rewrite (Bun/Deno/Rust/Python)** | Bash works; jq/quoting fragility not yet a measured blocker. Bun/Deno are middle ground (scripting feel + types + native JSON). | jq quoting bugs (SC1010) or `/tmp` path collisions measurably block development |

<!-- markdownlint-enable MD013 -->

**CLI rewrite scope** (when triggered):

- **Biggest wins**: Native JSON (eliminates jq), typed story/prd interfaces, proper tmp dir management, async process spawning
- **Maps cleanly**: jq queries → JSON.parse, string parsing → typed objects, background monitor → async/await + AbortController, `claude -p` piping → Bun.spawn/Deno.Command
- **Needs investigation**: `exec > >(tee)` dual logging, signal/trap handling, `ralph-in-worktree.sh` git coupling, `watch.sh`
- **Middle ground**: Bun/Deno keep scripting feel vs full Rust rewrite

## Deferred

<!-- markdownlint-disable MD013 -->

- [ ] **Intra-story teams**: Multiple agents on one story (e.g., test writer + implementer). Requires shared-file coordination, merge conflict handling, and split TDD ownership. Deferred until inter-story mode is validated.
- [ ] **Git worktrees for teams isolation**: True filesystem isolation eliminates all cross-contamination (`__pycache__`, ruff/test cross-pollution). Each story in a wave gets its own `git worktree`. Merge at wave boundaries via `git merge --squash`. Deferred until scoped checks + wave checkpoints are validated.
- [ ] **Automated impact-scope analysis**: Post-story function that diffs removed identifiers in `src/`, filters to renamed-only (removed but not re-added), and greps `tests/` for out-of-scope consumers. Currently handled by the agent via prompt instruction. Automate if a second incident occurs.
- [ ] **Inline snapshot drift detection**: Run `uv run pytest --inline-snapshot=review` after clean test passes to surface stale snapshots. Deferred until `--inline-snapshot=review` output format is confirmed stable for non-interactive use.
- [ ] **Cross-directory test warning**: Flag when a source module has tests in multiple directories (e.g., `tests/gui/` and `tests/test_gui/`). Consolidating test dirs (above) is the structural fix. Deferred as YAGNI.

<!-- markdownlint-enable MD013 -->

## Done

<!-- markdownlint-disable MD013 -->

- [x] **Intermediate progress visibility** — Monitor now tails agent log output at 30s intervals with `[CC]` (magenta) prefix for agent activity and red for agent errors, alongside existing phase detection from git log.
  - [x] **CC monitor log nesting** — `monitor_story_progress` now tracks byte offset (`wc -c`) between 30s cycles and reads only new log content via `tail -c +$offset`, preventing `[CC] [INFO] [CC] [INFO] ...` nesting chains.
- [x] **Agent Teams inter-story** — `ralph.sh` appends unblocked independent stories to the prompt; `check_tdd_commits` filters by story ID in teams mode to prevent cross-story marker false positives. Completed stories caught by existing `detect_already_complete` path.
- [x] **Scoped reset on red-green validation failure** — Untracked files are snapshot before story execution; on TDD failure, only story-created files are removed. Additionally, quality-failure retries skip TDD verification entirely (prior RED+GREEN already verified), and `check_tdd_commits` has a fallback that detects `refactor(` prefix when `[REFACTOR]` bracket marker is missing.
- [x] **Deduplicate log level in CC monitor output** — `monitor_story_progress` strips leading `[INFO]`/`[WARN]`/`[ERROR]` prefix from CC agent output before wrapping with `log_cc*`, preventing `[INFO] ... [CC] [INFO]` duplication.
- [x] **Fix AGENTS.md Ralph path**: Update `.claude/scripts/ralph/` to `ralph/scripts/` — fixed state tracking paths too (`ralph/docs/prd.json`, `ralph/docs/progress.txt`)
- [x] **Fix `ralph_status` jq query**: Change `.passes == true` to `.status == "passed"` in Makefile
- [x] **Disable git instructions for headless mode**: Set `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` in Ralph's env
- [x] **Remote Control for Ralph monitoring**: Documented in README.md Configuration section
- [x] **Per-story `CLAUDE_CODE_EFFORT_LEVEL`**: Deferred from `settings.json` to Ralph per-story computation (Branch 1)
- [x] **Namespace `/tmp` paths by worktree**: `RALPH_TMP_DIR="/tmp/claude/ralph_${_WT_HASH}"` via `sha256sum`
- [x] **Add `--check-overlaps` to `generate_prd_json.py`**: `--check-overlaps` flag warns on file overlaps without mutual `depends_on`
- [x] **Add De-Sloppify pass**: Opt-in post-story cleanup via `RALPH_DESLOPIFY=true` (Branch 1)
- [x] **Consolidate split test directories**: `tests/test_gui/` does not exist — already resolved
- [x] **Ad-hoc steering instructions**: `INSTRUCTION` parameter via CLI/Make (Branch 1)
- [x] **Trigger table in prompt.md**: File-pattern → skill routing table in `ralph/docs/templates/prompt.md`
- [x] **Codebase snapshot system**: `lib/snapshot.sh` generates `codebase-map.md` (file tree + grep-based signatures) and `story-context.md` (AC, file contents, tests). Content-hash diffing skips regeneration when `src/` unchanged. Grep-based — AST upgrade tracked as separate backlog item.

<!-- markdownlint-enable MD013 -->

## Decisions

| Decision | Rationale | Date |
| -------- | --------- | ---- |
| Adopt CC Remote Control over Omnara/CloudCLI | Free, native, zero-setup; sufficient for monitoring. See [CC-remote-control-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/execution-infrastructure/CC-remote-control-analysis.md) | 2026-03-07 |
| Skip fast mode for autonomous runs | See Monitor table above; rationale in [CC-fast-mode-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/configuration/CC-fast-mode-analysis.md) | 2026-03-07 |
| Fix `ralph_status` + AGENTS.md path ref | See Fix Now above; gap analysis in [CC-ralph-enhancement-research.md](https://github.com/qte77/claude-code-research/blob/main/docs/agent-orchestration/CC-ralph-enhancement-research.md) | 2026-03-07 |
| AST over grep for codebase map signatures | AST captures return types, decorators, full arg annotations; grep misses them. Speed negligible (1.2x). Complexipy stays as quality gate only. | 2026-03-08 |

## Sources

<!-- markdownlint-disable MD013 -->

- [CC-ralph-enhancement-research.md](https://github.com/qte77/claude-code-research/blob/main/docs/agent-orchestration/CC-ralph-enhancement-research.md) — gaps, external patterns, tiered enhancements
- [CC-fast-mode-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/configuration/CC-fast-mode-analysis.md) — fast mode cost analysis
- [CC-remote-control-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/execution-infrastructure/CC-remote-control-analysis.md) — remote monitoring mechanics
- [CC-remote-access-landscape.md](https://github.com/qte77/claude-code-research/blob/main/docs/execution-infrastructure/CC-remote-access-landscape.md) — Omnara, CloudCLI alternatives
- [CC-cloud-sessions-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/execution-infrastructure/CC-cloud-sessions-analysis.md) — cloud VM execution
- [CC-skills-adoption-analysis.md](https://github.com/qte77/claude-code-research/blob/main/docs/agent-orchestration/CC-skills-adoption-analysis.md) — Skills adoption and format analysis (completed)
- [CC-changelog-feature-scan.md](https://github.com/qte77/claude-code-research/blob/main/docs/CC-changelog-feature-scan.md) — changelog scan (structured outputs, `/loop`, HTTP hooks, worktree isolation)
- [Codified Context Infrastructure](https://arxiv.org/abs/2602.20478) — three-tier context architecture (constitution + specialist agents + cold-memory knowledge base), 283-session empirical study, 108K LOC C# project. Validates AGENTS.md + Skills + docs/ pattern.

<!-- markdownlint-enable MD013 -->
