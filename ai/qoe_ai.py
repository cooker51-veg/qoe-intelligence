"""
AI layer for QoE Intelligence.
Two jobs:
1. Read pre-filtered footnote text and identify qualitative red flags a
   rule-based screen can't catch (buried disclosures, related-party language, etc.)
2. Draft the QoE memo in Big 4 TAS house style, grounded strictly on the
   engine's actual computed bridge - never inventing figures.
"""
import os
import json
import anthropic

MODEL = "claude-sonnet-4-6"


def _client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set. Add it as an environment "
                            "variable or Streamlit secret.")
    return anthropic.Anthropic(api_key=api_key)


def identify_footnote_red_flags(footnote_text: str, company_name: str) -> list:
    """
    Sends pre-filtered footnote text to Claude and asks for structured,
    numbered red flags with a one-line rationale each - grounded only in
    what's actually in the text provided.
    """
    if not footnote_text.strip():
        return []

    client = _client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "You are a Big 4 Transaction Advisory Services associate performing "
            "financial due diligence. You will be given pre-filtered excerpts from "
            "a company's annual report footnotes. Identify specific, concrete "
            "Quality of Earnings red flags ONLY from what is stated in the text - "
            "never speculate beyond it. Respond ONLY with a JSON array, no other text, "
            "in this exact format: "
            '[{"flag": "short label", "detail": "1-2 sentence explanation citing what the note says", '
            '"severity": "high|medium|low"}]. If nothing material is found, return [].'
        ),
        messages=[{
            "role": "user",
            "content": f"Company: {company_name}\n\nFootnote excerpts:\n\n{footnote_text[:15000]}"
        }]
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [{"flag": "AI response parsing issue", "detail": raw[:300], "severity": "low"}]


def generate_qoe_memo(company_name: str, bridge: dict, footnote_flags: list) -> str:
    """Drafts the QoE narrative memo, grounded on the engine's actual bridge output."""
    client = _client()

    bridge_lines = "\n".join(
        f"  {step['label']}: {step['value']:,.0f}" for step in bridge["bridge_steps"]
    )
    review_lines = "\n".join(
        f"  - {a.label}: {a.rationale}" for a in bridge["flagged_for_review"]
    ) or "  None"
    flag_lines = "\n".join(
        f"  - [{f['severity'].upper()}] {f['flag']}: {f['detail']}" for f in footnote_flags
    ) or "  None identified from footnote review"

    data_block = (
        f"Company: {company_name}\n\n"
        f"EBITDA BRIDGE:\n{bridge_lines}\n\n"
        f"Total adjustment: {bridge['total_adjustment']:,.0f} "
        f"({bridge['adjustment_pct_of_reported']:.1f}% of reported EBITDA)\n\n"
        f"Items flagged for review (not auto-adjusted):\n{review_lines}\n\n"
        f"Footnote-identified qualitative red flags:\n{flag_lines}"
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=1400,
        system=(
            "You are a Big 4 Transaction Advisory Services associate drafting the "
            "Quality of Earnings section of a due diligence report. Use ONLY the "
            "figures and flags provided - never invent numbers. Write in terse, "
            "professional TAS house style with these sections: Executive Summary, "
            "EBITDA Normalization Bridge, Key Adjustments & Rationale, Items Requiring "
            "Further Diligence, Overall Earnings Quality Assessment. Under 500 words."
        ),
        messages=[{"role": "user", "content": f"Draft the QoE memo:\n\n{data_block}"}]
    )
    return message.content[0].text
