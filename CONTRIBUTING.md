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

- [Documentation Hierarchy](#documentation-hierarchy) - Authority structure and single source of truth principles
- [Human-Agent Collaboration](#human-agent-collaboration) - Guidelines for AI agents and escalation

## Development Commands & Environment

### Environment Setup

The project requirements are stated in `pyproject.toml`. Your development environment should be set up automatically using the provided `Makefile`, which configures the virtual environment.

Code formatting and type checking are managed by **ruff** and **pyright** and orchestrated via the `Makefile`.

**See the [Unified Command Reference](#unified-command-reference) section for all available commands with error recovery procedures.**

### Testing Strategy & Guidelines

**Always create focused, efficient tests** for new features following the testing hierarchy below:

#### Unit Tests (Always Required)

- **Mock external dependencies** (HTTP requests, file systems, APIs) using `@patch`
- **Test business logic** and data validation efficiently
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

#### Testing Anti-Patterns to Avoid

- ❌ **Only mocking external dependencies** without ever testing real integration
- ❌ **Assuming external APIs work** without verification during implementation
- ❌ **Testing only happy paths** - always include error cases
- ❌ **Brittle tests** that break with minor changes to implementation details

**To run tests** see the [Unified Command Reference](#unified-command-reference) for all testing commands with error recovery procedures.

## Style, Patterns & Documentation

### Coding Style

- **Follow existing codebase patterns exactly** - analyze file structure, naming conventions, and architectural decisions before writing any code
- **Write concise, focused, streamlined code** with no unnecessary features or verbose implementations
- **Use Pydantic** models in `src/app/datamodels/` for all data validation and data contracts. **Always use or update these models** when modifying data flows.
- Use the predefined error message functions for consistency. Update or create new if necessary.
- **Minimize dependencies** and prefer lightweight solutions over heavy libraries
- When writing complex logic, **add an inline `# Reason:` comment** explaining the *why*, not just the *what*.
- Comment non-obvious code to ensure it is understandable to a mid-level developer.
- **Avoid long output or lengthy code blocks** - keep implementations focused and minimal

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
- ✅ Concise, focused implementations vs ❌ verbose, feature-heavy code
- ✅ Minimal dependencies vs ❌ heavy library usage
- ✅ Streamlined file structures vs ❌ complex hierarchies

**Quick Reference**: Always prefer type-validated, well-documented, concise code with specific error handling over generic approaches. **Analyze existing codebase patterns before implementing anything new.**

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
- Provide focused PR summaries including the purpose of the changes and the testing performed.

### Pre-commit Checklist

1. **Automated validation**: `make validate` - runs streamlined sequence (ruff + type_check + test_all)
2. **Quick validation** (development): `make quick_validate` - runs fast checks (ruff + type_check only)
3. **Update CHANGELOG.md**: Add entry to `## [Unreleased]` section describing your changes
4. Update documentation as described above.

**Manual fallback** (if make commands fail):

1. `uv run ruff format . && uv run ruff check . --fix`
2. `uv run pyright`
3. `uv run pytest`

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
| `make setup_markdownlint` | Setup markdownlint CLI | Node.js and npm installed | Try `npm install -gs markdownlint-cli` |
| `make run_markdownlint INPUT_FILES="docs/**/*.md"` | Lint and fix markdown files | markdownlint installed | Try `markdownlint docs/**/*.md --fix` |
| `uv run pytest <path>` | Run specific test file/function | Pytest available | Check test file exists and syntax |
| `ocm` | Output commit message using repo style for all staged and changed changes | `git` available | Notify user |

## Documentation Hierarchy

This project follows a structured documentation hierarchy to prevent scope creep, eliminate redundancy, and maintain clear authority for different types of information.

### Authority Structure & Single Source of Truth

Each document type has specific authority and serves as the single source of truth for its domain:

#### Requirements & Strategy (What & Why)

- **[PRD.md](docs/PRD.md)** - **PRIMARY AUTHORITY** for business requirements, scope boundaries, and project goals
- **[UserStory.md](docs/UserStory.md)** - **AUTHORITY** for user workflows, acceptance criteria, and success metrics

#### Technical Implementation (How)

- **[architecture.md](docs/architecture.md)** - **AUTHORITY** for system design, technical decisions, and architectural patterns
- **[README.md](README.md)** - **AUTHORITY** for project overview, navigation, and current status

#### Implementation Details (When & Current State)

- **Sprint Documents** (`docs/sprints/`) - **AUTHORITY** for implementation timelines, current capabilities, and task execution
- **Usage Guides** (`docs/peerread-agent-usage.md`) - **AUTHORITY** for operational procedures and working features

#### Research & Reference (What's Possible)

- **Landscape Documents** (`docs/landscape/`) - **INFORMATIONAL ONLY** for technology research, feasibility analysis, and available options
- **Assessment Documents** (`docs/sprints/assessment/`) - **INFORMATIONAL ONLY** for capability gap analysis and technical evaluations

### Reference Flow & Decision Rules

#### Correct Reference Pattern

```text
PRD.md (requirements) → architecture.md (technical design) → Sprint docs (implementation) → Usage guides (operations)
     ↑
Landscape docs (inform strategic decisions, do not create requirements)
```

#### Anti-Scope-Creep Rules

1. **Landscape possibilities ≠ Requirements** - Research documents inform choices but do not dictate implementation
2. **Validate against authority chain** - Implementation decisions must align with PRD.md requirements
3. **Current vs Future clarity** - Clearly distinguish between implemented, planned, and possible features

#### Anti-Redundancy Rules

1. **Single source of truth** - Each piece of information should exist in exactly ONE authoritative document
2. **Reference, don't duplicate** - Other documents should link to authoritative sources, not repeat information
3. **Update procedures** - When updating requirements or technical decisions, update the authoritative document and remove duplicates elsewhere

### Document Maintenance Procedures

#### When Updating Strategic Documents (PRD.md, UserStory.md, architecture.md)

1. Review all dependent implementation documents for alignment
2. Update sprint plans if scope or technical approach changes
3. Ensure landscape references don't create unrealistic expectations
4. Remove outdated information from non-authoritative documents

#### When Creating New Documents

1. Reference appropriate authority documents in YAML frontmatter
2. Specify document category: requirements/technical/implementation/research
3. Include authority chain references to prevent conflicts
4. Avoid duplicating information available in authoritative sources

#### Quality Assurance

- Implementation documents must validate against PRD.md scope
- Technical decisions must align with architecture.md patterns
- Research findings should inform but not override strategic documents
- Sprint status should reflect actual implementation reality

This hierarchy prevents the confusion between "what could be built" (landscape research) vs. "what should be built" (PRD requirements) vs. "what is built" (implementation status).

## Human-Agent Collaboration

### Basic Guidelines for AI Agents

**For comprehensive AI agent instructions, see [AGENTS.md](AGENTS.md).**

**Key principles for AI agents working in this codebase:**

- Follow existing project structure and organization patterns
- Always use `make` recipes for commands (e.g., `make validate`, `make test_all`)
- Request clarification when requirements are unclear rather than making assumptions
- Write concise, focused code following established codebase patterns
- Update CHANGELOG.md for non-trivial changes and AGENTS.md when learning new patterns

### Requests to Humans

**For agent escalation and human collaboration, see [AGENT_REQUESTS.md](AGENT_REQUESTS.md).**

### Agent Learning

**For accumulated agent knowledge and patterns, see [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md).**
