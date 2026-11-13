"""STEP 7 - Streamlit dashboard (Power BI Executive Layout + ₹ KPIs + Light/Dark Mode).  Run:  streamlit run app.py"""
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

THEMES = {
    "light": {
        "bg": "#f8fafc",
        "sidebar": "#f1f5f9",
        "card": "#ffffff",
        "card_alt": "#f8fafc",
        "border": "#e2e8f0",
        "text": "#0f172a",
        "muted": "#475569",
        "nav_inactive": "#475569",
        "nav_hover": "#0f172a",
        "nav_active": "#4b2bd6",
        "accent": "#4b2bd6",
        "accent_solid": "#4b2bd6",
        "accent_soft": "rgba(75, 43, 214, 0.10)",
        "grid": "rgba(15, 23, 42, 0.10)",
        "zero": "rgba(15, 23, 42, 0.22)",
        "plotly_template": "plotly_white",
        "hover_bg": "#ffffff",
        "hover_border": "#cbd5e1",
        "spend_bar": "rgba(100, 116, 139, 0.45)",
        "target_line": "rgba(71, 85, 105, 0.65)",
        "table_hover": "#f1f5f9",
    },
    "dark": {
        "bg": "#0b1020",
        "sidebar": "#111827",
        "card": "#161f33",
        "card_alt": "#1a2540",
        "border": "#27344f",
        "text": "#f1f5f9",
        "muted": "#a3b1c6",
        "nav_inactive": "#D1D5DB",
        "nav_hover": "#F9FAFB",
        "nav_active": "#A78BFA",
        "accent": "#A78BFA",
        "accent_solid": "#6D4AFF",
        "accent_soft": "rgba(167, 139, 250, 0.16)",
        "grid": "rgba(148, 163, 184, 0.16)",
        "zero": "rgba(148, 163, 184, 0.30)",
        "plotly_template": "plotly_dark",
        "hover_bg": "#1e293b",
        "hover_border": "#334155",
        "spend_bar": "rgba(148, 163, 184, 0.45)",
        "target_line": "rgba(148, 163, 184, 0.65)",
        "table_hover": "#1e293b",
    },
}


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

# ------------------------------------------------------------------ theme + sidebar filters
try:
    sys_theme = getattr(getattr(st.context, "theme", None), "type", "light") or "light"
except Exception:
    sys_theme = "light"

st.sidebar.title("🔎 Filters")
theme_choice = st.sidebar.radio(
    "Theme mode",
    ["☀️ Light", "🌙 Dark"],
    index=1 if sys_theme == "dark" else 0,
    horizontal=True,
    key="theme_mode",
)
is_dark = theme_choice == "🌙 Dark"
PAL = THEMES["dark" if is_dark else "light"]

