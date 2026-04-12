# Axe Capital Step 4 — Alpha Hunter

Proactive daily opportunity scanner.

Outputs daily ranked JSON reports to `reports/YYYY-MM-DD.json`.

Sources scanned:
- SEC EDGAR 8-K event scanner
- Insider buying clusters via SEC ownership filings
- Earnings surprise with delayed price reaction
- Spin-off/restructuring tracker
- Unusual options activity via vendored `uw.py`

LLM usage is restricted to summarizing pre-identified opportunities into thesis + conviction using `gpt-4o-mini`.
