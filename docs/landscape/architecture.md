# Agents-eval Architecture

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

1. **Traditional Metrics**: Text similarity (BLEU, ROUGE, BERTScore), execution time measurement
2. **LLM-as-a-Judge**: Review quality assessment, agentic execution analysis
3. **Graph-Based Analysis**: Tool call complexity, agent interaction mapping
4. **Composite Scoring**: Final score calculation using formula: (Agentic Results / Execution Time / Graph Complexity)

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

**Model Selection**: See [Available Models - Large Context Window Models](landscape/landscape.md#available-models) in landscape.md for detailed model comparisons, context limits, and integration approaches for Claude 4 Opus/Sonnet, GPT-4 Turbo, and Gemini-1.5-Pro.

### Sprint 1: PeerRead Evaluation Components

#### Traditional Evaluation Metrics

**Location**: `src/app/evals/traditional_metrics.py`

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

**Location**: `src/app/evals/llm_judge.py`

- **Planning Rational Assessment** (config: `planning_rational`):
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

**Location**: `src/app/evals/graph_complexity.py`

**Approach**: Post-execution behavioral analysis where agents autonomously decide tool use during execution, then observability logs are processed to construct behavioral graphs for retrospective evaluation.

##### Integration Workflow

1. **Agent Execution** → PydanticAI agents (Manager/Researcher/Analyst/Synthesizer) autonomously decide tool use and coordination strategies during PeerRead paper processing
2. **Observability Logging** → AgentNeo and Comet Opik capture comprehensive execution traces, tool usage patterns, and agent interactions in real-time
3. **Graph Construction** → spaCy + NetworkX and Google LangExtract process trace logs to build behavioral graphs showing coordination patterns and decision flows
4. **Analysis** → NetworkX and NetworKit analyze coordination effectiveness, tool usage efficiency, and emergent behavioral patterns from constructed graphs

**Tool Selection**: See [Graph Analysis & Network Tools](landscape/landscape.md#graph-analysis--network-tools), [Post-Execution Graph Construction Tools](landscape/landscape.md#post-execution-graph-construction-tools), [Observability & Monitoring Platforms](landscape/landscape.md#observability--monitoring-platforms), and [Technical Analysis: Tracing Methods](landscape/trace_observe_methods.md) for detailed feasibility assessments and integration approaches.

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
  - Pattern recognition → influences planning_rational assessment via behavioral analysis

#### Composite Scoring System

**Location**: `src/app/evals/composite_scorer.py`

**Formula**: `Agent Score = Weighted Sum of Six Core Metrics`

**Configuration-Based Metrics** (from `config_eval.json`):

- `time_taken`: 0.167 (16.7% - execution time efficiency)
- `task_success`: 0.167 (16.7% - review completion and accuracy)
- `coordination_quality`: 0.167 (16.7% - agent interaction effectiveness)
- `tool_efficiency`: 0.167 (16.7% - tool usage optimization)
- `planning_rational`: 0.167 (16.7% - decision-making quality)
- `output_similarity`: 0.167 (16.7% - similarity to PeerRead ground truth)

**Configuration-Based Output**:

- Final weighted score using six config metrics (0.167 each)
- Individual metric breakdowns: time_taken, task_success, coordination_quality, tool_efficiency, planning_rational, output_similarity
- Similarity metrics selection (cosine, jaccard, semantic) with semantic as default
- Recommendation scoring with config weights and confidence threshold (0.8)
- Performance trend analysis with configurable evaluation parameters

### Sprint 2: Architectural Refactoring (Future)

The evaluation framework will be refactored into three independent engines:

- **Agents Engine**: Pure agent orchestration and execution
- **Dataset Engine**: PeerRead data loading, caching, and validation  
- **Eval Engine**: Evaluation metrics calculation and scoring

## Key Dependencies

The system relies on several key technology categories for implementation and evaluation.

**Core Technologies**: See [Agentic System Frameworks](landscape/landscape.md#agentic-system-frameworks) for PydanticAI agent orchestration details, [Graph Analysis & Network Tools](landscape/landscape.md#graph-analysis--network-tools) for NetworkX complexity analysis capabilities, and [Available Models](landscape/landscape.md#available-models) for LLM integration approaches.

**Evaluation Tools**: See [Traditional Metrics Libraries](landscape/landscape.md#traditional-metrics-libraries) for NLTK, Rouge-Score, and BERTScore implementation details and feasibility assessments.

**Development Infrastructure**: See [Development Infrastructure](landscape/landscape.md#development-infrastructure) for uv, Streamlit, Ruff, and pyright integration approaches and alternatives.

## Agents

### Manager Agent

- **Description**: Oversees research and analysis tasks, coordinating the efforts of the research, analysis, and synthesizer agents to provide comprehensive answers to user queries. Delegates tasks and ensures the accuracy of the information.
- **Responsibilities**:
  - Coordinates the research, analysis, and synthesis agents.
  - Delegates research tasks to the Research Agent.
  - Delegates analysis tasks to the Analysis Agent.
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

## Tools Available

Other pydantic-ai agents and [pydantic-ai DuckDuckGo Search Tool](https://ai.pydantic.dev/common-tools/#duckduckgo-search-tool).

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
