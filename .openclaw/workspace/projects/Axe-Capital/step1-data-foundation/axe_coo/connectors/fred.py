from __future__ import annotations

from dataclasses import dataclass

import httpx

from axe_coo.models import FredSeriesPoint


@dataclass
class FredResult:
    series_id: str
    points: list[FredSeriesPoint]
    used_key: bool


def fetch_fred_series(series_id: str, api_key: str | None, timeout: float = 10.0) -> FredResult:
    if not api_key:
        return FredResult(series_id=series_id, points=[], used_key=False)

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 60,
    }

    with httpx.Client(timeout=timeout) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json() or {}

    pts: list[FredSeriesPoint] = []
    for o in (data.get("observations") or [])[:60]:
        v = o.get("value")
        val = None
        try:
            if v is not None and v != ".":
                val = float(v)
        except Exception:
            val = None
        pts.append(FredSeriesPoint(date=o.get("date"), value=val))

    return FredResult(series_id=series_id, points=pts, used_key=True)
