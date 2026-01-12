---
title: Agent Evaluation Metrics Survey
description: Survey of agent evaluation metrics from the landscape analysis, focused on practical implementation for PeerRead multi-agent evaluation
date: 2026-01-12
status: draft
category: technical-analysis
tags:
  - agent-evaluation
  - metrics
  - peerread-evaluation
version: 1.1.0
---
<!-- markdownlint-disable MD024 no-duplicate-heading -->

Comprehensive catalog of evaluation metrics for AI agent systems, with
definitions, use cases, and primary research references for each metric.

## Core Evaluation Metrics

### Text Generation Quality

*See also: [Traditional Metrics Libraries](landscape.md#8-traditional-metrics-libraries) in landscape.md*

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

*See also: [Agent Evaluation & Benchmarking](landscape.md#agent-evaluation--benchmarking) and [Observability & Monitoring Platforms](landscape.md#4-observability--monitoring) in landscape.md*

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

#### Path Convergence

- **Definition**: Ratio of minimum required steps to actual steps taken
- **Use Case**: Measure agent execution efficiency in completing evaluation tasks
- **Calculation**: `minimum_steps / actual_steps`
- **Strengths**: Quantifies workflow efficiency, identifies optimization opportunities
- **Limitations**: Requires determination of optimal path
- **Reference**: [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854)
- **Landscape Reference**: [Arize Phoenix - Path Metrics](landscape.md#llm-application-observability)

#### Tool Call Accuracy

- **Definition**: Percentage of successful tool calls compared to attempted calls
- **Use Case**: Evaluate agent reliability in tool selection and parameter extraction
- **Calculation**: `successful_tool_calls / total_tool_calls`
- **Strengths**: Direct measure of agent competency with tools
- **Limitations**: Requires clear success/failure definitions
- **Reference**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **Landscape Reference**: [Arize Phoenix - LLM-as-a-Judge Templates](landscape.md#llm-application-observability)

#### Behavioral Fingerprint Profile

- **Definition**: Diagnostic assessment revealing agent behavioral characteristics beyond performance metrics
- **Use Case**: Agent identity evaluation, consistency tracking, alignment validation
- **Components**: Personality clustering (ISTJ/ESTJ patterns), semantic robustness, sycophancy detection
- **Strengths**: Captures behavioral patterns, reveals alignment choices
- **Limitations**: Requires diagnostic prompt suite, model-dependent patterns
- **Reference**: Behavioral Fingerprinting of LLMs (Agents4Science 2025)
- **Application**: Inform Tier 4 Self-Assessment for agent identity persistence across interactions

### Multi-Agent Coordination Metrics

*See also: [Graph Analysis & Network Tools](landscape.md#7-graph-analysis--network-tools) and [Agent Frameworks](landscape.md#1-agent-frameworks) in landscape.md*

#### Step Efficiency

- **Definition**: Ratio of productive work steps to total execution steps
- **Use Case**: Identify coordination overhead in multi-agent workflows
- **Calculation**: `productive_steps / total_steps`
- **Strengths**: Measures workflow optimization effectiveness
- **Limitations**: Requires classification of step types
- **Reference**: [Multi-agent coordination in distributed systems](https://link.springer.com/article/10.1007/s10458-013-9235-1)
- **Landscape Reference**: [Arize Phoenix - Path Metrics](landscape.md#llm-application-observability)

#### Centrality Measures

- **Definition**: Graph theory metrics measuring agent importance in
  coordination networks
- **Variants**: Betweenness, closeness, degree centrality
- **Use Case**: Identify coordination bottlenecks and key agents
- **Strengths**: Quantifies structural importance
- **Limitations**: Requires graph construction from interaction logs
- **Reference**: [Networks: An Introduction](https://oxford.universitypressscholarship.com/view/10.1093/acprof:oso/9780199206650.001.0001/acprof-9780199206650)
  (Newman, 2010)
- **Landscape Reference**: [Graph Analysis & Network Tools](landscape.md#7-graph-analysis--network-tools)

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
- **Landscape Reference**: [Agent Frameworks](landscape.md#1-agent-frameworks)

### Production Framework Metrics

Metrics derived from production evaluation frameworks and competition benchmarks

#### Plan Adherence

- **Definition**: Degree to which agent follows its own generated execution plan
- **Use Case**: Detect agents that generate good plans but deviate during execution
- **Calculation**: `planned_steps_executed / total_planned_steps`
- **Strengths**: Separates planning quality from execution discipline
- **Limitations**: Requires plan extraction and step matching
- **Reference**: DeepEval PlanAdherenceMetric
- **Landscape Reference**: [DeepEval Framework](landscape.md#agent-evaluation--benchmarking)

#### Argument Correctness

- **Definition**: Accuracy of arguments passed to tool calls beyond tool selection
- **Use Case**: Detect subtle tool misuse where correct tool is called with wrong parameters
- **Calculation**: `correct_arguments / total_tool_calls`
- **Strengths**: Catches parameter-level errors missed by tool selection metrics
- **Limitations**: Requires ground truth for argument values
- **Reference**: DeepEval ArgumentCorrectnessMetric

#### Handoff Quality

- **Definition**: Effectiveness of context transfer between agents in multi-agent systems
- **Use Case**: Evaluate multi-agent coordination efficiency
- **Calculation**: `successful_handoffs / total_handoffs` with context preservation score
- **Strengths**: Quantifies multi-agent coordination effectiveness
- **Limitations**: Requires handoff event detection and context comparison
- **Reference**: Arize Phoenix Multi-Agent Evaluation
- **Landscape Reference**: [Arize Phoenix](landscape.md#llm-application-observability)

#### Semantic Outcome

- **Definition**: Meaningful task completion beyond surface-level metrics
- **Use Case**: Evaluate if agent achieved the underlying intent, not just literal task
- **Measurement**: LLM-as-Judge assessment of outcome meaningfulness
- **Strengths**: Captures intent fulfillment vs. task completion
- **Limitations**: Requires clear outcome definitions
- **Reference**: LangSmith Multi-turn Evals

#### Evaluator Alignment

- **Definition**: Consistency between different evaluation methods on same outputs
- **Use Case**: Validate evaluation reliability and detect metric drift
- **Calculation**: Correlation coefficient between evaluator scores
- **Strengths**: Ensures evaluation trustworthiness
- **Limitations**: Requires multiple evaluation methods
- **Reference**: Self-Improving LLM Evals (Arize), TEAM-PHI (Agents4Science 2025)
- **Recent Advance**: TEAM-PHI demonstrates multi-LLM evaluator consensus through majority voting matches supervised evaluation without costly expert annotations

#### Fix Rate

- **Definition**: Percentage of issues successfully resolved in long-horizon tasks
- **Use Case**: Measure partial progress in complex multi-step tasks
- **Calculation**: `issues_fixed / total_issues_attempted`
- **Strengths**: Rewards incremental progress, not just full completion
- **Limitations**: Requires issue tracking and resolution verification
- **Reference**: SWE-EVO Benchmark (arXiv:2512.18470)

#### Rubric Alignment

- **Definition**: Degree to which agent output matches structured evaluation criteria
- **Use Case**: Self-grading against predefined quality rubrics
- **Calculation**: Weighted rubric criterion scores
- **Strengths**: Enables reproducible quality assessment
- **Limitations**: Requires rubric design and criterion weighting
- **Reference**: Rubric Rewards for AI Co-Scientists (arXiv:2512.23707)

#### Elicitation Rate

- **Definition**: Percentage of evaluation runs achieving threshold score (≥7/10)
- **Use Case**: Measure behavioral consistency across multiple runs
- **Calculation**: `runs_above_threshold / total_runs`
- **Strengths**: Simple, threshold-based behavioral assessment
- **Limitations**: Requires multiple runs and score threshold definition
- **Reference**: Bloom Framework (Anthropic)
- **Landscape Reference**: [Bloom](further_reading.md#practitioner-resources)

#### Session Continuity

- **Definition**: Quality of state preservation across agent sessions or context windows
- **Use Case**: Evaluate long-running agent performance with context handoffs
- **Measurement**: State reconstruction accuracy after session boundary
- **Strengths**: Critical for production agents with context limits
- **Limitations**: Requires session boundary detection and state comparison
- **Reference**: Anthropic Effective Harnesses Pattern

#### Scope Adherence

- **Definition**: Alignment between planned work scope and actual executed work
- **Use Case**: Detect scope creep or premature completion in agents
- **Calculation**: `overlap(planned_scope, actual_scope) / planned_scope`
- **Strengths**: Identifies planning-execution gaps
- **Limitations**: Requires scope definition and extraction
- **Reference**: Anthropic Effective Harnesses Pattern

#### Verification Coverage

- **Definition**: Completeness of agent self-testing and validation
- **Use Case**: Measure how thoroughly agent verifies its own work
- **Calculation**: `verified_outputs / total_outputs`
- **Strengths**: Quantifies agent reliability and self-correction
- **Limitations**: Requires verification action detection
- **Reference**: Anthropic Effective Harnesses Pattern

### Observability-Based Metrics

*See also: [Observability & Monitoring Platforms](landscape.md#4-observability--monitoring) in landscape.md*

#### Trace Coverage

- **Definition**: Percentage of agent execution paths captured in observability traces
- **Use Case**: Ensure comprehensive monitoring of agent behavior
- **Calculation**: `traced_execution_paths / total_execution_paths`
- **Strengths**: Validates observability completeness
- **Limitations**: Requires trace path definition
- **Reference**: [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/)
- **Landscape Reference**: [AgentNeo - Observability Platform](landscape.md#multi-agent-system-observability)

#### Error Recovery Rate

- **Definition**: Percentage of errors that agents successfully recover from
- **Use Case**: Measure system resilience and self-correction capability
- **Calculation**: `recovered_errors / total_errors`
- **Strengths**: Quantifies system robustness
- **Limitations**: Requires error classification and recovery detection
- **Reference**: [Fault tolerance in distributed systems](https://dl.acm.org/doi/10.1145/98163.98167)
- **Landscape Reference**: [Browser Use - Self-Correcting Architecture](landscape.md#ai-browser-automation--computer-use)

#### Memory Utilization Efficiency

- **Definition**: Ratio of relevant retrieved memory to total memory accessed
- **Use Case**: Optimize agent memory systems and context management
- **Calculation**: `relevant_memory_retrieved / total_memory_accessed`
- **Strengths**: Measures memory system effectiveness
- **Limitations**: Requires relevance assessment
- **Reference**: [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)
- **Landscape Reference**: [Letta - Advanced Memory Architecture](landscape.md#1-agent-frameworks)

### Security & Safety Metrics

*See also: [AI Model Testing & Validation Platforms](landscape.md#ai-model-testing--validation-platforms) in landscape.md*

#### Hallucination Rate

- **Definition**: Percentage of generated content not supported by source material
- **Use Case**: Ensure factual accuracy in academic review generation
- **Calculation**: `hallucinated_statements / total_statements`
- **Strengths**: Critical for academic integrity
- **Limitations**: Requires ground truth verification
- **Reference**: [Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629)
- **Landscape Reference**: [Patronus AI - Hallucination Detection](landscape.md#ai-model-testing--validation-platforms)

#### Bias Detection Score

- **Definition**: Quantified measurement of bias in agent outputs across demographic groups
- **Use Case**: Ensure fair evaluation across diverse academic content
- **Calculation**: Statistical variance in performance across protected attributes
- **Strengths**: Promotes fair and equitable agent behavior
- **Limitations**: Requires demographic data and bias definitions
- **Reference**: [Bias in AI Systems](https://arxiv.org/abs/1909.01326)
- **Landscape Reference**: [Patronus AI - Bias Assessment](landscape.md#ai-model-testing--validation-platforms)

#### Prompt Injection Resistance

- **Definition**: Ability to maintain intended behavior despite malicious input attempts
- **Use Case**: Prevent manipulation of academic evaluation processes
- **Measurement**: Success rate against standardized injection attacks
- **Strengths**: Essential for production security
- **Limitations**: Requires comprehensive attack vectors
- **Reference**: [Prompt injection attacks against large language models](https://arxiv.org/abs/2302.12173)
- **Landscape Reference**: [Giskard - Security Testing](landscape.md#ai-model-testing--validation-platforms)

#### LLM Evaluator Vulnerability

- **Definition**: Susceptibility of LLM-based evaluators to manipulation strategies
- **Use Case**: Validate robustness of LLM-as-Judge evaluation tier
- **Attack Vectors**: TooGoodGains (exaggerating metrics), BaselineSelect (cherry-picking), StatTheater (statistical facades), CoherencePolish (presentation quality), ProofGap (hiding oversights)
- **Observed Rate**: 67-82% acceptance rates for manipulated content
- **Critical Issue**: Concern-acceptance conflict where reviewers flag issues yet assign acceptance scores
- **Strengths**: Identifies critical LLM judge vulnerabilities
- **Limitations**: Requires adversarial testing framework
- **Reference**: BadScientist (Agents4Science 2025)
- **Mitigation**: Implement adversarial robustness validation and meta-evaluation to detect manipulation

## Implementation Frameworks

### Evaluation Platform Integration

*For comprehensive implementation guidance, see [Agent Evaluation & Benchmarking](landscape.md#agent-evaluation--benchmarking) in landscape.md*

- **AutoGenBench**: Docker-isolated evaluation with benchmark performance metrics
- **Swarms Agent Evaluation**: Continuous monitoring with real-time performance tracking  
- **DeepEval**: 30+ LLM-as-a-judge metrics with pytest integration
- **Braintrust Agent Evaluation**: Architecture-specific assessment with custom scorers
- **Google ADK Evaluation**: Trajectory analysis with multi-turn conversation testing

### Observability Tool Integration

*For detailed technical analysis, see [Observability & Monitoring Platforms](landscape.md#4-observability--monitoring) in landscape.md*

- **AgentNeo**: Decorator-based tracing with SQLite storage
- **Comet Opik**: OpenTelemetry-compatible spans with local deployment
- **Langfuse**: Comprehensive prompt management with evaluation integration
- **Arize Phoenix**: Path convergence metrics with LLM-as-a-judge templates
- **TruLens**: RAG Triad metrics with multi-step workflow assessment

### Graph Analysis Integration

*For network analysis capabilities, see [Graph Analysis & Network Tools](landscape.md#7-graph-analysis--network-tools) in landscape.md*

- **NetworkX**: Centrality measures and coordination pattern analysis
- **LangGraph**: Stateful agent workflow orchestration with conditional logic
- **PyTorch Geometric**: Graph neural networks for agent behavior modeling
- **NetworKit**: High-performance graph analysis with parallel processing

## Additional Resources

[Framework implementations and practical guidance on using these metrics](landscape.md#agent-evaluation--benchmarking)
