# Planning and Solution

## Three-Tier Evaluation Architecture

The developed solution is based on a three-tier evaluation architecture that combines complementary assessment methods to enable comprehensive evaluation of multi-agent systems. Each tier addresses a different dimension of agentic performance and mutually validates the findings of the other tiers.

### Tier 1: Traditional Metrics

The first evaluation tier implements classical, objective text similarity metrics as a quantitative baseline. This tier fulfills the role of a fast validator and delivers deterministically reproducible measurements without dependency on external language models.

**Output Similarity Scoring** (`output_similarity`): To determine the similarity between the system-generated review and the human reference review from the PeerRead dataset, three similarity measures are employed:

- Cosine similarity via TF-IDF vectorization (primary metric)
- Jaccard similarity with `textdistance` support (secondary metric)
- Semantic similarity on TF-IDF basis (default metric from configuration)

**Execution Time** (`time_taken`): The end-to-end processing duration of a scientific paper is measured and normalized. Additionally, resource utilization, API calls, and token consumption are captured.

**Task Success** (`task_success`): The completeness and structural correctness of the generated review is evaluated. Academic standard conformity and configurable recommendation weights are factored into the assessment.

The implementation resides in `src/app/judge/plugins/traditional.py`.

### Tier 2: LLM-as-Judge

The second tier employs a language model as evaluator to capture qualitative and semantic aspects not accessible to traditional metrics. A configured judge provider evaluates the agentic execution based on structured criteria.

**Planning Rationality** (`planning_rationality`): The decision logic of the agent system, the coherence of the reasoning chain, and the strategic effectiveness of planning are evaluated.

**Tool Efficiency** (`tool_efficiency`): The effectiveness of tool usage, resource optimization, and API call efficiency are analyzed.

**Recommendation Quality**: Generated reviews are compared against ground-truth reviews from PeerRead. Configurable recommendation weights control the evaluation: `accept` (1.0), `weak_accept` (0.7), `weak_reject` (-0.7), `reject` (-1.0) [@architecture2025].

A provider fallback mechanism (introduced in Sprint 5) validates API key availability before invocation. If no provider is available, Tier 2 is skipped entirely and the weights are redistributed to the remaining metrics.

The implementation resides in `src/app/judge/plugins/llm_judge.py`.

### Tier 3: Graph-Based Behavioral Analysis

The third evaluation tier represents the primary innovation of the framework. Rather than directly observing agentic behavior, execution traces are analyzed post-hoc and transformed into behavioral graphs.

**Coordination Quality** (`coordination_quality`): Agent interaction patterns are extracted from execution traces using NetworkX graph analysis. Centrality metrics quantify the communication efficiency between Manager, Researcher, Analyst, and Synthesizer agents.

**Execution Graph Construction**: Logfire auto-instrumentation captures comprehensive execution traces. NetworkX constructs behavioral graphs from these, mapping coordination patterns, tool usage sequences, and decision flows.

**Complexity Metrics Integration**: Node count (discrete actions), edge density (interaction frequency), and path optimization are incorporated into the overarching metrics.

The approach of post-hoc graph analysis (ADR-004) avoids performance overhead during agent execution and preserves agent autonomy in tool selection. The implementation resides in `src/app/judge/plugins/graph_metrics.py`.

### Integrated Pipeline

The three tiers operate as an integrated pipeline where results and context are passed sequentially:

| Tier | Role | Focus |
|------|------|-------|
| Tier 1 (Traditional) | VALIDATOR | Fast, objective text similarity baseline |
| Tier 2 (LLM-Judge) | VALIDATOR | Semantic quality assessment |
| Tier 3 (Graph) | PRIMARY | Coordination patterns from execution traces |

The validation logic follows a clear principle: if all three tiers agree, there is high confidence in the assessment quality. If Tier 3 is positive but Tiers 1 and 2 are negative, this indicates good coordination with weak output quality. The reverse case signals high-quality output with inefficient coordination.

## Four-Agent Architecture

### Agent Roles and Specialization

The system implements a specialized four-agent architecture that models collaborative research scenarios and provides realistic evaluation complexity.

**Manager Agent**: Primary orchestrator responsible for task delegation, coordination oversight, quality assurance, and system-wide decision-making. The Manager Agent serves as the central coordination point and ensures coherent system operation across all agent interactions. Large context window models are preferentially employed.

**Researcher Agent**: Specialized in information gathering with DuckDuckGo search integration for data collection, literature research, and fact verification [@pydantic_ai_tools]. This agent provides the external information acquisition capability required for comprehensive analysis. PeerRead dataset tools are assigned to this agent (separation of concerns, Sprint 5).

**Analyst Agent**: Focused on critical evaluation, data validation, and accuracy verification of research findings. The Analyst Agent provides the analytical capabilities for rigorous scientific assessment and returns detailed feedback when findings are not approved.

**Synthesizer Agent**: Generates coherent, well-structured reports that integrate insights from all agents. This agent transforms collaborative analysis into structured, scientifically formulated outputs while maintaining the original facts, conclusions, and sources.

