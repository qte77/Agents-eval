<!-- markdownlint-disable MD033 -->

# Agents-eval

> Evaluate multi-agent AI systems objectively — Three-tiered framework for researchers and developers building autonomous agent teams

A Multi-Agent System (MAS) evaluation framework using PydanticAI that generates and evaluates scientific paper reviews through a three-tiered assessment approach: Tier 1 (Traditional Metrics), Tier 2 (LLM-as-a-Judge), and Tier 3 (Graph-Based Analysis).

**I am a:** [**User/Researcher**](#userresearcher) | [**Human Developer**](#human-developer) | [**AI Agent**](#ai-agent)

[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
![Version](https://img.shields.io/badge/version-5.0.0-58f4c2.svg)
[![Deploy Docs](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)
[![CodeQL](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/Agents-eval/badge)](https://www.codefactor.io/repository/github/qte77/Agents-eval)
[![ruff](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/Agents-eval/actions/workflows/links-fail-fast.yaml)

[![llms.txt](https://img.shields.io/badge/llms.txt-spec-800080.svg)](https://qte77.github.io/Agents-eval/llms.txt)
[![Flat Repo (UitHub)](https://img.shields.io/badge/Flat_Repo-uithub-800080.svg)](https://uithub.com/qte77/Agents-eval)
[![Flat Repo (GitToDoc)](https://img.shields.io/badge/Flat_Repo-GitToDoc-fe4a60.svg)](https://gittodoc.com/qte77/Agents-eval)
[![vscode.dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=vscode.dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://vscode.dev/github/qte77/Agents-eval)
[![Codespace Dev](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval)
[![Codespace Dev Ollama](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Codespace%20Dev%20Ollama&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://github.com/codespaces/new?repo=qte77/Agents-eval&devcontainer_path=.devcontainer/setup_dev_ollama/devcontainer.json)

## Quick Start

```bash
make setup_dev && make app_quickstart    # downloads sample data, evaluates smallest paper
make app_cli ARGS="--help"               # all CLI options
```

**Common commands:**

```bash
make app_cli ARGS="--paper-id=1105.1072"                                          # evaluate a specific paper
make app_cli ARGS="--paper-id=1105.1072 --engine=cc"                              # Claude Code engine (requires claude CLI)
make app_cli ARGS="--paper-id=1105.1072 --engine=cc --cc-teams"                   # CC multi-agent orchestration
make app_sweep ARGS="--paper-ids 1105.1072 --repetitions 1 --all-compositions"    # benchmark all 8 agent compositions
make app_batch_run ARGS="--paper-ids 1105.1072 --parallel 4"                      # parallel runs, resilient to errors
make app_batch_eval                                                               # summarize all runs into output/summary.md
```

> All commands use the default provider (`github`). Set your API key in `.env` or pass `--chat-provider=<provider>`. See [.env.example](.env.example).

## User/Researcher

- [**Documentation Site**](https://qte77.github.io/Agents-eval) — Complete reference
- [**UserStory.md**](docs/UserStory.md) — User workflows, use cases, and acceptance criteria
- [**Agent Tools & CLI Reference**](docs/howtos/peerread-agent-usage.md) — Tool signatures, CLI examples by category, troubleshooting
- [**Codespace**](https://github.com/codespaces/new?repo=qte77/Agents-eval) — Immediate access in browser

## Human Developer

- [**CONTRIBUTING.md**](CONTRIBUTING.md) — Commands, workflows, coding patterns
- [**architecture.md**](docs/architecture.md) — Technical design and decisions
- [**roadmap.md**](docs/roadmap.md) — Development roadmap
- **Development flow:** Setup → Code → `make validate` → Commit

## AI Agent

- **READ FIRST:** [AGENTS.md](AGENTS.md) — Behavioral rules and compliance requirements
- **Technical Patterns:** [CONTRIBUTING.md](CONTRIBUTING.md) — Implementation standards and commands

## Project Outline

**System**: Multi-agent evaluation pipeline (Manager → Researcher → Analyst → Synthesizer) with PydanticAI, processing [PeerRead](https://github.com/allenai/PeerRead) scientific papers.

**Evaluation Approach**: Tier 1 (Traditional Metrics) + Tier 2 (LLM-as-a-Judge) + Tier 3 (Graph-Based Analysis) → Composite scoring. See [architecture.md](docs/architecture.md) for metric definitions.

For version history see the [CHANGELOG](CHANGELOG.md).

<details>
<summary><strong>Diagrams</strong></summary>

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

</details>

## Examples

See [src/examples/README.md](src/examples/README.md) for self-contained demonstrations:
`basic_evaluation.py`, `judge_settings_customization.py`, `engine_comparison.py`.

## References

- [AI Agent Evaluation Landscape](docs/landscape/landscape.md) — Frameworks, tools, datasets, benchmarks
- [Tracing & Observation Methods](docs/landscape/trace_observe_methods.md) — Observability analysis
- [List of papers inspected](docs/research/further_reading.md)
- [Enhancement Recommendations](https://qte77.github.io/ai-agents-eval-enhancement-recommendations/)
- [Papers Meta Review](https://qte77.github.io/ai-agents-eval-papers-meta-review/)
- [Papers Comprehensive Analysis](https://qte77.github.io/ai-agents-eval-comprehensive-analysis/)
