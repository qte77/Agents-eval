---
title: Product Requirements Document - Agents-eval Sprint 8
description: PeerRead tool fix, "not-required" fallback key removal, judge auto-mode model inheritance, CC engine consolidation, graph alignment, streaming check, report generation, GUI quality audit fixes.
version: 1.0.5
created: 2026-02-17
updated: 2026-02-18
---

## Project Overview

**Agents-eval** evaluates multi-agent AI systems using the PeerRead dataset. The system generates scientific paper reviews via a 4-agent delegation pipeline (Manager → Researcher → Analyst → Synthesizer) and evaluates them through three tiers: traditional metrics, LLM-as-Judge, and graph analysis.

Sprint 7 delivered: documentation alignment, example modernization, test suite refinement, GUI improvements (real-time logging, paper selection, editable settings), unified provider configuration, Claude Code engine option.

**Sprint 8 Focus**: Fix sweep-crashing tool bug, remove `"not-required"` fallback key + fix judge auto-mode model inheritance, consolidate CC engine logic, graph attribute alignment, streaming decision, report generation, GUI quality audit fixes.

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

3. **Cross-provider key mismatch untested** (`tests/judge/test_llm_evaluation_managers.py`): Three existing tests cover auto-mode but all seed the env with the *same* provider's key, so a cross-provider mismatch never surfaces:
   - `test_tier2_provider_auto_inherits_from_chat_provider` (line 427): sets `chat_provider="github"` with `GITHUB_API_KEY="ghp-test"` — key matches provider.
   - `test_auto_mode_inherits_chat_provider_correctly` (line 746): sets `chat_provider="github"` with `GITHUB_API_KEY="ghp-test"` — key matches provider.
   - `test_auto_mode_inherits_chat_provider` (line 684, Hypothesis property test): generates random `chat_provider` values from `["openai", "github", "cerebras", "grok"]` but always seeds `env_config` with that same provider's key (line 699: `env_kwargs = {env_keys[chat_provider]: "test-key"}`).

   None of these tests cover the scenario where `chat_provider="cerebras"` but only `GITHUB_API_KEY` is set (not `CEREBRAS_API_KEY`). In that case, auto resolves to cerebras, `_resolve_provider_key("cerebras", env_config)` fails (no key), and the engine falls back to `tier2_fallback_provider="github"`. The fallback chain works correctly, but this path is never exercised.

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

**Files**:
- `src/app/llms/models.py` (edit — 5 lines, sentinel removal)
- `src/app/judge/llm_evaluation_managers.py` (edit — add `chat_model` parameter, inherit model in auto-mode)
- `src/app/judge/evaluation_pipeline.py` (edit — forward `chat_model` to `LLMJudgeEngine`)
- `tests/llms/test_models.py` (edit — add sentinel removal test)
- `tests/judge/test_llm_evaluation_managers.py` (edit — add model inheritance and cross-provider tests)

---

#### Feature 3: Consolidate CC Engine into `src/app/engines/cc_engine.py` with Teams Support

**Description**: CC (Claude Code) engine logic is scattered across `run_cli.py`, `sweep_runner.py`, `run_app.py`, and `scripts/collect-cc-traces/*.sh` with duplicated subprocess invocation, inconsistent error handling, and incomplete wiring. The `subprocess.run(["claude", "-p", ...])` pattern is copy-pasted between CLI and sweep. The GUI accepts the engine selection but silently ignores it. `_run_cc_baselines()` in `sweep_runner.py` is a stub. Additionally, `--engine=cc` only supports solo mode — there is no way to invoke CC with Agent Teams orchestration. The shell scripts under `scripts/collect-cc-traces/` duplicate logic that should live in Python (DRY violation; they will inevitably diverge).

**Critical constraint**: CC teams artifacts (`~/.claude/teams/`, `~/.claude/tasks/`) are ephemeral in `claude -p` print mode — cleaned up after exit (see AGENT_LEARNINGS.md). The existing `run-cc.sh` works around this by copying artifacts during execution. The Python implementation uses `--output-format stream-json` with `Popen` to parse `TeamCreate`, `Task`, and inbox events from the live output stream, eliminating the need for filesystem artifact collection.

