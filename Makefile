# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: all setup_prod setup_dev setup_prod_ollama setup_dev_ollama setup_dev_claude setup_claude_code setup_ollama start_ollama stop_ollama clean_ollama ruff run_cli run_gui run_profile prp_gen_claude prp_exe_claude test_all coverage_all type_check validate quick_validate output_unset_app_env_sh help
# .DEFAULT: setup_dev_ollama
.DEFAULT_GOAL := setup_dev_ollama

SRC_PATH := src
APP_PATH := $(SRC_PATH)/app
CLI_PATH := $(SRC_PATH)/run_cli.py
GUI_PATH_ST := $(SRC_PATH)/run_gui.py
CHAT_CFG_FILE := $(APP_PATH)/config_chat.json
OLLAMA_SETUP_URL := https://ollama.com/install.sh
OLLAMA_MODEL_NAME := $$(jq -r '.providers.ollama.model_name' $(CHAT_CFG_FILE))
PRP_DEF_PATH := /context/PRPs/features
PRP_CLAUDE_GEN_CMD := generate-prp
PRP_CLAUDE_EXE_CMD := execute-prp

# construct the full path to the PRP definition file
define CLAUDE_PRP_RUNNER
	echo "Starting Claude Code PRP runner ..."
	# 1. Extract arguments and validate that they are not empty.
	prp_file=$(firstword $(strip $(1)))
	cmd_prp=$(firstword $(strip $(2)))
	if [ -z "$${prp_file}" ]; then
		echo "Error: ARGS for PRP filename is empty. Please provide a PRP filename."
		exit 1
	fi
	if [ -z "$${cmd_prp}" ]; then
		echo "Error: ARGS for command is empty. Please provide a command."
		exit 2
	fi
	cmd_prp="/project:$${cmd_prp} $(PRP_DEF_PATH)/$${prp_file}"
	cmd_cost="/cost"
	echo "Executing command '$${cmd_prp}' ..."
	claude -p "$${cmd_prp}" 2>&1
	claude -p "$${cmd_cost}" 2>&1
endef


# MARK: setup


setup_prod:  ## Install uv and deps, Download and start Ollama 
	echo "Setting up prod environment ..."
	pip install uv -q
	uv sync --frozen

setup_dev:  ## Install uv and deps, Download and start Ollama 
	echo "Setting up dev environment ..."
	pip install uv -q
	uv sync --all-groups

setup_prod_ollama:
	$(MAKE) -s setup_prod
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_dev_ollama:
	$(MAKE) -s setup_dev
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_dev_claude:
	echo "Starting setup ..."
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_dev
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_gemini_cli

setup_claude_code:  ## Setup claude code CLI, node.js and npm have to be present
	echo "Setting up claude code ..."
	npm install -g @anthropic-ai/claude-code
	claude config set --global preferredNotifChannel terminal_bell
	echo "npm version: $$(npm --version)"
	claude --version

setup_gemini_cli:  ## Setup Gemini CLI, node.js and npm have to be present
	echo "Setting up Gemini CLI ..."
	npm install -g @google/gemini-cli
	echo "Gemini CLI version: $$(gemini --version)"

# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
setup_ollama:  ## Download Ollama, script does start local Ollama server
	echo "Downloading Ollama binary... Using '$(OLLAMA_SETUP_URL)'."
	# script does start server but not consistently
	curl -fsSL $(OLLAMA_SETUP_URL) | sh
	echo "Pulling model '$(OLLAMA_MODEL_NAME)' ..."
	ollama pull $(OLLAMA_MODEL_NAME)

clean_ollama:  ## Remove local Ollama from system
	echo "Searching for Ollama binary..."
	for BINDIR in /usr/local/bin /usr/bin /bin; do
		if echo $$PATH | grep -q $$BINDIR; then
			echo "Ollama binary found in '$$BINDIR'"
			BIN="$$BINDIR/ollama"
			break
		fi
	done
	echo "Cleaning up..."
	rm -f $(BIN)


# MARK: run ollama


start_ollama:  ## Start local Ollama server, default 127.0.0.1:11434
	ollama serve

stop_ollama:  ## Stop local Ollama server
	echo "Stopping Ollama server..."
	pkill ollama


# MARK: run


run_cli:  ## Run app on CLI only
	PYTHONPATH=$(SRC_PATH) uv run python $(CLI_PATH) $(ARGS)

run_gui:  ## Run app with Streamlit GUI
	PYTHONPATH=$(SRC_PATH) uv run streamlit run $(GUI_PATH_ST)

run_profile:  ## Profile app with scalene
	uv run scalene --outfile \
		"$(APP_PATH)/scalene-profiles/profile-$(date +%Y%m%d-%H%M%S)" \
		"$(APP_PATH)/main.py"


# MARK: context


prp_gen_claude:  ## generates the PRP from the file passed in ARGS
	$(call CLAUDE_PRP_RUNNER, $(ARGS), $(PRP_CLAUDE_GEN_CMD))

prp_exe_claude:  ## executes the PRP from the file passed in ARGS
	$(call CLAUDE_PRP_RUNNER, $(ARGS), $(PRP_CLAUDE_EXE_CMD))


# MARK: sanity


ruff:  ## Lint: Format and check with ruff
	uv run ruff format
	uv run ruff check --fix

test_all:  ## Run all tests
	uv run pytest

coverage_all:  ## Get test coverage
	uv run coverage run -m pytest || true
	uv run coverage report -m

type_check:  ## Check for static typing errors
	uv run pyright

validate:  ## Complete pre-commit validation sequence
	echo "Running complete validation sequence..."
	$(MAKE) -s ruff
	-$(MAKE) -s type_check
	-$(MAKE) -s test_all
	echo "Validation sequence completed (check output for any failures)"

quick_validate:  ## Fast development cycle validation
	echo "Running quick validation..."
	$(MAKE) -s ruff
	-$(MAKE) -s type_check
	echo "Quick validation completed (check output for any failures)"

output_unset_app_env_sh:  ## Unset app environment variables
	uf="./unset_env.sh"
	echo "Outputing '$${uf}' ..."
	printenv | awk -F= '/_API_KEY=/ {print "unset " $$1}' > $$uf


# MARK: help


help:  ## Displays this message with available recipes
	# TODO add stackoverflow source
	echo "Usage: make [recipe]"
	echo "Recipes:"
	awk '/^[a-zA-Z0-9_-]+:.*?##/ {
		helpMessage = match($$0, /## (.*)/)
		if (helpMessage) {
			recipe = $$1
			sub(/:/, "", recipe)
			printf "  \033[36m%-20s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH)
		}
	}' $(MAKEFILE_LIST)
