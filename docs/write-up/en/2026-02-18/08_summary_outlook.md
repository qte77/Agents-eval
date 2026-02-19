# Summary and Outlook

## Achieved Goals

Over the course of seven sprints, the Agents-eval project has built a functional infrastructure for the empirical evaluation of multi-agent systems. The central deliverables comprise:

- **Three-Tier Evaluation Architecture** (Sprint 1): Tier 1 -- traditional text metrics, Tier 2 -- LLM-as-Judge, Tier 3 -- graph-based behavioral analysis. All three tiers are implemented and integrated through a typed plugin interface (`EvaluatorPlugin`).
- **PydanticAI Agent System** (Sprint 1--2): Four-agent pipeline (Manager $\rightarrow$ Researcher $\rightarrow$ Analyst $\rightarrow$ Synthesizer) with configurable composition. Supports single-LLM and multi-LLM operation through `AgentComposition` parameters.
- **Plugin Architecture** (Sprint 3): `EvaluatorPlugin` interface and `PluginRegistry` enable adding new evaluation metrics without changes to the core pipeline. Typed context exchange between tiers via Pydantic models.
- **Operational Resilience** (Sprint 4--5): Provider fallback chain for Tier 2, configurable token limits, adaptive weight redistribution in single-agent operation, background execution in the GUI without tab interruption.
- **Security Hardening** (Sprint 6): SSRF prevention with domain allowlisting, prompt injection resistance, sensitive data filtering from logs and traces, input size limits. OWASP MAESTRO 7-layer security review conducted.
- **Benchmarking Infrastructure** (Sprint 6): `SweepRunner` for 8 agent compositions x N papers x N repetitions, `SweepAnalyzer` for statistical analysis, `CCTraceAdapter` for processing Claude Code artifacts.
- **Claude Code Baseline** (Sprint 6--7): Complete CC Solo and CC Teams artifacts collected for Paper 1105.1072. `--engine=cc` flag for CLI and sweep implemented for direct comparability.
- **Documentation and Tests** (Sprint 7): Architecture, usage, and API documentation updated, test suite restructured toward behavioral coverage (595 $\rightarrow$ 564 tests without coverage loss).

---

## Core Empirical Findings

The findings derived from 30 traces and a single CC comparison run (Paper 1105.1072) can be summarized as follows:

**Latency and Scaling in PydanticAI MAS**: The Manager-Only configuration achieves a median duration of 4.8 s with an error rate of 0%. The three-agent configuration requires a mean of 12.3 s (+156%) with an initialization error rate of 25%. Execution time is dominated by LLM inference latency; tool execution times are negligible (0.004--0.09 s).

**Outliers from Provider Latency**: Two runs exceeded 69 s and 136 s respectively due to LLM provider latency spikes or rate limiting, not from coordination overhead. This underscores the need for retry mechanisms with exponential backoff.

**PydanticAI vs. Claude Code**: PydanticAI is 25--75x faster and approximately 50--100x more cost-effective than CC for the same task. CC uses 6--7x more tool calls because the codebase is explored at runtime. CC Teams incurs a 3x overhead over CC Solo. Structurally, CC Teams and PydanticAI multi-agent are analogous (each with Researcher/Analyst/Synthesizer), but differ significantly in latency and resource consumption.

**Evaluation Pipeline**: All three tiers are implemented and unit-tested. Composite quality scores could not be computed on real traces due to blocking issues. Latency and cost metrics from trace data are fully available.

---

## Scientific Contributions

The project makes the following methodological contributions:

- **Three-Tier Evaluation Methodology**: The combination of traditional text metrics (Tier 1), LLM-as-Judge (Tier 2), and graph-based behavioral analysis (Tier 3) enables multi-dimensional assessment that uses coordination patterns from execution traces as the primary information source.
- **Post-Execution Graph Analysis** (ADR-004): Agent behavior is retrospectively reconstructed from observability logs without influencing the execution itself.
- **Adaptive Weight Redistribution**: In single-agent operation, `coordination_quality` is automatically removed from the composite score, allowing single- and multi-agent configurations to be comparably evaluated.
- **Infrastructure for Empirical MAS Comparisons**: The combination of `SweepRunner`, `CCTraceAdapter`, and `BaselineComparison` model enables reproducible comparisons between PydanticAI MAS and Claude Code baseline on the same dataset and tasks.

