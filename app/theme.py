"""Custom CSS - dark advisory-grade theme, Fraunces serif headers + Inter body,
muted gold accent. Sidebar is forced permanently open (no collapse toggle)."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-deep: #0B0E16;
    --bg-surface: #111827;
    --bg-surface-2: #161F30;
    --bg-sidebar: #090C12;
    --gold: #C9A227;
    --gold-bright: #DDBA4A;
    --border: #232E42;
    --text-primary: #EDEFF2;
    --text-dim: #8993A6;
    --text-faint: #5C6579;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.stApp { background: var(--bg-deep); }

#MainMenu, footer, header {visibility: hidden;}
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[kind="header"] { display: none !important; }

/* Force sidebar permanently open - no collapse possible */
[data-testid="stSidebar"] {
    min-width: 320px !important;
    max-width: 320px !important;
    transform: none !important;
    visibility: visible !important;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 320px !important;
    max-width: 320px !important;
    margin-left: 0px !important;
}

.block-container { padding-top: 2.5rem; max-width: 1080px; }

/* Header */
.report-header {
    padding: 0 0 20px 0;
    margin-bottom: 28px;
    border-bottom: 1px solid var(--border);
}
.report-header .eyebrow {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--gold);
    font-weight: 600;
}
.report-header h1 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 2.3rem;
    color: var(--text-primary);
    margin: 6px 0 4px 0;
    letter-spacing: -0.5px;
}
.report-header .subtitle {
    font-size: 0.92rem;
    color: var(--text-dim);
}
.report-header .confidential {
    margin-top: 14px;
    font-size: 0.68rem;
    color: var(--text-faint);
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* Exhibit labels */
.exhibit-label {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.25rem;
    color: var(--text-primary);
    margin-top: 36px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--gold);
    display: inline-block;
}

/* Metric cards */
.metric-card {
    background: var(--bg-surface-2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 22px;
}
.metric-card .metric-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-dim);
}
.metric-card .metric-value {
    font-family: 'Fraunces', serif;
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--gold-bright);
    margin-top: 6px;
}

/* Risk flags */
.risk-flag {
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 3px solid;
    background: var(--bg-surface-2);
}
.risk-flag.high { border-color: #D45A5A; }
.risk-flag.medium { border-color: var(--gold); }
.risk-flag.low { border-color: var(--text-faint); }
.risk-flag .flag-title { font-weight: 600; color: var(--text-primary); }
.risk-flag .flag-severity {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.6px;
    font-weight: 700; margin-right: 8px; color: var(--text-dim);
}

/* Memo block */
.memo-block {
    background: var(--bg-surface-2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 30px 34px;
    font-family: 'Fraunces', serif;
    font-weight: 400;
    line-height: 1.75;
    color: var(--text-primary);
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] input {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

[data-testid="stTable"], .stDataFrame { background: var(--bg-surface-2) !important; }

[data-testid="stAlert"] {
    background: var(--bg-surface-2) !important;
    border-left: 3px solid var(--gold) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
}

.stButton > button {
    background: var(--gold);
    color: #0B0E16;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    letter-spacing: 0.2px;
    padding: 10px 22px;
}
.stButton > button:hover { background: var(--gold-bright); color: #0B0E16; }

.report-footer {
    margin-top: 44px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    font-size: 0.7rem;
    color: var(--text-faint);
    text-align: center;
}
</style>
"""
