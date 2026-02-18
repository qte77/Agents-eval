# Index {.unnumbered}

\section*{A}

**Agentic AI Systems**: Autonomous systems with goal-oriented behavior that independently make decisions and employ tools without being explicitly instructed for each step.

**AgentOps**: Cloud-based observability platform for agent behavior tracking and performance analytics (optional, commented out in pyproject.toml).

**Analyst Agent**: Specialized agent for verifying the correctness of assumptions, facts, and conclusions in the multi-agent workflow.

**Arize Phoenix**: Local trace viewer for PydanticAI execution traces (arize-phoenix>=13.0.0); replaces Docker-based alternatives.

\section*{B}

**Benchmarking Infrastructure**: Sweep-based system (SweepRunner, SweepAnalyzer) for systematic comparison of MAS compositions across multiple papers and repetitions.

\section*{C}

**CC Baseline**: Claude Code as reference engine (--engine=cc) for comparison against PydanticAI MAS; invoked via subprocess.run([claude, "-p"]) (ADR-008).

**Claude Code (CC)**: Anthropic's headless CLI tool for agentic development tasks; serves as baseline comparison in the benchmarking infrastructure.

**Composite Scoring**: Weighted summation formula from six core metrics (0.167 weight each) with adaptive weight redistribution for missing tiers.

**CompositeResult**: Pydantic output model of composite_scorer.py with overall score, individual metrics, and single_agent_mode flag.

\section*{D}

**DuckDuckGo Search Tool**: Search API of the Researcher Agent for external information acquisition (pydantic-ai-slim[duckduckgo]).

\section*{E}

**EvaluatorPlugin**: Abstract base class (ABC) for all evaluation engines; defines name, tier, evaluate(), and get_context_for_next_tier() interface.

\section*{G}

**GraphTraceData**: Pydantic model for representing execution graphs; contains agent IDs, coordination_events, and tool call sequences for Tier 3 analysis.

\section*{J}

**JudgeSettings**: pydantic-settings BaseSettings class with JUDGE_ prefix; replaces JSON configuration files (ADR-006).

\section*{K}

**KISS / DRY / YAGNI**: Core principles of the codebase (Keep It Simple, Don't Repeat Yourself, You Aren't Gonna Need It); mandatory for all implementation decisions.

\section*{L}

**LLM-as-Judge**: Evaluation methodology in which a large language model semantically assesses the quality of agent outputs (Tier 2).

**Logfire**: Structured logging framework (logfire>=4.24.0) with PydanticAI auto-instrumentation for trace capture and observability.

\section*{M}

**Manager Agent**: Primary orchestrator of the multi-agent system; delegates tasks to Researcher, Analyst, and Synthesizer agents.

**MAS (Multi-Agent System)**: Distributed system with multiple specialized, interacting agents; central evaluation subject of the framework.

**MAESTRO**: OWASP Multi-Agent Environment Security Threat and Risk Ontology; 7-layer security model (Model, Agent Logic, Integration, Monitoring, Execution, Environment, Orchestration).

\section*{N}

**NetworkX**: Python library for graph-based behavioral analysis (networkx>=3.6.1); constructs and analyzes execution graphs from observability traces (Tier 3).

\section*{O}

**OWASP**: Open Web Application Security Project; foundation of the MAESTRO security model.

\section*{P}

**PeerRead**: Academic dataset with 14,775 scientific papers from NIPS, ICLR, and ACL, including structured peer reviews; primary evaluation benchmark (ADR-002).

**Plugin Architecture**: Extension concept with EvaluatorPlugin interface and PluginRegistry for tier-ordered execution without modification of the core pipeline (ADR-005).

**PluginRegistry**: Central registration of all evaluation plugins; enables automatic discovery and execution in tier order (1 $\rightarrow$ 2 $\rightarrow$ 3).

**PydanticAI**: Type-safe agent framework (pydantic-ai-slim>=1.59.0) for structured multi-agent orchestration with Pydantic validation (ADR-001).

\section*{R}

**Researcher Agent**: Specialized agent for data collection and verification; equipped with DuckDuckGo search tool for external information acquisition.

\section*{S}

**Streamlit**: Web framework for the graphical user interface (streamlit>=1.54.0); supports background execution and real-time debug log streaming.

**SweepRunner**: Benchmarking component for systematic composition sweeps (8 agent compositions x N papers x N repetitions).

**Synthesizer Agent**: Specialized agent for creating formatted scientific reports from validated agent results.

\section*{T}

**Tier 1 (Traditional Metrics)**: Fast, objective text similarity measurement (cosine, Jaccard, BLEU/ROUGE) as validation baseline.

**Tier 2 (LLM-as-a-Judge)**: Semantic quality assessment through configurable judge provider; automatic fallback when API keys are missing.

**Tier 3 (Graph Analysis)**: Primary evaluation tier; post-execution behavioral analysis from observability traces using NetworkX (ADR-004).

\section*{W}

**Weave**: Weights & Biases ML experiment tracking integration (weave>=0.52.28); optionally available as wandb dependency group.
