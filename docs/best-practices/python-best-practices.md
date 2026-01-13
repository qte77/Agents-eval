---
title: Python Best Practices
name: python-best-practices
description: Security-first Python coding patterns for production AI systems
purpose: Prevent security vulnerabilities, ensure type safety, maintain code quality
scope: Python coding standards, Pydantic models, async patterns, testing
created: 2026-01-13
updated: 2026-01-13
type: best-practices
audience: ["developers", "agents", "data-scientists"]
related: ["CONTRIBUTING.md", "AGENTS.md"]
quality_tags: ["#security", "#type-safety", "#pydantic", "#async"]
applies_to: ["src/app/", "tests/"]
---

## Security First (Non-Negotiable)

### 1. Secrets in Environment Variables Only

```python
# .env - NEVER commit
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_API_KEY=ghp_...
```

**Load via Pydantic BaseSettings:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppEnv(BaseSettings):
    """Load secrets from environment variables."""

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GITHUB_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Usage
config = AppEnv()
api_key = config.OPENAI_API_KEY  # ✅ Safe
```

```python
# ❌ NEVER hardcode credentials
api_key = "sk-abc123..."  # SECURITY BREACH
OPENAI_API_KEY = "sk-proj-..."  # NEVER
```

### 2. Input Validation & Sanitization

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    """Validate external input immediately."""

    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)
    query: str = Field(..., min_length=1, max_length=1000)

# ✅ Input validated before processing
def process_user_data(data: dict) -> UserInput:
    return UserInput(**data)  # Raises ValidationError if invalid
```

### 3. SQL Injection Prevention

```python
# ✅ Use parameterized queries
from sqlalchemy import text

query = text("SELECT * FROM users WHERE id = :user_id")
result = connection.execute(query, {"user_id": user_id})

# ❌ NEVER concatenate SQL strings
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL INJECTION RISK
```

### 4. Safe Deserialization

```python
import yaml

# ✅ Use SafeLoader for YAML
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# ❌ NEVER use pickle with untrusted data
import pickle
data = pickle.loads(untrusted_input)  # CODE EXECUTION RISK
```

---

## Type Annotations & Pydantic Models

### Modern Type Syntax (Python 3.10+)

```python
# ✅ Modern union syntax
def process_data(
    items: list[str],
    config: dict[str, int] | None = None,
    timeout: float | None = 30.0,
) -> str | None:
    """Process items with optional configuration."""
    ...

# ✅ Type aliases (Python 3.12+)
type UserPromptType = str | list[dict[str, str]] | None
type ResultType = dict[str, str | int | list[str]]

# ❌ Outdated typing module syntax
from typing import Optional, List, Dict
def old_style(items: List[str], config: Optional[Dict[str, int]]) -> Optional[str]:
    ...
```

### Pydantic Models with Validation

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator

class GeneratedReview(BaseModel):
    """Structured review data with validation."""

    impact: int = Field(..., ge=1, le=5, description="Impact rating (1-5)")
    substance: int = Field(..., ge=1, le=5, description="Substance rating")
    comments: str = Field(..., min_length=100, description="Detailed comments")

    # Allow non-Pydantic types (e.g., OpenAI client, Model instances)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("comments")
    def validate_comments(cls, v: str) -> str:
        """Ensure comments are substantive."""
        if len(v.strip()) < 100:
            raise ValueError("Comments must be at least 100 characters")
        return v
```

### Pydantic for Configuration

```python
from pydantic import BaseModel, HttpUrl

class ProviderConfig(BaseModel):
    """Configuration for model provider."""

    model_name: str
    base_url: HttpUrl  # Validates URL format
    usage_limits: int | None = None
    max_content_length: int | None = 15000

class ChatConfig(BaseModel):
    """Application configuration."""

    providers: dict[str, ProviderConfig]
    inference: dict[str, str | int]
    prompts: dict[str, str]
```

---

## Error Handling & Logging

### Error Message Factory Pattern

```python
# src/app/utils/error_messages.py
from pathlib import Path

def file_not_found(file_path: str | Path) -> str:
    """Generate error message for missing file."""
    return f"File not found: {file_path}"

