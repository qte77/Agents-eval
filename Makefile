# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: setup_prod setup_dev setup_devc setup_devc_full setup_prod_ollama setup_dev_ollama setup_devc_ollama setup_devc_ollama_full setup_claude_code setup_sandbox setup_plantuml setup_pdf_converter setup_markdownlint setup_jscpd setup_ollama clean_ollama setup_dataset_sample setup_dataset_full dataset_get_smallest quick_start start_ollama stop_ollama run_puml_interactive run_puml_single run_pandoc run_markdownlint writeup writeup_generate run_cli run_gui sweep cc_run_solo cc_collect_teams cc_run_teams run_profile ruff ruff_tests complexity duplication test_all test_quick test_coverage type_check validate quick_validate output_unset_app_env_sh setup_phoenix start_phoenix stop_phoenix status_phoenix ralph_userstory ralph_prd_md ralph_prd_json ralph_init ralph_run ralph_worktree ralph_stop ralph_status ralph_watch ralph_get_log ralph_clean help
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
PLANTUML_SCRIPT := scripts/writeup/generate-plantuml-png.sh
PANDOC_SCRIPT := scripts/writeup/run-pandoc.sh
PDF_CONVERTER_SCRIPT := scripts/writeup/setup-pdf-converter.sh
RALPH_TIMEOUT ?=
TEAMS ?= false
PHOENIX_CONTAINER_NAME := phoenix-tracing
PHOENIX_PORT := 6006
PHOENIX_GRPC_PORT := 4317
PHOENIX_IMAGE := arizephoenix/phoenix:latest
# write-up
BIBLIOGRAPHY :=
CSL :=
LIST_OF_FIGURES :=
LIST_OF_TABLES :=
UNNUMBERED_TITLE :=
# CC baselines
CC_SOLO_OUTPUT := logs/cc/solo
CC_TEAMS_OUTPUT := logs/cc/teams
CC_TIMEOUT ?= 300
CC_TEAMS_TIMEOUT ?= 600
CC_MODEL ?=
# writeup
WRITEUP_DIR ?= docs/write-up
WRITEUP_OUTPUT ?= $(WRITEUP_DIR)/writeup.pdf
WRITEUP_BIB ?= $(WRITEUP_DIR)/09a_bibliography.bib
WRITEUP_CSL ?= scripts/writeup/citation-styles/ieee.csl
WRITEUP_PUML_DIR := docs/arch_vis
SKIP_PUML ?=
SKIP_CONTENT ?= 1
WRITEUP_TIMEOUT ?= 600


# MARK: setup


setup_prod:  ## Install uv and deps
	echo "Setting up prod environment ..."
	pip install uv -q
	uv sync --frozen

setup_dev:  ## Install uv and deps, claude code, mdlint, jscpd, plantuml
	echo "Setting up dev environment ..."
	# sudo apt-get install -y gh
	pip install uv -q
	uv sync --all-groups
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_markdownlint
	$(MAKE) -s setup_jscpd
	$(MAKE) -s setup_plantuml

setup_devc:  ## Setup dev environment with sandbox
	$(MAKE) -s setup_sandbox
	$(MAKE) -s setup_dev
	
setup_devc_full: ## Complete dev setup including sandbox
	$(MAKE) -s setup_devc

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

setup_devc_ollama_full:  ## Complete dev setup including Ollama and sandbox
	$(MAKE) -s setup_devc
	$(MAKE) -s setup_ollama
	$(MAKE) -s start_ollama

setup_claude_code:  ## Setup claude code CLI
	echo "Setting up Claude Code CLI ..."
	cp -r .claude/.claude.json ~/.claude.json
	curl -fsSL https://claude.ai/install.sh | bash
	claude plugin marketplace add anthropics/claude-plugins-official
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
	if command -v apt-get > /dev/null; then
		sudo apt-get update -qq && sudo apt-get install -y bubblewrap socat
	elif command -v dnf > /dev/null; then
		sudo dnf install -y bubblewrap socat
	else
		echo "Unsupported package manager. Install bubblewrap and socat manually."
		exit 1
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