---

## Limitations

This work has the following limitations:

- **Blocking Bug**: The `AgentRunResult.data` error on the `refactor-arch` branch prevents end-to-end evaluation runs. All composite quality scores are based on estimates or could not be computed.
- **Empty Sweep Results**: The `SweepRunner` produces no evaluable output. Composition comparisons are therefore not statistically grounded.
- **n=1 for Claude Code**: The CC comparison is based on a single paper and a single run per mode. Statistical significance requires at least 5 runs per configuration.
- **CC Teams Artifacts Ephemeral**: After completion of a `claude -p` run, `~/.claude/teams/` artifacts are not persistent. The `CCTraceAdapter` Teams parser cannot fully operate without these artifacts.
- **Tier 2 Blockage**: The `GITHUB_API_KEY` is not set in the execution environment. Tier 2 LLM-as-Judge evaluations are therefore unavailable, and composite scores are based solely on Tier 1 and Tier 3.
- **Missing Sub-Agent Token Counts**: Token consumption is only logged at the Manager level. Complete cost comparisons between configurations are therefore not possible.
- **No Quality Validation**: A comparison of the content quality of generated reviews (Tier 2, Tier 3 composite) is not available. All findings relate exclusively to latency, cost, and tool usage patterns.

---

## Outlook and Future Development

The planned further development addresses both identified blockers and strategic extensions of the framework.

**Short-term (Sprint 8)**:
- **Report Generation** (Feature 1): After completing an evaluation, a structured Markdown report with Tier 1/2/3 breakdown, identified weaknesses, and actionable improvement suggestions is generated. Available via the `--generate-report` flag in the CLI and as a button in the GUI.
- **Graph Attribute Alignment** (Feature 2): Alignment of Tier 3 graph metrics to attributes actually available in `GraphTraceData`, to avoid computation errors from missing fields.
- **MAESTRO Hardening** (Feature 3): Implementation of remaining findings from the Sprint 5 security review for the layers Model, Agent Logic, Integration, Monitoring, Execution, Environment, and Orchestration.
- **PydanticAI Streaming** (Feature 4): Investigation of the `NotImplementedError` exception for structured outputs in streaming mode (known AGENT_REQUESTS item).

**Medium-term**:
- **Bug Fix `AgentRunResult.data`**: Unblocks all end-to-end evaluation runs and enables computation of composite scores on real traces.
- **Sweep Results**: After bug fix, restart the composition sweep across all 8 configurations and multiple papers with statistically robust repetition counts ($\geq$5 runs).
- **Increase CC Sample Size**: At least 5 runs per CC mode (Solo/Teams) across multiple papers for statistically significant comparisons.
- **Claude Agent SDK Migration** (ADR-008): Replacement of `subprocess.run([claude, "-p"])` with the `claude-agent-sdk` package for more portable CC baseline invocation.
- **Per-Sub-Agent Token Logging**: Extension of the trace format with token counts at the sub-agent level for complete cost comparisons.

**Long-term**:
- **Framework Extension**: Integration of additional agent frameworks (LangChain, AutoGen, CrewAI) through standardized adapters to enable cross-framework comparisons.
- **Extended Metrics**: Implementation of candidate metrics identified in the architecture (`fix_rate`, `evaluator_consensus`, `delegation_depth`, `coordination_topology`, `path_convergence`, `rubric_alignment`) by priority.
- **Optional Container Deployment** (ADR-007): Docker images and Compose configurations for parallel judge execution and production isolation.
- **Domain Diversification**: Extension beyond scientific paper reviews to additional analytical tasks, to demonstrate the generalizability of the evaluation framework.
