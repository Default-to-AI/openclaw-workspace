from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest

from axe_portfolio.flex import fetch_flex_portfolio, FlexQueryConfig

SEND_SUCCESS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexStatementResponse timestamp="20260420;123000">
  <Status>Success</Status>
  <ReferenceCode>12345678</ReferenceCode>
  <Url>https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement</Url>
</FlexStatementResponse>"""

STATEMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="AxePortfolio" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U123456" fromDate="20260419" toDate="20260419">
      <OpenPositions>
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="STK" symbol="TSLA" description="TESLA INC"
          conid="76792991" secType="STK" listingExchange="NASDAQ"
          position="50" markPrice="170.00" positionValue="8500.00"
          openPrice="155.00" costBasisPrice="155.00" costBasisMoney="7750.00"
          percentOfNAV="10.5" fifoPnlUnrealized="750.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="STK" symbol="MSFT" description="MICROSOFT CORP"
          conid="272093" secType="STK" listingExchange="NASDAQ"
          position="30" markPrice="420.00" positionValue="12600.00"
          openPrice="400.00" costBasisPrice="400.00" costBasisMoney="12000.00"
          percentOfNAV="15.2" fifoPnlUnrealized="600.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
        <OpenPosition accountId="U123456" acctAlias="" model="" currency="USD"
          assetCategory="CASH" symbol="USD.EUR" description="USD.EUR"
          conid="12087792" secType="CASH" listingExchange=""
          position="1000" markPrice="0.93" positionValue="930.00"
          openPrice="0.93" costBasisPrice="0.93" costBasisMoney="930.00"
          percentOfNAV="1.1" fifoPnlUnrealized="0.00"
          side="Long" levelOfDetail="SUMMARY" openDateTime="" holdingPeriodDateTime=""
          currency2="" fxRateToBase="1" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency accountId="U123456" currency="BASE"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00"
          endingCashPaxos="" />
        <CashReportCurrency accountId="U123456" currency="USD"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00"
          endingCashPaxos="" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def _mock_responses(send_xml: str, statement_xml: str):
    """Return a side_effect list: first call returns send_xml, second returns statement_xml."""
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = send_xml

    stmt_resp = MagicMock()
    stmt_resp.raise_for_status.return_value = None
    stmt_resp.text = statement_xml

    return [send_resp, stmt_resp]


def test_happy_path():
    config = FlexQueryConfig(token="tok123", query_id="987654")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, STATEMENT_XML)):
        rows, cash = fetch_flex_portfolio(config)

    assert cash == pytest.approx(9253.0)
    assert len(rows) == 2  # CASH row filtered out

    symbols = {r["symbol"] for r in rows}
    assert symbols == {"TSLA", "MSFT"}

    tsla = next(r for r in rows if r["symbol"] == "TSLA")
    assert tsla["position"] == 50.0
    assert tsla["last"] == pytest.approx(170.00)
    assert tsla["avg_price"] == pytest.approx(155.00)
    assert tsla["cost_basis"] == pytest.approx(7750.00)
    assert tsla["unrealized_pl"] == pytest.approx(750.00)
    assert tsla["market_value"] == pytest.approx(8500.00)
    assert tsla["change_pct"] is None
    assert tsla["pe"] is None
    assert tsla["eps_current"] is None


SEND_ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexStatementResponse timestamp="20260420;123000">
  <Status>Fail</Status>
  <ErrorCode>1012</ErrorCode>
  <ErrorMessage>Token has expired.</ErrorMessage>
</FlexStatementResponse>"""

PENDING_XML = "Statement generation in progress"


def test_missing_env_vars_raises(monkeypatch):
    monkeypatch.delenv("AXE_IBKR_FLEX_TOKEN", raising=False)
    monkeypatch.delenv("AXE_IBKR_FLEX_QUERY_ID", raising=False)
    with pytest.raises(RuntimeError, match="AXE_IBKR_FLEX_TOKEN"):
        fetch_flex_portfolio()


def test_ibkr_error_code_raises():
    config = FlexQueryConfig(token="tok", query_id="123")
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = SEND_ERROR_XML
    with patch("axe_portfolio.flex.requests.get", return_value=send_resp):
        with pytest.raises(RuntimeError, match="Token has expired"):
            fetch_flex_portfolio(config)


def test_timeout_after_max_retries():
    config = FlexQueryConfig(token="tok", query_id="123")
    send_resp = MagicMock()
    send_resp.raise_for_status.return_value = None
    send_resp.text = SEND_SUCCESS_XML

    pending_resp = MagicMock()
    pending_resp.raise_for_status.return_value = None
    pending_resp.text = PENDING_XML

    side_effects = [send_resp] + [pending_resp] * 10
    with patch("axe_portfolio.flex.requests.get", side_effect=side_effects):
        with patch("axe_portfolio.flex.time.sleep"):
            with pytest.raises(TimeoutError):
                fetch_flex_portfolio(config)


