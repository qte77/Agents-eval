---
title: Product Requirements Document - Agents-eval Sprint 8
description: "Fix sweep-crashing tool bug (F1), remove API key sentinel + judge auto-mode model inheritance (F2), consolidate CC engine with teams support (F3), graph attribute alignment (F4), streaming dead code removal (F5), report generation with suggestion engine (F6), judge settings dropdowns (F7), GUI a11y/UX/environment fixes (F8). 14 stories."
version: 1.1.0
created: 2026-02-17
updated: 2026-02-18
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

**Sprint 8 Focus (8 features, 14 stories)**:

1. Fix sweep-crashing `read_paper_pdf_tool` → `get_paper_content` with parsed JSON fallback chain
2. Remove `"not-required"` API key sentinel (5 call sites) + fix judge auto-mode model inheritance
3. Consolidate CC engine into `cc_engine.py` with solo + teams support, retire shell scripts
4. Align graph node attribute (`type` vs `node_type` mismatch)
5. Remove dead `pydantic_ai_stream` parameter (upstream still unsupported)
6. Report generation: CLI `--generate-report`, GUI button, rule-based suggestion engine with optional LLM
7. Replace judge settings free-text inputs with populated dropdowns
8. GUI standalone fixes: WCAG a11y, App/Evaluation page UX, environment-aware URL resolution

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
- **Test behavior, not implementation** — test observable outcomes (return values, side effects, error messages), not internal structure.
- **Google-style docstrings** for every new file, function, class, and method.
- **`# Reason:` comments** for non-obvious logic.
- **`make validate` MUST pass** before any story is marked complete. No exceptions.

### Skills Usage

| Story type | Skills to invoke |
|------------|-----------------|
| Implementation (all features) | `testing-python` (RED) → `implementing-python` (GREEN) |
| Codebase research | `researching-codebase` (before non-trivial implementation) |
| Design phase (Feature 6) | `researching-codebase` → `designing-backend` |

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Replace `read_paper_pdf_tool` with `get_paper_content` Using Parsed JSON Fallback Chain

**Description**: `read_paper_pdf_tool` is exposed directly to the LLM and requires a local filesystem path as input. The LLM has no way to discover valid paths, leading to hallucinated URLs (e.g., `https://arxiv.org/pdf/1105.1072`) that crash the agent with `FileNotFoundError`. The correct content-loading logic already exists internally in `_load_paper_content_with_fallback()` (parsed JSON → raw PDF → abstract), but it's private — only called from `generate_paper_review_content_from_template`. Meanwhile, `get_peerread_paper` returns only title/abstract/reviews, no body text, so the LLM naturally reaches for `read_paper_pdf_tool` to get full paper content.

**Root cause**: The LLM needs full paper content but only has a raw-PDF-by-path tool with no way to supply a valid path. The parsed JSON data (primary content source) is not accessible via any tool.

**Acceptance Criteria**:
- [ ] `read_paper_pdf_tool` removed from agent tool registration (no longer LLM-callable)
- [ ] New tool `get_paper_content(paper_id: str) -> str` registered on the same agent (researcher or manager)
- [ ] `get_paper_content` internally calls `_load_paper_content_with_fallback()` fallback chain: parsed JSON → raw PDF → abstract
- [ ] Tool docstring clearly states: returns full paper text from local PeerRead dataset, requires `paper_id` (not a file path or URL)
- [ ] `read_paper_pdf()` function retained as internal helper (used by fallback chain), just not exposed as a tool
- [ ] `read_paper_pdf()` rejects URLs with a descriptive return instead of `FileNotFoundError` (defensive guard)
- [ ] Sweep with `--paper-id=1105.1072` no longer crashes with `FileNotFoundError`
- [ ] TDD: RED tests first (`tests/tools/test_peerread_tools.py`) covering `get_paper_content` happy path, URL rejection guard, fallback chain. GREEN: implement tool replacement. REFACTOR: remove dead `read_paper_pdf_tool` registration. Use `testing-python` skill.
- [ ] `make validate` passes

**Technical Requirements**:
- Remove `@agent.tool` decorator from `read_paper_pdf_tool` in `add_peerread_tools_to_agent()`
- Add new `@agent.tool get_paper_content(ctx, paper_id)` that instantiates `PeerReadLoader`, calls `_load_paper_content_with_fallback(ctx, loader, paper_id, abstract)` where `abstract` is obtained from `loader.get_paper_by_id(paper_id).abstract`
- Add URL guard in `read_paper_pdf()`: if `pdf_path` starts with `http`, return error string instead of raising
- `_load_paper_content_with_fallback` already handles all three tiers — no changes needed there
- Update tool trace logging (`trace_collector.log_tool_call`) for the new tool name

**Files**:
- `src/app/tools/peerread_tools.py` (edit — replace `read_paper_pdf_tool` with `get_paper_content`, add URL guard)
- `tests/tools/test_peerread_tools.py` (edit — update tool registration tests, add `get_paper_content` test)

---

#### Feature 2: Remove `"not-required"` Fallback Key + Fix Judge Auto-Mode Model Inheritance

**Description**: Three related issues in API key and model resolution:

1. **`"not-required"` fallback key in `create_llm_model()`** (`src/app/llms/models.py`): Uses `api_key or "not-required"` at 5 call sites (lines 78, 87, 98, 119, 128). When `api_key` is `None`, the expression evaluates to the string `"not-required"`, which the OpenAI SDK sends as a real API key — resulting in 401. It also prevents the SDK's built-in env var fallback (`OPENAI_API_KEY`, etc.), because the SDK only checks env vars when `api_key` is `None`. Sprint 8 commit `9e14931` fixed this in `create_simple_model()` (judge path). The same fix is needed in `create_llm_model()` for the main agent creation path.

2. **Auto-mode inherits provider but not model** (`src/app/judge/llm_evaluation_managers.py:58-66`): `LLMJudgeEngine.__init__()` accepts `chat_provider` but has no `chat_model` parameter. When `tier2_provider="auto"`, the constructor sets `self.provider = chat_provider` (line 60) but `self.model` always stays `settings.tier2_model` (line 66), which defaults to `"gpt-4o-mini"` (`src/app/judge/settings.py:75`). If the chat provider is cerebras with model `llama-4-scout-17b-16e-instruct`, the judge would use the combination `cerebras/gpt-4o-mini` — a model that doesn't exist on Cerebras, causing a 404 and unnecessary fallback. This is a design gap in the engine, not a test bug: auto-mode needs `chat_model` passed alongside `chat_provider` to inherit the correct model.

