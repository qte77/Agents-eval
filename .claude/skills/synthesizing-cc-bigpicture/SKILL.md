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
artifacts. Not a search tool. A reasoning tool that connects sessions, plans,
tasks, and memories into a coherent narrative of what you're working on, why,
and where you're headed.

## Arguments

| Position | Name | Required | Default | Description |
|----------|------|----------|---------|-------------|
| 1 | `project-name` | no | all projects | Filter to a single project. Matched against decoded project paths (substring, case-insensitive). E.g. `Agents-eval`, `polyforge`. |
| 2 | `time-range` | no | all time | Limit to recent activity. E.g. `7d`, `30d`, `this-week`. |
| 3 | `output-path` | no | auto (see below) | Where to write the output file. |

**Default output path:**
- When `project-name` is `all` or omitted: `~/.claude/bigpicture.md` (global)
- When `project-name` is set: `<decoded-project-path>/docs/bigpicture.md` (project-local).
  The project path is decoded from `~/.claude/projects/<encoded-path>/` (e.g.
  `-workspaces-Agents-eval` → `/workspaces/Agents-eval/docs/bigpicture.md`).
- When `output-path` is explicitly provided: uses that path regardless of filter.

**Examples:**

```
/synthesizing-cc-bigpicture                          # All projects → ~/.claude/bigpicture.md
/synthesizing-cc-bigpicture Agents-eval              # Single project → /workspaces/Agents-eval/docs/bigpicture.md
/synthesizing-cc-bigpicture Agents-eval 7d           # Single project, last 7 days → project docs/
/synthesizing-cc-bigpicture all 30d ./bigpicture.md  # All projects, 30 days, custom output path
```

**Project matching**: The `project-name` is matched against the decoded
`~/.claude/projects/<encoded-path>/` directories. The encoding replaces `/`
with `-` (e.g. `-workspaces-Agents-eval` → `/workspaces/Agents-eval`). A
substring match on any path segment is sufficient. Use `all` to explicitly
select all projects.

## Three Reasoning Axes

Track these per work stream to surface where you are and what shift is needed:

### Diverge / Converge

- **Diverge**: Expanding — brainstorming, exploring options, opening questions
- **Converge**: Narrowing — selecting approaches, committing, closing questions
- **Signals**: Open questions in plans = diverging. Task completion clustering = converging. Multiple branches = diverging. Merge activity = converging.
- **Alert**: Diverging for N sessions without convergence → decision debt

### Inductive / Deductive

- **Inductive** (bottom-up reasoning): Observations → patterns → principles
- **Deductive** (top-down reasoning): Principles → predictions → implementations
- **Signals**: `## Learnings` in session-memory, AGENT_LEARNINGS = inductive. PRD/plan goals driving task creation = deductive.
- **Alert**: Implementing without learning (assumptions) or learning without formalizing into plans (knowledge not actionized)

### Top-down / Bottom-up

- **Top-down**: Strategy → decomposition → tasks (PRD → architecture → implementation)
- **Bottom-up**: Details → integration → strategy (bugs reveal gaps, tests surface flaws)
- **Signals**: PRD→task flow = top-down. Blockers→plan revisions, AGENT_REQUESTS = bottom-up.
- **Alert**: All top-down (no implementation feedback) or all bottom-up (reactive without direction)

## When to Use

- Starting a work session — orient across projects
- Planning what to work on next — strategic prioritization
- Sprint/week boundary — maintain the meta-plan
- Feeling stuck — surface current reasoning mode and whether a shift is needed
- Onboarding someone to your work streams

## Do Not Use

- For searching a specific past conversation (use `/resume` or `/history`)
- For per-session context (session-memory does this automatically)
- For modifying or deleting session history
- For real-time usage monitoring (use `/insights`)

## CC Data Sources

```
~/.claude/
├── history.jsonl                              # Global prompt log (display, timestamp, project, sessionId)
├── stats-cache.json                           # Daily aggregates (messageCount, sessionCount, toolCallCount)
├── projects/<encoded-path>/
│   ├── memory/MEMORY.md                       # Per-project persistent knowledge
│   ├── <session-uuid>.jsonl                   # Full transcripts (metadata-scan only, never bulk-read)
│   └── <session-uuid>/
│       ├── subagents/agent-<id>.jsonl         # Subagent transcripts
│       └── tool-results/toolu_<id>.txt        # Large tool result storage
├── plans/*.md                                 # Plan mode files (whimsical auto-names)
├── tasks/<session-or-team-name>/
│   ├── .lock, .highwatermark                  # State files
│   └── <N>.json                               # Tasks (id, subject, description, status, activeForm, owner, blocks, blockedBy)
└── teams/<team-name>/
    ├── config.json                            # Team config (name, description, members with model/prompt/role)
    └── inboxes/<member-name>.json             # Agent-to-agent messages (from, text, summary, timestamp)
```

