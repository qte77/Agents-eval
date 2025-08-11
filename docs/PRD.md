# Product Requirements Document (PRD) for Agents-eval

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

- **Command Line Interface:**
  - Environment setup commands: `make setup_dev`, `make setup_dev_claude`, `make setup_dev_ollama`
  - Code quality commands: `make ruff`, `make type_check`, `make validate`, `make quick_validate`
  - Application execution: `make run_cli`, `make run_gui`
  - Testing commands: `make test_all`, `make coverage_all`
  - Ollama server management: `make setup_ollama`, `make start_ollama`, `make stop_ollama`
  - PeerRead dataset evaluation commands with configurable agent systems
  - Multi-agent system orchestration with delegation capabilities

### Frontend (Streamlit)

- **User Interface:**
  - Display test results and system performance metrics.
  - Interactive dashboard for PeerRead evaluation results.
  - Multi-agent system performance visualization.
  - Real-time monitoring of agent execution and delegation.

### (Optional) Backend (FastAPI)

- **Multi-Agent System Architecture:**
  - **Manager Agent:** Primary orchestrator for task delegation and coordination.
  - **Researcher Agent:** Specialized for information gathering using DuckDuckGo search tools.
  - **Analyst Agent:** Focused on data analysis and validation of research findings.
  - **Synthesizer Agent:** Responsible for generating comprehensive reports and summaries.
- **Agentic System Integration:**
  - Support for adding tools to agents using pydantic-ai.
  - PeerRead-specific tools for paper analysis and review processing.
  - Ensure agents can use tools effectively and return expected results.
- **Model Management:**
  - Ability to download, list, and manage models using the `ollama` Python package.
  - Support for multiple LLM providers (OpenAI, Gemini, HuggingFace).
- **API Endpoints:**
  - Endpoint to start and check the status of the Ollama server.
  - Endpoint to download and manage models.
  - Endpoint to run tests and return results.
  - Endpoints for PeerRead evaluation pipeline execution.

## Non-Functional Requirements

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance.
  - Implement logging and error handling for debugging and monitoring.
- **Documentation:**
  - Comprehensive documentation for setup, usage, and testing.
- **Scalability:**
  - Design the system to handle multiple concurrent requests.
- **Performance:**
  - Ensure low latency in server responses and model downloads.
  - Optimize for memory usage and CPU/GPU utilization.
- **Security:**
  - Implement secure communication between components.
  - Use environment variables for sensitive information.

## Assumptions

- **Remote Inference Endpoints:** The project can use remote inference endpoints provided within a `config.json` and using API keys from `.env`.
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

- **datasets:** HuggingFace datasets library for data management.
- **markitdown:** Document processing with PDF support.

### LLM Providers & Tools

- **google-genai:** Google Gemini integration.
- **httpx:** HTTP client for API requests.

### Monitoring & Logging

- **agentops:** Agent operations monitoring and tracking.
- **logfire:** Structured logging and observability.
- **loguru:** Enhanced logging capabilities.
- **weave:** ML experiment tracking and evaluation.
- **scalene:** Performance profiling for Python.

### Development & Testing

- **pytest:** Testing framework with async support and BDD.
- **pytest-cov:** Coverage reporting.
- **pyright:** Static type checking.
- **ruff:** Code formatting and linting.

### User Interface

- **streamlit:** Interactive web dashboard.

### Documentation

- **mkdocs:** Documentation generation with Material theme.
- **mkdocstrings:** API documentation from docstrings.

### Optional Dependencies

- **ollama:** (Optional) For local model hosting and inference.

## Evaluation Metrics

The system implements comprehensive metrics for assessing agent performance across multiple dimensions:

### Core Performance Metrics

- **Time Taken:** Measures execution duration for performance assessment and optimization.
- **Output Similarity:** Evaluates how closely agent outputs match expected results using string comparison.
- **Task Completion Rate:** Tracks successful completion of assigned tasks across different scenarios.

### Planned Advanced Metrics

- **Semantic Similarity:** Enhanced text comparison using embedding-based similarity scores.
- **Tool Usage Effectiveness:** Measures how appropriately agents select and utilize available tools.
- **Agent Coordination Quality:** Evaluates effectiveness of multi-agent collaboration and delegation.
- **Resource Utilization:** Monitors computational resources, API calls, and token usage.

### Monitoring & Observability

- **AgentOps Integration:** Real-time agent behavior tracking and performance monitoring.
- **Logfire Integration:** Structured logging for debugging and analysis.
- **Weave Integration:** ML experiment tracking for evaluation pipeline optimization.
- **Performance Profiling:** Scalene integration for detailed Python performance analysis.

## Future Enhancements

- **Integration with More Frameworks:** Expand compatibility with other agentic system frameworks. Meaning other popular agentic system frameworks like LangChain, AutoGen, CrewAI, LangGraph, Semantic Kernel, and smolAgents.
- **Advanced Evaluation Metrics:** Implement semantic similarity, reasoning quality assessment, and multi-modal evaluation capabilities.
- **Performance Optimization:** Further optimize for latency and resource usage.
- **User Feedback:** Implement a feedback loop for users to report issues or suggest improvements.
- **Benchmark Expansion:** Add more diverse datasets and evaluation scenarios beyond PeerRead.
