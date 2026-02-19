# Project Introduction

## Motivation and Problem Statement

### The Evaluation Gap for Agentic AI Systems

The emergence of agentic AI systems has created a fundamental challenge in the
field of artificial intelligence evaluation. Traditional benchmarking approaches,
developed for assessing individual language models, fail to capture the emergent
behaviors arising from multi-agent interactions: delegation patterns, collaborative
decision-making, and dynamic task distribution among specialized agents
[@surveyLLMAgents].

Existing benchmarks such as the Berkeley Function-Calling Leaderboard [@berkeleyFCL],
CORE-Bench [@coreBench], and GAIA [@gaia] focus on individual model performance or
narrowly defined capabilities. The question of how well a multi-agent system
coordinates -- that is, whether the manner of collaboration between agents leads
to better outcomes than simpler approaches -- remains unanswered within these
frameworks [@surveyLLMBasedAgentEval].

Framework fragmentation exacerbates the problem: the proliferation of agentic
frameworks such as PydanticAI [@pydanticai], AutoGen [@autogen], CrewAI [@crewai],
and LangChain [@langchain] has created an ecosystem in which each framework
implements its own evaluation approaches. Comparative analyses across framework
boundaries are therefore methodologically impractical.

### Goal: A Three-Tier Evaluation Framework

Agents-eval addresses this gap through an evaluation framework that combines three
complementary assessment dimensions:

- **Tier 1 -- Traditional Metrics**: Fast, objective text similarity metrics
  (BLEU, ROUGE, cosine similarity) as baseline validation
- **Tier 2 -- LLM-as-a-Judge**: Semantic quality assessment through a
  configurable language model judge
- **Tier 3 -- Graph-Based Analysis**: Coordination patterns from real
  execution traces, analyzed with NetworkX -- the primary innovation of the framework

The PeerRead dataset [@peerread2018; @peerreadGithub] serves as the evaluation
domain, an established collection of scientific papers with structured peer reviews.
A four-agent system (Manager $\rightarrow$ Researcher $\rightarrow$ Analyst $\rightarrow$ Synthesizer)
generates reviews, which are subsequently evaluated through the three-tier pipeline.

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/research-integration-visualization-light.png}
\caption{Visualization of the synthesis of research literature, production framework analysis, and systematic development approach informing the project.}
\end{figure}

## Current Project Status

### Development Progress (Sprint 1--7)

The project has been progressing since Sprint 1 in iterative two-week cycles.
The following table shows the progress:

| Sprint | Status    | Focus                                                                |
|--------|-----------|----------------------------------------------------------------------|
| 1      | Delivered | Three-tier evaluation framework, PeerRead integration                |
| 2      | Delivered | Eval wiring, trace capture, Logfire + Phoenix, Streamlit dashboard   |
| 3      | Delivered | Plugin architecture, GUI wiring, test alignment, trace quality       |
| 4      | Delivered | Operational resilience, Claude Code baseline comparison (Solo + Teams) |
| 5      | Delivered | Runtime fixes, GUI improvements, architecture improvements, code review |
| 6      | Delivered | Benchmarking infrastructure, CC baseline, security hardening, test quality |
| 7      | Active    | Documentation, examples, test refactoring, GUI, unified providers    |
| 8      | Draft     | Report generation, graph alignment, MAESTRO hardening, streaming     |

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/research-chronological-timeline-light.png}
\caption{Chronological overview of the development phases from Sprint 1 to the current state.}
\end{figure}

### Technical Implementation

The current implementation (version 3.3.0, Sprint 7 active) comprises the
following core components:

**Multi-Agent System**: Four specialized agents orchestrated with PydanticAI
[@pydanticai]:

- *Manager Agent*: Primary orchestrator for task delegation and coordination
- *Researcher Agent*: Information gathering with DuckDuckGo search integration
- *Analyst Agent*: Critical evaluation and data validation
- *Synthesizer Agent*: Generation of structured scientific reports

**Evaluation Pipeline**: Plugin-based architecture (`EvaluatorPlugin` interface)
with typed context passing between tiers. Six equally weighted metrics (16.7% each):
planning rationality, task success, tool efficiency, coordination quality,
execution time, and output similarity.

**Observability**: Logfire auto-instrumentation with Arize Phoenix for trace
inspection; Streamlit dashboard for Tier 1/2/3 result display and interactive
agent graph visualization.

**Security** (Sprint 6): SSRF prevention through URL validation with domain
allowlisting, prompt injection resistance, sensitive data masking in logs and
traces.

**Benchmarking** (Sprint 6): `SweepRunner` for 8 agent compositions x N papers
x N repetitions with statistical analysis (mean, standard deviation, min/max).

### Research Context

The project is embedded in current research on LLM-based agent systems
[@surveyLLMAgents; @surveyLLMBasedAgentEval]. The choice of the PeerRead dataset
[@peerread2018] enables the use of established peer review quality standards as
the evaluation foundation. The three-tier architecture is motivated by insights
into evaluation methodologies for agentic systems, particularly the distinction
between *what* a system produces (Tiers 1 and 2) and *how* it coordinates (Tier 3).

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/AI-agent-landscape-visualization-light.png}
\caption{Overview of the current AI agent framework landscape, in which Agents-eval is positioned.}
\end{figure}
