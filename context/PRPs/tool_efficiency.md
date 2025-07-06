# Tool Efficiency Feature PRP

## Goal

Implement a comprehensive tool efficiency measurement and optimization system for the multi-agent evaluation framework to assess and improve how effectively agents use tools, manage tool resources, and optimize tool performance.

## Why

- **Evaluation Completeness**: The tool_efficiency metric is defined in `config_eval.json` (0.167 weight) but not implemented
- **Resource Optimization**: Need to optimize tool usage costs, especially for expensive operations like web search
- **Performance Monitoring**: Identify slow or inefficient tools that impact overall system performance
- **Usage Analytics**: Provide insights into tool usage patterns for research and optimization

## What

A tool efficiency monitoring and optimization system that measures:

- Tool usage frequency and success rates
- Tool execution times and performance metrics
- Tool resource consumption and cost analysis
- Tool caching effectiveness and hit rates
- Tool failure recovery and fallback mechanisms

### Success Criteria

- [ ] Tool efficiency metric implemented and functional in evaluation system
- [ ] Tool usage tracking and analytics dashboard
- [ ] Tool result caching system for expensive operations
- [ ] Tool timeout and retry mechanism
- [ ] Tool usage quotas and cost management
- [ ] Integration with existing evaluation pipeline

## All Needed Context

### Documentation & References

```yaml
- file: /workspaces/Agents-eval/src/app/agents/agent_system.py
  why: Core tool integration, delegation tools, tool assignment patterns
  critical: Lines 195 (DuckDuckGo tool), 91-99 (delegation tools), tool validation

- file: /workspaces/Agents-eval/src/app/config/data_models.py
  why: Tool validation patterns, AgentConfig model with tools field
  critical: Lines 85-100 tool validation, arbitrary_types_allowed config

- file: /workspaces/Agents-eval/src/app/config/config_eval.json
  why: Tool efficiency metric weight (0.167) defined but not implemented
  critical: Need to implement missing tool_efficiency metric

- file: /workspaces/Agents-eval/src/app/evals/metrics.py
  why: Evaluation metrics implementation patterns, time_taken metric
  critical: Pattern for implementing new metrics in evaluation system

- file: /workspaces/Agents-eval/src/examples/utils/tools.py
  why: Example tool implementations and patterns
  critical: roll_die and get_player_name tool examples
```

### Current Codebase Tree

```bash
src/app/
├── agents/
│   ├── agent_system.py        # Core tool integration and delegation
│   └── llm_model_funs.py      # Model management
├── config/
│   ├── config_app.py          # Common app configuration
│   ├── data_models.py         # Tool validation patterns
│   ├── config_chat.json       # Agent configuration
│   └── config_eval.json       # Evaluation metrics (tool_efficiency: 0.167)
├── evals/
│   └── metrics.py             # Evaluation metrics (missing tool_efficiency)
├── utils/
│   ├── error_messages.py      # Error handling patterns
│   └── log.py                 # Logging utilities
└── examples/
    └── utils/
        └── tools.py           # Example tool implementations
```

### Desired Codebase Tree

```bash
src/app/
├── evals/
│   ├── [existing folders unchanged]
│   ├── tool_efficiency/
│   │   ├── __init__.py
│   │   ├── efficiency_monitor.py   # Tool efficiency monitoring
│   │   ├── cache_manager.py       # Tool result caching
│   │   ├── usage_tracker.py       # Tool usage analytics
│   │   └── optimizer.py           # Tool performance optimization
│   └── metrics.py             # Updated with tool_efficiency implementation
└── [existing files unchanged]
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: PydanticAI tool patterns
# - Tools are assigned using @agent.tool decorator
# - Tools must be validated through field_validator in AgentConfig
# - Tools require RunContext for accessing usage limits and dependencies

# GOTCHA: Tool validation requirements
# - Tools are stored as list[Any] but must be Tool instances
# - AgentConfig uses arbitrary_types_allowed=True for tool validation
# - _validate_model_return() required for tool result validation

# LIBRARY QUIRK: Usage limits and context
# - Usage limits are shared across agents via RunContext
# - Tools access context via ctx parameter
# - Usage tracking is cumulative across tool calls

# PERFORMANCE CONSIDERATION: DuckDuckGo search tool
# - Every research query triggers new search requests
# - No built-in caching mechanism
# - Can be expensive and slow for repeated queries
```

## Implementation Blueprint

### Data Models and Structure

```python
# tools/efficiency_monitor.py
class ToolUsageEvent(BaseModel):
    """Individual tool usage event tracking."""
    
    timestamp: datetime
    tool_name: str
    agent_name: str
    execution_time_ms: float
    success: bool
    input_size: int
    output_size: int
    cache_hit: bool = False
    error_message: str | None = None
    cost_estimate: float | None = None

class ToolEfficiencyMetrics(BaseModel):
    """Tool efficiency metrics data model."""
    
    tool_name: str
    usage_count: int
    success_rate: float
    avg_execution_time: float
    cache_hit_rate: float
    cost_per_usage: float
    efficiency_score: float

class ToolCacheEntry(BaseModel):
    """Tool result cache entry."""
    
    tool_name: str
    input_hash: str
    result: Any
    timestamp: datetime
    access_count: int
    ttl_seconds: int
```

