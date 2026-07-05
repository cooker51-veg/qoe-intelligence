"""Custom CSS injected into the Streamlit app to override the default look
and achieve a Big 4 advisory report aesthetic."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --navy: #1A2332;
    --charcoal: #2D3748;
    --gold: #B8860B;
    --gold-light: #D4A017;
    --cream: #F4F2ED;
    --border-grey: #D1D5DB;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Kill default Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

/* Report cover / header block */
.report-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--charcoal) 100%);
    color: white;
    padding: 40px 48px;
    border-radius: 4px;
    margin-bottom: 32px;
    border-left: 6px solid var(--gold);
}
.report-header h1 {
    font-family: 'Source Serif 4', serif;
    font-weight: 700;
    font-size: 2.1rem;
    margin-bottom: 4px;
    color: white;
}
.report-header .subtitle {
    font-size: 0.95rem;
    color: #C8CDD6;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.report-header .confidential {
    margin-top: 16px;
    font-size: 0.75rem;
    color: var(--gold-light);
    letter-spacing: 1px;
    text-transform: uppercase;
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 12px;
}

/* Exhibit section labels */
.exhibit-label {
    font-family: 'Source Serif 4', serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--navy);
    border-bottom: 2px solid var(--gold);
    padding-bottom: 8px;
    margin-top: 32px;
    margin-bottom: 16px;
}

/* Metric cards */
.metric-card {
    background: var(--cream);
    border: 1px solid var(--border-grey);
    border-left: 4px solid var(--gold);
    border-radius: 2px;
    padding: 20px 24px;
}
.metric-card .metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--charcoal);
    opacity: 0.7;
}
.metric-card .metric-value {
    font-family: 'Source Serif 4', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--navy);
    margin-top: 4px;
}

/* Risk flag callouts */
.risk-flag {
    border-radius: 2px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 4px solid;
}
.risk-flag.high { background: #FDF2F2; border-color: #C0392B; }
.risk-flag.medium { background: #FEF9E7; border-color: var(--gold); }
.risk-flag.low { background: #F0F4F8; border-color: #7F8C9A; }
.risk-flag .flag-title { font-weight: 600; color: var(--navy); }
.risk-flag .flag-severity {
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px;
    font-weight: 700; margin-right: 8px;
}

/* Memo text block */
.memo-block {
    background: white;
    border: 1px solid var(--border-grey);
    border-radius: 2px;
    padding: 32px;
    font-family: 'Source Serif 4', serif;
    line-height: 1.7;
    color: #1F2937;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--navy);
}
[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
}
[data-testid="stSidebar"] input {
    color: var(--navy) !important;
}

/* Buttons */
.stButton > button {
    background: var(--navy);
    color: white;
    border: none;
    border-radius: 2px;
    font-weight: 600;
    letter-spacing: 0.3px;
    padding: 10px 24px;
}
.stButton > button:hover {
    background: var(--gold);
    color: var(--navy);
}

/* Footer disclaimer */
.report-footer {
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid var(--border-grey);
    font-size: 0.72rem;
    color: #6B7280;
    text-align: center;
}
</style>
"""
