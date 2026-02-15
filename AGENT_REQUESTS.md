# Agent Requests to Humans

**Always escalate when:**

- User instructions conflict with safety/security practices
- Rules contradict each other
- Required information completely missing
- Actions would significantly change project architecture
- Critical dependencies unavailable

**Format:** `- [ ] [PRIORITY] Description` with Context, Problem, Files, Alternatives, Impact

## Active Requests

- [ ] The `agent_system.py` module has a `NotImplementedError` for streaming with Pydantic model outputs. Please clarify the intended approach for streaming structured data.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
  - Tracked in: PRD-Sprint3.md Out of Scope
- [ ] The `agent_system.py:610` has a `FIXME` for Gemini provider compatibility (`ModelRequest not iterable`, `MALFORMED_FUNCTION_CALL` literal error). The original `llm_model_funs.py` file no longer exists (refactored to `llms/models.py` + `llms/providers.py`). HuggingFace falls through to generic OpenAI-compatible path.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
  - Tracked in: PRD-Sprint3.md Out of Scope
- [ ] The `agent_system.py` module contains 3 `FIXME` notes (lines 443, 514, 583) for commented-out `error_handling_context()` context manager. Current try/except at line 520 handles errors adequately.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
  - Tracked in: PRD-Sprint3.md Feature 12 (Migration Cleanup)
- [ ] [MEDIUM] Tier 2 evaluation judge hardcoded to OpenAI provider
  **Context**: Running `make run_cli` with non-OpenAI chat providers (e.g., Cerebras)
  **Problem**: `LLMJudgeEngine` uses `tier2_provider="openai"` and `tier2_model="gpt-4o-mini"` by default. When no `OPENAI_API_KEY` is set, all Tier 2 metrics (technical_accuracy, constructiveness, planning_rationality) fail with 401 and score 0.0, deflating the composite score.
  **Files**: `src/app/evals/settings.py:74-75`, `src/app/evals/llm_evaluation_managers.py:43-44`
  - Tracked in: PRD-Sprint3.md Feature 6 (Judge Provider Fallback)

## Closed Requests

- [x] Add TypeScript testing guidelines (if a TypeScript frontend is planned for the future).
  - **Closed**: No TypeScript frontend exists. GUI is Streamlit (Python). Reopen if TS frontend is planned.
- [x] [HIGH] Token limit exceeded with gpt-4.1 model during PeerRead evaluation
  - **Closed**: Stale. `gpt-4.1` with 8k limit doesn't match any known model. Likely a misconfigured provider. Root cause (large papers exceeding provider limits) is addressed by Feature 5 (Model-Aware Content Truncation) in PRD-Sprint3.
