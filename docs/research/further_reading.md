---
title: Further Reading - Research Papers
description: Comprehensive curated list of research papers and academic resources for AI agent evaluation with thematic tagging, cross-references, and clustering
category: research
arxiv_categories: cs.AI, cs.MA, cs.CL, cs.LG, cs.SE, cs.CR
arxiv_search_url: "http://export.arxiv.org/api/query?search_query=(all:agent+OR+all:agentic+OR+all:multi-agent)&sortBy=submittedDate&sortOrder=descending"
tags: [agentic-ai, evaluation, benchmarking, multi-agent-systems, safety, architecture, tool-use, planning, scientific-discovery, code-generation]
features:
  - chronological-organization
  - thematic-tagging
  - cross-references
  - relationship-explanations
  - clustering-by-themes
papers_count: 260+
coverage_period: 2020-10 to 2026-02
created: 2025-08-24
updated: 2026-02-15
version: 3.2.0
---

## Overview

This document provides a comprehensive, curated collection of research papers on agentic AI systems, evaluation frameworks, and related topics. Papers are organized chronologically to show research evolution while featuring thematic tagging and cross-references for efficient navigation.

### Usage

- **Browse chronologically** by year/month to track research evolution
- **Filter by tags** like `[EVAL]`, `[SAFETY]`, `[MAS]` to find papers by topic
- **Follow cross-references** with explanations to discover related work
- **Use thematic clusters** at the end for quick topic-based navigation
- **Search arXiv IDs** to quickly locate specific papers

### Document Features

- 260+ papers covering 2020-2026 research
- 14 thematic tags for categorization
- Cross-references with relationship explanations
- Chronological organization preserving research timeline
- Thematic clustering summary for quick navigation

### Related Documents

- [Research Integration Analysis](research_integration_analysis.md) - Analysis of research trends and integration patterns across these papers

## Paper Tags and Categories Legend

- `[ARCH]` - Architecture and system design
- `[AUTO]` - Automation and workflow
- `[BENCH]` - Benchmarking and performance measurement
- `[CODE]` - Code generation and programming
- `[COMP]` - Compliance and observability
- `[EVAL]` - Evaluation frameworks and benchmarks
- `[MAS]` - Multi-agent systems
- `[MEM]` - Memory mechanisms
- `[PLAN]` - Planning and reasoning
- `[SAFETY]` - Safety, governance, and risk management
- `[SCI]` - Scientific discovery and research
- `[SPEC]` - Domain-specific applications
- `[SURVEY]` - Survey and review papers
- `[TOOL]` - Tool use and integration

## Thematic Clusters

**Evaluation & Benchmarking** `[EVAL]` `[BENCH]`:

- General benchmarks: 2308.03688 (AgentBench), 2404.06411 (AgentQuest), 2401.13178 (AgentBoard), 2311.12983 (GAIA)
- Web agents: 2307.13854 (WebArena), 2401.13649 (VisualWebArena), 2410.06703 (ST-WebAgentBench), 2404.07972 (OSWorld), 2412.05467 (BrowserGym), 2504.01382 (Online-Mind2Web), 2207.01206 (WebShop)
- Tool evaluation: 2307.16789 (ToolLLM), 2310.03128 (MetaTool), 2406.12045 (τ-bench), 2506.07982 (τ²-bench), 2304.08244 (API-Bank EMNLP 2023), BFCL
- Scientific: 2407.13168 (SciCode), 2409.11363 (CORE-Bench)
- Enterprise: 2509.10769 (AgentArch), 2511.14136 (CLEAR framework), 2412.14161 (TheAgentCompany), 2411.07763 (Spider 2.0), 2411.02305 (CRMArena), 2508.00828 (Finance), 2501.14654 (MedAgentBench)
- Code/SE: 2407.18901 (AppWorld), SWE-bench verified, 2404.10952 (USACO), 2507.05558 (Smart Contract)
- Safety/Security: 2504.14064 (DoomArena), 2504.18575 (WASP), 2506.02548 (CyberGym)
- Gaming/Embodied: 2407.13943 (Werewolf), 2310.08367 (Minecraft), 2010.03768 (ALFWorld), 2407.18416 (PersonaGym)
- Multi-agent: 2503.01935 (MultiAgentBench), 2512.08296 (scaling agent systems), 2507.05178 (CREW)
- Safety: 2402.05044 (SALAD-Bench ACL 2024), 2412.14470 (Agent-SafetyBench), 2412.13178 (SafeAgentBench), 2410.09024 (AgentHarm ICLR 2025)
- Recent 2025-2026: 2510.02271 (InfoMosaic-Bench), 2510.02190 (Deep Research), 2510.01670 (BLIND-ACT), 2512.12791 (assessment framework), TEAM-PHI (de-identification), Behavioral Fingerprinting (LLM profiles), Strategic Reasoning (digital twin)
- Observability/Production: 2601.00481 (MAESTRO), 2602.10133 (AgentTrace), 2512.04123 (measuring agents), 2601.19583 (architecture-aware metrics), 2512.18311 (monitorability)
- Surveys: 2503.16416 (evaluation survey), 2507.21504 (LLM agents survey), 2411.13768 (evaluation-driven), 2501.11067 (IntellAgent)

**Architecture & System Design** `[ARCH]`:

- Foundation: 2308.11432 (foundational survey), 2404.11584 (architecture landscape), 2510.09244 (fundamentals)
- Frameworks: 2508.10146 (agentic AI frameworks), 2501.10114 (infrastructure), 2601.01743 (AI agent systems), 2602.10479 (goal-directed systems)
- Surveys: 2510.25445 (comprehensive survey), 2503.23037 (agentic LLMs), 2506.01438 (architectural frameworks)
- Governance: 2508.03858 (governance protocol), 2503.00237 (systems theory)

**Safety & Risk Management** `[SAFETY]`:

- Constitutional AI: 2212.08073 (foundational), 2406.07814 (collective), 2501.17112 (inverse)
- Core frameworks: 2302.10329 (harms analysis), 2506.04133 (TRiSM), 2408.02205 (guardrails), 2507.06134 (OpenAgentSafety), MITRE ATLAS, OWASP MAESTRO
- Standards: NIST AI RMF 1.0, ISO/IEC 42001 (AI management system), ISO/IEC 23894 (AI risk management)
- Security: 2510.23883 (agentic AI security), 2512.06659 (cybersecurity evolution), BadScientist (AI publishing vulnerabilities)
- Safety benchmarks: 2402.05044 (SALAD-Bench ACL 2024), 2412.14470 (Agent-SafetyBench), 2412.13178 (SafeAgentBench), 2410.09024 (AgentHarm ICLR 2025)
- Monitoring: 2507.11473 (CoT monitorability), 2512.18311 (monitoring monitorability), 2512.20798 (constraint violations), 2601.00911 (privacy-preserving)
- Reports: 2510.13653 (AI safety first update), 2511.19863 (AI safety second update)
- Recent 2025: 2510.02286 (adversarial dialogue), 2510.01586 (AdvEvo-MARL), 2510.01569 (InvThink), 2510.02204 (reasoning-execution gaps)
- Multi-agent: 2503.13657 (MAS failures), 2402.04247 (safeguarding over autonomy), Hierarchical Delegated Oversight (scalable alignment)
- Self-correction: Architectural Immune System (materials discovery)

**Tool Use & Integration** `[TOOL]`:

- Benchmarks: 2307.16789 (ToolLLM), 2310.03128 (MetaTool), 2406.12045 (τ-bench), 2304.08244 (API-Bank EMNLP 2023), BFCL
- Surveys: 2405.17935 (tool learning), 2404.11584 (tool calling architectures)
- Augmentation: 2506.04625 (Tool-MVR meta-verification), 2511.18194 (agent-as-graph), 2512.16214 (PDE-Agent)
- MCP applications: 2512.03955 (Blocksworld MCP), 2510.02139 (BioinfoMCP), 2509.06917 (Paper2Agent)
- Recent 2025: 2510.01524 (WALT web agents), 2510.01179 (TOUCAN datasets), 2510.02271 (InfoMosaic-Bench), 2512.03420 (HarnessAgent)
- Applications: 2410.22457 (tool integration), 2410.09713 (agentic IR)

**Multi-Agent Systems** `[MAS]`:

