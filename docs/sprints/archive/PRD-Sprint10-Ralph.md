---
title: Product Requirements Document - Agents-eval Sprint 10
description: "Sprint 10: 6 features — E2E CLI/GUI parity for CC engine (solo + teams), graph visualization for all modes, expanded providers, judge UX, PydanticAI migration, test quality."
version: 3.1.0
created: 2026-02-21
updated: 2026-02-22
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager -> Researcher -> Analyst -> Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

**Sprint 10 goal**: E2E parity between CLI and GUI for all execution modes. The CC engine (solo + teams) works from CLI but is broken in the GUI — `app.main()` ignores the `engine` parameter and always runs MAS. Graphs must build and visualize for all modes including CC. Provider coverage is expanded with 7 new inference providers. Judge settings UX is improved, PydanticAI deprecated APIs are migrated, and `inspect.getsource` test anti-patterns are replaced.

### Current State

| Mode | CLI | GUI | Gap |
| --- | --- | --- | --- |
| Free-text query (MAS) | Works | Works | None |
| Paper review (MAS) | Works (`--paper-id`) | Works (dropdown) | None |
| CC solo | **Broken** — `args.pop("engine")` removes it before `main()`, MAS always runs after CC | Radio exists, but `app.main()` ignores `engine` — runs MAS | **Broken (both)** |
| CC teams | **Broken** — same CLI bug as solo | No toggle exists | **Broken + Missing** |
| Graph visualization | N/A (CLI) | Works for MAS; CC produces no graph data | **Partial** |
| CC evaluation | Pipeline is engine-agnostic (plain strings), but CC review text discarded (`_RESULT_KEYS` omits `"result"`) | Not wired | **No path** |
| Reference reviews | `reference_reviews=None` for ALL modes (MAS included) — Tier 1 scores against empty | Same | **Bug (all modes)** |

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

#### Feature 1: Connect All Execution Modes to the Same Three-Tier Evaluation Pipeline

**Description**: All execution modes (MAS, CC solo, CC teams) must produce comparable evaluation results through the same `evaluate_comprehensive()` call. The evaluation pipeline interface is already engine-agnostic — all three tiers operate on plain strings and dicts, not MAS types:

```
evaluate_comprehensive(
    paper: str,                    # Tier 1 + Tier 2
    review: str,                   # Tier 1 + Tier 2
    execution_trace: GraphTraceData | dict | None,  # Tier 2 (dict) + Tier 3 (GraphTraceData)
    reference_reviews: list[str] | None,            # Tier 1
) -> CompositeResult
```

No `GeneratedReview` wrapping needed — the pipeline already accepts plain strings. The work is building an adapter layer that translates each mode's output into these 4 parameters, plus fixing 4 bugs discovered during analysis:

| Bug | Location | Impact |
| --- | --- | --- |
| CLI `engine` pop | `run_cli.py:107` — `args.pop("engine")` removes engine before `main()` | MAS always runs after CC |
| `main()` ignores engine | `app.py:228` — logs value, unconditionally calls `_run_agent_execution()` | CC engine has no effect |
| CC review text discarded | `cc_engine.py:85` — `_RESULT_KEYS` omits `"result"` | CC response text lost |
| Reference reviews never loaded | `evaluation_runner.py:154` — `reference_reviews=None` for ALL modes | Tier 1 scores empty strings |

**Acceptance Criteria**:

- [ ] AC1: `evaluate_comprehensive()` is the sole evaluation entry point for MAS, CC solo, and CC teams — no mode-specific evaluation logic exists outside it
- [ ] AC2: CC solo and CC teams produce non-empty `review` text passed to the pipeline (extracted from `CCResult.output_data["result"]`)
- [ ] AC3: All modes load `reference_reviews` from PeerRead when `paper_id` is set — Tier 1 scores against actual ground truth, not empty strings
- [ ] AC4: CC solo produces a `GraphTraceData` (minimal or from `CCTraceAdapter`); composite scorer detects `single_agent_mode=True` and redistributes `coordination_quality` weight
- [ ] AC5: CC teams produces a `GraphTraceData` with `agent_interactions` mapped from `team_artifacts` Task events
- [ ] AC6: `run_cc_teams` uses process group kill (`os.killpg`) after timeout — not just `proc.kill()` — to clean up teammate child processes
- [ ] AC7: `CompositeResult.engine_type` is set to `"mas"`, `"cc_solo"`, or `"cc_teams"` for all results
- [ ] AC8: CLI `--engine=cc` does NOT run the MAS pipeline — `_run_agent_execution()` is not called
- [ ] AC9: GUI "Claude Code" radio invokes CC engine, not MAS; a "CC Teams" checkbox appears when CC is selected
- [ ] AC10: For the same `paper_id`, MAS and CC Tier 1 scores use identical `reference_reviews` (same ground truth)
- [ ] AC11: All existing MAS tests continue to pass; new tests cover the CC path (solo and teams)
- [ ] AC12: `make validate` passes with no regressions

