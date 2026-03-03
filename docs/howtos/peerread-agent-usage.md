---
title: PeerRead Agent System Usage Guide
description: Comprehensive guide for using the PeerRead dataset integration with multi-agent evaluation system
date: 2026-03-01
category: usage-guide
version: 3.0.0
---

**Document Status**: Updated 2026-03-01
**Version**: 3.0
**Target**: Current codebase implementation

This guide explains how to use the Multi-Agent System (MAS) to generate reviews for scientific papers using the PeerRead dataset integration.

## Quick Start

The fastest path — downloads sample data and evaluates the smallest available paper automatically:

```bash
make app_quickstart
```

To evaluate a specific paper by arxiv ID:

```bash
make app_cli ARGS="--paper-id=1105.1072"
```

**What this does:**

- Loads the PeerRead dataset and retrieves the specified paper
- Initializes the multi-agent system with the configured chat provider
- Provides agents with PeerRead-specific tools for paper analysis and review generation
- Runs the evaluation pipeline (Tier 1/2/3) and saves results to `output/runs/`

**Prerequisites:**

- PeerRead dataset downloaded (use `make app_cli ARGS="--download-peerread-samples-only"` for initial setup)
- API key for at least one chat provider set in `.env`
- Valid provider configuration in `src/app/config/config_chat.json`

## Available Agent Tools

The agent has access to the following tools, defined in `src/app/tools/peerread_tools.py`.

### Paper Retrieval

- **`get_peerread_paper(paper_id: str) -> PeerReadPaper`**: Retrieves a specific paper's metadata from the PeerRead dataset.
- **`query_peerread_papers(venue: str = "", min_reviews: int = 1) -> list[PeerReadPaper]`**: Queries papers with filters like venue and minimum number of reviews.
- **`get_paper_content(paper_id: str) -> str`**: Reads the full text content of a paper by ID, returning extracted text for analysis.

### Review Generation

- **`generate_paper_review_content_from_template(paper_id: str, review_focus: str = "comprehensive", tone: str = "professional") -> str`**: Creates a review template for a specific paper. **WARNING**: This creates a template structure, not an actual review. Designed for demonstration purposes.

**Parameters:**

- `review_focus`: Type of review — `"comprehensive"`, `"technical"`, `"high-level"`
- `tone`: Review tone — `"professional"`, `"constructive"`, `"critical"`

### Review Persistence

- **`save_structured_review(paper_id: str, structured_review: GeneratedReview) -> str`**: Saves a validated `GeneratedReview` object to persistent storage. **Recommended** for structured reviews.
- **`save_paper_review(paper_id: str, review_text: str, recommendation: str = "", confidence: float = 0.0) -> str`**: Saves raw review text with optional recommendation and confidence scores.

**Storage Format:**

- Files saved as: `{paper_id}_{timestamp}.json`
- Structured reviews also create: `{paper_id}_{timestamp}_structured.json`

## Review Storage

- **Location**: `output/runs/` (default configured in `ReviewPersistence`)
- **Format**: JSON files with timestamp: `{paper_id}_{timestamp}.json`
- **Structured Reviews**: Additional `{paper_id}_{timestamp}_structured.json` for validated reviews
- **Content**: Complete review with metadata, timestamps, and paper references
- **Access**: Use `ReviewPersistence` class in `src/app/data_utils/review_persistence.py` for programmatic access

## Module Architecture

The system is designed with a clear separation of concerns:

- **CLI Entrypoint**: `src/run_cli.py` — command-line argument parsing and lightweight dispatch
- **GUI Entrypoint**: `src/run_gui.py` — Streamlit application with pages: Home, Run App, Settings, Evaluation, Agent Graph
- **Main Application**: `src/app/app.py` — orchestrates agent execution and system initialization
- **Dataset Interaction**: `src/app/data_utils/datasets_peerread.py` — downloading and loading the PeerRead dataset
- **Agent Tools**: `src/app/tools/peerread_tools.py` — tools registered to the agent manager
- **Agent System**: `src/app/agents/agent_system.py` — multi-agent coordination (Manager, Researcher, Analyst, Synthesiser)
- **Review Persistence**: `src/app/data_utils/review_persistence.py` — saving/loading reviews, default dir `output/runs`
- **Data Models**:
  - `src/app/data_models/peerread_models.py`: `PeerReadPaper`, `PeerReadReview`, `GeneratedReview`, `ReviewGenerationResult`, `DownloadResult`
  - `src/app/data_models/evaluation_models.py`: `Tier1Result`, `Tier2Result`, `Tier3Result`, `CompositeEvaluationResult`, `BaselineComparison`
  - `src/app/data_models/app_models.py`: `ChatConfig`, `ProviderConfig`, `AgentConfig`, `PROVIDER_REGISTRY`
- **Evaluation**: `src/app/judge/traditional_metrics.py` — `TraditionalMetricsEngine` for Tier 1 metrics (cosine similarity, Jaccard, semantic similarity)

## Additional CLI Options

The system supports various command-line options:

### Dataset Management

```bash
# Download sample PeerRead data (recommended for testing)
make app_cli ARGS="--download-peerread-samples-only"

# Download full PeerRead dataset (large download)
make app_cli ARGS="--download-peerread-full-only"

# Limit sample download size
make app_cli ARGS="--download-peerread-samples-only --peerread-max-papers-per-sample-download 50"
```

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
```

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
```

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
```

### GUI

```bash
make app_gui
```

Opens the Streamlit interface at `localhost:8501` with pages for running evaluations, configuring providers, and visualizing agent interaction graphs and evaluation results.

## Troubleshooting

### Common Issues

**Paper not found error:**

- Ensure PeerRead dataset is downloaded: `make app_cli ARGS="--download-peerread-samples-only"`
- Paper IDs are arxiv IDs (e.g., `1105.1072`), not sequential numbers
- Use `query_peerread_papers` via the agent to list available papers

**Agent tools not working:**

- Verify chat provider configuration in `config_chat.json`
- Check API keys are set in `.env` for the chosen provider
- Review logs for specific error messages

**Review saving failures:**

- Ensure `output/runs/` directory is writable (created automatically on first run)
- Verify `GeneratedReview` object structure for structured reviews

**Claude Code engine failures (`--engine=cc`):**

- Check `claude` CLI is installed: `which claude`
- Ensure `ANTHROPIC_API_KEY` is set in `.env`

### Getting Help

For more detailed documentation:

- Review docstrings in `src/app/tools/peerread_tools.py`
- Check configuration examples in `src/app/config/`
- See implementation examples in `src/examples/`