All four agents are implemented in `src/app/agents/agent_system.py`.

### Coordination Protocols

**Hierarchical Delegation Structure**: The Manager Agent serves as the primary decision-maker for task allocation and coordination oversight. Specialized agents operate with defined autonomy within their domains.

**Data Flow**: PeerRead paper input $\rightarrow$ Manager Agent $\rightarrow$ optional delegation to Researcher Agent (with DuckDuckGo search) $\rightarrow$ optional results to Analyst Agent for validation $\rightarrow$ validated data to Synthesizer Agent $\rightarrow$ generated review $\rightarrow$ evaluation pipeline.

**Error Handling**: Robust mechanisms for agent failure and graceful degradation are implemented. The system maintains operational capability even during individual component failures.

**Agent Composition Modes**: The `SweepRunner` module (Sprint 6) enables systematic evaluation of eight different agent compositions, from single-agent configurations to full four-agent collaboration.

## Metrics Framework

### Six-Dimensional Assessment Architecture

The evaluation framework implements six equally weighted assessment dimensions that prevent optimization bias while ensuring comprehensive capability assessment.

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/metrics-eval-sweep-light.png}
\caption{Six-dimensional evaluation architecture with sweep analysis}
\end{figure}

The six metrics each comprise 16.7 percent of the total score:

- **`planning_rationality`** (16.7%): Assessment of decision logic, reasoning coherence, and strategic planning effectiveness
- **`task_success`** (16.7%): Quantification of review completeness, structural correctness, and academic standard conformity
- **`tool_efficiency`** (16.7%): Analysis of tool usage effectiveness, resource optimization, and API call efficiency
- **`coordination_quality`** (16.7%): Measurement of inter-agent communication effectiveness via graph centrality metrics
- **`time_taken`** (16.7%): Performance efficiency measurement and normalized execution time
- **`output_similarity`** (16.7%): Semantic alignment with PeerRead ground-truth reviews

The implementation resides in `src/app/judge/composite_scorer.py`.

### Composite Scoring

The composite score calculation follows the formula:

```
Agent Score = Weighted sum of six core metrics
```

Configuration-based thresholds classify the result into three categories:

- **accept**: Composite Score $\geq$ 0.863
- **weak_accept**: Composite Score $\geq$ 0.626
- **reject**: Composite Score < 0.626

All metric weights are configured via `JudgeSettings` through pydantic-settings and support override via environment variables with the prefix `JUDGE_`.

### Adaptive Weight Redistribution

The composite scoring system automatically detects whether a single-agent run is present by checking `GraphTraceData` for 0--1 unique agent IDs and empty `coordination_events`.

In single-agent mode, the `coordination_quality` metric (weight 0.167) is excluded and its weight is evenly distributed among the remaining five metrics (0.20 each). The `CompositeResult` object contains a `single_agent_mode: bool` flag that transparently documents the redistribution.

When Tier 2 absence (no valid provider) and single-agent mode are combined, all weights are redistributed to the available metrics so that the sum always equals ~1.0:

```python
# Reason: Compound redistribution ensures weights always sum to ~1.0
if single_agent_mode and tier2_skipped:
    available_metrics = [m for m in all_metrics
                         if m not in excluded_metrics]
    weight_per_metric = 1.0 / len(available_metrics)
```

*Code excerpt from `src/app/judge/composite_scorer.py`*

## PeerRead Dataset Integration

The PeerRead dataset serves as the primary evaluation benchmark scenario. It comprises over 14,000 scientific papers with structured peer reviews, acceptance and rejection decisions, and detailed metadata from leading conferences including NIPS, ICLR, and ACL [@peerread2018].

**Ground-Truth Validation**: PeerRead reviews serve as references for `output_similarity` and LLM-Judge evaluation. This enables objective performance measurement and validation of agentic system capabilities.

**Pydantic Data Models**: The dataset integration uses `validation_alias` and `ConfigDict(populate_by_name=True)` to map external field names (e.g., `IMPACT` $\rightarrow$ `impact`) to internal model attributes. The models reside in `src/app/data_models/peerread_models.py`.

**Resilient Validation**: Optional PeerRead fields (IMPACT, SUBSTANCE) are handled tolerantly. Missing values do not abort the evaluation pipeline but are replaced with configurable default values.

**Download and Caching**: The downloader in `src/app/data_utils/datasets_peerread.py` supports venue-specific splits (e.g., `iclr_2017`, `acl_2017`) and stores data in a configurable cache directory for offline use.

**Benchmarking Sweep**: The `SweepRunner` (Sprint 6) enables systematic evaluation of multiple agent compositions over N papers and M repetitions. Statistical analysis (`SweepAnalyzer`) computes mean, standard deviation, minimum, and maximum per composition.

## Plugin Architecture

### EvaluatorPlugin Interface

All evaluation modules (Traditional, LLM-Judge, Graph) implement a common abstract base class that ensures type-safe and extensible plugin integration (ADR-005):

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

*Code excerpt from `src/app/judge/plugins/`*

