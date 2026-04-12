# Axe Capital Step 5 — Portfolio Tracking

Pure Python portfolio tracking layer.

Inputs:
- raw IBKR export CSV from Vault (read-only source)
- normalized CSV stored inside Axe Capital project
- passive allocation and hishtalmut state from `INVESTOR_PROFILE.md`

Outputs:
- normalized portfolio CSV
- weekly review JSON
- numeric smoke test output
