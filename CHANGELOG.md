<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- `make lint_links` recipe and lychee link checker npm dependency for dead-link detection in docs
- Agent type indicator (red prefix) in Claude Code status line script (`.claude/scripts/statusline.sh`)
- WakaTime extension to devcontainer VS Code configurations
- `lychee.toml` link checker config accepting bot-blocked status codes (403/401/429), excluding archived sprints and unreachable domains
- AGENT_LEARNINGS.md: "Stale Test Fixtures Cause Cross-File Pollution" pattern

### Changed

- Docs: `security-advisories.md` Related Frameworks section restructured into Threat Modeling and AI Risk & Governance subsections; added NIST AI RMF 1.0, ISO 23894, ISO 42001
- Docs: Sprint 9 PRD expanded to 13 features incorporating review findings
- Commit skill updated for stats ordering and GPG signing
- pytest CI workflow: replaced pip+Python 3.12 with uv+Python 3.13, added project deps install and `pull_request` trigger

### Removed

- 5 stale review documents from `docs/reviews/` (evaluation-pipeline-parallel-review, gui-comprehensive-audit, sprint5-code-review, sprint5-test-audit, test-audit)
- `.cline/config.json` and `.gemini/config.json` — unused agent configs (project standardized on Claude Code)
- 72 stale files leaked from old `main` during squash merge: `.claude/agents/` (9), `opik/` (3), `docs/sprints/` (15), `src/app/evals/` (8), `scripts/citation-styles/` (4), `assets/images/` (4), `tests/` (8), `src/examples/` (2), `docker-compose.opik.yaml`

### Fixed

- `test_no_agentops_commented_code_in_login` hardcoded `/workspaces/` path broke pytest in GHA; replaced with `inspect.getfile()` for portability
- 24 broken URLs across landscape docs, further_reading, security-advisories (paper-qa repo, OWASP MAESTRO, StableToolBench org, OpenAI Operator, MatterGen publication)
- `lychee.toml`: accept 400/415/500 status codes, exclude `.venv` and `.github/workflows`, add `allenai.org` and Springer DOI to excludes
- Broken local file links: `architecture.md` landscape refs, `agent_eval_metrics.md` further_reading ref, `landscape.md` trace_processors path, `roadmap.md` sprint archive paths, `src/examples/README.md` relative paths
- Claude Code sandbox phantom files added to `.gitignore`
- Content diffs from stale merge fixed in `.gitignore`, `Makefile`, `pyproject.toml`, `agent_system.py`, `peerread_models.py`, `datasets_peerread.py`, `review_persistence.py`

## [4.0.0] - 2026-02-19

### Added

- Sprint 9 Feature 1: CC engine GUI wiring — PRD feature for routing "Claude Code" radio selection to `cc_engine.run_cc_solo`/`run_cc_teams` in GUI execution path (mirrors existing CLI logic in `run_cli.py:126-138`)
- `resolve_service_url(port)` in `src/gui/config/config.py`: detects GitHub Codespaces, Gitpod, and `PHOENIX_ENDPOINT` override to build correct service URLs in cloud dev environments; `PHOENIX_DEFAULT_ENDPOINT` now uses it (STORY-014)
- GUI report generation: "Generate Report" button on App page enabled after evaluation completes; report rendered inline as Markdown with a download button; shares `generate_report()` logic with CLI (STORY-010)
- App page UX: MAS-specific controls (sub-agents, provider, token limit, config summary) hidden entirely when CC engine selected — not just disabled (STORY-013)
- Evaluation Results page: `execution_id` displayed as caption below composite score; full ID shown in "Evaluation Details" expander (STORY-013)
- Baseline Comparison Configuration: path validation with `st.error` for non-existent directories; auto-populate from `logs/Agent_evals/traces/` if it exists (STORY-013)
- `execution_id` included in `_prepare_result_dict` return and threaded to session state via `_execute_query_background` (STORY-013)

### Removed

- 43 implementation-detail tests across 14 files: deleted `test_load_settings.py` (4 AST introspection guards), `test_sprint1_examples_deleted.py` (8 deleted-file guards), `test_opik_removal.py` (12 removal guards); removed file-exists/string-contains test classes from 3 example test files; removed individual `hasattr`/`callable`/`isinstance` checks from 8 test files. No behavioral coverage lost.

### Changed

- Docs: README Status section updated to Sprint 8 Delivered; architecture.md Implementation Status and Development Timeline aligned; Sprint 9 PRD stripped of all 14 solved stories (Features 1-8, Story Breakdown, Ralph Loop notes removed)

### Fixed

- `graph_builder.py`: aligned node attribute key `node_type` → `type` to match `agent_graph.py` reader (Sprint 8 Feature 4 residual); fixed stale `node_type=` fixtures in `test_session_state_wiring.py`
- `settings.py`: replaced `text("**Enable Sub-Agents:**")` and `text("**Token Limit:**")` with `st.markdown(...)` so bold formatting renders correctly; removed unused `text` import
- `render_output()` in `output.py`: renamed `type` parameter to `output_type` to avoid shadowing Python built-in `type` (STORY-013)

