"""STEP 7 - Streamlit dashboard (Power BI Executive Layout + ₹ KPIs).  Run:  streamlit run app.py"""
import datetime as dt
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.kpis import summarize, overall, fmt_inr
from src.insights import generate_insights
from src.report import build_html_report

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Marketing Performance Dashboard", page_icon="📊", layout="wide")

CHANNEL_COLORS = {
    "Google Ads": "#4b2bd6",
    "Email":      "#10b981",
    "Instagram":  "#f59e0b",
    "LinkedIn":   "#0ea5e9",
    "YouTube":    "#ef4444",
    "Facebook":   "#8b5cf6",
}

st.markdown("""
<style>
[data-testid="stMetric"] {
    background: rgba(128, 128, 128, 0.06);
    border: 1px solid rgba(128, 128, 128, 0.18);
    border-radius: 12px;
    padding: 14px 16px;
}
[data-testid="stMetricLabel"] {
    font-size: 0.80rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    opacity: 0.8;
}
[data-testid="stMetricValue"] {
    font-variant-numeric: tabular-nums;
}
.section-card-title {
    font-size: 1.02rem;
    font-weight: 600;
    margin-bottom: 0.15rem;
}
</style>
""", unsafe_allow_html=True)


def _style_fig(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        height=height,
        margin=dict(l=16, r=24, t=44 if title else 20, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.16)", zerolinecolor="rgba(128,128,128,0.25)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.16)", zerolinecolor="rgba(128,128,128,0.25)")
    return fig


# ------------------------------------------------------------------ data
@st.cache_data
def load_data() -> pd.DataFrame:
    db, csv = ROOT / "data" / "marketing.db", ROOT / "data" / "clean_marketing_data.csv"
    if db.exists():
        with sqlite3.connect(db) as conn:
            df = pd.read_sql("SELECT * FROM marketing", conn, parse_dates=["date", "month"])
    else:
        df = pd.read_csv(csv, parse_dates=["date", "month"])
    return df


df_all = load_data()

# ------------------------------------------------------------------ sidebar filters
st.sidebar.title("🔎 Filters")
min_d, max_d = df_all["date"].min().date(), df_all["date"].max().date()
if "date_range" not in st.session_state:
    st.session_state["date_range"] = (min_d, max_d)


PERIODS = {
    "Full Year": (min_d, max_d),
    "Q1": (max(min_d, dt.date(max_d.year, 1, 1)), min(max_d, dt.date(max_d.year, 3, 31))),
    "Q2": (max(min_d, dt.date(max_d.year, 4, 1)), min(max_d, dt.date(max_d.year, 6, 30))),
    "Q3": (max(min_d, dt.date(max_d.year, 7, 1)), min(max_d, dt.date(max_d.year, 9, 30))),
    "Q4": (max(min_d, dt.date(max_d.year, 10, 1)), min(max_d, dt.date(max_d.year, 12, 31))),
}


def _apply_period_pill():
    choice = st.session_state.get("period_pill") or "Full Year"
    st.session_state["date_range"] = PERIODS.get(choice, (min_d, max_d))


st.sidebar.pills(
    "Quick period",
    list(PERIODS.keys()),
    default="Full Year",
    required=True,
    key="period_pill",
    on_change=_apply_period_pill,
)

date_range = st.sidebar.date_input("Date range", key="date_range", min_value=min_d, max_value=max_d)
if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Select both a start and an end date.")
    st.stop()

compact_currency = st.sidebar.radio(
    "Currency format",
    ["Full (₹9,30,551)", "Compact (₹9.31L)"],
    horizontal=True,
) == "Compact (₹9.31L)"


def money(v, decimals: int = 0) -> str:
    return fmt_inr(v, decimals=decimals, compact=compact_currency)


channels = st.sidebar.multiselect("Channels", sorted(df_all["channel"].unique()),
                                  default=sorted(df_all["channel"].unique()))
camp_options = sorted(df_all[df_all["channel"].isin(channels)]["campaign"].unique())
campaigns = st.sidebar.multiselect("Campaigns", camp_options, default=camp_options)

start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df = df_all[(df_all["date"].between(start, end)) & df_all["channel"].isin(channels)
            & df_all["campaign"].isin(campaigns)]

# previous period of same length (for the delta arrows)
span = (end - start).days + 1
prev = df_all[(df_all["date"].between(start - pd.Timedelta(days=span), start - pd.Timedelta(days=1)))
              & df_all["channel"].isin(channels) & df_all["campaign"].isin(campaigns)]

