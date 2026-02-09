---
title: User Story - AI Agent Evaluation
description: User story and acceptance criteria for AI researchers evaluating multi-agent systems using PeerRead dataset
created: 2025-09-01
updated: 2026-02-09
category: user-story
version: 3.3.0
---

## Introduction

Agents-eval is designed to evaluate the effectiveness of open-source agentic AI systems across various use cases. This user story focuses on the perspective of an AI researcher who aims to assess and improve these systems using Agents-eval, with a primary focus on scientific paper review evaluation using the PeerRead dataset.

## As a user of the Agents-eval project, I want to

### Goals

- Evaluate and compare different open-source agentic AI systems using standardized benchmarks.
- Assess core capabilities such as task decomposition, tool integration, adaptability, and multi-agent coordination.
- Benchmark agent performance on scientific paper review tasks using the PeerRead dataset.
- Get use-case agnostic metrics for comprehensive assessment across different domains.
- Monitor and analyze agent behavior using integrated observability tools.
- Extend the evaluation pipeline with new metrics via a plugin system without modifying core pipeline code.
- Configure evaluation behavior (tier weights, timeouts, LLM model) via environment variables instead of JSON files.
- Get structured audit trails of evaluation decisions for debugging and compliance.

### Steps

1. **Set up the environment:**
   - See [CONTRIBUTING.md § Complete Command Reference](../CONTRIBUTING.md#complete-command-reference) for setup commands.
   - Configure API keys and variables in `.env.example` and rename to `.env`.
2. **Run the evaluation pipeline:**
   - **Fastest path:** `make quick_start` (downloads sample data, evaluates smallest paper).
   - See [CONTRIBUTING.md § Instant Commands](../CONTRIBUTING.md#instant-commands) for all execution and validation commands.
3. **Configure evaluation metrics:**
   - **Recommended:** Configure via environment variables (`JUDGE_*` for pipeline, `AGENT_*` for agents, `EVAL_*` for shared settings).
   - Defaults defined in Pydantic Settings classes (`src/app/*/settings.py`) - version-controlled, type-safe.
   - Override any setting via `.env` file (deployment-specific, never committed).
   - (Legacy) JSON config files (`config_eval.json`, `config_chat.json`) deprecated - migrating to Pydantic Settings per [12-Factor #3](best-practices/mas-design-principles.md) and [MAESTRO security principles](best-practices/mas-security.md).
4. **Execute multi-agent workflows:**
   - Run PeerRead review generation with Manager → Researcher → Analyst → Synthesizer delegation.
   - Evaluation runs automatically after generation (Sprint 2); use `--skip-eval` for generation-only mode.
   - Monitor agent coordination and tool usage effectiveness.
5. **Analyze the results:**
   - Review output logs and Streamlit UI to assess agent performance.
   - Use Opik for execution traces and detailed observability.
   - Optionally use additional monitoring tools (Weave, Logfire) for extended analysis.
   - Profile performance with `make run_profile` (Scalene).

### Expected Outcomes

- **Performance Metrics:** Clear quantitative measures for task completion time, output similarity, and coordination quality.
- **Multi-Agent Analysis:** Insights into delegation effectiveness, agent specialization benefits, and coordination overhead.
- **PeerRead Benchmarks:** Standardized scores for scientific paper review tasks across different agent configurations.
- **Tool Integration Assessment:** Evaluation of how effectively agents utilize DuckDuckGo search and PeerRead-specific tools.
- **Observability Insights:** Detailed execution traces, resource utilization patterns, and behavioral analytics.
- **Comparative Analysis:** Data-driven assessment enabling comparison between different agentic systems and configurations.
- **Plugin Extensibility:** New evaluation metrics addable without modifying pipeline code.
- **Configuration Flexibility:** Tier weights, timeouts, LLM model configurable via env vars.

### Acceptance Criteria

1. **Multi-Agent Evaluation Pipeline:** 🟡 **Partially Implemented**
   - ✅ MAS review generation with Manager, Researcher, Analyst, and Synthesizer agent roles.
   - ✅ Three-tier evaluation engine (traditional metrics, LLM-as-Judge, graph analysis) exists as standalone module.
   - 📋 Generation and evaluation not yet wired together in CLI flow (Sprint 2, [PRD Feature 9b](PRD.md#feature-9b-wire-evaluation-after-review-generation)). Evaluation runs by default with `--skip-eval` opt-out.
   - The pipeline should support the pydantic-ai framework with standardized PeerRead dataset benchmarks.

2. **Advanced Metric Development:** 🟡 **Partially Implemented**
   - ✅ The system implements core metrics: execution time, output similarity, task completion rates, and resource utilization.
   - 📋 Advanced metrics planned for Sprint 2/3: semantic similarity, tool usage effectiveness, and agent coordination quality.
   - ✅ Metrics are modular and easily integratable with existing evaluation logic.

3. **Comprehensive Monitoring & Observability:** 🟡 **Partially Implemented**
   - 🟡 Opik integration available but optional (full deployment planned for Sprint 3).
   - 🟡 Weave and Logfire dependencies installed and imported; full integration planned.
   - ❌ Scalene integration not yet implemented (planned).

4. **Enhanced CLI and GUI Interactions:** ✅ **Implemented**
   - ✅ Make-based CLI commands and Streamlit GUI available for user interaction.
   - ✅ Streamlit GUI displays evaluation results, agent coordination patterns, and performance analytics.
   - ✅ CLI supports multiple environment setups: basic dev, Claude Code integration, and Ollama local hosting.
   - 📋 Streaming output from pydantic-ai models (optional feature, not yet implemented).

5. **Documentation and Feedback:** ✅ **Implemented**
   - ✅ Comprehensive documentation for setup, usage, and testing with PeerRead evaluation examples.
   - ✅ Feedback mechanisms available through GitHub issues.
   - ✅ Detailed agent workflow documentation and best practices provided.

6. **Plugin-Based Evaluation Architecture:** 📋 **Planned**
   - Evaluation metrics registered as plugins implementing typed `EvaluatorPlugin` interface.
   - Each plugin is a stateless reducer: `evaluate(context) -> BaseModel` (12-Factor #12).
   - Plugins control what context passes to the next tier (12-Factor #3).
   - Plugin errors produce structured partial results, not crashes (12-Factor #9).
   - Per-plugin timeouts configurable via `JudgeSettings` (MAESTRO Execution Layer).
   - All inter-plugin data uses typed Pydantic models, not raw dicts (MAESTRO Agent Logic Layer).

7. **Security-Aligned Design:** 📋 **Planned**
   - Input validation at each plugin boundary (MAESTRO Integration Layer).
   - Rule-based fallback when LLM judge fails (MAESTRO Model Layer).
   - Thread-safe trace store for evaluation audit trail (MAESTRO Monitoring Layer).
   - Graceful degradation -- tier failures produce partial results (MAESTRO Environment Layer).

8. **Test-Driven Quality:** 📋 **Planned**
   - TDD per story following testing-strategy.md (no anti-patterns from Patterns to Remove).
   - Hypothesis property tests for critical scoring math.
   - E2E integration tests for full pipeline validation.
   - `make validate` passes at every story boundary.

9. **Multi-Channel Access:** 📋 **Planned**
   - Evaluate agents via CLI for local development.
   - Call evaluation API programmatically via FastAPI REST endpoints.
   - Access via MCP server for AI-to-AI evaluation workflows.
   - Existing Streamlit UI for interactive exploration.
   - Consistent results across all deployment channels.

### Benefits

- **Standardized Agent Evaluation:** Agents-eval provides a structured approach with PeerRead benchmarks for evaluating agentic AI systems, enabling consistent comparison across different implementations.
- **Multi-Agent System Insights:** The platform offers unique visibility into delegation patterns, coordination effectiveness, and specialization benefits in multi-agent workflows.
- **Comprehensive Observability:** Opik provides primary tracing and observability for agent execution, with optional monitoring tools (Weave, Scalene, Logfire) for extended insights into agent behavior, performance bottlenecks, and resource utilization.
- **Framework Flexibility:** The system supports pydantic-ai and allows for custom metric development, making it adaptable to diverse research needs.
- **Enhanced Developer Experience:** Multiple setup options (Claude Code, Ollama, basic dev) combined with CLI and GUI interfaces cater to different development preferences and workflows.
- **Production-Ready Tooling:** Built-in code quality checks, testing frameworks, and documentation generation support serious research and development efforts.

### Example Scenario: PeerRead Scientific Paper Review Evaluation

**Scenario:** A researcher wants to evaluate how well different multi-agent configurations perform on scientific paper review tasks.

**Steps:**

1. **Environment Setup:**
   - User runs `make setup_dev` to configure development environment (includes Claude Code).
   - User configures API keys in `.env` for OpenAI and other providers.

2. **Agent Configuration:**
   - User configures 4-agent system prompts (Manager, Researcher, Analyst, Synthesizer) via `config_chat.json` (migrating to Pydantic Settings).
   - Agent creation and tool assignment handled by `agent_factories.py`.
   - User sets up PeerRead dataset access and processing tools.

3. **Evaluation Execution:**
   - User launches the Streamlit GUI with `make run_gui`.
   - User selects PeerRead evaluation pipeline and chooses paper samples.
   - User initiates evaluation with Manager → Researcher delegation workflow.

4. **Multi-Agent Workflow:**
   - **Manager** receives paper review task and delegates research to Researcher agent.
   - **Researcher** uses DuckDuckGo to gather relevant context and background information.
   - **Analyst** validates research findings and performs detailed paper analysis.
   - **Synthesizer** generates comprehensive review combining all agent insights.

5. **Results Analysis** (Sprint 2: evaluation wired automatically after generation):
   - User reviews performance metrics: completion time (e.g., 45 seconds), output similarity score (0.87).
   - User analyzes agent coordination patterns and execution traces.
   - User compares results against baseline single-agent performance ([PRD Feature 9](PRD.md#feature-9-cc-style-evaluation-baselines)).

6. **Insights & Iteration:**
   - User identifies that delegation overhead reduced efficiency by 15% but improved review quality by 23%.
   - User adjusts agent prompts and re-runs evaluation to optimize performance.

**Expected Results:**

- Quantitative comparison showing multi-agent system achieves higher review quality scores.
- Detailed execution traces showing delegation decision points and tool usage patterns.
- Performance baseline for future agent system improvements.

### Additional Notes

- **Dependencies:** Built on Python 3.13 with pydantic-ai-slim (OpenAI, DuckDuckGo, Tavily), scikit-learn + textdistance (Tier 1 metrics), and networkx (Tier 3 graph analysis).
- **Development Tools:** Comprehensive toolchain including pytest for testing, ruff for linting, pyright for type checking, and mkdocs for documentation.
- **References:**
  - Use the [CHANGELOG](https://github.com/qte77/Agents-eval/blob/main/CHANGELOG.md) for version history and feature updates.
  - Refer to [AGENTS.md](https://github.com/qte77/Agents-eval/blob/main/AGENTS.md) for detailed agent instructions and architecture overview.
  - Check [PRD.md](https://github.com/qte77/Agents-eval/blob/main/docs/PRD.md) for comprehensive product requirements and technical specifications.