- GUI a11y/usability: text-prefix badges `[WARN]`/`[ERR]`/`[INFO]`/`[DBG]` in log panel (WCAG 1.4.1); `[CRIT]` for CRITICAL; module text color `#999999`→`#696969` for 5.9:1 contrast (WCAG 1.4.3); `"Navigation"` radio label with `label_visibility="collapsed"` (WCAG 1.3.1, 2.4.6); `"(opens in new tab)"` on Phoenix Traces link (WCAG 3.2.5); CSS radio-circle hiding hack removed (WCAG 1.3.3, 1.4.1); display-only warning on Prompts page; `HOME_INFO` onboarding corrected to Settings-before-App; `RUN_APP_QUERY_PLACEHOLDER` made domain-specific; `include_researcher`/`include_analyst` default to `True`; Streamlit primary color `#4A90E2` (agent graph blue) (STORY-012)
- GUI judge settings: `tier2_provider`, `tier2_model`, `tier2_fallback_provider`, `tier2_fallback_model` replaced with `selectbox` dropdowns populated from `PROVIDER_REGISTRY` and `config_chat.json`; `fallback_strategy` exposed as `selectbox` with "tier1_only"; judge settings expanders set to `expanded=False`; "Advanced Settings" header added (STORY-011)
- `report_generator.py` in `src/app/reports/`: `generate_report(result, suggestions)` → Markdown report with executive summary, tier breakdown, and weakness/suggestion sections; `save_report(md, path)` with auto-created parent dirs (STORY-009)
- `--generate-report` CLI flag (mutually exclusive with `--skip-eval`) writes report to `results/reports/<timestamp>.md` after evaluation (STORY-009)
- `--no-llm-suggestions` CLI flag to disable LLM-assisted suggestions in generated reports (STORY-009)
- `SuggestionEngine` with rule-based + optional LLM-assisted paths in `src/app/reports/suggestion_engine.py` (STORY-008)
- `Suggestion` Pydantic model and `SuggestionSeverity` enum (critical/warning/info) in `src/app/data_models/report_models.py` (STORY-008)
- `METRIC_LABELS` dict and `format_metric_label()` in `evaluation.py` for human-readable metric names (STORY-007)
- ARIA live regions (`role="status"`, `role="alert"`) in `_display_execution_result` for screen reader accessibility (STORY-007)
- Post-run navigation guidance in completed state ("Evaluation Results", "Agent Graph") (STORY-007)
- Sidebar execution-in-progress indicator (⏳) when `execution_state="running"` (STORY-007)
- `st.dataframe()` alt text below bar charts in `_render_metrics_comparison` (WCAG 1.1.1) (STORY-007)
- Baseline comparison inputs wrapped in collapsed expander in `render_evaluation` (STORY-007)
- Delta indicators in `_render_overall_results` from `BaselineComparison.tier_deltas` (STORY-007)
- GUI engine selector: radio toggle between MAS (PydanticAI) and Claude Code engines with CC availability check (STORY-014)
- GUI paper selection: dropdown with ID/title, abstract preview, free-form/paper mode toggle (STORY-009)
- GUI editable common settings: log level, max content length with tooltips; logfire consolidated to JudgeSettings (STORY-010)
- GUI real-time debug log: streaming log panel via `st.fragment` + `LogCapture` thread-safe polling (STORY-008)
- `--engine=mas|cc` flag for CLI and sweep, replacing `--cc-baseline` (STORY-013)
- Sweep rate-limit resilience: exponential backoff on 429 (max 3 retries), incremental `results.json` persistence (STORY-013b)
- `--judge-provider` and `--judge-model` CLI/sweep args for Tier 2 judge override (STORY-012)
- New examples: `basic_evaluation.py`, `judge_settings_customization.py`, `engine_comparison.py` with README (STORY-002)
- `--cc-teams` boolean flag for CLI (`run_cli.py`), sweep (`run_sweep.py`), and `SweepConfig` model; enables CC Agent Teams mode with `--engine=cc` (STORY-006)
- CC baseline Makefile recipes (`cc_run_solo`, `cc_run_teams`, `cc_collect_teams`)
- Test coverage improvements: `datasets_peerread` 27→60%, `models` 24→76%, `agent_factories` 39→75% (STORY-014)
- Security test suite: 135 tests across 5 modules (SSRF, prompt injection, data filtering, input limits, tool registration) (STORY-013)
- MAS composition sweep: `SweepRunner` for N×M×P benchmarking with CC headless baseline, 33 tests (STORY-007)
- CC artifact collection scripts with docs and tests (STORY-004)
- Spec-constrained mock tests for trace collection, review persistence, log config, logfire instrumentation
- UserStory.md: report generation user story and success criterion (Sprint 8 Feature 6 traceability)
- PRD-Sprint7-Ralph.md and PRD-Sprint8-Ralph.md
- Ralph: baseline-aware validation, process management, story-scoped lint, per-story baseline persistence, timeout protection

### Changed

