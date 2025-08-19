# Sprint 2: SoC/SRP Refactoring TODO

**Sprint Goal**: Resolve main Separation of Concerns (SoC) and Single Responsibility Principle (SRP) violations in the current codebase structure while maintaining existing module organization.

**Date**: 2025-08-19  
**Status**: Planning  
**Priority**: High Priority for code maintainability and extensibility

## Current Structure Analysis

The codebase does **not** achieve proper separation into `agents-engine`, `dataset-engine`, and `eval-engine`. Instead, it uses domain-driven organization with significant SoC/SRP violations that limit modularity, independence, and extensibility.

## Main SoC/SRP Violations and Solutions

### 1. **app.py: Multiple Responsibilities Violation (SRP)**

**Current Issues:**

- Application orchestration (main concern)  
- Dataset downloading logic (lines 65-85)
- User input handling (lines 92-115)
- Agent configuration and setup (lines 116-133)
- Login/authentication (line 122)
- **File size**: 146 lines mixing concerns

**Solution within current structure:**

```python
# Create src/app/orchestration/
src/app/orchestration/
├── app_launcher.py      # Pure application entry point
├── setup_handler.py     # Dataset download operations  
├── input_handler.py     # User input and query processing
└── session_manager.py   # Login and session management
```

**Implementation Example:**

```python
# app.py becomes minimal orchestrator
async def main(**kwargs):
    if kwargs.get('download_peerread_full_only'):
        return await SetupHandler().handle_full_download()
    
    session = SessionManager()
    await session.authenticate()
    
    input_handler = InputHandler()
    query = await input_handler.process_input(kwargs)
    
    # Only agent orchestration remains in main
    return await run_agent_workflow(query, kwargs)
```

### 2. **agent_system.py: God Class Violation (SRP)**

**Current Issues:**

- **File size**: 513 lines (exceeds 500-line limit from AGENTS.md)
- Agent creation and configuration
- Tool delegation logic  
- Environment setup
- Model validation
- Usage limit management
- Stream handling

**Solution within current structure:**

```python
# Split into focused classes in src/app/agents/
agents/
├── agent_factory.py      # Agent creation (get_manager)
├── delegation_manager.py # Tool delegation logic  
├── environment_setup.py  # Environment configuration
├── stream_handler.py     # Streaming operations
└── validation_utils.py   # Model validation helpers
```

**Migration Steps:**

1. Extract `get_manager()` function to `agent_factory.py`
2. Move tool delegation (@manager_agent.tool functions) to `delegation_manager.py`
3. Extract `setup_agent_env()` to `environment_setup.py`
4. Move streaming logic to `stream_handler.py`
5. Extract `_validate_model_return()` to `validation_utils.py`

### 3. **agents/peerread_tools.py: Tight Coupling Violation (SoC)**

**Current Issues:**

- Agent tool registration mixed with business logic
- Direct imports from data_utils and data_models  
- PDF processing mixed with dataset operations
- Review generation mixed with data retrieval

**Solution within current structure:**

```python
# agents/tools/
tools/
├── dataset_tools.py     # Pure dataset access tools
├── review_tools.py      # Review generation and evaluation  
├── file_tools.py        # PDF processing utilities
└── tool_registry.py     # Agent tool registration
```

**Implementation:**

- Move `read_paper_pdf()` to `file_tools.py`
- Move dataset access functions to `dataset_tools.py`
- Move review generation to `review_tools.py`
- Create `tool_registry.py` for agent tool registration patterns

### 4. **data_utils/datasets_peerread.py: Multiple Concerns (SoC)**

**Current Issues:**

- Download functionality mixed with loading  
- Configuration management mixed with data access
- HTTP client management mixed with file operations
- Validation mixed with persistence

**Solution within current structure:**

```python
# data_utils/peerread/
peerread/
├── downloader.py        # Pure download operations
├── loader.py           # Pure data loading  
├── validator.py        # Data validation
└── config_loader.py    # Configuration management
```

**Migration Steps:**

1. Extract `PeerReadDownloader` class to `downloader.py`
2. Extract `PeerReadLoader` class to `loader.py`
3. Move configuration functions to `config_loader.py`
4. Extract validation logic to `validator.py`

### 5. **Cross-Module Dependency Violations (SoC)**

**Current Issues:**

