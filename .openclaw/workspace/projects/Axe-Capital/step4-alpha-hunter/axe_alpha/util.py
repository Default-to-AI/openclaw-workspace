from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def workspace_root() -> Path:
    return project_root().parents[1]


def load_project_env() -> Path:
    env_path = project_root() / ".env"
    load_dotenv(env_path, override=False)
    return env_path


def today_local_iso() -> str:
    return datetime.now().astimezone().date().isoformat()


def openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENAI_API_KEY missing in project .env")
    return key
