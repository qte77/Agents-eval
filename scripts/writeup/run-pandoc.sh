#!/bin/sh
# Pandoc PDF generation script - Functionality:
#  - String splitting for space-separated file lists from Makefile variables
#  - Robust project name/version extraction from [project] section
#  - Proper directory changing logic for image paths
#  - ASCII Record Separator (\036) support for file paths with spaces
#  - LaTeX special character escaping for footer text
#  - File sorting to maintain proper chapter order
#  - Automatic figure placement controls (top/bottom of pages)
#  - Reduced vertical spacing for cleaner heading layout
#  - Multilingual support (English, German, Spanish, French, Italian)
#  - Language-specific figure/table/TOC/bibliography names
#  - Custom TOC title override capability
#  - Clickable cross-references and hyperlinks
#  - Auto-generated List of Figures after TOC (configurable)
#  - Auto-generated List of Tables after TOC (configurable)
#  - Unnumbered title page option (configurable)
set -eu

# Help
if [ "${1:-}" = "help" ]; then
    cat << 'EOF'
Usage: $0 [input_files] [output_file] [title_page] [template] [footer_text] [toc_title] [language] [number_sections] [bibliography] [csl] [list_of_figures] [list_of_tables] [unnumbered_title]

Arguments:
  input_files       Markdown files to convert (glob or \036-separated)
  output_file       Output PDF path (default: output.pdf)
  title_page        LaTeX title page file
  template          LaTeX template file
  footer_text       Footer text ("none" to disable, "all:text" for all pages)
  toc_title         Custom table of contents heading
  language          en-US (default), de-DE, es-ES, fr-FR, it-IT
  number_sections   true (default) or false
  bibliography      BibTeX .bib file — enables --citeproc with IEEE [1] style
  csl               Custom CSL file — overrides default IEEE style
  list_of_figures   true (default) or false — auto-generate List of Figures after TOC
  list_of_tables    true (default) or false — auto-generate List of Tables after TOC
  unnumbered_title  true (default) or false — suppress page number on title page

Examples:
  $0 "*.md" report.pdf title.tex template.tex "Custom Footer" "Table of Contents"
  $0 "*.md" report.pdf "" "" "" "" "en-US" "false"                 # No section numbers
  $0 "*.md" report.pdf "" "" "" "" "de-DE" "true"                  # German
  $0 "*.md" r.pdf "" "" "" "" "en-US" "true" "refs.bib"            # IEEE citations
  $0 "*.md" r.pdf "" "" "" "" "en-US" "true" "refs.bib" "apa.csl" # APA citations
  $0 "*.md" r.pdf "" "" "" "" "" "" "" "" "false" "false"          # No LoF/LoT
  dir=docs/path && make run_pandoc INPUT_FILES="$(printf '%s\036' $dir/*.md)" \
    OUTPUT_FILE="$dir/report.pdf" BIBLIOGRAPHY="$dir/refs.bib"
  make run_pandoc ... LIST_OF_FIGURES=false LIST_OF_TABLES=false   # Disable auto-lists
EOF
    exit 0
fi

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Error: pandoc is not installed. Exiting ..."
    exit 1
fi

# Resolve project root to absolute path (before any cd)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Setup temp directory (writable in sandbox)
TEMP_DIR="$PROJECT_ROOT/.tmp"
mkdir -p "$TEMP_DIR"

# Extract name and version from [project] section
PROJECT_FILE="$PROJECT_ROOT/pyproject.toml"
project_section=$(mktemp -p "$TEMP_DIR")
sed -n '/^\[project\]/,/^\[/p' "$PROJECT_FILE" | sed '$d' > "$project_section"
PROJECT_NAME=$(grep -E '^name[[:space:]]*=' "$project_section" | head -1 | sed -E 's/^name[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/')
VERSION=$(grep -E '^version[[:space:]]*=' "$project_section" | head -1 | sed -E 's/^version[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/')
rm -f "$project_section"

