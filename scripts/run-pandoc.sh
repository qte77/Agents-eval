#!/bin/bash

# Pandoc PDF generation script
# Converts markdown files to PDF with customizable options

# Check for help request first - if first argument is "help", show help and exit
if [ "$1" = "help" ]; then
    cat << EOF
Usage: $0 [help | input_file(s) [output_file] [title_page] [template] [footer_text]]

Arguments:
  help          : Show this help message and exit
  input_file(s) : Markdown files to convert (default: !(01_*)*.md)
  output_file   : Output PDF filename (default: output.pdf)
  title_page    : LaTeX file for title page, 'none' to skip (default: none)
  template      : Pandoc template file, 'none' to skip (default: none)
  footer_text   : Footer text, 'none' to disable (default: 'Agents-eval vX.X.X')

Examples:
  $0 help                               # Show this help
  $0                                    # Use all defaults
  $0 "*.md" report.pdf                  # Custom input/output
  $0 "*.md" report.pdf title.latex      # With title page
  $0 "*.md" report.pdf none none 'My Footer'  # Custom footer
  $0 "*.md" report.pdf none none none   # No footer
EOF
    exit 0
fi

# Get script directory for finding pyproject.toml
SCRIPT_DIR="$(dirname "$0")"

# Get version from pyproject.toml
VERSION=$(grep '^version = ' "$SCRIPT_DIR/../pyproject.toml" | sed 's/version = "\(.*\)"/\1/')

# Default values
DEFAULT_INPUT="!(01_*)*.md"
DEFAULT_OUTPUT="output.pdf"
DEFAULT_FOOTER="Agents-eval v${VERSION}"

# Parse arguments
input_file="${1:-$DEFAULT_INPUT}"
output_file="${2:-$DEFAULT_OUTPUT}"
title_file="${3:-}"
template_file="${4:-}"
footer_text="${5:-$DEFAULT_FOOTER}"

# Base pandoc parameters
pandoc_params=(
    "--toc"
    "--toc-depth=2"
    "-V" "geometry:margin=1in"
    "-V" "documentclass=report"
    "--pdf-engine=pdflatex"
    "-M" "protrusion"
    "--from" "markdown+smart"
)

# Configure footer parameters
footer_params=()
if [ -n "$footer_text" ] && [ "$footer_text" != "none" ]; then
    # Create LaTeX header for footer on all pages except title page
    footer_latex=$(cat << 'LATEX'
\usepackage{fancyhdr}

% Define fancy page style for regular pages
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[L]{FOOTER_TEXT_PLACEHOLDER}
\fancyfoot[R]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.4pt}

% Define plain style (used by first page of chapters)
\fancypagestyle{plain}{
    \fancyhf{}
    \fancyfoot[L]{FOOTER_TEXT_PLACEHOLDER}
    \fancyfoot[R]{\thepage}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0.4pt}
}

% Special style for title page only (no footer)
\fancypagestyle{empty}{
    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
}

% Apply empty style to title page if it exists
\AtBeginDocument{
    \ifx\maketitle\undefined\else
        \let\oldmaketitle\maketitle
        \renewcommand{\maketitle}{
            \oldmaketitle
            \thispagestyle{empty}
        }
    \fi
}
LATEX
)
    # Replace placeholder with actual footer text
    footer_latex="${footer_latex//FOOTER_TEXT_PLACEHOLDER/$footer_text}"
    
    # Add footer parameters using process substitution
    footer_params+=("-H" "<(echo '$footer_latex')")
fi

# We'll check and adjust title/template paths after determining work_dir
title_params=()
template_params=()

# Determine working directory and file patterns
# Check if we have multiple files or a single path with directory
work_dir=""
file_pattern="$input_file"

# Check if input contains directory path
if [[ "$input_file" == */* ]]; then
    # Extract common directory if all files share the same path
    first_dir=""
    all_same_dir=true
    
    # Check if it's a single pattern or multiple files
    for file in $input_file; do
        if [[ "$file" == */* ]]; then
            dir="$(dirname "$file")"
            if [ -z "$first_dir" ]; then
                first_dir="$dir"
            elif [ "$dir" != "$first_dir" ]; then
                all_same_dir=false
                break
            fi
        else
            all_same_dir=false
            break
        fi
    done
    
    # If all files are in the same directory, change to it
    if [ "$all_same_dir" = true ] && [ -n "$first_dir" ]; then
        work_dir="$first_dir"
        # Extract just the filenames
        file_pattern=""
        for file in $input_file; do
            file_pattern="$file_pattern $(basename "$file")"
        done
        file_pattern="${file_pattern# }"  # Remove leading space
    fi
