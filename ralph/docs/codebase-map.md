## Codebase Map

Auto-generated source tree and signatures. Do NOT read these files
unless the pre-loaded context below is insufficient.

### File Tree

```
  src/app/agents/agent_factories.py
  src/app/agents/agent_system.py
  src/app/agents/__init__.py
  src/app/agents/logfire_instrumentation.py
  src/app/app.py
  src/app/benchmark/__init__.py
  src/app/benchmark/sweep_analysis.py
  src/app/benchmark/sweep_config.py
  src/app/benchmark/sweep_runner.py
  src/app/common/error_messages.py
  src/app/common/__init__.py
  src/app/common/log.py
  src/app/common/models.py
  src/app/config/app_env.py
  src/app/config/common_settings.py
  src/app/config/config_app.py
  src/app/config/__init__.py
  src/app/config/judge_settings.py
  src/app/config/logfire_config.py
  src/app/config/peerread_config.py
  src/app/data_models/app_models.py
  src/app/data_models/evaluation_models.py
  src/app/data_models/__init__.py
  src/app/data_models/peerread_models.py
  src/app/data_models/report_models.py
  src/app/data_utils/datasets_peerread.py
  src/app/data_utils/__init__.py
  src/app/data_utils/review_persistence.py
  src/app/engines/cc_engine.py
  src/app/engines/__init__.py
  src/app/__init__.py
  src/app/judge/baseline_comparison.py
  src/app/judge/cc_trace_adapter.py
  src/app/judge/composite_scorer.py
  src/app/judge/evaluation_pipeline.py
  src/app/judge/evaluation_runner.py
  src/app/judge/graph_analysis.py
  src/app/judge/graph_builder.py
  src/app/judge/graph_export.py
  src/app/judge/__init__.py
  src/app/judge/llm_evaluation_managers.py
  src/app/judge/performance_monitor.py
  src/app/judge/plugins/base.py
  src/app/judge/plugins/graph_metrics.py
  src/app/judge/plugins/__init__.py
  src/app/judge/plugins/llm_judge.py
  src/app/judge/plugins/traditional.py
  src/app/judge/trace_processors.py
  src/app/judge/traditional_metrics.py
  src/app/llms/__init__.py
  src/app/llms/models.py
  src/app/llms/providers.py
  src/app/reports/__init__.py
  src/app/reports/report_generator.py
  src/app/reports/suggestion_engine.py
  src/app/tools/__init__.py
  src/app/tools/peerread_tools.py
  src/app/utils/artifact_registry.py
  src/app/utils/error_messages.py
  src/app/utils/__init__.py
  src/app/utils/load_configs.py
  src/app/utils/load_settings.py
  src/app/utils/login.py
  src/app/utils/log.py
  src/app/utils/log_scrubbing.py
  src/app/utils/paths.py
  src/app/utils/prompt_sanitization.py
  src/app/utils/run_context.py
  src/app/utils/url_validation.py
  src/app/utils/utils.py
  src/examples/basic_evaluation.py
  src/examples/cc_solo.py
  src/examples/cc_teams.py
  src/examples/engine_comparison.py
  src/examples/_helpers.py
  src/examples/judge_settings_customization.py
  src/examples/mas_multi_agent.py
  src/examples/mas_single_agent.py
  src/examples/sweep_benchmark.py
  src/gui/components/footer.py
  src/gui/components/header.py
  src/gui/components/__init__.py
  src/gui/components/output.py
  src/gui/components/prompts.py
  src/gui/components/sidebar.py
  src/gui/config/config.py
  src/gui/config/__init__.py
  src/gui/config/styling.py
  src/gui/config/text.py
  src/gui/__init__.py
  src/gui/pages/agent_graph.py
  src/gui/pages/evaluation.py
  src/gui/pages/home.py
  src/gui/pages/__init__.py
  src/gui/pages/prompts.py
  src/gui/pages/run_app.py
  src/gui/pages/settings.py
  src/gui/pages/trace_viewer.py
  src/gui/utils/__init__.py
  src/gui/utils/log_capture.py
  src/run_cli.py
  src/run_gui.py
  src/run_sweep.py
```

### Signatures

**src/app/agents/agent_factories.py**:
```python
  17:class AgentFactory:
  20:    def __init__(self, endpoint_config: EndpointConfig | None = None):
  25:    def get_models(
  46:    def create_manager_agent(self, system_prompt: str | None = None) -> Agent:
  61:    def create_researcher_agent(self, system_prompt: str | None = None) -> Agent:
  76:    def create_analyst_agent(self, system_prompt: str | None = None) -> Agent:
  90:    def create_synthesiser_agent(self, system_prompt: str | None = None) -> Agent:
  106:def create_evaluation_agent(
  172:def create_simple_agent(model: Model, system_prompt: str) -> Agent:
```

**src/app/agents/agent_system.py**:
```python
  72:def initialize_logfire_instrumentation_from_settings(
  93:def resilient_tool_wrapper(tool: Tool[Any]) -> Tool[Any]:
  145:def _validate_model_return(
  193:async def _execute_traced_delegation(
  249:def _add_research_tool(
  285:def _add_analysis_tool(
  317:def _add_synthesis_tool(
  349:def _add_tools_to_manager_agent(
  381:def _create_agent(agent_config: AgentConfig) -> Agent[None, BaseModel]:
  392:def _create_optional_agent(
  421:def _get_result_type(
  448:def _create_manager(
  542:def get_manager(
  586:def _extract_rate_limit_detail(error: ModelHTTPError) -> str:
  599:def _handle_model_http_error(error: ModelHTTPError, provider: str, model_name: str) -> NoReturn:
  617:async def run_manager(
  686:def _determine_effective_token_limit(
  708:def _validate_token_limit(effective_limit: int | None) -> None:
  731:def _create_usage_limits(effective_limit: int | None) -> UsageLimits | None:
  745:def setup_agent_env(
```

