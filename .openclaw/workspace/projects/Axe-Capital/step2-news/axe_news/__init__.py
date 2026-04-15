"""axe_news — RSS + LLM impact scoring."""
from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_shared_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    shared = repo_root / 'step0-shared'
    if shared.exists():
        shared_str = str(shared)
        if shared_str not in sys.path:
            sys.path.insert(0, shared_str)


_bootstrap_shared_path()
