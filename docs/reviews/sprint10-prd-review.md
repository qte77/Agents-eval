---
title: Sprint 10 PRD Post-Task Review
purpose: Audit trail for PRD v2.1.0 -> v3.0.0 review findings, resolutions, and deferred items
created: 2026-02-21
prd: docs/sprints/PRD-Sprint10-Ralph.md
---

## Things to Delete

1. **restack provider entry** -- Not an inference provider, it's a workflow orchestration platform. Having it in `PROVIDER_REGISTRY` is misleading.
   **Resolution**: Kept -- user decision: restack offers endpoints.

2. **together free model reference** -- `config_chat.json` has `Llama-3.3-70B-Instruct-Turbo-Free` which was removed Jul 2025. Fails silently at runtime.
   **Resolution**: Fixed in PRD v3.0.0 Feature 3 AC5 (live bug).

## Incoherences Found

1. **Feature 2 (Sweep) over-scoped** -- Full GUI sweep page with progress indicators, multi-select papers, composition toggles, and background threading is significant. Sprint goal is parity, not polish.
   **Resolution**: Removed from sprint. Moved to Out of Scope with rationale (`SweepRunner` lacks `engine` param, results shape mismatch).

2. **Feature 3 AC6 (sweep graphs) undeclared dependency** -- Creates dependency on Feature 2 completion but not declared in story breakdown.
   **Resolution**: AC6 dropped since sweep feature removed.

3. **STORY-015 `models.py` file-conflict undocumented** -- File-conflict table shows it but Feature 6 Files section doesn't list `models.py`. Conflict is indirect (`agent_system.py` uses providers that `models.py` defines).
   **Resolution**: Fixed in PRD v3.0.0 -- file-conflict table now has a Reason column documenting the indirect dependency.

## Quick Wins Missing

1. **`max_content_length` values wrong** -- Cerebras says 8192 but `gpt-oss-120b` has 128K context. Grok says 15000 but should be 131K. Data-only fix.
   **Resolution**: Fixed in PRD v3.0.0 Feature 3 AC7 -- focused on "maximum token usage allowed on free tier before blocking."

2. **huggingface `facebook/bart-large-mnli` is a classification model** -- Not a chat model. Will fail immediately if anyone selects HuggingFace as a provider. Live bug.
   **Resolution**: Fixed in PRD v3.0.0 Feature 3 AC4 (live bug).

## Things NOT to Add (YAGNI)

- Don't add provider health checks or connectivity validation -- not in scope.
- Don't add a "test connection" button in GUI -- nice-to-have, not parity.
- Don't refactor `create_llm_model()` into a registry pattern -- the if/elif chain is fine for 19 providers.
- Don't add `--judge-provider` validation to CLI argparse -- judge provider uses a separate settings model, not part of E2E parity.

**Resolution**: All listed in PRD v3.0.0 Out of Scope.

---

## Deep-Dive: E2E Pipeline Gaps

### CC Runs -- What Breaks After Subprocess Returns

1. **CC results don't flow into evaluation pipeline** -- `app.main()` ignores `engine` param, always runs MAS. Three-tier pipeline expects `GeneratedReview` + `GraphTraceData`. CC produces `CCResult` with different shape.
   **Resolution**: PRD v3.0.0 Feature 1 AC7 -- CC raw text wrapped into `GeneratedReview` so all 3 tiers work.

2. **`_prepare_result_dict()` assumes MAS output shape** -- Expects `composite_result` and `graph` keys. CC runs won't return this shape.
   **Resolution**: PRD v3.0.0 Feature 1 tech reqs -- `CCResultDict` shape defined explicitly.

3. **CC teams timeout orphans child processes** -- `proc.kill()` only kills lead process. Teammates linger as orphans.
    **Resolution**: PRD v3.0.0 Feature 1 AC6 -- `os.killpg` with `start_new_session=True`.

### Graph Visualization -- End-to-End Gaps

1. **CC solo has no meaningful graph data** -- Single JSON blob, 1 node 0 edges. Technically correct but useless.
    **Resolution**: PRD v3.0.0 Feature 2 AC1 -- single-agent runs (MAS solo or CC solo) show tool-call chain graph.

