from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "FRED_API_KEY",
    "NEWSAPI_KEY",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def env_file_path() -> Path:
    return project_root() / ".env"


def load_project_env() -> Path:
    env_path = env_file_path()
    load_dotenv(dotenv_path=env_path, override=False)
    return env_path


def env_status_rows() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for key in REQUIRED_ENV_KEYS:
        value = os.getenv(key, "")
        loaded = bool(value.strip())
        display = "loaded" if loaded else "missing"
        detail = "set" if loaded else "empty or unset"
        rows.append((key, display, detail))
    return rows


def print_env_status_table() -> None:
    rows = env_status_rows()
    key_width = max(len("KEY"), *(len(key) for key, _, _ in rows))
    status_width = max(len("STATUS"), *(len(status) for _, status, _ in rows))
    detail_width = max(len("DETAIL"), *(len(detail) for _, _, detail in rows))

    border = f"+-{'-' * key_width}-+-{'-' * status_width}-+-{'-' * detail_width}-+"
    print(f"Loaded env file: {env_file_path()}", file=sys.stderr)
    print(border, file=sys.stderr)
    print(
        f"| {'KEY'.ljust(key_width)} | {'STATUS'.ljust(status_width)} | {'DETAIL'.ljust(detail_width)} |",
        file=sys.stderr,
    )
    print(border, file=sys.stderr)
    for key, status, detail in rows:
        print(
            f"| {key.ljust(key_width)} | {status.ljust(status_width)} | {detail.ljust(detail_width)} |",
            file=sys.stderr,
        )
    print(border, file=sys.stderr)


def missing_required_env_keys() -> list[str]:
    return [key for key, status, _ in env_status_rows() if status == "missing"]
