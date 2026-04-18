# HEARTBEAT.md

Heartbeat checks: **ENABLED (triage-only)**

## Rules
- Heartbeats must be cheap and fast.
- Heartbeats must NOT do research, long web browsing, or multi-step workflows.
- Canonical instructions live in `Vault/CLAUDE.md`. When in doubt, follow that.
- Heartbeat responsibility is **detection + queueing** only:
  - If `Vault/_raw/` contains any pending source files (excluding `ingestion_log.md`), append **one** task under `## ⚡️ Jinx Claw Tasks` in `Vault/_raw/Tasks/Inbox.md`: “Ingest pending `_raw` sources per CLAUDE.md”.
  - If `Vault/_raw/Tasks/Inbox.md` contains any unchecked tasks, append **one** task under `## ⚡️ Jinx Claw Tasks`: “Triage Inbox → Master_Categorized_Tasks”.
  - Otherwise: reply `HEARTBEAT_OK`.

## Schedule (manual)
Configure cron later. For now, when a heartbeat poll arrives:

1) Check for urgent user messages or system failures.
2) If urgent: alert in chat.
3) If nothing urgent: reply HEARTBEAT_OK.

## Task format
- [ ] <short actionable task> (context: <where>, deadline: <if any>)
