<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Evaluation Framework Architecture

**Document Version**: 1.0  
**Sprint**: 1 - Three-Tiered PeerRead Evaluation System  
**Date**: 2025-08-25  
**Status**: Implementation Ready

## Executive Summary

This document specifies the complete architecture for a streamlined three-tiered evaluation framework that assesses multi-agent systems on PeerRead scientific paper review generation with minimal complexity and maximum efficiency.

**Performance Targets**: <1s (Tier 1), 5-10s (Tier 2), 5-15s (Tier 3)  
**Dependencies**: <50MB additional packages, actively maintained libraries only  
**Implementation**: Progressive Days 1-4 deployment strategy

## Architecture Overview

### Three-Tier Progressive Implementation

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tier 1        │    │   Tier 2        │    │   Tier 3        │
│  Traditional    │───→│  LLM-as-Judge   │───→│  Graph-Based    │
│  Metrics        │    │  Assessment     │    │  Analysis       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     Days 1-2              Days 2-3              Days 3-4
     <1s eval             5-10s eval            5-15s eval
```

### Core Components

**Evaluation Engine**: `src/app/evals/evaluation_engine.py`
**Configuration**: `src/app/config/config_eval.json`
**Data Models**: `src/app/data_models/evaluation_models.py`
**Metrics**: `src/app/evals/metrics.py`

## Tier 1: Traditional Metrics Engine

### Architecture Specification

**Module**: `TraditionalMetricsEngine`  
**Location**: `src/app/evals/traditional_metrics.py`  
**Dependencies**: torchmetrics[text], scikit-learn, nltk, textdistance  
**Performance**: <1s evaluation, <50MB dependencies

### Core Metrics Implementation

#### Text Similarity Metrics

```python
class TextSimilarityMetrics:
    def cosine_similarity(self, agent_output: str, reference: str) -> float:
        # Uses scikit-learn TfidfVectorizer + cosine_similarity
        # Formula: dot(A,B) / (||A|| * ||B||)
        
    def jaccard_similarity(self, agent_output: str, reference: str) -> float:
        # Uses textdistance.jaccard
        # Formula: |A ∩ B| / |A ∪ B|
        
    def semantic_similarity(self, agent_output: str, reference: str) -> float:
        # Uses torchmetrics BERTScore (distilbert-base-uncased)
        # Formula: cosine(BERT_embed(A), BERT_embed(B))
```

#### Execution Metrics

```python
class ExecutionMetrics:
    def time_taken(self, start_time: float, end_time: float) -> float:
        # Simple duration calculation
        # Formula: end_time - start_time
        
    def task_success(self, agent_output: str, confidence_threshold: float = 0.8) -> float:
        # Binary success with confidence scoring
        # Formula: 1.0 if similarity > threshold else 0.0
```

### Implementation Requirements

**Input Format**:

- Agent output: Generated review text
- Reference: PeerRead ground truth reviews
- Metadata: Paper ID, timestamp, model configuration

**Output Format**:

```python
class Tier1Result(BaseModel):
    paper_id: str
    cosine_score: float
    jaccard_score: float 
    semantic_score: float
    execution_time: float
    task_success: float
    overall_score: float  # Weighted average
```

**Configuration Integration**:

- Use `config_eval.json` similarity_metrics array
- Apply confidence_threshold for task success
- Weight metrics per metrics_and_weights configuration

## Tier 2: LLM-as-Judge Engine

### Architecture Specification

**Module**: `LLMJudgeEngine`  
**Location**: `src/app/evals/llm_judge.py`  
**Dependencies**: Existing PydanticAI providers (OpenAI, Anthropic)  
**Performance**: 5-10s evaluation, minimal API costs

### Assessment Categories

#### Review Quality Assessment

```python
class ReviewQualityJudge:
    def assess_technical_accuracy(self, paper: str, review: str) -> float:
        # Prompt: "Rate technical accuracy of review claims (1-5)"
        # Evaluation criteria: Factual correctness, methodology understanding
        
    def assess_constructiveness(self, paper: str, review: str) -> float:
        # Prompt: "Rate constructiveness of feedback (1-5)" 
        # Evaluation criteria: Actionable suggestions, improvement guidance
        
    def assess_clarity(self, review: str) -> float:
        # Prompt: "Rate clarity and coherence of review (1-5)"
        # Evaluation criteria: Structure, readability, logical flow
```

#### Agentic Execution Assessment

```python
class AgenticExecutionJudge:
    def assess_reasoning_quality(self, trace_data: dict) -> float:
        # Evaluation: Decision-making process, logical coherence
        
    def assess_tool_usage_effectiveness(self, tool_calls: list) -> float:
        # Evaluation: Appropriate tool selection, efficient usage patterns
        
    def assess_coordination_patterns(self, agent_interactions: list) -> float:
        # Evaluation: Manager→Researcher→Analyst→Synthesizer workflow
```

### Prompt Templates

**Minimal Complexity Design**: Single-shot evaluation prompts with structured output

```yaml
review_quality_template: |
  Evaluate this academic review on a scale of 1-5:
  
  Paper: {paper_content}
  Review: {review_content}
  
  Rate each aspect (1-5):
  - Technical Accuracy: How factually correct are the claims?
  - Constructiveness: How helpful is the feedback for improvement?
  - Clarity: How well-structured and readable is the review?
  
  Output JSON format: {"technical": X, "constructive": X, "clarity": X}