### List of Tasks

```yaml
Task 1:
CREATE src/app/tools/__init__.py:
  - EMPTY file for Python package

Task 2:
CREATE src/app/tools/efficiency_monitor.py:
  - IMPLEMENT ToolUsageEvent and ToolEfficiencyMetrics models
  - IMPLEMENT ToolEfficiencyMonitor class
  - PATTERN: Follow existing Pydantic models in data_models.py

Task 3:
CREATE src/app/tools/cache_manager.py:
  - IMPLEMENT ToolCacheManager class
  - CACHE expensive tool operations (especially search)
  - IMPLEMENT cache invalidation and TTL management

Task 4:
CREATE src/app/tools/usage_tracker.py:
  - IMPLEMENT ToolUsageTracker class
  - TRACK tool usage statistics and patterns
  - GENERATE tool usage reports and analytics

Task 5:
CREATE src/app/tools/optimizer.py:
  - IMPLEMENT ToolOptimizer class
  - OPTIMIZE tool execution and resource usage
  - IMPLEMENT tool timeout and retry logic

Task 6:
MODIFY src/app/agents/agent_system.py:
  - FIND tool assignment and delegation patterns
  - INJECT tool efficiency monitoring
  - PRESERVE existing tool functionality

Task 7:
MODIFY src/app/evals/metrics.py:
  - IMPLEMENT tool_efficiency metric function
  - INTEGRATE with existing metrics calculation
  - MIRROR pattern from time_taken metric

Task 8:
CREATE tests/test_tool_efficiency.py:
  - TEST tool efficiency monitoring
  - TEST tool caching mechanisms
  - TEST integration with evaluation pipeline
```

### Per Task Pseudocode

```python
# Task 2: efficiency_monitor.py
class ToolEfficiencyMonitor:
    def __init__(self):
        self.events: list[ToolUsageEvent] = []
        self.logger = logger  # From utils/log.py
    
    async def monitor_tool_execution(
        self, 
        tool_name: str, 
        agent_name: str, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Monitor tool execution with timing and success tracking."""
        start_time = time.time()
        input_size = len(str(args) + str(kwargs))
        
        try:
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            # PATTERN: Log successful tool usage
            self.logger.info(f"Tool {tool_name} executed successfully in {execution_time:.2f}ms")
            
            # Record successful event
            self._record_event(
                tool_name=tool_name,
                agent_name=agent_name,
                execution_time_ms=execution_time,
                success=True,
                input_size=input_size,
                output_size=len(str(result))
            )
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # PATTERN: Log tool failures
            self.logger.error(f"Tool {tool_name} failed after {execution_time:.2f}ms: {str(e)}")
            
            # Record failed event
            self._record_event(
                tool_name=tool_name,
                agent_name=agent_name,
                execution_time_ms=execution_time,
                success=False,
                input_size=input_size,
                output_size=0,
                error_message=str(e)
            )
            
            raise

# Task 3: cache_manager.py
class ToolCacheManager:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: dict[str, ToolCacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.logger = logger
    
    def _generate_cache_key(self, tool_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from tool name and arguments."""
        import hashlib
        key_data = f"{tool_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_execute(
        self, 
        tool_name: str, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> tuple[Any, bool]:  # Returns (result, cache_hit)
        """Get result from cache or execute function."""
        cache_key = self._generate_cache_key(tool_name, args, kwargs)
        
        # Check cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if self._is_valid(entry):
                entry.access_count += 1
                self.logger.info(f"Cache hit for tool {tool_name}")
                return entry.result, True
        
        # Execute function
        result = await func(*args, **kwargs)
        
        # Cache result
        self._cache_result(cache_key, tool_name, result)
        self.logger.info(f"Cache miss for tool {tool_name}, result cached")
        
        return result, False

# Task 5: optimizer.py
class ToolOptimizer:
    def __init__(self, timeout_seconds: int = 30, max_retries: int = 3):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.logger = logger
    
    async def execute_with_optimization(
        self, 
        tool_name: str, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute tool with timeout and retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                # PATTERN: Asyncio timeout for tool execution
                result = await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=self.timeout_seconds
                )
                
                if attempt > 0:
                    self.logger.info(f"Tool {tool_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except asyncio.TimeoutError:
                self.logger.warning(f"Tool {tool_name} timed out on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Tool {tool_name} timed out after {self.max_retries} attempts")
                
            except Exception as e:
                self.logger.warning(f"Tool {tool_name} failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

# Task 7: metrics.py integration
def tool_efficiency(tool_events: list[ToolUsageEvent]) -> float:
    """Calculate tool efficiency score from usage events."""
    if not tool_events:
        return 0.0
    
    # Calculate efficiency dimensions
    success_rate = sum(1 for event in tool_events if event.success) / len(tool_events)
    avg_execution_time = sum(event.execution_time_ms for event in tool_events) / len(tool_events)
    cache_hit_rate = sum(1 for event in tool_events if event.cache_hit) / len(tool_events)
    
    # Normalize execution time (lower is better)
    normalized_time = max(0.0, 1.0 - (avg_execution_time / 10000.0))  # 10s baseline
    
    # Weighted efficiency score
    efficiency_score = (
        success_rate * 0.4 +
        normalized_time * 0.3 +
        cache_hit_rate * 0.3
    )
    
    return min(1.0, max(0.0, efficiency_score))
```

