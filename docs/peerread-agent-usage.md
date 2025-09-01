# PeerRead Agent System Usage Guide

**Document Status**: Updated 2025-08-31  
**Version**: 2.0  
**Target**: Current codebase implementation

This guide explains how to use the Multi-Agent System (MAS) to generate reviews for scientific papers using the PeerRead dataset integration.

## Quick Start

To generate a review for a specific paper (e.g., paper 104), run the following command:

```bash
make run_cli ARGS="--paper-number=104 --chat-provider=github"
```

**What this does:**

- Loads the PeerRead dataset and retrieves paper 104
- Initializes the multi-agent system with the specified chat provider
- Provides agents with PeerRead-specific tools for paper analysis
- Agents attempt to generate a structured academic review

**Prerequisites:**

- PeerRead dataset downloaded (use `make run_cli ARGS="--download-peerread-samples-only"` for initial setup)
- Valid chat provider configuration in `src/app/config/config_chat.json`

## Available Agent Tools

The agent has access to the following tools, defined in `src/app/agents/peerread_tools.py`.

### Paper Retrieval

- **`get_peerread_paper(paper_id: str) -> PeerReadPaper`**: Retrieves a specific paper's metadata from the PeerRead dataset.
- **`query_peerread_papers(venue: str = "", min_reviews: int = 1) -> list[PeerReadPaper]`**: Queries papers with filters like venue and minimum number of reviews.
- **`read_paper_pdf(pdf_path: str | Path) -> str`**: Reads the full text content from a local PDF file using MarkItDown. **Note:** Requires the exact path to the PDF file. Handles both string and Path objects.

### Review Generation

- **`generate_paper_review_content_from_template(paper_id: str, review_focus: str = "comprehensive", tone: str = "professional") -> str`**: Creates a review template for a specific paper. **WARNING**: This creates a template structure, not an actual review. It's designed for demonstration purposes and requires manual completion or additional AI processing.

**Parameters:**

- `review_focus`: Type of review - "comprehensive", "technical", "high-level"
- `tone`: Review tone - "professional", "constructive", "critical"

### Review Persistence

- **`save_structured_review(paper_id: str, structured_review: GeneratedReview) -> str`**: Saves a structured, validated `GeneratedReview` object to persistent storage. **Recommended** for structured reviews.
- **`save_paper_review(paper_id: str, review_text: str, recommendation: str = "", confidence: float = 0.0) -> str`**: Saves raw review text with optional recommendation and confidence scores. Use for simple text-based reviews.

**Storage Format:**

- Files saved as: `{paper_id}_{timestamp}.json`
- Structured reviews also create: `{paper_id}_{timestamp}_structured.json`

## Review Storage

- **Location**: `src/app/data_utils/reviews/` (configured in `MAS_REVIEWS_PATH`)
- **Format**: JSON files with timestamp: `{paper_id}_{timestamp}.json`
- **Structured Reviews**: Additional `{paper_id}_{timestamp}_structured.json` for validated reviews
- **Content**: Complete review with metadata, timestamps, and paper references
- **Access**: Use `ReviewPersistence` class for programmatic access to saved reviews

## Module Architecture

The system is designed with a clear separation of concerns:

- **CLI Entrypoint**: `src/run_cli.py` handles command-line arguments and lightweight parsing
- **Main Application**: `src/app/app.py` orchestrates the agent execution and system initialization
- **Dataset Interaction**: `src/app/data_utils/datasets_peerread.py` handles downloading and loading the PeerRead dataset
- **Agent Tools**: `src/app/agents/peerread_tools.py` provides the tools for the agent manager
- **Agent System**: `src/app/agents/agent_system.py` manages multi-agent coordination and execution
- **Review Persistence**: `src/app/data_utils/review_persistence.py` and `src/app/data_utils/review_loader.py` manage saving and loading reviews
- **Data Models**:
  - `src/app/data_models/peerread_models.py`: Defines core data structures like `PeerReadPaper` and `GeneratedReview`
  - `src/app/data_models/evaluation_models.py`: Contains evaluation result models and PeerRead evaluation structures
  - `src/app/data_models/app_models.py`: Application-level configuration models
- **Evaluation**: `src/app/evals/traditional_metrics.py` contains comprehensive evaluation functionality including PeerRead-specific evaluation tools

## Additional CLI Options

The system supports various command-line options for different use cases:

### Dataset Management

```bash
# Download sample PeerRead data (recommended for testing)
make run_cli ARGS="--download-peerread-samples-only"

# Download full PeerRead dataset (large download)
make run_cli ARGS="--download-peerread-full-only"
```

### Agent Configuration

```bash
# Enable specific agent types
make run_cli ARGS="--paper-number=104 --include-researcher --include-analyst"

# Disable streaming output
make run_cli ARGS="--paper-number=104 --no-stream"

# Use custom chat configuration
make run_cli ARGS="--paper-number=104 --chat-config-file=/path/to/config.json"
```

### Supported Chat Providers

- `github` - GitHub Models API
- `ollama` - Local Ollama installation
- `openai` - OpenAI API
- `anthropic` - Anthropic Claude API

See `src/app/config/config_chat.json` for provider configuration details.

## Troubleshooting

### Common Issues

**Paper not found error:**

- Ensure PeerRead dataset is downloaded: `make run_cli ARGS="--download-peerread-samples-only"`
- Check if paper ID exists in the dataset using query tools

**Agent tools not working:**

- Verify chat provider configuration in `config_chat.json`
- Check API keys and model availability
- Review logs for specific error messages

**Review saving failures:**

- Ensure `src/app/data_utils/reviews/` directory exists
- Check write permissions on the reviews directory
- Verify `GeneratedReview` object structure for structured reviews

### Getting Help

For more detailed documentation:

- Review docstrings in `src/app/agents/peerread_tools.py`
- Check configuration examples in `src/app/config/`
- See implementation examples in `src/examples/`
