from __future__ import annotations

from dataclasses import dataclass

from axe_portfolio.ibkr import IBKRConnectionConfig, fetch_ibkr_portfolio


@dataclass
class _Contract:
    symbol: str
    secType: str = "STK"
    localSymbol: str = ""


@dataclass
class _PortfolioItem:
    contract: _Contract
    position: float
    marketPrice: float
    averageCost: float
    marketValue: float
    unrealizedPNL: float


@dataclass
class _AccountValue:
    tag: str
    value: str
    currency: str = "USD"


class _FakeIB:
    connected_with = None
    disconnected = False

    def connect(self, *args, **kwargs):
        type(self).connected_with = (args, kwargs)

    def managedAccounts(self):
        return ["DU123", "DU999"]

    def portfolio(self, account=None):
        if account == "DU123":
            return [
                _PortfolioItem(_Contract("MSFT"), 2, 425.5, 400.0, 851.0, 51.0),
                _PortfolioItem(_Contract("USD", "CASH"), 1000, 1, 1, 1000, 0),
            ]
        if account == "DU999":
            return [
                _PortfolioItem(_Contract("MSFT"), 1, 425.5, 410.0, 425.5, 15.5),
            ]
        raise AssertionError(f"unexpected account: {account}")

    def accountSummary(self, account=None):
        if account == "DU123":
            return [_AccountValue("TotalCashValue", "1234.56")]
        if account == "DU999":
            return [_AccountValue("TotalCashValue", "10.00")]
        raise AssertionError(f"unexpected account: {account}")

    def disconnect(self):
        type(self).disconnected = True


def test_fetch_ibkr_portfolio_maps_live_snapshot():
    config = IBKRConnectionConfig(host="localhost", port=4001, client_id=77, timeout=3)

    rows, cash = fetch_ibkr_portfolio(config=config, ib_factory=_FakeIB)

    assert cash == 1244.56
    assert rows == [
        {
            "symbol": "MSFT",
            "position": 3.0,
            "last": 425.5,
            "change_pct": None,
            "avg_price": 403.333333,
            "cost_basis": 1210.0,
            "market_value": 1276.5,
            "unrealized_pl": 66.5,
            "unrealized_pl_pct": 5.5,
            "pe": None,
            "eps_current": None,
        }
    ]
    assert _FakeIB.connected_with == (
        ("localhost", 4001),
        {"clientId": 77, "timeout": 3, "readonly": True, "account": ""},
    )
    assert _FakeIB.disconnected is True
