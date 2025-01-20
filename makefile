# Makefile for downloading and starting Ollama server locally
# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
# Ollama available at 127.0.0.1:11434

.PHONY: all ollama_setup_start ollama_start ollama_stop ollama_clean

# Default target
all: start

setup:
	@echo "Setting up tools..."
	@pip install uv
	@$(MAKE) ollama_setup_start

ollama_setup_start:
	@echo "Downloading Ollama binary..."
	@curl -fsSL https://ollama.com/install.sh | sh

ollama_start:
	@echo "Searching for Ollama binary..."
	@for BINDIR in /usr/local/bin /usr/bin /bin; do \
		if echo $$PATH | grep -q $$BINDIR; then \
			echo "Ollama binary found in '$$BINDIR'"; \
			BIN="$$BINDIR/ollama"; \
			$$BIN serve & \
			break; \
		fi; \
	done
	@echo $(BIN)

ollama_stop:
	@echo "Stopping Ollama server..."
	@pkill ollama

ollama_clean:
	@$(MAKE) search
	@echo "Cleaning up..."
	@rm -f $(BINDIR)
