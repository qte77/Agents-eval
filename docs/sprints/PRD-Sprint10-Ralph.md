---
title: Product Requirements Document - Agents-eval Sprint 10
description: "Sprint 10: 6 features — E2E CLI/GUI parity for CC engine (solo + teams), graph visualization for all modes, expanded providers, judge UX, PydanticAI migration, test quality."
version: 3.0.0
created: 2026-02-21
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Sprint 10 goal**: E2E parity between CLI and GUI for all execution modes. The CC engine (solo + teams) works from CLI but is broken in the GUI — `app.main()` ignores the `engine` parameter and always runs MAS. Graphs must build and visualize for all modes including CC. Provider coverage is expanded with 7 new inference providers. Judge settings UX is improved, PydanticAI deprecated APIs are migrated, and `inspect.getsource` test anti-patterns are replaced.

### Current State

| Mode | CLI | GUI | Gap |
| --- | --- | --- | --- |
| Free-text query (MAS) | Works | Works | None |
| Paper review (MAS) | Works (`--paper-id`) | Works (dropdown) | None |
| CC solo | Works (`--engine=cc`) | Radio exists, but `app.main()` ignores `engine` — runs MAS | **Broken** |
| CC teams | Works (`--engine=cc --cc-teams`) | No toggle exists | **Missing** |
| Graph visualization | N/A (CLI) | Works for MAS; CC produces no graph data | **Partial** |
| CC evaluation | Tier 1/2 expect `GeneratedReview` -- CC produces raw text, needs wrapping | Not wired | **No path** |

---

## Development Methodology

**All implementation stories MUST follow these practices. Ralph Loop enforces this order.**

### TDD Workflow (Mandatory for all features)

1. **RED**: Write failing tests first using `testing-python` skill. Tests define expected behavior before any implementation code exists.
2. **GREEN**: Implement minimal code to pass tests using `implementing-python` skill. No extra functionality.
3. **REFACTOR**: Clean up while keeping tests green. Run `make validate` before marking complete.

### Test Tool Selection

| Tool | Use for | NOT for |
|------|---------|------------|
| **pytest** | Core logic, unit tests, known edge cases (primary TDD tool) | Random inputs |
| **Hypothesis** | Property invariants, bounds, all-input guarantees | Snapshots, known cases |
| **inline-snapshot** | Regression, model dumps, complex structures | TDD red-green, ranges |

**Decision rule**: If the test wouldn't catch a real bug, don't write it. Test behavior, not implementation.

### Mandatory Practices

