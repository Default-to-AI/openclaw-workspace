from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def update_report_index(
    reports_dir: Path,
    ticker: str,
    agent: str,
    json_path: Path,
    md_path: Path | None = None,
) -> dict:
    reports_dir.mkdir(parents=True, exist_ok=True)
    index_path = reports_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"generated_at": None, "symbols": {}}

    symbol = ticker.upper()
    now = utc_now()
    index.setdefault("symbols", {}).setdefault(symbol, {})[agent] = {
        "json_path": json_path.name,
        "md_path": md_path.name if md_path else None,
        "updated_at": now,
    }
    index["generated_at"] = now

    tmp = index_path.with_name(index_path.name + ".tmp")
    tmp.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(index_path)
    return index
