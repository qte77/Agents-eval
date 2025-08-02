# Feature description for: [ Replace with your feature name ]

**Must** follow AGENTS.md setup and path conventions

## User Story

**As a** [type of user - developer/end user/agent/system]
**I want** [what functionality you need]
**So that** [why you need this - the business value]

### Acceptance Criteria

- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Edge case handling requirement]

## Feature Description

### What

[Clear, concise description of what the feature does]

### Why

[Business/technical justification - why is this needed now?]

### Scope

[What's included and what's explicitly NOT included in this feature]

## Technical Specifications

### Dependencies

- [ ] Existing libraries from `$PROJECT_REQUIREMENTS`: [list specific ones]
- [ ] New libraries needed: [justify per AGENTS.md - never assume]
- [ ] PydanticAI components: [agents, tools, etc.]

### Data Models

- [ ] New Pydantic models in `$DATAMODELS_PATH`: [describe purpose]
- [ ] Existing models to modify: [specific changes]
- [ ] Configuration changes: [specific settings needed]

### API/Interface Design

[If applicable - describe function signatures, CLI arguments, or agent interactions]

## Implementation Guidance

### Complexity Estimate

- [ ] **Simple** (single focused module)
- [ ] **Medium** (2-3 related modules)
- [ ] **Complex** (multiple modules, requires refactoring)

### File Structure

[Describe which files in `$APP_PATH` will be created/modified]

### Integration Points

- [ ] Existing agents to modify: [list]
- [ ] CLI commands to add/update: [describe]
- [ ] Configuration files to update: [list]

## Testing Strategy

### Test Coverage Required

- [ ] Feature-specific unit tests
- [ ] Agent interaction tests (if applicable)
- [ ] Domain-specific error cases

**Must** follow AGENTS.md testing requirements and validation commands

## Examples

[Provide and explain examples that you have in the `$CTX_EXAMPLES_PATH` folder or create new ones]

### Usage Examples

[Show how a user would interact with this feature]

### Code Examples

[Show key implementation patterns or API usage]

## Documentation

### Reference Materials

[List web pages, documentation, or MCP server sources needed during development]

### Documentation Updates

- [ ] Feature-specific documentation
- [ ] Update `AGENTS.md` if new patterns introduced
- [ ] Update `$CHANGELOG_PATH`

**Must** follow AGENTS.md docstring requirements

## Success Criteria

### Definition of Done

- [ ] All acceptance criteria met
- [ ] Feature-specific tests pass
- [ ] Integration works as expected
- [ ] Feature-specific documentation complete

**Must** also complete AGENTS.md pre-commit checklist

### Feature-Specific Quality Gates

- [ ] Domain logic correctly implemented
- [ ] User experience meets requirements
- [ ] Performance meets expectations

## Edge Cases & Error Handling

### Known Edge Cases

[List potential edge cases and how they should be handled]

### Error Scenarios

[Describe error conditions and expected behavior]

### Security Considerations

[Any security implications or requirements]

## Feature-Specific Considerations

[Domain-specific gotchas or requirements beyond AGENTS.md general rules]
