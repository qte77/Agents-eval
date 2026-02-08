# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: setup_prod setup_dev setup_devc setup_devc_full setup_prod_ollama setup_dev_ollama setup_devc_ollama setup_devc_ollama_full setup_claude_code setup_sandbox setup_plantuml setup_pdf_converter setup_markdownlint setup_ollama clean_ollama setup_dataset_sample setup_dataset_full dataset_get_smallest start_ollama stop_ollama run_puml_interactive run_puml_single run_pandoc run_markdownlint run_cli run_gui run_profile ruff ruff_tests complexity test_all test_quick test_coverage type_check validate quick_validate output_unset_app_env_sh setup_opik setup_opik_env start_opik stop_opik clean_opik status_opik ralph_userstory ralph_prd_md ralph_prd_json ralph_init ralph_run ralph_status ralph_clean ralph_reorganize help
# .DEFAULT: setup_dev_ollama
.DEFAULT_GOAL := help

SRC_PATH := src
APP_PATH := $(SRC_PATH)/app
CLI_PATH := $(SRC_PATH)/run_cli.py
CONFIG_PATH := $(APP_PATH)/config
GUI_PATH_ST := $(SRC_PATH)/run_gui.py
CHAT_CFG_FILE := $(CONFIG_PATH)/config_chat.json
OLLAMA_SETUP_URL := https://ollama.com/install.sh
OLLAMA_MODEL_NAME := $$(jq -r '.providers.ollama.model_name' $(CHAT_CFG_FILE))
PLANTUML_CONTAINER := plantuml/plantuml:latest
PLANTUML_SCRIPT := scripts/generate-plantuml-png.sh
PANDOC_SCRIPT := scripts/run-pandoc.sh
PDF_CONVERTER_SCRIPT := scripts/setup-pdf-converter.sh
PANDOC_PARAMS := --toc --toc-depth=2 -V geometry:margin=1in -V documentclass=report --pdf-engine=pdflatex
PANDOC_TITLE_FILE := 01_titel_abstrakt.md


# MARK: setup


setup_prod:  ## Install uv and deps
	echo "Setting up prod environment ..."
	pip install uv -q
	uv sync --frozen

setup_dev:  ## Install uv and deps, claude code, mdlint, plantuml
	echo "Setting up dev environment ..."
	pip install uv -q
	uv sync --all-groups
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_markdownlint
	$(MAKE) -s setup_plantuml

setup_devc:  ## Setup dev environment with sandbox
	$(MAKE) -s setup_sandbox
	$(MAKE) -s setup_dev
	
setup_devc_full: ## Complete dev setup including sandbox and Opik tracing stack
	$(MAKE) -s setup_devc
	$(MAKE) -s setup_opik

setup_prod_ollama:  ## Install uv and deps, Download and start Ollama 
	$(MAKE) -s setup_prod
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_dev_ollama:  ## Setup dev environment with ollama
	$(MAKE) -s setup_dev
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_devc_ollama:  ## Setup dev environment with ollama and sandbox
	$(MAKE) -s setup_devc
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_devc_ollama_full:  ## Complete dev setup including Ollama, sandbox and Opik tracing stack
	$(MAKE) -s setup_devc
	$(MAKE) -s setup_ollama
	$(MAKE) -s setup_opik
	$(MAKE) -s start_ollama

setup_claude_code:  ## Setup claude code CLI
	echo "Setting up Claude Code CLI ..."
	cp -r .claude/.claude.json ~/.claude.json
	curl -fsSL https://claude.ai/install.sh | bash
	echo "Claude Code CLI version: $$(claude --version)"

setup_sandbox:  ## Install sandbox deps (bubblewrap, socat) for Linux/WSL2
	# Required for Claude Code sandboxing on Linux/WSL2:
	# - bubblewrap: Provides filesystem and process isolation
	# - socat: Handles network socket communication for sandbox proxy
	# Without these, sandbox falls back to unsandboxed execution (security risk)
	# https://code.claude.com/docs/en/sandboxing
	# https://code.claude.com/docs/en/settings#sandbox-settings
	# https://code.claude.com/docs/en/security
	echo "Installing sandbox dependencies ..."
	if command -v apt-get > /dev/null; then \
		sudo apt-get update -qq && sudo apt-get install -y bubblewrap socat; \
	elif command -v dnf > /dev/null; then \
		sudo dnf install -y bubblewrap socat; \
	else \
		echo "Unsupported package manager. Install bubblewrap and socat manually."; \
		exit 1; \
	fi
	echo "Sandbox dependencies installed."

