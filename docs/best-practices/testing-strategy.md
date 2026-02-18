---
title: Testing Strategy
version: 5.0
applies-to: Agents and humans
purpose: High-level testing strategy aligned with KISS/DRY/YAGNI
see-also: tdd-best-practices.md, bdd-best-practices.md
---

**Purpose**: What to test, when to use TDD/BDD/Hypothesis, test organization, running commands.

## Core Principles

| Principle | Testing Application |
| ----------- | --------------------- |
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test library behavior (Pydantic, FastAPI, etc.) |

## What to Test

**High-Value** (Test these):

1. Business logic - Core algorithms, calculations, decision rules
2. Integration points - API handling, external service interactions
3. Edge cases with real impact - Empty inputs, error propagation, boundary conditions
4. Contracts - API response formats, model transformations

**Low-Value** (Avoid these):

1. Library behavior - Pydantic validation, `os.environ` reading, framework internals
2. Trivial assertions - `x is not None`, `isinstance(x, SomeClass)`, `hasattr()`, `callable()`
3. Default values - Unless defaults encode business rules
4. Documentation content - String contains checks

### Patterns to Remove (Test Suite Optimization)

| Pattern | Why Remove | Example |
| --------- | ------------ | --------- |
| Import/existence | Python/imports handle this | `test_module_exists()` |
| Field existence | Pydantic validates at instantiation | `test_model_has_field_x()` |
| Default constants | Testing `300 == 300` | `assert DEFAULT_TIMEOUT == 300` |
| Over-granular | Consolidate into schema validation | 8 tests for one model |
| Type checks | Type checker (pyright) handles | `assert isinstance(result, dict)` |

**Rule**: If the test wouldn't catch a real bug, remove it.

## Testing Approach

### Current Focus: TDD (with pytest + Hypothesis)

**Primary methodology**: Test-Driven Development (TDD)

**Tools** (see `tdd-best-practices.md`):

- **pytest**: Core tool for all TDD tests (specific test cases)
- **Hypothesis**: Optional extension for property-based edge case testing (generative tests)

**When to use each**:

- **pytest**: Known cases (specific inputs, API contracts, known edge cases)
- **Hypothesis**: Unknown edge cases (any string, any number, invariants for ALL inputs)

### Hypothesis Test Priorities (Edge Cases within TDD)

| Priority | Area | Why | Example |
| ---------- | ------ | ----- | --------- |
| **CRITICAL** | Scoring/math formulas | Math must work for ALL inputs | `test_score_always_in_bounds()` |
| **CRITICAL** | Loop termination | Must terminate for ANY input | `test_processor_always_terminates()` |
| **HIGH** | Input validation | Handle arbitrary text safely | `test_parser_never_crashes()` |
| **HIGH** | Output serialization | Must always produce valid JSON | `test_output_always_serializable()` |
| **MEDIUM** | Invariant sums | Total equals component sum | `test_total_equals_sum()` |

