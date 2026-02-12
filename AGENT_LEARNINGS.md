# Agent Learning Documentation

Non-obvious patterns that prevent repeated mistakes.

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves  
- **Solution**: Implementation approach
- **Example**: Working code
- **References**: Related files

Document when you discover novel solutions or common pitfalls that others might face.

## Learned Patterns

### Learned Pattern: Comprehensive Error Handling and Performance Monitoring

- **Date**: 2025-09-02T14:50:00Z
- **Context**: Evaluation pipeline enhancement for Phase 2 integration
- **Problem**: Basic error handling lacked context, performance bottlenecks were not identified, fallback strategies needed better reporting
- **Solution**: Implemented layered error handling with context-specific guidance, performance analysis with bottleneck detection, and detailed failure tracking with monitoring capabilities
- **Example**:

  ```python
  # Enhanced error handling with context
  except TimeoutError as e:
      execution_time = time.time() - start_time
      error_msg = f"Tier 2 timeout after {timeout}s (LLM-as-Judge evaluation)"
      logger.error(f"{error_msg}. Consider increasing tier2_max_seconds or check LLM service availability.")
      self._record_tier_failure(2, "timeout", execution_time, error_msg)
      return None, execution_time
      
  # Performance bottleneck detection
  bottleneck_threshold = total_time * 0.4
  for tier, time_taken in tier_times.items():
      if time_taken > bottleneck_threshold:
          logger.warning(f"Performance bottleneck detected: {tier} took {time_taken:.2f}s")
  ```

- **Validation**: All 19 pipeline tests pass, enhanced error messages provide actionable guidance, performance metrics collected successfully
- **References**: src/app/evals/evaluation_pipeline.py - comprehensive enhancement of error handling, performance monitoring, and fallback strategies

### Learned Pattern: PlantUML Theming

- **Date**: 2025-08-05T00:00:00Z
- **Context**: PlantUML diagrams in `docs/arch_vis`
- **Problem**: Redundant PlantUML files for light and dark themes.
- **Solution**: Use a variable to define the theme and include the appropriate style file. This allows for a single PlantUML file to be used for multiple themes.
- **Example**:

  ```plantuml
  !ifndef STYLE
  !define STYLE "light"
  !endif
  !include styles/github-$STYLE.puml
  ```

- **Validation**: Generate diagrams with different themes by setting the `STYLE` variable.
- **References**: `docs/arch_vis/`

### Learned Pattern: Module Naming Conflicts Resolution

- **Date**: 2025-07-22T14:30:00Z
- **Context**: PeerRead dataset integration with pyright validation
- **Problem**: Named module `src/app/datasets/` which conflicted with HuggingFace `datasets` library, causing "Source file found twice under different module names" pyright errors
- **Solution**: Rename modules to be specific and avoid common library names. Use descriptive prefixes like `datasets_peerread.py` instead of generic `datasets/`
- **Example**: `src/app/utils/datasets_peerread.py` instead of `src/app/datasets/peerread_loader.py`
- **Validation**: pyright now passes with `Success: no issues found in 16 source files`
- **References**: Added explicit guidance in AGENTS.md Code Organization Rules section

### Learned Pattern: External Dependencies Validation

- **Date**: 2025-07-23T11:00:39Z
- **Context**: PeerRead dataset integration with external API dependencies
- **Problem**: Over-reliance on mocking without validating real external services leads to implementation based on incorrect assumptions about data structure and API endpoints. Did not explicitly test download functionality with real network requests during implementation
- **Solution**: Balance unit test mocking with real integration validation during development. Research existing ecosystem solutions (e.g., HuggingFace datasets) before implementing custom downloaders. Always test critical external functionality explicitly, not just through mocks
- **Example**: Mock for unit tests, but validate real URLs/APIs early: `requests.head(url)` to verify accessibility before full implementation. Test actual download with small samples during development
- **Validation**: Test actual network requests during development, not just after implementation. Explicitly validate download functionality works with real data
- **References**: PeerRead integration - discovered incorrect URL assumptions that mocks didn't catch

### Learned Pattern: Testing Agent Teams with Parallel Code Review

- **Date**: 2026-02-11T23:57:00Z
- **Context**: Testing Claude Code experimental agent teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)
- **Problem**: Need reusable pattern for testing parallel agent orchestration with real trace verification
- **Solution**: Use parallel code review pattern with 3 independent reviewers (security, quality, coverage), shared task list with dependency blocking (3 reviews → 1 aggregation), and trace verification in `~/.claude/teams/` and `~/.claude/tasks/`
- **Example**:
  ```python
  # Team structure
  TeamCreate(team_name="parallel-code-review")

  # Create 3 parallel review tasks + 1 blocked aggregation
  TaskCreate(subject="Security review", ...)  # Task 1
  TaskCreate(subject="Quality review", ...)   # Task 2
  TaskCreate(subject="Coverage review", ...)  # Task 3
  TaskCreate(subject="Aggregate findings", blockedBy=["1","2","3"])  # Task 4

  # Spawn 3 teammates with specific prompts
  Task(subagent_type="general-purpose", team_name="...", name="security-reviewer", ...)
  Task(subagent_type="general-purpose", team_name="...", name="quality-reviewer", ...)
  Task(subagent_type="general-purpose", team_name="...", name="coverage-reviewer", ...)

  # Verify traces
  # ~/.claude/teams/{team-name}/config.json - member roster
  # ~/.claude/teams/{team-name}/inboxes/*.json - messages
  # ~/.claude/tasks/{team-name}/*.json - task status
  ```
- **Validation**: All 3 reviews completed in parallel (~26s total), task dependencies worked (aggregation waited for all 3), full message content preserved in mailboxes, timestamps prove concurrency (quality:23:57:29, coverage:23:57:35, security:23:57:55)
- **Key Finding**: Parallel execution reduces latency (3 sequential reviews ~60s vs parallel ~26s), but token cost scales linearly (3x teammates = 3x Claude instances)
- **References**: `docs/reviews/evaluation-pipeline-parallel-review-2026-02-11.md`, `docs/analysis/CC-agent-teams-orchestration.md`
