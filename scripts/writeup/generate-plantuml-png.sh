#!/bin/sh
# Renders a PlantUML file to PNG via Docker.
# Usage: generate-plantuml-png.sh <input.puml> [style] [output_dir] [check_only] [container]
set -eu

INPUT_FILE="$1"

CLI_PREFIX='shell: '
BOLD_RED='\033[1;31m'
NC='\033[0m'

if ! command -v docker >/dev/null 2>&1; then
    printf '%b%bDocker is not installed. Exiting ... %b\n' "$CLI_PREFIX" "$BOLD_RED" "$NC"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    printf '%b%bInput file "%s" does not exist. Exiting ... %b\n' "$CLI_PREFIX" "$BOLD_RED" "$INPUT_FILE" "$NC"
    exit 1
fi

STYLE="${2:-light}"
OUTPUT_PATH="${3:-$(dirname "$INPUT_FILE")}"
CHECK_ONLY="${4:-false}"
PLANTUML_CONTAINER="${5:-plantuml/plantuml:latest}"

INPUT_NAME="$(basename "$INPUT_FILE")"
INPUT_PATH=$(dirname "$INPUT_FILE")
OUTPUT_NAME="${INPUT_NAME%.*}.png"
OUTPUT_NAME_FULL="${INPUT_NAME%.*}-${STYLE}.png"

CONTAINER_INPUT="/data"
CONTAINER_OUTPUT="/output"
PLANTUML_SECURITY_PROFILE="ALLOWLIST"

mkdir -p "$OUTPUT_PATH"

run_plantuml() {
    docker run --rm \
        -v "$(pwd)/${INPUT_PATH}:${CONTAINER_INPUT}:ro" \
        -v "$(pwd)/${OUTPUT_PATH}:${CONTAINER_OUTPUT}" \
        -e "PLANTUML_SECURITY_PROFILE=${PLANTUML_SECURITY_PROFILE}" \
        -e "PLANTUML_INCLUDE_PATH=${CONTAINER_INPUT}" \
        "${PLANTUML_CONTAINER}" \
        -DSTYLE="${STYLE}" \
        -o "${CONTAINER_OUTPUT}" \
        "$@"
}

if [ "$CHECK_ONLY" = true ]; then
    run_plantuml -v -checkonly "${CONTAINER_INPUT}/${INPUT_NAME}"
else
    run_plantuml "${CONTAINER_INPUT}/${INPUT_NAME}"
fi

printf '%b%bRenaming %s to %s in %s ...%b\n' "$CLI_PREFIX" "$BOLD_RED" "$OUTPUT_NAME" "$OUTPUT_NAME_FULL" "$OUTPUT_PATH" "$NC"
mv "${OUTPUT_PATH}/${OUTPUT_NAME}" "${OUTPUT_PATH}/${OUTPUT_NAME_FULL}"
