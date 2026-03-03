# Writeup Template

Use this template when generating writeup files. Replace `<topic>` and
`<title>` with actual values.

## Title Page and Abstract (`00_title_abstract.tex`)

Raw LaTeX file passed via `TITLE_PAGE` parameter (`-B` before-body).
Gives full control over title page layout, abstract, and optional
abbreviation lists.

```latex
% Title page for pandoc -B (before-body) option
\hypersetup{pdftitle={<title>}}

\begin{titlepage}
\centering
{\Huge \textbf{<title>}}\\[1.5cm]
{\Large <subtitle>}\\[1cm]
\vfill
{\large Version X.Y.Z}\\[0.3cm]
{\large \today}
\end{titlepage}

\section*{Abstract}

Abstract text here.

\textbf{Keywords:} keyword1, keyword2

\newpage
```

## Build Settings (`00_frontmatter.md`)

YAML-only metadata for pandoc build configuration. No content.

```yaml
---
toc-depth: 3
reference-section-title: References
linestretch: 1.25
geometry: "margin=2.5cm,footskip=30pt"
---
```

- `reference-section-title` - Heading for the auto-generated reference list
- LoF/LoT are controlled by `LIST_OF_FIGURES` / `LIST_OF_TABLES` make
  variables (default: `true`), not YAML metadata

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

**List of Figures** and **List of Tables** are generated automatically
by `run-pandoc.sh` (default: both enabled). Disable via make variables:

```bash
make pandoc_run ... LIST_OF_FIGURES=false LIST_OF_TABLES=false
```

## Document Structure

### Simple (short reports, summaries)

```text
docs/write-up/<topic>/
├── 00_title_abstract.tex  # LaTeX title page + abstract (pandoc -B)
├── 00_frontmatter.md      # YAML-only build settings
├── 01_introduction.md
├── 02_methods.md
├── 03_results.md
├── 04_conclusion.md
└── references.bib
```

### Complex (research papers, technical reports)

```text
docs/write-up/<topic>/
├── 00_title_abstract.tex  # LaTeX title page + abstract (pandoc -B)
├── 00_frontmatter.md      # YAML-only build settings
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
