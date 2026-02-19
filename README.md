<!-- markdownlint-disable MD033 -->

# Agents-eval

A Multi-Agent System (MAS) evaluation framework using PydanticAI that generates and evaluates scientific paper reviews through a three-tiered assessment approach: traditional metrics, LLM-as-a-Judge, and graph-based complexity analysis.

> Ultimate Goal: Evaluate multi-agent AI systems objectively - Three-tiered framework for researchers and developers building autonomous agent teams

**I am a:** [**User/Researcher**](#userresearcher) | [**Human Developer**](#human-developer) | [**AI Agent**](#ai-agent)

[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
![Version](https://img.shields.io/badge/version-3.3.0-58f4c2.svg)
[![CodeQL](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/Agents-eval/badge)](https://www.codefactor.io/repository/github/qte77/Agents-eval)
[![ruff](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)

**DevEx** [![vscode.dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=vscode.dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://vscode.dev/github/qte77/Agents-eval)
[![Codespace Dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval)
[![Codespace Dev Ollama](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev%20Ollama&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev_ollama/devcontainer.json)
[![llms.txt (UitHub)](https://img.shields.io/badge/llms.txt-uithub-800080.svg)](https://uithub.com/qte77/Agents-eval)
[![llms.txt (GitToDoc)](https://img.shields.io/badge/llms.txt-GitToDoc-fe4a60.svg)](https://gittodoc.com/qte77/Agents-eval)

## User/Researcher

- [**Codespace Dev**](https://github.com/codespaces/new?repo=qte77/Agents-eval) - Immediate access
- [**Documentation Site**](https://qte77.github.io/Agents-eval) - Complete reference
- **Understanding the System:** [UserStory.md](docs/UserStory.md) - User workflows, use cases, and acceptance criteria

## Human Developer

- **Quick Start:** `make setup_dev && make app_quickstart` (downloads sample data, evaluates smallest paper)
- **Full Setup:** `make setup_dev` then `make app_cli ARGS="--help"`
- **Core Resources:**
  - [CONTRIBUTING.md](CONTRIBUTING.md) - Commands, workflows, coding patterns
  - [docs/architecture.md](docs/architecture.md) - Technical design and decisions
  - [docs/roadmap.md](docs/roadmap.md) - Development roadmap
- **Development Flow:** Setup → Code → `make validate` → Commit
- **Environment:** Configure API keys per [.env.example](.env.example)

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

**Current Release**: Version 3.3.0 - Sprint 8 (Delivered)

- CC engine consolidation: `cc_engine.py` with solo + teams support, retired shell scripts
- Report generation: CLI `--generate-report`, GUI button, rule-based suggestion engine with optional LLM
- Tool fix: `get_paper_content(paper_id)` replaces crash-prone `read_paper_pdf_tool`
- API key cleanup: removed `"not-required"` sentinel, fixed judge auto-mode model inheritance
- GUI a11y/UX: WCAG fixes, judge settings dropdowns, environment-aware URL resolution
- Graph alignment: unified `type` node attribute across export and rendering

**Next**: Sprint 9 (In Progress) — sweep results UI ([PRD](docs/sprints/PRD-Sprint9-Ralph.md))

For version history see the [CHANGELOG](CHANGELOG.md).

## Setup and Usage

See [CONTRIBUTING.md](CONTRIBUTING.md#complete-command-reference) for all commands.

Note: Chat configuration uses free inference endpoints and models which are subject to change by the providers. See [free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) for alternatives. LLM-as-judge is also subject to the chat configuration.

## Project Outline

**System**: Multi-agent evaluation pipeline (Manager → Researcher → Analyst → Synthesizer) with PydanticAI, processing [PeerRead](https://github.com/allenai/PeerRead) scientific papers.

**Evaluation Approach**: Traditional metrics + LLM-as-a-Judge + Graph-based complexity analysis → Composite scoring. See [PRD.md](docs/PRD.md#evaluation-metrics) for metric definitions.

**Requirements**: [PRD.md](docs/PRD.md) | **Architecture**: [architecture.md](docs/architecture.md) | **Dataset Usage**: [PeerRead Agent Usage Guide](docs/howtos/peerread-agent-usage.md)

## Diagrams

<details>
  <summary>Show Customer Journey</summary>
  <img src="assets/images/customer-journey-activity-light.png#gh-light-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
  <img src="assets/images/customer-journey-activity-dark.png#gh-dark-mode-only" alt="Customer Journey" title="Customer Journey" width="80%" />
</details>

<details>
  <summary>Show Review Workflow</summary>
  <img src="assets/images/MAS-Review-Workflow-dark.png#gh-light-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
  <img src="assets/images/MAS-Review-Workflow-light.png#gh-dark-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
</details>

<details>
  <summary>Show Eval Metrics Sweep</summary>
  <img src="assets/images/metrics-eval-sweep-light.png#gh-light-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
  <img src="assets/images/metrics-eval-sweep-dark.png#gh-dark-mode-only" alt="Eval Metrics Sweep" title="Eval Metrics Sweep" width="60%" />
</details>

## Examples

See [src/examples/README.md](src/examples/README.md) for self-contained demonstrations of Sprint 5-6 features:
`basic_evaluation.py`, `judge_settings_customization.py`, `engine_comparison.py`.

## References

- [AI Agent Evaluation Landscape](docs/landscape/landscape.md) - Frameworks, tools, datasets, benchmarks
- [Tracing & Observation Methods](docs/landscape/trace_observe_methods.md) - Observability analysis
- [List of papers inspected](docs/research/further_reading.md)
- [Enhancement Recommendations](https://qte77.github.io/ai-agents-eval-enhancement-recommendations/)
- [Papers Meta Review](https://qte77.github.io/ai-agents-eval-papers-meta-review/)
- [Papers Comprehensive Analysis](https://qte77.github.io/ai-agents-eval-comprehensive-analysis/)

</details>