dark_mode_css = """
html, body, .stApp {
    color-scheme: dark;
}
[data-testid="stHeader"] button,
[data-testid="stSidebar"] button[kind="headerNoPadding"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    color: var(--pbi-nav-inactive);
    transition: color 0.2s ease;
}
[data-testid="stHeader"] button:hover,
[data-testid="stSidebar"] button[kind="headerNoPadding"]:hover,
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    color: var(--pbi-nav-hover);
}
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] span,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] em,
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
[data-testid="stAppViewContainer"] label {
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] a {
    color: var(--pbi-accent);
}
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] code {
    background-color: var(--pbi-card-alt);
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] p {
    color: var(--pbi-muted);
}
[data-testid="stAppViewContainer"] [data-testid="stRadioGroup"],
[data-testid="stAppViewContainer"] [data-testid="stRadioOption"] p,
[data-testid="stAppViewContainer"] [data-testid="stCheckbox"] p {
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stRadioOption"]:not([data-selected]) > div > div:first-child {
    background-color: var(--pbi-card);
    border-color: var(--pbi-muted);
}
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"] {
    background-color: var(--pbi-card);
    color: var(--pbi-nav-inactive);
    border-color: var(--pbi-border);
    transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"][data-hovered] {
    color: var(--pbi-nav-hover);
    border-color: var(--pbi-accent);
    background-color: var(--pbi-card-alt);
}
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"][data-selected],
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"][aria-pressed="true"] {
    background-color: var(--pbi-accent-solid);
    color: #ffffff;
    border-color: var(--pbi-accent-solid);
}
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"][data-selected] p,
[data-testid="stAppViewContainer"] [data-testid="stButtonGroup"] button[data-variant="pills"][data-selected] span {
    color: #ffffff;
}
[data-testid="stAppViewContainer"] [data-testid="stDateInput"] [data-testid="stDateInputField"],
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] > div > div {
    background-color: var(--pbi-card);
    border-color: var(--pbi-border);
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stDateInputField"] input,
[data-testid="stAppViewContainer"] [data-testid="stDateInputField"] span,
[data-testid="stAppViewContainer"] [data-testid="stDateInputField"] button,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] input,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] span,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] button,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] input,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] button {
    color: var(--pbi-text);
}
[data-testid="stAppViewContainer"] [data-testid="stMultiSelectTagsContainer"] [role="button"],
[data-testid="stAppViewContainer"] [data-baseweb="tag"] {
    background-color: var(--pbi-accent-solid);
    color: #ffffff;
}
body [data-testid="stSelectboxVirtualDropdown"],
body [data-testid="stMultiSelectDropdown"],
body [data-testid="stDateInputCalendar"],
body [data-testid="stDateInputQuickSelectPopover"],
body #stFloatingOverlayPortal [role="dialog"],
body [role="listbox"] {
    background-color: var(--pbi-card);
    color: var(--pbi-text);
    border: 1px solid var(--pbi-border);
}
body [data-testid="stSelectboxVirtualDropdown"] [role="option"],
body [data-testid="stMultiSelectDropdown"] [role="option"],
body [data-testid="stDateInputCalendar"] button,
body [data-testid="stDateInputCalendar"] span,
body [data-testid="stDateInputCalendar"] div,
body [role="listbox"] [role="option"] {
    color: var(--pbi-text);
}
body [role="option"]:hover [data-item-hl],
body [role="option"][data-hovered] [data-item-hl],
body [role="option"][data-focused] [data-item-hl],
body [role="option"]:hover {
    background-color: var(--pbi-table-hover);
    color: var(--pbi-nav-hover);
}
[data-testid="stAppViewContainer"] [data-testid="stSlider"] [data-testid="stSliderTickBar"] {
    color: var(--pbi-muted);
}
[data-testid="stAppViewContainer"] [data-testid="stSlider"] [data-testid="stSliderThumbValue"] {
    color: var(--pbi-accent);
}
[data-testid="stAppViewContainer"] [data-testid="stAlertContainer"] {
    background-color: var(--pbi-card);
    color: var(--pbi-text);
    border: 1px solid var(--pbi-border);
}
[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"],
[data-testid="stAppViewContainer"] [data-testid="stDownloadButton"] button {
    background-color: var(--pbi-card);
    color: var(--pbi-text);
    border: 1px solid var(--pbi-border);
    transition: border-color 0.2s ease, color 0.2s ease;
}
[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stDownloadButton"] button:hover {
    border-color: var(--pbi-accent);
    color: var(--pbi-nav-hover);
}
""" if is_dark else ""

