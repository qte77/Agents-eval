# Default paths

## App

- `APP_PATH = src/app`: The core application logic. This is where most of your work will be.
- `CONFIG_PATH = ${APP_PATH}/config`: Contains configuration files to define system behavior before execution.
- `DATAMODELS_PATH = ${APP_PATH}/datamodels`: Contains **Pydantic** datamodels to evaluate types in run time and define data contracts. These are critical files for understanding data flow.
- `DATASETS_PATH = src/datasets`: Contains the datasets for the benchmarks
- `DATASETS_PY_PATH = ${APP_PATH}/datasets`: Contains files managing datasets to evaluate the MAS with.
- `TEST_PATH = tests/`: Contains all tests for the project.

### Important files

- `${APP_PATH}/main.py`: The main entry point for the CLI application.
- `${APP_PATH}/agents/agent_system.py`: Defines the multi-agent system, their interactions, and orchestration. **This is the central logic for agent behavior.**
- `${APP_PATH}/evals/metrics.py`: Implements the evaluation metrics.
- `${APP_PATH}/utils/error_messages.py`: Predefined error message functions.
- `${APP_PATH}/src/gui/`: Contains the source code for the Streamlit GUI.
- `${CONFIG_PATH}/config_chat.json`: Holds provider settings and system prompts for agents
- `${CONFIG_PATH}/config_eval.json`: Defines evaluation metrics and their weights.

## Context

- `AGENTSMD_PATH`: Contains the main context for cading agents.
- `CONTEXT_PATH = context`: Contains auxiliary context for coding agents.
- `CTX_CONFIG_PATH = ${CONTEXT_PATH}/config`
- `CTX_EXAMPLES_PATH = ${CONTEXT_PATH}/examples`
- `CTX_FEATURES_PATH = ${CONTEXT_PATH}/features`
- `CTX_LOGS_PATH = ${CONTEXT_PATH}/logs`
- `CTX_FRP_PATH = ${CONTEXT_PATH}/FRPs`
- `CTX_TEMPLATES_PATH = ${CONTEXT_PATH}/templates`

## Project

- `DOCS_PATH = docs`: Contains auxiliary files for project documentation, including the Product Requirements Document (`PRD.md`) and architecture model visualizations.

### Important files

- `ADR_PATH = ${DOCS_PATH}/ADR.md`: Contains data explaining Architecture Decision Records
- `CHANGELOG_PATH = CHANGELOG.md`: Contains the most important changes made in each version of the project.
- `LLMSTXT_PATH = ${DOCS_PATH}/llms.txt`: Contains the flattened project, i.e., the structure and content of the project in one text file to be ingested by LLMs. Might not reflect the current project state depending on update strategy.
- `PRD_PATH = ${DOCS_PATH}/PRD.md`: Contains the product requirements definitions for this project.
- `PROJECT_REQUIREMENTS = pyproject.toml`: Defines meta data like package name, dependencies and tool settings.