2. **CC teams graph data not persisted** -- `run_cc_teams()` parses JSONL events during execution. If GUI stores only final `CCResult`, stream events for graph construction are lost.
    **Resolution**: PRD v3.0.0 Feature 2 AC5 -- `CCResult.team_artifacts` must retain parsed team members and task delegation edges.

3. **`build_interaction_graph()` key format mismatch** -- Expects `from`/`source_agent` and `to`/`target_agent` keys. CC team artifacts use `members[].name` and `tasks[].owner`.
    **Resolution**: PRD v3.0.0 Feature 2 AC4 -- explicit mapping specified: `members[].name` -> nodes, `tasks[].owner` -> delegation edges, `tasks[].blockedBy` -> dependency edges.

### Metrics and Evaluation -- What's Actually Measurable

1. **Tier 3 graph metrics assume MAS delegation patterns** -- `path_convergence`, `coordination_centrality`, `task_distribution_balance` assume manager->researcher->analyst->synthesizer shape. CC teams (flat delegation) produces non-comparable scores.
    **Resolution**: PRD v3.0.0 Feature 2 AC8 -- CC graph metrics labeled "informational -- not comparable to MAS scores." CC-specific metrics (delegation fan-out, task completion rate) deferred to Out of Scope.

2. **Evaluation Results page empty after CC-only run** -- Tier 1/2 expect `GeneratedReview`, CC produces raw text. Page shows mostly empty.
    **Resolution**: PRD v3.0.0 Feature 1 AC7/AC8 -- CC raw text wrapped into `GeneratedReview`, all 3 tiers shown with CC engine banner.

### Sweeps -- Structural Issues

1. **`SweepRunner` hardcodes MAS-first ordering** -- `run()` calls `_run_mas_evaluations()` then `_run_cc_baselines()`. No `engine` parameter to skip MAS for CC-only sweeps.
    **Resolution**: Deferred -- sweep removed from sprint. Documented in Out of Scope with rationale.

2. **Sweep results shape differs from single-run results** -- `SweepRunner` produces `results.json` + `summary.md` files. Single-run path uses `st.session_state`. Format mismatch blocks evaluation page rendering.
    **Resolution**: Deferred -- sweep removed from sprint. Documented in Out of Scope.

---

## PRD v2.1.0 -> v3.0.0 Change Summary

**Feature 1 (CC Engine) -- integrated items 8, 9, 10, 15**:

- AC7: Changed from "skip Tier 1/2" to "wrap CC raw text into `GeneratedReview` so all 3 tiers work"
- AC8: Changed from "show N/A for Tier 1/2" to "show all 3 tiers with CC engine banner"
- AC6: Added `os.killpg` process group kill detail (item 10)
- Tech reqs: Added `CCResultDict` shape definition (item 9) and CC -> `GeneratedReview` wrapping

**Feature 2 (Graph Viz) -- integrated items 11, 12, 13, 14**:

- AC1/AC2: Unified graph approach -- single-agent runs (MAS solo or CC solo) show tool-call chain; multi-agent runs (MAS 4-agent or CC teams) show tool calls + delegation + inter-agent edges
- AC4: Explicit CC team artifact -> `GraphTraceData` mapping (item 13)
- AC5: `CCResult.team_artifacts` persistence requirement (item 12)
- AC8: CC Tier 3 metrics labeled "informational" (item 14)
- Dropped AC6 (sweep graphs) since sweep feature removed

**Feature 3 (Providers)**:

- Kept restack in registry (user decision: they offer endpoints)
- AC4/AC5: Called out huggingface and together as **live bugs**
- AC7: Focused `max_content_length` on "maximum token usage allowed on free tier before blocking"

**Orchestration**: Waves reorganized for 2-teammate execution with sequential batching within each wave.

**Removed**: Feature 2 (GUI Sweep) -- renumbered F3-F7 -> F2-F6, stories STORY-010 through STORY-015 (was STORY-016).
