# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Run `make help` to see all available recipes.


.SILENT:
.ONESHELL:
.PHONY: all setup_prod setup_dev setup_prod_ollama setup_dev_ollama setup_ollama start_ollama stop_ollama clean_ollama ruff run_cli run_gui run_profile test_all coverage_all type_check help
# .DEFAULT: setup_dev_ollama
.DEFAULT_GOAL := setup_dev_ollama

SRC_PATH := src
APP_PATH := $(SRC_PATH)/app
APP_CFG_FILE := $(APP_PATH)/config.json
SL_GUI_PATH := $(SRC_PATH)/streamlit.py
OLLAMA_SETUP_URL := https://ollama.com/install.sh

setup_prod: ## Install uv and deps, Download and start Ollama 
	echo "Setting up tools..."
	pip install uv -q
	uv sync --frozen

setup_dev: ## Install uv and deps, Download and start Ollama 
	echo "Setting up tools..."
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

# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
setup_ollama: ## Download Ollama, script does start local Ollama server
	echo "Downloading Ollama binary... Using '$(OLLAMA_SETUP_URL)'."
	# script does start server but not consistently
	curl -fsSL $(OLLAMA_SETUP_URL) | sh
	model_name=$$(jq -r '.providers.ollama.model_name' $(APP_CFG_FILE))
	echo "Pulling model '$${model_name}' ..."
	ollama pull $$model_name

start_ollama: ## Start local Ollama server, default 127.0.0.1:11434
	ollama serve

stop_ollama: ## Stop local Ollama server
	echo "Stopping Ollama server..."
	pkill ollama

clean_ollama: ## Remove local Ollama from system
	echo "Searching for Ollama binary..."
	for BINDIR in /usr/local/bin /usr/bin /bin; do
		if echo $$PATH | grep -q $$BINDIR; then
			echo "Ollama binary found in '$$BINDIR'"
			BIN="$$BINDIR/ollama"
			break
		fi
	done
	@echo "Cleaning up..."
	rm -f $(BIN)

ruff: ## Lint: Format and check with ruff
	uv run ruff format
	uv run ruff check --fix

run_cli: ## Run app on CLI only
	path=$$(echo "$(APP_PATH)" | tr '/' '.')
	uv run python -m $${path}.main

run_gui: ## Run app with Streamlit GUI
	uv run streamlit run $(SL_GUI_PATH)

run_profile: ## Profile app with scalene
	uv run scalene --outfile \
		"$(APP_PATH)/scalene-profiles/profile-$(date +%Y%m%d-%H%M%S)" \
		"$(APP_PATH)/main.py"

test_all: ## Run all tests
	uv run pytest
	
coverage_all: ## Get test coverage
	uv run coverage run -m pytest || true
	uv run coverage report -m

type_check: ## Check for static typing errors
	uv run mypy $(APP_PATH)

help:
	@echo "Usage: make [recipe]"
	@echo "Recipes:"
	@awk '/^[a-zA-Z0-9_-]+:.*?##/ {
		helpMessage = match($$0, /## (.*)/)
		if (helpMessage) {
			recipe = $$1
			sub(/:/, "", recipe)
			printf "  \033[36m%-20s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH)
		}
	}' $(MAKEFILE_LIST)