- Collaboration: 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms), 2512.20845 (MAR reflexion)
- Benchmarks: 2503.01935 (MultiAgentBench), 2512.08296 (scaling agent systems), 2505.12371 (MedAgentBoard), Job Marketplaces (OpenReview)
- Analysis: 2503.13657 (failure analysis), 2505.21298 (LLMs miss the mark), 2511.02303 (lazy to deliberation)
- Applications: 2507.02097 (recommender systems), 2512.20618 (LongVideoAgent), 2512.16214 (PDE-Agent), Echo (pharmacovigilance), Drug Discovery (Alzheimer's), PsySpace (space missions), Evolutionary Boids (agent societies)
- Oversight: Hierarchical Delegated Oversight (scalable alignment)
- Observability: 2602.10133 (AgentTrace), 2601.00481 (MAESTRO)
- Recent 2026: 2601.03328 (design patterns evaluation), 2602.10479 (goal-directed systems)

**Planning & Reasoning** `[PLAN]`:

- ReAct family: 2210.03629 (ReAct), 2411.00927 (ReSpAct), 2310.04406 (LATS)
- Core: 2402.02716 (planning survey), 2508.03682 (self-questioning), 2512.14474 (model-first reasoning)
- Training: 2508.00344 (PilotRL global planning), 2510.01833 (plan-then-action), 2511.02303 (lazy to deliberation)
- Multi-agent: 2512.20845 (MAR), 2512.08296 (scaling agent systems)
- Applications: 2410.22457 (task decomposition), 2404.11584 (reasoning architectures), 2512.03955 (Blocksworld MCP)

**Scientific Discovery** `[SCI]`:

- Research agents: 2506.18096 (deep research), 2508.00414 (cognitive kernel), 2509.06917 (Paper2Agent)
- Discovery: 2408.06292 (AI scientist), 2503.08979 (scientific discovery survey), Beyond Adam (symbolic optimization), Architectural Immune System (self-correcting)
- Domain applications: AlphaGenome (genomics), Drug Discovery (multi-target Alzheimer's)

**Code Generation** `[CODE]`:

- Surveys: 2508.00083 (comprehensive survey), 2508.11126 (agentic programming), 2511.18538 (code foundation models)
- SE 3.0: 2507.15003 (AI teammates), 2510.21413 (context engineering), 2512.14012 (professional developers)
- Automation: 2505.18646 (SEW self-evolving), 2504.17192 (Paper2Code), 2510.09721 (software engineering benchmarks)
- Explanations: 2507.22414 (symbolic explanations), 2402.01030 (executable actions)
- Recent 2025: 2510.02185 (FalseCrashReducer), 2510.01379 (multi-LLM orchestration), 2510.01003 (repository memory), 2512.03420 (HarnessAgent)
- Applications: 2506.13131 (AlphaEvolve), 2410.14393 (debug agents)

**Memory Systems** `[MEM]`:

- Surveys: 2512.13564 (memory in AI agents), 2512.23343 (AI meets brain), 2404.13501 (memory mechanisms)
- Frameworks: 2601.03236 (MAGMA multi-graph), 2601.01885 (agentic memory), 2502.12110 (A-Mem)
- Learning: 2512.18950 (MACLA hierarchical procedural), 2511.18423 (GAM deep research), 2509.25250 (long-running agents)
- Applications: 2510.01003 (repository memory), 2508.11120 (marketing MAS), 2510.11290 (AI-Agent School dual memory)

**Self-Improvement & Reflection** `[AUTO]`:

- Self-reflection: 2303.11366 (Reflexion foundation), 2405.06682 (self-reflection effects), 2512.20845 (MAR)
- Recursive improvement: 2407.18219 (recursive introspection), 2410.04444 (Gödel Agent)
- Training approaches: 2406.01495 (Re-ReST), 2508.15805 (ALAS autonomous learning), 2508.00344 (PilotRL)
- Workflows: 2505.18646 (SEW self-evolving), 2505.22967 (MermaidFlow), 2506.04625 (Tool-MVR)
- Human guidance: 2507.17131 (HITL self-improvement), 2508.07407 (self-evolving survey)

## Future Research Areas

The following areas represent emerging or under-explored topics in agentic AI research that warrant additional investigation:

**Advanced Multi-Modal Agents** - Integration of vision, audio, and text processing for comprehensive environmental understanding beyond current multi-modal benchmarks.

**Long-Term Memory & Retrieval** - Advanced memory architectures for persistent knowledge retention and contextual recall across extended agent interactions.

**Human-AI Collaboration** - Frameworks for seamless human-agent teamwork, including explanation mechanisms, trust calibration, and collaborative decision-making.

**Adversarial Robustness** - Agent resilience against adversarial attacks, prompt injection, and manipulation attempts in production environments.

**Automated Code Generation Agents** - Next-generation coding assistants with advanced debugging, testing, and architectural design capabilities.

**Edge & Resource-Constrained Deployment** - Efficient agent architectures for mobile devices, IoT systems, and bandwidth-limited environments.

**Governance & Policy Implementation** - Practical frameworks for regulatory compliance, audit trails, and policy enforcement in agent systems.

**Long-Term Autonomy & Reliability** - Systems capable of sustained autonomous operation with minimal human intervention over extended periods.

**Domain Transfer & Generalization** - Techniques for rapid agent adaptation across different domains with minimal retraining or fine-tuning.

### Priority Research Focus

Based on current gaps and transformative potential, three areas warrant immediate attention:

**1. Compositional Self-Improvement** - Moving beyond single-agent reflection to systems that can redesign their own architectures, create specialized sub-agents, and evolve coordination protocols. This represents the next leap from current self-reflection work toward truly recursive intelligence.

**2. Persistent Contextual Memory** - Current agents lack genuine episodic memory across sessions. Developing memory systems that maintain context, relationships, and learned preferences over months or years is critical for practical deployment and user trust.

**3. Robust Human-Agent Teaming** - Most current work treats humans as either supervisors or users. Research on agents as true collaborators—with theory-of-mind, explanation capabilities, and dynamic role adaptation—is essential for high-stakes domains like healthcare, research, and decision-making.

## 2026-02

- [[2602.10479] From Prompt-Response to Goal-Directed Systems: The Evolution of Agentic AI Software Architecture](https://arxiv.org/abs/2602.10479) `[ARCH]` `[MAS]` `[SURVEY]` `cs.SE` `cs.AI`
  - Reference architecture for production-grade LLM agents, taxonomy of multi-agent topologies with failure modes, enterprise hardening checklist covering governance, observability, and reproducibility
  - Cross-ref: 2601.01743 (agent system architectures), 2601.03328 (MAS design patterns), 2508.10146 (agentic frameworks)
- [[2602.10133] AgentTrace: A Structured Logging Framework for Agent System Observability](https://arxiv.org/abs/2602.10133) `[COMP]` `[EVAL]` `[MAS]` `cs.AI` `cs.SE`
  - First open standard for structured agent logging via schema-based protocol spanning cognitive, operational, and contextual traces; enables fine-grained debugging, failure attribution, and transparent governance
  - Cross-ref: 2601.00481 (MAESTRO evaluation suite), 2512.04123 (measuring agents in production), 2508.02121 (AgentOps survey)
- [[2601.19583] Toward Architecture-Aware Evaluation Metrics for LLM Agents](https://arxiv.org/abs/2601.19583) `[EVAL]` `[ARCH]` `cs.SE` `cs.AI`
  - Links agent architectural components (planners, memory, tool routers) to observable behaviors and appropriate evaluation metrics; enables targeted and actionable evaluation
  - Cross-ref: 2512.12791 (assessment framework), 2503.16416 (evaluation survey), 2507.21504 (LLM agents survey)
- [[2601.00481] MAESTRO: Multi-Agent Evaluation Suite for Testing, Reliability, and Observability](https://arxiv.org/abs/2601.00481) `[EVAL]` `[MAS]` `[BENCH]` `[COMP]` `cs.MA` `cs.AI`
  - Standardizes MAS configuration and exports framework-agnostic execution traces with system-level signals (latency, cost, failures); 12 representative MAS across popular frameworks show architecture is the dominant driver of resource profiles and cost-latency-accuracy trade-offs
  - Cross-ref: 2602.10133 (AgentTrace), 2512.04123 (measuring agents), 2508.02121 (AgentOps survey)
- [[2512.18311] Monitoring Monitorability](https://arxiv.org/abs/2512.18311) `[SAFETY]` `[EVAL]` `[COMP]` `cs.AI` `cs.LG`
  - Proposes monitorability metric and evaluation archetypes (intervention, process, outcome-property) for chain-of-thought monitoring; finds longer CoTs are more monitorable and smaller models at higher reasoning effort can yield higher monitorability
  - Cross-ref: 2512.12791 (assessment framework), 2601.01743 (agent architectures survey)
- [[2512.04123] Measuring Agents in Production](https://arxiv.org/abs/2512.04123) `[EVAL]` `[COMP]` `cs.SE` `cs.AI`
  - Interview-based study (306 survey responses, 20 in-depth interviews across 26 domains) arguing agent evaluation must move beyond correctness metrics to assess reliability under varying autonomy levels
  - Cross-ref: 2512.12791 (assessment framework), 2601.00481 (MAESTRO), 2503.16416 (evaluation survey)

## 2026-01

- [[2601.03328] LLM-Enabled Multi-Agent Systems: Empirical Evaluation and Insights into Emerging Design Patterns & Paradigms](https://arxiv.org/abs/2601.03328) `[MAS]` `[EVAL]` `[ARCH]` `cs.MA` `cs.AI`
  - Empirical evaluation of LLM-based multi-agent systems with analysis of emerging design patterns and architectural paradigms
  - Cross-ref: 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms), 2506.01438 (architectural frameworks)
- [[2601.03236] MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents](https://arxiv.org/abs/2601.03236) `[MEM]` `[ARCH]` `cs.AI` `cs.LG`
  - Multi-graph memory architecture representing memories across semantic, temporal, causal, and entity graphs with hierarchical intent-aware querying
  - Cross-ref: 2512.13564 (memory systems survey), 2601.01885 (agentic memory), 2404.13501 (memory mechanisms)
- [[2601.01885] Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents](https://arxiv.org/abs/2601.01885) `[MEM]` `[ARCH]` `cs.AI` `cs.CL`
  - Unified framework integrating long-term and short-term memory management as tool-based actions in agent policy
  - Cross-ref: 2512.13564 (memory systems), 2404.13501 (memory survey), 2511.18423 (GAM)
- [[2601.01743] AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/abs/2601.01743) `[ARCH]` `[SAFETY]` `[SURVEY]` `cs.AI`
  - Comprehensive survey of AI agent system architectures with focus on tool-centric safety risks and security challenges
  - Cross-ref: 2508.10146 (agentic frameworks), 2510.23883 (agentic AI security), 2506.04133 (TRiSM)
- [[2601.00911] Device-Native Autonomous Agents for Privacy-Preserving Negotiations](https://arxiv.org/abs/2601.00911) `[SAFETY]` `[SPEC]` `cs.AI` `cs.CR`
  - Framework for privacy-preserving autonomous agent negotiations running on local devices
  - Cross-ref: 2510.01815 (human-AI teaming), 2503.06416 (negotiation competition)

## 2025-12

- [[2512.23343] AI Meets Brain: Memory Systems from Cognitive Neuroscience to Autonomous Agents](https://arxiv.org/abs/2512.23343) `[MEM]` `[SURVEY]` `[ARCH]` `cs.AI` `cs.HC`
  - Unified survey bridging cognitive neuroscience and AI agent memory systems with agentic perspective on external memory design
  - Cross-ref: 2512.13564 (memory age survey), 2404.13501 (memory mechanisms), 2601.03236 (MAGMA)
- [[2512.20845] MAR: Multi-Agent Reflexion Improves Reasoning Abilities in LLMs](https://arxiv.org/abs/2512.20845) `[MAS]` `[PLAN]` `[AUTO]` `cs.AI` `cs.CL`
  - Multi-agent extension of Reflexion with diverse reasoning personas and judge model for unified reflection synthesis
  - Cross-ref: 2303.11366 (Reflexion foundation), 2405.06682 (self-reflection effects), 2501.06322 (collaboration mechanisms)
- [[2512.20798] A Benchmark for Evaluating Outcome-Driven Constraint Violations in Autonomous AI Agents](https://arxiv.org/abs/2512.20798) `[BENCH]` `[SAFETY]` `[EVAL]` `cs.AI` `cs.CR`
  - Benchmark evaluating agents that independently take unethical or dangerous actions toward KPI achievement
  - Cross-ref: 2510.01670 (BLIND-ACT), 2507.06134 (OpenAgentSafety), 2506.04133 (TRiSM)
- [[2512.20618] LongVideoAgent: Multi-Agent Reasoning with Long Videos](https://arxiv.org/abs/2512.20618) `[MAS]` `[SPEC]` `cs.CV` `cs.AI`
  - Multi-agent framework for reasoning over long video content with distributed processing
  - Cross-ref: 2508.10494 (MAGUS multimodal), 2501.06322 (collaboration mechanisms)
- [[2512.18950] Learning Hierarchical Procedural Memory for LLM Agents through Bayesian Selection and Contrastive Refinement](https://arxiv.org/abs/2512.18950) `[MEM]` `[AUTO]` `cs.AI` `cs.LG`
  - MACLA system constructing hierarchical procedural memory 2,800× faster than parameter-training baselines
  - Accepted at AAMAS 2026
  - Cross-ref: 2512.13564 (memory systems), 2511.18423 (GAM), 2404.13501 (memory survey)
- [[2512.16214] PDE-Agent: A toolchain-augmented multi-agent framework for PDE solving](https://arxiv.org/abs/2512.16214) `[MAS]` `[TOOL]` `[SPEC]` `cs.AI` `cs.CE`
  - First toolchain-augmented multi-agent framework for automated PDE solving from natural language descriptions
  - Cross-ref: 2511.18194 (agent-as-graph), 2405.17935 (tool learning), 2501.06322 (collaboration)
- [[2512.14474] Model-First Reasoning LLM Agents: Reducing Hallucinations through Explicit Problem Modeling](https://arxiv.org/abs/2512.14474) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - Two-phase paradigm where LLM constructs explicit problem model before solution planning, reducing constraint violations
  - Cross-ref: 2210.03629 (ReAct), 2402.02716 (planning survey), 2510.01833 (plan-then-action)
- [[2512.14012] Professional Software Developers Don't Vibe, They Control](https://arxiv.org/abs/2512.14012) `[CODE]` `[SPEC]` `cs.SE` `cs.AI`
  - Analysis of professional developer requirements for AI coding agents emphasizing control over automation
  - Cross-ref: 2508.00083 (code generation survey), 2507.15003 (SE 3.0)
- [[2512.13564] Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) `[MEM]` `[SURVEY]` `cs.AI` `cs.CL`
  - Comprehensive survey of memory as core capability for foundation model-based agents addressing field fragmentation
  - Cross-ref: 2404.13501 (memory mechanisms survey), 2512.23343 (neuroscience perspective), 2601.01885 (agentic memory)
- [[2512.23707] Training AI Co-Scientists Using Rubric Rewards](https://arxiv.org/abs/2512.23707) `[SCI]` `[AUTO]` `[EVAL]` `cs.AI` `cs.CL`
  - RL training for research plan generation with self-grading rubrics; 70% expert preference, cross-domain validation
  - Cross-ref: 2303.11366 (Reflexion), 2506.18096 (deep research agents), 2508.00414 (cognitive kernel)
- [[2512.18470] SWE-EVO: Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios](https://arxiv.org/abs/2512.18470) `[BENCH]` `[CODE]` `[EVAL]` `cs.SE` `cs.AI`
  - Long-horizon evolution benchmark; 48 tasks, avg 21 files, 874 tests; introduces Fix Rate metric for partial progress
  - Cross-ref: 2508.00083 (code generation survey), 2507.15003 (SE 3.0), 2512.14012 (professional developers)
- [[2512.12791] Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems](https://arxiv.org/abs/2512.12791) `[EVAL]` `[ARCH]` `[SAFETY]` `cs.AI` `cs.SE`
  - Assessment framework across four pillars (LLM, Memory, Tools, Environment) with static and dynamic analysis phases
  - Cross-ref: 2511.14136 (CLEAR framework), 2503.16416 (evaluation survey), 2506.04133 (TRiSM)
- [[2512.10398] Confucius Code Agent: Scalable Agent Scaffolding for Real-World Codebases](https://arxiv.org/abs/2512.10398) `[CODE]` `[ARCH]` `cs.SE` `cs.AI`
  - Hierarchical working memory + persistent note-taking for large codebases; 54.3% on SWE-Bench-Pro
  - Cross-ref: 2512.18470 (SWE-EVO), 2512.13564 (memory systems), 2508.00083 (code generation)
- [[2512.08296] Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) `[MAS]` `[BENCH]` `[ARCH]` `cs.AI` `cs.MA`
  - Controlled evaluation of five agent architectures across 180 configurations spanning diverse benchmarks
  - Cross-ref: 2507.05178 (CREW benchmark), 2509.10769 (AgentArch), 2501.06322 (collaboration)
- [[2512.06659] The Evolution of Agentic AI in Cybersecurity: From Single LLM Reasoners to Multi-Agent Systems and Autonomous Pipelines](https://arxiv.org/abs/2512.06659) `[SPEC]` `[MAS]` `[SURVEY]` `cs.CR` `cs.AI`
  - Survey of agentic AI evolution in cybersecurity from tool-augmented agents to autonomous investigative pipelines
  - Cross-ref: 2510.01751 (cybersecurity framework), 2510.01654 (CLASP), 2511.18194 (agent-as-graph)
- [[2512.03955] Benchmark for Planning and Control with Large Language Model Agents: Blocksworld with Model Context Protocol](https://arxiv.org/abs/2512.03955) `[BENCH]` `[PLAN]` `[TOOL]` `cs.AI` `cs.RO`
  - Planning and control benchmark using MCP for Blocksworld domain evaluation
  - Cross-ref: 2402.02716 (planning survey), 2510.02139 (BioinfoMCP), 2509.06917 (Paper2Agent MCP)
- [[2512.03420] HarnessAgent: Scaling Automatic Fuzzing Harness Construction with Tool-Augmented LLM Pipelines](https://arxiv.org/abs/2512.03420) `[CODE]` `[TOOL]` `[SPEC]` `cs.SE` `cs.CR`
  - Tool-augmented agentic framework for automated fuzzing harness construction at scale
  - Cross-ref: 2510.02185 (FalseCrashReducer), 2405.17935 (tool learning)

## 2025-11

- [[2511.19863] International AI Safety Report 2025: Second Key Update: Technical Safeguards and Risk Management](https://arxiv.org/abs/2511.19863) `[SAFETY]` `[SURVEY]` `cs.AI` `cs.CY`
  - Second key update covering advances in adversarial training, data curation, and monitoring systems for AI safety
  - Cross-ref: 2510.13653 (first key update), 2506.04133 (TRiSM), 2508.03858 (governance protocol)
- [[2511.18538] From Code Foundation Models to Agents and Applications: A Practical Guide to Code Intelligence](https://arxiv.org/abs/2511.18538) `[CODE]` `[SURVEY]` `[ARCH]` `cs.SE` `cs.AI`
  - Practical guide covering evolution from code foundation models to agentic applications
  - Cross-ref: 2508.00083 (code generation survey), 2508.11126 (agentic programming), 2507.15003 (SE 3.0)
- [[2511.18423] General Agentic Memory Via Deep Research](https://arxiv.org/abs/2511.18423) `[MEM]` `[ARCH]` `cs.AI` `cs.IR`
  - GAM framework following just-in-time compilation principle for optimized runtime contexts with simple offline memory
  - Cross-ref: 2512.13564 (memory survey), 2601.01885 (agentic memory), 2512.18950 (MACLA)
- [[2511.18194] Agent-as-a-Graph: Knowledge Graph-Based Tool and Agent Retrieval for LLM Multi-Agent Systems](https://arxiv.org/abs/2511.18194) `[MAS]` `[TOOL]` `[ARCH]` `cs.AI` `cs.IR`
  - Knowledge graph representation for tools and agents with weighted reciprocal rank fusion for reranking
  - Cross-ref: 2405.17935 (tool learning), 2512.16214 (PDE-Agent), 2501.06322 (collaboration)
- [[2511.14136] Beyond Accuracy: A Multi-Dimensional Framework for Evaluating Enterprise Agentic AI Systems](https://arxiv.org/abs/2511.14136) `[EVAL]` `[BENCH]` `[ARCH]` `cs.AI` `cs.SE`
  - CLEAR framework (Cost, Latency, Efficacy, Assurance, Reliability) for enterprise agent evaluation with ρ=0.83 production correlation
  - Cross-ref: 2509.10769 (AgentArch enterprise), 2512.12791 (assessment framework), 2503.16416 (evaluation survey)
- [[2511.02303] Unlocking the Power of Multi-Agent LLM for Reasoning: From Lazy Agents to Deliberation](https://arxiv.org/abs/2511.02303) `[MAS]` `[PLAN]` `cs.AI` `cs.CL`
  - Framework transitioning from lazy to deliberative reasoning in multi-agent LLM systems
  - Cross-ref: 2512.20845 (MAR), 2501.06322 (collaboration mechanisms), 2402.02716 (planning survey)

## 2025-10

- [[2510.26887] The Denario Project: Deep Knowledge AI Agents for Scientific Discovery](https://arxiv.org/abs/2510.26887) `[SCI]` `[MAS]` `[AUTO]` `cs.AI`
  - Multi-agent system for scientific research: idea generation, code execution, paper drafting; generated 11 AI-authored papers across disciplines
  - Cross-ref: 2506.18096 (deep research agents), 2502.14776 (SurveyX)
- [[2510.25445] Agentic AI: A Comprehensive Survey of Architectures, Applications, and Future Directions](https://arxiv.org/abs/2510.25445) `[SURVEY]` `[ARCH]` `cs.AI`
  - Comprehensive survey of agentic AI covering architectures, diverse applications, and future research directions
  - Cross-ref: 2308.11432 (foundational survey), 2503.21460 (LLM agent survey), 2508.10146 (frameworks)
- [[2510.23883] Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges](https://arxiv.org/abs/2510.23883) `[SAFETY]` `[EVAL]` `[SURVEY]` `cs.CR` `cs.AI`
  - Survey of agentic AI security covering attack methodologies, defense strategies, benchmarks, and open challenges
  - Cross-ref: 2507.06134 (OpenAgentSafety), 2510.01654 (CLASP), 2506.04133 (TRiSM), 2601.01743 (AI agent systems)
- [[2510.21413] Context Engineering for AI Agents in Open-Source Software](https://arxiv.org/abs/2510.21413) `[CODE]` `[ARCH]` `cs.SE` `cs.AI`
  - Framework for deliberate context design and information structuring for LLMs in open-source development
  - Cross-ref: 2508.00083 (code generation survey), 2507.15003 (SE 3.0), 2510.09244 (building agents fundamentals)
- [[2510.13653] International AI Safety Report 2025: First Key Update: Capabilities and Risk Implications](https://arxiv.org/abs/2510.13653) `[SAFETY]` `[SURVEY]` `cs.AI` `cs.CY`
  - First key update with capability improvements and implications for biological, cyber, monitoring, and controllability risks
  - Authors: Yoshua Bengio and 72 others
  - Cross-ref: 2511.19863 (second key update), 2302.10329 (harms analysis), 2506.04133 (TRiSM)
- [[2510.11290] Evolution in Simulation: AI-Agent School with Dual Memory for High-Fidelity Educational Dynamics](https://arxiv.org/abs/2510.11290) `[MAS]` `[MEM]` `[SPEC]` `cs.AI` `cs.CL`
  - LLM-based agents simulate complex educational dynamics with dual memory (experience/knowledge bases) enabling self-evolving cognitive development
  - Accepted at EMNLP 2025
  - Cross-ref: 2512.13564 (memory systems), 2404.13501 (memory mechanisms), 2510.01297 (SimCity urban simulation)
- [Simulating Two-Sided Job Marketplaces with AI Agents](https://openreview.net/forum?id=pjpkEHH5YS), [gh/upwork/simploy](https://github.com/upwork/simploy) `[MAS]` `[SPEC]` `[BENCH]` `OpenReview`
  - LLM agents demonstrate reasoning capabilities create fundamentally different market behaviors compared to rule-based simulations; reveals trade-offs between transaction volume and match quality
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2510.01297 (SimCity urban simulation), 2501.06322 (collaboration mechanisms)
- [Echo: A multi-agent AI system for patient-centered pharmacovigilance](https://openreview.net/forum?id=4nrWtE6oZ9) `[MAS]` `[SPEC]` `OpenReview`
  - Four specialized agents (Explorer, Analyzer, Verifier, Proposer) mine Reddit health communities identifying 640 drug-symptom associations including novel signals absent from FDA databases
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2507.16940 (AURA medical agent), 2508.21803 (clinical problem detection)
- [Multi-target Parallel Drug Discovery with Multi-agent Orchestration](https://openreview.net/forum?id=AhFsKmuaCb), [gh/UAB-SPARC/agentic-drug-discovery](https://github.com/UAB-SPARC/agentic-drug-discovery) `[MAS]` `[SCI]` `[SPEC]` `OpenReview`
  - End-to-end multi-agent framework for Alzheimer's disease drug discovery generating novel compounds with favorable characteristics for four protein targets
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2501.06590 (ChemAgent), 2510.02139 (BioinfoMCP)
- [PsySpace: Simulating Emergent Psychological Dynamics in Long-Duration Space Missions using Multi-Agent LLMs](https://openreview.net/forum?id=WAbHXkmBIn) `[MAS]` `[SPEC]` `[EVAL]` `OpenReview`
  - Multi-agent LLM framework simulating astronaut crew psychology with dual-component architecture (static personality profiles + dynamic stress/loneliness vectors) replicating third-quarter effect
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2509.24877 (social science LLMs), 2510.01815 (human-AI teaming)
- [Simulating Strategic Reasoning: A Digital Twin Approach to AI Advisors in Decision-Making](https://openreview.net/forum?id=L4arZChBJD) `[ARCH]` `[SPEC]` `[EVAL]` `OpenReview`
  - Digital twin framework modeling senior strategist reasoning revealing LLM performance gap between simple and complex multi-step strategic decision-making
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2510.01815 (human-AI teaming), 2512.14474 (model-first reasoning)
- [Towards Automatic Evaluation and Selection of PHI De-identification Models via Multi-Agent Collaboration](https://openreview.net/forum?id=MIjY6VNtY0) `[MAS]` `[EVAL]` `[SPEC]` `OpenReview`
  - TEAM-PHI framework using multiple LLM evaluators with majority voting to automate clinical de-identification model selection without costly expert annotations
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2507.21504 (evaluation survey), 2501.11067 (IntellAgent evaluation)
- [BadScientist: Can a Research Agent Write Convincing but Unsound Papers that Fool LLM Reviewers?](https://openreview.net/forum?id=7MPstNz66e) `[SAFETY]` `[SCI]` `[EVAL]` `OpenReview`
  - Exposes critical vulnerability in AI-driven scientific publishing with five manipulation strategies (TooGoodGains, BaselineSelect, StatTheater, CoherencePolish, ProofGap) achieving 67-82% acceptance rates fooling LLM reviewers
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2510.01359 (security assessment code agents), 2502.02649 (autonomy concerns)
- [Beyond Adam: AI-Authored Discovery of Symbolic Optimization Rules](https://openreview.net/forum?id=vUJOhgV3zh) `[AUTO]` `[SCI]` `[CODE]` `OpenReview`
  - Algorithmic Greenhouse demonstrates end-to-end autonomous AI authorship discovering interpretable optimization rules competitive with SGD, Momentum, and Adam
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2506.13131 (AlphaEvolve coding agent), 2507.21046 (self-evolving survey)
- [Behavioral Fingerprinting of Large Language Models](https://openreview.net/forum?id=s4gTj3fOIo) `[EVAL]` `[BENCH]` `[ARCH]` `OpenReview`
  - Diagnostic Prompt Suite analyzing 18 models revealing behavioral profiles beyond performance metrics; documents ISTJ/ESTJ personality clustering reflecting deliberate alignment choices
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2507.17257 (agent identity evals), 2411.13768 (evaluation-driven approach)
- [Scalable Oversight in Multi-Agent Systems: Provable Alignment via Delegated Debate and Hierarchical Verification](https://openreview.net/forum?id=l5Wrcgyobp) `[MAS]` `[SAFETY]` `[ARCH]` `OpenReview`
  - Hierarchical Delegated Oversight (HDO) framework with PAC-Bayesian bounds on misalignment risk enabling weak overseers to delegate verification through structured debates
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2506.04133 (TRiSM safety framework), 2508.03858 (governance protocol)
- [The Architectural Immune System: A Framework for Correcting Synthetic Fallacies in AI-Driven Science](https://openreview.net/forum?id=ShWjvhAZGs) `[SCI]` `[SAFETY]` `[ARCH]` `OpenReview`
  - Self-correcting framework for AI-driven materials discovery detecting statistically implausible results; integrates ten tools including adversarial critique and database validation
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2503.08979 (scientific discovery survey), 2408.06292 (AI scientist automation)
- [Survival of the Useful: Evolutionary Boids as a Sandbox for Agent Societies](https://openreview.net/forum?id=N7Kh0K33Dk) `[MAS]` `[AUTO]` `[ARCH]` `OpenReview`
  - Combines Boids-style coordination (cohesion, separation, alignment) with evolutionary selection for agent societies; observe-reflect-build cycle generates self-contained tools through decentralized rules
  - Published: 08 Oct 2025 (Agents4Science 2025 Conference)
  - Cross-ref: 2505.22954 (Darwin Godel Machine), 2508.07407 (self-evolving survey)
- [[2510.09721] A Comprehensive Survey on Benchmarks and Solutions in Software Engineering of LLM-Empowered Agentic System](https://arxiv.org/abs/2510.09721) `[SURVEY]` `[CODE]` `[BENCH]` `cs.SE` `cs.AI`
  - Survey analyzing 100 MAS LLMs benchmarks and evaluations papers published 2023-2025
  - Cross-ref: 2508.00083 (code generation), 2503.16416 (evaluation survey), 2507.02825 (benchmark practices)
- [[2510.09244] Fundamentals of Building Autonomous LLM Agents](https://arxiv.org/abs/2510.09244) `[ARCH]` `[SURVEY]` `cs.AI` `cs.CL`
  - Technical fundamentals covering agent perception, memory, reasoning, planning, and execution capabilities
  - Cross-ref: 2308.11432 (foundational survey), 2404.11584 (architecture landscape), 2503.21460 (LLM agent survey)
- [[2510.02297] Interactive Training: Feedback-Driven Neural Network Optimization](https://arxiv.org/abs/2510.02297) `[AUTO]` `[ARCH]` `cs.LG`
  - Framework enabling real-time human or AI agent intervention during neural network training with dynamic optimization parameter adjustments
  - Cross-ref: 2507.17131 (HITL self-improvement), 2405.06682 (feedback effects)
- [[2510.02286] Tree-based Dialogue Reinforced Policy Optimization for Red-Teaming Attacks](https://arxiv.org/abs/2510.02286) `[SAFETY]` `[AUTO]` `cs.LG`
  - DialTree-RPO reinforcement learning framework for discovering multi-turn attack strategies in dialogue settings
  - Cross-ref: 2510.01586 (adversarial safety), 2506.04133 (TRiSM safety framework)
- [[2510.02271] InfoMosaic-Bench: Evaluating Multi-Source Information Seeking in Tool-Augmented Agents](https://arxiv.org/abs/2510.02271) `[BENCH]` `[TOOL]` `[EVAL]` `cs.CL`
  - Benchmark testing agents' ability to integrate general web search with domain-specific tools across six domains
  - Cross-ref: 2405.17935 (tool learning survey), 2505.15872 (InfoDeepSeek RAG)
- [[2510.02263] RLAD: Training LLMs to Discover Abstractions for Solving Reasoning Problems](https://arxiv.org/abs/2510.02263) `[PLAN]` `[AUTO]` `cs.AI`
  - Two-player reinforcement learning approach enabling LLMs to generate and use reasoning abstractions
  - Cross-ref: 2510.01833 (plan-then-action), 2402.02716 (planning survey)
- [[2510.02250] The Unreasonable Effectiveness of Scaling Agents for Computer Use](https://arxiv.org/abs/2510.02250) `[ARCH]` `[BENCH]` `cs.AI`
  - Behavior Best-of-N (bBoN) method for scaling computer-use agents via multiple rollouts and trajectory selection
  - Cross-ref: 2510.01670 (BLIND-ACT benchmark), 2501.16150 (computer use review)
- [[2510.02245] ExGRPO: Learning to Reason from Experience](https://arxiv.org/abs/2510.02245) `[AUTO]` `[PLAN]` `cs.LG`
  - Framework for organizing and prioritizing valuable reasoning experiences in reinforcement learning
  - Cross-ref: 2405.06682 (self-reflection effects), 2406.01495 (Re-ReST)
- [[2510.02227] More Than One Teacher: Adaptive Multi-Guidance Policy Optimization](https://arxiv.org/abs/2510.02227) `[AUTO]` `[ARCH]` `cs.CL`
  - Adaptive Multi-Guidance Policy Optimization (AMPO) leveraging multiple teacher models for enhanced exploration
  - Cross-ref: 2510.02245 (ExGRPO), 2507.17131 (HITL guidance)
- [[2510.02209] StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?](https://arxiv.org/abs/2510.02209) `[BENCH]` `[SPEC]` `cs.LG`
  - Multi-month benchmark evaluating LLM agents' capabilities in real-world stock trading with sequential decision-making
  - Cross-ref: 2408.06361 (financial trading survey), 2501.00881 (industry applications)
- [[2510.02204] Say One Thing, Do Another? Diagnosing Reasoning-Execution Gaps in VLM-Powered Mobile-Use Agents](https://arxiv.org/abs/2510.02204) `[SAFETY]` `[EVAL]` `cs.CL`
  - Framework for diagnosing misalignments between reasoning and execution in vision-language mobile agents
  - Cross-ref: 2510.01670 (blind goal-directedness), 2501.16150 (computer use review)
- [[2510.02190] A Rigorous Benchmark with Multidimensional Evaluation for Deep Research Agents](https://arxiv.org/abs/2510.02190) `[BENCH]` `[SCI]` `[EVAL]` `cs.AI`
  - Comprehensive benchmark for Deep Research Agents with 214 expert-curated queries and multidimensional scoring
  - Cross-ref: 2506.18096 (deep research agents), 2501.04227 (research assistants)
- [[2510.02185] FalseCrashReducer: Mitigating False Positive Crashes in OSS-Fuzz-Gen Using Agentic AI](https://arxiv.org/abs/2510.02185) `[CODE]` `[MAS]` `cs.SE`
  - AI-driven strategies reducing false positives in multi-agent fuzz driver generation systems
  - Cross-ref: 2503.14713 (test generation), 2410.14393 (debug agents)
- [[2510.02157] Agentic Reasoning and Refinement through Semantic Interaction](https://arxiv.org/abs/2510.02157) `[PLAN]` `[ARCH]` `cs.HC`
  - VIS-ReAct two-agent framework for report refinement using semantic interactions in human-LLM collaboration
  - Cross-ref: 2507.17131 (HITL self-improvement), 2411.00927 (ReSpAct)
- [[2510.02139] BioinfoMCP: A Unified Platform Enabling MCP Interfaces in Agentic Bioinformatics](https://arxiv.org/abs/2510.02139) `[SPEC]` `[MAS]` `[TOOL]` `cs.MA`
  - Platform converting bioinformatics tools to MCP-compliant servers for natural-language interaction
  - Cross-ref: 2510.01724 (MetaboT), 2501.06590 (ChemAgent)
- [[2510.02087] Cooperative Guidance for Aerial Defense in Multiagent Systems](https://arxiv.org/abs/2510.02087) `[MAS]` `[SPEC]` `cs.MA`
  - Cooperative guidance framework for multi-drone aerial defense with time-constrained interception
  - Cross-ref: 2510.01869 (TACOS multi-drone), 2507.05178 (CREW benchmark)
- [[2510.01869] TACOS: Task Agnostic COordinator of a multi-drone System](https://arxiv.org/abs/2510.01869) `[MAS]` `[ARCH]` `cs.RO`
  - Natural language control framework for multi-UAV systems using LLMs for high-level task delegation
  - Cross-ref: 2510.02087 (aerial defense), 2501.06322 (collaboration mechanisms)
- [[2510.01833] Plan Then Action: High-Level Planning Guidance Reinforcement Learning for LLM Reasoning](https://arxiv.org/abs/2510.01833) `[PLAN]` `[AUTO]` `cs.AI`
  - Two-stage framework generating high-level guidance then using RL to optimize reasoning trajectories
  - Cross-ref: 2402.02716 (planning survey), 2310.04406 (LATS)
- [[2510.01815] Human-AI Teaming Co-Learning in Military Operations](https://arxiv.org/abs/2510.01815) `[SAFETY]` `[ARCH]` `cs.AI`
  - Co-learning model for human-AI teams with adjustable autonomy and multi-layered control
  - Cross-ref: 2507.17131 (HITL self-improvement), 2402.04247 (safeguarding priority)
- [[2510.01751] A cybersecurity AI agent selection and decision support framework](https://arxiv.org/abs/2510.01751) `[SPEC]` `[SAFETY]` `[ARCH]` `cs.AI`
  - Framework aligning AI agent architectures with NIST Cybersecurity Framework for threat response
  - Cross-ref: 2510.01654 (CLASP security), 2506.04133 (TRiSM)
- [[2510.01724] MetaboT: AI-based agent for natural language-based interaction with metabolomics knowledge graphs](https://arxiv.org/abs/2510.01724) `[SPEC]` `[MAS]` `[TOOL]` `cs.AI`
  - Multi-agent system translating natural language to SPARQL queries for metabolomics knowledge graphs
  - Cross-ref: 2510.02139 (BioinfoMCP), 2501.06590 (ChemAgent)
- [[2510.01670] Just Do It!? Computer-Use Agents Exhibit Blind Goal-Directedness](https://arxiv.org/abs/2510.01670) `[BENCH]` `[SAFETY]` `[EVAL]` `cs.AI`
  - BLIND-ACT benchmark systematically evaluating agents' tendency to pursue goals without considering feasibility
  - Cross-ref: 2510.02250 (computer use scaling), 2510.02204 (reasoning-execution gaps)
- [[2510.01654] SoK: Measuring What Matters for Closed-Loop Security Agents](https://arxiv.org/abs/2510.01654) `[BENCH]` `[SAFETY]` `[SPEC]` `cs.CL`
  - CLASP framework for evaluating autonomous cybersecurity agents with Closed-Loop Capability Score
  - Cross-ref: 2510.01751 (cybersecurity framework), 2506.04133 (TRiSM)
- [[2510.01635] MIMIC: Integrating Diverse Personality Traits for Better Game Testing Using Large Language Model](https://arxiv.org/abs/2510.01635) `[SPEC]` `[CODE]` `cs.SE`
  - Framework integrating personality traits into gaming agents for improved test coverage
  - Cross-ref: 2503.14713 (test generation), 2505.22583 (GitGoodBench)
- [[2510.01586] AdvEvo-MARL: Shaping Internalized Safety through Adversarial Co-Evolution](https://arxiv.org/abs/2510.01586) `[SAFETY]` `[MAS]` `[AUTO]` `cs.AI`
  - Multi-agent RL framework improving safety by jointly optimizing attackers and defenders
  - Cross-ref: 2510.02286 (adversarial attacks), 2506.04133 (TRiSM)
- [[2510.01569] InvThink: Towards AI Safety via Inverse Reasoning](https://arxiv.org/abs/2510.01569) `[SAFETY]` `[ARCH]` `cs.AI`
  - Method for LLMs to enumerate and analyze potential harms before generating responses
  - Cross-ref: 2501.17112 (inverse constitutional AI), 2508.03858 (governance protocol)
- [[2510.01553] IoDResearch: Deep Research on Private Heterogeneous Data](https://arxiv.org/abs/2510.01553) `[SCI]` `[MAS]` `cs.IR`
  - Multi-agent framework for deep research on private heterogeneous scientific data with knowledge graphs
  - Cross-ref: 2510.02190 (deep research benchmark), 2506.18096 (deep research agents)
- [[2510.01538] TimeSeriesScientist: A General-Purpose AI Agent for Time Series Analysis](https://arxiv.org/abs/2510.01538) `[SCI]` `[SPEC]` `cs.LG`
  - LLM-driven framework with specialized agents for time series forecasting and analysis
  - Cross-ref: 2501.04227 (research assistants), 2506.18096 (deep research agents)
- [[2510.01531] Information Seeking for Robust Decision Making under Partial Observability](https://arxiv.org/abs/2510.01531) `[PLAN]` `[ARCH]` `cs.AI`
  - InfoSeeker framework integrating planning with information seeking for decision-making under uncertainty
  - Cross-ref: 2402.02716 (planning survey), 2410.09713 (agentic IR)
- [[2510.01524] WALT: Web Agents that Learn Tools](https://arxiv.org/abs/2510.01524) `[TOOL]` `[ARCH]` `cs.CV`
  - Framework for web agents reverse-engineering website functionalities as reusable tools
  - Cross-ref: 2405.17935 (tool learning), 2510.02271 (InfoMosaic-Bench)
- [[2510.01427] A Tale of LLMs and Induced Small Proxies: Scalable Agents for Knowledge Mining](https://arxiv.org/abs/2510.01427) `[SCI]` `[ARCH]` `cs.AI`
  - Falconer collaborative framework combining LLM reasoning with lightweight proxy models for knowledge mining
  - Cross-ref: 2510.01553 (IoDResearch), 2506.18096 (deep research agents)
- [[2510.01379] Beyond Single LLMs: Enhanced Code Generation via Multi-Stage Performance-Guided LLM Orchestration](https://arxiv.org/abs/2510.01379) `[CODE]` `[ARCH]` `cs.SE`
  - Multi-stage orchestration framework routing coding tasks to optimal LLMs across programming languages
  - Cross-ref: 2507.22414 (code explanations), 2506.13131 (AlphaEvolve)
- [[2510.01359] Breaking the Code: Security Assessment of AI Code Agents Through Systematic Jailbreaking Attacks](https://arxiv.org/abs/2510.01359) `[SAFETY]` `[CODE]` `cs.CR`
  - Security evaluation of code-generating AI agents through systematic jailbreaking attack testing
  - Cross-ref: 2510.01569 (InvThink safety), 2506.04133 (TRiSM)
- [[2510.01297] SimCity: Multi-Agent Urban Development Simulation with Rich Interactions](https://arxiv.org/abs/2510.01297) `[MAS]` `[SPEC]` `cs.MA`
  - Multi-agent framework for macroeconomic simulation using LLMs modeling heterogeneous urban agents
  - Cross-ref: 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms)
- [[2510.01179] TOUCAN: Synthesizing 1.5M Tool-Agentic Data from Real-World MCP Environments](https://arxiv.org/abs/2510.01179) `[TOOL]` `[BENCH]` `cs.LG`
  - Large dataset of tool-agentic interactions using real-world Model Context Protocols for training
  - Cross-ref: 2405.17935 (tool learning survey), 2510.02271 (InfoMosaic-Bench)
- [[2510.01003] Improving Code Localization with Repository Memory](https://arxiv.org/abs/2510.01003) `[CODE]` `[MEM]` `cs.SE`
  - Augmenting language agents with repository memory leveraging commit history for code understanding
  - Cross-ref: 2404.13501 (memory mechanisms), 2410.14393 (debug agents)

## 2025-09

- [[2509.25250] Memory Management and Contextual Consistency for Long-Running Low-Code Agents](https://arxiv.org/abs/2509.25250) `[MEM]` `[ARCH]` `cs.AI` `cs.SE`
  - Memory management framework ensuring contextual consistency in long-running low-code agent systems
  - Cross-ref: 2512.13564 (memory survey), 2511.18423 (GAM), 2404.13501 (memory mechanisms)
- [[2509.10769] AgentArch: A Comprehensive Benchmark to Evaluate Agent Architectures in Enterprise](https://arxiv.org/abs/2509.10769) `[BENCH]` `[EVAL]` `[ARCH]` `cs.AI` `cs.SE`
  - Benchmark evaluating 18 agent architecture configurations on enterprise use cases across orchestration, prompting, memory, and tools
  - Cross-ref: 2511.14136 (CLEAR framework), 2512.08296 (scaling agent systems), 2308.03688 (AgentBench)
- [[2509.06917] Paper2Agent: Reimagining Research Papers As Interactive and Reliable AI Agents](https://arxiv.org/abs/2509.06917) `[RESEARCH]` `[AUTO]` `[TOOL]` `cs.AI` `cs.SE`
  - Framework converting research papers into interactive AI agents using Model Context Protocol servers with automated testing
  - Systematically analyzes papers and codebases to construct MCP servers for dynamic knowledge dissemination
  - Cross-ref: 2505.18705 (AI-Researcher), 2312.07559 (PaperQA), 2501.04227 (research assistants)
- [[2509.24877] The Emergence of Social Science of Large Language Models](https://arxiv.org/abs/2509.24877) `[SURVEY]` `[ARCH]` `cs.AI`
  - Systematic review of 270 studies examining LLM social interactions and computational taxonomy
  - Cross-ref: 2503.21460 (LLM agent survey), 2308.11432 (foundational survey)
- [[2509.00629] Can Multi-turn Self-refined Single Agent LMs with Retrieval Solve Hard Coding Problems?](https://arxiv.org/abs/2509.00629) `[CODE]` `[BENCH]` `cs.CL`
  - ICPC benchmark with 254 competitive programming problems achieving 42.2% solve rate with self-refinement
  - Cross-ref: 2505.22583 (GitGoodBench), 2410.14393 (debug agents)
- [[2509.00625] NetGent: Agent-Based Automation of Network Application Workflows](https://arxiv.org/abs/2509.00625) `[AUTO]` `[SPEC]` `cs.AI`
  - AI agent framework compiling natural-language workflow rules into executable code for network automation
  - Cross-ref: 2505.22967 (MermaidFlow workflows), 2502.05957 (AutoAgent)
- [[2509.00616] TimeCopilot](https://arxiv.org/abs/2509.00616) `[SCI]` `[SPEC]` `cs.LG`
  - Open-source agentic framework for time series forecasting combining models with LLMs and natural language explanations
  - Cross-ref: 2510.01538 (TimeSeriesScientist), 2501.04227 (research assistants)
- [[2509.00581] SQL-of-Thought: Multi-agentic Text-to-SQL with Guided Error Correction](https://arxiv.org/abs/2509.00581) `[MAS]` `[CODE]` `cs.DB`
  - Multi-agent framework for natural language to SQL conversion with schema linking and error correction
  - Cross-ref: 2508.15809 (Chain-of-Query), 2402.01030 (executable actions)
- [[2509.00559] Social World Models](https://arxiv.org/abs/2509.00559) `[ARCH]` `[SPEC]` `cs.AI`
  - Structured social world representation for agent reasoning about social interactions and theory-of-mind
  - Cross-ref: 2509.24877 (social science LLMs), 2510.01815 (human-AI teaming)
- [[2509.00531] MobiAgent: A Systematic Framework for Customizable Mobile Agents](https://arxiv.org/abs/2509.00531) `[SPEC]` `[ARCH]` `cs.MA`
  - Comprehensive mobile agent system with advanced GUI perception and planning capabilities
  - Cross-ref: 2501.16150 (computer use review), 2510.02250 (computer use scaling)
- [[2509.24380] Agentic Services Computing](https://arxiv.org/abs/2509.24380) `[SURVEY]` `[ARCH]` `cs.SE`
  - Lifecycle-driven framework for Agentic Service Computing examining multi-agent service design and evolution
  - Cross-ref: 2508.10146 (agentic frameworks), 2501.10114 (infrastructure)
- [[2509.23988] LLM/Agent-as-Data-Analyst: A Survey](https://arxiv.org/abs/2509.23988) `[SURVEY]` `[SPEC]` `cs.AI`
  - Review of LLM and agent techniques for data analysis across different modalities
  - Cross-ref: 2503.21460 (LLM agent survey), 2501.04227 (research assistants)
- [[2510.00078] Adaptive and Resource-efficient Agentic AI Systems for Mobile and Embedded Devices: A Survey](https://arxiv.org/abs/2510.00078) `[SURVEY]` `[ARCH]` `cs.LG`
  - Survey of adaptive, resource-efficient agentic AI for mobile and embedded device deployment
  - Cross-ref: 2508.10146 (agentic frameworks), 2501.10114 (infrastructure)

## 2025-08

- [[2508.00828] FinanceBench: Measuring Finance Domain Knowledge of LLM Agents](https://arxiv.org/abs/2508.00828) `[BENCH]` `[SPEC]` `cs.CL`
  - Benchmark for evaluating agents on SEC filing research and financial analysis automation
- [[2508.11126] AI Agentic Programming: A Survey of Techniques, Challenges, and Opportunities](https://arxiv.org/abs/2508.11126) `[CODE]` `[SURVEY]` `cs.SE` `cs.AI`
  - Survey of agentic programming paradigm where LLM agents autonomously plan, execute, and interact with development tools
  - Cross-ref: 2508.00083 (code generation survey), 2511.18538 (code foundation models), 2507.15003 (SE 3.0)
- [[2508.00344] PilotRL: Training Language Model Agents via Global Planning-Guided Progressive Reinforcement Learning](https://arxiv.org/abs/2508.00344) `[AUTO]` `[PLAN]` `cs.AI` `cs.LG`
  - Global planning-guided RL framework achieving state-of-the-art with LLaMA3.1-8B-Instruct surpassing GPT-4o by 3.60%
  - Cross-ref: 2510.01833 (plan-then-action), 2402.02716 (planning survey), 2406.01495 (Re-ReST)
- [[2508.00083] A Survey on Code Generation with LLM-based Agents](https://arxiv.org/abs/2508.00083) `[CODE]` `[SURVEY]` `cs.SE` `cs.AI`
  - Comprehensive survey of LLM code generation agents covering autonomy and expanded scope throughout SDLC
  - Cross-ref: 2508.11126 (agentic programming), 2511.18538 (code foundation models), 2507.15003 (SE 3.0)
- [[2508.21803] Automated Clinical Problem Detection from SOAP Notes using a Collaborative Multi-Agent LLM Architecture](https://arxiv.org/abs/2508.21803) `[MAS]` `[SPEC]` `cs.AI`
  - Collaborative multi-agent system for clinical problem identification with hierarchical debate for diagnostic conclusions
  - Cross-ref: 2507.16940 (AURA medical agent), 2501.06322 (collaboration mechanisms)
- [[2508.15809] Chain-of-Query: Unleashing the Power of LLMs in SQL-Aided Table Understanding via Multi-Agent Collaboration](https://arxiv.org/abs/2508.15809) `[MAS]` `[CODE]` `cs.CL`
  - Multi-agent framework for SQL generation and table understanding with clause-by-clause generation strategy
  - Cross-ref: 2509.00581 (SQL-of-Thought), 2402.01030 (executable actions)
- [[2508.15805] ALAS: Autonomous Learning Agent for Self-Updating Language Models](https://arxiv.org/abs/2508.15805) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - Autonomous learning framework for continuous self-updating of language models with data acquisition and fine-tuning pipeline
  - Cross-ref: 2507.17131 (HITL self-improvement), 2410.04444 (Gödel Agent recursive improvement)
- [[2508.11120] Towards Reliable Multi-Agent Systems for Marketing Applications via Reflection, Memory, and Planning](https://arxiv.org/abs/2508.11120) `[MAS]` `[MEM]` `[SPEC]` `cs.CL`
  - Multi-agent framework for audience curation with iterative planning, tool verification, and long-term memory
  - Cross-ref: 2404.13501 (memory mechanisms), 2501.06322 (collaboration mechanisms)
- [[2508.11030] Families' Vision of Generative AI Agents for Household Safety](https://arxiv.org/abs/2508.11030) `[SPEC]` `[SAFETY]` `cs.HC`
  - Multi-agent system design for household safety with privacy-preserving principles and family-centric roles
  - Cross-ref: 2510.01815 (human-AI teaming), 2506.04133 (TRiSM safety)
- [[2508.10572] Towards Agentic AI for Multimodal-Guided Video Object Segmentation](https://arxiv.org/abs/2508.10572) `[SPEC]` `[ARCH]` `cs.CV`
  - Multi-modal agent system for video object segmentation using LLMs for dynamic workflow generation
  - Cross-ref: 2408.08632 (multimodal benchmarking), 2507.16940 (AURA multimodal)
- [[2508.10494] A Unified Multi-Agent Framework for Universal Multimodal Understanding and Generation](https://arxiv.org/abs/2508.10494) `[MAS]` `[ARCH]` `cs.LG`
  - MAGUS modular framework for multimodal understanding and generation via multi-agent collaboration
  - Cross-ref: 2408.08632 (multimodal benchmarking), 2501.06322 (collaboration mechanisms)
- [[2508.10146] Agentic AI Frameworks: Architectures, Protocols, and Design Challenges](https://arxiv.org/abs/2508.10146) `[ARCH]` `[SURVEY]` `cs.AI` `cs.SE`
  - Systematic review of leading agentic AI frameworks including CrewAI, LangGraph, AutoGen, and MetaGPT with architectural analysis
  - Cross-ref: 2502.05957 (AutoAgent framework), 2501.00881 (industry applications)
- [[2508.07407] A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems](https://arxiv.org/abs/2508.07407) `[SURVEY]` `[AUTO]` `cs.AI` `cs.LG`
  - Comprehensive survey of self-evolving agents covering evolutionary techniques, environmental feedback, and lifelong learning paradigms
  - Cross-ref: 2507.21046 (self-evolving survey), 2505.22954 (Darwin Godel Machine)
- [[2508.03858] MI9 - Agent Intelligence Protocol: Runtime Governance forAgentic AI Systems](https://arxiv.org/abs/2508.03858) `[SAFETY]` `[ARCH]` `cs.AI` `cs.CR`
  - Runtime governance framework for ensuring safe and controllable agentic AI systems
  - Cross-ref: 2408.02205 (complementary safety layers), 2506.04133 (similar safety framework), 2302.10329 (foundational risk analysis)
- [[2508.03682] SELF-QUESTIONING LANGUAGE MODELS](https://www.arxiv.org/abs/2508.03682) `[PLAN]` `[ARCH]` `cs.CL` `cs.AI`
  - Framework for improving LLM reasoning through self-generated questions and introspective analysis
  - Cross-ref: 2402.02716 (broader planning context), 2411.13768 (evaluation methodology overlap)
- [[2508.00414] Cognitive Kernel-Pro: A Framework for Deep Research Agents and Agent Foundation Models Training](https://www.arxiv.org/abs/2508.00414) `[SCI]` `[ARCH]` `cs.AI` `cs.LG`
  - Training framework for developing specialized research agents with enhanced cognitive capabilities
  - Cross-ref: 2506.18096 (research agent foundations), 2501.04227 (practical research applications)
- [[2508.00032] Strategic Communication and Language Bias in Multi-Agent LLM Coordination](https://arxiv.org/abs/2508.00032) `[MAS]` `[ARCH]` `cs.MA`
  - Examines how communication influences cooperative behavior in multi-agent LLM systems
  - Cross-ref: 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms)

## 2025-07

- [[2507.05558] Can LLM Agents Exploit Smart Contract Vulnerabilities?](https://arxiv.org/abs/2507.05558) `[BENCH]` `[SAFETY]` `cs.CR`
  - Benchmark for vulnerability exploitation assessment in smart contracts
- [[2507.21504] Evaluation and Benchmarking of LLM Agents: A Survey](https://arxiv.org/abs/2507.21504) `[EVAL]` `[BENCH]` `[SURVEY]` `cs.AI` `cs.CL`
  - Taxonomy of LLM agent evaluation covering objectives (behavior, capabilities, reliability, safety) and process (interaction, datasets, metrics, environments)
  - Cross-ref: 2503.16416 (evaluation survey), 2507.02825 (benchmark best practices), 2411.13768 (evaluation-driven)
- [[2507.15003] The Rise of AI Teammates in Software Engineering (SE) 3.0: How Autonomous Coding Agents Are Reshaping Software Engineering](https://arxiv.org/abs/2507.15003) `[CODE]` `[SURVEY]` `cs.SE` `cs.AI`
  - SE 3.0 vision of intent-driven conversational development with autonomous AI teammates operating at task level
  - Cross-ref: 2508.00083 (code generation survey), 2508.11126 (agentic programming), 2511.18538 (code foundation models)
- [[2507.11473] Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety](https://arxiv.org/abs/2507.11473) `[SAFETY]` `[EVAL]` `cs.AI` `cs.LG`
  - Framework for monitoring LLM agent chain-of-thought reasoning with holistic risk assessments
  - Cross-ref: 2510.13653 (AI safety report), 2506.04133 (TRiSM), 2508.03858 (governance protocol)
- [[2507.06134] OpenAgentSafety: A Comprehensive Framework for Evaluating Real-World AI Agent Safety](https://arxiv.org/abs/2507.06134) `[SAFETY]` `[EVAL]` `[BENCH]` `cs.AI` `cs.CR`
  - Comprehensive framework for evaluating AI agent safety in real-world deployment scenarios
  - Cross-ref: 2506.04133 (TRiSM framework), 2508.03858 (governance protocol), 2410.06703 (ST-WebAgentBench)
- [[2507.23276] How Far Are AI Scientists from Changing the World?](https://arxiv.org/abs/2507.23276), [gh/ResearAI/Awesome-AI-Scientist](https://github.com/ResearAI/Awesome-AI-Scientist) `[SCI]` `[SURVEY]`
  - Survey of research on AI scientists, AI researchers, AI engineers, and a series of AI-driven research studies
  - Cross-ref: 2408.06292 (automated scientific discovery implementation), 2506.18096 (systematic research agent analysis)
- [[2507.23096] ChatVis: Large Language Model Agent for Generating Scientific Visualizations](https://arxiv.org/abs/2507.23096) `[CODE]` `[SPEC]` `cs.HC`
  - LLM assistant for generating Python code for scientific visualizations using chain-of-thought and RAG
  - Cross-ref: 2507.22414 (code explanations), 2410.09713 (agentic IR)
- [[2507.23095] SMART-Editor: A Multi-Agent Framework for Human-Like Design Editing](https://arxiv.org/abs/2507.23095) `[MAS]` `[ARCH]` `cs.CL`
  - Framework for compositional layout and content editing with reward-guided refinement
  - Cross-ref: 2501.06322 (collaboration mechanisms), 2510.02157 (VIS-ReAct)
- [[2507.22800] The Multi-Agent Fault Localization System Based on Monte Carlo Tree Search Approach](https://arxiv.org/abs/2507.22800) `[MAS]` `[SPEC]` `cs.SE`
  - Multi-agent system for root cause analysis in microservices using LLMs with knowledge-based approach
  - Cross-ref: 2510.01751 (cybersecurity framework), 2501.06322 (collaboration mechanisms)
- [[2507.17131] Enabling Self-Improving Agents to Learn at Test Time With Human-In-The-Loop Guidance](https://arxiv.org/abs/2507.17131) `[AUTO]` `[ARCH]` `cs.AI` `cs.HC`
  - Framework for enabling agents to self-improve through human-in-the-loop guidance and knowledge gap assessment
  - Cross-ref: 2508.15805 (ALAS autonomous learning), 2405.06682 (self-reflection effects)
- [[2507.22414] AutoCodeSherpa: Symbolic Explanations in AI Coding Agents](https://arxiv.org/abs/2507.22414) `[CODE]` `[ARCH]`
  - Framework for providing symbolic explanations of code generation decisions in AI coding agents
  - Cross-ref: 2402.01030 (code action effectiveness), 2506.13131 (evolutionary coding approach)
- [[2507.21046] A SURVEY OF SELF-EVOLVING AGENTS: ON PATH TO ARTIFICIAL SUPER INTELLIGENCE](https://arxiv.org/abs/2507.21046), [gh/CharlesQ9/Self-Evolving-Agents](https://github.com/CharlesQ9/Self-Evolving-Agents) `[SURVEY]` `[ARCH]`
  - Comprehensive survey of self-improving AI agents and their potential path toward artificial superintelligence
  - Cross-ref: 2505.22954 (theoretical self-evolution framework), 2507.17311 (domain-specific self-evolution)
- [[2507.18074] AlphaGo Moment for Model Architecture Discovery](https://arxiv.org/abs/2507.18074), [gh/GAIR-NLP/ASI-Arch](https://github.com/GAIR-NLP/ASI-Arch) `[ARCH]` `[AUTO]`
  - Automated neural architecture search using AI agents for discovering novel model architectures
  - Cross-ref: 2408.08435 (broader automated design scope), 2506.16499 (ML automation methods)
- [[2507.17311] EarthLink: A Self-Evolving AI Agent forClimate Science](https://arxiv.org/abs/2507.17311) `[SCI]` `[SPEC]`
  - Self-improving AI agent specialized for climate science research and analysis
  - Cross-ref: 2507.21046 (general self-evolution theory), 2501.06590 (similar scientific domain agent)
- [[2507.17257] Agent Identity Evals: Measuring Agentic Identity](https://arxiv.org/abs/2507.17257) `[EVAL]` `[BENCH]`
  - Evaluation framework for measuring and understanding agent identity and persona consistency
  - Cross-ref: 2411.13768 (evaluation methodology synergy), 2503.16416 (comprehensive evaluation landscape)
- [[2507.16940] AURA: A Multi-Modal Medical Agent forUnderstanding, Reasoning & Annotation](https://arxiv.org/abs/2507.16940) `[SPEC]` `[ARCH]`
  - Multi-modal AI agent for medical data understanding, clinical reasoning, and annotation tasks
  - Cross-ref: 2408.08632 (multimodal benchmarking context), 2404.13501 (memory for complex reasoning)
- [[2507.10584] ARPaCCino: An Agentic-RAG for Policy as CodeCompliance](https://arxiv.org/abs/2507.10584) `[COMP]` `[TOOL]`
  - Agentic RAG system for automated policy-as-code compliance checking and enforcement
  - Cross-ref: 2505.15872 (RAG benchmarking methods), 2410.09713 (agentic retrieval techniques)
- [[2507.05178] CREW-WILDFIRE: Benchmarking AgenticMulti-Agent Collaborations at Scale](https://arxiv.org/abs/2507.05178) `[BENCH]` `[MAS]`
  - Large-scale benchmark for evaluating collaborative multi-agent systems in complex scenarios
  - Cross-ref: 2501.06322 (collaboration mechanism design), 2503.13657 (failure mode analysis)
- [[2507.02825] Establishing Best Practices for Building RigorousAgentic Benchmarks](https://arxiv.org/abs/2507.02825) `[BENCH]` `[EVAL]`
  - Guidelines and methodology for creating robust evaluation benchmarks for agentic AI systems
  - Cross-ref: 2404.06411 (AgentQuest), 2308.03688 (AgentBench)
- [[2507.02097] The Future is Agentic: Definitions, Perspectives, and OpenChallenges of Multi-Agent Recommender Systems](https://arxiv.org/abs/2507.02097) `[MAS]` `[SURVEY]`
  - Survey of multi-agent recommender systems, definitions, current perspectives, and future research directions
  - Cross-ref: 2501.06322 (collaboration mechanisms), 2507.05178 (CREW benchmark)

## 2025-06

- [[2506.07982] τ²-bench: A Benchmark for Tool Use with Dual-Control User-Agent Interactions](https://arxiv.org/abs/2506.07982) `[BENCH]` `[TOOL]` `[EVAL]` `cs.AI` `cs.CL`
  - Extension of τ-bench with dual-control evaluation for user-agent tool interactions
  - Cross-ref: 2406.12045 (τ-bench), 2307.16789 (ToolLLM)
- [[2506.04625] Advancing Tool-Augmented Large Language Models via Meta-Verification and Reflection Learning](https://arxiv.org/abs/2506.04625) `[TOOL]` `[AUTO]` `cs.AI` `cs.CL`
  - Tool-MVR framework achieving state-of-the-art on StableToolBench, surpassing ToolLLM by 23.9% and GPT-4 by 15.3%
  - Cross-ref: 2307.16789 (ToolLLM), 2405.17935 (tool learning survey), 2406.12045 (τ-bench)
- [[2506.02548] CyberGym: Real CVE Vulnerability Assessment Benchmark](https://arxiv.org/abs/2506.02548) `[BENCH]` `[SAFETY]` `cs.CR`
  - Security benchmark for evaluating agents on real CVE vulnerability detection and assessment
- [[2506.23408] Do LLMs Dream of Discrete Algorithms?](https://arxiv.org/abs/2506.23408) `[PLAN]` `[ARCH]` `cs.LG`
  - Neurosymbolic approach augmenting LLMs with logic-based reasoning modules for improved agent planning precision
  - Cross-ref: 2210.03629 (ReAct planning), 2310.04406 (LATS reasoning)
- [[2506.23329] IR3D-Bench: Evaluating Vision-Language Model Scene Understanding as Agentic Inverse Rendering](https://arxiv.org/abs/2506.23329) `[BENCH]` `[EVAL]` `cs.CV`
  - Benchmark challenging vision-language agents to recreate 3D scene structures through tool use
  - Cross-ref: 2408.08632 (multimodal benchmarking), 2510.02271 (InfoMosaic-Bench)
- [AlphaGenome: advancing regulatory variant effect prediction with a unified DNA sequence model](https://www.biorxiv.org/content/10.1101/2025.06.25.661532v1), [gh/google-deepmind/alphagenome](https://github.com/google-deepmind/alphagenome) `[SCI]` `[SPEC]` `[ARCH]` `bioRxiv`
  - Google DeepMind's unified DNA sequence model predicting functional genomic tracks at single base pair resolution across diverse modalities; matches or exceeds strongest models on 24/26 variant effect prediction evaluations
  - Published: 27 Jun 2025 (bioRxiv)
  - Cross-ref: 2510.01724 (MetaboT domain-specific), 2501.06590 (ChemAgent scientific)
- [[2506.23306] GATSim: Urban Mobility Simulation with Generative Agents](https://arxiv.org/abs/2506.23306) `[MAS]` `[SPEC]` `cs.AI`
  - Urban mobility simulation framework using generative agents with adaptive behaviors and memory systems
  - Cross-ref: 2510.01297 (SimCity urban simulation), 2404.13501 (memory mechanisms)
- [[2506.18096] Deep Research Agents: A Systematic Examination And Roadmap](https://arxiv.org/abs/2506.18096), [gh/ai-agents-2030/awesome-deep-research-agent](https://github.com/ai-agents-2030/awesome-deep-research-agent) `[SCI]` `[SURVEY]`
  - Comprehensive examination of AI agents for research tasks with roadmap for future development
  - Cross-ref: 2507.23276 (AI scientist impact assessment), 2501.04227 (practical research implementation)
- [[2506.16499] ML-Master: Towards AI-for-AI via Integration ofExploration and Reasoning](https://arxiv.org/abs/2506.16499) `[AUTO]` `[ARCH]`
  - AI system for automated machine learning through integrated exploration and reasoning capabilities
  - Cross-ref: 2507.18074 (automated architecture search), 2411.10478 (workflow optimization survey)
- [[2506.13131] AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131) `[CODE]` `[SCI]`
  - Evolutionary coding agent for automated scientific discovery and algorithm development
  - Cross-ref: 2507.22414 (code explanation methods), 2408.06292 (scientific discovery automation)
- [AlphaGenome: advancing regulatory variant effect prediction with a unified DNA sequence model](https://www.biorxiv.org/content/10.1101/2025.06.25.661532v1), [gh/google-deepmind/alphagenome](https://github.com/google-deepmind/alphagenome) `[SCI]` `[SPEC]` `[ARCH]` `bioRxiv` `cs.AI` `q-bio.GN`
  - Google DeepMind's unified DNA sequence model predicting thousands of functional genomic tracks at single base pair resolution; matches or exceeds 24/26 variant effect prediction benchmarks
  - Trained on human and mouse genomes; provides API and tools for genome track and variant effect predictions from sequence
  - Cross-ref: 2510.01724 (MetaboT bioinformatics), 2501.06590 (ChemAgent domain applications)
- [[2506.04133] TRiSM for Agentic AI: A Review of Trust, Risk, and SecurityManagement in LLM-based Agentic Multi-Agent Systems](https://arxiv.org/abs/2506.04133) `[SAFETY]` `[MAS]`
  - Framework for managing trust, risk, and security in LLM-based multi-agent systems
  - Cross-ref: 2508.03858 (runtime governance approach), 2408.02205 (layered safety model)
- [[2506.01438] Distinguishing Autonomous AI Agents from Collaborative Agentic Systems: A Comprehensive Framework for Understanding Modern Intelligent Architectures](https://arxiv.org/abs/2506.01438) `[ARCH]` `[SURVEY]` `cs.AI` `cs.MA`
  - Framework for understanding the distinction between autonomous AI agents and collaborative agentic systems
  - Cross-ref: 2508.10146 (framework architectures), 2505.10468 (conceptual taxonomy)

## 2025-05

- [[2505.23135] VERINA: A Benchmark for Code Verification and Proof Generation](https://arxiv.org/abs/2505.23135) `[BENCH]` `[CODE]` `cs.SE`
  - Code verification and automated proof generation benchmark
- [[2505.18878] CRMArena-Pro: Expanded Business Scenario Diversity](https://arxiv.org/abs/2505.18878) `[BENCH]` `[SPEC]` `cs.AI`
  - Extended CRM benchmark with expanded business scenario coverage
- [[2505.21298] Large Language Models Miss the Multi-Agent Mark](https://arxiv.org/abs/2505.21298) `[MAS]` `[EVAL]` `cs.AI` `cs.CL`
  - Analysis of LLM limitations in multi-agent scenarios with evaluation of collaborative performance gaps
  - Cross-ref: 2503.01935 (MultiAgentBench), 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms)
- [[2505.18646] SEW: Self-Evolving Agentic Workflows for Automated Code Generation](https://arxiv.org/abs/2505.18646) `[CODE]` `[AUTO]` `cs.SE` `cs.AI`
  - Self-evolving framework automatically generating and optimizing multi-agent workflows without hand-crafted designs
  - Cross-ref: 2508.00083 (code generation survey), 2507.21046 (self-evolving survey), 2408.08435 (automated design)
- [[2505.12371] MedAgentBoard: Benchmarking Multi-Agent Collaboration with Conventional Methods for Diverse Medical Tasks](https://arxiv.org/abs/2505.12371) `[BENCH]` `[MAS]` `[SPEC]` `cs.AI` `cs.CL`
  - Comprehensive medical benchmark for multi-agent collaboration across visual QA, lay summaries, EHR prediction, and workflow automation
  - Cross-ref: 2507.16940 (AURA medical), 2508.21803 (clinical problem detection), 2507.05178 (CREW)
- [[2505.22967] MermaidFlow: Redefining Agentic WorkflowGeneration via Safety-Constrained EvolutionaryProgramming](https://arxiv.org/abs/2505.22967), [gh/chengqiArchy/MermaidFlow](https://github.com/chengqiArchy/MermaidFlow) `[AUTO]` `[SAFETY]`
  - Safety-constrained evolutionary programming approach for agentic workflow generation
  - Cross-ref: 2408.08435 (automated design), 2507.21046 (self-evolving survey)
- [[2505.10468] AI Agents vs. Agentic AI: A Conceptual Taxonomy, Applications and Challenges](https://arxiv.org/abs/2505.10468) `[SURVEY]` `[ARCH]` `cs.AI` `cs.CY`
  - Comprehensive conceptual taxonomy distinguishing AI agents from agentic AI with application analysis
  - Cross-ref: 2506.01438 (architectural frameworks), 2308.11432 (foundational agent survey)
- [[2405.17935] Tool Learning with Foundation Models](https://arxiv.org/abs/2405.17935) `[TOOL]` `[SURVEY]`
  - Comprehensive survey of tool learning capabilities in foundation models and LLMs for agentic applications
- [[2505.22954] Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) `[ARCH]` `[AUTO]`
  - Framework for open-ended evolution of self-improving AI agents based on Gödel machine principles
  - Cross-ref: 2507.21046 (self-evolving survey), 2408.01768 (living systems)
- [[2505.22583] GitGoodBench: A Novel Benchmark For Evaluating Agentic PerformanceOn Git](https://arxiv.org/abs/2505.22583), [infodeepseek.github.io](https://infodeepseek.github.io/) `[BENCH]` `[CODE]`
  - Benchmark for evaluating AI agent performance on Git version control tasks and workflows
  - Cross-ref: 2308.03688 (AgentBench), 2404.06411 (AgentQuest)
- [[2505.19764] Agentic Predictor: Performance Prediction for Agentic Workflows via Multi-View Encoding](https://arxiv.org/abs/2505.19764) `[EVAL]` `[ARCH]`
  - System for predicting agent performance in complex workflows using multi-view encoding techniques
  - Cross-ref: 2411.13768 (evaluation-driven), 2410.22457 (workflow metrics)
- [[2505.18946] SANNet: A Semantic-Aware Agentic AI Networking Framework for Multi-Agent Cross-Layer Coordination](https://arxiv.org/abs/2505.18946) `[MAS]` `[ARCH]`
  - Networking framework for semantic-aware coordination in multi-agent AI systems
  - Cross-ref: 2507.05178 (collaboration benchmark), 2501.06322 (collaboration mechanisms)
- [[2505.15872] InfoDeepSeek: Benchmarking Agentic InformationSeeking for Retrieval-Augmented Generation](https://arxiv.org/abs/2505.15872) `[BENCH]` `[TOOL]`
  - Benchmark for evaluating agentic information-seeking capabilities in RAG systems
  - Cross-ref: 2410.09713 (agentic IR), 2507.10584 (compliance RAG)
- [[2505.18705] AI-Researcher: Fully Autonomous Research System from Literature Review to Publication](https://arxiv.org/abs/2505.18705), [gh/HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) `[RESEARCH]` `[AUTO]` **NeurIPS 2025 Spotlight**
  - Fully autonomous AI research system transforming scientific discovery from literature review to publication-ready manuscripts
  - Features Writer Agent for automatic paper generation and Scientist-Bench for systematic research quality evaluation
  - Cross-ref: 2408.14033 (MLR-Copilot), 2501.10120 (PaSa), 2509.06917 (Paper2Agent)

## 2025-04

- [[2504.05559] SciSciGPT: Advancing Human-AI Collaboration in the Science of Science](https://arxiv.org/abs/2504.05559) `[SCI]` `[ARCH]` `[MAS]` `cs.AI` `cs.DL`
  - Open-source AI collaborator with LLM Agent capability maturity model for human-AI research partnerships
  - Cross-ref: 2506.18096 (deep research agents), 2509.06917 (Paper2Agent), 2508.00414 (cognitive kernel)
- [[2504.01382] Online-Mind2Web: Live Web Task Evaluation Benchmark](https://arxiv.org/abs/2504.01382) `[BENCH]` `[TOOL]` `cs.AI`
  - Live web agent evaluation with 300 real-world tasks
- [[2504.14064] DoomArena: Security Threat Testing for Agent Frameworks](https://arxiv.org/abs/2504.14064) `[BENCH]` `[SAFETY]` `cs.CR`
  - Security benchmark testing agent framework vulnerabilities and threat resilience
- [[2504.18575] WASP: Prompt Injection Attack Resilience Benchmark](https://arxiv.org/abs/2504.18575) `[BENCH]` `[SAFETY]` `cs.CR`
  - Benchmark for evaluating agent resilience to prompt injection attacks
- [[2504.17192] Paper2Code: Automating Code Generation from Scientific Papers in Machine Learning](https://arxiv.org/abs/2504.17192) `[CODE]` `[SCI]` `[AUTO]` `cs.SE` `cs.AI`
  - Multi-agent framework transforming ML papers into functional code with planning, analysis, and modular generation
  - Cross-ref: 2509.06917 (Paper2Agent), 2508.00083 (code generation survey), 2505.18705 (AI-Researcher)
- [[2504.19678] From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review](https://arxiv.org/abs/2504.19678)
  - Comprehensive review of the evolution from LLM reasoning to fully autonomous AI agents
- [[2504.16902] Building A Secure Agentic AI ApplicationLeveraging Google's A2A Protocol](https://arxiv.org/abs/2504.16902)
  - Guide for building secure agentic AI applications using Google's Agent-to-Agent protocol

## 2025-03

- [[2503.23037] Agentic Large Language Models, a survey](https://arxiv.org/abs/2503.23037) `[SURVEY]` `[ARCH]` `cs.AI` `cs.CL`
  - Survey of agentic LLMs showing mutual benefits across retrieval, tool use, reflection, reasoning, and multi-agent collaboration
  - Cross-ref: 2503.21460 (LLM agent survey), 2308.11432 (foundational survey), 2510.09244 (fundamentals)
- [[2503.01935] MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents](https://arxiv.org/abs/2503.01935) `[BENCH]` `[MAS]` `[EVAL]` `cs.AI` `cs.MA`
  - Comprehensive benchmark for multi-agent systems measuring collaboration and competition quality across diverse coordination protocols
  - Cross-ref: 2507.05178 (CREW benchmark), 2512.08296 (scaling agent systems), 2501.06322 (collaboration mechanisms)
- [[2503.21460] Large Language Model Agent: A Survey on Methodology, Applications and Challenges](https://arxiv.org/abs/2503.21460) `[SURVEY]` `[ARCH]`
  - Comprehensive survey of LLM agents covering methodology, applications, and current challenges
  - Cross-ref: 2308.11432 (foundational survey), 2404.11584 (architecture landscape)
- [[2503.16416] Survey on Evaluation of LLM-based Agents](https://arxiv.org/abs/2503.16416) `[SURVEY]` `[EVAL]`
  - Survey of evaluation methods and benchmarks for LLM-based agent systems
  - Cross-ref: 2411.13768 (evaluation-driven), 2507.02825 (benchmark best practices)
- [[2503.14713] TestForge: Feedback-Driven, Agentic Test Suite Generation](https://arxiv.org/abs/2503.14713) `[AUTO]` `[CODE]`
  - Agentic system for automated test suite generation using feedback-driven approaches
  - Cross-ref: 2410.14393 (debug agents), 2402.01030 (executable code)
- [[2503.13657] Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) `[MAS]` `[SAFETY]`
  - Analysis of failure modes and challenges in multi-agent LLM systems
  - Cross-ref: 2507.05178 (MAS benchmarking), 2506.04133 (TRiSM safety)
- [[2503.08979] AGENTIC AI FOR SCIENTIFIC DISCOVERY: A SURVEY OF PROGRESS, CHALLENGES, AND FUTURE DIRECTION](https://arxiv.org/abs/2503.08979) `[SCI]` `[SURVEY]`
  - Survey of agentic AI applications in scientific discovery with progress assessment and future directions
  - Cross-ref: 2408.06292 (AI scientist), 2506.18096 (deep research agents)
- [[2503.06416] Advancing AI Negotiations:New Theory and Evidence from a Large-ScaleAutonomous Negotiation Competition](https://arxiv.org/abs/2503.06416) `[MAS]` `[BENCH]`
  - Theory and empirical evidence from large-scale autonomous agent negotiation competitions
  - Cross-ref: 2507.05178 (collaboration benchmark), 2501.06322 (collaboration mechanisms)
- [[2503.00237] Agentic AI Needs a Systems Theory](https://arxiv.org/abs/2503.00237) `[ARCH]` `[SURVEY]`
  - Argument for developing systems theory approaches to understand and design agentic AI
  - Cross-ref: 2404.11584 (architecture landscape), 2503.21460 (methodology survey)

## 2025-02

- [[2502.06559] Can We Trust AI Benchmarks? An Interdisciplinary Review](https://arxiv.org/abs/2502.06559) `[BENCH]` `[EVAL]` `[SURVEY]` `cs.AI`
  - Interdisciplinary review of ~100 studies on benchmark shortcomings: dataset biases, data contamination, construct validity, and gaming
  - Cross-ref: 2507.02825 (agentic benchmark checklist), 2308.03688 (AgentBench)
- [[2502.12110] A-Mem: Agentic Memory for LLM Agents](https://arxiv.org/abs/2502.12110) `[MEM]` `[ARCH]` `cs.AI` `cs.CL`
  - Autonomous memory system with contextual description generation and connection establishment for continuous evolution
  - Cross-ref: 2512.13564 (memory survey), 2601.01885 (agentic memory), 2512.18950 (MACLA)
- [[2502.14776] SurveyX: Academic Survey Automation via Large Language Models](https://arxiv.org/abs/2502.14776) `[AUTO]` `[SCI]`
  - Framework for automating academic survey generation and literature review using LLMs
  - Cross-ref: 2506.18096 (deep research agents), 2501.04227 (research assistants)
- [[2502.05957] AutoAgent: A Fully-Automated and Zero-Code Framework for LLM Agents](https://arxiv.org/abs/2502.05957) `[AUTO]` `[ARCH]`
  - Zero-code framework for creating and deploying LLM agents without programming requirements
  - Cross-ref: 2412.04093 (practical considerations), 2501.00881 (industry guide)
- [[2502.02649] Fully Autonomous AI Agents Should Not be Developed](https://arxiv.org/abs/2502.02649) `[SAFETY]` `[SURVEY]`
  - Position paper arguing against development of fully autonomous AI agents with safety considerations
  - Cross-ref: 2302.10329 (harms analysis), 2402.04247 (safeguarding priority)

## 2025-01

- [[2501.14654] MedAgentBench: Benchmark for Virtual EHR Healthcare Workflows](https://arxiv.org/abs/2501.14654) `[BENCH]` `[SPEC]` `cs.AI`
  - Healthcare agent benchmark evaluating performance on virtual electronic health record workflows
- [[2501.11067] IntellAgent: A Multi-Agent Framework for Evaluating Conversational AI Systems](https://arxiv.org/abs/2501.11067), [gh/plurai-ai/intellagent](https://github.com/plurai-ai/intellagent) `[EVAL]` `[MAS]` `[BENCH]` `cs.AI` `cs.CL`
  - Multi-agent framework for comprehensive diagnosis and optimization of conversational agents using simulated realistic synthetic interactions
  - Provides systematic evaluation methodology to uncover agent blind spots and improve performance
  - Cross-ref: 2503.16416 (evaluation survey), 2507.02825 (benchmark best practices), 2411.13768 (evaluation-driven)
- [[2501.17112] Decoding Human Preferences in Alignment: An Improved Approach to Inverse Constitutional AI](https://arxiv.org/abs/2501.17112) `[SAFETY]` `[ARCH]` `cs.AI` `cs.LG`
  - Improved approach for inverse constitutional AI and human preference alignment in agent systems
  - Cross-ref: 2406.07814 (collective constitutional AI), 2212.08073 (foundational constitutional AI)
- [[2501.10114] Infrastructure for AI Agents](https://arxiv.org/abs/2501.10114) `[ARCH]` `[COMP]` `cs.AI` `cs.SE`
  - Infrastructure requirements and protocols for deploying AI agents in production environments
  - Cross-ref: 2508.10146 (framework architectures), 2412.04093 (practical considerations)
- [[2501.16150] AI Agents for Computer Use: A Review of Instruction-based Computer Control, GUI Automation, and Operator Assistants](https://arxiv.org/abs/2501.16150) `[SURVEY]` `[SPEC]`
  - Review of AI agents for computer control, GUI automation, and operator assistance systems
  - Cross-ref: 2410.14393 (debug agents), 2503.14713 (test generation)
- [[2501.06590] ChemAgent](https://arxiv.org/abs/2501.06590) `[SCI]` `[SPEC]`
  - AI agent system specialized for chemistry research and chemical compound analysis
  - Cross-ref: 2507.17311 (EarthLink climate), 2507.16940 (AURA medical)
- [[2501.06322] Multi-Agent Collaboration Mechanisms: A Survey of LLMs](https://arxiv.org/abs/2501.06322) `[MAS]` `[SURVEY]`
  - Survey of collaboration mechanisms in multi-agent LLM systems and coordination strategies
  - Cross-ref: 2507.05178 (CREW benchmark), 2503.06416 (negotiation competition)
- [[2501.04227] Agent Laboratory: Using LLM Agents as Research Assitants](https://arxiv.org/abs/2501.04227), [AgentRxiv:Towards Collaborative Autonomous Research](https://agentrxiv.github.io/) `[SCI]` `[ARCH]`
  - Framework for using LLM agents as research assistants in academic and scientific workflows
  - Cross-ref: 2506.18096 (deep research agents), 2502.14776 (SurveyX)
- [[2501.00881] Agentic Systems: A Guide to Transforming Industries with Vertical AI Agents](https://arxiv.org/abs/2501.00881) `[SPEC]` `[SURVEY]`
  - Guide for implementing vertical AI agents across different industries and use cases
  - Cross-ref: 2412.04093 (practical considerations), 2408.06361 (financial trading)
- [[2501.10120] PaSa: LLM-Powered Paper Search Agent with Reinforcement Learning](https://arxiv.org/abs/2501.10120) `[RESEARCH]` `[TOOL]`
  - LLM-powered paper search agent using reinforcement learning trained on AutoScholarQuery dataset with 35k academic queries
  - Autonomous search workflow with tool invocation, paper reading, and reference filtering for comprehensive scholarly search
  - Cross-ref: 2505.18705 (AI-Researcher), 2312.07559 (PaperQA), 2501.04227 (Agent Laboratory)

## 2024-12

- [[2412.14470] Agent-SafetyBench: Evaluating the Safety of LLM Agents](https://arxiv.org/abs/2412.14470) `[BENCH]` `[SAFETY]` `[EVAL]` `cs.AI` `cs.CL`
  - Safety benchmark with 349 interaction environments and 2,000 test cases evaluating 8 risk categories and 10 failure modes
  - Cross-ref: 2412.13178 (SafeAgentBench), 2507.06134 (OpenAgentSafety), 2402.05044 (SALAD-Bench)
- [[2412.14161] TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks](https://arxiv.org/abs/2412.14161) `[BENCH]` `[EVAL]` `cs.AI` `cs.SE`
  - Benchmark testing agents in simulated software company environment with real-world consequential tasks
  - Cross-ref: 2509.10769 (AgentArch enterprise), 2511.14136 (CLEAR framework), 2308.03688 (AgentBench)
- [[2412.13178] SafeAgentBench: A Benchmark for Safe Task Planning of Embodied LLM Agents](https://arxiv.org/abs/2412.13178) `[BENCH]` `[SAFETY]` `[SPEC]` `cs.AI` `cs.RO`
  - First comprehensive benchmark for safety-aware task planning with 750 tasks covering 10 hazards in embodied agents
  - Cross-ref: 2412.14470 (Agent-SafetyBench), 2507.06134 (OpenAgentSafety), 2512.20798 (constraint violations)
- [[2412.17149] A Multi-AI Agent System for Autonomous Optimization of Agentic AISolutions via Iterative Refinement and LLM-Driven Feedback Loop](https://arxiv.org/abs/2412.17149) `[MAS]` `[AUTO]`
  - Multi-agent system for autonomous optimization of agentic AI solutions using iterative refinement and LLM feedback loops
  - Cross-ref: 2408.08435 (automated design), 2507.18074 (architecture discovery)
- [[2412.04093] Practical Considerations for Agentic LLM Systems](https://arxiv.org/abs/2412.04093) `[ARCH]` `[COMP]`
  - Practical guidance for implementing and deploying agentic LLM systems in production
  - Cross-ref: 2411.05285 (agentops taxonomy), 2502.05957 (AutoAgent)
- [[2412.05467] BrowserGym: A Gym Environment for Web Task Automation](https://arxiv.org/abs/2412.05467) `[BENCH]` `[TOOL]` `cs.AI`
  - Web agent benchmarking ecosystem with standardized evaluation framework
- [[2412.17259] LegalAgentBench: Evaluating LLM Agents in Legal Domain](https://arxiv.org/abs/2412.17259) `[BENCH]` `[SPEC]` `cs.CL`
  - Benchmark for evaluating agents in Chinese legal domain tasks

## 2024-11

- [[2411.13768] Evaluation-driven Approach to LLM Agents](https://arxiv.org/abs/2411.13768) `[EVAL]` `[ARCH]`
  - Framework for designing and improving LLM agents through evaluation-driven development
  - Cross-ref: 2503.16416 (comprehensive evaluation taxonomy), 2507.17257 (specific identity evaluation methods)
- [[2411.13543] BALROG: BENCHMARKING AGENTIC LLM ANDVLM REASONING ON GAMES](https://arxiv.org/abs/2411.13543) `[BENCH]` `[EVAL]`
  - Benchmark for evaluating agentic reasoning capabilities of LLMs and VLMs in game environments
  - Cross-ref: 2308.03688 (foundational agent benchmarking), 2404.06411 (modular benchmark design)
- [[2411.10478] Large Language Models for Constructing and Optimizing Machine Learning Workflows: A Survey](https://arxiv.org/abs/2411.10478) `[AUTO]` `[SURVEY]`
  - Survey of LLMs for automated machine learning workflow construction and optimization
  - Cross-ref: 2506.16499 (practical ML automation), 2507.18074 (automated architecture search)
- [[2411.00927] ReSpAct: Harmonizing Reasoning, Speaking, and Acting Towards Building Large Language Model-Based Conversational AI Agents](https://arxiv.org/abs/2411.00927) `[ARCH]` `[PLAN]` `cs.AI` `cs.CL`
  - Extension of ReAct framework for conversational AI agents with integrated reasoning, speaking, and acting
  - Cross-ref: 2210.03629 (foundational ReAct), 2403.14589 (ReAct training autonomy)
- [[2411.05285] A taxonomy of agentops for enabling observability of foundation model based agents](https://arxiv.org/abs/2411.05285) `[COMP]` `[ARCH]`
  - Taxonomy and framework for observability and operations of foundation model-based agents
  - Cross-ref: 2412.04093 (practical considerations), 2507.10584 (compliance RAG)
- [[2411.07763] Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows](https://arxiv.org/abs/2411.07763) `[BENCH]` `[SPEC]` `cs.DB`
  - Enterprise text-to-SQL benchmark with real-world database workflows
- [[2411.02305] CRMArena: Understanding the Capacity of LLM Agents to Perform Professional CRM Tasks](https://arxiv.org/abs/2411.02305) `[BENCH]` `[SPEC]` `cs.AI`
  - Benchmark for evaluating agents on enterprise CRM professional scenarios

## 2024-10

- [[2410.09024] AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024) `[BENCH]` `[SAFETY]` `[EVAL]` `cs.AI` `cs.CR`
  - Benchmark measuring harmful behaviors in LLM agents across malicious and benign agentic scenarios
  - Accepted at ICLR 2025
  - Cross-ref: 2512.20798 (constraint violations), 2507.06134 (OpenAgentSafety), 2510.23883 (agentic AI security)
- [[2410.22457] Advancing Agentic Systems: Dynamic Task Decomposition, Tool Integration and Evaluation using Novel Metrics and Dataset](https://arxiv.org/abs/2410.22457) `[EVAL]` `[TOOL]` `[PLAN]`
  - Framework for dynamic task decomposition and tool integration in agentic systems with evaluation metrics
  - Cross-ref: 2405.17935 (foundational tool learning theory), 2402.02716 (planning mechanism foundations)
- [[2410.14393] Debug Smarter, Not Harder: AI Agents for Error Resolution in Computational Notebooks](https://arxiv.org/abs/2410.14393) `[CODE]` `[AUTO]`
  - AI agents for automated debugging and error resolution in computational notebook environments
  - Cross-ref: 2503.14713 (automated testing synergy), 2402.01030 (executable code foundations)
- [[2410.07959] Compl-AI Framework: A Technical Interpretation and LLM Benchmarking](https://arxiv.org/abs/2410.07959) `[BENCH]` `[COMP]`
  - Technical framework for interpreting and benchmarking LLM compliance and capabilities
  - Cross-ref: 2411.05285 (observability framework overlap), 2412.04093 (deployment considerations)
- [[2410.06703] ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents](https://arxiv.org/abs/2410.06703) `[BENCH]` `[SAFETY]` `cs.AI` `cs.CR`
  - Benchmark for evaluating safety and trustworthiness of web agents in enterprise environments
  - Cross-ref: 2307.13854 (WebArena foundation), 2401.13649 (VisualWebArena)
- [[2410.04444] Gödel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement](https://arxiv.org/abs/2410.04444) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - Self-referential framework inspired by Gödel machines enabling recursive self-improvement without predefined routines
  - Cross-ref: 2505.22954 (Darwin Godel Machine), 2508.15805 (ALAS autonomous learning)
- [[2410.02810] StateAct: State Tracking and Reasoning for Acting and Planning with Large Language Models](https://arxiv.org/abs/2410.02810) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - Framework for state tracking and reasoning in LLM-based agents for improved planning and acting
  - Cross-ref: 2210.03629 (ReAct foundation), 2310.04406 (LATS reasoning)
- [[2410.09713] Agentic Information Retrieval](https://arxiv.org/abs/2410.09713) `[TOOL]` `[ARCH]`
  - Framework for agentic approaches to information retrieval and knowledge discovery
  - Cross-ref: 2505.15872 (InfoDeepSeek), 2507.10584 (policy compliance RAG)
- [[2408.08435] AUTOMATED DESIGN OF AGENTIC SYSTEMS](https://arxiv.org/abs/2408.08435) `[AUTO]` `[ARCH]`
  - Automated methodology for designing and optimizing agentic AI systems
  - Cross-ref: 2507.18074 (architecture discovery), 2506.16499 (ML-Master)
- [[2408.01768] Building Living Software Systems with Generative & Agentic AI](https://arxiv.org/abs/2408.01768) `[ARCH]` `[AUTO]`
  - Approach for creating self-evolving software systems using generative and agentic AI
  - Cross-ref: 2507.21046 (self-evolving survey), 2505.22954 (Darwin Godel)

## 2024-09

- [[2409.11363] CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark](https://arxiv.org/abs/2409.11363) `[BENCH]` `[SCI]` `[EVAL]` `cs.AI`
  - Computational reproducibility benchmark for assessing agent ability to verify research claims
  - Cross-ref: 2407.13168 (SciCode), 2412.14161 (TheAgentCompany)

## 2024-08

- [[2408.14033] MLR-Copilot: Autonomous Machine Learning Research Framework](https://arxiv.org/abs/2408.14033), [gh/du-nlp-lab/MLR-Copilot](https://github.com/du-nlp-lab/MLR-Copilot) `[RESEARCH]` `[AUTO]`
  - Autonomous machine learning research framework with three-phase pipeline for idea generation, implementation, and validation
  - Mimics researchers' thought processes for systematic ML research automation and executable research contributions
  - Cross-ref: 2505.18705 (AI-Researcher), 2501.10120 (PaSa), 2408.06292 (AI Scientist)
- [[2408.06361] Large Language Model Agent in Financial Trading: A Survey](https://arxiv.org/abs/2408.06361)
  - Survey of LLM agents in financial trading applications and market analysis
- [[2408.06292] The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery](https://arxiv.org/abs/2408.06292)
  - Framework for fully automated scientific discovery using AI agents
- [[2408.08632] A Survey on Benchmarks of Multimodal Large Language Models](https://arxiv.org/abs/2408.08632) `[BENCH]` `[SURVEY]`
  - Comprehensive survey of benchmarks for evaluating multimodal LLMs and their capabilities
  - Cross-ref: 2411.13543 (BALROG games), 2507.16940 (AURA multimodal)
- [[2408.02205] A Taxonomy of Multi-layered Runtime Guardrails for Designing Foundation Model-based Agents: Swiss Cheese Model for AI Safety by Design](https://arxiv.org/abs/2408.02205) `[SAFETY]` `[ARCH]`
  - Taxonomy of multi-layered runtime guardrails for safe foundation model-based agent design using Swiss cheese safety model
  - Cross-ref: 2508.03858 (governance protocol), 2506.04133 (TRiSM)

## 2024-07

- [[2407.13168] SciCode: A Research Coding Benchmark Curated by Scientists](https://arxiv.org/abs/2407.13168) `[BENCH]` `[CODE]` `[SCI]` `cs.AI` `cs.SE`
  - Scientific domain code problems requiring research-level understanding
  - Cross-ref: 2507.15003 (SE 3.0), 2508.00083 (code generation survey)
- [[2407.18901] AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents](https://arxiv.org/abs/2407.18901) `[BENCH]` `[CODE]` `cs.SE`
  - Multi-app coding agent benchmark with controllable environments
- [[2407.18416] PersonaGym: Evaluating Persona Agents and LLMs](https://arxiv.org/abs/2407.18416) `[BENCH]` `[SPEC]` `cs.CL`
  - Benchmark for persona-following agent evaluation
- [[2407.13943] Werewolf Arena: Strategic Reasoning in LLM Agents](https://arxiv.org/abs/2407.13943) `[BENCH]` `[SPEC]` `cs.AI`
  - Social deduction game benchmark for strategic reasoning assessment
- [[2407.18219] Recursive Introspection: Teaching Language Model Agents How to Self-Improve](https://arxiv.org/abs/2407.18219) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - RISE framework for fine-tuning LLMs to introduce recursive introspection and self-improvement capabilities
  - Cross-ref: 2405.06682 (self-reflection effects), 2410.04444 (Gödel Agent recursive)

## 2024-06

- [[2406.12045] τ-bench: A Benchmark for Tool-Agent-User Interaction](https://arxiv.org/abs/2406.12045) `[BENCH]` `[TOOL]` `[EVAL]` `cs.AI` `cs.CL`
  - Benchmark evaluating agents on tool use, user interaction, and domain-specific rule adherence; introduces pass^k consistency metric
  - Cross-ref: 2506.07982 (τ²-bench), 2307.16789 (ToolLLM), 2308.03688 (AgentBench)
- [[2406.01495] Re-ReST: Reflection-Reinforced Self-Training for Language Agents](https://arxiv.org/abs/2406.01495) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - Reflection-reinforced self-training approach using environmental feedback to enhance sample quality and agent performance
  - Cross-ref: 2303.11366 (Reflexion foundation), 2407.18219 (recursive introspection)

## 2024-05

- [[2405.06682] Self-Reflection in LLM Agents: Effects on Problem-Solving Performance](https://arxiv.org/abs/2405.06682) `[AUTO]` `[EVAL]` `cs.AI` `cs.CL`
  - Empirical study demonstrating significant improvement in problem-solving through self-reflection mechanisms
  - Cross-ref: 2407.18219 (recursive introspection), 2303.11366 (Reflexion framework)

## 2024-04

- [[2404.07972] OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972) `[BENCH]` `[EVAL]` `[TOOL]` `cs.AI`
  - Comprehensive OS/web task benchmark across multiple applications with real-world grounding
  - Cross-ref: 2307.13854 (WebArena), 2412.14161 (TheAgentCompany), 2401.13649 (VisualWebArena)
- [[2404.13501] A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501) `[MEM]` `[SURVEY]`
  - Survey of memory mechanisms and architectures in LLM-based agent systems
  - Cross-ref: 2507.16940 (complex reasoning memory needs), 2503.21460 (broader agent architecture context)
- [[2404.11584] Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling](https://arxiv.org/abs/2404.11584) `[ARCH]` `[SURVEY]` `[PLAN]` `[TOOL]`
  - Survey of emerging AI agent architectures focusing on reasoning, planning, and tool calling capabilities
  - Cross-ref: 2405.17935 (tool integration foundations), 2402.02716 (planning mechanism details)
- [[2404.06411] AgentQuest: A Modular Benchmark Framework to Measure Progress and Improve LLM Agents](https://arxiv.org/abs/2404.06411) `[BENCH]` `[EVAL]`
  - Modular benchmark framework for measuring progress and improvement in LLM agent capabilities
  - Cross-ref: 2308.03688 (comprehensive benchmarking precedent), 2401.13178 (multi-turn evaluation focus)
- [[2404.10952] Can Language Models Solve Olympiad Programming?](https://arxiv.org/abs/2404.10952) `[BENCH]` `[CODE]` `cs.AI`
  - USACO benchmark for programming competition problem-solving

## 2024-02

- [[2402.05044] SALAD-Bench: A Hierarchical and Comprehensive Safety Benchmark for Large Language Models](https://arxiv.org/abs/2402.05044) `[BENCH]` `[SAFETY]` `[EVAL]` `cs.CL` `cs.AI`
  - Hierarchical safety benchmark with large scale, rich diversity, and intricate three-level taxonomy
  - Accepted at ACL 2024 (Findings)
  - Cross-ref: 2412.14470 (Agent-SafetyBench), 2507.06134 (OpenAgentSafety), 2510.23883 (agentic AI security)
- [[2402.06360] CoSearchAgent: A Lightweight Collaborative Search Agent with Large Language Models](https://arxiv.org/abs/2402.06360) `[TOOL]` `[MAS]`
  - Lightweight collaborative search agent system using LLMs for information retrieval
  - Cross-ref: 2410.09713 (agentic IR), 2505.15872 (InfoDeepSeek)
- [[2402.04247] Prioritizing Safeguarding Over Autonomy: Risks of LLM Agents for Science](https://arxiv.org/abs/2402.04247) `[SAFETY]` `[SCI]`
  - Analysis of safety risks and the need to prioritize safeguarding over autonomy in scientific LLM agents
  - Cross-ref: 2302.10329 (harms analysis), 2502.02649 (autonomy concerns)
- [[2402.02716] Understanding the planning of LLM agents: A survey](https://arxiv.org/abs/2402.02716) `[PLAN]` `[SURVEY]`
  - Survey of planning mechanisms and strategies in LLM-based agent systems
  - Cross-ref: 2404.11584 (reasoning architectures), 2508.03682 (self-questioning)
- [[2402.01030] Executable Code Actions Elicit Better LLM Agents](https://arxiv.org/abs/2402.01030) `[CODE]` `[ARCH]`
  - Framework showing how executable code actions improve LLM agent performance
  - Cross-ref: 2507.22414 (code explanations), 2503.14713 (test generation)

## 2024-01

- [[2401.13178] AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents](https://arxiv.org/abs/2401.13178) `[BENCH]` `[EVAL]`
  - Analytical evaluation framework for multi-turn interactions and performance assessment of LLM agents
  - Cross-ref: 2308.03688 (broader agent evaluation scope), 2404.06411 (modular evaluation approach)

## 2023-08

- [[2308.11432] A Survey on Large Language Model based Autonomous Agents](https://arxiv.org/abs/2308.11432) `[SURVEY]` `[ARCH]` `cs.AI` `cs.CL`
  - Foundational survey of LLM-based autonomous agents, covering architecture, capabilities, and applications
  - Cross-ref: 2503.21460 (methodology evolution), 2404.11584 (architectural advances)
- [[2308.03688] AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) `[BENCH]` `[EVAL]` `cs.AI` `cs.CL`
  - Comprehensive benchmark for evaluating LLMs as autonomous agents across diverse tasks and environments
  - Cross-ref: 2404.06411 (modular benchmark evolution), 2401.13178 (multi-turn evaluation specialization)

## 2023-04

- [[2304.08244] API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs](https://arxiv.org/abs/2304.08244) `[BENCH]` `[TOOL]` `[EVAL]` `cs.CL` `cs.AI`
  - Comprehensive benchmark with 73 API tools, 314 tool-use dialogues, and 753 API calls for evaluating planning, retrieval, and calling
  - Published at EMNLP 2023; includes 1,888 training dialogues from 2,138 APIs across 1,000 domains
  - Cross-ref: 2307.16789 (ToolLLM), 2310.03128 (MetaTool), 2405.17935 (tool learning survey)
- [[2304.05376] ChemCrow: LLM Chemistry Agent with Expert-Designed Tools](https://arxiv.org/abs/2304.05376) `[RESEARCH]` `[SCI]` `[TOOL]`
  - LLM chemistry agent augmented with 18 expert-designed tools for organic synthesis, drug discovery, and materials design
  - Autonomous synthesis planning and execution with emergent capabilities from tool combination
  - Cross-ref: 2310.10632 (BioPlanner), 2501.06590 (ChemAgent), 2505.18705 (AI-Researcher)

## 2023-03

- [[2303.11366] Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) `[AUTO]` `[ARCH]` `cs.AI` `cs.CL`
  - Foundational framework for self-reflective agents using verbal reinforcement learning and iterative improvement
  - Cross-ref: 2405.06682 (self-reflection effects), 2406.01495 (Re-ReST extension)

## 2023-02

- [[2302.10329] Harms from Increasingly Agentic Algorithmic Systems](https://arxiv.org/abs/2302.10329) `[SAFETY]` `[SURVEY]`
  - Analysis of potential harms and risks from increasingly autonomous algorithmic systems
  - Cross-ref: 2508.03858 (governance solutions), 2506.04133 (risk management framework)

## 2023-07

- [[2307.16789] ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs](https://arxiv.org/abs/2307.16789) `[TOOL]` `[BENCH]` `cs.AI` `cs.CL`
  - Framework for training LLMs to master real-world APIs with comprehensive tool benchmarking
  - Cross-ref: 2405.17935 (tool learning survey), 2406.12045 (τ-bench evaluation)
- [[2307.13854] WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) `[BENCH]` `[SPEC]` `cs.AI` `cs.HC`
  - Realistic web environment benchmark for evaluating autonomous agents on web-based tasks
  - Cross-ref: 2401.13649 (VisualWebArena), 2410.06703 (ST-WebAgentBench safety)

## 2023-10

- [[2310.10632] BioPlanner: Automated AI Approach for Protocol Planning in Biology](https://arxiv.org/abs/2310.10632), [gh/bioplanner/bioplanner](https://github.com/bioplanner/bioplanner) `[RESEARCH]` `[SCI]`
  - Automated protocol generation for biological experiments using LLMs with BIOPROT dataset of 9,000+ protocols
  - Generates accurate experimental protocols from natural language with real-world laboratory validation
  - Cross-ref: 2505.18705 (AI-Researcher), 2304.05376 (ChemCrow), 2501.06590 (ChemAgent)
- [[2310.04406] Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models](https://arxiv.org/abs/2310.04406) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - LATS framework integrating Monte Carlo Tree Search with LM reasoning, acting, and planning capabilities
  - Cross-ref: 2210.03629 (ReAct foundation), 2410.02810 (StateAct)
- [[2310.03128] MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use](https://arxiv.org/abs/2310.03128) `[BENCH]` `[TOOL]` `cs.AI` `cs.CL`
  - Benchmark for evaluating LLM tool selection and usage decision-making capabilities
- [[2310.08367] Minecraft Gaming Agent Benchmark](https://arxiv.org/abs/2310.08367) `[BENCH]` `[SPEC]` `cs.AI`
  - Open-ended game environment for evaluating agent learning and exploration
  - Cross-ref: 2307.16789 (ToolLLM), 2406.12045 (τ-bench)

## 2023-12

- [[2312.07559] PaperQA: Open-Source RAG Agent for Scientific Literature Question Answering](https://arxiv.org/abs/2312.07559), [gh/Future-House/paper-qa](https://github.com/Future-House/paper-qa) `[RESEARCH]` `[TOOL]`
  - RAG agent for answering questions over scientific literature with hallucination reduction and provenance tracking
  - Information retrieval across full-text articles with source attribution for transparent evaluation evidence
  - Cross-ref: 2505.18705 (AI-Researcher), 2501.10120 (PaSa), 2509.06917 (Paper2Agent)

## 2023-11

- [[2311.12983] GAIA: a benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) `[BENCH]` `[EVAL]` `cs.AI` `cs.CL`
  - Benchmark with 466 real-world questions requiring reasoning, multi-modality, web browsing, and tool-use proficiency
  - Human performance: 92% vs GPT-4 with plugins: 15%; leaderboard at [https://huggingface.co/gaia-benchmark](https://huggingface.co/gaia-benchmark)
  - Cross-ref: 2308.03688 (AgentBench), 2404.06411 (AgentQuest), 2307.13854 (WebArena)

## 2022-12

- [[2212.08073] Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) `[SAFETY]` `[ARCH]` `cs.AI` `cs.LG`
  - Foundational constitutional AI approach for training harmless AI systems through AI feedback
  - Cross-ref: 2406.07814 (collective constitutional AI), 2501.17112 (inverse constitutional AI)

## 2022-10

- [[2210.03629] ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - Foundational ReAct framework for interleaving reasoning and acting in language model agents
  - Cross-ref: 2411.00927 (ReSpAct extension), 2310.04406 (LATS integration)

## 2022-07

- [[2207.01206] WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents](https://arxiv.org/abs/2207.01206) `[BENCH]` `[SPEC]` `cs.AI`
  - E-commerce web interaction benchmark for evaluating grounded language agents

## 2020-10

- [[2010.03768] ALFWorld: Aligning Text and Embodied Environments for Interactive Learning](https://arxiv.org/abs/2010.03768) `[BENCH]` `[SPEC]` `cs.AI`
  - Text-to-embodied task alignment benchmark for interactive agent learning

## Practitioner Resources

Industry blog posts and engineering articles providing implementation insights and production patterns.

- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) - Anthropic Engineering (2025)
  - Two-agent harness pattern: Initializer + Coding agents for context window management
  - Key patterns: JSON feature lists, git-based state tracking, incremental development
  - Failure modes: Premature completion, undocumented progress, testing gaps, setup confusion
  - Cross-ref: 2512.13564 (memory systems), 2509.25250 (long-running agents), 2510.01003 (repository memory)
- [Inspect AI](https://inspect.aisi.org.uk/) - UK AI Safety Institute (2025)
  - 100+ pre-built evaluations, three-component model (datasets, solvers, scorers)
  - Direct PydanticAI support, MCP integration, multi-agent compositions
  - Cross-ref: 2507.21504 (evaluation taxonomy), 2503.16416 (evaluation survey)
- [Bloom](https://github.com/safety-research/bloom) - Anthropic (2025)
  - Four-stage behavioral evaluation: Understanding → Ideation → Rollout → Judgment
  - Elicitation rate metric (≥7/10 threshold), meta-judge for suite-level analysis
  - Cross-ref: 2507.06134 (OpenAgentSafety), 2412.14470 (Agent-SafetyBench)
- [Petri](https://github.com/safety-research/petri) - Anthropic (2025)
  - Auditor/Target/Judge architecture for alignment auditing, built on Inspect AI
  - Multi-turn audits, transcript scoring (deception, oversight subversion, harmful content)
  - Cross-ref: 2410.09024 (AgentHarm), 2402.05044 (SALAD-Bench)
- [DeepEval AI Agent Evaluation Guide](https://deepeval.com/guides/guides-ai-agent-evaluation) - Confident AI (2025)
  - Three-layer evaluation model: Reasoning (plan quality/adherence), Action (tool/argument correctness), Execution (task completion/efficiency)
  - Component-level metric attachment via `@observe()` decorator pattern
  - GEval framework for custom LLM-as-Judge criteria using plain English definitions
  - Cross-ref: 2503.16416 (evaluation survey), 2507.21504 (LLM agents survey)
- [Pydantic Evals](https://ai.pydantic.dev/evals/) - Pydantic (2025)
  - Span-based evaluation using OpenTelemetry for internal agent behavior analysis
  - Loosely coupled framework evaluating any callable (not dependent on pydantic-ai)
  - Flexible scoring (0.0-1.0 float) with Logfire integration for web-based visualization
  - Philosophy: "Correctness depends on how the answer was reached, not just the final output"
  - Cross-ref: 2411.05285 (AgentOps observability taxonomy), 2503.16416 (evaluation survey)
- [Arize Phoenix Multi-Agent Evaluation](https://arize.com/docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems) - Arize (2025)
  - Three evaluation strategies: Agent Handoff, System-Level, Coordination
  - Multi-level metrics: Agent, Interaction, System, User performance measurement
  - Five coordination patterns: Network, Supervisor, Hierarchical, Tool-calling, Custom Workflow
  - Handoff evaluation: Appropriateness, information transfer, timing
  - Cross-ref: 2501.06322 (collaboration mechanisms), 2503.13657 (MAS failures), 2512.08296 (scaling agent systems)
- [Claude Evaluation Framework](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) - Anthropic (2025)
  - SMART success criteria (Specific, Measurable, Achievable, Relevant); grading hierarchy: Code-based (fastest) → LLM-based (nuanced) → Human (flexible)
  - Best practice: Volume over quality; encourage reasoning before scoring
  - Bloom correlation: Claude Opus 4.1 (0.86), Sonnet 4.5 (0.75) with human scores
  - Cross-ref: Bloom (alignment.anthropic.com), 2503.16416 (evaluation survey)
- [Pydantic Logfire](https://logfire.pydantic.dev/) - Pydantic (2025-2026)
  - First-party OpenTelemetry-based observability for PydanticAI agents via `logfire.instrument_pydantic_ai()`
  - Three instrumentation paths: Logfire cloud, raw OpenTelemetry with custom `TracerProvider`, or hybrid routing to alternative backends
  - Multi-language SDKs (Python, TypeScript, Rust); follows OpenTelemetry GenAI Semantic Conventions
  - Cross-ref: Pydantic Evals (above), 2602.10133 (AgentTrace), 2601.00481 (MAESTRO)
- [How to Build a Production Agentic App, the Pydantic Way](https://pydantic.dev/articles/building-agentic-application) - Pydantic (2026)
  - End-to-end guide combining Pydantic AI (agents), Logfire (observability), Pydantic Evals (evaluation), and FastAPI (serving)
  - Demonstrates full agentic stack: agent → instrument → evaluate → deploy pattern
  - Cross-ref: Pydantic Evals (above), Pydantic Logfire (above)
- [OpenTelemetry AI Agent Observability Blog](https://opentelemetry.io/blog/2025/ai-agent-observability/) - OpenTelemetry (2025)
  - Establishes need for standardized agent observability; covers OpenTelemetry GenAI semantic conventions for agent tracing
  - Cross-ref: 2508.02121 (AgentOps survey), 2602.10133 (AgentTrace)
- [OTel GenAI Agentic Systems Semantic Conventions Proposal](https://github.com/open-telemetry/semantic-conventions/issues/2664) - OpenTelemetry (2025)
  - Defines attributes for tracing tasks, actions, agents, teams, artifacts, and memory in OpenTelemetry
  - Standardizes telemetry across complex AI workflows for traceability, reproducibility, and analysis
  - Cross-ref: 2601.00481 (MAESTRO), 2602.10133 (AgentTrace)
- [otel-tui](https://github.com/ymtdzzz/otel-tui) - ymtdzzz (2025)
  - Terminal-based OpenTelemetry trace viewer; single binary accepting OTLP on ports 4317/4318
  - Zero-infrastructure local debugging; referenced in PydanticAI docs as alternative local backend
  - Cross-ref: Pydantic Logfire (above), Arize Phoenix (trace_observe_methods.md)
- [MITRE ATLAS](https://atlas.mitre.org/) - MITRE (2021-2026)
  - Adversarial Threat Landscape for Artificial-Intelligence Systems; ATT&CK-style framework for AI/ML threats
  - 2026 updates add agentic AI attack surfaces: runtime decision manipulation, credential abuse, tool misuse, AI Service API (AML.T0096)
  - Cross-ref: 2510.23883 (agentic AI security), 2506.04133 (TRiSM), OWASP MAESTRO (below)
- [OWASP MAESTRO Framework](https://genai.owasp.org/) - OWASP GenAI Security Project (2025)
  - Multi-Agent Environment, Security, Threat, Risk, and Outcome; 7-layer threat modeling for multi-agent systems
  - Applies OWASP ASI threat taxonomy to MAS: Tool Misuse, Intent Manipulation, Privilege Compromise; companion to MITRE ATLAS
  - Cross-ref: MITRE ATLAS (above), 2503.13657 (MAS failures), 2601.00911 (privacy-preserving agents)
- [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework) - NIST (2023)
  - Four core functions: Govern, Map, Measure, Manage for trustworthy AI lifecycle risk management
  - Flexible, voluntary framework; official crosswalk to ISO/IEC 42001 available from NIST
  - Cross-ref: ISO 42001 (below), ISO 23894 (below), 2506.04133 (TRiSM)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) - ISO/IEC (2023)
  - World's first AI management system standard; requirements for establishing, implementing, and maintaining an AIMS
  - Covers ethical considerations, transparency, continuous learning, auditability, and data handling
  - Cross-ref: NIST AI RMF (above), ISO 23894 (below)
- [ISO/IEC 23894:2023](https://www.iso.org/standard/77304.html) - ISO/IEC (2023)
  - AI risk management guidance; provides principles and processes for managing risk specific to AI systems
  - Complements ISO 42001 (management system) with focused risk assessment and treatment methodology
  - Cross-ref: ISO 42001 (above), NIST AI RMF (above)
