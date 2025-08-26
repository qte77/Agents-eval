# Implementation Handoff: Three-Tiered Evaluation Framework

**Document Version**: 1.0  
**Sprint**: 1 - Three-Tiered PeerRead Evaluation System  
**Date**: 2025-08-26  
**Status**: Ready for Developer Implementation

## Executive Summary

This document provides complete implementation specifications for Python developers to build the three-tiered evaluation framework following the architecture design. All technical requirements, file structures, and integration patterns are specified for direct implementation.

**Implementation Timeline**: Days 2-4 (Post Architecture Phase)  
**Primary Dependencies**: Lightweight-first approach (<100MB total)  
**Performance Targets**: <5s pipeline latency

## Project Structure & Files

### Required Directory Structure

```text
src/app/evals/
├── __init__.py
├── evaluation_engine.py          # Main orchestrator
├── traditional_metrics.py        # Tier 1 implementation
├── llm_judge.py                  # Tier 2 implementation  
├── graph_analysis.py             # Tier 3 implementation
├── trace_processors.py           # Observability integration
└── composite_scoring.py          # Final score calculation

src/app/data_models/
├── evaluation_models.py          # New evaluation data models
└── peerread_evaluation_models.py # Existing (extend as needed)

src/app/config/
└── config_eval.json             # Evaluation configuration

tests/evals/
├── __init__.py
├── test_traditional_metrics.py
├── test_llm_judge.py
├── test_graph_analysis.py
├── test_evaluation_engine.py
└── fixtures/                     # Test data samples
```

## Implementation Phase 1: Traditional Metrics Engine

### File: `src/app/evals/traditional_metrics.py`

```python
"""
Traditional metrics implementation for Tier 1 evaluation.

Provides fast, lightweight text similarity and execution metrics
using minimal dependencies with <1s performance target.
"""

import time
import math
from typing import Dict, List, Any
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textdistance
from torchmetrics.text import BERTScore
from pydantic import BaseModel, Field

from app.utils.log import get_logger
from app.data_models.evaluation_models import Tier1Result

logger = get_logger(__name__)


class TraditionalMetricsEngine:
    """Lightweight traditional metrics engine for fast evaluation."""
    
    def __init__(self):
        """Initialize metrics engine with cached components."""
        self._vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000  # Limit for performance
        )
        self._bertscore = None  # Lazy loading
        
    def _get_bertscore_model(self) -> BERTScore:
        """Lazy load BERTScore model to save memory."""
        if self._bertscore is None:
            self._bertscore = BERTScore(
                model_name_or_path='distilbert-base-uncased',
                device='cpu'  # CPU for compatibility
            )
        return self._bertscore
    
    def compute_cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity between two texts.
        
        Args:
            text1: Agent-generated review text
            text2: Reference review text
            
        Returns:
            Similarity score between 0.0 and 1.0
            
        Performance: ~50ms for typical review lengths
        """
        try:
            if not text1.strip() or not text2.strip():
                return 1.0 if text1 == text2 else 0.0
                
            # Create TF-IDF vectors
            tfidf_matrix = self._vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
            
        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def compute_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Compute word-level Jaccard similarity.
        
        Args:
            text1: Agent-generated review text
            text2: Reference review text
            
        Returns:
            Similarity score between 0.0 and 1.0
            
        Performance: ~10ms for typical review lengths
        """
        try:
            # Tokenize and convert to sets
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if len(words1) == 0 and len(words2) == 0:
                return 1.0
                
            # Calculate Jaccard index
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"Jaccard similarity calculation failed: {e}")
            return 0.0
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute BERT-based semantic similarity.
        
        Args:
            text1: Agent-generated review text
            text2: Reference review text
            
        Returns:
            BERTScore F1 between 0.0 and 1.0
            
        Performance: ~200ms including model inference
        """
        try:
            bertscore = self._get_bertscore_model()
            scores = bertscore([text1], [text2])
            return float(scores['f1'][0])
            
        except Exception as e:
            logger.warning(f"Semantic similarity calculation failed: {e}")
            # Fallback to cosine similarity
            return self.compute_cosine_similarity(text1, text2)
    
    def measure_execution_time(self, start_time: float, end_time: float) -> float:
        """Calculate execution time with normalization for scoring.
        
        Args:
            start_time: Start timestamp (from time.perf_counter())
            end_time: End timestamp (from time.perf_counter())
            
        Returns:
            Normalized time score for composite scoring (0.0-1.0)
        """
        duration = max(0.001, end_time - start_time)  # Minimum 1ms
        
        # Normalize using log scale: faster is better
        # Formula: 1 / (1 + log(time_seconds))
        normalized_score = 1.0 / (1.0 + math.log(duration))
        return min(1.0, normalized_score)
    
    def assess_task_success(self, similarity_scores: Dict[str, float], 
                          threshold: float = 0.8) -> float:
        """Assess task completion success based on similarity threshold.
        
        Args:
            similarity_scores: Dict with semantic, cosine, jaccard scores
            threshold: Minimum similarity for success (from config)
            
        Returns:
            1.0 for success, 0.0 for failure
        """
        try:
            # Weighted average of similarity metrics
            weights = {
                'semantic': 0.5,
                'cosine': 0.3,
                'jaccard': 0.2
            }
            
            overall_similarity = sum(
                similarity_scores.get(metric, 0.0) * weight 
                for metric, weight in weights.items()
            )
            
            return 1.0 if overall_similarity >= threshold else 0.0
            
        except Exception as e:
            logger.warning(f"Task success assessment failed: {e}")
            return 0.0
    
    def evaluate_traditional_metrics(self, agent_output: str, 
                                   reference_texts: List[str],
                                   start_time: float,
                                   end_time: float,
                                   config: Dict[str, Any]) -> Tier1Result:
        """Complete traditional metrics evaluation.
        
        Args:
            agent_output: Generated review text
            reference_texts: List of ground truth reviews
            start_time: Execution start timestamp
            end_time: Execution end timestamp
            config: Configuration from config_eval.json
            
        Returns:
            Tier1Result with all traditional metrics
        """
        # Calculate similarity against all reference texts
        similarity_results = []
        
        for reference in reference_texts:
            cosine_score = self.compute_cosine_similarity(agent_output, reference)
            jaccard_score = self.compute_jaccard_similarity(agent_output, reference)
            semantic_score = self.compute_semantic_similarity(agent_output, reference)
            
            similarity_results.append({
                'cosine': cosine_score,
                'jaccard': jaccard_score,
                'semantic': semantic_score
            })
        
        # Take best scores (agent might match one review better than others)
        best_scores = {
            'cosine': max(r['cosine'] for r in similarity_results),
            'jaccard': max(r['jaccard'] for r in similarity_results),
            'semantic': max(r['semantic'] for r in similarity_results)
        }
        
        # Calculate execution metrics
        time_score = self.measure_execution_time(start_time, end_time)
        task_success = self.assess_task_success(
            best_scores, 
            config.get('confidence_threshold', 0.8)
        )
        
        # Calculate weighted overall score
        weights = config.get('metrics_and_weights', {})
        overall_score = (
            best_scores['semantic'] * weights.get('semantic', 0.4) +
            best_scores['cosine'] * weights.get('cosine', 0.3) +
            best_scores['jaccard'] * weights.get('jaccard', 0.2) +
            time_score * weights.get('time_taken', 0.1)
        )
        
        return Tier1Result(
            cosine_score=best_scores['cosine'],
            jaccard_score=best_scores['jaccard'],
            semantic_score=best_scores['semantic'],
            execution_time=end_time - start_time,
            time_score=time_score,
            task_success=task_success,
            overall_score=overall_score
        )
```

