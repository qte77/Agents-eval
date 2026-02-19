---
title: Evaluation Metrics Definitions
description: Exact mathematical formulas, implementation specifications, and developer guidance for all evaluation metrics in the three-tiered PeerRead evaluation framework
date: 2025-08-25
category: evaluation
version: 1.0.0
---

**Document Version**: 1.0  
**Sprint**: 1 - Three-Tiered PeerRead Evaluation System  
**Date**: 2025-08-25  
**Status**: Implementation Ready

## Executive Summary

This document provides exact mathematical formulas, implementation specifications, and developer guidance for all evaluation metrics in the three-tiered PeerRead evaluation framework.

**Target Audience**: Python developers implementing evaluation metrics  
**Implementation Guide**: Complete formulas with library-specific implementations  
**Dependencies**: torchmetrics[text], scikit-learn, nltk, textdistance, NetworkX

## Tier 1: Traditional Metrics - Mathematical Definitions

### Text Similarity Metrics

#### Cosine Similarity

**Formula**:

```text
cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
```

**Implementation**:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_cosine_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity using TF-IDF vectors.
    
    Args:
        text1: Agent-generated review text
        text2: Reference review text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(similarity[0][0])
```

**Range**: [0.0, 1.0] where 1.0 = identical, 0.0 = no similarity  
**Performance**: ~50ms for typical review lengths (500-2000 tokens)

#### Jaccard Similarity

**Formula**:

```text
jaccard_similarity(A, B) = |A ∩ B| / |A ∪ B|
```

**Implementation**:

```python
import textdistance

def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Compute Jaccard similarity using word-level tokens.
    
    Args:
        text1: Agent-generated review text
        text2: Reference review text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Tokenize and convert to sets for intersection/union
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if len(words1) == 0 and len(words2) == 0:
        return 1.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0
```

**Range**: [0.0, 1.0] where 1.0 = identical word sets, 0.0 = no common words  
**Performance**: ~10ms for typical review lengths

#### Semantic Similarity

**Formula**:

```text
semantic_similarity(A, B) = cosine(BERT_embed(A), BERT_embed(B))
```

**Implementation**:

```python
from torchmetrics.text import BERTScore

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity using BERTScore.
    
    Args:
        text1: Agent-generated review text
        text2: Reference review text
        
    Returns:
        F1 score between 0.0 and 1.0
    """
    bertscore = BERTScore(model_name_or_path='distilbert-base-uncased')
    score = bertscore([text1], [text2])
    return float(score['f1'][0])  # Return F1 component
```

**Range**: [0.0, 1.0] where 1.0 = semantically identical, 0.0 = unrelated  
**Performance**: ~200ms for typical review lengths (includes model inference)

### Execution Performance Metrics

#### Time Taken

**Formula**:

```text
execution_time = end_timestamp - start_timestamp
```

**Implementation**:

```python
import time

def measure_execution_time(func):
    """Decorator to measure function execution time.
    
    Returns:
        Duration in seconds with microsecond precision
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper
```

**Units**: Seconds with microsecond precision  
**Normalization**: For composite scoring, normalize using `1 / (1 + log(time_seconds))`

#### Task Success Assessment

**Formula**:

```text
task_success = {
    1.0 if overall_similarity >= confidence_threshold
    0.0 otherwise
}
```

**Implementation**:

```python
def assess_task_success(similarity_scores: dict, threshold: float = 0.8) -> float:
    """Assess task completion success based on similarity threshold.
    
    Args:
        similarity_scores: Dict with cosine, jaccard, semantic scores
        threshold: Minimum similarity for success (default 0.8)
        
    Returns:
        1.0 for success, 0.0 for failure
    """
    # Weighted average of similarity metrics
    weights = {'semantic': 0.5, 'cosine': 0.3, 'jaccard': 0.2}
    
    overall_similarity = sum(
        similarity_scores[metric] * weight 
        for metric, weight in weights.items()
    )
    
    return 1.0 if overall_similarity >= threshold else 0.0