# Parse arguments
input_files_raw="${1:-*.md}"
output_file="${2:-output.pdf}"
title_file="${3:-}"
template_file="${4:-}"
footer_text="${5:-${PROJECT_NAME} v${VERSION}}"
toc_title="${6:-}"
language="${7:-en-US}"
number_sections="${8:-true}"
bibliography_file="${9:-}"
csl_file="${10:-}"
list_of_figures="${11:-true}"
list_of_tables="${12:-true}"
unnumbered_title="${13:-true}"

# Handle separator-delimited file lists
RS_CHAR=$(printf '\036')
if echo "$input_files_raw" | grep -q "$RS_CHAR"; then
    input_files=$(echo "$input_files_raw" | tr "$RS_CHAR" ' ')
else
    input_files="$input_files_raw"
fi

# Build base command with language metadata
set -- --toc --toc-depth=2 \
       -V geometry:"margin=1in,footskip=35pt" \
       -V documentclass=report \
       --pdf-engine=xelatex \
       --from markdown+smart \
       -V pagestyle=plain \
       --metadata lang="$language"

# Add number-sections if enabled
[ "$number_sections" = "true" ] && set -- "$@" --number-sections
# Add custom TOC title if specified
[ -n "$toc_title" ] && set -- "$@" -V toc-title="$toc_title"

# Handle directory changes for image paths
work_dir=""
title_added=false
if echo "$input_files" | grep -q "/"; then
    for file in $input_files; do
        [ -f "$file" ] && work_dir=$(dirname "$file") && break
    done
    
    if [ -n "$work_dir" ]; then
        # Convert paths before changing directory
        temp_files=""
        for file in $input_files; do
            [ -f "$file" ] && temp_files="$temp_files $(basename "$file")"
        done
        if [ -n "$title_file" ] && [ -f "$title_file" ]; then
            set -- "$@" -B "$(basename "$title_file")"
            title_added=true
        fi
        
        # Convert relative paths to absolute before cd
        case "$output_file" in /*) ;; *) output_file="$(pwd)/$output_file" ;; esac
        if [ -n "$bibliography_file" ] && [ -f "$bibliography_file" ]; then
            case "$bibliography_file" in /*) ;; *) bibliography_file="$(pwd)/$bibliography_file" ;; esac
        fi
        if [ -n "$csl_file" ] && [ -f "$csl_file" ]; then
            case "$csl_file" in /*) ;; *) csl_file="$(pwd)/$csl_file" ;; esac
        fi
        cd "$work_dir"
        input_files=$(printf '%s\n' $temp_files | sort | tr '\n' ' ' | sed 's/^ *//; s/ *$//')
    fi
fi

# Add title if not set by directory change
[ "$title_added" = false ] && [ -n "$title_file" ] && [ -f "$title_file" ] && set -- "$@" -B "$title_file"

# Add template
[ -n "$template_file" ] && [ -f "$template_file" ] && set -- "$@" --template="$template_file"

# Add header settings (figure placement + footer)
header_temp=$(mktemp -p "$TEMP_DIR")
cleanup_header=1

