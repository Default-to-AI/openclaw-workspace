# HEARTBEAT.md

Heartbeat checks: **ENABLED (triage-only)**

## Rules
- Heartbeats must be cheap and fast.
- Heartbeats must NOT do research, long web browsing, or multi-step workflows.
- If something needs work, write a single task into the vault task list and stop.

## Schedule (manual)
Configure cron later. For now, when a heartbeat poll arrives:

1) Check for urgent user messages or system failures.
2) If urgent: alert in chat.
3) If non-urgent work is needed: create a task in `10_Tasks/10_Tasks.md` and reply HEARTBEAT_OK.

## Task format
- [ ] <short actionable task> (context: <where>, deadline: <if any>)