- **Mock external dependencies** (HTTP, LLM providers, file systems, subprocess) using `@patch`. Never call real APIs in unit tests.
- **Test behavior, not implementation** -- test observable outcomes (return values, side effects, error messages), not internal structure.
- **Google-style docstrings** for every new file, function, class, and method.
- **`# Reason:` comments** for non-obvious logic.
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (all features) | `testing-python` (RED) -> `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |
| Design phase | `researching-codebase` -> `designing-backend` |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->
<!-- PARSER REQUIREMENT: No compound sub-features — one heading per story -->
<!-- PARSER REQUIREMENT: Flatten AC items — no indented sub-items under a checkbox -->
<!-- PARSER REQUIREMENT: Each sub-feature MUST have its own **Files**: section -->

#### Feature 1: Wire CC Engine to GUI Execution Path (Solo + Teams)

**Description**: The "Claude Code" radio button in `run_app.py` sets `engine="cc"` and passes it to `app.main()`, but `main()` only logs the value and unconditionally runs the MAS PydanticAI pipeline. The CLI (`run_cli.py:126-138`) correctly branches to `cc_engine.run_cc_solo`/`run_cc_teams` -- the GUI must do the same. Additionally, there is no CC teams toggle in the GUI at all. CC-only runs have no defined evaluation path: the three-tier pipeline expects `GeneratedReview` + `GraphTraceData` from the MAS trace collector, but CC produces `CCResult` with a different shape. The evaluation page must handle CC output gracefully.

**Acceptance Criteria**:

- [ ] AC1: Selecting "Claude Code" in the GUI radio button invokes `cc_engine.run_cc_solo()` instead of the MAS pipeline
- [ ] AC2: A "CC Teams" checkbox appears when CC engine is selected; when enabled, `run_cc_teams()` is invoked instead of `run_cc_solo()`
- [ ] AC3: CC engine results are stored in session state and available to Evaluation Results and Agent Graph pages
- [ ] AC4: MAS-specific controls (sub-agents, provider, token limit) remain hidden when CC engine is selected (existing behavior preserved)
- [ ] AC5: Error handling for missing `claude` CLI binary shows user-friendly message in GUI
- [ ] AC6: `run_cc_teams` uses process group kill (`os.killpg`) after timeout — not just `proc.kill()` — to clean up teammate child processes
- [ ] AC7: CC-only runs produce all three evaluation tiers: CC raw text output is wrapped into a `GeneratedReview`-compatible structure so Tier 1 (traditional metrics) and Tier 2 (LLM-as-Judge) can score it; Tier 3 graph analysis uses CC artifacts
- [ ] AC8: When engine is CC, the Evaluation Results page shows all three tiers with a banner noting "CC engine output — review text extracted from raw CC response"
- [ ] AC9: All existing MAS tests continue to pass; new tests cover the CC GUI path (solo and teams)
- [ ] AC10: `make validate` passes with no regressions

**Technical Requirements**:

- Add CC engine branch in `_execute_query_background()` mirroring `run_cli.py:126-138` logic
- Add `cc_teams` checkbox in `render_app()` -- visible only when `engine == "cc"`
- Handle subprocess execution within Streamlit's threading model (background thread already exists)
- Define `CCResultDict` shape for `_prepare_result_dict()`: `{"engine": "cc", "raw_response": str, "token_count": int, "latency_seconds": float, "cc_result": CCResult, "graph_trace": GraphTraceData | None, "composite_result": CompositeResult}`. MAS result dict keeps existing shape with `"engine": "mas"`
- Wrap CC raw text output into a `GeneratedReview` structure: extract the review text from `CCResult.output_data`, populate `review_text` field, set metadata fields (model="claude-code", provider="cc"). This allows Tier 1 and Tier 2 to score CC output using the same pipeline as MAS
- Fix `run_cc_teams` timeout: start subprocess with `start_new_session=True`, then on timeout use `os.killpg(os.getpgid(proc.pid), signal.SIGTERM)` followed by `proc.kill()` to ensure teammate child processes are cleaned up (`cc_engine.py:236-256`)
- Wire evaluation page to check `result["engine"]` and render CC-specific layout when `engine == "cc"`
- Mock `subprocess.run` and `subprocess.Popen` in tests -- never call real `claude` CLI

**Files**:

- `src/gui/pages/run_app.py` (edit -- CC branch in `_execute_query_background`, add CC teams checkbox, CC result dict handling)
- `src/app/engines/cc_engine.py` (edit -- enforce timeout with process group kill in `run_cc_teams`)
- `src/gui/pages/evaluation_results.py` (edit -- CC-specific layout when engine is CC)
- `tests/test_gui/test_session_state_wiring.py` (edit -- CC engine path tests, solo + teams, CC eval page)

---

#### Feature 2: Graph Building and Visualization for All Execution Modes

**Description**: NetworkX graphs are only built from MAS trace data. When CC engine runs, no graph is produced -- `CCTraceAdapter.parse()` returns `GraphTraceData` for evaluation scoring but it is never converted to an `nx.DiGraph` for the Agent Graph page. The graph shape depends on whether the run is single-agent or multi-agent: single-agent runs (MAS solo query or CC solo) show a tool-call graph (agent -> tool1 -> tool2 -> ...); multi-agent runs (MAS 4-agent pipeline or CC teams) show tool calls plus team delegation and inter-agent communication edges. CC teams parse `TeamCreate`/`Task` JSONL events during execution but the stream data may not persist in `CCResult`. Tier 3 graph metrics assume MAS delegation patterns; CC teams produce flat delegation which yields non-comparable scores.

**Acceptance Criteria**:

- [ ] AC1: Single-agent runs (MAS solo or CC solo) produce an `nx.DiGraph` showing a tool-call chain: agent node -> tool_call_1 -> tool_call_2 -> ... (extracted from trace data or CC output)
- [ ] AC2: Multi-agent runs (MAS 4-agent or CC teams) produce an `nx.DiGraph` showing agent/team member nodes, tool-call edges, and delegation/communication edges between agents
- [ ] AC3: `CCTraceAdapter.parse()` output (`GraphTraceData`) is converted to `nx.DiGraph` via `build_interaction_graph()`
- [ ] AC4: `cc_result_to_graph_trace()` maps CC team artifacts to `GraphTraceData` format: `members[].name` -> nodes, `tasks[].owner` -> delegation edges (lead -> owner), `tasks[].blockedBy` -> dependency edges
- [ ] AC5: `CCResult.team_artifacts` retains parsed team members and task delegation edges from the JSONL stream so graph data survives after execution
- [ ] AC6: Empty graphs (0 nodes, 0 edges) display a descriptive warning instead of the generic "No agent interaction data available" message
- [ ] AC7: MAS graph visualization continues to work unchanged
- [ ] AC8: Tier 3 graph metrics are documented as MAS-specific; CC graph metrics are labeled "informational -- not comparable to MAS scores" in evaluation output
- [ ] AC9: `make validate` passes with no regressions

**Technical Requirements**:

- In the CC branch added by Feature 1, after CC execution: call `CCTraceAdapter` on CC result artifacts, then `build_interaction_graph()` to produce `nx.DiGraph`, store in `st.session_state.execution_graph`
- **Single-agent graph** (MAS solo query or CC solo): parse tool calls from trace data or `CCResult.output_data`; build linear chain graph (agent node -> tool_call_1 -> tool_call_2 -> ...). If no tool calls, show single agent node with info message
- **Multi-agent graph** (MAS 4-agent or CC teams): include tool-call edges (agent -> tool) plus inter-agent edges. For MAS: delegation edges from trace collector (manager -> researcher, etc.). For CC teams: map `TeamCreate` members to nodes, `Task` owner assignments to delegation edges (lead -> teammate), `Task` blockedBy to dependency edges, teammate tool calls to tool-call edges
- `build_interaction_graph()` expects `agent_interactions` with `from`/`source_agent` and `to`/`target_agent` keys. `cc_result_to_graph_trace()` must translate: team lead -> task owner = delegation edge (edge type "delegation"), task blockedBy = dependency edge (edge type "dependency")
- In `agent_graph.py`: distinguish between `graph is None` (no execution yet), empty graph (execution produced no interactions), and populated graph -- show appropriate messages for each
- For Tier 3 metrics on CC runs: add `engine_type` field to graph metric output; when `engine_type == "cc"`, prefix metric labels with "Informational" in evaluation display

**Files**:

- `src/app/engines/cc_engine.py` (edit -- add `cc_result_to_graph_trace()` helper with CC solo and CC teams graph mapping)
- `src/gui/pages/run_app.py` (edit -- wire CC graph into session state after Feature 1 CC branch)
- `src/gui/pages/agent_graph.py` (edit -- differentiate empty vs missing graph messages, CC graph labeling)
- `tests/test_gui/test_agent_graph.py` (new -- graph rendering for MAS, CC solo, CC teams)

---

#### Feature 3: Expand Inference Provider Registry and Update Stale Models

**Description**: The current `PROVIDER_REGISTRY` has 12 providers but is missing many popular OpenAI-compatible inference providers. Key omissions: Groq, Fireworks AI, DeepSeek, Mistral, SambaNova, Nebius, Cohere. The `anthropic` provider entry falls through to the generic `OpenAIChatModel` handler in `create_llm_model()` instead of using PydanticAI's native Anthropic support. Several existing `config_chat.json` entries have stale/deprecated model IDs -- two are live bugs: `huggingface` uses `facebook/bart-large-mnli` (a classification model, not chat -- will fail immediately) and `together` uses `Llama-3.3-70B-Instruct-Turbo-Free` (removed Jul 2025 -- will fail silently). Multiple `max_content_length` values are wrong (e.g., `cerebras` says 8192 but `gpt-oss-120b` has 128K context; `grok` says 15000 but should be 131K). Values must reflect the maximum token usage allowed on each provider's free tier before requests get blocked. See [Inference-Providers.md](../analysis/Inference-Providers.md) for the full provider analysis.

**Acceptance Criteria**:

- [ ] AC1: `PROVIDER_REGISTRY` includes the following new providers: `groq`, `fireworks`, `deepseek`, `mistral`, `sambanova`, `nebius`, `cohere`
- [ ] AC2: Each new provider has correct `env_key`, `base_url`, and `model_name_prefix` in `PROVIDER_REGISTRY`
- [ ] AC3: Each new provider has a matching entry in `config_chat.json` with best free-tier model and correct `max_content_length`
- [ ] AC4: Live bug fixed: `huggingface` model updated from `facebook/bart-large-mnli` (classification, not chat) to `meta-llama/Meta-Llama-3.3-70B-Instruct`
- [ ] AC5: Live bug fixed: `together` model updated from removed `Llama-3.3-70B-Instruct-Turbo-Free` to `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- [ ] AC6: Existing stale `config_chat.json` entries updated to current models: `gemini-2.0-flash`, `gpt-4.1-mini` (openai + github), `grok-3-mini`, `claude-sonnet-4-20250514`, `qwen/qwen3-next-80b-a3b-instruct:free` (openrouter), `llama3.3:latest` (ollama)
- [ ] AC7: `max_content_length` in `config_chat.json` reflects the maximum token usage allowed on each provider's free tier before requests get rate-limited or blocked (per [Inference-Providers.md](../analysis/Inference-Providers.md) "Key Limit" column)
- [ ] AC8: `create_llm_model()` handles `anthropic` provider using PydanticAI's native `AnthropicModel` instead of the generic OpenAI-compatible fallback
- [ ] AC9: `create_llm_model()` handles `groq` with `OpenAIModelProfile(openai_supports_strict_tool_definition=False)` (same as existing `cerebras` handling)
- [ ] AC10: GUI Settings page provider dropdown automatically includes all new providers (already dynamic from `PROVIDER_REGISTRY.keys()`)
- [ ] AC11: CLI `--chat-provider` accepts all new provider names and validates against `PROVIDER_REGISTRY` at argument parsing time
- [ ] AC12: `make validate` passes with no regressions