- Makefile: renamed recipes for clarity (`ruff`→`lint_src`, `ruff_tests`→`lint_tests`, `test_all`→`test`, `test_quick`→`test_rerun`, `sweep`→`run_sweep`, `quick_start`→`quickstart`, `dataset_get_smallest`→`dataset_smallest`, `run_puml_*`→`plantuml_*`, `run_markdownlint`→`lint_md`); backward-compat aliases preserved
- Makefile: collapsed 3 Ollama setup variants into `OLLAMA=1` flag on `setup_prod`/`setup_dev`/`setup_devc`
- Makefile: grouped `make help` output with section headers from `# MARK:` comments
- Makefile: renamed MARK sections for consistency (`Sanity`→`quality`, `run ollama`→`ollama`, etc.)
- `--paper-number` renamed to `--paper-id` (string, supports arxiv IDs); `--provider` renamed to `--chat-provider` across CLI, sweep, config (STORY-012)
- `SweepConfig.paper_numbers: list[int]` → `paper_ids: list[str]`; added `judge_provider`, `judge_model`, `engine`, `cc_teams` fields (STORY-012, STORY-013, STORY-006)
- `render_sidebar()` accepts `execution_state` parameter; shows in-progress indicator when running (STORY-007)
- Engine selector `st.radio` now includes `help=` text explaining MAS vs Claude Code (STORY-007)
- Paper selectbox `st.selectbox` now includes `help=` kwarg (STORY-007)
- `_render_paper_selection_input` no-papers message changed from "Downloads page" to `make setup_dataset_sample` CLI instruction (STORY-007)
- `run_cli.py` CC branch now delegates to `cc_engine.run_cc_solo` / `run_cc_teams` (removes inline subprocess logic) (STORY-006)
- `sweep_runner._invoke_cc_comparison` delegates to `cc_engine`; `_run_cc_baselines` wires through `CCTraceAdapter` (STORY-006)
- `app.main()` now accepts `engine` parameter; `run_app._execute_query_background` passes it through (STORY-006)
- Makefile `cc_run_solo` / `cc_run_teams` recipes use Python CLI entry point instead of shell scripts (STORY-006)
- `JudgeSettings.tier2_provider` default changed from `"openai"` to `"auto"` — judge inherits MAS chat provider at runtime (STORY-011)
- 429 errors in `agent_system.py` now re-raise `ModelHTTPError` instead of `SystemExit(1)`, enabling caller retry logic (STORY-013b)
- PeerRead review score fields coerce int→str via `BeforeValidator(str)` to handle numeric JSON values (STORY-009)
- PeerRead `_create_review_from_dict` aggregates missing optional fields into single debug log line (STORY-008)
- Composite scoring tests consolidated: 3 files → 1 (`test_composite_scorer.py`) with BDD structure template in conftest (STORY-007)
- Removed 3 FIXME dead code blocks from `agent_system.py` and `orchestration.py` (STORY-007)
- PlantUML diagrams updated: `metrics-eval-sweep` (sweep workflow + CC path), `MAS-Review-Workflow` (MAESTRO security boundaries) (STORY-006)
- Docs: architecture.md v3.7.0 — Sprint 8 scope, report generation section, CC stream-json integration, ADR-008 status, researcher tool update
- Docs: roadmap.md v4.3.0 — Sprint 8 description aligned with PRD scope
- Docs updated: README v4.0.0, architecture.md (benchmarking + security sections), roadmap, CC OTel analysis corrected (STORY-003/004/005)
- CC baseline scripts renamed: `collect-cc-solo.sh` → `run-cc.sh`, `collect-cc-teams.sh` → `collect-team-artifacts.sh`
- ADR-008: CC baseline engine subprocess vs SDK decision
- Testing best practices: added mock safety rules (`spec=RealClass`) and unspec'd mock anti-pattern
- Ralph: staleness detection, story-scoped commit scanning, complexity checks, sandbox compatibility (`sed -n '1p'`)

### Removed

- `scripts/collect-cc-traces/` shell scripts directory — replaced by `cc_engine.py` Python module (STORY-006)
- Makefile: dead recipes `setup_devc_full`, `setup_devc_ollama_full`, `output_unset_app_env_sh`
- Legacy config keys `paper_numbers` and `provider` in sweep JSON — use `paper_ids` and `chat_provider`
- `"not-required"` API key sentinel in `create_simple_model` — `None` lets SDK fall back to env vars
- 3 composite scoring test files merged into `test_composite_scorer.py` (STORY-007)
- Deprecated examples: `run_evaluation_example*.py`, `run_simple_agent_*.py`, `utils/`, `config.json` (STORY-001)

### Fixed

- Judge 401 auth failures: validated API key now forwarded through `_resolve_provider_key` → `select_available_provider` → `create_judge_agent` instead of being discarded
- `run_cli.py` CLI parser: space-separated args (`--paper-id 1105.1072`) now parsed correctly instead of treating value flags as booleans

- `CCTraceAdapter._extract_coordination_events()` stub now parses `inboxes/*.json` messages (STORY-014)
- `test_download_success_mocked` AttributeError — patched correct import path (STORY-007)
- `agent_system.py`: `result.output` instead of deprecated `result.data`
- `trace_processors.py`: `end_execution()` now idempotent
- `logfire_instrumentation.py`: correct "Phoenix"/"Logfire" init log messages
- `review_persistence.py`: reviews saved under project root, not `src/app/`
- Log paths aligned to `logs/Agent_evals/` (`config_app.py`, `judge/settings.py`)
- Ralph: story-scoped lint (no pre-existing violations), restart baseline isolation, validate scope

### Changed (Sprint 6)

- STORY-015: Executed Sprint 5 test audit refactoring plan — deleted ~61 implementation-detail tests from `test_trace_store.py` (basic CRUD and metadata tests) while preserving all behavioral coverage (thread-safety, context manager tests retained)
- STORY-014: Fixed failing test expectations to match actual behavior — removed tests for non-existent error propagation, empty string validation, corrupted PDF errors
- STORY-009: Review tools enabled by default; `--no-review-tools` to opt out
- STORY-008: Review tools routed to researcher agent (was manager-only); single-agent fallback preserved
- STORY-001: Complete Opik removal (~140 lines) — replaced 13 references with Phoenix/Logfire equivalents
- Logfire scrubbing: `get_logfire_scrubbing_patterns()` returns only 7 extra patterns not covered by Logfire defaults

### Fixed (Sprint 6)

- STORY-013: Log scrubbing edge cases — natural language patterns ("password to"), broadened OpenAI key regex to `sk-\S+`
- STORY-003: CCTraceAdapter supports sibling and legacy directory layouts with auto-discovery; `--cc-teams-tasks-dir` flag
- STORY-002: Phoenix Docker recipe (persistent volume, gRPC 4317, auto-restart); graph renders when `execution_id` exists
- SSRF allowlist: added `api.github.com`, removed 3 unused LLM provider domains

### Removed (Sprint 6)

- STORY-006: Orphaned `cc_otel` module and tests — wrong abstraction for CC tracing

### Security (Sprint 6)