**Current state:**
- `run_cli.py:108-126` — inline `subprocess.run()`, solo only, captures `session_dir`
- `sweep_runner.py:143-185` — duplicate `subprocess.run()`, solo only, stub baseline loop
- `run_app.py:481-532` — engine selector UI, `engine` param silently dropped
- `scripts/collect-cc-traces/run-cc.sh` — shell implementation with teams artifact collection (260 lines)
- `scripts/collect-cc-traces/collect-team-artifacts.sh` — standalone teams artifact collector
- `scripts/collect-cc-traces/lib/collect-common.sh` — shared shell helpers
- `cc_trace_adapter.py` — artifact parser, only called from `evaluation_runner.py` (not from subprocess paths)

**Acceptance Criteria**:
- [ ] New module `src/app/engines/cc_engine.py` with:
  - `check_cc_available() -> bool` — `shutil.which("claude")` (replaces 3 inline checks)
  - `run_cc_solo(query: str, timeout: int = 600) -> CCResult` — solo subprocess with `--output-format json`
  - `run_cc_teams(query: str, timeout: int = 600) -> CCResult` — teams subprocess with `--output-format stream-json` + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env var, parses team events from live stream via `Popen`
  - `CCResult` Pydantic model: `execution_id`, `output_data`, `session_dir` (solo), `team_artifacts` (teams: parsed from stream events)
  - `parse_stream_json(stream) -> CCResult` — JSONL line parser extracting `init`, `result`, `TeamCreate`, `Task` events
- [ ] `--cc-teams` boolean flag added to CLI (`run_cli.py`), sweep (`run_sweep.py`), and GUI (`run_app.py`)
- [ ] `--engine=cc` without `--cc-teams`: calls `run_cc_solo()` (current behavior, consolidated)
- [ ] `--engine=cc --cc-teams`: calls `run_cc_teams()` with teams env var and stream-json parsing
- [ ] `run_cli.py` CC branch delegates to `cc_engine` — no inline subprocess code
- [ ] `sweep_runner.py._invoke_cc_comparison()` delegates to `cc_engine` — no inline subprocess code
- [ ] `run_app.py._execute_query_background()` passes `engine` to `main()` when `engine == "cc"` (currently silently dropped)
- [ ] `_run_cc_baselines()` wires CC results through `CCTraceAdapter` → evaluation (not a stub)
- [ ] `scripts/collect-cc-traces/` directory removed (replaced by Python implementation)
- [ ] Makefile recipes `cc_run_solo`, `cc_run_teams`, `cc_collect_teams` updated to use Python entry point instead of shell scripts
- [ ] `src/app/engines/__init__.py` created
- [ ] TDD: RED tests first (`tests/engines/test_cc_engine.py`) covering `run_cc_solo`, `run_cc_teams`, `parse_stream_json`, `check_cc_available` with mocked `subprocess`. GREEN: implement `cc_engine.py`. REFACTOR: remove inline subprocess code from callers. Use `testing-python` skill.
- [ ] `make validate` passes

*GUI polish (implement alongside core CC work — same files already being edited):*
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

**Files**:
- `src/app/engines/__init__.py` (new)
- `src/app/engines/cc_engine.py` (new — consolidated CC logic, solo + teams)
- `src/run_cli.py` (edit — add `--cc-teams` flag, delegate to `cc_engine`)
- `src/run_sweep.py` (edit — add `--cc-teams` flag)
- `src/app/benchmark/sweep_runner.py` (edit — delegate to `cc_engine`, wire adapter)
- `src/app/benchmark/sweep_config.py` (edit — add `cc_teams: bool` field)
- `src/gui/pages/run_app.py` (edit — add teams toggle, pass `engine` through, wire CC path, GUI polish)
- `src/gui/pages/evaluation.py` (edit — metric labels, baseline expander, delta indicators, dataframe alt)
- `src/gui/components/sidebar.py` (edit — execution-in-progress indicator)
- `tests/engines/test_cc_engine.py` (new — TDD RED: subprocess mock tests, stream-json parsing tests)
- `scripts/collect-cc-traces/` (delete — replaced by Python)
- `Makefile` (edit — update `cc_run_solo`, `cc_run_teams`, `cc_collect_teams` recipes)

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
- TBD — choose canonical attribute name, update both sides

**Files**:
- `src/app/judge/graph_analysis.py` (edit)
- `src/gui/pages/agent_graph.py` (edit — attribute fix, a11y wrapper, interaction hints)
- `tests/judge/test_graph_analysis.py` (edit — TDD RED: attribute consistency tests)

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