```

### Implementation Requirements

**Integration**: Use existing PydanticAI model configurations
**Error Handling**: Fallback to Tier 1 metrics on API failures
**Cost Optimization**: Batch processing, model selection based on paper complexity

## Tier 3: Graph-Based Analysis Engine

### Architecture Specification

**Module**: `GraphAnalysisEngine`  
**Location**: `src/app/evals/graph_analysis.py`  
**Dependencies**: NetworkX (graph construction and analysis)  
**Performance**: 5-15s analysis, lightweight implementation

### Core Analysis Components

#### Tool Call Complexity Analysis

```python
class ToolCallAnalyzer:
    def build_tool_graph(self, execution_trace: dict) -> nx.DiGraph:
        # Creates directed graph of tool call sequences
        # Nodes: Tool calls, Edges: Dependencies/sequences
        
    def calculate_complexity_metrics(self, graph: nx.DiGraph) -> dict:
        # Metrics: Path length, branching factor, cycle detection
        # Formula: complexity = avg_path_length * branching_factor
```

#### Agent Interaction Graph

```python
class AgentInteractionAnalyzer:
    def build_interaction_graph(self, agent_traces: list) -> nx.DiGraph:
        # Nodes: Agents (Manager, Researcher, Analyst, Synthesizer)
        # Edges: Communication patterns, data flow
        
    def measure_coordination_quality(self, graph: nx.DiGraph) -> float:
        # Centrality measures: betweenness, closeness, degree
        # Formula: coordination_quality = (1 - communication_overhead) * efficiency
```

### Essential Metrics Only

**Tool Efficiency**:

- Path convergence ratio: `minimum_steps / actual_steps`
- Tool selection accuracy: `correct_tools / total_tools`
- Execution flow efficiency: Graph diameter and clustering coefficient

**Coordination Quality**:

- Communication overhead: `coordination_msgs / productive_msgs`
- Agent utilization balance: `1 - std_dev(agent_tasks) / mean(agent_tasks)`
- Information flow centrality: NetworkX centrality measures

### Trace Data Integration

**Input Sources**:

- AgentNeo decorator traces (@agentneo.trace)
- PydanticAI execution logs
- Tool call metadata from agent system

**Data Format**:

```python
class GraphTraceData(BaseModel):
    execution_id: str
    agent_interactions: list[dict]  # Agent-to-agent communications
    tool_calls: list[dict]         # Tool usage sequence
    timing_data: dict              # Execution timestamps
    coordination_events: list[dict] # Manager delegation patterns
```

## Composite Scoring System

### Weighted Formula Implementation

**Configuration-Based Weights** (from config_eval.json):

```python
def calculate_composite_score(metrics: dict) -> float:
    weights = {
        "time_taken": 0.167,
        "task_success": 0.167, 
        "coordination_quality": 0.167,
        "tool_efficiency": 0.167,
        "planning_rational": 0.167,
        "output_similarity": 0.167
    }
    
    return sum(metrics[key] * weights[key] for key in weights.keys())
```

### Score Normalization

**Standardization**: All metrics normalized to 0-1 scale
**Recommendation Mapping**:

- Accept (1.0), Weak Accept (0.7), Weak Reject (-0.7), Reject (-1.0)
- Threshold: 0.8 for task success evaluation

## Local Observability Integration

### Trace Collection Strategy

**AgentNeo Integration**:

```python
@agentneo.trace_agent()
def manager_agent_execution():
    # Automatic trace collection for Tier 3 analysis
    
@agentneo.trace_tool() 
def tool_call_wrapper():
    # Tool usage pattern collection
```

**Data Storage**:

- SQLite databases for structured queries
- JSON log files for trace analysis
- `./logs/traces/` directory with timestamped execution traces

### Comet Opik Integration

**Local Deployment**: Docker-based Opik instance for trace analysis
**Custom Metrics**: BaseMetric implementations for PeerRead-specific evaluation
**Export Capabilities**: JSONL format for offline graph construction

## Implementation Handoff Specifications

### Phase 1: Traditional Metrics (Days 1-2)

**Required Implementations**:

1. `TraditionalMetricsEngine` class with similarity metrics
2. `ExecutionMetrics` class with timing and success measurement  
3. Configuration integration with `config_eval.json`
4. Unit tests with BDD approach

**Dependencies**: Install torchmetrics[text], scikit-learn, nltk, textdistance

### Phase 2: LLM Judge Integration (Days 2-3)

**Required Implementations**:

1. `LLMJudgeEngine` class with quality assessment
2. Prompt template system for structured evaluation
3. Integration with existing PydanticAI providers
4. Error handling and fallback mechanisms

**API Integration**: Use existing model configurations, implement cost optimization

### Phase 3: Graph Analysis (Days 3-4)

**Required Implementations**:

1. `GraphAnalysisEngine` class with NetworkX integration
2. Trace data processing pipeline
3. Coordination quality metrics calculation
4. AgentNeo decorator integration

**Performance Optimization**: Efficient graph construction, minimal memory usage

### Phase 4: Integration & Testing (Days 4-6)

**Required Implementations**:

1. `EvaluationOrchestrator` class coordinating all tiers
2. Composite scoring with weighted formulas
3. End-to-end testing with PeerRead samples
4. Performance benchmarking and optimization

## Validation Requirements

**Performance Benchmarks**:

- Tier 1: <1s evaluation time with <50MB dependencies
- Tier 2: 5-10s evaluation with minimal API costs  
- Tier 3: 5-15s analysis with efficient memory usage

**Quality Assurance**:

- >90% test coverage for all evaluation components
- BDD testing approach with realistic PeerRead scenarios
- Error handling for malformed inputs and API failures

**Integration Testing**:

- End-to-end pipeline with actual PeerRead papers
- Score interpretability validation
- Robust error handling verification

This architecture provides focused, streamlined implementation guidance for developers with exact specifications, minimal complexity, and clear performance targets for the three-tiered PeerRead evaluation system.
