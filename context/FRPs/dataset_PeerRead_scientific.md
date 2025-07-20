# Product Requirements Prompt (PRP) - PeerRead Dataset Integration

## Goal

Implement PeerRead dataset integration as an MVP for the Multi-Agent System (MAS) evaluation framework. Create a functional dataset loader with configuration support that enables benchmarking of scientific paper review quality. The MAS will review papers from PeerRead and results will be benchmarked against existing expert reviews.

**End State:** Working dataset loader with configuration, data models, and loading utilities that integrate seamlessly with the existing codebase for MAS evaluation purposes.

## Why

- **Evaluation Capability**: Enables benchmarking MAS review quality against expert human reviews from ACL/NIPS/ICLR conferences
- **Scientific Validation**: PeerRead is the first public dataset of scientific peer reviews (14.7K papers, 10.7K reviews) 
- **Integration Value**: Leverages existing `data/peerread/` directory structure and follows established codebase patterns
- **Research Applications**: Supports novel NLP tasks like acceptance prediction and review aspect scoring

## What

**User-visible behavior:**
- Load PeerRead dataset with configurable venue/split selection
- Provide structured paper and review data for MAS evaluation
- Support batched loading for performance with large dataset
- Enable benchmarking of MAS review outputs against expert reviews

**Technical requirements:**
- MVP implementation with download, configuration, and loading capabilities
- Follow existing Pydantic datamodel patterns from `app/datamodels/app_models.py`
- Use configuration file approach similar to `config_chat.json`
- Integrate with existing `data/peerread/` directory structure
- Support the agent task format specified in feature requirements

### Success Criteria

- [ ] Dataset downloads and loads successfully from HuggingFace
- [ ] Pydantic models validate paper and review data correctly
- [ ] Configuration allows venue/split selection (acl_2017, nips_2013-2017, etc.)
- [ ] Loading utilities support batch processing for performance
- [ ] Integration tests verify data format matches agent task requirements
- [ ] All validation gates pass (ruff, mypy, pytest)

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: https://huggingface.co/datasets/allenai/peer_read
  why: Official HuggingFace dataset with standardized loading API
  critical: Main data source with consistent API
  
- url: https://arxiv.org/abs/1804.09635
  why: Original paper with dataset structure and task definitions
  section: Dataset composition and fields (parsed_pdfs, reviews)
  
- url: https://github.com/allenai/PeerRead
  why: Original implementation patterns and data organization
  section: Code examples and data processing utilities
  
- file: src/app/datamodels/app_models.py
  why: Existing Pydantic patterns with validators and docstrings
  pattern: BaseModel with typed fields, field_validator decorators
  
- file: src/app/config/config_chat.json
  why: Configuration file structure and JSON schema patterns
  pattern: Nested JSON with providers, inference settings
  
- file: tests/providers/test_provider_config.py
  why: Testing patterns for Pydantic model validation
  pattern: model_validate() usage with assertions
```

### Current Codebase tree

```bash
src/app/
├── datasets/
│   └── __init__.py  # Currently empty - will add PeerRead loader
├── datamodels/
│   └── app_models.py  # Pydantic patterns to follow
├── config/
│   ├── config_chat.json  # JSON config pattern
│   └── config_eval.json
└── utils/
    ├── error_messages.py  # Custom error handling
    └── load_configs.py   # Config loading utilities

data/
└── peerread/  # Existing structure (empty)
    ├── dev/
    ├── test/
    └── train/
```

### Desired Codebase tree with files to be added

```bash
src/app/
├── datasets/
│   ├── __init__.py
│   └── peerread.py          # Main dataset loader class and functions
├── datamodels/
│   ├── app_models.py
│   └── peerread_models.py   # Pydantic models for papers and reviews
├── config/
│   ├── config_peerread.json # Configuration for venues, splits, etc.
│   └── (existing files...)

tests/
└── datasets/
    └── test_peerread_*.py   # Unit tests for dataset loading
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: HuggingFace datasets requires specific setup
# Install: pip install datasets (likely already available via dependencies)
# Usage: datasets.load_dataset("allenai/peer_read", split="train")

