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

### Review-to-PRD Traceability

- **Context**: Planning a sprint after a security review or code audit produced findings tagged for future sprints
- **Problem**: Review findings fall through the cracks between sprints. The Sprint 5 MAESTRO review tagged 14 findings as "Sprint 6" or "Sprint 7+" but the initial Sprint 6 PRD had zero of them.
- **Solution**: After any review/audit sprint, the next PRD must account for every finding: feature, Out of Scope with sprint attribution, or explicitly dismissed with rationale. Checklist: for each review finding, grep the PRD for its ID or description.
- **Anti-pattern**: Assuming review findings will be remembered. They won't.
- **References**: Sprint 5 `docs/reviews/sprint5-code-review.md` → Sprint 6 Features 10-13 + Out of Scope

### Coverage Before Audit Ordering

- **Context**: Sprint includes both adding test coverage and deleting low-value tests
- **Problem**: Deleting implementation-detail tests first creates a coverage gap. A module at 27% loses tests before behavioral replacements exist.
- **Solution**: Order coverage improvements before test pruning. Express as `depends:` in story breakdown. Prove behavioral coverage exists, then safely prune.
- **Anti-pattern**: "Clean up first, then build" — creates a coverage valley between deletion and addition.
- **References**: Sprint 6 Features 14-15 (STORY-015 depends on STORY-014)

### CVE Version Check Before PRD Story

- **Context**: Writing a CVE remediation story from a security review finding
- **Problem**: Review says "upgrade scikit-learn to >=1.5.0 for CVE-2024-5206." Author writes the story without checking `pyproject.toml`. Turns out `scikit-learn>=1.8.0` already pinned — CVE already mitigated. Wasted story.
- **Solution**: Before writing any CVE story, check current dependency version. If patched, note in PRD description ("already mitigated by...") and skip.
- **References**: Sprint 6 Feature 10 (scikit-learn CVE dismissed after version check)

### SSRF Allowlist Must Match Actual HTTP Call Sites

- **Context**: SSRF URL validation with domain allowlisting
- **Problem**: Allowlist built from *conceptual* dependencies (which services we use) rather than *actual* `validate_url()` call sites. Result: `api.github.com` missing (used but rejected), 3 LLM provider domains present (listed but never checked — PydanticAI uses its own HTTP clients).
- **Solution**: Grep for `validate_url(` calls, trace each URL back to its domain. Only list domains that actually pass through the validation function.
- **Anti-pattern**: Listing domains based on "what services does the project talk to" instead of "what domains flow through this specific validation gate."
- **References**: `src/app/utils/url_validation.py`, `src/app/data_utils/datasets_peerread.py:300`

### Test Filesystem Isolation (tmp_path)

- **Context**: Tests that mock network calls but call real write paths (e.g., `_save_file_data`, `_download_single_data_type`)
- **Problem**: Mocking `download_file` prevents network access but unmocked methods still write to real project directories (e.g., `datasets/peerread/`). Mock data pollutes the source tree and breaks subsequent app runs.
- **Solution**: Always redirect `cache_dir` or any write-target path to `tmp_path` in tests that trigger file writes, even when the download itself is mocked.
- **Example**: `downloader.cache_dir = tmp_path / "cache"` before calling `download_venue_split()`
- **Anti-pattern**: Only mocking the network layer and assuming no disk side-effects. If the code has `mkdir` + `open()` + `write()`, those still execute against real paths.
- **References**: `tests/data_utils/test_datasets_peerread.py:601`, `src/app/data_utils/datasets_peerread.py:468`

### CC Teams Artifacts Ephemeral in Print Mode

- **Context**: Running `claude -p` (headless/print mode) for CC baseline collection
- **Problem**: `~/.claude/teams/` and `~/.claude/tasks/` are empty after `claude -p` completes. `CCTraceAdapter` teams parser finds no artifacts to parse.
- **Solution**: Teams artifacts are ephemeral in print mode — they exist only during execution. For teams trace data, parse `raw_stream.jsonl` for `TeamCreate`, `Task`, `TodoWrite` events instead of relying on filesystem artifacts.
- **Anti-pattern**: Assuming `~/.claude/teams/` persists after headless invocation. It doesn't — only interactive sessions leave persistent team state.
- **References**: `scripts/collect-cc-traces/run-cc.sh`, ADR-008

### Makefile $(or) Does Not Override ?= Defaults

- **Context**: Makefile variable defaults with `?=` and `$(or $(VAR),fallback)` pattern
- **Problem**: `CC_MODEL ?= sonnet` sets `CC_MODEL` to `"sonnet"` at parse time. `$(or $(CC_MODEL),fallback)` always sees `CC_MODEL` as truthy (non-empty), so the fallback never triggers — even when the user hasn't explicitly set the variable.
- **Solution**: Use separate variables for user-facing defaults and internal fallbacks. Or use `ifdef`/`ifndef` guards instead of `$(or)` when the variable has a `?=` default.
- **Example**: Instead of `TIMEOUT := $(or $(CC_TEAMS_TIMEOUT),600)`, use `CC_TEAMS_TIMEOUT ?= 600` directly — the `?=` already provides the default.
- **References**: `Makefile` (cc_run_solo, cc_run_teams recipes)