st.markdown(f"""
<style>
:root {{
    --pbi-bg: {PAL['bg']};
    --pbi-sidebar: {PAL['sidebar']};
    --pbi-card: {PAL['card']};
    --pbi-card-alt: {PAL['card_alt']};
    --pbi-border: {PAL['border']};
    --pbi-text: {PAL['text']};
    --pbi-muted: {PAL['muted']};
    --pbi-nav-inactive: {PAL['nav_inactive']};
    --pbi-nav-hover: {PAL['nav_hover']};
    --pbi-nav-active: {PAL['nav_active']};
    --pbi-accent: {PAL['accent']};
    --pbi-accent-solid: {PAL['accent_solid']};
    --pbi-table-hover: {PAL['table_hover']};
}}
.stApp, [data-testid="stAppViewContainer"] {{
    background-color: var(--pbi-bg);
    color: var(--pbi-text);
}}
[data-testid="stHeader"] {{
    background-color: var(--pbi-bg);
    color: var(--pbi-text);
}}
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
    background-color: var(--pbi-sidebar);
    color: var(--pbi-text);
    border-right: 1px solid var(--pbi-border);
}}
[data-testid="stAppViewContainer"] [data-testid="stMetric"] {{
    background-color: var(--pbi-card);
    border: 1px solid var(--pbi-border);
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, {"0.25" if is_dark else "0.04"});
}}
[data-testid="stAppViewContainer"] [data-testid="stMetricLabel"],
[data-testid="stAppViewContainer"] [data-testid="stMetricLabel"] p {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--pbi-muted);
}}
[data-testid="stAppViewContainer"] [data-testid="stMetricValue"] {{
    color: var(--pbi-text);
    font-variant-numeric: tabular-nums;
}}
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [role="tablist"]::after {{
    background-color: var(--pbi-border);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"] p,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"] span {{
    color: var(--pbi-nav-inactive);
    transition: color 0.2s ease, opacity 0.2s ease;
}}
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"]:hover [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"]:hover p,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"]:hover span,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-hovered],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-hovered] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-hovered] p,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-hovered] span {{
    color: var(--pbi-nav-hover);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] span,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-selected],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-selected] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-selected] p,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-selected] span {{
    color: var(--pbi-nav-active);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] .react-aria-SelectionIndicator,
[data-testid="stAppViewContainer"] [data-testid="stTabs"] [data-testid="stTab"][data-selected] .react-aria-SelectionIndicator {{
    background-color: var(--pbi-nav-active);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollLeft"],
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollRight"] {{
    color: var(--pbi-nav-inactive);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollLeft"] {{
    background-image: linear-gradient(to left, transparent, var(--pbi-bg) 40%);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollRight"] {{
    background-image: linear-gradient(to right, transparent, var(--pbi-bg) 40%);
}}
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollLeft"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stTabsScrollRight"]:hover {{
    color: var(--pbi-nav-hover);
}}
{dark_mode_css}
.section-card-title {{
    font-size: 1.02rem;
    font-weight: 600;
    color: var(--pbi-text);
    margin-bottom: 0.2rem;
}}
.pbi-table-wrap {{
    background-color: var(--pbi-card);
    border: 1px solid var(--pbi-border);
    border-radius: 12px;
    overflow: auto;
    max-width: 100%;
}}
.pbi-table-wrap table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    font-variant-numeric: tabular-nums;
    color: var(--pbi-text);
}}
.pbi-table-wrap th {{
    position: sticky;
    top: 0;
    background-color: var(--pbi-card-alt);
    color: var(--pbi-muted);
    font-weight: 600;
    text-align: right;
    padding: 9px 10px;
    border-bottom: 1px solid var(--pbi-border);
    white-space: nowrap;
}}
.pbi-table-wrap td {{
    text-align: right;
    padding: 8px 10px;
    border-bottom: 1px solid var(--pbi-border);
    white-space: nowrap;
}}
.pbi-table-wrap th:first-child,
.pbi-table-wrap td:first-child {{
    text-align: left;
    font-weight: 500;
}}
.pbi-table-wrap tr:hover td {{
    background-color: var(--pbi-table-hover);
}}
</style>
""", unsafe_allow_html=True)


