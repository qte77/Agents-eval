# Task 1.2 Handoff: Backend Architect → Evaluation Specialist

## Task Context

- **Task**: Design complete evaluation framework architecture following Backend Architect → Evaluation Specialist handoff process
- **Objective**: Create streamlined three-tiered evaluation framework with composite scoring system per sprint requirements
- **Dependencies**: Sprint document analysis completed, existing codebase assessment completed

## Deliverables for Next Agent

- [x] Complete three-tiered architecture specification
- [x] Mathematical formulas and scoring algorithms  
- [x] Integration patterns with existing codebase
- [x] Performance targets and dependency requirements
- [x] Implementation handoff documentation for developers
- [x] Configuration integration with config_eval.json

## Implementation Requirements

### Architecture Overview

The evaluation framework implements a streamlined three-tiered progressive architecture:

**Tier 1: Traditional Metrics Engine** - Fast lightweight text similarity and performance metrics
**Tier 2: LLM-as-Judge Engine** - Quality assessment using existing PydanticAI infrastructure  
**Tier 3: Graph-Based Analysis Engine** - NetworkX-based agent coordination and tool usage analysis
**Composite Scoring System** - Weighted formula integrating all three tiers

### Detailed Architecture Specifications

#### 1. Tier 1: Traditional Metrics Engine

**Performance Target**: <1s evaluation, <50MB dependencies
**Location**: `src/app/evals/traditional_metrics.py` (existing, requires enhancement)

**Mathematical Formulas**:

```python
# Cosine Similarity
cosine_similarity = dot_product(vector_a, vector_b) / (norm(vector_a) * norm(vector_b))

# Jaccard Similarity  
jaccard_similarity = |intersection(set_a, set_b)| / |union(set_a, set_b)|

# Semantic Similarity (BERTScore fallback)
semantic_similarity = bert_f1_score(reference, candidate)

# Composite Tier 1 Score
tier1_score = (semantic * 0.4 + cosine * 0.3 + jaccard * 0.2 + time_penalty * 0.1)
```

**Dependency Strategy** (Lightweight-first):

- **Primary**: ROUGE-Score (~10MB), NLTK BLEU (~20MB), scikit-learn (~50MB), textdistance (~5MB)
- **Fallback**: HuggingFace Evaluate for BERTScore when lightweight metrics insufficient
- **Total Primary Stack**: <100MB as per sprint requirement

**Implementation Requirements**:

1. Enhance existing TraditionalMetricsEngine class
2. Add ROUGE-Score and NLTK BLEU integration
3. Implement textdistance for Jaccard similarity
4. Add execution time tracking with sub-second precision
5. Implement task success evaluation with confidence threshold (0.8)

#### 2. Tier 2: LLM-as-Judge Engine

**Performance Target**: 5-10s evaluation, minimal API costs (<$0.05 per evaluation)
**Location**: `src/app/evals/llm_judge.py` (existing, requires enhancement)

**Assessment Components**:

```python
# Technical Accuracy Assessment
technical_accuracy = llm_judge_score(paper_excerpt, review, "technical_accuracy_prompt")

# Constructiveness Assessment  
constructiveness = llm_judge_score(review, "constructiveness_prompt")

# Planning Rationality Assessment
planning_rationality = llm_judge_score(agent_trace, "planning_rationality_prompt")

# Composite Tier 2 Score
tier2_score = (technical_accuracy * 0.4 + constructiveness * 0.3 + planning_rationality * 0.3)
```

**Cost Optimization Strategy**:

- Use gpt-4o-mini as default model (cost-efficient)
- Limit paper excerpts to 2000 characters
- Implement retry logic with exponential backoff
- Graceful fallback to traditional metrics on failure

**Implementation Requirements**:

1. Enhance existing LLMJudgeEngine class
2. Add structured prompt templates for three assessment types
3. Implement cost tracking and budget enforcement
4. Add timeout handling (30s max per assessment)
5. Integrate with existing PydanticAI infrastructure

#### 3. Tier 3: Graph-Based Analysis Engine

**Performance Target**: 5-15s analysis, efficient memory usage
**Location**: `src/app/evals/graph_analysis.py` (existing, requires enhancement)

**Graph Construction Algorithms**:

```python
# Agent Interaction Graph
G_agents = nx.DiGraph()
for interaction in agent_traces:
    G_agents.add_edge(interaction.from_agent, interaction.to_agent, 
                      weight=interaction.frequency)

# Tool Usage Graph  
G_tools = nx.DiGraph()
for tool_call in tool_traces:
    G_tools.add_edge(tool_call.agent, tool_call.tool, 
                     weight=tool_call.efficiency_score)

# Coordination Quality Metrics
coordination_quality = (
    nx.average_clustering(G_agents) * 0.3 +
    (1.0 / nx.average_shortest_path_length(G_agents)) * 0.25 +
    nx.density(G_agents) * 0.25 +
    task_balance_metric(G_agents) * 0.2
)
```

**NetworkX-based Analysis Metrics**:

