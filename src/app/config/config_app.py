"""Configuration constants for the application."""

# MARK: chat env
API_SUFFIX = "_API_KEY"
CHAT_DEFAULT_PROVIDER = "github"


# MARK: project
PROJECT_NAME = "rd-mas-example"


# MARK: paths, files
CHAT_CONFIG_FILE = "config_chat.json"
CONFIGS_PATH = "config"
DATASETS_PATH = "datasets"
LOGS_BASE_PATH = "logs/Agent_evals"
LOGS_PATH = f"{LOGS_BASE_PATH}/logs"
DATASETS_CONFIG_FILE = "config_datasets.json"
OUTPUT_PATH = "output"
DATASETS_PEERREAD_PATH = f"{DATASETS_PATH}/peerread"
REVIEW_PROMPT_TEMPLATE = "review_template.md"
DEFAULT_REVIEW_PROMPT_TEMPLATE = "Generate a structured peer review for paper '{paper_id}'."