```

**Range**: Binary {0.0, 1.0} based on threshold  
**Configuration**: Uses `confidence_threshold` from config_eval.json

## Tier 2: LLM-as-Judge Metrics - Assessment Criteria

### Review Quality Assessment

#### Technical Accuracy Score

**Assessment Criteria**:

```text
technical_accuracy = LLM_judge(paper, review, criteria)
where criteria = {
    "factual_correctness": "Claims supported by paper content",
    "methodology_understanding": "Proper grasp of experimental approach", 
    "domain_knowledge": "Appropriate use of technical terminology"
}
```

**Implementation**:

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class TechnicalAccuracyResult(BaseModel):
    factual_correctness: float  # 1-5 scale
    methodology_understanding: float  # 1-5 scale  
    domain_knowledge: float  # 1-5 scale
    overall_score: float  # Weighted average

async def assess_technical_accuracy(paper: str, review: str) -> TechnicalAccuracyResult:
    """Assess technical accuracy using LLM judge.
    
    Args:
        paper: Full paper content or relevant sections
        review: Agent-generated review text
        
    Returns:
        Structured assessment with 1-5 scores
    """
    prompt = f"""
    Evaluate technical accuracy of this review (1-5 scale):
    
    Paper: {paper[:2000]}...
    Review: {review}
    
    Rate each aspect:
    1. Factual Correctness: Are claims supported by paper?
    2. Methodology Understanding: Does reviewer grasp approach?
    3. Domain Knowledge: Appropriate technical terminology?
    
    Return scores 1-5 where 5=excellent, 1=poor.
    """
    
    agent = Agent(model_name='gpt-4o-mini')  # Cost-optimized model
    result = await agent.run(prompt, result_type=TechnicalAccuracyResult)
    
    # Calculate weighted overall score
    result.overall_score = (
        result.factual_correctness * 0.5 +
        result.methodology_understanding * 0.3 + 
        result.domain_knowledge * 0.2
    ) / 5.0  # Normalize to 0-1
    
    return result
```

**Range**: [0.0, 1.0] normalized from 1-5 scale  
**Performance**: 5-8s with gpt-4o-mini, ~$0.01 per evaluation

#### Constructiveness Score

**Assessment Criteria**:

```text
constructiveness = LLM_judge(review, criteria)
where criteria = {
    "actionable_feedback": "Specific improvement suggestions",
    "balanced_critique": "Both strengths and weaknesses addressed",
    "improvement_guidance": "Clear next steps for authors"
}
```

**Implementation**:

```python
class ConstructivenessResult(BaseModel):
    actionable_feedback: float  # 1-5 scale
    balanced_critique: float    # 1-5 scale
    improvement_guidance: float # 1-5 scale
    overall_score: float       # Weighted average

async def assess_constructiveness(review: str) -> ConstructivenessResult:
    """Assess constructiveness of review feedback.
    
    Args:
        review: Agent-generated review text
        
    Returns:
        Structured assessment with normalized scores
    """
    prompt = f"""
    Evaluate constructiveness of this academic review (1-5 scale):
    
    Review: {review}
    
    Rate each aspect:
    1. Actionable Feedback: Specific, implementable suggestions?
    2. Balanced Critique: Both strengths and weaknesses noted?
    3. Improvement Guidance: Clear direction for authors?
    
    Return scores 1-5 where 5=excellent, 1=poor.
    """
    
    agent = Agent(model_name='gpt-4o-mini')
    result = await agent.run(prompt, result_type=ConstructivenessResult)
    
    # Equal weighting for constructiveness aspects
    result.overall_score = (
        result.actionable_feedback + 
        result.balanced_critique + 
        result.improvement_guidance
    ) / 15.0  # Normalize to 0-1
    
    return result
```

### Agentic Execution Assessment

#### Planning Rationality

**Assessment Criteria**:

```text
planning_rationality = LLM_judge(execution_trace, criteria)
where criteria = {
    "logical_flow": "Coherent step-by-step progression",
    "decision_quality": "Appropriate choices at decision points",
    "resource_efficiency": "Optimal use of available tools/agents"
}
```

**Implementation**:

```python
class PlanningRationalityResult(BaseModel):
    logical_flow: float        # 1-5 scale
    decision_quality: float    # 1-5 scale 
    resource_efficiency: float # 1-5 scale
    overall_score: float      # Weighted average

async def assess_planning_rationality(execution_trace: dict) -> PlanningRationalityResult:
    """Assess quality of agent planning and decision-making.
    
    Args:
        execution_trace: Dict containing agent execution steps
        
    Returns:
        Structured assessment with normalized scores
    """
    # Extract key planning decisions from trace
    planning_summary = extract_planning_decisions(execution_trace)
    
    prompt = f"""
    Evaluate planning rationality of this agent execution (1-5 scale):
    
    Execution Summary: {planning_summary}
    
    Rate each aspect:
    1. Logical Flow: Coherent step progression?
    2. Decision Quality: Appropriate choices made?  
    3. Resource Efficiency: Optimal tool/agent usage?
    
    Return scores 1-5 where 5=excellent, 1=poor.
    """
    
    agent = Agent(model_name='gpt-4o-mini')
    result = await agent.run(prompt, result_type=PlanningRationalityResult)
    
    # Weight decision quality most heavily
    result.overall_score = (
        result.logical_flow * 0.3 +
        result.decision_quality * 0.5 + 
        result.resource_efficiency * 0.2
    ) / 5.0  # Normalize to 0-1
    
    return result
```

