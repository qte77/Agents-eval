# Agent Instructions for Agents-eval

**Behavioral rules, compliance requirements, and decision frameworks for AI coding
agents.** For technical workflows and coding standards, see
[CONTRIBUTING.md](CONTRIBUTING.md). For project overview, see
[README.md](README.md).

**External References:**

- @CONTRIBUTING.md - Command reference, testing guidelines, code style patterns
- @AGENT_REQUESTS.md - Escalation and human collaboration  
- @AGENT_LEARNINGS.md - Pattern discovery and knowledge sharing

## Core Rules & AI Behavior

- Follow SDLC principles: maintainability, modularity, reusability, adaptability
- Use BDD approach for feature development
- **Never assume missing context** - Ask questions if uncertain about requirements
- **Never hallucinate libraries** - Only use packages verified in `pyproject.toml`
- **Always confirm file paths exist** before referencing in code or tests
- **Never delete existing code** unless explicitly instructed or documented refactoring
- **Document new patterns** in AGENT_LEARNINGS.md (concise, laser-focused, streamlined)
- **Request human feedback** in AGENT_REQUESTS.md (concise, laser-focused, streamlined)

## Decision Framework

**Priority Order:** User instructions → AGENTS.md compliance → Documentation
hierarchy → Project patterns → General best practices

**Information Source Rules:**

- **Requirements/scope:** PRD.md ONLY (PRIMARY AUTHORITY)
- **User workflows:** UserStory.md ONLY (AUTHORITY)  
- **Technical implementation:** architecture.md ONLY (AUTHORITY)
- **Current status:** Sprint documents ONLY (AUTHORITY)
- **Operations:** Usage guides ONLY (AUTHORITY)
- **Research:** Landscape documents (INFORMATIONAL ONLY)

**Anti-Scope-Creep Rules:**

- **NEVER implement landscape possibilities without PRD.md validation**
- **Landscape documents are research input ONLY, not implementation requirements**
- **Always validate implementation decisions against PRD.md scope boundaries**

**Anti-Redundancy Rules:**

- **NEVER duplicate information across documents** - reference authoritative sources
- **Update authoritative document, then remove duplicates elsewhere**

**When to Escalate to AGENT_REQUESTS.md:**

- User instructions conflict with safety/security practices
- AGENTS.md rules contradict each other
- Required information completely missing
- Actions would significantly change project architecture

## Architecture Overview

Multi-Agent System (MAS) evaluation framework using **PydanticAI** for agent
orchestration. For detailed architecture, see
[architecture.md](docs/architecture.md).

**Code Organization Principles:**

- Maintain modularity: Keep files focused and manageable
- Follow established patterns: Use consistent structure and naming
- Avoid conflicts: Choose module names that don't conflict with existing libraries
- Use clear organization: Group related functionality with descriptive naming

## AI Agent Behavior & Compliance

## Agent Neutrality Requirements

**ALL AI AGENTS MUST MAINTAIN STRICT NEUTRALITY AND REQUIREMENT-DRIVEN DESIGN:**

1. **Extract requirements from specified documents ONLY**
   - Read provided sprint documents, task descriptions, or reference materials
   - Do NOT make assumptions about unstated requirements
   - Do NOT add functionality not explicitly requested
   - Do NOT assume production-level complexity unless specified

2. **Request clarification for ambiguous scope**
   - If task boundaries are unclear, ASK for clarification
   - If complexity level is not specified, ASK for target complexity
   - Do NOT assume scope or make architectural decisions without validation

3. **Design to stated requirements exactly**
   - Match the complexity level requested (simple vs complex)
   - Stay within specified line count targets when provided
   - Follow "minimal," "streamlined," or "focused" guidance literally
   - Do NOT over-engineer solutions beyond stated needs

**Scope Validation Checkpoints (MANDATORY):**

- **Before design completion**: Validate design stays within specified task scope
- **Before handoff**: Confirm complexity matches stated targets
- **During review**: Check implementation matches original requirements, not assumed
  needs

## Subagent Role Boundaries

### MANDATORY Compliance Requirements for All Subagents

**ALL SUBAGENTS MUST STRICTLY ADHERE TO THE FOLLOWING:**

1. **Separation of Concerns (MANDATORY)**:
   - **Architects MUST NOT implement code** - only design, plan, and specify
     requirements
   - **Developers MUST NOT make architectural decisions** - follow architect specifications exactly
   - **Evaluators MUST NOT implement** - only design evaluation frameworks and
     metrics
   - **Code reviewers MUST focus solely on quality, security, and standards compliance**
   - **NEVER cross role boundaries** without explicit handoff documentation

2. **Command Execution (MANDATORY)**:
   - **ALWAYS use make recipes** - See [Complete Command Reference](CONTRIBUTING.md#complete-command-reference)
   - **Document any deviation** from make commands with explicit reason

3. **Quality Validation (MANDATORY)**:
   - **MUST run `make validate`** before task completion
   - **MUST fix ALL issues** found by validation steps
   - **MUST NOT proceed** with type errors or lint failures

4. **Coding Style Adherence (MANDATORY)**:
   - **MUST follow project patterns** - see
     [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation) for detailed
     standards
   - **MUST write concise, focused code** with no unnecessary features

5. **Documentation Updates (MANDATORY)**:
   - **MUST update documentation** - see
     [CONTRIBUTING.md](CONTRIBUTING.md#style-patterns--documentation) for
     requirements
   - **MUST update AGENT_LEARNINGS.md** when learning new patterns (concise,
     laser-focused, streamlined)

6. **Testing Requirements (MANDATORY)**:
   - **MUST create tests** for new functionality - see
     [CONTRIBUTING.md](CONTRIBUTING.md#testing-strategy--guidelines) for approach
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

### Below Threshold Action

Gather more context or escalate to AGENT_REQUESTS.md

## Agent Quick Reference

**Pre-Task:**

- Read AGENTS.md → CONTRIBUTING.md for technical details
- Confirm role: Architect|Developer|Reviewer
- Verify quality thresholds met (Context: 8/10, Clarity: 7/10, Alignment: 8/10,
  Success: 7/10)

**During Task:**

- Use make commands (document deviations)
- Follow BDD approach for tests
- Update documentation when learning patterns

**Post-Task:**

- Run `make validate` - must pass all checks
- Update CHANGELOG.md for non-trivial changes
- Document new patterns in AGENT_LEARNINGS.md (concise, laser-focused,
  streamlined)
- Escalate to AGENT_REQUESTS.md if blocked
