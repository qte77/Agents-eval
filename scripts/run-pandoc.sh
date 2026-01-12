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

# Help
if [ "$1" = "help" ]; then
    cat << 'EOF'
Usage: $0 [input_files [output_file] [title_page] [template] [footer_text] [toc_title] [language] [number_sections]]

Available Languages:
  en-US, en    English (default)
  de-DE, de    German
  es-ES, es    Spanish
  fr-FR, fr    French
  it-IT, it    Italian

Examples:
  $0 "*.md" report.pdf title.tex template.tex "Custom Footer" "Table of Contents"
  $0 "*.md" report.pdf "" "" "" "" "en-US" "false"  # Disable section numbering
  $0 "*.md" report.pdf "" "" "" "" "de-DE" "true"   # German with section numbering
  dir=docs/path && make run_pandoc INPUT_FILES="$(printf '%s\036' $dir/*.md)" OUTPUT_FILE="$dir/report.pdf"
EOF
    exit 0
fi

# Extract name and version from [project] section
PROJECT_FILE="$(dirname "$0")/../pyproject.toml"
project_section=$(mktemp)
sed -n '/^\[project\]/,/^\[/p' "$PROJECT_FILE" | head -n -1 > "$project_section"
PROJECT_NAME=$(grep -E '^name[[:space:]]*=' "$project_section" | head -1 | sed -E 's/^name[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/')
VERSION=$(grep -E '^version[[:space:]]*=' "$project_section" | head -1 | sed -E 's/^version[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/')
rm -f "$project_section"

# Parse arguments
input_files_raw="${1:-!(01_*)*.md}"
output_file="${2:-output.pdf}"
title_file="$3"
template_file="$4"
footer_text="${5:-${PROJECT_NAME} v${VERSION}}"
toc_title="$6"
language="${7:-en-US}"
number_sections="${8:-true}"

# Handle separator-delimited file lists
RS_CHAR=$(printf '\036')
if echo "$input_files_raw" | grep -q "$RS_CHAR"; then
    input_files=$(echo "$input_files_raw" | tr "$RS_CHAR" ' ')
else
    input_files="$input_files_raw"
fi

# Build base command with language metadata
set -- --toc --toc-depth=2 \
       -V geometry:margin=1in \
       -V documentclass=report \
       --pdf-engine=pdflatex \
       -M protrusion \
       --from markdown+smart \
       -V pagestyle=plain \
       --metadata lang="$language"

# Add number-sections if enabled
[ "$number_sections" = "true" ] && set -- "$@" --number-sections
# Add custom TOC title if specified
[ -n "$toc_title" ] && set -- "$@" -V toc-title="$toc_title"

# Handle directory changes for image paths
work_dir=""
title_arg=""
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
        [ -n "$title_file" ] && [ -f "$title_file" ] && title_arg="-B $(basename "$title_file")"
        
        # Change directory and update paths
        case "$output_file" in /*) ;; *) output_file="$(pwd)/$output_file" ;; esac
        cd "$work_dir"
        input_files=$(printf '%s\n' $temp_files | sort | tr '\n' ' ' | sed 's/^ *//; s/ *$//')
    fi
fi

# Add title if not set by directory change
[ -z "$title_arg" ] && [ -n "$title_file" ] && [ -f "$title_file" ] && title_arg="-B $title_file"

# Add template
[ -n "$template_file" ] && [ -f "$template_file" ] && set -- "$@" --template="$template_file"

# Add header settings (figure placement + footer)
header_temp=$(mktemp)
cleanup_header=1

# Always add figure placement controls and spacing adjustments
cat > "$header_temp" << EOF
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
        ;;
    es-ES|es)
        figure_name="Figura"
        table_name="Tabla"
        contents_name="Índice"
        bibliography_name="Bibliografía"
        ;;
    fr-FR|fr)
        figure_name="Figure"
        table_name="Tableau"
        contents_name="Table des matières"
        bibliography_name="Bibliographie"
        ;;
    it-IT|it)
        figure_name="Figura"
        table_name="Tabella"
        contents_name="Indice"
        bibliography_name="Bibliografia"
        ;;
    *)
        figure_name="Figure"
        table_name="Table"
        contents_name=""
        bibliography_name=""
        ;;
esac

# Apply language settings
cat >> "$header_temp" << EOF
\\renewcommand{\\figurename}{$figure_name}
\\renewcommand{\\tablename}{$table_name}
EOF

# Add contents name only if specified (non-English languages)
[ -n "$contents_name" ] && cat >> "$header_temp" << EOF
\\renewcommand{\\contentsname}{$contents_name}
EOF

# Add bibliography name only if specified (non-English languages)
[ -n "$bibliography_name" ] && cat >> "$header_temp" << EOF
\\renewcommand{\\bibname}{$bibliography_name}
\\renewcommand{\\refname}{$bibliography_name}
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
    \\ifnum \\c@secnumdepth >\\m@ne
        \\huge\\bfseries \\@chapapp\\space \\thechapter
        \\par\\nobreak
        \\vskip 20\\p@
    \\fi
    \\interlinepenalty\\@M
    \\Huge \\bfseries #1\\par\\nobreak
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
\\makeatother
EOF

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
\\usepackage{etoolbox}
\\pagestyle{fancy}
\\fancyhf{}
\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0.4pt}
\\fancyfoot[L]{$safe_footer}
\\fancyfoot[R]{\\thepage}
\\fancypagestyle{empty}{\\fancyhf{}\\renewcommand{\\headrulewidth}{0pt}\\renewcommand{\\footrulewidth}{0pt}}
\\fancypagestyle{plain}{\\fancyhf{}\\fancyfoot[L]{$safe_footer}\\fancyfoot[R]{\\thepage}\\renewcommand{\\headrulewidth}{0pt}\\renewcommand{\\footrulewidth}{0.4pt}}
\\AtBeginDocument{\\pagenumbering{roman}\\thispagestyle{empty}}
\\preto\\tableofcontents{\\clearpage\\pagenumbering{roman}\\setcounter{page}{1}}
\\appto\\tableofcontents{\\clearpage\\pagenumbering{arabic}\\setcounter{page}{1}}
EOF
    fi
fi

# Add the header to pandoc arguments
set -- "$@" -H "$header_temp"

# Enable extended globbing
[ -n "${BASH_VERSION}" ] && shopt -s extglob 2>/dev/null

# Run pandoc
echo "Converting '$input_files_raw' to '$output_file'..."
if [ -n "$title_arg" ]; then
    pandoc "$@" $title_arg -o "$output_file" $input_files
else
    pandoc "$@" -o "$output_file" $input_files
fi
result=$?

# Cleanup
[ "$cleanup_header" -eq 1 ] && rm -f "$header_temp"

# Check result
if [ $result -eq 0 ]; then
    echo "PDF generated successfully: $output_file"
else
    echo "Error: PDF generation failed"
    exit 1
fi