"""End-to-end verification script for the expanded marketing dataset and database."""
import sqlite3
import pandas as pd
from src.kpis import overall, summarize, fmt_inr
from src.insights import generate_insights

print("=== 1 & 2. RECORD COUNT VERIFICATION ===")
print("Original Number of Records: 680")
clean_df = pd.read_csv("data/clean_marketing_data.csv", parse_dates=["date", "month"])
raw_df = pd.read_csv("data/raw_marketing_data.csv")
print(f"Raw Dataset Records:        {len(raw_df):,}")
print(f"New Clean Dataset Records:  {len(clean_df):,}")

print("\n=== 3. DATA QUALITY VERIFICATION ===")
raw_na = raw_df.isna().sum()
print("Raw Dataset Missing Values:\n", raw_na[raw_na > 0].to_dict())
print("Raw Dataset Duplicates:    ", int(raw_df.duplicated().sum()))
print("Clean Dataset Missing:     ", int(clean_df.isna().sum().sum()))
print("Clean Dataset Duplicates:  ", int(clean_df.duplicated().sum()))
print("Unique Record IDs:         ", int(clean_df["record_id"].nunique()))

print("\n=== 4. DATABASE INTEGRITY & CONNECTIVITY ===")
with sqlite3.connect("data/marketing.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables in marketing.db:    ", tables)
    for tbl in tables:
        cur.execute(f"SELECT count(*) FROM {tbl}")
        print(f"  Row count in {tbl:<15}: {cur.fetchone()[0]:,}")
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='marketing'")
    indexes = [r[0] for r in cur.fetchall()]
    print("Indexes on marketing table:", indexes)

print("\n=== 5. DASHBOARD KPIS & CALCULATIONS ===")
tot = overall(clean_df)
print(f"Total Revenue:          {fmt_inr(tot['revenue'])}")
print(f"Total Ad Spend:         {fmt_inr(tot['spend'])}")
print(f"Net Profit:             {fmt_inr(tot['profit'])}")
print(f"Total Impressions:      {tot['impressions']:,.0f}")
print(f"Total Clicks:           {tot['clicks']:,.0f}")
print(f"Total Conversions:      {tot['conversions']:,.0f}")
print(f"Average CTR:            {tot['ctr']:.2%}")
print(f"Conversion Rate (CVR):  {tot['cvr']:.2%}")
print(f"ROI %:                  {tot['roi_pct']:.0f}%")
print(f"ROAS:                   {tot['roas']:.2f}x")
print(f"Cost Per Acq (CPA):     {fmt_inr(tot['cpa'], decimals=2)}")

print("\n=== 6. DIMENSION COVERAGE ===")
print("Channels (", clean_df["channel"].nunique(), "):", list(clean_df["channel"].unique()))
print("Campaigns (", clean_df["campaign"].nunique(), "):", list(clean_df["campaign"].unique()[:5]), "...")
print("Campaign Types (", clean_df["campaign_type"].nunique(), "):", list(clean_df["campaign_type"].unique()))
print("Locations (", clean_df["location"].nunique(), "):", list(clean_df["location"].unique()))
print("Device Types (", clean_df["device_type"].nunique(), "):", list(clean_df["device_type"].unique()))
print("Purchase Statuses (", clean_df["purchase_status"].nunique(), "):", list(clean_df["purchase_status"].unique()))
print("Date Span:", clean_df["date"].min().strftime("%Y-%m-%d"), "to", clean_df["date"].max().strftime("%Y-%m-%d"))

print("\n=== 7. AUTOMATED INSIGHTS SAMPLE ===")
for i in generate_insights(clean_df)[:5]:
    print(" ", i)
