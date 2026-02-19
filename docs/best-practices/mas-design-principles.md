---
title: Multi-Agent System Design Principles
description: >-
  Design principles for building maintainable,
  secure, and scalable multi-agent systems
created: 2026-02-09
category: best-practices
version: 2.0.0
see-also: mas-security.md
---

Synthesized from
[12-Factor Agents](https://github.com/humanlayer/12-factor-agents),
[Anthropic Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents),
and [PydanticAI](https://pydantic.dev/articles/building-agentic-application).

## 12-Factor Agents (Selected)

### #3: Config in Environment

Store configuration in environment variables, not code
or JSON files. Use typed settings classes
(e.g., `BaseSettings`) with env-var prefixes per module.

### #4: Backing Services as Attached Resources

Treat LLM providers, trace stores, and databases as
swappable resources behind interfaces. Plugin/registry
patterns enable runtime discovery without vendor lock-in.

### #8: Stateless Processes

Agent components should be stateless pure functions:
`(context) -> result`. Persist state externally
(database, trace store). Enables horizontal scaling
and deterministic behavior.

### #9: Graceful Degradation

Component errors produce structured partial results,
not crashes. Pipeline continues with degraded output.
Per-component timeouts prevent cascading failures.

### #10: Dev/Prod Parity

Same architecture in all environments. Environment
variables control behavior differences, not code
branches. Local infrastructure (Docker Compose)
mirrors production.

### #12: Logs as Event Streams

Structured logging with JSON output. Traces capture
agent event streams. Queryable audit trails for
debugging and compliance.

## Anthropic Harnesses

### Incremental Boundaries

Break long-running tasks into checkpoints where state
is saved and validated. Each stage produces typed output
consumable by the next. Explicit boundary methods define
what context passes forward.

### Structured State Management

Use typed data structures for all inter-component state.
No raw dicts or untyped strings between stages. Explicit
context arguments, no implicit data passing.

## Framework Patterns

### Typed Outputs

Use validated models for agent outputs, not unstructured
text. Schema enforcement at boundaries catches errors
early and provides self-documenting API contracts.

### Provider Abstraction

Abstract LLM provider details behind a unified interface.
Same agent code works across providers (OpenAI,
Anthropic, Gemini, local). Configurable via environment
variables.

## Agent/Plugin Design Checklist

For security-specific checks, see the
[Security Checklist](mas-security.md#security-checklist).

- [ ] **Stateless Reducer**: Pure function, no shared state
- [ ] **Own Context Window**: Manages own context
- [ ] **Structured Outputs**: Typed validated model
- [ ] **Own Control Flow**: Handles errors and timeouts
- [ ] **Compact Errors**: Structured results, not exceptions
- [ ] **Single Responsibility**: One task per component
- [ ] **Type-Safe Boundaries**: Contracts enforced
- [ ] **Environment Config**: Settings via env vars
- [ ] **Graceful Degradation**: Partial results on failure
- [ ] **Observable**: Structured logs and traces

## References

- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
- [Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [PydanticAI](https://ai.pydantic.dev/)
- [OWASP MAESTRO](https://genai.owasp.org/resource/multi-agentic-system-threat-modeling-guide-v1-0/)