**Technical Requirements**:

- Add entries to `PROVIDER_REGISTRY` in `src/app/data_models/app_models.py` with correct base URLs:
  - `groq`: `https://api.groq.com/openai/v1`, env: `GROQ_API_KEY`
  - `fireworks`: `https://api.fireworks.ai/inference/v1`, env: `FIREWORKS_API_KEY`
  - `deepseek`: `https://api.deepseek.com/v1`, env: `DEEPSEEK_API_KEY`
  - `mistral`: `https://api.mistral.ai/v1`, env: `MISTRAL_API_KEY`
  - `sambanova`: `https://api.sambanova.ai/v1`, env: `SAMBANOVA_API_KEY`
  - `nebius`: `https://api.studio.nebius.ai/v1`, env: `NEBIUS_API_KEY`
  - `cohere`: `https://api.cohere.com/v2`, env: `COHERE_API_KEY`
- Add matching entries to `config_chat.json` with models from [Inference-Providers.md](../analysis/Inference-Providers.md)
- Update stale existing `config_chat.json` model IDs and `max_content_length` values (see AC4-AC7 and analysis doc)
- Add `anthropic` branch in `create_llm_model()` using `from pydantic_ai.models.anthropic import AnthropicModel`
- Add `groq` branch in `create_llm_model()` with `openai_supports_strict_tool_definition=False`
- Providers that need `openai_supports_strict_tool_definition=False`: `groq`, `cerebras` (already handled), `fireworks`, `together`, `sambanova`
- Add `choices=list(PROVIDER_REGISTRY.keys())` to CLI `--chat-provider` argparse definition for early validation