- **Path Convergence**: Measures efficient information flow
- **Tool Accuracy**: Analyzes tool usage effectiveness  
- **Coordination Quality**: Evaluates agent interaction patterns
- **Task Balance**: Assesses workload distribution

**Implementation Requirements**:

1. Enhance existing GraphAnalysisEngine class
2. Implement agent interaction graph construction from traces
3. Add tool usage pattern analysis with NetworkX centrality measures
4. Create visualization capabilities using NetworkX native functions (nx.draw())
5. Integrate with AgentNeo trace processing pipeline

#### 4. Composite Scoring System

**Mathematical Formula** (From config_eval.json):

```python
# Six-metric weighted composite score (equal weights: 0.167 each)
composite_score = (
    time_taken * 0.167 +        # Execution efficiency
    task_success * 0.167 +      # Completion accuracy
    coordination_quality * 0.167 + # Agent interaction effectiveness  
    tool_efficiency * 0.167 +   # Tool usage optimization
    planning_rational * 0.167 + # Decision-making quality
    output_similarity * 0.167   # Similarity to ground truth
)

# Recommendation Mapping
if composite_score >= 0.8: recommendation = "Accept" (weight: 1.0)
elif composite_score >= 0.6: recommendation = "Weak Accept" (weight: 0.7) 
elif composite_score >= 0.4: recommendation = "Weak Reject" (weight: -0.7)
else: recommendation = "Reject" (weight: -1.0)
```

**Implementation Requirements**:

1. Create new CompositeScorer class in `src/app/evals/composite_scorer.py`
2. Implement weighted scoring formula from config_eval.json
3. Add recommendation threshold mapping
4. Create score interpretation and trend analysis
5. Integrate with all three evaluation tiers

#### 5. Local Observability Infrastructure

**Integration Strategy**:

- **AgentNeo**: JSON/JSONL tracing for agent execution logging
- **Trace Storage**: `./logs/traces/` directory with timestamped files
- **Post-execution Analysis**: Graph construction from execution traces

**Implementation Requirements**:

1. Enhance existing trace processing in `src/app/evals/trace_processors.py`
2. Integrate AgentNeo tracing with agent execution pipeline
3. Implement trace file parsing for graph construction
4. Add real-time trace collection during agent execution
5. Create trace-to-graph conversion pipeline

### Performance Targets and Dependencies

#### Performance Requirements

- **Tier 1**: <1s evaluation time, <50MB base dependencies
- **Tier 2**: 5-10s evaluation time, <$0.05 API cost per evaluation
- **Tier 3**: 5-15s analysis time, memory-efficient graph processing
- **Total Pipeline**: <25s end-to-end evaluation

#### Dependency Management

- **Lightweight Primary Stack**: ROUGE-Score, NLTK BLEU, scikit-learn, textdistance
- **Heavy Fallbacks**: HuggingFace Evaluate (BERTScore) only when needed
- **Graph Analysis**: NetworkX (primary), igraph (optional performance fallback)
- **Observability**: AgentNeo for local tracing

### Integration with Existing Codebase

#### Configuration Integration

- All parameters configurable via `src/app/config/config_eval.json`
- Weights, thresholds, and model selections externalized
- Progressive deployment strategy: Tier 1 → Tier 1+2 → All Tiers

#### Data Model Integration

- Use existing Pydantic models in `src/app/data_models/evaluation_models.py`
- Tier1Result, Tier2Result, Tier3Result for structured output
- GraphTraceData for trace processing integration

#### Agent Factory Integration

- Leverage existing `src/app/agents/agent_factories.py`
- Use create_evaluation_agent for LLM judge instantiation
- Maintain consistency with Manager/Researcher/Analyst/Synthesizer patterns

## Validation Criteria

The receiving agent should validate:

1. **Architecture Completeness**: All three tiers fully specified with mathematical formulas
2. **Performance Feasibility**: All performance targets achievable with specified dependencies
3. **Configuration Alignment**: All specifications match config_eval.json structure
4. **Integration Consistency**: All components integrate with existing codebase patterns
5. **Implementation Clarity**: All specifications provide sufficient detail for developer handoff

## Files/Locations

**Architecture Documents**:

- `/workspaces/Agents-eval/docs/sprints/handoffs/task-1.2-backend_architect-to-evaluation_specialist.md` (this file)

**Implementation Targets**:

- `src/app/evals/traditional_metrics.py` (enhance existing)
- `src/app/evals/llm_judge.py` (enhance existing)  
- `src/app/evals/graph_analysis.py` (enhance existing)
- `src/app/evals/composite_scorer.py` (create new)
- `src/app/evals/trace_processors.py` (enhance existing)

**Configuration Files**:

- `src/app/config/config_eval.json` (existing configuration)

**Data Models**:

- `src/app/data_models/evaluation_models.py` (existing Pydantic models)

This architecture specification provides complete implementation requirements for the evaluation specialist to design detailed framework components while maintaining strict separation of architectural design from code implementation.