**src/app/agents/logfire_instrumentation.py**:
```python
  25:class LogfireInstrumentationManager:
  32:    def __init__(self, config: LogfireConfig):
  36:    def _initialize_logfire(self) -> None:
  61:    def _configure_phoenix_endpoint(self) -> None:
  95:    def _configure_logfire(self) -> None:
  120:    def _log_initialization_info(self) -> None:
  138:def initialize_logfire_instrumentation(config: LogfireConfig) -> None:
  148:def get_instrumentation_manager() -> LogfireInstrumentationManager | None:
```

**src/app/app.py**:
```python
  30:    def op() -> Callable[[_T], _T]:  # type: ignore[reportRedeclaration]
  75:def _resolve_engine_type(engine: str, cc_teams: bool) -> str:
  90:async def _run_agent_execution(
  152:def _handle_download_mode(
  179:def _initialize_instrumentation() -> None:
  186:def _prepare_query(paper_id: str | None, query: str, prompts: dict[str, str]) -> tuple[str, bool]:
  204:def _prepare_result_dict(
  234:def _extract_cc_artifacts(cc_result: Any) -> tuple[str, Any, Any]:
  250:async def _run_cc_engine_path(
  310:async def _run_mas_engine_path(
  385:async def main(
```

**src/app/benchmark/sweep_analysis.py**:
```python
  16:def calculate_statistics(scores: list[float]) -> dict[str, float]:
  43:class CompositionStats(BaseModel):
  63:class SweepAnalyzer:
  69:    def __init__(self, results: list[tuple[AgentComposition, CompositeResult]]):
  77:    def analyze(self) -> list[CompositionStats]:
  143:def generate_markdown_summary(stats: list[CompositionStats]) -> str:
```

**src/app/benchmark/sweep_config.py**:
```python
  15:class AgentComposition(BaseModel):
  26:    def get_name(self) -> str:
  51:class SweepConfig(BaseModel):
  102:    def validate_compositions_not_empty(cls, v: list[AgentComposition]) -> list[AgentComposition]:
  120:    def validate_repetitions_positive(cls, v: int) -> int:
  138:    def validate_paper_ids_not_empty(cls, v: list[str]) -> list[str]:
  155:def generate_all_compositions() -> list[AgentComposition]:
```

**src/app/benchmark/sweep_runner.py**:
```python
  26:class SweepRunner:
  33:    def __init__(self, config: SweepConfig):
  42:    def _build_judge_settings(self) -> JudgeSettings | None:
  297:async def run_sweep(config: SweepConfig) -> list[tuple[AgentComposition, CompositeResult]]:
```

**src/app/common/error_messages.py**:
```python
  11:def api_connection_error(error: str) -> str:
  24:def failed_to_load_config(error: str) -> str:
  37:def file_not_found(file_path: str | Path) -> str:
  50:def generic_exception(error: str) -> str:
  63:def invalid_data_model_format(error: str) -> str:
  76:def invalid_json(error: str) -> str:
  89:def invalid_type(expected_type: str, actual_type: str) -> str:
  103:def get_key_error(error: str) -> str:
```

**src/app/common/models.py**:
```python
  11:class CommonBaseModel(BaseModel):
```

**src/app/config/app_env.py**:
```python
  11:class AppEnv(BaseSettings):
```

**src/app/config/common_settings.py**:
```python
  13:class CommonSettings(BaseSettings):
```

**src/app/config/judge_settings.py**:
```python
  16:class JudgeSettings(BaseSettings):
  117:    def get_enabled_tiers(self) -> set[int]:
  126:    def is_tier_enabled(self, tier: int) -> bool:
  138:    def get_performance_targets(self) -> dict[str, float]:
```

**src/app/config/logfire_config.py**:
```python
  13:class LogfireConfig(BaseModel):
  27:    def from_settings(cls, settings: JudgeSettings) -> LogfireConfig:
```

**src/app/config/peerread_config.py**:
```python
  8:class PeerReadConfig(BaseModel):
```

**src/app/data_models/app_models.py**:
```python
  25:class ResearchResult(BaseModel):
  33:class ResearchResultSimple(BaseModel):
  41:class AnalysisResult(BaseModel):
  49:class ResearchSummary(BaseModel):
  59:class ProviderMetadata(BaseModel):
  73:class ProviderConfig(BaseModel):
  82:class ChatConfig(BaseModel):
  90:class EndpointConfig(BaseModel):
  101:class AgentConfig(BaseModel):
  118:    def validate_tools(cls, v: list[Any]) -> list[Tool[Any]]:  # noqa: N805
  131:class ModelDict(BaseModel):
  141:class EvalConfig(BaseModel):
```

