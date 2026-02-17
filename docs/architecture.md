---
title: Agents-eval Architecture
description: Detailed architecture information for the Agents-eval Multi-Agent System (MAS) evaluation framework
created: 2025-08-31
updated: 2026-02-17
category: architecture
version: 3.6.0
---

This document provides detailed architecture information for the Agents-eval Multi-Agent System (MAS) evaluation framework.

## System Overview

This is a Multi-Agent System (MAS) evaluation framework for assessing agentic AI systems using the **PeerRead dataset** for comprehensive agent performance measurement. The project uses **PydanticAI** as the core framework for agent orchestration and implements a three-tiered evaluation approach: traditional metrics, LLM-as-a-judge assessment, and graph-based complexity analysis.

**Primary Purpose**: Evaluate agent performance in generating academic paper reviews through multiple evaluation methodologies to produce composite performance scores.

## Data Flow

### Agent Execution Flow

1. PeerRead paper input → Manager Agent (with large context window models)
2. Optional: Manager delegates to Researcher Agent (with DuckDuckGo search)
3. Optional: Researcher results → Analyst Agent for validation
4. Optional: Validated data → Synthesizer Agent for review generation
5. Generated review → Comprehensive evaluation pipeline

### Evaluation Pipeline Flow

1. **Traditional Metrics**: Text similarity (BLEU, ROUGE), execution time measurement
2. **LLM-as-a-Judge**: Review quality assessment, agentic execution analysis
3. **Graph-Based Analysis**: Tool call complexity, agent interaction mapping
4. **Composite Scoring**: Final score calculation using formula: (Agentic Results / Execution Time / Graph Complexity)

### Three-Tier Validation Strategy

**Core Principle:** Tiers validate and enhance each other for robust evaluation.

| Tier | Role | Focus |
| ------ | ------ | ------- |
| Tier 1 (Traditional) | VALIDATOR | Fast, objective text similarity baseline |
| Tier 2 (LLM-Judge) | VALIDATOR | Semantic quality assessment |
| Tier 3 (Graph) | PRIMARY | Coordination patterns from execution traces |

**Validation Logic:**

- **All 3 tiers agree** → High confidence in MAS quality
- **Tier 3 good, Tier 1/2 fail** → Good coordination, poor output quality
- **Tier 1/2 good, Tier 3 fail** → Good output, inefficient coordination

**Design Goals:**

- **Graph (Tier 3)**: Rich analysis from execution traces - PRIMARY innovation
- **Traditional (Tier 1)**: Keep SIMPLE - lightweight metrics only
- **LLM-Judge (Tier 2)**: Keep SIMPLE - single LLM call, structured output

### Evaluation Approach Decision Tree

```text
Evaluation Requirements Assessment
│
├─ Quick Development/Prototyping?
│  ├─ YES → Use Traditional Metrics Only
│  │         ├─ Basic similarity: BLEU, ROUGE
│  │         └─ Add execution time measurement
│  │
│  └─ NO → Continue Assessment
│
├─ Need Semantic Understanding?
│  ├─ NO → Traditional Metrics + Graph Analysis
│  │        ├─ Focus on coordination patterns
│  │        └─ Tool usage efficiency
│  │
│  └─ YES → Continue Assessment
│
├─ Budget Constraints (API Costs)?
│  ├─ HIGH → Traditional + Graph (Skip LLM Judge)
│  │         ├─ Use local models only
│  │         └─ Focus on behavioral patterns
│  │
│  └─ LOW → Full Three-Tier Evaluation
│
├─ Research/Production Setting?
│  ├─ RESEARCH → Full Pipeline + Extended Analysis
│  │            ├─ All three evaluation tiers
│  │            ├─ Comparative studies
│  │            └─ Statistical significance testing
│  │
│  └─ PRODUCTION → Optimized Pipeline
│               ├─ Cached traditional metrics
│               ├─ Selective LLM judging
│               └─ Real-time graph analysis
│
└─ Result: Choose appropriate combination based on constraints
```

