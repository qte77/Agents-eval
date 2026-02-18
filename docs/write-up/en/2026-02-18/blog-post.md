---
layout: post
title: "Agents-eval: A Three-Tier Evaluation Framework for Multi-Agent Systems"
excerpt: "Writeup on building and benchmarking a PydanticAI-based MAS evaluation framework with graph-based behavioral analysis."
categories: [ml, ai, agents, evaluation, multi-agent-systems, pydantic-ai, benchmarking]
---

# Agents-eval: A Three-Tier Evaluation Framework for Multi-Agent Systems

How do you evaluate whether a multi-agent system actually coordinates well -- or whether a single agent would have done the job faster and cheaper? **Agents-eval** is a framework that answers this through three complementary evaluation tiers.

## The Problem

Existing LLM benchmarks (Berkeley FCL, CORE-Bench, GAIA) measure individual model performance. They don't capture what happens when multiple agents collaborate: delegation patterns, coordination overhead, and whether the collaboration actually improves outcomes. Framework fragmentation (PydanticAI, AutoGen, CrewAI, LangChain) makes cross-framework comparison even harder.

## The Approach

Agents-eval combines three evaluation tiers:

- **Tier 1 -- Traditional Metrics**: Fast text similarity (cosine, Jaccard, semantic) as a quantitative baseline
- **Tier 2 -- LLM-as-Judge**: Semantic quality assessment via a configurable judge model
- **Tier 3 -- Graph Analysis**: Post-execution behavioral analysis of coordination patterns using NetworkX -- the primary differentiator

A four-agent system (Manager, Researcher, Analyst, Synthesizer) built on **PydanticAI** generates scientific peer reviews from the PeerRead dataset, which are then evaluated through the pipeline.

## Key Findings (30 Traces)

| Configuration | Median Latency | Cost (approx.) | Error Rate |
|---------------|---------------|----------------|------------|
| PydanticAI Manager-only | ~4.8 s | ~$0.01 | 0% |
| PydanticAI 3-agent | ~12.3 s | ~$0.03 | 25% |
| Claude Code Solo | 118.3 s | $0.94 | 0% |
| Claude Code Teams | 359.9 s | $1.35 | 0% |

PydanticAI-based agents are **25--75x faster** and **50--100x cheaper** than Claude Code baselines for the same task. The difference comes from purpose-built typed tools vs. runtime codebase exploration.

## Architecture Highlights

- **Plugin-based evaluation**: `EvaluatorPlugin` interface with `PluginRegistry` for tier-ordered execution
- **Adaptive weight redistribution**: Single-agent mode automatically excludes `coordination_quality` and redistributes weights
- **Six equally weighted metrics** (16.7% each): planning rationality, task success, tool efficiency, coordination quality, execution time, output similarity
- **Security hardened**: SSRF prevention, prompt injection resistance, log/trace data redaction (OWASP MAESTRO audit)

Built iteratively over 7 sprints, currently at version 3.3.0.

## Read More

- **[Full English Writeup (PDF)](https://github.com/qte77/Agents-eval/blob/main/docs/write-up/en/2026-02-18/writeup.pdf)**
- **[Full English Writeup (Markdown sources)](https://github.com/qte77/Agents-eval/tree/main/docs/write-up/en/2026-02-18/)**
- **[Agents-eval Repository](https://github.com/qte77/Agents-eval)**

---

**Keywords:** Multi-Agent Systems, LLM Evaluation, PydanticAI, Agentic AI, LLM-as-Judge, Peer Review, Benchmarking, Tracing, Observability
