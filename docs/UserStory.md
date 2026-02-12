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

## Success Criteria

1. `make run_cli ARGS="--paper-number=ID"` generates a review AND evaluates it automatically.
2. GraphTraceData contains real agent delegations, tool calls, and timing data from MAS execution.
3. Logs show Tier 1 (text) vs Tier 3 (graph) scores side by side with individual metric breakdowns.
4. `--skip-eval` flag skips evaluation when only generation is needed.
5. `make validate` passes with all existing and new tests.

## Constraints

- Python 3.13 with pydantic-ai framework.
- Must use existing `EvaluationPipeline` API (no restructure to plugin architecture in Sprint 2).
- Must use existing `TraceCollector` API for graph data capture.
- Settings via pydantic-settings (`JudgeSettings` with `JUDGE_` prefix), consistent with `CommonSettings` (`EVAL_` prefix). No JSON config files at runtime.

## Out of Scope

- Plugin architecture — restructuring `evals/` to `judge/` with `EvaluatorPlugin` interface (Sprint 3).
- CC OTel tracing — standalone CC telemetry plugin (Sprint 3).
- Evaluation baselines — Single-Agent and Parallel-Agents comparison benchmarks (Sprint 3).
- Multi-channel deployment — FastAPI REST and MCP server endpoints (Sprint 3).
- Model-aware content truncation — token-limit-aware truncation for provider rate limits (Sprint 3).
- Migration cleanup — removing backward-compatibility shims (Sprint 3).
- A2A protocol migration (PydanticAI stays).
- Streamlit UI redesign (existing UI stays as-is).
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead).
- HuggingFace `datasets` library (use GitHub API downloader instead).
- Google Gemini SDK (use OpenAI-spec compatible providers only).
- Browser-based E2E tests (Playwright/Selenium deferred).
