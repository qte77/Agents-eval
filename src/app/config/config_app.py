"""Configuration constants for the application."""

# MARK: chat env
API_SUFFIX = "_API_KEY"
CHAT_DEFAULT_PROVIDER = "github"


# MARK: project
PROJECT_NAME = "rd-mas-example"


# MARK: paths, files
_OUTPUT_BASE = "_Agents-eval"
CHAT_CONFIG_FILE = "config_chat.json"
CONFIGS_PATH = "config"
DATASETS_PATH = f"{_OUTPUT_BASE}/datasets"
LOGS_PATH = f"{_OUTPUT_BASE}/logs"
DATASETS_CONFIG_FILE = "config_datasets.json"
OUTPUT_PATH = f"{_OUTPUT_BASE}/output"
RUNS_PATH = f"{OUTPUT_PATH}/runs"
MAS_RUNS_PATH = f"{RUNS_PATH}/mas"
CC_RUNS_PATH = f"{RUNS_PATH}/cc"
DATASETS_PEERREAD_PATH = f"{DATASETS_PATH}/peerread"
TRACES_DB_FILE = "traces.db"
REVIEW_PROMPT_TEMPLATE = "review_template.md"
DEFAULT_REVIEW_PROMPT_TEMPLATE = "Generate a structured peer review for paper '{paper_id}'."
