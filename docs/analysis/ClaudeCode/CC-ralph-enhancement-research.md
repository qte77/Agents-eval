---
title: Ralph Loop Enhancement Research
source: ralph/scripts/ralph.sh, ralph/README.md, external Ralph pattern research
purpose: Identify actionable enhancements to the Ralph loop based on internal gap analysis and external pattern research.
created: 2026-03-07
---

**Status**: Research (informational — feeds into sprint planning)

## Current Architecture Summary

Ralph is an autonomous TDD development loop driving `claude -p` to implement stories from `prd.json`. Full architecture in [ralph/README.md](../../../ralph/README.md); skills adoption in [CC-skills-adoption-analysis.md](CC-skills-adoption-analysis.md).

## Known Gaps (Internal)

Identified from codebase exploration — these are bugs or inconsistencies, not feature requests.

### High Priority (Broken Functionality)

<!-- markdownlint-disable MD013 -->

| Gap | Impact | Fix |
| --- | ------ | --- |
| **`ralph_status` uses legacy `.passes` field** | Always shows 0 completed stories on current `status` schema | Change `jq` query from `.passes == true` to `.status == "passed"` in Makefile recipe |
| **Documentation path inconsistency** | AGENTS.md references `.claude/scripts/ralph/` but actual path is `ralph/scripts/` | Update AGENTS.md to reference `ralph/scripts/` |

<!-- markdownlint-enable MD013 -->

### Medium Priority (Concurrency / Robustness)

<!-- markdownlint-disable MD013 -->

| Gap | Impact | Fix |
| --- | ------ | --- |
| **`/tmp` path collision across worktrees** | `BASELINE_FILE`, `RETRY_CONTEXT_FILE`, `TDD_VERIFIED_DIR` use fixed `/tmp/claude/ralph_*` paths — concurrent worktrees overwrite each other | Namespace paths by worktree: `/tmp/claude/ralph_<worktree_hash>/` |
| **Stale snapshot tests in teams mode** | Story A's baseline doesn't account for story B's concurrent changes | No clean fix without sequential validation; document as known limitation |
| **File-conflict dependencies not auto-detected** | `generate_prd_json.py` doesn't auto-detect file overlaps between stories | Add `--check-overlaps` flag to `generate_prd_json.py` that warns when stories share files without `depends_on` |

<!-- markdownlint-enable MD013 -->

### Low Priority (Enhancement Opportunities)

<!-- markdownlint-disable MD013 -->

| Gap | Impact | Fix |
| --- | ------ | --- |
| **No BDD support** | Only TDD `[RED]/[GREEN]/[REFACTOR]` accepted; BDD workflows need different markers | Add `RALPH_TEST_WORKFLOW=tdd\|bdd` switch (TODO noted in ralph.sh header) |
| **Bash brittleness** | Shell script untestable, hard to extend | Rewrite in Rust or Python (acknowledged TODO — YAGNI until measured need) |

<!-- markdownlint-enable MD013 -->

## External Pattern Research

### Ralphinho — RFC-Driven Multi-Agent DAG

**Source**: `affaan-m/everything-claude-code` ([GitHub][ralphinho], 58k stars)

Extends Ralph from sequential story execution to DAG-based parallel orchestration:

- RFC (Request for Comments) documents define features with dependency graphs
- BFS wave computation (similar to our `compute_waves()`)
- Parallel agents with merge coordination
- "De-Sloppify" cleanup passes after initial implementation

**Relevance**: Our `generate_prd_json.py` already computes waves and our teams mode already delegates wave-peers. Ralphinho formalizes this further with RFC documents. The "De-Sloppify" pass pattern is worth adopting — a post-story cleanup iteration focused on code quality rather than feature implementation.

### Trellis — Cross-Layer Validation Commands

**Source**: Trellis ([docs][trellis])

Adds layer-specific quality checks as slash commands:

- `/check-backend` — backend-specific validation (API contracts, DB migrations)
- `/check-frontend` — frontend-specific validation (UI tests, accessibility)
- `/check-cross-layer` — cross-layer consistency

**Relevance**: Our validation is currently monolithic (`make validate`). For future multi-layer projects, scoped validation commands would reduce false-positive blocking. Not needed now — single-layer Python project.

### Stop-Hook Pattern (Official Plugin)

**Source**: Anthropic `ralph-wiggum` plugin ([GitHub][ralph-official])

The official plugin uses a `StopTool` hook that intercepts session exit and re-prompts with the original task. Simpler than our bash loop but less control:

