# QoE Intelligence — AI-Powered Quality of Earnings Platform

Automated Big 4-style financial due diligence tool. Enter a ticker (and optionally
upload an annual report PDF) and it generates an EBITDA normalization bridge,
footnote-level red flag detection, and an AI-drafted QoE memorandum.

## Project structure
```
qoe-intelligence/
├── data/
│   └── ingest.py          # yfinance pull + PDF footnote extraction
├── engine/
│   └── qoe_engine.py      # rule-based adjustment screen + EBITDA bridge builder
├── ai/
│   └── qoe_ai.py          # Claude API - footnote red flags + memo drafting
├── app/
│   ├── theme.py           # custom CSS (navy/charcoal/gold, Big 4 report styling)
│   ├── main.py            # Streamlit app - the website itself
│   └── .streamlit/
│       └── config.toml    # base theme colors
└── requirements.txt
```

## Run locally
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
streamlit run app/main.py
```

## Deploy to Streamlit Community Cloud
See the step-by-step deployment guide provided separately. Summary:
1. Push this folder to a GitHub repo
2. Connect the repo at share.streamlit.io
3. Set main file path to `app/main.py`
4. Add `ANTHROPIC_API_KEY` under app Settings → Secrets
