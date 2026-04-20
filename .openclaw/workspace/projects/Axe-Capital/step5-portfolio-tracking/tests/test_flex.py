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
