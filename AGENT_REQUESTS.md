# Agent Requests to Humans

This document contains questions, clarifications, and tasks that AI agents need humans to complete or elaborate on. This serves as the primary escalation and communication channel between agents and human collaborators.

## Escalation Process

### When to Escalate

**Always escalate when:**

- Explicit user instructions conflict with safety/security practices
- Rules in AGENTS.md or otherwise provided context contradict each other
- Required information completely missing from all sources
- Actions would significantly change project architecture
- Critical dependencies or libraries are unavailable

### How to Escalate

1. **Add to list below** using checkbox format with clear description
2. **Set priority**: `[HIGH]`, `[MEDIUM]`, `[LOW]` based on blocking impact
3. **Provide context**: Include relevant file paths, error messages, or requirements
4. **Suggest alternatives**: What could be done instead, if anything

### Response Format

- Human responses should be added as indented bullet points under each item
- Use `# TODO` for non-urgent items with reminder frequency
- Mark completed items with `[x]` checkbox

## Active Requests

- [ ] The `agent_system.py` module has a `NotImplementedError` for streaming with Pydantic model outputs. Please clarify the intended approach for streaming structured data.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
- [ ] The `llm_model_funs.py` module has `NotImplementedError` for the Gemini and HuggingFace providers. Please provide the correct implementation or remove them if they are not supported.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
- [ ] The `agent_system.py` module contains a `FIXME` note regarding the use of a try-catch context manager. Please review and implement the intended error handling.
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
- [ ] Add TypeScript testing guidelines (if a TypeScript frontend is planned for the future).
  - Human: `# TODO` but not of priority as of now. Remind me once a week.
- [ ] [HIGH] Token limit exceeded with gpt-4.1 model during PeerRead evaluation
  **Context**: Running evaluation pipeline with PeerRead dataset papers
  **Problem**: gpt-4.1 model has 8000 token limit, but papers exceed this limit
  **Error**: `status_code: 413, model_name: gpt-4.1, body: {'code': 'tokens_limit_reached', 'message': 'Request body too large for gpt-4.1 model. Max size: 8000 tokens.'}`
  **Files**: Evaluation pipeline or agent system where model is called
  **Alternatives**: 
    - Switch to higher-capacity model (gpt-4-turbo: 128k tokens, claude-3-sonnet: 200k tokens)
    - Implement document chunking strategy for large papers
    - Use smaller papers for testing (find smallest with shell command)
  **Impact**: Blocks evaluation pipeline for papers exceeding 8k tokens

## Guidelines for Agents

### What to Include in Requests

- **Specific file paths** and line numbers when applicable
- **Error messages** or diagnostic output
- **Context** about what you were trying to accomplish
- **Alternative approaches** you considered
- **Impact assessment** - what's blocked by this issue

### What NOT to Escalate

- Minor implementation details that can be resolved with existing patterns
- Questions answered by existing documentation
- Standard coding decisions covered by AGENTS.md or CONTRIBUTE.md
- Issues that can be resolved through the Decision Framework

### Request Template

```markdown
- [ ] [PRIORITY] Brief description of the issue
  **Context**: What were you trying to do?
  **Problem**: What specific issue or conflict occurred?
  **Files**: Relevant file paths and line numbers
  **Alternatives**: What other approaches could work?
  **Impact**: What functionality is blocked?
```

## Completed Requests Archive

When requests are completed, move them here with resolution details:

### Resolved Items

<!-- Example:
- [x] [MEDIUM] Clarify testing framework choice
  - **Resolution**: Use pytest as specified in AGENTS.md
  - **Date**: 2025-01-15
  - **Impact**: Unblocked test development for all new features
-->

*No completed requests yet.*
