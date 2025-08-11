# User Story

## Introduction

Agents-eval is designed to evaluate the effectiveness of open-source agentic AI systems across various use cases. This user story focuses on the perspective of an AI researcher who aims to assess and improve these systems using Agents-eval, with a primary focus on scientific paper review evaluation using the PeerRead dataset.

## As a user of the Agents-eval project, I want to

### Goals

- Evaluate and compare different open-source agentic AI systems using standardized benchmarks.
- Assess core capabilities such as task decomposition, tool integration, adaptability, and multi-agent coordination.
- Benchmark agent performance on scientific paper review tasks using the PeerRead dataset.
- Get use-case agnostic metrics for comprehensive assessment across different domains.
- Monitor and analyze agent behavior using integrated observability tools.

### Steps

1. **Set up the environment:**
   - Use `make setup_dev` for basic development environment.
   - Use `make setup_dev_claude` for Claude Code integration.
   - Use `make setup_dev_ollama` for local Ollama server setup.
   - Configure API keys and variables in `.env.example` and rename to `.env`.
2. **Run the evaluation pipeline:**
   - Execute the CLI with `make run_cli` or the GUI with `make run_gui`.
   - Run code quality checks with `make validate` or `make quick_validate`.
3. **Configure evaluation metrics:**
   - Adjust weights in `src/app/config/config_eval.json`.
   - Configure agent behavior in `src/app/config/config_chat.json`.
4. **Execute multi-agent workflows:**
   - Run PeerRead evaluation with Manager → Researcher → Analyst → Synthesizer delegation.
   - Monitor agent coordination and tool usage effectiveness.
5. **Analyze the results:**
   - Review output logs and Streamlit UI to assess agent performance.
   - Use integrated monitoring tools (AgentOps, Logfire, Weave) for detailed analysis.

### Expected Outcomes

- **Performance Metrics:** Clear quantitative measures for task completion time, output similarity, and coordination quality.
- **Multi-Agent Analysis:** Insights into delegation effectiveness, agent specialization benefits, and coordination overhead.
- **PeerRead Benchmarks:** Standardized scores for scientific paper review tasks across different agent configurations.
- **Tool Integration Assessment:** Evaluation of how effectively agents utilize DuckDuckGo search and PeerRead-specific tools.
- **Observability Insights:** Detailed execution traces, resource utilization patterns, and behavioral analytics.
- **Comparative Analysis:** Data-driven assessment enabling comparison between different agentic systems and configurations.

### Acceptance Criteria

1. **Multi-Agent Evaluation Pipeline:**
   - The system should provide a comprehensive evaluation pipeline supporting Manager, Researcher, Analyst, and Synthesizer agent roles.
   - The pipeline should measure core agentic capabilities: task decomposition, tool integration, delegation effectiveness, and coordination quality.
   - The pipeline should support multiple agentic AI frameworks (e.g., pydantic-ai, LangChain) with standardized PeerRead dataset benchmarks.

2. **Advanced Metric Development:**
   - The system should implement core metrics: execution time, output similarity, task completion rates, and resource utilization.
   - The system should support planned advanced metrics: semantic similarity, tool usage effectiveness, and agent coordination quality.
   - These metrics should be modular and easily integratable with existing evaluation logic.

3. **Comprehensive Monitoring & Observability:**
   - The system should integrate AgentOps for real-time agent behavior tracking.
   - The system should provide Logfire integration for structured logging and debugging.
   - The system should support Weave integration for ML experiment tracking and evaluation optimization.
   - Performance profiling should be available through Scalene integration.

4. **Enhanced CLI and GUI Interactions:**
   - The system should offer both Make-based CLI commands and a Streamlit GUI for user interaction.
   - The Streamlit GUI should display real-time evaluation results, agent coordination patterns, and performance analytics.
   - The CLI should support multiple environment setups: basic dev, Claude Code integration, and Ollama local hosting.
   - Optional: The CLI should support streaming output from pydantic-ai models.

5. **Documentation and Feedback:**
   - The system should include comprehensive documentation for setup, usage, and testing with specific PeerRead evaluation examples.
   - There should be a feedback loop for users to report issues or suggest improvements.
   - The system should provide detailed agent workflow documentation and best practices.

### Benefits

- **Standardized Agent Evaluation:** Agents-eval provides a structured approach with PeerRead benchmarks for evaluating agentic AI systems, enabling consistent comparison across different implementations.
- **Multi-Agent System Insights:** The platform offers unique visibility into delegation patterns, coordination effectiveness, and specialization benefits in multi-agent workflows.
- **Comprehensive Observability:** Integrated monitoring tools (AgentOps, Logfire, Weave, Scalene) provide deep insights into agent behavior, performance bottlenecks, and resource utilization.
- **Framework Flexibility:** The system supports multiple frameworks (pydantic-ai, future LangChain integration) and allows for custom metric development, making it adaptable to diverse research needs.
- **Enhanced Developer Experience:** Multiple setup options (Claude Code, Ollama, basic dev) combined with CLI and GUI interfaces cater to different development preferences and workflows.
- **Production-Ready Tooling:** Built-in code quality checks, testing frameworks, and documentation generation support serious research and development efforts.

### Example Scenario: PeerRead Scientific Paper Review Evaluation

**Scenario:** A researcher wants to evaluate how well different multi-agent configurations perform on scientific paper review tasks.

**Steps:**

1. **Environment Setup:**
   - User runs `make setup_dev_claude` to configure Claude Code integration.
   - User configures API keys in `.env` for OpenAI and other providers.

2. **Agent Configuration:**
   - User configures a 4-agent system (Manager, Researcher, Analyst, Synthesizer) in `config_chat.json`.
   - User enables DuckDuckGo search tools for the Researcher agent.
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

5. **Results Analysis:**
   - User reviews performance metrics: completion time (e.g., 45 seconds), output similarity score (0.87).
   - User analyzes agent coordination patterns via AgentOps dashboard.
   - User compares results against baseline single-agent performance.

6. **Insights & Iteration:**
   - User identifies that delegation overhead reduced efficiency by 15% but improved review quality by 23%.
   - User adjusts agent prompts and re-runs evaluation to optimize performance.

**Expected Results:**

- Quantitative comparison showing multi-agent system achieves higher review quality scores.
- Detailed execution traces showing delegation decision points and tool usage patterns.
- Performance baseline for future agent system improvements.

### Additional Notes

- **Current Status:** The project is under active development with core PeerRead evaluation and multi-agent coordination features implemented (v3.1.0).
- **Dependencies:** Built on Python 3.13 with pydantic-ai-slim, supporting OpenAI, DuckDuckGo, and Tavily integrations.
- **Development Tools:** Comprehensive toolchain including pytest for testing, ruff for linting, pyright for type checking, and mkdocs for documentation.
- **References:**
  - Use the [CHANGELOG](https://github.com/qte77/Agents-eval/blob/main/CHANGELOG.md) for version history and feature updates.
  - Refer to [AGENTS.md](https://github.com/qte77/Agents-eval/blob/main/AGENTS.md) for detailed agent instructions and architecture overview.
  - Check [PRD.md](https://github.com/qte77/Agents-eval/blob/main/docs/PRD.md) for comprehensive product requirements and technical specifications.
