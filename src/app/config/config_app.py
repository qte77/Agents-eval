"""Configuration constants for the application."""

# MARK: chat env
API_SUFFIX = "_API_KEY"
CHAT_DEFAULT_PROVIDER = "github"


# MARK: project
PROJECT_NAME = "rd-mas-example"


# MARK: paths, files
CHAT_CONFIG_FILE = "config_chat.json"
LOGS_PATH = "logs/Agent_evals"
CONFIGS_PATH = "config"
DATASETS_PATH = "datasets"
DATASETS_CONFIG_FILE = "config_datasets.json"
DATASETS_PEERREAD_PATH = f"{DATASETS_PATH}/peerread"
MAS_REVIEWS_PATH = f"{DATASETS_PEERREAD_PATH}/MAS_reviews"
REVIEW_PROMPT_TEMPLATE = "review_template.md"
