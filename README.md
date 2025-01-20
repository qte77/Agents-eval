# Agents-eval

This project aims to implement an evaluation pipeline to assess the effectiveness of open-source agentic AI systems across various use cases, focusing on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

![Version](https://img.shields.io/badge/version-0.0.1-8A2BE2)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/Agents-eval/badge)](https://www.codefactor.io/repository/github/qte77/Agents-eval)
[![CodeQL](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml)
[![ruff](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)
[![vscode.dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=vscode.dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://vscode.dev/github/qte77/Agents-eval)

## Status

(DRAFT) (WIP) ----> Not fully implemented yet

For version history have a look at the [CHANGELOG](CHANGELOG.md).

## Setup

`uv sync`

## Usage

`uv run python -m src`

## Testing

`uv run pytest`

## Documentation

[Agents-eval](https://qte77.github.io/Agents-eval)

### Architecture

`#TODO`

<!--
<img src="assets/images/c4-arch.dark.png#gh-dark-mode-only" alt="C4-Arch" title="C4-Arch" width="60%" />
<img src="assets/images/c4-arch.light.png#gh-light-mode-only" alt="C4-Arch" title="C4-Arch" width="60%" />
-->

### Project Structure

```sh
#TODO
```

## TODO

### Project outline

`#TODO`

### Agentic System Frameworks

- [LangChain](https://github.com/langchain-ai/langchain)
- [AutoGen](https://github.com/microsoft/autogen)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [smolAgents](https://github.com/huggingface/smolagents)

### Evaluation Tools and Frameworks

- [AutoGenBench](https://github.com/microsoft/autogen/blob/0.2/samples/tools/autogenbench)
- [AgentNeo](https://github.com/raga-ai-hub/agentneo)
- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [RAGAs](https://github.com/explodinggradients/ragas)
- [MLFlow LLM Evaluate](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html)
- [DeepEval](https://github.com/confident-ai/deepeval)

### Core Agentic Evaluation Metrics

- Task Decomposition and Planning
  - Structural Similarity Index (SSI)
  - Node F1 Score
- Tool Integration and Utilization
  - Tool F1 Score
  - Tool Utilisation Efficacy (TUE)
  - Tool Integration Effectiveness
- Memory and Context Management
  - Memory Coherence and Retrieval (MCR)
- System Adaptability and Learning Rate
- Automation Rate
- Overall System Performance
  - Task Success Rate
  - Latency and Efficiency (computational overhead)
  - Component Synergy Score (CSS)
  - Strategic Planning Index (SPI)
- LLM-as-a-judge, eval by LLM

### Possible Use Cases

- Financial Services
  - Automated Trading Strategies
  - Fraud Detection
- Supply Chain Management
  - Inventory Optimization
  - Demand Forecasting
- Customer Service
  - AI Chatbots
  - Virtual Assistants
- Intelligent Document Processing (IDP)
  - Contract Management
  - Financial Statement Processing
  - Insurance Claims Processing
- Healthcare
  - Treatment planning
  - Drug discovery
- Image Processing
  - Medical Imaging
  - Object Detection
  - Image Classification

## Further Reading

- [Advancing Agentic Systems: Dynamic Task Decomposition, Tool Integration and Evaluation using Novel Metrics and Dataset](https://arxiv.org/abs/2410.22457)
