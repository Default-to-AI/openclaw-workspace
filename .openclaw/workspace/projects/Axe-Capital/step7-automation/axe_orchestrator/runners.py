"""Thin wrappers that invoke each agent's CLI. Return codes are failure counts."""
from __future__ import annotations

import subprocess

from axe_core.paths import project_root


def _run_module(module: str, cwd_subdir: str) -> int:
    cwd = project_root() / cwd_subdir
    result = subprocess.run(
        ["python", "-m", module],
        check=False,
        cwd=cwd,
    )
    return 0 if result.returncode == 0 else 1


def run_alpha() -> int:
    return _run_module("axe_alpha.cli", "step4-alpha-hunter")


def run_portfolio() -> int:
    return _run_module("axe_portfolio.cli", "step5-portfolio-tracking")


def run_news() -> int:
    # Placeholder until Task 7 ships axe_news.
    return _run_module("axe_news.cli", "step2-news")
