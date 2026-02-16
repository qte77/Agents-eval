<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Fixed (Sprint 6 - STORY-003)

- CCTraceAdapter: supports both sibling (`~/.claude/teams/` + `~/.claude/tasks/`) and legacy child layout with automatic discovery
- CLI flag `--cc-teams-tasks-dir` for explicit tasks directory (optional, auto-discovered by default)

### Added (Ralph Monitoring)

- Process management: `make ralph_stop`, `make ralph_watch`, `make ralph_get_log`
- Timeout protection: `make ralph_run RALPH_TIMEOUT=3600` prevents infinite hangs

### Fixed (Sprint 6 - STORY-002)

- Phoenix Docker recipe: persistent volume, gRPC port (4317), auto-restart, stale container cleanup
- Agent interaction graph renders when `execution_id` exists regardless of evaluation success

### Removed (Sprint 6 - STORY-001)

- Complete Opik removal (~140 lines instrumentation, Docker stack, data model fields, Makefile targets, env vars, tests, docs) — replaced by Logfire/Phoenix in Sprint 4

### Changed (Sprint 6 - STORY-001)

- Replaced 13 Opik references with Phoenix/Logfire equivalents in docs and docstrings

### Added (Sprint 5)

- STORY-001: Tier 2 judge provider fallback chain — `select_available_provider()`, `tier2_provider=auto` mode, `tier2_available` skip flag, Hypothesis property tests
- STORY-002: Token limit override — CLI `--token-limit`, GUI input, `AGENT_TOKEN_LIMIT` env var; priority: CLI/GUI > env > config; bounds 1000–1000000
- STORY-003: Single-agent mode — detection from trace data, weight redistribution (excludes `coordination_quality`), compound redistribution for Tier 2 skip + single-agent, `evaluate_composite_with_trace()`, Hypothesis property tests
- STORY-004: PeerRead optional field handling — "UNKNOWN" defaults for missing review fields, Hypothesis property tests
- STORY-006: Streamlit background execution — session state persistence, progress spinner, navigation resilience
- STORY-007: Debug log panel — `LogCapture` utility, loguru sink, HTML color-coded levels, persistence during background execution
- STORY-008: Graph visualization wiring — `graph_builder.py` (GraphTraceData→NetworkX), session state for results/graphs, real-time data to Evaluation/Graph tabs
- STORY-009: Editable judge settings page — timeouts, thresholds, provider/model, observability toggles, "Reset to Defaults", `judge_settings` plumbed through pipeline
- STORY-010: MAESTRO 7-layer security review — code audit, Context7/Exa MCP verification, 2 critical CVEs in PydanticAI dependencies
- STORY-014: Test suite for wandb import guard behavior and telemetry settings

### Changed (Sprint 5)

- STORY-016: PeerRead tools moved from manager to researcher in multi-agent mode; single-agent retains tools on manager
- STORY-008: `main()` returns `dict` with `composite_result`/`graph` keys; complexity 19→10 via extracted helpers
- STORY-011: Deleted 31 implementation-detail tests (595→564, no behavioral coverage loss)
- STORY-005: README, roadmap, architecture docs updated for Sprint 5
- AGENT_LEARNINGS.md condensed ~25% with YAML frontmatter

### Removed (Sprint 5)

- STORY-017: Duplicate `AppEnv` class and module-level `chat_config` from `load_settings.py` — canonical in `app.data_models.app_models`
- STORY-011: `test_opik_removal.py` and `test_migration_cleanup.py`
- STORY-014: Dead agentops commented code from `login.py`

### Fixed (Sprint 5)

- STORY-012: OTLP endpoint double-path bug — base URL instead of traces-specific endpoint (HTTP 405)
- STORY-013: Tool `success_rate` tracks all calls instead of overwriting with last outcome
- STORY-013: Agent-tool edge weights averaged across repeated calls; removed dead `communication_overhead` metric
- STORY-014: wandb/weave imports guarded with try/except; `WANDB_ERROR_REPORTING` defaults to "false"
- STORY-015: Debug log in `get_api_key()` for diagnosing empty .env strings
- STORY-004: PeerRead papers 304-308, 330 — `.get()` for optional review fields, improving dataset coverage

### Security (Sprint 5)

- STORY-010: **CRITICAL** — CVE-2026-25580 (PydanticAI SSRF), CVE-2026-25640 (Stored XSS)
- STORY-010: **MEDIUM** — CVE-2024-5206 (scikit-learn data leakage)
- STORY-010: 31 findings across 7 MAESTRO layers (3 critical, 6 high, 8 medium, 2 low) — mitigations in `docs/reviews/sprint5-code-review.md`

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
- Pandoc `--citeproc` integration: `BIBLIOGRAPHY` and `CSL` variables in `make run_pandoc`, auto-resolves IEEE CSL from `scripts/citation-styles/ieee.csl`
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