### Required Data Model: `src/app/data_models/evaluation_models.py`

```python
"""
Data models for three-tiered evaluation system.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Tier1Result(BaseModel):
    """Traditional metrics evaluation result."""
    
    cosine_score: float = Field(ge=0.0, le=1.0, description="TF-IDF cosine similarity")
    jaccard_score: float = Field(ge=0.0, le=1.0, description="Word-level Jaccard similarity")
    semantic_score: float = Field(ge=0.0, le=1.0, description="BERT-based semantic similarity")
    execution_time: float = Field(ge=0.0, description="Raw execution time in seconds")
    time_score: float = Field(ge=0.0, le=1.0, description="Normalized time score")
    task_success: float = Field(description="Binary success indicator (0.0 or 1.0)")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted traditional metrics score")


class Tier2Result(BaseModel):
    """LLM-as-Judge evaluation result."""
    
    technical_accuracy: float = Field(ge=0.0, le=1.0, description="Technical accuracy score")
    constructiveness: float = Field(ge=0.0, le=1.0, description="Constructiveness score")
    clarity: float = Field(ge=0.0, le=1.0, description="Clarity and coherence score")
    planning_rationality: float = Field(ge=0.0, le=1.0, description="Planning quality score")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted LLM judge score")
    model_used: str = Field(description="LLM model used for evaluation")
    api_cost: Optional[float] = Field(description="Estimated API cost in USD")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")


class Tier3Result(BaseModel):
    """Graph-based analysis result."""
    
    path_convergence: float = Field(ge=0.0, le=1.0, description="Tool usage efficiency")
    tool_selection_accuracy: float = Field(ge=0.0, le=1.0, description="Tool choice accuracy")
    communication_overhead: float = Field(ge=0.0, le=1.0, description="Communication efficiency")
    coordination_centrality: float = Field(ge=0.0, le=1.0, description="Coordination quality")
    task_distribution_balance: float = Field(ge=0.0, le=1.0, description="Load balancing")
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted graph analysis score")
    graph_complexity: int = Field(description="Number of nodes in interaction graph")


class CompositeEvaluationResult(BaseModel):
    """Complete three-tier evaluation result."""
    
    paper_id: str = Field(description="Evaluated paper identifier")
    agent_review: str = Field(description="Generated review text")
    
    tier1_results: Tier1Result
    tier2_results: Optional[Tier2Result] = None
    tier3_results: Optional[Tier3Result] = None
    
    composite_score: float = Field(ge=0.0, le=1.0, description="Final weighted score")
    recommendation: str = Field(description="accept/weak_accept/weak_reject/reject")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in evaluation")
    
    # Performance metrics
    tier1_duration: float = Field(description="Tier 1 execution time")
    tier2_duration: Optional[float] = None
    tier3_duration: Optional[float] = None
    total_duration: float = Field(description="Total evaluation time")
    
    # Metadata
    timestamp: str = Field(description="ISO 8601 evaluation timestamp")
    config_version: str = Field(description="Configuration version used")
```

## Implementation Phase 2: LLM-as-Judge Engine

### File: `src/app/evals/llm_judge.py`