EMPTY_STATEMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="AxePortfolio" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U123456" fromDate="20260419" toDate="20260419">
      <OpenPositions />
      <CashReport>
        <CashReportCurrency accountId="U123456" currency="BASE"
          fromDate="20260419" toDate="20260419"
          startingCash="9000.00" endingCash="9253.00" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def test_empty_positions_raises():
    config = FlexQueryConfig(token="tok", query_id="123")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, EMPTY_STATEMENT_XML)):
        with pytest.raises(RuntimeError, match="no positions"):
            fetch_flex_portfolio(config)


MULTI_ACCOUNT_NO_BASE_CASH_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="Axe Portfolio" type="AF">
  <FlexStatements count="2">
    <FlexStatement accountId="U21335661" fromDate="17/04/2026" toDate="17/04/2026">
      <CashReport>
        <CashReportCurrency endingCash="41.87" endingCashSec="41.87" endingCashCom="0" />
      </CashReport>
      <OpenPositions>
        <OpenPosition symbol="QQQ" position="29.31" markPrice="648.85"
          costBasisPrice="559.112702149" costBasisMoney="16387.5933"
          fifoPnlUnrealized="2630.1967" />
      </OpenPositions>
    </FlexStatement>
    <FlexStatement accountId="U3314869" fromDate="17/04/2026" toDate="17/04/2026">
      <CashReport>
        <CashReportCurrency endingCash="7161.076529624" endingCashSec="7161.076529624" endingCashCom="0" />
      </CashReport>
      <OpenPositions>
        <OpenPosition symbol="AMZN" position="37.1998" markPrice="250.56"
          costBasisPrice="227.006749606" costBasisMoney="8444.605684"
          fifoPnlUnrealized="876.174316" />
      </OpenPositions>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def test_cash_falls_back_to_sum_when_base_currency_missing():
    config = FlexQueryConfig(token="tok", query_id="123")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, MULTI_ACCOUNT_NO_BASE_CASH_XML)):
        rows, cash = fetch_flex_portfolio(config)

    assert len(rows) == 2
    assert cash == pytest.approx(7202.946529624)


DUPLICATE_SYMBOL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="Axe Portfolio" type="AF">
  <FlexStatements count="2">
    <FlexStatement accountId="U111">
      <OpenPositions>
        <OpenPosition symbol="QQQ" position="29.31" markPrice="648.85"
          costBasisPrice="559.11" costBasisMoney="16387.59"
          fifoPnlUnrealized="2630.20" />
        <OpenPosition symbol="AMZN" position="10.0" markPrice="250.00"
          costBasisPrice="200.00" costBasisMoney="2000.00"
          fifoPnlUnrealized="500.00" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency endingCash="100.00" />
      </CashReport>
    </FlexStatement>
    <FlexStatement accountId="U222">
      <OpenPositions>
        <OpenPosition symbol="QQQ" position="39.97" markPrice="648.85"
          costBasisPrice="625.48" costBasisMoney="25001.29"
          fifoPnlUnrealized="934.02" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency endingCash="200.00" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def test_duplicate_symbols_aggregated():
    config = FlexQueryConfig(token="tok", query_id="123")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, DUPLICATE_SYMBOL_XML)):
        rows, cash = fetch_flex_portfolio(config)

    symbols = [r["symbol"] for r in rows]
    assert symbols.count("QQQ") == 1, "duplicate QQQ should be merged into one row"
    assert len(rows) == 2  # QQQ (merged) + AMZN

    qqq = next(r for r in rows if r["symbol"] == "QQQ")
    assert qqq["position"] == pytest.approx(29.31 + 39.97)
    assert qqq["cost_basis"] == pytest.approx(16387.59 + 25001.29)
    assert qqq["unrealized_pl"] == pytest.approx(2630.20 + 934.02)
    assert qqq["last"] == pytest.approx(648.85)
    assert qqq["avg_price"] == pytest.approx((16387.59 + 25001.29) / (29.31 + 39.97), rel=1e-3)
    assert cash == pytest.approx(300.00)


ILS_CASH_XML = """<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="Axe Portfolio" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U111">
      <OpenPositions>
        <OpenPosition symbol="TSLA" position="5.0" markPrice="400.00"
          costBasisPrice="380.00" costBasisMoney="1900.00"
          fifoPnlUnrealized="100.00" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency currency="USD" endingCash="7202.95" />
        <CashReportCurrency currency="ILS" endingCash="3500.00" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>"""


def test_cash_excludes_non_usd_when_currency_attr_present():
    config = FlexQueryConfig(token="tok", query_id="123")
    with patch("axe_portfolio.flex.requests.get", side_effect=_mock_responses(SEND_SUCCESS_XML, ILS_CASH_XML)):
        rows, cash = fetch_flex_portfolio(config)

    assert cash == pytest.approx(7202.95), "ILS cash should be excluded when currency attr is present"
    assert len(rows) == 1
