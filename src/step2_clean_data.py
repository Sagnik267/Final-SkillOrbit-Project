"""STEP 2 - Clean the raw data, then store it in CSV + SQLite with relational tables and indexes.
Run:  python src/step2_clean_data.py
Output: data/clean_marketing_data.csv and data/marketing.db
"""
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

CHANNEL_MAP = {
    "email": "Email", "email ": "Email",
    "google ads": "Google Ads", "googleads": "Google Ads", "google ads ": "Google Ads",
    "facebook": "Facebook", "fb": "Facebook", "facebook ": "Facebook",
    "instagram": "Instagram", "insta": "Instagram", "instagram ": "Instagram",
    "youtube": "YouTube", "youtube ": "YouTube",
    "linkedin": "LinkedIn", "linkedin ": "LinkedIn",
    "website": "Website", "website direct": "Website", "website ": "Website",
}


def clean(df: pd.DataFrame, target_clean_count: int = 50000) -> pd.DataFrame:
    log = {"rows_start": len(df)}

    # 1. Standardise text columns
    df["channel"] = df["channel"].astype(str).str.strip().str.lower().map(CHANNEL_MAP)
    df["campaign"] = df["campaign"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()
    df["device_type"] = df["device_type"].astype(str).str.strip()
    df["campaign_type"] = df["campaign_type"].astype(str).str.strip()
    df["target_audience"] = df["target_audience"].astype(str).str.strip()
    df["purchase_status"] = df["purchase_status"].astype(str).str.strip()

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
    cpc_by_channel = df.groupby("channel")["cpc_tmp"].transform("median").fillna(0.8)
    log["missing_spend"] = int(df["spend"].isna().sum())
    df["spend"] = df["spend"].fillna((df["clicks"] * cpc_by_channel).round(2))
    df.loc[df["channel"] == "Website", "spend"] = 0.0

    df["rpc_tmp"] = df["revenue"] / df["conversions"].replace(0, np.nan)
    rpc_by_channel = df.groupby("channel")["rpc_tmp"].transform("median").fillna(75.0)
    log["missing_revenue"] = int(df["revenue"].isna().sum())
    df["revenue"] = df["revenue"].fillna((df["conversions"] * rpc_by_channel).round(2))
    df.loc[df["conversions"] == 0, "revenue"] = 0.0

    log["missing_likes"] = int(df["likes"].isna().sum())
    df["likes"] = df["likes"].fillna(df.groupby("channel")["likes"].transform("median")).fillna(0)

    df = df.drop(columns=["ctr_tmp", "cpc_tmp", "rpc_tmp"])

    # 6. Logical rules: clicks <= impressions, conversions <= clicks, reach <= impressions
    df["clicks"] = np.minimum(df["clicks"], df["impressions"])
    df["conversions"] = np.minimum(df["conversions"], df["clicks"])
    df["reach"] = np.minimum(df["reach"], df["impressions"])
    df["new_customers"] = np.minimum(df["new_customers"], df["conversions"])

    # 7. Re-align purchase status logically
    # If conversions > 0, status should be Completed or Refunded
    conv_positive = df["conversions"] > 0
    df.loc[conv_positive & df["purchase_status"].isin(["Abandoned", "Cancelled"]), "purchase_status"] = "Completed"
    # If conversions == 0, status cannot be Completed
    conv_zero = df["conversions"] == 0
    df.loc[conv_zero & (df["purchase_status"] == "Completed"), "purchase_status"] = "Abandoned"

    # 8. Calculate engagement score & helper columns
    int_cols = ["impressions", "reach", "clicks", "conversions", "likes", "shares",
                "comments", "website_sessions", "new_customers"]
    df[int_cols] = df[int_cols].round().astype(int)
    df["engagement_score"] = (df["likes"] * 1 + df["comments"] * 3 + df["shares"] * 5).astype(int)
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["date"].dt.day_name()
    df["campaign_name"] = df["campaign"]

    # 9. Sort by date and cap at target clean count if larger
    df = df.sort_values(["date", "campaign"]).reset_index(drop=True)
    if len(df) > target_clean_count:
        df = df.iloc[:target_clean_count].copy()

    # Assign primary key ID
    df["record_id"] = [f"REC-{i:06d}" for i in range(1, len(df) + 1)]

    # Arrange column order cleanly
    col_order = [
        "record_id", "date", "campaign_id", "campaign", "campaign_name", "channel",
        "customer_id", "campaign_type", "target_audience", "location", "device_type",
        "purchase_status", "impressions", "reach", "clicks", "conversions", "spend",
        "revenue", "likes", "shares", "comments", "engagement_score",
        "website_sessions", "bounce_rate", "new_customers", "month", "weekday"
    ]
    df = df[col_order]

    log["rows_end"] = len(df)
    print("Cleaning log:")
    for k, v in log.items():
        print(f"  {k:28s}: {v}")
    return df


def update_database(df: pd.DataFrame, db_path: Path):
    """Write relational tables and indexes to SQLite."""
    print(f"Updating database at {db_path}...")

    # Build dimension tables
    dim_campaigns = (
        df[["campaign_id", "campaign_name", "channel", "campaign_type", "target_audience"]]
        .drop_duplicates(subset=["campaign_id"])
        .reset_index(drop=True)
    )
    dim_campaigns["budget"] = dim_campaigns["channel"].map({
        "Google Ads": 150000.0, "Facebook": 120000.0, "Instagram": 130000.0,
        "YouTube": 140000.0, "LinkedIn": 180000.0, "Email": 40000.0, "Website": 25000.0
    }).fillna(50000.0)

    dim_customers = (
        df[["customer_id", "location", "device_type"]]
        .drop_duplicates(subset=["customer_id"])
        .reset_index(drop=True)
    )

    dim_channels = pd.DataFrame([
        {"channel_name": "Email", "category": "Direct Messaging", "primary_goal": "Retention & Repeat Orders"},
        {"channel_name": "Google Ads", "category": "Paid Search & Display", "primary_goal": "High-Intent Acquisition"},
        {"channel_name": "Facebook", "category": "Social Media", "primary_goal": "Brand Engagement & Conversion"},
        {"channel_name": "Instagram", "category": "Social Media", "primary_goal": "Visual Discovery & Influencers"},
        {"channel_name": "LinkedIn", "category": "Professional Network", "primary_goal": "B2B Lead Generation"},
        {"channel_name": "YouTube", "category": "Video Streaming", "primary_goal": "Video Demos & Awareness"},
        {"channel_name": "Website", "category": "Direct & Organic SEO", "primary_goal": "Organic Traffic & Retention"},
    ])

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # 1. Dimension Tables
        dim_campaigns.to_sql("dim_campaigns", conn, if_exists="replace", index=False)
        dim_customers.to_sql("dim_customers", conn, if_exists="replace", index=False)
        dim_channels.to_sql("dim_channels", conn, if_exists="replace", index=False)

        # 2. Fact Marketing Table with proper Primary Key and Constraints
        cur.execute("DROP TABLE IF EXISTS marketing")
        cur.execute("""
        CREATE TABLE marketing (
            record_id TEXT PRIMARY KEY,
            date TIMESTAMP NOT NULL,
            campaign_id TEXT,
            campaign TEXT NOT NULL,
            campaign_name TEXT,
            channel TEXT NOT NULL,
            customer_id TEXT,
            campaign_type TEXT,
            target_audience TEXT,
            location TEXT,
            device_type TEXT,
            purchase_status TEXT,
            impressions INTEGER NOT NULL,
            reach INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            spend REAL NOT NULL,
            revenue REAL NOT NULL,
            likes INTEGER NOT NULL,
            shares INTEGER NOT NULL,
            comments INTEGER NOT NULL,
            engagement_score INTEGER NOT NULL,
            website_sessions INTEGER NOT NULL,
            bounce_rate REAL NOT NULL,
            new_customers INTEGER NOT NULL,
            month TIMESTAMP NOT NULL,
            weekday TEXT NOT NULL,
            FOREIGN KEY (campaign_id) REFERENCES dim_campaigns(campaign_id),
            FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
            FOREIGN KEY (channel) REFERENCES dim_channels(channel_name)
        );
        """)

        # Insert records into fact table
        df.to_sql("marketing", conn, if_exists="append", index=False)

        # 3. Create high-performance indexes on frequently queried columns
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_date ON marketing(date);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_channel ON marketing(channel);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_campaign ON marketing(campaign);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_type ON marketing(campaign_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_location ON marketing(location);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_device ON marketing(device_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_purchase ON marketing(purchase_status);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mkt_customer ON marketing(customer_id);")

        conn.commit()

    print(f"Database successfully updated with {len(df)} records in 'marketing' table and 8 performance indexes.")


if __name__ == "__main__":
    raw = pd.read_csv(DATA_DIR / "raw_marketing_data.csv")
    na = raw.isna().sum()
    print("Missing values BEFORE:\n", na[na > 0], "\n")
    cleaned = clean(raw, target_clean_count=50000)
    print("\nMissing values AFTER:", int(cleaned.isna().sum().sum()))

    cleaned.to_csv(DATA_DIR / "clean_marketing_data.csv", index=False)
    update_database(cleaned, DATA_DIR / "marketing.db")
    print("Saved data/clean_marketing_data.csv and data/marketing.db (table: marketing)")