See [Hypothesis documentation](https://hypothesis.readthedocs.io/) for usage patterns.

### BDD: Stakeholder Collaboration (Optional)

**BDD** (see `bdd-best-practices.md`) - Different approach from TDD:

- **TDD**: Developer-driven, Red-Green-Refactor, all test levels
- **BDD**: Stakeholder-driven, Given-When-Then, acceptance criteria in plain language

**When to use BDD**:

- User-facing features requiring stakeholder validation
- Complex acceptance criteria needing plain-language documentation
- Collaboration between technical and non-technical team members

### Test Levels: Unit vs Integration

**Unit Tests**:

- Test single component in isolation
- Fast execution (<10ms per test)
- No external dependencies (databases, APIs, file I/O)
- Use mocks/fakes for dependencies
- Most common TDD use case

**Integration Tests**:

- Test multiple components working together
- Slower execution (may involve I/O)
- Use real or in-memory services
- Validate component interactions
- Fewer tests, broader coverage

**When to use each**:

```python
# UNIT TEST - Component in isolation
def test_order_calculator_computes_total():
    calculator = OrderCalculator()
    items = [Item(10), Item(15)]
    assert calculator.total(items) == 25  # Pure logic, no I/O

# INTEGRATION TEST - Components + external service
async def test_order_service_saves_to_database(db_session):
    service = OrderService(db_session)  # Real or in-memory DB
    order = await service.create_order(items=[Item(10)])
    saved = await service.get_order(order.id)
    assert saved.total == 10  # Tests service + DB interaction
```

### Mocking Strategy

**When to use mocks**:

- ✅ External APIs you don't control (payment gateways, third-party services)
- ✅ Slow operations (file I/O, network calls) in unit tests
- ✅ Non-deterministic dependencies (time, random, UUIDs)
- ✅ Error scenarios hard to reproduce (network timeouts, API rate limits)

**When to use real services**:

- ✅ In-memory alternatives exist (SQLite for PostgreSQL, Redis mock)
- ✅ Integration tests validating actual behavior
- ✅ Your own services/components (test real interactions)
- ✅ Testing the integration itself (verifying protocols, serialization)

**Mocking libraries**:

- `unittest.mock` - Standard library, use `patch()` and `MagicMock`
- `pytest-mock` - Pytest fixtures for mocking
- `responses` - Mock HTTP requests
- `freezegun` - Mock time/dates

```python
# MOCK external API
from unittest.mock import patch

def test_payment_processor_handles_api_failure():
    with patch('stripe.Charge.create') as mock_charge:
        mock_charge.side_effect = stripe.APIError("Rate limited")
        processor = PaymentProcessor()
        result = processor.charge(100)
        assert result.status == "failed"

# REAL service (in-memory)
def test_order_repository_saves_order(tmp_path):
    db = SQLite(":memory:")  # Real SQLite, in-memory
    repo = OrderRepository(db)
    order = repo.save(Order(total=100))
    assert repo.get(order.id).total == 100
```

### Priority Test Areas

1. **Core business logic** - Algorithms, calculations, decision rules (unit tests)
2. **API contracts** - Request/response formats, protocol handling (unit + integration)
3. **Edge cases** - Empty/null inputs, boundary values, numeric stability (unit with Hypothesis)
4. **Integration points** - External services, database operations (integration tests)

## Test Organization

**Flat structure** (small projects):

```text
tests/
├── test_*.py             # TDD unit tests
└── conftest.py           # Shared fixtures
```

**Organized structure** (larger projects):

```text
tests/
├── unit/                  # TDD unit tests (pytest)
│   ├── test_services.py
│   └── test_models.py
├── properties/            # Property tests (hypothesis)
│   ├── test_math_props.py
│   └── test_validation_props.py
├── acceptance/            # BDD scenarios (optional)
│   ├── features/*.feature
│   └── step_defs/
└── conftest.py           # Shared fixtures
```

## Running Tests

```bash
# Make recipes (project standard)
make test_all              # All tests
make test_quick            # Rerun failed tests only (fast iteration)
make test_coverage         # Tests with coverage gate (70% threshold)

# Direct pytest (for specific suites)
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests only
pytest -k pattern          # Filter by name
pytest -m marker           # Filter by marker
```

See `Makefile` for all recipes or `pytest --help` for full CLI reference.

## Pre-Commit Validation

```bash
make validate              # Full validation (ruff, pyright, complexity, tests)
make quick_validate        # Fast validation (ruff, pyright only - no tests)
```

Run `make validate` before committing to ensure all quality gates pass.

## Naming Conventions

**Format**: `test_{module}_{component}_{behavior}`

```python
# Unit tests
test_user_service_creates_new_user()
test_order_processor_validates_items()

# Property tests
test_score_always_in_bounds()
test_percentile_ordering()
```

**Benefits**: Clear ownership, easier filtering (`pytest -k test_user_`), better organization

## Decision Checklist

Before writing a test, ask:

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **a library** (skip)?
4. Which approach:
   - **TDD** (default) - Unit tests, business logic, known edge cases
   - **Hypothesis** - Unknown edge cases (any input), numeric invariants
   - **BDD** (optional) - Acceptance criteria, stakeholder communication

## References

- TDD practices: `docs/best-practices/tdd-best-practices.md`
- BDD practices: `docs/best-practices/bdd-best-practices.md`
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