See `references/cc-entry-types.md` for JSONL entry type reference.

## Workflow

1. **Parse arguments** — Extract `project-name`, `time-range`, and `output-path`
   from `$ARGUMENTS` per the Arguments table above. Apply defaults for omitted params.
   **Resolve output path**: If `output-path` is not explicitly provided, apply the
   default: when `project-name` is set (not `all`), decode the matched project path
   from `~/.claude/projects/<encoded-path>/` and write to `<decoded-path>/docs/bigpicture.md`.
   When `project-name` is `all` or omitted, write to `~/.claude/bigpicture.md`.

2. **Check existing** — Read output path. If bigpicture.md exists, load it for
   incremental update (preserve structure, update content).

3. **Discover projects** — Glob `~/.claude/projects/*/memory/MEMORY.md` and
   `~/.claude/projects/*/*.jsonl`. Decode project names from path encoding
   (`-` → `/`). If `project-name` is set and not `all`, filter to directories
   whose decoded path contains the value (case-insensitive substring match).

4. **Collect signals** (sequential, metadata-first — no subagents):
   a. **Activity**: Read `~/.claude/stats-cache.json` — daily message/session/tool-call counts for trajectory
   b. **Sessions**: Read `~/.claude/history.jsonl` — extract unique sessionIds per project, timestamps, prompt topics.
      **When `project-name` is set**: filter history entries to those whose `project` field
      contains the project name (case-insensitive). Collect the matching `sessionId` values
      into a **session allowlist** for use in steps 4e and 4h.
   c. **Projects**: Glob `~/.claude/projects/*/memory/MEMORY.md` — persistent knowledge per project
      (already filtered by step 3)
   d. **Plans**: Glob + Read `~/.claude/plans/*.md` — goals, open questions, decisions, scope.
      **When `project-name` is set**: only include plans that mention the project name
      in their content (case-insensitive grep). Exclude plans that don't reference the
      filtered project. This is a content-based filter since plan files have no project
      metadata in their filenames.
   e. **Tasks**: Glob + Read `~/.claude/tasks/*/*.json` — skip `.lock`/`.highwatermark`,
      parse dependency graph + status.
      **When `project-name` is set**: correlate task directory names against the session
      allowlist from step 4b. Task dirs named as session UUIDs match if the UUID is in the
      allowlist. Task dirs named as team names match via step 4f. Exclude unmatched dirs.
   f. **Teams**: Glob + Read `~/.claude/teams/*/config.json` — team structure, member roles, models.
      **When `project-name` is set**: only include teams whose `config.json` description or
      member prompts reference the project name (case-insensitive grep). Collect matching
      team names for use in step 4e task dir correlation.
   g. **Team comms**: Glob + Read `~/.claude/teams/*/inboxes/*.json` — agent findings,
      cross-agent synthesis. Only read inboxes for teams that passed the filter in step 4f.
   h. **Session metadata**: For recent sessions, read first+last 5 lines of `.jsonl` files
      to extract timestamps, branches, user prompts (never bulk-read full transcripts).
      **When `project-name` is set**: only read `.jsonl` files whose session UUID is in
      the session allowlist from step 4b.
   i. **Project docs**: For each project in `projects/`, decode the project path
      and scan for `docs/roadmap.md`, `CHANGELOG.md`, `AGENT_REQUESTS.md`.
      Extract: sprint status table, `[Unreleased]` changes, backlog items, open requests.
      (Already filtered by step 3.)

   **Critical**: Never read full session `.jsonl` transcripts in bulk. Use
   `history.jsonl` for session discovery and first+last lines for metadata only.

   **Critical**: When `project-name` is set, ALL sections of the output must respect the
   filter. Do not include plans, tasks, teams, blockers, or mode transitions from other
   projects. The only exception is "Cross-Project Connections" which may reference other
   projects but only as they relate *to* the filtered project (outbound connections).