**Files**:

- `src/app/data_models/app_models.py` (edit -- add 7 providers to `PROVIDER_REGISTRY`)
- `src/app/llms/models.py` (edit -- add `anthropic`, `groq` branches in `create_llm_model()`, update strict-tool handling)
- `src/app/config/config_chat.json` (edit -- add 7 provider config entries, fix 2 live bugs, update 7 stale models)
- `src/run_cli.py` (edit -- add `choices=` to `--chat-provider` argument)
- `tests/llms/test_models.py` (edit -- test new provider branches)

---

#### Feature 4: Judge Auto Mode -- Conditional Settings Display

**Description**: When `tier2_provider` is set to `"auto"` in the GUI Settings page, the downstream Tier 2 LLM Judge controls (model, fallback provider, fallback model, fallback strategy, timeout) are still displayed. Since "auto" delegates provider selection to the runtime, these manual overrides are confusing and logically redundant. They should be hidden when "auto" is selected.

**Acceptance Criteria**:

- [ ] AC1: When `tier2_provider` is `"auto"`, the following controls are hidden: primary model selectbox, fallback provider, fallback model, fallback strategy
- [ ] AC2: When `tier2_provider` is changed from `"auto"` to a specific provider, the hidden controls reappear immediately
- [ ] AC3: Timeout and cost budget controls remain visible regardless of provider selection (they apply to all modes)
- [ ] AC4: Session state values for hidden controls retain their defaults (not cleared when hidden)
- [ ] AC5: `make validate` passes with no regressions

