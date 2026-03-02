---
title: Development Roadmap
description: Sprint roadmap and implementation status for the Agents-eval project
category: roadmap
created: 2025-09-04
updated: 2026-03-02
version: 4.6.0
---

Sprint timeline for Agents-eval. See [architecture.md](architecture.md) for technical decisions (ADRs).

| Sprint | Status | Goal | Reference |
| --- | --- | --- | --- |
| **Sprint 1** | Delivered | Three-tiered evaluation framework | [Sprint 1](sprints/archive/2025-08_Sprint1_ThreeTieredEval.md) |
| **Sprint 2** | Delivered | Eval wiring, trace capture, Logfire+Phoenix, Streamlit dashboard | [PRD Sprint 2](sprints/archive/PRD-Sprint2-Ralph.md) |
| **Sprint 3** | Delivered | Plugin architecture, GUI wiring, test alignment, optional weave, trace quality | [PRD Sprint 3](sprints/archive/PRD-Sprint3-Ralph.md) |
| **Sprint 4** | Delivered | Operational resilience, Claude Code baseline comparison (solo + teams) | [PRD Sprint 4](sprints/archive/PRD-Sprint4-Ralph.md) |
| **Sprint 5** | Delivered | Runtime fixes, GUI enhancements, architecture improvements, code quality review | [PRD Sprint 5](sprints/archive/PRD-Sprint5-Ralph.md) |
| **Sprint 6** | Delivered | Benchmarking infrastructure, CC baseline completion, security hardening, test quality | [PRD Sprint 6](sprints/archive/PRD-Sprint6-Ralph.md) |
| **Sprint 7** | Delivered | Documentation, examples, test refactoring, GUI improvements, unified providers, CC engine | [PRD Sprint 7](sprints/archive/PRD-Sprint7-Ralph.md) |
| **Sprint 8** | Delivered | Tool bug fix, API key/model cleanup, CC engine consolidation, graph alignment, dead code removal, report generation, judge settings UX, GUI a11y/UX | [PRD Sprint 8](sprints/archive/PRD-Sprint8-Ralph.md) |
| **Sprint 9** | Delivered | Correctness & security hardening — dead code deletion, format string sanitization, PDF size guard, API key env cleanup, security hardening, judge accuracy, AgentConfig typing, type safety fixes, test suite quality sweep | [PRD Sprint 9](sprints/archive/PRD-Sprint9-Ralph.md) |
| **Sprint 10** | Substantially Delivered | CC evaluation pipeline parity (STORY-010: main() CC/MAS branch, extract_cc_review_text, cc_result_to_graph_trace, engine_type, GUI CC execution, reference reviews, process group kill); graph viz polish (STORY-011); inspect.getsource removal (STORY-015). STORY-012/013/014 not started. | [PRD Sprint 10](sprints/archive/PRD-Sprint10-Ralph.md) |
| **Sprint 11** | Delivered | Observability, UX polish, test quality: end-of-run artifact summary (ArtifactRegistry), GUI sidebar tabs, CC engine empty query fix (build_cc_query), CC JSONL stream persistence, search tool HTTP resilience, sub-agent validation JSON parsing fix, query persistence fix, assert isinstance→behavioral replacements, conftest consolidation, dispatch registry refactor, config model consolidation, examples modernization (8 total) | [PRD Sprint 11](sprints/archive/PRD-Sprint11-Ralph.md) |
| **Sprint 12** | Delivered | CC teams mode fixes (stream event parsing, cc_teams flag passthrough, engine_type fix), scoring system fixes (Tier 3 empty-trace skip, composite trace awareness, time_taken timestamps, semantic score dedup, continuous task_success), per-run output directories (RunContext consolidation) | [PRD Sprint 12](sprints/archive/PRD-Sprint12-Ralph.md) |
| **Sprint 13** | Delivered | GUI audit remediation & theming — accessibility fixes (ARIA live regions, landmarks, keyboard traps, graph alt text), theming system (3 curated themes, selector widget, graph color integration), UX improvements (onboarding, validation placement, report caching, navigation consistency, string consolidation, type-aware output rendering) | [PRD Sprint 13](sprints/archive/PRD-Sprint13-Ralph.md) |