The interface follows the Adapter pattern: existing evaluation engines are embedded without modification of the core pipeline code. New metrics can be added without interrupting existing functionality (12-Factor Principles #4, #10, #12).

Inter-plugin data passing occurs exclusively through typed Pydantic models (no raw dictionaries). Each plugin returns a typed context via `get_context_for_next_tier()` that is consumed by the subsequent tier.

### PluginRegistry and Tier Execution

The `PluginRegistry` serves as the central management instance for plugin discovery and tier-ordered execution. Plugins register themselves at import time and are executed in the order Tier 1 $\rightarrow$ Tier 2 $\rightarrow$ Tier 3:

```python
class PluginRegistry:
    def register(self, plugin: EvaluatorPlugin) -> None: ...
    def get_plugins_by_tier(self, tier: int) -> list[EvaluatorPlugin]: ...
    def execute_all(self, context: BaseModel) -> list[BaseModel]: ...
```

*Code excerpt from `src/app/judge/`*

**JudgeSettings Configuration** replaces JSON configuration files with a `pydantic-settings` `BaseSettings` class with the environment variable prefix `JUDGE_` (ADR-006). Timeouts, tier weights, and metric parameters are fully configurable:

```python
class JudgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JUDGE_")

    tier1_timeout: int = 30
    tier2_timeout: int = 60
    tier3_timeout: int = 45
    tier_weights: dict[int, float] = {1: 0.33, 2: 0.33, 3: 0.34}
```

*Code excerpt from `src/app/judge/`*

## System Architecture Overview

### C4 Model Overview

The system architecture follows the C4 model [@c4model] and documents the system at different abstraction levels. The following diagram shows the high-level system components and their relationships.

\begin{figure}[!htbp]
\centering
\rotatebox{90}{\oldincludegraphics[width=0.85\textheight,height=0.85\textwidth,keepaspectratio]{../../../../assets/images/MAS-C4-Overview-light.png}}
\caption{C4 model overview of the Agents-eval MAS framework}
\end{figure}

The architectural design emphasizes clear separation between the Multi-Agent System (MAS) responsible for review generation and the evaluation system responsible for assessment and analysis. This separation enables independent evolution of both subsystems while maintaining clean interfaces and data contracts.

The system follows core architectural principles: modular design enables independent development of each major component with clearly defined interfaces. Technology-agnosticism ensures that abstract interfaces enable support for multiple agentic frameworks, LLM providers, and evaluation methodologies without architectural changes.

### Detailed Component Architecture

\begin{figure}[!htbp]
\centering
\rotatebox{90}{\oldincludegraphics[width=0.85\textheight,height=0.85\textwidth,keepaspectratio]{../../../../assets/images/MAS-C4-Detailed-light.png}}
\caption{Detailed C4 component architecture with data flow}
\end{figure}

The detailed architecture reveals the interaction patterns between system components. The main application layer serves as the primary orchestration point: it manages user interactions through CLI and Streamlit GUI interfaces, coordinates agent sessions, and routes evaluation requests to appropriate subsystems.

The Agent System core implements multi-agent coordination logic with the PydanticAI framework [@pydanticai] and manages agent lifecycles, inter-agent communication, and task delegation patterns across the four specialized agents.

### Review Workflow

\begin{figure}[!htbp]
\centering
\rotatebox{90}{\oldincludegraphics[width=0.85\textheight,height=0.85\textwidth,keepaspectratio]{../../../../assets/images/MAS-Review-Workflow-light.png}}
\caption{Multi-agent review workflow with sequential delegation}
\end{figure}

The workflow architecture demonstrates the agent coordination patterns:

**Primary Workflow**: User request $\rightarrow$ Manager Agent (paper retrieval) $\rightarrow$ template-based review generation $\rightarrow$ LLM processing $\rightarrow$ structured review output $\rightarrow$ persistent storage

**Delegation Workflow**: Manager Agent $\rightarrow$ Researcher Agent activation $\rightarrow$ DuckDuckGo search execution $\rightarrow$ research synthesis $\rightarrow$ result integration into main workflow

**Quality Assurance**: Built-in validation at each stage ensures data integrity and consistency across different execution paths.

### Workflow Evolution

The development of the multi-agent evaluation framework proceeded through systematic architectural refinements, documenting the evolution from basic agent coordination to sophisticated collaborative intelligence.

\begin{figure}[!htbp]
\centering
\rotatebox{90}{\oldincludegraphics[width=0.85\textheight,height=0.85\textwidth,keepaspectratio]{../../../../assets/images/mas-workflow-light.png}}
\caption{Original workflow implementation with basic agent coordination}
\end{figure}

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/mas-enhanced-workflow-light.png}
\caption{Enhanced workflow with feedback loops and observability integration}
\end{figure}

The workflow evolution demonstrates improvements in agent coordination, error handling, and performance optimization. The original implementation offered basic agent delegation and task coordination, while the enhanced version incorporates feedback loops, dynamic task allocation, and observability integration.

## ADR Summary

A summary of all architectural decisions is provided in Appendix A.