# TODO: evaluate Python-native alternative to markdownlint (pymarkdownlnt, mdformat) to reduce npm dependency
setup_markdownlint:  ## Setup markdownlint CLI, node.js and npm have to be present
	echo "Setting up markdownlint CLI ..."
	npm install -gs markdownlint-cli
	echo "markdownlint version: $$(markdownlint --version)"

setup_jscpd:  ## Setup jscpd copy-paste detector, node.js and npm have to be present
	echo "Setting up jscpd ..."
	npm install -gs jscpd
	echo "jscpd version: $$(jscpd --version)"
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

dataset_get_smallest:  ## Show N smallest papers by file size. Usage: make dataset_get_smallest N=5
	@find datasets/peerread -path "*/parsed_pdfs/*.json" \
		-type f -printf '%s %p\n' 2>/dev/null | sort -n | head -$(or $(N),10)


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


run_pandoc:  ## Convert MD to PDF using pandoc. Usage: dir=docs/en && make run_pandoc INPUT_FILES="$$(printf '%s\\036' $$dir/*.md)" OUTPUT_FILE="$$dir/report.pdf" [BIBLIOGRAPHY="$$dir/refs.bib"] [CSL="$$dir/style.csl"] | Help: make run_pandoc HELP=1
	if [ -n "$(HELP)" ]; then
		$(PANDOC_SCRIPT) help
	else
		chmod +x $(PANDOC_SCRIPT)
		$(PANDOC_SCRIPT) "$(INPUT_FILES)" "$(OUTPUT_FILE)" \
			"$(TITLE_PAGE)" "$(TEMPLATE)" "$(FOOTER_TEXT)" \
			"$(TOC_TITLE)" "$(LANGUAGE)" "$(NUMBER_SECTIONS)" \
			"$(BIBLIOGRAPHY)" "$(CSL)" \
			"$(LIST_OF_FIGURES)" "$(LIST_OF_TABLES)" "$(UNNUMBERED_TITLE)"
	fi


# Convenience wrapper: content generation (CC teams) + PlantUML regen + pandoc PDF build.
writeup:  ## Build writeup PDF. Usage: make writeup WRITEUP_DIR=docs/write-up/bs-new [LANGUAGE=de-DE] [SKIP_CONTENT=1] [SKIP_PUML=1]
	if [ -z "$(SKIP_CONTENT)" ]; then
		echo "=== Generating writeup content with Claude Code teams ==="
		$(MAKE) -s writeup_generate
	fi
	if [ -z "$(SKIP_PUML)" ]; then
		echo "=== Regenerating PlantUML diagrams ==="
		for f in $(WRITEUP_PUML_DIR)/*.plantuml $(WRITEUP_PUML_DIR)/*.puml; do
			[ -f "$$f" ] || continue
			echo "  Processing $$f ..."
			$(MAKE) -s run_puml_single INPUT_FILE="$$f" STYLE="light" OUTPUT_PATH="assets/images"
		done
	fi
	echo "=== Building writeup PDF ==="
	$(MAKE) -s run_pandoc \
		INPUT_FILES="$$(printf '%s\036' $(WRITEUP_DIR)/01_*.md $(WRITEUP_DIR)/0[2-8]_*.md $(WRITEUP_DIR)/09b_*.md $(WRITEUP_DIR)/10_*.md $(WRITEUP_DIR)/11_*.md)" \
		OUTPUT_FILE="$(WRITEUP_OUTPUT)" \
		BIBLIOGRAPHY="$(WRITEUP_BIB)" \
		CSL="$(WRITEUP_CSL)" \
		LANGUAGE="$(LANGUAGE)" \
		NUMBER_SECTIONS="true" \
		LIST_OF_FIGURES="true" \
		LIST_OF_TABLES="false" \
		UNNUMBERED_TITLE="true"
	echo "=== Writeup PDF: $(WRITEUP_OUTPUT) ==="

# Generate writeup content using CC teams + /generating-writeup skill.
writeup_generate:  ## Generate writeup markdown via CC teams. Usage: make writeup_generate WRITEUP_DIR=docs/write-up/bs-new [WRITEUP_TIMEOUT=600] [CC_MODEL=sonnet]
	echo "=== Generating writeup content (timeout: $(WRITEUP_TIMEOUT)s) ==="
	mkdir -p "$(WRITEUP_DIR)"
	CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 \
	timeout $(WRITEUP_TIMEOUT) claude -p \
		"/generating-writeup $(notdir $(WRITEUP_DIR)) IEEE -- Use agent teams for parallel chapter creation. Target: $(WRITEUP_DIR)" \
		--output-format stream-json --verbose \
		$(if $(CC_MODEL),--model $(CC_MODEL)) \
		> "$(WRITEUP_DIR)/generate.jsonl" 2>&1 \
		|| { EXIT_CODE=$$?; [ $$EXIT_CODE -eq 124 ] && echo "Content generation timed out after $(WRITEUP_TIMEOUT)s"; exit $$EXIT_CODE; }
	echo "=== Content generation complete. Output: $(WRITEUP_DIR)/generate.jsonl ==="


# MARK: run markdownlint


run_markdownlint:  ## Lint markdown files. Usage from root dir: make run_markdownlint INPUT_FILES="docs/**/*.md"
	if [ -z "$(INPUT_FILES)" ]; then
		echo "Error: No input files specified. Use INPUT_FILES=\"docs/**/*.md\""
		exit 1
	fi
	markdownlint $(INPUT_FILES) --fix


