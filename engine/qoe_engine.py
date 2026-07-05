"""
Quality of Earnings engine: rule-based screening on reported financials to
flag candidate adjustments, plus the EBITDA bridge builder that is the
centerpiece exhibit of any real QoE report.

Pure functions, no I/O - independently testable.
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class Adjustment:
    label: str
    amount: float          # positive = add back to EBITDA, negative = deduct
    category: str          # "rule_based" or "ai_identified"
    rationale: str


def compute_reported_ebitda(income_stmt: pd.DataFrame) -> pd.Series:
    """Reported EBITDA = Operating Income + D&A (yfinance field names vary by ticker;
    this handles the common cases with fallbacks)."""
    ebitda = None
    for col_name in ["EBITDA", "Normalized EBITDA"]:
        if col_name in income_stmt.columns:
            ebitda = income_stmt[col_name]
            break

    if ebitda is None:
        op_income_col = next((c for c in ["Operating Income", "EBIT"] if c in income_stmt.columns), None)
        da_col = next((c for c in ["Depreciation And Amortization", "Reconciled Depreciation"]
                       if c in income_stmt.columns), None)
        if op_income_col and da_col:
            ebitda = income_stmt[op_income_col] + income_stmt[da_col]
        else:
            raise ValueError("Could not derive EBITDA from available fields - "
                              "check income_stmt columns for this ticker.")
    return ebitda


def screen_rule_based_adjustments(income_stmt: pd.DataFrame,
                                   balance_sheet: pd.DataFrame,
                                   working_capital_swing_threshold_pct: float = 25.0) -> list:
    """
    Flags adjustments a rule-based screen can catch from headline numbers alone:
    - Unusual/exceptional items line (if disclosed as a separate line)
    - Large YoY working capital swings (receivables/payables/inventory)
    - Large forex gain/loss lines
    """
    adjustments = []

    for col in ["Unusual Items", "Special Income Charges", "Exceptional Items"]:
        if col in income_stmt.columns:
            val = income_stmt[col].iloc[0]
            if pd.notna(val) and abs(val) > 0:
                adjustments.append(Adjustment(
                    label=f"Exceptional/unusual item ({col})",
                    amount=-val,
                    category="rule_based",
                    rationale=f"Reported {col} of {val:,.0f} in most recent period - "
                              f"reversed out as non-recurring for normalized EBITDA."
                ))

    wc_lines = ["Receivables", "Inventory", "Accounts Payable", "Payables"]
    for line in wc_lines:
        matching_cols = [c for c in balance_sheet.columns if line.lower() in c.lower()]
        for col in matching_cols:
            series = balance_sheet[col].dropna()
            if len(series) >= 2:
                yoy_pct = (series.iloc[0] - series.iloc[1]) / abs(series.iloc[1]) * 100 if series.iloc[1] != 0 else 0
                if abs(yoy_pct) > working_capital_swing_threshold_pct:
                    adjustments.append(Adjustment(
                        label=f"Unusual working capital swing - {col}",
                        amount=0.0,
                        category="rule_based",
                        rationale=f"{col} moved {yoy_pct:.1f}% YoY, exceeding the "
                                  f"{working_capital_swing_threshold_pct}% threshold - "
                                  f"may indicate channel stuffing, factoring, or payment timing shifts."
                    ))

    for col in ["Other Non Operating Income Expenses", "Net Non Operating Interest Income Expense"]:
        if col in income_stmt.columns:
            series = income_stmt[col].dropna()
            if len(series) >= 2 and series.iloc[1] != 0:
                yoy_pct = (series.iloc[0] - series.iloc[1]) / abs(series.iloc[1]) * 100
                if abs(yoy_pct) > 50:
                    adjustments.append(Adjustment(
                        label=f"Volatile non-operating item - {col}",
                        amount=-series.iloc[0],
                        category="rule_based",
                        rationale=f"{col} swung {yoy_pct:.1f}% YoY - flagged as non-core "
                                  f"and reversed out of normalized EBITDA."
                    ))

    return adjustments


def build_ebitda_bridge(reported_ebitda: float, adjustments: list) -> dict:
    """Builds the reported -> normalized EBITDA bridge, the centerpiece QoE exhibit."""
    auto_adjustments = [a for a in adjustments if a.amount != 0]
    review_only = [a for a in adjustments if a.amount == 0]

    total_adjustment = sum(a.amount for a in auto_adjustments)
    normalized_ebitda = reported_ebitda + total_adjustment

    bridge_steps = [{"label": "Reported EBITDA", "value": reported_ebitda}]
    running_total = reported_ebitda
    for adj in auto_adjustments:
        running_total += adj.amount
        bridge_steps.append({"label": adj.label, "value": adj.amount})
    bridge_steps.append({"label": "Normalized EBITDA", "value": normalized_ebitda})

    return {
        "reported_ebitda": reported_ebitda,
        "normalized_ebitda": normalized_ebitda,
        "total_adjustment": total_adjustment,
        "adjustment_pct_of_reported": (total_adjustment / reported_ebitda * 100) if reported_ebitda else None,
        "bridge_steps": bridge_steps,
        "auto_adjustments": auto_adjustments,
        "flagged_for_review": review_only,
    }


def plain_english_conclusion(bridge: dict) -> str:
    """
    A simple, jargon-free summary of what the analysis found - deterministic,
    not AI-generated, so it's always consistent and instantly available.
    """
    pct = bridge["adjustment_pct_of_reported"]
    if pct is None:
        return "Not enough data was available to draw a conclusion."

    abs_pct = abs(pct)
    if abs_pct < 5:
        quality = "look strong — reported profit closely matches the company's real, repeatable performance."
    elif abs_pct < 15:
        quality = "look reasonably solid, though a moderate slice of reported profit came from one-off items rather than the core business."
    else:
        quality = "deserve a closer look — a significant portion of reported profit came from one-time or unusual items, not day-to-day operations."

    return (
        f"In simple terms: this company reported EBITDA of {bridge['reported_ebitda']:,.0f}. "
        f"After removing one-off and unusual items, the real, repeatable EBITDA is "
        f"{bridge['normalized_ebitda']:,.0f} — a {pct:.1f}% adjustment. "
        f"This company's earnings {quality}"
    )
