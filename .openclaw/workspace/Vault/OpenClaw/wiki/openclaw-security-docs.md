---
title: OpenClaw Security Documentation
type: source-summary
domain: openclaw
created: 15-04-2026
updated: 15-04-2026
sources:
  - "[[OpenClaw/raw/15-04-2026-openclaw-security-docs]]"
tags:
  - security
  - openclaw
  - official-docs
---

# OpenClaw Security Documentation

The official security documentation from the OpenClaw team, functioning as the authoritative hardening baseline and risk posture for gateway deployments.

## Core Defensive Concepts

- **Personal Assistant Boundary:** OpenClaw defaults to a personal operator trust model in which the user has total authority over the host, gateway, and nodes. It does not provide hostile multi-tenant boundaries out-of-the-box for random internet participants. Mixed trust environments require separated deployment instances.
- **Audit Tooling:** Run `openclaw security audit` (with `--deep` and `--fix` flags) for self-service hardening validation.
- **Sandboxing vs Tools:** Control-plane and OS tools (browser, filesystem access, remote code exec) are extremely powerful. For public-facing environments or agents that consume untrusted web content, enable docker sandboxing and strict `/exec` allowlists.
- **Network Boundaries:** Reverse proxies should drop non-trusted IP forwardings. Use Tailscale Serve or local loopbacks instead of port-forwarding across the public internet.

## See also

- [[openclaw-team]]
- [[security-hardening-ai-agents]]
- [[openclaw]]
