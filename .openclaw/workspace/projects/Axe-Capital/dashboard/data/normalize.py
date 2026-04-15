#!/usr/bin/env python3
"""Normalize Axe Capital dashboard inputs into stable, easy-to-parse CSVs.

No external deps (no pandas).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]  # .../dashboard
DATA = ROOT / "data"


def read_manifest() -> dict:
    with (DATA / "manifest.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _strip_bom(s: str) -> str:
    return s.lstrip("\ufeff") if isinstance(s, str) else s


def _to_number(s: str) -> str:
    """Return a normalized numeric string or empty.

    Removes commas, surrounding quotes/spaces.
    """
    if s is None:
        return ""
    s = str(s).strip().strip('"')
    if s == "":
        return ""
    s = s.replace(",", "")
    return s


def _to_percent(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().strip('"')
    if s.endswith("%"):
        s = s[:-1]
    s = s.replace(",", "")
    return s


def normalize_portfolio(src: Path, dst: Path) -> None:
    with src.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        fieldnames = [
            "symbol",
            "position",
            "last",
            "change_pct",
            "avg_price",
            "cost_basis",
            "market_value",
            "unrealized_pl",
            "unrealized_pl_pct",
            "pe",
            "eps_current",
        ]
        rows = []
        for row in r:
            row = { _strip_bom(k): v for k,v in row.items() }
            sym = (row.get("Financial Instrument") or "").strip()
            if sym.lower() in {"total", ""}:
                continue
            if sym.lower() == "cash":
                # keep as a row so the dashboard can show cash.
                pass
            out = {
                "symbol": sym,
                "position": _to_number(row.get("Position", "")),
                "last": _to_number(row.get("Last", "")),
                "change_pct": _to_percent(row.get("Change %", "")),
                "avg_price": _to_number(row.get("Avg Price", "")),
                "cost_basis": _to_number(row.get("Cost Basis", "")),
                "market_value": _to_number(row.get("Market Value", "")),
                "unrealized_pl": _to_number(row.get("Unrealized P&L", "")),
                "unrealized_pl_pct": _to_percent(row.get("Unrealized P&L %", "")),
                "pe": _to_number(row.get("P/E", "")),
                "eps_current": _to_number(row.get("EPS (current)", "")),
            }
            rows.append(out)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def normalize_kv_statement(src: Path, dst: Path) -> None:
    """Statement exports are already KV rows: Section, Header/Data, Field Name, Field Value.

    We just strip BOM and normalize to stable columns: section, record_type, field, value.
    """
    with src.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        header = [_strip_bom(x) for x in header]
        # Expect: Statement, Header, Field Name, Field Value
        out_rows = []
        for row in r:
            if not row:
                continue
            # pad
            row = row + [""] * (4 - len(row))
            section, record_type, field, value = row[0], row[1], row[2], row[3]
            out_rows.append(
                {
                    "section": section.strip(),
                    "record_type": record_type.strip(),
                    "field": field.strip(),
                    "value": str(value).strip(),
                }
            )

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["section", "record_type", "field", "value"])
        w.writeheader()
        w.writerows(out_rows)


def main() -> int:
    m = read_manifest()
    inputs = m["inputs"]

    # portfolio
    p_src = ROOT / inputs["portfolio"]["source_file"]
    p_dst = ROOT / inputs["portfolio"]["normalized_file"]
    if not p_src.exists():
        print(f"ERROR: portfolio source not found: {p_src}", file=sys.stderr)
        return 1
    normalize_portfolio(p_src, p_dst)

    # statements (KV)
    for key in ("activity", "realized", "mtm"):
        src = ROOT / inputs[key]["source_file"]
        dst = ROOT / inputs[key]["normalized_file"]
        if not src.exists():
            print(f"WARNING: {key} source not found: {src} — skipping", file=sys.stderr)
            continue
        normalize_kv_statement(src, dst)

    print("OK: normalized ->")
    print(" -", inputs["portfolio"]["normalized_file"])
    print(" -", inputs["activity"]["normalized_file"])
    print(" -", inputs["realized"]["normalized_file"])
    print(" -", inputs["mtm"]["normalized_file"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