```python
"""
LLM-as-Judge implementation for Tier 2 evaluation.

Provides quality assessment using existing PydanticAI infrastructure
with cost optimization and fallback mechanisms.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from pydantic_ai import Agent
from app.utils.log import get_logger
from app.data_models.evaluation_models import Tier2Result
from app.evals.traditional_metrics import TraditionalMetricsEngine

logger = get_logger(__name__)


class TechnicalAccuracyAssessment(BaseModel):
    """Structured LLM assessment of technical accuracy."""
    factual_correctness: float  # 1-5 scale
    methodology_understanding: float  # 1-5 scale  
    domain_knowledge: float  # 1-5 scale
    explanation: str


class ConstructivenessAssessment(BaseModel):
    """Structured LLM assessment of review constructiveness."""
    actionable_feedback: float  # 1-5 scale
    balanced_critique: float    # 1-5 scale
    improvement_guidance: float # 1-5 scale
    explanation: str


class PlanningRationalityAssessment(BaseModel):
    """Structured LLM assessment of planning quality."""
    logical_flow: float        # 1-5 scale
    decision_quality: float    # 1-5 scale 
    resource_efficiency: float # 1-5 scale
    explanation: str


class LLMJudgeEngine:
    """LLM-as-Judge evaluation engine with fallback mechanisms."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM judge with configuration."""
        self.config = config
        self.fallback_engine = TraditionalMetricsEngine()
        
        # Cost-optimized model selection
        self.default_model = config.get('llm_judge_model', 'gpt-4o-mini')
        self.max_retries = config.get('llm_max_retries', 2)
        self.timeout = config.get('llm_timeout', 30.0)
    
    async def assess_technical_accuracy(self, paper: str, review: str) -> float:
        """Assess technical accuracy of review against paper.
        
        Args:
            paper: Paper content (truncated for API efficiency)
            review: Agent-generated review
            
        Returns:
            Normalized technical accuracy score (0.0-1.0)
        """
        try:
            # Truncate paper content for cost efficiency
            paper_excerpt = paper[:2000] if len(paper) > 2000 else paper
            
            prompt = f"""
            Evaluate the technical accuracy of this academic review (1-5 scale):
            
            Paper Excerpt: {paper_excerpt}
            
            Review: {review}
            
            Rate each aspect (1=poor, 5=excellent):
            1. Factual Correctness: Are claims supported by the paper?
            2. Methodology Understanding: Does reviewer grasp the approach?
            3. Domain Knowledge: Appropriate technical terminology?
            
            Provide scores and brief explanation.
            """
            
            agent = Agent(model_name=self.default_model)
            
            result = await asyncio.wait_for(
                agent.run(prompt, result_type=TechnicalAccuracyAssessment),
                timeout=self.timeout
            )
            
            # Calculate weighted score and normalize to 0-1
            weighted_score = (
                result.factual_correctness * 0.5 +
                result.methodology_understanding * 0.3 + 
                result.domain_knowledge * 0.2
            ) / 5.0
            
            return min(1.0, max(0.0, weighted_score))
            
        except Exception as e:
            logger.warning(f"Technical accuracy assessment failed: {e}")
            # Fallback to semantic similarity
            return self.fallback_engine.compute_semantic_similarity(paper, review)
    
    async def assess_constructiveness(self, review: str) -> float:
        """Assess constructiveness and helpfulness of review.
        
        Args:
            review: Agent-generated review text
            
        Returns:
            Normalized constructiveness score (0.0-1.0)
        """
        try:
            prompt = f"""
            Evaluate the constructiveness of this academic review (1-5 scale):
            
            Review: {review}
            
            Rate each aspect (1=poor, 5=excellent):
            1. Actionable Feedback: Specific, implementable suggestions?
            2. Balanced Critique: Both strengths and weaknesses noted?
            3. Improvement Guidance: Clear direction for authors?
            
            Provide scores and brief explanation.
            """
            
            agent = Agent(model_name=self.default_model)
            
            result = await asyncio.wait_for(
                agent.run(prompt, result_type=ConstructivenessAssessment),
                timeout=self.timeout
            )
            
            # Equal weighting for constructiveness aspects
            average_score = (
                result.actionable_feedback + 
                result.balanced_critique + 
                result.improvement_guidance
            ) / 15.0  # Normalize to 0-1
            
            return min(1.0, max(0.0, average_score))
            
        except Exception as e:
            logger.warning(f"Constructiveness assessment failed: {e}")
            # Simple fallback: check for key constructive phrases
            return self._fallback_constructiveness_check(review)
    
    async def assess_planning_rationality(self, execution_trace: Dict[str, Any]) -> float:
        """Assess quality of agent planning and decision-making.
        
        Args:
            execution_trace: Agent execution trace data
            
        Returns:
            Normalized planning rationality score (0.0-1.0)
        """
        try:
            # Extract planning summary from trace
            planning_summary = self._extract_planning_decisions(execution_trace)
            
            prompt = f"""
            Evaluate the planning rationality of this agent execution (1-5 scale):
            
            Execution Summary: {planning_summary}
            
            Rate each aspect (1=poor, 5=excellent):
            1. Logical Flow: Coherent step progression?
            2. Decision Quality: Appropriate choices made?  
            3. Resource Efficiency: Optimal tool/agent usage?
            
            Provide scores and brief explanation.
            """
            
            agent = Agent(model_name=self.default_model)
            
            result = await asyncio.wait_for(
                agent.run(prompt, result_type=PlanningRationalityAssessment),
                timeout=self.timeout
            )
            
            # Weight decision quality most heavily
            weighted_score = (
                result.logical_flow * 0.3 +
                result.decision_quality * 0.5 + 
                result.resource_efficiency * 0.2
            ) / 5.0
            
            return min(1.0, max(0.0, weighted_score))
            
        except Exception as e:
            logger.warning(f"Planning rationality assessment failed: {e}")
            # Simple fallback based on trace structure
            return self._fallback_planning_check(execution_trace)
    
    async def evaluate_llm_judge(self, paper: str, review: str, 
                               execution_trace: Dict[str, Any]) -> Tier2Result:
        """Complete LLM-as-Judge evaluation with error handling.
        
        Args:
            paper: Full paper content
            review: Agent-generated review
            execution_trace: Agent execution data
            
        Returns:
            Tier2Result with all LLM judge assessments
        """
        fallback_used = False
        api_cost = 0.0
        
        try:
            # Run assessments concurrently for efficiency
            technical_task = self.assess_technical_accuracy(paper, review)
            constructiveness_task = self.assess_constructiveness(review)
            planning_task = self.assess_planning_rationality(execution_trace)
            
            technical_score, constructiveness_score, planning_score = await asyncio.gather(
                technical_task, constructiveness_task, planning_task,
                return_exceptions=True
            )
            
            # Handle individual assessment failures
            if isinstance(technical_score, Exception):
                logger.warning(f"Technical assessment failed: {technical_score}")
                technical_score = self.fallback_engine.compute_semantic_similarity(paper, review)
                fallback_used = True
                
            if isinstance(constructiveness_score, Exception):
                logger.warning(f"Constructiveness assessment failed: {constructiveness_score}")
                constructiveness_score = self._fallback_constructiveness_check(review)
                fallback_used = True
                
            if isinstance(planning_score, Exception):
                logger.warning(f"Planning assessment failed: {planning_score}")
                planning_score = self._fallback_planning_check(execution_trace)
                fallback_used = True
            
            # Estimate API cost (approximate for gpt-4o-mini)
            total_tokens = len(paper) / 4 + len(review) / 4 + 500  # Rough estimate
            api_cost = (total_tokens / 1000) * 0.0001  # $0.0001 per 1K tokens
            
            # Calculate overall LLM judge score
            overall_score = (
                technical_score * 0.4 +
                constructiveness_score * 0.3 +
                planning_score * 0.3
            )
            
            return Tier2Result(
                technical_accuracy=technical_score,
                constructiveness=constructiveness_score,
                clarity=constructiveness_score,  # Use constructiveness as proxy
                planning_rationality=planning_score,
                overall_score=overall_score,
                model_used=self.default_model,
                api_cost=api_cost,
                fallback_used=fallback_used
            )
            
        except Exception as e:
            logger.error(f"Complete LLM judge evaluation failed: {e}")
            # Full fallback to traditional metrics
            return self._complete_fallback(paper, review, execution_trace)
    
    def _extract_planning_decisions(self, execution_trace: Dict[str, Any]) -> str:
        """Extract key planning decisions from execution trace."""
        try:
            decisions = execution_trace.get('agent_interactions', [])
            tool_calls = execution_trace.get('tool_calls', [])
            
            summary = f"Agents involved: {len(decisions)} interactions, "
            summary += f"Tools used: {len(tool_calls)} calls"
            
            return summary[:500]  # Limit length for API efficiency
            
        except Exception:
            return "Limited trace data available"
    
    def _fallback_constructiveness_check(self, review: str) -> float:
        """Simple fallback for constructiveness assessment."""
        constructive_phrases = [
            'suggest', 'recommend', 'could improve', 'might consider',
            'strength', 'weakness', 'clear', 'unclear', 'future work'
        ]
        
        review_lower = review.lower()
        matches = sum(1 for phrase in constructive_phrases if phrase in review_lower)
        
        return min(1.0, matches / len(constructive_phrases))
    
    def _fallback_planning_check(self, execution_trace: Dict[str, Any]) -> float:
        """Simple fallback for planning rationality."""
        try:
            interactions = len(execution_trace.get('agent_interactions', []))
            tool_calls = len(execution_trace.get('tool_calls', []))
            
            # Simple heuristic: moderate activity indicates good planning
            activity_score = min(1.0, (interactions + tool_calls) / 10.0)
            return activity_score
            
        except Exception:
            return 0.5  # Neutral score when trace unavailable
    
    def _complete_fallback(self, paper: str, review: str, 
                          execution_trace: Dict[str, Any]) -> Tier2Result:
        """Complete fallback when all LLM assessments fail."""
        # Use traditional metrics as fallback
        semantic_score = self.fallback_engine.compute_semantic_similarity(paper, review)
        constructiveness_score = self._fallback_constructiveness_check(review)
        planning_score = self._fallback_planning_check(execution_trace)
        
        overall_score = (semantic_score + constructiveness_score + planning_score) / 3.0
        
        return Tier2Result(
            technical_accuracy=semantic_score,
            constructiveness=constructiveness_score,
            clarity=constructiveness_score,
            planning_rationality=planning_score,
            overall_score=overall_score,
            model_used="fallback_traditional",
            api_cost=0.0,
            fallback_used=True
        )
```

