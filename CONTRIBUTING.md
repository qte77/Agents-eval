---
title: Contributing to Agents-eval
description: Technical development workflows, coding standards, and implementation guidelines
version: 1.0.0
created: 2025-08-23
updated: 2026-02-16
---

**This document contains technical development workflows, coding standards, and implementation guidelines shared by both human developers and AI coding agents.** For AI agent behavioral rules and compliance requirements, see [AGENTS.md](AGENTS.md). For project overview and navigation, see [README.md](README.md).

## Instant Commands

**Development Workflow:**

- `make setup_dev` → Setup development environment  
- `make quick_validate` → Fast validation during development (lint + type checking + complexity + duplication)
- `make validate` → Complete pre-commit validation (lint + type check + test)

**Testing:**

- `make test` → Run all tests with pytest
- `uv run pytest <path>` → Run specific test file/function

**Emergency Fallback** (if make commands fail):

- `uv run ruff format . && uv run ruff check . --fix` → Format and lint code
- `uv run pyright` → Type checking
- `uv run pytest` → Run tests

## Complete Command Reference

| Command | Purpose | Prerequisites | Error Recovery |
|---------|---------|---------------|----------------|
| `make setup_dev` | Install all dev dependencies | Makefile exists, uv installed | Try `uv sync --dev` directly |
| `make setup_claude_code` | Setup Claude Code CLI | Above + Claude Code available | Manual setup per Claude docs |
| `make setup_dev OLLAMA=1` | Setup with Ollama local LLM | Above + Ollama installed | Check Ollama installation |
| `make quickstart` | Download samples + evaluate smallest paper | API key in `.env` | `make setup_dataset` then `make run_cli ARGS="--paper-id=ID"` |
| `make run_cli` | Run CLI application | Dev environment setup | Try `uv run python src/app/main.py` |
| `make run_cli ARGS="--help"` | Run CLI with arguments | Above | Try `uv run python src/app/main.py --help` |
| `make run_gui` | Run Streamlit GUI | Above + Streamlit installed | Try `uv run streamlit run src/run_gui.py` |
| `make lint_src` | Format and lint src with ruff | Ruff installed | Try `uv run ruff format . && uv run ruff check . --fix` |
| `make type_check` | Run pyright static type checking | pyright installed | Try `uv run pyright` |
| `make test` | Run all tests with pytest | Pytest installed | Try `uv run pytest` |
| `make test_coverage` | Run tests with coverage report | Above + coverage installed | Try `uv run coverage run -m pytest \|\| true && uv run coverage report -m` |
| `make validate` | Complete pre-commit validation | Above dependencies | Run individual commands manually |
| `make quick_validate` | Fast development validation | Ruff, pyright, complexipy, jscpd installed | Run `make lint_src && make type_check && make complexity && make duplication` |
| `make duplication` | Detect copy-paste duplication in src/ | jscpd installed | Try `jscpd src/ --min-lines 5 --min-tokens 50` |
| `make setup_npm_tools` | Setup npm dev tools (markdownlint, jscpd) | Node.js and npm installed | Try `npm install -gs markdownlint-cli jscpd` |
| `make lint_md INPUT_FILES="docs/**/*.md"` | Lint and fix markdown files | markdownlint installed | Try `markdownlint docs/**/*.md --fix` |
| `make run_pandoc` | Convert MD to PDF with citations. See `make run_pandoc HELP=1` | pandoc + texlive installed | Try `make setup_pdf_converter CONVERTER=pandoc` |
| `uv run pytest <path>` | Run specific test file/function | Pytest available | Check test file exists and syntax |
| `ocm` | Output commit message using repo style for all staged and changed changes | `git` available | Notify user |

## Code Patterns Quick Reference

**Essential Patterns:**

- **Imports**: Use absolute imports (`from app.module import Class`)
- **Models**: Use Pydantic models in `src/app/data_models/` for all data validation  
- **Docstrings**: Google style format for all functions, classes, methods
- **Comments**: Add `# Reason:` for complex logic explaining the *why*
- **Dependencies**: Verify in `pyproject.toml` before using

**Testing Patterns:**

- **Mock externals**: Use `@patch` for HTTP requests, file systems, APIs
- **BDD approach**: Write tests first, implement code iteratively  
- **Test location**: Mirror `src/app/` structure in `tests/`

## Table of Contents

### Development Workflow

