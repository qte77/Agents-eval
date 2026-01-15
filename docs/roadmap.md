---
title: Development Roadmap
description: Sprint roadmap and implementation status for the Agents-eval project
category: roadmap
created: 2025-09-04
updated: 2026-01-14
version: 3.2.0
---

Authoritative roadmap for Agents-eval development phases and current status.

## Timeline Overview

**Note**: Sprint files use `YYYY-MM_Sprint#_Name.md` format where the sprint number may reset each month. Roadmap sprint numbers are sequential across the project lifecycle.

| Sprint | Period | Status | Goal | Reference |
| -------- | -------- | -------- | ------ | ----------- |
| **Sprint 1** | Aug 23-28, 2025 | ✅ Complete | Three-tiered evaluation framework | [Sprint1 Details](sprints/2025-08_Sprint1_ThreeTieredEval.md) |
| **Sprint 2** | Planned | 📋 Not Started | Opik + NetworkX Integration | [Sprint2 Details](sprints/2025-08_Sprint2_Opik-NetworkX-Integration.md) |
| **Sprint 3** | Planned | 📋 Blocked | SoC/SRP architectural refactoring (requires Sprint 2) | [Sprint3 Details](sprints/2025-08_Sprint3_SoC_SRP.md) |
| **Sprint 4** | Planned | 📋 Blocked | Pipeline enhancements (requires Sprint 2) | [Sprint4 Details](sprints/2025-09_Sprint4_Pipeline-Enhancements.md) |
| **Sprint 5** | Planned | 📋 Blocked | Advanced features (requires Sprint 2) | [Sprint5 Details](sprints/2025-09_Sprint5_Advanced-Features.md) |

## Current Implementation Status

### ✅ Sprint 1 Complete (Aug 23-28, 2025)

**Delivered**: Fully operational three-tiered evaluation system

- Traditional metrics (`src/app/evals/traditional_metrics.py`)
- LLM-as-a-Judge (`src/app/evals/llm_evaluation_managers.py`)
- Graph analysis (`src/app/evals/graph_analysis.py`)
- Composite scoring (`src/app/evals/composite_scorer.py`)
- Evaluation pipeline (`src/app/evals/evaluation_pipeline.py`)

**Note**: Opik tracing integration (Tasks 4.4-4.5) moved to Sprint 2 (highest priority). ROUGE/BLEU metrics moved to Sprint 4 (Pipeline Enhancements).

### 📋 Sprint 2 Planned: Opik + NetworkX Integration

**Goal**: Deploy Opik AND connect to NetworkX Graph Analysis (Tier 3 PRIMARY)
**Dependencies**: Sprint 1 ✅ Complete
**Key Principle**: Don't introduce SoC/SRP issues - keep Opik code isolated

**MUST Deliver (before Sprint 3 can start):**

- Isolated `src/app/observability/` module
- Local Opik deployment (docker-compose) with ClickHouse
- Opik traces → NetworkX graph conversion
- Graph analysis metrics working from Opik data
- Tier 3 (Graph - PRIMARY) fully operational with Opik
- Abstract `Tracer` interface (dependency injection)
- Configuration-driven enable/disable

**Success Criteria:**

- Run evaluation → Opik captures traces → Graph analysis produces metrics
- All 3 tiers working: Traditional + LLM-Judge + Graph (from Opik)
- Sprint 3 (SoC/SRP) can proceed without breaking Opik+Graph

### 📋 Sprint 3 Blocked

**Goal**: SoC/SRP architectural refactoring
**Dependencies**: Sprint 2 ✅ MUST BE COMPLETE (Opik + NetworkX working)
**Status**: Waiting for Sprint 2 completion before proceeding
**Note**: Opik's isolated module moves cleanly to new architecture

### 📋 Sprint 4 Blocked

**Goal**: Pipeline enhancements with third-party metrics (ROUGE, BLEU)
**Dependencies**: Sprint 2 ✅ Required
**Status**: Waiting for Sprint 2 completion before proceeding

### 📋 Sprint 5 Blocked

**Goal**: Advanced features and external integrations
**Dependencies**: Sprint 2 ✅ Required
**Status**: Waiting for Sprint 2 completion before proceeding

## Key Decisions

See [architecture.md § Architecture Decision Records](architecture.md#architecture-decision-records) for full ADR documentation:

- **ADR-001** (2025-03-01): PydanticAI as Agent Framework
- **ADR-002** (2025-08-01): PeerRead Dataset Integration
- **ADR-003** (2025-08-23): Three-Tiered Evaluation Framework
- **ADR-004** (2025-08-25): Post-Execution Graph Analysis

**Architecture Details**: See [architecture.md](architecture.md) for technical implementation.
**Sprint Details**: Individual sprint documents in `/docs/sprints/` contain complete specifications.
