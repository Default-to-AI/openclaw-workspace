"""Thin wrappers that invoke each agent's CLI. Return codes are failure counts."""
from __future__ import annotations

import subprocess
import sys

from axe_core.paths import project_root


AGENT_ORDER = ("portfolio", "alpha", "news")


def _run_module(module: str, cwd_subdir: str) -> int:
    cwd = project_root() / cwd_subdir
    result = subprocess.run(
        [sys.executable, "-m", module],
        check=False,
        cwd=cwd,
    )
    return 0 if result.returncode == 0 else 1


def run_alpha() -> int:
    return _run_module("axe_alpha.cli", "step4-alpha-hunter")


def run_portfolio() -> int:
    return _run_module("axe_portfolio.cli", "step5-portfolio-tracking")


def run_news() -> int:
    return _run_module("axe_news.cli", "step2-news")


def run_all() -> dict[str, int]:
    return {
        "portfolio": run_portfolio(),
        "alpha": run_alpha(),
        "news": run_news(),
    }
