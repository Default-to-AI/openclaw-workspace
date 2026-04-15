#!/bin/bash

# --- Colors for formatting ---
RESET='\033[0m'
GREEN='\033[1;32m'
RED='\033[1;31m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'

echo -e "${BLUE}=================================================${RESET}"
echo -e "${CYAN}      OpenClaw Ultimate Health Check 🚀          ${RESET}"
echo -e "${BLUE}=================================================${RESET}\n"

# ---------------------------------------------------------
# 1. API / Gateway Health
# ---------------------------------------------------------
echo -e "${YELLOW}1. Gateway API Status:${RESET}"
if openclaw health >/dev/null 2>&1; then
    echo -e "${GREEN}[OK] Gateway is ONLINE and actively listening.${RESET}"
else
    echo -e "${RED}[ERROR] Gateway is DOWN or unreachable. (Try: openclaw gateway restart)${RESET}"
fi
echo ""

# ---------------------------------------------------------
# 2. Dashboard (Web UI) Reachability
# ---------------------------------------------------------
echo -e "${YELLOW}2. Dashboard (Web UI):${RESET}"
# Fetch port from config, fallback to 18789
PORT=$(openclaw config get gateway.port 2>/dev/null || echo "18789")
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}[OK] Dashboard is accessible at http://127.0.0.1:$PORT/${RESET}"
else
    echo -e "${RED}[ERROR] Dashboard is offline. (HTTP Status: $HTTP_CODE)${RESET}"
fi
echo ""

# ---------------------------------------------------------
# 3. Tailscale Status
# ---------------------------------------------------------
echo -e "${YELLOW}3. Tailscale / Remote Access:${RESET}"
TS_MODE=$(openclaw config get gateway.tailscale.mode 2>/dev/null || echo "off")

if [[ "$TS_MODE" == "serve" || "$TS_MODE" == "funnel" ]]; then
    echo -e "${CYAN}[INFO] OpenClaw Tailscale mode is set to: $TS_MODE${RESET}"
    if command -v tailscale >/dev/null 2>&1 && tailscale status >/dev/null 2>&1; then
        echo -e "${GREEN}[OK] Tailscale service is running on the host system.${RESET}"
    else
        echo -e "${RED}[ERROR] Tailscale is NOT running or not installed on the host!${RESET}"
    fi
else
    echo -e "${YELLOW}[WARN] Tailscale is disabled in OpenClaw config (mode: $TS_MODE).${RESET}"
fi
echo ""

# ---------------------------------------------------------
# 4. Models & Auth Status
# ---------------------------------------------------------
echo -e "${YELLOW}4. Models & API Authentication:${RESET}"
if openclaw models status --check >/dev/null 2>&1; then
    echo -e "${GREEN}[OK] All API keys and OAuth tokens are valid.${RESET}"
else
    echo -e "${RED}[ERROR] Auth issues detected! Some keys/tokens are missing or expired.${RESET}"
fi

MAIN_MODEL=$(openclaw models status --plain 2>/dev/null || echo "Unknown")
echo -e "${CYAN}[INFO] Current Primary Model:${RESET} $MAIN_MODEL"
echo ""

# ---------------------------------------------------------
# 5. Channels (Telegram) Live Probe
# ---------------------------------------------------------
echo -e "${YELLOW}5. Channels (Live Probe):${RESET}"
CHANNEL_STATUS=$(openclaw channels status --probe 2>&1)

if echo "$CHANNEL_STATUS" | grep -qi "connected\|ready"; then
    echo -e "${GREEN}[OK] Channels connected successfully:${RESET}"
    # Filter and display only the relevant channel lines
    echo "$CHANNEL_STATUS" | grep -iE "telegram|whatsapp|discord|slack|connected|ready|Error"
else
    echo -e "${RED}[ERROR] Channels are NOT connected. Output:${RESET}"
    echo "$CHANNEL_STATUS"
fi
echo ""

echo -e "${BLUE}=================================================${RESET}"
echo -e "For a detailed report, run: ${CYAN}openclaw status --deep${RESET}"
echo -e "${BLUE}=================================================${RESET}"