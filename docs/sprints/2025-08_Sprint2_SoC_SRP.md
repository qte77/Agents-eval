# Sprint 2: Separation of Concerns (SoC) & Single Responsibility Principle (SRP) Refactoring

**Sprint Goal**: Refactor the codebase to achieve proper Separation of Concerns (SoC) and Single Responsibility Principle (SRP) by implementing clean, modular engine architecture that separates agents, dataset, and evaluation concerns into independent, testable components.

**Priority**: High Priority for architectural foundation and technical debt resolution

## Architectural Refactoring Requirements

The current system has several SoC/SRP violations that need to be addressed before implementing the comprehensive evaluation framework. This sprint focuses on restructuring the codebase into clear, modular engines with well-defined boundaries.

## Sprint Dependencies

**Critical Dependency**: Sprint 2 depends on Sprint 1 completion.

**Rationale**: Functionality is demanded first. Sprint 1 implements the PeerRead evaluation framework that provides the concrete use cases and requirements needed to design proper engine boundaries in Sprint 2.

### Resolved in Sprint 1

**These tasks are definitively completed in Sprint 1 and will not be carried forward:**

- **PDF Ingestion Capability**: Implemented in Sprint 1 with large context models
- **Prompt Configuration Audit**: All prompts externalized in Sprint 1
- **Error Message Strategy**: Unified error handling implemented in Sprint 1
- **Security & Quality Review**: Comprehensive audit completed in Sprint 1

## Current SoC/SRP Violations Analysis

### Major Architectural Issues

#### 1. **Mixed Concerns in `app.py` (Main Entry Point)**

**Violation**: Single file handling authentication, configuration loading, agent orchestration, dataset operations, and CLI interface.

**Current Issues**:

- Direct dataset download calls in main application flow
- Agent system setup mixed with application initialization
- Configuration loading scattered throughout the function
- No clear separation between CLI concerns and business logic

**Resolution Strategy**: Separate into three independent engines with clear boundaries and responsibilities.

#### 2. **Agent System Mixed Responsibilities (`agents/agent_system.py`)**

**Violation**: Agent creation, LLM provider management, environment setup, and execution orchestration in single module.

**Current Issues**:

- Provider configuration logic mixed with agent orchestration
- Environment setup responsibilities scattered
- Tool integration tightly coupled to agent creation
- Model selection logic embedded in agent system

**Resolution Strategy**: Extract agent creation, provider management, and tool integration into separate modules with single responsibilities.

#### 3. **Dataset Operations Mixed with Business Logic (`data_utils/`)**

**Violation**: Dataset downloading, paper loading, review persistence mixed with application-specific logic.

**Current Issues**:

- Configuration loading embedded in dataset functions
- Logging scattered throughout data operations  
- No clear abstraction between dataset format and business models
- Caching logic tightly coupled to download implementation

**Resolution Strategy**: Create isolated dataset engine with pure data operations separated from business logic.

#### 4. **Evaluation Logic Incomplete and Scattered (`evals/`)**

**Violation**: Minimal evaluation implementation with missing separation between metrics calculation and evaluation orchestration.

**Current Issues**:

- Only 2 basic metrics implemented with TODOs
- No separation between metric calculation and result aggregation
- Missing evaluation pipeline coordination
- No abstraction for different evaluation types

**Resolution Strategy**: Build complete evaluation engine with separation between metrics calculation and result aggregation.

### Engine Architecture Overview

**Three Independent Engines:**

- **Agents Engine**: Agent orchestration and execution (no external dependencies)
- **Dataset Engine**: Data loading and caching (no external dependencies)  
- **Eval Engine**: Metrics and scoring (consumes from agents and dataset engines)

## Implementation Priority Tasks

### **Phase 1: Architectural Foundation (Days 1-2)**

#### Task 1: Create Engine Directory Structure

- [ ] Create `src/app/engines/` directory structure
- [ ] Move existing modules to appropriate engines following SoC principles
- [ ] Update all import statements to reflect new structure
- [ ] Create engine-specific `__init__.py` files with clear APIs

#### Task 2: Agents Engine Separation

- [ ] Extract agent creation logic to `agents_engine/core/agent_factory.py`
- [ ] Move LLM provider management to `agents_engine/providers/`
- [ ] Separate tool management to `agents_engine/tools/tool_registry.py`
- [ ] Create clean agent execution interface

#### Task 3: Dataset Engine Isolation

- [ ] Move PeerRead operations to `dataset_engine/sources/peerread_source.py`
- [ ] Extract caching logic to `dataset_engine/core/dataset_cache.py`
- [ ] Create dataset-agnostic loading interface
- [ ] Implement dataset validation abstraction

### **Phase 2: Evaluation Engine Implementation (Days 3-4)**

#### Task 4: Evaluation Framework Architecture

- [ ] Implement `eval_engine/core/evaluation_coordinator.py`
- [ ] Create metric calculation abstractions
- [ ] Build result aggregation system
- [ ] Design composite scoring interface

#### Task 5: Engine Refactoring Integration

- [ ] **Refactor PDF Ingestion**: Move Sprint 1 PDF processing implementation to `dataset_engine` boundaries
- [ ] **Refactor Configuration**: Ensure Sprint 1 externalized prompts align with engine separation
- [ ] **Refactor Error Handling**: Adapt Sprint 1 unified error handling to engine boundaries
- [ ] **Engine Security Review**: Apply Sprint 1 security audit findings to engine architecture

