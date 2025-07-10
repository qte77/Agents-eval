# Product Requirements Prompt (PRP): PeerRead Dataset Integration

## Purpose

This PRP provides comprehensive context for implementing PeerRead dataset integration into the Multi-Agent System evaluation framework. The integration will enable benchmarking of scientific paper review quality using existing agent architectures (single LLM or multi-agentic Manager → Researcher → Analyst → Synthesizer).

## Core Principles

1. **Context is King**: All necessary documentation, examples, and caveats included
2. **Validation Loops**: Executable tests/lints for iterative refinement
3. **Information Dense**: Uses patterns from existing codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in AGENTS.md
6. **Top-to-Bottom**: BDD and TDD approach

## Goal

Implement PeerRead dataset integration as a benchmark for the Multi-Agent System evaluation framework. The data must be made available for other components of this project, enabling benchmarking of scientific paper review quality using the existing agent architecture.

Provide functional tests and logic code implementation which can be integrated with other components.

## Why

- **Business value**: Enables scientific paper review quality benchmarking
- **Integration**: Seamlessly integrates with existing agent evaluation framework
- **Problems solved**: Provides standardized dataset for evaluating agent performance on peer review tasks
- **Target users**: Researchers evaluating agent systems on scientific review tasks

## What

User-visible behavior and technical requirements:
- Load PeerRead dataset from JSON files
- Provide structured data models for papers, reviews, and decisions
- Enable agent task generation from dataset entries
- Support evaluation metrics for review quality assessment

### Success Criteria

- [ ] PeerRead dataset loads successfully with proper validation
- [ ] Data models follow existing Pydantic patterns in the codebase
- [ ] Agent tasks can be generated from dataset entries
- [ ] Integration with existing evaluation framework works
- [ ] Performance is acceptable for dataset size (14.7K papers, 10.7K reviews)
- [ ] All tests pass with >90% coverage
- [ ] Configuration follows existing JSON patterns

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: https://arxiv.org/abs/1804.09635
  why: Official PeerRead dataset paper with structure and use cases
  
- url: https://github.com/allenai/PeerRead
  why: Official repository with implementation examples and data format
  
- url: https://github.com/allenai/PeerRead/tree/master/data
  why: Data organization and file structure patterns
  
- url: https://huggingface.co/datasets/allenai/peer_read
  why: Alternative loading method and dataset documentation
  
- file: /workspaces/Agents-eval/src/app/config/data_models.py
  why: Existing Pydantic model patterns to follow
  
- file: /workspaces/Agents-eval/src/app/utils/load_configs.py
  why: Generic configuration loading pattern to mirror
  
- file: /workspaces/Agents-eval/src/app/config/config_eval.json
  why: Existing evaluation configuration pattern
  
- file: /workspaces/Agents-eval/tests/test_provider_config.py
  why: Test patterns and structure to follow
```

### Current Codebase Tree

```bash
src/
├── app/
│   ├── agents/
│   │   └── agent_system.py          # Multi-agent orchestration
│   ├── config/
│   │   ├── data_models.py          # Pydantic models (CRITICAL)
│   │   ├── config_eval.json        # Evaluation configuration
│   │   └── config_chat.json        # Chat configuration
│   ├── evals/
│   │   └── metrics.py              # Evaluation metrics
│   ├── utils/
│   │   └── load_configs.py         # Generic config loader (CRITICAL)
│   └── main.py                     # CLI entry point
├── gui/
│   └── (Streamlit components)
tests/
├── test_provider_config.py         # Test patterns
├── test_agent_system.py
└── (other test files)
```

### Desired Codebase Tree with Files to Add

```bash
src/app/
├── datasets/                        # NEW: Dataset integration
│   ├── __init__.py
│   ├── peerread_loader.py          # NEW: PeerRead data loading
│   └── peerread_models.py          # NEW: PeerRead Pydantic models
├── config/
│   └── config_peerread.json        # NEW: PeerRead configuration
data/                               # NEW: Dataset storage
├── peerread/                       # NEW: PeerRead dataset files
│   ├── train/
│   ├── dev/
│   └── test/
tests/
├── test_peerread_loader.py         # NEW: PeerRead loader tests
├── test_peerread_models.py         # NEW: PeerRead model tests
└── test_peerread_integration.py    # NEW: Integration tests
```

### Known Gotchas of Our Codebase & Library Quirks

```python
# CRITICAL: Use existing load_config function from utils/load_configs.py
# Pattern: load_config(config_path: str | Path, data_model: type[BaseModel]) -> BaseModel

# CRITICAL: All data models must inherit from BaseModel and follow existing patterns
# Pattern: class NewModel(BaseModel): with proper docstrings and type hints

# CRITICAL: Use ConfigDict(arbitrary_types_allowed=True) for complex types
# Pattern: model_config = ConfigDict(arbitrary_types_allowed=True)

# CRITICAL: Follow existing test patterns in tests/ directory
# Pattern: pytest with happy path, edge cases, error handling

# CRITICAL: PeerRead JSON files can be large (14.7K papers)
# Consider memory usage and performance for large datasets

