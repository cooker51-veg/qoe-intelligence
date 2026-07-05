"""
Artha — AI-Powered Earnings Diligence
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
from engine.qoe_engine import (compute_reported_ebitda, screen_rule_based_adjustments,
                                 build_ebitda_bridge, plain_english_conclusion)
from ai.qoe_ai import identify_footnote_red_flags, generate_qoe_memo
from export.pdf_export import build_pdf_report

st.set_page_config(page_title="Artha", layout="wide", page_icon="📊",
                    initial_sidebar_state="expanded")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="report-header">
    <h1>Artha</h1>
    <div class="subtitle">AI-powered earnings diligence and normalized EBITDA analysis</div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR: INPUTS ----------
st.sidebar.markdown("### Engagement Setup")
ticker = st.sidebar.text_input("Company ticker (NSE, e.g. TATASTEEL.NS)", value="")
uploaded_pdf = st.sidebar.file_uploader("Upload Annual Report (PDF, optional)", type=["pdf"])
wc_threshold = st.sidebar.slider("Working capital swing threshold (%)", 10, 50, 25)
run = st.sidebar.button("Run QoE Analysis")

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
conclusion = plain_english_conclusion(bridge)

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

# ---------- THE BOTTOM LINE (plain-English conclusion) ----------
st.markdown('<div class="exhibit-label">The Bottom Line</div>', unsafe_allow_html=True)
st.markdown(f'<div class="conclusion-block">{conclusion}</div>', unsafe_allow_html=True)

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
    connector={"line": {"color": "#232E42"}},
    decreasing={"marker": {"color": "#D45A5A"}},
    increasing={"marker": {"color": "#6B7C93"}},
    totals={"marker": {"color": "#C9A227"}},
))
fig.update_layout(
    showlegend=False,
    plot_bgcolor="#161F30",
    paper_bgcolor="#161F30",
    font=dict(family="Inter, sans-serif", color="#EDEFF2"),
    xaxis=dict(gridcolor="#232E42", color="#EDEFF2"),
    yaxis=dict(gridcolor="#232E42", color="#EDEFF2"),
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

if "memo_text" not in st.session_state:
    st.session_state.memo_text = None

if st.button("Generate QoE Memo"):
    with st.spinner("Drafting memo from engine output..."):
        try:
            st.session_state.memo_text = generate_qoe_memo(company_name, bridge, footnote_flags)
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.memo_text:
    st.markdown(f'<div class="memo-block">{st.session_state.memo_text}</div>', unsafe_allow_html=True)

    pdf_bytes = build_pdf_report(company_name, bridge, conclusion, st.session_state.memo_text)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"Artha_QoE_{company_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
    )

st.markdown("""
<div class="report-footer">
    Artha — analysis generated from publicly reported financial data and,
    where provided, user-uploaded disclosures. For illustrative purposes only;
    not investment or audit advice.
</div>
""", unsafe_allow_html=True)