3. **Cross-provider key mismatch untested** (`tests/judge/test_llm_evaluation_managers.py`): Three existing auto-mode tests all seed the env with the *same* provider's key, so a cross-provider mismatch (e.g., `chat_provider="cerebras"` with only `GITHUB_API_KEY` set) never surfaces. The fallback chain works correctly but this path is never exercised.

**Note**: Line 70 (`ollama` provider) legitimately uses `"not-required"` as a literal — Ollama doesn't need auth. This should remain hardcoded.

**Acceptance Criteria**:
- [ ] `create_llm_model()` passes `api_key` directly to `OpenAIProvider` for all providers except `ollama` (5 sites: lines 78, 87, 98, 119, 128)
- [ ] Ollama provider retains `api_key="not-required"` (no auth needed)
- [ ] When `api_key=None`, OpenAI SDK falls back to `OPENAI_API_KEY` env var (verified by test)
- [ ] `LLMJudgeEngine.__init__` accepts `chat_model: str | None` parameter alongside `chat_provider`
- [ ] When `tier2_provider="auto"` and `chat_model` is provided, `self.model` inherits `chat_model` (not hardcoded `tier2_model`)
- [ ] When `tier2_provider="auto"` and `chat_model` is `None`, `self.model` falls back to `tier2_model` (current behavior preserved)
- [ ] Cross-provider mismatch test: `chat_provider="cerebras"` with only `GITHUB_API_KEY` set → engine falls back to github provider and github-compatible model
- [ ] `EvaluationPipeline` passes `chat_model` through to `LLMJudgeEngine` (caller must supply it)
- [ ] Existing tests pass — no behavioral change when API key is provided explicitly
- [ ] TDD: RED tests first covering sentinel removal (`api_key=None` → `OpenAIProvider(api_key=None)`), model inheritance (`chat_model` pass-through), cross-provider fallback. GREEN: implement fixes. REFACTOR: simplify any redundant provider resolution logic. Use `testing-python` skill.
- [ ] `make validate` passes

**Technical Requirements**:
- Replace `api_key=api_key or "not-required"` with `api_key=api_key` at 5 call sites in `create_llm_model()`
- Add `chat_model: str | None = None` parameter to `LLMJudgeEngine.__init__`; when `resolved_provider != settings.tier2_provider` and `chat_model` is provided, set `self.model = chat_model`
- Update `EvaluationPipeline.__init__` to accept and forward `chat_model`
- Add test: `create_llm_model(provider="openai", ..., api_key=None)` results in `OpenAIProvider(api_key=None)`, not `"not-required"`
- Add test: `LLMJudgeEngine(settings, chat_provider="cerebras", chat_model="llama-4-scout-17b-16e-instruct")` → `engine.model == "llama-4-scout-17b-16e-instruct"`
- Add test: `chat_provider="cerebras"` with only `GITHUB_API_KEY` → falls back to github with `tier2_fallback_model`
- Existing auto-mode tests to verify still pass (all seed same-provider keys): `test_tier2_provider_auto_inherits_from_chat_provider` (line 427), `test_auto_mode_inherits_chat_provider_correctly` (line 746), `test_auto_mode_inherits_chat_provider` (line 684, Hypothesis)

**Files**:
- `src/app/llms/models.py` (edit — 5 lines, sentinel removal)
- `src/app/judge/llm_evaluation_managers.py` (edit — add `chat_model` parameter, inherit model in auto-mode)
- `src/app/judge/evaluation_pipeline.py` (edit — forward `chat_model` to `LLMJudgeEngine`)
- `tests/llms/test_models.py` (edit — add sentinel removal test)
- `tests/judge/test_llm_evaluation_managers.py` (edit — add model inheritance and cross-provider tests)

---

#### Feature 3: Consolidate CC Engine into `src/app/engines/cc_engine.py` with Teams Support

**Description**: CC (Claude Code) engine logic is duplicated across 4 locations with inconsistent error handling and incomplete wiring. Solo mode only — no teams orchestration path. Shell scripts duplicate logic that should live in Python.

**Critical constraint**: CC teams artifacts (`~/.claude/teams/`, `~/.claude/tasks/`) are ephemeral in `claude -p` print mode — cleaned up after exit (see AGENT_LEARNINGS.md). The Python implementation uses `--output-format stream-json` with `Popen` to parse team events from the live stream, eliminating filesystem artifact collection.

**Current state:**
- `run_cli.py:108-126` — inline `subprocess.run()`, solo only
- `sweep_runner.py:143-185` — duplicate `subprocess.run()`, solo only, stub baseline loop
- `run_app.py:481-532` — engine selector UI, `engine` param silently dropped
- `scripts/collect-cc-traces/` — 3 shell scripts (run-cc.sh, collect-team-artifacts.sh, lib/collect-common.sh) duplicating Python-target logic
- `cc_trace_adapter.py` — artifact parser, only called from `evaluation_runner.py` (not from subprocess paths)

##### 3.1 Core CC Engine Module

**Acceptance Criteria**:
- [ ] New module `src/app/engines/cc_engine.py` created
- [ ] `check_cc_available() -> bool` — `shutil.which("claude")` (replaces 3 inline checks)
- [ ] `run_cc_solo(query: str, timeout: int = 600) -> CCResult` — solo subprocess with `--output-format json`
- [ ] `run_cc_teams(query: str, timeout: int = 600) -> CCResult` — teams subprocess with `--output-format stream-json` + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env var, parses team events from live stream via `Popen`
- [ ] `CCResult` Pydantic model: `execution_id`, `output_data`, `session_dir` (solo), `team_artifacts` (teams: parsed from stream events)
- [ ] `parse_stream_json(stream) -> CCResult` — JSONL line parser extracting `init`, `result`, `TeamCreate`, `Task` events
- [ ] `src/app/engines/__init__.py` created
- [ ] TDD: RED tests first (`tests/engines/test_cc_engine.py`) covering `run_cc_solo`, `run_cc_teams`, `parse_stream_json`, `check_cc_available` with mocked `subprocess`. GREEN: implement `cc_engine.py`. Use `testing-python` skill.
- [ ] `make validate` passes

**Files**:
- `src/app/engines/__init__.py` (new)
- `src/app/engines/cc_engine.py` (new — consolidated CC logic, solo + teams)
- `tests/engines/test_cc_engine.py` (new — TDD RED: subprocess mock tests)

##### 3.2 CLI/Sweep/GUI Integration

