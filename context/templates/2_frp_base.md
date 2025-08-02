# Feature Requirements Prompt (FRP) Template

This template is optimized for AI agents to implement features with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

## 🚨 MANDATORY FIRST STEP: Context Gathering

**Before reading anything else, AI agents MUST:**

1. Read ALL files listed in "Required Context" section below
2. Validate understanding by summarizing key patterns found
3. Only proceed to implementation after context is complete

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
# AI Agent: Read these files and cache their contents
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
# Add your specific references here
REQUIRED_CONTEXT:
- file: [path/to/similar_feature.py]
  why: [Pattern to follow, gotchas to avoid]
  read_for: [Specific patterns or structures]

- file: $DATAMODELS_PATH/[relevant_model].py
  why: [Existing data structures to reference]
  read_for: [Model patterns to follow]

- url: [External documentation if needed]
  why: [Specific API or library patterns]
  critical: [Key insights that prevent errors]
```

### STEP 3: Current Project Structure

```bash
# Run: tree -I '__pycache__|*.pyc|.git' --dirsfirst
# Paste output here to show current structure
```

### STEP 4: Planned File Structure

```bash
# Show where new files will go (follow $DEFAULT_PATHS_MD structure)
# Example:
# $APP_PATH/[module]/
# ├── new_feature.py        # Main implementation (< 500 lines)
# └── new_feature_utils.py  # Helper functions if needed
# $TEST_PATH/[module]/
# └── test_new_feature.py   # Comprehensive tests
```

### STEP 5: Critical Project Patterns

```python
# CRITICAL patterns AI must follow:
# - All data models use Pydantic BaseModel in $DATAMODELS_PATH
# - Files must not exceed 500 lines (refactor if approaching)
# - All functions/classes need Google-style docstrings
# - PydanticAI agents follow specific initialization patterns
# - Error handling uses project-defined error functions

# Add your specific gotchas here:
# [Known library quirks or project-specific requirements]
# Error handling: Use functions from ${APP_PATH}/utils/error_messages.py or add new ones if not present but necessary. 
```

## When to Stop and Ask Humans

**STOP immediately if:**

- Required files/paths don't exist
- Conflicting instructions in AGENTS.md
- Architecture changes needed
- Security implications unclear

## Goal

**What specific functionality should exist after implementation?**

[Describe observable behavior and integration points. Be specific about the end state.]

**Success Definition:** Provide functional tests and logic code implementation which integrates seamlessly with existing components.

## Why

- **Business Value:** [Who benefits and how?]
- **Integration Value:** [What does this enable in the system?]
- **Problem Solved:** [Specific pain points addressed and for whom?]

## What

**Scope:** [User-visible behavior and technical requirements]

### Success Criteria

- [ ] [Specific functional requirement - testable]
- [ ] [Performance/quality requirement - measurable]
- [ ] [Integration requirement - verifiable]

## Implementation Plan

### Implementation Tasks (Follow AGENTS.md BDD/TDD)

```yaml
Task 1: Write Tests First (TDD)
CREATE: $TEST_PATH/[module]/test_[feature].py
ACTION: Define test cases that describe desired behavior
PATTERN: Follow existing test patterns in project

Task 2: Create Data Models (if needed)  
CREATE: $DATAMODELS_PATH/[feature]_models.py
ACTION: Pydantic models following AGENTS.md patterns
EXAMPLE: |
  class YourFeatureModel(BaseModel):
      """Brief description following AGENTS.md docstring requirements."""
      field_name: str = Field(description="Clear purpose")

Task 3: Implement Core Logic
CREATE: $APP_PATH/[module]/[feature].py
ACTION: Make tests pass with minimal viable implementation
PATTERN: Follow AGENTS.md coding patterns

Task 4: Integration
[Feature-specific integration steps]
```

### Integration Points

```yaml
# Specify exact integration needs
AGENT_SYSTEM:
  - modify: $APP_PATH/agents/[relevant_agent].py
  - add: New agent capabilities or tools
  
CLI:
  - modify: $APP_PATH/main.py
  - add: New command-line options
  
CONFIG:
  - check: Existing configuration files
  - add: Any new settings needed
  
TEST_INTEGRATION:
  - ensure: All tests pass with `make test_all`
  - verify: No conflicts with existing functionality
  
AGENT_SYSTEM:
  - verify: Integration with ${APP_PATH}/agents/agent_system.py
  - test: PydanticAI agent compatibility
  - check: No conflicts with existing agent workflows
```

## 🔄 Validation-Driven Implementation

### Step 1: Write Tests First (TDD)

```python
# CREATE: $TEST_PATH/[module]/test_[feature].py
# Follow existing test patterns in the project

def test_happy_path():
    """Test basic functionality works as expected."""
    # Arrange
    input_data = "valid_input"
    expected_status = "success"
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result.status == expected_status
    assert result.data is not None

def test_validation_error():
    """Test invalid input raises appropriate ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        feature_function("")
    assert "required" in str(exc_info.value)

def test_edge_cases():
    """Test edge cases and error conditions."""
    # Test specific edge cases relevant to your feature
    pass
```

### Step 2: Validate Test Structure

```bash
# Ensure tests are properly structured
make ruff
make type_check
# Fix any errors before proceeding
```

### Step 3: Implement Core Logic

```python
# Follow project patterns from context files
def feature_function(input_param: str) -> FeatureResult:
    """Brief description of what this function does.
    
    Args:
        input_param: Description of the parameter.
        
    Returns:
        FeatureResult: Description of return value.
        
    Raises:
        ValidationError: When input validation fails.
    """
    # Implementation following project patterns
    pass
```

### Step 4: Validate Implementation

```bash
# Run validation after implementation
make ruff          # Code formatting and linting
make type_check    # Static type checking
# Fix all errors before proceeding to tests
```

### Step 5: Run and Fix Tests

```bash
# Run tests and iterate until passing
# run specific tests:
uv run pytest tests/[module]/test_[feature].py -v
# Run all tests
make test_all

# If tests fail:
# 1. Read the error message carefully
# 2. Understand the root cause
# 3. Fix the implementation (never mock to pass)
# 4. Re-run tests
```

### Step 6: Integration Testing

```bash
# Test feature in application context
make run_cli ARGS="[test your feature]"
# OR
make run_gui

# Verify:
# - Feature works in real application context
# - No conflicts with existing functionality
# - Error handling works as expected
```

## ✅ Final Validation

**Complete AGENTS.md pre-commit checklist, plus:**

- [ ] **Feature-specific tests pass:** [Describe specific test]
- [ ] **Integration works:** Feature works in application context
- [ ] **Manual verification:** [Specific command that proves it works]

## ✅ Quality Evaluation Framework

**Before** proceeding with implementation, rate FRP readiness using AGENTS.md framework.

## 🚫 Feature-Specific Anti-Patterns

**Beyond AGENTS.md anti-patterns, avoid:**

- ❌ **Skipping Feature Context:** Don't implement without reading similar features
- ❌ **Ignoring Domain Patterns:** Don't create new patterns when domain-specific ones exist

**Follow AGENTS.md escalation process when in doubt.**
