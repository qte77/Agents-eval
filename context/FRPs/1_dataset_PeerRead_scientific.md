# Feature Requirements Prompt (FRP): PeerRead Dataset Integration

This FRP is optimized for AI agents to implement PeerRead dataset integration with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

## 🚨 MANDATORY FIRST STEP: Context Gathering

**Before reading anything else, AI agents MUST:**

1. Read ALL files listed in "Required Context" section below
2. Validate understanding by summarizing key patterns found
3. **CRITICAL**: Test real external dependencies early (HuggingFace, download URLs)
4. Only proceed to implementation after context AND external validation complete

## Core Principles

1. **Context is King** 🔑
   - Gather ALL context BEFORE any implementation
   - Never assume - always verify against actual codebase
   - Include docstrings for files, classes, methods and functions
2. **Validation Loops**: Run tests/lints after each step
3. **Information Dense**: Use actual patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Follow AGENTS.md**: All rules in AGENTS.md override other guidance
6. **BDD/TDD Approach**: Behavior → Tests → Implementation → Iterate
7. **Keep it Simple**: MVP first, not full-featured production

## 🔑 Required Context (READ ALL BEFORE PROCEEDING)

### STEP 1: Essential Files to Read First

```yaml
MUST_READ_FIRST:
- file: context/config/paths.md
  action: Cache all $VARIABLE definitions
  critical: All paths used throughout this template

- file: AGENTS.md
  action: Review all rules and patterns
  critical: Project conventions that override defaults

- file: pyproject.toml
  action: Note available dependencies
  critical: Never assume libraries exist
```

### STEP 2: Feature-Specific Context

```yaml
REQUIRED_CONTEXT:
- file: src/app/agents/agent_system.py
  why: Core agent architecture and delegation patterns
  read_for: Agent tool integration patterns, manager delegation, PydanticAI usage

- file: src/app/datamodels/app_models.py
  why: Existing Pydantic models for structured data
  read_for: Model patterns to follow, ResearchResult/AnalysisResult structure

- file: src/app/utils/load_configs.py
  why: Configuration loading patterns
  read_for: Generic config loader pattern using Pydantic validation

- file: src/app/config/config_chat.json
  why: Existing configuration structure
  read_for: JSON configuration format and organization

- file: tests/agents/test_agent_system.py
  why: Testing patterns for agent functionality
  read_for: Agent testing approach, mocking patterns

- url: https://huggingface.co/datasets/allenai/peer_read
  why: Primary PeerRead dataset source via HuggingFace
  critical: Preferred method using existing infrastructure over custom download

- url: https://github.com/allenai/PeerRead/tree/master/data
  why: Fallback - PeerRead dataset structure and format if HuggingFace unavailable
  critical: Understanding actual data schema for proper models

- url: https://arxiv.org/abs/1804.09635
  why: PeerRead paper methodology and evaluation approach
  critical: Domain knowledge for proper evaluation metrics
```

### STEP 3: Current Project Structure

```bash
src/
├── app/
│   ├── agents/
│   │   └── agent_system.py        # Core multi-agent orchestration
│   ├── config/
│   │   ├── config_chat.json       # Agent provider configurations
│   │   └── config_eval.json       # Evaluation metrics
│   ├── datamodels/
│   │   └── app_models.py          # Pydantic data models
│   └── utils/
│       ├── error_messages.py      # Predefined error functions
│       └── load_configs.py        # Configuration loading utilities
├── datasets/                      # Empty - for benchmark datasets
└── gui/
    └── [streamlit files]
tests/
├── agents/
│   └── test_agent_system.py       # Agent system tests
└── [other test modules]
```

### STEP 4: Planned File Structure

```bash
# New files following $DEFAULT_PATHS_MD structure and AGENTS.md rules
src/app/utils/
└── datasets_peerread.py          # PeerRead dataset utilities (< 500 lines)

src/app/config/
└── config_datasets.json          # Dataset configurations

src/app/datamodels/
└── peerread_models.py            # PeerRead-specific Pydantic models

tests/utils/
└── test_datasets_peerread.py     # Comprehensive tests

src/datasets/
└── peerread/                     # Actual dataset files (downloaded)
    ├── train/
    ├── test/
    └── dev/
```

### STEP 5: Critical Project Patterns

