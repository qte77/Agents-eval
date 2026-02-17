---
title: Architecture Visualizations
description: PlantUML source files and rendering instructions for project architecture diagrams
date: 2025-09-01
updated: 2026-02-17
category: documentation
version: 2.0.0
---

This directory contains PlantUML source files for the project's architecture diagrams. PNGs are rendered into `assets/images/` (light and dark themes). Source files live here; generated PNGs do not.

## Diagrams

| File | Type | Description |
|---|---|---|
| `MAS-C4-Overview.plantuml` | C4 | High-level architecture: MAS, Benchmark, Evaluation boundaries |
| `MAS-C4-Detailed.plantuml` | C4 | All containers: agents, evaluation tiers, benchmark, security, providers |
| `MAS-Review-Workflow.plantuml` | Sequence | Full evaluation workflow with security boundaries: URL validation (SSRF), prompt sanitization (MAESTRO L3), log scrubbing (MAESTRO L5) |
| `mas-workflow.plantuml` | Sequence | Agent tool usage: Manager → Researcher/Analyst/Synthesizer delegation |
| `mas-enhanced-workflow.plantuml` | Sequence | Separation of concerns: Loader, Evaluator, Manager (SRP/SoC) |
| `metrics-eval-sweep.plantuml` | Sequence | Benchmarking sweep: SweepConfig → SweepRunner → compositions × papers × repetitions → SweepAnalysis → results.json/summary.md; optional CC headless path (CCTraceAdapter) |
| `customer-journey-activity.plantuml` | Activity | End-to-end user journey: CLI/GUI → evaluation → sweep |
| `documentation-hierarchy.plantuml` | Component | Doc authority hierarchy: agent vs human flows |
| `AI-agent-landscape-visualization.puml` | Landscape | AI agent ecosystem snapshot (informational) |

## Rendering

### Prerequisites

- **Docker**: Uses the official `plantuml/plantuml` Docker image.

### Setup (one-time)

```shell
make setup_plantuml
```

### Generate PNGs

Render a single diagram to `assets/images/`:

```shell
make run_puml_single INPUT_FILE="docs/arch_vis/metrics-eval-sweep.plantuml" STYLE="light" OUTPUT_PATH="assets/images"
```

Generate both themes for all diagrams:

```shell
for f in docs/arch_vis/*.plantuml; do
  make run_puml_single INPUT_FILE="$f" STYLE="light" OUTPUT_PATH="assets/images"
  make run_puml_single INPUT_FILE="$f" STYLE="dark" OUTPUT_PATH="assets/images"
done
```

### Interactive Mode

```shell
make run_puml_interactive
```

Starts a server on `http://localhost:8080` that re-renders on file changes.

## Online Rendering (PlantUML.com)

For rendering without Docker, use the [PlantUML Web Server](http://www.plantuml.com/plantuml). Local `!include` paths must be replaced with raw GitHub URLs:

Replace:

```plantuml
!include styles/github-$STYLE.puml
```

With (light):

```plantuml
!include https://raw.githubusercontent.com/qte77/Agents-eval/main/docs/arch_vis/styles/github-light.puml
```

Or (dark):

```plantuml
!include https://raw.githubusercontent.com/qte77/Agents-eval/main/docs/arch_vis/styles/github-dark.puml
```

Then paste the modified source into the web editor.
