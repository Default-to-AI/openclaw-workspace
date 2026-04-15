# Axe Capital — Telegram Integration Path

Telegram is for interrupts, not for every background event.

## Good alert classes

- refresh failed
- portfolio artifact stale beyond threshold
- stop-loss proximity or breach
- high-conviction new alpha candidate
- decision memo ready for review

## Bad alert classes

- routine successful refreshes
- low-impact news
- duplicate alerts for the same unresolved issue

## Recommended pattern

1. Run orchestrator refresh.
2. Regenerate `health.json`.
3. Evaluate alert conditions from artifacts.
4. Send a compact Telegram message only if the event crosses a decision threshold.

## Message shape

Keep alerts short and decision-oriented.

```text
AXE CAPITAL
ALERT: stop-loss breach risk
Ticker: MSFT
State: within 2.0% of stop
Action: review manually in dashboard
```

## Implementation note

Do not wire Telegram sends directly inside every agent. Centralize alerting in the orchestration layer after artifact generation so duplicate suppression and thresholding stay coherent.