# MARK: run app


quick_start:  ## Download sample data and run evaluation on smallest paper
	echo "=== Quick Start: Download samples + evaluate smallest paper ==="
	if [ ! -d datasets/peerread ]; then
		$(MAKE) -s setup_dataset_sample
	else
		echo "PeerRead dataset already present, skipping download."
	fi
	PAPER_ID=$$($(MAKE) -s dataset_get_smallest N=1 \
		| awk '{print $$2}' | sed 's|.*/parsed_pdfs/||;s|\.pdf\.json||')
	if [ -z "$$PAPER_ID" ]; then
		echo "ERROR: No papers found. Run 'make setup_dataset_sample' first."
		exit 1
	fi
	echo "Selected smallest paper: $$PAPER_ID"
	$(MAKE) -s run_cli ARGS="--paper-id=$$PAPER_ID"


run_cli:  ## Run app on CLI only. Usage: make run_cli ARGS="--help" or make run_cli ARGS="--download-peerread-samples-only"
	PYTHONPATH=$(SRC_PATH) uv run python $(CLI_PATH) $(ARGS)

run_gui:  ## Run app with Streamlit GUI
	PYTHONPATH=$(SRC_PATH) uv run streamlit run $(GUI_PATH_ST)

sweep:  ## Run MAS composition sweep. Usage: make sweep ARGS="--paper-numbers 1,2,3 --repetitions 3 --all-compositions"
	PYTHONPATH=$(SRC_PATH) uv run python $(SRC_PATH)/run_sweep.py $(ARGS)

run_profile:  ## Profile app with scalene
	uv run scalene --outfile \
		"$(APP_PATH)/scalene-profiles/profile-$$(date +%Y%m%d-%H%M%S)" \
		"$(APP_PATH)/main.py"


# MARK: CC baselines


cc_run_solo:  ## Run CC solo via Python entry point. Usage: make cc_run_solo PAPER_ID=1105.1072 [CC_TIMEOUT=300]
	if [ -z "$(PAPER_ID)" ]; then
		echo "Error: PAPER_ID required. Usage: make cc_run_solo PAPER_ID=1105.1072"
		exit 1
	fi
	uv run python $(CLI_PATH) \
		--engine cc \
		--paper-id "$(PAPER_ID)"

