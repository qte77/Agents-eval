# Makefile for downloading and starting Ollama server locally
# Ollama BINDIR in /usr/local/bin /usr/bin /bin 
# Ollama available at 127.0.0.1:11434

.PHONY: all download_start search start stop clean

# Default target
all: start

download_start:
	@echo "Downloading Ollama binary..."
	@curl -fsSL https://ollama.com/install.sh | sh

start:
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

stop:
	@echo "Stopping Ollama server..."
	@pkill ollama

clean:
	@$(MAKE) search
	@echo "Cleaning up..."
	@rm -f $(BINDIR)
