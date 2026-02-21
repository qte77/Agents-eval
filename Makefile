# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: \
	setup_prod setup_dev setup_claude_code setup_sandbox \
	setup_plantuml setup_pdf_converter setup_npm_tools \
	setup_ollama clean_ollama setup_dataset \
	dataset_smallest app_quickstart \
	ollama_start ollama_stop \
	plantuml_serve plantuml_render \
	pandoc_run writeup writeup_generate \
	lint_links lint_md \
	app_cli app_gui app_sweep app_profile \
	cc_run_solo cc_collect_teams cc_run_teams \
	lint_src lint_tests complexity duplication lint_hardcoded_paths \
	test test_rerun test_coverage type_check validate quick_validate \
	setup_phoenix phoenix_start phoenix_stop phoenix_status \
	ralph_userstory ralph_prd_md ralph_prd_json ralph_init ralph_run \
	ralph_worktree ralph_run_worktree ralph_stop ralph_status ralph_watch ralph_get_log ralph_clean \
	clean_results clean_logs \
	help
.DEFAULT_GOAL := help


# MARK: params


# -- paths --
SRC_PATH := src
APP_PATH := $(SRC_PATH)/app
CLI_PATH := $(SRC_PATH)/run_cli.py
CONFIG_PATH := $(APP_PATH)/config
GUI_PATH_ST := $(SRC_PATH)/run_gui.py
CHAT_CFG_FILE := $(CONFIG_PATH)/config_chat.json

# -- ollama (local LLM) --
OLLAMA_SETUP_URL := https://ollama.com/install.sh
OLLAMA_MODEL_NAME := $$(jq -r '.providers.ollama.model_name' $(CHAT_CFG_FILE))

# -- plantuml (diagram generation) --
PLANTUML_CONTAINER := plantuml/plantuml:latest
PLANTUML_SCRIPT := scripts/writeup/generate-plantuml-png.sh

# -- pandoc / writeup --
PANDOC_SCRIPT := scripts/writeup/run-pandoc.sh
PDF_CONVERTER_SCRIPT := scripts/writeup/setup-pdf-converter.sh
# pandoc_run optional overrides (empty = disabled)
BIBLIOGRAPHY :=
CSL :=
LIST_OF_FIGURES :=
LIST_OF_TABLES :=
UNNUMBERED_TITLE :=
# writeup recipe overrides
WRITEUP_DIR ?= docs/write-up
WRITEUP_OUTPUT ?= $(WRITEUP_DIR)/writeup.pdf
WRITEUP_BIB ?= $(WRITEUP_DIR)/09a_bibliography.bib
WRITEUP_CSL ?= scripts/writeup/citation-styles/ieee.csl
WRITEUP_PUML_DIR := docs/arch_vis
SKIP_PUML ?=
SKIP_CONTENT ?= 1
WRITEUP_TIMEOUT ?= 600

# -- phoenix (trace viewer) --
PHOENIX_CONTAINER_NAME := phoenix-tracing
PHOENIX_IMAGE := arizephoenix/phoenix:latest
PHOENIX_PORT := 6006
PHOENIX_GRPC_PORT := 4317

# -- cc baselines (Claude Code artifact collection) --
CC_TRACES_SCRIPT := scripts/collect-cc-traces
CC_SOLO_OUTPUT := logs/cc/solo
CC_TEAMS_OUTPUT := logs/cc/teams
CC_TIMEOUT ?= 300
CC_TEAMS_TIMEOUT ?= 600
CC_MODEL ?=

# -- ralph (autonomous loop) --
RALPH_PROJECT ?= $(notdir $(CURDIR))
RALPH_TIMEOUT ?=
TEAMS ?= false


# MARK: setup


setup_prod:  ## Install uv and deps. Flags: OLLAMA=1
	echo "Setting up prod environment ..."
	pip install uv -q
	uv sync --frozen
	$(if $(filter 1,$(OLLAMA)),$(MAKE) -s setup_ollama && $(MAKE) -s ollama_start)

setup_dev:  ## Install uv and deps, claude code, mdlint, jscpd, plantuml. Flags: OLLAMA=1
	echo "Setting up dev environment ..."
	# sudo apt-get install -y gh
	pip install uv -q
	uv sync --all-groups
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_npm_tools
	$(MAKE) -s setup_plantuml
	$(if $(filter 1,$(OLLAMA)),$(MAKE) -s setup_ollama && $(MAKE) -s ollama_start)

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

