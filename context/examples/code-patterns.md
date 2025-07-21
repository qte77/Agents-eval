# Code Pattern Examples

**Purpose**: Reference guide for agents showing preferred coding patterns in the agents-eval codebase.

## Pydantic Model Usage

### ✅ Good: Proper Model Definition
```python
from src.app.datamodels.base import BaseModel

class AgentRequest(BaseModel):
    query: str
    max_tokens: int = 1000
    provider: str = "openai"
    
    # Reason: Validation ensures data integrity at runtime
    class Config:
        validate_assignment = True
```

### ❌ Bad: Direct Dictionary Usage
```python
# Avoid: No validation, prone to typos and runtime errors
request = {"query": "test", "max_tokens": "invalid", "provider": None}
```

## Import Structure

### ✅ Good: Absolute Imports
```python
# Use absolute imports within the project
from src.app.agents.agent_system import get_manager
from src.app.datamodels.agent_models import AgentResponse
from src.app.utils.error_messages import format_validation_error
```

### ❌ Bad: Relative Imports
```python
# Avoid: Fragile and causes import conflicts
from ..agent_system import get_manager
from ...datamodels import AgentResponse
```

## Error Handling

### ✅ Good: Specific Error Handling with Context
```python
try:
    result = await agent.process_query(request)
except ValidationError as e:
    # Reason: Specific error handling provides better debugging
    logger.error(f"Validation failed: {format_validation_error(e)}")
    raise AgentProcessingError("Invalid request format") from e
except TimeoutError as e:
    logger.warning(f"Agent timeout: {e}")
    raise AgentTimeoutError("Request took too long") from e
```

### ❌ Bad: Generic Error Handling
```python
try:
    result = await agent.process_query(request)
except Exception:
    # Avoid: Swallows all errors, makes debugging impossible
    return None
```

## Test Structure

### ✅ Good: Comprehensive Test with Clear Structure
```python
def test_agent_request_validation():
    """Test that AgentRequest validates input correctly.
    
    This test ensures data integrity at the model level.
    """
    # Arrange
    valid_data = {"query": "test", "max_tokens": 100}
    invalid_data = {"query": "", "max_tokens": -1}
    
    # Act & Assert - Valid case
    request = AgentRequest(**valid_data)
    assert request.query == "test"
    assert request.max_tokens == 100
    
    # Act & Assert - Invalid case
    with pytest.raises(ValidationError):
        AgentRequest(**invalid_data)
```

### ❌ Bad: Minimal Test without Context
```python
def test_request():
    r = AgentRequest(query="test")
    assert r.query == "test"
```

## Documentation Patterns

### ✅ Good: Complete Docstring with Examples
```python
def process_agent_query(request: AgentRequest) -> AgentResponse:
    """Process an agent query and return structured response.
    
    Args:
        request: Validated agent request containing query and parameters.
        
    Returns:
        AgentResponse: Structured response with result and metadata.
        
    Raises:
        AgentProcessingError: If query processing fails.
        ValidationError: If request format is invalid.
        
    Example:
        >>> request = AgentRequest(query="What is AI?", max_tokens=100)
        >>> response = process_agent_query(request)
        >>> print(response.content)
        "AI is artificial intelligence..."
    """
    # Implementation here
```

### ❌ Bad: Minimal or Missing Documentation
```python
def process_query(req):
    # Does something with the request
    return some_result
```

## Configuration Handling

### ✅ Good: Using Pydantic for Configuration
```python
from src.app.datamodels.config import ChatConfig

def load_agent_config(config_path: str) -> ChatConfig:
    """Load and validate agent configuration."""
    with open(config_path) as f:
        config_data = json.load(f)
    
    # Reason: Pydantic validates config structure
    return ChatConfig(**config_data)
```

### ❌ Bad: Direct JSON Access
```python
def load_config(path):
    with open(path) as f:
        # Avoid: No validation, runtime errors likely
        return json.load(f)
```

## Logging Patterns

### ✅ Good: Structured Logging with Context
```python
import logging

logger = logging.getLogger(__name__)

def process_request(request_id: str, query: str):
    logger.info(f"Processing request {request_id}", extra={
        "request_id": request_id,
        "query_length": len(query),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    try:
        result = perform_processing(query)
        logger.info(f"Request {request_id} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Request {request_id} failed: {e}", exc_info=True)
        raise
```

### ❌ Bad: Print Statements or Minimal Logging
```python
def process_request(request_id, query):
    print(f"Processing: {query}")  # Avoid: Not configurable, poor formatting
    result = perform_processing(query)
    return result
```