---
title: PeerRead Agent System Usage Guide
description: Agent tools reference, CLI examples, and troubleshooting for the PeerRead MAS
created: 2025-08-02
updated: 2026-03-07
category: usage-guide
version: 3.1.0
validated_links: 2026-03-12
---

# Peerread Agent Usage

For quick start, module architecture, and review storage details, see [README.md](../../README.md) and [architecture.md](../architecture.md).

## Available Agent Tools

The agent has access to the following tools, defined in `src/app/tools/peerread_tools.py`.

### Paper Retrieval

- **`get_peerread_paper(paper_id: str) -> PeerReadPaper`**: Retrieves a specific paper's metadata from the PeerRead dataset.
- **`query_peerread_papers(venue: str = "", min_reviews: int = 1) -> list[PeerReadPaper]`**: Queries papers with filters like venue and minimum number of reviews.
- **`get_paper_content(paper_id: str) -> str`**: Reads the full text content of a paper by ID, returning extracted text for analysis.

### Review Generation

- **`generate_paper_review_content_from_template(paper_id: str, review_focus: str = "comprehensive", tone: str = "professional") -> str`**: Creates a review template for a specific paper. **WARNING**: This creates a template structure, not an actual review. Designed for demonstration purposes.

### Parameters:

- `review_focus`: Type of review — `"comprehensive"`, `"technical"`, `"high-level"`
- `tone`: Review tone — `"professional"`, `"constructive"`, `"critical"`

### Review Persistence

- **`save_structured_review(paper_id: str, structured_review: GeneratedReview) -> str`**: Saves a validated `GeneratedReview` object to persistent storage. **Recommended** for structured reviews.
- **`save_paper_review(paper_id: str, review_text: str, recommendation: str = "", confidence: float = 0.0) -> str`**: Saves raw review text with optional recommendation and confidence scores.

### Storage Format:

- Files saved as: `{paper_id}_{timestamp}.json`
- Structured reviews also create: `{paper_id}_{timestamp}_structured.json`

## CLI Options

### Dataset Management

```bash
# Download sample PeerRead data (recommended for testing)
make app_cli ARGS="--download-peerread-samples-only"

# Download full PeerRead dataset (large download)
make app_cli ARGS="--download-peerread-full-only"

# Limit sample download size
make app_cli ARGS="--download-peerread-samples-only --peerread-max-papers-per-sample-download 50"
```bash

### Agent Configuration

```bash
# Enable specific agent types
make app_cli ARGS="--paper-id=1105.1072 --include-researcher --include-analyst --include-synthesiser"

# Enable streaming output
make app_cli ARGS="--paper-id=1105.1072 --pydantic-ai-stream"

# Use custom chat configuration
make app_cli ARGS="--paper-id=1105.1072 --chat-config-file=/path/to/config.json"
```

### Evaluation Control

```bash
# Skip evaluation after agent run
make app_cli ARGS="--paper-id=1105.1072 --skip-eval"

# Generate a Markdown report after evaluation (mutually exclusive with --skip-eval)
make app_cli ARGS="--paper-id=1105.1072 --generate-report"

# Override Tier 2 judge provider/model
make app_cli ARGS="--paper-id=1105.1072 --judge-provider=openai --judge-model=gpt-4o"
```bash

### Review Tools Control

```bash
# Disable review generation tools (opt-out)
make app_cli ARGS="--paper-id=1105.1072 --no-review-tools"

# Explicitly enable review tools (default, rarely needed)
make app_cli ARGS="--paper-id=1105.1072 --enable-review-tools"
```

### Execution Engine

```bash
# MAS engine (default)
make app_cli ARGS="--paper-id=1105.1072 --engine=mas"

# Claude Code headless engine (requires claude CLI installed)
make app_cli ARGS="--paper-id=1105.1072 --engine=cc"

# Claude Code with Agent Teams mode
make app_cli ARGS="--paper-id=1105.1072 --engine=cc --cc-teams"
```bash

### Sweep & Profiling

```bash
# Sweep across multiple papers and MAS compositions
make app_sweep ARGS="--paper-ids 1105.1072,2301.00001 --repetitions 3 --all-compositions"
```

### Supported Chat Providers

All providers configured in `src/app/config/config_chat.json` are available. Common choices:

- `github` — GitHub Models API
- `ollama` — Local Ollama installation (see `make setup_ollama`)
- `openai` — OpenAI API
- `anthropic` — Anthropic Claude API
- `gemini`, `groq`, `cerebras`, `mistral`, `openrouter` — and more (see `PROVIDER_REGISTRY` in `app_models.py`)

```bash
make app_cli ARGS="--paper-id=1105.1072 --chat-provider=openai"
```bash

## Troubleshooting

### Paper not found error:

- Ensure PeerRead dataset is downloaded: `make app_cli ARGS="--download-peerread-samples-only"`
- Paper IDs are arxiv IDs (e.g., `1105.1072`), not sequential numbers
- Use `query_peerread_papers` via the agent to list available papers

### Agent tools not working:

- Verify chat provider configuration in `config_chat.json`
- Check API keys are set in `.env` for the chosen provider
- Review logs for specific error messages

### Review saving failures:

- Ensure output directory is writable (created automatically on first run)
- Verify `GeneratedReview` object structure for structured reviews

### Claude Code engine failures (`--engine=cc`):

- Check `claude` CLI is installed: `which claude`
- Ensure `ANTHROPIC_API_KEY` is set in `.env`

For more detailed documentation, review docstrings in `src/app/tools/peerread_tools.py` and configuration examples in `src/app/config/`.
