"""
QoE Intelligence — AI-Powered Quality of Earnings Platform
Run: streamlit run app/main.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tempfile

from theme import CUSTOM_CSS
from data.ingest import fetch_reported_financials, extract_pdf_text, find_relevant_footnote_sections
from engine.qoe_engine import compute_reported_ebitda, screen_rule_based_adjustments, build_ebitda_bridge
from ai.qoe_ai import identify_footnote_red_flags, generate_qoe_memo

st.set_page_config(page_title="QoE Intelligence", layout="wide", page_icon="📊")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- REPORT HEADER ----------
st.markdown("""
<div class="report-header">
    <h1>QoE Intelligence</h1>
    <div class="subtitle">AI-Augmented Quality of Earnings &amp; Financial Due Diligence</div>
    <div class="confidential">Draft for Internal Discussion Purposes Only — Not Investment Advice</div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR: INPUTS ----------
st.sidebar.markdown("### Engagement Setup")
ticker = st.sidebar.text_input("Company ticker (NSE, e.g. TATASTEEL.NS)", value="")
uploaded_pdf = st.sidebar.file_uploader("Upload Annual Report (PDF, optional)", type=["pdf"])
wc_threshold = st.sidebar.slider("Working capital swing threshold (%)", 10, 50, 25)
run = st.sidebar.button("Run QoE Analysis")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Ticker pulls reported financials automatically. Uploading the annual report "
    "enables footnote-level red flag detection — the qualitative layer a "
    "ratio screen alone cannot see."
)

if not run:
    st.info("Enter a ticker in the sidebar and click **Run QoE Analysis** to generate "
            "the EBITDA normalization bridge and AI-drafted due diligence memo.")
    st.stop()

if not ticker:
    st.error("Enter a company ticker to proceed.")
    st.stop()

# ---------- STEP 1: FETCH DATA ----------
with st.spinner(f"Pulling reported financials for {ticker}..."):
    try:
        data = fetch_reported_financials(ticker)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

company_name = data["company_name"]
st.markdown(f'<div class="exhibit-label">Exhibit 1 — Reported Financial Overview: {company_name}</div>',
            unsafe_allow_html=True)
st.dataframe(data["income_statement"].head(3), use_container_width=True)

# ---------- STEP 2: RULE-BASED SCREEN ----------
try:
    reported_ebitda = compute_reported_ebitda(data["income_statement"]).iloc[0]
except ValueError as e:
    st.error(str(e))
    st.stop()

adjustments = screen_rule_based_adjustments(
    data["income_statement"], data["balance_sheet"],
    working_capital_swing_threshold_pct=wc_threshold
)
bridge = build_ebitda_bridge(reported_ebitda, adjustments)

# ---------- STEP 3: FOOTNOTE AI SCREEN (if PDF uploaded) ----------
footnote_flags = []
if uploaded_pdf is not None:
    with st.spinner("Extracting and screening annual report footnotes..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_pdf.read())
            tmp_path = tmp.name
        full_text = extract_pdf_text(tmp_path)
        relevant_text = find_relevant_footnote_sections(full_text)
        try:
            footnote_flags = identify_footnote_red_flags(relevant_text, company_name)
        except RuntimeError as e:
            st.warning(f"AI footnote screen skipped: {e}")

# ---------- EXHIBIT 2: EBITDA BRIDGE ----------
st.markdown('<div class="exhibit-label">Exhibit 2 — EBITDA Normalization Bridge</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="metric-card"><div class="metric-label">Reported EBITDA</div>'
            f'<div class="metric-value">{bridge["reported_ebitda"]:,.0f}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-card"><div class="metric-label">Normalized EBITDA</div>'
            f'<div class="metric-value">{bridge["normalized_ebitda"]:,.0f}</div></div>', unsafe_allow_html=True)
adj_pct = bridge["adjustment_pct_of_reported"]
c3.markdown(f'<div class="metric-card"><div class="metric-label">Total Adjustment</div>'
            f'<div class="metric-value">{adj_pct:,.1f}%</div></div>' if adj_pct is not None else "",
            unsafe_allow_html=True)

fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute"] + ["relative"] * (len(bridge["bridge_steps"]) - 2) + ["total"],
    x=[s["label"] for s in bridge["bridge_steps"]],
    y=[s["value"] for s in bridge["bridge_steps"]],
    connector={"line": {"color": "#D1D5DB"}},
    decreasing={"marker": {"color": "#C0392B"}},
    increasing={"marker": {"color": "#7F8C9A"}},
    totals={"marker": {"color": "#1A2332"}},
))
fig.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1A2332"),
    margin=dict(t=20, b=20),
    height=420,
)
st.plotly_chart(fig, use_container_width=True)

# ---------- EXHIBIT 3: ADJUSTMENT DETAIL ----------
st.markdown('<div class="exhibit-label">Exhibit 3 — Adjustment Detail</div>', unsafe_allow_html=True)
if bridge["auto_adjustments"]:
    df_adj = pd.DataFrame([{
        "Adjustment": a.label, "Amount": f"{a.amount:,.0f}", "Rationale": a.rationale
    } for a in bridge["auto_adjustments"]])
    st.table(df_adj)
else:
    st.caption("No rule-based adjustments identified from reported financials.")

if bridge["flagged_for_review"]:
    st.markdown("**Flagged for further review (not auto-adjusted into EBITDA):**")
    for a in bridge["flagged_for_review"]:
        st.markdown(f'<div class="risk-flag medium"><span class="flag-severity">Review</span>'
                    f'<span class="flag-title">{a.label}</span><br>{a.rationale}</div>',
                    unsafe_allow_html=True)

# ---------- EXHIBIT 4: FOOTNOTE RED FLAGS (AI) ----------
if footnote_flags:
    st.markdown('<div class="exhibit-label">Exhibit 4 — Footnote-Level Red Flags (AI-Identified)</div>',
                unsafe_allow_html=True)
    for f in footnote_flags:
        sev = f.get("severity", "low")
        st.markdown(f'<div class="risk-flag {sev}"><span class="flag-severity">{sev}</span>'
                    f'<span class="flag-title">{f.get("flag", "")}</span><br>{f.get("detail", "")}</div>',
                    unsafe_allow_html=True)

# ---------- EXHIBIT 5: AI-DRAFTED QOE MEMO ----------
st.markdown('<div class="exhibit-label">Exhibit 5 — Quality of Earnings Memorandum</div>', unsafe_allow_html=True)
if st.button("Generate QoE Memo"):
    with st.spinner("Drafting memo from engine output..."):
        try:
            memo = generate_qoe_memo(company_name, bridge, footnote_flags)
            st.markdown(f'<div class="memo-block">{memo}</div>', unsafe_allow_html=True)
        except RuntimeError as e:
            st.error(str(e))

st.markdown("""
<div class="report-footer">
    QoE Intelligence — analysis generated from publicly reported financial data and,
    where provided, user-uploaded disclosures. This output is for illustrative and
    educational purposes and does not constitute due diligence, audit, or investment advice.
</div>
""", unsafe_allow_html=True)
