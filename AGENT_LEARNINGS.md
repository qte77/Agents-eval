---
title: Agent Learning Documentation
description: Non-obvious patterns that prevent repeated mistakes across sprints
version: 1.0.0
created: 2025-08-19
updated: 2026-02-16
---

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **Example**: Working code
- **References**: Related files

## Learned Patterns

### Error Handling and Performance Monitoring

- **Context**: Evaluation pipeline
- **Problem**: Generic errors lacked context; no bottleneck detection
- **Solution**: Tier-specific error messages + bottleneck warnings when >40% of total time
- **Example**: `if tier_time > total_time * 0.4: logger.warning(f"Bottleneck: {tier}")`
- **References**: `src/app/evals/evaluation_pipeline.py`

### PlantUML Theming

- **Context**: PlantUML diagrams in `docs/arch_vis`
- **Problem**: Redundant files for light/dark themes
- **Solution**: Single file with theme variable: `!ifndef STYLE !define STYLE "light" !endif` then `!include styles/github-$STYLE.puml`
- **References**: `docs/arch_vis/`

### Module Naming Conflicts

- **Context**: pyright validation with third-party libraries
- **Problem**: `src/app/datasets/` shadowed HuggingFace `datasets` library
- **Solution**: Use specific names: `datasets_peerread.py` not `datasets/`
- **References**: AGENTS.md Code Organization Rules

### External Dependencies Validation

- **Context**: Integrating external APIs (PeerRead dataset)
- **Problem**: Mocking without validation led to incorrect API assumptions
- **Solution**: Validate real APIs first (`requests.head(url)`), then mock. Test with small samples.
- **References**: PeerRead integration — wrong URLs undetected by mocks

### Agent Teams Parallel Orchestration

- **Context**: Claude Code agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)
- **Problem**: Need reusable pattern for parallel agent orchestration
- **Solution**: Independent reviewers with shared task list + dependency-blocked aggregation task. Traces in `~/.claude/teams/` and `~/.claude/tasks/`.
- **Example**:

  ```python
  TaskCreate(subject="Security review", ...)   # Task 1
  TaskCreate(subject="Quality review", ...)    # Task 2
  TaskCreate(subject="Coverage review", ...)   # Task 3
  TaskCreate(subject="Aggregate", blockedBy=["1","2","3"])  # Task 4
  ```

- **Key Finding**: Parallel reduces latency but token cost scales linearly (N teammates = N instances)
- **References**: `docs/reviews/evaluation-pipeline-parallel-review-2026-02-11.md`, `docs/analysis/CC-agent-teams-orchestration.md`

### OpenAI-Compatible Provider Strict Tool Definitions

- **Context**: PydanticAI with OpenAI-compatible providers (Cerebras, Groq)
- **Problem**: PydanticAI's per-tool `strict` inference causes HTTP 422 with mixed values
- **Solution**: Disable via `OpenAIModelProfile(openai_supports_strict_tool_definition=False)`. Don't force `strict=True` — breaks defaults.
- **Example**: `OpenAIChatModel(provider=..., profile=OpenAIModelProfile(openai_supports_strict_tool_definition=False))`
- **References**: `src/app/llms/models.py`, [OpenAI Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)

### Pydantic validation_alias for External Data Mapping

- **Context**: Pydantic models with different external key names (PeerRead `IMPACT` → `impact`)
- **Problem**: `alias` breaks constructor signature; `model_validator(mode="before")` couples to external format
- **Solution**: Use `validation_alias` (only affects `model_validate()`) + `ConfigDict(populate_by_name=True)`
- **Example**: `impact: str = Field(default="UNKNOWN", validation_alias="IMPACT")`
- **Anti-pattern**: Sentinel keys in data dicts (e.g., `_paper_id`). Use Pydantic's `context` parameter.
- **References**: `src/app/data_models/peerread_models.py`, `src/app/data_utils/datasets_peerread.py`

### Measurable Acceptance Criteria for Meta-Tasks

- **Context**: PRD meta-tasks (reviews, audits, assessments)
- **Problem**: "Review completed" not verifiable
- **Solution**: Three gates: (1) Coverage - every scope item has findings or explicit "no issues", (2) Severity - zero critical unfixed; high findings fixed or tracked, (3) Artifact - document exists with required structure. No minimum finding counts to avoid padding.
- **Anti-pattern**: Minimum finding counts incentivize noise
- **References**: Sprint 5 Features 10-11, `docs/reviews/sprint5-code-review.md`

### Streamlit Background Execution Strategy

- **Context**: Long tasks (LLM calls, pipelines) without blocking UI
- **Problem**: Tab navigation aborts execution; `threading.Thread` session state writes not thread-safe
- **Solution**: Prefer `st.fragment` (1.33+) for isolated re-runs. Fall back to `threading.Thread` + synchronized writes when execution must survive full re-renders.
- **Decision rule**: `st.fragment` for single component; `threading.Thread` + callback for page-level survival
- **References**: `src/gui/pages/run_app.py`, Streamlit docs

### PRD Files List Completeness Check

- **Context**: Writing sprint PRD features with acceptance criteria, technical requirements, and files lists
- **Problem**: Files referenced in acceptance criteria or technical requirements but missing from Files list. Implementers working from Files list miss changes.
- **Solution**: After writing each feature, verify every file referenced in AC and tech requirements appears in Files with correct annotation (new/edit/delete).
- **References**: Sprint 6 Features 2, 7 (caught in post-task review)

### Claude Code Headless Invocation for Benchmarking

- **Context**: Running CC from Python for MAS vs CC baseline comparison
- **Problem**: Sprint 3 `cc_otel` used wrong abstraction — CC tracing is infrastructure (env vars), not application code
- **Solution**: `claude -p "prompt" --output-format json` via `subprocess.run()`. Check with `shutil.which("claude")`. Collect artifacts from `~/.claude/teams/` + `~/.claude/tasks/`, parse via `CCTraceAdapter`.
- **References**: `docs/analysis/CC-agent-teams-orchestration.md`, Sprint 6 Feature 7
