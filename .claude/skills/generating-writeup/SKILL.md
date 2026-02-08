---
name: generating-writeup
description: Generates academic/technical writeups with IEEE citations and pandoc PDF output. Use when creating research papers, technical reports, or documentation with references.
compatibility: Designed for Claude Code
metadata:
  argument-hint: [topic] [citation-style]
  allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Writeup Generation

**Target**: $ARGUMENTS

Generates **structured academic/technical writeups** with pandoc citation
support. IEEE `[1]` style by default.

## Workflow

1. **Parse arguments** - Extract topic and optional citation style
2. **Create directory** - `docs/write-up/<topic>/`
3. **Generate sections** - Use [template.md](template.md) for structure and formats
4. **Setup bibliography** - Create `references.bib` (see template for BibTeX format)
5. **Add YAML frontmatter** - See template for required fields
6. **Run markdownlint** - `make run_markdownlint INPUT_FILES="docs/write-up/<topic>/*.md"`
7. **Generate PDF** - `make run_pandoc` with `BIBLIOGRAPHY` variable

## Additional Resources

- For document structure, frontmatter, and BibTeX format, see [template.md](template.md)

## Citation Styles

| Style | How | Notes |
| ----- | --- | ----- |
| IEEE (default) | Bundled (`scripts/citation-styles/ieee.csl`) | Numeric `[1]` |
| APA | Bundled (`scripts/citation-styles/apa.csl`) | Author-date `(Smith, 2024)` |
| Chicago | Bundled (`scripts/citation-styles/chicago-author-date.csl`) | Author-date `(Smith 2024)` |
| Vancouver | Bundled (`scripts/citation-styles/vancouver.csl`) | Numeric `(1)` |

Additional CSL files are available from the
[Zotero Style Repository](https://www.zotero.org/styles).

## Pandoc Command

Generate PDF with citations:

```bash
dir=docs/write-up/<topic> && \
make run_pandoc \
  INPUT_FILES="$$(printf '%s\036' $$dir/*.md)" \
  OUTPUT_FILE="$$dir/output.pdf" \
  BIBLIOGRAPHY="$$dir/references.bib"
```

With custom citation style:

```bash
dir=docs/write-up/<topic> && \
make run_pandoc \
  INPUT_FILES="$$(printf '%s\036' $$dir/*.md)" \
  OUTPUT_FILE="$$dir/output.pdf" \
  BIBLIOGRAPHY="$$dir/references.bib" \
  CSL="scripts/citation-styles/apa.csl"
```

## Quality Checks

Before completing:

1. **Markdownlint** - `make run_markdownlint INPUT_FILES="docs/write-up/<topic>/*.md"`
2. **Citation validation** - Verify all `[@key]` references exist in `.bib` file
3. **PDF generation** - Run pandoc command above and confirm output
