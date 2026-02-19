# Desired State and End Goals

## Vision

### Strategic Goals

The strategic vision of Agents-eval encompasses three goal areas:

**Universal Evaluation Standard**: Agents-eval aims to be established as a
reference framework for the assessment of agentic AI systems -- with standardized
metrics that enable systematic comparisons across different frameworks, models,
and configurations.

**Technology-Agnostic Extensibility**: The framework shall support additional
agentic frameworks (AutoGen, CrewAI, LangChain) beyond the current PydanticAI
implementation through a pluggable adapter architecture. Standardized interfaces
and Pydantic data models form the foundation for this.

**Continuous Innovation Platform**: The architecture shall adapt to emerging
agentic AI paradigms and new evaluation methodologies without losing backward
compatibility. New metrics are integrated as plugins without modifying the
existing pipeline.

### Distinction from Current State

The current state (Sprint 7 active) delivers a functional framework with
PydanticAI as the sole agent framework, seven identified candidate metrics
for future integration, and an evaluation domain limited to PeerRead. The
desired state extends this through multi-framework support, a broader metric
palette, and cross-domain evaluation scenarios.

## Target Architecture

The target architecture extends the existing plugin architecture across four layers:

**Abstraction Layer**: Technology-agnostic interfaces (`EvaluatorPlugin`,
`AgentAdapter`) enable the integration of arbitrary agentic frameworks without
changes to the evaluation pipeline.

**Evaluation Engine**: Extension of the three-tier architecture with new metrics
from the candidate catalog (see table below). Configurable weighting and adaptive
weight redistribution for missing tier results are retained.

**Observability Layer**: Expansion of the existing Logfire/Phoenix integration
with structured trace analysis for multi-framework comparisons and sweep results.

**Report Generation** (Sprint 8): Structured Markdown reports with tier scores,
identified weaknesses, and actionable improvement suggestions -- available via
CLI (`--generate-report`) and Streamlit GUI.

## Roadmap (Sprint 8+)

Sprint 8 (Draft) focuses on:

- **Feature 1**: Report generation in CLI and GUI with actionable suggestions
- **Feature 2--3**: Graph attribute alignment and MAESTRO security hardening
- **Feature 4--5**: Code quality improvements and PydanticAI streaming support

Beyond that, the following extensions are planned for later sprints:

- Integration of candidate metrics from the research context
- Multi-framework adapters (AutoGen, CrewAI, LangChain)
- Optional containerized deployment modes (ADR-007, unscheduled)
- `--engine=claude-api` as a separate comparison mode for model-vs-model analyses
  (ADR-008)

## Quantitative Success Goals

The following table shows candidate metrics identified for future integration,
ordered by priority:

| Metric                  | Source                    | Complexity | Impact |
|-------------------------|---------------------------|------------|--------|
| `fix_rate`              | SWE-EVO                   | Low        | High   |
| `evaluator_consensus`   | TEAM-PHI / Agents4Science | Low        | High   |
| `delegation_depth`      | HDO / Agents4Science      | Low        | High   |
| `rubric_alignment`      | [2512.23707]              | Medium     | High   |
| `handoff_quality`       | Arize Multi-Agent         | Medium     | High   |
| `coordination_topology` | Evolutionary Boids        | Low        | Medium |
| `path_convergence`      | Arize Phoenix             | Low        | Medium |

Technical target values include:

- Evaluation latency under one second for Tier 1 (traditional metrics)
- Complete validation (`make validate`) with zero critical security findings
- Test coverage above 60% for all critical modules (achieved for `llms/models.py`,
  `agent_factories.py`, `datasets_peerread.py` in Sprint 6)
- Sweep results for all 8 agent compositions reproducible with statistically
  evaluable sample sizes