```python
# CRITICAL patterns AI must follow:
# 1. All data models use Pydantic BaseModel in $DATAMODELS_PATH
# 2. Files must not exceed 500 lines (refactor if approaching)
# 3. All functions/classes need Google-style docstrings
# 4. PydanticAI agents follow specific initialization patterns
# 5. Error handling uses project-defined error functions

# Agent Tool Integration Pattern (from agent_system.py):
@manager_agent.tool
async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:
    """Delegate research task to ResearchAgent."""
    result = await research_agent.run(query, usage=ctx.usage)
    return _validate_model_return(str(result.output), ResearchResult)

# Configuration Loading Pattern (from load_configs.py):
def load_config(config_path: str | Path, data_model: type[BaseModel]) -> BaseModel:
    """Generic configuration loader that validates against any Pydantic model."""
    
# Data Model Pattern (from app_models.py):
class ResearchResult(BaseModel):
    """Research findings with sources and analysis."""
    topic: str = Field(description="Research topic or query")
    findings: list[str] = Field(description="Key research findings")
    sources: list[str] = Field(description="Source URLs or references")

# Error handling: Use functions from ${APP_PATH}/utils/error_messages.py or add new ones
# Available dependencies: datasets>=4.0.0, requests>=2.32.3 (test), pydantic>=2.10.6
```

## When to Stop and Ask Humans

**STOP immediately if:**

- Required files/paths don't exist
- Conflicting instructions in AGENTS.md
- Architecture changes needed
- Security implications unclear
- PeerRead dataset access restrictions unclear

## Goal

**What specific functionality should exist after implementation?**

Implement a robust PeerRead dataset integration that enables the Multi-Agent System to evaluate scientific paper review quality by:

1. **Download Management**: Automated download and caching of PeerRead dataset
2. **Data Access**: Structured access to papers, reviews, and metadata via Pydantic models
3. **Agent Integration**: Tools for agents to request papers and evaluate their reviews against ground truth
4. **Evaluation Framework**: Metrics to compare agent-generated reviews with PeerRead annotations

**Success Definition:** Provide functional tests and logic code implementation which integrates seamlessly with existing agent system for scientific paper review evaluation.

## Why

- **Business Value:** Enables quantitative evaluation of agent review quality against academic peer review standards
- **Integration Value:** Provides benchmark dataset for Multi-Agent System evaluation pipeline
- **Problem Solved:** Lack of standardized evaluation data for scientific review quality assessment

## What

**Scope:** PeerRead dataset download, loading, structured access, and integration with existing agent evaluation system

### Success Criteria

- [ ] Dataset can be downloaded programmatically with progress tracking and error recovery
- [ ] Dataset can be loaded into structured Pydantic models for type-safe access
- [ ] Papers can be queried by ID, venue, or content filters
- [ ] Agent review results can be compared against ground truth reviews with similarity metrics
- [ ] Integration with existing agent system via tools and configuration
- [ ] Comprehensive test coverage including download, loading, and evaluation workflows

## Implementation Plan

### Implementation Tasks (Follow AGENTS.md BDD/TDD)

```yaml
Task 1: Write Tests First (TDD)
CREATE: tests/utils/test_datasets_peerread.py
ACTION: Define test cases for download, loading, querying, and evaluation
PATTERN: Follow existing test patterns in tests/agents/test_agent_system.py
FOCUS: Mock external dependencies, test business logic thoroughly
CRITICAL: Include explicit download validation tests during implementation

Task 2: Validate HuggingFace Integration
PREFER: Use HuggingFace datasets library for data access
FALLBACK: Custom download implementation only if HuggingFace unavailable
VALIDATE: Test real HuggingFace dataset access early in implementation
VERIFY: Actual data structure matches expected models before full implementation

Task 3: Create Data Models
CREATE: src/app/datamodels/peerread_models.py
ACTION: Pydantic models for papers, reviews, metadata, and evaluation results
BASE_ON: Real HuggingFace dataset structure validation
EXAMPLE: |
  class PeerReadPaper(BaseModel):
      """Scientific paper from PeerRead dataset."""
      paper_id: str = Field(description="Unique paper identifier")
      title: str = Field(description="Paper title")
      abstract: str = Field(description="Paper abstract")
      venue: str = Field(description="Publication venue")
      reviews: list[PeerReadReview] = Field(description="Peer reviews")

Task 4: Configuration Management
CREATE: src/app/config/config_datasets.json
ACTION: Dataset-specific configuration using existing config pattern
PATTERN: Follow config_chat.json structure with Pydantic validation
INCLUDE: HuggingFace dataset parameters and fallback URLs

Task 5: Core Dataset Utilities
CREATE: src/app/utils/datasets_peerread.py
ACTION: HuggingFace integration first, then cache, load, and query functionality
PATTERN: Follow AGENTS.md patterns, < 500 lines, comprehensive docstrings
PRIORITY: Use existing ecosystem tools before custom implementation

Task 6: Agent System Integration
MODIFY: src/app/agents/agent_system.py
ACTION: Add PeerRead evaluation tools to manager agent
PATTERN: Follow existing @manager_agent.tool delegation pattern

Task 7: Integration Testing with Real Dependencies
ACTION: End-to-end testing with actual HuggingFace dataset
VERIFY: Full workflow from dataset access to evaluation works correctly
REQUIRED: Test download/access functionality explicitly during implementation
DOCUMENT: Real integration test results for future reference
```

