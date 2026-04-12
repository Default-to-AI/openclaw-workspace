from __future__ import annotations

from datetime import datetime, timedelta

from axe_coo.models import FreshnessPolicy


def age_seconds(now: datetime, fetched_at: datetime) -> int:
    return int((now - fetched_at).total_seconds())


def is_stale(now: datetime, fetched_at: datetime, max_age_seconds: int) -> bool:
    return fetched_at < (now - timedelta(seconds=max_age_seconds))


def build_freshness_report(now: datetime, fetched_at_by_source: dict[str, datetime], policy: FreshnessPolicy):
    # We only track sources that were actually fetched.
    return {
        "now": now.isoformat(),
        "sources": {
            name: {
                "fetched_at": ts.isoformat(),
                "age_seconds": age_seconds(now, ts),
                "max_age_seconds": getattr(policy, f"{name}_max_age_seconds", None),
            }
            for name, ts in fetched_at_by_source.items()
        },
    }