- [Development Commands & Environment](#development-commands--environment) - Setup and execution  
- [Testing Strategy & Guidelines](#testing-strategy--guidelines) - Comprehensive testing approach

### Code Standards

- [Style, Patterns & Documentation](#style-patterns--documentation) - Coding standards
- [Code Review & PR Guidelines](#code-review--pr-guidelines) - Quality assurance

### Collaboration

- [Documentation Hierarchy](#documentation-hierarchy) - Authority structure and single source of truth principles
- [Human-Agent Collaboration](#human-agent-collaboration) - Guidelines for AI agents and escalation

## Development Commands & Environment

### Environment Setup

The project requirements are in `pyproject.toml`. Use the provided `Makefile` to set up your development environment automatically. Code formatting and type checking are managed by **ruff** and **pyright**.

### Testing Strategy & Guidelines

**Always create focused, efficient tests** for new features:

#### Unit Tests (Always Required)

- **Mock external dependencies** (HTTP requests, file systems, APIs) using `@patch`
- **Test business logic** and data validation efficiently
- **Test error handling** for all failure modes and edge cases
- Use `pytest` with clear arrange/act/assert structure
- Tests must live in the `tests/` folder, mirroring the `src/app/` structure

#### Integration Tests (Required for External Dependencies)

- **Test real external integrations** at least once during implementation
- **Verify actual URLs, APIs, and data formats** work as expected
- **Use real test data** when feasible, fallback to representative samples

#### BDD Approach (Behavior Driven Development)

- **Write tests first**, then implement corresponding code
- Keep iterations **concise** to maintain low complexity
- **Iteratively improve** tests and code until feature requirements are met
- All code quality and tests must **pass before advancing** to the next step

#### Security Tests (`tests/security/`)

- SSRF prevention (URL validation, domain allowlisting, internal IP blocking)
- Prompt injection resistance (length limits, XML delimiter wrapping, format string prevention)
- Sensitive data filtering in logs and traces (API keys, passwords, tokens, env var names)
- Input size limits (DoS prevention)
- Tool registration scope validation

Security tests run as part of `make test` (no separate command needed).

**Testing Guidelines:**

- **Mock for**: Unit tests, CI/CD pipelines, deterministic behavior
- **Real test for**: Initial implementation validation, external API changes
- **Always test real integrations** during development, then mock for automated tests
- **Avoid**: Only mocking without real testing, testing only happy paths, brittle tests

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

**Follow these guidelines:**

- ✅ Pydantic model usage vs ❌ direct dictionaries
- ✅ Absolute imports vs ❌ relative imports  
- ✅ Specific error handling vs ❌ generic try/catch
- ✅ Complete docstrings vs ❌ minimal documentation
- ✅ Concise, focused implementations vs ❌ verbose, feature-heavy code
- ✅ Minimal dependencies vs ❌ heavy library usage

**Always analyze existing codebase patterns before implementing anything new.**

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

1. **Automated validation**: `make validate` - runs streamlined sequence (lint + type_check + test)
2. **Quick validation** (development): `make quick_validate` - runs fast checks (lint + type_check + complexity)
3. **Update CHANGELOG.md**: Add entry to `## [Unreleased]` section describing your changes
4. Update documentation as described above.

**Manual fallback** (if make commands fail):

1. `uv run ruff format . && uv run ruff check . --fix`
2. `uv run pyright`
3. `uv run pytest`

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

### Agent Integration Guidelines

**For comprehensive AI agent instructions, see [AGENTS.md](AGENTS.md).**

**Key integration points:**

- Agent behavioral rules and compliance → [AGENTS.md](AGENTS.md)
- Technical implementation standards → This document
- Command execution → [Complete Command Reference](#complete-command-reference)
- Testing approach → [Testing Strategy & Guidelines](#testing-strategy--guidelines)

### Context7 MCP Documentation Access

This project integrates with Context7 MCP for accessing comprehensive documentation. Context7 MCP access may require a `CONTEXT7_API_KEY` environment variable.

#### Core Dependencies Available

- `/agentops-ai/agentops`, `/delgan/loguru`, `/lightning-ai/torchmetrics`
- `/microsoft/markitdown`, `/networkx/networkx`, `/pydantic/logfire`
- `/pydantic/pydantic`, `/pydantic/pydantic-ai`, `/scikit-learn/scikit-learn`
- `/wandb/weave`, `/pytest-dev/pytest`, `/websites/streamlit_io`

#### Usage Examples

```bash
# Search for a library ID
mcp__context7__resolve-library-id --libraryName "pydantic"

# Get documentation
mcp__context7__get-library-docs --context7CompatibleLibraryID "/pydantic/pydantic" --tokens 8000

# Focus on specific topics  
mcp__context7__get-library-docs --context7CompatibleLibraryID "/pydantic/pydantic-ai" --topic "agents" --tokens 5000
```

### Requests to Humans

**For agent escalation and human collaboration, see [AGENT_REQUESTS.md](AGENT_REQUESTS.md).**

### Agent Learning

**For accumulated agent knowledge and patterns, see [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md).**