**Caller chain** (all sites that pass `pydantic_ai_stream`):
- `src/app/app.py:79` — `run_pipeline()` accepts `pydantic_ai_stream: bool` parameter
- `src/app/app.py:117` — `run_pipeline()` passes it to `run_orchestration()`
- `src/app/app.py:200` — `run_query()` accepts `pydantic_ai_stream: bool = False`
- `src/app/app.py:251` — `run_query()` passes it to `run_pipeline()`
- `src/app/agents/orchestration.py:248` — `run_orchestration()` accepts `pydantic_ai_stream: bool = False`
- `src/app/agents/orchestration.py:267` — `run_orchestration()` guards with `if pydantic_ai_stream: raise NotImplementedError`
- `src/app/agents/agent_system.py:517` — `run_manager()` accepts `pydantic_ai_stream: bool = False`
- `src/app/agents/agent_system.py:546` — `run_manager()` guards with `if pydantic_ai_stream: raise NotImplementedError`

If not supported upstream: remove the parameter from all 8 sites above plus the module docstring at `agent_system.py:18`.

**Files**:
- `src/app/agents/agent_system.py` (edit — remove parameter + dead code block)
- `src/app/agents/orchestration.py` (edit — remove parameter + guard)
- `src/app/app.py` (edit — remove parameter from `run_pipeline()` and `run_query()`)

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
- TBD — requires design phase to determine report structure, suggestion generation approach (rule-based vs LLM-assisted), and integration with `CompositeResult`

**Files**:
- `src/run_cli.py` (edit — add `--generate-report` flag)
- `src/app/reports/` (new — report generation module)
- TBD

##### 6.2 GUI Report Generation

**Acceptance Criteria**:
- [ ] "Generate Report" button on App page, enabled after evaluation completes
- [ ] Report displayed inline (Markdown rendered via `st.markdown`) with download option
- [ ] Same report content as CLI (shared generation logic)
- [ ] `make validate` passes

**Files**:
- `src/gui/pages/run_app.py` (edit — add report button and display)
- TBD

##### 6.3 Report Content and Suggestion Engine

**Acceptance Criteria**:
- [ ] Suggestions are specific and actionable (not generic "improve quality")
- [ ] Each suggestion references the metric/tier that triggered it
- [ ] Severity levels: critical (score < threshold), warning (below average), info (improvement opportunity)
- [ ] Optional LLM-assisted suggestions (uses judge provider) for richer content recommendations
- [ ] Rule-based fallback when LLM is unavailable or `--no-llm-suggestions` is set

**Technical Requirements**:
- TBD — requires research into what makes suggestions actionable for the PeerRead evaluation context

**Files**:
- `src/app/reports/` (new — suggestion engine)
- TBD

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

##### 8.2 App Page UX (moved from Feature 3 — independent GUI concerns)

