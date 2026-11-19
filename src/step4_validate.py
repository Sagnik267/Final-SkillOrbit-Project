"""STEP 4 - Comprehensive data validation / testing. Run:  python -m src.step4_validate"""
import pandas as pd
from pathlib import Path
from src.kpis import overall, summarize

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "clean_marketing_data.csv"
df = pd.read_csv(DATA_FILE, parse_dates=["date", "month"])

required_columns = [
    "record_id", "date", "campaign_id", "campaign", "channel",
    "customer_id", "campaign_type", "target_audience", "location", "device_type",
    "purchase_status", "impressions", "reach", "clicks", "conversions", "spend",
    "revenue", "likes", "shares", "comments", "engagement_score",
    "website_sessions", "bounce_rate", "new_customers", "month", "weekday"
]

checks = {
    "Target record size >= 10,000 (actual: 50,000)": len(df) >= 10000,
    "Exactly 50,000 clean records": len(df) == 50000,
    "All required marketing columns present": all(col in df.columns for col in required_columns),
    "No missing values in any column": df.isna().sum().sum() == 0,
    "No duplicate record IDs": df["record_id"].nunique() == len(df),
    "No duplicate rows": not df.duplicated().any(),
    "No negative spend/revenue/clicks": (df[["spend", "revenue", "clicks"]] >= 0).all().all(),
    "clicks <= impressions": (df["clicks"] <= df["impressions"]).all(),
    "conversions <= clicks": (df["conversions"] <= df["clicks"]).all(),
    "reach <= impressions": (df["reach"] <= df["impressions"]).all(),
    "All 7 channels represented": df["channel"].nunique() == 7,
    "Date range spans at least 1-2 years": (df["date"].max() - df["date"].min()).days >= 365,
    "CTR between 0 and 1": 0 < overall(df)["ctr"] < 1,
    "Channel sums equal grand total": abs(summarize(df, "channel")["revenue"].sum() - df["revenue"].sum()) < 1e-4,
    "Multiple performance tiers present": df.groupby("campaign")["revenue"].sum().std() > 0,
}

print(f"\n--- DATA VALIDATION REPORT ({len(df):,} records) ---")
for name, ok in checks.items():
    print(("PASS  " if ok else "FAIL  ") + name)

assert all(checks.values()), "Some validation checks failed!"
print(f"\nAll {len(checks)} validation checks passed successfully!\n")
