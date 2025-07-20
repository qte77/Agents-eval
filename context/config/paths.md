# Default paths

## Context

- `CONTEXT_PATH = context`
- `CONFIG_PATH = ${CONTEXT_PATH}/config`
- `EXAMPLES_PATH = ${CONTEXT_PATH}/examples`
- `FEATURES_PATH = ${CONTEXT_PATH}/features`
- `LOGS_CONTEXT_PATH = ${CONTEXT_PATH}/templates`
- `PRP_PATH = ${CONTEXT_PATH}/PRPs`
- `TEMPLATES_PATH = ${CONTEXT_PATH}/templates`

## App

- `APP_PATH = src/app`: The core application logic. This is where most of your work will be.
- `CONFIG_PATH = ${APP_PATH}/config`: Contains configuration files to define system behavior before execution.
- `DATAMODELS_PATH = ${APP_PATH}/datamodels`: Contains **Pydantic** datamodels to evaluate types in run time and define data contracts. These are critical files for understanding data flow.
- `DATASETS_PATH = ${APP_PATH}/datasets`: Contains datasets to evaluate the MAS with.
- `DOCS_PATH = docs`: Contains files aimed at documenting the project.
- `PROJECT_REQUIREMENTS = pyproject.toml`: Defines meta data like package name, dependencies and tool settings.
- `TEST_PATH = tests/`: Contains all tests for the project.

### Important files

- `${APP_PATH}/main.py`: The main entry point for the CLI application.
- `${APP_PATH}/agents/agent_system.py`: Defines the multi-agent system, their interactions, and orchestration. **This is the central logic for agent behavior.**
- `${APP_PATH}/config/config_chat.json`: Holds provider settings and system prompts for agents
- `${APP_PATH}/config/config_eval.json`: Defines evaluation metrics and their weights.
- `${APP_PATH}/docs/`: Contains project documentation, including the Product Requirements Document (`PRD.md`) and the C4 architecture model.
- `${APP_PATH}/evals/metrics.py`: Implements the evaluation metrics.
- `${APP_PATH}/utils/error_messages.py`: Predefined error message functions.
- `${APP_PATH}/src/gui/`: Contains the source code for the Streamlit GUI.