**Technical Requirements**:

- In `_render_tier2_llm_judge()` in `settings.py`, wrap the model/fallback controls in `if selected_provider != "auto":` conditional
- Keep `tier2_timeout_seconds` and `tier2_cost_budget_usd` outside the conditional -- they apply regardless
- Ensure `_build_judge_settings_from_session()` in `run_app.py` still constructs a valid `JudgeSettings` when auto is selected (fields use defaults from the model)

**Files**:

- `src/gui/pages/settings.py` (edit -- conditional display in `_render_tier2_llm_judge()`)
- `tests/test_gui/test_settings_judge_auto.py` (new -- verify controls hidden/shown based on provider selection)

---

#### Feature 5: PydanticAI API Migration -- `manager.run()`, `RunContext`, and Private Attribute Access

**Description**: `agent_system.py:543-551` uses the deprecated `manager.run()` PydanticAI API with 3 FIXME markers and broad `type: ignore` directives (`reportDeprecated`, `reportUnknownArgumentType`, `reportCallOverload`, `call-overload`). The `result.usage()` call also requires `type: ignore`. Additionally, `RunContext` may be deprecated in the installed PydanticAI version (Review F6), and `_model_name` private attribute access at `agent_system.py:537` should use the public `model_name` API (Review F23). Migrate all three patterns in one pass.

**Acceptance Criteria**:

