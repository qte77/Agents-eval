---
title: Sprint 2 - Opik + NetworkX Integration
description: Deploy Opik tracing and connect to NetworkX Graph Analysis before SoC/SRP refactoring
date: 2026-01-14
category: sprint
version: 1.0.0
---

## Sprint Goal

*IMPLEMENT Opik + NetworkX Integration (code working) BEFORE Sprint 3 (SoC/SRP refactoring)

Deploy local Opik tracing infrastructure AND connect it to NetworkX Graph Analysis to make Tier 3 (Graph - PRIMARY) fully operational with Opik traces.

**Critical Execution Order:**

```text
Sprint 2: IMPLEMENT Opik + NetworkX (code working)
              │
              ▼ MUST BE COMPLETE (code implemented, tested, working)
              │
Sprint 3: SoC/SRP cleanup/optimization (ONLY THEN)
```

**Key Principle:** SoC/SRP is cleanup/optimization, NOT a blocker for Opik+NetworkX. Implement core functionality FIRST, optimize AFTER.

---

## Sprint Dates

**Duration:** 5-7 days
**Status:** 📋 Not Started
**Priority:** HIGHEST (unblocks all other sprints)

---

## Dependencies

- ✅ Sprint 1 Complete: Three-tiered evaluation framework operational
- ✅ Existing docker-compose.opik.yaml file
- ✅ Graph analysis code (`src/app/evals/graph_analysis.py`)

---

## MUST Deliver (Before Sprint 3 Can Start)

### 1. Isolated Observability Module

**Location:** `src/app/observability/`

**Structure:**

```text
src/app/observability/
├── __init__.py
├── tracer_interface.py      # Abstract Tracer (ABC)
├── opik_tracer.py           # OpikTracer implementation
├── opik_client.py           # Opik client singleton
├── opik_config.py           # Configuration handling
└── trace_exporters.py       # Export to NetworkX/JSON
```

**Anti-Pattern Prevention:**

- ❌ NO `import opik` in core files (agents/, evals/)
- ❌ NO Opik-specific code in evaluation_pipeline.py
- ✅ YES dependency injection via `Tracer` interface
- ✅ YES configuration-driven enable/disable

---

### 2. Local Opik Deployment

**Requirements:**

- Local Opik deployment using existing `docker-compose.opik.yaml`
- ClickHouse backend configured and accessible
- Health checks passing
- Make recipe: `make deploy_opik` and `make stop_opik`

**Deliverables:**

- `make deploy_opik` → Opik + ClickHouse running locally
- Opik dashboard accessible at `http://localhost:5173`
- ClickHouse accessible for trace queries

---

### 3. Opik Traces → NetworkX Graph Conversion

**Requirements:**

- Opik captures agent execution traces
- Trace data exported to NetworkX graph format
- Graph analysis metrics computed from Opik data

**Implementation:**

- `OpikTracer.export_to_networkx()` method
- Update `graph_analysis.py` to accept Opik-sourced graphs
- Preserve existing graph analysis logic

**Success Criteria:**

- Run evaluation → Opik logs traces → Export to NetworkX → Graph metrics work
- No regression in graph analysis functionality

---

### 4. Tier 3 (Graph) Fully Operational with Opik

**Requirements:**

- All graph metrics working with Opik-sourced data:
  - Path convergence
  - Coordination centrality
  - Tool selection accuracy
  - Communication overhead
- Performance equivalent or better than current implementation

---

### 5. Abstract Tracer Interface (Dependency Injection)

**Pattern:**

```python
# tracer_interface.py
from abc import ABC, abstractmethod

class Tracer(ABC):
    @abstractmethod
    def start_trace(self, name: str): pass

    @abstractmethod
    def log_step(self, data: dict): pass

    @abstractmethod
    def export_to_networkx(self) -> nx.Graph: pass

# opik_tracer.py
class OpikTracer(Tracer):
    def start_trace(self, name: str):
        # Opik-specific implementation
        pass
```

**Usage in core code:**

```python
# evaluation_pipeline.py (CORRECT)
def run_evaluation(
    agent_system: AgentSystem,
    tracer: Optional[Tracer] = None  # ✅ Dependency injection
):
    if tracer:
        tracer.start_trace("evaluation")
```