## Tier 3: Graph-Based Metrics - Network Analysis

### Tool Efficiency Metrics

#### Path Convergence Ratio

**Formula**:

```text
path_convergence = minimum_required_steps / actual_steps_taken
```

**Implementation**:

```python
import networkx as nx

def calculate_path_convergence(tool_graph: nx.DiGraph, start_node: str, end_node: str) -> float:
    """Calculate efficiency of tool usage path.
    
    Args:
        tool_graph: NetworkX graph of tool call dependencies
        start_node: Starting tool/state
        end_node: Goal tool/state
        
    Returns:
        Convergence ratio between 0.0 and 1.0
    """
    try:
        # Calculate shortest path (optimal)
        optimal_path = nx.shortest_path(tool_graph, start_node, end_node)
        minimum_steps = len(optimal_path) - 1
        
        # Calculate actual path length from execution trace
        actual_steps = calculate_actual_steps(tool_graph, start_node, end_node)
        
        return minimum_steps / actual_steps if actual_steps > 0 else 0.0
        
    except nx.NetworkXNoPath:
        return 0.0  # No path found
```

**Range**: [0.0, 1.0] where 1.0 = optimal path, 0.0 = no valid path  
**Performance**: ~10ms for typical tool graphs (<50 nodes)

#### Tool Selection Accuracy

**Formula**:

```text
tool_accuracy = correct_tool_selections / total_tool_selections
```

**Implementation**:

```python
def calculate_tool_selection_accuracy(tool_calls: list[dict], optimal_tools: dict) -> float:
    """Calculate accuracy of tool selection decisions.
    
    Args:
        tool_calls: List of actual tool calls with context
        optimal_tools: Dict mapping contexts to optimal tools
        
    Returns:
        Accuracy ratio between 0.0 and 1.0
    """
    if not tool_calls:
        return 0.0
        
    correct_selections = 0
    
    for call in tool_calls:
        context = call.get('context', '')
        selected_tool = call.get('tool_name', '')
        
        # Determine optimal tool for this context
        optimal_tool = determine_optimal_tool(context, optimal_tools)
        
        if selected_tool == optimal_tool:
            correct_selections += 1
    
    return correct_selections / len(tool_calls)
```

### Coordination Quality Metrics

#### Communication Overhead

**Formula**:

```text
communication_overhead = coordination_messages / total_messages
```

**Implementation**:

```python
def calculate_communication_overhead(agent_interactions: list[dict]) -> float:
    """Calculate efficiency of agent communication.
    
    Args:
        agent_interactions: List of agent-to-agent communications
        
    Returns:
        Overhead ratio between 0.0 and 1.0 (lower is better)
    """
    if not agent_interactions:
        return 0.0
    
    coordination_msgs = sum(
        1 for msg in agent_interactions 
        if msg.get('type') in ['coordination', 'status_update', 'handoff']
    )
    
    productive_msgs = sum(
        1 for msg in agent_interactions
        if msg.get('type') in ['task_request', 'result_delivery', 'data_transfer']
    )
    
    total_messages = len(agent_interactions)
    
    return coordination_msgs / total_messages if total_messages > 0 else 0.0
```

#### Agent Centrality Analysis

**Formula**:

```text
coordination_centrality = (betweenness + closeness + degree) / 3
```

**Implementation**:

```python
def calculate_coordination_centrality(interaction_graph: nx.DiGraph) -> dict:
    """Calculate centrality measures for coordination analysis.
    
    Args:
        interaction_graph: NetworkX graph of agent interactions
        
    Returns:
        Dict with centrality scores for each agent
    """
    # Calculate centrality measures
    betweenness = nx.betweenness_centrality(interaction_graph)
    closeness = nx.closeness_centrality(interaction_graph)
    degree = nx.degree_centrality(interaction_graph)
    
    # Combine centrality measures
    centrality_scores = {}
    for node in interaction_graph.nodes():
        combined_centrality = (
            betweenness.get(node, 0.0) +
            closeness.get(node, 0.0) + 
            degree.get(node, 0.0)
        ) / 3.0
        
        centrality_scores[node] = combined_centrality
    
    return centrality_scores
```

