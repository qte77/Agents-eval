---
name: securing-mas
description: Apply OWASP MAESTRO 7-layer security framework to MAS designs
compatibility: Designed for Claude Code
metadata:
  argument-hint: [component-or-feature]
  allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---

# Securing Multi-Agent Systems

**Target**: $ARGUMENTS

## When to Use

Trigger this skill when:

- Conducting security reviews of agent systems
- Threat modeling for multi-agent architectures
- Reviewing plugin implementations for security
- Designing security controls for pipelines

## References

**MUST READ**:
`docs/best-practices/mas-security.md`

## MAESTRO 7-Layer Security Check

For each new component, verify across all 7 layers:

### Layer 1: Model Layer

- [ ] No user-controlled prompts sent to LLM
- [ ] Structured outputs prevent text injection
- [ ] No sensitive data in model training/tuning

### Layer 2: Agent Logic Layer

- [ ] All inputs validated via typed schemas
- [ ] Type safety enforced at boundaries
- [ ] Logic bugs prevented by typed interfaces

### Layer 3: Integration Layer

- [ ] Timeouts configured for external services
- [ ] Graceful degradation on service failures
- [ ] API keys from environment variables only

### Layer 4: Monitoring Layer

- [ ] Structured logging (no log injection)
- [ ] No PII in default log output
- [ ] Trace data integrity protected

### Layer 5: Execution Layer

- [ ] Per-component timeout enforcement
- [ ] Stateless design (no race conditions)
- [ ] Resource limits configured

### Layer 6: Environment Layer

- [ ] Container isolation for services
- [ ] `.env` files excluded from version control
- [ ] Network segmentation applied

### Layer 7: Orchestration Layer

- [ ] Explicit execution ordering (not configurable)
- [ ] Registry with type checking
- [ ] Static imports (no dynamic loading)

## Security Checklist for Plugins

Before marking implementation as complete:

### Input Validation

- [ ] All inputs validated via typed model schema
- [ ] String inputs sanitized (no code injection)
- [ ] Numeric inputs range-checked
- [ ] File paths validated (no directory traversal)

### Output Safety

- [ ] Outputs use typed validated models
- [ ] No sensitive data in outputs (PII, API keys)
- [ ] Error messages don't leak internal state
- [ ] Structured errors for graceful degradation

### Resource Management

- [ ] Timeouts configured per component
- [ ] Memory usage bounded (no unbounded loops)
- [ ] File descriptors properly closed
- [ ] Network connections have timeouts

### Observability

- [ ] Structured logging with context
- [ ] Trace events emitted for debugging
- [ ] No sensitive data in logs
- [ ] Error paths logged for audit

### External Dependencies

- [ ] API keys from environment variables
- [ ] External service failures handled gracefully
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker for cascading failures

## Common Vulnerabilities

### Prompt Injection (Layer 1)

**Vulnerable**:

```python
prompt = f"Evaluate: {user_input}"
```

**Secure**:

```python
result = agent.run(EvalContext(text=user_input))
```

### Type Confusion (Layer 2)

**Vulnerable**:

```python
def evaluate(self, context: dict) -> dict:
    return {"score": context["data"]}
```

**Secure**:

```python
def evaluate(
    self, context: EvalContext
) -> EvalResult:
    return EvalResult(score=context.compute())
```

### Resource Exhaustion (Layer 5)

**Vulnerable**:

```python
def evaluate(self, context):
    while True:  # Infinite loop
        process(context)
```

**Secure**:

```python
def evaluate(self, context):
    with timeout_context(self.settings.timeout):
        return process(context)
```

### Secret Leakage (Layer 6)

**Vulnerable**:

```python
api_key = "sk-1234..."  # Hardcoded
```

**Secure**:

```python
api_key = os.environ["API_KEY"]  # From env
```

## Threat Matrix Template

For each new feature, document threats:

| Layer | Component | Threat | Sev | Mitigation |
| ----- | --------- | ------ | --- | ---------- |
| 1 | LLM caller | Prompt inj. | HIGH | Structured out |
| 2 | Plugin | Type confusion | MED | Validation |
| 3 | API | Svc downtime | MED | Degradation |
| 4 | Logs | Log injection | MED | Structured log |
| 5 | Runner | Resource exh. | HIGH | Timeouts |
| 6 | Infra | Secret exposure | HIGH | Env vars |
| 7 | Registry | Hijacking | MED | Static import |

## Security Testing

Test security controls explicitly:

```python
def test_input_validation():
    """Layer 2: Reject invalid inputs."""
    plugin = MyPlugin(settings)
    with pytest.raises(ValidationError):
        plugin.evaluate(EvalContext(score=999))


def test_timeout_enforcement():
    """Layer 5: Prevent infinite execution."""
    plugin = MyPlugin(settings)
    with pytest.raises(TimeoutError):
        plugin.evaluate(EvalContext(data="loop"))


def test_error_message_safety():
    """Layer 2: Don't leak internal state."""
    plugin = MyPlugin(settings)
    result = plugin.evaluate(
        EvalContext(data="trigger_error")
    )
    assert "secret" not in result.error.lower()
```

## Further Reading

- [OWASP MAESTRO v1.0](https://genai.owasp.org/resource/multi-agentic-system-threat-modeling-guide-v1-0/)
- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [12-Factor Security](https://12factor.net/)
