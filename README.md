# Agents-eval

This project aims to implement an evaluation pipeline to assess the effectiveness of open-source agentic AI systems using the PeerRead dataset, focusing on use case agnostic metrics that measure core capabilities such as task decomposition, tool integration, adaptability, and overall performance.

**This README is intended for human developers and users.** For shared development workflows and standards (valid for both agents and humans), see [CONTRIBUTING.md](CONTRIBUTING.md). For AI coding agent instructions, see [AGENTS.md](AGENTS.md).

[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
![Version](https://img.shields.io/badge/version-3.2.0-58f4c2.svg)
[![CodeQL](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/Agents-eval/badge)](https://www.codefactor.io/repository/github/qte77/Agents-eval)
[![ruff](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)

**DevEx** [![vscode.dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=vscode.dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://vscode.dev/github/qte77/Agents-eval)
[![Codespace Dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev/devcontainer.json)
[![Codespace Dev Claude Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev%20Claude%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev_claude/devcontainer.json)
[![Codespace Dev Ollama](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev%20Ollama&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev_ollama/devcontainer.json)
[![TalkToGithub](https://img.shields.io/badge/TalkToGithub-7a83ff.svg)](https://talktogithub.com/qte77/Agents-eval)
[![llms.txt (UitHub)](https://img.shields.io/badge/llms.txt-uithub-800080.svg)](https://github.com/qte77/Agents-eval)
[![llms.txt (GitToDoc)](https://img.shields.io/badge/llms.txt-GitToDoc-fe4a60.svg)](https://gittodoc.com/qte77/Agents-eval)

## Status

(DRAFT) (WIP) ----> Not fully implemented yet

For version history have a look at the [CHANGELOG](CHANGELOG.md).

## Setup and Usage

- `make setup_prod`
- `make setup_dev` or `make setup_dev_ollama`
- `make run_cli` or `make run_cli ARGS="--help"`
- `make run_gui`
- `make test_all`

### Environment

[.env.example](.env.example) contains examples for usage of API keys and variables.

```text
# inference EP
GEMINI_API_KEY="xyz"

# tools
TAVILY_API_KEY=""

# log/mon/trace
WANDB_API_KEY="xyz"
```

### Configuration

- [config_app.py](src/app/config/config_app.py) contains configuration constants for the application.
- [config_chat.json](src/app/config/config_chat.json) contains inference provider configuration and prompts. inference endpoints used should adhere to [OpenAI Model Spec 2024-05-08](https://cdn.openai.com/spec/model-spec-2024-05-08.html) which is used by [pydantic-ai OpenAI-compatible Models](https://ai.pydantic.dev/models/#openai-compatible-models).
- [config_eval.json](src/app/config/config_eval.json) contains evaluation metrics and their weights.
- [data_models.py](src/app/config/data_models.py) contains the pydantic data models for agent system configuration and results.

### Note

1. The contained chat configuration uses free inference endpoints which are subject to change by the providers. See lists such as [free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) to find other providers.
2. The contained chat configuration uses models which are also subject to change by the providers and have to be updated from time to time.
3. LLM-as-judge is also subject to the chat configuration.

## Documentation

[Agents-eval](https://qte77.github.io/Agents-eval)

### Project Outline

`# TODO`

## Customer Journey and User Story

Have a look at the [example user story](docs/UserStory.md).

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show Customer Journey</summary>
  <img src="assets/images/customer-journey-activity-light.png#gh-light-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
  <img src="assets/images/customer-journey-activity-dark.png#gh-dark-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

### Agents

#### Manager Agent

- **Description**: Oversees research and analysis tasks, coordinating the efforts of the research, analysis, and synthesizer agents to provide comprehensive answers to user queries. Delegates tasks and ensures the accuracy of the information.
- **Responsibilities**:
  - Coordinates the research, analysis, and synthesis agents.
  - Delegates research tasks to the Research Agent.
  - Delegates analysis tasks to the Analysis Agent.
  - Delegates synthesis tasks to the Synthesizer Agent.
  - Ensures the accuracy of the information.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

#### Researcher Agent

- **Description**: Gathers and analyzes data relevant to a given topic, utilizing search tools to collect data and verifying the accuracy of assumptions, facts, and conclusions.
- **Responsibilities**:
  - Gathers and analyzes data relevant to the topic.
  - Uses search tools to collect data.
  - Checks the accuracy of assumptions, facts, and conclusions.
- **Tools**:
  - [DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool)
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

#### Analyst Agent

- **Description**: Checks the accuracy of assumptions, facts, and conclusions in the provided data, providing relevant feedback and ensuring data integrity.
- **Responsibilities**:
  - Checks the accuracy of assumptions, facts, and conclusions.
  - Provides relevant feedback if the result is not approved.
  - Ensures data integrity.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

#### Synthesizer Agent

- **Description**: Outputs a well-formatted scientific report using the data provided, maintaining the original facts, conclusions, and sources.
- **Responsibilities**:
  - Outputs a well-formatted scientific report using the provided data.
  - Maintains the original facts, conclusions, and sources.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Dataset used

#### PeerRead Scientific Paper Review Dataset

The system includes comprehensive integration with the [PeerRead dataset](https://github.com/allenai/PeerRead) for scientific paper review evaluation:

- **Purpose**: Generate and evaluate scientific paper reviews using the Multi-Agent System
- **Architecture**: Clean separation between review generation (MAS) and evaluation (external system)
- **Workflow**:
  1. **MAS**: PDF → Review Generation → Persistent Storage (`src/app/data_utils/reviews/`)
  2. **External Evaluation**: Load Reviews → Similarity Analysis → Results
- **Documentation**: See [PeerRead Agent Usage Guide](docs/peerread-agent-usage.md)

<!-- # FIXME
- **Architecture Diagram**: [Refactored PeerRead System](docs/arch_vis/c4-refactored-peerread-system.plantuml)
-->

### Review Workflow

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show Review Workflow</summary>
  <img src="assets/images/MAS-Review-Workflow-dark.png#gh-light-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
  <img src="assets/images/MAS-Review-Workflow-light.png#gh-dark-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
</details>

### LLM-as-a-Judge

`# TODO`

### Custom Evaluations Metrics Baseline

As configured in [config_eval.json](src/app/config/config_eval.json).

```json
{
    "evaluators_and_weights": {
        "planning_rational": "1/6",
        "task_success": "1/6",
        "tool_efficiency": "1/6",
        "coordination_quality": "1/6",
        "time_taken": "1/6",
        "text_similarity": "1/6"
    }
}
```

### Eval Metrics Sweep

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Eval Metrics Sweep</summary>
  <img src="assets/images/metrics-eval-sweep-light.png#gh-light-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
  <img src="assets/images/metrics-eval-sweep-dark.png#gh-dark-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
</details>

<!-- markdownlint-enable MD033 -->

### Tools available

Other pydantic-ai agents and [pydantic-ai DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool).

<!-- # TODO
- Exa
- Ffirecrawl
-->

### Agentic System Architecture

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show MAS Overview</summary>
  <img src="assets/images/MAS-C4-Overview-dark.png#gh-dark-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
  <img src="assets/images/MAS-C4-Overview-light.png#gh-light-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
</details>
<details>
  <summary>Show MAS Detailed</summary>
  <img src="assets/images/MAS-C4-Detailed-dark.png#gh-dark-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
  <img src="assets/images/MAS-C4-Detailed-light.png#gh-light-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

### Project Repo Structure

```sh
|- .devcontainer  # pre-configured dev env
|- .github  # workflows
|- .streamlit  # config.toml
|- .vscode  # extensions, settings
|- assets/images
|- docs
|- src  # source code
   |- app
      |- agents
      |- config
      |- evals
      |- utils
      |- __init__.py
      |- main.py
      \- py.typed
   |- examples
   |- gui
   \- run_gui.py
|- tests
|- .env.example  # example env vars
|- .gitignore
|- .gitmessage
|- AGENTS.md  # north star document for AI agents (agentsmd.com)
|- CHANGEOG.md  # short project history
|- CLAUDE.md  # points to AGENTS.md
|- Dockerfile  # create app image
|- LICENSE.md
|- Makefile  # helper scripts
|- mkdocs.yaml  # docu from docstrings
|- pyproject.toml  # project settings
|- README.md  # project description
\- uv.lock  # resolved package versions
```

## Landscape overview

### Agentic System Frameworks

- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [restack](https://www.restack.io/)
- [smolAgents](https://github.com/huggingface/smolagents)
- [AutoGen](https://github.com/microsoft/autogen)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [Langchain](https://github.com/langchain-ai/langchain)
- [Langflow](https://github.com/langflow-ai/langflow)

### Agent-builder

- [Archon](https://github.com/coleam00/Archon)
- [Agentstack](https://github.com/AgentOps-AI/AgentStack)

### Evaluation

- Focusing on agentic systems
  - [AgentNeo](https://github.com/raga-ai-hub/agentneo)
  - [AutoGenBench](https://github.com/microsoft/autogen/blob/0.2/samples/tools/autogenbench)
  - [Langchain AgentEvals](https://github.com/langchain-ai/agentevals), trajectory or LLM-as-a-judge
  - [Mosaic AI Agent Evaluation](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html)
  - [RagaAI-Catalyst](https://github.com/raga-ai-hub/RagaAI-Catalyst)
  - [AgentBench](https://github.com/THUDM/AgentBench)
- RAG oriented
  - [RAGAs](https://github.com/explodinggradients/ragas)
- LLM apps
  - [DeepEval](https://github.com/confident-ai/deepeval)
  - [Langchain OpenEvals](https://github.com/langchain-ai/openevals)
  - [MLFlow LLM Evaluate](https://mlflow.org/docs/latest/llms/llcheckm-evaluate/index.html)
  - [DeepEval (DeepSeek)]( github.com/confident-ai/deepeval)

### Observation, Monitoring, Tracing

- [AgentOps - Agency](https://www.agentops.ai/)
- [arize](https://arize.com/)
- [Langtrace](https://www.langtrace.ai/)
- [LangSmith - Langchain](https://www.langchain.com/langsmith)
- [Weave - Weights & Biases](https://wandb.ai/site/weave/)
- [Pydantic- Logfire](https://pydantic.dev/logfire)
- [comet Opik](https://github.com/comet-ml/opik)
- [Langfuse](https://github.com/langfuse/langfuse)
- [helicone](https://github.com/Helicone/helicone)
- [langwatch](https://github.com/langwatch/langwatch)

### Datasets

- [awesome-reasoning - Collection of datasets](https://github.com/neurallambda/awesome-reasoning)

#### Scientific

- [SWIF2T](https://arxiv.org/abs/2405.20477), Automated Focused Feedback Generation for Scientific Writing Assistance, 2024, 300 peer reviews citing weaknesses in scientific papers and conduct human evaluation
- [PeerRead](https://github.com/allenai/PeerRead), A Dataset of Peer Reviews (PeerRead): Collection, Insights and NLP Applications, 2018, 14K paper drafts and the corresponding accept/reject decisions, over 10K textual peer reviews written by experts for a subset of the papers, structured JSONL, clear labels, See [A Dataset of Peer Reviews (PeerRead):Collection, Insights and NLP Applications](https://arxiv.org/pdf/1804.09635)
- [BigSurvey](https://www.ijcai.org/proceedings/2022/0591.pdf), Generating a Structured Summary of Numerous Academic Papers: Dataset and Method, 2022, 7K survey papers and 430K referenced papers abstracts
- [SciXGen](https://arxiv.org/abs/2110.10774), A Scientific Paper Dataset for Context-Aware Text Generation, 2021, 205k papers
- [scientific_papers](https://huggingface.co/datasets/armanc/scientific_papers), 2018, two sets of long and structured documents, obtained from ArXiv and PubMed OpenAccess, 300k+ papers, total disk 7GB

#### Reasoning, Deduction, Commonsense, Logic

- [LIAR](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip), fake news detection, only 12.8k records, single label
- [X-Fact](https://github.com/utahnlp/x-fact/), Benchmark Dataset for Multilingual Fact Checking, 31.1k records, large, multilingual
- [MultiFC](https://www.copenlu.com/publication/2019_emnlp_augenstein/), A Real-World Multi-Domain Dataset for Evidence-Based Fact Checking of Claims, 34.9k records
- [FEVER](https://fever.ai/dataset/fever.html), Fact Extraction and VERification, 185.4k records
- TODO GSM8K, bAbI, CommonsenseQA, DROP, LogiQA, MNLI

#### Planning, Execution

- [Plancraft](https://arxiv.org/abs/2412.21033), an evaluation dataset for planning with LLM agents, both a text-only and multi-modal interface
- [IDAT](https://arxiv.org/abs/2407.08898), A Multi-Modal Dataset and Toolkit for Building and Evaluating Interactive Task-Solving Agents
- [PDEBench](https://github.com/pdebench/PDEBench), set of benchmarks for scientific machine learning
- [MatSci-NLP](https://arxiv.org/abs/2305.08264), evaluating the performance of natural language processing (NLP) models on materials science text
- TODO BigBench Hard, FSM Game

#### Tool Use, Function Invocation

- [Trelis Function Calling](https://huggingface.co/datasets/Trelis/function_calling_v3)
- [KnowLM Tool](https://huggingface.co/datasets/zjunlp/KnowLM-Tool)
- [StatLLM](https://arxiv.org/abs/2502.17657), statistical analysis tasks, LLM-generated SAS code, and human evaluation scores
- TODO ToolComp

### Benchmarks

- [SciArena: A New Platform for Evaluating Foundation Models in Scientific Literature Tasks](https://allenai.org/blog/sciarena)
- [AgentEvals CORE-Bench Leaderboard](https://huggingface.co/spaces/agent-evals/core_leaderboard)
- [Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Chatbot Arena LLM Leaderboard](https://lmsys.org/projects/)
- [GAIA Leaderboard](https://gaia-benchmark-leaderboard.hf.space/)
- [GalileoAI Agent Leaderboard](https://huggingface.co/spaces/galileo-ai/agent-leaderboard)
- [WebDev Arena Leaderboard](https://web.lmarena.ai/leaderboard)
- [MiniWoB++: a web interaction benchmark for reinforcement learning](https://miniwob.farama.org/)

### Research Agents

- [Ai2 Scholar QA](https://qa.allen.ai/chat)

## Further Reading

- List of papers inspected: [further_reading](docs/papers/further_reading.md)
- [Visualization of Papers inspected](https://claude.ai/public/artifacts/7761a54c-f49b-486b-9e28-7aa2de8b3c86)
- [Agents-eval Enhancement Recommendations based on the Papers](https://qte77.github.io/ai-agents-eval-enhancement-recommendations/)
- [Papers Meta Review](https://qte77.github.io/ai-agents-eval-papers-meta-review/)
- [Papers Comprehensive Analysis](https://qte77.github.io/ai-agents-eval-comprehensive-analysis/)

## Note: Context Framework for AI Agents

This project includes a context framework for AI coding agents designed for structured development and collaboration.

### Documentation Hierarchy

The framework uses a layered documentation approach:

```bash
CLAUDE.md (entry point)
    ↓
AGENTS.md (core agent instructions)
    ↓
├── CONTRIBUTING.md (shared development workflows & standards)
├── AGENT_REQUESTS.md (agentic requests to humans, escalation & collaboration)
└── AGENT_LEARNINGS.md (agentic pattern discovery & knowledge sharing)
```

### CLI/Extensions used

- [OpenCode](https://github.com/sst/opencode)
- [crush](https://github.com/charmbracelet/crush)
- [cline](https://github.com/cline/cline)
- [Claude Code](https://github.com/anthropics/claude-code)
- [Google Gemini](https://github.com/google-gemini/gemini-cli)
- [Alibaba qwen-code](https://github.com/QwenLM/qwen-code )

### Core Components

- **AGENTS.md**: Core agent instructions with project patterns, conventions, and decision framework
- **CONTRIBUTING.md**: Shared development workflows, coding standards, and collaboration guidelines
- **AGENT_REQUESTS.md**: Human escalation process and active collaboration requests
- **AGENT_LEARNINGS.md**: Accumulated patterns, solutions, and knowledge sharing

### Agent Development Workflow

1. **Follow AGENTS.md** - Read project conventions, patterns, and quality standards
2. **Use CONTRIBUTING.md** - Reference development workflows, testing guidelines, and coding standards
3. **Apply Quality Framework** - Use task readiness assessment before implementation

### Quality Framework Integration

- Built-in quality evaluation with minimum thresholds (Context: 8/10, Clarity: 7/10, Alignment: 8/10, Success: 7/10)
- BDD/TDD approach integration following project patterns
- Automatic validation using unified command reference with error recovery
- TodoWrite tool integration for progress tracking and transparency
