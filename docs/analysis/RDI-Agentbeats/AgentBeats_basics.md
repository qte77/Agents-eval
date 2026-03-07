---
title: AgentBeats Competition Participation Guide
description: Strategic analysis and participation roadmap for AgentX-AgentBeats competition covering outstanding tracks (Research Agent, Multi-Agent, AAA), unique differentiators, and implementation priorities for Agents-eval project
created: 2026-01-11
updated: 2026-01-11
---

## Overview

[AgentX-AgentBeats Competition](https://rdi.berkeley.edu/agentx-agentbeats.html) - Berkeley RDI (Oct 2025 - Jan 2026)

**Competition Structure**: Phase 1 (Green Agent) builds evaluation benchmarks, Phase 2 (Purple Agent) builds competing agents.

**Deadline Phase 1 (Green)**: January 15, 2026
**Deadline Phase 2 (Purple)**: February 22, 2026

---

## Strategic Context

**AgentBeats Competition (Deadline: Jan 15, 2026):**

- Outstanding tracks: Research Agent ($16k OpenAI), Multi-Agent, AAA
- Critical gap: A2A Protocol (2-3 days effort)
- Unique advantage: Graph-based coordination analysis (NOVEL)

**Tool Synergy Discovered:**

```text
PydanticAI + Pydantic Evals + Logfire + Agents-eval
         ↓
Complete evaluation infrastructure
```

---

## Why Agents-eval is an OUTSTANDING Competition Entry

### For AgentBeats

**Fills critical evaluation gap**: While 28 benchmarks exist in AgentBeats (SciCode, GAIA, TheAgentCompany, etc.), **NONE** evaluate multi-agent coordination quality through graph-based behavioral analysis. Agents-eval brings a **category-defining approach** that quantifies what others ignore: how agents collaborate, not just whether they succeed.

**Addresses competition judging criteria perfectly**:

- ✅ **Innovation & Impact**: Post-execution graph analysis is NOVEL - no existing benchmark measures coordination centrality, communication overhead, or task distribution balance
- ✅ **Evaluation Methodology**: Three-tier system (Traditional + LLM-as-Judge + Graph) provides multi-dimensional scoring vs. competitors' binary pass/fail
- ✅ **Benchmark Design**: PeerRead uses real academic papers with ground truth reviews, not synthetic tasks
- ✅ **Technical Quality**: Production-ready with PydanticAI, comprehensive tests, type safety
- ✅ **Reproducibility**: Config-driven with deterministic metrics and Docker deployment

### How Agents-eval Stands Out

**vs. Existing Benchmarks**:

| Benchmark | What They Measure | What Agents-eval Adds |
| ----------- | ------------------- | ---------------------- |
| SciCode, CORE-Bench | Task completion (binary) | Multi-dimensional scoring + behavioral patterns |
| TheAgentCompany | Real-world task success | Coordination quality metrics |
| GAIA | Accuracy | Planning rationality, tool efficiency |
| All others | **Whether** agents succeed | **How** agents collaborate |

**Unique differentiators NO competitor has**:

1. **Graph-based coordination analysis** - NetworkX betweenness centrality, communication overhead, path convergence
2. **Post-execution behavioral tracing** - Agents operate autonomously, patterns analyzed retrospectively without interference
3. **Composite academic scoring** - 6 balanced metrics mapping to accept/reject decisions (mirrors real peer review)
4. **Three-tier graceful degradation** - Fast metrics (<1s) → LLM quality → Graph complexity, with fallback strategies

**Bottom line**: Agents-eval doesn't just test if agents work — it reveals **how well they work together**, filling a gap that no existing benchmark addresses.

---

## OUTSTANDING Participation Tracks for Agents-eval

### 🏆 Research Agent Track (OpenAI-sponsored, $16k prizes)

**Perfect fit**: PeerRead benchmark IS research agent evaluation with ground truth reviews

**USP**: "First research agent benchmark with post-execution behavioral analysis measuring coordination quality, planning rationality, and tool efficiency beyond task completion"

**Differentiator**: Three-tier evaluation (Traditional + LLM-as-Judge + Graph Analysis) vs. single-metric competitors

---

### 🏆 Multi-Agent Track (Category-defining opportunity)

**Unique position**: NO existing benchmark evaluates multi-agent coordination with graph metrics

**USP**: "Only benchmark that quantifies multi-agent coordination quality through NetworkX graph analysis, enabling comparison of agent architectures on collaboration efficiency"

**Novel metrics**: Coordination centrality, communication overhead, task distribution balance, path convergence

---

### 🏆 AAA Track (Agentified Agent Assessment)

**Natural alignment**: Tier 2 LLM-as-Judge = agent evaluating agents

**USP**: Three-tier system inherently implements "agents assess other agents" vision

[Agentified Agent Assessment (AAA): A New Paradigm for Open, Standardized, Reproducible Agent Evaluation](https://docs.google.com/document/d/1Gy5O3J8r2ZyDx6BSI84G3fVdrxCHXZlJHKvXxDbjfwI/edit?tab=t.0#heading=h.6c1kqou5jhz3)

- Goals
    1. Agentified evaluation
    2. Standardization
    3. Reproducibility
- Obstacles
  1. System implementation complexity
  2. Lack of openness and adoption

---

## Key Competitive Advantages

1. **Three-Tier Evaluation** - Combines fast traditional metrics (<1s), LLM-as-Judge quality assessment, and graph-based behavioral analysis
2. **Composite Scoring** - 6 weighted metrics mapping to academic review decisions (accept/reject) vs. binary pass/fail
3. **Real Academic Domain** - PeerRead provides ground truth scientific reviews vs. synthetic tasks
4. **Post-Execution Behavioral Analysis** - NOVEL approach: agents operate autonomously, observability logs analyzed retrospectively

---

## Critical Gap: A2A Protocol Compliance

Required for all tracks:

- Implement Google A2A protocol wrapper for agents
- Add MCP (Model Context Protocol) compliance for tool access
- AgentBeats SDK integration
- **Estimated effort**: 2-3 days using [agentbeats/tutorial](https://github.com/agentbeats/tutorial)

---

## Implementation Files

### New files required

- `docker/Dockerfile` - Production containerization
- `docker/docker-compose.yml` - Multi-service orchestration
- `src/app/protocols/a2a_wrapper.py` - A2A protocol implementation
- `src/app/protocols/mcp_compliance.py` - MCP tool access
- `docs/agentbeats/README.md` - Competition-focused documentation
- `docs/agentbeats/demo_script.md` - 3-minute demo video script

### Files to modify

- `src/app/agents/orchestration.py` - A2A protocol integration
- `pyproject.toml` - AgentBeats SDK dependency

---

## Quick Win Prioritization

1. **fix_rate metric** (30 min) - immediate value
2. **Ralph completion promise** (1 hour) - proven pattern
3. **"Think first" Tier 2** (30 min) - 0.86 correlation

---

## Immediate Next Steps

1. Register team on [AgentBeats platform](https://forms.gle/1C5d8KXny2JBpZhz7)
2. Fork [agentbeats/tutorial](https://github.com/agentbeats/tutorial) repository
3. Create A2A wrapper prototype
4. Build production Dockerfile
5. Join [Discord](https://discord.gg/uqZUta3MYa) for community support

---

## Recommended Strategy

**Dual-track submission** (Research Agent + Multi-Agent) - same codebase, different marketing angles for 2x prize opportunity.