# CRITICAL: This codebase uses Pydantic v2 (>=2.10.6)
# Use model_validate() instead of parse_obj()
# Use ConfigDict instead of Config class

# CRITICAL: PeerRead has licensing constraints
# Some data requires separate download, but HuggingFace handles this
# Use HuggingFace datasets for consistent access

# Performance: Large dataset (14.7K papers)
# Implement batch loading to avoid memory issues
# Use streaming mode for datasets if needed: streaming=True

# Data structure complexity:
# parsed_pdfs: nested dict with sections, references, etc.
# reviews: variable fields depending on venue
# Handle missing fields gracefully with Optional types
```

## Implementation Blueprint

### Data models and structure

```python
# peerread_models.py - Core data models ensuring type safety
from typing import Any, Optional
from pydantic import BaseModel, field_validator

class PeerReadPaper(BaseModel):
    """Represents a scientific paper from PeerRead dataset."""
    
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    venue: str
    year: int
    sections: Optional[dict[str, str]] = None
    references: Optional[list[str]] = None
    
    @field_validator("paper_id")
    @classmethod
    def validate_paper_id(cls, v: str) -> str:
        """Ensure paper ID is not empty."""
        if not v.strip():
            raise ValueError("Paper ID cannot be empty")
        return v.strip()

class PeerReadReview(BaseModel):
    """Represents a peer review from PeerRead dataset."""
    
    paper_id: str
    reviewer_id: str
    recommendation: str  # "accept", "reject", etc.
    comments: str
    scores: Optional[dict[str, float]] = None  # originality, clarity, etc.
    confidence: Optional[float] = None
    
class PeerReadAgentTask(BaseModel):
    """Agent task format for PeerRead evaluation."""
    
    paper_id: str
    title: str
    abstract: str
    agent_task: str = "Provide a peer review with rating (1-10) and recommendation"
    expected_output: dict[str, Any]

class PeerReadConfig(BaseModel):
    """Configuration for PeerRead dataset loading."""
    
    venues: list[str] = ["acl_2017", "nips_2013-2017", "iclr_2017"]
    splits: list[str] = ["train", "dev", "test"]  
    batch_size: int = 100
    cache_dir: str = "data/peerread"
    streaming: bool = False
```

### List of tasks to be completed in order

```yaml
Task 1: Create Pydantic data models
CREATE src/app/datamodels/peerread_models.py:
  - MIRROR pattern from: src/app/datamodels/app_models.py
  - IMPLEMENT: PeerReadPaper, PeerReadReview, PeerReadAgentTask, PeerReadConfig
  - INCLUDE: docstrings, type hints, field validators
  - KEEP: error handling pattern identical to app_models.py

Task 2: Create configuration file  
CREATE src/app/config/config_peerread.json:
  - MIRROR pattern from: src/app/config/config_chat.json
  - DEFINE: venues list, splits, batch_size, cache settings
  - ORGANIZE: logical grouping similar to chat config structure

Task 3: Implement dataset loader utilities
CREATE src/app/datasets/peerread.py:
  - IMPLEMENT: load_peerread_dataset() function
  - IMPLEMENT: PeerReadLoader class for batch processing
  - USE: HuggingFace datasets library for data access
  - INCLUDE: error handling from utils/error_messages.py
  - SUPPORT: configuration-driven loading

Task 4: Create comprehensive unit tests
CREATE tests/datasets/test_peerread_loader.py:
  - MIRROR pattern from: tests/providers/test_provider_config.py
  - TEST: model validation, data loading, configuration
  - INCLUDE: async tests if needed, pytest fixtures
  - VERIFY: batch processing and error handling

Task 5: Integration with existing data directory
MODIFY existing data/peerread structure:
  - ENSURE: proper integration with loader utilities
  - VERIFY: caching works correctly in existing directories
```

### Integration Points

```yaml
DATAMODELS:
  - add to: src/app/datamodels/__init__.py
  - import: PeerReadPaper, PeerReadReview, PeerReadAgentTask
  - pattern: "from .peerread_models import PeerReadPaper"

CONFIG:
  - add to: src/app/config/config_app.py  
  - constant: PEERREAD_CONFIG_FILE = "config/config_peerread.json"
  - pattern: Follow existing CHAT_CONFIG_FILE pattern

