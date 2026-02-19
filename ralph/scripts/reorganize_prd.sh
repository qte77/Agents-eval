#!/bin/bash
# Script to reorganize PRD files for ralph-loop
set -euo pipefail

# Usage info
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <new_prd_file>

Archives current PRD and ralph state, then activates a new PRD.

Arguments:
  new_prd_file    Path to new PRD file (relative to project root)

Options:
  -v VERSION      Archive version (default: auto-detected)
  -h              Show this help message

Examples:
  $0 docs/PRD-Benchmarking.md
  $0 -v 2 docs/PRD-Benchmarking.md

Auto-detection:
  Version is auto-detected by counting existing archives (v1, v2, v3, ...)
EOF
    exit 1
}

# Parse options
VERSION=""
while getopts "v:h" opt; do
    case $opt in
        v) VERSION="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done
shift $((OPTIND-1))

# Validate arguments
if [ $# -ne 1 ]; then
    echo "Error: Missing new PRD file argument"
    usage
fi

NEW_PRD="$1"

# Validate new PRD exists
if [ ! -f "$NEW_PRD" ]; then
    echo "Error: File not found: $NEW_PRD"
    exit 1
fi

# Auto-detect version if not provided
if [ -z "$VERSION" ]; then
    # Count existing PRD archives
    COUNT=$(find docs/archive -maxdepth 1 -name "PRD-v*.md" 2>/dev/null | wc -l)
    VERSION=$((COUNT + 1))
    echo "Auto-detected version: v$VERSION"
fi

ARCHIVE_DIR="docs/archive/ralph-v${VERSION}"
PRD_ARCHIVE="docs/archive/PRD-v${VERSION}.md"

echo "📁 Creating archive directory: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR"

echo "📦 Archiving current PRD: $PRD_ARCHIVE"
if [ -f "docs/PRD.md" ]; then
    mv docs/PRD.md "$PRD_ARCHIVE"
else
    echo "Warning: No current PRD.md to archive"
fi

echo "📦 Archiving ralph state to: $ARCHIVE_DIR"
if [ -f "ralph/docs/prd.json" ]; then
    mv ralph/docs/prd.json "$ARCHIVE_DIR/prd.json"
fi
if [ -f "ralph/docs/progress.txt" ]; then
    mv ralph/docs/progress.txt "$ARCHIVE_DIR/progress.txt"
fi

echo "📝 Activating new PRD: $NEW_PRD -> docs/PRD.md"
cp "$NEW_PRD" docs/PRD.md
rm "$NEW_PRD"

echo "✅ Reorganization complete!"
echo ""
echo "Archived:"
echo "  - PRD: $PRD_ARCHIVE"
echo "  - Ralph state: $ARCHIVE_DIR"
echo ""
echo "Next step: Run 'make ralph_init' to generate new prd.json"