- No TDD enforcement
- No baseline-aware validation
- No story dependency tracking
- No teams mode

**Relevance**: Our implementation is more sophisticated. The stop-hook pattern is useful for simple tasks but insufficient for our structured PRD-driven workflow.

### Context Rot Prevention

**Source**: Geoffrey Huntley ([blog][ghuntley-loop]), LinearB podcast ([source][linearb])

Key insight: "Context rot" — agent quality degrades as context fills with stale information. Solutions:

- Fresh context per iteration (our approach: `claude -p` starts clean each time)
- Filesystem as memory (our approach: `prd.json` + `progress.txt` + git)
- Never let the agent compact — start fresh instead

**Relevance**: Already implemented. Our Ralph loop spawns a fresh `claude -p` per story, using external state files for continuity. This is the recommended approach per Huntley and Anthropic's "effective harnesses" guide ([source][effective-harnesses]).

### LobeHub Skills Marketplace

**Source**: LobeHub ([ralph-loop skill][lobehub-ralph])

Community-published Ralph loop as a CC Skill. Uses `.claude/ralph-loop.local.md` as state file. Simpler implementation (no PRD, no TDD, no teams) but demonstrates the pattern's portability as a skill.

**Relevance**: Validates that Ralph can be packaged as a CC Skill or Plugin. See [CC-plugin-packaging-research.md](CC-plugin-packaging-research.md) for packaging analysis.

## Actionable Enhancements

### Tier 1 — Fix Now (bugs, 15 min each)

1. **Fix `ralph_status` jq query**: `.passes == true` → `.status == "passed"`
2. **Fix AGENTS.md path reference**: `.claude/scripts/ralph/` → `ralph/scripts/`

### Tier 2 — Improve Next Sprint (robustness)

3. **Namespace `/tmp` paths by worktree**: Prevent concurrent worktree collisions
4. **Add `--check-overlaps` to `generate_prd_json.py`**: Warn on file conflicts without `depends_on`
5. **Add De-Sloppify pass**: Post-story cleanup iteration — run `make quick_validate` with a "fix all lint/type/complexity issues" prompt before marking story passed

### Tier 3 — Monitor (not yet actionable)

6. **BDD workflow support**: Add `RALPH_TEST_WORKFLOW` switch when a BDD project needs Ralph
7. **Cross-layer validation commands**: Add `/check-backend` etc. when project becomes multi-layer
8. **Rust/Python rewrite**: When bash brittleness measurably blocks development
9. **`/loop` command as alternative** (v2.1.71): CC now has a built-in `/loop` command with cron scheduling for recurring prompts/commands on intervals. This overlaps with Ralph's core loop mechanic. Key differences: `/loop` is session-bound (no external state), lacks TDD enforcement, no story dependencies or PRD tracking. Could replace Ralph for simple repeating tasks but insufficient for structured multi-story workflows. Worth monitoring if `/loop` gains state persistence or hook integration.

## References

- [Effective Harnesses for Long-Running Agents][effective-harnesses] — Anthropic engineering blog
- [Ralph Pattern][ghuntley-ralph] — Geoffrey Huntley original post
- [Ralph Playbook][ralph-playbook] — ClaytonFarr comprehensive guide (853 stars)
- [Everything Claude Code][ralphinho] — Autonomous loop patterns including Ralphinho
- [Trellis docs][trellis] — Cross-layer validation commands
- [LobeHub Ralph Loop skill][lobehub-ralph] — Community skill implementation
- [Ralph Wiggum plugin][ralph-official] — Official Anthropic plugin
- [LinearB podcast][linearb] — Huntley on context rot and loop discipline
- [Shipyard Ralph guide][shipyard] — Ralph loop pattern explanation

[effective-harnesses]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[ghuntley-ralph]: https://ghuntley.com/ralph/
[ghuntley-loop]: https://ghuntley.com/loop/
[ralph-playbook]: https://github.com/ClaytonFarr/ralph-playbook
[ralphinho]: https://github.com/affaan-m/everything-claude-code
[trellis]: https://docs.trytrellis.app/guide/ch05-commands
[lobehub-ralph]: https://lobehub.com/skills/101mare-skill-library-ralph-loop
[ralph-official]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop
[linearb]: https://linearb.io/dev-interrupted/podcast/inventing-the-ralph-wiggum-loop
[shipyard]: https://shipyard.build/blog/claude-code-ralph-loop/