**src/app/data_models/evaluation_models.py**:
```python
  15:class TechnicalAccuracyAssessment(BaseModel):
  26:class ConstructivenessAssessment(BaseModel):
  35:class PlanningRationalityAssessment(BaseModel):
  44:class Tier1Result(BaseModel):
  66:class Tier2Result(BaseModel):
  84:class Tier3Result(BaseModel):
  99:class CompositeEvaluationResult(BaseModel):
  128:class CompositeResult(BaseModel):
  183:class GraphTraceData(BaseModel):
  203:    def from_trace_dict(
  226:class AgentMetrics(BaseModel):
  233:    def get_agent_composite_score(self) -> float:
  247:class EvaluationResults(BaseModel):
  254:    def is_complete(self) -> bool:
  259:class BaselineComparison(BaseModel):
  288:class PeerReadEvalResult(BaseModel):
```

**src/app/data_models/peerread_models.py**:
```python
  39:def _coerce_score_to_int(v: Any) -> Any:
  64:def _coerce_presentation_format(v: Any) -> Any:
  81:class PeerReadReview(BaseModel):
  139:    def is_compliant(self) -> bool:
  156:class PeerReadPaper(BaseModel):
  168:class DownloadResult(BaseModel):
  177:class GeneratedReview(BaseModel):
  257:    def validate_comments_structure(cls, v: str) -> str:  # noqa: N805
  276:    def to_peerread_format(self) -> dict[str, str | None]:
  294:class ReviewGenerationResult(BaseModel):
```

**src/app/data_models/report_models.py**:
```python
  12:class SuggestionSeverity(StrEnum):
  26:class Suggestion(BaseModel):
```

**src/app/data_utils/datasets_peerread.py**:
```python
  31:class DataTypeSpec:
  50:def _perform_downloads(
  84:def _verify_downloads(
  115:def _validate_download_results(
  139:def download_peerread_dataset(
  193:def load_peerread_config() -> PeerReadConfig:
  215:class PeerReadDownloader:
  222:    def __init__(self, config: PeerReadConfig):
  238:    def _construct_url(
  274:    def _extract_paper_id_from_filename(
  293:    def _discover_available_files(
  342:    def _handle_download_error(
  369:    def download_file(
  419:    def _get_cache_filename(self, data_type: str, paper_id: str) -> str:
  435:    def _save_file_data(
  456:    def _download_single_data_type(
  500:    def _download_paper_all_types(
  532:    def download_venue_split(
  586:class PeerReadLoader:
  589:    def __init__(self, config: PeerReadConfig | None = None):
  599:    def _extract_text_from_parsed_data(self, parsed_data: dict[str, Any]) -> str:
  615:    def _load_parsed_file(self, parsed_file: Path) -> str | None:
  632:    def _find_parsed_pdf_in_split(
  658:    def load_parsed_pdf_content(self, paper_id: str) -> str | None:
  677:    def get_raw_pdf_path(self, paper_id: str) -> str | None:
  693:    def _create_review_from_dict(self, review_data: dict[str, Any]) -> PeerReadReview:
  704:    def _validate_papers(
  756:    def load_papers(
  809:    def _load_paper_from_path(self, cache_path: Path, paper_id: str) -> PeerReadPaper | None:
  828:    def get_paper_by_id(self, paper_id: str) -> PeerReadPaper | None:
  849:    def query_papers(
```

**src/app/data_utils/review_persistence.py**:
```python
  14:class ReviewPersistence:
  17:    def __init__(self, reviews_dir: str = _DEFAULT_REVIEWS_DIR):
  27:    def save_review(
  76:    def load_review(self, filepath: str) -> tuple[str, PeerReadReview]:
  93:    def list_reviews(self, paper_id: str | None = None) -> list[str]:
  105:    def get_latest_review(self, paper_id: str) -> str | None:
```

**src/app/engines/cc_engine.py**:
```python
  48:def _sanitize_cc_query(query: str) -> str:
  75:class CCResult(BaseModel):
  97:def build_cc_query(query: str, paper_id: str | None = None, cc_teams: bool = False) -> str:
  135:def check_cc_available() -> bool:
  148:def _parse_jsonl_line(line: str) -> dict[str, Any] | None:
  172:def _apply_event(
  200:def parse_stream_json(stream: Iterator[str]) -> CCResult:
  240:def extract_cc_review_text(cc_result: CCResult) -> str:
  257:def _normalize_task_started(artifact: dict[str, Any]) -> dict[str, Any]:
  273:def cc_result_to_graph_trace(cc_result: CCResult) -> GraphTraceData:
  313:def _tee_stream(stream: Iterator[str], path: Path) -> Iterator[str]:
  334:def _persist_solo_stream(raw_stdout: str, stream_path: Path) -> None:
  346:def run_cc_solo(query: str, timeout: int = 600, run_context: RunContext | None = None) -> CCResult:
  413:def _wait_with_timeout(proc: subprocess.Popen[str], remaining: int, timeout: int) -> None:
  434:def run_cc_teams(query: str, timeout: int = 600, run_context: RunContext | None = None) -> CCResult:
```

**src/app/judge/baseline_comparison.py**:
```python
  15:def compare(
  90:def compare_all(
```