## Implementation Phase 3: Graph-Based Analysis

### File: `src/app/evals/graph_analysis.py`

```python
"""
Graph-based analysis implementation for Tier 3 evaluation.

Provides NetworkX-based analysis of tool usage and agent coordination
patterns with performance optimization for <15s execution.
"""

import statistics
from typing import Dict, List, Any, Tuple, Optional
import networkx as nx
from dataclasses import dataclass

from app.utils.log import get_logger
from app.data_models.evaluation_models import Tier3Result

logger = get_logger(__name__)


@dataclass
class GraphMetrics:
    """Container for graph analysis metrics."""
    path_convergence: float
    tool_accuracy: float
    communication_overhead: float
    centrality_scores: Dict[str, float]
    task_balance: float


class GraphAnalysisEngine:
    """NetworkX-based graph analysis for agent coordination evaluation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize graph analysis engine."""
        self.config = config
        self.optimal_tools = self._load_optimal_tool_mappings()
    
    def build_tool_graph(self, execution_trace: Dict[str, Any]) -> nx.DiGraph:
        """Build directed graph of tool call dependencies.
        
        Args:
            execution_trace: Execution trace with tool_calls data
            
        Returns:
            NetworkX directed graph of tool dependencies
        """
        try:
            tool_calls = execution_trace.get('tool_calls', [])
            
            if not tool_calls:
                return nx.DiGraph()
            
            G = nx.DiGraph()
            
            # Add nodes for each tool call
            for i, call in enumerate(tool_calls):
                tool_name = call.get('tool_name', f'unknown_{i}')
                G.add_node(
                    tool_name,
                    timestamp=call.get('timestamp', 0),
                    context=call.get('context', ''),
                    success=call.get('success', True)
                )
            
            # Add edges based on temporal dependencies
            sorted_calls = sorted(tool_calls, key=lambda x: x.get('timestamp', 0))
            
            for i in range(1, len(sorted_calls)):
                prev_tool = sorted_calls[i-1].get('tool_name', f'unknown_{i-1}')
                curr_tool = sorted_calls[i].get('tool_name', f'unknown_{i}')
                
                # Add edge if tools are related or sequential
                if self._tools_are_related(sorted_calls[i-1], sorted_calls[i]):
                    G.add_edge(prev_tool, curr_tool, weight=1.0)
            
            return G
            
        except Exception as e:
            logger.warning(f"Tool graph construction failed: {e}")
            return nx.DiGraph()
    
    def build_interaction_graph(self, execution_trace: Dict[str, Any]) -> nx.DiGraph:
        """Build directed graph of agent interactions.
        
        Args:
            execution_trace: Execution trace with agent_interactions data
            
        Returns:
            NetworkX directed graph of agent communications
        """
        try:
            interactions = execution_trace.get('agent_interactions', [])
            
            G = nx.DiGraph()
            
            # Add nodes for each unique agent
            agents = set()
            for interaction in interactions:
                agents.add(interaction.get('from', 'unknown'))
                agents.add(interaction.get('to', 'unknown'))
            
            G.add_nodes_from(agents)
            
            # Add edges for communications
            for interaction in interactions:
                from_agent = interaction.get('from', 'unknown')
                to_agent = interaction.get('to', 'unknown')
                msg_type = interaction.get('type', 'generic')
                
                if G.has_edge(from_agent, to_agent):
                    # Increment weight for repeated communications
                    G[from_agent][to_agent]['weight'] += 1
                    G[from_agent][to_agent]['types'].append(msg_type)
                else:
                    G.add_edge(
                        from_agent, to_agent,
                        weight=1,
                        types=[msg_type]
                    )
            
            return G
            
        except Exception as e:
            logger.warning(f"Interaction graph construction failed: {e}")
            return nx.DiGraph()
    
    def calculate_path_convergence(self, tool_graph: nx.DiGraph) -> float:
        """Calculate tool usage path efficiency.
        
        Args:
            tool_graph: NetworkX graph of tool dependencies
            
        Returns:
            Path convergence ratio (0.0-1.0, higher is better)
        """
        try:
            if len(tool_graph.nodes()) < 2:
                return 1.0  # Perfect for single/no tools
            
            # Find start and end nodes (nodes with no predecessors/successors)
            start_nodes = [n for n in tool_graph.nodes() 
                          if tool_graph.in_degree(n) == 0]
            end_nodes = [n for n in tool_graph.nodes() 
                        if tool_graph.out_degree(n) == 0]
            
            if not start_nodes or not end_nodes:
                return 0.5  # Neutral score for unclear structure
            
            # Calculate efficiency for each start-end pair
            convergence_scores = []
            
            for start in start_nodes:
                for end in end_nodes:
                    try:
                        shortest_path = nx.shortest_path(tool_graph, start, end)
                        optimal_steps = len(shortest_path) - 1
                        
                        # Estimate actual steps (could be improved with trace data)
                        actual_steps = self._estimate_actual_steps(tool_graph, start, end)
                        
                        if actual_steps > 0:
                            convergence = optimal_steps / actual_steps
                            convergence_scores.append(convergence)
                            
                    except nx.NetworkXNoPath:
                        continue
            
            return statistics.mean(convergence_scores) if convergence_scores else 0.5
            
        except Exception as e:
            logger.warning(f"Path convergence calculation failed: {e}")
            return 0.5
    
    def calculate_tool_selection_accuracy(self, execution_trace: Dict[str, Any]) -> float:
        """Calculate accuracy of tool selection decisions.
        
        Args:
            execution_trace: Execution trace with tool usage data
            
        Returns:
            Tool selection accuracy (0.0-1.0)
        """
        try:
            tool_calls = execution_trace.get('tool_calls', [])
            
            if not tool_calls:
                return 1.0  # No tools used = no errors
            
            correct_selections = 0
            
            for call in tool_calls:
                context = call.get('context', '').lower()
                selected_tool = call.get('tool_name', '')
                
                # Determine optimal tool for this context
                optimal_tool = self._determine_optimal_tool(context)
                
                if selected_tool == optimal_tool:
                    correct_selections += 1
            
            return correct_selections / len(tool_calls)
            
        except Exception as e:
            logger.warning(f"Tool selection accuracy calculation failed: {e}")
            return 0.5
    
    def calculate_communication_overhead(self, interaction_graph: nx.DiGraph) -> float:
        """Calculate communication efficiency.
        
        Args:
            interaction_graph: NetworkX graph of agent interactions
            
        Returns:
            Communication overhead (0.0-1.0, lower is better)
        """
        try:
            if len(interaction_graph.edges()) == 0:
                return 0.0  # No communication = no overhead
            
            coordination_weight = 0
            productive_weight = 0
            
            for edge in interaction_graph.edges(data=True):
                types = edge[2].get('types', [])
                weight = edge[2].get('weight', 1)
                
                for msg_type in types:
                    if msg_type in ['coordination', 'status_update', 'handoff']:
                        coordination_weight += weight
                    elif msg_type in ['task_request', 'result_delivery', 'data_transfer']:
                        productive_weight += weight
            
            total_weight = coordination_weight + productive_weight
            
            if total_weight == 0:
                return 0.0
            
            overhead_ratio = coordination_weight / total_weight
            return min(1.0, overhead_ratio)
            
        except Exception as e:
            logger.warning(f"Communication overhead calculation failed: {e}")
            return 0.5
    
    def calculate_coordination_centrality(self, interaction_graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate centrality measures for coordination analysis.
        
        Args:
            interaction_graph: NetworkX graph of agent interactions
            
        Returns:
            Dict mapping agent names to centrality scores
        """
        try:
            if len(interaction_graph.nodes()) == 0:
                return {}
            
            # Calculate different centrality measures
            try:
                betweenness = nx.betweenness_centrality(interaction_graph)
            except:
                betweenness = {node: 0.0 for node in interaction_graph.nodes()}
            
            try:
                closeness = nx.closeness_centrality(interaction_graph)
            except:
                closeness = {node: 0.0 for node in interaction_graph.nodes()}
            
            try:
                degree = nx.degree_centrality(interaction_graph)
            except:
                degree = {node: 0.0 for node in interaction_graph.nodes()}
            
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
            
        except Exception as e:
            logger.warning(f"Centrality calculation failed: {e}")
            return {}
    
    def calculate_task_distribution_balance(self, execution_trace: Dict[str, Any]) -> float:
        """Calculate balance of task distribution across agents.
        
        Args:
            execution_trace: Execution trace with agent activity data
            
        Returns:
            Task balance score (0.0-1.0, higher is more balanced)
        """
        try:
            interactions = execution_trace.get('agent_interactions', [])
            
            if not interactions:
                return 1.0  # Perfect balance for no interactions
            
            # Count tasks per agent
            agent_tasks = {}
            for interaction in interactions:
                from_agent = interaction.get('from', 'unknown')
                if interaction.get('type') in ['task_request', 'result_delivery']:
                    agent_tasks[from_agent] = agent_tasks.get(from_agent, 0) + 1
            
            if len(agent_tasks) < 2:
                return 1.0  # Perfect balance for single agent
            
            task_counts = list(agent_tasks.values())
            
            if all(count == 0 for count in task_counts):
                return 1.0  # No tasks = perfect balance
            
            mean_tasks = statistics.mean(task_counts)
            if mean_tasks == 0:
                return 1.0
            
            std_dev = statistics.stdev(task_counts) if len(task_counts) > 1 else 0.0
            
            balance_score = 1.0 - (std_dev / mean_tasks)
            return max(0.0, balance_score)
            
        except Exception as e:
            logger.warning(f"Task distribution balance calculation failed: {e}")
            return 0.5
    
    def evaluate_graph_analysis(self, execution_trace: Dict[str, Any]) -> Tier3Result:
        """Complete graph-based analysis evaluation.
        
        Args:
            execution_trace: Complete execution trace data
            
        Returns:
            Tier3Result with all graph analysis metrics
        """
        try:
            # Build analysis graphs
            tool_graph = self.build_tool_graph(execution_trace)
            interaction_graph = self.build_interaction_graph(execution_trace)
            
            # Calculate core metrics
            path_convergence = self.calculate_path_convergence(tool_graph)
            tool_accuracy = self.calculate_tool_selection_accuracy(execution_trace)
            comm_overhead = self.calculate_communication_overhead(interaction_graph)
            centrality_scores = self.calculate_coordination_centrality(interaction_graph)
            task_balance = self.calculate_task_distribution_balance(execution_trace)
            
            # Calculate coordination quality (inverse of overhead)
            coordination_quality = 1.0 - comm_overhead
            
            # Calculate overall coordination centrality
            avg_centrality = (
                statistics.mean(centrality_scores.values()) 
                if centrality_scores else 0.5
            )
            
            # Calculate weighted overall score
            weights = self.config.get('graph_weights', {
                'path_convergence': 0.3,
                'tool_accuracy': 0.25,
                'coordination_quality': 0.25,
                'task_balance': 0.2
            })
            
            overall_score = (
                path_convergence * weights.get('path_convergence', 0.3) +
                tool_accuracy * weights.get('tool_accuracy', 0.25) +
                coordination_quality * weights.get('coordination_quality', 0.25) +
                task_balance * weights.get('task_balance', 0.2)
            )
            
            return Tier3Result(
                path_convergence=path_convergence,
                tool_selection_accuracy=tool_accuracy,
                communication_overhead=comm_overhead,
                coordination_centrality=avg_centrality,
                task_distribution_balance=task_balance,
                overall_score=overall_score,
                graph_complexity=len(interaction_graph.nodes())
            )
            
        except Exception as e:
            logger.error(f"Graph analysis evaluation failed: {e}")
            # Return neutral scores on failure
            return Tier3Result(
                path_convergence=0.5,
                tool_selection_accuracy=0.5,
                communication_overhead=0.5,
                coordination_centrality=0.5,
                task_distribution_balance=0.5,
                overall_score=0.5,
                graph_complexity=0
            )
    
    # Helper methods
    def _load_optimal_tool_mappings(self) -> Dict[str, str]:
        """Load optimal tool mappings for accuracy assessment."""
        return {
            'search': 'duckduckgo_search',
            'retrieve': 'paper_retrieval',
            'extract': 'content_extraction',
            'synthesize': 'review_synthesis'
        }
    
    def _tools_are_related(self, call1: Dict, call2: Dict) -> bool:
        """Determine if two tool calls are logically related."""
        # Simple heuristic: tools used within 5 seconds are related
        time_diff = abs(call1.get('timestamp', 0) - call2.get('timestamp', 0))
        return time_diff < 5.0
    
    def _estimate_actual_steps(self, graph: nx.DiGraph, start: str, end: str) -> int:
        """Estimate actual steps taken (simplified for implementation)."""
        try:
            # Use graph diameter as proxy for actual complexity
            return max(3, len(graph.nodes()) // 2)
        except:
            return 3  # Default assumption
    
    def _determine_optimal_tool(self, context: str) -> str:
        """Determine optimal tool for given context."""
        for keyword, tool in self.optimal_tools.items():
            if keyword in context:
                return tool
        return 'unknown'  # Default when no clear match
```

