# Implementation

## Core Framework Implementation

### Application Architecture

The main entry point of the application is implemented in `src/app/app.py` as the asynchronous function `main()`. It coordinates the entire lifecycle of an execution: loading configuration, initializing agents, starting execution, and subsequently triggering the evaluation pipeline. The function is instrumented with the optional `@op()` decorator from Weave, which activates when `WANDB_API_KEY` is set; if the key is absent, a no-op fallback is used.

```python
@op()  # type: ignore[reportUntypedFunctionDecorator]
async def main(
    chat_provider: str = CHAT_DEFAULT_PROVIDER,
    query: str = "",
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    pydantic_ai_stream: bool = False,
    chat_config_file: str | Path | None = None,
    enable_review_tools: bool = True,
    paper_number: str | None = None,
    skip_eval: bool = False,
    ...
) -> dict[str, Any] | None:
```

*Code excerpt from `src/app/app.py:196`*

The function returns a dictionary with the keys `composite_result` and `graph`, allowing the Streamlit GUI and CLI to share the same logic. For the CLI, `src/app/main.py` handles argument processing with Typer; for the GUI, `run_gui.py` calls `main()` programmatically.

### Multi-Provider LLM Integration

The system supports multiple LLM providers (OpenAI, GitHub Models, Gemini, Ollama, Cerebras, Groq) through a unified `PROVIDER_REGISTRY` mechanism in `src/app/data_models/app_models.py`. Each registry entry contains the model name, base URL, and API key environment variable. The function `setup_agent_env()` in `agent_system.py` resolves the active provider and creates an `EndpointConfig` object with a validated API key and token limits:

```python
def setup_agent_env(
    provider: str,
    query: UserPromptType,
    chat_config: ChatConfig | BaseModel,
    chat_env_config: AppEnv,
    token_limit: int | None = None,
) -> EndpointConfig:
```

*Code excerpt from `src/app/agents/agent_system.py:629`*

The token limit is determined with a three-level priority: CLI/GUI parameter > environment variable `AGENT_TOKEN_LIMIT` > provider configuration value. For OpenAI-compatible providers with strict tool definitions, an `OpenAIModelProfile(openai_supports_strict_tool_definition=False)` is set to avoid HTTP 422 errors with mixed strict values [@pydanticai].

### Type-Safe Data Model Architecture

All data boundaries are secured by Pydantic models in `src/app/data_models/`. The `ChatConfig` model describes provider configurations and prompts; `AppEnv` (`BaseSettings` with `AGENTS_EVAL_` prefix) reads API keys from the environment. Evaluation results are typed in `evaluation_models.py` as `Tier1Result`, `Tier2Result`, `Tier3Result`, and `CompositeResult`. For external data mapping fields (PeerRead dataset), `validation_alias` is used to map external key names (`IMPACT`) to internal field names (`impact`) without altering the constructor signature:

```python
impact: str = Field(default="UNKNOWN", validation_alias="IMPACT")
```

*Code excerpt from `src/app/data_models/peerread_models.py`*

---

## Multi-Agent System

### Agent Orchestration

Agent orchestration is based on PydanticAI [@pydanticai]. The Manager Agent receives the user query and delegates subtasks to up to three sub-agents (Researcher, Analyst, Synthesizer) via typed tool calls. The composition is configured at runtime:

```python
def get_manager(
    provider: str,
    provider_config: ProviderConfig,
    api_key: str | None,
    prompts: dict[str, str],
    include_researcher: bool = False,
    include_analyst: bool = False,
    include_synthesiser: bool = False,
    enable_review_tools: bool = False,
) -> Agent[None, BaseModel]:
```

*Code excerpt from `src/app/agents/agent_system.py:432`*

Within `_create_manager()`, sub-agents are created as `Agent` instances with their own model and system prompt, and registered as tool functions on the Manager via `_add_tools_to_manager_agent()`. Each delegation tool (`delegate_research`, `delegate_analysis`, `delegate_synthesis`) invokes the respective sub-agent, logs the interaction in the `TraceCollector`, and returns a typed Pydantic model:

```python
@manager_agent.tool
async def delegate_research(
    ctx: RunContext[None], query: str
) -> ResearchResult | ResearchResultSimple | ReviewGenerationResult:
    """Delegate research task to ResearchAgent."""
    trace_collector.log_agent_interaction(
        from_agent="manager",
        to_agent="researcher",
        interaction_type="delegation",
        data={"query": query, "task_type": "research"},
    )
    result = await research_agent.run(query, usage=ctx.usage)
    ...
```

