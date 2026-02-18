---
title: "Agents-eval: A Multi-Agent Evaluation Framework for Agentic AI Systems"
subtitle: "Writeup"
author: "[Author Name]"
date: "2026"
lang: en-US
toc: true
toc-depth: 3
bibliography: 09a_bibliography.bib
csl: ../../../../scripts/writeup/citation-styles/ieee.csl
link-citations: true
reference-section-title: References
linkcolor: blue
urlcolor: blue
citecolor: blue
geometry: "margin=2.5cm,footskip=30pt"
documentclass: report
fontsize: 11pt
linestretch: 1.25
header-includes:
  - \providecommand{\refname}{\bibname}
abstract: |
  This work describes the conception, implementation, and empirical evaluation of **Agents-eval**, a three-tier evaluation framework for agentic AI systems based on PydanticAI. The framework addresses the growing need to systematically and reproducibly assess Multi-Agent Systems (MAS) by combining three complementary evaluation tiers: **Tier 1** encompasses text-based metrics (ROUGE, BLEU, BERTScore) for quantitative output analysis, **Tier 2** implements LLM-as-Judge evaluations for qualitative assessments, and **Tier 3** analyzes agent graph behavior for structural execution assessment.

  The PeerRead corpus serves as the benchmark dataset, providing scientific peer-review data from leading conferences and journals. Agent orchestration is handled entirely through PydanticAI, which enables type-safe, model-agnostic agent construction.

  The empirical evaluation is based on **30 traces** and compares four configurations: A **Manager-only** setup achieves a median throughput of 4.8 seconds per task with an error rate of 0%. The **3-agent** configuration requires a median of 12.3 seconds (+156% compared to Manager-only) with an error rate of 25%. In comparison, Claude Code-based systems show significantly higher resource requirements: **CC Solo** requires 118.3 seconds and \$0.94 per execution, **CC Teams** 359.9 seconds and \$1.35. PydanticAI-based agents prove to be 25 to 75 times faster and 50 to 100 times more cost-effective than the Claude Code baselines.

  The framework was iteratively developed over **7 sprints** and is at version **3.3.0** at the time of completion. The results confirm that lightweight, specialized MAS architectures offer significant performance advantages over general-purpose coding agents, provided the task scope is clearly defined.

  **Keywords:** Multi-Agent Systems, LLM Evaluation, PydanticAI, Agentic AI, Evaluation Framework, LLM-as-Judge, Peer Review, Benchmarking, Tracing, Observability
---

\newpage