- [ ] AC1: `manager.run()` replaced with current PydanticAI API (non-deprecated call)
- [ ] AC2: All `type: ignore` comments on lines 548 and 551 removed -- pyright passes cleanly
- [ ] AC3: All 3 FIXME comments (lines 543-544, 550) removed
- [ ] AC4: Agent execution produces identical results (same `execution_id`, same `result.output`)
- [ ] AC5: `RunContext` verified against installed PydanticAI version; updated to current name (e.g., `AgentRunContext`) if deprecated (Review F6)
- [ ] AC6: `_model_name` private attribute access replaced with public `model_name` API (Review F23)
- [ ] AC7: `make validate` passes with no new type errors or test failures

**Technical Requirements**:

- Research current PydanticAI `Agent.run()` signature and migrate `mgr_cfg` dict unpacking accordingly
- Verify `result.usage()` return type is properly typed after migration
- Verify `RunContext` deprecation status: `python -c "from pydantic_ai import RunContext; print(RunContext)"`. If deprecated, update all tool function signatures in `agent_system.py` and `peerread_tools.py`
- Replace `getattr(manager, "model")._model_name` with `getattr(manager, "model").model_name` (public attribute) with fallback to `"unknown"`
- Preserve `trace_collector` start/end calls and error handling structure
- Mock PydanticAI agent in tests -- never call real LLM providers

**Files**:

- `src/app/agents/agent_system.py` (edit -- lines 537-551, migrate `manager.run()`, fix `_model_name`, check `RunContext`)
- `src/app/tools/peerread_tools.py` (edit -- update `RunContext` import if deprecated)
- `tests/agents/test_agent_system.py` (edit -- update/add tests for migrated call)

---

#### Feature 6: Replace `inspect.getsource` Tests with Behavioral Tests

**Description**: Six test files use `inspect.getsource(module)` then assert string presence (e.g., `'engine != "cc"' in source`). This pattern breaks on code reformatting, passes if the string appears anywhere in source, and couples tests to implementation rather than behavior. Identified as a top-3 anti-pattern by prevalence in the tests parallel review (H5, H6, M14, M15 -- ~20 occurrences across 6 files).

**Acceptance Criteria**:

- [ ] AC1: `tests/utils/test_weave_optional.py` -- `inspect.getsource` replaced with behavioral test: import module with weave absent, verify `op()` is a callable no-op decorator (tests-review H5)
- [ ] AC2: `tests/gui/test_story012_a11y_fixes.py` -- all 11 `inspect.getsource` occurrences replaced with Streamlit mock-based assertions (tests-review H6)
- [ ] AC3: `tests/gui/test_story013_ux_fixes.py` -- source inspection replaced with behavioral widget assertions (tests-review H6)
- [ ] AC4: `tests/gui/test_story010_gui_report.py` -- 2 source inspections replaced with output assertions (tests-review H6)
- [ ] AC5: `tests/cli/test_cc_engine_wiring.py` -- 4 source inspections removed; behavioral tests already exist alongside (tests-review H6, M15)
- [ ] AC6: `tests/gui/test_prompts_integration.py` -- source file read + string assertion replaced with render function mock test (tests-review M14)
- [ ] AC7: Zero occurrences of `inspect.getsource` remain in `tests/` directory
- [ ] AC8: `make validate` passes with no regressions

**Technical Requirements**:

- Replace source-level string assertions with behavioral tests: call the function with relevant inputs and assert outputs
- For UI tests, verify widgets called via Streamlit mocks instead of inspecting source
- For CLI tests, remove redundant source inspections where behavioral `parse_args` tests already cover the logic
- Run `grep -r "inspect.getsource" tests/` to verify zero remaining occurrences

**Files**:

- `tests/utils/test_weave_optional.py` (edit)
- `tests/gui/test_story012_a11y_fixes.py` (edit)
- `tests/gui/test_story013_ux_fixes.py` (edit)
- `tests/gui/test_story010_gui_report.py` (edit)
- `tests/cli/test_cc_engine_wiring.py` (edit)
- `tests/gui/test_prompts_integration.py` (edit)

---

## Non-Functional Requirements