### Integration Points

```yaml
AGENT_SYSTEM:
  - modify: src/app/agents/agent_system.py
  - add: @manager_agent.tool for PeerRead paper evaluation
  - pattern: Follow delegate_research pattern for consistency
  
CLI:
  - modify: src/app/main.py (if CLI commands needed)
  - add: Dataset management commands (download, status, clean)
  
CONFIG:
  - create: src/app/config/config_datasets.json
  - pattern: Use load_config utility with PeerReadConfig model
  
TEST_INTEGRATION:
  - ensure: All tests pass with `make test_all`
  - verify: No conflicts with existing agent functionality
  - check: Mock external dependencies properly
  
EVALUATION_SYSTEM:
  - integrate: With existing evaluation metrics in config_eval.json
  - add: PeerRead-specific similarity and quality metrics
```

## 🔄 Validation-Driven Implementation

### Step 1: Write Tests First (TDD with Real Validation)

```python
# CREATE: tests/utils/test_datasets_peerread.py
# Follow existing test patterns in the project
# CRITICAL: Include real external dependency testing during implementation

import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from src.app.utils.datasets_peerread import (
    PeerReadDownloader, 
    PeerReadLoader,
    evaluate_review_similarity
)
from src.app.datamodels.peerread_models import (
    PeerReadPaper, 
    PeerReadReview,
    PeerReadConfig
)

# IMPLEMENTATION REQUIREMENT: Test real HuggingFace access during development
def test_huggingface_dataset_access_real():
    """Test actual HuggingFace dataset access (run during implementation only).
    
    This test validates real external dependency during development.
    Mock for CI/CD but run real test during implementation.
    """
    # IMPLEMENTATION: Run this test with real HuggingFace access
    # to validate dataset structure before full implementation
    loader = PeerReadLoader()
    try:
        # Test actual HuggingFace access - replace with real call during dev
        sample_papers = loader.load_papers(split="train", use_hf=True)
        assert len(sample_papers) > 0
        assert isinstance(sample_papers[0], PeerReadPaper)
    except Exception as e:
        # Document failure and implement fallback
        pytest.skip(f"HuggingFace access failed: {e}. Fallback required.")

def test_download_dataset_success_mock():
    """Test successful dataset download with progress tracking (mocked for CI)."""
    # Arrange
    downloader = PeerReadDownloader(cache_dir="test_cache")
    
    # Act & Assert
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'test data']
        mock_response.headers = {'content-length': '9'}
        mock_get.return_value = mock_response
        
        result = downloader.download()
        assert result.success is True
        assert Path(result.cache_path).exists()

# IMPLEMENTATION REQUIREMENT: Test actual download during development
def test_download_functionality_real():
    """Test actual download functionality (run during implementation).
    
    CRITICAL: Must validate real download works during implementation.
    Mock for automated tests but verify real functionality first.
    """
    # IMPLEMENTATION: Test actual URL accessibility and download
    # Use small sample file to verify download mechanics work
    # Document results for future reference
    import requests
    
    # Test real URL accessibility during implementation
    test_url = "https://github.com/allenai/PeerRead/raw/master/data/acl_2017/train/reviews/104.json"
    try:
        response = requests.head(test_url, timeout=10)
        assert response.status_code == 200
        # Log success: "Real download URL validated during implementation"
    except Exception as e:
        pytest.skip(f"Real download test failed: {e}. Update implementation.")

def test_load_papers_validation():
    """Test paper loading with Pydantic validation."""
    # Arrange - use realistic data structure based on real validation
    test_data = {
        "paper_id": "test_001",
        "title": "Test Paper",
        "abstract": "Test abstract",
        "venue": "Test Venue",
        "reviews": []
    }
    
    # Act
    paper = PeerReadPaper.model_validate(test_data)
    
    # Assert
    assert paper.paper_id == "test_001"
    assert paper.title == "Test Paper"

def test_evaluate_review_similarity():
    """Test review similarity evaluation against ground truth."""
    # Arrange
    agent_review = "This paper presents solid methodology..."
    ground_truth = "The methodology is well-designed..."
    
    # Act
    similarity = evaluate_review_similarity(agent_review, ground_truth)
    
    # Assert
    assert 0.0 <= similarity <= 1.0
    assert isinstance(similarity, float)

def test_validation_error_handling():
    """Test proper error handling for invalid data."""
    with pytest.raises(ValidationError) as exc_info:
        PeerReadPaper.model_validate({"invalid": "data"})
    assert "required" in str(exc_info.value).lower()
```