setup_plantuml:  ## Setup PlantUML with docker, $(PLANTUML_SCRIPT) and $(PLANTUML_CONTAINER)
	chmod +x $(PLANTUML_SCRIPT)
	if ! command -v plantuml >/dev/null 2>&1; then
		echo "Setting up PlantUML ..."
		sudo apt-get -yyqq update
		sudo apt-get -yyqq install plantuml graphviz
	else
		echo "PlantUML already installed"
	fi
	plantuml -version | grep "PlantUML version"

setup_pdf_converter:  ## Setup PDF converter tools. Usage: make setup_pdf_converter CONVERTER=pandoc | For help: make setup_pdf_converter HELP
	if [ -n "$(HELP)" ] || [ "$(origin HELP)" = "command line" ]; then
		$(PDF_CONVERTER_SCRIPT) help
	else
		chmod +x $(PDF_CONVERTER_SCRIPT)
		$(PDF_CONVERTER_SCRIPT) "$(CONVERTER)"
	fi

setup_markdownlint:  ## Setup markdownlint CLI, node.js and npm have to be present
	echo "Setting up markdownlint CLI ..."
	npm install -gs markdownlint-cli
	echo "markdownlint version: $$(markdownlint --version)"

# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
setup_ollama:  ## Download Ollama, script does start local Ollama server
	echo "Downloading Ollama binary ... Using '$(OLLAMA_SETUP_URL)'."
	# script does start server but not consistently
	curl -fsSL $(OLLAMA_SETUP_URL) | sh
	echo "Pulling model '$(OLLAMA_MODEL_NAME)' ..."
	ollama pull $(OLLAMA_MODEL_NAME)

clean_ollama:  ## Remove local Ollama from system
	echo "Searching for Ollama binary ..."
	for BINDIR in /usr/local/bin /usr/bin /bin; do
		if echo $$PATH | grep -q $$BINDIR; then
			echo "Ollama binary found in '$${BINDIR}'"
			BIN="$$BINDIR/ollama"
			break
		fi
	done
	echo "Cleaning up ..."
	rm -f $(BIN)

setup_dataset_sample:  ## Download small sample of PeerRead dataset
	echo "Downloading small sample of PeerRead dataset ..."
	$(MAKE) -s run_cli ARGS=--download-peerread-samples-only
	$(MAKE) -s dataset_get_smallest

setup_dataset_full:  ## Download full PeerRead dataset
	echo "Downloading full PeerRead dataset ..."
	$(MAKE) -s run_cli ARGS=--download-peerread-full-only
	$(MAKE) -s dataset_get_smallest

dataset_get_smallest:
	SMALLEST_N=10
	DATASETS_PATH='datasets/peerread'
	echo "Finding smallest $${SMALLEST_N} parsed PDFs in $${DATASETS_PATH}..."
	find $$DATASETS_PATH -path "*/parsed_pdfs/*.json" \
		-type f -printf '%s %p\n' 2>/dev/null | sort -n | head -$$SMALLEST_N


# MARK: run ollama


start_ollama:  ## Start local Ollama server, default 127.0.0.1:11434
	ollama serve

stop_ollama:  ## Stop local Ollama server
	echo "Stopping Ollama server ..."
	pkill ollama


# MARK: run plantuml


run_puml_interactive:  ## Generate a themed diagram from a PlantUML file interactively.
	# https://github.com/plantuml/plantuml-server
	# plantuml/plantuml-server:tomcat
	docker run -d -p 8080:8080 "$(PLANTUML_CONTAINER)"

run_puml_single:  ## Generate a themed diagram from a PlantUML file.
	$(PLANTUML_SCRIPT) "$(INPUT_FILE)" "$(STYLE)" "$(OUTPUT_PATH)" \
		"$(CHECK_ONLY)" "$(PLANTUML_CONTAINER)"


# MARK: run pandoc