# Always add figure placement controls and spacing adjustments
cat > "$header_temp" << EOF
% Unicode-complete fonts (TeX Gyre: POSIX standard equivalents)
% Fallback chain: TeX Gyre -> Latin Modern (XeLaTeX default)
\\usepackage{fontspec}
\\IfFontExistsTF{TeX Gyre Termes}{%
  \\setmainfont{TeX Gyre Termes}%
  \\setsansfont{TeX Gyre Heros}%
  \\setmonofont[HyphenChar="002D,Scale=MatchLowercase]{TeX Gyre Cursor}%
}{}

% Typography: protrusion + narrower word spacing
\\PassOptionsToPackage{protrusion=true,expansion=false}{microtype}
\\spaceskip=0.33em plus 0.15em minus 0.12em
\\emergencystretch=3em

% Fix monospace overflow: wrap long lines in code blocks and inline code
\\usepackage{fvextra}
\\fvset{breaklines=true,breakanywhere=true}
\\usepackage[htt]{hyphenat}
\\usepackage{xurl}

% Landscape pages for wide figures (auto-scale images to fit)
\\usepackage{pdflscape}
\\AtBeginEnvironment{landscape}{\\setkeys{Gin}{width=\\linewidth,keepaspectratio}}

% Prevent oversized images from overflowing page width or height
\\usepackage[export]{adjustbox}
\\makeatletter
\\def\\ScaleWidthIfNeeded{%
  \\ifdim\\Gin@nat@width>\\linewidth
    \\linewidth
  \\else
    \\Gin@nat@width
  \\fi
}
\\def\\ScaleHeightIfNeeded{%
  \\ifdim\\Gin@nat@height>0.9\\textheight
    0.9\\textheight
  \\else
    \\Gin@nat@height
  \\fi
}
\\makeatother
\\setkeys{Gin}{width=\\ScaleWidthIfNeeded,height=\\ScaleHeightIfNeeded,keepaspectratio}
% TODO: Auto-rotate landscape images 90° CCW when nat_width > threshold * nat_height
% and nat_width > \\linewidth (i.e., the image would be scaled down to fit portrait).
%
% Problem: \\renewcommand{\\includegraphics} conflicts with pandoc's default
% template \\setkeys{Gin}{width=\\maxwidth,...} and raw LaTeX [width=\\textwidth]
% overrides in content files. The Gin defaults mask natural dimensions during
% measurement, and explicit width= in #1 overrides rotation constraints.
%
% Recommended fix: pandoc Lua filter (auto-rotate.lua) that inspects image
% dimensions at the AST level and wraps qualifying images in sidewaysfigure:
%   function Image(img)
%     local w, h = img_dimensions(img.src)
%     if w > 1.3 * h then
%       return pandoc.RawInline('latex',
%         '\\begin{sidewaysfigure}[!htbp]\\centering'
%         .. '\\includegraphics[width=\\textheight,keepaspectratio]{'..img.src..'}'
%         .. '\\caption{'..pandoc.utils.stringify(img.caption)..'}'
%         .. '\\end{sidewaysfigure}')
%     end
%   end
% Invoke via: pandoc --lua-filter=auto-rotate.lua
%
% Threshold guidance (nat_width / nat_height):
%   1.0 = any landscape image (too aggressive, catches near-square)
%   1.2 = mildly landscape (4:3 screens, some diagrams)
%   1.3 = recommended (catches wide diagrams/timelines, skips near-square)
%   1.5 = only very wide images (panoramic, wide flowcharts)
%   2.0 = ultra-wide only (banners, timeline strips)

\\usepackage{float}
\\floatplacement{figure}{!tb}
\\renewcommand{\\topfraction}{0.9}
\\renewcommand{\\bottomfraction}{0.9}
\\renewcommand{\\textfraction}{0.1}
\\setcounter{topnumber}{3}
\\setcounter{bottomnumber}{3}

% Language-specific figure and table names
EOF

# Add language-specific commands
case "$language" in
    de-DE|de)
        figure_name="Abbildung"
        table_name="Tabelle"
        contents_name="Inhaltsverzeichnis"
        bibliography_name="Literaturverzeichnis"
        list_of_figures_name="Abbildungsverzeichnis"
        list_of_tables_name="Tabellenverzeichnis"
        chapter_name="Kapitel"
        abstract_name="Abstrakt"
        ;;
    es-ES|es)
        figure_name="Figura"
        table_name="Tabla"
        contents_name="Índice"
        bibliography_name="Bibliografía"
        list_of_figures_name="Índice de figuras"
        list_of_tables_name="Índice de tablas"
        chapter_name="Capítulo"
        abstract_name="Resumen"
        ;;
    fr-FR|fr)
        figure_name="Figure"
        table_name="Tableau"
        contents_name="Table des matières"
        bibliography_name="Bibliographie"
        list_of_figures_name="Table des figures"
        list_of_tables_name="Liste des tableaux"
        chapter_name="Chapitre"
        abstract_name="Résumé"
        ;;
    it-IT|it)
        figure_name="Figura"
        table_name="Tabella"
        contents_name="Indice"
        bibliography_name="Bibliografia"
        list_of_figures_name="Elenco delle figure"
        list_of_tables_name="Elenco delle tabelle"
        chapter_name="Capitolo"
        abstract_name="Sommario"
        ;;
    *)
        figure_name="Figure"
        table_name="Table"
        contents_name=""
        bibliography_name=""
        list_of_figures_name=""
        list_of_tables_name=""
        chapter_name=""
        abstract_name=""
        ;;
