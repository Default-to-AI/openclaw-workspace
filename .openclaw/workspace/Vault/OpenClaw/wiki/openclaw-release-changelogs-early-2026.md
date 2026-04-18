---
title: OpenClaw Release Changelogs (Early 2026)
type: source-summary
domain: openclaw
created: 15-04-2026
updated: 15-04-2026
sources:
  - "[[OpenClaw/raw/15-04-2026-openclaw-releases-changelog]]"
tags:
  - releases
  - updates
  - openclaw
---

# OpenClaw Release Changelogs (Early 2026)

Summary of OpenClaw release iterations from `v2026.4.8` to `v2026.4.14` spanning early to mid-April 2026.

## Major Changes
- **Memory Plugins:** Introduced the new `Active Memory` plugin allowing a sub-agent memory before main reply in order to proactively provide context. Added `Dreaming/memory-wiki` with `Imported Insights` capabilities for better digestion of long-term inputs.
- **Security & Infrastructure:** Tightened browser and sandbox navigations across SSRF defaults, hostnames, CDP discovery, and existing sessions. Improved `Tailscale` deployments to let remote operators work during sidecar updates and stalled startups. Enhancements to `gateway/auth` and `.env` handling restrictions.
- **Model Providers:** Added Codex provider and OpenAI-compatible provider updates, allowing ChatGPT 5-class `gpt-5.4-pro` support and new LLM idling features. Improved local open-source and reasoning support (e.g., local MLX speech providers).

## See also

- [[openclaw]]
- [[agent-orchestration]]