run_pandoc:  ## Convert MD to PDF using pandoc. Usage: dir=docs/en && make run_pandoc INPUT_FILES="$$(printf '%s\\036' $$dir/*.md)" OUTPUT_FILE="$$dir/report.pdf" TITLE_PAGE="$$dir/title.tex" TOC_TITLE="ToC" LANGUAGE="en-US" NUMBER_SECTIONS="true" | Help: make run_pandoc HELP=1
	if [ -n "$(HELP)" ]; then
		$(PANDOC_SCRIPT) help
	else
		chmod +x $(PANDOC_SCRIPT)
		$(PANDOC_SCRIPT) "$(INPUT_FILES)" "$(OUTPUT_FILE)" \
			"$(TITLE_PAGE)" "$(TEMPLATE)" "$(FOOTER_TEXT)" \
			"$(TOC_TITLE)" "$(LANGUAGE)" "$(NUMBER_SECTIONS)"
	fi


# MARK: run markdownlint


run_markdownlint:  ## Lint markdown files. Usage from root dir: make run_markdownlint INPUT_FILES="docs/**/*.md"
	if [ -z "$(INPUT_FILES)" ]; then
		echo "Error: No input files specified. Use INPUT_FILES=\"docs/**/*.md\""
		exit 1
	fi
	markdownlint $(INPUT_FILES) --fix


# MARK: run app


run_cli:  ## Run app on CLI only. Usage: make run_cli ARGS="--help" or make run_cli ARGS="--download-peerread-samples-only"
	PYTHONPATH=$(SRC_PATH) uv run python $(CLI_PATH) $(ARGS)

run_gui:  ## Run app with Streamlit GUI
	PYTHONPATH=$(SRC_PATH) uv run streamlit run $(GUI_PATH_ST)

run_profile:  ## Profile app with scalene
	uv run scalene --outfile \
		"$(APP_PATH)/scalene-profiles/profile-$$(date +%Y%m%d-%H%M%S)" \
		"$(APP_PATH)/main.py"


# MARK: Sanity


ruff:  ## Lint: Format and check with ruff (src only)
	uv run ruff format --exclude tests
	uv run ruff check --fix --exclude tests
	
ruff_tests:  ## Lint: Format and fix tests with ruff
	uv run ruff format tests
	uv run ruff check tests --fix



complexity:  ## Check cognitive complexity with complexipy
	uv run complexipy

test_all:  ## Run all tests
	uv run pytest

test_quick:  ## Quick test - rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test_coverage:  ## Run tests with coverage threshold (configured in pyproject.toml)
	echo "Running tests with coverage gate (fail_under% defined in pyproject.toml)..."
	uv run pytest --cov

type_check:  ## Check for static typing errors
	uv run pyright src

validate:  ## Complete pre-commit validation sequence
	set -e
	echo "Running complete validation sequence..."
	$(MAKE) -s ruff
	$(MAKE) -s ruff_tests
	$(MAKE) -s type_check
	$(MAKE) -s complexity
	$(MAKE) -s test_coverage
	echo "Validation completed successfully"

quick_validate:  ## Fast development cycle validation
	echo "Running quick validation ..."
	$(MAKE) -s ruff
	$(MAKE) -s type_check
	echo "Quick validation completed (check output for any failures)"

output_unset_app_env_sh:  ## Unset app environment variables
	uf="./unset_env.sh"
	echo "Outputing '$${uf}' ..."
	printenv | awk -F= '/_API_KEY=/ {print "unset " $$1}' > $$uf


# MARK: opik

setup_opik:  ## Complete Opik setup (start services + configure environment)
	echo "Setting up Opik tracing stack..."
	$(MAKE) start_opik
	echo "Waiting for services to be healthy..."
	sleep 20
	$(MAKE) setup_opik_env
	echo "Opik setup complete!"

setup_opik_env:  ## Setup Opik environment variables for local development
	echo "Setting up Opik environment variables ..."
	echo "export OPIK_URL_OVERRIDE=http://localhost:8080" >> ~/.bashrc  # do not send to comet.com/api
	echo "export OPIK_WORKSPACE=peerread-evaluation" >> ~/.bashrc
	echo "export OPIK_PROJECT_NAME=peerread-evaluation" >> ~/.bashrc
	echo "Environment variables added to ~/.bashrc"
	echo "Run: source ~/.bashrc"

