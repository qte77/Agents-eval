# Agent Learning Documentation

This document captures patterns, solutions, and important insights discovered by AI agents during development. It serves as a growing knowledge base that helps both current and future agents avoid common pitfalls and apply proven solutions.

## Purpose

- **Knowledge Accumulation**: Preserve solutions and patterns discovered during development
- **Pattern Sharing**: Help agents learn from each other's experiences
- **Mistake Prevention**: Document common pitfalls and their solutions
- **Best Practice Evolution**: Track how coding practices improve over time

## Template for New Learnings

When documenting a new pattern, use this format:

**Structure:**

- **Date**: [ISO timestamp - use `date -u "+%Y-%m-%dT%H:%M:%SZ"`]
- **Context**: [When/where this pattern applies]
- **Problem**: [What issue this solves]
- **Solution**: [Implementation approach]
- **Example**: [Code example with language specified]
- **Validation**: [How to verify this works]
- **References**: [Related files, documentation, or PRs]

**Example Entry:**

```markdown
### Learned Pattern: Async Error Handling in Agents

- **Date**: 2025-07-20T14:30:00Z
- **Context**: PydanticAI agent processing with timeouts
- **Problem**: Agents hanging on long requests without proper timeout handling
- **Solution**: Use asyncio.wait_for with context manager for cleanup
- **Example**: Use asyncio.wait_for with timeout and proper cleanup
- **Validation**: Test with deliberately slow mock responses
- **References**: src/app/agents/agent_system.py:142
```

## Active Learning Entries

Agents should add new patterns discovered during development here.

### Learned Pattern: PlantUML Theming

- **Date**: 2025-08-05T00:00:00Z
- **Context**: PlantUML diagrams in `docs/arch_vis`
- **Problem**: Redundant PlantUML files for light and dark themes.
- **Solution**: Use a variable to define the theme and include the appropriate style file. This allows for a single PlantUML file to be used for multiple themes.
- **Example**:

  ```plantuml
  !ifndef STYLE
  !define STYLE "light"
  !endif
  !include styles/github-$STYLE.puml
  ```

- **Validation**: Generate diagrams with different themes by setting the `STYLE` variable.
- **References**: `docs/arch_vis/`

### Learned Pattern: Module Naming Conflicts Resolution

- **Date**: 2025-07-22T14:30:00Z
- **Context**: PeerRead dataset integration with pyright validation
- **Problem**: Named module `src/app/datasets/` which conflicted with HuggingFace `datasets` library, causing "Source file found twice under different module names" pyright errors
- **Solution**: Rename modules to be specific and avoid common library names. Use descriptive prefixes like `datasets_peerread.py` instead of generic `datasets/`
- **Example**: `src/app/utils/datasets_peerread.py` instead of `src/app/datasets/peerread_loader.py`
- **Validation**: pyright now passes with `Success: no issues found in 16 source files`
- **References**: Added explicit guidance in AGENTS.md Code Organization Rules section

### Learned Pattern: External Dependencies Validation

- **Date**: 2025-07-23T11:00:39Z
- **Context**: PeerRead dataset integration with external API dependencies
- **Problem**: Over-reliance on mocking without validating real external services leads to implementation based on incorrect assumptions about data structure and API endpoints. Did not explicitly test download functionality with real network requests during implementation
- **Solution**: Balance unit test mocking with real integration validation during development. Research existing ecosystem solutions (e.g., HuggingFace datasets) before implementing custom downloaders. Always test critical external functionality explicitly, not just through mocks
- **Example**: Mock for unit tests, but validate real URLs/APIs early: `requests.head(url)` to verify accessibility before full implementation. Test actual download with small samples during development
- **Validation**: Test actual network requests during development, not just after implementation. Explicitly validate download functionality works with real data
- **References**: PeerRead integration - discovered incorrect URL assumptions that mocks didn't catch

## Guidelines for Adding Learnings

### When to Document

- **Novel Solutions**: When you solve a problem in a way not covered by existing documentation
- **Common Pitfalls**: When you encounter and solve a tricky issue that others might face
- **Performance Insights**: When you discover performance optimization techniques
- **Integration Patterns**: When you successfully integrate new libraries or services
- **Error Resolution**: When you solve complex debugging or configuration issues

### What to Include

- **Specific Context**: Be clear about when this pattern applies
- **Complete Solutions**: Include enough detail for another agent to implement
- **Working Examples**: Provide code examples that actually work
- **Validation Steps**: How to verify the solution works correctly
- **Related Information**: Link to relevant files, docs, or external resources

### What NOT to Document

- **Basic Language Features**: Standard Python/library usage covered in official docs
- **Temporary Workarounds**: Solutions that are meant to be replaced
- **Project-Specific Details**: Information that only applies to this exact codebase
- **Incomplete Solutions**: Partial patterns that haven't been fully validated

## Pattern Categories

### Development Workflow

- Build system optimizations
- Testing strategies
- Code organization patterns

### Technical Solutions

- Library integration approaches
- Performance optimization techniques
- Error handling patterns

### Project-Specific

- Architecture decisions
- Data flow patterns
- Configuration management

## Archive Policy

- Keep entries current and relevant
- Archive outdated patterns to separate section
- Update patterns when better solutions are discovered
- Reference patterns in AGENTS.md when they become standard practice
