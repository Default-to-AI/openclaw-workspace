from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from axe_coo.models import EdgarFiling


UA = "AxeCapitalCOO/0.1 (research; contact: robert@local)"


@dataclass
class EdgarResult:
    cik: str | None
    filings: list[EdgarFiling]


def _headers() -> dict[str, str]:
    return {
        "User-Agent": UA,
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov",
    }


def _normalize_cik(cik: str) -> str:
    cik = str(int(cik))
    return cik.zfill(10)


def lookup_cik_by_ticker(ticker: str, timeout: float = 10.0) -> str | None:
    url = "https://www.sec.gov/files/company_tickers.json"
    with httpx.Client(timeout=timeout, headers={"User-Agent": UA}) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()

    t = ticker.upper()
    for _, row in data.items():
        if str(row.get("ticker", "")).upper() == t:
            return _normalize_cik(str(row.get("cik_str")))
    return None


def fetch_recent_filings_by_cik(cik: str, timeout: float = 10.0) -> list[EdgarFiling]:
    cik_norm = _normalize_cik(cik)
    url = f"https://data.sec.gov/submissions/CIK{cik_norm}.json"
    with httpx.Client(timeout=timeout, headers=_headers()) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()

    recent = (((data or {}).get("filings") or {}).get("recent")) or {}
    forms = recent.get("form") or []
    filing_dates = recent.get("filingDate") or []
    report_dates = recent.get("reportDate") or []
    accession_numbers = recent.get("accessionNumber") or []
    primary_docs = recent.get("primaryDocument") or []

    out: list[EdgarFiling] = []
    for i in range(min(len(forms), 50)):
        form = forms[i]
        accession = accession_numbers[i] if i < len(accession_numbers) else None
        filing_date = filing_dates[i] if i < len(filing_dates) else None
        report_date = report_dates[i] if i < len(report_dates) else None
        primary = primary_docs[i] if i < len(primary_docs) else None

        filing_url = None
        if accession and primary:
            acc_no = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no}/{primary}"

        out.append(
            EdgarFiling(
                form=form,
                filing_date=filing_date,
                report_date=report_date,
                accession_number=accession,
                primary_document=primary,
                filing_url=filing_url,
            )
        )

    return out


def fetch_edgar_bundle(ticker: str, timeout: float = 10.0) -> EdgarResult:
    cik = None
    filings: list[EdgarFiling] = []
    try:
        cik = lookup_cik_by_ticker(ticker, timeout=timeout)
        if cik:
            filings = fetch_recent_filings_by_cik(cik, timeout=timeout)
    except Exception:
        pass
    return EdgarResult(cik=cik, filings=filings)