**Technical Requirements**:

- **Capture CC review text**: Add `"result"` to `_RESULT_KEYS` in `cc_engine.py:85` so `cc_result.output_data["result"]` contains the review text. Add `extract_cc_review_text(cc_result) -> str` helper
- **Build `GraphTraceData` from CC artifacts**: Add `cc_result_to_graph_trace(cc_result) -> GraphTraceData` that maps `team_artifacts` Task/TeamCreate events to `agent_interactions`, `tool_calls`, and `coordination_events`. CC solo: minimal `GraphTraceData(execution_id=cc_result.execution_id)` with empty lists — `CompositeScorer._detect_single_agent_mode()` already redistributes `coordination_quality` weight. CC teams: `Task.owner` -> delegation interactions, completed tasks -> `tool_calls`, `TeamCreate` -> `coordination_events`
- **Load reference reviews for all modes**: In `evaluation_runner.py`, before `evaluate_comprehensive()`, load from PeerRead: `paper.reviews[*].comments` when `paper_id` is set. This fixes the existing bug for ALL modes (MAS included)
- **Add `engine_type` to `CompositeResult`**: `engine_type: str = Field(default="mas")` — enables downstream consumers to know the source engine. Backward-compatible default
- **Wire `main()` to branch on engine**: Add `cc_result: CCResult | None = None` param. When `engine == "cc"`: skip `_run_agent_execution()` entirely, extract review text via `extract_cc_review_text()`, build `GraphTraceData` via `cc_result_to_graph_trace()`, load paper content + reference reviews from PeerRead, call `evaluate_comprehensive()` with same 4 parameters as MAS, build `nx.DiGraph` via `build_interaction_graph()`
- **Fix CLI wiring**: Pass `engine` and `cc_result` explicitly to `main()`: `run(main(**args, engine=engine, cc_result=cc_result))`. Remove pattern where CC runs first then MAS runs anyway
- **Fix GUI wiring**: In `_execute_query_background()`, add CC branch that calls `run_cc_solo()` / `run_cc_teams()` before calling `main()` with `cc_result`. Add CC teams checkbox visible when engine is CC
- **Fix `run_cc_teams` timeout**: Use `start_new_session=True` + `os.killpg(os.getpgid(proc.pid), signal.SIGTERM)` then `proc.kill()` to clean up teammate child processes
- Mock `subprocess.run` and `subprocess.Popen` in tests — never call real `claude` CLI

**Comparability Matrix**:

| Metric | Tier | MAS vs CC | Rationale |
| --- | --- | --- | --- |
| `output_similarity` | 1 | **Comparable** | Same review text vs same references |
| `task_success` | 1 | **Comparable** | Same threshold on same similarity scores |
| `time_taken` | 1 | **Comparable** | Wall-clock time for both |
| `technical_accuracy` | 2 | **Comparable** | LLM judges review text quality |
| `constructiveness` | 2 | **Comparable** | LLM judges review text quality |
| `planning_rationality` | 2 | **Partial** | CC has sparse trace -> less signal |
| `coordination_centrality` | 3 | **Not comparable** | MAS: rich delegation graph; CC solo: empty; CC teams: flat |
| `tool_selection_accuracy` | 3 | **Partial** | CC teams: task completions as proxy |
| `path_convergence` | 3 | **Not comparable** | Structurally different graphs |
| `task_distribution_balance` | 3 | **Partial** | CC teams has distribution data |

Tier 1 + Tier 2 (review quality) are directly comparable. Tier 3 (graph/coordination) is structurally different but still computed — the composite scorer handles this via `single_agent_mode` weight redistribution for CC solo.

**Files**:

- `src/app/engines/cc_engine.py` (edit -- add `"result"` to `_RESULT_KEYS`, add `extract_cc_review_text()`, add `cc_result_to_graph_trace()`, fix `run_cc_teams` process group kill)
- `src/app/data_models/evaluation_models.py` (edit -- add `engine_type` field to `CompositeResult`)
- `src/app/judge/evaluation_runner.py` (edit -- load reference reviews from PeerRead for all modes, accept `cc_result`/`engine_type` params, CC adapter branch)
- `src/app/app.py` (edit -- add `cc_result` param to `main()`, CC engine branch that skips `_run_agent_execution()`)
- `src/run_cli.py` (edit -- pass `engine=engine, cc_result=cc_result` to `main()`, remove MAS-after-CC pattern)
- `src/gui/pages/run_app.py` (edit -- CC branch in `_execute_query_background()`, add CC teams checkbox)
- `tests/engines/test_cc_engine.py` (edit -- tests for `extract_cc_review_text`, `cc_result_to_graph_trace`, `"result"` in `_RESULT_KEYS`)
- `tests/cli/test_cc_engine_wiring.py` (edit -- test CLI passes `engine`+`cc_result` to main, CC does not invoke MAS)
- `tests/judge/test_evaluation_runner.py` (edit -- test reference reviews loaded for all modes, CC result adapter path)