### Step 2: Validate Test Structure

```bash
# Ensure tests are properly structured
make ruff
make type_check
# Fix any errors before proceeding
```

### Step 3: Implement Core Logic (HuggingFace First)

```python
# CREATE: src/app/utils/datasets_peerread.py
# Follow project patterns from context files
# PRIORITY: Use HuggingFace datasets library before custom implementation

from pathlib import Path
from typing import Optional
import json
from datasets import load_dataset  # Primary data source
import requests  # Fallback only

from src.app.datamodels.peerread_models import (
    PeerReadPaper, 
    PeerReadConfig,
    DownloadResult
)
from src.app.utils.error_messages import dataset_error_message

class PeerReadLoader:
    """Loads and queries PeerRead dataset using HuggingFace datasets.
    
    Primary implementation uses HuggingFace datasets library.
    Fallback to direct download only if HuggingFace unavailable.
    """
    
    def __init__(self, config: PeerReadConfig):
        """Initialize loader with configuration.
        
        Args:
            config: PeerRead dataset configuration.
        """
        self.config = config
        self.cache_dir = Path(config.cache_directory)
    
    def load_papers(self, split: str = "train", use_hf: bool = True) -> list[PeerReadPaper]:
        """Load papers from specified dataset split.
        
        Args:
            split: Dataset split ("train", "test", "dev").
            use_hf: Use HuggingFace datasets (preferred) vs custom download.
            
        Returns:
            List of validated PeerReadPaper models.
            
        Raises:
            DatasetLoadError: When dataset loading fails.
        """
        if use_hf:
            try:
                # IMPLEMENTATION: Use HuggingFace datasets/allenai/peer_read
                dataset = load_dataset("allenai/peer_read", split=split)
                # Convert to PeerReadPaper models with validation
                # Implementation with Pydantic validation
                pass
            except Exception as e:
                # Log HuggingFace failure, attempt fallback
                pass
        
        # Fallback: Custom download implementation
        return self._load_papers_custom(split)
    
    def _load_papers_custom(self, split: str) -> list[PeerReadPaper]:
        """Fallback: Load papers from custom download.
        
        Only used when HuggingFace datasets unavailable.
        """
        # Custom implementation as fallback
        pass

class PeerReadDownloader:
    """Downloads PeerRead dataset directly (fallback only).
    
    Use only when HuggingFace datasets unavailable.
    Handles download, caching, and integrity verification.
    """
    
    def download(self) -> DownloadResult:
        """Download PeerRead dataset with progress tracking.
        
        Returns:
            DownloadResult: Download status and cached file paths.
            
        Raises:
            DatasetDownloadError: When download fails or is corrupted.
        """
        try:
            # Implementation following project error handling patterns
            # REQUIREMENT: Must test actual download during implementation
            # Use requests library from test dependencies
            pass
        except Exception as e:
            raise dataset_error_message("download_failed", str(e))
```

### Step 4: Real External Dependency Validation (Critical)

```bash
# MANDATORY: Test real external dependencies during implementation
# Run these tests during development, not just after implementation

# 1. Validate HuggingFace dataset access
python -c "from datasets import load_dataset; ds = load_dataset('allenai/peer_read', split='train[:5]'); print(f'Success: {len(ds)} samples loaded')"

# 2. Test actual download URL accessibility
curl -I "https://github.com/allenai/PeerRead/raw/master/data/acl_2017/train/reviews/104.json"

# 3. Document real test results for future reference
echo "[$(date -u "+%Y-%m-%dT%H:%M:%SZ")] External dependency validation completed" >> validation_log.txt
```