cc_collect_teams:  ## Collect existing CC teams artifacts (stub — use cc_run_teams instead)
	echo "Note: Use 'make cc_run_teams' to run CC in teams mode via the Python engine."
	echo "Direct artifact collection is no longer supported (shell scripts removed)."

cc_run_teams:  ## Run CC teams via Python entry point. Usage: make cc_run_teams PAPER_ID=1105.1072 [CC_TEAMS_TIMEOUT=600]
	if [ -z "$(PAPER_ID)" ]; then
		echo "Error: PAPER_ID required. Usage: make cc_run_teams PAPER_ID=1105.1072"
		exit 1
	fi
	uv run python $(CLI_PATH) \
		--engine cc \
		--cc-teams \
		--paper-id "$(PAPER_ID)"


# MARK: Sanity


ruff:  ## Lint: Format and check with ruff (src only)
	uv run ruff format --exclude tests
	uv run ruff check --fix --exclude tests
	
ruff_tests:  ## Lint: Format and fix tests with ruff
	uv run ruff format tests
	uv run ruff check tests --fix

complexity:  ## Check cognitive complexity with complexipy
	uv run complexipy

# TODO: evaluate Python-native alternative to jscpd (pylint R0801, PMD CPD) to reduce npm dependency
duplication:  ## Detect copy-paste duplication with jscpd
	if command -v jscpd > /dev/null 2>&1; then
		jscpd src/ --min-lines 5 --min-tokens 50 --reporters console
	else
		echo "jscpd not installed — skipping duplication check (run 'make setup_jscpd' to enable)"
	fi

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
	$(MAKE) -s duplication
	$(MAKE) -s test_coverage
	echo "Validation completed successfully"

quick_validate:  ## Fast development cycle validation
	echo "Running quick validation ..."
	$(MAKE) -s ruff
	$(MAKE) -s type_check
	$(MAKE) -s complexity
	$(MAKE) -s duplication
	echo "Quick validation completed (check output for any failures)"

output_unset_app_env_sh:  ## Unset app environment variables
	uf="./unset_env.sh"
	echo "Outputing '$${uf}' ..."
	printenv | awk -F= '/_API_KEY=/ {print "unset " $$1}' > $$uf


# MARK: phoenix


setup_phoenix:  ## Pull Phoenix Docker image (pre-download without starting)
	echo "Pulling Arize Phoenix image ..."
	docker pull $(PHOENIX_IMAGE)
	echo "Phoenix image ready: $(PHOENIX_IMAGE)"

start_phoenix:  ## Start local Arize Phoenix trace viewer (OTLP endpoint on port 6006)
	echo "Starting Arize Phoenix ..."
	docker rm -f $(PHOENIX_CONTAINER_NAME) 2>/dev/null || true
	docker run -d --name $(PHOENIX_CONTAINER_NAME) \
		--restart unless-stopped \
		-v phoenix_data:/mnt/data \
		-e PHOENIX_WORKING_DIR=/mnt/data \
		-p $(PHOENIX_PORT):$(PHOENIX_PORT) \
		-p $(PHOENIX_GRPC_PORT):$(PHOENIX_GRPC_PORT) \
		$(PHOENIX_IMAGE)
	echo "Phoenix UI: localhost:$(PHOENIX_PORT)"
	echo "OTLP HTTP endpoint: localhost:$(PHOENIX_PORT)/v1/traces"
	echo "OTLP gRPC endpoint: localhost:$(PHOENIX_GRPC_PORT)"

stop_phoenix:  ## Stop Phoenix trace viewer (volume data preserved)
	echo "Stopping Phoenix ..."
	docker stop $(PHOENIX_CONTAINER_NAME)

status_phoenix:  ## Check Phoenix health status
	echo "Checking Phoenix status ..."
	docker ps --filter name=$(PHOENIX_CONTAINER_NAME) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	curl -sf http://localhost:$(PHOENIX_PORT) > /dev/null 2>&1 && \
		echo "Phoenix UI: healthy (http://localhost:$(PHOENIX_PORT))" || echo "Phoenix UI: not responding"