# CRITICAL: Handle missing fields gracefully (some JSON fields are optional)
# Pattern: Optional[type] for nullable fields

# CRITICAL: Use pathlib.Path for file paths, not strings
# Pattern: from pathlib import Path
```

## Implementation Blueprint

### Data Models and Structure

Create the core data models to ensure type safety and consistency:

```python
# src/app/datasets/peerread_models.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from pathlib import Path

class PeerReadSection(BaseModel):
    """Represents a section of a scientific paper."""
    heading: Optional[str] = None
    text: str

class PeerReadReference(BaseModel):
    """Represents a reference in a scientific paper."""
    title: str
    author: List[str]
    venue: Optional[str] = None
    year: int
    citeRegEx: str
    shortCiteRegEx: str

class PeerReadReferenceMention(BaseModel):
    """Represents a reference mention in paper text."""
    referenceID: int
    context: str
    startOffset: int
    endOffset: int

class PeerReadPaper(BaseModel):
    """Represents a scientific paper from PeerRead dataset."""
    name: str
    metadata: Dict[str, Any]
    references: List[PeerReadReference]
    referenceMentions: List[PeerReadReferenceMention]
    year: int
    abstractText: str
    creator: str
    title: Optional[str] = None
    authors: List[str] = []
    sections: List[PeerReadSection] = []
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class PeerReadReview(BaseModel):
    """Represents a peer review from PeerRead dataset."""
    paper_id: str
    review_text: str
    rating: Optional[int] = None
    recommendation: Optional[str] = None
    aspects: Dict[str, Any] = {}

class PeerReadAgentTask(BaseModel):
    """Agent task format for PeerRead evaluation."""
    paper_id: str
    title: str
    abstract: str
    agent_task: str
    expected_output: Dict[str, Any]

class PeerReadConfig(BaseModel):
    """Configuration for PeerRead dataset loading."""
    data_path: Path
    venues: List[str]
    splits: List[str]
    max_papers: Optional[int] = None
    load_reviews: bool = True
    load_references: bool = True
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

### List of Tasks to Complete (in order)

```yaml
Task 1: Create PeerRead Data Models
CREATE src/app/datasets/__init__.py:
  - EMPTY file to make it a Python package

CREATE src/app/datasets/peerread_models.py:
  - IMPLEMENT PeerRead data models as shown above
  - FOLLOW existing Pydantic patterns from src/app/config/data_models.py
  - INCLUDE proper docstrings and type hints

Task 2: Create PeerRead Configuration
CREATE src/app/config/config_peerread.json:
  - MIRROR pattern from src/app/config/config_eval.json
  - INCLUDE data_path, venues, splits, performance settings
  - FOLLOW existing JSON configuration structure

Task 3: Create PeerRead Data Loader
CREATE src/app/datasets/peerread_loader.py:
  - IMPLEMENT PeerReadLoader class
  - MIRROR pattern from src/app/utils/load_configs.py
  - INCLUDE methods: load_papers, load_reviews, generate_agent_tasks
  - HANDLE file I/O errors gracefully
  - IMPLEMENT lazy loading for performance

Task 4: Update Data Models Registry
MODIFY src/app/config/data_models.py:
  - ADD import for PeerReadConfig
  - PRESERVE existing model patterns
  - ENSURE consistency with existing models

Task 5: Create Dataset Storage Structure
CREATE data/peerread/ directory structure:
  - MIRROR pattern from PeerRead GitHub repository
  - INCLUDE placeholder files for train/dev/test splits
  - DOCUMENT expected file structure in README

Task 6: Write Unit Tests
CREATE tests/test_peerread_models.py:
  - FOLLOW pattern from tests/test_provider_config.py
  - TEST model validation, serialization, edge cases
  - INCLUDE happy path, validation errors, optional fields

CREATE tests/test_peerread_loader.py:
  - TEST data loading functionality
  - INCLUDE file not found, invalid JSON, performance tests
  - MOCK file system operations for testing

Task 7: Write Integration Tests
CREATE tests/test_peerread_integration.py:
  - TEST end-to-end dataset loading
  - TEST agent task generation
  - TEST integration with existing evaluation framework

Task 8: Update Main Configuration
MODIFY src/app/main.py:
  - ADD command-line options for PeerRead dataset
  - PRESERVE existing functionality
  - INCLUDE proper error handling and logging
```

### Integration Points

```yaml
CONFIG:
  - add to: src/app/config/config_peerread.json
  - pattern: Follow existing JSON configuration structure
  
DATA_MODELS:
  - add to: src/app/config/data_models.py
  - pattern: Import PeerReadConfig and related models
  
EVALUATION:
  - integrate with: src/app/evals/metrics.py
  - pattern: Add PeerRead-specific evaluation metrics
  
AGENT_SYSTEM:
  - integrate with: src/app/agents/agent_system.py
  - pattern: Support PeerRead agent tasks as input
  
CLI:
  - integrate with: src/app/main.py
  - pattern: Add --dataset peerread command-line option
```

## Validation Loop

