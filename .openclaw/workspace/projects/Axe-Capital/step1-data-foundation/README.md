# Axe Capital — Step 1 (Data Foundation)

COO data foundation: fetch + normalize ticker data into a single JSON bundle.

## Run

```bash
cd /home/tiger/.openclaw/workspace/projects/Axe-Capital/step1-data-foundation
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .

axe-coo-bundle AAPL > /tmp/aapl.bundle.json
```

## Environment file

The CLI loads credentials from:

```bash
/home/tiger/.openclaw/workspace/projects/Axe-Capital/.env
```

A matching `.env.example` is provided for documentation.

Required keys checked at startup:

- `OPENAI_API_KEY`
- `FRED_API_KEY`
- `NEWSAPI_KEY`

Startup prints a status table to `stderr` and exits with code `2` if any required key is missing.

Reddit is optional. If Reddit credentials are absent, the connector stays non-blocking and the bundle still builds.

News wiring:
- `NewsAPI` is primary
- `DuckDuckGo` is the fallback when NewsAPI fails or returns zero items

Options flow wiring:
- `uw.py` is vendored from the Stock Market Pro skill
- `options_flow` is included in the bundle
- on failure, `options_flow` is emitted as `null` and the CLI logs a warning without crashing

## Exit criteria mapping

- Given a ticker, returns a complete data bundle (prices, basic snapshot, filings, news, macro, reddit, options_flow) in a single JSON.
- Freshness fields included per source.