## Implementation Phase 4: Main Evaluation Engine

### File: `src/app/evals/evaluation_engine.py`

```python
"""
Main evaluation engine orchestrating all three tiers.

Coordinates traditional metrics, LLM-as-Judge, and graph analysis
with performance monitoring and composite scoring.
"""

import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.utils.log import get_logger
from app.utils.load_configs import load_evaluation_config
from app.data_models.evaluation_models import CompositeEvaluationResult
from app.evals.traditional_metrics import TraditionalMetricsEngine
from app.evals.llm_judge import LLMJudgeEngine
from app.evals.graph_analysis import GraphAnalysisEngine
from app.evals.composite_scoring import CompositeScorer

logger = get_logger(__name__)


class EvaluationEngine:
    """Main orchestrator for three-tiered evaluation system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize evaluation engine with configuration."""
        self.config = load_evaluation_config(config_path)
        
        # Initialize tier engines
        self.tier1_engine = TraditionalMetricsEngine()
        self.tier2_engine = LLMJudgeEngine(self.config)
        self.tier3_engine = GraphAnalysisEngine(self.config)
        self.scorer = CompositeScorer(self.config)
        
        # Performance monitoring
        self.performance_targets = {
            'tier1_max': 1.0,   # seconds
            'tier2_max': 10.0,  # seconds
            'tier3_max': 15.0,  # seconds
            'total_max': 25.0   # seconds
        }
    
    async def evaluate_complete(
        self,
        paper_id: str,
        paper_content: str,
        agent_review: str,
        reference_reviews: List[str],
        execution_trace: Dict[str, Any],
        tiers_enabled: List[int] = [1, 2, 3]
    ) -> CompositeEvaluationResult:
        """
        Run complete three-tiered evaluation.
        
        Args:
            paper_id: Unique identifier for the paper
            paper_content: Full paper text content
            agent_review: Agent-generated review
            reference_reviews: Ground truth reviews from PeerRead
            execution_trace: Agent execution trace data
            tiers_enabled: Which tiers to run (default: all)
            
        Returns:
            Complete evaluation result with all metrics
        """
        total_start_time = time.perf_counter()
        
        try:
            logger.info(f"Starting evaluation for paper {paper_id}")
            
            # Initialize result structure
            result_data = {
                'paper_id': paper_id,
                'agent_review': agent_review,
                'timestamp': datetime.utcnow().isoformat(),
                'config_version': self.config.get('version', '1.0')
            }
            
            # Tier 1: Traditional Metrics (Always run for baseline)
            tier1_result = None
            tier1_duration = 0.0
            
            if 1 in tiers_enabled:
                tier1_start = time.perf_counter()
                
                tier1_result = self.tier1_engine.evaluate_traditional_metrics(
                    agent_output=agent_review,
                    reference_texts=reference_reviews,
                    start_time=tier1_start,
                    end_time=tier1_start + 0.1,  # Placeholder timing
                    config=self.config
                )
                
                tier1_end = time.perf_counter()
                tier1_duration = tier1_end - tier1_start
                
                logger.info(f"Tier 1 completed in {tier1_duration:.3f}s")
                
                # Check performance target
                if tier1_duration > self.performance_targets['tier1_max']:
                    logger.warning(f"Tier 1 exceeded target: {tier1_duration:.3f}s > {self.performance_targets['tier1_max']}s")
            
            # Tier 2: LLM-as-Judge (Optional with fallback)
            tier2_result = None
            tier2_duration = 0.0
            
            if 2 in tiers_enabled:
                tier2_start = time.perf_counter()
                
                try:
                    tier2_result = await self.tier2_engine.evaluate_llm_judge(
                        paper=paper_content,
                        review=agent_review,
                        execution_trace=execution_trace
                    )
                    
                    tier2_end = time.perf_counter()
                    tier2_duration = tier2_end - tier2_start
                    
                    logger.info(f"Tier 2 completed in {tier2_duration:.3f}s")
                    
                    if tier2_duration > self.performance_targets['tier2_max']:
                        logger.warning(f"Tier 2 exceeded target: {tier2_duration:.3f}s > {self.performance_targets['tier2_max']}s")
                        
                except Exception as e:
                    logger.error(f"Tier 2 evaluation failed: {e}")
                    tier2_duration = time.perf_counter() - tier2_start
            
            # Tier 3: Graph-based Analysis (Optional)
            tier3_result = None
            tier3_duration = 0.0
            
            if 3 in tiers_enabled and execution_trace:
                tier3_start = time.perf_counter()
                
                try:
                    tier3_result = self.tier3_engine.evaluate_graph_analysis(
                        execution_trace=execution_trace
                    )
                    
                    tier3_end = time.perf_counter()
                    tier3_duration = tier3_end - tier3_start
                    
                    logger.info(f"Tier 3 completed in {tier3_duration:.3f}s")
                    
                    if tier3_duration > self.performance_targets['tier3_max']:
                        logger.warning(f"Tier 3 exceeded target: {tier3_duration:.3f}s > {self.performance_targets['tier3_max']}s")
                        
                except Exception as e:
                    logger.error(f"Tier 3 evaluation failed: {e}")
                    tier3_duration = time.perf_counter() - tier3_start
            
            # Calculate composite score
            total_end_time = time.perf_counter()
            total_duration = total_end_time - total_start_time
            
            composite_score, recommendation, confidence = self.scorer.calculate_composite_score(
                tier1_result=tier1_result,
                tier2_result=tier2_result,
                tier3_result=tier3_result
            )
            
            # Build final result
            result = CompositeEvaluationResult(
                paper_id=result_data['paper_id'],
                agent_review=result_data['agent_review'],
                tier1_results=tier1_result,
                tier2_results=tier2_result,
                tier3_results=tier3_result,
                composite_score=composite_score,
                recommendation=recommendation,
                confidence=confidence,
                tier1_duration=tier1_duration,
                tier2_duration=tier2_duration if tier2_result else None,
                tier3_duration=tier3_duration if tier3_result else None,
                total_duration=total_duration,
                timestamp=result_data['timestamp'],
                config_version=result_data['config_version']
            )
            
            # Performance summary
            logger.info(f"Evaluation completed: {total_duration:.3f}s total, score: {composite_score:.3f}, recommendation: {recommendation}")
            
            if total_duration > self.performance_targets['total_max']:
                logger.warning(f"Total evaluation exceeded target: {total_duration:.3f}s > {self.performance_targets['total_max']}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation engine failed for paper {paper_id}: {e}")
            # Return minimal result on complete failure
            return self._create_fallback_result(paper_id, agent_review, str(e))
    
    async def evaluate_batch(
        self,
        evaluation_requests: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[CompositeEvaluationResult]:
        """
        Evaluate multiple papers concurrently with rate limiting.
        
        Args:
            evaluation_requests: List of evaluation request dicts
            max_concurrent: Maximum concurrent evaluations
            
        Returns:
            List of evaluation results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def evaluate_single(request: Dict[str, Any]) -> CompositeEvaluationResult:
            async with semaphore:
                return await self.evaluate_complete(**request)
        
        tasks = [evaluate_single(req) for req in evaluation_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in batch results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch evaluation {i} failed: {result}")
                fallback = self._create_fallback_result(
                    paper_id=evaluation_requests[i].get('paper_id', f'batch_{i}'),
                    agent_review=evaluation_requests[i].get('agent_review', ''),
                    error_msg=str(result)
                )
                processed_results.append(fallback)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _create_fallback_result(self, paper_id: str, agent_review: str, error_msg: str) -> CompositeEvaluationResult:
        """Create minimal fallback result on complete failure."""
        from app.data_models.evaluation_models import Tier1Result
        
        # Create minimal Tier 1 result
        fallback_tier1 = Tier1Result(
            cosine_score=0.0,
            jaccard_score=0.0,
            semantic_score=0.0,
            execution_time=0.0,
            time_score=0.0,
            task_success=0.0,
            overall_score=0.0
        )
        
        return CompositeEvaluationResult(
            paper_id=paper_id,
            agent_review=agent_review,
            tier1_results=fallback_tier1,
            tier2_results=None,
            tier3_results=None,
            composite_score=0.0,
            recommendation="error",
            confidence=0.0,
            tier1_duration=0.0,
            tier2_duration=None,
            tier3_duration=None,
            total_duration=0.0,
            timestamp=datetime.utcnow().isoformat(),
            config_version=f"error: {error_msg}"
        )


# Convenience functions for common usage patterns

async def evaluate_single_paper(
    paper_id: str,
    paper_content: str,
    agent_review: str,
    reference_reviews: List[str],
    execution_trace: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None
) -> CompositeEvaluationResult:
    """
    Convenience function for single paper evaluation.
    
    Usage:
        result = await evaluate_single_paper(
            paper_id="paper_001",
            paper_content=paper_text,
            agent_review=generated_review,
            reference_reviews=[ref1, ref2],
            execution_trace=trace_data
        )
    """
    engine = EvaluationEngine(config_path)
    return await engine.evaluate_complete(
        paper_id=paper_id,
        paper_content=paper_content,
        agent_review=agent_review,
        reference_reviews=reference_reviews,
        execution_trace=execution_trace or {}
    )


def evaluate_single_paper_sync(
    paper_id: str,
    paper_content: str,
    agent_review: str,
    reference_reviews: List[str],
    execution_trace: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None
) -> CompositeEvaluationResult:
    """
    Synchronous wrapper for single paper evaluation.
    
    Usage:
        result = evaluate_single_paper_sync(
            paper_id="paper_001",
            paper_content=paper_text,
            agent_review=generated_review,
            reference_reviews=[ref1, ref2]
        )
    """
    return asyncio.run(evaluate_single_paper(
        paper_id, paper_content, agent_review, 
        reference_reviews, execution_trace, config_path
    ))
```

