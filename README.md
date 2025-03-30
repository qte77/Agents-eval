# Agents-eval

This project aims to implement an evaluation pipeline to assess the effectiveness of open-source agentic AI systems across various use cases, focusing on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

![Version](https://img.shields.io/badge/version-1.1.0-8A2BE2)
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
- `make run_cli`
- `make run_gui`
- `make test_all`

## Configuration

[config.json](./src/config.json) contains . Inference endpoints used should adhere to [OpenAI Model Spec 2024-05-08](https://cdn.openai.com/spec/model-spec-2024-05-08.html) which is used by [pydantic-ai OpenAI-compatible Models](https://ai.pydantic.dev/models/#openai-compatible-models).

## Environment

[.env.example](./.env.example) contains example for usage of API keys and variables.

```text
# inference EP
GEMINI_API_KEY="xyz"

# tools
TAVILY_API_KEY=""

# log/mon/trace
WANDB_API_KEY="xyz"
```

## Documentation

[Agents-eval](https://qte77.github.io/Agents-eval)

### Project outline

`#TODO`

#### Metrics used

`#TODO`

#### Tools used

`#TODO`

### Architecture

<img src="assets/images/c4-multi-agent-system.png" alt="C4-Arch" title="C4-Arch" width="60%" />

### Project Structure

```sh
#TODO
```

## Landscape overview

Some contenders from the current landscape.

### Agentic System Frameworks

- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [restack](https://www.restack.io/)
- [smolAgents](https://github.com/huggingface/smolagents)
- [AutoGen](https://github.com/microsoft/autogen)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [Langchain](https://github.com/langchain-ai/langchain)
- [Langflow](github.com/langflow-ai/langflow)

### Agent-builder

- [Archon](https://github.com/coleam00/Archon)
- [Agentstack](https://github.com/AgentOps-AI/AgentStack)

### Evaluation

- Focusing on agentic systems
  - [AgentNeo](https://github.com/raga-ai-hub/agentneo)
  - [AutoGenBench](https://github.com/microsoft/autogen/blob/0.2/samples/tools/autogenbench)
  - [Langchain AgentEvals](https://github.com/langchain-ai/agentevals)
  - [Mosaic AI Agent Evaluation](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
  - [RagaAI-Catalyst](https://github.com/raga-ai-hub/RagaAI-Catalyst)
- RAG oriented
  - [RAGAs](https://github.com/explodinggradients/ragas)
- LLM apps
  - [DeepEval](https://github.com/confident-ai/deepeval)
  - [Langchain OpenEvals](https://github.com/langchain-ai/openevals)
  - [MLFlow LLM Evaluate](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html)

### Observation, Monitoring, Tracing

- [AgentOps - Agency](https://www.agentops.ai/)
- [arize](https://arize.com/)
- [Langtrace](https://www.langtrace.ai/)
- [LangSmith - Langchain](https://www.langchain.com/langsmith)
- [Weave - Weights & Biases](https://wandb.ai/site/weave/)

### Benchmarks

- [AgentEvals CORE-Bench Leaderboard](https://huggingface.co/spaces/agent-evals/core_leaderboard)
- [Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Chatbot Arena LLM Leaderboard](https://lmsys.org/projects/)
- [GAIA Leaderboard](https://gaia-benchmark-leaderboard.hf.space/)
- [GalileoAI Agent Leaderboard](https://huggingface.co/spaces/galileo-ai/agent-leaderboard)
- [WebDev Arena Leaderboard](https://web.lmarena.ai/leaderboard)

## Python Tools

- [`commitizen`](https://pypi.org/project/commitizen/)
  - Instead of [`bump-my-version`](https://pypi.org/project/bump-my-version/).
  - Python commitizen client tool.
  - Commitizen is release management tool designed for teams.
  - [Documentation](https://commitizen-tools.github.io/commitizen/)
- [`httpx`](https://pypi.org/project/httpx/)
  - Instead of [`requests`](https://pypi.org/project/requests/).
  - The next generation HTTP client.
  - HTTPX is a fully featured HTTP client library for Python 3. It includes an integrated command line client, has support for both HTTP/1.1 and HTTP/2, and provides both sync and async APIs.
- [`logfire`](https://pypi.org/project/logfire/)
  - Instead of `logger` or `loguru`. With OpenTelemetry.
  - The best Python observability tool!
  - Pydantic Logfire — Uncomplicated Observability
  - [logfire Docs](https://logfire.pydantic.dev/docs/)
- [`loguru`](https://pypi.org/project/loguru/)
  - Instead of `logger`.
  - Python logging made (stupidly) simple
  - Loguru is a library which aims to bring enjoyable logging in Python.
  - [API Reference](https://loguru.readthedocs.io/en/stable/api/logger.html)
  - See also: [Security considerations when using Loguru](https://loguru.readthedocs.io/en/stable/resources/recipes.html#security-considerations-when-using-loguru).
- [`pdoc`](https://pypi.org/project/pdoc/)
  - Instead of [`mkdocs`](https://pypi.org/project/mkdocs/).
  - API Documentation for Python Projects
  - pdoc's main feature is a focus on simplicity: pdoc aims to do one thing and do it well.
  - [pdoc.dev/docs](https://pdoc.dev/docs/pdoc.html)
- [`pre-commit`](https://pypi.org/project/pre-commit/) (again)
  - Instead of gh-actions.
  - A framework for managing and maintaining multi-language pre-commit hooks.
  - [more information](https://pre-commit.com/)
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
  - [Typer Docs](https://typer.tiangolo.com)

## Further Reading

- [[2501.16150] AI Agents for Computer Use: A Review of Instruction-based Computer Control, GUI Automation, and Operator Assistants](https://arxiv.org/abs/2501.16150)
- [[2501.06590] ChemAgent](https://arxiv.org/abs/2501.06590)
- [[2501.04227] Agent Laboratory: Using LLM Agents as Research Assitants](https://arxiv.org/abs/2501.04227)
- [[2412.04093] Practical Considerations for Agentic LLM Systems](https://arxiv.org/abs/2412.04093)
- [[2411.13768] Evaluation-driven Approach to LLM Agents](https://arxiv.org/abs/2411.13768)
- [[2411.10478] Large Language Models for Constructing and Optimizing Machine Learning Workflows: A Survey](https://arxiv.org/abs/2411.10478)
- [[2411.05285] A taxonomy of agentops for enabling observability of foundation model based agents](https://arxiv.org/abs/2411.05285)
- [[2410.22457] Advancing Agentic Systems: Dynamic Task Decomposition, Tool Integration and Evaluation using Novel Metrics and Dataset](https://arxiv.org/abs/2410.22457)
- [[2408.06361] Large Language Model Agent in Financial Trading: A Survey](https://arxiv.org/abs/2408.06361)
- [[2404.13501] A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/pdf/2404.13501)
- [[2402.02716] Understanding the planning of LLM agents: A survey](https://arxiv.org/abs/2402.02716)
- [[2402.01030] Executable Code Actions Elicit Better LLM Agents](https://arxiv.org/abs/2402.01030)
- [[2308.11432] A Survey on Large Language Model based Autonomous Agents](https://arxiv.org/abs/2308.11432)
