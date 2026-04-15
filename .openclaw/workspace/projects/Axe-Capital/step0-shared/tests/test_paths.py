from pathlib import Path
from axe_core.paths import project_root, public_dir, traces_dir

def test_project_root_is_axe_capital_dir():
    root = project_root()
    assert root.name == "Axe-Capital"
    assert (root / "CLAUDE.md").exists()

def test_public_dir_points_to_step6_public():
    assert public_dir() == project_root() / "step6-dashboard" / "public"

def test_traces_dir_is_public_slash_traces(tmp_path, monkeypatch):
    assert traces_dir() == public_dir() / "traces"
