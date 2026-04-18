#!/usr/bin/env python3
"""Cheap triage checks for Vault ingestion + task flow.

Intended for heartbeat use: detect whether there's anything to do,
without performing ingestion/refiles.

Rules encoded from Vault/CLAUDE.md:
- Raw intake lives in Vault/_raw (underscore folder).
- Task intake lives in Vault/_raw/Tasks/Inbox.md.
- Master tasks live in Vault/Master_Categorized_Tasks.md.

Exit codes:
  0 = nothing to do
  10 = raw intake pending (non-task files in _raw excluding ingestion_log.md)
  11 = inbox has open tasks
  12 = both raw intake pending and inbox has open tasks
"""

from __future__ import annotations

from pathlib import Path

VAULT = Path("/home/tiger/.openclaw/workspace/Vault")
RAW = VAULT / "_raw"
INBOX = RAW / "Tasks" / "Inbox.md"

EXCLUDE_RAW = {"ingestion_log.md"}


def raw_pending() -> list[Path]:
    if not RAW.exists():
        return []
    files = [p for p in RAW.iterdir() if p.is_file() and p.name not in EXCLUDE_RAW]
    return sorted(files)


def inbox_open_tasks() -> int:
    if not INBOX.exists():
        return 0
    text = INBOX.read_text(encoding="utf-8")
    # Count unchecked tasks anywhere in inbox (cheap + robust)
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("- [ ]"))


def main() -> None:
    raw = raw_pending()
    open_tasks = inbox_open_tasks()

    raw_flag = bool(raw)
    tasks_flag = open_tasks > 0

    if raw_flag and tasks_flag:
        raise SystemExit(12)
    if raw_flag:
        raise SystemExit(10)
    if tasks_flag:
        raise SystemExit(11)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