def _style_fig(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    fig.update_layout(
        template=PAL["plotly_template"],
        title=dict(text=title, font=dict(size=15, color=PAL["text"])),
        font=dict(color=PAL["text"]),
        height=height,
        margin=dict(l=16, r=24, t=44 if title else 20, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=PAL["text"]),
        ),
        hoverlabel=dict(
            bgcolor=PAL["hover_bg"],
            bordercolor=PAL["hover_border"],
            font=dict(color=PAL["text"]),
        ),
    )
    fig.update_xaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["zero"], tickfont=dict(color=PAL["muted"]), title_font=dict(color=PAL["muted"]))
    fig.update_yaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["zero"], tickfont=dict(color=PAL["muted"]), title_font=dict(color=PAL["muted"]))
    return fig


def _render_table(styler, max_height: int | None = None):
    html = styler.hide(axis="index").to_html()
    style_attr = f' style="max-height:{max_height}px;"' if max_height else ""
    st.markdown(f'<div class="pbi-table-wrap"{style_attr}>{html}</div>', unsafe_allow_html=True)


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
            fig1.update_traces(textposition="outside", cliponaxis=False, showlegend=False, textfont=dict(color=PAL["text"]))
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
            mode="lines+markers", line=dict(color=PAL["accent"], width=3),
            fill="tozeroy", fillcolor=PAL["accent_soft"],
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
            fig3_layout["yaxis2"] = dict(overlaying="y", side="right", title="ROI %", ticksuffix="%", showgrid=False, tickfont=dict(color=PAL["muted"]), title_font=dict(color=PAL["muted"]))
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
                         orientation="h", marker_color=PAL["spend_bar"])
            fig2.add_bar(y=camp_sorted["campaign"], x=camp_sorted["revenue"], name="Revenue (₹)",
                         orientation="h", marker_color=PAL["accent"])
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
            fig2.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=PAL["text"]))
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
            fig4.update_traces(textposition="outside", cliponaxis=False, showlegend=False, textfont=dict(color=PAL["text"]))
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
            color_discrete_map={"High (>=150%)": "#10b981", "Target (75-149%)": PAL["accent"], "Low (<75%)": "#f59e0b"},
        )
        fig5.add_vline(x=100, line_dash="dash", line_color=PAL["target_line"], annotation_text="100% Target", annotation_font_color=PAL["muted"])
        fig5.add_vline(x=0, line_dash="dot", line_color="#ef4444")
        fig5.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=PAL["text"]))
        min_roi = min(0, float(roi_df["roi_pct"].min()) * 1.15)
        max_roi = max(105, float(roi_df["roi_pct"].max()) * 1.24)
        fig5.update_xaxes(range=[min_roi, max_roi], title="ROI %", ticksuffix="%")
        fig5.update_yaxes(title="")
        st.plotly_chart(_style_fig(fig5, height=370), width="stretch")

    with col_r3:
        st.markdown('<div class="section-card-title">Channel Scorecard</div>', unsafe_allow_html=True)
        sc = ch[["channel", "revenue", "spend", "ctr", "cvr", "cpa", "roi_pct"]].rename(columns={
            "channel": "Channel", "revenue": "Revenue", "spend": "Spend",
            "ctr": "CTR", "cvr": "CVR", "cpa": "CPA", "roi_pct": "ROI %",
        })
        _render_table(
            sc.style.format({
                "Revenue": lambda v: money(v, 0),
                "Spend": lambda v: money(v, 0),
                "CTR": "{:.2%}",
                "CVR": "{:.2%}",
                "CPA": lambda v: fmt_inr(v, 2),
                "ROI %": "{:.0f}%",
            }),
            max_height=370,
        )

