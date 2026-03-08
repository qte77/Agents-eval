---
paths:
  - "src/app/agents/**/*.py"
  - ".claude/agents/*.md"
  - ".claude/skills/**/*.md"
---

# Agent Implementation Rules

- Use PydanticAI agent patterns from agent_system.py
- Follow delegation chain: Manager → Researcher → Analyst → Synthesizer
- Use Pydantic models from data_models/ for all agent I/O