DATASETS:
  - update: src/app/datasets/__init__.py
  - import: load_peerread_dataset, PeerReadLoader
  - pattern: "from .peerread import load_peerread_dataset"

DEPENDENCIES:
  - verify: datasets library available (check pyproject.toml)
  - add if missing: "datasets>=2.0.0" to dependencies
```

## Validation Loop

### Level 1: Write tests first (TDD approach)

```python
# CREATE tests/datasets/test_peerread_loader.py
def test_peerread_paper_validation():
    """Test PeerReadPaper model validates correctly."""
    paper_data = {
        "paper_id": "acl_2017_001", 
        "title": "Test Paper",
        "abstract": "Test abstract",
        "authors": ["Author One"],
        "venue": "acl_2017",
        "year": 2017
    }
    paper = PeerReadPaper.model_validate(paper_data)
    assert paper.paper_id == "acl_2017_001"
    assert paper.title == "Test Paper"

def test_config_loading():
    """Test configuration loads correctly."""
    config = load_config("config/config_peerread.json", PeerReadConfig)
    assert isinstance(config.venues, list)
    assert config.batch_size > 0

def test_dataset_loading():
    """Test dataset loads with proper format."""
    loader = PeerReadLoader(config=test_config)
    papers = loader.load_papers(limit=5)
    assert len(papers) == 5
    assert all(isinstance(p, PeerReadPaper) for p in papers)
```

### Level 2: Syntax & Style validation

```bash
# Run these FIRST - fix any errors before proceeding
make ruff
make type_check
# Expected: No errors. If errors, READ the error and fix.
```

### Level 3: Implement core logic

```python
# peerread.py implementation
def load_peerread_dataset(config: PeerReadConfig) -> dict[str, list[PeerReadPaper]]:
    """Load PeerRead dataset with configuration."""
    try:
        dataset = datasets.load_dataset(
            "allenai/peer_read",
            cache_dir=config.cache_dir,
            streaming=config.streaming
        )
        # Process and validate data
        return processed_data
    except Exception as e:
        raise DatasetLoadError(f"Failed to load PeerRead: {e}")
```

### Level 4: Syntax & Style validation

```bash
make ruff  
make type_check
# Expected: No errors. Fix any issues before proceeding.
```

### Level 5: Unit Tests validation

```bash
# Run and iterate until passing:
uv run pytest tests/datasets/test_peerread_loader.py -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 6: Integration Test

```bash
# Test the dataset loading in context
uv run python -c "
from app.datasets.peerread import load_peerread_dataset
from app.config.config_app import PEERREAD_CONFIG_FILE
from app.utils.load_configs import load_config
from app.datamodels.peerread_models import PeerReadConfig

config = load_config(PEERREAD_CONFIG_FILE, PeerReadConfig)
data = load_peerread_dataset(config)
print(f'Loaded {len(data)} venues with papers')
"

# Expected: Success message with data counts
# If error: Check logs and debug loading process
```

## Final Validation Checklist

- [ ] All tests pass: `uv run pytest tests/datasets/ -v`
- [ ] No linting errors: `make ruff`
- [ ] No type errors: `make type_check`
- [ ] Manual loading test successful
- [ ] Configuration loads without errors  
- [ ] Data models validate sample data correctly
- [ ] Batch processing works for large datasets
- [ ] Integration with existing data/ directory structure

## Anti-Patterns to Avoid

- ❌ Don't reinvent dataset loading - use HuggingFace datasets API
- ❌ Don't ignore missing fields - handle with Optional types gracefully
- ❌ Don't load entire dataset at once - implement batch processing
- ❌ Don't skip field validation - use Pydantic validators for data integrity
- ❌ Don't hardcode venue names - make configurable via JSON
- ❌ Don't ignore licensing constraints - use HuggingFace for proper access

---

**PRP Confidence Score: 9/10**

This PRP provides comprehensive context from both codebase analysis and external research, follows established patterns, includes executable validation gates, and addresses the key challenges of dataset integration, performance, and configuration management for successful one-pass implementation.