# MARK: ralph


ralph_userstory:  ## [Optional] Create UserStory.md interactively. Usage: make ralph_userstory
	echo "Creating UserStory.md through interactive Q&A ..."
	claude -p "/generating-interactive-userstory-md"

ralph_prd_md:  ## [Optional] Generate PRD.md from UserStory.md
	echo "Generating PRD.md from UserStory.md ..."
	claude -p "/generating-prd-md-from-userstory-md"

ralph_prd_json:  ## [Optional] Generate PRD.json from PRD.md (DRY_RUN=1 for parse-only)
	$(if $(DRY_RUN),python ralph/scripts/generate_prd_json.py --dry-run,echo "Generating PRD.json from PRD.md ..." && claude -p "/generating-prd-json-from-prd-md")

ralph_init:  ## Initialize Ralph loop environment
	echo "Initializing Ralph loop environment ..."
	bash ralph/scripts/init.sh

ralph_run:  ## Run Ralph loop (MAX_ITERATIONS=N, MODEL=sonnet|opus|haiku, RALPH_TIMEOUT=seconds, TEAMS=true|false EXPERIMENTAL)
	echo "Starting Ralph loop ..."
	$(if $(RALPH_TIMEOUT),timeout $(RALPH_TIMEOUT)) \
		RALPH_MODEL=$(MODEL) MAX_ITERATIONS=$(MAX_ITERATIONS) \
		RALPH_TEAMS=$(TEAMS) \
		$(if $(filter true,$(TEAMS)),CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) \
		bash ralph/scripts/ralph.sh \
		|| { EXIT_CODE=$$?; [ $$EXIT_CODE -eq 124 ] && echo "Ralph loop timed out after $(RALPH_TIMEOUT)s"; exit $$EXIT_CODE; }

ralph_worktree:  ## Run Ralph in a git worktree (BRANCH=required, TEAMS=true|false, MAX_ITERATIONS=N, MODEL=sonnet|opus|haiku, RALPH_TIMEOUT=seconds)
	$(if $(BRANCH),,$(error BRANCH is required. Usage: make ralph_worktree BRANCH=ralph/sprint8-name))
	echo "Starting Ralph in worktree for branch '$(BRANCH)' ..."
	$(if $(RALPH_TIMEOUT),timeout $(RALPH_TIMEOUT)) \
		RALPH_MODEL=$(MODEL) MAX_ITERATIONS=$(MAX_ITERATIONS) \
		RALPH_TEAMS=$(TEAMS) \
		$(if $(filter true,$(TEAMS)),CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) \
		bash ralph/scripts/ralph-in-worktree.sh "$(BRANCH)" \
		|| { EXIT_CODE=$$?; [ $$EXIT_CODE -eq 124 ] && echo "Ralph worktree timed out after $(RALPH_TIMEOUT)s"; exit $$EXIT_CODE; }

ralph_stop:  ## Stop all running Ralph loops (keeps state and data)
	bash ralph/scripts/lib/stop_ralph_processes.sh

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

ralph_watch:  ## Live-watch Ralph loop output with process tree
	bash ralph/scripts/watch.sh watch

ralph_get_log:  ## Show latest Ralph log (or specific: make ralph_get_log LOG=path/to/file.log)
	bash ralph/scripts/watch.sh log $(LOG)

ralph_clean:  ## Reset Ralph state (WARNING: removes prd.json and progress.txt)
	echo "WARNING: This will reset Ralph loop state!"
	echo "Press Ctrl+C to cancel, Enter to continue..."
	read
	rm -f ralph/docs/prd.json ralph/docs/progress.txt
	echo "Ralph state cleaned. Run 'make ralph_init' to reinitialize."


# MARK: help


help:  ## Displays this message with available recipes
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
