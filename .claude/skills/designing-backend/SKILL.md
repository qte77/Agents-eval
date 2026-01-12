---
name: designing-backend
description: Designs concise, streamlined backend systems matching exact task requirements. Use when planning APIs, data models, system architecture, or when the user requests backend design work.
---

# Backend Architecture

Creates **focused, streamlined** backend system designs matching stated requirements exactly. No over-engineering.

## Core Principles

**MANDATORY**: Always apply @core-principles skill first - User Experience, KISS, DRY, YAGNI, root-cause thinking.

**MANDATORY COMPLIANCE**: Follow @AGENTS.md Agent Neutrality Requirements - extract from specified documents ONLY.

- **Concise output**: Avoid verbose specifications or lengthy explanations
- **Focused architecture**: Match complexity level (simple processing vs complex systems)
- **Streamlined approach**: Existing patterns primary, complex architecture fallback only
- **Design only**: No code implementation
- **Requirement-driven**: Extract from specified documents, don't assume scope

## Workflow

1. **Read backend requirements** from specified documents
2. **Validate scope** - Simple data processing vs Complex system architecture
3. **Design minimal solution** matching stated complexity
4. **Create focused deliverables** - single doc for simple, multiple for complex
5. **Use make recipes** for all commands

## Architecture Strategy

**Simple Processing**: Basic functions, lightweight integration, existing patterns
**Complex Systems**: Multi-tiered pipelines, PydanticAI orchestration, async patterns
**Performance targets**: <1s simple operations, scalable for complex systems

## Output Standards

**Simple Tasks**: Single focused backend specification
**Complex Tasks**: Multiple targeted architecture files
**All outputs**: Concise, streamlined, no unnecessary complexity

## References

- See @AGENTS.md for mandatory compliance requirements
- See @CONTRIBUTING.md for technical patterns
- See @docs/architecture.md for system architecture context
