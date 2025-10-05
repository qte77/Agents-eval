---
title: Core Principles & 80/20 Analysis
description: Ruthless complexity elimination roadmap for Agents-eval
date: 2025-10-05
category: analysis
version: 1.0.0
principles:
  - Measure review quality vs reference (output, not complexity)
  - One tier evaluation (traditional metrics only)
  - Minimal code, maximum value (80% deletion target)
adherence_score: 18%
target_score: 80%
---

**Current State**: 18% principle adherence (82% bloat)
**Target State**: 80% principle adherence (80% code reduction)
**Value Impact**: Zero (100% retention)

## Core Principles

### 1. Measure Review Quality vs Reference

**Truth**: Users need BLEU/ROUGE scores comparing generated reviews to references.
**Violation**: Graph complexity analysis, LLM-as-Judge evaluation tiers measure *how* not *what*.

### 2. One Tier Evaluation

**Truth**: Traditional metrics (BLEU/ROUGE) are sufficient for quality assessment.
**Violation**: Three-tier evaluation (Traditional → LLM Judge → Graph) is complexity theater.

### 3. Minimal Code, Maximum Value

**Truth**: Each dependency must justify its >100MB footprint and maintenance burden.
**Violation**: 4 tracing systems (agentops, logfire, weave, opik), unused HuggingFace/PyTorch.

## 80/20 Analysis

### Keep (20% - Core Value)

```yaml
evaluation_core:
  - src/app/evals/evaluation_pipeline.py: "Orchestrator (simplify to 50 lines)"
  - src/app/evals/traditional_metrics.py: "BLEU/ROUGE/BERTScore only"

data_layer:
  - src/app/data_utils/datasets_peerread.py: "Dataset loader"
  - src/app/data_models/peerread_models.py: "Data contracts"

agent_runtime:
  - src/app/agents/agent_system.py: "Single agent runner"

total_files: 5
total_lines: ~800 (down from ~4000)
```

### Delete (80% - Bloat)

```yaml
tracing_theater:
  - "4 tracing systems → 0": "agentops, logfire, weave, opik"
  - "Impact": "Remove 4 dependencies, 500+ lines config/integration code"

evaluation_bloat:
  - src/app/evals/graph_analysis.py: "NetworkX complexity theater"
  - src/app/evals/llm_evaluation_managers.py: "API judging APIs"
  - src/app/evals/composite_scorer.py: "Multi-tier orchestration"
  - "Impact": "Remove 3 files, 800+ lines, NetworkX dependency"

agent_zoo:
  - src/app/agents/orchestration.py: "Manager/Researcher/Analyst/Synthesizer"
  - src/app/agents/agent_factories.py: "Factory pattern for 1 agent type"
  - "Impact": "Merge to single agent, remove 2 files, 400+ lines"

config_sprawl:
  - src/app/evals/evaluation_config.py: "Multi-tier config"
  - src/app/utils/load_configs.py: "Over-abstracted config loading"
  - "Impact": "Simplify to single config file, remove 200+ lines"

total_deletion: ~2000 lines, 6 dependencies
```

## Principle Violations (Hit List)

### Priority 1 (Immediate Deletion)

1. **Graph Analysis Module** → Violates Principle 1 (measure output, not complexity)
   - File: `src/app/evals/graph_analysis.py`
   - Dependency: NetworkX
   - Reason: Counting tool calls ≠ measuring review quality

2. **LLM-as-Judge Tier** → Violates Principle 2 (one tier evaluation)
   - File: `src/app/evals/llm_evaluation_managers.py`
   - Reason: Using expensive API to judge... other APIs

3. **Tracing Quadruplet** → Violates Principle 3 (minimal dependencies)
   - Dependencies: agentops, logfire, weave, opik
   - Reason: Four systems doing same job (choose ONE or ZERO)

### Priority 2 (Next Sprint)

1. **Multi-Agent Orchestration** → Violates Principle 2 (one path)
   - Files: `orchestration.py`, `agent_factories.py`
   - Reason: Manager→Researcher→Analyst→Synthesizer when one agent suffices

2. **Composite Scoring** → Violates Principle 1 (measure output)
   - File: `src/app/evals/composite_scorer.py`
   - Reason: Complex formula combining tiers that shouldn't exist

### Priority 3 (Technical Debt)

1. **Performance Monitor** → Violates Principle 3 (minimal code)
   - File: `src/app/evals/performance_monitor.py`
   - Reason: Sophisticated timing when `time.time()` suffices

2. **Trace Processors** → Violates Principle 3 (minimal code)
   - File: `src/app/evals/trace_processors.py`
   - Reason: Processing traces we shouldn't collect

## Streamlined Future Architecture

### Before (Current Bloat)

```text
40+ files → 4 tracing systems → 3 evaluation tiers →
Multi-agent orchestration → Graph complexity → Composite scores
```

### After (Laser-Focused)

```python
# The ENTIRE evaluation pipeline
def evaluate(paper: str, agent: Agent) -> EvalResult:
    """Generate review and compare to reference."""
    generated = agent.run(paper)
    reference = load_reference(paper)

    return EvalResult(
        bleu=calculate_bleu(generated, reference),
        rouge=calculate_rouge(generated, reference),
        bertscore=calculate_bertscore(generated, reference),
        execution_time=measure_time()
    )

# That's it. 15 lines vs 2000.
```

### Dependencies Before → After

```yaml
delete:
  - agentops: "Tracing theater"
  - logfire: "Tracing theater"
  - weave: "Tracing theater"
  - opik: "Tracing theater"
  - networkx: "Graph theater"
  - torchmetrics: "Already disabled, remove entirely"

keep:
  - pydantic: "Data validation (core)"
  - pydantic-ai-slim: "Agent runtime (core)"
  - scikit-learn: "BLEU/ROUGE metrics (core)"
  - textdistance: "Text similarity (core)"
  - httpx: "HTTP client (core)"

reduction: 60% fewer dependencies
```

## Implementation Roadmap

### Sprint 1: Core Elimination

```yaml
week_1:
  - Delete graph_analysis.py and NetworkX dependency
  - Delete llm_evaluation_managers.py (Tier 2)
  - Remove 3 of 4 tracing systems (keep opik or NONE)

week_2:
  - Simplify evaluation_pipeline.py to single tier
  - Delete composite_scorer.py
  - Remove performance_monitor.py (use basic timing)
```

### Sprint 2: Agent Consolidation

```yaml
week_3:
  - Merge multi-agent orchestration to single agent
  - Delete agent_factories.py and orchestration.py
  - Simplify agent_system.py

week_4:
  - Consolidate config files
  - Remove trace_processors.py
  - Update documentation to reflect simplicity
```

### Success Criteria

- **Code Reduction**: 80% (4000 → 800 lines)
- **Dependency Reduction**: 60% (15 → 6 packages)
- **Principle Adherence**: 80% (up from 18%)
- **User Workflows**: 100% functional
- **Maintainability**: 10x improved

## Validation Checklist

- [ ] All PeerRead evaluation workflows still work
- [ ] BLEU/ROUGE/BERTScore metrics still calculate correctly
- [ ] Agent generates reviews from papers
- [ ] Execution time measured accurately
- [ ] Zero feature regression for users
- [ ] Documentation updated to reflect simplicity
- [ ] `make validate` passes all checks

---

**Bottom Line**: Delete 2000 lines, remove 6 dependencies, keep 100% functionality. No complexity theater. Just measure review quality vs reference. That's the job.
