# User Story: Agents-eval

## Problem Statement

The multi-agent system (MAS) generates scientific paper reviews via agent delegation (Manager → Researcher → Analyst → Synthesizer), but the execution graph is never captured or evaluated. There is no way to compare graph-based coordination metrics (how agents coordinate) against conventional text similarity metrics (what agents produce). Generation (`run_manager()`) and evaluation (`EvaluationPipeline.evaluate_comprehensive()`) are disconnected, and `TraceCollector` is not wired into agent execution.

## Target Users

AI researchers evaluating multi-agent system coordination quality using the PeerRead dataset.

## Value Proposition

Understand whether graph-based analysis (how agents coordinate) provides different insights than text similarity (what agents produce) for the same review generation task. Enable automated evaluation immediately after generation so researchers can iterate on agent configurations with rapid feedback.

## User Stories

- As a researcher, I want evaluation to run automatically after review generation so I don't have to wire it manually.
- As a researcher, I want real agent execution traces captured as GraphTraceData so Tier 3 graph analysis uses actual data instead of synthetic traces.
- As a researcher, I want to see graph metrics alongside text metrics so I can compare evaluation approaches.
- As a researcher, I want to skip evaluation with `--skip-eval` when I only need generation.
- As a researcher, I want evaluation settings configurable via environment variables so I can tune tier weights, timeouts, and model selection without editing code or JSON files.
- As a researcher, I want local tracing via `pip install` (Logfire + Phoenix) instead of 11 Docker containers so I can inspect agent traces without complex infrastructure setup.
- As a researcher, I want a Streamlit dashboard showing Tier 1/2/3 evaluation scores so I can visually compare graph-based and text-based metrics without parsing log output.
- As a researcher, I want an interactive agent graph visualization so I can see how agents delegated tasks and coordinated during review generation.
- As a researcher, I want to compare PydanticAI MAS evaluation results against Claude Code baselines (solo and teams) so I can quantify the coordination quality difference between orchestration approaches.

## Success Criteria

1. `make run_cli ARGS="--paper-number=ID"` generates a review AND evaluates it automatically.
2. GraphTraceData contains real agent delegations, tool calls, and timing data from MAS execution.
3. Logs show Tier 1 (text) vs Tier 3 (graph) scores side by side with individual metric breakdowns.
4. `--skip-eval` flag skips evaluation when only generation is needed.
5. `make validate` passes with all existing and new tests.
6. `phoenix serve` starts a local trace viewer at localhost:6006; agent traces appear via Logfire auto-instrumentation without manual decorators.
7. Streamlit "Evaluation Results" page displays tier scores and graph-vs-text comparison charts.
8. Streamlit "Agent Graph" page renders the NetworkX delegation graph interactively via Pyvis.

## Constraints

- Python 3.13 with pydantic-ai framework.
- Must use existing `EvaluationPipeline` API (no restructure to plugin architecture in Sprint 2).
- Must use existing `TraceCollector` API for graph data capture.
- Settings via pydantic-settings (`JudgeSettings` with `JUDGE_` prefix), consistent with `CommonSettings` (`EVAL_` prefix). No JSON config files at runtime.
- Tracing via Logfire SDK + Arize Phoenix (zero Docker containers). `logfire.instrument_pydantic_ai()` auto-instruments all PydanticAI agents.
- Streamlit + Phoenix are complementary (separate services on different ports), not embedded. Phoenix for trace inspection, Streamlit for custom evaluation dashboards.

## Out of Scope

- ~~Plugin architecture — restructuring `evals/` to `judge/` with `EvaluatorPlugin` interface.~~ (delivered Sprint 3)
- ~~CC OTel tracing — standalone CC telemetry plugin.~~ (delivered Sprint 3)
- ~~Evaluation baselines — CC solo and teams comparison.~~ (Sprint 4, Features 5-7)
- Multi-channel deployment — FastAPI REST and MCP server endpoints.
- Model-aware content truncation — token-limit-aware truncation for provider rate limits.
- Migration cleanup — removing backward-compatibility shims.
- A2A protocol migration (PydanticAI stays).
- Streamlit UI redesign (existing UI stays as-is).
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead).
- HuggingFace `datasets` library (use GitHub API downloader instead).
- Google Gemini SDK (use OpenAI-spec compatible providers only).
- Browser-based E2E tests (Playwright/Selenium deferred).
