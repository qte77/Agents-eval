# Spec-Kit Adoption Plan for Agents-eval

## Executive Summary

Adopt GitHub's Spec-Kit methodology to standardize and improve the
specification-driven development process, enhance subagent coordination,
and create consistent documentation templates across all sprints.

## Phase 1: Foundation Setup (Week 1)

### 1.1 Download and Adapt Spec-Kit Templates

- Clone spec-kit repository and extract templates
- Create `docs/templates/spec-kit/` directory structure:

```text
docs/templates/spec-kit/
├── spec-template.md        # Requirements specification
├── plan-template.md        # Technical implementation plan  
├── tasks-template.md       # Task breakdown structure
└── agent-file-template.md  # Subagent instructions
```

### 1.2 Customize Templates for Agents-eval

- Adapt spec-template.md to include:
  - PRD.md reference section
  - Mandatory vs optional requirements
  - Acceptance criteria from UserStory.md
- Modify plan-template.md to include:
  - Architecture.md alignment
  - Three-tier evaluation references
  - Worktree strategy section
- Enhance agent-file-template.md with:
  - Subagent role boundaries (AGENTS.md compliance)
  - Handoff documentation requirements
  - Validation commands

## Phase 2: Retrofit Current Sprint2 (Week 1-2)

### 2.1 Convert Sprint2 Document

Transform `2025-09_Sprint2_Pipeline-Enhancements.md` into spec-kit structure:

```text
docs/sprints/2025-09_Sprint2/
├── spec.md         # Extract requirements section
├── plan.md         # Technical implementation details
├── tasks.md        # Structured task breakdown
└── agent-files/
    ├── python-developer.md
    └── code-reviewer.md
```

### 2.2 Create Agent Files

- python-developer.md: Third-party metrics implementation instructions
- code-reviewer.md: Validation and quality assurance requirements

## Phase 3: Process Integration (Week 2)

### 3.1 Update CONTRIBUTING.md

Add new section "Spec-Driven Development Workflow":

- Template usage guidelines
- Sprint documentation structure
- Subagent file creation process

### 3.2 Update AGENTS.md

Add "Specification Templates" section:

- How subagents should read spec files
- Agent file interpretation guidelines
- Task execution from tasks.md

### 3.3 Create Spec-Kit CLI Helper

Create `scripts/spec-kit/init-sprint.sh`:

```bash
#!/bin/bash
# Initialize new sprint with spec-kit structure
# Usage: ./init-sprint.sh [sprint-name]
```

## Phase 4: Migration Strategy (Week 2-3)

### 4.1 Historical Sprint Documentation

- Keep existing sprint docs as-is (historical record)
- Add README.md in docs/sprints/ explaining old vs new format

### 4.2 Future Sprint Template

Create `docs/sprints/TEMPLATE/`:

```text
TEMPLATE/
├── spec.md         # Copy from spec-template.md
├── plan.md         # Copy from plan-template.md
├── tasks.md        # Copy from tasks-template.md
├── agent-files/    # Directory for subagent instructions
└── artifacts/      # Generated code, configs, etc.
```

## Phase 5: Validation & Rollout (Week 3)

### 5.1 Test with Sprint3 Planning

- Use spec-kit templates for next sprint
- Document lessons learned
- Refine templates based on experience

### 5.2 Create Documentation

- Write docs/guides/spec-driven-development.md
- Add examples of completed specs, plans, tasks
- Create subagent instruction examples

### 5.3 Automation Scripts

- Create make target: `make new-sprint NAME=Sprint3`
- Auto-generate sprint structure from templates
- Include git worktree setup commands

## Benefits Expected

1. **Standardized Documentation**: Consistent structure across all sprints
2. **Better Subagent Coordination**: Clear agent files with specific instructions
3. **Improved Requirements Tracking**: Specs separate from implementation
4. **Enhanced Task Management**: Structured tasks.md replacing ad-hoc todos
5. **Clearer Handoffs**: Agent files define exact responsibilities

## Success Metrics

- Reduced sprint planning time by 30%
- Improved subagent task completion accuracy
- Consistent documentation quality across sprints
- Clear separation of requirements vs implementation
- Better traceability from PRD → spec → plan → tasks

## Implementation Order

1. Setup templates directory (30 min)
2. Customize templates for project (2 hours)
3. Retrofit Sprint2 as proof-of-concept (4 hours)
4. Update documentation (2 hours)
5. Create automation scripts (2 hours)
6. Test with Sprint3 planning (ongoing)

## Alignment with Current Project

### Existing Strengths to Preserve

- PRD-driven development approach
- Three-tier document hierarchy (PRD → architecture → UserStory)
- Subagent coordination patterns
- Git worktree workflow

### Improvements Spec-Kit Brings

- **Specification Structure**: Replace ad-hoc sprint documents with structured specs
- **Task Management**: Replace TodoWrite with comprehensive tasks.md
- **Agent Instructions**: Standardize subagent files instead of inline commands
- **Planning Consistency**: Uniform plan.md format across all sprints

### Integration Points

- Spec-Kit templates will reference existing PRD.md/architecture.md/UserStory.md
- Agent files will enforce AGENTS.md compliance requirements
- Tasks.md will include make commands from CONTRIBUTING.md
- Plans will incorporate worktree strategy from scripts/worktrees/

## Risk Mitigation

### Potential Risks

1. **Adoption Resistance**: Team familiar with current process
2. **Over-documentation**: Too many templates might slow development
3. **Template Rigidity**: Might not fit all sprint types

### Mitigation Strategies

1. **Gradual Adoption**: Start with Sprint2 retrofit, learn, then expand
2. **Template Flexibility**: Mark optional sections clearly
3. **Regular Reviews**: Refine templates based on sprint retrospectives
4. **Automation**: Scripts to reduce manual template work

## Next Steps

1. **Immediate**: Create docs/spec-kit-adoption-plan.md (this document)
2. **Week 1**: Download spec-kit, adapt templates, retrofit Sprint2
3. **Week 2**: Update documentation, create automation
4. **Week 3**: Test with Sprint3, gather feedback
5. **Month 1**: Full rollout across all new sprints
