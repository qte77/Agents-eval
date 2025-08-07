#!/bin/bash
# set -e

STYLE="$1"
INPUT_FILE="$2"
OUTPUT_FILE="${3:-${INPUT_FILE%.*}.png}"

CLI_PREFIX='Generate PNG from PlantUML: '
BOLD_RED='\e[1;31m'
NC='\e[0m'

if [ ! -f "$INPUT_FILE" ]; then
    printf "${CLI_PREFIX}${BOLD_RED}Input file '$INPUT_FILE' does not exist. Exiting ... ${NC}\n"
    exit 1
fi

# Determine the path where PlantUML will generate the file.
GENERATED_FILE_ON_HOST="$(dirname "$INPUT_FILE")/$(basename "${INPUT_FILE%.*}").png"

# Run the Docker command, redirecting PlantUML's verbose output to /dev/null.
docker run --rm -v "$(pwd)":/data plantuml/plantuml:latest \
    -DSTYLE="$STYLE" -o "/data/$(dirname "$INPUT_FILE")" "/data/$INPUT_FILE" >/dev/null

# If the desired output path is different from where the file was generated, move it.
if [ "$OUTPUT_FILE" != "$GENERATED_FILE_ON_HOST" ]; then
    in=$(basename $GENERATED_FILE_ON_HOST)
    out=$(dirname $OUTPUT_FILE)
    printf "${CLI_PREFIX}${BOLD_RED}Moving ${in} to ${out} ...${NC}\n"
    mkdir -p "${out}"
    mv "$GENERATED_FILE_ON_HOST" "$OUTPUT_FILE"
fi
