"""
Data ingestion for QoE Intelligence.
1. Pulls reported financials via yfinance (structured, headline numbers).
2. Extracts footnote/MD&A text from an uploaded annual report PDF (unstructured,
   where real QoE red flags actually live - related-party notes, contingencies,
   one-off items buried in disclosures).
"""
import yfinance as yf
import pdfplumber


def fetch_reported_financials(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    try:
        income_stmt = t.financials.T
        balance_sheet = t.balance_sheet.T
        cashflow = t.cashflow.T
        info = t.info
    except Exception as e:
        raise RuntimeError(f"Failed to fetch financials for {ticker}: {e}")

    return {
        "ticker": ticker,
        "company_name": info.get("longName", ticker),
        "income_statement": income_stmt,
        "balance_sheet": balance_sheet,
        "cashflow": cashflow,
        "info": info,
    }


def extract_pdf_text(pdf_path: str, max_pages: int = 150) -> str:
    """
    Extracts raw text from an uploaded annual report PDF.
    Capped at max_pages to keep AI context manageable - notes-to-accounts
    are usually in the back half of the report, so this should be tuned
    if a specific report is unusually long.
    """
    text_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(f"--- Page {i + 1} ---\n{page_text}")
    return "\n\n".join(text_chunks)


def find_relevant_footnote_sections(full_text: str, keywords: list = None) -> str:
    """
    Cheap pre-filter before sending to Claude: keeps only paragraphs containing
    QoE-relevant keywords, so the AI reads the signal, not 150 pages of noise.
    This keeps API costs down and improves the quality of what gets flagged.
    """
    if keywords is None:
        keywords = [
            "related party", "related-party", "exceptional item", "one-time",
            "one-off", "contingent liability", "litigation", "impairment",
            "discontinued operation", "restructuring", "write-off", "write off",
            "change in accounting policy", "prior period", "settlement",
            "provision", "extraordinary item"
        ]

    paragraphs = full_text.split("\n\n")
    relevant = [
        p for p in paragraphs
        if any(kw.lower() in p.lower() for kw in keywords)
    ]
    return "\n\n---\n\n".join(relevant)
