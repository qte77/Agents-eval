# Agent instructions for `Agents-eval` repository

This file is intended to serve as an entrypoint for AI coding agents, to provide baselines and guardrails concerning this project and as a tool for communication between humans and coding agents. As proposed by [agentsmd.net](https://agentsmd.net/) and used by [wandb weave AGENTS.md](https://github.com/wandb/weave/blob/master/AGENTS.md).

## Table of Contents

### Getting Started

- [Path Variables](#path-variables) - Variable resolution and caching
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

- @CONTRIBUTE.md - Development workflows, coding standards, and collaboration guidelines
- @AGENT_REQUESTS.md - Escalation and human collaboration
- @AGENT_LEARNINGS.md - Pattern discovery and knowledge sharing

## Path Variables

**IMPORTANT**: All `$VARIABLE` path references in this document are defined in `context/config/paths.md`.

### Agent Setup - Read Once, Cache Locally

**Before starting any task**, agents should:

1. Read `context/config/paths.md` ONCE at the beginning of the session
2. Cache all path variables in memory for the entire session
3. Use cached values to resolve `$VARIABLE` references throughout the task

This eliminates the need to repeatedly read `paths.md` for every variable lookup, significantly improving workflow efficiency.

## Core Rules & AI Behavior

- Use the paths and structure defined in $DEFAULT_PATHS_MD (located at context/config/paths.md).
- Aim for Software Development Lifecycle (SDLC) principles like maintainability, modularity, reusability, and adaptability for coding agents and humans alike
- Adhere to a Behavior Driven Development (BDD) approach which focuses on generating concise goal-oriented Minimum Viable Products (MVPs) with minimal yet functional features sets.
  - Keep it simple!
  - The outlined behavior should be described by defining tests first and implementing corresponding code afterwards.
  - Then iteratively improve tests and code until the feature requirements are met.
  - The iterations should be as concise as possible to keep complexity low
  - All code quality and tests have to be passed to advance to the next step
- Always follow the established coding patterns, conventions, and architectural decisions documented here and in the $DOCS_PATH directory.
- **Never assume missing context.** Ask questions if you are uncertain about requirements or implementation details.
- **Never hallucinate libraries or functions.** Only use known, verified Python packages listed in $PROJECT_REQUIREMENTS.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or as part of a documented refactoring task.
- If something doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add it to the **`Requests to Humans`** section below.
- When you learn something new about the codebase or introduce a new concept, **update this file (`AGENTS.md`)** to reflect the new knowledge. This is YOUR FILE! It should grow and evolve with you.

## Decision Framework for Agents

When facing conflicting instructions or ambiguous situations, use this priority hierarchy:

### Priority Hierarchy

1. **Explicit user instructions** - Always override all other guidelines
2. **AGENTS.md rules** - Override general best practices when specified
3. **paths.md structure** - Source of truth for all path references
4. **Project-specific patterns** - Found in existing codebase
5. **General best practices** - Default fallback for unspecified cases

### Common Conflict Resolution

#### Path Conflicts

- **Always use paths.md** as the definitive source
- If paths.md conflicts with other files, update the other files
- Never hardcode paths that exist as variables

#### Command Execution Conflicts

- **Prefer make commands** when available (e.g., `make ruff` over direct `uv run ruff`)
- If make commands fail, try direct commands as fallback
- Always document when deviating from standard commands

#### Documentation Update Conflicts

- Update **both AGENTS.md and related files** to maintain consistency
- When learning something new, add it to the appropriate section
- Prefer specific examples over vague instructions

### Decision Examples

#### Example 1: Missing Library

**Situation:** Code references library not in `pyproject.toml`

**Decision Process:**

1. User instruction? *(None given)*
2. AGENTS.md rule? *"Never hallucinate libraries"* ✅
3. **Action:** Ask user to confirm library or find alternative

#### Example 2: Test Framework Unclear

**Situation:** Need to write tests but framework not specified

**Decision Process:**

1. User instruction? *(None given)*
2. AGENTS.md rule? *"Always create Pytest unit tests"* ✅  
3. **Action:** Use pytest as specified

#### Example 3: Code Organization

**Situation:** File approaching 500 lines

**Decision Process:**

1. User instruction? *(None given)*
2. AGENTS.md rule? *"Never create files longer than 500 lines"* ✅
3. **Action:** Refactor into smaller modules

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

This is a Multi-Agent System (MAS) evaluation framework for assessing agentic AI systems. The project uses **PydanticAI** as the core framework for agent orchestration and is designed for evaluation purposes, not for production agent deployment.

### Data Flow

1. User input → Manager Agent (can be single-LLM)
2. Optional: Manager delegates to Researcher Agent (with DuckDuckGo search)
3. Optional: Researcher results → Analyst Agent for validation
4. Optional: Validated data → Synthesizer Agent for report generation
5. Results evaluated using configurable metrics

### Key Dependencies

- **PydanticAI**: Agent framework and orchestration
- **uv**: Fast Python dependency management
- **Streamlit**: GUI framework
- **Ruff**: Code formatting and linting
- **pyright**: Static type checking

## Codebase Structure & Modularity

### Main Components

See the "Important files" sections in $DEFAULT_PATHS_MD for key application entry points and core modules.

### Code Organization Rules

- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into smaller, more focused modules or helper files.
- Organize code into clearly separated modules grouped by feature.
- Use clear, consistent, and absolute imports within packages.
- **Never name modules/packages after existing Python libraries.** This creates import conflicts and pyright resolution issues.
  - ❌ `src/app/datasets/` (conflicts with HuggingFace `datasets` library)
  - ❌ `src/app/requests/` (conflicts with `requests` library)
  - ❌ `src/app/typing/` (conflicts with built-in `typing` module)
  - ✅ `src/app/utils/datasets_peerread.py` (specific, descriptive naming)
  - ✅ `src/app/api_client/` (instead of `requests`)
  - ✅ `src/app/datamodels/` (instead of `typing`)

## Quality Evaluation Framework

Use this universal framework to assess task readiness before implementation:

**Rate task readiness (1-10 scale):**

- **Context Completeness**: All required information and patterns gathered from codebase, documentation, and requirements
- **Implementation Clarity**: Clear understanding and actionable implementation path of what needs to be built and how to build it.
- **Requirements Alignment**: Solution follows feature requirements, project patterns, conventions, and architectural decisions
- **Success Probability**: Confidence level for completing the task successfully in one pass

**Minimum thresholds for proceeding:**

- Context Completeness: 8/10 or higher
- Implementation Clarity: 7/10 or higher  
- Requirements Alignment: 8/10 or higher
- Success Probability: 7/10 or higher

**If any score is below threshold:** Stop and gather more context, clarify requirements, or escalate to humans using the [Decision Framework](#decision-framework-for-agents).

## Testing Strategy

**For comprehensive testing guidelines, see [CONTRIBUTE.md](CONTRIBUTE.md#testing-strategy--guidelines).**

**Agent-specific reminders:**

- Follow BDD approach: write tests first, then implement
- Balance mocking with real integration validation during development
- Document real test results in implementation logs

## Agent Quick Reference - Critical Reminders

**Before ANY task, verify:**

- All `$VARIABLE` paths resolve via `$DEFAULT_PATHS_MD`
- Libraries exist in `$PROJECT_REQUIREMENTS`
- No missing context assumptions

**Documentation tasks:**

- Apply [markdownlint rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- Use ISO 8601 timestamps (`YYYY-mm-DDTHH:MM:SSZ`)
- Consistent `$VARIABLE` syntax

**Code tasks:**

- Max 500 lines/file
- Create tests in `$TEST_PATH`
- Google-style docstrings
- Verify imports exist

**Always finish with:**

- Follow [pre-commit checklist](CONTRIBUTE.md#pre-commit-checklist)
- Update AGENTS.md if learned something new

**🛑 STOP if blocked:** Add to [AGENT_REQUESTS.md](AGENT_REQUESTS.md) rather than assume or proceed with incomplete info

**📚 LEARNED SOMETHING NEW:** Document patterns in [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md) to help future agents
