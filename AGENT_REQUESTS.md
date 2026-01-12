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
