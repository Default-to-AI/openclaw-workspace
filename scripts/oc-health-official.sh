#!/bin/bash

# Configuration
DEBUG=0
if [[ "$1" == "-d" || "$1" == "--debug" ]]; then
    DEBUG=1
fi

# Formatting and Colors
C_GRN='\033[1;32m'
C_RED='\033[1;31m'
C_CYN='\033[1;36m'
C_YLW='\033[1;33m'
C_RST='\033[0m'
C_GRA='\033[0;90m'

# Logging functions
log_info() {
    echo -e "${C_CYN}[INFO]${C_RST} $1"
}

log_error() {
    echo -e "${C_RED}[ERROR]${C_RST} $1"
}

log_debug() {
    if [[ $DEBUG -eq 1 ]]; then
        echo -e "  ${C_GRA}[DEBUG] $1${C_RST}"
    fi
}

echo -e "\n🦞 ${C_CYN}OpenClaw Deep Health Check${C_RST}"
echo -e "${C_GRA}─────────────────────────────────────────────────${C_RST}"
[[ $DEBUG -eq 1 ]] && echo -e "${C_YLW}Debug Mode Enabled${C_RST}\n"

# 1. API Gateway Check
log_info "Checking API / Gateway Health"
log_debug "The API checked here is the underlying OpenClaw RPC Gateway."
log_debug "Executing command: \`openclaw health\`"

if openclaw health >/dev/null 2>&1; then
    echo -e "  ↳ ✅ Gateway: ${C_GRN}ONLINE and WORKING${C_RST}"
else
    log_error "Gateway check failed. The OpenClaw API is completely unreachable or timing out."
    echo -e "  ↳ ❌ Gateway: ${C_RED}UNREACHABLE OR ERROR${C_RST}"
fi

echo ""

# 2. OpenClaw Model Check
log_info "Checking Currently Running Model"
log_debug "Executing command: \`openclaw models status --plain\`"
log_debug "This resolves the primary model dynamically based on OpenClaw CLI output."

MODEL=$(openclaw models status --plain 2>/dev/null)
EXIT_CODE=$?

if [[ -n "$MODEL" && $EXIT_CODE -eq 0 ]]; then
    echo -e "  ↳ 🤖 Active Model: ${C_CYN}$MODEL${C_RST}"
else
    log_error "Model lookup failed or resolved to nothing."
    echo -e "  ↳ 🤖 Active Model: ${C_RED}UNKNOWN OR OFFLINE${C_RST}"
fi

echo ""

# 3. Dashboard Web UI Check
log_info "Checking Dashboard (Web UI) Reachability"
log_debug "Executing command finding port: \`openclaw config get gateway.port\`"

PORT=$(openclaw config get gateway.port 2>/dev/null)
PORT=${PORT:-18789}

log_debug "The Dashboard Web UI is expected locally at port ${PORT}."
log_debug "Executing command: \`curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:$PORT/\`"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/)
if [[ "$HTTP_CODE" -eq 200 ]]; then
    echo -e "  ↳ 🌐 Dashboard: ${C_GRN}ONLINE${C_RST} (http://127.0.0.1:$PORT/)"
elif [[ "$HTTP_CODE" -eq 000 ]]; then
    log_error "cURL returned 000, meaning the HTTP request failed to connect to 127.0.0.1:${PORT}."
    echo -e "  ↳ 🌐 Dashboard: ${C_RED}OFFLINE${C_RST} (Cannot Reach Server)"
else
    log_error "Received non-200 HTTP Status Code response."
    echo -e "  ↳ 🌐 Dashboard: ${C_RED}OFFLINE${C_RST} (HTTP Status: $HTTP_CODE)"
fi

echo -e "\n${C_GRA}─────────────────────────────────────────────────${C_RST}\n"