## Configuration Integration

### File: `src/app/config/config_eval.json`

```json
{
  "version": "1.0.0",
  "evaluation_system": {
    "tiers_enabled": [1, 2, 3],
    "performance_targets": {
      "tier1_max_seconds": 1.0,
      "tier2_max_seconds": 10.0,
      "tier3_max_seconds": 15.0,
      "total_max_seconds": 25.0
    }
  },
  
  "tier1_traditional": {
    "similarity_metrics": ["cosine", "jaccard", "semantic"],
    "confidence_threshold": 0.8,
    "bertscore_model": "distilbert-base-uncased",
    "tfidf_max_features": 5000,
    "weights": {
      "semantic": 0.4,
      "cosine": 0.3,
      "jaccard": 0.2,
      "time_taken": 0.1
    }
  },
  
  "tier2_llm_judge": {
    "model": "gpt-4o-mini",
    "max_retries": 2,
    "timeout_seconds": 30.0,
    "cost_budget_usd": 0.05,
    "paper_excerpt_length": 2000,
    "weights": {
      "technical_accuracy": 0.4,
      "constructiveness": 0.3,
      "planning_rationality": 0.3
    }
  },
  
  "tier3_graph": {
    "min_nodes_for_analysis": 2,
    "centrality_measures": ["betweenness", "closeness", "degree"],
    "weights": {
      "path_convergence": 0.3,
      "tool_accuracy": 0.25,
      "coordination_quality": 0.25,
      "task_balance": 0.2
    }
  },
  
  "composite_scoring": {
    "metrics_and_weights": {
      "time_taken": 0.167,
      "task_success": 0.167,
      "coordination_quality": 0.167,
      "tool_efficiency": 0.167,
      "planning_rational": 0.167,
      "output_similarity": 0.167
    },
    "recommendation_thresholds": {
      "accept": 0.8,
      "weak_accept": 0.6,
      "weak_reject": 0.4,
      "reject": 0.0
    },
    "fallback_strategy": "tier1_only"
  },
  
  "observability": {
    "trace_collection": true,
    "agentneo_enabled": true,
    "opik_enabled": false,
    "trace_storage_path": "./logs/traces/",
    "performance_logging": true
  }
}
```

