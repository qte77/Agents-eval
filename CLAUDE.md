# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

- `make setup_dev` - Install uv and all dev dependencies
- `make setup_dev_claude` - Setup dev environment with Claude Code CLI
- `make setup_dev_ollama` - Setup dev environment with Ollama local LLM

### Running the Application

- `make run_cli` - Run the CLI application (`uv run python -m src.app.main`)
- `make run_cli ARGS="--help"` - Run CLI with arguments
- `make run_gui` - Run the Streamlit GUI (`uv run streamlit run src/run_gui.py`)

### Testing and Code Quality

- `make test_all` - Run all tests with pytest
- `make coverage_all` - Run tests with coverage report
- `make ruff` - Format code and fix linting issues with ruff
- `make type_check` - Run mypy static type checking on src/app/

### Single Test Execution

- `uv run pytest tests/test_specific_file.py` - Run specific test file
- `uv run pytest tests/test_specific_file.py::test_function` - Run specific test function

## Architecture Overview

This is a multi-agent evaluation system for assessing agentic AI systems. The project uses **PydanticAI** as the core framework for agent orchestration.

### Core Components

**Agent System** (`src/app/agents/agent_system.py`):

- Multi-agent orchestration with Manager, Researcher, Analyst, and Synthesizer agents
- Manager coordinates research and analysis tasks
- Researcher gathers data using DuckDuckGo search
- Analyst validates assumptions and conclusions
- Synthesizer formats scientific reports

**Configuration** (`src/app/config/`):

- `data_models.py` - Pydantic models for all data contracts (critical for understanding data flow)
- `config_chat.json` - Provider settings and system prompts for agents
- `config_eval.json` - Evaluation metrics and weights

**Evaluation** (`src/app/evals/metrics.py`):

- Metrics: planning_rational, task_success, tool_efficiency, coordination_quality, time_taken, text_similarity
- Each metric weighted equally (1/6) in baseline configuration

### Data Flow

1. User input → Manager Agent
2. Manager delegates to Researcher Agent (with DuckDuckGo search)
3. Researcher results → Analyst Agent for validation
4. Validated data → Synthesizer Agent for report generation
5. Results evaluated using configurable metrics

### Key Dependencies

- **PydanticAI**: Agent framework and orchestration
- **uv**: Fast Python dependency management
- **Streamlit**: GUI framework
- **Ruff**: Code formatting and linting
- **MyPy**: Static type checking

## Development Patterns

### Data Models

Always use or extend Pydantic models in `src/app/config/data_models.py` for any data structures. This ensures type safety and consistent data contracts across agents.

### Error Handling

Use predefined error functions from `src/app/utils/error_messages.py` for consistency.

### Configuration Management

Agent prompts and provider settings are in `config_chat.json`. The system supports OpenAI-compatible inference endpoints.

### Testing

Project uses pytest with specific configuration in `pyproject.toml`. Tests are in `tests/` directory with path configuration set to include `src/`.

## Important Notes

- Python 3.13 is required (`requires-python = "==3.13.*"`)
- The project uses uv for dependency management instead of pip/conda
- All agent interactions follow the PydanticAI framework patterns
- The system is designed for evaluation of agentic AI systems, not for production agent deployment
- There's an existing `AGENTS.md` file with additional agent-specific instructions that should be consulted for agent development patterns
