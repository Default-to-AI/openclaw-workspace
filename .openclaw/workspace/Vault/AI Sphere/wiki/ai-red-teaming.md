---
title: "AI Red Teaming"
type: concept
domain: aisphere
created: 14-04-2026
updated: 14-04-2026
tags: [red-teaming, mental-models, decision-making]
---

# AI Red Teaming

A tactical approach for using AI to stress-test ideas, strategies, and assumptions before implementation. Because AI lacks an ego and can assume specific hostile personas (e.g., a competitor or hacker), it is highly effective at overcoming human confirmation bias.

## Core Methodology

According to the workflow outlined in [[dan-martell-smart-with-ai]], AI Red Teaming follows a three-step sequence:

1. **The Pre-Mortem (Fatal Flaw Discovery)**
   Prompt the AI to imagine evaluating the project 6 months in the future after a catastrophic failure, and force it to explain *why* it failed. This helps identify the single point of failure without emotional attachment.
2. **Steelmanning / Competitor Exploitation**
   Supply the AI with the business constraints, resource limitations, and timelines. Ask it to assume the persona of a cynical, highly successful competitor and explicitly detail how it would steal your customers by exploiting blind spots.
3. **Risk Contingency Ranking**
   Have the AI rank the identified risks by likelihood and impact, generating a strict contingency plan or checklist for the top three vulnerabilities.

## Use Cases
- Business plan stress-testing (see above)
- Hedge fund execution (e.g., dedicated risk agents with veto power in [[Finance/wiki/axe-capital-architecture-summary|Axe-Capital's architecture]])
- Cybersecurity agent bounds checking (see [[OpenClaw/wiki/security-hardening-ai-agents|OpenClaw Security Hardening]])