**Acceptance Criteria**:
- [ ] `--cc-teams` boolean flag added to CLI (`run_cli.py`), sweep (`run_sweep.py`), and GUI (`run_app.py`)
- [ ] `--engine=cc` without `--cc-teams`: calls `run_cc_solo()` (current behavior, consolidated)
- [ ] `--engine=cc --cc-teams`: calls `run_cc_teams()` with teams env var and stream-json parsing
- [ ] `run_cli.py` CC branch delegates to `cc_engine` — no inline subprocess code
- [ ] `sweep_runner.py._invoke_cc_comparison()` delegates to `cc_engine` — no inline subprocess code
- [ ] `run_app.py._execute_query_background()` passes `engine` to `main()` when `engine == "cc"` (currently silently dropped)
- [ ] `_run_cc_baselines()` wires CC results through `CCTraceAdapter` → evaluation (not a stub)
- [ ] `scripts/collect-cc-traces/` directory removed (replaced by Python implementation)
- [ ] Makefile recipes `cc_run_solo`, `cc_run_teams`, `cc_collect_teams` updated to use Python entry point instead of shell scripts
- [ ] REFACTOR: remove inline subprocess code from callers
- [ ] `make validate` passes

**Files**:
- `src/run_cli.py` (edit — add `--cc-teams` flag, delegate to `cc_engine`)
- `src/run_sweep.py` (edit — add `--cc-teams` flag)
- `src/app/benchmark/sweep_runner.py` (edit — delegate to `cc_engine`, wire adapter)
- `src/app/benchmark/sweep_config.py` (edit — add `cc_teams: bool` field)
- `src/gui/pages/run_app.py` (edit — add teams toggle, pass `engine` through)
- `scripts/collect-cc-traces/` (delete — replaced by Python)
- `Makefile` (edit — update CC recipes)

##### 3.3 GUI Polish (same files as 3.2)

**Acceptance Criteria**:
- [ ] Add ARIA live region (`role="status"`) for execution state transitions, `role="alert"` for errors *(WCAG 4.1.3)* (`run_app.py:343-361`)
- [ ] Fix dead "Downloads page" reference — replace with CLI instructions (`make setup_dataset_sample`) (`run_app.py:381`)
- [ ] Add `help=` to engine selector explaining MAS vs Claude Code (`run_app.py:481`)
- [ ] Add `help=` parameter to paper selectbox (`run_app.py:384-389`)
- [ ] Add post-run navigation guidance to Evaluation Results and Agent Graph (`run_app.py:349-354`)
- [ ] Add sidebar execution-in-progress indicator when `execution_state == "running"` (`sidebar.py:14-27`)
- [ ] Replace raw metric snake_case keys with human-readable labels (`evaluation.py:136-142`)
- [ ] Wrap baseline comparison inputs in collapsed expander with explanation (`evaluation.py:249-259`)
- [ ] Add `st.dataframe()` text alternative below bar charts (`evaluation.py:130`)
- [ ] Populate `st.metric()` `delta` parameter from `BaselineComparison.tier_deltas` when baseline exists (`evaluation.py`)
- [ ] Replace `st.text()` metric displays with `st.dataframe()` or tabular-nums HTML for decimal alignment (`evaluation.py`)

**Files**:
- `src/gui/pages/run_app.py` (edit — ARIA, help text, navigation guidance)
- `src/gui/pages/evaluation.py` (edit — metric labels, baseline expander, delta indicators, dataframe alt)
- `src/gui/components/sidebar.py` (edit — execution-in-progress indicator)