**src/app/judge/cc_trace_adapter.py**:
```python
  19:class CCTraceAdapter:
  34:    def __init__(self, artifacts_dir: Path, *, tasks_dir: Path | None = None):
  58:    def _detect_mode(self) -> Literal["teams", "solo"]:
  85:    def _resolve_tasks_dir(self, explicit_tasks_dir: Path | None) -> Path | None:
  129:    def parse(self) -> GraphTraceData:
  143:    def _parse_teams_mode(self) -> GraphTraceData:
  188:    def _parse_solo_mode(self) -> GraphTraceData:
  230:    def _parse_agent_messages(self) -> list[dict[str, Any]]:
  252:    def _parse_team_tasks(self) -> list[dict[str, Any]]:
  289:    def _parse_solo_tool_calls(self) -> list[dict[str, Any]]:
  314:    def _derive_timing_data(
  343:    def _extract_coordination_events(self) -> list[dict[str, Any]]:
```

**src/app/judge/composite_scorer.py**:
```python
  24:class CompositeScorer:
  39:    def __init__(
  81:    def extract_metric_values(self, results: EvaluationResults) -> dict[str, float]:
  134:    def calculate_composite_score(self, results: EvaluationResults) -> float:
  160:    def map_to_recommendation(self, composite_score: float) -> str:
  179:    def get_recommendation_weight(self, recommendation: str) -> float:
  190:    def _score_and_recommend(
  208:    def _detect_single_agent_mode(self, trace_data: GraphTraceData) -> bool:
  232:    def evaluate_composite(self, results: EvaluationResults) -> CompositeResult:
  288:    def get_scoring_summary(self) -> dict[str, Any]:
  302:    def _calculate_tool_score(self, tools_used: list[str]) -> float:
  311:    def _calculate_coherence_score(
  326:    def _calculate_coordination_score(self, delegation_count: int, output_length: int) -> float:
  338:    def assess_agent_performance(
  376:    def _determine_excluded_metrics(
  404:    def _extract_tier1_metrics(
  417:    def _extract_tier3_metrics(
  428:    def _extract_metrics_with_exclusions(
  456:    def evaluate_composite_with_trace(
  519:    def evaluate_composite_with_optional_tier2(self, results: EvaluationResults) -> CompositeResult:
```

**src/app/judge/evaluation_pipeline.py**:
```python
  31:class EvaluationPipeline:
  40:    def __init__(
  83:    def enabled_tiers(self) -> set[int]:
  92:    def performance_targets(self) -> dict[str, float]:
  101:    def fallback_strategy(self) -> str:
  110:    def config_path(self) -> Path | None:
  119:    def execution_stats(self) -> dict[str, Any]:
  127:    def _is_tier_enabled(self, tier: int) -> bool:
  138:    def _skip_tier1(self, reason: str) -> tuple[None, float]:
  285:    def _create_trace_data(self, execution_trace: dict[str, Any] | None) -> GraphTraceData:
  289:    def _should_apply_fallback(self, results: EvaluationResults) -> bool:
  302:    def _generate_composite_score(
  331:    def _composite_without_tier1(self, results: EvaluationResults) -> CompositeResult:
  397:    def _composite_without_tier2(self, results: EvaluationResults) -> CompositeResult:
  442:    def _handle_tier3_error(
  515:    def _apply_fallback_strategy(self, results: EvaluationResults) -> EvaluationResults:
  570:    def _log_metric_comparison(
  716:    def get_execution_stats(self) -> dict[str, Any]:
  724:    def get_pipeline_summary(self) -> dict[str, Any]:
```

**src/app/judge/evaluation_runner.py**:
```python
  27:def _load_reference_reviews(paper_id: str | None) -> list[str] | None:
  48:def _extract_paper_and_review_content(manager_output: Any) -> tuple[str, str]:
  78:def _load_paper_content(paper_id: str) -> str:
  101:def _resolve_execution_trace(execution_trace: Any, execution_id: str | None) -> Any:
  133:def build_graph_from_trace(execution_id: str | None) -> nx.DiGraph[str] | None:
  160:async def run_evaluation_if_enabled(
  259:async def run_baseline_comparisons(
```

**src/app/judge/graph_analysis.py**:
```python
  28:class GraphAnalysisEngine:
  36:    def __init__(self, settings: JudgeSettings) -> None:
  63:    def _validate_trace_data(self, trace_data: GraphTraceData) -> None:
  79:    def _validate_agent_interactions(self, interactions: list[dict[str, Any]]) -> None:
  87:    def _validate_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
  95:    def _check_data_size_limits(self, trace_data: GraphTraceData) -> None:
  110:    def _with_timeout(self, func: Any, *args: Any, **kwargs: Any) -> Any:
  145:    def _accumulate_tool_outcomes(
  176:    def _build_tool_graph(
  212:    def analyze_tool_usage_patterns(self, trace_data: GraphTraceData) -> dict[str, float]:
  257:    def analyze_agent_interactions(self, trace_data: GraphTraceData) -> dict[str, float]:
  289:    def _build_interaction_graph(self, interactions: list[dict[str, Any]]) -> Any:
  303:    def _calculate_communication_efficiency(self, graph: Any) -> float:
  314:    def _calculate_coordination_centrality(self, graph: Any) -> float:
  322:    def analyze_task_distribution(self, trace_data: GraphTraceData) -> float:
  349:    def _count_agent_activities(self, trace_data: GraphTraceData) -> dict[str, int]:
  363:    def _calculate_balance_score(self, activities: list[int]) -> float:
  376:    def _calculate_path_convergence(self, graph: Any) -> float:
  398:    def _calculate_connected_graph_convergence(self, graph: Any, undirected_graph: Any) -> float:
  407:    def _normalize_path_length(self, num_nodes: int, avg_path_length: float) -> float:
  418:    def evaluate_graph_metrics(self, trace_data: GraphTraceData) -> Tier3Result:
  476:    def export_trace_to_networkx(self, trace_data: GraphTraceData) -> nx.DiGraph[str] | None:
  503:    def _add_agent_interactions_to_graph(
  521:    def _ensure_agent_node(self, graph: Any, agent_id: str) -> None:
  526:    def _add_interaction_edge(self, graph: Any, source: str, target: str) -> None:
  535:    def _add_tool_usage_to_graph(self, graph: Any, tool_calls: list[dict[str, Any]]) -> None:
  544:    def _ensure_tool_node(self, graph: Any, tool_name: str) -> None:
  549:    def _add_tool_usage_edge(self, graph: Any, agent_id: str, tool_name: str) -> None:
  557:    def _add_graph_metadata(
  572:def evaluate_single_graph_analysis(
```

