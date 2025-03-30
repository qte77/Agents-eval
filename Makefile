
OLLAMA_SETUP := https://ollama.com/install.sh

.PHONY: all

# Default target
all: setup_dev_ollama

setup_prod: ## Install uv and deps, Download and start Ollama 
	@echo "Setting up tools..."
	@pip install uv
	@uv sync --frozen

setup_dev: ## Install uv and deps, Download and start Ollama 
	@echo "Setting up tools..."
	@pip install uv
	@uv sync --all-groups --frozen

setup_prod_ollama:
	@$(MAKE) setup_prod
	@$(MAKE) setup_ollama
	@$(MAKE) start_ollama

setup_dev_ollama:
	@$(MAKE) setup_dev
	@$(MAKE) setup_ollama
	@$(MAKE) start_ollama

# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
setup_ollama: ## Download Ollama, script does start local Ollama server
	@echo "Downloading Ollama binary... Using '$(OLLAMA_SETUP)'."
	# script does start server but not consistently
	@curl -fsSL $(OLLAMA_SETUP) | sh

start_ollama: ## Start local Ollama server, default 127.0.0.1:11434
	@ollama serve

stop_ollama: ## Stop local Ollama server
	@echo "Stopping Ollama server..."
	@pkill ollama

clean_ollama: ## Remove local Ollama from system
	@echo "Searching for Ollama binary..."
	@for BINDIR in /usr/local/bin /usr/bin /bin; do \
		if echo $$PATH | grep -q $$BINDIR; then \
			echo "Ollama binary found in '$$BINDIR'"; \
			BIN="$$BINDIR/ollama"; \
			break; \
		fi; \
	done
	@echo "Cleaning up..."
	@rm -f $(BIN)

ruff: ## Lint: Format and check with ruff
	@uv run ruff format
	@uv run ruff check --fix

run_cli: ## Run app on CLI only
	@uv run python -m src main

run_gui: ## Run app with Streamlit GUI
	@uv run streamlit run streamlit.py

run_profile: ## Profile app with scalene
	@uv run scalene --outfile "src/scalene-profiles/profile-$(date +%Y%m%d-%H%M%S)" "src/main.py"

test_all: ## Run all tests
	@uv run pytest
	
coverage_all: ## Get test coverage
	@uv run coverage run -m pytest || true
	@uv run coverage report -m

type_check: ## Check for static typing errors
	@uv run mypy src

help:
	@echo "Usage: make [recipe]"
	@echo "Recipes:"
	@awk '/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			recipe = $$1; \
			sub(/:/, "", recipe); \
			printf "  \033[36m%-20s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH); \
		} \
	}' $(MAKEFILE_LIST)
