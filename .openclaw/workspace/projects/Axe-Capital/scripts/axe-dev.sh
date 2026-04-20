#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
#  Axe-Capital  ·  Dev Environment Launcher
#  Starts the API (uvicorn) and Dashboard (vite) with port safety checks.
#  Usage:  axe-dev          (or bash axe-dev.sh)
#  Stop:   Ctrl+C           (graceful shutdown of both services)
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Paths ─────────────────────────────────────────────────────────────
AXE_ROOT="$HOME/.openclaw/workspace/projects/Axe-Capital"
STEP7="$AXE_ROOT/step7-automation"
STEP6="$AXE_ROOT/step6-dashboard"
VENV="$AXE_ROOT/.venv"

# ── Ports (must match vite.config.js proxy target) ────────────────────
API_PORT=8000
DASH_PORT=5173

# ── Colors (ANSI-C quoting so escape bytes are real, not literal) ─────
RED=$'\e[0;31m'
GREEN=$'\e[0;32m'
YELLOW=$'\e[0;33m'
CYAN=$'\e[0;36m'
BLUE=$'\e[0;34m'
MAGENTA=$'\e[0;35m'
WHITE=$'\e[1;37m'
BOLD=$'\e[1m'
DIM=$'\e[2m'
ULINE=$'\e[4m'
RESET=$'\e[0m'

# ── Log helpers ───────────────────────────────────────────────────────
# These take a pre-formatted string via printf so callers can inline colors.
info()    { printf "  ${CYAN}ℹ${RESET}  %b\n" "$*"; }
success() { printf "  ${GREEN}✔${RESET}  %b\n" "$*"; }
warn()    { printf "  ${YELLOW}⚠${RESET}  %b\n" "$*"; }
fail()    { printf "  ${RED}✖${RESET}  %b\n" "$*"; }
step()    { printf "\n${BOLD}${MAGENTA} ── %b ${RESET}${DIM}─────────────────────────────────────────${RESET}\n" "$*"; }
header()  { printf "\n${BOLD}${BLUE}  📈  %b${RESET}\n" "$*"; }

# ── PIDs to track for cleanup ─────────────────────────────────────────
API_PID=""
DASH_PID=""