- STORY-010 **(CRITICAL)**: CVE-2026-25580 SSRF mitigation — URL validation with HTTPS-only + domain allowlist in `datasets_peerread.py` (49 tests). CVE advisories in `SECURITY.md`
- STORY-011 **(HIGH)**: Prompt injection mitigation — input sanitization with length limits + XML delimiter wrapping in LLM judge prompts (25 tests)
- STORY-012 **(HIGH)**: Log/trace data scrubbing — pattern-based redaction for API keys, passwords, tokens in Loguru sinks and Logfire OTLP exports (13 tests)

### Added (Sprint 5)

- STORY-001: Tier 2 judge provider fallback chain (`tier2_provider=auto`)
- STORY-002: Token limit override (CLI `--token-limit`, GUI, env var)
- STORY-003: Single-agent mode detection + weight redistribution
- STORY-004: PeerRead optional field handling ("UNKNOWN" defaults)
- STORY-006: Streamlit background execution with session state persistence
- STORY-007: Debug log panel (`LogCapture`, loguru sink, HTML output)
- STORY-008: Graph visualization wiring (GraphTraceData→NetworkX→GUI)
- STORY-009: Editable judge settings page with pipeline plumbing
- STORY-010: MAESTRO 7-layer security review (2 critical CVEs found)
- STORY-014: wandb import guard tests

### Changed (Sprint 5)

- STORY-016: PeerRead tools moved from manager to researcher in multi-agent mode
- STORY-008: `main()` returns dict; complexity 19→10 via extracted helpers
- STORY-011: Deleted 31 implementation-detail tests (no behavioral coverage loss)
- STORY-005: README, roadmap, architecture docs updated

### Removed (Sprint 5)

- STORY-017: Duplicate `AppEnv` class from `load_settings.py`
- STORY-011: `test_opik_removal.py` and `test_migration_cleanup.py`
- STORY-014: Dead agentops code from `login.py`

### Fixed (Sprint 5)

- STORY-012: OTLP endpoint double-path bug (HTTP 405)
- STORY-013: Tool `success_rate` overwrite; agent-tool edge weight averaging; dead `communication_overhead` metric
- STORY-014: wandb/weave import guards; `WANDB_ERROR_REPORTING` defaults to "false"
- STORY-015: Debug log in `get_api_key()` for empty .env strings
- STORY-004: PeerRead papers 304-308, 330 — `.get()` for optional review fields

### Security (Sprint 5)

- STORY-010: **CRITICAL** — CVE-2026-25580 (PydanticAI SSRF), CVE-2026-25640 (Stored XSS)
- STORY-010: **MEDIUM** — CVE-2024-5206 (scikit-learn data leakage)
- STORY-010: 31 findings across 7 MAESTRO layers — mitigations in `docs/reviews/sprint5-code-review.md`

### Added (Sprint 2)

- STORY-001: `JudgeSettings` pydantic-settings class replacing `config_eval.json`
- STORY-002: Post-run evaluation wiring with `--skip-eval` CLI flag
- STORY-003: `TraceCollector` integration into agent orchestration with `GraphTraceData` support
- STORY-004: Graph vs text metric comparison logging in evaluation pipeline
- STORY-005: Logfire + Phoenix tracing infrastructure (replacing Opik)
- STORY-006: Streamlit evaluation dashboard with agent graph visualization

### Added (Sprint 3)

- STORY-007: Plugin architecture with `EvaluatorPlugin` base class and `PluginRegistry`
- STORY-007: `JudgeAgent` orchestrator replacing `EvaluationPipeline`
- STORY-007: `TraceStore` for thread-safe trace storage
- STORY-007: Plugin wrappers for all three evaluation tiers
- STORY-009: `cc_otel` module for Claude Code OpenTelemetry instrumentation with Phoenix OTLP backend
- STORY-010: GUI settings page displays actual values from `CommonSettings` and `JudgeSettings` pydantic-settings classes
- STORY-010: GUI prompts page loads directly from `ChatConfig.prompts` without hardcoded fallback
- STORY-011: Property-based tests using Hypothesis for score bounds, input validation, and math invariants
- STORY-011: Snapshot tests using inline-snapshot for Pydantic model dumps and structure regression
- STORY-012: Optional weave dependency group in `pyproject.toml` (only loaded when `WANDB_API_KEY` is set)
- STORY-013: Trace logging to all 6 PeerRead manager tools (get_peerread_paper, query_peerread_papers, read_paper_pdf_tool, generate_paper_review_content_from_template, save_paper_review, save_structured_review) with time.perf_counter() timing
- STORY-013: Property-based tests for trace event schema invariants (agent_id always present in tool_call dicts)
- STORY-013: Snapshot tests for GraphTraceData transformation output structure
- STORY-014: Session state initialization for provider and sub-agent configuration in run_gui.py
- STORY-014: Provider selectbox with all PROVIDER_REGISTRY options on Settings page
- STORY-014: Checkboxes for include_researcher/analyst/synthesiser on Settings page
- STORY-014: Run App page reads configuration from session state and displays current settings
- STORY-014: Session state persistence across page navigation for provider and agent selection

### Added (Sprint 4)