def invalid_json(error: str) -> str:
    """Generate error message for invalid JSON."""
    return f"Invalid JSON: {error}"

def api_connection_error(error: str) -> str:
    """Generate error message for API connection error."""
    return f"API connection error: {error}"
```

### Proper Exception Handling

```python
import json
from app.utils.error_messages import file_not_found, invalid_json
from app.utils.log import logger

try:
    with open(config_path) as f:
        config_data = json.load(f)
except FileNotFoundError as e:
    msg = file_not_found(config_path)
    logger.error(msg)
    raise FileNotFoundError(msg) from e  # ✅ Chain exception
except json.JSONDecodeError as e:
    msg = invalid_json(str(e))
    logger.error(msg)
    raise json.JSONDecodeError(msg, str(config_path), 0) from e
except Exception as e:
    msg = f"Unexpected error: {e}"
    logger.exception(msg)  # ✅ Logs full traceback
    raise

# ❌ NEVER use bare except
try:
    risky_operation()
except:  # Catches SystemExit, KeyboardInterrupt - BAD
    pass
```

### Logging with Loguru

```python
from loguru import logger
from app.config.config_app import LOGS_PATH

# Configure logger (in src/app/utils/log.py)
logger.add(
    f"{LOGS_PATH}/{{time}}.log",
    rotation="1 MB",
    retention="7 days",
    compression="zip",
)

# Usage
logger.info("Processing started")
logger.warning(f"Slow operation: {duration:.2f}s")
logger.error(f"Failed to process {item_id}: {error}")
logger.exception("Unhandled exception occurred")  # Includes traceback

# ❌ NEVER use print() for logging
print("Debug info")  # No production visibility
```

---

## Import Organization

### Absolute Imports Only

```python
# ✅ CORRECT: Absolute imports
import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from app.config.config_app import PROJECT_NAME
from app.data_models.app_models import ChatConfig
from app.utils.error_messages import file_not_found
from app.utils.log import logger

# ❌ NEVER use relative imports
from .models import ChatConfig      # WRONG
from ..utils import logger          # WRONG
from ...config import PROJECT_NAME  # WRONG
```

### Import Order (enforced by ruff)

1. **Standard library** imports
2. **Third-party** library imports
3. **Local application** imports (from `app.`)

Separate each group with a blank line.

---

## Async Patterns

### Async Function Definition

```python
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from app.utils.log import logger

async def run_agent(
    agent: Agent,
    query: str,
    usage_limits: UsageLimits | None = None,
) -> dict:
    """Run agent with async/await pattern."""
    try:
        logger.info("Waiting for model response...")
        result = await agent.run(user_prompt=query, usage=usage_limits)
        logger.info(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise
```

### Timeout Handling

```python
import asyncio

async def evaluate_with_timeout(
    data: dict,
    timeout: float = 30.0
) -> dict | None:
    """Execute evaluation with timeout protection."""
    try:
        async with asyncio.timeout(timeout):
            return await _run_evaluation(data)
    except TimeoutError:
        logger.error(f"Evaluation timed out after {timeout}s")
        return None
```

### Concurrent Execution

```python
async def process_multiple_items(items: list[str]) -> list[dict]:
    """Process multiple items concurrently."""
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results
```

---

## Testing Patterns

### Pytest Fixtures

```python
import pytest
import tempfile
import json
from pathlib import Path

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "version": "1.0.0",
        "providers": {"openai": {"model_name": "gpt-4"}},
    }

@pytest.fixture
def config_file(sample_config):
    """Temporary configuration file with cleanup."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_config, f)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()
```

### Mocking External Dependencies

```python
from unittest.mock import patch, AsyncMock
import pytest

@patch("app.agents.agent_system.get_api_key")
def test_agent_initialization(mock_get_api_key):
    """Test agent setup with mocked API key."""
    mock_get_api_key.return_value = (True, "test-key")

    agent = initialize_agent()

    assert agent is not None
    mock_get_api_key.assert_called_once()

# Async mock pattern
@pytest.mark.asyncio
async def test_async_evaluation():
    """Test async evaluation with mocked engine."""
    mock_engine = AsyncMock()
    mock_engine.evaluate.return_value = {"score": 0.85}

    result = await mock_engine.evaluate({"input": "test"})
    assert result["score"] == 0.85
```

### Test Organization

```python
# tests/evals/test_evaluation_pipeline.py

class TestPipelineInitialization:
    """Test pipeline initialization and configuration."""

    def test_load_config_success(self, config_file):
        """Test successful configuration loading."""
        ...

class TestTierExecution:
    """Test individual tier execution methods."""

    @pytest.mark.asyncio
    async def test_tier1_execution(self, pipeline):
        """Test Tier 1 execution."""
        ...

class TestErrorHandling:
    """Test error handling and fallback strategies."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self, pipeline):
        """Test timeout error handling."""
        ...