cleanup() {
    trap - EXIT SIGINT SIGTERM
    echo ""
    step "Shutting down"
    if [[ -n "$API_PID" ]] && kill -0 "$API_PID" 2>/dev/null; then
        kill "$API_PID" 2>/dev/null && wait "$API_PID" 2>/dev/null || true
        success "${WHITE}API server${RESET}  ${GREEN}stopped${RESET}  ${DIM}pid ${API_PID}${RESET}"
    fi
    if [[ -n "$DASH_PID" ]] && kill -0 "$DASH_PID" 2>/dev/null; then
        kill "$DASH_PID" 2>/dev/null && wait "$DASH_PID" 2>/dev/null || true
        success "${WHITE}Dashboard${RESET}   ${GREEN}stopped${RESET}  ${DIM}pid ${DASH_PID}${RESET}"
    fi
    # Return ports to the systemd services
    if systemctl --user is-enabled axe-api.service &>/dev/null; then
        systemctl --user start axe-api.service 2>/dev/null || true
        success "${WHITE}axe-api.service${RESET}  ${GREEN}restarted${RESET}"
    fi
    if systemctl --user is-enabled axe-dashboard.service &>/dev/null; then
        systemctl --user start axe-dashboard.service 2>/dev/null || true
        success "${WHITE}axe-dashboard.service${RESET}  ${GREEN}restarted${RESET}"
    fi
    success "${GREEN}Clean exit.${RESET} See you, boss."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ══════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════
header "AXE-CAPITAL  ·  Dev Environment Launcher"

# ══════════════════════════════════════════════════════════════════════
#  1. PREFLIGHT CHECKS
# ══════════════════════════════════════════════════════════════════════
step "Preflight checks"

# ── Release ports from systemd services if running ───────────────────
if systemctl --user is-active axe-api.service &>/dev/null; then
    warn "${WHITE}axe-api.service${RESET}  ${YELLOW}is running — stopping it to free port ${API_PORT}${RESET}"
    systemctl --user stop axe-api.service 2>/dev/null || true
    success "${WHITE}axe-api.service${RESET}  ${GREEN}stopped${RESET}  ${DIM}port ${API_PORT} is now free${RESET}"
else
    success "${WHITE}axe-api.service${RESET}  ${GREEN}not running${RESET}  ${DIM}port ${API_PORT} is free${RESET}"
fi
if systemctl --user is-active axe-dashboard.service &>/dev/null; then
    warn "${WHITE}axe-dashboard.service${RESET}  ${YELLOW}is running — stopping it to free port ${DASH_PORT}${RESET}"
    systemctl --user stop axe-dashboard.service 2>/dev/null || true
    success "${WHITE}axe-dashboard.service${RESET}  ${GREEN}stopped${RESET}  ${DIM}port ${DASH_PORT} is now free${RESET}"
else
    success "${WHITE}axe-dashboard.service${RESET}  ${GREEN}not running${RESET}  ${DIM}port ${DASH_PORT} is free${RESET}"
fi

# ── Python venv ───────────────────────────────────────────────────────
if [[ -f "$VENV/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    success "${WHITE}Python venv${RESET}  ${GREEN}activated${RESET}  ${DIM}${VENV}${RESET}"
else
    fail "${WHITE}Python venv${RESET}  ${RED}not found${RESET}  ${DIM}${VENV}${RESET}"
    info "Create it with:  ${WHITE}python3 -m venv ${VENV}${RESET}"
    exit 1
fi

# ── Uvicorn ───────────────────────────────────────────────────────────
if command -v uvicorn &>/dev/null; then
    success "${WHITE}uvicorn${RESET}      ${GREEN}found${RESET}      ${DIM}$(command -v uvicorn)${RESET}"
else
    fail "${WHITE}uvicorn${RESET}      ${RED}not found${RESET}  ${DIM}not in PATH even after venv activation${RESET}"
    info "Install it:  ${WHITE}pip install uvicorn[standard]${RESET}"
    exit 1
fi

# ── npm ───────────────────────────────────────────────────────────────
if command -v npm &>/dev/null; then
    success "${WHITE}npm${RESET}          ${GREEN}found${RESET}      ${DIM}v$(npm --version)${RESET}"
else
    fail "${WHITE}npm${RESET}          ${RED}not found${RESET}  ${DIM}not in PATH${RESET}"
    exit 1
fi

# ── Project directories ──────────────────────────────────────────────
if [[ -d "$STEP7" ]]; then
    success "${WHITE}API dir${RESET}      ${GREEN}exists${RESET}     ${DIM}${STEP7}${RESET}"
else
    fail "${WHITE}API dir${RESET}      ${RED}missing${RESET}    ${DIM}${STEP7}${RESET}"
    exit 1
fi

if [[ -d "$STEP6" ]]; then
    success "${WHITE}Dashboard${RESET}    ${GREEN}exists${RESET}     ${DIM}${STEP6}${RESET}"
else
    fail "${WHITE}Dashboard${RESET}    ${RED}missing${RESET}    ${DIM}${STEP6}${RESET}"
    exit 1
fi

# ══════════════════════════════════════════════════════════════════════
#  2. PORTFOLIO DATA SOURCE
# ══════════════════════════════════════════════════════════════════════
step "Portfolio data source"

ENV_FILE="$AXE_ROOT/.env"

# ── IBKR TWS reachability ─────────────────────────────────────────────
AXE_IBKR_HOST=""
AXE_IBKR_PORT=""
if [[ -f "$ENV_FILE" ]]; then
    AXE_IBKR_HOST=$(grep -m1 '^AXE_IBKR_HOST=' "$ENV_FILE" | cut -d= -f2 | tr -d ' \r')
    AXE_IBKR_PORT=$(grep -m1 '^AXE_IBKR_PORT=' "$ENV_FILE" | cut -d= -f2 | tr -d ' \r')
fi

if [[ -n "$AXE_IBKR_HOST" && -n "$AXE_IBKR_PORT" ]]; then
    if timeout 3 bash -c "echo >/dev/tcp/${AXE_IBKR_HOST}/${AXE_IBKR_PORT}" 2>/dev/null; then
        success "${WHITE}IBKR TWS${RESET}      ${GREEN}reachable${RESET}     ${DIM}${AXE_IBKR_HOST}:${AXE_IBKR_PORT}${RESET}"
    else
        warn "${WHITE}IBKR TWS${RESET}      ${YELLOW}unreachable${RESET}   ${DIM}${AXE_IBKR_HOST}:${AXE_IBKR_PORT} — will try Flex Query fallback${RESET}"
    fi
else
    warn "${WHITE}IBKR TWS${RESET}      ${YELLOW}not configured${RESET} ${DIM}AXE_IBKR_HOST / AXE_IBKR_PORT missing in .env${RESET}"
fi

# ── Flex Query config ─────────────────────────────────────────────────
FLEX_TOKEN=""
FLEX_QUERY_ID=""
if [[ -f "$ENV_FILE" ]]; then
    FLEX_TOKEN=$(grep -m1 '^AXE_IBKR_FLEX_TOKEN=' "$ENV_FILE" | cut -d= -f2 | tr -d ' \r')
    FLEX_QUERY_ID=$(grep -m1 '^AXE_IBKR_FLEX_QUERY_ID=' "$ENV_FILE" | cut -d= -f2 | tr -d ' \r')
fi

if [[ -n "$FLEX_TOKEN" && -n "$FLEX_QUERY_ID" ]]; then
    success "${WHITE}Flex Query${RESET}    ${GREEN}configured${RESET}    ${DIM}query_id=${FLEX_QUERY_ID}${RESET}"
else
    warn "${WHITE}Flex Query${RESET}    ${YELLOW}not configured${RESET} ${DIM}AXE_IBKR_FLEX_TOKEN or AXE_IBKR_FLEX_QUERY_ID missing${RESET}"
fi

# ── Current portfolio snapshot ────────────────────────────────────────
PORTFOLIO_JSON="$AXE_ROOT/step6-dashboard/public/portfolio.json"
if [[ -f "$PORTFOLIO_JSON" ]]; then
    _pfx() { python3 -c "import json,sys; d=json.load(open('$PORTFOLIO_JSON')); print(d.get('$1','?'))"; }
    DATA_SOURCE=$(_pfx data_source)
    REVIEW_DATE=$(_pfx review_date)
    GENERATED_AT=$(_pfx generated_at)
    POS_COUNT=$(python3 -c "import json; d=json.load(open('$PORTFOLIO_JSON')); print(len(d.get('positions', d.get('position_table', []))))")
    CASH=$(python3 -c "import json; d=json.load(open('$PORTFOLIO_JSON')); print(d.get('summary',{}).get('cash','?'))")

    case "$DATA_SOURCE" in
        ibkr)
            success "${WHITE}Last snapshot${RESET}  ${GREEN}IBKR live${RESET}           ${DIM}${POS_COUNT} positions · \$${CASH} cash · ${REVIEW_DATE}${RESET}" ;;
        flex)
            success "${WHITE}Last snapshot${RESET}  ${CYAN}Flex Query (T+1)${RESET}    ${DIM}${POS_COUNT} positions · \$${CASH} cash · ${REVIEW_DATE}${RESET}" ;;
        normalized|raw)
            warn "${WHITE}Last snapshot${RESET}  ${YELLOW}stale CSV fallback${RESET}  ${DIM}${POS_COUNT} positions · \$${CASH} cash · ${REVIEW_DATE}${RESET}" ;;
        *)
            info "${WHITE}Last snapshot${RESET}  ${DIM}source=${DATA_SOURCE} · ${POS_COUNT} positions · ${REVIEW_DATE}${RESET}" ;;
    esac
    info "${DIM}Generated: ${GENERATED_AT}${RESET}"