*Code excerpt from `src/app/agents/agent_system.py:121`*

In single-agent mode (Manager only), the Manager handles all tasks itself. PeerRead-specific tools are registered directly on the Manager in this case; otherwise on the Researcher Agent (separation of concerns, Sprint 5 [@changelog]).

### Tool Integration

The Researcher Agent has access to the `duckduckgo_search_tool()` from PydanticAI's common tools [@pydanticai] as well as PeerRead-specific tools from `src/app/tools/peerread_tools.py`: `get_peerread_paper`, `read_paper_pdf_tool`, `query_peerread_papers`, `generate_paper_review_content_from_template`, `save_paper_review`, and `save_structured_review`. All tool calls are captured by the `TraceCollector`'s `log_tool_call()` with timestamp and success flag.

The result model is chosen based on provider: Gemini receives `ResearchResultSimple` (no `additionalProperties` support in JSON schema), all other providers receive `ResearchResult`. When review tools are enabled, `ReviewGenerationResult` is used.

---

## Evaluation Pipeline

### Three-Tier Implementation

The class `EvaluationPipeline` in `src/app/judge/evaluation_pipeline.py` orchestrates the sequential execution of all three evaluation tiers with individual timeouts and error handling:

```python
async def evaluate_comprehensive(
    self,
    paper: str,
    review: str,
    execution_trace: GraphTraceData | dict[str, Any] | None = None,
    reference_reviews: list[str] | None = None,
) -> CompositeResult:
    tier1_result, _ = await self._execute_tier1(paper, review, reference_reviews)
    tier2_result, _ = await self._execute_tier2(paper, review, trace_dict)
    tier3_result, _ = await self._execute_tier3(trace_dict)
    ...
```

*Code excerpt from `src/app/judge/evaluation_pipeline.py:484`*

**Tier 1 -- Traditional Metrics** (`src/app/judge/plugins/traditional.py`): TF-IDF cosine similarity, Jaccard similarity, and semantic similarity (TF-IDF cosine), execution time, and task success score. Timeout: 1 second.

**Tier 2 -- LLM-as-Judge** (`src/app/judge/plugins/llm_judge.py`): A single LLM call evaluates technical accuracy, constructiveness, clarity, and planning rationality. The provider is automatically resolved via a fallback chain (`tier2_provider=auto` inherits the active chat provider; if no valid provider is available, Tier 2 is skipped and the weights are redistributed to Tier 1 and Tier 3). Timeout: 10 seconds.

**Tier 3 -- Graph-Based Analysis** (`src/app/judge/plugins/graph_metrics.py`): NetworkX processes the `GraphTraceData` from the `TraceCollector` into a directed graph and computes `path_convergence`, `tool_selection_accuracy`, `coordination_centrality`, and `task_distribution_balance`. This is the primary differentiating metric of the framework [@architecture2025]. Timeout: 15 seconds.

If a tier fails, depending on the `fallback_strategy` setting, a fallback (neutral 0.5 values) is applied or the tier is skipped. The performance metrics of all tier executions are captured in the `PerformanceMonitor`, which issues a bottleneck warning when exceeding 40% of total runtime.

### Plugin Registry and Composite Scorer

Each evaluation tier implements the abstract `EvaluatorPlugin` interface from `src/app/judge/plugins/base.py`:

```python
class EvaluatorPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def tier(self) -> int: ...

    @abstractmethod
    def evaluate(self, context: BaseModel) -> BaseModel: ...

    @abstractmethod
    def get_context_for_next_tier(self, result: BaseModel) -> BaseModel: ...
```

*Code excerpt from `src/app/judge/plugins/base.py`*

The `PluginRegistry` discovers plugins at import time and executes them in tier order (1 $\rightarrow$ 2 $\rightarrow$ 3). Typed context passing between tiers prevents runtime errors.

The `CompositeScorer` (`src/app/judge/composite_scorer.py`) computes the weighted overall score from six equally weighted metrics (16.7% each): `time_taken`, `task_success`, `coordination_quality`, `tool_efficiency`, `planning_rationality`, `output_similarity`. In single-agent mode, `coordination_quality` is excluded and the weight is redistributed to the remaining five metrics (20% each), which is transparently communicated through the `single_agent_mode` flag in `CompositeResult`. The decision thresholds are: accept $\geq$ 0.863 | weak_accept $\geq$ 0.626 | reject < 0.626 [@mas-findings].

---

