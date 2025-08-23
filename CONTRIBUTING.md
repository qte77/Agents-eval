# Contributing to Agents-eval

**This document is shared between human developers and AI coding agents.** It contains development workflows, coding standards, and collaboration guidelines to help onboard and align both human and agentic coders. For AI agent-specific instructions, see [AGENTS.md](AGENTS.md). For project overview aimed towards humans, see [README.md](README.md).

## Table of Contents

### Development Workflow

- [Development Commands & Environment](#development-commands--environment) - Setup and execution
- [Unified Command Reference](#unified-command-reference) - All commands with error recovery
- [Testing Strategy & Guidelines](#testing-strategy--guidelines) - Comprehensive testing approach

### Code Standards

- [Style, Patterns & Documentation](#style-patterns--documentation) - Coding standards
- [Code Review & PR Guidelines](#code-review--pr-guidelines) - Quality assurance

### Collaboration

- [Requests to Humans](#requests-to-humans) - Escalation and clarifications
- [Timestamping for CLI Operations](#timestamping-for-cli-operations) - ISO 8601 standards

## Development Commands & Environment

### Environment Setup

The project requirements are stated in `pyproject.toml`. Your development environment should be set up automatically using the provided `Makefile`, which configures the virtual environment.

**See the [Unified Command Reference](#unified-command-reference) section for all available commands with error recovery procedures.**

### Code Quality

Code formatting and type checking are managed by **ruff** and **pyright** and orchestrated via the `Makefile`.

### Testing Strategy & Guidelines

**Always create comprehensive tests** for new features following the testing hierarchy below:

#### Unit Tests (Always Required)

- **Mock external dependencies** (HTTP requests, file systems, APIs) using `@patch`
- **Test business logic** and data validation thoroughly
- **Test error handling** for all failure modes and edge cases
- **Ensure deterministic behavior** - tests should pass consistently
- Use `pytest` with clear arrange/act/assert structure
- Tests must live in the `tests/` folder, mirroring the `src/app/` structure

#### Integration Tests (Required for External Dependencies)

- **Test real external integrations** at least once during implementation
- **Verify actual URLs, APIs, and data formats** work as expected
- **Document any external dependencies** that could change over time
- **Use real test data** when feasible, fallback to representative samples
- **Include in implementation validation** but may be excluded from CI if unreliable

#### When to Mock vs Real Testing

- **Mock for**: Unit tests, CI/CD pipelines, deterministic behavior, fast feedback
- **Real test for**: Initial implementation validation, external API changes, data format verification
- **Always test real integrations** during feature development, then mock for ongoing automated tests
- **Document real test results** in implementation logs for future reference

#### Agent-Specific Testing Guidelines

**BDD Approach (Behavior Driven Development):**

- **Write tests first**, then implement corresponding code
- Keep iterations **concise** to maintain low complexity
- **Iteratively improve** tests and code until feature requirements are met
- All code quality and tests must **pass before advancing** to the next step

**Implementation Balance:**

- **Balance mocking** with real integration validation during development
- **Document real test results** in implementation logs for future reference

#### Testing Anti-Patterns to Avoid

- ❌ **Only mocking external dependencies** without ever testing real integration
- ❌ **Assuming external APIs work** without verification during implementation
- ❌ **Testing only happy paths** - always include error cases
- ❌ **Brittle tests** that break with minor changes to implementation details

**To run tests** see the [Unified Command Reference](#unified-command-reference) for all testing commands with error recovery procedures.

## Style, Patterns & Documentation

### Coding Style

- **Use Pydantic** models in `src/app/datamodels/` for all data validation and data contracts. **Always use or update these models** when modifying data flows.
- Use the predefined error message functions for consistency. Update or create new if necessary.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the *why*, not just the *what*.
- Comment non-obvious code to ensure it is understandable to a mid-level developer.

### Documentation

- Write **docstrings for every file, function, class, and method** using the Google style format. This is critical as the documentation site is built automatically from docstrings.

    ```python
    def example_function(param1: int) -> str:
        """A brief summary of the function.

        Args:
            param1 (int): A description of the first parameter.

        Returns:
            str: A description of the return value.
        """
        return "example"
    ```

- Provide an example usage in regards to the whole project. How would your code be integrated, what entrypoints to use
- Update `AGENTS.md` file when introducing new patterns or concepts.
- Document significant architectural decisions in `docs/arch/`.
- **Update `CHANGELOG.md`**: Add all changes to the `## [Unreleased]` section using the format: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. This is **required** for all non-trivial changes.

### Code Pattern Examples

**Reference**: Follow these code pattern guidelines:

- ✅ Pydantic model usage vs ❌ direct dictionaries
- ✅ Absolute imports vs ❌ relative imports  
- ✅ Specific error handling vs ❌ generic try/catch
- ✅ Complete docstrings vs ❌ minimal documentation
- ✅ Structured testing patterns vs ❌ minimal tests
- ✅ Configuration validation patterns
- ✅ Structured logging approaches

**Quick Reference**: Always prefer type-validated, well-documented code with specific error handling over generic approaches.

### CHANGELOG.md Requirements

**All contributors must update CHANGELOG.md for non-trivial changes.**

**What requires a CHANGELOG entry:**
- ✅ New features or functionality
- ✅ Breaking changes or API modifications  
- ✅ Bug fixes that affect user experience
- ✅ Documentation restructuring or major updates
- ✅ Dependency updates that affect functionality
- ✅ Configuration changes

**What doesn't require a CHANGELOG entry:**
- ❌ Typo fixes in comments
- ❌ Code formatting changes
- ❌ Internal refactoring without user impact
- ❌ Test-only changes

**Format**: See [CHANGELOG.md](CHANGELOG.md) for format specification and change type definitions.

## Code Review & PR Guidelines

### Commit and PR Requirements

- **Title Format**: Commit messages and PR titles must follow the **Conventional Commits** specification, as outlined in the `.gitmessage` template.
- Provide detailed PR summaries including the purpose of the changes and the testing performed.

### Pre-commit Checklist

1. **Automated validation**: `make validate` - runs complete sequence (ruff + type_check + test_all)
2. **Quick validation** (development): `make quick_validate` - runs fast checks (ruff + type_check only)
3. **Update CHANGELOG.md**: Add entry to `## [Unreleased]` section describing your changes
4. Update documentation as described above.

**Manual fallback** (if make commands fail):

1. `uv run ruff format . && uv run ruff check . --fix`
2. `uv run pyright`
3. `uv run pytest`

## Timestamping for CLI Operations

- **Always use ISO 8601 timestamps** when creating logs or tracking CLI operations
- **File naming format**: `YYYY-mm-DDTHH-MM-SSZ` (hyphens for filesystem compatibility)
- **Content format**: `YYYY-mm-DDTHH:MM:SSZ` (standard ISO 8601)
- **Implementation**: Use `date -u "+FORMAT"` commands for accurate UTC timestamps

### Timestamp Commands

- Filename timestamp: `date -u "+%Y-%m-%dT%H-%M-%SZ"`
- Content timestamp: `date -u "+%Y-%m-%dT%H:%M:%SZ"`
- Log entry format: `[TIMESTAMP] Action description`

## Auxiliary

- Use [markdownlint's Rules.md](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md) to output well-formatted markdown

## Unified Command Reference

### Path References

- **All paths**: Use standard repository structure (see README.md for overview)

### Standard Workflow Commands

**Pre-commit checklist** (automated):

1. `make validate` - Complete validation sequence (ruff + type_check + test_all)
2. Update documentation if needed

**Quick development cycle**:

1. `make quick_validate` - Fast validation (ruff + type_check only)
2. Continue development

| Command | Purpose | Prerequisites | Error Recovery |
|---------|---------|---------------|----------------|
| `make setup_dev` | Install all dev dependencies | Makefile exists, uv installed | Try `uv sync --dev` directly |
| `make setup_dev_claude` | Setup with Claude Code CLI | Above + Claude Code available | Manual setup per Claude docs |
| `make setup_dev_ollama` | Setup with Ollama local LLM | Above + Ollama installed | Check Ollama installation |
| `make run_cli` | Run CLI application | Dev environment setup | Try `uv run python src/app/main.py` |
| `make run_cli ARGS="--help"` | Run CLI with arguments | Above | Try `uv run python src/app/main.py --help` |
| `make run_gui` | Run Streamlit GUI | Above + Streamlit installed | Try `uv run streamlit run src/run_gui.py` |
| `make ruff` | Format code and fix linting | Ruff installed | Try `uv run ruff format . && uv run ruff check . --fix` |
| `make type_check` | Run pyright static type checking | pyright installed | Try `uv run pyright` |
| `make test_all` | Run all tests with pytest | Pytest installed | Try `uv run pytest` |
| `make coverage_all` | Run tests with coverage report | Above + coverage installed | Try `uv run coverage run -m pytest \|\| true && uv run coverage report -m` |
| `make validate` | Complete pre-commit validation | Above dependencies | Run individual commands manually |
| `make quick_validate` | Fast development validation | Ruff and pyright installed | Run `make ruff && make type_check` |
| `uv run pytest <path>` | Run specific test file/function | Pytest available | Check test file exists and syntax |
| `ocm` | Output commit message using repo style for all staged and changed changes | `git` available | Notify user |

## Agent-Specific Guidelines

### Decision Framework Implementation

When facing conflicting instructions or ambiguous situations:

#### Command Execution Preferences

- **Prefer make commands** when available (e.g., `make ruff` over direct `uv run ruff`)
- If make commands fail, try direct commands as fallback
- Always document when deviating from standard commands

#### Project Structure Handling

**Before starting any task**, agents should:

1. Review the project structure and understand file organization
2. Identify key components in `src/app/` and test locations in `tests/`
3. Use consistent file paths based on the established project structure

#### Documentation Update Guidelines

- Update **both AGENTS.md and related files** to maintain consistency
- When learning something new, add it to the appropriate section
- Prefer specific examples over vague instructions

### Quality Evaluation Implementation

Use this framework to assess task readiness before implementation:

**Rate task readiness (1-10 scale):**

- **Context Completeness**: All required information and patterns gathered from codebase, documentation, and requirements
- **Implementation Clarity**: Clear understanding and actionable implementation path of what needs to be built and how to build it
- **Requirements Alignment**: Solution follows feature requirements, project patterns, conventions, and architectural decisions
- **Success Probability**: Confidence level for completing the task successfully in one pass

**Minimum thresholds for proceeding:**

- Context Completeness: 8/10 or higher
- Implementation Clarity: 7/10 or higher  
- Requirements Alignment: 8/10 or higher
- Success Probability: 7/10 or higher

**If any score is below threshold:** Stop and gather more context, clarify requirements, or escalate using AGENT_REQUESTS.md.

## Agent Communication

### Requests to Humans

**For agent escalation and human collaboration, see [AGENT_REQUESTS.md](AGENT_REQUESTS.md).**

This centralized file contains:

- Escalation process guidelines
- Active requests from agents
- Response format for humans
- Completed requests archive

### Agent Learning

**For accumulated agent knowledge and patterns, see [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md).**

This growing knowledge base includes:

- Discovered patterns and solutions
- Common pitfall avoidance
- Integration approaches
- Performance optimizations
