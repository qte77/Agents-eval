# Agent instructions for `Agents-eval` repository

As proposed by [agentsmd.net](https://agentsmd.net/) and used by [wandb weave AGENTS.md](https://github.com/wandb/weave/blob/master/AGENTS.md).

## Core Rules

* When you learn something new about the codebase or introduce a new concept, **update this file (`AGENTS.md`)** to reflect the new knowledge. This is YOUR FILE! It should grow and evolve with you.
* If there is something that doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add it to the **`Requests to Humans`** section below.
* Always follow the established coding patterns and conventions in the codebase, particularly the use of **Pydantic** for data contracts and the modular structure.
* Always document changes according to the **`Documentation`** section below.

## Architecture Overview

This is a multi-agent evaluation system for assessing agentic AI systems. The project uses **PydanticAI** as the core framework for agent orchestration. The system is designed for evaluation purposes, not for production agent deployment.

### Data Flow

1. User input → Manager Agent
2. Manager delegates to Researcher Agent (with DuckDuckGo search)
3. Researcher results → Analyst Agent for validation
4. Validated data → Synthesizer Agent for report generation
5. Results evaluated using configurable metrics

### Key Dependencies

* **PydanticAI**: Agent framework and orchestration
* **uv**: Fast Python dependency management
* **Streamlit**: GUI framework
* **Ruff**: Code formatting and linting
* **MyPy**: Static type checking

## Codebase Structure

### Main Components

* `src/app/`: The core application logic. This is where most of your work will be.
  * `main.py`: The main entry point for the CLI application.
  * `agents/agent_system.py`: Defines the multi-agent system, their interactions, and orchestration. **This is the central logic for agent behavior.**
  * `config/data_models.py`: Contains all **Pydantic** models that define the data contracts. This is a critical file for understanding data flow.
  * `config/config_chat.json`: Holds provider settings and system prompts for agents.
  * `config/config_eval.json`: Defines evaluation metrics and their weights.
  * `evals/metrics.py`: Implements the evaluation metrics (e.g., `planning_rational`, `task_success`, `text_similarity`).
* `src/gui/`: Contains the source code for the Streamlit GUI.
  * `run_gui.py`: The entry point for launching the GUI.
* `docs/`: Contains project documentation, including the Product Requirements Document (`PRD.md`) and the C4 architecture model.
* `tests/`: Contains all tests for the project, written using **pytest**.

## Development Commands

### Environment Setup

The project requires **Python 3.13** and uses **uv** for dependency management. Your development environment should be set up automatically using the provided `Makefile`.

* `make setup_dev`: Install uv and all dev dependencies.
* `make setup_dev_claude`: Setup dev environment with Claude Code CLI.
* `make setup_dev_ollama`: Setup dev environment with Ollama local LLM.

### Running the Application

* `make run_cli`: Run the CLI application.
* `make run_cli ARGS="--help"`: Run CLI with specific arguments.
* `make run_gui`: Run the Streamlit GUI.

### Testing and Code Quality

Testing is managed by **pytest** and orchestrated via the `Makefile`.

* `make test_all`: Run all tests with pytest.
* `make coverage_all`: Run tests and generate a coverage report.
* `make ruff`: Format code and fix linting issues with Ruff.
* `make type_check`: Run mypy static type checking on `src/app/`.

### Single Test Execution

To run a specific test file or function, use `uv run pytest` directly:

* `uv run pytest tests/test_specific_file.py`
* `uv run pytest tests/test_specific_file.py::test_function`

## Common Development Patterns

### Structured Data and Configuration

* **Pydantic Models**: All data structures for agent inputs, outputs, and configurations are strictly defined using Pydantic models in `src/app/config/data_models.py`. **Always use or update these models** when modifying data flows to ensure type safety.
* **Configuration Files**: Agent prompts and provider settings are managed in `src/app/config/config_chat.json`. The system supports OpenAI-compatible inference endpoints.

### Error Handling

* Use the predefined error message functions from `src/app/utils/error_messages.py` for consistency. Add new error types or messages to this file as needed.

### Code Organization

* The Python code follows a modular structure within `src/app/`, separating `agents`, `config`, `evals`, and `utils`.
* The Streamlit GUI code is organized by feature under `src/gui/`, with separate directories for `components`, `config`, and `pages`.

## Code Review & PR Guidelines

### PR Requirements

* **Title Format**: Commit messages and PR titles must follow the **Conventional Commits** specification, as outlined in the `.gitmessage` template. Start the title with one of:
  * `feat:` (new feature)
  * `fix:` (bug fix)
  * `docs:` (documentation changes)
  * `style:` (formatting, missing semi colons, etc;)
  * `refactor:` (refactoring production code)
  * `test:` (adding or refactoring tests)
  * `chore:` (updating grunt tasks etc; no production code change)
* Provide detailed PR summaries including the purpose of the changes and the testing performed.

### Pre-commit Checklist

1. Run the linter and formatter: `make ruff`.
2. Ensure all tests pass: `make test_all`.
3. Ensure static type checks pass: `make type_check`.
4. Update documentation as described below.

### Documentation

* Update this `AGENTS.md` file when introducing new patterns or concepts.
* Add and update docstrings to all files, classes, methods, function and data classes you create or change. Because the documentation site is built using **MkDocs** and is automatically deployed via a GitHub Actions workflow.
* Document any significant architectural decisions into `docs/ADR.md`. If not present, create it.
* Document all significant changes, features, and bug fixes in `docs/CHANGELOG.md`.

## Requests to Humans

This section contains a list of questions, clarifications, or tasks that AI agents wish to have humans complete. If something doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add to this list.

* [ ] The `agent_system.py` module has a `NotImplementedError` for streaming with Pydantic model outputs. Please clarify the intended approach for streaming structured data.
* [ ] The `llm_model_funs.py` module has `NotImplementedError` for the Gemini and HuggingFace providers. Please provide the correct implementation or remove them if they are not supported.
* [ ] The `agent_system.py` module contains a `FIXME` note regarding the use of a try-catch context manager. Please review and implement the intended error handling.
* [ ] Add TypeScript testing guidelines (if a TypeScript frontend is planned for the future).
