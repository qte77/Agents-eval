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

- [ ] The `agent_system.py:526` module has a `NotImplementedError` for streaming with Pydantic model outputs. Please clarify the intended approach for streaming structured data.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
  - Tracked in: PRD-Sprint3.md Out of Scope

## Closed Requests

None. All closed requests purged on 2026-02-17 (Sprint 7 start).
