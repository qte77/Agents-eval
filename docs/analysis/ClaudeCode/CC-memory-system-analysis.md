---
title: CC Memory System Analysis
source: https://code.claude.com/docs/en/memory
purpose: Analysis of Claude Code's dual memory system (CLAUDE.md + auto memory) for optimizing agent instructions, cross-session learning, and Ralph loop context management within Agents-eval.
created: 2026-03-07
---

**Status**: Generally available (CLAUDE.md); Auto memory enabled by default

## What the Memory System Is

Two complementary mechanisms that carry knowledge across Claude Code sessions ([source][cc-mem]):

1. **CLAUDE.md files**: Human-written persistent instructions (project standards, workflows, architecture)
2. **Auto memory**: Claude-written notes accumulated from corrections and discoveries

Both load at session start. Neither is enforced configuration — they're context. Specificity and conciseness improve adherence ([source][cc-mem]).

### CLAUDE.md vs Auto Memory

<!-- markdownlint-disable MD013 -->

| Aspect | CLAUDE.md | Auto Memory |
| ------ | --------- | ----------- |
| Author | Human | Claude |
| Content | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per working tree (git repo) |
| Loaded | Every session (full file) | Every session (first 200 lines of MEMORY.md) |
| Use for | Coding standards, workflows, architecture | Build commands, debugging insights, preferences |

<!-- markdownlint-enable MD013 -->

### CLAUDE.md Scope Hierarchy

<!-- markdownlint-disable MD013 -->

| Scope | Location | Shared with |
| ----- | -------- | ----------- |
| Managed policy | `/etc/claude-code/CLAUDE.md` (Linux) | All users in org (cannot be excluded) |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via source control |
| User | `~/.claude/CLAUDE.md` | Just you (all projects) |
| Local | `./CLAUDE.local.md` | Just you (current project, gitignored) |

<!-- markdownlint-enable MD013 -->

More specific locations take precedence. Files in parent directories load at launch; files in subdirectories load on demand when Claude reads files there ([source][cc-mem]).

### `.claude/rules/` System

Topic-specific instruction files with optional path scoping:

```text
.claude/
├── CLAUDE.md
└── rules/
    ├── code-style.md      # Always loaded
    ├── testing.md          # Always loaded
    └── api-design.md       # Path-scoped (see below)
```

Path-specific rules use YAML frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All endpoints must include input validation
```

Rules without `paths` frontmatter load unconditionally. Path-scoped rules load when Claude reads matching files ([source][cc-mem]).

### Auto Memory Architecture

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Concise index (first 200 lines loaded at session start)
├── debugging.md       # Topic file (loaded on demand)
├── api-conventions.md # Topic file (loaded on demand)
└── ...
```

- `<project>` derived from git repo — all worktrees share one auto memory directory
- Machine-local; not shared across machines or cloud environments
- Claude reads/writes during session; "Writing memory" / "Recalled memory" indicators shown

### Key Behaviors

- **Import syntax**: `@path/to/file` expands imports in CLAUDE.md (max 5 hops recursion) ([source][cc-mem])
- **Size target**: Under 200 lines per CLAUDE.md for best adherence ([source][cc-mem])
- **`/init`**: Auto-generates starting CLAUDE.md from codebase analysis ([source][cc-mem])
- **`/memory`**: Lists all loaded instruction files; toggles auto memory; opens memory folder ([source][cc-mem])
- **Compaction survival**: CLAUDE.md fully survives `/compact` (re-read from disk) ([source][cc-mem])
- **`claudeMdExcludes`**: Skip irrelevant CLAUDE.md files in monorepos ([source][cc-mem])
- **Symlinks**: `.claude/rules/` supports symlinks for cross-project shared rules ([source][cc-mem])
- **Subagent memory**: Subagents can maintain their own auto memory ([source][cc-sub])

### Configuration

```json
{
  "autoMemoryEnabled": false,
  "claudeMdExcludes": ["**/other-team/CLAUDE.md"]
}
```

Or: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` env var.

## Current Project Usage

This project already uses both systems extensively:

### CLAUDE.md Structure

```text
CLAUDE.md              → @AGENTS.md import
AGENTS.md              → Behavioral rules, compliance, decision framework
CONTRIBUTING.md        → Technical workflows, coding standards
AGENT_REQUESTS.md      → Escalation protocol
AGENT_LEARNINGS.md     → Accumulated pattern knowledge
.claude/rules/
├── context-management.md  → ACE-FCA context window principles
└── core-principles.md     → KISS/DRY/YAGNI mandatory principles
```

### Auto Memory

Active at `~/.claude/projects/-workspaces-Agents-eval/memory/`. Contains `MEMORY.md` index and topic files accumulated across sessions.

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Aspect | Current State | Optimization Opportunity |
| ------ | ------------- | ------------------------ |
| CLAUDE.md size | AGENTS.md is 200+ lines | Consider splitting role boundaries into `.claude/rules/agent-roles.md` with path scoping |
| Import chain | CLAUDE.md → AGENTS.md → CONTRIBUTING.md → AGENT_LEARNINGS.md | Deep chain; ensure total token cost is acceptable |
| Path-scoped rules | 2 rules (context-management, core-principles), both unconditional | Could add path-scoped rules for `src/app/agents/` (agent patterns), `tests/` (testing conventions) |
| Auto memory | Active, accumulating learnings | Cross-check with AGENT_LEARNINGS.md for duplicates — auto memory and manual learnings may diverge |
| Ralph loop context | Each iteration starts fresh; reads CLAUDE.md + auto memory | Working as designed — see [CC-ralph-enhancement-research.md](CC-ralph-enhancement-research.md#context-rot-prevention) for context rot analysis |
| Cloud sessions | N/A | Auto memory is machine-local; cloud sessions rely on committed CLAUDE.md only (see [CC-cloud-sessions-analysis.md](CC-cloud-sessions-analysis.md)) |
| Managed policy | Not used | Could use for org-wide CC standards if deploying across team |

<!-- markdownlint-enable MD013 -->

### Decision Rule

**CLAUDE.md and rules files are the project's primary instruction mechanism and already well-structured. Focus optimization on: (1) path-scoping rules to reduce context noise, (2) keeping CLAUDE.md import chain under 400 total lines, (3) deduplicating auto memory vs AGENT_LEARNINGS.md.**

### Potential Optimizations

1. **Path-scope agent role boundaries**:

   ```markdown
   ---
   paths:
     - "src/app/agents/**/*.py"
   ---
   # Agent Implementation Rules
   - Use PydanticAI agent patterns from agent_system.py
   ```

2. **Deduplicate auto memory vs AGENT_LEARNINGS.md**: Run periodic review to ensure auto memory doesn't accumulate stale patterns that contradict updated AGENT_LEARNINGS.md entries.

**Recommendation**: No structural changes needed. The current CLAUDE.md + rules + auto memory setup is well-aligned with the documented best practices. Minor wins from path-scoping and deduplication reviews.

## References

- [CC Memory docs][cc-mem]
- [CC Skills docs][cc-skills]
- [CC Settings docs][cc-settings]
- [CC Subagent memory][cc-sub]

[cc-mem]: https://code.claude.com/docs/en/memory
[cc-skills]: https://code.claude.com/docs/en/skills
[cc-settings]: https://code.claude.com/docs/en/settings
[cc-sub]: https://code.claude.com/docs/en/sub-agents#enable-persistent-memory
