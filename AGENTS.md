# Agent instructions for `Agents-eval` repository

**This file contains behavioral rules, compliance requirements, and decision frameworks specifically for AI coding agents.** For technical development workflows and coding standards (shared by both humans and AI agents), see [CONTRIBUTING.md](CONTRIBUTING.md). For project overview and navigation, see [README.md](README.md).

This file serves as the primary behavioral guideline for AI coding agents, defining mandatory compliance requirements, role boundaries, and quality standards for autonomous development work.

## Table of Contents

### Getting Started

- [Project Structure](#project-structure) - Development environment and project organization
- [Decision Framework for Agents](#decision-framework-for-agents) - Conflict resolution and priorities
- [Core Rules & AI Behavior](#core-rules--ai-behavior) - Fundamental guidelines

### Project Understanding

- [Architecture Overview](#architecture-overview) - System design and data flow
- [Codebase Structure & Modularity](#codebase-structure--modularity) - Organization principles

### AI Agent Behavior & Compliance

- [Agent Neutrality Requirements](#agent-neutrality-requirements) - Requirement-driven design principles
- [Subagent Role Boundaries](#subagent-role-boundaries) - Role separation and coordination
- [Quality Thresholds](#quality-thresholds) - Task readiness assessment

### Development Workflow

- [Testing Strategy](#testing-strategy) - Testing approach for agents
- [Quality Thresholds](#quality-thresholds) - Task readiness assessment

### Utilities & References

- [Agent Quick Reference](#agent-quick-reference) - Critical reminders

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

### Decision Framework

**Priority Order (highest to lowest):**

1. **User instructions** override agent rules (except security conflicts → escalate)
2. **AGENTS.md compliance** overrides project patterns  
3. **Documentation hierarchy** - See [CONTRIBUTING.md](CONTRIBUTING.md#documentation-hierarchy) for complete authority structure
4. **Project patterns** from existing codebase
5. **General best practices** as fallback

**When unclear or conflicted → escalate to AGENT_REQUESTS.md**  

**Agent-Specific Information Source Rules:**

1. **Need requirements or scope validation?** → **PRD.md ONLY** (PRIMARY AUTHORITY)
2. **Need user workflow understanding?** → **UserStory.md ONLY** (AUTHORITY)
3. **Need technical implementation approach?** → **architecture.md ONLY** (AUTHORITY)
4. **Need current implementation status?** → **Sprint documents ONLY** (AUTHORITY)
5. **Need operational procedures?** → **Usage guides ONLY** (AUTHORITY)
6. **Need technology research?** → **Landscape documents** (INFORMATIONAL ONLY)

**Critical Agent Anti-Scope-Creep Rules:**

- **NEVER implement landscape possibilities without PRD.md validation**
- **Landscape documents are research input ONLY, not implementation requirements**
- **Always validate implementation decisions against PRD.md scope boundaries**
- **If landscape docs suggest capabilities beyond PRD.md scope, escalate to AGENT_REQUESTS.md**

**Agent Anti-Redundancy Rules:**

- **NEVER duplicate information across documents** - always reference the authoritative source
- **Before adding information, check if it exists in the authority document**
- **Update the authoritative document, then remove duplicates elsewhere**

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

## Agent Neutrality Requirements

**ALL AI AGENTS MUST MAINTAIN STRICT NEUTRALITY AND REQUIREMENT-DRIVEN DESIGN:**

### Information Source Requirements (MANDATORY)

1. **Extract requirements from specified documents ONLY**
   - Read provided sprint documents, task descriptions, or reference materials
   - Do NOT make assumptions about unstated requirements
   - Do NOT add functionality not explicitly requested
   - Do NOT assume production-level complexity unless specified

2. **Request clarification for ambiguous scope**
   - If task boundaries are unclear, ASK the main agent for clarification
   - If complexity level is not specified, ASK for target complexity
   - If integration points are unclear, ASK for specific requirements
   - Do NOT assume scope or make architectural decisions without validation

3. **Design to stated requirements exactly**
   - Match the complexity level requested (simple vs complex)
   - Stay within specified line count targets when provided
   - Follow "minimal," "streamlined," or "focused" guidance literally
   - Do NOT over-engineer solutions beyond stated needs

### Example Neutral vs Problematic Prompts

**✅ GOOD (Neutral) Prompt:**

```text
"Design composite scoring system per Task 4.1 requirements in docs/sprints/2025-08_Sprint1_ThreeTieredEval.md lines 374-394. 
Target: 100-200 lines total. 
Scope: Simple scoring formula only, no tier integration.
If requirements unclear, request specific clarification."
```

**❌ BAD (Assumption-Heavy) Prompt:**

```text
"Design comprehensive composite scoring system with advanced tier integration, 
complex normalization, extensive error handling, and production-ready architecture."
```

### Scope Validation Checkpoints (MANDATORY)

- **Before design completion**: Validate design stays within specified task scope
- **Before handoff**: Confirm complexity matches stated targets
- **During review**: Check implementation matches original requirements, not assumed needs

## Subagent Role Boundaries

### MANDATORY Compliance Requirements for All Subagents

**ALL SUBAGENTS MUST STRICTLY ADHERE TO THE FOLLOWING:**

1. **Separation of Concerns (MANDATORY)**:
   - **Architects MUST NOT implement code** - only design, plan, and specify requirements
   - **Developers MUST NOT make architectural decisions** - follow architect specifications exactly
   - **Evaluators MUST NOT implement** - only design evaluation frameworks and metrics
   - **Code reviewers MUST focus solely on quality, security, and standards compliance**
   - **NEVER cross role boundaries** without explicit handoff documentation

2. **Command Execution (MANDATORY)**:
   - **ALWAYS use make recipes** - see [CONTRIBUTING.md](CONTRIBUTING.md#unified-command-reference) for complete command reference
   - **Document any deviation** from make commands with explicit reason

3. **Quality Validation (MANDATORY)**:
   - **MUST run `make validate`** before task completion
   - **MUST fix ALL issues** found by validation steps
   - **MUST NOT proceed** with type errors or lint failures

4. **Coding Style Adherence (MANDATORY)**:
   - **MUST follow project patterns** - see [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation) for detailed standards
   - **MUST write concise, focused code** with no unnecessary features

5. **Documentation Updates (MANDATORY)**:
   - **MUST update documentation** - see [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation) for requirements
   - **MUST update AGENTS.md** when learning new patterns

6. **Testing Requirements (MANDATORY)**:
   - **MUST create tests** for new functionality - see [CONTRIBUTING.md](CONTRIBUTING.md#testing-strategy--guidelines) for approach
   - **MUST achieve meaningful validation** with appropriate mocking strategy

7. **Code Standards (MANDATORY)**:
   - **MUST follow existing project patterns** and conventions
   - **MUST use absolute imports** not relative imports
   - **MUST add `# Reason:` comments** for complex logic only when necessary

**FAILURE TO FOLLOW THESE REQUIREMENTS WILL RESULT IN TASK REJECTION**  

### Role-Specific Agent Boundaries

**ARCHITECTS (backend-architect, agent-systems-architect, evaluation-specialist):**

- **SCOPE**: Design, plan, specify requirements, create architecture diagrams
- **DELIVERABLES**: Technical specifications, architecture documents, requirement lists
- **FORBIDDEN**: Writing implementation code, making code changes, running tests
- **HANDOFF**: Must provide focused specifications to developers before any implementation begins

**DEVELOPERS (python-developer, python-performance-expert, frontend-developer):**

- **SCOPE**: Implement code based on architect specifications, optimize performance
- **DELIVERABLES**: Working code, tests, performance improvements
- **FORBIDDEN**: Making architectural decisions, changing system design without architect approval
- **REQUIREMENTS**: Must follow architect specifications exactly, request clarification if specifications are insufficient

**REVIEWERS (code-reviewer):**

- **SCOPE**: Quality assurance, security review, standards compliance, final validation
- **DELIVERABLES**: Code review reports, security findings, compliance verification
- **FORBIDDEN**: Making implementation decisions, writing new features
- **TIMING**: Must be used immediately after any code implementation

### Subagent Prompt Requirements

**DOCUMENT INGESTION ORDER (MANDATORY):**

Subagents must ingest documents in this specific sequence:

1. **AGENTS.md FIRST** - Behavioral rules, compliance requirements, role boundaries
2. **CONTRIBUTING.md SECOND** - Technical workflows, command reference, implementation standards

**ALL SUBAGENT PROMPTS MUST INCLUDE:**

```text
MANDATORY: Read AGENTS.md first for compliance requirements, then CONTRIBUTING.md for technical standards.
All requirements in the "MANDATORY Compliance Requirements for All Subagents" section are non-negotiable.
RESPECT ROLE BOUNDARIES: Stay within your designated role scope. Do not cross into other agents' responsibilities.
```

**Subagents MUST:**

- Reference and follow ALL mandatory compliance requirements above
- Ingest both AGENTS.md (rules) and CONTRIBUTING.md (implementation) in sequence
- Explicitly confirm they will respect role boundaries and separation of concerns
- Use make recipes instead of direct commands
- Validate their work using `make validate` before completion (developers/reviewers only)

## Quality Thresholds

**Before starting any task, ensure:**

- **Context**: 8/10 - Understand requirements, codebase patterns, dependencies
- **Clarity**: 7/10 - Clear implementation path and expected outcomes  
- **Alignment**: 8/10 - Follows project patterns and architectural decisions
- **Success**: 7/10 - Confident in completing task correctly

**Below threshold → gather more context or escalate to AGENT_REQUESTS.md**  

## Testing Strategy

**For comprehensive testing guidelines and BDD approach, see [CONTRIBUTING.md](CONTRIBUTING.md#testing-strategy--guidelines).**

## Agent Quick Reference

**Pre-Task:**

- Read AGENTS.md → CONTRIBUTING.md for technical details
- Confirm role: Architect|Developer|Reviewer
- Verify quality thresholds met (Context: 8/10, Clarity: 7/10, Alignment: 8/10, Success: 7/10)

**During Task:**

- Use make commands (document deviations)
- Follow BDD approach for tests
- Update documentation when learning patterns

**Post-Task:**

- Run `make validate` - must pass all checks
- Update CHANGELOG.md for non-trivial changes
- Document new patterns in AGENT_LEARNINGS.md
- Escalate to AGENT_REQUESTS.md if blocked