- Sprint 4 PRD v2 with Features 1-7 (standalone numbering, operational resilience + Claude Code baseline comparison)
- Feature 1 (STORY-001): Graceful Logfire trace export failure handling (suppress connection error stack traces for both span and metrics exports, affects CLI and GUI)
- Feature 2 (STORY-002): Thread-safe timeout handling in graph analysis using ThreadPoolExecutor (replaces signal-based timeouts)
- Feature 3 (STORY-003): Tier 2 judge provider fallback integration tests and troubleshooting documentation
- Feature 3 (STORY-003): Auth failure detection in all Tier 2 assessments (technical_accuracy, constructiveness, planning_rationality) with neutral fallback scores (0.5)
- Feature 7 (STORY-007): CLI `--cc-solo-dir` and `--cc-teams-dir` flags for baseline comparison against Claude Code artifacts
- Feature 7 (STORY-007): `_run_baseline_comparisons()` function in app.py for evaluating Claude Code solo and teams baselines
- Feature 7 (STORY-007): `render_baseline_comparison()` GUI section for side-by-side metrics display and three-way comparison tables
- Feature 7 (STORY-007): CLI baseline comparison logging with summary output for each pairwise comparison
- Feature 4 (STORY-004): Complete test suite alignment with hypothesis and inline-snapshot (no BDD/Gherkin)
- Feature 5 (STORY-005): Claude Code trace adapter for solo and teams modes parsing Claude Code artifacts into GraphTraceData format
- Feature 4 (STORY-004): Hypothesis property-based tests for data validation invariants, score bounds, URL construction, execution traces, and metrics output
- Feature 4 (STORY-004): Inline-snapshot regression tests for Pydantic model dumps, configuration outputs, benchmark results, and GUI state structures
- Feature 4 (STORY-004): Test coverage for integration tests (PeerRead dataset compatibility), benchmarks (performance baselines), GUI pages (evaluation/graph/sidebar), and data utilities (datasets_peerread)
- Feature 3 (STORY-003): `docs/best-practices/troubleshooting.md` with provider fallback chain guidance
- Feature 4: Complete test suite alignment (hypothesis property tests + inline-snapshot regression tests for remaining 12 test files)

### Fixed (Sprint 4)

- Feature 2 (STORY-002): Thread-safe graph analysis timeout handling
  - Replace signal-based timeout with `concurrent.futures.ThreadPoolExecutor`
  - Fix "signal only works in main thread" error in Streamlit GUI
  - `path_convergence` calculation now works in non-main threads
  - Graceful fallback to 0.3 when timeout occurs (maintains existing behavior)
  - Added 5 comprehensive tests for thread-safe timeout behavior

### Fixed (Sprint 4)

- STORY-001: Noisy ConnectionRefusedError stack traces when Logfire/OTLP endpoint unreachable (both CLI and GUI)
- Feature 5 (STORY-005): Claude Code trace adapter -- parse Claude Code artifacts into `GraphTraceData` in two modes: solo (single Claude Code instance, no orchestration) and teams (Claude Code Agent Teams with delegation), both with full tool/plugin/MCP access
- Feature 6 (STORY-006): Baseline comparison engine -- `BaselineComparison` Pydantic model + `compare()`/`compare_all()` for three-way `CompositeResult` diffing (PydanticAI vs Claude Code solo vs Claude Code teams)
  - `compare()` function for pairwise diffing of any two `CompositeResult` instances
  - `compare_all()` convenience function for all three pairwise comparisons
  - Metric-level deltas for all 6 composite metrics (time_taken, task_success, coordination_quality, tool_efficiency, planning_rationality, output_similarity)
  - Tier-level deltas (Tier 1, Tier 2, Tier 3) with graceful handling of missing Tier 2
  - Human-readable comparison summaries with average delta and largest metric difference
  - Property-based tests for delta symmetry (swap inputs → negated deltas)
  - Snapshot tests for model structure and comparison output validation
- Feature 7: CLI & GUI baseline integration -- `--cc-solo-dir` and `--cc-teams-dir` CLI flags, three-way comparison in GUI

### Added

- `inline-snapshot` as supplementary testing tool
- `common` module with shared utilities extracted from scattered helpers
- MAS design principles, security, and plugin design skills
- Sprint 3 PRD with Features 5-15 (plugin architecture, judge fallback, GUI wiring, test alignment)

### Changed