**DON'T:**

```python
# evaluation_pipeline.py (WRONG)
from app.observability.opik_client import opik  # ❌ Hard dependency
```

---

### 6. Configuration-Driven Enable/Disable

**File:** `config/config_observability.json`

```json
{
  "enabled": true,
  "provider": "opik",
  "opik": {
    "local_deployment": true,
    "clickhouse_url": "http://localhost:8123",
    "workspace": "default"
  }
}
```

**Code:**

```python
# Main entrypoint
from app.observability.tracer_factory import create_tracer

if config.observability.enabled:
    tracer = create_tracer(config.observability.provider)
else:
    tracer = None
```

---

## Success Criteria

### Functional Requirements

- [ ] Run `make deploy_opik` → Opik + ClickHouse running
- [ ] Run evaluation pipeline → Opik captures traces
- [ ] Traces visible in Opik dashboard
- [ ] Export traces → NetworkX graph
- [ ] Graph analysis metrics working from Opik data
- [ ] All 3 tiers operational: Traditional + LLM-Judge + Graph (from Opik)

### Architecture Requirements

- [ ] Opik code isolated in `src/app/observability/`
- [ ] Zero `import opik` in core files (agents/, evals/)
- [ ] Tracer injected via parameters, not imported directly
- [ ] Can disable Opik via config without code changes
- [ ] Sprint 3 (SoC/SRP) can move `observability/` module cleanly

### Testing Requirements

- [ ] Evaluation works with Opik enabled
- [ ] Evaluation works with Opik disabled
- [ ] `make validate` passes
- [ ] No regression in evaluation results
- [ ] Performance benchmarks: Opik overhead < 10%

---

## Refactor-Friendly Implementation Guidelines

### 1. Isolation

**Principle:** All Opik code in one module

**DO:**

- Single `src/app/observability/` module
- Clear module boundary
- No leakage into other modules

**DON'T:**

- Scatter Opik imports across codebase
- Mix Opik logic with business logic

---

### 2. Dependency Injection

**Principle:** No hard dependencies on Opik

**DO:**

```python
def agent_method(tracer: Optional[Tracer] = None):
    if tracer:
        tracer.log("event")
```

**DON'T:**

```python
from observability.opik_client import opik
def agent_method():
    opik.log("event")  # ❌ Hard dependency
```

---

### 3. Interface-Driven

**Principle:** Code depends on interfaces, not implementations

**DO:**

- Define `Tracer` abstract base class
- Implement `OpikTracer(Tracer)`
- Core code uses `Tracer`, not `OpikTracer`

**DON'T:**

- Direct usage of Opik classes in core code
- Type hints with concrete Opik types

---

### 4. Configuration-Driven

**Principle:** Enable/disable without code changes

**DO:**

- Read from `config_observability.json`
- Factory pattern: `create_tracer(provider)`
- Environment variable overrides

**DON'T:**

- Hardcoded `OPIK_AVAILABLE` flags scattered everywhere
- Feature flags in code

---

### 5. Minimal Touch Points

**Principle:** Instrument only at entry points

**Touch Points (ONLY these):**

1. `src/app/agents/agent_system.py` - Agent execution entry
2. `src/app/evals/evaluation_pipeline.py` - Pipeline entry
3. `src/app/main.py` - CLI entry (optional)

**DON'T:**

- Add tracing to every helper function
- Instrument internal implementation details

---

## Implementation Checklist

### Phase 1: Isolated Module Setup (Day 1)

- [ ] Create `src/app/observability/` directory
- [ ] Define `Tracer` abstract interface (`tracer_interface.py`)
- [ ] Implement `OpikTracer` concrete class (`opik_tracer.py`)
- [ ] Create `config/config_observability.json` schema
- [ ] Implement `create_tracer()` factory function
- [ ] Add unit tests for `OpikTracer`

### Phase 2: Local Deployment (Day 1-2)

- [ ] Test existing `docker-compose.opik.yaml`
- [ ] Add `make deploy_opik` and `make stop_opik` commands
- [ ] Add health check script (`scripts/check_opik_health.sh`)
- [ ] Document deployment steps in README
- [ ] Verify Opik dashboard accessible