st.title("📊 Marketing Performance Dashboard")
st.caption(f"{len(df):,} records  |  {start:%d %b %Y} to {end:%d %b %Y}  |  {df['channel'].nunique()} channels  |  {df['campaign'].nunique()} campaigns")
if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

t = overall(df)
p = overall(prev) if not prev.empty else None


def delta(key):
    if p is None or not p.get(key):
        return None
    return f"{(t[key] - p[key]) / abs(p[key]) * 100:+.1f}%"


tab_exec, tab_ch, tab_camp, tab_trend, tab_ins, tab_rep = st.tabs(
    ["Executive Overview", "Channels", "Campaigns", "Engagement Trends", "Insights", "Reports"])

# ------------------------------------------------------------------ Executive Overview (Power BI Layout)
with tab_exec:
    # Top 4 Core Power BI KPIs
    k = st.columns(4)
    k[0].metric("Total Revenue (₹)", money(t["revenue"]), delta("revenue"))
    k[1].metric("Total Ad Spend (₹)", money(t["spend"]), delta("spend"), delta_color="inverse")
    k[2].metric("Average CTR", f"{t['ctr']:.2%}", delta("ctr"))
    k[3].metric("Conversions", f"{t['conversions']:,.0f}", delta("conversions"))

    # Secondary Efficiency Strip
    s = st.columns(5)
    s[0].metric("Net Profit", money(t["profit"]), delta("profit"))
    s[1].metric("ROI %", f"{t['roi_pct']:.0f}%", delta("roi_pct"))
    s[2].metric("ROAS", f"{t['roas']:.2f}x", delta("roas"))
    s[3].metric("Conversion Rate", f"{t['cvr']:.2%}", delta("cvr"))
    s[4].metric("Cost / Acquisition", fmt_inr(t["cpa"], 2), delta("cpa"), delta_color="inverse")
    st.caption("Arrows compare against the immediately preceding period of equal length.")

    ch = summarize(df, "channel").sort_values("revenue", ascending=False)
    m = summarize(df, "month").sort_values("month")
    camp = summarize(df, ["campaign", "channel"]).sort_values("revenue", ascending=False)

    # Row 1: 1. Revenue by Marketing Channel + 3. Monthly Revenue Trends
    col_l, col_r = st.columns([5, 7], gap="medium")
    with col_l:
        st.markdown('<div class="section-card-title">1. Revenue by Marketing Channel</div>', unsafe_allow_html=True)
        rev_view = st.radio("View", ["Bar Chart", "Donut Share"], horizontal=True, key="exec_rev_view", label_visibility="collapsed")
        if rev_view == "Bar Chart":
            ch_asc = ch.sort_values("revenue", ascending=True).copy()
            tot_rev = ch_asc["revenue"].sum() or 1
            ch_asc["lbl"] = ch_asc["revenue"].map(lambda v: f"{money(v)} ({v / tot_rev:.1%})")
            fig1 = px.bar(
                ch_asc, x="revenue", y="channel", orientation="h",
                color="channel", color_discrete_map=CHANNEL_COLORS, text="lbl",
            )
            fig1.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
            fig1.update_xaxes(range=[0, (ch_asc["revenue"].max() or 1) * 1.28], tickprefix="₹", title="")
            fig1.update_yaxes(title="")
            st.plotly_chart(_style_fig(fig1, height=340), width="stretch")
        else:
            fig1 = px.pie(
                ch, names="channel", values="revenue", hole=0.52,
                color="channel", color_discrete_map=CHANNEL_COLORS,
            )
            fig1.update_traces(textinfo="percent+label", textposition="inside")
            fig1.update_layout(showlegend=False)
            st.plotly_chart(_style_fig(fig1, height=340), width="stretch")

    with col_r:
        st.markdown('<div class="section-card-title">3. Monthly Revenue Trends</div>', unsafe_allow_html=True)
        show_roi = st.checkbox("Overlay ROI % trend", value=True, key="exec_roi_overlay")
        fig3 = go.Figure()
        fig3.add_bar(x=m["month"], y=m["spend"], name="Ad Spend (₹)", marker_color="#a78bfa", opacity=0.75)
        fig3.add_scatter(
            x=m["month"], y=m["revenue"], name="Revenue (₹)",
            mode="lines+markers", line=dict(color="#4b2bd6", width=3),
            fill="tozeroy", fillcolor="rgba(75, 43, 214, 0.12)",
        )
        if show_roi:
            fig3.add_scatter(
                x=m["month"], y=m["roi_pct"], name="ROI %", yaxis="y2",
                mode="lines+markers", line=dict(color="#f59e0b", width=2.5, dash="dot"),
            )
        fig3_layout = dict(
            barmode="overlay",
            hovermode="x unified",
            yaxis=dict(title="Amount (₹)", tickprefix="₹"),
        )
        if show_roi:
            fig3_layout["yaxis2"] = dict(overlaying="y", side="right", title="ROI %", ticksuffix="%", showgrid=False)
        fig3.update_layout(**fig3_layout)
        st.plotly_chart(_style_fig(fig3, height=340), width="stretch")

    # Row 2: 2. Campaign Performance Comparison + 4. Channel-wise Conversion Analysis
    col_l2, col_r2 = st.columns([7, 5], gap="medium")
    with col_l2:
        st.markdown('<div class="section-card-title">2. Campaign Performance Comparison</div>', unsafe_allow_html=True)
        sort_by = st.selectbox(
            "Sort campaigns by",
            ["revenue", "spend", "conversions", "roas", "ctr"],
            format_func=lambda x: {"revenue": "Sort by: Revenue (₹)", "spend": "Sort by: Ad Spend (₹)",
                                   "conversions": "Sort by: Conversions", "roas": "Sort by: ROAS", "ctr": "Sort by: CTR %"}[x],
            label_visibility="collapsed",
            key="exec_camp_sort",
        )
        camp_sorted = camp.sort_values(sort_by, ascending=True)
        if sort_by in ("revenue", "spend"):
            fig2 = go.Figure()
            fig2.add_bar(y=camp_sorted["campaign"], x=camp_sorted["spend"], name="Ad Spend (₹)",
                         orientation="h", marker_color="rgba(148, 163, 184, 0.6)")
            fig2.add_bar(y=camp_sorted["campaign"], x=camp_sorted["revenue"], name="Revenue (₹)",
                         orientation="h", marker_color="#4b2bd6")
            fig2.update_layout(barmode="group")
            fig2.update_xaxes(tickprefix="₹", title="")
        else:
            fmt_col = (lambda v: f"{v:,.0f}") if sort_by == "conversions" else (
                (lambda v: f"{v:.2f}x") if sort_by == "roas" else (lambda v: f"{v:.2%}")
            )
            camp_sorted = camp_sorted.copy()
            camp_sorted["lbl"] = camp_sorted[sort_by].map(fmt_col)
            fig2 = px.bar(
                camp_sorted, x=sort_by, y="campaign", color="channel",
                orientation="h", color_discrete_map=CHANNEL_COLORS, text="lbl",
            )
            fig2.update_traces(textposition="outside", cliponaxis=False)
            fig2.update_xaxes(range=[0, (camp_sorted[sort_by].max() or 1) * 1.24], title="")
        fig2.update_yaxes(title="")
        st.plotly_chart(_style_fig(fig2, height=400), width="stretch")

    with col_r2:
        st.markdown('<div class="section-card-title">4. Channel-wise Conversion Analysis</div>', unsafe_allow_html=True)
        conv_view = st.radio(
            "Conversion view",
            ["Channel CVR % & Volume", "Sales Funnel"],
            horizontal=True,
            key="exec_conv_view",
            label_visibility="collapsed",
        )
        if conv_view == "Channel CVR % & Volume":
            ch_conv = ch.sort_values("conversions", ascending=True).copy()
            ch_conv["lbl"] = ch_conv.apply(
                lambda r: f"{r['conversions']:,.0f} ({r['cvr']:.2%} CVR · {fmt_inr(r['cpa'], 2)} CPA)", axis=1
            )
            fig4 = px.bar(
                ch_conv, x="conversions", y="channel", orientation="h",
                color="channel", color_discrete_map=CHANNEL_COLORS, text="lbl",
            )
            fig4.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
            fig4.update_xaxes(range=[0, (ch_conv["conversions"].max() or 1) * 1.48], title="Conversions")
            fig4.update_yaxes(title="")
            st.plotly_chart(_style_fig(fig4, height=400), width="stretch")
        else:
            fig4 = go.Figure(go.Funnel(
                y=["Impressions", "Clicks", "Website Sessions", "Conversions"],
                x=[t["impressions"], t["clicks"], t["website_sessions"], t["conversions"]],
                textinfo="value+percent initial",
                marker=dict(color=["#6366f1", "#4b2bd6", "#0ea5e9", "#10b981"]),
            ))
            st.plotly_chart(_style_fig(fig4, height=400), width="stretch")

    # Row 3: 5. ROI Comparison + Channel Scorecard
    col_l3, col_r3 = st.columns([7, 5], gap="medium")
    with col_l3:
        st.markdown('<div class="section-card-title">5. ROI Comparison</div>', unsafe_allow_html=True)
        roi_scope = st.radio("Group ROI by", ["By Channel", "By Campaign"], horizontal=True, key="exec_roi_scope", label_visibility="collapsed")
        if roi_scope == "By Channel":
            roi_df = ch.sort_values("roi_pct", ascending=True).copy()
            y_col = "channel"
        else:
            roi_df = camp.sort_values("roi_pct", ascending=True).copy()
            y_col = "campaign"
        roi_df["lbl"] = roi_df.apply(lambda r: f"{r['roi_pct']:.0f}% ({r['roas']:.2f}x)", axis=1)
        roi_df["tier"] = roi_df["roi_pct"].map(
            lambda v: "High (>=150%)" if v >= 150 else ("Target (75-149%)" if v >= 75 else "Low (<75%)")
        )
        fig5 = px.bar(
            roi_df, x="roi_pct", y=y_col, orientation="h", color="tier", text="lbl",
            color_discrete_map={"High (>=150%)": "#10b981", "Target (75-149%)": "#4b2bd6", "Low (<75%)": "#f59e0b"},
        )
        fig5.add_vline(x=100, line_dash="dash", line_color="rgba(128,128,128,0.65)", annotation_text="100% Target")
        fig5.add_vline(x=0, line_dash="dot", line_color="#ef4444")
        fig5.update_traces(textposition="outside", cliponaxis=False)
        min_roi = min(0, float(roi_df["roi_pct"].min()) * 1.15)
        max_roi = max(105, float(roi_df["roi_pct"].max()) * 1.24)
        fig5.update_xaxes(range=[min_roi, max_roi], title="ROI %", ticksuffix="%")
        fig5.update_yaxes(title="")
        st.plotly_chart(_style_fig(fig5, height=370), width="stretch")

    with col_r3:
        st.markdown('<div class="section-card-title">Channel Scorecard</div>', unsafe_allow_html=True)
        st.dataframe(
            ch[["channel", "revenue", "spend", "ctr", "cvr", "cpa", "roi_pct"]].style.format({
                "revenue": lambda v: money(v, 0),
                "spend": lambda v: money(v, 0),
                "ctr": "{:.2%}",
                "cvr": "{:.2%}",
                "cpa": lambda v: fmt_inr(v, 2),
                "roi_pct": "{:.0f}%",
            }),
            width="stretch",
            hide_index=True,
            height=370,
        )

