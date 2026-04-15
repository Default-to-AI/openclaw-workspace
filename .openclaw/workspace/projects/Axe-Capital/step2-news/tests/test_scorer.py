from __future__ import annotations

from axe_news.ingest import RawItem
from axe_news.scorer import ImpactScore, build_prompt, parse_response, score_item


def _item(title="t", summary="s") -> RawItem:
    return RawItem(
        title=title,
        url="https://x",
        source="reuters-biz",
        published_at="2026-04-15T00:00:00Z",
        summary=summary,
    )


def test_build_prompt_includes_item_and_tickers():
    prompt = build_prompt(_item("MSFT antitrust probe"), tickers=["MSFT"])
    assert "MSFT" in prompt
    assert "antitrust" in prompt


def test_parse_response_happy_path():
    raw = '{"impact_score": 8, "impact_rationale": "DOJ probe could force structural remedy", "decision_hook": "Consider trimming MSFT if probe widens", "portfolio_relevance": "held"}'
    out = parse_response(raw)
    assert out == ImpactScore(
        impact_score=8,
        impact_rationale="DOJ probe could force structural remedy",
        decision_hook="Consider trimming MSFT if probe widens",
        portfolio_relevance="held",
    )


def test_parse_response_tolerates_markdown_fence():
    raw = "```json\n{\"impact_score\": 6, \"impact_rationale\": \"r\", \"decision_hook\": null, \"portfolio_relevance\": \"sector\"}\n```"
    out = parse_response(raw)
    assert out.impact_score == 6
    assert out.decision_hook is None


def test_parse_response_returns_none_on_garbage():
    assert parse_response("not json at all") is None


def test_score_item_uses_anthropic_sdk_with_cache_control(monkeypatch):
    calls = {}

    class FakeMessage:
        def __init__(self):
            self.content = [type("B", (), {"text": '{"impact_score": 7, "impact_rationale": "r", "decision_hook": null, "portfolio_relevance": "held"}'})]

    class FakeMessages:
        def create(self, **kwargs):
            calls["kwargs"] = kwargs
            return FakeMessage()

    class FakeClient:
        def __init__(self, *a, **k):
            self.messages = FakeMessages()

    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)

    item = _item("MSFT probe", "DOJ opens inquiry")
    result = score_item(item, tickers=["MSFT"], relevance="held", api_key="sk-test")

    assert result.impact_score == 7
    assert calls["kwargs"]["model"] == "claude-haiku-4-5-20251001"
    # The system block must be marked as cacheable
    system_blocks = calls["kwargs"]["system"]
    assert any(b.get("cache_control", {}).get("type") == "ephemeral" for b in system_blocks)