# ------------------------------------------------------------------ Channels
with tab_ch:
    ch = summarize(df, "channel").sort_values("revenue", ascending=False)
    a, b = st.columns(2)
    a.plotly_chart(_style_fig(px.bar(ch, x="channel", y="roi_pct", color="channel",
                                     color_discrete_map=CHANNEL_COLORS, text_auto=".0f",
                                     title="ROI % by Channel")), width="stretch")
    fig_ch_cvr = px.bar(ch, x="channel", y="cvr", color="channel",
                        color_discrete_map=CHANNEL_COLORS, text_auto=".2%",
                        title="Conversion Rate by Channel")
    fig_ch_cvr.update_yaxes(tickformat=".1%")
    b.plotly_chart(_style_fig(fig_ch_cvr), width="stretch")
    a, b = st.columns(2)
    a.plotly_chart(_style_fig(px.pie(ch, names="channel", values="revenue", hole=0.45,
                                     color="channel", color_discrete_map=CHANNEL_COLORS,
                                     title="Revenue Share by Channel")), width="stretch")
    fig_scat = px.scatter(ch, x="spend", y="revenue", size="conversions",
                          color="channel", color_discrete_map=CHANNEL_COLORS,
                          title="Spend vs Revenue (bubble = conversions)")
    fig_scat.update_xaxes(tickprefix="₹")
    fig_scat.update_yaxes(tickprefix="₹")
    b.plotly_chart(_style_fig(fig_scat), width="stretch")
    st.subheader("Channel scorecard")
    _render_table(ch[["channel", "spend", "revenue", "profit", "roi_pct", "roas", "ctr", "cvr", "cpa",
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
    }))

# ------------------------------------------------------------------ Campaigns
with tab_camp:
    camp = summarize(df, ["campaign", "channel"]).sort_values("revenue", ascending=False)
    top_n = st.slider("Show top N campaigns", 1, len(camp), min(14, len(camp))) if len(camp) > 3 else len(camp)
    fig_c1 = px.bar(camp.head(top_n).sort_values("revenue"), x="revenue", y="campaign",
                    color="channel", color_discrete_map=CHANNEL_COLORS, orientation="h",
                    title=f"Top {top_n} Campaigns by Revenue (₹)")
    fig_c1.update_xaxes(tickprefix="₹")
    st.plotly_chart(_style_fig(fig_c1, height=420), width="stretch")
    st.plotly_chart(_style_fig(px.bar(camp.sort_values("roas"), x="roas", y="campaign",
                                      color="channel", color_discrete_map=CHANNEL_COLORS, orientation="h",
                                      title="ROAS by Campaign (1.0 = break-even)")
                               .add_vline(x=1, line_dash="dash", line_color="#ef4444"), height=420),
                    width="stretch")
    _render_table(camp[["campaign", "channel", "spend", "revenue", "profit", "roi_pct", "roas", "ctr", "cvr",
                        "cpa"]].style.format({
        "spend": lambda v: fmt_inr(v, 0),
        "revenue": lambda v: fmt_inr(v, 0),
        "profit": lambda v: fmt_inr(v, 0),
        "roi_pct": "{:.0f}%",
        "roas": "{:.2f}x",
        "ctr": "{:.2%}",
        "cvr": "{:.2%}",
        "cpa": lambda v: fmt_inr(v, 2),
    }), max_height=420)

# ------------------------------------------------------------------ Engagement trends
with tab_trend:
    grain = st.radio("Group by", ["Week", "Month"], horizontal=True)
    d = df.copy()
    d["period"] = d["date"].dt.to_period("W-SUN" if grain == "Week" else "M").dt.start_time
    tr = summarize(d, "period").sort_values("period")
    fig_eng = px.line(tr, x="period", y="engagement_rate", markers=True, title=f"Engagement Rate per {grain}")
    fig_eng.update_yaxes(tickformat=".1%")
    st.plotly_chart(_style_fig(fig_eng), width="stretch")
    a, b = st.columns(2)
    fig_ctr = px.line(tr, x="period", y="ctr", markers=True, title="Click-Through Rate")
    fig_ctr.update_yaxes(tickformat=".1%")
    a.plotly_chart(_style_fig(fig_ctr), width="stretch")
    fig_cvr = px.line(tr, x="period", y="cvr", markers=True, title="Conversion Rate")
    fig_cvr.update_yaxes(tickformat=".1%")
    b.plotly_chart(_style_fig(fig_cvr), width="stretch")
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