# TODO: evaluate Python-native alternatives (pymarkdownlnt, mdformat, pylint R0801) to reduce npm dependency
setup_npm_tools:  ## Setup npm-based dev tools (markdownlint, jscpd, lychee). Requires node.js and npm
	echo "Setting up npm dev tools ..."
	npm install -gs markdownlint-cli jscpd lychee
	echo "markdownlint version: $$(markdownlint --version)"
	echo "jscpd version: $$(jscpd --version)"
	echo "lychee version: $$(lychee --version)"

# Ollama BINDIR in /usr/local/bin /usr/bin /bin
setup_ollama:  ## Download Ollama, script does start local Ollama server
	echo "Downloading Ollama binary ... Using '$(OLLAMA_SETUP_URL)'."
	# script does start server but not consistently
	curl -fsSL $(OLLAMA_SETUP_URL) | sh
	echo "Pulling model '$(OLLAMA_MODEL_NAME)' ..."
	ollama pull $(OLLAMA_MODEL_NAME)

clean_ollama:  ## Remove local Ollama from system
	echo "Searching for Ollama binary ..."
	BIN=""
	for BINDIR in /usr/local/bin /usr/bin /bin; do
		if [ -x "$$BINDIR/ollama" ]; then
			echo "Ollama binary found in '$$BINDIR'"
			BIN="$$BINDIR/ollama"
			break
		fi
	done
	if [ -z "$$BIN" ]; then
		echo "Ollama binary not found in PATH"
		exit 1
	fi
	echo "Removing $$BIN ..."
	sudo rm -f "$$BIN"

setup_dataset:  ## Download PeerRead dataset. Usage: make setup_dataset [MODE=full] [MAX_PAPERS=5]
	$(if $(filter full,$(MODE)),\
		echo "Downloading full PeerRead dataset ..." && \
		$(MAKE) -s app_cli ARGS=--download-peerread-full-only,\
		echo "Downloading PeerRead sample ..." && \
		$(MAKE) -s app_cli ARGS="--download-peerread-samples-only $(if $(MAX_PAPERS),--peerread-max-papers-per-sample-download $(MAX_PAPERS))")
	$(MAKE) -s dataset_smallest

dataset_smallest:  ## Show N smallest papers by file size. Usage: make dataset_smallest N=5
	@find datasets/peerread -path "*/parsed_pdfs/*.json" \
		-type f -printf '%s %p\n' 2>/dev/null | sort -n | head -$(or $(N),10)

setup_dataset_sample:  ## Download small sample of PeerRead dataset
	echo "Downloading small sample of PeerRead dataset ..."
	$(MAKE) -s run_cli ARGS=--download-peerread-samples-only
	$(MAKE) -s dataset_smallest

# MARK: ollama


ollama_start:  ## Start local Ollama server, default 127.0.0.1:11434
	ollama serve

ollama_stop:  ## Stop local Ollama server
	echo "Stopping Ollama server ..."
	pkill ollama


# MARK: plantuml


plantuml_serve:  ## Start PlantUML server for interactive diagram editing
	# https://github.com/plantuml/plantuml-server
	# plantuml/plantuml-server:tomcat
	docker run -d -p 8080:8080 "$(PLANTUML_CONTAINER)"

plantuml_render:  ## Render a themed diagram from a PlantUML file
	$(PLANTUML_SCRIPT) "$(INPUT_FILE)" "$(STYLE)" "$(OUTPUT_PATH)" \
		"$(CHECK_ONLY)" "$(PLANTUML_CONTAINER)"


# MARK: pandoc


pandoc_run:  ## Convert MD to PDF using pandoc. Usage: dir=docs/en && make pandoc_run INPUT_FILES="$$(printf '%s\\036' $$dir/*.md)" OUTPUT_FILE="$$dir/report.pdf" [BIBLIOGRAPHY="$$dir/refs.bib"] [CSL="$$dir/style.csl"] | Help: make pandoc_run HELP=1
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
			$(MAKE) -s plantuml_render INPUT_FILE="$$f" STYLE="light" OUTPUT_PATH="assets/images"
		done
	fi
	echo "=== Building writeup PDF ==="
	$(MAKE) -s pandoc_run \
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


# MARK: markdown


lint_links:  ## Check for broken links with lychee. Usage: make lint_links [INPUT_FILES="docs/**/*.md"]
	if command -v lychee > /dev/null 2>&1; then
		lychee $(or $(INPUT_FILES),.)
	else
		echo "lychee not installed — skipping link check (run 'make setup_npm_tools' to enable)"
	fi