start_opik:  ## Start local Opik tracing with ClickHouse database
	# https://github.com/comet-ml/opik/blob/main/deployment/docker-compose/docker-compose.yaml
	# https://www.comet.com/docs/opik/self-host/local_deployment/
	echo "Starting Opik stack with ClickHouse ..."
	docker-compose -f docker-compose.opik.yaml up -d
	echo "Frontend: http://localhost:5173"
	echo "Backend API: http://localhost:8080"
	echo "ClickHouse: http://localhost:8123"

stop_opik:  ## Stop local Opik tracing stack
	echo "Stopping Opik stack ..."
	docker-compose -f docker-compose.opik.yaml down

clean_opik:  ## Stop Opik and remove all trace data (WARNING: destructive)
	echo "WARNING: This will remove all Opik trace data!"
	echo "Press Ctrl+C to cancel, Enter to continue..."
	read
	docker-compose -f docker-compose.opik.yaml down -v

status_opik:  ## Check Opik services health status
	echo "Checking Opik services status ..."
	docker-compose -f docker-compose.opik.yaml ps
	echo "API Health:"
	curl -f http://localhost:8080/health-check 2>/dev/null && \
		echo "Opik API healthy" || echo "Opik API not responding"
	echo "ClickHouse:"
	curl -s http://localhost:8123/ping 2>/dev/null && \
		echo "ClickHouse healthy" || echo "ClickHouse not responding"


# MARK: ralph


ralph_userstory:  ## [Optional] Create UserStory.md interactively. Usage: make ralph_userstory
	echo "Creating UserStory.md through interactive Q&A ..."
	claude -p "/generating-interactive-userstory-md"

ralph_prd_md:  ## [Optional] Generate PRD.md from UserStory.md
	echo "Generating PRD.md from UserStory.md ..."
	claude -p "/generating-prd-md-from-userstory-md"

ralph_prd_json:  ## [Optional] Generate PRD.json from PRD.md
	echo "Generating PRD.json from PRD.md ..."
	claude -p "/generating-prd-json-from-prd-md"

ralph_init:  ## Initialize Ralph loop environment
	echo "Initializing Ralph loop environment ..."
	bash ralph/scripts/init.sh

ralph_run:  ## Run Ralph autonomous development loop (MAX_ITERATIONS=N, MODEL=sonnet|opus|haiku)
	echo "Starting Ralph loop ..."
	RALPH_MODEL=$(MODEL) MAX_ITERATIONS=$(MAX_ITERATIONS) bash ralph/scripts/ralph.sh

ralph_status:  ## Show Ralph loop progress and status
	echo "Ralph Loop Status"
	echo "================="
	if [ -f ralph/docs/prd.json ]; then
		total=$$(jq '.stories | length' ralph/docs/prd.json)
		passing=$$(jq '[.stories[] | select(.passes == true)] | length' ralph/docs/prd.json)
		echo "Stories: $$passing/$$total completed"
		echo ""
		echo "Incomplete stories:"
		jq -r '.stories[] | select(.passes == false) | "  - [\(.id)] \(.title)"' ralph/docs/prd.json
	else
		echo "prd.json not found. Run 'make ralph_init' first."
	fi

ralph_clean:  ## Reset Ralph state (WARNING: removes prd.json and progress.txt)
	echo "WARNING: This will reset Ralph loop state!"
	echo "Press Ctrl+C to cancel, Enter to continue..."
	read
	rm -f ralph/docs/prd.json ralph/docs/progress.txt
	echo "Ralph state cleaned. Run 'make ralph_init' to reinitialize."

ralph_reorganize:  ## Archive current PRD and start new iteration. Usage: make ralph_reorganize NEW_PRD=path/to/new.md [VERSION=2]
	if [ -z "$(NEW_PRD)" ]; then
		echo "Error: NEW_PRD parameter required"
		echo "Usage: make ralph_reorganize NEW_PRD=docs/PRD-New.md [VERSION=2]"
		exit 1
	fi
	VERSION_ARG=""
	if [ -n "$(VERSION)" ]; then
		VERSION_ARG="-v $(VERSION)"
	fi
	bash ralph/scripts/reorganize_prd.sh $$VERSION_ARG $(NEW_PRD)


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
