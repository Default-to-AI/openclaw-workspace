from __future__ import annotations

from axe_technical.agent import _normalize_result, build_technical_context, classify_trend


def test_classify_trend_uses_moving_average_relationship():
    assert classify_trend(last_price=110, sma_50=100, sma_200=90) == "uptrend"
    assert classify_trend(last_price=80, sma_50=90, sma_200=100) == "downtrend"
    assert classify_trend(last_price=95, sma_50=100, sma_200=90) == "mixed"


def test_build_technical_context_calculates_levels_from_history():
    rows = [
        {"Close": 10.0, "High": 11.0, "Low": 9.0, "Volume": 100},
        {"Close": 12.0, "High": 13.0, "Low": 10.0, "Volume": 150},
        {"Close": 11.0, "High": 12.0, "Low": 8.0, "Volume": 120},
    ]

    context = build_technical_context("goog", rows)

    assert context["ticker"] == "GOOG"
    assert context["last_price"] == 11.0
    assert context["support"] == 8.0
    assert context["resistance"] == 13.0


def test_normalize_result_maps_text_confidence_to_number():
    report = _normalize_result("pfe", {}, {"confidence": "High"})

    assert report["confidence"] == 8
