from __future__ import annotations

from typing import Any


def safe_float(value: Any) -> float | None:
    """Canonical float coercion for COO bundle values.

    Strips commas, leading ``$``/``%``, Unicode minus (−), and leading ``+``.
    Returns ``None`` for empty, ``None``, or unparseable input.
    """
    try:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = (
                value.strip()
                .replace(",", "")
                .replace("$", "")
                .replace("%", "")
                .replace("\u2212", "-")  # Unicode minus sign
            )
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except Exception:
        return None
