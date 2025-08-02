# PeerRead Agent System Usage Guide

This guide explains how to use the Multi-Agent System (MAS) to generate reviews for scientific papers using the PeerRead dataset integration.

## Quick Start

To generate a review for a specific paper (e.g., paper 104), run the following command:

```bash
make run_cli ARGS="--paper-number=104 --chat-provider=github"
```

This command instructs the system to use a predefined template to generate a query for reviewing the specified paper. The agent will then use its available tools to attempt to complete this task.

## Available Agent Tools

The agent has access to the following tools, defined in `src/app/agents/peerread_tools.py`.

### Paper Retrieval

- **`get_peerread_paper(paper_id: str) -> PeerReadPaper`**: Retrieves a specific paper's metadata from the PeerRead dataset.
- **`query_peerread_papers(venue: str = "", min_reviews: int = 1) -> list[PeerReadPaper]`**: Queries papers with filters like venue and minimum number of reviews.
- **`read_paper_pdf_tool(pdf_path: str) -> str`**: Reads the full text content from a local PDF file. **Note:** This tool requires the user to provide the exact path to the PDF file.

### Review Generation

- **`generate_structured_review(paper_id: str, tone: str = "professional", review_focus: str = "comprehensive") -> GeneratedReview`**: Generates a structured review using the paper's metadata. The output is a `GeneratedReview` object.
- **`generate_actual_review(paper_id: str, pdf_content: str, review_focus: str = "comprehensive", tone: str = "professional") -> str`**: Creates a detailed prompt for the LLM to generate a review based on the full paper content.
- **`get_review_prompt_for_paper(paper_id: str, tone: str = "professional", review_focus: str = "comprehensive") -> dict`**: A helper tool that combines paper metadata and a template to create a review prompt.

### Review Persistence

- **`save_structured_review(paper_id: str, structured_review: GeneratedReview) -> str`**: Saves a structured, validated review to persistent storage. This is the recommended way to save reviews.
- **`save_paper_review(paper_id: str, review_text: str, recommendation: str = "", confidence: float = 0.0) -> str`**: A simpler tool to save raw review text.

## Review Storage

- **Location**: `src/app/data_utils/reviews/`
- **Format**: JSON files with a timestamp: `{paper_id}_{timestamp}.json`. A `_structured.json` version is also saved for the validated, structured review.
- **Content**: The JSON file contains the complete review with metadata.

## Module Architecture

The system is designed with a clear separation of concerns:

- **CLI Entrypoint**: `src/app/main.py` handles command-line arguments and orchestrates the agent execution.
- **Dataset Interaction**: `src/app/data_utils/datasets_peerread.py` handles downloading and loading the PeerRead dataset.
- **Agent Tools**: `src/app/agents/peerread_tools.py` provides the tools for the agent manager.
- **Review Persistence**: `src/app/data_utils/review_persistence.py` and `src/app/data_utils/review_loader.py` manage saving and loading reviews.
- **Data Models**:
  - `src/app/data_models/peerread_models.py`: Defines core data structures like `PeerReadPaper` and `GeneratedReview`.
  - `src/app/data_models/peerread_evaluation_models.py`: Contains models for the external evaluation system.
- **Evaluation**: `src/app/evals/peerread_evaluation.py` is part of a separate system that consumes the saved reviews for evaluation.
