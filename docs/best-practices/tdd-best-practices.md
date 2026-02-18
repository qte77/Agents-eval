---
title: TDD Best Practices
version: 2.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md
---

**Purpose**: How to do TDD - Red-Green-Refactor cycle, AAA structure, best practices, anti-patterns.

## Test-Driven Development (TDD)

TDD is a development methodology where tests are written before implementation code, driving design and ensuring testability from the start.

## The Red-Green-Refactor Cycle

```text
┌─────────────┐
│  1. RED     │  Write a failing test
│             │  (test what should happen)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  2. GREEN   │  Write minimal code to pass
│             │  (make it work)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  3. REFACTOR│  Improve code quality
│             │  (make it clean)
└─────┬───────┘
      │
      └──────> Repeat
```

## Core Practices

### 1. Write Tests First

**Why**: Enforces modular, decoupled code with clear interfaces

```python
# RED: Write failing test first
def test_user_service_creates_new_user():
    service = UserService()
    user = service.create(name="Alice", email="alice@example.com")
    assert user.id is not None
    assert user.name == "Alice"
```

**Then** implement minimal code to pass.

### 2. Use Arrange-Act-Assert (AAA)

Structure every test in three phases:

```python
def test_order_processor_calculates_total():
    # ARRANGE - Set up test data
    items = [Item(price=10.00, qty=2), Item(price=5.00, qty=1)]
    processor = OrderProcessor()

    # ACT - Execute the behavior
    total = processor.calculate_total(items)

    # ASSERT - Verify the outcome
    assert total == 25.00
```

### 3. Keep Tests Atomic and Isolated

**One behavior per test**: `test_calculator_adds_numbers()` tests addition only, not subtraction, multiplication, etc.

### 4. Test Edge Cases Before Happy Paths

Cover failure modes first (empty input, malformed data), then success cases.

### 5. Descriptive Test Names

Name describes behavior: `test_user_service_returns_404_for_unknown_user()` not `test_service_response()`.

## Benefits of TDD

**Design quality**: Forces modular, testable code with clear interfaces

**Fast feedback**: Catches bugs immediately while context is fresh

**Refactoring confidence**: Tests enable safe code improvements

**Living documentation**: Tests describe how the system behaves

**Defect reduction**: Studies show 40-90% reduction in defect density

## TDD Anti-Patterns to Avoid

**Testing implementation details**:

```python
# BAD - Tests internal structure
def test_service_uses_specific_library():
    assert isinstance(service._internal_client, SomeLibrary)

# GOOD - Tests behavior
def test_service_fetches_data():
    assert service.fetch("key") == expected_value
```

**Overly complex tests**: If test setup is harder to understand than the code, simplify. Avoid excessive mocking.

**Chasing 100% coverage**: Aim for meaningful behavior coverage, not line coverage percentage.

**Low-value patterns**: See `testing-strategy.md` → "Patterns to Remove" for full list.

## Running Tests

Use project make recipes for consistent test execution:

```bash
make test_all           # Run all tests
make quick_validate     # Fast validation (ruff + type checking, no tests)
make validate          # Full validation (ruff + type check + tests)
```

For TDD iterations, run specific tests:

```bash
uv run pytest tests/test_module.py::test_specific_function  # Single test
uv run pytest tests/test_module.py                         # Single file
uv run pytest -k pattern                                    # Pattern match
```

See `testing-strategy.md` for complete test execution guide.

## When to Use TDD

**Use TDD for**:

- Business logic (calculations, algorithms, rules)
- Data transformations (model conversions, parsing)
- Edge case handling (empty inputs, nulls, boundaries)
- API endpoints (request/response validation)

**Consider alternatives for**:

- Simple CRUD operations
- UI layouts (use visual testing)
- Exploratory prototypes (add tests after)