**Acceptance Criteria**:
- [ ] `run_app.py`: when `engine == "cc"`, MAS-specific controls are hidden (not just disabled) — sub-agent checkboxes, provider selectbox, token limit, configuration summary (`_display_configuration`). Currently `mas_disabled` (line 496) shows an info banner but all controls remain visible.
- [ ] `run_app.py`: custom query `text_input` visible in both "Free-form query" and "Select a paper" modes. Currently free-form mode (line 514) renders only the query input, while paper mode renders paper selectbox + custom query inside `_render_paper_selection_input()` (line 395-398). Refactor so the query input is rendered once after the mode-specific controls, visible in both modes — paper mode just adds the paper selectbox above it.
- [ ] `output.py`: rename `type` parameter to `output_type` — currently shadows Python built-in `type` (`output.py:6`). When reworking `render_output()` to format `CompositeResult` as a summary card (audit item #23), fix the parameter name.

##### 8.3 Evaluation Results Page UX (moved from Feature 3 — independent GUI concerns)

**Acceptance Criteria**:
- [ ] Evaluation Results page displays shortened run ID. The `execution_id` (format `exec_{uuid.hex[:12]}`, generated at `agent_system.py:538`) is returned through `app.py:120` but never stored in session state — the GUI only stores `composite_result` and `graph`. Fix: (1) `run_app.py:_execute_query_background()` stores `execution_id` in `st.session_state`, (2) `evaluation.py:_render_overall_results()` displays it as a metric or caption alongside composite score, (3) "Evaluation Details" expander (line 271) also shows the full `execution_id`.
- [ ] Evaluation Results page "Baseline Comparison Configuration" (`evaluation.py:249-259`): add path validation and directory picker for CC Solo/Teams directory inputs. Currently only free-text `st.text_input` (lines 250, 255) with no existence check. Fix: (1) validate entered paths exist on disk (`Path.is_dir()`), show `st.error` if not, (2) auto-populate from known CC artifact locations (e.g., `logs/Agent_evals/traces/`) if they exist, (3) optionally add a directory picker widget alongside `text_input` for browsing.

##### 8.4 Environment-Aware Service URL Resolution (moved from Feature 7 — infrastructure concern)

**Acceptance Criteria**:
- [ ] Sidebar "Trace Viewer" link (`src/gui/components/sidebar.py:20-25`) resolves to the correct environment URL, not hardcoded `localhost:6006`. A generalized `resolve_service_url(port: int) -> str` function detects the environment and constructs the correct URL. Detection chain (first match wins): (1) `PHOENIX_ENDPOINT` env var override — explicit user config, (2) GitHub Codespaces — `CODESPACE_NAME` + `GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN` → `https://{name}-{port}.{domain}/`, (3) Gitpod — `GITPOD_WORKSPACE_URL` → replace scheme with port prefix, (4) fallback — `http://localhost:{port}`. Current state: `PHOENIX_DEFAULT_ENDPOINT` (`src/gui/config/config.py:5`) reads from `JudgeSettings().phoenix_endpoint` which defaults to `http://localhost:6006`.

##### 8.5 Testing

**Acceptance Criteria**:
- [ ] TDD: RED tests first for `resolve_service_url()` (Codespaces env, Gitpod env, explicit override, fallback). RED tests for run ID threading (session state stores `execution_id`, evaluation page renders it). GREEN: implement. Use `testing-python` skill.
- [ ] `make validate` passes

**Files**:
- `src/gui/config/styling.py` (edit — remove CSS radio hack)
- `src/gui/config/text.py` (edit — update `HOME_INFO`, query placeholder)
- `src/gui/config/config.py` (edit — add `resolve_service_url()`, use for `PHOENIX_DEFAULT_ENDPOINT`)
- `src/gui/pages/run_app.py` (edit — CC MAS hidden, custom query refactor, store `execution_id`)
- `src/gui/pages/evaluation.py` (edit — display run ID, baseline path validation)
- `src/gui/pages/home.py` (edit — onboarding order)
- `src/gui/pages/prompts.py` (edit — display-only warning)
- `src/gui/components/sidebar.py` (edit — radio label, external link warning, resolved URL caption)
- `src/gui/utils/log_capture.py` (edit — text badges, contrast fix)
- `.streamlit/config.toml` (new — theme)
- `tests/gui/test_config.py` (new — TDD RED: `resolve_service_url` tests)
- `tests/gui/test_run_app.py` (edit — TDD RED: run ID threading, CC hidden controls)

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

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (TBD stories total):

**Sprint 8 scope (in priority order):**
- Feature 1 (replace `read_paper_pdf_tool` with `get_paper_content`) — fixes sweep crash
- Feature 2 (remove `"not-required"` fallback key + fix judge auto-mode model inheritance) — replace `api_key or "not-required"` with `api_key` (5 call sites) + auto-mode `chat_model` pass-through + cross-provider fallback test
- Feature 3 (consolidate CC engine into `cc_engine.py` with teams support) — consolidate scattered subprocess + shell scripts into Python, add `--cc-teams` flag, stream-json parsing for teams artifacts, retire `scripts/collect-cc-traces/`
- Feature 4 (graph alignment) — small fix, 2 files
- Feature 5 (structured output streaming) — binary check, AGENT_REQUESTS.md item
- Feature 6 (report generation) — flagship feature, needs design phase first
- Feature 7 (judge settings dropdowns) — replace 4 free-text inputs with populated `selectbox` in Tier 2 LLM Judge GUI, reuse `PROVIDER_REGISTRY` pattern from Agent Configuration
- Feature 8 (GUI standalone fixes) — standalone a11y/usability (styling, sidebar, log, home, prompts, theme), App page UX (CC hidden controls, custom query), Evaluation page UX (run ID, baseline path validation), environment URL resolution. Synergy items folded into Features 3, 4, 7 as GUI polish sub-sections. Can run in parallel with Features 1-5.

Story breakdown TBD after Feature 6 design phase.