# ------------------------------------------------------------------ Channels
with tab_ch:
    ch = summarize(df, "channel").sort_values("revenue", ascending=False)
    a, b = st.columns(2)
    a.plotly_chart(_style_fig(px.bar(ch, x="channel", y="roi_pct", color="channel",
                                     color_discrete_map=CHANNEL_COLORS, text_auto=".0f",
                                     title="ROI % by Channel")), width="stretch")
    b.plotly_chart(_style_fig(px.bar(ch, x="channel", y="cvr", color="channel",
                                     color_discrete_map=CHANNEL_COLORS, text_auto=".2%",
                                     title="Conversion Rate by Channel")), width="stretch")
    a, b = st.columns(2)
    a.plotly_chart(_style_fig(px.pie(ch, names="channel", values="revenue", hole=0.45,
                                     color="channel", color_discrete_map=CHANNEL_COLORS,
                                     title="Revenue Share by Channel")), width="stretch")
    b.plotly_chart(_style_fig(px.scatter(ch, x="spend", y="revenue", size="conversions",
                                         color="channel", color_discrete_map=CHANNEL_COLORS,
                                         title="Spend vs Revenue (bubble = conversions)")), width="stretch")
    st.subheader("Channel scorecard")
    st.dataframe(ch[["channel", "spend", "revenue", "profit", "roi_pct", "roas", "ctr", "cvr", "cpa",
                     "engagement_rate"]].style.format({
        "spend": lambda v: fmt_inr(v, 0),
        "revenue": lambda v: fmt_inr(v, 0),
        "profit": lambda v: fmt_inr(v, 0),
        "roi_pct": "{:.0f}%",
        "roas": "{:.2f}x",
        "ctr": "{:.2%}",
        "cvr": "{:.2%}",
        "cpa": lambda v: fmt_inr(v, 2),
        "engagement_rate": "{:.2%}",
    }), width="stretch", hide_index=True)

