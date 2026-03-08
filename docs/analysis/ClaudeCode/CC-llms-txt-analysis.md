---
title: llms.txt Specification, Anthropic Documentation Index, and Project Implementation
description: Analysis of the llms.txt standard, Anthropic's documentation surface area, and this project's template and workflows.
source: https://llmstxt.org/, https://platform.claude.com/llms.txt, https://code.claude.com/docs/llms.txt
category: analysis
created: 2026-03-07
---

**Status**: Stable (spec analysis + 651-page Anthropic index + project implementation)

## Summary

[llms.txt](https://llmstxt.org/) is a curated markdown index file served at a
site's root, designed for AI agents to discover project documentation at
inference time. It solves the context-window problem: websites have too much
HTML/JS/nav boilerplate for LLMs to process efficiently.

This project implements llms.txt via two GitHub workflows and a curated template.

## Specification (llmstxt.org)

### Required Structure

```markdown
# Title                              <- REQUIRED (only mandatory element)

> Optional summary blockquote

Optional body content (no headings)

## Section Name                      <- H2 sections with file lists

- [Link title](url): Optional notes

## Optional                          <- Special: tools may skip this section
                                       for shorter context

- [Link title](url): Secondary info
```

### Key Rules

- File must be valid markdown
- H1 title is the only required element
- Blockquote summary provides key context for understanding the rest
- Body content: any markdown except headings (paragraphs, lists, etc.)
- H2 sections contain file lists: `- [name](url): description`
- `## Optional` has semantic meaning: tools may skip it for shorter context
- Designed for on-demand/inference-time use, not crawling or training

### File Naming and Location

| File | Purpose |
| ---- | ------- |
| `/llms.txt` | Primary index at site root |
| `/llms-full.txt` | Expanded version with all pages |
| `page.html.md` | Markdown version of individual pages |
| `llms-ctx.txt` | Generated expanded context (no URLs) |
| `llms-ctx-full.txt` | Generated expanded context (with URLs) |

### Relationship to Other Standards

- **robots.txt**: Governs crawler access; llms.txt provides content context
  (complementary)
- **sitemap.xml**: Lists all indexable pages; llms.txt curates a focused,
  LLM-sized subset

## Anthropic's Documentation Surface

### platform.claude.com/llms.txt (API/SDK docs)

651 English pages across 11 language versions. Full content at
`platform.claude.com/llms-full.txt`.

<!-- markdownlint-disable MD013 -->

| Section | Pages | Key Topics |
| ------- | ----- | ---------- |
| Getting Started | 3 | Intro, quickstart, features overview |
| Models | 5 | Overview, selection guide, Claude 4.6 changes, migration, deprecations |
| Core API | 4 | Messages API, streaming, token counting, stop reasons |
| Prompt Engineering | 3 | Overview, best practices, console tools |
| Vision & Multimodal | 3 | Vision, PDF support, Files API |
| Reasoning | 2 | Extended thinking, adaptive thinking |
| Output & Structured Data | 2 | Structured outputs, citations |
| Performance & Cost | 5 | Batch processing, prompt caching, compaction, fast mode, latency |
| Tool Use | 10 | Overview, implementation, bash, code execution, computer use, memory, text editor, search |
| Agent SDK | 20+ | Overview, Python/TypeScript SDKs, custom tools, MCP, plugins, skills, hooks, sessions |
| Agent Skills | 4 | Overview, quickstart, best practices, enterprise |
| MCP | 2 | MCP connector, remote MCP servers |
| Quality & Safety | 7 | Evals, hallucinations, consistency, jailbreaks, prompt leak, refusals |
| Admin & Data | 6 | Data residency, ZDR, admin API, usage/cost API, CC analytics, workspaces |
| API Reference | 40+ | Messages, batches, completions, models, files, skills, admin |
| Client SDKs | 9 | Python, TypeScript, C#, Go, Java, PHP, Ruby, OpenAI compat |

<!-- markdownlint-enable MD013 -->

Multi-language SDK coverage: CLI, C#, Go, Java, Kotlin, PHP, Python,
Ruby, Terraform, TypeScript.

### code.claude.com/docs/llms.txt (CC docs)

- ~70 entries in a single flat alphabetical list (no H2 sub-sections)
- Each entry has 1-2 sentence description
- No `## Optional` section, no `llms-full.txt` companion

### Key URLs for This Project

<!-- markdownlint-disable MD013 -->

| Category | URL | Why It Matters |
| -------- | --- | -------------- |
| Agent SDK Overview | `platform.claude.com/docs/en/agent-sdk/overview` | Foundation for understanding CC internals |
| Agent SDK Plugins | `platform.claude.com/docs/en/agent-sdk/plugins` | Plugin architecture for portable agent bundles |
| Agent SDK Skills | `platform.claude.com/docs/en/agent-sdk/skills` | Skills API for programmatic skill management |
| Agent SDK Subagents | `platform.claude.com/docs/en/agent-sdk/subagents` | Subagent architecture reference |
| Agent SDK Hooks | `platform.claude.com/docs/en/agent-sdk/hooks` | Hook system for execution control |
| Agent SDK Cost Tracking | `platform.claude.com/docs/en/agent-sdk/cost-tracking` | Cost/usage monitoring patterns |
| Fast Mode | `platform.claude.com/docs/en/build-with-claude/fast-mode` | API-level fast mode |
| Batch Processing | `platform.claude.com/docs/en/build-with-claude/batch-processing` | 50% cost reduction for async workloads |
| Structured Outputs | `platform.claude.com/docs/en/build-with-claude/structured-outputs` | JSON schema enforcement |
| CC Analytics API | `platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api` | Programmatic CC usage data |
| Eval Tool | `platform.claude.com/docs/en/test-and-evaluate/eval-tool` | Anthropic's evaluation tooling |

<!-- markdownlint-enable MD013 -->

### Pattern Comparison

<!-- markdownlint-disable MD013 -->

| Attribute | platform.claude.com | code.claude.com | This project |
| --------- | ------------------- | --------------- | ------------ |
| H2 sections | 3 grouped | None (flat list) | 5 grouped |
| Link count | ~400+ | ~70 | ~17 |
| Link format | `**[name](url)** - desc` | `[name](url): desc` | `[name](url): desc` |
| URL pattern | `.md` suffix | `.md` suffix | GitHub blob links |
| `## Optional` | Not used | Not used | Used |
| Companion file | `llms-full.txt` | None | None |

<!-- markdownlint-enable MD013 -->

## This Project's Implementation

### Template

`.github/templates/llms.txt.tpl` — curated markdown with `${BLOB}` placeholder
for GitHub blob URLs. Currently has 5 H2 sections and 17 links.

### Workflows

**`write-llms-txt.yaml`** — Generates `docs/llms.txt` from template:

1. Validates all template links point to existing files
2. Substitutes `${BLOB}` with `github.com/{repo}/blob/main`
3. Commits `docs/llms.txt` if changed
4. Triggers on push to `main` when docs/src/template change

**`generate-deploy-mkdocs-ghpages.yaml`** — Deploys docs site:

1. Copies `docs/llms.txt` to `site/llms.txt` at site root
2. Serves raw llms.txt at the documentation site root per spec

### Current Template Sections

| Section | Links | Coverage |
| ------- | ----- | -------- |
| Getting Started | 3 | README, CONTRIBUTING, AGENTS |
| Architecture & Design | 3 | architecture.md, UserStory, roadmap |
| Usage & Operations | 2 | PeerRead usage, troubleshooting |
| Best Practices | 4 | MAS design, security, testing, Python |
| Optional | 5 | Security advisories, CC analysis, landscape |

## Relevance to This Project

<!-- markdownlint-disable MD013 -->

| Documentation Area | Fit | Rationale |
| ------------------ | --- | --------- |
| Agent SDK | Strong | Alternative/complement to PydanticAI for agent orchestration |
| Batch Processing | Strong | 50% cost reduction for evaluation runs |
| CC Analytics API | Strong | Programmatic cost/usage data for CC baseline evaluation |
| Structured Outputs | Moderate | API-level reference for debugging PydanticAI structured outputs |
| Eval Tool | Moderate | Compare with our three-tier pipeline |
| Skills API | Moderate | Programmatic skill management if adopting Cowork plugins |

<!-- markdownlint-enable MD013 -->

### Priority Research Queue

1. **Batch Processing** — Evaluate for tier 2 LLM judge calls (50% cost savings)
2. **CC Analytics API** — Programmatic alternative to manual cost tracking
3. **Agent SDK Subagents** — Compare with PydanticAI delegation patterns
4. **Eval Tool** — Compare Anthropic's evaluation approach with our pipeline

### Improvement Opportunities (Project llms.txt)

- [ ] Add `llms-full.txt` companion (following platform.claude.com pattern)
- [ ] Add descriptions to links (currently most have none)
- [ ] Add Ralph section for autonomous development documentation
- [ ] Add blockquote summary (spec recommends it)

## References

- [llmstxt.org](https://llmstxt.org/) — specification
- [platform.claude.com/llms.txt](https://platform.claude.com/llms.txt) — API docs index
- [platform.claude.com/llms-full.txt](https://platform.claude.com/llms-full.txt) — full API docs
- [code.claude.com/docs/llms.txt](https://code.claude.com/docs/llms.txt) — CC docs index
- `llms_txt2ctx` — CLI tool to expand llms.txt into a flat context file
