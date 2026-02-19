#!/bin/bash
# PDF Converter Setup Script
# Installs and configures PDF conversion tools (pandoc or wkhtmltopdf)

# Check for help request first
if [ "$1" = "help" ]; then
    cat << EOF
Usage: $0 [help | converter_type]

Setup PDF converter tools for document conversion.

Arguments:
  help           : Show this help message and exit
  converter_type : Type of converter to install (pandoc or wkhtmltopdf)

Supported converters:
  pandoc      : Install pandoc with LaTeX packages for PDF generation
                Usage: pandoc combined.md -o output.pdf
  
  wkhtmltopdf : Install wkhtmltopdf for HTML to PDF conversion
                Usage: markdown your_document.md | wkhtmltopdf - output.pdf

Examples:
  $0 help         # Show this help
  $0 pandoc       # Install pandoc and LaTeX packages
  $0 wkhtmltopdf  # Install wkhtmltopdf
EOF
    exit 0
fi

# Parse converter choice
CONVERTER_CHOICE="${1:-}"
SUPPORTED_MSG="Use 'pandoc' or 'wkhtmltopdf'."

# Validate converter choice
if [ -z "$CONVERTER_CHOICE" ]; then
    echo "Error: No PDF converter specified. $SUPPORTED_MSG"
    echo "Run '$0 help' for usage information."
    exit 1
fi

echo "Setting up PDF converter '$CONVERTER_CHOICE' ..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update -yqq

# Install based on converter choice
case "$CONVERTER_CHOICE" in
    pandoc)
        echo "Installing pandoc and LaTeX packages..."
        sudo apt-get install -yqq pandoc
        sudo apt-get install -yqq texlive-latex-recommended texlive-fonts-recommended

        # Display version info
        if command -v pandoc &> /dev/null; then
            echo "Successfully installed pandoc:"
            pandoc --version | head -n 1
        else
            echo "Error: pandoc installation may have failed."
            exit 1
        fi
        ;;
        
    wkhtmltopdf)
        echo "Installing wkhtmltopdf..."
        sudo apt-get install -yqq wkhtmltopdf
        
        # Display version info
        if command -v wkhtmltopdf &> /dev/null; then
            echo "Successfully installed wkhtmltopdf:"
            wkhtmltopdf --version | head -n 1
            echo ""
            echo "Usage example:"
            echo "  markdown your_document.md | wkhtmltopdf - output.pdf"
        else
            echo "Error: wkhtmltopdf installation may have failed."
            exit 1
        fi
        ;;
        
    *)
        echo "Error: Unsupported PDF converter choice '$CONVERTER_CHOICE'. $SUPPORTED_MSG"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac

echo "PDF converter setup complete!"