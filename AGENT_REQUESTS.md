---
title: Agent Requests to Humans
description: Escalation protocol and active requests requiring human decision
version: 1.0.0
created: 2025-08-19
updated: 2026-02-16
---

**Always escalate when:**

- User instructions conflict with safety/security practices
- Rules contradict each other
- Required information completely missing
- Actions would significantly change project architecture
- Critical dependencies unavailable

**Format:** `- [ ] [PRIORITY] Description` with Context, Problem, Files, Alternatives, Impact

## Active Requests

None.

## Closed Requests

- [x] The `agent_system.py:526` module had a `NotImplementedError` for streaming with Pydantic model outputs.
  - Closed in STORY-004 (Sprint 8): PydanticAI `run_stream()` still does not support structured `BaseModel` output_type. Dead code path removed. Parameter `pydantic_ai_stream` deleted from `run_manager()`, `run_manager_orchestrated()`, `_run_agent_execution()`, and `main()`.
  - Closed: 2026-02-18
