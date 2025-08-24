# Agent instructions for `Agents-eval` repository

**This file is intended for AI coding agents.** For shared development workflows and standards (valid for both agents and humans), see [CONTRIBUTING.md](CONTRIBUTING.md). For project overview aimed towards humans, see [README.md](README.md).

This file serves as an entrypoint for AI coding agents, providing baselines and guardrails concerning this project and facilitating communication between humans and coding agents. As proposed by [agentsmd.net](https://agentsmd.net/) and used by [wandb weave AGENTS.md](https://github.com/wandb/weave/blob/master/AGENTS.md).

## Table of Contents

### Getting Started

- [Project Structure](#project-structure) - Development environment and project organization
- [Decision Framework for Agents](#decision-framework-for-agents) - Conflict resolution and priorities
- [Core Rules & AI Behavior](#core-rules--ai-behavior) - Fundamental guidelines

### Project Understanding

- [Architecture Overview](#architecture-overview) - System design and data flow
- [Codebase Structure & Modularity](#codebase-structure--modularity) - Organization principles

### Development Workflow

- [Quality Evaluation Framework](#quality-evaluation-framework) - Task readiness assessment
- [Testing Strategy](#testing-strategy) - Testing approach for agents

### Utilities & References

- [Agent Quick Reference](#agent-quick-reference---critical-reminders) - Critical reminders

### External References

- @CONTRIBUTING.md - Command reference, pre-commit checklist, testing guidelines, code style patterns, and human collaboration workflows
- @AGENT_REQUESTS.md - Escalation and human collaboration
- @AGENT_LEARNINGS.md - Pattern discovery and knowledge sharing

## Project Structure

**For development environment setup and project structure guidance, see [CONTRIBUTING.md](CONTRIBUTING.md).**

## Core Rules & AI Behavior

- Follow established project structure and organization patterns.
- Aim for Software Development Lifecycle (SDLC) principles like maintainability, modularity, reusability, and adaptability for coding agents and humans alike
- Follow Behavior Driven Development (BDD) approach for feature development (see [CONTRIBUTING.md](CONTRIBUTING.md#agent-specific-testing-guidelines) for detailed methodology)
- Always follow established coding patterns, conventions, and architectural decisions (see [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation) for detailed standards).
- **Never assume missing context.** Ask questions if you are uncertain about requirements or implementation details.
- **Never hallucinate libraries or functions.** Only use known, verified Python packages listed in `pyproject.toml`. When introducing new packages, verify they exist on [PyPI](https://pypi.org) first.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or as part of a documented refactoring task.
- If something doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add it to the **`Requests to Humans`** section below.
- When you learn something new about the codebase or introduce a new concept, **update this file (`AGENTS.md`)** to reflect the new knowledge. This is YOUR FILE! It should grow and evolve with you.

## Decision Framework for Agents

When facing conflicting instructions or ambiguous situations, use this priority hierarchy:

### Priority Hierarchy

1. **Explicit user instructions** - Always override all other guidelines
2. **AGENTS.md rules** - Override general best practices when specified
3. **Project structure** - Follow established file organization patterns
4. **Project-specific patterns** - Found in existing codebase
5. **General best practices** - Default fallback for unspecified cases

**For detailed conflict resolution procedures, command preferences, and decision examples, see [CONTRIBUTING.md](CONTRIBUTING.md#decision-framework-implementation).**

### When to Stop and Ask

**Always stop and ask for clarification when:**

- Explicit user instructions conflict with safety/security practices
- Multiple AGENTS.md rules contradict each other  
- Required information is completely missing from all sources
- Actions would significantly change project architecture

**Don't stop to ask when:**

- Clear hierarchy exists to resolve the conflict
- Standard patterns can be followed safely
- Minor implementation details need decisions

## Architecture Overview

This is a Multi-Agent System (MAS) evaluation framework using **PydanticAI** for agent orchestration. For detailed architecture and component descriptions, see [README.md](README.md).

## Codebase Structure & Modularity

### Main Components

See the project structure in the repository root directory for key application entry points and core modules.

### Code Organization Principles

- **Maintain modularity**: Keep files focused and manageable in size
- **Follow established patterns**: Use consistent project structure and naming conventions
- **Avoid conflicts**: Choose module names that don't conflict with existing libraries
- **Use clear organization**: Group related functionality and use descriptive naming

**For detailed coding standards, file organization rules, and specific examples, see [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation).**

## Quality Evaluation Framework

**For detailed task readiness assessment criteria, scoring scales, and implementation procedures, see [CONTRIBUTING.md](CONTRIBUTING.md#quality-evaluation-implementation).**

## Testing Strategy

**For comprehensive testing guidelines and BDD approach, see [CONTRIBUTING.md](CONTRIBUTING.md#testing-strategy--guidelines).**

## Agent Quick Reference - Critical Reminders

**Before ANY task, verify:**

- Project structure and file locations are understood
- Libraries exist in `pyproject.toml`
- No missing context assumptions

**For all development tasks:**

- Follow project coding standards, testing strategy, and quality guidelines (see [CONTRIBUTING.md](CONTRIBUTING.md))
- Apply quality evaluation framework before implementation

**Always finish with:**

- Complete validation and commit processes (see [CONTRIBUTING.md](CONTRIBUTING.md#pre-commit-checklist))
- Update AGENTS.md if learned something new

**🛑 Do not use emojis or icons in code:** Do not use emojis or icons in code, documentation, or files unless explicitly requested by users.

**🛑 STOP if blocked:** Add to [AGENT_REQUESTS.md](AGENT_REQUESTS.md) rather than assume or proceed with incomplete info

**📚 LEARNED SOMETHING NEW:** Document patterns in [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md) to help future agents
