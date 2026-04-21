from __future__ import annotations

import pytest

fastapi = pytest.importorskip('fastapi')
pytest.importorskip('sse_starlette')
from fastapi.testclient import TestClient

from axe_orchestrator import api as api_mod


def test_health_endpoint_returns_report(tmp_path, monkeypatch):
    report = {
        'generated_at': '2026-04-15T12:00:00Z',
        'artifacts': {},
        'freshness_thresholds_min': {'portfolio': 240, 'alpha': 1440, 'news': 60},
    }

    monkeypatch.setattr(api_mod, 'public_dir', lambda: tmp_path)
    monkeypatch.setattr(api_mod, 'generate_health', lambda public_dir: report)
    monkeypatch.setattr(api_mod, 'write_health', lambda: tmp_path / 'health.json')

    client = TestClient(api_mod.create_app())
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json()['generated_at'] == '2026-04-15T12:00:00Z'


def test_refresh_endpoint_returns_runner_payload(monkeypatch):
    async def fake_run_agent(target: str):
        return {'target': target, 'ok': True, 'return_code': 0, 'failure_count': 0}

    monkeypatch.setattr(api_mod, '_run_agent', fake_run_agent)

    client = TestClient(api_mod.create_app())
    response = client.post('/refresh/alpha')

    assert response.status_code == 200
    assert response.json()['target'] == 'alpha'
    assert response.json()['ok'] is True


def test_command_center_endpoint_returns_projected_payload(tmp_path, monkeypatch):
    payload = {
        "generated_at": "2026-04-21T00:25:19Z",
        "partial": False,
        "decision_inbox": [],
        "live_missions": [],
        "watchers": [],
        "surveillance_alerts": [],
        "firm_exceptions": [],
        "current_focus": None,
        "data_freshness": {},
    }

    monkeypatch.setattr(api_mod, 'write_command_center_artifacts', lambda public_dir: payload)

    client = TestClient(api_mod.create_app())
    response = client.get('/api/command-center')

    assert response.status_code == 200
    assert response.json()["generated_at"] == "2026-04-21T00:25:19Z"
    assert response.json()["partial"] is False