esac

# Apply language settings (deferred to \AtBeginDocument to override polyglossia/babel)
lang_renames="\\renewcommand{\\figurename}{$figure_name}\\renewcommand{\\tablename}{$table_name}"
[ -n "$list_of_figures_name" ] && lang_renames="$lang_renames\\renewcommand{\\listfigurename}{$list_of_figures_name}"
[ -n "$list_of_tables_name" ] && lang_renames="$lang_renames\\renewcommand{\\listtablename}{$list_of_tables_name}"
[ -n "$chapter_name" ] && lang_renames="$lang_renames\\renewcommand{\\chaptername}{$chapter_name}"
[ -n "$contents_name" ] && lang_renames="$lang_renames\\renewcommand{\\contentsname}{$contents_name}"
[ -n "$abstract_name" ] && lang_renames="$lang_renames\\renewcommand{\\abstractname}{$abstract_name}"
if [ -n "$bibliography_name" ]; then
    lang_renames="$lang_renames\\renewcommand{\\bibname}{$bibliography_name}"
    lang_renames="$lang_renames\\@ifundefined{refname}{}{\\renewcommand{\\refname}{$bibliography_name}}"
fi
cat >> "$header_temp" << EOF
\\makeatletter
\\AtBeginDocument{$lang_renames}
\\makeatother
EOF

# Override TOC title if explicitly provided
[ -n "$toc_title" ] && cat >> "$header_temp" << EOF
\\renewcommand{\\contentsname}{$toc_title}
EOF

cat >> "$header_temp" << EOF

% Reduce vertical space above headings using standard LaTeX
\\makeatletter
\\renewcommand{\\@makechapterhead}[1]{%
  \\vspace*{20\\p@}%
  {\\parindent \\z@ \\raggedright \\normalfont
    \\interlinepenalty\\@M
    \\Huge \\bfseries
    \\ifnum \\c@secnumdepth >\\m@ne
        \\thechapter\\quad
    \\fi
    #1\\par\\nobreak
    \\vskip 20\\p@
  }}
\\renewcommand{\\@makeschapterhead}[1]{%
  \\vspace*{20\\p@}%
  {\\parindent \\z@ \\raggedright
    \\normalfont
    \\interlinepenalty\\@M
    \\Huge \\bfseries  #1\\par\\nobreak
    \\vskip 20\\p@
  }}

% Enable clickable cross-references
\\usepackage{hyperref}
\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}
\\usepackage{etoolbox}
\\makeatother
EOF

# Suppress page number on title page (always-injected, independent of footer)
if [ "$unnumbered_title" = "true" ]; then
    cat >> "$header_temp" << EOF
\\AtBeginDocument{\\thispagestyle{empty}}
EOF
fi

# Add footer (skip if using template)
if [ -n "$footer_text" ] && [ "$footer_text" != "none" ] && [ -z "$template_file" ]; then
    # Check if footer should include title/TOC pages (if footer_text contains "all:")
    if echo "$footer_text" | grep -q "^all:"; then
        # Include footer on all pages including title and TOC
        actual_footer=$(echo "$footer_text" | sed 's/^all://')
        safe_footer=$(printf '%s' "$actual_footer" | sed 's/[&\\]/\\&/g; s/#/\\#/g; s/\$/\\$/g; s/_/\\_/g; s/%/\\%/g')
        cat >> "$header_temp" << EOF
\\usepackage{fancyhdr}
\\pagestyle{fancy}
\\fancyhf{}
\\fancyfoot[L]{$safe_footer}
\\fancyfoot[R]{\\thepage}
\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0.4pt}
\\fancypagestyle{plain}{\\fancyhf{}\\fancyfoot[L]{$safe_footer}\\fancyfoot[R]{\\thepage}}
EOF
    else
        # Default: no footer on title page, roman numerals with footer on TOC, arabic+footer on content
        safe_footer=$(printf '%s' "$footer_text" | sed 's/[&\\]/\\&/g; s/#/\\#/g; s/\$/\\$/g; s/_/\\_/g; s/%/\\%/g')
        cat >> "$header_temp" << EOF