**src/app/judge/graph_builder.py**:
```python
  16:def build_interaction_graph(trace_data: GraphTraceData) -> nx.DiGraph[str]:
```

**src/app/judge/graph_export.py**:
```python
  20:def export_graph_json(graph: nx.DiGraph[str], output_dir: Path) -> Path:
  38:def export_graph_png(graph: nx.DiGraph[str], output_dir: Path) -> Path:
  112:def persist_graph(graph: nx.DiGraph[str] | None, output_dir: Path) -> None:
```

**src/app/judge/llm_evaluation_managers.py**:
```python
  33:class LLMJudgeEngine:
  36:    def __init__(
  102:    def _resolve_model(
  131:    def _resolve_provider_key(self, provider: str, env_config: AppEnv) -> tuple[bool, str | None]:
  147:    def select_available_provider(self, env_config: AppEnv) -> tuple[str, str, str | None] | None:
  357:    def _handle_assessment_failures(
  408:    def _calculate_overall_score(
  484:    def _extract_planning_decisions(self, execution_trace: dict[str, Any]) -> str:
  511:    def _fallback_constructiveness_check(self, review: str) -> float:
  541:    def _fallback_planning_check(self, execution_trace: dict[str, Any]) -> float:
  567:    def _complete_fallback(
```

**src/app/judge/performance_monitor.py**:
```python
  14:class PerformanceMonitor:
  22:    def __init__(self, performance_targets: dict[str, float]):
  31:    def _initialize_stats(self) -> dict[str, Any]:
  49:    def reset_stats(self) -> None:
  53:    def record_tier_execution(self, tier: int, duration: float) -> None:
  68:    def record_tier_failure(
  91:    def record_fallback_usage(self, fallback_used: bool) -> None:
  100:    def finalize_execution(self, total_time: float) -> None:
  109:    def _detect_bottlenecks(
  136:    def _check_tier_targets(self, tier_times: dict[str, float]) -> None:
  154:    def _check_total_time_target(self, total_time: float) -> None:
  163:    def _analyze_performance(self, total_time: float) -> None:
  182:    def _record_performance_warning(self, warning_type: str, message: str, value: float) -> None:
  199:    def get_execution_stats(self) -> dict[str, Any]:
  217:    def get_performance_summary(self) -> str:
  229:    def has_performance_issues(self) -> bool:
  240:    def get_bottlenecks(self) -> list[dict[str, Any]]:
  248:    def get_warnings(self) -> list[dict[str, Any]]:
  256:    def get_failures(self) -> list[dict[str, Any]]:
```

**src/app/judge/plugins/base.py**:
```python
  18:class EvaluatorPlugin(ABC):
  31:    def name(self) -> str:
  41:    def tier(self) -> int:
  50:    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
  67:    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
  79:class PluginRegistry:
  86:    def __init__(self) -> None:
  90:    def register(self, plugin: EvaluatorPlugin) -> None:
  105:    def get_plugin(self, name: str) -> EvaluatorPlugin | None:
  116:    def list_plugins(self) -> list[EvaluatorPlugin]:
  124:    def execute_all(self, input_data: BaseModel) -> list[BaseModel]:
```

**src/app/judge/plugins/graph_metrics.py**:
```python
  21:class GraphEvaluatorPlugin(EvaluatorPlugin):
  33:    def __init__(self, timeout_seconds: float | None = None):
  44:    def name(self) -> str:
  53:    def tier(self) -> int:
  61:    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
  106:    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
```

**src/app/judge/plugins/llm_judge.py**:
```python
  22:class LLMJudgePlugin(EvaluatorPlugin):
  34:    def __init__(self, timeout_seconds: float | None = None):
  45:    def name(self) -> str:
  54:    def tier(self) -> int:
  62:    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
  98:    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
```

**src/app/judge/plugins/traditional.py**:
```python
  20:class TraditionalMetricsPlugin(EvaluatorPlugin):
  32:    def __init__(self, timeout_seconds: float | None = None):
  43:    def name(self) -> str:
  52:    def tier(self) -> int:
  60:    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
  92:    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
```