lint_md:  ## Lint markdown files. Usage: make lint_md INPUT_FILES="docs/**/*.md"
	if [ -z "$(INPUT_FILES)" ]; then
		echo "Error: No input files specified. Use INPUT_FILES=\"docs/**/*.md\""
		exit 1
	fi
	markdownlint $(INPUT_FILES) --fix


# MARK: app


app_quickstart:  ## Download sample data and run evaluation on smallest paper
	echo "=== Quick Start: Download samples + evaluate smallest paper ==="
	if [ ! -d datasets/peerread ]; then
		$(MAKE) -s setup_dataset
	else
		echo "PeerRead dataset already present, skipping download."
	fi
	PAPER_ID=$$($(MAKE) -s dataset_smallest N=1 \
		| awk '{print $$2}' | sed 's|.*/parsed_pdfs/||;s|\.pdf\.json||')
	if [ -z "$$PAPER_ID" ]; then
		echo "ERROR: No papers found. Run 'make setup_dataset' first."
		exit 1
	fi
	echo "Selected smallest paper: $$PAPER_ID"
	$(MAKE) -s app_cli ARGS="--paper-id=$$PAPER_ID"


app_cli:  ## Run app on CLI only. Usage: make app_cli ARGS="--help" or make app_cli ARGS="--download-peerread-samples-only"
	PYTHONPATH=$(SRC_PATH) uv run python $(CLI_PATH) $(ARGS)

app_gui:  ## Run app with Streamlit GUI
	PYTHONPATH=$(SRC_PATH) uv run streamlit run $(GUI_PATH_ST)

app_sweep:  ## Run MAS composition sweep. Usage: make app_sweep ARGS="--paper-ids 1,2,3 --repetitions 3 --all-compositions"
	PYTHONPATH=$(SRC_PATH) uv run python $(SRC_PATH)/run_sweep.py $(ARGS)

app_profile:  ## Profile app with scalene
	mkdir -p logs/scalene-profiles
	uv run scalene --outfile \
		"logs/scalene-profiles/profile-$$(date +%Y%m%d-%H%M%S)" \
		"$(CLI_PATH)"

