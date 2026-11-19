"""STEP 5 - Turn numbers into plain-English business insights."""
import pandas as pd
from src.kpis import summarize, overall, fmt_inr


def generate_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No data for the selected filters."]
    out = []
    ch = summarize(df, "channel")
    camp = summarize(df, "campaign")
    tot = overall(df)

    best_roi = ch.loc[ch["roi_pct"].idxmax()]
    worst_roi = ch.loc[ch["roi_pct"].idxmin()]
    out.append(f"**Best ROI channel:** {best_roi['channel']} returns {best_roi['roi_pct']:.0f}% "
               f"(ROAS {best_roi['roas']:.2f}x). Consider shifting more budget here.")
    if len(ch) > 1:
        out.append(f"**Weakest ROI channel:** {worst_roi['channel']} returns only {worst_roi['roi_pct']:.0f}%. "
                   f"Review targeting, creatives and bids before spending more.")

    best_cvr = ch.loc[ch["cvr"].idxmax()]
    out.append(f"**Highest-converting channel:** {best_cvr['channel']} converts "
               f"{best_cvr['cvr']:.2%} of clicks (overall average {tot['cvr']:.2%}).")

    best_eng = ch.loc[ch["engagement_rate"].idxmax()]
    if best_eng["engagement_rate"] > 0:
        out.append(f"**Most engaging channel:** {best_eng['channel']} has an engagement rate of "
                   f"{best_eng['engagement_rate']:.2%}.")

    top = camp.loc[camp["revenue"].idxmax()]
    roas_str = f"with a ROAS of {top['roas']:.2f}x." if pd.notna(top['roas']) and top['spend'] > 0 else f"driven by {top['conversions']:,.0f} conversions (organic/zero ad spend)."
    out.append(f"**Top campaign by revenue:** '{top['campaign']}' generated {fmt_inr(top['revenue'])} {roas_str}")
    losers = camp[camp["roi_pct"] < 0]
    if len(losers):
        names = ", ".join(losers["campaign"].head(3))
        out.append(f"**Loss-making campaigns ({len(losers)}):** {names}. Pause or restructure them.")
    else:
        out.append("**No loss-making campaigns** in this selection. Every campaign earned more than it cost.")

    cheapest = ch.loc[ch["cpa"].idxmin()]
    out.append(f"**Cheapest customer acquisition:** {cheapest['channel']} at {fmt_inr(cheapest['cpa'], decimals=2)} per conversion "
               f"(overall {fmt_inr(tot['cpa'], decimals=2)}).")

    # Location & Device insights if present
    if "location" in df.columns and df["location"].nunique() > 1:
        loc_df = summarize(df, "location").sort_values("revenue", ascending=False)
        top_loc = loc_df.iloc[0]
        out.append(f"**Top revenue location:** {top_loc['location']} generated {fmt_inr(top_loc['revenue'])} "
                   f"({top_loc['revenue'] / (tot['revenue'] or 1):.1%} of total revenue).")

    if "device_type" in df.columns and df["device_type"].nunique() > 1:
        dev_df = summarize(df, "device_type").sort_values("conversions", ascending=False)
        top_dev = dev_df.iloc[0]
        out.append(f"**Dominant device:** {top_dev['device_type']} drives {top_dev['conversions']:,.0f} conversions "
                   f"({top_dev['cvr']:.2%} conversion rate).")

    if "campaign_type" in df.columns and df["campaign_type"].nunique() > 1:
        type_df = summarize(df, "campaign_type").sort_values("roas", ascending=False)
        best_type = type_df.iloc[0]
        out.append(f"**Highest ROAS campaign type:** {best_type['campaign_type']} leads with {best_type['roas']:.2f}x ROAS.")

    m = summarize(df, "month").sort_values("month")
    if len(m) >= 2:
        last, prev = m.iloc[-1], m.iloc[-2]
        chg = (last["revenue"] - prev["revenue"]) / prev["revenue"] * 100 if prev["revenue"] else 0
        direction = "up" if chg >= 0 else "down"
        out.append(f"**Monthly trend:** revenue in {last['month']:%b %Y} is {direction} {abs(chg):.1f}% "
                   f"vs {prev['month']:%b %Y}.")
    best_day = summarize(df, "weekday").sort_values("conversions", ascending=False).iloc[0]
    out.append(f"**Best weekday:** {best_day['weekday']} brings the most conversions ({best_day['conversions']:,.0f}).")

    out.append("**Recommendation:** move 10-15% of budget from the lowest-ROI channel to the highest-ROI "
               "channel, test new creatives on high-impression/low-CTR channels, and retarget website "
               "visitors who did not convert.")
    return out