**src/app/judge/trace_processors.py**:
```python
  27:class TraceEvent:
  38:class ProcessedTrace:
  50:class TraceCollector:
  57:    def __init__(self, settings: JudgeSettings) -> None:
  80:    def _init_database(self):
  118:    def start_execution(self, execution_id: str) -> None:
  132:    def log_agent_interaction(
  160:    def log_tool_call(
  195:    def log_coordination_event(
  227:    def end_execution(self) -> ProcessedTrace | None:
  262:    def _process_events(self) -> ProcessedTrace:
  313:    def _store_trace(self, trace: ProcessedTrace) -> None:
  394:    def _parse_trace_events(
  414:    def _build_timing_data(self, execution: tuple[Any, ...]) -> dict[str, Any]:
  422:    def load_trace(self, execution_id: str) -> GraphTraceData | None:
  472:    def list_executions(self, limit: int = 50) -> list[dict[str, Any]]:
  515:class TraceProcessor:
  518:    def __init__(self, collector: TraceCollector):
  526:    def process_for_graph_analysis(self, execution_id: str) -> dict[str, Any] | None:
  552:def get_trace_collector(settings: JudgeSettings | None = None) -> TraceCollector:
  573:def trace_execution(execution_id: str) -> Any:
  586:    def decorator(func: Any) -> Any:
```

**src/app/judge/traditional_metrics.py**:
```python
  35:class SimilarityScores:
  44:class TraditionalMetricsEngine:
  56:    def __init__(self):
  68:    def _get_bertscore_model(self):
  88:    def _compute_word_overlap_fallback(self, text1: str, text2: str) -> float:
  101:    def compute_cosine_similarity(self, text1: str, text2: str) -> float:
  135:    def _compute_jaccard_basic(self, text1: str, text2: str) -> float:
  147:    def _compute_jaccard_regex_fallback(self, text1: str, text2: str) -> float:
  159:    def compute_jaccard_similarity(self, text1: str, text2: str, enhanced: bool = False) -> float:
  194:    def _compute_char_overlap_fallback(self, text1: str, text2: str) -> float:
  209:    def compute_levenshtein_similarity(self, text1: str, text2: str) -> float:
  237:    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
  264:    def measure_execution_time(self, start_time: float, end_time: float) -> float:
  281:    def assess_task_success(
  315:    def compute_all_similarities(
  346:    def find_best_match(
  380:    def evaluate_traditional_metrics(
  437:    def evaluate_enhanced_similarity(
  501:def evaluate_single_traditional(
  541:def evaluate_single_enhanced(
  583:def create_evaluation_result(
  667:def calculate_cosine_similarity(text1: str, text2: str) -> float:
  688:def calculate_jaccard_similarity(text1: str, text2: str) -> float:
  705:def evaluate_review_similarity(agent_review: str, ground_truth: str) -> float:
```

**src/app/llms/models.py**:
```python
  17:def get_llm_model_name(provider: str, model_name: str) -> str:
  50:def _create_model_for_provider(
  129:def create_llm_model(endpoint_config: EndpointConfig) -> Model:
  149:def create_agent_models(
  179:def create_simple_model(provider: str, model_name: str, api_key: str | None = None) -> Model:
```

**src/app/llms/providers.py**:
```python
  14:def get_api_key(
  53:def get_provider_config(provider: str, providers: dict[str, ProviderConfig]) -> ProviderConfig:
  79:def setup_llm_environment(api_keys: dict[str, str]) -> None:
  97:def get_supported_providers() -> list[str]:
```

**src/app/reports/report_generator.py**:
```python
  25:def generate_report(
  52:def save_report(markdown: str, output_path: Path) -> None:
  73:def _render_executive_summary(result: CompositeResult) -> str:
  101:def _render_tier_breakdown(result: CompositeResult) -> str:
  140:def _render_weaknesses(suggestions: list[Suggestion]) -> str:
```

**src/app/reports/suggestion_engine.py**:
```python
  110:def _classify_severity(score: float) -> SuggestionSeverity:
  126:class SuggestionEngine:
  142:    def __init__(self, no_llm_suggestions: bool = False) -> None:
  150:    def generate(self, result: CompositeResult) -> list[Suggestion]:
```

**src/app/tools/peerread_tools.py**:
```python
  35:def read_paper_pdf(
  85:async def _traced_tool_call(  # noqa: UP047
  138:def add_peerread_tools_to_agent(agent: Agent[None, BaseModel], agent_id: str = "manager"):
  253:def _truncate_paper_content(abstract: str, body: str, max_length: int) -> str:
  291:def _load_paper_content_with_fallback(
  320:def _load_and_format_template(
  377:def add_peerread_review_tools_to_agent(
  556:def add_peerread_review_tools_to_manager(
```

**src/app/utils/artifact_registry.py**:
```python
  18:class ArtifactRegistry:
  26:    def __init__(self) -> None:
  31:    def register(self, label: str, path: Path) -> None:
  42:    def summary(self) -> list[tuple[str, Path]]:
  51:    def reset(self) -> None:
  56:    def format_summary_block(self) -> str:
  78:def get_artifact_registry() -> ArtifactRegistry:
  91:def _reset_global_registry() -> None:  # pyright: ignore[reportUnusedFunction]
```

**src/app/utils/error_messages.py**:
```python
  11:def api_connection_error(error: str) -> str:
  18:def failed_to_load_config(error: str) -> str:
  25:def file_not_found(file_path: str | Path) -> str:
  32:def generic_exception(error: str) -> str:
  39:def invalid_data_model_format(error: str) -> str:
  46:def invalid_json(error: str) -> str:
  53:def invalid_type(expected_type: str, actual_type: str) -> str:
  60:def get_key_error(error: str) -> str:
```

**src/app/utils/load_configs.py**:
```python
  27:def load_config[T: BaseModel](config_path: str | Path, data_model: type[T]) -> T:
```