5. **Classify reasoning modes** per work stream:
   - Count open questions vs. closed decisions in plans → diverge/converge
   - Count learning entries vs. plan-driven tasks → inductive/deductive
   - Trace flow: PRD→tasks (top-down) vs. blockers→revisions (bottom-up)
   - Flag mismatches per axis (see alerts above)

6. **Synthesize connections**:
   - Group sessions by project, then by time clusters (work streams)
   - Link plans → sessions (timestamp + project correlation)
   - Link tasks → plans (session-id in task path)
   - Identify recurring themes across project memories
   - Surface blockers: tasks with unresolved `blockedBy`
   - Detect trajectory: momentum (recent activity) vs. stale (no sessions in N days)
   - **When `project-name` is set**: Only synthesize filtered data. The "Cross-Project
     Connections" section shows only outbound connections *from* the filtered project.
     All other sections (Active Plans, Blockers, Mode Transitions, TODOs & DONEs) must
     contain ONLY items from the filtered project. If a plan/task/team didn't pass the
     filter in step 4, it must not appear anywhere in the output.

7. **Output** using format below. Write to output path.

## Output Format

```markdown
# Big Picture — <date>

## Reasoning Mode Summary

| Project | Phase | D/C | I/D | T/B | Alert |
|---------|-------|-----|-----|-----|-------|
| <name>  | <phase> | Diverging | Inductive | Bottom-up | <alert or —> |

Legend: D/C = Diverge/Converge, I/D = Inductive/Deductive, T/B = Top-down/Bottom-up

## Active Work Streams

### <Project Name>
- **Status:** <active/stalled/completed> — <N sessions in last 7d>
- **Current focus:** <from latest summaries + memory>
- **Reasoning mode:** <diverging+inductive = exploring> | <converging+deductive = building>
- **Key decisions:** <from plans + session memory>
- **Open questions:** <unresolved — divergence points>
- **Open tasks:** <N open> / <N total> — blockers: <list>
- **Trajectory:** <accelerating/steady/stalled>

## Cross-Project Connections
<!-- When project-name is set: only show outbound connections FROM the filtered project.
     When no filter: show all cross-project links. Omit section entirely if no connections. -->
- <Filtered Project> depends on / informs <Other Project>: <specific connection>
- Shared pattern: "<theme across memories>"

## Active Plans
| Plan | Project | Mode | Status | Key Goals |
|------|---------|------|--------|-----------|

## Project-Arching TODOs & DONEs

### <Project Name>

**Shipped (DONEs):**
- <Sprint/version>: <summary> — from roadmap.md / CHANGELOG.md

**In Progress:**
- [Unreleased]: <summary> — from CHANGELOG.md
- <N> tasks across <M> team dirs (<team names>)

**Pending (TODOs):**
- Backlog: <items> — from roadmap.md
- <N> pending CC tasks across <M> task dirs
- <N> open agent requests — from AGENT_REQUESTS.md

**Stale:**
- Tasks pending >7 days with no activity

## Blockers & Stale Items
- Task "<subject>" blocked since <date>
- Project "<name>" — no sessions in <N> days

## Mode Transitions Needed
- <Project>: Shift diverging → converging (enough options explored)
- <Project>: Shift top-down → bottom-up (implementation feedback needed)
- <Project>: Formalize learnings (inductive) into plan updates (deductive)
```

## Common Pitfalls

- **Data dump instead of synthesis**: If output exceeds ~200 lines, raise abstraction level. The skill interprets, not lists.
- **Stale big picture**: Only as fresh as last invocation. Not auto-updating.
- **Reading full transcripts**: Use `history.jsonl` for session discovery and first+last lines for metadata. Never bulk-read `.jsonl` files.
- **False mode classification**: Reasoning modes are heuristic signals, not definitive judgments. Present as evidence-based assessment.
- **Spawning subagents**: Do not use Agent tool. Sequential processing within the fork context is sufficient. Only justified at extreme scale (50+ projects) with explicit user request.

## Quality Check

- Correct > Complete > Minimal (ACE-FCA)
- ~100-200 lines output (concise, not exhaustive)
- Every claim traces to a specific CC artifact (file path, session summary, plan name)
- Incremental update preserves structure, refreshes content
- No subagents spawned during normal operation

## References

See `references/cc-entry-types.md` for JSONL session entry type taxonomy.
