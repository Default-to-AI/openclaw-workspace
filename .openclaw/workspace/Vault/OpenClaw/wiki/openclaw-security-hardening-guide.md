---
title: OpenClaw Security Hardening Guide
type: source-summary
domain: openclaw
created: 15-04-2026
updated: 15-04-2026
sources:
  - "[[OpenClaw/raw/15-04-2026-openclaw-security-hardening-guide]]"
tags:
  - openclaw
  - security
---

# OpenClaw Security Hardening Guide

A summary of [[alex-followell|Alex Followell]]'s 10-step security walkthrough for [[openclaw]]. Focuses on practical actions without needing terminal access, instead using prompts to direct the agent itself.

## Key Hardening Steps

1. **Security Audit:** Use the built-in `security audit` capability to scan for vulnerabilities.
2. **Channel lockdown:** Set a DM policy for channels like Telegram/WhatsApp restricting to an approved senders list.
3. **Session isolation:** Keep different user outputs strictly separate so secrets aren't inadvertently shared.
4. **Tool restriction:** Reduce default tool policies to `message only`, blocking terminal and file system access by default.
5. **Docker Sandboxing:** Ensure Docker is installed and direct OpenClaw to run experimental tools in isolated environments to limit "blast radius".
6. **Port Randomization:** Move away from the predictable default port (18789).
7. **Tailscale/VPN:** Bind gateway only to localhost or Tailnet (private network) rather than exposing to the public internet.
8. **SSH Hardening:** Audit and restrict SSH to key-based auth only.
9. **System Prompt Rules:** Add strict rules against API key revelation and processing untrusted attachments.
10. **Automated audits:** Schedule daily cron jobs to re-run security checks and assure latest versions.

## See also

- [[security-hardening-ai-agents]]
- [[openclaw-setup-and-efficiency]]
