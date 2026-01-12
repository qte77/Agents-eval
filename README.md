<!-- markdownlint-disable MD033 -->

# Agents-eval

A Multi-Agent System (MAS) evaluation framework using PydanticAI that generates and evaluates scientific paper reviews through a three-tiered assessment approach: traditional metrics, LLM-as-a-Judge, and graph-based complexity analysis.

> Ultimate Goal: Evaluate multi-agent AI systems objectively - Three-tiered framework for researchers and developers building autonomous agent teams

**I am a:** [**User/Researcher**](#userresearcher) | [**Human Developer**](#human-developer) | [**AI Agent**](#ai-agent)

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
[![Codespace Dev Ollama](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev%20Ollama&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev_ollama/devcontainer.json)
[![llms.txt (UitHub)](https://img.shields.io/badge/llms.txt-uithub-800080.svg)](https://github.com/qte77/Agents-eval)
[![llms.txt (GitToDoc)](https://img.shields.io/badge/llms.txt-GitToDoc-fe4a60.svg)](https://gittodoc.com/qte77/Agents-eval)

## User/Researcher

- [**Codespace Dev**](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev/devcontainer.json) - Immediate access
- [**Documentation Site**](https://qte77.github.io/Agents-eval) - Complete reference
- **Understanding the System:**
  - **What it does**: [UserStory.md](docs/UserStory.md) - User workflows and use cases
  - **How it works**: Multi-agent evaluation pipeline using PeerRead dataset for AI system assessment

## Human Developer

- **Quick Start:** `make setup_dev && make run_cli`
- **Core Resources:**
  - **Development Standards**: [CONTRIBUTING.md](CONTRIBUTING.md) - Commands, workflows, coding patterns
  - **System Architecture**: [docs/architecture.md](docs/architecture.md) - Technical design and decisions
  - **Current Sprint**: [Sprint 1 Status](docs/sprints/2025-08_Sprint1_ThreeTieredEval.md) - Active development
- **Development Flow:** Setup → Code → `make validate` → Commit

## AI Agent

- **READ FIRST:** [AGENTS.md](AGENTS.md) - Behavioral rules and compliance requirements
- **Technical Patterns:** [CONTRIBUTING.md](CONTRIBUTING.md) - Implementation standards and commands
- **Agent Workflow:** AGENTS.md (rules) → CONTRIBUTING.md (patterns) → Execute

---

<details>
<summary><strong>
  Expand for Project Details
</strong></summary>

## Status

(DRAFT) (WIP) ----> Not fully implemented yet

For version history have a look at the [CHANGELOG](CHANGELOG.md).

## Setup and Usage

- `make setup_prod`
- `make setup_dev` or `make setup_dev_ollama`
- `make run_cli` or `make run_cli ARGS="--help"`
  - `make run_cli ARGS="--paper-number=350 --chat-provider=ollama"`
- `make run_gui`
- `make test_all`

### Environment

[.env.example](.env.example) contains examples for usage of API keys and variables.

```text
# inference EP example
GEMINI_API_KEY="xyz"

# tools
TAVILY_API_KEY=""

# log/mon/trace example
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

## Documentation Site

[Agents-eval Documentation](https://qte77.github.io/Agents-eval) - Complete project reference

### Technical Analysis

- [Tracing & Observation Methods](docs/landscape/trace_observe_methods.md) - Technical analysis of observability tool implementations

### Project Outline

**System**: Multi-agent evaluation pipeline (Manager → Researcher → Analyst → Synthesizer) with PydanticAI, processing PeerRead scientific papers through large context models.

**Evaluation Approach**: Traditional metrics + LLM-as-a-Judge + Graph-based complexity analysis → Composite scoring

**Requirements**: See [PRD.md](docs/PRD.md) for functional requirements and feature specifications.  
**Implementation**: See [architecture.md](docs/architecture.md) for technical details, current status, and development timeline.

## Customer Journey and User Story

Have a look at the [example user story](docs/UserStory.md).

<details>
  <summary>Show Customer Journey</summary>
  <img src="assets/images/customer-journey-activity-light.png#gh-light-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
  <img src="assets/images/customer-journey-activity-dark.png#gh-dark-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
</details>

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
- **Documentation**: See [PeerRead Agent Usage Guide](docs/howtos/maintaining-agents-md.md)

### Review Workflow

<details>
  <summary>Show Review Workflow</summary>
  <img src="assets/images/MAS-Review-Workflow-dark.png#gh-light-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
  <img src="assets/images/MAS-Review-Workflow-light.png#gh-dark-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
</details>

### Custom Evaluations Metrics Baseline

As configured in [config_eval.json](src/app/config/config_eval.json).

```json
{
    "composite_scoring": {
        "metrics_and_weights": {
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167,
            "tool_efficiency": 0.167,
            "planning_rationality": 0.167,
            "output_similarity": 0.167
        }
    }
}
```

### Eval Metrics Sweep

<details>
  <summary>Eval Metrics Sweep</summary>
  <img src="assets/images/metrics-eval-sweep-light.png#gh-light-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
  <img src="assets/images/metrics-eval-sweep-dark.png#gh-dark-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
</details>

### Project Repo Structure

<details>
<summary><strong>Expand Structure</strong></summary>

**Key Directories:**

- `src/app/` - Core application (agents, config, evals, utils)
- `docs/` - Architecture, landscape analysis, sprint docs
- `tests/` - Test suite mirroring src structure
- `.claude/` - Claude Code skills and Ralph loop scripts

**Documentation:**

- `AGENTS.md` - AI agent instructions
- `CONTRIBUTING.md` - Development workflows
- `architecture.md` - System design details

**Configuration:**

- `pyproject.toml` - Dependencies and project settings
- `Makefile` - Development commands
- `.env.example` - Environment variables template

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete structure details.

</details>

## Related Work

For a comprehensive overview of AI agent frameworks, evaluation tools, datasets, and benchmarks, see:

- [AI Agent Evaluation Landscape Overview](docs/landscape/landscape.md) - Navigation guide and document overview
- [Agent Frameworks & Infrastructure](docs/landscape/landscape-agent-frameworks-infrastructure.md) - Agent frameworks, LLMs, observability, and development tools  
- [Evaluation & Data Resources](docs/landscape/landscape-evaluation-data-resources.md) - Evaluation frameworks, datasets, benchmarks, and analysis tools

## Further Reading

- [Project architecture](docs/architecture.md)
- [List of papers inspected](docs/papers/further_reading.md)
- [AI Agent Evaluation Landscape](docs/landscape/landscape.md)
- [Agents-eval Enhancement Recommendations based on the Papers](https://qte77.github.io/ai-agents-eval-enhancement-recommendations/)
- [Papers Meta Review](https://qte77.github.io/ai-agents-eval-papers-meta-review/)
- [Papers Comprehensive Analysis](https://qte77.github.io/ai-agents-eval-comprehensive-analysis/)

## Note: Context Framework for AI Agents

This project includes a context framework for AI coding agents designed for structured development and collaboration.

### Documentation Hierarchy

**Project Documentation**: See [CONTRIBUTING.md](CONTRIBUTING.md#documentation-hierarchy) for complete project authority structure and single source of truth principles.

**AI Agent Framework**: The framework uses a layered documentation approach:

```text
CLAUDE.md (entry point)
    ↓
AGENTS.md (core agent instructions, decision framework, etc.)
    ↓
├── CONTRIBUTING.md (human and agent shared development workflows & standards)
├── AGENT_REQUESTS.md (agentic requests to humans, escalation & collaboration)
└── AGENT_LEARNINGS.md (agentic pattern discovery, knowledge & solution sharing, long-term memory)
```

### Agent Development Workflow

1. **Follow AGENTS.md** - Read project conventions, patterns, and quality standards
2. **Use CONTRIBUTING.md** - Reference development workflows, testing guidelines, and coding standards
3. **Apply Quality Framework** - Use task readiness assessment before implementation

### Quality Framework Integration

- Built-in quality evaluation with minimum thresholds (Context: 8/10, Clarity: 7/10, Alignment: 8/10, Success: 7/10)
- BDD/TDD approach integration following project patterns
- Automatic validation using unified command reference with error recovery
- TodoWrite tool integration for progress tracking and transparency

</details>
