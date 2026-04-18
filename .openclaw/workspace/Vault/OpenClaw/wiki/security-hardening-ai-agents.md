---
title: Security Hardening for AI Agents
type: concept
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/secure-openclaw-wsl-windows]]"
  - "[[OpenClaw/raw/openclaw-first-15-messages-localized]]"
  - "[[Claude Can Now TRADE For You On TradingView (Insane)]]"
  - "[[openclaw-security-hardening-guide]]"
  - "[[openclaw-security-docs]]"
tags:
  - security
  - agents
  - hardening
  - isolation
  - secrets
---

# Security Hardening for AI Agents

Principles and checklists for securing AI agent deployments, generalized from [[openclaw]] runbooks and [[claude-tradingview-trading|trading bot]] security.

## Threat Model

| Threat | Vector | Impact |
|---|---|---|
| Prompt injection | Chat, email, ingested content | Tool execution, data exfiltration |
| Malicious skills / supply chain | Third-party skills, plugins | Arbitrary code execution |
| Exposed gateway | Public port binding, weak auth | Unauthorized agent control |
| Runaway costs | Loops, excessive API calls | Financial drain |
| Secret leakage | Env vars in logs, git, chat | API key compromise |
| Overprivileged agents | Too many tools/permissions | Blast radius on compromise |

## Defense Layers

### 1. Network Isolation
- Bind gateway/UI to `127.0.0.1` only (never `0.0.0.0`)
- No public port forwards
- Tailscale/tailnet-only remote access with ACLs
- SSH local port-forwarding for UI access

### 2. Container Hardening (Docker/WSL)
- Rootless Docker or non-root container user
- `--cap-drop=ALL` (drop all Linux capabilities)
- Read-only root filesystem; only workspace as writable mount
- Default seccomp + AppArmor profiles
- No privileged containers
- Do NOT mount host filesystem (`/mnt/c`) into container

### 3. Authentication & Authorization
- Gateway token required for all connections
- Tool execution on ask/allowlist (not blanket approve)
- Telegram/chat allowlist (your user ID only)
- Require mentions in group chats (prevent ambient triggering)

### 4. Secrets Management
- All secrets in `.env` file with `chmod 600`
- Parent directory `chmod 700`
- Never paste secrets into chat
- Never commit `.env` (enforce via `.gitignore`)
- Rotate keys after any suspicion of compromise
- API keys use minimum required permissions (read-only where possible)

### 5. Operational Guardrails
- No destructive commands without explicit YES confirmation
- Stop after 3 failed attempts
- Command logging / audit trail
- Budget limits and spending caps
- Maximum trades per day / maximum position size (for trading agents)
- Paper trading mode as default; live mode requires explicit switch

### 6. Agent-Level Controls
- Each agent gets minimum necessary tools
- Separate output folders per agent
- Approval gates for high-impact actions
- Progressive trust: start restricted, expand as system proves reliable

## Minimum Secure Baseline

Before running any agent in production:
1. Localhost-only binding
2. Gateway token
3. Tool execution approval gates
4. `.env` with strict permissions + spending caps
5. Tailnet-only remote access (if remote)
6. Audit logging enabled

## See also

- [[openclaw-setup-and-efficiency]]
- [[openclaw]]
- [[agent-orchestration]]
- [[openclaw-guides-summary]]
- [[claude-tradingview-trading]]
- [[openclaw-security-hardening-guide]]
- [[openclaw-security-docs]]
