# Coordination Quality Feature PRP

## Goal

Implement a comprehensive coordination quality measurement and monitoring system for the multi-agent evaluation framework to assess how effectively agents collaborate, delegate tasks, and maintain workflow integrity.

## Why

- **Evaluation Completeness**: The coordination_quality metric is defined in `config_eval.json` (0.167 weight) but not implemented
- **System Reliability**: Need to measure and improve agent coordination failures and bottlenecks
- **Performance Optimization**: Identify coordination inefficiencies that impact overall system performance
- **Research Value**: Provide quantitative data on multi-agent coordination patterns for evaluation research

## What

A coordination quality monitoring system that measures:

- Task delegation success rates between agents
- Inter-agent communication efficiency and latency
- Workflow completion rates and error recovery
- Resource utilization across agent interactions
- Coordination failure detection and analysis

### Success Criteria

- [ ] Coordination quality metric implemented and functional in evaluation system
- [ ] Real-time coordination monitoring dashboard
- [ ] Coordination failure detection and alerting
- [ ] Performance metrics collection and analysis
- [ ] Integration with existing evaluation pipeline

## All Needed Context

### Documentation & References

```yaml
- file: /workspaces/Agents-eval/src/app/agents/agent_system.py
  why: Core coordination logic, delegation patterns, tool-based coordination
  critical: Lines 91-99 show delegation pattern, _validate_model_return validation

- file: /workspaces/Agents-eval/src/app/config/data_models.py
  why: Data contracts for coordination, Pydantic models for agent communication
  critical: ResearchResult, AnalysisResult, ResearchSummary models

- file: /workspaces/Agents-eval/src/app/config/config_eval.json
  why: Coordination quality metric weight (0.167) defined but not implemented
  critical: Need to implement the missing coordination_quality metric

- file: /workspaces/Agents-eval/src/app/evals/metrics.py
  why: Evaluation metrics implementation patterns
  critical: How other metrics are implemented and integrated

- file: /workspaces/Agents-eval/src/app/config/config_chat.json
  why: Agent prompts defining coordination behavior and approval workflows
  critical: Manager agent orchestration prompts
```

### Current Codebase Tree

```bash
src/app/
├── agents/
│   ├── agent_system.py        # Core coordination logic
│   └── llm_model_funs.py      # Model management
├── config/
│   ├── config_app.py          # Common app configuration
│   ├── data_models.py         # Coordination data contracts
│   ├── config_chat.json       # Agent coordination prompts
│   └── config_eval.json       # Evaluation metrics (coordination_quality: 0.167)
├── evals/
│   └── metrics.py             # Evaluation metrics implementation
├── utils/
│   ├── error_messages.py      # Error handling patterns
│   └── log.py                 # Logging utilities
└── main.py                    # Entry point
```

### Desired Codebase Tree

```bash
src/app/
├── evals/
│   ├── [existing folders unchanged]
│   ├── coordination_quality/
│   │   ├── __init__.py
│   │   ├── quality_metrics.py     # Coordination quality measurement
│   │   ├── monitoring.py          # Real-time coordination monitoring
│   │   └── analyzer.py            # Coordination pattern analysis
│   └── metrics.py             # Updated with coordination_quality implementation
└── [existing files unchanged]
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: PydanticAI coordination patterns
# - Tool-based delegation via @agent.tool decorator
# - Usage tracking shared via RunContext
# - Streaming with Pydantic models has NotImplementedError in agent_system.py

# GOTCHA: Validation requirements
# - All agent communication must use _validate_model_return()
# - Pydantic models required for type safety
# - Error handling must follow utils/error_messages.py patterns

# LIBRARY QUIRK: PydanticAI Usage Limits
# - UsageLimits shared across agents via RunContext
# - Coordination can fail if usage limits exceeded
# - Need to track usage per coordination step
```

## Implementation Blueprint

### Data Models and Structure