### Phase 3: Minimal Instrumentation (Day 2-3)

- [ ] Add `@track` decorator to `agent_system.py:run_agent()`
- [ ] Add optional `tracer` parameter to `evaluation_pipeline.py`
- [ ] Wire tracer via dependency injection in `main.py`
- [ ] Test: Verify traces appear in Opik dashboard
- [ ] Test: Verify evaluation works with tracer=None

### Phase 4: Graph Export (Day 3-4)

- [ ] Implement `OpikTracer.export_to_networkx()`
- [ ] Update `graph_analysis.py` to accept external graphs
- [ ] Test: Graph metrics work with Opik-sourced data
- [ ] Test: No regression in graph analysis results
- [ ] Performance benchmark: Measure Opik overhead

### Phase 5: Integration Testing (Day 4-5)

- [ ] Run full evaluation with Opik enabled
- [ ] Run full evaluation with Opik disabled
- [ ] Verify: All 3 tiers produce consistent results
- [ ] Verify: `make validate` passes
- [ ] Document: Integration architecture in `docs/opik-integration-architecture.md`

### Phase 6: Validation & Handoff (Day 5-7)

- [ ] Code review: Check isolation, dependency injection, interfaces
- [ ] Performance validation: Opik overhead < 10%
- [ ] Documentation review: Complete and accurate
- [ ] Sprint 3 readiness: Confirm `observability/` can move cleanly
- [ ] Create handoff document for Sprint 3 (SoC/SRP)

---

## Makefile Additions

```makefile
# Opik deployment commands
deploy_opik:
 docker-compose -f docker-compose.opik.yaml up -d
 @echo "Opik deployed. Dashboard: http://localhost:5173"

stop_opik:
 docker-compose -f docker-compose.opik.yaml down

status_opik:
 docker-compose -f docker-compose.opik.yaml ps
 @./scripts/check_opik_health.sh

clean_opik:
 docker-compose -f docker-compose.opik.yaml down -v
 @echo "WARNING: All Opik trace data deleted"
```

---

## Documentation to Create

### 1. `docs/opik-integration-architecture.md`

**Content:**

- Design principles (isolation, dependency injection, interfaces)
- Integration points (3-5 locations)
- Configuration schema
- Testing strategy (with/without Opik)
- Why this design (enables Sprint 3 refactoring)

### 2. `README.md` updates

**Add section:**

```markdown
## Opik Tracing (Optional)

Deploy local Opik tracing:
```bash
make deploy_opik
```

Run evaluation with tracing:

```bash
make run_cli  # Opik traces automatically if deployed
```

View traces:

```bash
open http://localhost:5173
```

---

## Sprint 3 Handoff Requirements

Before Sprint 3 (SoC/SRP refactoring) can start:

### Deliverables Checklist

- [ ] All Phase 1-6 tasks completed
- [ ] Opik + NetworkX fully operational
- [ ] Documentation complete
- [ ] Tests passing
- [ ] Performance validated

### Handoff Document

Create: `docs/sprints/handoffs/sprint2-to-sprint3.md`

**Content:**

- Sprint 2 accomplishments
- `observability/` module structure
- Integration points in codebase
- How to move `observability/` in Sprint 3
- Known issues or technical debt

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Opik deployment issues | Medium | High | Use existing docker-compose, add health checks |
| Performance overhead | Low | Medium | Benchmark early, optimize if >10% overhead |
| Complex Opik API | Medium | Medium | Use simple `@track` decorator, abstract complexity |
| Integration breaks tests | Low | High | Maintain tracer=None mode, test both paths |

---

## Success Metrics

- **Functional:** All 3 tiers working with Opik traces
- **Performance:** Opik overhead < 10%
- **Architecture:** Zero `import opik` in core files
- **Refactorability:** Sprint 3 can move `observability/` cleanly

---

## References

- [Three-Tier Validation Strategy](../architecture.md#three-tier-validation-strategy)
- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Existing docker-compose.opik.yaml](../../docker-compose.opik.yaml)
- [Sprint 3: SoC/SRP Refactoring](2025-08_Sprint3_SoC_SRP.md)
