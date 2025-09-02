---
title: Further Reading - Research Papers
description: Comprehensive curated list of research papers and academic resources for AI agent evaluation with thematic tagging, cross-references, and clustering
date: 2025-09-02
category: research
version: 2.0.0
tags: [agentic-ai, evaluation, benchmarking, multi-agent-systems, safety, architecture, tool-use, planning, scientific-discovery, code-generation]
features:
  - chronological-organization
  - thematic-tagging
  - cross-references
  - relationship-explanations
  - clustering-by-themes
papers_count: 100+
coverage_period: 2022-10 to 2025-08
last_updated: 2025-09-02
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

- 100+ papers covering 2022-2025 research
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

- Key papers: 2308.03688 (AgentBench), 2404.06411 (AgentQuest), 2401.13178 (AgentBoard)
- Web agents: 2307.13854 (WebArena), 2401.13649 (VisualWebArena), 2410.06703 (ST-WebAgentBench)
- Tool evaluation: 2307.16789 (ToolLLM), 2310.03128 (MetaTool), 2406.12045 (τ-bench)
- 2411.13768 (evaluation-driven), 2507.17257 (identity evals), 2503.16416 (evaluation survey)

**Architecture & System Design** `[ARCH]`:

- Foundation: 2308.11432 (foundational survey), 2404.11584 (architecture landscape)
- Frameworks: 2508.10146 (agentic AI frameworks), 2501.10114 (infrastructure)
- Governance: 2508.03858 (governance protocol), 2503.00237 (systems theory)

**Safety & Risk Management** `[SAFETY]`:

- Constitutional AI: 2212.08073 (foundational), 2406.07814 (collective), 2501.17112 (inverse)
- Core: 2302.10329 (harms analysis), 2506.04133 (TRiSM), 2408.02205 (guardrails)
- Multi-agent: 2503.13657 (MAS failures), 2402.04247 (safeguarding over autonomy)

**Tool Use & Integration** `[TOOL]`:

- Benchmarks: 2307.16789 (ToolLLM), 2310.03128 (MetaTool), 2406.12045 (τ-bench)
- Surveys: 2405.17935 (tool learning), 2404.11584 (tool calling architectures)
- Applications: 2410.22457 (tool integration), 2410.09713 (agentic IR)

**Multi-Agent Systems** `[MAS]`:

- Collaboration: 2507.05178 (CREW benchmark), 2501.06322 (collaboration mechanisms)
- Analysis: 2503.13657 (failure analysis), 2507.02097 (recommender systems)

**Planning & Reasoning** `[PLAN]`:

- ReAct family: 2210.03629 (ReAct), 2411.00927 (ReSpAct), 2310.04406 (LATS)
- Core: 2402.02716 (planning survey), 2508.03682 (self-questioning)
- Applications: 2410.22457 (task decomposition), 2404.11584 (reasoning architectures)

**Scientific Discovery** `[SCI]`:

- Research agents: 2506.18096 (deep research), 2508.00414 (cognitive kernel)
- Discovery: 2408.06292 (AI scientist), 2503.08979 (scientific discovery survey)

**Code Generation** `[CODE]`:

- Explanations: 2507.22414 (symbolic explanations), 2402.01030 (executable actions)
- Applications: 2506.13131 (AlphaEvolve), 2410.14393 (debug agents)

**Self-Improvement & Reflection** `[AUTO]`:

- Self-reflection: 2303.11366 (Reflexion foundation), 2405.06682 (self-reflection effects)
- Recursive improvement: 2407.18219 (recursive introspection), 2410.04444 (Gödel Agent)
- Training approaches: 2406.01495 (Re-ReST), 2508.15805 (ALAS autonomous learning)
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

## 2025-08