**Technical Requirements**:
- **Solo path**: `subprocess.run(["claude", "-p", query, "--output-format", "json"], ...)` — blocking, parse JSON stdout (same as current, consolidated)
- **Teams path**: `subprocess.Popen(["claude", "-p", query, "--output-format", "stream-json", "--verbose"], env={..., "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"})` — stream stdout line-by-line, parse JSONL events:
  - `type=system, subtype=init` → `session_id`, `model`
  - `type=assistant` → tool_use content blocks → `tool_calls`
  - `type=result` → `duration_ms`, `total_cost_usd`, `num_turns`
  - Team-related events (from CC's internal orchestration) → `team_artifacts`
- Error handling consolidated: `RuntimeError` for non-zero exit/timeout, `ValueError` for JSON parse failure
- `check_cc_available()` replaces `shutil.which("claude")` in `run_cli.py:94`, `sweep_runner.py:189`, `run_app.py:472`
- Wire `CCTraceAdapter` into the result flow: `CCResult` → `CCTraceAdapter` → `GraphTraceData` → evaluation pipeline
- Teams prompt uses orchestration-specific wording (from `run-cc.sh:100-104`): assigns researcher, analyst, synthesizer roles

---

#### Feature 4: Graph Node Attribute Alignment

**Description**: `graph_analysis.py:export_trace_to_networkx()` uses `type` as node attribute, while `agent_graph.py:render_agent_graph()` expects `node_type`. Direct callers of `export_trace_to_networkx()` get wrong visual node types. Sprint 7 avoided this by routing through `build_interaction_graph()`, but the latent mismatch should be fixed.

**Acceptance Criteria**:
- [ ] Unified node attribute name across graph export and rendering
- [ ] All callers of `export_trace_to_networkx()` produce correct visual node types
- [ ] TDD: RED tests first verifying attribute name consistency between `export_trace_to_networkx()` output and `render_agent_graph()` expectations. GREEN: fix attribute name. REFACTOR: remove any adapter shims. Use `testing-python` skill.
- [ ] `make validate` passes

*GUI polish (implement alongside graph fix — same files):*
- [ ] Add `role="region" aria-label="Agent Interaction Graph"` wrapper around Pyvis iframe + text-based node/edge summary in expander *(WCAG 1.1.1, 4.1.2)* (`agent_graph.py:140`)
- [ ] Add graph interaction hints and color legend caption (`agent_graph.py:140`)

**Technical Requirements**:
- Canonical attribute name: `type` (already used by `graph_analysis.py:export_trace_to_networkx()` at 4 call sites and internally by `_build_tool_graph`/`analyze_tool_usage_patterns`)
- Fix consumer side: `agent_graph.py:render_agent_graph()` reads `node_data.get("node_type")` at lines 101 and 150 — change to `node_data.get("type")` (2 edits)
- No changes to `graph_analysis.py` — it already uses the canonical name

**Files**:
- `src/gui/pages/agent_graph.py` (edit — change `"node_type"` → `"type"` at lines 101, 150; a11y wrapper, interaction hints)
- `tests/judge/test_graph_analysis.py` (edit — TDD RED: attribute consistency tests verifying `export_trace_to_networkx()` nodes have `"type"` attribute)

---

#### Feature 5: PydanticAI Structured Output Streaming

**Description**: `run_manager()` raises `NotImplementedError` when `pydantic_ai_stream=True` because PydanticAI's `run_stream()` only supports `output_type=str`, not structured `BaseModel` outputs. Check if upstream PydanticAI has resolved this limitation; if so, enable streaming. If not, remove the dead code path and the `pydantic_ai_stream` parameter.

**Acceptance Criteria**:
- [ ] Check PydanticAI `run_stream()` structured output support status (upstream)
- [ ] If supported: enable streaming for structured output in `run_manager()`, remove `NotImplementedError`
- [ ] If not supported: delete dead code block (`agent_system.py:525-536`), remove `pydantic_ai_stream` parameter from `run_manager()` signature and all callers
- [ ] Update `AGENT_REQUESTS.md` entry (close or revise)
- [ ] TDD: If removing dead code, RED test first verifying `pydantic_ai_stream` parameter no longer exists on `run_manager()` signature. GREEN: remove parameter from all 8 call sites. Use `testing-python` skill.
- [ ] `make validate` passes

If not supported upstream: remove the parameter from all 8 call sites across `agent_system.py`, `orchestration.py`, and `app.py`, plus the module docstring at `agent_system.py:18`.

**Files**:
- `src/app/agents/agent_system.py` (edit — remove parameter + dead code block)
- `src/app/agents/orchestration.py` (edit — remove parameter + guard)
- `src/app/app.py` (edit — remove parameter from `run_pipeline()` and `run_query()`)
- `tests/agents/test_agent_system.py` (edit — TDD RED: verify `pydantic_ai_stream` parameter absent from `run_manager()` signature)

---

#### Feature 6: Report Generation in CLI and GUI

**Description**: After evaluation completes, users should be able to generate a structured report that summarizes evaluation results and suggests improvements. The report synthesizes Tier 1/2/3 scores, highlights weaknesses (low-scoring dimensions), and proposes actionable content suggestions (e.g., "Tier 1 BLEU score low — review lacks specific technical terminology from the paper abstract"). Available via `--generate-report` in CLI and a "Generate Report" button in the GUI.

##### 6.1 CLI Report Generation

**Acceptance Criteria**:
- [ ] `run_cli.py` accepts `--generate-report` flag (requires evaluation to have run, incompatible with `--skip-eval`)
- [ ] Report includes: executive summary, per-tier score breakdown, identified weaknesses, actionable suggestions
- [ ] Suggestions are grounded in evaluation data (reference specific metric scores and thresholds)
- [ ] Report output as Markdown file in `--output-dir` (default: `results/reports/<timestamp>.md`)
- [ ] `make validate` passes

**Technical Requirements**:
- New module `src/app/reports/report_generator.py` with `generate_report(result: CompositeResult, settings: JudgeSettings) -> str` returning Markdown
- Report structure: (1) Executive summary (composite score, recommendation, timestamp), (2) Per-tier breakdown (`tier1_score`, `tier2_score`, `tier3_score` with `weights_used`), (3) Weakness identification (metrics in `metric_scores` below threshold), (4) Actionable suggestions (from suggestion engine, Feature 6.3)
- Threshold bands from `JudgeSettings`: accept ≥ 0.8, weak_accept 0.6–0.8, weak_reject 0.4–0.6, reject < 0.4
- Output path: `{output_dir}/reports/{timestamp}.md` (default `results/reports/`)
- `--generate-report` flag in `run_cli.py`: requires evaluation to have run, incompatible with `--skip-eval`; calls `generate_report()` after `CompositeResult` is returned

**Files**:
- `src/run_cli.py` (edit — add `--generate-report` flag)
- `src/app/reports/__init__.py` (new)
- `src/app/reports/report_generator.py` (new — report generation from `CompositeResult`)
- `tests/reports/test_report_generator.py` (new — TDD RED: report structure, threshold-based suggestions)

##### 6.2 GUI Report Generation

**Acceptance Criteria**:
- [ ] "Generate Report" button on App page, enabled after evaluation completes
- [ ] Report displayed inline (Markdown rendered via `st.markdown`) with download option
- [ ] Same report content as CLI (shared generation logic)
- [ ] `make validate` passes

**Files**:
- `src/gui/pages/run_app.py` (edit — add report button and display)
- `src/app/reports/report_generator.py` (shared with 6.1 — same generation logic)

##### 6.3 Report Content and Suggestion Engine

**Acceptance Criteria**:
- [ ] Suggestions are specific and actionable (not generic "improve quality")
- [ ] Each suggestion references the metric/tier that triggered it
- [ ] Severity levels: critical (score < threshold), warning (below average), info (improvement opportunity)
- [ ] Optional LLM-assisted suggestions (uses judge provider) for richer content recommendations
- [ ] Rule-based fallback when LLM is unavailable or `--no-llm-suggestions` is set

**Technical Requirements**:
- New module `src/app/reports/suggestion_engine.py` with `generate_suggestions(result: CompositeResult, settings: JudgeSettings) -> list[Suggestion]`
- `Suggestion` Pydantic model: `severity` (critical/warning/info), `metric_name`, `tier`, `score`, `threshold`, `message`
- Rule-based engine: iterate `metric_scores` dict, compare each against tier thresholds from `JudgeSettings` (accept=0.8, weak_accept=0.6, weak_reject=0.4). Severity: critical if score < weak_reject, warning if < weak_accept, info if < accept
- Suggestion templates keyed by metric name (e.g., BLEU low → "Review lacks specific technical terminology from the paper", coherence low → "Review structure needs clearer logical flow between sections")
- Optional LLM-assisted: when `--no-llm-suggestions` is not set and judge provider is available, pass rule-based suggestions + `metric_scores` to judge LLM for enrichment. Fallback to rule-based if LLM unavailable or errors
- `--no-llm-suggestions` flag added to `run_cli.py`

**Files**:
- `src/app/reports/suggestion_engine.py` (new — rule-based + optional LLM suggestion generation)
- `src/app/data_models/report_models.py` (new — `Suggestion` Pydantic model)
- `tests/reports/test_suggestion_engine.py` (new — TDD RED: severity classification, metric-specific templates, LLM fallback)

---

#### Feature 7: Replace Free-Text Inputs with Populated Dropdowns in Judge Settings GUI

**Description**: The "Judge Settings - Tier 2 LLM Judge" section in `src/gui/pages/settings.py:169-211` uses `text_input` for provider and model fields (lines 172, 178, 184, 192). Users must type provider names and model IDs from memory, with no validation or discovery. In contrast, "Agent Configuration" (line 30-42) already uses `selectbox` populated from `PROVIDER_REGISTRY` — the same pattern should be reused for judge settings.

**Current state** (`_render_tier2_llm_judge()` in `settings.py:169`):
- `tier2_provider` — `text_input`, free-text (line 172)
- `tier2_model` — `text_input`, free-text (line 178)
- `tier2_fallback_provider` — `text_input`, free-text (line 184)
- `tier2_fallback_model` — `text_input`, free-text (line 192)

**Reference pattern** (`_render_agent_configuration()` in `settings.py:26`):
- `chat_provider` — `selectbox` populated from `PROVIDER_REGISTRY.keys()` (line 37)

**Data sources for dropdown population**:
- Providers: `PROVIDER_REGISTRY` (`src/app/data_models/app_models.py:142`) — already used by Agent Configuration
- Models: `config_chat.json` providers → `model_name` per provider (loaded via `ChatConfig`), plus `"auto"` option for `tier2_provider`
- `fallback_strategy`: `JudgeSettings.fallback_strategy` (`settings.py:91`) is a string field (`"tier1_only"`) but not exposed in GUI — could be added as a dropdown with known strategies

**Acceptance Criteria**:
- [ ] `tier2_provider` field uses `selectbox` populated from `PROVIDER_REGISTRY.keys()` + `"auto"` option
- [ ] `tier2_model` field uses `selectbox` populated from `config_chat.json` model names for the selected provider (dynamic, updates when provider changes)
- [ ] `tier2_fallback_provider` field uses `selectbox` populated from `PROVIDER_REGISTRY.keys()` (no `"auto"`)
- [ ] `tier2_fallback_model` field uses `selectbox` populated from `config_chat.json` model names for the selected fallback provider
- [ ] Existing `text_input` free-text entry removed for all 4 fields
- [ ] `fallback_strategy` exposed as `selectbox` with known strategies (at minimum: `"tier1_only"`)
- [ ] TDD: RED tests first verifying `selectbox` renders with correct options from `PROVIDER_REGISTRY` and `ChatConfig`. GREEN: replace `text_input` with `selectbox`. REFACTOR: extract shared provider-loading logic if duplicated with `_render_agent_configuration()`. Use `testing-python` skill.
- [ ] `make validate` passes

*GUI polish (implement alongside dropdown work — same file):*
- [ ] Default all Judge Settings expanders to `expanded=False` + add "Advanced Settings" section header (`settings.py:90,131,171,215`)

**Technical Requirements**:
- Reuse the same `PROVIDER_REGISTRY` + `selectbox` pattern from `_render_agent_configuration()`
- For model dropdowns: load `ChatConfig` from `config_chat.json`, extract `model_name` for the selected provider key
- Model selectbox must react to provider selection (Streamlit reruns on widget change, so the model list updates naturally)

**Files**:
- `src/gui/pages/settings.py` (edit — `_render_tier2_llm_judge()`, replace 4 `text_input` with `selectbox`, progressive disclosure expanders)
- `tests/gui/test_settings.py` (edit — TDD RED: verify selectbox options match registry)

---

#### Feature 8: GUI Standalone Fixes — UX, Accessibility, Environment URL, Run ID

**Description**: Standalone GUI improvements that don't share files with Features 3, 4, or 7. Synergy items (touching `run_app.py`, `evaluation.py`, `settings.py`, `agent_graph.py`) have been folded into their parent features as GUI polish sub-sections. This feature contains: (1) items with their own dedicated files, (2) items moved from Features 3/7 that are independent GUI concerns. Consolidated audit: `docs/reviews/gui-comprehensive-audit.md`.

##### 8.1 Standalone Accessibility and Usability Fixes

**Acceptance Criteria**:
- [ ] Remove CSS radio button circle hiding hack — restores native selection indicator *(Critical, Level A — WCAG 1.3.3, 1.4.1)* (`styling.py:14-16`)
- [ ] Fix sidebar radio: replace `" "` label with `"Navigation"` + `label_visibility="collapsed"` *(Level AA — WCAG 1.3.1, 2.4.6)* (`sidebar.py:16`)
- [ ] Add text-prefix badges (`[WARN]`, `[ERR]`, etc.) to log levels — not color-only *(Level AA — WCAG 1.4.1)* (`log_capture.py:117-134`)
- [ ] Fix log module text color `#999999` → `#696969` (contrast 2.8:1 → 5.9:1) *(Level AA — WCAG 1.4.3)* (`log_capture.py:131`)
- [ ] Add "(opens in new tab)" to Phoenix Traces link (`sidebar.py:21-24`)
- [ ] Update `HOME_INFO` to reflect correct onboarding order: Settings before App *(Critical)* (`text.py:1`, `home.py:7-9`)
- [ ] Add prominent warning on Prompts page that edits are display-only *(Critical)* (`prompts.py:50`)
- [ ] Update query placeholder to domain-specific example: `"e.g., Evaluate this paper's methodology and novelty"` (`text.py:16`)
- [ ] Add `.streamlit/config.toml` theme — primary `#4A90E2` (matches agent graph blue), replace default red
- [ ] Default sub-agents to True: change `"include_researcher": False` → `True`, `"include_analyst": False` → `True` in `get_session_state_defaults()` (`run_gui.py:63-64`)
- [ ] Move `subheader(OUTPUT_SUBHEADER)` after the `button(RUN_APP_BUTTON)` call — "Output" header currently appears above the Run button (`run_app.py:519-521`)

**Files**:
- `src/gui/config/styling.py` (edit — remove CSS radio hack)
- `src/gui/config/text.py` (edit — update `HOME_INFO`, query placeholder)
- `src/gui/pages/home.py` (edit — onboarding order)
- `src/gui/pages/prompts.py` (edit — display-only warning)
- `src/gui/pages/run_app.py` (edit — move subheader after run button)
- `src/gui/components/sidebar.py` (edit — radio label, external link warning)
- `src/gui/utils/log_capture.py` (edit — text badges, contrast fix)
- `src/run_gui.py` (edit — default sub-agents to True)
- `.streamlit/config.toml` (new — theme)

##### 8.2 App Page UX + Evaluation Page UX (moved from Feature 3 — independent GUI concerns)

**Acceptance Criteria**:
- [ ] `run_app.py`: when `engine == "cc"`, MAS-specific controls are hidden (not just disabled) — sub-agent checkboxes, provider selectbox, token limit, configuration summary (`_display_configuration`). Currently `mas_disabled` (line 496) shows an info banner but all controls remain visible.
- [ ] `run_app.py`: custom query `text_input` visible in both "Free-form query" and "Select a paper" modes. Currently free-form mode (line 514) renders only the query input, while paper mode renders paper selectbox + custom query inside `_render_paper_selection_input()` (line 395-398). Refactor so the query input is rendered once after the mode-specific controls, visible in both modes — paper mode just adds the paper selectbox above it.
- [ ] `output.py`: rename `type` parameter to `output_type` in `render_output()` signature — currently shadows Python built-in `type` (`output.py:6`). Update all callers. When reworking `render_output()` to format `CompositeResult` as a summary card (audit item #23), fix the parameter name.
- [ ] Evaluation Results page displays shortened run ID. The `execution_id` (format `exec_{uuid.hex[:12]}`, generated at `agent_system.py:538`) is returned through `app.py:120` but never stored in session state — the GUI only stores `composite_result` and `graph`. Fix: (1) `run_app.py:_execute_query_background()` stores `execution_id` in `st.session_state`, (2) `evaluation.py:_render_overall_results()` displays it as a metric or caption alongside composite score, (3) "Evaluation Details" expander (line 271) also shows the full `execution_id`.
- [ ] Evaluation Results page "Baseline Comparison Configuration" (`evaluation.py:249-259`): add path validation and directory picker for CC Solo/Teams directory inputs. Currently only free-text `st.text_input` (lines 250, 255) with no existence check. Fix: (1) validate entered paths exist on disk (`Path.is_dir()`), show `st.error` if not, (2) auto-populate from known CC artifact locations (e.g., `logs/Agent_evals/traces/`) if they exist, (3) optionally add a directory picker widget alongside `text_input` for browsing.

**Technical Requirements**:
- CC hidden controls: wrap MAS-specific block (`run_app.py:484-515` — sub-agent checkboxes, provider selectbox, token limit slider, `_display_configuration()`) in `if engine != "cc":` guard instead of current `disabled=True` approach
- Custom query refactor: extract `text_input` from both the free-form branch (line 514) and `_render_paper_selection_input()` (line 395-398) into a single render call placed after mode-specific controls
- `output.py:6` rename: `type` → `output_type` in `render_output()` signature; grep for `render_output(` to find all callers in `run_app.py`
- Run ID threading: `_execute_query_background()` stores `execution_id` in session state (`st.session_state["execution_id"] = result.execution_id`) — `main()` already returns it via `app.py:120` but caller discards it
- Run ID display: `evaluation.py:_render_overall_results()` shows `st.caption(f"Run: {execution_id}")` alongside composite score; "Evaluation Details" expander (line 271) shows full ID
- Baseline path validation: `Path(path).is_dir()` check on `st.text_input` values (lines 250, 255), `st.error("Directory not found")` when invalid; auto-populate default from `Path("logs/Agent_evals/traces/")` if it exists

**Files**:
- `src/gui/pages/run_app.py` (edit — CC MAS hidden, custom query refactor, store `execution_id`)
- `src/gui/pages/evaluation.py` (edit — display run ID, baseline path validation)
- `src/gui/components/output.py` (edit — rename `type` → `output_type` parameter)
- `tests/gui/test_run_app.py` (edit — TDD RED: run ID threading, CC hidden controls)

##### 8.4 Environment-Aware Service URL Resolution + Testing (moved from Feature 7 — infrastructure concern)

**Acceptance Criteria**:
- [ ] Sidebar "Trace Viewer" link (`src/gui/components/sidebar.py:20-25`) resolves to the correct environment URL, not hardcoded `localhost:6006`. A generalized `resolve_service_url(port: int) -> str` function detects the environment and constructs the correct URL. Detection chain (first match wins): (1) `PHOENIX_ENDPOINT` env var override — explicit user config, (2) GitHub Codespaces — `CODESPACE_NAME` + `GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN` → `https://{name}-{port}.{domain}/`, (3) Gitpod — `GITPOD_WORKSPACE_URL` → replace scheme with port prefix, (4) fallback — `http://localhost:{port}`. Current state: `PHOENIX_DEFAULT_ENDPOINT` (`src/gui/config/config.py:5`) reads from `JudgeSettings().phoenix_endpoint` which defaults to `http://localhost:6006`.
- [ ] TDD: RED tests first for `resolve_service_url()` (Codespaces env, Gitpod env, explicit override, fallback). RED tests for run ID threading (session state stores `execution_id`, evaluation page renders it). GREEN: implement. Use `testing-python` skill.
- [ ] `make validate` passes

**Files**:
- `src/gui/config/config.py` (edit — add `resolve_service_url()`, use for `PHOENIX_DEFAULT_ENDPOINT`)
- `tests/gui/test_config.py` (new — TDD RED: `resolve_service_url` tests)

---

## Non-Functional Requirements

- Report generation (Feature 6) latency target: < 5s for rule-based suggestions, < 30s for LLM-assisted
- No new external dependencies for Features 1-8
- **Change comments**: Every non-trivial code change must include a concise inline comment with sprint, story, and reason. Format: `# S8-F{N}: {why}`. Examples:
  - `# S8-F1: replace LLM-callable tool with internal fallback chain`
  - `# S8-F8.1: WCAG 1.3.1 — sidebar radio needs accessible label`
  - `# S8-F3: consolidate CC subprocess into cc_engine module`
  Keep comments to one line. Omit for trivial changes (string edits, config values).

## Out of Scope

**Deferred to Sprint 9 (TBD acceptance criteria, low urgency):**
- Centralized Tool Registry with Module Allowlist (MAESTRO L7.2) — architectural, needs design
- Plugin Tier Validation at Registration (MAESTRO L7.1) — architectural, needs design
- Error Message Sanitization (MAESTRO) — TBD acceptance criteria
- Configuration Path Traversal Protection (MAESTRO) — TBD acceptance criteria
- GraphTraceData Construction Simplification (`model_validate()`) — TBD acceptance criteria
- Timeout Bounds Enforcement — low urgency
- Hardcoded Settings Audit — continuation of Sprint 7
- Time Tracking Consistency Across Tiers — low urgency
- BDD Scenario Tests for Evaluation Pipeline — useful but not blocking
- Tier 1 Reference Comparison Fix — requires ground-truth review integration
- Cerebras Structured Output Validation Retries — provider-specific edge case
- PlantUML Diagram Audit — cosmetic, no user impact
- Unify API Key Resolution Across Agent and Judge Paths — partially addressed by Feature 2 auto-mode fix; full unification deferred
- ~~CC engine SDK migration~~ — **Removed.** Keeping `subprocess.run([claude, "-p"])` per ADR-008.

**Already completed (Sprint 8 pre-work, commits a5ac5c9→9e14931→9329fc3):**
- Legacy config key removal (`paper_numbers`, `provider`) from `run_sweep.py`
- Judge API key forwarding: `_resolve_provider_key` → `select_available_provider` → `create_judge_agent`
- `"not-required"` sentinel removed from `create_simple_model()` — `None` lets SDK use env vars

---

## Notes for Ralph Loop

### Priority Order

- **P0 (sweep-crashing)**: STORY-001
- **P1 (correctness)**: STORY-002, STORY-003, STORY-004
- **P2 (consolidation)**: STORY-005, STORY-006, STORY-007
- **P3 (new capability)**: STORY-008, STORY-009, STORY-010
- **P4 (polish)**: STORY-011, STORY-012, STORY-013, STORY-014

STORY-011 has no file overlaps and can run in any wave. STORY-012, STORY-013, and STORY-014 share files with STORY-007 (`sidebar.py`, `run_app.py`, `evaluation.py`, `config.py`) — see File-Conflict Dependencies table below for sequencing.

### Shared File Coordination

Features 3, 7, and 8 all edit `run_app.py`. Features 3 and 8 both edit `evaluation.py` and `sidebar.py`. GUI polish items are folded into their parent features (3.3, 4 GUI polish, 7 GUI polish) to avoid merge conflicts — implementers editing the same file handle both core and polish AC items in one pass.

`output.py` is edited by Feature 8.2 (parameter rename). No other feature touches this file.

### Notes for CC Agent Teams

**Alternative orchestration mode**: Instead of Ralph's bash loop driving `claude -p` iterations, the CC main orchestrator agent spawns a team using `TeamCreate` + `Task` tool. Each story becomes a `TaskCreate` entry with `blockedBy` dependencies. Teammates execute stories in parallel where dependencies allow.

**Why dual-mode**: Ralph's teams mode (`TEAMS=true`) has 4 documented failure modes (see `ralph/README.md`): Sisyphean reset loops, cross-contamination, cross-story complexity gates, stale snapshots. CC Agent Teams avoids these structurally:

<!-- markdownlint-disable MD013 -->

| Ralph Failure Mode | CC Teams Mitigation |
|---|---|
| 1. TDD commits don't survive reset | No external reset — teammates self-manage commits |
| 2. Cross-contamination | Each teammate has isolated context window |
| 3. Cross-story complexity gate | Lead runs scoped validation per story's changed files |
| 4. Stale snapshot tests | `blockedBy` ensures sequential stories see predecessor's changes |
| 5. File-conflict deps not tracked | `blockedBy` includes both logical AND file-overlap deps (see table below) |

<!-- markdownlint-enable MD013 -->

#### Team Structure

- **Lead**: Orchestrator (current CC session). Creates team, assigns stories, validates between waves. Does not implement (use delegate mode for 3+ teammates).
- **Teammates**: 3–4 max concurrent (token cost scales linearly per CC instance). CLAUDE.md, skills, and MCP servers auto-loaded.
- **Models**: Teammates inherit lead's model. For cost optimization: `sonnet` for P0–P2 stories, `haiku` for P4 polish.

#### File-Conflict Dependencies

Beyond logical dependencies (`depends_on` in prd.json), file overlaps require additional sequencing. These are only needed for CC Teams parallel execution — Ralph's sequential mode ignores them harmlessly.

<!-- markdownlint-disable MD013 -->

| Story | Logical Dep | + File-Conflict Dep | Shared File |
|---|---|---|---|
| STORY-006 | STORY-005 | — | — |
| STORY-007 | STORY-006 | — | — |
| STORY-009 | STORY-008 | + STORY-006 | `run_cli.py` |
| STORY-010 | STORY-009 | + STORY-007, STORY-013 | `run_app.py` |
| STORY-012 | — | + STORY-007 | `sidebar.py`, `run_app.py` |
| STORY-013 | — | + STORY-007, STORY-012 | `run_app.py`, `evaluation.py` |
| STORY-014 | — | + STORY-012 | `config.py` |

<!-- markdownlint-enable MD013 -->

#### Orchestration Waves

Stories within a wave can run in parallel; waves are sequential.

```text
Wave 1 (all independent — no blockers):
  STORY-001, STORY-002, STORY-003, STORY-004, STORY-005, STORY-008, STORY-011

Wave 2 (after STORY-005):
  STORY-006

Wave 3 (after STORY-006; STORY-009 also waits for STORY-008):
  STORY-007, STORY-009

Wave 4a (after STORY-007):
  STORY-012

Wave 4b (after STORY-012 [file: run_app.py]):
  STORY-013

Wave 4c (after STORY-013 [file: run_app.py]; STORY-010 also waits for STORY-009):
  STORY-010

Wave 5 (after STORY-012):
  STORY-014
```

Wave 1 has 7 stories but 3–4 teammates max. Lead batches: assign 001+002+003+004 first, then 005+008+011 as teammates free up. STORY-011 (`settings.py`, zero overlaps) can start in any wave.

#### Quality Gates

- **Each teammate**: Runs `make quick_validate` before marking task complete
- **Lead**: Runs `make validate` after each wave completes (catches cross-story regressions)
- **Final gate**: `make validate` + `make test_all` after all stories complete

#### Teammate Prompt Template

Lead injects this via `Task(prompt=...)` when spawning each teammate:

```text
MANDATORY: Read AGENTS.md first, then CONTRIBUTING.md for technical standards.
ROLE: Developer. Follow specifications exactly. Do not make architectural decisions.

## TDD Commit Discipline (ENFORCED)

Make SEPARATE git commits per phase:
1. `git add tests/ && git commit -m "test(STORY-XXX): ... [RED]"`
2. `git add src/ && git commit -m "feat(STORY-XXX): ... [GREEN]"`
3. `git add . && git commit -m "refactor(STORY-XXX): ... [REFACTOR]"` (optional)

DO NOT bundle work into a single commit. DO NOT skip the [RED] or [GREEN] markers.

## Quality

Run `make quick_validate` before marking your task complete.
During development: `make ruff`, `make type_check`, `uv run pytest <test-file>`.

## Your Story

Read Feature {N} in docs/PRD.md for full acceptance criteria, technical
requirements, and file list. Story-specific context follows below.
```

### Story Breakdown

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (14 stories total):

- **Feature 1** → STORY-001: Replace `read_paper_pdf_tool` with `get_paper_content` using parsed JSON fallback chain
  Remove LLM-callable `read_paper_pdf_tool`, add `get_paper_content(paper_id)` tool that internally uses `_load_paper_content_with_fallback()`. Add URL rejection guard in `read_paper_pdf()`. Files: `peerread_tools.py`, `test_peerread_tools.py`.

- **Feature 2** → STORY-002: Remove `"not-required"` sentinel (5 call sites) + fix judge auto-mode model inheritance + cross-provider fallback test
  Replace `api_key or "not-required"` with `api_key` at 5 sites in `create_llm_model()`. Add `chat_model` parameter to `LLMJudgeEngine.__init__` for auto-mode inheritance. Add cross-provider fallback test. Files: `models.py`, `llm_evaluation_managers.py`, `evaluation_pipeline.py`, tests.

- **Feature 4** → STORY-003: Fix graph node attribute alignment (`"node_type"` → `"type"` in `agent_graph.py`) + GUI a11y wrapper
  Change `node_data.get("node_type")` to `node_data.get("type")` at 2 sites in `render_agent_graph()`. Add ARIA region wrapper + interaction hints. Files: `agent_graph.py`, `test_graph_analysis.py`.

- **Feature 5** → STORY-004: Remove dead `pydantic_ai_stream` parameter from 8 call sites + close `AGENT_REQUESTS.md` entry
  Check upstream PydanticAI `run_stream()` status. If still unsupported: delete dead code block `agent_system.py:525-536`, remove parameter from `run_manager()` and all 8 callers. Files: `agent_system.py`, `orchestration.py`, `app.py`, `test_agent_system.py`.

- **Feature 3.1** → STORY-005: Create `cc_engine.py` core module (`CCResult`, `run_cc_solo`, `run_cc_teams`, `parse_stream_json`, `check_cc_available`)
  New module `src/app/engines/cc_engine.py` with Pydantic `CCResult` model, solo subprocess (`--output-format json`), teams subprocess (`--output-format stream-json` + `Popen` JSONL parser). All new files, no overlap. Files: `engines/__init__.py`, `engines/cc_engine.py`, `tests/engines/test_cc_engine.py`.

- **Feature 3.2** → STORY-006: Wire `cc_engine` into CLI/sweep/GUI, add `--cc-teams` flag, retire shell scripts (depends: STORY-005)
  Replace inline `subprocess.run()` in `run_cli.py`, `sweep_runner.py`, `run_app.py` with `cc_engine` calls. Add `--cc-teams` CLI flag. Delete `scripts/collect-cc-traces/`. Update Makefile. Files: `run_cli.py`, `run_sweep.py`, `sweep_runner.py`, `sweep_config.py`, `run_app.py`, Makefile.

- **Feature 3.3** → STORY-007: GUI polish for `run_app.py`, `evaluation.py`, `sidebar.py` (ARIA, help text, metric labels, delta indicators) (depends: STORY-006)
  Add ARIA live regions, fix dead "Downloads page" reference, add help text to engine/paper selectors, execution-in-progress indicator, human-readable metric labels, baseline expander, dataframe alt text. Files: `run_app.py`, `evaluation.py`, `sidebar.py`.

- **Feature 6.3** → STORY-008: Suggestion engine (`suggestion_engine.py`, `Suggestion` model, rule-based + optional LLM)
  New module: iterate `metric_scores`, compare against tier thresholds, assign severity (critical/warning/info). Templates keyed by metric name. Optional LLM enrichment via judge provider. All new files, no overlap. Files: `suggestion_engine.py`, `report_models.py`, `test_suggestion_engine.py`.

- **Feature 6.1** → STORY-009: CLI report generation (`report_generator.py`, `--generate-report` flag) (depends: STORY-008, STORY-006 [file: run_cli.py])
  New module `report_generator.py`: executive summary, per-tier breakdown, weakness identification, suggestions from STORY-008 engine. `--generate-report` flag added to `run_cli.py` arg parser (shared with STORY-006's `--cc-teams`). Files: `run_cli.py`, `reports/__init__.py`, `report_generator.py`, `test_report_generator.py`.

- **Feature 6.2** → STORY-010: GUI report generation (report button + inline display) (depends: STORY-009, STORY-007, STORY-013 [file: run_app.py])
  "Generate Report" button on App page, enabled after evaluation. Inline Markdown display with download. Shares `report_generator.py` logic with CLI. Files: `run_app.py`, `report_generator.py`.

- **Feature 7** → STORY-011: Replace 4 free-text inputs with populated `selectbox` in Tier 2 LLM Judge GUI + expander polish
  Replace `text_input` with `selectbox` for provider/model fields. Populate from `PROVIDER_REGISTRY` + `config_chat.json`. No file overlaps with other stories. Files: `settings.py`, `test_settings.py`.

- **Feature 8.1** → STORY-012: Standalone a11y/usability fixes (styling, sidebar, log, home, prompts, theme, defaults) (depends: STORY-007 [file: sidebar.py])
  Remove CSS radio hack, fix sidebar radio label, add log text badges, fix contrast, update HOME_INFO, add prompts warning, Streamlit theme, default sub-agents to True. Files: `styling.py`, `text.py`, `run_app.py`, `home.py`, `prompts.py`, `sidebar.py`, `log_capture.py`, `run_gui.py`, `.streamlit/config.toml`.

- **Feature 8.2** → STORY-013: App page UX + Evaluation page UX (depends: STORY-007, STORY-012 [file: run_app.py, evaluation.py])
  CC hidden controls (hide MAS widgets when engine=cc), custom query refactor, `output.py` type→output_type rename, run ID threading, baseline path validation. Files: `run_app.py`, `evaluation.py`, `output.py`, `test_run_app.py`.

- **Feature 8.4** → STORY-014: Environment-aware `resolve_service_url()` + tests (depends: STORY-012 [file: config.py])
  New function `resolve_service_url(port)`: PHOENIX_ENDPOINT override → Codespaces → Gitpod → localhost fallback. Tests for all environments. Files: `config.py`, `test_config.py`.