### Level 1: Write Tests

```python
# tests/test_peerread_models.py
def test_peerread_paper_validation():
    """Test PeerReadPaper model validation with valid data."""
    paper_data = {
        "name": "test_paper.pdf",
        "metadata": {"source": "ACL"},
        "references": [],
        "referenceMentions": [],
        "year": 2017,
        "abstractText": "This is a test abstract",
        "creator": "Test Author"
    }
    paper = PeerReadPaper.model_validate(paper_data)
    assert paper.name == "test_paper.pdf"
    assert paper.year == 2017

def test_peerread_paper_optional_fields():
    """Test optional fields are handled correctly."""
    minimal_data = {
        "name": "minimal.pdf",
        "metadata": {},
        "references": [],
        "referenceMentions": [],
        "year": 2017,
        "abstractText": "Abstract",
        "creator": "Creator"
    }
    paper = PeerReadPaper.model_validate(minimal_data)
    assert paper.title is None
    assert paper.authors == []

def test_peerread_config_validation():
    """Test PeerReadConfig validation."""
    config_data = {
        "data_path": "/path/to/data",
        "venues": ["ACL", "NIPS"],
        "splits": ["train", "dev", "test"],
        "max_papers": 1000,
        "load_reviews": True,
        "load_references": True
    }
    config = PeerReadConfig.model_validate(config_data)
    assert len(config.venues) == 2
    assert config.max_papers == 1000

# tests/test_peerread_loader.py
def test_load_papers_success():
    """Test successful paper loading."""
    # Mock file system and test actual loading
    pass

def test_load_papers_file_not_found():
    """Test graceful handling of missing files."""
    # Test FileNotFoundError handling
    pass

def test_generate_agent_tasks():
    """Test agent task generation from papers."""
    # Test task format matches expected structure
    pass
```

### Level 2: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
make ruff
make type_check
# Expected: No errors. If errors, READ the error and fix.
```

### Level 3: Implement Logic Code

```python
# src/app/datasets/peerread_loader.py
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import logging
from .peerread_models import PeerReadPaper, PeerReadConfig, PeerReadAgentTask

logger = logging.getLogger(__name__)

class PeerReadLoader:
    """Loads and manages PeerRead dataset for agent evaluation."""
    
    def __init__(self, config: PeerReadConfig):
        """Initialize with configuration."""
        self.config = config
        self.papers_cache: Dict[str, PeerReadPaper] = {}
    
    def load_papers(self, split: str = "train") -> List[PeerReadPaper]:
        """Load papers from specified split."""
        # Implementation following existing patterns
        pass
    
    def generate_agent_tasks(self, papers: List[PeerReadPaper]) -> List[PeerReadAgentTask]:
        """Generate agent tasks from papers."""
        # Implementation for task generation
        pass
```

### Level 4: Syntax & Style

```bash
# Run these AFTER implementing - fix any errors before proceeding
make ruff
make type_check
# Expected: No errors. If errors, READ the error and fix.
```

### Level 5: Unit Tests

```bash
# Run and iterate until passing:
uv run pytest tests/test_peerread_models.py -v
uv run pytest tests/test_peerread_loader.py -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 6: Integration Test

```bash
# Test the complete integration
uv run python -c "
from src.app.datasets.peerread_loader import PeerReadLoader
from src.app.config.data_models import PeerReadConfig
from pathlib import Path

config = PeerReadConfig(
    data_path=Path('data/peerread'),
    venues=['ACL'],
    splits=['train', 'dev', 'test'],
    max_papers=10
)
loader = PeerReadLoader(config)
papers = loader.load_papers('train')
print(f'Loaded {len(papers)} papers successfully')
"

# Expected: "Loaded X papers successfully"
# If error: Check implementation and file paths
```

## Final Validation Checklist

- [ ] All tests pass: `uv run pytest tests/test_peerread_*.py -v`
- [ ] No linting errors: `make ruff`
- [ ] No type errors: `make type_check`
- [ ] Manual integration test successful
- [ ] Performance acceptable for large datasets
- [ ] Error cases handled gracefully
- [ ] Follows existing codebase patterns
- [ ] Documentation complete with docstrings

## Anti-Patterns to Avoid

- ❌ Don't create new loading patterns when load_config exists
- ❌ Don't skip Pydantic validation for performance
- ❌ Don't hardcode file paths - use configuration
- ❌ Don't load entire dataset into memory at once
- ❌ Don't ignore missing JSON fields - handle gracefully
- ❌ Don't use string paths instead of pathlib.Path
- ❌ Don't create models without proper docstrings
- ❌ Don't skip error handling for file operations

## Confidence Score

**9/10** - This PRP provides comprehensive context including:
- Detailed existing codebase patterns to follow
- Complete data model specifications
- Step-by-step implementation plan
- Comprehensive validation loops
- External documentation and examples
- Known gotchas and anti-patterns
- Performance considerations for large datasets

The high confidence comes from thorough analysis of existing patterns, detailed external research, and comprehensive validation strategy. The implementation should succeed in one pass with this level of context.