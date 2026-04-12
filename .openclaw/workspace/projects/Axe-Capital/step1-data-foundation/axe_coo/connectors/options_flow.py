from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass
class OptionsFlowResult:
    data: dict[str, Any] | None
    warning: str | None = None


def fetch_options_flow(ticker: str, timeout_seconds: int = 20) -> OptionsFlowResult:
    try:
        from axe_coo.vendors import uw as uw_vendor
    except Exception as exc:
        return OptionsFlowResult(data=None, warning=f"options_flow unavailable: {exc}")

    try:
        data = asyncio.run(uw_vendor._run_with_timeout(ticker, total_timeout_s=timeout_seconds))
    except Exception as exc:
        return OptionsFlowResult(data=None, warning=f"options_flow unavailable: {exc}")

    if isinstance(data, str):
        return OptionsFlowResult(data=None, warning=data)

    if not isinstance(data, dict):
        return OptionsFlowResult(data=None, warning="options_flow unavailable: unexpected payload")

    return OptionsFlowResult(data=data)