### Step 5: Validate Implementation

```bash
# Run validation after real dependency testing
make ruff          # Code formatting and linting
make type_check    # Static type checking
# Fix all errors before proceeding to tests
```

### Step 6: Run and Fix Tests (Including Real Tests)

```bash
# PRIORITY: Run real external dependency tests during implementation
uv run pytest tests/utils/test_datasets_peerread.py::test_huggingface_dataset_access_real -v
uv run pytest tests/utils/test_datasets_peerread.py::test_download_functionality_real -v

# Then run all tests
uv run pytest tests/utils/test_datasets_peerread.py -v
make test_all

# If tests fail:
# 1. Read the error message carefully
# 2. Understand the root cause
# 3. Fix the implementation (never mock to pass)
# 4. Document real test results
# 5. Re-run tests
```

### Step 7: Integration Testing

```bash
# Test feature in application context
make run_cli ARGS="--help"  # Verify no CLI conflicts
# Test agent integration
uv run python -c "from src.app.utils.datasets_peerread import PeerReadLoader; print('Import successful')"

# Verify:
# - Feature works in real application context
# - No conflicts with existing functionality
# - Error handling works as expected
# - Real external dependencies accessible
```

## ✅ Final Validation

**Complete AGENTS.md pre-commit checklist, plus:**

- [ ] **PeerRead tests pass:** All download, loading, and evaluation tests
- [ ] **Agent integration works:** Manager agent can use PeerRead tools
- [ ] **Manual verification:** `make run_cli` with PeerRead evaluation command
- [ ] **No import conflicts:** No naming conflicts with datasets library
- [ ] **Configuration loads:** PeerRead config validates and loads correctly
- [ ] **HuggingFace integration:** Primary data access via HuggingFace datasets works
- [ ] **Real download testing:** Explicit validation of download functionality during implementation
- [ ] **Ecosystem integration:** Verified existing tools used before custom implementation

## ✅ Quality Evaluation Framework

**Updated after implementation learnings** - rate FRP readiness using AGENTS.md framework:

- **Context Completeness**: 10/10 (comprehensive codebase analysis, real external dependency validation, HuggingFace research)
- **Implementation Clarity**: 9/10 (clear tasks, prioritized HuggingFace integration, explicit testing requirements)
- **Requirements Alignment**: 10/10 (follows AGENTS.md rules, incorporates learned patterns, addresses anti-patterns)
- **Success Probability**: 9/10 (detailed tests, real dependency validation, documented learnings)

**All scores exceed AGENTS.md minimum thresholds - proceed with confidence based on implementation learnings.**

## 🚫 Feature-Specific Anti-Patterns

**Beyond AGENTS.md anti-patterns, avoid:**

- ❌ **Creating `src/app/datasets/` module:** Conflicts with HuggingFace datasets library
- ❌ **Assuming dataset availability:** Always handle download failures gracefully
- ❌ **Hardcoded file paths:** Use configuration and $VARIABLE patterns
- ❌ **Blocking downloads:** Implement async download with progress tracking
- ❌ **Missing validation:** All external data must use Pydantic validation
- ❌ **Ignoring caching:** Implement proper cache management to avoid re-downloads
- ❌ **Custom implementation first:** Always research existing ecosystem solutions (HuggingFace) before custom development
- ❌ **Mocking without real validation:** Must test actual external dependencies during implementation
- ❌ **Skipping download verification:** Explicitly test download functionality with real network requests
- ❌ **Assuming API structure:** Validate actual data formats before implementing data models

**Follow AGENTS.md escalation process when in doubt.**

## Implementation Success Metrics

**Technical Metrics:**

- All tests pass (`make test_all`)
- Code quality passes (`make ruff`, `make type_check`)
- File size < 500 lines per file
- Full docstring coverage

**Functional Metrics:**

- **Primary**: HuggingFace datasets integration works (`allenai/peer_read`)
- **Fallback**: Dataset downloads successfully from PeerRead repository
- Papers load into Pydantic models without validation errors
- Agent system can query papers and evaluate reviews
- Similarity metrics provide meaningful comparison scores

**Integration Metrics:**

- No conflicts with existing agent functionality
- Configuration integrates with existing config system
- CLI commands work without breaking existing interface
- Performance acceptable for typical evaluation workflows

**External Dependency Metrics (Critical):**

- Real HuggingFace dataset access validated during implementation
- Actual download functionality tested with network requests
- External API structure verified before model implementation
- Real integration test results documented for future reference
