#!/bin/bash
#
# Common utilities for Ralph scripts
# Source this file: source "$SCRIPT_DIR/lib/common.sh"
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" >&2; }

# Check if command exists
require_command() {
    local cmd="$1"
    local install_hint="${2:-}"
    if ! command -v "$cmd" &> /dev/null; then
        log_error "$cmd not found"
        [ -n "$install_hint" ] && log_info "Install: $install_hint"
        return 1
    fi
    return 0
}