```

---

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Hardcoded API keys | Security breach | Use `BaseSettings` with `.env` |
| `Optional[str]` syntax | Outdated style | Use `str \| None` |
| `List[str]` annotation | Outdated style | Use `list[str]` |
| Relative imports | Import errors | Use absolute `from app.x import Y` |
| Bare `except:` | Hidden errors | Catch specific exceptions |
| Missing type hints | Type errors | Add annotations to all functions |
| Direct dict access | Runtime errors | Use Pydantic models |
| `print()` for logging | No production logs | Use `logger.info/error()` |
| Generic error messages | Hard to debug | Use error factory functions |
| Missing `from e` chain | Lost stack trace | Always chain: `raise ... from e` |
| No input validation | Security risks | Use Pydantic `Field()` constraints |
| String SQL queries | SQL injection | Use parameterized queries |

---

## Performance Best Practices

### Bottleneck Detection

```python
import time
from app.utils.log import logger

def detect_bottlenecks(tier_times: dict[str, float], total_time: float) -> None:
    """Identify performance bottlenecks in tier execution."""
    bottleneck_threshold = total_time * 0.4
    for tier, time_taken in tier_times.items():
        if time_taken > bottleneck_threshold:
            logger.warning(
                f"Performance bottleneck detected: {tier} took {time_taken:.2f}s "
                f"({time_taken/total_time*100:.1f}% of total time)"
            )
```

### Async Concurrency for I/O

```python
# ✅ Concurrent API calls
async def fetch_multiple_papers(paper_ids: list[str]) -> list[dict]:
    """Fetch multiple papers concurrently."""
    tasks = [fetch_paper(paper_id) for paper_id in paper_ids]
    return await asyncio.gather(*tasks)

# ❌ Sequential API calls (slow)
async def fetch_multiple_papers_slow(paper_ids: list[str]) -> list[dict]:
    """Slow sequential fetching."""
    results = []
    for paper_id in paper_ids:
        results.append(await fetch_paper(paper_id))  # Waits for each
    return results
```

---

## Checklist

### Security
- [ ] No hardcoded secrets or API keys in code
- [ ] All credentials loaded via `BaseSettings` from `.env`
- [ ] External input validated with Pydantic models
- [ ] SQL queries use parameterized statements
- [ ] YAML loaded with `SafeLoader`
- [ ] No `pickle` usage with untrusted data

### Type Safety
- [ ] All functions have type annotations
- [ ] Modern syntax used (`str | None`, `list[str]`)
- [ ] Pydantic models used for data validation
- [ ] `Field()` constraints defined for validation
- [ ] `ConfigDict` used when needed

### Code Quality
- [ ] Absolute imports only (`from app.x import Y`)
- [ ] Import order: stdlib → third-party → local
- [ ] Google-style docstrings on all functions/classes
- [ ] Error factory functions used for messages
- [ ] Specific exceptions caught (not bare `except:`)
- [ ] Exceptions chained with `raise ... from e`
- [ ] Loguru `logger` used (not `print()`)

### Testing
- [ ] Unit tests created for new functionality
- [ ] External dependencies mocked with `@patch`
- [ ] Async tests use `@pytest.mark.asyncio`
- [ ] Tests mirror `src/app/` structure in `tests/`
- [ ] Fixtures use cleanup (yield pattern)

### Validation
- [ ] `make validate` passes (ruff + pyright + pytest)
- [ ] No pyright errors in `src/app/`
- [ ] No ruff lint warnings
- [ ] All tests pass
