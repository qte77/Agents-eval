# Agent instructions for `Agents-eval` repository

As proposed by [agentsmd.net](https://agentsmd.net/) and used by [wandb weave AGENTS.md](https://github.com/wandb/weave/blob/master/AGENTS.md).

## Core Rules

* When you learn something new about the codebase or introduce a new concept, **update this file (`AGENTS.md`)** to reflect the new knowledge. This is YOUR FILE! It should grow and evolve with you.
* If there is something that doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add it to the **`Requests to Humans`** section below.
* Always follow the established coding patterns and conventions in the codebase, particularly the use of **Pydantic** for data contracts and the modular structure.
* Always document changes according to the **`Documentation`** section below.

## Development Setup

Your development environment should be set up automatically using the provided `Makefile`. This project uses **uv** for fast dependency management.

* To install all dependencies, including development tools, run: `make setup_dev`
* For specialized setups, you can use `make setup_dev_claude` or `make setup_dev_ollama`.
* If you encounter any setup issues:
  1. Check the `Makefile` for potential problems in the `setup_*` recipes.
  2. Update the `Makefile` with necessary fixes.
  3. Document any required manual steps in this section.

## Codebase Structure

### Main Components

* `src/app/`: The core application logic. This is where most of your work will be.
  * `main.py`: The main entry point for the CLI application.
  * `agents/agent_system.py`: Defines the multi-agent system, their interactions, and orchestration. **This is the central logic for agent behavior.**
  * `config/data_models.py`: Contains all **Pydantic** data models that define the data contracts for agent inputs, outputs, and configurations. This is a critical file for understanding data flow.
  * `config/config_chat.json`: Holds provider settings and system prompts for all agents.
  * `evals/metrics.py`: Implements the evaluation metrics used to assess agent performance.
* `src/gui/`: Contains the source code for the Streamlit GUI.
  * `run_gui.py`: The entry point for launching the GUI.
* `docs/`: Contains project documentation, including the Product Requirements Document (`PRD.md`) and the C4 architecture model.
* `tests/`: Contains all tests for the project, written using **pytest**.

## Python Testing Guidelines

### Test Framework

Testing is managed by **pytest** and orchestrated via the `Makefile`. Key commands include `make test_all` and `make coverage_all`.

### Running Tests

1. **Run all tests:** `make test_all`
2. **Run tests and generate a coverage report:** `make coverage_all`
3. **Run linting and formatting checks with Ruff:** `make ruff`
4. **Run static type checking with mypy:** `make type_check`

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
4. Update documentation in `docs/` if you have introduced new features or made significant changes.

## Common Development Patterns

### Code Organization

* The Python code follows a modular structure within `src/app/`, separating `agents`, `config`, `evals`, and `utils`.
* The Streamlit GUI code is organized by feature under `src/gui/`, with separate directories for `components`, `config`, and `pages`.

### Error Handling

* Use the predefined error message functions from `src/app/utils/error_messages.py` for consistency.
* Add new error types or messages to this file as needed.

### Structured Data and Configuration

* **Pydantic Models**: All data structures for agent inputs, outputs, and configurations are strictly defined using Pydantic models in `src/app/config/data_models.py`. **Always use or update these models** when modifying data flows.
* **Configuration Files**: Agent prompts and provider settings are managed in `src/app/config/config_chat.json`.

### Documentation

* Add end-user documentation to the `docs/` directory when creating new features. The documentation site is built using **MkDocs** and is automatically deployed via a GitHub Actions workflow (`generate-deploy-mkdocs-ghpages.yaml`).
* Update this `AGENTS.md` file when introducing new patterns or concepts.
* Document any significant architectural decisions or changes in the `docs/` directory.
* Document any significant changes, features, bug fixes, or improvements in the `docs/CHANGELOG.md` file. This helps keep track of the project's evolution and provides context for future developers.

## Requests to Humans

This section contains a list of questions, clarifications, or tasks that AI agents wish to have humans complete. If something doesn't make sense architecturally, from a developer experience standpoint, or product-wise, please add to this list.

* [ ] The `agent_system.py` module has a `NotImplementedError` for streaming with Pydantic model outputs. Please clarify the intended approach for streaming structured data.
* [ ] The `llm_model_funs.py` module has `NotImplementedError` for the Gemini and HuggingFace providers. Please provide the correct implementation or remove them if they are not supported.
* [ ] The `agent_system.py` module contains a `FIXME` note regarding the use of a try-catch context manager. Please review and implement the intended error handling.
* [ ] Add TypeScript testing guidelines (if a TypeScript frontend is planned for the future).