## Testing Requirements

### File: `tests/evals/test_evaluation_engine.py`

```python
"""
BDD-style tests for the complete evaluation engine.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from app.evals.evaluation_engine import EvaluationEngine, evaluate_single_paper_sync
from app.data_models.evaluation_models import CompositeEvaluationResult


class TestEvaluationEngine:
    """Test suite for three-tiered evaluation engine."""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample evaluation data."""
        return {
            'paper_id': 'test_paper_001',
            'paper_content': 'This paper presents a novel machine learning approach...',
            'agent_review': 'The paper demonstrates solid methodology and clear results...',
            'reference_reviews': [
                'The work shows promise but needs more evaluation...',
                'Strong technical contribution with minor issues...'
            ],
            'execution_trace': {
                'agent_interactions': [
                    {'from': 'Manager', 'to': 'Researcher', 'type': 'task_request', 'timestamp': 1.0},
                    {'from': 'Researcher', 'to': 'Analyst', 'type': 'data_transfer', 'timestamp': 2.0}
                ],
                'tool_calls': [
                    {'tool_name': 'paper_retrieval', 'timestamp': 1.5, 'success': True},
                    {'tool_name': 'duckduckgo_search', 'timestamp': 2.5, 'success': True}
                ]
            }
        }
    
    def test_engine_initialization(self):
        """Test that evaluation engine initializes properly."""
        # Given: Default configuration
        # When: Creating evaluation engine
        engine = EvaluationEngine()
        
        # Then: All components should be initialized
        assert engine.tier1_engine is not None
        assert engine.tier2_engine is not None
        assert engine.tier3_engine is not None
        assert engine.scorer is not None
        assert engine.config is not None
    
    @pytest.mark.asyncio
    async def test_complete_evaluation_all_tiers(self, sample_data):
        """Test complete three-tier evaluation."""
        # Given: Evaluation engine and sample data
        engine = EvaluationEngine()
        
        # When: Running complete evaluation
        result = await engine.evaluate_complete(**sample_data)
        
        # Then: Should return complete result
        assert isinstance(result, CompositeEvaluationResult)
        assert result.paper_id == sample_data['paper_id']
        assert result.tier1_results is not None
        assert result.tier2_results is not None
        assert result.tier3_results is not None
        assert 0.0 <= result.composite_score <= 1.0
        assert result.recommendation in ['accept', 'weak_accept', 'weak_reject', 'reject', 'error']
    
    @pytest.mark.asyncio
    async def test_tier1_only_evaluation(self, sample_data):
        """Test evaluation with only Tier 1 enabled."""
        # Given: Engine with only Tier 1 enabled
        engine = EvaluationEngine()
        
        # When: Running evaluation with Tier 1 only
        result = await engine.evaluate_complete(
            **sample_data,
            tiers_enabled=[1]
        )
        
        # Then: Only Tier 1 should have results
        assert result.tier1_results is not None
        assert result.tier2_results is None
        assert result.tier3_results is None
        assert result.composite_score > 0.0  # Should still calculate score
    
    @pytest.mark.asyncio
    async def test_performance_targets(self, sample_data):
        """Test that performance targets are met."""
        # Given: Evaluation engine with performance monitoring
        engine = EvaluationEngine()
        
        # When: Running evaluation
        result = await engine.evaluate_complete(**sample_data)
        
        # Then: Should meet performance targets
        assert result.tier1_duration < 1.0  # <1s for Tier 1
        if result.tier2_duration:
            assert result.tier2_duration < 10.0  # <10s for Tier 2
        if result.tier3_duration:
            assert result.tier3_duration < 15.0  # <15s for Tier 3
        assert result.total_duration < 25.0  # <25s total
    
    def test_synchronous_evaluation(self, sample_data):
        """Test synchronous evaluation wrapper."""
        # Given: Sample data
        # When: Running synchronous evaluation
        result = evaluate_single_paper_sync(**sample_data)
        
        # Then: Should return valid result
        assert isinstance(result, CompositeEvaluationResult)
        assert result.composite_score is not None
        assert 0.0 <= result.composite_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling_fallback(self, sample_data):
        """Test error handling and fallback behavior."""
        # Given: Engine with mocked failing components
        engine = EvaluationEngine()
        
        with patch.object(engine.tier2_engine, 'evaluate_llm_judge', side_effect=Exception("API Error")):
            # When: Running evaluation with Tier 2 failure
            result = await engine.evaluate_complete(**sample_data)
            
            # Then: Should handle gracefully
            assert result.tier1_results is not None  # Tier 1 should still work
            assert result.tier2_results is None or result.tier2_results.fallback_used
            assert result.composite_score > 0.0  # Should still provide score
    
    @pytest.mark.asyncio
    async def test_batch_evaluation(self, sample_data):
        """Test concurrent batch evaluation."""
        # Given: Multiple evaluation requests
        engine = EvaluationEngine()
        
        batch_requests = [
            {**sample_data, 'paper_id': f'batch_paper_{i}'}
            for i in range(3)
        ]
        
        # When: Running batch evaluation
        results = await engine.evaluate_batch(batch_requests, max_concurrent=2)
        
        # Then: Should return results for all requests
        assert len(results) == 3
        assert all(isinstance(r, CompositeEvaluationResult) for r in results)
        assert all(r.paper_id.startswith('batch_paper_') for r in results)
    
    def test_config_integration(self):
        """Test configuration loading and integration."""
        # Given: Custom configuration
        engine = EvaluationEngine()
        
        # When: Accessing configuration
        config = engine.config
        
        # Then: Should load proper configuration
        assert 'tier1_traditional' in config
        assert 'tier2_llm_judge' in config
        assert 'tier3_graph' in config
        assert 'composite_scoring' in config
```

