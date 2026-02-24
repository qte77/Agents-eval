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
CC_STREAMS_PATH = f"{LOGS_BASE_PATH}/cc_streams"
DATASETS_CONFIG_FILE = "config_datasets.json"
RESULTS_PATH = "results"
DATASETS_PEERREAD_PATH = f"{DATASETS_PATH}/peerread"
MAS_REVIEWS_PATH = f"{RESULTS_PATH}/MAS_reviews"
REVIEW_PROMPT_TEMPLATE = "review_template.md"
DEFAULT_REVIEW_PROMPT_TEMPLATE = "Generate a structured peer review for paper '{paper_id}'."
