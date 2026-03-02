---
name: designing-mas-plugins
description: Design evaluation plugins following 12-Factor + MAESTRO principles
compatibility: Designed for Claude Code
metadata:
  argument-hint: [component-name]
  allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---

# Designing MAS Plugins

**Target**: $ARGUMENTS

## When to Use

Trigger this skill when:

- Designing agent plugins or evaluation components
- Planning pipeline architecture
- Architecting new metrics or evaluation tiers
- Refactoring engines into plugin patterns

## References

**MUST READ**:
`docs/best-practices/mas-design-principles.md`

## Core Principles

### Stateless Reducer Pattern

Each plugin is a pure function:
`evaluate(context: BaseModel) -> BaseModel`

```python
def evaluate(self, context: TierContext) -> TierResult:
    # Pure function - no side effects, no shared state
    # All inputs from context parameter
    # All outputs in return value
    return TierResult(...)
```

### Own Context Window

Plugin manages its own context - no global state access.

```python
def get_context_for_next_tier(
    self, result: TierResult
) -> NextTierContext:
    # Explicit context passing
    # Next tier only sees what this method returns
    return NextTierContext(
        relevant_data=result.extract_relevant(),
    )
```

### Structured Outputs

All data uses validated models - no raw dicts.

```python
class TierResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    metrics: dict[str, float]
```

### Own Control Flow

Plugin handles its own errors and timeouts.

```python
def evaluate(self, context: TierContext) -> TierResult:
    try:
        result = self._compute(context)
        return TierResult(score=result, error=None)
    except Exception as e:
        # Return structured error, don't raise
        return TierResult(score=0.0, error=str(e))
```

### Compact Errors

Errors produce structured partial results, not exceptions.

### Single Responsibility

One metric or tier per plugin.

## Plugin Design Checklist

Before implementing a plugin, verify:

- [ ] **Stateless**: No class attributes, no global state
- [ ] **Own Context**: All inputs via `evaluate()` parameter
- [ ] **Typed I/O**: Validated models for inputs and outputs
- [ ] **Own Errors**: Returns error results, doesn't raise
- [ ] **Own Timeout**: Respects configured timeout
- [ ] **Single Responsibility**: One metric or tier
- [ ] **Explicit Context**: Filters output for next stage
- [ ] **Env Config**: All config via env vars / settings
- [ ] **Observable**: Emits structured logs for debugging
- [ ] **Graceful Degradation**: Partial results on failures

## Anti-Patterns

- Shared State: `self.cache = {}` (breaks stateless)
- Raw Dicts: `return {"score": 0.5}` (use models)
- Raising Exceptions: `raise ValueError()` (return error)
- Global Access: `config.get_global()` (use settings)
- Implicit Context: Passing entire result to next tier
- Multiple Responsibilities: One plugin, 3 metrics

## Implementation Template

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class PluginContext(BaseModel):
    """Input context from previous tier."""
    data: str
    metadata: dict[str, str]


class PluginResult(BaseModel):
    """Structured output."""
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    error: str | None = None


class EvaluatorPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def tier(self) -> int: ...

    @abstractmethod
    def evaluate(
        self, context: PluginContext
    ) -> PluginResult: ...

    @abstractmethod
    def get_context_for_next_tier(
        self, result: PluginResult
    ) -> BaseModel: ...


class MyPlugin(EvaluatorPlugin):
    def __init__(self, settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "my_evaluator"

    @property
    def tier(self) -> int:
        return 1

    def evaluate(
        self, context: PluginContext
    ) -> PluginResult:
        try:
            score = self._compute(context)
            return PluginResult(
                score=score, reasoning="...",
            )
        except Exception as e:
            return PluginResult(
                score=0.0, reasoning="", error=str(e),
            )

    def get_context_for_next_tier(
        self, result: PluginResult
    ) -> BaseModel:
        return NextTierContext(score=result.score)

    def _compute(self, context: PluginContext) -> float:
        ...
```

## Testing Strategy

Test plugins in isolation with mocked context:

```python
def test_plugin_happy_path():
    plugin = MyPlugin(settings)
    context = PluginContext(data="test", metadata={})
    result = plugin.evaluate(context)
    assert result.score >= 0.0
    assert result.error is None


def test_plugin_error_handling():
    plugin = MyPlugin(settings)
    context = PluginContext(data="bad", metadata={})
    result = plugin.evaluate(context)
    # Structured error, not exception
    assert result.error is not None
```

## Further Reading

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
- [Anthropic Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [PydanticAI Patterns](https://pydantic.dev/articles/building-agentic-application)
