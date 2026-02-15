# Agent Learning Documentation

Non-obvious patterns that prevent repeated mistakes.

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **Example**: Working code
- **References**: Related files

## Learned Patterns

### Error Handling and Performance Monitoring

- **Context**: Evaluation pipeline (Phase 2)
- **Problem**: Generic error handling lacked actionable context; no bottleneck detection
- **Solution**: Layered error handling with tier-specific messages and bottleneck detection (>40% of total time)
- **Example**:

  ```python
  except TimeoutError as e:
      error_msg = f"Tier 2 timeout after {timeout}s (LLM-as-Judge evaluation)"
      logger.error(f"{error_msg}. Consider increasing tier2_max_seconds.")
      self._record_tier_failure(2, "timeout", time.time() - start_time, error_msg)

  bottleneck_threshold = total_time * 0.4
  for tier, t in tier_times.items():
      if t > bottleneck_threshold:
          logger.warning(f"Bottleneck: {tier} took {t:.2f}s")
  ```

- **References**: `src/app/evals/evaluation_pipeline.py`

### PlantUML Theming

- **Context**: PlantUML diagrams in `docs/arch_vis`
- **Problem**: Redundant files for light/dark themes
- **Solution**: Single file with theme variable: `!include styles/github-$STYLE.puml`
- **Example**:

  ```plantuml
  !ifndef STYLE
  !define STYLE "light"
  !endif
  !include styles/github-$STYLE.puml
  ```

- **References**: `docs/arch_vis/`

### Module Naming Conflicts

- **Context**: pyright validation with third-party libraries
- **Problem**: `src/app/datasets/` conflicted with HuggingFace `datasets` library — "Source file found twice under different module names"
- **Solution**: Use specific names that don't shadow libraries: `datasets_peerread.py` instead of `datasets/`
- **References**: AGENTS.md Code Organization Rules

### External Dependencies Validation

- **Context**: Integrating external APIs (PeerRead dataset)
- **Problem**: Over-reliance on mocking led to incorrect assumptions about real API endpoints and data structures
- **Solution**: Validate real URLs/APIs early (`requests.head(url)`), mock only after confirming real behavior. Test actual downloads with small samples during development.
- **References**: PeerRead integration — incorrect URL assumptions undetected by mocks

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
  # Spawn 3 teammates → parallel execution (~26s vs ~60s sequential)
  ```

- **Key Finding**: Parallel reduces latency but token cost scales linearly (N teammates = N instances)
- **References**: `docs/reviews/evaluation-pipeline-parallel-review-2026-02-11.md`, `docs/analysis/CC-agent-teams-orchestration.md`

### OpenAI-Compatible Provider Strict Tool Definitions

- **Context**: PydanticAI with OpenAI-compatible providers (Cerebras, Groq, etc.)
- **Problem**: OpenAI `strict: true` on tool definitions enforces model arguments exactly match the JSON schema ([Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)). PydanticAI infers `strict` per-tool based on schema compatibility — mixed values cause HTTP 422 on providers like Cerebras.
- **Solution**: Disable strict inference via `OpenAIModelProfile(openai_supports_strict_tool_definition=False)`. Do NOT force all tools to `strict=True` — risks stripped `default` values and forced `additionalProperties: false`.
- **Example**:

  ```python
  from pydantic_ai.profiles.openai import OpenAIModelProfile

  OpenAIChatModel(
      model_name=model_name,
      provider=OpenAIProvider(base_url=base_url, api_key=api_key),
      profile=OpenAIModelProfile(openai_supports_strict_tool_definition=False),
  )
  ```

- **References**: `src/app/llms/models.py`, [OpenAI Function Calling Guide](https://developers.openai.com/api/docs/guides/function-calling/)

### Pydantic validation_alias for External Data Mapping

- **Context**: Pydantic models receiving external data with different key names (e.g., PeerRead uppercase `IMPACT` → model lowercase `impact`)
- **Problem**: `alias` changes constructor signature — breaks pyright `reportCallIssue` for direct `Model(field=value)` calls. `model_validator(mode="before")` couples model to external format, violates separation of concerns.
- **Solution**: Use `validation_alias` — only affects `model_validate()`, not the constructor. Combine with `ConfigDict(populate_by_name=True)` to accept both alias and field name.
- **Example**:

  ```python
  class PeerReadReview(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      impact: str = Field(
          default="UNKNOWN", validation_alias="IMPACT"
      )
  ```

- **Anti-pattern**: Smuggling context via sentinel keys (e.g., `_paper_id`) in data dicts passed to `model_validate()`. Use Pydantic's `context` parameter instead.
- **References**: `src/app/data_models/peerread_models.py`, `src/app/data_utils/datasets_peerread.py`
