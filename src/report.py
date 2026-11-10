"""STEP 6 - Automatic HTML reports (campaign / summary / monthly)."""
import pandas as pd
from datetime import datetime
from src.kpis import summarize, overall, fmt_inr
from src.insights import generate_insights

CSS = """<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:40px;color:#1e293b;background:#ffffff}
h1{color:#4b2bd6;margin-bottom:4px}h2{border-bottom:2px solid #4b2bd6;padding-bottom:4px;margin-top:32px}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#4b2bd6;color:#fff;padding:8px 6px;text-align:right}th:first-child,td:first-child{text-align:left}
td{padding:6px;border-bottom:1px solid #e2e8f0;text-align:right}
.kpi{display:inline-block;background:#f5f3ff;border:1px solid #ddd6fe;border-radius:10px;padding:12px 18px;margin:6px;min-width:140px}
.kpi b{display:block;font-size:20px;color:#4b2bd6;margin-top:4px}
</style>"""

FMT = {
    "impressions": "{:,.0f}",
    "clicks": "{:,.0f}",
    "conversions": "{:,.0f}",
    "spend": lambda v: fmt_inr(v, 0),
    "revenue": lambda v: fmt_inr(v, 0),
    "ctr": "{:.2%}",
    "cvr": "{:.2%}",
    "cpa": lambda v: fmt_inr(v, 2),
    "roas": "{:.2f}x",
    "roi_pct": "{:.0f}%",
    "engagement_rate": "{:.2%}",
    "profit": lambda v: fmt_inr(v, 0),
}
SHOW = ["impressions", "clicks", "conversions", "spend", "revenue", "profit",
        "ctr", "cvr", "cpa", "roas", "roi_pct", "engagement_rate"]


def _table(df, key):
    t = df[[key] + SHOW].copy()
    if key == "month":
        t[key] = t[key].dt.strftime("%b %Y")
    return t.style.format(FMT, na_rep="-").hide(axis="index").to_html()


def build_html_report(df: pd.DataFrame, kind: str = "summary") -> str:
    t = overall(df)
    start, end = df["date"].min().date(), df["date"].max().date()
    titles = {"summary": "Marketing Summary Report", "campaign": "Campaign Performance Report",
              "monthly": "Monthly Analytics Report"}
    kpis = [
        ("Total Revenue", fmt_inr(t["revenue"])),
        ("Total Ad Spend", fmt_inr(t["spend"])),
        ("Average CTR", f"{t['ctr']:.2%}"),
        ("Conversions", f"{t['conversions']:,.0f}"),
        ("ROI", f"{t['roi_pct']:.0f}%"),
        ("ROAS", f"{t['roas']:.2f}x"),
        ("Conv. Rate", f"{t['cvr']:.2%}"),
        ("CPA", fmt_inr(t["cpa"], decimals=2)),
    ]
    html = [f"<html><head><meta charset='utf-8'>{CSS}</head><body>",
            f"<h1>{titles.get(kind, titles['summary'])}</h1>",
            f"<p>Period: {start} to {end} &nbsp;|&nbsp; Generated: {datetime.now():%Y-%m-%d %H:%M}</p>",
            "<h2>Key Performance Indicators</h2>"]
    html += [f"<div class='kpi'>{k}<b>{v}</b></div>" for k, v in kpis]
    if kind in ("summary", "monthly"):
        html += ["<h2>Monthly Performance</h2>", _table(summarize(df, "month").sort_values("month"), "month")]
    if kind in ("summary", "campaign"):
        html += ["<h2>Campaign Performance</h2>",
                 _table(summarize(df, "campaign").sort_values("revenue", ascending=False), "campaign")]
    if kind in ("summary", "monthly"):
        html += ["<h2>Channel Comparison</h2>",
                 _table(summarize(df, "channel").sort_values("revenue", ascending=False), "channel")]
    html.append("<h2>Business Insights</h2><ul>")
    html += [f"<li>{i.replace('**', '')}</li>" for i in generate_insights(df)]
    html.append("</ul></body></html>")
    return "\n".join(html)


if __name__ == "__main__":
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    data = pd.read_csv(root / "data" / "clean_marketing_data.csv", parse_dates=["date", "month"])
    for kind in ("summary", "campaign", "monthly"):
        p = root / "reports" / f"{kind}_report.html"
        p.write_text(build_html_report(data, kind), encoding="utf-8")
        print("Wrote", p)
