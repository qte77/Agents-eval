<!-- markdownlint-disable MD024 no-duplicate-heading -->
# Sprint 1: PeerRead Dataset Agent Evaluation Framework

## Sprint Dates: August 23-28, 2025 (6 Days)

**Sprint Goal**: Implement a comprehensive three-tiered evaluation framework (Traditional + LLM-as-Judge + Graph-based) with research-backed enhancements for assessing multi-agent systems on PeerRead scientific paper review generation, establishing a solid foundation for advanced architectural development.

**Priority**: Critical Priority for evaluation framework foundation and Sprint 2 architectural prerequisites

## Executive Summary

**Project Goal**: Assess and evaluate AI agents on the PeerRead dataset by implementing a comprehensive evaluation framework that measures agent performance in generating academic paper reviews through multiple evaluation approaches.

**Key Requirements**:

- Large context window models to ingest full PeerRead dataset papers
- Traditional evaluation metrics (text similarity, execution time)
- LLM-as-a-judge evaluation for review quality and agentic execution assessment
- Graph-based complexity analysis of tool and agent interactions
- Composite scoring system: (agentic results / execution time / graph complexity)

**Sprint Goals**: Implement comprehensive PeerRead evaluation framework with traditional, LLM-judge, and graph-based evaluation approaches to enable agent performance scoring. See [Evaluation Approach Decision Tree](../architecture.md#evaluation-approach-decision-tree) for guidance on approach selection.

## Three-Tiered Evaluation Engine Strategy

The Sprint 1 implementation follows a progressive three-tier approach, allowing selection of appropriate evaluation depth based on requirements and constraints.

### **Tier 1: Traditional Metrics Engine**

**Status**: Well-defined foundation (Tasks 1.3, 1.4)  
**Scope**: Fast, deterministic text similarity and performance metrics  
**Tools**: NLTK, Rouge-Score, BERTScore (see [Traditional Metrics Libraries](../landscape.md#traditional-metrics-libraries))  
**Sprint Priority**: High - Foundation for all evaluation approaches  
**Implementation**: Days 1-2 with HuggingFace evaluate + sklearn integration  
**Performance Target**: <1s evaluation time, minimal computational overhead

### **Tier 2: LLM-as-a-Judge Engine**

**Status**: ⚠️ Medium complexity implementation (Tasks 2.1, 2.2)  
**Scope**: Semantic understanding, quality assessment, reasoning evaluation  
**Tools**: DeepEval, Langchain OpenEvals (see [LLM Evaluation & Benchmarking](../landscape.md#llm-evaluation--benchmarking))  
**Sprint Priority**: High - Core semantic evaluation capability  
**Implementation**: Days 2-3 with LLM provider coordination and prompt engineering  
**Performance Target**: 5-15s evaluation time, moderate API costs

### **Tier 3: Graph-Based Analysis Engine**

**Status**: Excellently architected post-execution analysis (Tasks 3.1-3.3)  
**Scope**: Behavioral pattern analysis, coordination effectiveness, emergent complexity  
**Tools**: NetworkX + PyTorch Geometric + NetworKit (see [Graph Analysis & Network Tools](../landscape.md#graph-analysis--network-tools))  
**Sprint Priority**: High - Advanced multi-agent coordination analysis  
**Implementation**: Days 3-4 with execution trace processing and graph neural networks  
**Performance Target**: 10-30s analysis time, computationally intensive but offline

### **Progressive Implementation Strategy for Sprint 1**

**Days 1-2 (Foundation)**: Tier 1 → Fast validation and baseline metrics with local observability infrastructure  
**Days 2-3 (Intelligence)**: Tier 1+2 → Add semantic understanding and quality assessment  
**Days 3-4 (Advanced Analysis)**: All Tiers → Complete behavioral and coordination analysis  
**Days 4-6 (Integration & Production)**: Selective Tiers → Optimized pipeline with composite scoring

### **Local Observability Infrastructure (Critical for Tier 3)**

**Implementation Requirements** (Tasks 1.4, 2.3):

- **AgentNeo Integration**: Local JSON/JSONL tracing with comprehensive agent execution logging
- **Comet Opik Integration**: Local storage capabilities for trace analysis and behavioral pattern extraction  
- **Trace File Structure**: `./logs/traces/` directory with timestamped execution traces for offline graph construction
- **Real-time Monitoring**: Agent coordination patterns, tool usage effectiveness, and delegation sequences
- **Post-execution Analysis**: Graph construction from execution traces for Tier 3 behavioral analysis

## Evaluation Framework Overview

### Traditional Evaluation Metrics (from config_eval.json)

- **Output Similarity**: Compare generated reviews to PeerRead reference reviews using HuggingFace evaluate library and sklearn for cosine, jaccard, and semantic similarity  
- **Time Taken**: Measure agent processing time for paper ingestion and review generation
- **Task Success**: Assess successful completion of review generation task with confidence threshold (0.8)

### Advanced Evaluation Metrics (from config_eval.json)

- **Coordination Quality**: Assess multi-agent interactions and workflow efficiency between Manager/Researcher/Analyst/Synthesizer
- **Tool Efficiency**: Evaluate effectiveness of DuckDuckGo search and PeerRead-specific tools usage
- **Planning Rational**: Assess reasoning quality and decision-making processes in agent orchestration

### Enhanced Evaluation Methodologies

**Arize Phoenix Cyclical Development Approach**:

- **Path Convergence Metrics**: Measure agent step efficiency and iteration optimization
- **Granular Skill Evaluation**: Router selection accuracy, tool calling precision, parameter extraction validation
- **LLM-as-a-Judge Templates**: Agent planning validation, reflection assessment, convergence scoring

**Swarms Continuous Evaluation Framework**:

- **Comprehensive Performance Tracking**: Accuracy, precision, recall, F1 score, response time, task completion rate, error rate
- **Dynamic Assessment Criteria**: Baseline establishment with regular comparative evaluations
- **User Feedback Integration**: Continuous improvement loops with realistic scenario testing

### Graph-Based Complexity Analysis

See [Graph Analysis & Network Tools in landscape.md](../landscape.md#graph-analysis--network-tools) for comprehensive tool recommendations.

- **Tool Call Complexity**: Analyze patterns and efficiency of tool utilizations using NetworkX for graph construction and PyTorch Geometric for advanced pattern recognition
- **Agent Interaction Graphs**: Map and measure complexity of agent-to-agent communications using NetworkX centrality measures and igraph for performance-critical computations
- **Execution Flow Analysis**: Compare actual vs. expected execution patterns with graph visualization using Graphviz and interactive dashboards via Plotly

### Composite Scoring Formula (from config_eval.json)

```python
# Equal weights for all 6 metrics (0.167 each)
Agent Score = (
    time_taken * 0.167 +
    task_success * 0.167 + 
    coordination_quality * 0.167 +
    tool_efficiency * 0.167 +
    planning_rational * 0.167 +
    output_similarity * 0.167
)
```

**Recommendation Weights**: Accept (1.0), Weak Accept (0.7), Weak Reject (-0.7), Reject (-1.0)  
**Confidence Threshold**: 0.8 for task success evaluation

### Model Requirements

- **Large Context Windows**: Models capable of processing full PeerRead papers (>50k tokens, preferably 200k+ for full papers)
- **Suggested Models** (see [Available Models](../landscape.md#available-models) for detailed comparisons):
  - **Claude 4 Opus/Sonnet** (1M context limit, Anthropic provider)
  - **GPT-4 Turbo** (128k context limit, OpenAI provider)  
  - **Gemini-1.5-Pro** (1M context limit, Google provider)
- **Fallback Strategy**: Intelligent document chunking for smaller context models
- **Implementation**: Model selection logic based on paper token count with automatic fallback

### Implementation Architecture Details

#### Config-Based Evaluation Implementation

```python
# Extends existing src/app/evals/metrics.py (time_taken, output_similarity already exist)
class ConfigBasedEvaluator:
    def __init__(self, config_path: str = "src/app/config/config_eval.json"):
        self.config = load_config(config_path)
        self.weights = self.config["metrics_and_weights"]  # All 6 metrics with 0.167 weights
        self.similarity_metrics = self.config["evaluation"]["similarity_metrics"]  # cosine, jaccard, semantic
        
    def calculate_output_similarity(self, generated: str, reference: str) -> float:
        """Calculate similarity using HuggingFace and sklearn metrics."""
        # Use HuggingFace evaluate library for standard metrics
        # Use sklearn for cosine similarity, jaccard coefficient
        return self._multi_similarity_hf_sklearn(generated, reference, self.similarity_metrics)
    
    def time_taken(self, start_time: float, end_time: float) -> float:
        """Existing implementation - execution time tracking."""
        return end_time - start_time
    
    def evaluate_task_success(self, generated_review: str, confidence: float) -> float:
        """Task completion assessment with confidence threshold (0.8)."""
        return 1.0 if confidence >= self.config["evaluation"]["confidence_threshold"] else 0.0
```

#### Advanced Metrics Implementation

```python
# src/app/evals/advanced_metrics.py - New metrics from config_eval.json
class AdvancedEvaluator:
    def evaluate_coordination_quality(self, agent_interactions: List[Dict]) -> float:
        """Assess Manager->Researcher->Analyst->Synthesizer coordination efficiency."""
        coordination_score = self._analyze_delegation_patterns(agent_interactions)
        return min(1.0, max(0.0, coordination_score))
    
    def evaluate_tool_efficiency(self, tool_calls: List[Dict]) -> float:
        """Assess DuckDuckGo search and PeerRead tools usage effectiveness."""
        efficiency_metrics = self._analyze_tool_usage(tool_calls)
        return efficiency_metrics["success_rate"] * efficiency_metrics["response_time_factor"]
    
    def evaluate_planning_rational(self, decision_trace: List[Dict]) -> float:
        """Assess reasoning quality in agent decision-making processes."""
        rationality_score = self._analyze_decision_quality(decision_trace)
        return rationality_score
```

#### Graph-Based Complexity Analysis

**Tools**: See [Graph Analysis & Network Tools in landscape.md](../landscape.md#graph-analysis--network-tools) for detailed tool selection rationale and integration approaches.

```python
# src/app/evals/graph_complexity.py
# Primary tools: NetworkX (graph construction), PyTorch Geometric (GNN analysis), igraph (performance)
class GraphComplexityEvaluator:
    def build_execution_graph(self, execution_trace: List[Dict]) -> nx.DiGraph:
        """Convert execution trace to directed graph representation using NetworkX."""
        graph = nx.DiGraph()
        for step in execution_trace:
            self._add_execution_step(graph, step)
        return graph
    
    def calculate_complexity_metrics(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate graph complexity measures using NetworkX algorithms."""
        return {
            "node_count": graph.number_of_nodes(),
            "edge_density": nx.density(graph),
            "cyclic_complexity": self._calculate_cyclomatic_complexity(graph),
            "average_path_length": nx.average_shortest_path_length(graph),
            "betweenness_centrality": max(nx.betweenness_centrality(graph).values())
        }
    
    def apply_gnn_analysis(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Advanced pattern recognition using PyTorch Geometric GNN models."""
        # Convert NetworkX to PyG Data format for GNN processing
        # Apply graph attention networks for communication pattern analysis
        # Return advanced coordination and efficiency predictions
        pass
```

#### Composite Scoring System

```python
# src/app/evals/composite_scorer.py - Using config_eval.json structure  
class CompositeScorer:
    def __init__(self, config_path: str = "src/app/config/config_eval.json"):
        self.config = load_config(config_path)
        self.weights = self.config["metrics_and_weights"]  # All 0.167 equal weights
        self.recommendation_weights = self.config["evaluation"]["recommendation_weights"]
    
    def calculate_agent_score(self, metrics_results: Dict[str, float]) -> Dict[str, Any]:
        """Calculate final score using config_eval.json weighted approach."""
        
        # Apply config weights to all 6 metrics
        weighted_score = (
            metrics_results["time_taken"] * self.weights["time_taken"] +
            metrics_results["task_success"] * self.weights["task_success"] + 
            metrics_results["coordination_quality"] * self.weights["coordination_quality"] +
            metrics_results["tool_efficiency"] * self.weights["tool_efficiency"] +
            metrics_results["planning_rational"] * self.weights["planning_rational"] +
            metrics_results["output_similarity"] * self.weights["output_similarity"]
        )
        
        # Apply recommendation weights based on performance
        if weighted_score >= 0.8: recommendation = "accept"
        elif weighted_score >= 0.6: recommendation = "weak_accept" 
        elif weighted_score >= 0.4: recommendation = "weak_reject"
        else: recommendation = "reject"
        
        final_score = weighted_score * self.recommendation_weights[recommendation]
        
        return {
            "final_score": final_score,
            "weighted_score": weighted_score,
            "recommendation": recommendation,
            "individual_metrics": metrics_results
        }
```

---

## Core Sprint Tasks

### Immediate Implementation Priorities

### Core Tasks (Must Complete in Sprint 1)

**These tasks are essential for the evaluation framework and will be resolved in Sprint 1:**

- [ ] **Three-Tiered Evaluation System**: Implement comprehensive evaluation framework with traditional metrics, LLM-as-a-judge, and graph-based complexity analysis
- [ ] **Local Observability Infrastructure**: Implement local JSON/JSONL tracing with evaluation of Comet, Opik, Helicone, and Logfire for local storage capabilities. See [Technical Analysis: Tracing Methods](../trace_observe_methods.md) for detailed technical mechanisms of observability tools and their tracing implementations.
- [ ] **Technical Analysis Investigation**: Complete investigation into actual source code implementations of tracing and observation mechanisms within each observability tool's codebase for deeper technical understanding and integration planning.
- [ ] **PDF Ingestion Capability**: Implement agents processing of parsed PDFs from PeerRead dataset with large context models
- [ ] **Prompt Configuration Audit**: Complete externalization of all prompts to config files, eliminate hardcoded prompts
- [ ] **Error Message Strategy**: Implement unified error handling patterns across all evaluation components
- [ ] **Security & Quality Review**: Complete comprehensive codebase audit for issues, redundancies, inconsistencies

---

## Day-by-Day Sprint Plan

### **Day 1 (Aug 23): PeerRead Integration & Large Context Models**

- [ ] **Task 1.1**: PeerRead Dataset Integration Assessment
  - Evaluate PDF parsing capabilities for PeerRead papers
  - Test agent ingestion of full papers with large context models
  - **Deliverable**: PDF processing capability assessment

- [ ] **Task 1.2**: Large Context Model Configuration
  - Configure Claude 4 Opus/Sonnet, GPT-4 Turbo for extended context (see [Available Models](../landscape.md#available-models))
  - Test full paper ingestion (>50k tokens) capability
  - **Deliverable**: Large context model pipeline ready

- [ ] **Task 1.3**: Traditional Evaluation Metrics Implementation
  - Implement text similarity metrics using HuggingFace evaluate library and sklearn
  - Add execution time measurement infrastructure
  - **Deliverable**: Traditional evaluation metrics operational

- [ ] **Task 1.4**: Core Implementation Tasks (Must Complete)
  - **PDF Ingestion**: Implement PeerRead PDF processing with large context models
  - **Prompt Configuration**: Complete audit and externalization of all hardcoded prompts
  - **Error Message Strategy**: Begin unified error handling implementation
  - **Security Review**: Start comprehensive codebase security and quality audit
  - **Deliverable**: PDF processing operational, prompts externalized, error handling framework, security audit findings

**Day 1 DoD**: PeerRead integration ready, large context models configured, traditional metrics implemented

---

### **Day 2 (Aug 24): LLM-as-a-Judge Implementation**

- [ ] **Task 2.1**: LLM-as-a-Judge Framework Development
  - Implement judge system for review quality assessment
  - Create agentic execution assessment judges
  - **Deliverable**: LLM judge framework operational

- [ ] **Task 2.2**: Agent Coordination Assessment
  - Develop judges for multi-agent interaction quality
  - Implement tool usage efficiency assessment
  - **Deliverable**: Agent coordination evaluation system

- [ ] **Task 2.3**: Core Implementation Tasks
  - **Security & Quality Review**: Complete comprehensive audit findings and resolution plan
  - **Error Message Strategy**: Finalize unified error handling across evaluation components
  - **Configuration Validation**: Ensure all prompts are properly externalized and functional
  - **Deliverable**: Security audit complete, error handling unified, configuration validated

**Day 2 DoD**: LLM-as-a-judge system operational, security audit complete

---

### **Day 3 (Aug 25): Graph-Based Complexity Analysis**

- [ ] **Task 3.1**: Graph-Based Evaluation Architecture
  - Design tool call complexity measurement system using NetworkX graph construction
  - Create agent interaction graph mapping infrastructure with PyTorch Geometric for advanced analysis
  - **Deliverable**: Graph analysis architecture leveraging landscape.md recommended tools

- [ ] **Task 3.2**: Tool Call Pattern Analysis
  - Implement tool usage pattern recognition using NetworkX centrality measures
  - Create efficiency metrics for tool interactions with igraph for performance-critical computations
  - **Deliverable**: Tool call complexity analyzer with visualization via Graphviz

- [ ] **Task 3.3**: Agent Interaction Graph Generation
  - Map agent-to-agent communication patterns using NetworkX directed graphs
  - Measure interaction complexity and efficiency with interactive dashboards via Plotly
  - **Deliverable**: Agent interaction complexity metrics with real-time visualization capabilities

- [ ] **Task 3.4**: External Tool Assessment (Phase 2)
  - Evaluate AdalFlow for agent workflow optimization
  - Assess agentfile format for agent definitions
  - **Deliverable**: Additional tool integration recommendations

**Day 3 DoD**: Graph-based complexity analysis system operational, comprehensive external tool assessment complete

---

### **Day 4 (Aug 26): Composite Scoring & Integration**

- [ ] **Task 4.1**: Composite Scoring System Implementation
  - Implement scoring formula: (Agentic Results / Execution Time / Graph Complexity)
  - Create score normalization and weighting system
  - **Deliverable**: Functional composite scoring system

- [ ] **Task 4.2**: Full Evaluation Pipeline Integration
  - Connect traditional, LLM-judge, and graph-based evaluations
  - End-to-end testing with PeerRead dataset samples
  - **Deliverable**: Complete integrated evaluation pipeline

- [ ] **Task 4.3**: Testing and Validation
  - Implement comprehensive unit tests for all evaluation components
  - Create integration tests for pipeline components
  - **Deliverable**: Complete test coverage for evaluation system

- [ ] **Task 4.4**: Performance Optimization
  - Optimize large context model processing
  - Improve evaluation pipeline efficiency
  - **Deliverable**: Optimized evaluation system performance

**Day 4 DoD**: Complete PeerRead evaluation system with composite scoring operational

---

### **Day 5 (Aug 27): PeerRead Validation & Testing**

- [ ] **Task 5.1**: Comprehensive PeerRead Dataset Testing
  - Test full pipeline with actual PeerRead papers and reviews
  - Validate all three evaluation approaches with real data
  - **Deliverable**: Validated evaluation system with real dataset

- [ ] **Task 5.2**: Scoring System Validation
  - Test composite scoring formula with varied performance scenarios
  - Validate score interpretability and ranking accuracy
  - **Deliverable**: Validated and calibrated scoring system

- [ ] **Task 5.3**: Error Handling & Edge Case Testing
  - Complete error message strategy implementation
  - Test edge cases with malformed papers, missing reviews
  - **Deliverable**: Robust error handling system

- [ ] **Task 5.4**: Documentation & Usage Guide
  - Create PeerRead evaluation workflow documentation
  - Document scoring interpretation and benchmarking
  - **Deliverable**: Complete user documentation

**Day 5 DoD**: Production-ready PeerRead evaluation system with comprehensive validation and documentation

---

### **Day 6 (Aug 28): Final Integration & Sprint Analysis**

- [ ] **Task 6.1**: Final System Integration Testing
  - Complete end-to-end testing with full PeerRead workflow
  - Performance benchmarking and optimization
  - **Deliverable**: Production-ready evaluation system

- [ ] **Task 6.2**: Sprint Retrospective & Analysis
  - Analyze implementation effectiveness against goals
  - Document lessons learned and optimization opportunities
  - **Deliverable**: Comprehensive sprint analysis report

- [ ] **Task 6.3**: Future Sprint Planning
  - Identify next priorities based on current implementation
  - Plan enhancements for evaluation framework expansion
  - **Deliverable**: Next sprint roadmap and priorities

- [ ] **Task 6.4**: Final Validation & Handoff
  - Complete system validation checklist
  - Prepare handoff documentation for production use
  - **Deliverable**: Production-ready system with handoff materials

**Day 6 DoD**: Complete PeerRead evaluation system ready for production use with comprehensive analysis and future roadmap

---

## Success Metrics

### Core PeerRead Evaluation Framework

- [ ] PDF ingestion capability for full PeerRead papers operational
- [ ] Large context window models (>50k tokens) configured and tested
- [ ] Traditional evaluation metrics implemented
- [ ] LLM-as-a-judge framework operational
- [ ] Graph-based complexity analysis system functional
- [ ] Composite scoring system: (Agentic Results / Execution Time / Graph Complexity) implemented

### Technical Implementation

- [ ] All prompts externalized to configuration files (none hardcoded)
- [ ] Error message strategy fully implemented and separated  
- [ ] Security and quality issues identified and prioritized for resolution
- [ ] Local observability infrastructure for trace analysis functional

### Performance & Quality

- [ ] <5s evaluation pipeline latency for standard PeerRead paper processing
- [ ] >90% test coverage for evaluation modules
- [ ] End-to-end validation with real PeerRead dataset samples
- [ ] Robust error handling for edge cases and malformed inputs

### System Integration

- [ ] Complete evaluation pipeline integration operational
- [ ] Score interpretability and ranking validation completed
- [ ] Production-ready system with comprehensive documentation
- [ ] Future sprint roadmap established based on implementation learnings

## Pre-Sprint Checklist

- [ ] **Environment Ready**: `make setup_dev && make validate` passes
- [ ] **Large Context Model Access**: GPT-4 Turbo, Claude-3 Opus, or Gemini Pro 1.5 API keys configured
- [ ] **PeerRead Dataset Access**: Dataset available for PDF processing tests
- [ ] **Baseline Tests**: Current test suite runs successfully
- [ ] **Configuration Audit Ready**: Identify all hardcoded prompts for externalization
- [ ] **Security Review Tools**: Static analysis and security scanning tools available

## Definition of Done (Sprint)

- [ ] **PeerRead Integration**: Agents can ingest and process full PeerRead papers via large context models
- [ ] **Traditional Evaluation**: Text similarity and execution time metrics operational
- [ ] **LLM-as-a-Judge**: Review quality and agentic execution assessment functional
- [ ] **Graph-Based Analysis**: Tool call and agent interaction complexity measurement system operational
- [ ] **Composite Scoring**: Complete scoring formula implemented and validated
- [ ] **Technical Requirements**: All prompts externalized, error messages separated, security issues identified
- [ ] **Production Ready**: >90% test coverage, <5s latency, comprehensive documentation, robust error handling

---

**Note**: Advanced features, external tool assessments, and research enhancements have been moved to [Sprint 3: Advanced Features & Research Integration](2025-08_Sprint3_Advanced-Features.md).