else
    warn "${WHITE}Last snapshot${RESET}  ${YELLOW}no portfolio.json found${RESET}  ${DIM}run: axe-portfolio-review${RESET}"
fi

# ══════════════════════════════════════════════════════════════════════
#  3. PORT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════
step "Port management"

free_port() {
    local port=$1
    local label=$2
    local pids

    # Grab PIDs listening on this port (skip header line from ss)
    pids=$(ss -tlnp "sport = :$port" 2>/dev/null \
        | tail -n +2 \
        | grep -oP 'pid=\K[0-9]+' \
        | sort -u || true)

    if [[ -z "$pids" ]]; then
        success "Port ${YELLOW}${port}${RESET}  ${GREEN}is free${RESET}          ${DIM}${label}${RESET}"
        return 0
    fi

    warn "Port ${YELLOW}${port}${RESET}  ${RED}in use${RESET}           ${DIM}${label}${RESET}"
    for pid in $pids; do
        local cmd
        cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        info "  └─ ${YELLOW}killing${RESET} pid ${WHITE}${pid}${RESET}  ${DIM}(${cmd})${RESET}"
        kill "$pid" 2>/dev/null || true
    done

    # Give processes a moment to die, then verify
    sleep 1
    local remaining
    remaining=$(ss -tlnp "sport = :$port" 2>/dev/null \
        | tail -n +2 \
        | grep -oP 'pid=\K[0-9]+' \
        | sort -u || true)

    if [[ -n "$remaining" ]]; then
        warn "${YELLOW}Graceful kill${RESET} didn't work, sending ${RED}SIGKILL${RESET}…"
        for pid in $remaining; do
            kill -9 "$pid" 2>/dev/null || true
        done
        sleep 0.5
    fi

    # Final check
    local final
    final=$(ss -tlnp "sport = :$port" 2>/dev/null \
        | tail -n +2 \
        | grep -oP 'pid=\K[0-9]+' \
        | sort -u || true)

    if [[ -z "$final" ]]; then
        success "Port ${YELLOW}${port}${RESET}  ${GREEN}freed${RESET}            ${DIM}${label}${RESET}"
    else
        fail "Port ${YELLOW}${port}${RESET}  ${RED}could not free${RESET}   ${DIM}something is stubbornly holding it${RESET}"
        info "Try manually:  ${WHITE}sudo fuser -k ${port}/tcp${RESET}"
        exit 1
    fi
}

