# Axe Capital Step 5 — Portfolio Tracking

Pure Python portfolio tracking layer.

Inputs:
- portfolio CSV discovered under dashboard/data, preferably the normalized snapshot
- live IBKR portfolio/account snapshot when `AXE_PORTFOLIO_SOURCE=ibkr`
- normalized CSV stored inside dashboard/data and refreshed as needed
- passive allocation and hishtalmut state from `INVESTOR_PROFILE.md`

Outputs:
- normalized portfolio CSV
- weekly review JSON
- numeric smoke test output

Live IBKR mode:

```bash
AXE_PORTFOLIO_SOURCE=ibkr \
AXE_IBKR_HOST=127.0.0.1 \
AXE_IBKR_PORT=7496 \
AXE_IBKR_CLIENT_ID=51 \
python -m axe_portfolio.cli
```

Use port `7496` for TWS paper by default or `8000` for IB Gateway. This adapter is read-only and does not place orders.

Supported environment variables:

```text
AXE_PORTFOLIO_SOURCE=csv|ibkr|auto
AXE_IBKR_HOST=127.0.0.1
AXE_IBKR_PORT=7496
AXE_IBKR_CLIENT_ID=51
AXE_IBKR_ACCOUNT=U3314869 (optional)
AXE_IBKR_ACCOUNTS=U3314869, U21335661 (optional; overrides AXE_IBKR_ACCOUNT; default: all managed accounts)
AXE_IBKR_READONLY=1
AXE_IBKR_TIMEOUT=10
```