# ------------------------------------------------------------------ Campaigns
with tab_camp:
    camp = summarize(df, ["campaign", "channel"]).sort_values("revenue", ascending=False)
    top_n = st.slider("Show top N campaigns", 1, len(camp), min(14, len(camp))) if len(camp) > 3 else len(camp)
    st.plotly_chart(_style_fig(px.bar(camp.head(top_n).sort_values("revenue"), x="revenue", y="campaign",
                                      color="channel", color_discrete_map=CHANNEL_COLORS, orientation="h",
                                      title=f"Top {top_n} Campaigns by Revenue (₹)"), height=420),
                    width="stretch")
    st.plotly_chart(_style_fig(px.bar(camp.sort_values("roas"), x="roas", y="campaign",
                                      color="channel", color_discrete_map=CHANNEL_COLORS, orientation="h",
                                      title="ROAS by Campaign (1.0 = break-even)")
                               .add_vline(x=1, line_dash="dash", line_color="red"), height=420),
                    width="stretch")
    st.dataframe(camp[["campaign", "channel", "spend", "revenue", "profit", "roi_pct", "roas", "ctr", "cvr",
                       "cpa"]].style.format({
        "spend": lambda v: fmt_inr(v, 0),
        "revenue": lambda v: fmt_inr(v, 0),
        "profit": lambda v: fmt_inr(v, 0),
        "roi_pct": "{:.0f}%",
        "roas": "{:.2f}x",
        "ctr": "{:.2%}",
        "cvr": "{:.2%}",
        "cpa": lambda v: fmt_inr(v, 2),
    }), width="stretch", hide_index=True)