free_port "$API_PORT"  "API / uvicorn"
free_port "$DASH_PORT" "Dashboard / vite"

# ══════════════════════════════════════════════════════════════════════
#  3. LAUNCH SERVICES
# ══════════════════════════════════════════════════════════════════════
step "Starting services"

# ── API  (uvicorn) ────────────────────────────────────────────────────
info "${WHITE}API server${RESET}   ${CYAN}starting${RESET}   ${DIM}port ${API_PORT}${RESET}"
(
    cd "$STEP7"
    uvicorn axe_orchestrator.api:app \
        --reload \
        --host 127.0.0.1 \
        --port "$API_PORT" \
        2>&1 | sed "s/^/  ${DIM}[API]${RESET}  /"
) &
API_PID=$!
info "${WHITE}API server${RESET}   ${CYAN}launched${RESET}   ${DIM}pid ${API_PID}${RESET}"

# Brief pause to let uvicorn bind
sleep 2

# Verify API actually started
if kill -0 "$API_PID" 2>/dev/null; then
    success "${WHITE}API server${RESET}   ${GREEN}is running${RESET}  ${CYAN}${ULINE}http://127.0.0.1:${API_PORT}${RESET}"
else
    fail "${WHITE}API server${RESET}   ${RED}exited unexpectedly${RESET}"
    info "Check the output above for errors"
    exit 1
fi

# ── Dashboard  (vite) ────────────────────────────────────────────────
info "${WHITE}Dashboard${RESET}    ${CYAN}starting${RESET}   ${DIM}port ${DASH_PORT}${RESET}"
(
    cd "$STEP6"
    npx vite --host 0.0.0.0 --port "$DASH_PORT" \
        2>&1 | sed "s/^/  ${DIM}[UI]${RESET}   /"
) &
DASH_PID=$!
info "${WHITE}Dashboard${RESET}    ${CYAN}launched${RESET}   ${DIM}pid ${DASH_PID}${RESET}"

sleep 2

if kill -0 "$DASH_PID" 2>/dev/null; then
    success "${WHITE}Dashboard${RESET}    ${GREEN}is running${RESET}  ${CYAN}${ULINE}http://localhost:${DASH_PORT}${RESET}"
else
    fail "${WHITE}Dashboard${RESET}    ${RED}exited unexpectedly${RESET}"
    info "Check the output above for errors"
    exit 1
fi

# ══════════════════════════════════════════════════════════════════════
#  4. READY
# ══════════════════════════════════════════════════════════════════════
step "All systems go"
echo ""
printf "  ${WHITE}API${RESET}        ${CYAN}${ULINE}http://127.0.0.1:${API_PORT}${RESET}      ${DIM}uvicorn · auto-reload${RESET}\n"
printf "  ${WHITE}Dashboard${RESET}  ${CYAN}${ULINE}http://localhost:${DASH_PORT}${RESET}      ${DIM}vite · HMR${RESET}\n"
printf "  ${WHITE}Proxy${RESET}      ${DIM}/api/*${RESET} → ${DIM}localhost:${API_PORT}${RESET}       ${DIM}vite proxy${RESET}\n"
echo ""
printf "  ${DIM}Press ${WHITE}Ctrl+C${RESET}${DIM} to stop both services.${RESET}\n"
echo ""

# ── Keep script alive, forwarding output until interrupted ────────────
wait
