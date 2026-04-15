"""axe_core — shared utilities for Axe Capital agents."""
from __future__ import annotations

from importlib import import_module

from axe_core.paths import project_root, public_dir, traces_dir
from axe_core.trace import Tracer

__all__ = [
    'project_root',
    'public_dir',
    'traces_dir',
    'Tracer',
    'AlphaOpportunity',
    'AlphaReport',
    'ArtifactHealth',
    'DecisionLogEntry',
    'HealthReport',
    'NewsItem',
    'NewsReport',
    'TraceIndex',
    'TraceIndexRun',
]

_SCHEMA_EXPORTS = {
    'AlphaOpportunity',
    'AlphaReport',
    'ArtifactHealth',
    'DecisionLogEntry',
    'HealthReport',
    'NewsItem',
    'NewsReport',
    'TraceIndex',
    'TraceIndexRun',
}


def __getattr__(name: str):
    if name in _SCHEMA_EXPORTS:
        module = import_module('axe_core.schemas')
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'axe_core' has no attribute {name!r}")
