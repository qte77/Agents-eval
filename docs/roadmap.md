---
title: Development Roadmap
description: Sprint roadmap and implementation status for the Agents-eval project
category: roadmap
created: 2025-09-04
updated: 2026-01-12
version: 3.2.0
---

Authoritative roadmap for Agents-eval development phases and current status.

## Timeline Overview

**Note**: Sprint files use `YYYY-MM_Sprint#_Name.md` format where the sprint number may reset each month. Roadmap sprint numbers are sequential across the project lifecycle.

| Sprint | Period | Status | Goal | Reference |
| -------- | -------- | -------- | ------ | ----------- |
| **Sprint 1** | Aug 23-28, 2025 | ✅ Complete | Three-tiered evaluation framework | [Sprint1 Details](sprints/2025-08_Sprint1_ThreeTieredEval.md) |
| **Sprint 2** | Planned | 📋 Not Started | SoC/SRP architectural refactoring | [Sprint2 Details](sprints/2025-08_Sprint2_SoC_SRP.md) |
| **Sprint 3** | Planned | 📋 Blocked | Advanced features (requires Sprint 2) | [Sprint3 Details](sprints/2025-09_Sprint1_Advanced-Features.md) |

## Current Implementation Status

### ✅ Sprint 1 Complete (Aug 23-28, 2025)

**Delivered**: Fully operational three-tiered evaluation system

- Traditional metrics (`src/app/evals/traditional_metrics.py`)
- LLM-as-a-Judge (`src/app/evals/llm_evaluation_managers.py`)
- Graph analysis (`src/app/evals/graph_analysis.py`)
- Composite scoring (`src/app/evals/composite_scorer.py`)
- Evaluation pipeline (`src/app/evals/evaluation_pipeline.py`)

### 📋 Sprint 2 Planned

**Goal**: Clean engine separation (agents/dataset/eval)
**Dependencies**: Sprint 1 ✅ Complete

### 📋 Sprint 3 Blocked

**Goal**: External tool integration and advanced features
**Dependencies**: Sprint 1 ✅ Complete, Sprint 2 ❌ Required (not started)
**Status**: Waiting for Sprint 2 completion before proceeding

## Key Decisions

- **ADR-001** (2025-03-01): PydanticAI as Agent Framework
- **ADR-002** (2025-08-01): PeerRead Dataset Integration
- **ADR-003** (2025-08-23): Three-Tiered Evaluation Framework
- **ADR-004** (2025-08-25): Post-Execution Graph Analysis

**Architecture Details**: See [architecture.md](architecture.md) for technical implementation.
**Sprint Details**: Individual sprint documents in `/docs/sprints/` contain complete specifications.
