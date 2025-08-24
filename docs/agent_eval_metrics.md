---
title: Agent Evaluation Metrics Survey
description: Survey of agent evaluation metrics from the landscape analysis, focused on practical implementation for PeerRead multi-agent evaluation
date: 2025-08-24
status: draft
category: technical-analysis
tags:
  - agent-evaluation
  - metrics
  - peerread-evaluation
author: AI Research Team
version: 0.1.0
---

Comprehensive catalog of evaluation metrics for AI agent systems, with
definitions, use cases, and primary research references for each metric.

## Core Evaluation Metrics

### Text Generation Quality

*See also: [Traditional Metrics Libraries](landscape.md#traditional-metrics-libraries) in landscape.md*

#### BLEU (Bilingual Evaluation Understudy)

- **Definition**: N-gram precision metric measuring overlap between
  generated and reference text
- **Use Case**: Evaluate generated review similarity to reference reviews
- **Strengths**: Fast computation, established baseline
- **Limitations**: Ignores semantic meaning, favors exact matches
- **Reference**: [BLEU: a Method for Automatic Evaluation of Machine Translation](https://aclanthology.org/P02-1040/)

#### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

- **Definition**: Recall-based metric measuring content overlap using
  n-grams and longest common subsequences
- **Use Case**: Assess coverage of key paper concepts in generated reviews
- **Strengths**: Captures content coverage, multiple variants (ROUGE-1,
  ROUGE-2, ROUGE-L)
- **Limitations**: Surface-level matching, no semantic understanding
- **Reference**: [ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013/)

#### BERTScore

- **Definition**: Contextual embedding-based similarity using pre-trained
  BERT models
- **Use Case**: Measure semantic similarity beyond lexical matching
- **Strengths**: Captures semantic meaning, correlates with human judgment
- **Limitations**: Computationally expensive, model-dependent
- **Reference**: [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675)

#### Semantic Similarity (Cosine)

- **Definition**: Vector similarity between sentence embeddings using
  cosine distance
- **Use Case**: Compare semantic content of generated vs reference reviews
- **Strengths**: Fast, captures semantic relationships
- **Limitations**: Single similarity score, no aspect-specific assessment
- **Reference**: [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084)

### LLM-as-a-Judge Quality Assessment

*See also: [Agent Evaluation & Benchmarking](landscape.md#agent-evaluation--benchmarking) and [LLM Evaluation & Benchmarking](landscape.md#llm-evaluation--benchmarking) in landscape.md*

#### Answer Relevancy

- **Definition**: LLM assessment of how well generated content addresses
  the input query/paper
- **Use Case**: Evaluate if generated reviews address key paper aspects
- **Strengths**: Contextual understanding, query-specific evaluation
- **Limitations**: LLM bias, requires careful prompt engineering
- **Reference**: [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)

#### Faithfulness

- **Definition**: Degree to which generated content remains factually
  consistent with source material
- **Use Case**: Ensure generated reviews don't hallucinate paper content
- **Strengths**: Detects factual inconsistencies, source-grounded
- **Limitations**: Requires clear source-target relationships
- **Reference**: [TRUE: Re-evaluating Factual Consistency Evaluation](https://arxiv.org/abs/2204.04991)

#### Hallucination Detection

- **Definition**: Identification of generated content not supported by
  source documents
- **Use Case**: Detect fabricated claims about paper methodology/results
- **Strengths**: Critical for academic accuracy, prevents misinformation
- **Limitations**: Difficult to define ground truth, context-dependent
- **Reference**: [Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629)

#### Context Relevance

- **Definition**: Assessment of how well retrieved/provided context relates
  to the query
- **Use Case**: Evaluate if paper sections support generated review claims
- **Strengths**: RAG-specific, improves retrieval quality
- **Limitations**: Requires clear context-query relationships
- **Reference**: [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- **Landscape Reference**: [RAG System Evaluation](landscape.md#rag-system-evaluation)

### Agent Performance Metrics

*See also: [Agent Evaluation & Benchmarking](landscape.md#agent-evaluation--benchmarking) and [Observability & Monitoring Platforms](landscape.md#observability--monitoring-platforms) in landscape.md*

#### Tool Selection Accuracy

- **Definition**: Percentage of correct tool choices for given tasks
- **Use Case**: Assess agent ability to select appropriate research tools
- **Measurement**: `correct_selections / total_selections`
- **Strengths**: Directly measures decision-making quality
- **Limitations**: Requires clear correct/incorrect labels
- **Reference**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

#### Path Convergence

- **Definition**: Ratio of minimum required steps to actual steps taken
- **Use Case**: Measure agent efficiency in task completion
- **Calculation**: `minimum_steps / actual_steps`
- **Strengths**: Quantifies execution efficiency
- **Limitations**: Requires optimal path knowledge
- **Reference**: [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) (efficiency metrics for web agents)

#### Response Time

- **Definition**: End-to-end processing time from input to output
- **Use Case**: Evaluate system performance for real-time applications
- **Measurement**: Wall clock time in seconds/milliseconds
- **Strengths**: Simple, directly impacts user experience
- **Limitations**: Hardware-dependent, varies with load
- **Reference**: [The Computer Systems Performance Handbook](https://dl.acm.org/doi/book/10.5555/280288) (standard performance measurement)

#### Token Usage Efficiency

- **Definition**: Ratio of useful output tokens to total consumed tokens
- **Use Case**: Optimize LLM API costs and computational efficiency
- **Calculation**: `output_tokens / (input_tokens + output_tokens)`
- **Strengths**: Cost optimization, resource management
- **Limitations**: Doesn't account for output quality
- **Reference**: [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) (RLHF efficiency considerations)

### Multi-Agent Coordination Metrics

*See also: [Graph Analysis & Network Tools](landscape.md#graph-analysis--network-tools) and [Agentic System Frameworks](landscape.md#agentic-system-frameworks) in landscape.md*

#### Centrality Measures

- **Definition**: Graph theory metrics measuring agent importance in
  coordination networks
- **Variants**: Betweenness, closeness, degree centrality
- **Use Case**: Identify coordination bottlenecks and key agents
- **Strengths**: Quantifies structural importance
- **Limitations**: Requires graph construction from interaction logs
- **Reference**: [Networks: An Introduction](https://oxford.universitypressscholarship.com/view/10.1093/acprof:oso/9780199206650.001.0001/acprof-9780199206650)
  (Newman, 2010)
- **Landscape Reference**: [Graph Analysis & Network Tools](landscape.md#graph-analysis--network-tools)

#### Communication Overhead

- **Definition**: Ratio of coordination messages to productive work messages
- **Use Case**: Optimize agent communication efficiency
- **Calculation**: `coordination_messages / total_messages`
- **Strengths**: Measures coordination cost
- **Limitations**: Requires message classification
- **Reference**: Coulouris et al., "Distributed Systems: Concepts and Design"
  (5th Edition, 2012)

#### Task Distribution Balance

- **Definition**: Measure of workload evenness across agents using
  statistical variance
- **Use Case**: Ensure fair load balancing in multi-agent systems
- **Calculation**: `1 - std_dev(agent_tasks) / mean(agent_tasks)`
- **Strengths**: Quantifies load balancing effectiveness
- **Limitations**: Doesn't account for task complexity differences
- **Reference**: [Multi-agent coordination in distributed systems](https://link.springer.com/article/10.1007/s10458-013-9235-1) (coordination metrics)
- **Landscape Reference**: [Agentic System Frameworks](landscape.md#agentic-system-frameworks)

## Additional Resources

[Framework implementations and practical guidance on using these metrics](landscape.md#agent-evaluation--benchmarking)