**src/app/utils/load_settings.py**:
```python
  20:def load_config(config_path: str | Path) -> ChatConfig:
```

**src/app/utils/login.py**:
```python
  17:def login(project_name: str, chat_env_config: AppEnv):
```

**src/app/utils/log_scrubbing.py**:
```python
  62:def scrub_log_record(record: dict[str, Any]) -> bool:
  87:def get_logfire_scrubbing_patterns() -> list[str]:
```

**src/app/utils/paths.py**:
```python
  8:def get_project_root() -> Path:
  17:def get_app_root() -> Path:
  27:def resolve_project_path(relative_path: str) -> Path:
  39:def resolve_app_path(relative_path: str) -> Path:
  55:def get_config_dir() -> Path:
  64:def resolve_config_path(filename: str) -> Path:
  80:def get_review_template_path() -> Path:
```

**src/app/utils/prompt_sanitization.py**:
```python
  16:def sanitize_for_prompt(content: str, max_length: int, delimiter: str = "content") -> str:
  38:def sanitize_paper_title(title: str) -> str:
  50:def sanitize_paper_abstract(abstract: str) -> str:
  62:def sanitize_paper_content(content: str, max_length: int = 50000) -> str:
  84:def sanitize_review_text(review: str) -> str:
```

**src/app/utils/run_context.py**:
```python
  25:def _sanitize_path_component(value: str) -> str:
  42:class RunContext:
  63:    def create(
  108:    def _write_metadata(self, cli_args: dict[str, Any] | None) -> None:
  126:    def stream_path(self) -> Path:
  136:    def trace_path(self) -> Path:
  145:    def review_path(self) -> Path:
  154:    def report_path(self) -> Path:
  163:    def evaluation_path(self) -> Path:
  172:    def graph_json_path(self) -> Path:
  181:    def graph_png_path(self) -> Path:
  194:def get_active_run_context() -> RunContext | None:
  203:def set_active_run_context(ctx: RunContext | None) -> None:
```

**src/app/utils/url_validation.py**:
```python
  27:def validate_url(url: str) -> str:
```

**src/app/utils/utils.py**:
```python
  25:def log_research_result(summary: ResearchSummary, usage: RunUsage) -> None:
```

**src/examples/basic_evaluation.py**:
```python
  30:def _make_synthetic_paper() -> PeerReadPaper:
  56:def _make_synthetic_trace() -> GraphTraceData:
  83:async def run_example() -> CompositeResult:
```

**src/examples/cc_solo.py**:
```python
  35:async def run_example() -> CCResult | None:
```

**src/examples/cc_teams.py**:
```python
  36:async def run_example() -> CCResult | None:
```

**src/examples/engine_comparison.py**:
```python
  83:async def evaluate_mas(trace: GraphTraceData, label: str) -> CompositeResult:
  106:def load_cc_trace(artifacts_dir: Path) -> GraphTraceData | None:
  131:async def run_example() -> dict[str, CompositeResult]:
```

**src/examples/_helpers.py**:
```python
  6:def print_mas_result(output: dict[str, Any] | None) -> None:
```

**src/examples/judge_settings_customization.py**:
```python
  29:def example_timeout_adjustment() -> JudgeSettings:
  49:def example_tier_selection() -> JudgeSettings:
  62:def example_provider_selection() -> JudgeSettings:
  80:def example_composite_thresholds() -> JudgeSettings:
```

**src/examples/mas_multi_agent.py**:
```python
  33:async def run_example() -> dict[str, Any] | None:
```

**src/examples/mas_single_agent.py**:
```python
  32:async def run_example() -> dict[str, Any] | None:
```

**src/examples/sweep_benchmark.py**:
```python
  34:def _build_sweep_config(output_dir: Path) -> SweepConfig:
  74:async def run_example() -> list[tuple[AgentComposition, CompositeResult]]:
```

**src/gui/components/footer.py**:
```python
  4:def render_footer(footer_caption: str):
```

**src/gui/components/header.py**:
```python
  4:def render_header(header_title: str):
```

**src/gui/components/output.py**:
```python
  14:def render_output(
```

**src/gui/components/prompts.py**:
```python
  4:def render_prompt_editor(prompt_name: str, prompt_value: str, height: int = 150) -> str | None:
```

**src/gui/components/sidebar.py**:
```python
  7:def render_sidebar(sidebar_title: str, execution_state: str = "idle") -> str:
```

**src/gui/config/config.py**:
```python
  9:def resolve_service_url(port: int) -> str:
```

**src/gui/config/styling.py**:
```python
  45:def add_custom_styling(page_title: str):
  61:def _is_streamlit_light_mode() -> bool:
  77:def get_active_theme_name() -> str:
  89:def get_active_theme() -> dict[str, str]:
  99:def is_light_theme(theme_name: str) -> bool:
  111:def get_graph_font_color() -> str:
  125:def get_theme_node_colors() -> tuple[str, str]:
  136:def get_graph_node_colors() -> tuple[str, str]:
  148:def get_theme_bgcolor() -> str:
```

**src/gui/pages/agent_graph.py**:
```python
  44:def render_agent_graph(
```