fi

# Change directory if needed
if [ -n "$work_dir" ]; then
    pushd "$work_dir" > /dev/null
    
    # Handle output path relative to the new working directory
    if [[ "$output_file" == /* ]]; then
        # Absolute path - use as is
        output_path="$output_file"
    elif [[ "$output_file" == */* ]]; then
        # Relative path with directory - need to go back to original directory
        original_dir="$(dirs +1)"
        output_path="$original_dir/$output_file"
    else
        # Just filename - use in current directory
        output_path="$output_file"
    fi
    
    output_file="$output_path"
    
    # Configure title page parameters - check in current directory first
    if [ -n "$title_file" ] && [ "$title_file" != "none" ]; then
        # Check if title file exists in current directory
        if [ -f "$(basename "$title_file")" ]; then
            title_params+=("-B" "$(basename "$title_file")")
        elif [ -f "$title_file" ]; then
            # Try with original path
            title_params+=("-B" "$title_file")
        elif [ -f "$original_dir/$title_file" ]; then
            # Try relative to original directory
            title_params+=("-B" "$original_dir/$title_file")
        else
            echo "Warning: Title file '$title_file' not found, skipping..."
        fi
    fi
    
    # Configure template parameters - check in current directory first
    if [ -n "$template_file" ] && [ "$template_file" != "none" ]; then
        # Check if template file exists in current directory
        if [ -f "$(basename "$template_file")" ]; then
            template_params+=("--template=$(basename "$template_file")")
            echo "Converting '$file_pattern' to '$output_file' using template '$(basename "$template_file")' ..."
        elif [ -f "$template_file" ]; then
            # Try with original path
            template_params+=("--template=$template_file")
            echo "Converting '$file_pattern' to '$output_file' using template '$template_file' ..."
        elif [ -f "$original_dir/$template_file" ]; then
            # Try relative to original directory
            template_params+=("--template=$original_dir/$template_file")
            echo "Converting '$file_pattern' to '$output_file' using template '$template_file' ..."
        else
            echo "Warning: Template file '$template_file' not found, using defaults..."
            echo "Converting '$file_pattern' to '$output_file' using pandoc defaults ..."
        fi
    else
        echo "Converting '$file_pattern' to '$output_file' using pandoc defaults ..."
    fi
else
    # Not changing directory, use original title/template logic
    if [ -n "$title_file" ] && [ "$title_file" != "none" ]; then
        if [ -f "$title_file" ]; then
            title_params+=("-B" "$title_file")
        else
            echo "Warning: Title file '$title_file' not found, skipping..."
        fi
    fi
    
    if [ -n "$template_file" ] && [ "$template_file" != "none" ]; then
        if [ -f "$template_file" ]; then
            template_params+=("--template=$template_file")
            echo "Converting '$file_pattern' to '$output_file' using template '$template_file' ..."
        else
            echo "Warning: Template file '$template_file' not found, using defaults..."
            echo "Converting '$file_pattern' to '$output_file' using pandoc defaults ..."
        fi
    else
        echo "Converting '$file_pattern' to '$output_file' using pandoc defaults ..."
    fi
fi

# Enable extended globbing if needed
if [[ "$file_pattern" == *"!("* ]]; then
    shopt -s extglob
fi

# Build and run command
if [ ${#footer_params[@]} -gt 0 ]; then
    # Use eval to properly handle process substitution in footer_params
    eval "pandoc ${pandoc_params[*]} ${footer_params[*]} ${template_params[*]} ${title_params[*]} -o \"$output_file\" $file_pattern"
    result=$?
else
    # No footer, simple execution
    eval "pandoc ${pandoc_params[*]} ${template_params[*]} ${title_params[*]} -o \"$output_file\" $file_pattern"
    result=$?
fi

# Return to original directory if we changed
if [ -n "$work_dir" ]; then
    popd > /dev/null
fi

# Check exit status
if [ $result -eq 0 ]; then
    echo "PDF generated successfully: $output_file"
else
    echo "Error: PDF generation failed"
    exit 1
fi