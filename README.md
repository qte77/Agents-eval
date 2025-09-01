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

### Technical Analysis

- [Tracing & Observation Methods](docs/landscape/trace_observe_methods.md) - Technical analysis of observability tool implementations

### Project Outline

**Current Phase**: Sprint 1 - Three-Tiered Evaluation Framework Implementation

**System**: Multi-agent evaluation pipeline (Manager → Researcher → Analyst → Synthesizer) with PydanticAI, processing PeerRead scientific papers through large context models.

**Evaluation Approach**: Traditional metrics + LLM-as-a-Judge + Graph-based complexity analysis → Composite scoring

**Next**: Sprint 2 architectural refactoring (engine separation), then advanced evaluation features and production deployment.

## Customer Journey and User Story

Have a look at the [example user story](docs/UserStory.md).

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show Customer Journey</summary>
  <img src="assets/images/customer-journey-activity-light.png#gh-light-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
  <img src="assets/images/customer-journey-activity-dark.png#gh-dark-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

### Architecture

For detailed agent descriptions, data flow, and system architecture, see [docs/architecture.md](docs/architecture.md).

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

### Project Repo Structure

```sh
|- .devcontainer  # pre-configured dev env
|- .github  # workflows
|- .streamlit  # config.toml
|- .vscode  # extensions, settings
|- assets/images  # generated diagrams (PNG)
|- docs
   |- arch_vis  # PlantUML source files + generation tools
   |- architecture.md  # detailed system architecture
   |- landscape/       # landscape analysis and evaluation tools
      |- landscape.md  # AI agent ecosystem overview
      |- landscape-agent-frameworks-infrastructure.md  # agent frameworks & tools
      |- landscape-evaluation-data-resources.md  # evaluation frameworks & datasets
      |- agent_eval_metrics.md  # evaluation metrics catalog
      \- trace_observe_methods.md  # observability analysis
   \- papers/  # research papers and analysis
|- src  # source code
   |- app
      |- agents
      |- config
      |- evals
      |- utils
      |- main.py
      \- py.typed
   |- examples
   |- gui
   \- run_gui.py
|- tests
|- .env.example  # example env vars
|- .gitignore
|- .gitmessage
|- AGENTS.md  # AI agent instructions and guidelines
|- CHANGELOG.md  # project history
|- CLAUDE.md  # points to AGENTS.md
|- CONTRIBUTING.md  # shared human and agent development workflows
|- AGENT_REQUESTS.md  # agent-human escalation
|- AGENT_LEARNINGS.md  # accumulated agent knowledge
|- Dockerfile  # create app image
|- LICENSE.md
|- Makefile  # helper scripts
|- mkdocs.yaml  # docu from docstrings
|- pyproject.toml  # project settings
|- README.md  # project description (for humans)
\- uv.lock  # resolved package versions
```

## Related Work

For a comprehensive overview of AI agent frameworks, evaluation tools, datasets, and benchmarks, see:

- [AI Agent Evaluation Landscape Overview](docs/landscape/landscape.md) - Navigation guide and document overview
- [Agent Frameworks & Infrastructure](docs/landscape/landscape-agent-frameworks-infrastructure.md) - Agent frameworks, LLMs, observability, and development tools  
- [Evaluation & Data Resources](docs/landscape/landscape-evaluation-data-resources.md) - Evaluation frameworks, datasets, benchmarks, and analysis tools

## Further Reading

- [Project architecture](docs/architecture.md)
- [List of papers inspected](docs/papers/further_reading.md)
- [AI Agent Evaluation Landscape](docs/landscape/landscape.md)
- [Visualization of Papers inspected](https://claude.ai/public/artifacts/7761a54c-f49b-486b-9e28-7aa2de8b3c86)
- [Visualization of related frameworks inspected](https://claude.ai/public/artifacts/e883fe7a-f500-4acc-b397-d6b73e1765ed)
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
- **docs/architecture.md**: Detailed system architecture, agents, and data flow
- **docs/landscape/**: Comprehensive AI agent ecosystem analysis and evaluation resources

### Agent Development Workflow

1. **Follow AGENTS.md** - Read project conventions, patterns, and quality standards
2. **Use CONTRIBUTING.md** - Reference development workflows, testing guidelines, and coding standards
3. **Apply Quality Framework** - Use task readiness assessment before implementation

### Quality Framework Integration

- Built-in quality evaluation with minimum thresholds (Context: 8/10, Clarity: 7/10, Alignment: 8/10, Success: 7/10)
- BDD/TDD approach integration following project patterns
- Automatic validation using unified command reference with error recovery
- TodoWrite tool integration for progress tracking and transparency
