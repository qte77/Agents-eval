#!/bin/bash
#
# Common utilities for Ralph scripts
# Source this file: source "$SCRIPT_DIR/lib/common.sh"
#

# Colors: [INFO]=blue, [WARN]=yellow, [ERROR]=red,
# [SUCCESS]=green, [CC]=magenta, [CC error]=red
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Utilities
_ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
fmt_elapsed() { echo "$((${1} / 60))m$((${1} % 60))s"; }

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $(_ts) $1" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(_ts) $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $(_ts) $1" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $(_ts) $1" >&2; }
log_cc() { echo -e "${BLUE}[INFO]${NC} $(_ts) ${MAGENTA}[CC]${NC} $1" >&2; }
log_cc_error() { echo -e "${RED}[ERROR]${NC} $(_ts) ${RED}[CC]${NC} $1" >&2; }

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