"""STEP 2 - Clean the raw data, then store it in CSV + SQLite.
Run:  python src/step2_clean_data.py
Output: data/clean_marketing_data.csv and data/marketing.db
"""
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

CHANNEL_MAP = {
    "email": "Email", "google ads": "Google Ads", "googleads": "Google Ads",
    "facebook": "Facebook", "fb": "Facebook", "instagram": "Instagram", "insta": "Instagram",
    "youtube": "YouTube", "linkedin": "LinkedIn",
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    log = {"rows_start": len(df)}

    # 1. Standardise text columns
    df["channel"] = df["channel"].str.strip().str.lower().map(CHANNEL_MAP)
    df["campaign"] = df["campaign"].str.strip()
    log["unknown_channels_dropped"] = int(df["channel"].isna().sum())
    df = df.dropna(subset=["channel", "campaign"])

    # 2. Fix data types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # 3. Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = before - len(df)

    # 4. Impossible values -> missing (so they get imputed below)
    for col in ["spend", "revenue", "clicks"]:
        bad = df[col] < 0
        log[f"negative_{col}"] = int(bad.sum())
        df.loc[bad, col] = np.nan

    # 5. Impute missing values using sensible business logic
    df["ctr_tmp"] = df["clicks"] / df["impressions"]
    ctr_by_channel = df.groupby("channel")["ctr_tmp"].transform("median")
    log["missing_clicks"] = int(df["clicks"].isna().sum())
    df["clicks"] = df["clicks"].fillna((df["impressions"] * ctr_by_channel).round())

    df["cpc_tmp"] = df["spend"] / df["clicks"].replace(0, np.nan)
    cpc_by_channel = df.groupby("channel")["cpc_tmp"].transform("median")
    log["missing_spend"] = int(df["spend"].isna().sum())
    df["spend"] = df["spend"].fillna((df["clicks"] * cpc_by_channel).round(2))

    df["rpc_tmp"] = df["revenue"] / df["conversions"].replace(0, np.nan)
    rpc_by_channel = df.groupby("channel")["rpc_tmp"].transform("median")
    log["missing_revenue"] = int(df["revenue"].isna().sum())
    df["revenue"] = df["revenue"].fillna((df["conversions"] * rpc_by_channel).round(2))

    log["missing_likes"] = int(df["likes"].isna().sum())
    df["likes"] = df["likes"].fillna(df.groupby("channel")["likes"].transform("median")).fillna(0)

    df = df.drop(columns=["ctr_tmp", "cpc_tmp", "rpc_tmp"])

    # 6. Logical rules: clicks <= impressions, conversions <= clicks
    df["clicks"] = np.minimum(df["clicks"], df["impressions"])
    df["conversions"] = np.minimum(df["conversions"], df["clicks"])

    # 7. Final types + helper columns used by the dashboard
    int_cols = ["impressions", "reach", "clicks", "conversions", "likes", "shares",
                "comments", "website_sessions", "new_customers"]
    df[int_cols] = df[int_cols].round().astype(int)
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["date"].dt.day_name()

    log["rows_end"] = len(df)
    print("Cleaning log:")
    for k, v in log.items():
        print(f"  {k:28s}: {v}")
    return df.sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    raw = pd.read_csv(DATA_DIR / "raw_marketing_data.csv")
    na = raw.isna().sum()
    print("Missing values BEFORE:\n", na[na > 0], "\n")
    cleaned = clean(raw)
    print("\nMissing values AFTER:", int(cleaned.isna().sum().sum()))

    cleaned.to_csv(DATA_DIR / "clean_marketing_data.csv", index=False)
    with sqlite3.connect(DATA_DIR / "marketing.db") as conn:
        cleaned.to_sql("marketing", conn, if_exists="replace", index=False)
    print("Saved data/clean_marketing_data.csv and data/marketing.db (table: marketing)")