# ------------------------------------------------------------------ Engagement trends
with tab_trend:
    grain = st.radio("Group by", ["Week", "Month"], horizontal=True)
    d = df.copy()
    d["period"] = d["date"].dt.to_period("W-SUN" if grain == "Week" else "M").dt.start_time
    tr = summarize(d, "period").sort_values("period")
    st.plotly_chart(_style_fig(px.line(tr, x="period", y="engagement_rate", markers=True,
                                       title=f"Engagement Rate per {grain}")), width="stretch")
    a, b = st.columns(2)
    a.plotly_chart(_style_fig(px.line(tr, x="period", y="ctr", markers=True, title="Click-Through Rate")),
                   width="stretch")
    b.plotly_chart(_style_fig(px.line(tr, x="period", y="cvr", markers=True, title="Conversion Rate")),
                   width="stretch")
    st.plotly_chart(_style_fig(px.area(tr, x="period", y="website_sessions", title="Website Sessions")),
                    width="stretch")
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = summarize(df, ["channel", "weekday"]).pivot(index="channel", columns="weekday", values="cvr")
    heat = heat.reindex(columns=[x for x in order if x in heat.columns])
    st.plotly_chart(_style_fig(px.imshow(heat, text_auto=".1%", aspect="auto", color_continuous_scale="Purples",
                                         title="Conversion Rate: Channel x Weekday")), width="stretch")

# ------------------------------------------------------------------ Insights
with tab_ins:
    st.subheader("💡 Automated business insights")
    for line in generate_insights(df):
        st.markdown(f"- {line}")

# ------------------------------------------------------------------ Reports
with tab_rep:
    st.subheader("📄 Generate reports for the current filters")
    kind = st.selectbox("Report type", ["summary", "campaign", "monthly"],
                        format_func=lambda x: {"summary": "Marketing Summary", "campaign": "Campaign Report",
                                               "monthly": "Monthly Analytics Report"}[x])
    html = build_html_report(df, kind)
    st.download_button("⬇️ Download report (HTML)", html, file_name=f"{kind}_report.html", mime="text/html")
    st.download_button("⬇️ Download filtered data (CSV)", df.to_csv(index=False),
                       file_name="filtered_marketing_data.csv", mime="text/csv")
    st.caption("Open the downloaded HTML file in any browser, or print it to PDF (Ctrl+P).")