## Development Instructions

### Phase 1: Setup Dependencies (Day 2 Morning)

```bash
# Add to pyproject.toml [dependencies]
torchmetrics = {version = ">=1.4.0", extras = ["text"]}
scikit-learn = ">=1.5.0"
nltk = ">=3.9.0"
textdistance = ">=4.6.0"
networkx = ">=3.0"

# Install dependencies
uv sync
```

### Phase 2: Implementation Order (Days 2-3)

1. **Create data models** (`evaluation_models.py`)
2. **Implement Tier 1** (`traditional_metrics.py`)
3. **Create configuration** (`config_eval.json`)
4. **Implement main engine** (`evaluation_engine.py`)
5. **Add Tier 2** (`llm_judge.py`)
6. **Add Tier 3** (`graph_analysis.py`)
7. **Implement composite scoring** (`composite_scoring.py`)

### Phase 3: Testing & Validation (Days 3-4)

1. **Unit tests** for each tier engine
2. **Integration tests** for complete pipeline
3. **Performance benchmarking** against targets
4. **Real PeerRead data** validation

### Phase 4: Quality Assurance (Days 4-6)

1. **Run `make validate`** before commits
2. **Code review** with `code-reviewer` agent
3. **Documentation updates** in CHANGELOG.md
4. **Production deployment** preparation

## Success Criteria

- [ ] **Performance**: <5s total pipeline latency
- [ ] **Dependencies**: <100MB additional packages
- [ ] **Test Coverage**: >90% for evaluation modules
- [ ] **Real Data**: Validated with PeerRead samples
- [ ] **Error Handling**: Graceful degradation on failures
- [ ] **Configuration**: Externalized in JSON format

This implementation handoff provides complete specifications for developers to build the three-tiered evaluation framework following the established architecture and meeting all performance requirements.