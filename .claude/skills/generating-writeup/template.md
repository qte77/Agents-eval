# Writeup Template

Use this template when generating writeup files. Replace `<topic>` and
`<title>` with actual values.

## Frontmatter (`00_frontmatter.md`)

```yaml
---
title: "<title>"
bibliography: references.bib
reference-section-title: References
nocite: ""
---
```

- `bibliography` - Path to `.bib` file (relative to document directory)
- `reference-section-title` - Heading for the auto-generated reference list
- `nocite: "@*"` - Include all entries even if not cited (optional)

## BibTeX (`references.bib`)

```bibtex
@article{smith2024,
  author  = {Smith, John and Doe, Jane},
  title   = {A Study of Multi-Agent Systems},
  journal = {Journal of AI Research},
  year    = {2024},
  volume  = {42},
  pages   = {1--15},
  doi     = {10.1234/jair.2024.001}
}

@inproceedings{lee2023,
  author    = {Lee, Alice},
  title     = {Evaluation Frameworks for LLM Agents},
  booktitle = {Proceedings of NeurIPS},
  year      = {2023},
  pages     = {100--110}
}

@book{russell2021,
  author    = {Russell, Stuart and Norvig, Peter},
  title     = {Artificial Intelligence: A Modern Approach},
  publisher = {Pearson},
  year      = {2021},
  edition   = {4th}
}

@online{anthropic2024,
  author  = {{Anthropic}},
  title   = {Claude Code Documentation},
  url     = {https://docs.anthropic.com/en/docs/claude-code},
  urldate = {2026-02-08},
  year    = {2024}
}
```

## Citation Syntax

Use pandoc-citeproc `[@key]` references in markdown text:

```markdown
[@key]                    → [1]
[@key1; @key2]            → [1, 2]
[-@key]                   → suppress author
@key says...              → author-in-text (APA style)
```

## Bibliography Placement

By default, pandoc appends the reference list at the end of the document.

For explicit placement, add this div where references should appear:

```markdown
::: {#refs}
:::
```

## Figures and Tables

Pandoc auto-numbers figures and tables per chapter (e.g. Figure 1.1,
Table 2.1). Reference them by description in the text:

```markdown
Figure 1 shows the system overview.

![Caption text](diagrams/figure.png){width=90%}

Table 1 summarizes the results.

| Col1 | Col2 |
|------|------|
| data | data |

: Caption text
```

To generate a **List of Figures** or **List of Tables** after the
table of contents, add to the frontmatter:

```yaml
---
lof: true
lot: true
---
```

## Document Structure

### Simple (short reports, summaries)

```text
docs/write-up/<topic>/
├── 00_frontmatter.md    # Title, abstract, YAML frontmatter
├── 01_introduction.md
├── 02_methods.md
├── 03_results.md
├── 04_conclusion.md
└── references.bib
```

### Complex (research papers, technical reports)

```text
docs/write-up/<topic>/
├── 00_frontmatter.md
├── 01_introduction.md
├── 02_background.md
├── 03_methodology.md
├── 04_implementation.md
├── 05_evaluation.md
├── 06_results.md
├── 07_discussion.md
├── 08_conclusion.md
├── 09_appendix.md
├── diagrams/
└── references.bib
```