```python
# coordination/quality_metrics.py
class CoordinationMetrics(BaseModel):
    """Coordination quality metrics data model."""
    
    delegation_success_rate: float
    communication_latency: float
    workflow_completion_rate: float
    error_recovery_rate: float
    resource_utilization: float
    coordination_score: float

class CoordinationEvent(BaseModel):
    """Individual coordination event tracking."""
    
    timestamp: datetime
    source_agent: str
    target_agent: str
    event_type: str  # delegation, response, error, retry
    success: bool
    latency_ms: float
    error_message: str | None = None
```

### List of Tasks

```yaml
Task 1:
CREATE src/app/coordination/__init__.py:
  - EMPTY file for Python package

Task 2:
CREATE src/app/coordination/quality_metrics.py:
  - IMPLEMENT CoordinationMetrics and CoordinationEvent models
  - IMPLEMENT calculate_coordination_quality() function
  - PATTERN: Follow existing Pydantic models in data_models.py

Task 3:
CREATE src/app/coordination/monitoring.py:
  - IMPLEMENT CoordinationMonitor class
  - TRACK delegation events, latency, success rates
  - PATTERN: Use existing logging patterns from utils/log.py

Task 4:
CREATE src/app/coordination/analyzer.py:
  - IMPLEMENT coordination pattern analysis
  - DETECT coordination failures and bottlenecks
  - GENERATE coordination quality reports

Task 5:
MODIFY src/app/agents/agent_system.py:
  - FIND _add_tools_to_manager_agent function
  - INJECT coordination monitoring into delegation tools
  - PRESERVE existing delegation patterns

Task 6:
MODIFY src/app/evals/metrics.py:
  - IMPLEMENT coordination_quality metric function
  - INTEGRATE with existing metrics calculation
  - MIRROR pattern from other metric implementations

Task 7:
CREATE tests/test_coordination_quality.py:
  - TEST coordination metrics calculation
  - TEST monitoring functionality
  - TEST integration with evaluation pipeline
```

### Per Task Pseudocode

```python
# Task 2: quality_metrics.py
class CoordinationMetrics(BaseModel):
    delegation_success_rate: float = Field(ge=0.0, le=1.0)
    communication_latency: float = Field(ge=0.0)
    workflow_completion_rate: float = Field(ge=0.0, le=1.0)
    error_recovery_rate: float = Field(ge=0.0, le=1.0)
    resource_utilization: float = Field(ge=0.0, le=1.0)
    coordination_score: float = Field(ge=0.0, le=1.0)

def calculate_coordination_quality(events: list[CoordinationEvent]) -> CoordinationMetrics:
    """Calculate coordination quality from event history."""
    # PATTERN: Weighted average of coordination dimensions
    # CRITICAL: Handle empty events list gracefully
    if not events:
        return CoordinationMetrics(...)
    
    # Calculate individual metrics
    success_rate = sum(e.success for e in events) / len(events)
    avg_latency = sum(e.latency_ms for e in events) / len(events)
    # ... other calculations
    
    # Weighted coordination score
    coordination_score = (
        success_rate * 0.3 +
        normalized_latency * 0.2 +
        completion_rate * 0.3 +
        recovery_rate * 0.2
    )
    
    return CoordinationMetrics(
        coordination_score=coordination_score,
        # ... other metrics
    )

# Task 3: monitoring.py
class CoordinationMonitor:
    def __init__(self):
        self.events: list[CoordinationEvent] = []
        self.logger = logger  # From utils/log.py
    
    async def track_delegation(self, source: str, target: str, func: Callable):
        """Track delegation with timing and success monitoring."""
        start_time = time.time()
        
        try:
            result = await func()
            # PATTERN: Log successful coordination
            self.logger.info(f"Delegation {source} -> {target} successful")
            
            # Record successful event
            self._record_event(
                source_agent=source,
                target_agent=target,
                event_type="delegation",
                success=True,
                latency_ms=(time.time() - start_time) * 1000
            )
            
            return result
            
        except Exception as e:
            # PATTERN: Log coordination failures
            self.logger.error(f"Delegation {source} -> {target} failed: {str(e)}")
            
            # Record failed event
            self._record_event(
                source_agent=source,
                target_agent=target,
                event_type="delegation",
                success=False,
                latency_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
            
            raise

# Task 5: agent_system.py integration
# MODIFY delegate_research function
@manager_agent.tool
async def delegate_research(ctx: RunContext[None], query: str) -> ResearchResult:
    """Delegate research task to ResearchAgent."""
    # INJECT: Coordination monitoring
    monitor = CoordinationMonitor()
    
    async def _research_task():
        result = await research_agent.run(query, usage=ctx.usage)
        return _validate_model_return(str(result.output), ResearchResult)
    
    # PATTERN: Track delegation with monitoring
    return await monitor.track_delegation("manager", "researcher", _research_task)
```

