# Product Requirements Document (PRD) for Agents-eval

## Overview

**Agents-eval** is a project aimed at evaluating the effectiveness of open-source agentic AI systems across various use cases. The focus is on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

## Goals

- **Evaluate Agentic AI Systems:** Provide a comprehensive evaluation pipeline to assess the performance of agentic AI systems.
- **Metric Development:** Develop and implement metrics that are agnostic to specific use cases but measure core agentic capabilities.
- **Integration with Existing Frameworks:** Ensure compatibility with popular agentic system frameworks like LangChain, AutoGen, CrewAI, LangGraph, Semantic Kernel, and smolAgents.
- **Continuous Improvement:** Promote continuous improvement through automated testing, version control, and documentation.

## Functional Requirements

### Backend (FastAPI)

- **API Endpoints:**
  - Endpoint to start and check the status of the Ollama server.
  - Endpoint to download and manage models.
  - Endpoint to run tests and return results.

- **Model Management:**
  - Ability to download, list, and manage models using the `ollama` Python package.

- **Agentic System Integration:**
  - Support for adding tools to agents using Pydantic-AI.
  - Ensure agents can use tools effectively and return expected results.

### Frontend (Streamlit)

- **User Interface:**
  - A dashboard to monitor the status of the Ollama server.
  - Interface to initiate model downloads and manage models.
  - Display test results and system performance metrics.

### CLI

- **Command Line Interface:**
  - Commands to start, stop, and check the status of the Ollama server.
  - Commands to download models and run tests.

## Non-Functional Requirements

- **Performance:**
  - Ensure low latency in server responses and model downloads.
  - Optimize for memory usage and CPU/GPU utilization.

- **Security:**
  - Implement secure communication between components.
  - Use environment variables for sensitive information.

- **Scalability:**
  - Design the system to handle multiple concurrent requests and model downloads.

- **Maintainability:**
  - Use modular design patterns for easy updates and maintenance.
  - Implement logging and error handling for debugging and monitoring.

- **Documentation:**
  - Comprehensive documentation for setup, usage, and testing.

## Assumptions

- **Ollama Server:** The project assumes the use of an Ollama server for local model hosting and inference.
- **Python Environment:** The project uses Python 3.12 and related tools like `uv` for dependency management.
- **GitHub Actions:** CI/CD pipelines are set up using GitHub Actions for automated testing, version bumping, and documentation deployment.

## Constraints

- **Hardware:** The project assumes access to hardware capable of running the Ollama server and models, including sufficient RAM and GPU capabilities.
- **Software:** Requires Python 3.12, `uv`, and other dependencies listed in `pyproject.toml`.

## Dependencies

- **Ollama:** For local model hosting and inference.
- **Pydantic-AI:** For agent and tool management.
- **FastAPI:** For backend API development.
- **Streamlit:** For frontend dashboard.
- **Pytest:** For testing.
- **Ruff:** For code linting.
- **MkDocs:** For documentation generation.

## Future Enhancements

- **Additional Metrics:** Develop more metrics to evaluate agentic systems.
- **Integration with More Frameworks:** Expand compatibility with other agentic system frameworks.
- **Performance Optimization:** Further optimize for latency and resource usage.
- **User Feedback:** Implement a feedback loop for users to report issues or suggest improvements.
