---
title: llms.txt Specification and Implementation Analysis
description: Analysis of the llms.txt standard, Anthropic's implementations, and this project's template and workflows.
source: https://llmstxt.org/, https://platform.claude.com/llms.txt, https://code.claude.com/docs/llms.txt
category: analysis
created: 2026-03-07
---

**Status**: Research (informational — feeds into template and workflow improvements)

## Summary

[llms.txt](https://llmstxt.org/) is a curated markdown index file served at a
site's root, designed for AI agents to discover project documentation at
inference time. It solves the context-window problem: websites have too much
HTML/JS/nav boilerplate for LLMs to process efficiently.

This project implements llms.txt via two GitHub workflows and a curated template.

## Specification (llmstxt.org)

### Required Structure

```markdown
# Title                              ← REQUIRED (only mandatory element)

> Optional summary blockquote

Optional body content (no headings)

## Section Name                      ← H2 sections with file lists

- [Link title](url): Optional notes

## Optional                          ← Special: tools may skip this section
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

## Anthropic's Implementations

### platform.claude.com/llms.txt (API/SDK docs)

- H1: "Anthropic Developer Documentation"
- 3 H2 sections: Developer Guide (~130 links), API Reference (~400+ links),
  Resources (~10 links)
- All links use `.md` suffix: `platform.claude.com/docs/en/{category}/{topic}.md`
- References `llms-full.txt` companion for all 651 pages
- Excludes: non-English pages, code examples, API schemas
- Note: `docs.anthropic.com/llms.txt` redirects to `platform.claude.com`

### code.claude.com/docs/llms.txt (CC docs)

- ~70 entries in a single flat alphabetical list (no H2 sub-sections)
- All links use `.md` suffix: `code.claude.com/docs/en/{slug}.md`
- Each entry has 1-2 sentence description
- No `## Optional` section, no `llms-full.txt` companion
- Covers: getting started, configuration, plugins, skills, sandboxing,
  enterprise deployment, monitoring

### Pattern Comparison

| Attribute | platform.claude.com | code.claude.com | This project |
| --------- | ------------------- | --------------- | ------------ |
| H2 sections | 3 grouped | None (flat list) | 5 grouped |
| Link count | ~400+ | ~70 | ~17 |
| Link format | `**[name](url)** - desc` | `[name](url): desc` | `[name](url): desc` |
| URL pattern | `.md` suffix | `.md` suffix | GitHub blob links |
| `## Optional` | Not used | Not used | Used |
| Companion file | `llms-full.txt` | None | None |

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

### Improvement Opportunities

- [ ] Add `llms-full.txt` companion (following platform.claude.com pattern)
- [ ] Add descriptions to links (currently most have none beyond the link title)
- [ ] Add Ralph section for autonomous development documentation
- [ ] Add CC Skills/infrastructure section for agent capability docs
- [ ] Consider flat list alternative (code.claude.com pattern) for simpler
  maintenance
- [ ] Add blockquote summary (currently absent — spec recommends it)
- [ ] Validate against spec: body content should not contain headings between
  H1 and first H2

## References

- [llmstxt.org](https://llmstxt.org/) — specification
- [platform.claude.com/llms.txt](https://platform.claude.com/llms.txt) — Anthropic API docs index
- [code.claude.com/docs/llms.txt](https://code.claude.com/docs/llms.txt) — CC docs index
- [llms_txt2ctx](https://github.com/nicholasgasior/llms-txt2ctx) — CLI tool to expand llms.txt
