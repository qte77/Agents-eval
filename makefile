# Makefile for downloading and starting Ollama server locally
# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
# Ollama available at 127.0.0.1:11434

OLLAMA_SETUP := https://ollama.com/install.sh

.PHONY: all ollama_setup_start ollama_start ollama_stop ollama_clean

# Default target
all: setup_env

setup_env:
	@echo "Setting up tools..."
	@pip install uv
	@uv sync --frozen
	@$(MAKE) setup_ollama
	@$(MAKE) start_ollama

setup_ollama:
	@echo "Downloading Ollama binary... Using '$(OLLAMA_SETUP)'."
	# script does start server but not consistently
	@curl -fsSL $(OLLAMA_SETUP) | sh

start_ollama:
	@ollama serve

stop_ollama:
	@echo "Stopping Ollama server..."
	@pkill ollama

clean_ollama:
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

run_app:
	@uv run python -m src

test_all:
	@uv run pytest

ruff:
	@uv run ruff format
	@uv run ruff check --fix
