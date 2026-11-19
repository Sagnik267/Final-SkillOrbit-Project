"""STEP 3 - KPI formulas used everywhere (dashboard, insights, reports)."""
import numpy as np
import pandas as pd

SUM_COLS = ["impressions", "reach", "clicks", "conversions", "spend", "revenue",
            "likes", "shares", "comments", "engagement_score", "website_sessions", "new_customers"]


def _div(a, b):
    return a / b.replace(0, np.nan)


def add_ratios(d: pd.DataFrame) -> pd.DataFrame:
    """Add KPI columns to a frame that already contains summed base metrics."""
    d = d.copy()
    d["ctr"] = _div(d["clicks"], d["impressions"])            # click-through rate
    d["cvr"] = _div(d["conversions"], d["clicks"])            # conversion rate
    d["cpc"] = _div(d["spend"], d["clicks"])                  # cost per click
    d["cpa"] = _div(d["spend"], d["conversions"])             # cost per acquisition
    d["roas"] = _div(d["revenue"], d["spend"])                # return on ad spend
    d["roi_pct"] = _div(d["revenue"] - d["spend"], d["spend"]) * 100
    d["engagements"] = d["likes"] + d["shares"] + d["comments"]
    d["engagement_rate"] = _div(d["engagements"], d["impressions"])
    d["profit"] = d["revenue"] - d["spend"]
    return d


def summarize(df: pd.DataFrame, by) -> pd.DataFrame:
    """Aggregate by one column (or list of columns) and compute KPIs."""
    g = df.groupby(by, as_index=False)[SUM_COLS].sum()
    return add_ratios(g)


def overall(df: pd.DataFrame) -> dict:
    """Totals + KPIs for the whole (filtered) dataset as a dict."""
    total = df[SUM_COLS].sum().to_frame().T
    return add_ratios(total).iloc[0].to_dict()


def fmt_inr(value, decimals: int = 0, compact: bool = False) -> str:
    """Format a numeric value in Indian Rupees (e.g. ₹9,30,551 or ₹9.31L)."""
    if value is None or pd.isna(value):
        return "-"
    val = float(value)
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    if compact:
        if abs_val >= 1e7:
            return f"{sign}₹{abs_val / 1e7:.2f}Cr"
        if abs_val >= 1e5:
            return f"{sign}₹{abs_val / 1e5:.2f}L"
        if abs_val >= 1e3:
            return f"{sign}₹{abs_val / 1e3:.1f}K"
        return f"{sign}₹{abs_val:.{decimals}f}"

    formatted = f"{abs_val:.{decimals}f}"
    int_part, *dec_part = formatted.split(".")
    if len(int_part) > 3:
        head, tail = int_part[:-3], int_part[-3:]
        groups = []
        while len(head) > 2:
            groups.append(head[-2:])
            head = head[:-2]
        if head:
            groups.append(head)
        int_part = ",".join(reversed(groups)) + "," + tail
    suffix = f".{dec_part[0]}" if dec_part else ""
    return f"{sign}₹{int_part}{suffix}"