- `agents/peerread_tools.py` imports from `data_utils/` and `data_models/`
- `app.py` directly calls `data_utils.download_peerread_dataset`
- `evals/` not used by any other module (orphaned)

**Solution within current structure:**

```python
# Create service layer: src/app/services/
services/
├── dataset_service.py   # Abstract dataset operations
├── agent_service.py     # Abstract agent operations  
├── eval_service.py      # Abstract evaluation operations
└── __init__.py         # Service registry and injection
```

**Implementation Example:**

```python
# Usage in app.py
from services import DatasetService, AgentService

dataset_service = DatasetService()
agent_service = AgentService()

# Instead of direct imports across modules
```

### 6. **Configuration Scattered Across Modules (SoC)**

**Current Issues:**

- `config/` module exists but config loading spread across modules
- Environment variables mixed with file config
- Provider config in agents module

**Solution within current structure:**

```python
# Centralize in src/app/config/
config/
├── config_manager.py    # Single config entry point
├── providers.py         # Provider configurations
├── datasets.py          # Dataset configurations  
└── environments.py      # Environment management
```

**Implementation:**

```python
# Single import everywhere
from config import ConfigManager
config = ConfigManager()
```

## Implementation Priority

### **High Priority (Immediate Impact)**

- [ ] **Task 1**: Split `app.py` into orchestration modules
  - Create `src/app/orchestration/` directory
  - Extract setup, input, and session management
  - Reduce `app.py` to pure orchestration logic
  - **Estimated effort**: 1-2 days

- [ ] **Task 2**: Break down `agent_system.py` god class
  - Split 513-line file into focused modules  
  - Extract agent factory, delegation, environment setup
  - **Estimated effort**: 2-3 days

- [ ] **Task 3**: Create service layer for cross-module dependencies
  - Design service interfaces
  - Implement dataset, agent, and eval services
  - Update imports across modules
  - **Estimated effort**: 2-3 days

### **Medium Priority (Maintainability)**

- [ ] **Task 4**: Separate concerns in `peerread_tools.py`
  - Create `agents/tools/` structure
  - Split PDF processing, dataset access, and tool registration
  - **Estimated effort**: 1-2 days

- [ ] **Task 5**: Split `datasets_peerread.py` by functionality
  - Create `data_utils/peerread/` structure
  - Separate download, loading, validation, and config
  - **Estimated effort**: 1-2 days

- [ ] **Task 6**: Centralize configuration management
  - Create unified `ConfigManager`
  - Consolidate environment and file configuration
  - **Estimated effort**: 1 day

## Success Criteria

### **Code Quality Metrics**

- [ ] No files exceed 500 lines (AGENTS.md compliance)
- [ ] Each module has single, clear responsibility
- [ ] Reduced cross-module imports (measured via dependency analysis)
- [ ] Service layer abstracts cross-cutting concerns

### **Maintainability Improvements**

- [ ] New datasets can be added without modifying agent code
- [ ] Agent types can be extended without touching data utilities
- [ ] Configuration changes don't require code modifications across modules

### **Testing Requirements**

- [ ] All refactored modules have unit tests
- [ ] Integration tests verify service layer contracts
- [ ] No regression in existing functionality

## Migration Strategy

### **Phase 1: Foundation** (Week 1)

1. Create new directory structures
2. Extract and test individual components
3. Maintain backward compatibility

### **Phase 2: Service Layer** (Week 2)

1. Implement service interfaces
2. Update cross-module dependencies
3. Test integration points

### **Phase 3: Cleanup** (Week 3)

1. Remove old code and imports
2. Update documentation
3. Validate all functionality works

## Risk Mitigation

### **Potential Risks**

- Breaking existing functionality during refactoring
- Integration issues between refactored modules
- Test coverage gaps during migration

### **Mitigation Strategies**

- Incremental refactoring with continuous testing
- Maintain parallel old/new implementations during transition
- Comprehensive integration test suite before old code removal

## Notes

- **Current violations stem from**: mixing orchestration, business logic, and infrastructure concerns within single modules
- **Proposed solutions**: maintain existing module structure while creating focused, single-responsibility classes and clear separation boundaries
- **Long-term goal**: This refactoring prepares the codebase for future engine-based architecture if needed

## References

- AGENTS.md: Code organization rules (500-line limit)
- CONTRIBUTE.md: Testing strategy and code quality standards
- Current analysis: Cross-module dependency mapping completed