- [[2508.15805] ALAS: Autonomous Learning Agent for Self-Updating Language Models](https://arxiv.org/abs/2508.15805) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - Autonomous learning framework for continuous self-updating of language models with data acquisition and fine-tuning pipeline
  - Cross-ref: 2507.17131 (HITL self-improvement), 2410.04444 (Gödel Agent recursive improvement)
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

## 2025-07

- [[2507.23276] How Far Are AI Scientists from Changing the World?](https://arxiv.org/abs/2507.23276), [gh/ResearAI/Awesome-AI-Scientist](https://github.com/ResearAI/Awesome-AI-Scientist) `[SCI]` `[SURVEY]`
  - Survey of research on AI scientists, AI researchers, AI engineers, and a series of AI-driven research studies
  - Cross-ref: 2408.06292 (automated scientific discovery implementation), 2506.18096 (systematic research agent analysis)
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

- [[2506.18096] Deep Research Agents: A Systematic Examination And Roadmap](https://arxiv.org/abs/2506.18096), [gh/ai-agents-2030/awesome-deep-research-agent](https://github.com/ai-agents-2030/awesome-deep-research-agent) `[SCI]` `[SURVEY]`
  - Comprehensive examination of AI agents for research tasks with roadmap for future development
  - Cross-ref: 2507.23276 (AI scientist impact assessment), 2501.04227 (practical research implementation)
- [[2506.16499] ML-Master: Towards AI-for-AI via Integration ofExploration and Reasoning](https://arxiv.org/abs/2506.16499) `[AUTO]` `[ARCH]`
  - AI system for automated machine learning through integrated exploration and reasoning capabilities
  - Cross-ref: 2507.18074 (automated architecture search), 2411.10478 (workflow optimization survey)
- [[2506.13131] AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131) `[CODE]` `[SCI]`
  - Evolutionary coding agent for automated scientific discovery and algorithm development
  - Cross-ref: 2507.22414 (code explanation methods), 2408.06292 (scientific discovery automation)
- [[2506.04133] TRiSM for Agentic AI: A Review of Trust, Risk, and SecurityManagement in LLM-based Agentic Multi-Agent Systems](https://arxiv.org/abs/2506.04133) `[SAFETY]` `[MAS]`
  - Framework for managing trust, risk, and security in LLM-based multi-agent systems
  - Cross-ref: 2508.03858 (runtime governance approach), 2408.02205 (layered safety model)
- [[2506.01438] Distinguishing Autonomous AI Agents from Collaborative Agentic Systems: A Comprehensive Framework for Understanding Modern Intelligent Architectures](https://arxiv.org/abs/2506.01438) `[ARCH]` `[SURVEY]` `cs.AI` `cs.MA`
  - Framework for understanding the distinction between autonomous AI agents and collaborative agentic systems
  - Cross-ref: 2508.10146 (framework architectures), 2505.10468 (conceptual taxonomy)

## 2025-05

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

## 2025-04

- [[2504.19678] From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review](https://arxiv.org/abs/2504.19678)
  - Comprehensive review of the evolution from LLM reasoning to fully autonomous AI agents
- [[2504.16902] Building A Secure Agentic AI ApplicationLeveraging Google's A2A Protocol](https://arxiv.org/abs/2504.16902)
  - Guide for building secure agentic AI applications using Google's Agent-to-Agent protocol

## 2025-03

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

## 2024-12

- [[2412.17149] A Multi-AI Agent System for Autonomous Optimization of Agentic AISolutions via Iterative Refinement and LLM-Driven Feedback Loop](https://arxiv.org/abs/2412.17149) `[MAS]` `[AUTO]`
  - Multi-agent system for autonomous optimization of agentic AI solutions using iterative refinement and LLM feedback loops
  - Cross-ref: 2408.08435 (automated design), 2507.18074 (architecture discovery)
- [[2412.04093] Practical Considerations for Agentic LLM Systems](https://arxiv.org/abs/2412.04093) `[ARCH]` `[COMP]`
  - Practical guidance for implementing and deploying agentic LLM systems in production
  - Cross-ref: 2411.05285 (agentops taxonomy), 2502.05957 (AutoAgent)

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

## 2024-10

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

## 2024-08

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

- [[2407.18219] Recursive Introspection: Teaching Language Model Agents How to Self-Improve](https://arxiv.org/abs/2407.18219) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - RISE framework for fine-tuning LLMs to introduce recursive introspection and self-improvement capabilities
  - Cross-ref: 2405.06682 (self-reflection effects), 2410.04444 (Gödel Agent recursive)

## 2024-06

- [[2406.01495] Re-ReST: Reflection-Reinforced Self-Training for Language Agents](https://arxiv.org/abs/2406.01495) `[AUTO]` `[ARCH]` `cs.AI` `cs.LG`
  - Reflection-reinforced self-training approach using environmental feedback to enhance sample quality and agent performance
  - Cross-ref: 2303.11366 (Reflexion foundation), 2407.18219 (recursive introspection)

## 2024-05

- [[2405.06682] Self-Reflection in LLM Agents: Effects on Problem-Solving Performance](https://arxiv.org/abs/2405.06682) `[AUTO]` `[EVAL]` `cs.AI` `cs.CL`
  - Empirical study demonstrating significant improvement in problem-solving through self-reflection mechanisms
  - Cross-ref: 2407.18219 (recursive introspection), 2303.11366 (Reflexion framework)

## 2024-04

- [[2404.13501] A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501) `[MEM]` `[SURVEY]`
  - Survey of memory mechanisms and architectures in LLM-based agent systems
  - Cross-ref: 2507.16940 (complex reasoning memory needs), 2503.21460 (broader agent architecture context)
- [[2404.11584] Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling](https://arxiv.org/abs/2404.11584) `[ARCH]` `[SURVEY]` `[PLAN]` `[TOOL]`
  - Survey of emerging AI agent architectures focusing on reasoning, planning, and tool calling capabilities
  - Cross-ref: 2405.17935 (tool integration foundations), 2402.02716 (planning mechanism details)
- [[2404.06411] AgentQuest: A Modular Benchmark Framework to Measure Progress and Improve LLM Agents](https://arxiv.org/abs/2404.06411) `[BENCH]` `[EVAL]`
  - Modular benchmark framework for measuring progress and improvement in LLM agent capabilities
  - Cross-ref: 2308.03688 (comprehensive benchmarking precedent), 2401.13178 (multi-turn evaluation focus)

## 2024-02

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

- [[2310.04406] Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models](https://arxiv.org/abs/2310.04406) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - LATS framework integrating Monte Carlo Tree Search with LM reasoning, acting, and planning capabilities
  - Cross-ref: 2210.03629 (ReAct foundation), 2410.02810 (StateAct)
- [[2310.03128] MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use](https://arxiv.org/abs/2310.03128) `[BENCH]` `[TOOL]` `cs.AI` `cs.CL`
  - Benchmark for evaluating LLM tool selection and usage decision-making capabilities
  - Cross-ref: 2307.16789 (ToolLLM), 2406.12045 (τ-bench)

## 2022-12

- [[2212.08073] Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) `[SAFETY]` `[ARCH]` `cs.AI` `cs.LG`
  - Foundational constitutional AI approach for training harmless AI systems through AI feedback
  - Cross-ref: 2406.07814 (collective constitutional AI), 2501.17112 (inverse constitutional AI)

## 2022-10

- [[2210.03629] ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) `[PLAN]` `[ARCH]` `cs.AI` `cs.CL`
  - Foundational ReAct framework for interleaving reasoning and acting in language model agents
  - Cross-ref: 2411.00927 (ReSpAct extension), 2310.04406 (LATS integration)