- Report generation latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies without PRD validation
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S10-F{N}: {why}`. Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

**Deferred from original Sprint 10 plan (not aligned with E2E parity goal):**

- GUI Sweep Page -- full sweep GUI with progress indicators, multi-select papers, composition toggles. `SweepRunner` hardcodes MAS-first ordering, doesn't support `engine` parameter, and sweep results shape differs from single-run session state format. Needs design work before implementation.
- GUI Layout Refactor -- sidebar tabs and page separation (cosmetic, not blocking E2E)
- Data Layer Robustness -- narrow exceptions + contradictory log (Review F9, F17)
- Dispatch Chain Registry Refactor in `datasets_peerread.py` (Review F10)
- `create_llm_model()` registry pattern refactor -- the if/elif chain is fine for 19 providers
- Provider health checks or connectivity validation
- `--judge-provider` CLI validation -- judge provider uses a separate settings model, not part of E2E parity
- CC-specific Tier 3 graph metrics (delegation fan-out, task completion rate, teammate utilization) -- MAS-specific metrics labeled "informational" for CC runs is sufficient for Sprint 10

**Deferred test review findings (MEDIUM/LOW from tests-parallel-review-2026-02-21.md):**

- `assert isinstance()` replacements with behavioral assertions (H4, M1-M3) -- ~30+ occurrences across 12 files
- Subdirectory `conftest.py` creation for `tests/agents/`, `tests/tools/`, `tests/evals/`, `tests/judge/` (M5, M6)
- `@pytest.mark.parametrize` additions for provider tests and recommendation tests (M7, M8)
- `hasattr()` replacements with behavioral tests (M4)
- Weak assertion strengthening in `test_suggestion_engine.py` and `test_report_generator.py` (M18, L5)
- Hardcoded relative path fix in `test_peerread_tools_error_handling.py` (H8)
- `tempfile` -> `tmp_path` in integration tests (L7, L8)
- `@pytest.mark.slow` markers on performance baselines (L10)

**Deferred to future sprint (TBD acceptance criteria, low urgency):**

- Centralized Tool Registry with Module Allowlist (MAESTRO L7.2) -- architectural, needs design
- Plugin Tier Validation at Registration (MAESTRO L7.1) -- architectural, needs design
- Error Message Sanitization (MAESTRO) -- TBD acceptance criteria
- Configuration Path Traversal Protection (MAESTRO) -- TBD acceptance criteria
- GraphTraceData Construction Simplification (`model_validate()`) -- TBD acceptance criteria
- Timeout Bounds Enforcement -- low urgency
- Hardcoded Settings Audit -- continuation of Sprint 7
- Time Tracking Consistency Across Tiers -- low urgency
- BDD Scenario Tests for Evaluation Pipeline -- useful but not blocking
- Tier 1 Reference Comparison Fix -- requires ground-truth review integration
- Cerebras Structured Output Validation Retries -- provider-specific edge case
- PlantUML Diagram Audit -- cosmetic, no user impact

---

## Notes for Ralph Loop

### Priority Order

- **P1 (E2E parity)**: STORY-010 (CC engine GUI), STORY-011 (graph visualization)
- **P2 (infrastructure)**: STORY-012 (providers), STORY-013 (judge auto UX)
- **P3 (code health)**: STORY-014 (PydanticAI migration), STORY-015 (source inspection tests)

### Notes for CC Agent Teams

- **Team Structure**: Lead + 2 teammates max
- **Delegate Mode**: Recommended -- lead coordinates, teammates implement

#### File-Conflict Dependencies

Stories sharing files need `blockedBy` deps beyond logical `depends_on`.

| Story | Logical Dep | + File-Conflict Dep | Shared File | Reason |
| --- | --- | --- | --- | --- |
| STORY-011 | STORY-010 | -- | `run_app.py`, `cc_engine.py` | Graph viz wires into CC branch added by F1 |
| STORY-014 | STORY-010 | + STORY-012 | `models.py` (via `agent_system.py` provider usage) | PydanticAI migration touches agent_system.py which imports from models.py; provider changes in STORY-012 must land first |

#### Orchestration Waves

```text
Wave 1 (independent, no file conflicts):
  teammate-1: STORY-012 (F3 providers) then STORY-013 (F4 judge auto)
  teammate-2: STORY-010 (F1 CC engine GUI) then STORY-015 (F6 source inspection)