\\usepackage{fancyhdr}
\\pagestyle{fancy}
\\fancyhf{}
\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0.4pt}
\\fancyfoot[L]{$safe_footer}
\\fancyfoot[R]{\\thepage}
\\fancypagestyle{empty}{\\fancyhf{}\\renewcommand{\\headrulewidth}{0pt}\\renewcommand{\\footrulewidth}{0pt}}
\\fancypagestyle{plain}{\\fancyhf{}\\fancyfoot[L]{$safe_footer}\\fancyfoot[R]{\\thepage}\\renewcommand{\\headrulewidth}{0pt}\\renewcommand{\\footrulewidth}{0.4pt}}
\\AtBeginDocument{\\pagenumbering{roman}}
\\preto\\tableofcontents{\\clearpage\\pagenumbering{roman}\\setcounter{page}{1}}
EOF
    fi
fi

# Auto-inject abbreviations after TOC if 00_abbreviations.tex exists in work dir
# After cd into work_dir, the file is in the current directory
if [ -f "00_abbreviations.tex" ]; then
    cat >> "$header_temp" << EOF
\\appto\\tableofcontents{\\clearpage\\input{00_abbreviations.tex}}
EOF
fi

# Auto-generate List of Figures / List of Tables after TOC (before arabic page numbering)
if [ "$list_of_figures" = "true" ]; then
    cat >> "$header_temp" << EOF
\\appto\\tableofcontents{\\clearpage\\listoffigures}
EOF
fi
if [ "$list_of_tables" = "true" ]; then
    cat >> "$header_temp" << EOF
\\appto\\tableofcontents{\\clearpage\\listoftables}
EOF
fi

# Switch to arabic page numbering after TOC/LoF/LoT (when footer provides roman numerals)
if [ -n "$footer_text" ] && [ "$footer_text" != "none" ] && [ -z "$template_file" ]; then
    if ! echo "$footer_text" | grep -q "^all:"; then
        cat >> "$header_temp" << EOF
\\appto\\tableofcontents{\\clearpage\\pagenumbering{arabic}\\setcounter{page}{1}}
EOF
    fi
fi

# Add the header to pandoc arguments
set -- "$@" -H "$header_temp"

# Add bibliography/citation support if provided
if [ -n "$bibliography_file" ] && [ -f "$bibliography_file" ]; then
    set -- "$@" --citeproc --bibliography="$bibliography_file"
    set -- "$@" -M link-citations=true
    # Language-specific references heading on a new page
    set -- "$@" -M reference-section-title="${bibliography_name:-References}"
    echo "Bibliography: $bibliography_file"
    if [ -n "$csl_file" ] && [ -f "$csl_file" ]; then
        set -- "$@" --csl="$csl_file"
        echo "Citation style: $csl_file"
    else
        # Pandoc default is Chicago author-date; use IEEE numeric [1] style
        default_csl="$PROJECT_ROOT/scripts/writeup/citation-styles/ieee.csl"
        if [ -f "$default_csl" ]; then
            set -- "$@" --csl="$default_csl"
        fi
        echo "Citation style: IEEE (default)"
    fi
fi

# Run pandoc
echo "Converting '$input_files_raw' to '$output_file'..."
if ! pandoc "$@" -o "$output_file" $input_files; then
    [ "$cleanup_header" -eq 1 ] && rm -f "$header_temp"
    echo "Error: PDF generation failed"
    exit 1
fi

# Cleanup
[ "$cleanup_header" -eq 1 ] && rm -f "$header_temp"

echo "PDF generated successfully: $output_file"