- STORY-013: Logfire instrumentation now initialized at app startup (app.py:207-209) when `JudgeSettings.logfire_enabled=True`
- STORY-013: `_store_trace()` logging enhanced to include full storage path for JSONL + SQLite (trace_processors.py:357)
- STORY-012: `login.py` conditionally imports weave only when `WANDB_API_KEY` is configured
- STORY-012: `app.py` provides no-op `@op()` decorator fallback when weave unavailable
- STORY-008: Consolidated all evaluation code from `app.evals.*` to `app.judge.*`
- STORY-010: GUI settings page refactored from provider selection to read-only settings display with Streamlit expanders
- STORY-010: GUI prompts page updated to load prompts from `ChatConfig` without `PROMPTS_DEFAULT` fallback
- Makefile: DRY refactor of `quick_start`/`dataset_get_smallest` via `_find_smallest_papers` helper; removed redundant `\` from `.ONESHELL` blocks
- Pandoc: configurable LoF/LoT generation and unnumbered title support
- Ralph PRD parser rewritten with typed models and safe updates
- All dependencies updated to latest 2026 versions

### Removed

- STORY-010: `PROMPTS_DEFAULT` hardcoded constant from `gui/config/config.py` (DRY principle - single source of truth in `config_chat.json`)

### Fixed

- STORY-013: `agent_id` now included in tool_call dicts during trace processing (_process_events at trace_processors.py:269, _parse_trace_events at trace_processors.py:377)
- STORY-013: GraphTraceData transformation succeeds with researcher traces (no "missing agent_id" error)
- STORY-013: Manager-only runs now produce non-empty trace data (tools log trace events)
- Cerebras provider 422 error from mixed `strict` tool definitions — added `OpenAIModelProfile` with strict disabled
- Statusline `ctx(left)` accuracy — compute true usable space by subtracting 16.5% autocompact buffer (33k tokens) from remaining percentage; added `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` environment variable support for configurable buffer threshold

### Removed

- STORY-008: Entire `app.evals` module (migrated to `app.judge`)
- STORY-008: Duplicate `src/app/agents/peerread_tools.py` (canonical at `src/app/tools/`)
- Deprecated `config/config_eval.json` (superseded by `JudgeSettings` pydantic-settings)
- Opik tracing from evaluation pipeline (replaced by Logfire + Phoenix)
- Unused `pytest-bdd` and `agentops` dependencies

## [3.3.0] - 2026-02-09

### Added

- `generating-writeup` skill: academic/technical writeup generation with pandoc citation support, IEEE `[1]` default style, and `template.md` for document structure
- Pandoc `--citeproc` integration: `BIBLIOGRAPHY` and `CSL` variables in `make run_pandoc`, auto-resolves IEEE CSL from `scripts/writeup/citation-styles/ieee.csl`
- Claude Code Skills infrastructure (5 skills): core-principles (KISS, DRY, YAGNI), designing-backend, implementing-python, reviewing-code, generating-prd
- Ralph Loop autonomous execution system (.claude/scripts/ralph/): ralph.sh orchestrator, prompt.md, init.sh
- Template-based state file management (.claude/templates/ralph/): prd.json.template, progress.txt.template
- Makefile recipes for Ralph: ralph_init, ralph, ralph_status, ralph_clean
- AGENTS.md Claude Code Infrastructure section with Skills and Ralph Loop references
- Comprehensive benchmark catalog expansion: 40+ benchmarks from further_reading.md integrated into landscape-evaluation-data-resources.md across 10 categories (General Agent, Web Agents, Code/SE, Tool Use, Scientific, Enterprise, Multi-Agent, Safety/Security, Planning, Specialized Domains). Key additions: **CORE-Bench** (computational reproducibility - highly relevant for PeerRead), **MultiAgentBench** (multi-agent coordination evaluation), WebArena/VisualWebArena/BrowserGym (web interaction), ToolLLM/MetaTool/StableToolBench (tool usage), CLEAR framework (enterprise metrics with ρ=0.83 production correlation), safety benchmarks (SALAD-Bench, Agent-SafetyBench, SafeAgentBench, AgentHarm, WASP, CyberGym)
- Research paper expansion: 232+ papers covering 2020-2026 (from 154+)
- Practitioner resources section in further_reading.md with Anthropic engineering insights
- Evaluation frameworks: Inspect AI (UK AISI, PydanticAI support), Bloom (behavioral evals), Petri (alignment auditing), DeepEval (three-layer evaluation model)
- DeepEval integration analysis: Three-layer model (Reasoning/Action/Execution), component-level metrics, GEval custom criteria
- Failure mode taxonomy from Anthropic harness pattern mapped to evaluation metrics
- Key benchmarks from survey papers: GAIA, API-Bank, SALAD-Bench, Agent-SafetyBench, SafeAgentBench, AgentHarm
- AgentBeats Competition benchmarks (20 added): Scientific (SciCode, CORE-Bench), Web (BrowserGym, Online-Mind2Web, WebShop), Enterprise (Spider 2.0, CRMArena, CRMArena-Pro, Finance, MedAgentBench), Code (AppWorld, USACO, VERINA), Safety (DoomArena, WASP, CyberGym, Smart Contract), Gaming/Embodied (Werewolf, Minecraft, ALFWorld, PersonaGym), Legal (LegalAgentBench)
- AgentBeats Competition participation guide (AgentBeats_basics.md): OUTSTANDING opportunities for Research Agent Track ($16k), Multi-Agent Track (category-defining), and AAA Track with dual-track submission strategy, implementation roadmap, and immediate next steps
- Tool evaluation expansion: τ²-bench (2506.07982) dual-control user-agent evaluation
- OS/Web benchmarks: OSWorld (2404.07972) comprehensive task evaluation
- Memory systems research: MAGMA, MACLA, comprehensive memory surveys
- Enterprise evaluation frameworks: CLEAR (ρ=0.83), AgentArch, TheAgentCompany, MultiAgentBench
- Pydantic Evals to Practitioner Resources: Span-based evaluation with OpenTelemetry, Logfire integration, philosophy validates post-execution behavioral analysis
- Arize Phoenix Multi-Agent to Practitioner Resources: Three evaluation strategies (Agent Handoff, System-Level, Coordination), multi-level metrics, five coordination patterns
- Production Framework Integration Matrix: Added Pydantic Evals and Arize Phoenix rows (now 10 frameworks)
- New candidate metrics from production frameworks: path_convergence (Arize Phoenix), handoff_quality (Arize Multi-Agent), semantic_outcome (LangSmith), evaluator_alignment (Self-Improving Evals)
- Research papers: Rubric Rewards AI Co-Scientists [2512.23707], SWE-EVO long-horizon benchmark [2512.18470], Confucius Code Agent [2512.10398], SciSciGPT [2504.05559]
- New Metrics for Implementation section in architecture.md: fix_rate, rubric_alignment, path_convergence, handoff_quality
- SWE-EVO benchmark to landscape-evaluation-data-resources.md with Fix Rate metric for partial progress evaluation
- SciSciGPT to landscape-research-agents.md with LLM Agent capability maturity model
- Research Plan Evaluation methodology to research_integration_analysis.md: rubric-based self-grading, long-horizon partial progress, hierarchical memory assessment
- Claude Evaluation Framework to Practitioner Resources: SMART criteria, grading hierarchy (Code→LLM→Human), Bloom correlation 0.86
- Claude Eval Framework to Integration Matrix (now 11 frameworks): validates three-tier approach
- Clear audience targeting for all main documentation files
- PyPI verification requirement for new package introductions in AGENTS.md
- architecture.md: Comprehensive system architecture documentation
- landscape analysis: AI agent ecosystem split into focused documents (landscape.md overview, landscape-agent-frameworks-infrastructure.md, landscape-evaluation-data-resources.md)
- agent_eval_metrics.md: Evaluation metrics catalog
- Comprehensive three-tier evaluation pipeline test with realistic scientific paper data
- Full pipeline workflow demonstration with PeerRead-compatible data models
- Performance monitoring and observability testing with trace collection
- Error handling and fallback strategy validation across all evaluation tiers
- Task 4.3: Complete PeerRead integration validation framework with 7 comprehensive test files
- Real dataset validation testing for PeerRead data compatibility and performance
- Composite scoring validation with 5 performance scenarios and edge case testing
- Performance baseline documentation with empirical analysis and optimization recommendations
- Enhanced integration testing with multi-paper scenarios and production readiness validation

### Changed

- AGENTS.md: Added Skills and Ralph infrastructure references, updated Agent Role Boundaries section
- Ralph scripts location: Moved from scripts/ralph/ to .claude/scripts/ralph/
- Research integration analysis: Updated to 208+ papers with 2022-2026 coverage (version 3.0.0)
- Further reading document: Enhanced with 54 new papers including safety benchmarks and memory systems
- Research validation references: Added CLEAR framework and evaluation taxonomy citations
- Enhanced error handling in evaluation pipeline with detailed context logging and specific guidance for different error types
- Improved performance monitoring with bottleneck detection and comprehensive metrics collection
- Enhanced fallback strategy reliability with better status reporting and detailed failure tracking
- Added configuration validation to prevent invalid pipeline configurations
- Improved logging throughout pipeline execution with performance insights and failure analysis

### Fixed

- Evaluation pipeline integration: Fixed data model field name mismatches in composite scorer tests
- Test integration issues: Corrected field mappings between Tier3Result model and composite scorer expectations
- trace_observe_methods.md: Observability analysis
- Modular architecture with functional separation: agents/, evals/, llms/, tools/
- LLM provider abstraction layer with multi-provider support
- Agent factory patterns for creating specialized agents
- Evaluation engine orchestration and management systems
- Configuration-based prompt management for evaluation agents
- Comprehensive docstrings for all major modules (agents/, data_models/, config/)
- GitHub models integration with OpenAI-compatible API
- Three-tier evaluation system with traditional metrics, LLM-as-judge, and trace collection
- Typed Pydantic models for LLM assessment results (TechnicalAccuracyAssessment, ConstructivenessAssessment, PlanningRationalityAssessment)
- Composite scoring system integrating all three evaluation tiers into unified assessment
- MetricNormalizer with six normalization functions for consistent scoring ranges
- CompositeScorer with weighted aggregation of normalized metrics
- RecommendationEngine with threshold-based paper acceptance recommendations
- TierIntegrationManager orchestrating fallback handling for missing evaluation tiers
- Performance-optimized composite scoring achieving <100ms latency target
- Comprehensive test suite with >95% coverage for composite scoring system
- Enhanced type safety with explicit type annotations for trace processors and evaluation pipelines
- Modern datetime handling with timezone-aware UTC timestamps
- Comprehensive exception handling patterns for evaluation fallback mechanisms

### Changed

- Documentation structure: clarified purpose statements for README.md (humans), AGENTS.md (agents), CONTRIBUTING.md (shared)
- AGENTS.md: streamlined content, removed duplicated architecture information
- CHANGELOG.md: reduced boilerplate, consolidated change type descriptions
- README.md: major reorganization, moved detailed content to dedicated docs
- Restructured codebase from monolithic to modular architecture
- Migrated LLM functionality from single file to focused modules
- Updated GUI import paths to use new modular structure
- Refactored agent creation to use configuration-based prompts
- Shortened evaluation prompt strings for improved readability

### Fixed

- Import errors after architectural restructuring
- Line length violations in evaluation modules
- CLI argument parsing for proper provider selection
- GUI import paths to work with new module structure
- Time score calculation in traditional metrics to prevent negative values
- PydanticAI deprecation warnings where feasible
- Datetime deprecation warnings by migrating to datetime.now(datetime.UTC)
- Type safety issues in trace processors with explicit type annotations
- BaseException type issues in evaluation pipelines with proper exception handling
- LLM assessment model definitions with comprehensive Pydantic validation
- Data model imports using direct module references instead of `__init__.py` exports
- Graph analysis engine configuration validation now allows partial weight specifications for improved usability
- Test data structures in graph analysis tests to include required fields
- NetworkX error handling test expectations to match actual fallback behavior

### Removed

- Obsolete context/ directory and .claude/commands framework references
- FRP (Feature Requirements Prompt) command references from documentation
- Redundant architecture details from AGENTS.md
- Monolithic llm_model_funs.py file after successful migration

## [3.2.0] - 2025-08-19

### Added

- Evaluation engine for PeerRead dataset
- Documentation updates: separation of human and agent files, clear CONTRIBUTING.md

### Fixed

- Cleaned up obsolete documentation and logs, removed outdated markdown files and datasets

## [3.1.0] - 2025-08-10

### Added

- Inspected paper visualization
- PlantUML local  generation with Docker

### Changed

- Updated project documentation
- Sprint plans
- PlantUML diagrams with CSS for better clarity and consistency

## [3.0.0] - 2025-08-03

### Added

- MAS review engine using PeerRead dataset

### Changed

- Agent Context

## [2.1.0] - 2025-07-25

### Added

- PeerRead dataset functionality
- PeerRead agent usage documentation to reflect new architecture with `data_models` instead of `datamodels` path structure
- Eval functionality in separate system
- Gemini CLI as fallback for Claude Code CLI

## [2.0.0] - 2025-07-06

### Added

- Claude Code CLI commands and settings

## [1.1.0] - 2025-07-05

### Added

- Makefile command and devcontainer.json for Claude Code CLI usage

### Changed

- Moved streamlit_gui and examples to /src
- Moved app to /src/app

## [1.0.0] - 2025-03-18

### 2025-03-18

- refactor(agent,streamlit): Convert main and run_manager functions again to async for streamli output
- fix(prompts): Update system prompts for manager,researcher and synthesiser roles to remove complexity
- chore(workflows): Update action versions in GitHub workflows for consistency
- chore(workflows): Update action versions for deploy docs to pgh-pages
- docs(deps): Add documentation dependencies for MkDocs and related plugins to pyproject.toml

### 2025-03-17

- feat(main,agent): refactor entry point to support async execution and enhance login handling
- feat(cli,login,log): refactor entry point to integrate Typer, enhance logging, added login every run
- feat(streamlit): replace load_config with load_app_config, enhance sidebar rendering, and improve output rendering with type support
- feat(streamlit): enhance render_output function with detailed docstring and improve query handling in run_app
- feat(streamlit): enhance render_output function with additional info parameter and improve output handling in run_app
- feat(streamlit,app): add Typer dependency, update main entry point for async execution, add streamlit provider input
- feat(agent): update configuration and improve agent system setup with enhanced error handling and new environment variables
- feat(config,login,catch): add inference settings with usage limits and result retries, enhance login function to initialize environment and handle exceptions, comment out raise in error handling context to prevent unintended crashes
- feat(login,catch): integrate logfire configuration in login function and improve error handling context

### 2025-03-16

- feat(devcontainer): Refactor devcontainer setup: remove old configurations and add new setup targets for development and Ollama
- feat(devcontainer): Changed from vscode to astral-sh devcontainer
- feat(devcontainer): Changed to vscode container, added postcreatecommand make setup_env
- feat(devcontainer): restructure environment setup with new devcontainer configurations
- feat(devcontainer): update environment names for clarity in devcontainer configurations
- refactor(agent): Added AgentConfig class for better agent configuration management, Refactored main function for streamlined agent initialization.
- feat(config,agents): Update model providers and enhance configuration management, examples: Added new model providers: Gemini and OpenRouter, src: Enabled streaming responses in the agent system
- chore: Remove unused prompt files, update configuration, and enhance logging setup
- refactor(exception,logfire): Enhance error handling and update model configurations in agent system

### 2025-03-14

- feat(scalene): Add profiling support and update dependencies
- refactor(Makefile): Improve target descriptions and organization

### 2025-03-13

- refactor(API,except): .env.example, add OpenRouter configuration, enhance error handling in run_simple_agent_system.py, and update ModelConfig to allow optional API key.
- feat(streamlit): add Streamlit app structure with header, footer, sidebar, and main content components
- feat(streamlit): enhance Streamlit app with detailed docstrings, improved header/footer, and refined main content layout
- feat(makefile,streamlit): update Makefile commands for CLI and GUI execution, and modify README for usage instructions, add streamlit config.toml
- feat(streamlit): restructure Streamlit app by removing unused components, adding new header, footer, sidebar, and output components, and updating configuration settings
- chore: replace app entrypoint with main, remove unused tools and tests, and update makefile for linting and type checking
- chore: Enhance makefile with coverage and help commands, update mkdocs.yaml and pyproject.toml for improved project structure and documentation
- test: Update makefile for coverage reporting, modify pyproject.toml to include pytest-cov, and adjust dependency settings
- test: Add coverage support with pytest-cov and update makefile for coverage reporting
- test: makefile for coverage reporting, update dependencies in pyproject.toml for improved testing and coverage support
- chore: Remove redundant help command from makefile
- refactor(agent,async): Refactor agent tests to use async fixtures and update verification methods for async results
- fix(Dockerfile): Remove unnecessary user creation and pip install commands from Dockerfile
- feat(agent): Update dependencies and add new example structures; remove obsolete files
- chore(structure): simplified agents.py
- fix(pyproject): Replace pydantic-ai with pydantic-ai-slim and update dependencies
- feat(examples): add new examples and data models; update configuration structure
- feat(agent): update dependencies, enhance examples, and introduce new data models for research and analysis agents
- feat(examples): enhance prompts structure and refactor research agent integration
- feat(examples): improve documentation and enhance error handling in agent examples
- feat(agent): Added data models and configuration for research and analysis agents, Added System C4 plantuml
- feat(weave,dependencies): update dependencies and integrate Weave for enhanced functionality in the agent system
- feat(agent): initialize agentops with API key and default tags for enhanced agent functionality
- feat(agent): integrate logfire for logging and configure initial logging settings
- feat(agent): adjust usage limits for ollama provider to enhance performance
- feat(agent): refine system prompts and enhance data model structure for improved agent interactions
- feat(agent): update system prompts for improved clarity and accuracy; add example environment configuration
- feat(agent): enhance agent system with synthesiser functionality and update prompts for improved coordination
- feat(agent): add Grok and Gemini API configurations; initialize logging and agent operations
- feat(agent): improve documentation and refactor model configuration handling for agent system
- feat(agent): update environment configuration, enhance logging, and refine agent management functionality
- feat(agent): refactor login handling, update model retrieval, and enhance agent configuration

## [0.0.2] - 2025-01-20

### Added

- PRD.md
- C4 architecture diagrams: system context, code
- tests: basic agent evals, config.json

### Changed

- make recipes

## [0.0.1] - 2025-01-20

### Added

- Makefile: setup, test, ruff
- devcontainer: python only, w/o Jetbrains clutter from default devcontainer
- ollama: server and model download successful
- agent: tools use full run red
- pytest: e2e run, final result red
- Readme: basic project info
- pyproject.toml