**Range**: [0.0, 1.0] where higher values indicate more central coordination role

#### Task Distribution Balance

**Formula**:

```text
balance_score = 1 - (std_dev(agent_tasks) / mean(agent_tasks))
```

**Implementation**:

```python
import statistics

def calculate_task_distribution_balance(agent_tasks: dict) -> float:
    """Calculate balance of task distribution across agents.
    
    Args:
        agent_tasks: Dict mapping agent_id to task_count
        
    Returns:
        Balance score between 0.0 and 1.0 (higher is more balanced)
    """
    if not agent_tasks or len(agent_tasks) < 2:
        return 1.0  # Perfect balance for single/no agents
    
    task_counts = list(agent_tasks.values())
    
    if all(count == 0 for count in task_counts):
        return 1.0  # No tasks assigned yet
    
    mean_tasks = statistics.mean(task_counts)
    if mean_tasks == 0:
        return 1.0
    
    std_dev = statistics.stdev(task_counts) if len(task_counts) > 1 else 0.0
    
    balance_score = 1 - (std_dev / mean_tasks)
    return max(0.0, balance_score)  # Ensure non-negative
```

## Composite Scoring Implementation

### Weighted Average Formula

**Configuration-Based Weights**:

```python
def calculate_composite_score(metrics: dict, weights: dict = None) -> float:
    """Calculate weighted composite score from all tiers.
    
    Args:
        metrics: Dict containing all normalized metric scores
        weights: Optional custom weights (defaults to config_eval.json)
        
    Returns:
        Composite score between 0.0 and 1.0
    """
    if weights is None:
        weights = {
            "time_taken": 0.167,
            "task_success": 0.167,
            "coordination_quality": 0.167, 
            "tool_efficiency": 0.167,
            "planning_rational": 0.167,
            "output_similarity": 0.167
        }
    
    # Normalize time_taken (lower is better)
    if "time_taken" in metrics:
        metrics["time_taken"] = 1 / (1 + math.log(max(0.1, metrics["time_taken"])))
    
    # Calculate weighted sum
    composite_score = sum(
        metrics.get(metric, 0.0) * weight 
        for metric, weight in weights.items()
    )
    
    return min(1.0, max(0.0, composite_score))  # Clamp to [0,1]
```

### Recommendation Mapping

**Score-to-Recommendation Formula**:

```python
def map_score_to_recommendation(composite_score: float) -> tuple[str, float]:
    """Map composite score to academic recommendation.
    
    Args:
        composite_score: Normalized score between 0.0 and 1.0
        
    Returns:
        Tuple of (recommendation_label, recommendation_weight)
    """
    if composite_score >= 0.8:
        return ("accept", 1.0)
    elif composite_score >= 0.6:
        return ("weak_accept", 0.7)
    elif composite_score >= 0.4:
        return ("weak_reject", -0.7)
    else:
        return ("reject", -1.0)
```

## Implementation Dependencies

### Required Libraries

```python
# Core dependencies (already in pyproject.toml)
torchmetrics[text]>=1.4.0      # BERT-based semantic similarity
scikit-learn>=1.5.0            # Cosine similarity, vectorization
nltk>=3.9.0                    # Text processing utilities  
textdistance>=4.6.0            # Jaccard and other text distances
pydantic-ai-slim>=0.2.12       # LLM-as-Judge implementations

# Additional for Tier 3 (lightweight)
networkx>=3.0                  # Graph analysis (no additional dependencies)
```

### Performance Optimization

**Memory Management**:

- Stream processing for large documents  
- Batch processing for multiple evaluations
- Lazy loading of models and embeddings

**Computational Efficiency**:

- Cache TF-IDF vectorizers for repeated use
- Reuse BERT models across evaluations  
- Parallel processing for independent metrics

**Error Handling**:

- Graceful degradation on API failures
- Fallback to simpler metrics when complex ones fail
- Comprehensive logging for debugging

This specification provides complete implementation guidance for all evaluation metrics with exact formulas, performance targets, and error handling requirements for the three-tiered PeerRead evaluation system.