# --- Auto-generate BUILD.md ---
_out_dir=$(dirname "$output_file")
_out_name=$(basename "$output_file")
_pv=$(pandoc --version 2>/dev/null | head -1 | sed 's/pandoc //' || echo "unknown")
_cwd="${work_dir:-.}"
# Build file lists with directory prefix for BUILD.md
_input_full=""
for _f in $input_files; do _input_full="$_input_full $_cwd/$_f"; done
_input_full=$(echo "$_input_full" | sed 's/^ //')
# Resolve title_file path (may be basename after cd into work_dir)
_title_full=""
[ -n "$title_file" ] && _title_full="$_cwd/$(basename "$title_file")"
# Strip PROJECT_ROOT prefix to produce relative paths
_bib_rel=$(echo "$bibliography_file" | sed "s|^$PROJECT_ROOT/||")
_csl_rel=$(echo "$csl_file" | sed "s|^$PROJECT_ROOT/||")
{
    printf '# Build Instructions for %s v%s\n\n' "$PROJECT_NAME" "$VERSION"

    # --- Make recipe (recommended) ---
    printf '## Make Recipe (Recommended)\n\n```bash\n'
    printf 'make pandoc_run \\\n'
    printf '  INPUT_FILES="$$(printf '\''%%s\\036'\'' %s)" \\\n' "$_input_full"
    printf '  OUTPUT_FILE="%s"' "$_cwd/$_out_name"
    [ -n "$_title_full" ] && \
        printf ' \\\n  TITLE_PAGE="%s"' "$_title_full"
    [ -n "$bibliography_file" ] && [ -f "$bibliography_file" ] && \
        printf ' \\\n  BIBLIOGRAPHY="%s"' "$_bib_rel"
    [ -n "$csl_file" ] && [ -f "$csl_file" ] && \
        printf ' \\\n  CSL="%s"' "$_csl_rel"
    [ "$number_sections" = "true" ] && \
        printf ' \\\n  NUMBER_SECTIONS="true"'
    [ "$list_of_figures" != "true" ] && \
        printf ' \\\n  LIST_OF_FIGURES="false"'
    [ "$list_of_tables" != "true" ] && \
        printf ' \\\n  LIST_OF_TABLES="false"'
    printf '\n```\n\n'

    # --- Raw pandoc command (standalone) ---
    printf '## Raw Pandoc Command (Standalone)\n\n```bash\ncd %s && \\\npandoc \\\n' "$_cwd"
    for _f in $input_files; do printf '  %s \\\n' "$_f"; done
    [ -n "$_title_full" ] && \
        printf '  -B %s \\\n' "$(basename "$_title_full")"
    printf '  --toc --toc-depth=2 \\\n'
    [ "$number_sections" = "true" ] && printf '  --number-sections \\\n'
    printf '  -V geometry:"margin=1in,footskip=35pt" \\\n'
    printf '  -V documentclass=report \\\n'
    printf '  --pdf-engine=xelatex \\\n'
    printf '  --from markdown+smart \\\n'
    printf '  -V pagestyle=plain'
    [ -n "$bibliography_file" ] && [ -f "$bibliography_file" ] && \
        printf ' \\\n  --citeproc \\\n  --bibliography=%s' "$(basename "$bibliography_file")"
    [ -n "$csl_file" ] && [ -f "$csl_file" ] && \
        printf ' \\\n  --csl=%s' "$_csl_rel"
    printf ' \\\n  -o %s\n```\n\n' "$_out_name"
    printf '> **Note**: The raw command omits header-includes (font setup, image scaling,\n'
    printf '> LoF/LoT, footer). Use the make recipe for full-featured builds.\n\n'

    # --- Prerequisites & Notes ---
    printf '## Prerequisites\n\n'
    printf '%s\n' "- \`make\` with project Makefile"
    printf '%s\n' "- \`pandoc\` (tested with $_pv)"
    printf '%s\n\n' "- \`xelatex\` (TeX Live) — install via \`make setup_pdf_converter CONVERTER=pandoc\`"
    printf '## Notes\n\n'
    printf '%s\n' "- **PDF engine**: \`xelatex\` (hardcoded in \`run-pandoc.sh\`)"
    printf '%s\n' "- **LoF/LoT**: enabled by default; disable with \`LIST_OF_FIGURES=false\`"
} > "$_out_dir/BUILD.md"
echo "Build instructions: $_out_dir/BUILD.md"

# --- Create/update blog-post.md template ---
printf '%s\n' "---" "layout: post" "title: \"$PROJECT_NAME v$VERSION\"" \
    "excerpt: \"\"" "categories: []" "---" "" "# $PROJECT_NAME" "" \
    "TODO: Write blog post summary." > "$_out_dir/blog-post.md"
echo "Blog post template: $_out_dir/blog-post.md"