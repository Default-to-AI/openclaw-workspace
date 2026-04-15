"""Canonical filesystem paths for the Axe Capital project."""
from __future__ import annotations
from pathlib import Path

def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name == "Axe-Capital" and (parent / "CLAUDE.md").exists():
            return parent
    raise RuntimeError("Could not locate Axe-Capital project root from axe_core")

def public_dir() -> Path:
    return project_root() / "step6-dashboard" / "public"

def traces_dir() -> Path:
    return public_dir() / "traces"