**src/gui/pages/evaluation.py**:
```python
  34:def _safe_resolve_dir(user_path: str) -> Path | None:
  51:def format_metric_label(metric_key: str) -> str:
  65:def _extract_graph_metrics(metric_scores: dict[str, float]) -> dict[str, float]:
  83:def _extract_text_metrics(metric_scores: dict[str, float]) -> dict[str, float]:
  96:def _render_overall_results(
  136:def _render_tier_scores(result: CompositeResult) -> None:
  184:def _render_metrics_comparison(result: CompositeResult) -> None:
  217:def _render_three_way_table(comparisons: list[BaselineComparison]) -> None:
  237:def _render_tier_deltas(comp: BaselineComparison) -> None:
  264:def _render_single_comparison(comp: BaselineComparison) -> None:
  276:def render_baseline_comparison(comparisons: list[BaselineComparison] | None) -> None:
  300:def _validate_dir_input(label: str, key: str, default: str = "") -> None:
  313:def _render_empty_state() -> None:
  334:def _render_evaluation_details(result: CompositeResult) -> None:
  353:def render_evaluation(result: CompositeResult | None = None) -> None:
```

**src/gui/pages/home.py**:
```python
  6:def render_home():
```

**src/gui/pages/prompts.py**:
```python
  19:def render_prompts(chat_config: ChatConfig | BaseModel):  # -> dict[str, str]:
```

**src/gui/pages/run_app.py**:
```python
  52:def _collect_unique_papers(
  80:def _load_available_papers() -> list[PeerReadPaper]:
  100:def _format_paper_option(paper: PeerReadPaper) -> str:
  112:def _get_session_config(provider: str | None) -> tuple[str, bool, bool, bool]:
  130:def _build_judge_settings_from_session() -> JudgeSettings | None:
  154:def _build_common_settings_from_session() -> CommonSettings | None:
  176:def _format_enabled_agents(
  199:def _initialize_execution_state() -> None:
  205:def _get_execution_state() -> str:
  214:def _capture_execution_logs(capture: LogCapture) -> None:
  224:def _render_artifact_summary_panel() -> None:
  241:def _render_debug_log_panel() -> None:
  258:def _prepare_cc_result(
  278:def _store_successful_result(result: dict[str, Any] | None) -> None:
  299:def _store_execution_error(e: Exception) -> None:
  308:async def _execute_query_background(
  388:def _display_configuration(provider: str, token_limit: int | None, agents_text: str) -> None:
  402:def _display_execution_result(execution_state: str) -> None:
  466:def _render_paper_selection_input() -> tuple[str, str | None]:
  509:async def _handle_query_submission(
  559:def _render_report_section(composite_result: CompositeResult | None) -> None:
  602:def _render_engine_selector() -> tuple[str, bool]:
  635:def _render_engine_status(
  673:def _render_query_input() -> tuple[str, str | None]:
  692:async def render_app(provider: str | None = None, chat_config_file: str | Path | None = None):
```

**src/gui/pages/settings.py**:
```python
  24:def _render_agent_configuration() -> None:
  91:def _render_tier_configuration(judge_settings: JudgeSettings) -> None:
  132:def _render_composite_scoring(judge_settings: JudgeSettings) -> None:
  172:def _get_model_options(chat_config: object, provider: str, fallback_model: str) -> list[str]:
  189:def _render_provider_model_selectboxes(
  262:def _render_tier2_llm_judge(judge_settings: JudgeSettings) -> None:
  351:def _render_observability_settings(judge_settings: JudgeSettings) -> None:
  374:def _render_common_settings(common_settings: CommonSettings) -> None:
  413:def _render_reset_button() -> None:
  427:def render_settings(common_settings: CommonSettings, judge_settings: JudgeSettings) -> None:
```

**src/gui/pages/trace_viewer.py**:
```python
  19:def _get_db_path() -> Path:
  28:def _query_executions(db_path: Path) -> list[dict[str, object]]:
  62:def _query_events(db_path: Path, execution_id: str) -> list[dict[str, object]]:
  97:def render_trace_viewer() -> None:
```

**src/gui/utils/log_capture.py**:
```python
  15:class LogCapture:
  27:    def __init__(self) -> None:
  33:    def add_log_entry(self, timestamp: str, level: str, module: str, message: str) -> None:
  56:    def get_new_logs_since(self, index: int) -> list[dict[str, str]]:
  72:    def log_count(self) -> int:
  81:    def get_logs(self) -> list[dict[str, str]]:
  90:    def clear(self) -> None:
  95:    def format_html(self) -> str:
  104:    def format_logs_as_html(logs: list[dict[str, str]]) -> str:
  149:    def _sink_handler(self, message: Any) -> None:
  163:    def attach_to_logger(self) -> int:
  172:    def detach_from_logger(self, handler_id: int) -> None:
```

**src/run_cli.py**:
```python
  94:def parse_args(argv: list[str]) -> dict[str, Any]:
  110:def _run_cc_engine(args: dict[str, Any], cc_teams: bool) -> Any:
  133:def _maybe_generate_report(result_dict: dict[str, Any], no_llm_suggestions: bool) -> None:
  169:def cli_main() -> None:
```

**src/run_gui.py**:
```python
  48:def get_session_state_defaults() -> dict[str, str | bool]:
  63:def initialize_session_state() -> None:
  75:async def main():
```

**src/run_sweep.py**:
```python
  20:def parse_args() -> argparse.Namespace:
  95:def _load_config_from_file(config_path: Path) -> SweepConfig | None:
  130:def _build_config_from_args(args: argparse.Namespace) -> SweepConfig | None:
  167:async def main_async() -> int:
  209:def main() -> int:
```