## Observability Integration

The observability layer combines **Logfire** for structured tracing and **Arize Phoenix** as a local trace viewer (Docker-free). Initialization occurs in `src/app/agents/logfire_instrumentation.py` via `logfire.instrument_pydantic_ai()`, which automatically instruments all PydanticAI agents -- no manual decorators on agent functions are required:

```python
def initialize_logfire_instrumentation_from_settings(
    settings: JudgeSettings | None = None,
) -> None:
    ...
    initialize_logfire_instrumentation(logfire_config)
```

*Code excerpt from `src/app/agents/agent_system.py:72`*

The `TraceCollector` (`src/app/judge/trace_processors.py`) captures agent-to-agent interactions and tool calls with timestamps during agent execution in a `GraphTraceData` instance, which subsequently serves as input for Tier 3. Traces are persistently stored in SQLite (`logs/traces/traces.db`) and as JSONL files in `logs/traces/`. API keys and tokens are redacted before persistence through Loguru scrubbing patterns (Sprint 6, STORY-012 [@changelog]).

Wandb/Weave is implemented as an optional dependency: if `WANDB_API_KEY` is absent, a no-op decorator activates that completely suppresses the import.

---

## User Interfaces

### CLI (Typer)

The CLI is implemented in `src/app/main.py` with Typer. It exposes all parameters of `main()` as command-line flags with runtime type checking. Key flags include `--paper-number`, `--chat-provider`, `--include-researcher`, `--include-analyst`, `--include-synthesiser`, `--skip-eval`, `--token-limit`, and `--engine=mas|cc` (Sprint 7) for switching between PydanticAI MAS and Claude Code baseline. A separate CLI `run_sweep.py` controls the `SweepRunner` (`src/app/benchmark/`) for composition sweeps across multiple agent configurations and papers (Sprint 6 [@changelog]).

Example invocation:

```bash
make app_cli ARGS="--paper-number=1105.1072 --chat-provider=github \
    --include-researcher --include-analyst --include-synthesiser"
```

### Streamlit GUI

The Streamlit GUI (`src/app/gui/`) is organized into several pages:

- **Run App**: Starts agent execution in the background via `threading.Thread` (tab navigation does not abort execution); displays real-time debug logs from a `LogCapture` Loguru sink.
- **Evaluation Results**: Displays Tier 1/2/3 scores and comparison charts.
- **Agent Graph**: Renders the delegation graph from `GraphTraceData` interactively with NetworkX and Pyvis (Sprint 5 [@changelog]).
- **Settings**: Editable settings with session state persistence; reads default values from `JudgeSettings` and `CommonSettings`.

The system architecture (see Chapter 4, Section 4.6) visualizes the interaction of all components.

The following customer journey shows the complete interaction path of a researcher from paper selection to evaluation view:

\begin{figure}[!htbp]
\centering
\includegraphics{../../../../assets/images/customer-journey-activity-light.png}
\caption{Customer journey -- user interaction patterns and system touchpoints}
\end{figure}

---

## Development Process Across Seven Sprints

The implementation followed a sprint-based BDD approach with iterative refinement [@agents-md]:

| Sprint | Key Deliverables |
|--------|------------------|
| Sprint 1 | Three-tier evaluation framework (Tier 1--3 base implementation), PeerRead dataset integration, `JudgeSettings` pydantic-settings |
| Sprint 2 | Post-run evaluation wiring (`--skip-eval`), Logfire + Phoenix tracing infrastructure, Streamlit evaluation dashboard |
| Sprint 3 | Plugin architecture (`EvaluatorPlugin`, `PluginRegistry`), `TraceStore`, `JudgeAgent`, optional Weave dependency, Hypothesis/snapshot tests |
| Sprint 4 | Operational resilience (thread-safe graph timeout, Logfire error handling), Claude Code `CCTraceAdapter`, GUI baseline comparison |
| Sprint 5 | Tier 2 fallback chain, token limit override, single-agent weight redistribution, Streamlit background execution, OWASP MAESTRO security audit |
| Sprint 6 | Benchmarking infrastructure (`SweepRunner`, `SweepAnalyzer`), security hardening (SSRF, prompt injection, log scrubbing), test coverage increase, Opik removal |
| Sprint 7 | Unified provider configuration (`--judge-provider`, `--judge-model`), `--engine=mas\|cc` flag, sweep rate-limit resilience, GUI real-time debug log, architecture documentation |

The complete change history is documented in `CHANGELOG.md` [@changelog].