### Integration Points

```yaml
EVALUATION_SYSTEM:
  - modify: src/app/evals/metrics.py
  - pattern: "def tool_efficiency(tool_events: list[ToolUsageEvent]) -> float:"
  - integration: "Add to evaluation pipeline alongside existing metrics"

AGENT_SYSTEM:
  - modify: src/app/agents/agent_system.py
  - pattern: "Wrap tool execution with efficiency monitoring"
  - integration: "Inject monitoring into existing delegation tools"

CONFIGURATION:
  - modify: src/app/config/config_eval.json
  - pattern: "tool_efficiency metric already defined with weight 0.167"
  - validation: "Ensure metric returns float between 0.0 and 1.0"

CACHING:
  - integrate: Tool result caching for expensive operations
  - pattern: "Especially important for DuckDuckGo search tool"
  - storage: "In-memory cache with TTL and size limits"
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
# CREATE tests/test_tool_efficiency.py
def test_tool_efficiency_monitoring():
    """Test tool efficiency monitoring functionality."""
    monitor = ToolEfficiencyMonitor()
    
    # Test successful tool execution
    async def dummy_tool():
        await asyncio.sleep(0.1)  # Simulate work
        return "success"
    
    result = await monitor.monitor_tool_execution(
        "dummy_tool", "test_agent", dummy_tool
    )
    
    assert result == "success"
    assert len(monitor.events) == 1
    assert monitor.events[0].success is True
    assert monitor.events[0].execution_time_ms > 0

def test_tool_caching():
    """Test tool result caching functionality."""
    cache_manager = ToolCacheManager()
    
    call_count = 0
    async def expensive_tool():
        nonlocal call_count
        call_count += 1
        return f"result_{call_count}"
    
    # First call - cache miss
    result1, cache_hit1 = await cache_manager.get_or_execute(
        "expensive_tool", expensive_tool
    )
    assert result1 == "result_1"
    assert cache_hit1 is False
    
    # Second call - cache hit
    result2, cache_hit2 = await cache_manager.get_or_execute(
        "expensive_tool", expensive_tool
    )
    assert result2 == "result_1"  # Same result from cache
    assert cache_hit2 is True
    assert call_count == 1  # Function only called once

def test_tool_efficiency_metric():
    """Test tool efficiency metric calculation."""
    events = [
        ToolUsageEvent(
            timestamp=datetime.now(),
            tool_name="test_tool",
            agent_name="test_agent",
            execution_time_ms=100.0,
            success=True,
            input_size=10,
            output_size=20,
            cache_hit=False
        ),
        ToolUsageEvent(
            timestamp=datetime.now(),
            tool_name="test_tool",
            agent_name="test_agent",
            execution_time_ms=50.0,
            success=True,
            input_size=10,
            output_size=20,
            cache_hit=True
        )
    ]
    
    efficiency_score = tool_efficiency(events)
    assert isinstance(efficiency_score, float)
    assert 0.0 <= efficiency_score <= 1.0
```

```bash
# Run and iterate until passing:
make test_all
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Test tool efficiency in full evaluation
make run_cli ARGS="--query 'test tool efficiency' --eval"

# Expected: Tool efficiency metric appears in evaluation results
# Test caching by running same query twice and checking logs
```

## Final Validation Checklist

- [ ] All tests pass: `make test_all`
- [ ] No linting errors: `make ruff`
- [ ] No type errors: `make type_check`
- [ ] Tool efficiency metric integrated in evaluation pipeline
- [ ] Tool caching working for expensive operations
- [ ] Tool monitoring tracks usage events
- [ ] Tool timeout and retry mechanisms functional
- [ ] Performance impact minimal (< 10% overhead)
- [ ] Documentation updated in AGENTS.md if needed

## Anti-Patterns to Avoid

- ❌ Don't break existing tool functionality when adding monitoring
- ❌ Don't cache results that should be fresh (time-sensitive data)
- ❌ Don't add excessive monitoring overhead that slows tools
- ❌ Don't hardcode cache sizes or TTL values - make them configurable
- ❌ Don't ignore tool failures - track and analyze them
- ❌ Don't assume all tools benefit from caching - evaluate per tool type
- ❌ Don't make caching mandatory - allow tools to opt-out if needed
  