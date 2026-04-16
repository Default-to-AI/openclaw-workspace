from __future__ import annotations

from axe_macro.agent import _normalize_result, infer_asset_context, normalize_macro_context


def test_infer_asset_context_identifies_etfs():
    context = infer_asset_context({"quoteType": "ETF", "category": "Large Growth"})

    assert context["instrument_type"] == "ETF"
    assert "Large Growth" in context["macro_exposures"]


def test_normalize_macro_context_has_uppercase_ticker_and_sector():
    context = normalize_macro_context("goog", {"sector": "Communication Services", "quoteType": "EQUITY"})

    assert context["ticker"] == "GOOG"
    assert context["sector"] == "Communication Services"


def test_normalize_result_maps_text_confidence_to_number():
    report = _normalize_result("pfe", {}, {"confidence": "Medium"})

    assert report["confidence"] == 5