Wave 2 (after Wave 1 completes):
  teammate-1: STORY-011 (F2 graph viz, depends: STORY-010)
  teammate-2: STORY-014 (F5 PydanticAI, depends: STORY-010, STORY-012)
```

- **Quality Gates**: Teammate runs `make quick_validate`; lead runs `make validate` after each wave
- **Teammate Prompt Template**: Sprint 8 pattern with TDD `[RED]`/`[GREEN]` commit markers

Story Breakdown - Phase 1 (6 stories total):

- **Feature 1** -> STORY-010: Wire CC engine to GUI execution path (solo + teams)
  Add CC engine branch in `_execute_query_background()` mirroring CLI logic. Add CC teams checkbox. Fix `run_cc_teams` timeout with process group kill. Define CCResultDict shape. Wrap CC raw text into `GeneratedReview` structure so all three evaluation tiers work. Wire evaluation page with CC banner. Files: `src/gui/pages/run_app.py`, `src/app/engines/cc_engine.py`, `src/gui/pages/evaluation_results.py`, `tests/test_gui/test_session_state_wiring.py`.

- **Feature 2** -> STORY-011: Graph building and visualization for all execution modes (depends: STORY-010)
  Convert CC artifacts to `GraphTraceData` -> `nx.DiGraph`. Single-agent runs (MAS solo or CC solo): tool-call chain graph. Multi-agent runs (MAS 4-agent or CC teams): tool calls + team delegation + inter-agent edges. Differentiate empty vs missing graphs. Label CC Tier 3 metrics as "informational." Files: `src/app/engines/cc_engine.py`, `src/gui/pages/run_app.py`, `src/gui/pages/agent_graph.py`, `tests/test_gui/test_agent_graph.py`.

- **Feature 3** -> STORY-012: Expand inference provider registry and update stale models
  Add 7 new providers (Groq, Fireworks, DeepSeek, Mistral, SambaNova, Nebius, Cohere). Fix 2 live bugs (huggingface classification model, together removed free model). Update 7 stale model IDs. Set `max_content_length` to free-tier token limits. Fix Anthropic to use native PydanticAI model. See `docs/analysis/Inference-Providers.md`. Files: `src/app/data_models/app_models.py`, `src/app/llms/models.py`, `src/app/config/config_chat.json`, `src/run_cli.py`, `tests/llms/test_models.py`.

- **Feature 4** -> STORY-013: Judge auto mode -- conditional settings display
  Hide downstream Tier 2 controls when provider is "auto". Files: `src/gui/pages/settings.py`, `tests/test_gui/test_settings_judge_auto.py`.

- **Feature 5** -> STORY-014: PydanticAI API migration (depends: STORY-010, STORY-012)
  Migrate `manager.run()`, fix `RunContext`, replace `_model_name`. Files: `src/app/agents/agent_system.py`, `src/app/tools/peerread_tools.py`, `tests/agents/test_agent_system.py`.

- **Feature 6** -> STORY-015: Replace inspect.getsource tests with behavioral tests
  Rewrite ~20 `inspect.getsource` assertions across 6 test files. Files: `tests/utils/test_weave_optional.py`, `tests/gui/test_story012_a11y_fixes.py`, `tests/gui/test_story013_ux_fixes.py`, `tests/gui/test_story010_gui_report.py`, `tests/cli/test_cc_engine_wiring.py`, `tests/gui/test_prompts_integration.py`.
