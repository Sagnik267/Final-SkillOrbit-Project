"""STEP 1 - Create an expanded, realistic (and deliberately messy) marketing dataset.
Generates 50,000+ records across 2024-2025 with rich attributes:
- Campaign ID & Name
- Customer ID
- Date
- Marketing Channel (Email, Google Ads, Facebook, Instagram, LinkedIn, YouTube, Website)
- Campaign Type (Search Ads, Social Media, Email Newsletter, Video Campaign, Influencer Collab, Display Retargeting, Content Marketing, Affiliate / Partner)
- Target Audience (Tech Enthusiasts, B2B Professionals, Gen Z & Students, Young Professionals, High Net Worth, Value Shoppers, Home & Lifestyle)
- Impressions, Reach, Clicks, Conversions, Spend, Revenue
- Engagement (Likes, Shares, Comments, Engagement Score)
- Website Traffic (Website Sessions, Bounce Rate)
- Location (Mumbai, Delhi NCR, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, International)
- Device Type (Mobile, Desktop, Tablet)
- Purchase Status (Completed, Abandoned, Pending, Refunded, Cancelled)
- High, average, and loss-making campaign tiers.

Run:  python src/step1_generate_data.py
Output: data/raw_marketing_data.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------ Channel baselines
CHANNELS = {
    "Email":       dict(ctr=0.045, cvr=0.055, cpc=0.35, aov=60,  imp=(8000, 22000),  social=0.00),
    "Google Ads":  dict(ctr=0.038, cvr=0.048, cpc=1.25, aov=80,  imp=(16000, 45000), social=0.00),
    "Facebook":    dict(ctr=0.013, cvr=0.022, cpc=0.82, aov=62,  imp=(22000, 55000), social=0.05),
    "Instagram":   dict(ctr=0.017, cvr=0.029, cpc=0.92, aov=68,  imp=(20000, 58000), social=0.08),
    "YouTube":     dict(ctr=0.009, cvr=0.017, cpc=0.62, aov=72,  imp=(32000, 85000), social=0.04),
    "LinkedIn":    dict(ctr=0.011, cvr=0.036, cpc=3.60, aov=155, imp=(6000, 18000),  social=0.03),
    "Website":     dict(ctr=0.065, cvr=0.072, cpc=0.00, aov=88,  imp=(12000, 30000), social=0.02),
}

# ------------------------------------------------------------------ Campaigns portfolio (34 distinct campaigns)
CAMPAIGN_DEFS = [
    # --- 2024 Campaigns ---
    ("CMP-101", "New Year Kickoff 2024",      "Email",       "Email Newsletter",    "Value Shoppers",      "2024-01-01", 31, "high"),
    ("CMP-102", "Republic Day Tech Fest",     "Google Ads",  "Search Ads",          "Tech Enthusiasts",    "2024-01-15", 40, "high"),
    ("CMP-103", "Q1 B2B Enterprise Lead Gen", "LinkedIn",    "Content Marketing",   "B2B Professionals",   "2024-02-01", 75, "high"),
    ("CMP-104", "Spring Fashion Drops",       "Instagram",   "Influencer Collab",   "Gen Z & Students",    "2024-03-01", 50, "average"),
    ("CMP-105", "Holi Color Extravaganza",    "Facebook",    "Social Media",        "Home & Lifestyle",    "2024-03-10", 35, "average"),
    ("CMP-106", "Tech Review Series 2024",    "YouTube",     "Video Campaign",      "Tech Enthusiasts",    "2024-04-01", 65, "average"),
    ("CMP-107", "Broad Video Outreach Test",  "YouTube",     "Video Campaign",      "Young Professionals", "2024-02-15", 45, "low"),
    ("CMP-108", "Summer Clearance 2024",      "Google Ads",  "Display Retargeting", "Value Shoppers",      "2024-05-01", 60, "average"),
    ("CMP-109", "Organic Search SEO Growth",  "Website",     "Content Marketing",   "Tech Enthusiasts",    "2024-01-01", 365, "high"),
    ("CMP-110", "Monsoon Wellness Drive",     "Email",       "Email Newsletter",    "Young Professionals", "2024-07-01", 45, "average"),
    ("CMP-111", "Cold Display Outreach 2024", "Facebook",    "Display Retargeting", "Value Shoppers",      "2024-06-15", 45, "low"),
    ("CMP-112", "Independence Day Mega Sale", "Facebook",    "Social Media",        "Home & Lifestyle",    "2024-08-01", 40, "high"),
    ("CMP-113", "Q3 SaaS Executive Summit",   "LinkedIn",    "Content Marketing",   "B2B Professionals",   "2024-08-15", 60, "average"),
    ("CMP-114", "Festive Season Preview",     "Instagram",   "Influencer Collab",   "Gen Z & Students",    "2024-09-01", 60, "high"),
    ("CMP-115", "Diwali Super Blast 2024",    "Google Ads",  "Search Ads",          "High Net Worth",      "2024-10-01", 50, "high"),
    ("CMP-116", "Black Friday Global 2024",   "Google Ads",  "Search Ads",          "Value Shoppers",      "2024-11-15", 25, "high"),
    ("CMP-117", "Year End Grand Finale 2024", "Email",       "Email Newsletter",    "Young Professionals", "2024-12-01", 31, "average"),

    # --- 2025 Campaigns ---
    ("CMP-201", "New Year Sale",              "Email",       "Email Newsletter",    "Value Shoppers",      "2025-01-01", 45, "average"),
    ("CMP-202", "Spring Launch",              "Google Ads",  "Search Ads",          "Tech Enthusiasts",    "2025-03-01", 60, "high"),
    ("CMP-203", "Brand Awareness Q1",         "YouTube",     "Video Campaign",      "Young Professionals", "2025-01-15", 70, "average"),
    ("CMP-204", "Influencer Push",            "Instagram",   "Influencer Collab",   "Gen Z & Students",    "2025-04-01", 55, "high"),
    ("CMP-205", "Summer Mega Sale",           "Facebook",    "Social Media",        "Home & Lifestyle",    "2025-06-01", 60, "average"),
    ("CMP-206", "B2B Lead Gen",               "LinkedIn",    "Content Marketing",   "B2B Professionals",   "2025-02-01", 90, "high"),
    ("CMP-207", "Retargeting Boost",          "Google Ads",  "Display Retargeting", "Tech Enthusiasts",    "2025-07-01", 70, "average"),
    ("CMP-208", "Monsoon Offers",             "Email",       "Email Newsletter",    "Young Professionals", "2025-07-15", 45, "average"),
    ("CMP-209", "Unoptimized Affiliate Push", "Facebook",    "Affiliate / Partner", "Value Shoppers",      "2025-05-15", 50, "low"),
    ("CMP-210", "Festive Season",             "Instagram",   "Influencer Collab",   "Gen Z & Students",    "2025-09-15", 65, "high"),
    ("CMP-211", "Product Demo Series",        "YouTube",     "Video Campaign",      "Tech Enthusiasts",    "2025-08-01", 75, "average"),
    ("CMP-212", "Diwali Blast",               "Facebook",    "Social Media",        "High Net Worth",      "2025-10-10", 45, "high"),
    ("CMP-213", "Website Direct & SEO 2025",  "Website",     "Content Marketing",   "Tech Enthusiasts",    "2025-01-01", 365, "high"),
    ("CMP-214", "Year End Clearance",         "Email",       "Email Newsletter",    "Value Shoppers",      "2025-11-20", 42, "average"),
    ("CMP-215", "Webinar Promotion",          "LinkedIn",    "Content Marketing",   "B2B Professionals",   "2025-09-01", 65, "average"),
    ("CMP-216", "Black Friday",               "Google Ads",  "Search Ads",          "Value Shoppers",      "2025-11-15", 30, "high"),
    ("CMP-217", "Cold Outreach Test 2025",    "LinkedIn",    "Display Retargeting", "Young Professionals", "2025-04-10", 40, "low"),
]

LOCATIONS = [
    ("Mumbai", 0.20),
    ("Delhi NCR", 0.18),
    ("Bengaluru", 0.16),
    ("Hyderabad", 0.12),
    ("Chennai", 0.10),
    ("Pune", 0.08),
    ("Kolkata", 0.06),
    ("Ahmedabad", 0.05),
    ("International", 0.05),
]
LOC_NAMES = [l[0] for l in LOCATIONS]
LOC_PROBS = np.array([l[1] for l in LOCATIONS])
LOC_PROBS = LOC_PROBS / LOC_PROBS.sum()

DEVICES = {
    "Mobile":  dict(weight=0.58, ctr_mult=1.05, cvr_mult=0.88, aov_mult=0.92, b_min=42, b_max=68),
    "Desktop": dict(weight=0.32, ctr_mult=0.95, cvr_mult=1.28, aov_mult=1.22, b_min=25, b_max=45),
    "Tablet":  dict(weight=0.10, ctr_mult=0.98, cvr_mult=1.00, aov_mult=1.04, b_min=32, b_max=52),
}
DEV_NAMES = list(DEVICES.keys())
DEV_PROBS = np.array([DEVICES[d]["weight"] for d in DEV_NAMES])
DEV_PROBS = DEV_PROBS / DEV_PROBS.sum()

CUSTOMER_POOL = np.array([f"CUST-{i:05d}" for i in range(10001, 25001)])


def generate_marketing_data(target_clean_count: int = 50000) -> pd.DataFrame:
    print(f"Generating realistic dataset targeted at {target_clean_count} records (Vectorized)...")
    dfs = []
    total_campaign_days = sum(duration for *_, duration, _ in CAMPAIGN_DEFS)
    slices_per_day = int(np.ceil(51000 / total_campaign_days)) + 1  # ~21

    for camp_id, name, ch, c_type, audience, start_str, duration, tier in CAMPAIGN_DEFS:
        p = CHANNELS[ch]
        # Tier modifiers
        if tier == "high":
            t_ctr, t_cvr, t_aov, t_cpc = 1.35, 1.45, 1.25, 0.85
        elif tier == "low":
            t_ctr, t_cvr, t_aov, t_cpc = 0.55, 0.45, 0.65, 1.35
        else:
            t_ctr, t_cvr, t_aov, t_cpc = 1.00, 1.00, 1.00, 1.00

        dates = pd.date_range(start_str, periods=duration)
        n_dates = len(dates)
        # Vectorized generation for this campaign
        reps = np.repeat(slices_per_day, n_dates)
        date_series = np.repeat(dates, reps)
        n_rows = len(date_series)

        # Device assignment
        devs = rng.choice(DEV_NAMES, size=n_rows, p=DEV_PROBS)
        dev_ctr_mult = np.array([DEVICES[d]["ctr_mult"] for d in devs])
        dev_cvr_mult = np.array([DEVICES[d]["cvr_mult"] for d in devs])
        dev_aov_mult = np.array([DEVICES[d]["aov_mult"] for d in devs])
        dev_b_min = np.array([DEVICES[d]["b_min"] for d in devs])
        dev_b_max = np.array([DEVICES[d]["b_max"] for d in devs])

        # Locations & Customers
        locs = rng.choice(LOC_NAMES, size=n_rows, p=LOC_PROBS)
        custs = rng.choice(CUSTOMER_POOL, size=n_rows)

        # Impressions
        weekends = np.where(pd.Series(date_series).dt.dayofweek >= 5, 1.15, 1.0)
        base_imp = rng.integers(int(p["imp"][0] / slices_per_day), int(p["imp"][1] / slices_per_day) + 1, size=n_rows)
        impressions = np.maximum(50, (base_imp * weekends * rng.uniform(0.8, 1.2, size=n_rows)).astype(int))

        # CTR & Clicks
        ctrs = np.clip(p["ctr"] * t_ctr * dev_ctr_mult * rng.normal(1.0, 0.12, size=n_rows), 0.002, 0.35)
        clicks = rng.binomial(impressions, ctrs)

        # CVR & Conversions
        cvrs = np.clip(p["cvr"] * t_cvr * dev_cvr_mult * rng.normal(1.0, 0.15, size=n_rows), 0.002, 0.40)
        conversions = np.where(clicks > 0, rng.binomial(np.maximum(clicks, 1), cvrs), 0)

        # Spend
        if ch == "Website":
            spend = np.zeros(n_rows, dtype=float)
        else:
            spend = np.round(np.maximum(5.0, clicks * p["cpc"] * t_cpc * rng.normal(1.0, 0.08, size=n_rows) + rng.uniform(3, 15, size=n_rows)), 2)

        # Revenue
        aov = np.maximum(20.0, p["aov"] * t_aov * dev_aov_mult * rng.normal(1.0, 0.10, size=n_rows))
        revenue = np.where(conversions > 0, np.round(conversions * aov, 2), 0.0)

        # Purchase Status
        r_status = rng.random(size=n_rows)
        status = np.where(
            conversions > 0,
            np.where(r_status > 0.06, "Completed", "Refunded"),
            np.where(
                clicks > 0,
                np.where(r_status < 0.75, "Abandoned", np.where(r_status < 0.92, "Pending", "Cancelled")),
                "Abandoned"
            )
        )
        # Adjust revenue for refunds
        revenue = np.where(status == "Refunded", np.round(revenue * rng.uniform(0.0, 0.5, size=n_rows), 2), revenue)

        # Reach, Engagements & Sessions
        reach = (impressions * rng.uniform(0.65, 0.88, size=n_rows)).astype(int)
        likes = (impressions * p["social"] * rng.uniform(0.5, 1.4, size=n_rows)).astype(int)
        shares = (likes * rng.uniform(0.12, 0.28, size=n_rows)).astype(int)
        comments = (likes * rng.uniform(0.06, 0.18, size=n_rows)).astype(int)
        eng_score = likes * 1 + comments * 3 + shares * 5
        sessions = (clicks * rng.uniform(0.82, 0.98, size=n_rows)).astype(int)
        bounce = np.round(rng.uniform(dev_b_min, dev_b_max), 1)
        new_cust = (conversions * rng.uniform(0.55, 0.90, size=n_rows)).astype(int)

        camp_df = pd.DataFrame({
            "date": pd.Series(date_series).dt.strftime("%Y-%m-%d"),
            "campaign_id": camp_id,
            "campaign": name,
            "channel": ch,
            "customer_id": custs,
            "campaign_type": c_type,
            "target_audience": audience,
            "location": locs,
            "device_type": devs,
            "purchase_status": status,
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "conversions": conversions,
            "spend": spend,
            "revenue": revenue,
            "likes": likes,
            "shares": shares,
            "comments": comments,
            "engagement_score": eng_score,
            "website_sessions": sessions,
            "bounce_rate": bounce,
            "new_customers": new_cust,
        })
        dfs.append(camp_df)

    df = pd.concat(dfs, ignore_index=True)
    print(f"Vectorized generation complete: {len(df)} initial clean rows.")

    # ------------------------------------------------------------------ Inject deliberate messiness for Step 2
    n = len(df)
    # 1. Missing values (~1.5% in key metrics)
    for col in ["clicks", "spend", "revenue", "likes"]:
        missing_idx = rng.choice(n, int(n * 0.015), replace=False)
        df.loc[missing_idx, col] = np.nan

    # 2. Duplicate rows (~120 duplicates)
    dups = df.sample(120, random_state=42)
    df = pd.concat([df, dups], ignore_index=True)

    # 3. Inconsistent channel casing / naming (4% of selected channels)
    messy_channels = {
        "Google Ads": ["google ads", "Google ads ", "GoogleAds"],
        "Facebook":   ["FB", "facebook", "Facebook "],
        "Instagram":  ["insta", "INSTAGRAM", "Instagram "],
        "Email":      ["email", "Email "],
        "Website":    ["website", "Website Direct"],
    }
    for good, bads in messy_channels.items():
        idx = df.index[df["channel"] == good]
        pick = rng.choice(idx, int(len(idx) * 0.04), replace=False)
        df.loc[pick, "channel"] = rng.choice(bads, len(pick))

    # 4. A few negative values to test validation cleaning
    df.loc[rng.choice(n, 8, replace=False), "spend"] = -50.0

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    out_path = DATA_DIR / "raw_marketing_data.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path} with {len(df)} raw records (with missing values, duplicates, and messy formatting).")
    return df


if __name__ == "__main__":
    generate_marketing_data(50000)
