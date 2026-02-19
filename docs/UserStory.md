# User Story: Agents-eval

## Problem Statement

The multi-agent system (MAS) generates scientific paper reviews via agent delegation (Manager → Researcher → Analyst → Synthesizer), but the execution graph is never captured or evaluated. There is no way to compare graph-based coordination metrics (how agents coordinate) against conventional text similarity metrics (what agents produce). Generation and evaluation are disconnected.

## Target Users

AI researchers evaluating multi-agent system coordination quality using the PeerRead dataset.

## Value Proposition

Understand whether graph-based analysis (how agents coordinate) provides different insights than text similarity (what agents produce) for the same review generation task. Enable automated evaluation immediately after generation so researchers can iterate on agent configurations with rapid feedback.

## User Stories

- As a researcher, I want evaluation to run automatically after review generation so I don't have to wire it manually.
- As a researcher, I want real agent execution traces captured so graph analysis uses actual data instead of synthetic traces.
- As a researcher, I want to see graph metrics alongside text metrics so I can compare evaluation approaches.
- As a researcher, I want to skip evaluation with `--skip-eval` when I only need generation.
- As a researcher, I want evaluation settings configurable via environment variables so I can tune tier weights, timeouts, and model selection without editing code.
- As a researcher, I want local tracing without Docker containers so I can inspect agent traces without complex infrastructure setup.
- As a researcher, I want a Streamlit dashboard showing Tier 1/2/3 evaluation scores so I can visually compare graph-based and text-based metrics without parsing log output.
- As a researcher, I want an interactive agent graph visualization so I can see how agents delegated tasks and coordinated during review generation.
- As a researcher, I want to compare MAS evaluation results against Claude Code baselines so I can quantify coordination quality differences between orchestration approaches.
- As a researcher, I want to run the evaluation pipeline across all agent composition variations so I can identify which agent combination produces the best review quality compared to graph quality.
- As a researcher, I want to generate evaluation reports with actionable improvement suggestions so I can systematically identify weaknesses in review quality without manually interpreting raw metric scores.

## Success Criteria

1. `make run_cli ARGS="--paper-id=ID"` generates a review AND evaluates it automatically.
2. Execution traces contain real agent delegations, tool calls, and timing data.
3. Logs show Tier 1 (text) vs Tier 3 (graph) scores side by side with metric breakdowns.
4. `--skip-eval` flag skips evaluation when only generation is needed.
5. `make validate` passes with all existing and new tests.
6. Local trace viewer shows agent execution traces without Docker setup.
7. Streamlit "Evaluation Results" page displays tier scores and comparison charts.
8. Streamlit "Agent Graph" page renders the delegation graph interactively.
9. `--generate-report` produces a Markdown report with per-tier breakdown and actionable suggestions grounded in evaluation data.

## Constraints

- Python 3.13 with PydanticAI framework.
- Plugin-based evaluation architecture (see [architecture.md](architecture.md) for technical details).
- Zero-Docker local tracing (Logfire + Arize Phoenix).
- Streamlit for evaluation dashboards, Phoenix for trace inspection (complementary, separate services).

For implementation details, see [architecture.md](architecture.md). For sprint status, see [roadmap.md](roadmap.md).

## Out of Scope

- ~~Plugin architecture — restructuring `evals/` to `judge/` with `EvaluatorPlugin` interface.~~ (delivered Sprint 3)
- ~~Claude Code OTel tracing — standalone Claude Code telemetry plugin.~~ (delivered Sprint 3)
- ~~Evaluation baselines — Claude Code solo and teams comparison.~~ (delivered Sprint 4)
- Multi-channel deployment — FastAPI REST and MCP server endpoints.
- Model-aware content truncation — token-limit-aware truncation for provider rate limits.
- Migration cleanup — removing backward-compatibility shims.
- A2A protocol migration (PydanticAI stays).
- Streamlit full redesign or new pages (incremental enhancements to existing pages are in scope).
- pytest-bdd / Gherkin scenarios (use pytest + hypothesis instead).
- HuggingFace `datasets` library (use GitHub API downloader instead).
- Google Gemini SDK (use OpenAI-spec compatible providers only).
- Browser-based E2E tests (Playwright/Selenium deferred).