app_clean_results:  ## Remove all sweep result files from results/sweeps/
	echo "Removing results/sweeps/ contents ..."
	rm -rf results/sweeps/*
	echo "Sweep results cleaned."

app_clean_logs:  ## Remove accumulated agent evaluation logs from logs/Agent_evals/
	echo "WARNING: This will delete all logs in logs/Agent_evals/ (including traces)!"
	echo "Press Ctrl+C to cancel, Enter to continue..."
	read
	rm -rf logs/Agent_evals/*
	echo "Agent evaluation logs cleaned."


# MARK: cc-baselines


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


# MARK: quality


lint_src:  ## Lint and format src with ruff
	uv run ruff format --exclude tests
	uv run ruff check --fix --exclude tests

lint_tests:  ## Lint and format tests with ruff
	uv run ruff format tests
	uv run ruff check tests --fix

complexity:  ## Check cognitive complexity with complexipy
	uv run complexipy

# TODO: evaluate Python-native alternative to jscpd (pylint R0801, PMD CPD) to reduce npm dependency
duplication:  ## Detect copy-paste duplication with jscpd
	if command -v jscpd > /dev/null 2>&1; then
		jscpd src/ --min-lines 5 --min-tokens 50 --reporters console
	else
		echo "jscpd not installed — skipping duplication check (run 'make setup_npm_tools' to enable)"
	fi

lint_hardcoded_paths:  ## Check for hardcoded /workspaces/ paths in tests
	if grep -rn --include='*.py' '/workspaces/' tests/; then
		echo "ERROR: Hardcoded /workspaces/ paths found in tests (breaks GHA). Use relative paths or inspect.getfile()."
		exit 1
	fi

test:  ## Run all tests
	uv run pytest

test_rerun:  ## Rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test_coverage:  ## Run tests with coverage threshold (configured in pyproject.toml)
	echo "Running tests with coverage gate (fail_under% defined in pyproject.toml)..."
	uv run pytest --cov

type_check:  ## Check for static typing errors
	uv run pyright src

validate:  ## Complete pre-commit validation (lint + type check + complexity + duplication + test coverage)
	set -e
	echo "Running complete validation sequence..."
	$(MAKE) -s lint_src
	$(MAKE) -s lint_tests
	$(MAKE) -s type_check
	$(MAKE) -s complexity
	$(MAKE) -s duplication
	$(MAKE) -s test_coverage
	echo "Validation completed successfully"

quick_validate:  ## Fast development cycle validation
	echo "Running quick validation ..."
	$(MAKE) -s lint_src
	$(MAKE) -s type_check
	$(MAKE) -s complexity
	$(MAKE) -s duplication
	$(MAKE) -s lint_hardcoded_paths
	echo "Quick validation completed (check output for any failures)"


# MARK: phoenix


setup_phoenix:  ## Pull Phoenix Docker image (pre-download without starting)
	echo "Pulling Arize Phoenix image ..."
	docker pull $(PHOENIX_IMAGE)
	echo "Phoenix image ready: $(PHOENIX_IMAGE)"

phoenix_start:  ## Start local Arize Phoenix trace viewer (OTLP endpoint on port 6006)
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

phoenix_stop:  ## Stop Phoenix trace viewer (volume data preserved)
	echo "Stopping Phoenix ..."
	docker stop $(PHOENIX_CONTAINER_NAME)

phoenix_status:  ## Check Phoenix health status
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

ralph_init:  ## Initialize Ralph loop environment. Usage: make ralph_init [RALPH_PROJECT=name]
	echo "Initializing Ralph loop environment ..."
	RALPH_PROJECT=$(RALPH_PROJECT) bash ralph/scripts/init.sh

ralph_run:  ## Run Ralph loop (MAX_ITERATIONS=N, MODEL=sonnet|opus|haiku, RALPH_TIMEOUT=seconds, TEAMS=true|false EXPERIMENTAL)
	echo "Starting Ralph loop ..."
	$(if $(RALPH_TIMEOUT),timeout $(RALPH_TIMEOUT)) \
		RALPH_MODEL=$(MODEL) MAX_ITERATIONS=$(MAX_ITERATIONS) \
		RALPH_TEAMS=$(TEAMS) \
		$(if $(filter true,$(TEAMS)),CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) \
		bash ralph/scripts/ralph.sh \
		|| { EXIT_CODE=$$?; [ $$EXIT_CODE -eq 124 ] && echo "Ralph loop timed out after $(RALPH_TIMEOUT)s"; exit $$EXIT_CODE; }

ralph_worktree:  ## Create a git worktree for Ralph and cd into it (BRANCH=required)
	$(if $(BRANCH),,$(error BRANCH is required. Usage: make ralph_worktree BRANCH=ralph/sprint-name))
	bash ralph/scripts/ralph-in-worktree.sh "$(BRANCH)"

ralph_run_worktree:  ## Create worktree + run Ralph in it (BRANCH=required, MAX_ITERATIONS=N, MODEL=sonnet|opus|haiku, RALPH_TIMEOUT=seconds, TEAMS=true|false)
	$(if $(BRANCH),,$(error BRANCH is required. Usage: make ralph_run_worktree BRANCH=ralph/sprint-name))
	bash ralph/scripts/ralph-in-worktree.sh "$(BRANCH)"
	$(if $(RALPH_TIMEOUT),timeout $(RALPH_TIMEOUT)) \
		RALPH_MODEL=$(MODEL) MAX_ITERATIONS=$(MAX_ITERATIONS) \
		RALPH_TEAMS=$(TEAMS) \
		$(if $(filter true,$(TEAMS)),CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) \
		bash -c 'cd "../$$(basename $(BRANCH))" && bash ralph/scripts/ralph.sh' \
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


help:  ## Show available recipes grouped by section
	@echo "Usage: make [recipe]"
	@echo ""
	@awk '/^# MARK:/ { \
		section = substr($$0, index($$0, ":")+2); \
		printf "\n\033[1m%s\033[0m\n", section \
	} \
	/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			recipe = $$1; \
			sub(/:/, "", recipe); \
			printf "  \033[36m%-22s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH) \
		} \
	}' $(MAKEFILE_LIST)


# MARK: FIXME backward-compat aliases


ruff: lint_src
ruff_tests: lint_tests
test_all: test
test_quick: test_rerun
sweep: run_sweep
quick_start: quickstart
dataset_get_smallest: dataset_smallest
run_puml_interactive: plantuml_serve
run_puml_single: plantuml_render
run_markdownlint: lint_md
setup_prod_ollama: ; $(MAKE) setup_prod OLLAMA=1
setup_dev_ollama: ; $(MAKE) setup_dev OLLAMA=1
setup_devc_ollama: ; $(MAKE) setup_devc OLLAMA=1