### **Phase 3: Engine Integration & Validation (Days 5-6)**

#### Task 6: Dependency Injection System

- [ ] Create `core/dependency_injection.py` for engine coordination
- [ ] Implement clean interfaces between engines
- [ ] Update `app.py` to use engine coordination instead of direct calls
- [ ] Validate engine independence and modularity

#### Task 7: Final Validation & Testing

- [ ] **Engine Integration Testing**: Validate all engines work together through dependency injection
- [ ] **SoC/SRP Compliance Audit**: Ensure all architectural violations are resolved
- [ ] **Performance Validation**: Verify refactoring doesn't degrade Sprint 1 functionality
- [ ] **Documentation Update**: Update all architectural documentation to reflect engine structure

**Sprint 1 → Sprint 2 Handoff Requirements**:

- Working PeerRead evaluation pipeline
- Identified architectural pain points from implementation
- Clear interface contracts based on actual usage patterns
- Performance bottlenecks and scaling requirements from real evaluation workloads

## Engine Architecture Context

### Engine Refactoring Focus

Sprint 2 addresses the architectural foundation needed to support the evaluation framework implemented in Sprint 1. The focus is purely on refactoring existing code to achieve proper Separation of Concerns and Single Responsibility Principle.

### Refactoring Scope

- **Agents Engine**: Clean separation of agent orchestration, LLM provider management, and tool integration
- **Dataset Engine**: Pure data operations isolated from business logic and evaluation concerns  
- **Eval Engine**: Evaluation framework architecture that can consume clean interfaces from other engines

### Key Architectural Improvements

1. **Dependency Inversion**: Engines depend on abstractions, not concrete implementations
2. **Interface Segregation**: Each engine exposes only what other engines need
3. **Single Responsibility**: Each module has one reason to change
4. **Open/Closed Principle**: Engines are open for extension, closed for modification

## Success Criteria

### **Architectural Refactoring (SoC/SRP)**

- [ ] Clear separation into three independent engines: `agents_engine`, `dataset_engine`, `eval_engine`
- [ ] Each engine has single, well-defined responsibility with no cross-concerns
- [ ] Engine dependencies follow dependency inversion principle (eval depends on agents/dataset, but not vice versa)
- [ ] Clean interfaces between engines with no direct implementation coupling

### **Sprint 1 Integration**

- [ ] **PDF Ingestion Refactoring**: Sprint 1 implementation properly separated into `dataset_engine` boundaries
- [ ] **Configuration Refactoring**: Sprint 1 externalized prompts integrated with engine-specific config management
- [ ] **Error Handling Refactoring**: Sprint 1 unified error handling adapted to respect engine boundaries
- [ ] **Security Architecture**: Sprint 1 security audit findings applied to engine separation design

### **Engine Independence Validation**

- [ ] `agents_engine` can be tested in complete isolation without dataset or evaluation dependencies
- [ ] `dataset_engine` can load and cache data without agent or evaluation logic
- [ ] `eval_engine` can calculate metrics given standardized input interfaces
- [ ] Each engine has comprehensive unit tests with mocked dependencies
- [ ] Integration tests validate engine coordination without breaking encapsulation

### **Code Quality Improvements**

- [ ] All SoC/SRP violations identified and resolved
- [ ] Import structure reflects clean engine boundaries
- [ ] Configuration loading centralized and not scattered across modules
- [ ] Logging abstracted and not embedded in business logic
- [ ] Error handling consistent across all engine boundaries

## Implementation Strategy

### **Phase 1: Architectural Foundation** (Days 1-2)

1. Create engine directory structure and move existing modules
2. Separate agent system into `agents_engine` with clean interfaces
3. Extract dataset operations into `dataset_engine` with caching abstraction
4. Update all import statements to reflect new modular structure

### **Phase 2: Engine Implementation** (Days 3-4)  

1. Implement `eval_engine` architecture with metric calculation separation
2. Resolve all Sprint 1 TODOs within appropriate engine boundaries
3. Create dependency injection system for engine coordination
4. Validate engine independence and interface contracts

### **Phase 3: Integration & Validation** (Days 5-6)

1. Update main application to use engine coordination pattern
2. Implement comprehensive testing for each engine in isolation
3. Validate SoC/SRP compliance and architectural improvements
4. Finalize Sprint 1 integration within proper engine boundaries

## Notes

- **Architectural Focus**: This sprint prioritizes clean code architecture and technical debt resolution as foundation for Sprint 1 evaluation goals
- **SoC/SRP Compliance**: Strict adherence to Separation of Concerns and Single Responsibility Principle for maintainable, extensible system
- **Engine Independence**: Each engine must be testable and developable in complete isolation from other engines
- **Foundation for Future**: Clean architecture enables rapid implementation of evaluation framework in subsequent sprints
- **Sprint 1 Integration**: All Sprint 1 TODOs are addressed within appropriate engine boundaries during refactoring

## References

- [CONTRIBUTING.md](../../CONTRIBUTING.md): Development workflow and quality standards
- [Landscape Analysis](../landscape.md): Comprehensive tool and framework analysis
- [Architecture Documentation](../architecture.md): System design and architectural decisions
