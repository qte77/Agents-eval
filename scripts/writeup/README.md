# Writeup Scripts

PDF generation and diagram rendering scripts for the project writeup.

## Scripts

- `run-pandoc.sh` — Convert markdown to PDF with citations via pandoc + texlive
- `setup-pdf-converter.sh` — Install pandoc or other PDF converters
- `generate-plantuml-png.sh` — Render PlantUML diagrams to PNG

## Usage

```bash
make pandoc_run          # Convert writeup to PDF (see make pandoc_run HELP=1)
make writeup             # Full writeup pipeline with title page
make setup_pdf_converter CONVERTER=pandoc
```

## Known Gotchas

### LaTeX `\@commands` in `\AtBeginDocument` Require Outer `\makeatletter`

`\AtBeginDocument` tokenizes its argument at parse time. If `@` has catcode
"other" (default), `\@ifundefined` is tokenized as `\@` (spacefactor) + literal
text. At `\begin{document}`, `\@` executes in vertical mode →
`! You can't use \spacefactor in vertical mode`.

**Fix**: Wrap in `\makeatletter...\makeatother` *outside* `\AtBeginDocument`,
not inside — catcode changes only affect future tokenization.

```latex
\makeatletter
\AtBeginDocument{\@ifundefined{refname}{}{...}}
\makeatother
```

Relevant: `run-pandoc.sh:292-296`

### `make writeup` — Title Page Not Appearing

`00_title_abstract.tex` must be passed explicitly via `TITLE_PAGE=` to the
`pandoc_run` sub-make. Pandoc does not auto-discover files by naming convention.

```makefile
$(MAKE) pandoc_run TITLE_PAGE="$(WRITEUP_DIR)/00_title_abstract.tex" ...
```
