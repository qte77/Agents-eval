# Agents-eval

This project aims to implement an evaluation pipeline to assess the effectiveness of open-source agentic AI systems across various use cases, focusing on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

![Version](https://img.shields.io/badge/version-0.0.2-8A2BE2)
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

## Setup and Usage

- `make setup_env`
- `make run_app`
- `make test_all`

## Documentation

[Agents-eval](https://qte77.github.io/Agents-eval)

### Architecture

<img src="assets/images/Agents-eval.C4.System.mono.png" alt="C4-Arch" title="C4-Arch" width="60%" />
<img src="assets/images/Agents-eval.C4.Code.mono.png" alt="C4-Arch" title="C4-Arch" width="60%" />

### Project Structure

```sh
#TODO
```

## TODO

### Project outline

`#TODO`

## Landscape overview

### Agentic System Frameworks

- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [smolAgents](https://github.com/huggingface/smolagents)
- [AutoGen](https://github.com/microsoft/autogen)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Langflow](github.com/langflow-ai/langflow)

### Evaluation Tools and Frameworks

- Focusing on agentic systems
  - [Mosaic AI Agent Evaluation](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
  - [AutoGenBench](https://github.com/microsoft/autogen/blob/0.2/samples/tools/autogenbench)
  - [RagaAI-Catalyst](https://github.com/raga-ai-hub/RagaAI-Catalyst)
  - [AgentNeo](https://github.com/raga-ai-hub/agentneo)
- More RAG oriented
  - [DeepEval](https://github.com/confident-ai/deepeval)
  - [RAGAs](https://github.com/explodinggradients/ragas)
- LLM apps
  - [MLFlow LLM Evaluate](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html)

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

### Python Tools

- [`commitizen`](https://pypi.org/project/commitizen/)
  - Instead of [`bump-my-version`](https://pypi.org/project/bump-my-version/).
  - Python commitizen client tool.
  - Commitizen is release management tool designed for teams.
  - [Documentation](https://commitizen-tools.github.io/commitizen/)
- [`httpx`](https://pypi.org/project/httpx/)
  - Instead of [`requests`](https://pypi.org/project/requests/).
  - The next generation HTTP client.
  - HTTPX is a fully featured HTTP client library for Python 3. It includes an integrated command line client, has support for both HTTP/1.1 and HTTP/2, and provides both sync and async APIs.
- [`justfile`](https://pypi.org/project/justfile/)
  - Instead of `with`-context.
  - JustFile is a Python library that provides a function to either read, write, or append.
  - It’s pretty straight-foward. No creating a file handle. no `with`-syntax. Just reading from a path.
  - [https://python-justfile.readthedocs.io/](https://python-justfile.readthedocs.io/)
- [`loguru`](https://pypi.org/project/loguru/)
  - Instead of `logger`.
  - Python logging made (stupidly) simple
  - Loguru is a library which aims to bring enjoyable logging in Python.
  - [API Reference](https://loguru.readthedocs.io/en/stable/api/logger.html)
  - See also: [Security considerations when using Loguru](https://loguru.readthedocs.io/en/stable/resources/recipes.html#security-considerations-when-using-loguru). 
- [`pdoc`](https://pypi.org/project/pdoc/)
  - Instead of [`mkdocs`]https://pypi.org/project/mkdocs/).
  - API Documentation for Python Projects
  - pdoc's main feature is a focus on simplicity: pdoc aims to do one thing and do it well.
  - [pdoc.dev/docs](https://pdoc.dev/docs/pdoc.html)
- [`pre-commit`](https://pypi.org/project/pre-commit/) (again)
  - Instead of gh-actions.
  - A framework for managing and maintaining multi-language pre-commit hooks.
  - For more information see: https://pre-commit.com/.
- [`pydantic-settings`](https://pypi.org/project/pydantic-settings/)
  - Instead of [`OmegaConf`](https://pypi.org/project/omegaconf/) or `dotenv`.
  - Settings management using Pydantic, this is the new official home of Pydantic's BaseSettings.
  - See [documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for more details.
- [`pyright`](https://pypi.org/project/pyright/)
  - Instead of [`pydantic`](https://pypi.org/project/pydantic/) or [`mypy`](https://pypi.org/project/mypy/).
  - Pyright for Python is a Python command-line wrapper over [pyright](https://github.com/microsoft/pyright), a static type checker for Python.
- [`rich`](https://pypi.org/project/rich/)
  - Instead of [`tqdm`](https://pypi.org/project/tqdm/).
  - Render rich text, tables, progress bars, syntax highlighting, markdown and more to the terminal
  - Rich is a Python library for _rich_ text and beautiful formatting in the terminal.
  - [Documentation](https://rich.readthedocs.io/en/latest/)
- [`Tenacity`](https://pypi.org/project/tenacity/)
  - Retry code until it succeeds.
  - Tenacity is a general-purpose retrying library to simplify the task of adding retry behavior to just about anything.
- [`Typer`](https://pypi.org/project/typer/)
  - Instead of [`argparse`](https://pypi.org/project/argparse/).
  - Typer, build great CLIs. Easy to code. Based on Python type hints.
  - Documentation: https://typer.tiangolo.com

## Further Reading

- [[2501.16150] AI Agents for Computer Use: A Review of Instruction-based Computer Control, GUI Automation, and Operator Assistants](https://arxiv.org/abs/2501.16150)
- [[2408.06361] Large Language Model Agent in Financial Trading: A Survey](https://arxiv.org/abs/2408.06361)
- [[2411.10478] Large Language Models for Constructing and Optimizing Machine Learning Workflows: A Survey](https://arxiv.org/abs/2411.10478)
- [[2410.22457] Advancing Agentic Systems: Dynamic Task Decomposition, Tool Integration and Evaluation using Novel Metrics and Dataset](https://arxiv.org/abs/2410.22457)
- [[2404.13501] A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/pdf/2404.13501)
- [[2402.02716] Understanding the planning of LLM agents: A survey](https://arxiv.org/abs/2402.02716)
- [[2402.01030] Executable Code Actions Elicit Better LLM Agents](https://arxiv.org/abs/2402.01030)
- [[2308.11432] A Survey on Large Language Model based Autonomous Agents](https://arxiv.org/abs/2308.11432)