## Evaluation Framework Architecture

### Large Context Model Integration

The evaluation framework is built around large context window models capable of processing full PeerRead papers with automatic selection based on paper token count and intelligent fallback to document chunking for smaller context models.

**Model Selection**: Configurable per provider via `--chat-provider` and `--judge-provider`. See [Large Language Models](landscape-agent-frameworks-infrastructure.md#2-large-language-models) for model comparisons, context limits, and integration approaches.

### Sprint 1: PeerRead Evaluation Components

#### Traditional Evaluation Metrics

**Location**: `src/app/judge/plugins/traditional.py`

- **Output Similarity Assessment** (config: `output_similarity`):
  - Cosine similarity (primary metric from config)
  - Jaccard similarity (secondary metric)
  - Semantic similarity (default metric from config)
  - Confidence threshold: 0.8 (from config)
- **Performance Metrics** (config: `time_taken`):
  - Execution time tracking (end-to-end paper processing)
  - Resource usage monitoring (memory, API calls, token consumption)
- **Task Success Evaluation** (config: `task_success`):
  - Review completeness scoring
  - Structure adherence measurement
  - Academic standard compliance with recommendation weights

#### LLM-as-a-Judge Framework

**Location**: `src/app/judge/plugins/llm_judge.py`

- **Planning Rationality Assessment** (config: `planning_rationality`):
  - Decision-making process quality evaluation
  - Reasoning chain coherence analysis
  - Strategic planning effectiveness
- **Tool Efficiency Evaluation** (config: `tool_efficiency`):
  - Tool usage effectiveness analysis
  - Resource optimization assessment
  - API call efficiency measurement
- **Recommendation Quality Scoring**:
  - Uses config recommendation weights: accept (1.0), weak_accept (0.7), weak_reject (-0.7), reject (-1.0)
  - Generated review vs. ground truth PeerRead reviews
  - Multi-dimensional quality scoring with confidence threshold (0.8)

#### Graph-Based Complexity Analysis

**Location**: `src/app/judge/plugins/graph_metrics.py`

**Approach**: Post-execution behavioral analysis where agents autonomously decide tool use during execution, then observability logs are processed to construct behavioral graphs for retrospective evaluation.

##### Integration Workflow

1. **Agent Execution** → PydanticAI agents (Manager/Researcher/Analyst/Synthesizer) autonomously decide tool use and coordination strategies during PeerRead paper processing
2. **Observability Logging** → Logfire auto-instrumentation captures comprehensive execution traces, tool usage patterns, and agent interactions (viewable via Arize Phoenix)
3. **Graph Construction** → NetworkX processes trace data to build behavioral graphs showing coordination patterns and decision flows
4. **Analysis** → NetworkX analyzes coordination effectiveness, tool usage efficiency, and emergent behavioral patterns from constructed graphs

**Tool Selection**: See [Graph Analysis & Network Tools](landscape-evaluation-data-resources.md#6-graph-analysis--network-tools), [Post-Execution Graph Construction Tools](landscape-evaluation-data-resources.md#8-post-execution-graph-construction-tools), [Observability & Monitoring Platforms](landscape-agent-frameworks-infrastructure.md#4-observability--monitoring), and [Technical Analysis: Tracing Methods](landscape/trace_observe_methods.md) for detailed feasibility assessments and integration approaches.

##### Key Applications for Agent Evaluation

- **Agent Interaction Patterns** - Identify communication flows, coordination effectiveness, and collaboration bottlenecks between Manager/Researcher/Analyst/Synthesizer agents
- **Tool Usage Sequences** - Analyze autonomous tool selection patterns, decision quality, and usage efficiency across agent types and tasks
- **Decision Flow Analysis** - Map how decisions and information propagate through the multi-agent system during PeerRead review generation
- **Coordination Effectiveness** - Correlate behavioral patterns with successful task outcomes and identify optimal coordination strategies
- **Performance Bottlenecks** - Detect where autonomous coordination breaks down, communication fails, or tool usage becomes inefficient

##### Technical Implementation

- **Coordination Quality Analysis** (config: `coordination_quality`):
  - Agent interaction effectiveness using NetworkX post-execution graph analysis
  - Multi-agent orchestration pattern analysis from behavioral traces
  - Communication efficiency measurement through graph centrality metrics
- **Execution Graph Construction**:
  - Tool call pattern mapping from observability logs using spaCy + NetworkX
  - Agent interaction relationship modeling through trace log analysis
  - Decision branching visualization from autonomous agent decision sequences
- **Complexity Metrics Integration**:
  - Node count (discrete actions) → feeds into coordination_quality scoring
  - Edge density (interaction frequency) → affects tool_efficiency evaluation
  - Path optimization → impacts time_taken scoring through coordination analysis
  - Pattern recognition → influences planning_rationality assessment via behavioral analysis

#### Composite Scoring System

**Location**: `src/app/judge/composite_scorer.py`

**Formula**: `Agent Score = Weighted Sum of Six Core Metrics`

**Configuration-Based Metrics** (from `JudgeSettings` via pydantic-settings):

- `time_taken`: 0.167 (16.7% - execution time efficiency)
- `task_success`: 0.167 (16.7% - review completion and accuracy)
- `coordination_quality`: 0.167 (16.7% - agent interaction effectiveness)
- `tool_efficiency`: 0.167 (16.7% - tool usage optimization)
- `planning_rationality`: 0.167 (16.7% - decision-making quality)
- `output_similarity`: 0.167 (16.7% - similarity to PeerRead ground truth)

**Configuration-Based Output**:

- Final weighted score using six metrics above (0.167 each)
- Similarity metrics selection (cosine, jaccard, semantic) with semantic as default
- Recommendation scoring with config weights and confidence threshold (0.8)
- Performance trend analysis with configurable evaluation parameters

**Adaptive Weight Redistribution** (Sprint 5):

- **Single-Agent Mode Detection**: Automatically detects single-agent runs from `GraphTraceData` (0-1 unique agent IDs, empty `coordination_events`)
- **Weight Redistribution**: When single-agent mode is detected, the `coordination_quality` metric (0.167 weight) is excluded and its weight is redistributed equally across the remaining 5 metrics (0.20 each)
- **Transparency**: `CompositeResult` includes `single_agent_mode: bool` flag to indicate when redistribution occurred
- **Compound Redistribution**: When both Tier 2 is skipped (no valid provider) AND single-agent mode is detected, weights are redistributed across the remaining available metrics to always sum to ~1.0

## Implementation Status

**Detailed Timeline**: See [roadmap.md](roadmap.md) for comprehensive sprint history, dependencies, and development phases.

### Current Implementation (Sprint 7 - Active)

**Sprint 6 Key Deliverables** (Delivered):

- **Benchmarking Infrastructure**:
  - MAS composition sweep (`SweepRunner`): 8 agent compositions × N papers × N repetitions
  - Statistical analysis (`SweepAnalyzer`): mean, stddev, min, max per composition
  - Sweep CLI (`run_sweep.py`) with `--provider`, `--paper-numbers`, `--repetitions`, `--all-compositions`
  - Results output: `results.json` (raw) + `summary.md` (Markdown table)

- **CC Baseline Completion**:
  - `CCTraceAdapter` for parsing Claude Code artifacts from headless invocation
  - Artifact collection from `~/.claude/teams/` and `~/.claude/tasks/`

- **Security Hardening**:
  - SSRF prevention: URL validation with domain allowlisting
  - Prompt injection resistance: length limits, XML delimiter wrapping
  - Sensitive data filtering in logs and traces (API keys, tokens)
  - Input size limits for DoS prevention

- **Test Quality**:
  - Security tests in `tests/security/` (SSRF, prompt injection, data scrubbing)
  - Test filesystem isolation via `tmp_path`

**Sprint 7 In Progress**:

- Unified provider configuration (`--chat-provider`, `--judge-provider`, `--judge-model`)
- `--engine=mas|cc` flag for CLI and sweep (replaces `--cc-baseline`)
- Sweep rate-limit resilience (retry with backoff, incremental result persistence)
- GUI: real-time debug log streaming, paper selection dropdown, editable settings
- `_handle_model_http_error` fix: re-raise instead of `SystemExit(1)` on HTTP 429

**Sprint 5 Key Improvements** (Delivered):

- **Runtime Fixes**:
  - Tier 2 judge provider fallback with automatic API key validation
  - Configurable agent token limits via CLI (`--token-limit`), GUI, and env var
  - PeerRead dataset validation resilience for optional fields (IMPACT, SUBSTANCE)
  - OTLP endpoint double-path bug fix for Phoenix trace export

- **GUI Enhancements**:
  - Background query execution with tab navigation resilience
  - Debug log panel in App tab with real-time capture
  - Evaluation Results and Agent Graph tabs wired to live data
  - Editable settings page with session-scoped persistence

- **Architecture Improvements**:
  - Single-agent composite score weight redistribution (adaptive scoring)
  - PeerRead tools moved from manager to researcher agent (separation of concerns)
  - Tier 3 tool accuracy accumulation bug fixes
  - Dead code removal (duplicate AppEnv class, commented agentops code)

- **Code Quality**:
  - OWASP MAESTRO 7-layer security review (Model, Agent Logic, Integration, Monitoring, Execution, Environment, Orchestration)
  - Test suite refactoring to remove implementation-detail tests (595 → 564 tests, no behavioral coverage loss)
  - Debug logging for empty API keys in provider resolution

### Previous Implementation (Sprint 4 Complete)

The three-tiered evaluation framework is fully operational with plugin architecture:

**✅ Tier 1 - Traditional Metrics** (`src/app/judge/plugins/traditional.py`):

- Cosine similarity using TF-IDF vectorization
- Jaccard similarity with enhanced textdistance support
- Semantic similarity using TF-IDF cosine
- Execution time measurement and normalization
- Task success assessment with configurable thresholds

**✅ Tier 2 - LLM-as-a-Judge** (`src/app/judge/plugins/llm_judge.py`):

- Quality assessment using configurable judge provider (default: auto-inherits chat provider)
- Planning rationality evaluation
- Technical accuracy scoring
- Cost-budgeted evaluation with retry mechanisms
- **Provider Fallback Chain** (Sprint 5): Automatically selects available LLM provider by validating API key availability before attempting calls
  - Primary provider validation → Fallback provider if primary unavailable → Skip Tier 2 entirely if both unavailable
  - `tier2_provider=auto` mode inherits the agent system's active `chat_provider` for consistency
  - When Tier 2 is skipped, its 3 metrics (`technical_accuracy`, `constructiveness`, `planning_rationality`) are excluded from composite scoring and weights redistributed to Tier 1 and Tier 3
  - Prevents 401 authentication errors and neutral 0.5 fallback scores when providers are unavailable

**✅ Tier 3 - Graph Analysis (PRIMARY)** (`src/app/judge/plugins/graph_metrics.py`):

- NetworkX-based behavioral pattern analysis **from execution traces**
- Agent coordination quality measurement
- Tool usage effectiveness evaluation
- Performance bottleneck detection
- **Primary differentiator** - all other tiers validate this

**✅ Composite Scoring** (`src/app/judge/composite_scorer.py`):

- Six-metric weighted formula implementation
- Recommendation mapping (accept/weak_accept/weak_reject/reject)
- Configuration-driven weights from `JudgeSettings`

**✅ Evaluation Pipeline** (`src/app/judge/agent.py`):

- End-to-end evaluation orchestration
- Performance monitoring and error handling
- Fallback strategies and timeout management

### Plugin Architecture (Sprint 3 - Delivered)

**Design Principles**: See [best-practices/mas-design-principles.md](best-practices/mas-design-principles.md) for 12-Factor Agents, Anthropic Harnesses, and PydanticAI integration patterns.

**Security Framework**: See [best-practices/mas-security.md](best-practices/mas-security.md) for OWASP MAESTRO 7-layer security model.

#### EvaluatorPlugin Interface

All evaluation engines (Traditional, LLM-Judge, Graph) implement the typed `EvaluatorPlugin` abstract base class:

```python
class EvaluatorPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def tier(self) -> int: ...

    @abstractmethod
    def evaluate(self, context: BaseModel) -> BaseModel: ...

    @abstractmethod
    def get_context_for_next_tier(self, result: BaseModel) -> BaseModel: ...
```

#### PluginRegistry

Central registry for plugin discovery and tier-ordered execution. Plugins register at import time and are executed in tier order (1 → 2 → 3) with typed context passing between tiers.

#### JudgeSettings Configuration

Replaces `EvaluationConfig` JSON with `pydantic-settings` BaseSettings class using `JUDGE_` environment variable prefix:

```python
class JudgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JUDGE_")

    tier1_timeout: int = 30
    tier2_timeout: int = 60
    tier3_timeout: int = 45
    tier_weights: dict[int, float] = {1: 0.33, 2: 0.33, 3: 0.34}
    # ... other settings
```

JSON fallback available during migration period via `json_file` parameter.

#### Typed Context Passing

All inter-plugin data uses Pydantic models (no raw dicts). Each plugin's `get_context_for_next_tier()` method returns typed context consumed by the next tier's `evaluate()` method.

### Development Timeline

- **Sprint 1**: Three-tiered evaluation framework -- Delivered
- **Sprint 2**: Eval wiring, trace capture, Logfire+Phoenix, Streamlit dashboard -- Delivered
- **Sprint 3**: Plugin architecture, GUI wiring, test alignment, optional weave, trace quality -- Delivered
- **Sprint 4**: Operational resilience, Claude Code baseline comparison (solo + teams) -- Delivered
- **Sprint 5**: Runtime fixes, GUI enhancements, architecture improvements, code quality review -- Delivered
- **Sprint 6**: Benchmarking infrastructure, CC baseline completion, security hardening, test quality -- Delivered
- **Sprint 7**: Documentation, examples, test refactoring, GUI improvements, unified providers, CC engine -- Active

For sprint details, see [roadmap.md](roadmap.md).

### New Metrics for Implementation

Candidate metrics identified from production frameworks and recent research for future evaluation enhancement:

| Metric | Source | Current Gap | Complexity | Impact |
| -------- | -------- | ------------- | ------------ | -------- |
| `path_convergence` | Arize Phoenix | No path efficiency | Low | Medium |
| `handoff_quality` | Arize Multi-Agent | No inter-agent transition | Medium | High |
| `fix_rate` | SWE-EVO [2512.18470] | Binary task success only | Low | High |
| `rubric_alignment` | [2512.23707] | No self-grading assessment | Medium | High |
| `evaluator_consensus` | TEAM-PHI (Agents4Science) | Single LLM judge | Low | High |
| `coordination_topology` | Evolutionary Boids (Agents4Science) | No breadth vs depth | Low | Medium |
| `delegation_depth` | HDO (Agents4Science) | No hierarchy verification | Low | High |

**Integration Priority**: `fix_rate` → `evaluator_consensus` (Tier 2 robustness) → `delegation_depth` (Tier 3 coordination) → `coordination_topology` (Tier 3 pattern detection) → `path_convergence` (Tier 3 efficiency) → `rubric_alignment` (Tier 2 self-assessment)

## Key Dependencies

The system relies on several key technology categories for implementation and evaluation.

**Core Technologies**: See [Agent Frameworks](landscape-agent-frameworks-infrastructure.md#1-agent-frameworks) for PydanticAI agent orchestration details, [Graph Analysis & Network Tools](landscape-evaluation-data-resources.md#6-graph-analysis--network-tools) for NetworkX complexity analysis capabilities, and [Large Language Models](landscape-agent-frameworks-infrastructure.md#2-large-language-models) for LLM integration approaches.

**Evaluation Tools**: See [Traditional Metrics Libraries](landscape-evaluation-data-resources.md#7-traditional-metrics-libraries) for NLTK and Rouge-Score implementation details and feasibility assessments.

**Development Infrastructure**: See [Development Infrastructure](landscape-agent-frameworks-infrastructure.md#development-infrastructure) for uv, Streamlit, Ruff, and pyright integration approaches and alternatives.

## Agents

### Manager Agent

- **Description**: Oversees research and analysis tasks, coordinating the efforts of the research, analysis, and synthesizer agents to provide comprehensive answers to user queries. Delegates tasks and ensures the accuracy of the information.
- **Responsibilities**:
  - Coordinates the research, analysis, and synthesis agents.
  - Delegates research tasks to the Research Agent.
  - Delegates analysis tasks to the Analyst Agent.
  - Delegates synthesis tasks to the Synthesizer Agent.
  - Ensures the accuracy of the information.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Researcher Agent

- **Description**: Gathers and analyzes data relevant to a given topic, utilizing search tools to collect data and verifying the accuracy of assumptions, facts, and conclusions.
- **Responsibilities**:
  - Gathers and analyzes data relevant to the topic.
  - Uses search tools to collect data.
  - Checks the accuracy of assumptions, facts, and conclusions.
- **Tools**:
  - [DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool)
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Analyst Agent

- **Description**: Checks the accuracy of assumptions, facts, and conclusions in the provided data, providing relevant feedback and ensuring data integrity.
- **Responsibilities**:
  - Checks the accuracy of assumptions, facts, and conclusions.
  - Provides relevant feedback if the result is not approved.
  - Ensures data integrity.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Synthesizer Agent

- **Description**: Outputs a well-formatted scientific report using the data provided, maintaining the original facts, conclusions, and sources.
- **Responsibilities**:
  - Outputs a well-formatted scientific report using the provided data.
  - Maintains the original facts, conclusions, and sources.
- **Location**: [src/app/agents/agent_system.py](https://github.com/qte77/Agents-eval/blob/main/src/app/agents/agent_system.py)

### Critic Agent (Proposed - Unscheduled)

- **Description**: Dedicated skeptical reviewer that participates in all agent interactions to reduce hallucinations and compounding errors. Based on Stanford Virtual Lab research showing critic agents significantly improve output quality.
- **Responsibilities**:
  - Challenge assumptions in Researcher outputs
  - Question methodology in Analyst assessments
  - Flag potential hallucinations in Synthesizer reports
  - Provide conservative feedback to reduce errors
  - Participate in both group coordination and individual agent assessments
- **Location**: Planned for `src/app/agents/critic_agent.py` or extension of `agent_system.py`
- **Research Basis**: Stanford's Virtual Lab demonstrated that dedicated critic agents reduce compounding errors in multi-agent systems

## Research-Validated Evaluation Enhancements (Planned)

Based on Stanford's Agents4Science conference (300+ AI-generated papers analyzed):

### Priority 1: Citation Hallucination Detection

- **Metric**: `reference_accuracy_score`
- **Finding**: 56% of AI-generated papers contained ≥1 hallucinated reference
- **Implementation**: Automated web search verification of cited sources
- **Location**: Planned for `src/app/judge/citation_validator.py`

### Priority 2: Reviewer Calibration

- **Metric**: `reviewer_calibration_score`, `reviewer_consistency_score`
- **Finding**: Claude most balanced (closest to human experts), GPT most conservative, Gemini most sycophantic
- **Implementation**: Tune LLM-as-Judge using PeerRead accepted/rejected baseline
- **Location**: Enhancement to `src/app/judge/plugins/llm_judge.py`

### Priority 3: Social Dynamics Tracking

- **Metrics**: `agent_dominance_score`, `coordination_balance`
- **Finding**: Agent speaking order affects outcome quality
- **Implementation**: Extract from execution traces - agent invocation order, message frequency/length
- **Location**: Enhancement to `src/app/judge/plugins/graph_metrics.py`

## Tools Available

Other pydantic-ai agents and [pydantic-ai DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool).

## Decision Log

This section documents architectural decisions made during system development to provide context, rationale, and alternatives considered.

### Decision Format

Each architectural decision includes:

- **Date**: When the decision was made
- **Decision**: What was decided
- **Context**: Why this decision was needed
- **Alternatives**: What other options were considered
- **Rationale**: Why this option was chosen
- **Status**: Active/Superseded/Deprecated

### Architectural Decisions Records

#### ADR-001: PydanticAI as Agent Framework

- **Date**: 2025-03-01
- **Decision**: Use PydanticAI for multi-agent orchestration
- **Context**: Need type-safe, production-ready agent framework
- **Alternatives**: LangChain, AutoGen, CrewAI, custom implementation
- **Rationale**: Type safety, async support, Pydantic validation, lightweight architecture
- **Status**: Active

#### ADR-002: PeerRead Dataset Integration

- **Date**: 2025-08-01
- **Decision**: Use PeerRead scientific paper review dataset as primary evaluation benchmark
- **Context**: Need standardized, academic-quality evaluation dataset
- **Alternatives**: Custom dataset, multiple datasets, synthetic data
- **Rationale**: Established academic benchmark, complex reasoning tasks, real-world data quality
- **Status**: Active

#### ADR-003: Three-Tiered Evaluation Framework

- **Date**: 2025-08-23
- **Decision**: Implement Traditional Metrics → LLM-as-a-Judge → Graph Analysis evaluation pipeline
- **Context**: Need comprehensive agent evaluation beyond simple metrics
- **Alternatives**: Single-tier evaluation, two-tier approach, external evaluation only
- **Rationale**: Provides complementary evaluation dimensions (quantitative, qualitative, behavioral) while maintaining modularity
- **Status**: Active

#### ADR-004: Post-Execution Graph Analysis

- **Date**: 2025-08-25
- **Decision**: Analyze agent behavior through post-execution trace processing rather than real-time monitoring
- **Context**: Need to evaluate coordination patterns without affecting agent performance
- **Alternatives**: Real-time graph construction, embedded monitoring, manual analysis
- **Rationale**: Avoids performance overhead, enables comprehensive analysis, preserves agent autonomy
- **Status**: Active

#### ADR-005: Plugin-Based Evaluation Architecture

- **Date**: 2026-02-09
- **Decision**: Wrap existing evaluation engines in `EvaluatorPlugin` interface with `PluginRegistry` for tier-ordered execution
- **Context**: Need extensibility without modifying core pipeline code; enable new metrics without breaking existing functionality
- **Alternatives**: Direct engine refactoring, new parallel pipeline, microservices architecture
- **Rationale**: Pure adapter pattern preserves existing engines; 12-Factor #4/#10/#12 (backing services, dev/prod parity, stateless processes); MAESTRO Agent Logic Layer typed interfaces
- **Status**: Active

#### ADR-006: pydantic-settings Migration

- **Date**: 2026-02-09
- **Decision**: Replace JSON config files with `BaseSettings` classes (`JudgeSettings`, `CommonSettings`) using environment variables
- **Context**: Need 12-Factor #3 (config in env) compliance; eliminate JSON parsing overhead; enable per-environment configuration
- **Alternatives**: Keep JSON, YAML config, TOML config, mixed approach
- **Rationale**: Type-safe config with Pydantic validation; environment variable support; JSON fallback during transition; aligns with 12-Factor app principles
- **Status**: Active

#### ADR-007: Optional Container-Based Deployment

- **Date**: 2026-02-09
- **Decision**: Support both local (default) and containerized (optional) deployment modes for MAS orchestrator and judge components
- **Context**: Future need for distributed evaluation, parallel judge execution, production isolation, and scalable infrastructure; current single-machine execution sufficient but architecture should enable growth
- **Alternatives**:
  - Local-only - simple but doesn't scale
  - Container-only - production-ready but development friction
  - Hybrid (chosen) - local default, containers optional
  - Microservices - over-engineered for current scale
- **Rationale**:
  - Local execution remains default (zero friction for development)
  - Containers optional (opt-in for production/CI/CD scenarios)
  - API-first communication (FastAPI Feature 10 enables inter-container communication)
  - Stateless judge design (plugin architecture naturally supports containerization)
  - 12-Factor #6 compliance (execute as stateless processes)
  - Parallel evaluation via multiple judge replicas per tier
- **Implementation**:
  - Phase 1: Document pattern only, no implementation
  - Phase 2: Docker images, compose files, deployment docs
  - Prerequisite: FastAPI API stability
- **Status**: Proposed (deferred, unscheduled)

#### ADR-008: CC Baseline Engine — subprocess vs SDK

- **Date**: 2026-02-17
- **Decision**: Keep `subprocess.run([claude, "-p"])` for Sprint 7 STORY-013; evaluate SDK migration for Sprint 8
- **Context**: `--engine=cc` invokes Claude Code headless to compare CC's agentic approach against PydanticAI MAS. Three implementation options exist.
- **Alternatives**:
  - `subprocess.run([claude, "-p"])` (Sprint 7) — full CC tool use, external CLI dependency, correct agentic semantics
  - `anthropic` SDK (`messages.create`) — pure Python, no CLI, but **no tool use** — reduces CC to a raw LLM call, not a valid agentic baseline
  - `claude-agent-sdk` — wraps CLI in Python package, full CC tools, bundles CLI (~100MB), proprietary license
- **Rationale**:
  - The CC baseline measures **orchestration approach** (CC agents vs PydanticAI agents), not model quality
  - CC solo used 19 tool calls (Task, Bash, Glob, Grep, Read) — removing tools changes what's being measured
  - `subprocess.run` is the simplest correct approach (KISS); `shutil.which("claude")` provides fail-fast validation
  - `anthropic` SDK is valid as a **separate** `--engine=claude-api` mode for model-vs-model comparison, not as a CC replacement
  - `claude-agent-sdk` is a valid Sprint 8 refinement if subprocess proves brittle
- **Status**: Active (subprocess); SDK migration deferred pending research

## Agentic System Architecture

**PlantUML Source**: [arch_vis/MAS-C4-Overview.plantuml](arch_vis/MAS-C4-Overview.plantuml) | [arch_vis/MAS-C4-Detailed.plantuml](arch_vis/MAS-C4-Detailed.plantuml)

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show MAS Overview</summary>
  <img src="../assets/images/MAS-C4-Overview-dark.png#gh-dark-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
  <img src="../assets/images/MAS-C4-Overview-light.png#gh-light-mode-only" alt="MAS Architecture Overview" title="MAS Architecture Overview" width="80%" />
</details>
<details>
  <summary>Show MAS Detailed</summary>
  <img src="../assets/images/MAS-C4-Detailed-dark.png#gh-dark-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
  <img src="../assets/images/MAS-C4-Detailed-light.png#gh-light-mode-only" alt="MAS Architecture Detailed" title="MAS Architecture Detailed" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

## Review Workflow

**PlantUML Source**: [arch_vis/MAS-Review-Workflow.plantuml](arch_vis/MAS-Review-Workflow.plantuml)

<!-- markdownlint-disable MD033 -->
<details>
  <summary>Show Review Workflow</summary>
  <img src="../assets/images/MAS-Review-Workflow-dark.png#gh-light-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
  <img src="../assets/images/MAS-Review-Workflow-light.png#gh-dark-mode-only" alt="Review Workflow" title="Review Workflow" width="80%" />
</details>
<!-- markdownlint-enable MD033 -->

## Diagram Generation

All architecture diagrams are generated from PlantUML source files in the `arch_vis/` directory. For rendering instructions and PlantUML setup, see [arch_vis/README.md](arch_vis/README.md).
