---
title: "Summary: OpenClaw Operational Guides (First 15 Messages + Efficiency Playbook + Security Runbook)"
type: source-summary
domain: openclaw
created: 12-04-2026
updated: 12-04-2026
sources:
  - "[[OpenClaw/raw/openclaw-first-15-messages-localized]]"
  - "[[OpenClaw/raw/openclaw-efficiency-playbook]]"
  - "[[OpenClaw/raw/secure-openclaw-wsl-windows]]"
tags: [openclaw, security, efficiency, setup, wsl]
---

# Summary: OpenClaw Operational Guides

Three internal guides covering [[openclaw]] setup, efficiency, and security hardening on Windows + WSL.

## First 15 Messages (Setup Playbook)

Structured onboarding in 5 phases:

1. **Lock it down (Messages 1-3):** Security audit, bind gateway to loopback, token auth, Telegram allowlist, secrets in `.env` with `chmod 600`, safety guardrails (no destructive commands without explicit YES, stop after 3 failures, budget limits).
2. **Teach it who you are (Messages 4-5):** USER.md (<=1KB) and SOUL.md (<=2KB). Keep short.
3. **Cost controls (Messages 6-8):** Model routing (cheap model for heartbeats, big model for architecture). Rate limits between API/search calls.
4. **Phone/Telegram (Messages 9-11):** Bot token in env, allowlist Telegram ID, require mentions in groups.
5. **Knowledge + files (Messages 12-15):** Vault write policy, templates for Runbooks/Decision Logs/Incident Response.

## Efficiency Playbook (Context + Reliability)

On subscription, optimize for speed and precision, not dollar cost. Six efficiency drivers:

1. Wrong default model (latency/quality impact)
2. Heartbeats doing real work (noise + unpredictable behavior)
3. **Bloated context** (#1 cause of slow responses and hallucinations)
4. No caching / repeated work (drift from re-derivation)
5. Session bloat (long sessions degrade precision)
6. Verbose tool outputs (logs in chat instead of files)

**Context discipline rules (non-negotiable):**
- Index-first navigation (never open 20 notes; start from `_INDEX.md`)
- Pull, don't push (load minimal snippets)
- One objective per session
- Prefer files over chat (long outputs to vault, TL;DR in chat)

**Heartbeats:** Only check urgent messages + 1-2 status conditions. If work found, create a task and stop.

## Security Runbook (WSL + Windows)

Threat model: prompt injection, malicious skills/supply chain, exposed gateway, runaway costs, secret leakage.

Key hardening steps:
- Keep workspace inside WSL filesystem (not on `C:\`)
- Do NOT mount `/mnt/c` into container
- Docker: rootless, `--cap-drop=ALL`, read-only root FS, bind ports to `127.0.0.1`
- Gateway: not on `0.0.0.0`, require token, tool execution on ask/allowlist
- Tailscale: tailnet-only access, SSH, ACLs for device/user restriction
- Secrets: `.env` with `chmod 600`, never paste in chat, never commit, rotate on suspicion

See [[security-hardening-ai-agents]] for the generalized concept.

## See also

- [[openclaw]]
- [[openclaw-setup-and-efficiency]]
- [[security-hardening-ai-agents]]
- [[agent-orchestration]]
