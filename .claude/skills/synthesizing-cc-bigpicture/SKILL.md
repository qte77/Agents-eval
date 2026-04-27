---
name: synthesizing-cc-bigpicture
description: Synthesizes a living big-picture meta-plan from Claude Code sessions, plans, tasks, and team communications. Use when orienting across projects, assessing reasoning modes, or creating a plan-to-plan overview.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob
  argument-hint: [project-name] [time-range] [output-path]
  context: fork
---

# Big-Picture Synthesis

**Target**: $ARGUMENTS

Synthesizes a **plan to plan** — an overarching view across all Claude Code
artifacts. A reasoning tool that connects sessions, plans, tasks, and memories
into a coherent narrative of what you're working on, why, and where you're headed.

## Arguments

| Position | Name | Required | Default | Description |
|----------|------|----------|---------|-------------|
| 1 | `project-name` | no | all projects | Filter to a single project (substring, case-insensitive). Use `all` for all. |
| 2 | `time-range` | no | all time | E.g. `7d`, `30d`, `this-week`. |
| 3 | `output-path` | no | auto | Where to write output. |

**Default output path:**
- `project-name` set: `<decoded-project-path>/docs/bigpicture.md`
- `all` or omitted: `~/.claude/bigpicture.md`
- Explicit `output-path`: overrides both.

**Project matching**: Matched against decoded `~/.claude/projects/<encoded-path>/`
directories (`-` → `/` in encoding). Substring match on any path segment.

**Examples:**

```
/synthesizing-cc-bigpicture                          # All → ~/.claude/bigpicture.md
/synthesizing-cc-bigpicture Agents-eval              # Single → project docs/
/synthesizing-cc-bigpicture Agents-eval 7d           # Single, last 7 days
/synthesizing-cc-bigpicture all 30d ./bigpicture.md  # All, 30 days, custom path
```

## Two Reasoning Axes

Track per work stream to surface where you are and what shift is needed.

### Diverge / Converge

- **Diverge**: Expanding — brainstorming, exploring options, opening questions
- **Converge**: Narrowing — selecting approaches, committing, closing decisions
- **Signals**: Open questions in plans = diverging. Task completion clustering = converging.
- **Alert**: Diverging for N sessions without convergence → decision debt

### Strategic / Tactical

- **Strategic** (top-down, deductive): Principles → plans → tasks. PRD → architecture → implementation.
- **Tactical** (bottom-up, inductive): Observations → patterns → principles. Bugs → learnings → plan revisions.
- **Signals**: PRD→task flow = strategic. AGENT_LEARNINGS, blockers→revisions = tactical.
- **Alert**: All strategic (no implementation feedback) or all tactical (reactive without direction)

## When to Use

- Starting a work session — orient across projects
- Planning what to work on next — strategic prioritization
- Sprint/week boundary — maintain the meta-plan
- Feeling stuck — surface current reasoning mode and whether a shift is needed

## Do Not Use

- Searching a specific past conversation (use `/resume` or `/history`)
- Per-session context (session-memory does this automatically)
- Real-time usage monitoring (use `/insights`)

## CC Data Sources

```
~/.claude/
├── history.jsonl                    # Global prompt log (display, timestamp, project, sessionId)
├── stats-cache.json                 # Daily aggregates (messageCount, sessionCount, toolCallCount)
├── projects/<encoded-path>/
│   ├── memory/MEMORY.md             # Per-project persistent knowledge
│   ├── <session-uuid>.jsonl         # Full transcripts (metadata-scan only)
│   └── <session-uuid>/subagents/    # Subagent transcripts
├── plans/*.md                       # Plan mode files
├── tasks/<session-or-team-name>/    # Tasks (*.json, skip .lock/.highwatermark)
└── teams/<team-name>/               # config.json + inboxes/<member>.json
```

See `references/cc-entry-types.md` for JSONL entry type reference.

## Project Filtering

When `project-name` is set (not `all`), ALL data collection and output must
respect the filter. Apply these rules once, consistently:

1. **Session allowlist**: From `history.jsonl`, collect `sessionId` values whose
   `project` field matches (case-insensitive).
2. **Project dirs**: Filter `~/.claude/projects/*/` to matching decoded paths.
3. **Plans**: Content-based — include only plans mentioning the project name.
4. **Tasks**: Match task dir names against session allowlist (UUIDs) or filtered
   team names.
5. **Teams**: Include only teams whose `config.json` references the project name.
6. **Session .jsonl**: Only read files whose UUID is in the session allowlist.
7. **Output**: Every section scoped to filtered data only. Exception:
   "Cross-Project Connections" may reference other projects as outbound links.

## Workflow

1. **Parse arguments** — Apply defaults per Arguments table. Resolve output path.

2. **Check existing** — If bigpicture.md exists at output path, load for
   incremental update (preserve structure, refresh content).

3. **Discover & filter projects** — Glob `~/.claude/projects/*/`. Decode paths.
   Apply project filter if set. Build session allowlist from `history.jsonl`.

4. **Collect signals** (sequential, metadata-first, no subagents):
   - **Activity**: `stats-cache.json` — daily counts for trajectory
   - **Sessions**: `history.jsonl` — unique sessionIds, timestamps, topics
   - **Memory**: `projects/*/memory/MEMORY.md` — persistent knowledge
   - **Plans**: `plans/*.md` — goals, open questions, decisions
   - **Tasks**: `tasks/*/*.json` — dependency graph, status
   - **Teams**: `teams/*/config.json` + `inboxes/*.json` — structure, comms
   - **Session metadata**: First+last 5 lines of `.jsonl` — timestamps, branches
   - **Project docs**: Decoded project path → `CHANGELOG.md`, `AGENT_REQUESTS.md`

   **Critical**: Never bulk-read full `.jsonl` transcripts. Use `history.jsonl`
   for discovery and first+last lines for metadata only.

5. **Classify reasoning modes** per work stream:
   - Open questions vs. closed decisions → diverge/converge
   - Plan-driven tasks vs. learning entries → strategic/tactical
   - Flag imbalances (see alerts above)

6. **Synthesize** — Group by project → time clusters. Link plans↔sessions↔tasks.
   Surface blockers, trajectory, recurring themes, cross-project connections.

7. **Output** using format below. Write to output path.

## Output Format

```markdown
# Big Picture — <date>

## Reasoning Mode Summary
| Project | Phase | D/C | S/T | Alert |
|---------|-------|-----|-----|-------|

## Active Work Streams
### <Project>
- **Status:** active/stalled — N sessions in last 7d
- **Focus:** <from memory + latest sessions>
- **Mode:** <diverging+tactical = exploring> | <converging+strategic = building>
- **Key decisions / Open questions:** <from plans>
- **Tasks:** N open / N total — blockers: <list>
- **Trajectory:** accelerating/steady/stalled

## Cross-Project Connections
## Active Plans
## TODOs & DONEs
## Blockers & Stale Items
## Mode Transitions Needed
```

## Common Pitfalls

- **Data dump**: If output exceeds ~200 lines, raise abstraction. Interpret, don't list.
- **Reading full transcripts**: Use `history.jsonl` + first/last lines only.
- **False mode classification**: Reasoning modes are heuristic signals, not verdicts.
- **Spawning subagents**: Don't. Sequential within fork context is sufficient.

## Quality Check

- Correct > Complete > Minimal (ACE-FCA)
- ~100-200 lines output
- Every claim traces to a specific CC artifact
- Incremental update preserves structure, refreshes content

## References

See `references/cc-entry-types.md` for JSONL session entry type taxonomy.