---

#### Feature 2: Graph Visualization Polish for All Execution Modes

**Description**: Feature 1 builds `GraphTraceData` and `nx.DiGraph` for CC runs. This feature handles the visualization layer: the Agent Graph page must distinguish between no-execution-yet, empty graph (CC solo), and populated graph (MAS or CC teams). CC Tier 3 graph metrics need "informational" labeling since they aren't comparable to MAS scores. `CCResult.team_artifacts` already retains parsed events from the JSONL stream (per `cc_engine.py:111-112`).

**Acceptance Criteria**:

- [ ] AC1: CC solo produces an `nx.DiGraph` (may be minimal — single node) displayed on Agent Graph page
- [ ] AC2: CC teams produces an `nx.DiGraph` showing team member nodes and delegation edges
- [ ] AC3: Empty graphs (0 nodes, 0 edges) display a descriptive warning (e.g., "CC solo mode — no agent interactions to display") instead of generic "No agent interaction data available"
- [ ] AC4: MAS graph visualization continues to work unchanged
- [ ] AC5: Tier 3 graph metrics from CC runs are labeled "informational — not comparable to MAS scores" in evaluation display
- [ ] AC6: `make validate` passes with no regressions

**Technical Requirements**:

- In `agent_graph.py`: distinguish between `graph is None` (no execution yet), empty graph (execution produced no interactions — show mode-specific message using `CompositeResult.engine_type`), and populated graph
- For Tier 3 metrics on CC runs: when `engine_type` starts with `"cc"`, prefix metric labels with "Informational" in evaluation display
- Graph building itself is handled by Feature 1 (`cc_result_to_graph_trace()` + `build_interaction_graph()`)

**Files**:

- `src/gui/pages/agent_graph.py` (edit -- differentiate empty vs missing graph messages, CC graph labeling)
- `src/gui/pages/evaluation_results.py` (edit -- CC-specific Tier 3 labeling when `engine_type` is CC)
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
- Cerebras Structured Output Validation Retries -- provider-specific edge case
- PlantUML Diagram Audit -- cosmetic, no user impact

---

## Notes for Ralph Loop

### Priority Order

- **P1 (E2E parity)**: STORY-010 (CC eval pipeline parity — biggest story, most files), STORY-011 (graph viz polish)
- **P2 (infrastructure)**: STORY-012 (providers), STORY-013 (judge auto UX)
- **P3 (code health)**: STORY-014 (PydanticAI migration), STORY-015 (source inspection tests)

### Running Ralph in CC Agent Teams Mode

Ralph supports CC Agent Teams for inter-story parallelism. Use this when multiple stories can run concurrently (different files, no conflicts).

```bash
# Teams mode: lead coordinates, 2 teammates implement in parallel
make ralph_run TEAMS=true MAX_ITERATIONS=12 MODEL=opus

# Worktree + teams (isolated branch):
make ralph_run_worktree BRANCH=ralph/sprint10-e2e-parity TEAMS=true MAX_ITERATIONS=12
```

**How teams mode works in Ralph** (see [CC-agent-teams-orchestration.md](../analysis/CC-agent-teams-orchestration.md)):

- Sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` automatically when `TEAMS=true`
- Lead picks primary story, delegates wave peers to teammates via the shared task list
- Teammates implement in parallel; each runs `make quick_validate` on their story's files
- Lead runs `make validate` at wave boundaries before advancing to next wave
- Scoped lint/tests in teams mode: only story-specific files are checked per teammate
- Wave boundary detection: when primary story passes, Ralph checks if next story is in a new wave

**Key limitations** (from orchestration analysis):

- No session resumption — if Ralph times out, restart from scratch
- Task status can lag — teammates sometimes don't mark tasks complete, blocking dependents
- Linear token cost — each teammate is a separate Claude instance (~3x cost for 2 teammates)
- Cross-story interference possible in teams mode — scoped validation mitigates but doesn't eliminate

**Recommendation for Sprint 10**: Use `TEAMS=true` for Wave 1 (STORY-010 + STORY-012 are independent). Run Wave 2 sequentially — both stories depend on Wave 1 and share indirect file conflicts.

### Notes for CC Agent Teams

- **Team Structure**: Lead + 2 teammates max
- **Delegate Mode**: Recommended -- lead coordinates, teammates implement

#### File-Conflict Dependencies

Stories sharing files need `blockedBy` deps beyond logical `depends_on`.

| Story | Logical Dep | + File-Conflict Dep | Shared File | Reason |
| --- | --- | --- | --- | --- |
| STORY-011 | STORY-010 | -- | `cc_engine.py`, `evaluation_runner.py` | Graph viz polish uses `cc_result_to_graph_trace()` added by F1 |
| STORY-014 | STORY-010 | + STORY-012 | `models.py` (via `agent_system.py` provider usage) | PydanticAI migration touches agent_system.py which imports from models.py; provider changes in STORY-012 must land first |

#### Orchestration Waves

```text
Wave 1 (independent, no file conflicts):
  teammate-1: STORY-012 (F3 providers) then STORY-013 (F4 judge auto)
  teammate-2: STORY-010 (F1 CC eval pipeline parity) — largest story, give full wave

Wave 2 (after Wave 1 completes):
  teammate-1: STORY-011 (F2 graph viz polish, depends: STORY-010) then STORY-015 (F6 source inspection)
  teammate-2: STORY-014 (F5 PydanticAI migration, depends: STORY-010, STORY-012)
```

- **Quality Gates**: Teammate runs `make quick_validate`; lead runs `make validate` after each wave
- **Teammate Prompt Template**: Sprint 8 pattern with TDD `[RED]`/`[GREEN]` commit markers

Story Breakdown - Phase 1 (6 stories total):

- **Feature 1** → STORY-010: Connect all execution modes to the same three-tier evaluation pipeline
  Fix 4 bugs (CLI engine pop, main() ignores engine, CC review text discarded, reference reviews never loaded). Add adapter layer: `extract_cc_review_text()`, `cc_result_to_graph_trace()` in cc_engine.py. Add `engine_type` to CompositeResult. Wire `main()` CC branch (skip MAS, pass cc_result). Fix CLI to pass `engine+cc_result` to main(). Fix GUI to run CC before main(). Load reference reviews from PeerRead for all modes. Files: `src/app/engines/cc_engine.py`, `src/app/data_models/evaluation_models.py`, `src/app/judge/evaluation_runner.py`, `src/app/app.py`, `src/run_cli.py`, `src/gui/pages/run_app.py`, `tests/engines/test_cc_engine.py`, `tests/cli/test_cc_engine_wiring.py`, `tests/judge/test_evaluation_runner.py`.

- **Feature 2** → STORY-011: Graph visualization polish for all execution modes (depends: STORY-010)
  Handle empty vs missing graphs on Agent Graph page. Label CC Tier 3 metrics as "informational." Graph building itself is done by Feature 1. Files: `src/gui/pages/agent_graph.py`, `src/gui/pages/evaluation_results.py`, `tests/test_gui/test_agent_graph.py`.

- **Feature 3** → STORY-012: Expand inference provider registry and update stale models
  Add 7 new providers (Groq, Fireworks, DeepSeek, Mistral, SambaNova, Nebius, Cohere). Fix 2 live bugs (huggingface classification model, together removed free model). Update 7 stale model IDs. Set `max_content_length` to free-tier token limits. Fix Anthropic to use native PydanticAI model. See `docs/analysis/Inference-Providers.md`. Files: `src/app/data_models/app_models.py`, `src/app/llms/models.py`, `src/app/config/config_chat.json`, `src/run_cli.py`, `tests/llms/test_models.py`.

- **Feature 4** → STORY-013: Judge auto mode -- conditional settings display
  Hide downstream Tier 2 controls when provider is "auto". Files: `src/gui/pages/settings.py`, `tests/test_gui/test_settings_judge_auto.py`.

- **Feature 5** → STORY-014: PydanticAI API migration (depends: STORY-010, STORY-012)
  Migrate `manager.run()`, fix `RunContext`, replace `_model_name`. Files: `src/app/agents/agent_system.py`, `src/app/tools/peerread_tools.py`, `tests/agents/test_agent_system.py`.

- **Feature 6** → STORY-015: Replace inspect.getsource tests with behavioral tests
  Rewrite ~20 `inspect.getsource` assertions across 6 test files. Files: `tests/utils/test_weave_optional.py`, `tests/gui/test_story012_a11y_fixes.py`, `tests/gui/test_story013_ux_fixes.py`, `tests/gui/test_story010_gui_report.py`, `tests/cli/test_cc_engine_wiring.py`, `tests/gui/test_prompts_integration.py`.
