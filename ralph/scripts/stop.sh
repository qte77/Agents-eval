#!/bin/bash
# Stops all running Ralph loops (keeps state and data).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/stop_ralph_processes.sh"

stop_ralph_processes