### Integration Points

```yaml
EVALUATION_SYSTEM:
  - modify: src/app/evals/metrics.py
  - pattern: "def coordination_quality(result: Any) -> float:"
  - integration: "Add to evaluation pipeline alongside existing metrics"

CONFIGURATION:
  - modify: src/app/config/config_eval.json
  - pattern: "coordination_quality metric already defined with weight 0.167"
  - validation: "Ensure metric returns float between 0.0 and 1.0"

LOGGING:
  - integrate: src/app/utils/log.py
  - pattern: "Use existing logger for coordination events"
  - level: "INFO for successful coordination, ERROR for failures"
```

## Validation Loop

### Level 1: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
make ruff                    # Format and fix linting issues
make type_check             # Type checking with mypy

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests

```python
# CREATE tests/test_coordination_quality.py
def test_coordination_metrics_calculation():
    """Test coordination quality calculation with sample events."""
    events = [
        CoordinationEvent(
            timestamp=datetime.now(),
            source_agent="manager",
            target_agent="researcher",
            event_type="delegation",
            success=True,
            latency_ms=150.0
        ),
        # ... more test events
    ]
    
    metrics = calculate_coordination_quality(events)
    assert 0.0 <= metrics.coordination_score <= 1.0
    assert metrics.delegation_success_rate >= 0.0

def test_coordination_monitoring():
    """Test coordination monitoring functionality."""
    monitor = CoordinationMonitor()
    
    # Test successful delegation tracking
    async def dummy_task():
        return "success"
    
    result = await monitor.track_delegation("manager", "researcher", dummy_task)
    assert result == "success"
    assert len(monitor.events) == 1
    assert monitor.events[0].success is True

def test_coordination_quality_metric():
    """Test integration with evaluation metrics."""
    # PATTERN: Test similar to other metrics in the evaluation system
    sample_result = {"coordination_events": [...]}
    quality_score = coordination_quality(sample_result)
    assert isinstance(quality_score, float)
    assert 0.0 <= quality_score <= 1.0
```

```bash
# Run and iterate until passing:
make test_all
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Test the coordination quality in full evaluation
make run_cli ARGS="--query 'test coordination quality' --eval"

# Expected: Coordination quality metric appears in evaluation results
# If error: Check logs for coordination monitoring issues
```

## Final Validation Checklist

- [ ] All tests pass: `make test_all`
- [ ] No linting errors: `make ruff`
- [ ] No type errors: `make type_check`
- [ ] Coordination quality metric integrated in evaluation pipeline
- [ ] Coordination monitoring tracks delegation events
- [ ] Error cases handled gracefully with proper logging
- [ ] Performance impact minimal (< 5% overhead)
- [ ] Documentation updated in AGENTS.md if needed

## Anti-Patterns to Avoid

- ❌ Don't break existing delegation patterns in agent_system.py
- ❌ Don't ignore coordination failures - log and track them
- ❌ Don't add excessive monitoring overhead that slows coordination
- ❌ Don't hardcode coordination thresholds - make them configurable
- ❌ Don't skip validation of coordination metrics calculation
- ❌ Don't assume all coordination events are successful - handle failures gracefully
