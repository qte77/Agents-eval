#!/bin/bash
#
# Codebase snapshot generation for Ralph Loop
#
# Pre-computes codebase context (file tree + signatures) and story-scoped
# context (AC, files, tests) so agents start implementing immediately
# instead of spending 5-15 tool calls discovering the codebase.
#
# Source order: common.sh → baseline.sh → teams.sh → snapshot.sh
# Requires globals from common.sh: RALPH_DOCS_DIR, RALPH_PRD_JSON

CODEBASE_MAP_FILE="$RALPH_DOCS_DIR/codebase-map.md"
CODEBASE_MAP_SHA="$RALPH_DOCS_DIR/.codebase-map.sha"
STORY_CONTEXT_FILE="$RALPH_DOCS_DIR/story-context.md"
_EXTRACT_SIGS="$(dirname "${BASH_SOURCE[0]}")/extract_signatures.py"
SNAPSHOT_SIG_LIMIT="${SNAPSHOT_SIG_LIMIT:-100}"

# Generate codebase map: src/ file tree + function/class signatures.
# Content-hash src/ to skip regeneration when unchanged.
generate_codebase_map() {
    local start_time
    start_time=$(date +%s)

    # Content-hash all src/ files (not just .py — catches .pyi, .yaml, configs)
    local current_hash
    current_hash=$(find src/ -type f | sort | xargs cat 2>/dev/null | sha256sum | cut -d' ' -f1)

    if [ -f "$CODEBASE_MAP_SHA" ] && [ -f "$CODEBASE_MAP_FILE" ]; then
        local stored_hash
        stored_hash=$(cat "$CODEBASE_MAP_SHA")
        if [ "$current_hash" = "$stored_hash" ]; then
            log_info "Codebase map unchanged — skipping regeneration"
            return 0
        fi
    fi

    log_info "Generating codebase map..."

    {
        echo "## Codebase Map"
        echo ""
        echo "Auto-generated source tree and signatures. Do NOT read these files"
        echo "unless the pre-loaded context below is insufficient."
        echo ""
        echo "### File Tree"
        echo ""
        echo '```'
        find src/ -type f -name '*.py' | sort | sed 's|^|  |'
        echo '```'
        echo ""
        echo "### Signatures"
        echo ""
        # Global overview: all src/ signatures, capped per file
        find src/ -type f -name '*.py' | sort | while IFS= read -r pyfile; do
            local sigs
            sigs=$(python3 "$_EXTRACT_SIGS" "$pyfile" 2>/dev/null | head -"$SNAPSHOT_SIG_LIMIT" || true)
            if [ -n "$sigs" ]; then
                echo "**$pyfile**:"
                echo '```python'
                echo "$sigs" | sed 's/^/  /'
                echo '```'
                echo ""
            fi
        done
    } > "$CODEBASE_MAP_FILE"

    echo "$current_hash" > "$CODEBASE_MAP_SHA"

    local elapsed=$(( $(date +%s) - start_time ))
    local line_count
    line_count=$(wc -l < "$CODEBASE_MAP_FILE")
    log_success "Codebase map generated: $line_count lines in ${elapsed}s"
}

# Generate story-scoped context: AC, tech requirements, file contents, test files.
# Args: $1 - story ID
generate_story_context() {
    local story_id="$1"
    local prd_json="$RALPH_PRD_JSON"

    log_info "Generating story context for $story_id..."

    {
        echo "## Story Context: $story_id"
        echo ""

        # Section 1: Acceptance criteria
        echo "### Acceptance Criteria"
        echo ""
        local ac
        ac=$(jq -r --arg id "$story_id" '
            .stories[] | select(.id == $id) |
            .acceptance_criteria // [] | .[] // "none"
        ' "$prd_json" 2>/dev/null || true)
        if [ -n "$ac" ] && [ "$ac" != "none" ]; then
            echo "$ac" | while IFS= read -r line; do
                echo "- $line"
            done
        else
            echo "(no acceptance criteria found)"
        fi
        echo ""

        # Section 2: Technical requirements
        echo "### Technical Requirements"
        echo ""
        local tech
        tech=$(jq -r --arg id "$story_id" '
            .stories[] | select(.id == $id) |
            .technical_requirements // [] | .[] // "none"
        ' "$prd_json" 2>/dev/null || true)
        if [ -n "$tech" ] && [ "$tech" != "none" ]; then
            echo "$tech" | while IFS= read -r line; do
                echo "- $line"
            done
        else
            echo "(no technical requirements found)"
        fi
        echo ""

        # Section 3: Story files — full content for ≤200 lines, signatures for larger
        echo "### Story Files"
        echo ""
        local files
        files=$(jq -r --arg id "$story_id" '
            .stories[] | select(.id == $id) |
            .files // [] | .[]
        ' "$prd_json" 2>/dev/null || true)

        if [ -n "$files" ]; then
            echo "$files" | while IFS= read -r filepath; do
                if [ ! -f "$filepath" ]; then
                    echo "**$filepath** (new file — does not exist yet)"
                    echo ""
                    continue
                fi
                local lines
                lines=$(wc -l < "$filepath")
                if [ "$lines" -le 200 ]; then
                    echo "**$filepath** ($lines lines):"
                    echo '```'
                    cat "$filepath"
                    echo '```'
                else
                    # Story-scoped source file: full signatures (no cap — agent edits these)
                    echo "**$filepath** ($lines lines, signatures only):"
                    echo '```'
                    python3 "$_EXTRACT_SIGS" "$filepath" 2>/dev/null | sed 's/^/  /' || true
                    echo '```'
                fi
                echo ""
            done
        else
            echo "(no files listed)"
        fi

        # Section 4: Matching test files (same size-gated strategy)
        echo "### Test Files"
        echo ""
        if [ -n "$files" ]; then
            local found_tests=false
            # Reason: here-string (<<<) keeps loop in current shell so found_tests propagates
            while IFS= read -r filepath; do
                local test_path
                test_path=$(echo "$filepath" | sed 's|^src/app/|tests/|; s|/\([^/]*\)\.py$|/test_\1.py|')
                [ -f "$test_path" ] || continue
                found_tests=true
                local tlines
                tlines=$(wc -l < "$test_path")
                if [ "$tlines" -le 200 ]; then
                    echo "**$test_path** ($tlines lines):"
                    echo '```'
                    cat "$test_path"
                    echo '```'
                else
                    # Story-scoped test file: full signatures (no cap — agent edits these)
                    echo "**$test_path** ($tlines lines, signatures only):"
                    echo '```'
                    python3 "$_EXTRACT_SIGS" "$test_path" 2>/dev/null | sed 's/^/  /' || true
                    echo '```'
                fi
                echo ""
            done <<< "$files"
            if [ "$found_tests" = "false" ]; then
                echo "(no matching test files found)"
            fi
        else
            echo "(no files listed)"
        fi
    } > "$STORY_CONTEXT_FILE"

    local ctx_lines
    ctx_lines=$(wc -l < "$STORY_CONTEXT_FILE")
    log_info "Story context generated: $ctx_lines lines"
}
