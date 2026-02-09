---
title: Product Requirements Document (PRD) for Agents-eval
description: Comprehensive product requirements document for the multi-agent AI system evaluation framework
date: 2025-09-01
updated: 2026-02-09
category: requirements
version: 3.3.0
---

## Overview

**Agents-eval** is a project aimed at evaluating the effectiveness of open-source agentic AI systems across various use cases. The focus is on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

The project implements a comprehensive evaluation pipeline using the **PeerRead dataset** for scientific paper review assessment, providing a standardized benchmark for measuring multi-agent system performance in complex analytical tasks.

## Goals

- **Evaluate Agentic AI Systems:** Provide a concise evaluation pipeline to assess the performance of agentic AI systems.
- **PeerRead Dataset Integration:** Implement comprehensive evaluation using scientific paper review data to assess agent performance in research analysis tasks.
- **Metric Development:** Develop and implement metrics that are agnostic to specific use cases but measure core agentic capabilities.
- **Multi-Agent System Assessment:** Evaluate the effectiveness of agent delegation, coordination, and specialized task handling.
- **Continuous Improvement:** Promote continuous improvement through automated testing, version control, and documentation.

## Functional Requirements

### CLI

- **Command Line Interface:** See [CONTRIBUTING.md § Complete Command Reference](../CONTRIBUTING.md#complete-command-reference) for setup, validation, testing, and execution commands
  - Multi-agent system orchestration with delegation capabilities

### Frontend (Streamlit)

- **User Interface:**
  - Display test results and system performance metrics.
  - Interactive dashboard for PeerRead evaluation results.
  - Multi-agent system performance visualization.
  - Real-time monitoring of agent execution and delegation.

### Sprint 2: Plugin-Based Judge Architecture

#### Feature 5: Shared Infrastructure Module

- **Description**: Extract shared utilities into `common/` module with pydantic-settings configuration following [12-Factor #3 (Config)](../best-practices/mas-design-principles.md) and [MAESTRO Integration Layer](../best-practices/mas-security.md).
- **Acceptance Criteria**:
  - [ ] `common/` module with log + error_messages + shared models + CommonSettings
  - [ ] `CommonSettings(BaseSettings)` with `EVAL_` env prefix and typed defaults in code
  - [ ] Backward-compatible re-exports from original locations
  - [ ] `make validate` passes
- **Technical Requirements**:
  - Use pydantic-settings BaseSettings pattern with defaults in code (not JSON)
  - Re-export shims for zero-breakage migration
  - All defaults version-controlled, overrides via .env only
- **Implementation Suggestions**:
  ```python
  # src/app/common/settings.py
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class CommonSettings(BaseSettings):
      log_level: str = "INFO"  # Default in code
      enable_opik: bool = False

      model_config = SettingsConfigDict(
          env_prefix='EVAL_',
          env_file='.env',
          env_file_encoding='utf-8'
      )
  ```
- **Best Practices References**:
  - [MAS Design Principles](../best-practices/mas-design-principles.md) - 12-Factor #3, typed boundaries
  - [MAS Security](../best-practices/mas-security.md) - Input validation, secrets management
- **Files**:
  - `src/app/common/__init__.py`
  - `src/app/common/models.py`
  - `src/app/common/settings.py`
  - `src/app/common/log.py`
  - `src/app/common/error_messages.py`

##### 5.1 Model-Aware Content Truncation

- **Description**: Implement token-limit-aware content truncation to prevent 413 errors when paper content exceeds provider rate limits (e.g., GitHub Models free tier enforces 8,000 token request limit for `gpt-4.1`, despite the model supporting 1M tokens natively).
- **Root Cause**: `peerread_tools.py:149` accepts `max_content_length` parameter but never applies it (`TODO` at line 210). Full paper content is sent regardless of model token limits.
- **Acceptance Criteria**:
  - [ ] `CommonSettings` includes per-provider `max_content_length` defaults
  - [ ] `generate_paper_review_content_from_template` truncates `paper_content_for_template` to `max_content_length` before formatting into template
  - [ ] Truncation preserves abstract (always included) and truncates body with `[TRUNCATED]` marker
  - [ ] Warning logged when truncation occurs with original vs truncated size
  - [ ] `make validate` passes
- **Implementation Suggestions**:
  ```python
  # In peerread_tools.py - replace TODO at line 210
  if len(paper_content_for_template) > max_content_length:
      logger.warning(
          f"Paper {paper_id} content ({len(paper_content_for_template)} chars) "
          f"exceeds max_content_length ({max_content_length}). Truncating."
      )
      paper_content_for_template = paper_content_for_template[:max_content_length] + "\n[TRUNCATED]"
  ```
- **Provider Rate Limits** (for reference, distinct from model context windows):
  - GitHub Models free tier `gpt-4.1`: 8,000 tokens/request (~6,000 chars for content after prompt overhead)
  - OpenAI direct `gpt-4-turbo`: 128,000 tokens context
  - Anthropic `claude-3-5-sonnet`: 200,000 tokens context
- **Files**:
  - `src/app/agents/peerread_tools.py` (truncation logic)
  - `src/app/common/settings.py` (per-provider defaults)

#### Feature 6: Plugin-Based Judge Module

- **Description**: Restructure `evals/` into `judge/` with EvaluatorPlugin interface, pydantic-settings, and typed context passing between tiers.

##### 6.1 Judge Settings and Models

- **Acceptance Criteria**:
  - [ ] `JudgeSettings(BaseSettings)` with `JUDGE_` env prefix replacing EvaluationConfig
  - [ ] Typed defaults in code (tier weights, timeouts, model selection)
  - [ ] JSON config deprecated - settings from code defaults + env var overrides only
  - [ ] Evaluation models moved to `judge/models.py` with Pydantic validation
  - [ ] `make validate` passes
- **Implementation Suggestions**:
  ```python
  # src/app/judge/settings.py
  class JudgeSettings(BaseSettings):
      tier_weights: list[float] = [0.3, 0.4, 0.3]  # Default in code
      tier1_max_seconds: int = 30
      tier2_max_seconds: int = 60
      tier3_max_seconds: int = 45
      llm_model: str = "gpt-4o"

      model_config = SettingsConfigDict(
          env_prefix='JUDGE_',
          env_file='.env'
      )

      @field_validator('tier_weights')
      @classmethod
      def validate_weights_sum(cls, v: list[float]) -> list[float]:
          if abs(sum(v) - 1.0) > 0.01:
              raise ValueError("Tier weights must sum to 1.0")
          return v
  ```
- **Best Practices References**:
  - [MAS Design Principles](../best-practices/mas-design-principles.md) - Stateless reducers, typed context
  - [MAS Security](../best-practices/mas-security.md) - Input validation at boundaries
  - [Testing Strategy](../best-practices/testing-strategy.md) - Property tests for weight validation
- **Files**:
  - `src/app/judge/settings.py`
  - `src/app/judge/models.py`

##### 6.2 EvaluatorPlugin Base and Registry

- **Acceptance Criteria**:
  - [ ] `EvaluatorPlugin` ABC with name/tier/evaluate/get_context_for_next_tier
  - [ ] `PluginRegistry` for registration and tier-ordered execution
  - [ ] Typed Pydantic models at all plugin boundaries
  - [ ] Structured error results from plugins
- **Files**:
  - `src/app/judge/plugins/base.py`
  - `src/app/judge/plugins/__init__.py`

##### 6.3 Engine Plugin Adapters

- **Acceptance Criteria**:
  - [ ] TraditionalMetricsPlugin wrapping existing engine
  - [ ] LLMJudgePlugin with opt-in Tier 1 context enrichment
  - [ ] GraphEvaluatorPlugin wrapping existing engine
  - [ ] All existing engine tests pass unchanged
  - [ ] Per-plugin configurable timeouts
- **Files**:
  - `src/app/judge/plugins/traditional.py`
  - `src/app/judge/plugins/llm_judge.py`
  - `src/app/judge/plugins/graph_metrics.py`

##### 6.4 Plugin-Driven Pipeline

- **Acceptance Criteria**:
  - [ ] JudgeAgent replaces EvaluationPipeline using PluginRegistry
  - [ ] Explicit tier execution order in code
  - [ ] Context flows Tier 1 → Tier 2 → Tier 3
  - [ ] TraceStore with thread-safe storage
  - [ ] Graceful degradation preserved
  - [ ] Re-export shim for EvaluationPipeline
- **Files**:
  - `src/app/judge/agent.py`
  - `src/app/judge/trace_store.py`
  - `src/app/judge/composite_scorer.py`
  - `src/app/judge/performance_monitor.py`

#### Feature 7: Migration Cleanup

- **Description**: Remove backward-compatibility shims, update all imports, delete deprecated JSON config.
- **Acceptance Criteria**:
  - [ ] All imports use `judge.`, `common.` paths
  - [ ] No re-export shims remain
  - [ ] `config/config_eval.json` removed
  - [ ] CHANGELOG.md updated
  - [ ] `make validate` passes, no dead code
- **Files**: All source and test files (import updates), `CHANGELOG.md`

#### Feature 8: CC OTel Observability Plugin

- **Description**: Standalone CC telemetry plugin using OTel → Opik pipeline. Enables CC session tracing alongside PydanticAI Opik instrumentation.
- **Acceptance Criteria**:
  - [ ] `src/app/cc_otel/` module with config + enable/disable API
  - [ ] `CCOtelConfig` with env var export
  - [ ] OTel Collector service added to `docker-compose.opik.yaml`
  - [ ] Separate from existing `opik_instrumentation.py`
  - [ ] Graceful degradation when OTel unavailable
  - [ ] `make validate` passes
- **Files**:
  - `src/app/cc_otel/__init__.py`
  - `src/app/cc_otel/config.py`
  - `docker-compose.opik.yaml`

#### Feature 9: CC-Style Evaluation Baselines

- **Description**: Single-Agent and Parallel-Agents baselines (CC orchestration patterns) implemented in PydanticAI for benchmarking against the MAS pipeline.
- **Acceptance Criteria**:
  - [ ] Single-Agent baseline (one agent, one pass, GeneratedReview output)
  - [ ] Parallel-Agents baseline (asyncio.gather researcher + analyst, then synthesizer)
  - [ ] Both scored through same evaluate_comprehensive() pipeline
  - [ ] Reuses existing GeneratedReview output type and AgentFactory
  - [ ] `make validate` passes
- **Files**:
  - `src/app/agents/baselines.py`
  - `tests/test_baselines.py`

#### Feature 9b: Wire Evaluation After Review Generation

- **Description**: Connect `run_manager()` output to `EvaluationPipeline.evaluate_comprehensive()` in the CLI flow. Currently generation and evaluation are disconnected -- `app.py` generates reviews but never scores them. Evaluation should run by default; `--skip-eval` flag to run generation only.
- **Acceptance Criteria**:
  - [ ] After `run_manager()` completes, `EvaluationPipeline` runs automatically comparing generated review against ground-truth PeerRead reviews
  - [ ] `--skip-eval` CLI flag disables evaluation (generation-only mode)
  - [ ] Evaluation results logged and persisted alongside generated review
  - [ ] Graceful skip when no ground-truth reviews available for the paper
  - [ ] `make validate` passes
- **Files**:
  - `src/app/app.py` (wire evaluation call)
  - `src/run_cli.py` (add `--skip-eval` flag)

#### Feature 10: E2E Integration Tests & Multi-Channel Deployment

- **Description**: End-to-end integration tests for full evaluation pipeline and multi-channel API access (FastAPI + MCP server) alongside existing Streamlit UI.
- **Acceptance Criteria**:
  - [ ] E2E integration test covering full pipeline (agent execution → evaluation → scoring)
  - [ ] FastAPI server with `/evaluate` REST endpoint
  - [ ] MCP server exposing evaluation as AI-accessible resource
  - [ ] OpenAPI spec generation for API documentation
  - [ ] Consistent results across CLI/API/MCP/UI channels
  - [ ] Rate limiting and basic auth for API endpoints
  - [ ] `make validate` passes including E2E tests
- **Technical Requirements**: FastAPI for REST, MCP SDK for AI-to-AI integration, keep Streamlit UI as-is
- **Files**:
  - `tests/integration/test_e2e_pipeline.py`
  - `src/app/api/server.py`
  - `src/app/api/routes.py`
  - `src/app/mcp_server/server.py`
  - `src/app/mcp_server/resources.py`

## Non-Functional Requirements

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance per [MAS Design Principles](best-practices/mas-design-principles.md).
  - Implement logging and error handling for debugging and monitoring.
  - Follow stateless reducer pattern for plugin architecture.
- **Documentation:**
  - Comprehensive documentation for setup, usage, and testing.
  - Reference [Testing Strategy](best-practices/testing-strategy.md) for quality assurance approach.
- **Scalability:**
  - Design the system to handle multiple concurrent requests.
  - Thread-safe trace storage and plugin execution.
- **Performance:**
  - Ensure low latency in server responses and model downloads.
  - Optimize for memory usage and CPU/GPU utilization.
- **Security:**
  - Follow [OWASP MAESTRO 7-layer framework](best-practices/mas-security.md) for MAS security.
  - Input validation at all plugin boundaries (Integration Layer).
  - Secrets management via environment variables only (never committed).
  - Structured error handling with graceful degradation (Environment Layer).

## Assumptions

- **Remote Inference Endpoints:** The project uses OpenAI-spec compatible inference providers configured in `config_chat.json` (migrating to Pydantic Settings) with API keys from `.env`.
- **Local Ollama Server:** The project can make use of a local Ollama server for model hosting and inference.
- **Python Environment:** The project uses Python 3.13 and related tools like `uv` for dependency management.
- **GitHub Actions:** CI/CD pipelines are set up using GitHub Actions for automated testing, version bumping, and documentation deployment.

## Constraints

- **Hardware:** The project assumes access to appropriate hardware if running the Ollama server and models, including sufficient RAM and GPU capabilities.
- **Software:** Requires Python 3.13, `uv`, and other dependencies listed in `pyproject.toml`.

## Main Dependencies

### Core Framework

- **pydantic-ai-slim:** Agent framework with DuckDuckGo, OpenAI, and Tavily integrations.
- **pydantic:** Data validation and settings management.
- **pydantic-settings:** Configuration loading from .env and environment variables.

### Data Processing & Evaluation

- **markitdown:** Document processing with PDF support.
- **scikit-learn:** TF-IDF vectorization and cosine similarity for Tier 1 metrics.
- **textdistance:** Multiple text similarity algorithms for Tier 1 metrics.
- **networkx:** Graph analysis for Tier 3 agent coordination and tool usage patterns.

### LLM Providers & Tools

- **httpx:** HTTP client for OpenAI-spec compatible inference providers.

### Monitoring & Logging

- **opik:** Primary trace and observability platform for agent execution monitoring.
- **loguru:** Enhanced logging capabilities.
- **weave:** (Optional) ML experiment tracking and evaluation.
- **logfire:** (Optional) Structured logging and observability.

### Development & Testing

- **pytest:** Testing framework with async support.
- **pytest-asyncio:** Async test execution support.
- **pytest-cov:** Coverage reporting.
- **hypothesis:** Property-based testing for scoring math (Sprint 2).
- **pyright:** Static type checking.
- **ruff:** Code formatting and linting.

### User Interface

- **streamlit:** Interactive web dashboard.

### Documentation

- **mkdocs:** Documentation generation with Material theme.
- **mkdocstrings:** API documentation from docstrings.

### System Dependencies (not in pyproject.toml)

- **ollama:** (Optional) Local model hosting, installed via `make setup_dev_ollama`.
- **scalene:** Performance profiling, installed as Python dep but invoked via `make run_profile`.

## Evaluation Metrics

The system implements comprehensive metrics for assessing agent performance across multiple dimensions:

### Core Performance Metrics

- **Time Taken:** Measures execution duration for performance assessment and optimization.
- **Output Similarity:** Evaluates how closely agent outputs match expected results using string comparison.
- **Task Completion Rate:** Tracks successful completion of assigned tasks across different scenarios.

### Required Advanced Metrics

- **Semantic Similarity:** Enhanced text comparison using TF-IDF cosine similarity (scikit-learn) and string distance algorithms (textdistance). Embedding-based similarity deferred pending `torchmetrics` build resolution.
- **Tool Usage Effectiveness:** Measures how appropriately agents select and utilize available tools.
- **Agent Coordination Quality:** Evaluates effectiveness of multi-agent collaboration and delegation.
- **Resource Utilization:** Monitors computational resources, API calls, and token usage.

See [roadmap.md](roadmap.md) for implementation timeline.

### Research-Validated Metrics

Based on Stanford's Agents4Science conference findings.

#### Citation Accuracy Metrics

- **Reference Hallucination Detection:** Automated verification that agent-generated citations and references exist (56% of AI-generated papers contained hallucinated references).
- **Citation Accuracy Score:** Percentage of verifiable references in agent outputs.

#### Reviewer Quality Metrics

- **Reviewer Calibration Score:** Alignment with human expert baseline using historical PeerRead accepted/rejected papers for calibration.
- **Reviewer Consistency Score:** Agreement across multiple evaluations of the same content.

#### Agent Social Dynamics

- **Agent Speaking Order Tracking:** Monitor which agent responds first and most frequently in multi-agent coordination (speaking order affects outcomes).
- **Coordination Balance:** Measure communication distribution across agents to detect dominance patterns.

### Monitoring & Observability

- **Opik Integration:** Primary platform for agent execution traces, performance monitoring, and observability.
- **Scalene Integration:** (Optional) Performance profiling for detailed Python performance analysis.
- **Weave Integration:** (Optional) ML experiment tracking for evaluation pipeline optimization.
- **Logfire Integration:** (Optional) Structured logging for debugging and analysis.

## Future Enhancements

- **Advanced Evaluation Metrics:** Implement semantic similarity, reasoning quality assessment, and multi-modal evaluation capabilities.
- **Performance Optimization:** Further optimize for latency and resource usage.
- **User Feedback:** Implement a feedback loop for users to report issues or suggest improvements.
- **Benchmark Expansion:** Add more diverse datasets and evaluation scenarios beyond PeerRead.

## Out of Scope

- A2A protocol migration (PydanticAI stays)
- Agent system restructuring (`src/app/agents/` unchanged except baselines.py)
- New evaluation algorithms (pure adapter pattern only)
- Streamlit UI redesign (existing UI stays as-is)
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead)
- HuggingFace `datasets` library (use GitHub API downloader instead)
- Google Gemini SDK (`google-genai`) - use OpenAI-spec compatible providers only
- VCR-based network mocking (use @patch for unit tests)
- Browser-based E2E tests (Playwright/Selenium deferred to Sprint 4)
- Sprint 3 features: Critic Agent, citation hallucination detection, social dynamics tracking

## Notes for Ralph Loop

Story Breakdown - Phase 2 (12 stories total):

- **Feature 5 (Shared Infrastructure)** → STORY-001: Create common/ module
- **Feature 6 (Judge Settings)** → STORY-002: Create judge/ skeleton with settings (depends: STORY-001)
- **Feature 6 (Plugin Base)** → STORY-003: Create EvaluatorPlugin base and registry (depends: STORY-002)
- **Feature 6 (Engine Adapters)** → STORY-004: Wrap TraditionalMetricsEngine (depends: STORY-003), STORY-005: Wrap LLMJudgeEngine (depends: STORY-003), STORY-006: Wrap GraphAnalysisEngine (depends: STORY-003)
- **Feature 6 (Pipeline)** → STORY-007: Refactor EvaluationPipeline to JudgeAgent (depends: STORY-004, STORY-005, STORY-006)
- **Feature 7 (Cleanup)** → STORY-008: Remove shims and update imports (depends: STORY-007)
- **Feature 8 (CC OTel)** → STORY-009: CC OTel observability plugin (depends: STORY-007)
- **Feature 9 (CC Baselines)** → STORY-010: CC-style evaluation baselines (depends: STORY-007)
- **Feature 9b (Wire Eval)** → STORY-010b: Wire evaluation after review generation (depends: STORY-007)
- **Feature 10 (E2E + API)** → STORY-011: E2E integration tests and multi-channel deployment (depends: STORY-010b)
