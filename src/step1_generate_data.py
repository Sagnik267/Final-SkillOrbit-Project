"""STEP 1 - Create a realistic (and deliberately messy) marketing dataset.
Run:  python src/step1_generate_data.py
Output: data/raw_marketing_data.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)

# Typical behaviour of each channel
CHANNELS = {
    "Email":      dict(ctr=0.045, cvr=0.060, cpc=0.35, aov=55,  imp=(6000, 15000),  social=0.0),
    "Google Ads": dict(ctr=0.035, cvr=0.050, cpc=1.20, aov=75,  imp=(15000, 40000), social=0.0),
    "Facebook":   dict(ctr=0.012, cvr=0.022, cpc=0.80, aov=60,  imp=(20000, 50000), social=0.05),
    "Instagram":  dict(ctr=0.015, cvr=0.028, cpc=0.90, aov=65,  imp=(20000, 55000), social=0.08),
    "YouTube":    dict(ctr=0.008, cvr=0.018, cpc=0.60, aov=70,  imp=(30000, 80000), social=0.04),
    "LinkedIn":   dict(ctr=0.010, cvr=0.035, cpc=3.50, aov=150, imp=(5000, 15000),  social=0.03),
}

# (campaign name, channel, start date, duration in days)
CAMPAIGNS = [
    ("New Year Sale",        "Email",      "2025-01-01", 20),
    ("Spring Launch",        "Google Ads", "2025-03-01", 45),
    ("Brand Awareness Q1",   "YouTube",    "2025-01-15", 60),
    ("Influencer Push",      "Instagram",  "2025-04-01", 40),
    ("Summer Mega Sale",     "Facebook",   "2025-06-01", 50),
    ("B2B Lead Gen",         "LinkedIn",   "2025-02-01", 90),
    ("Retargeting Boost",    "Google Ads", "2025-07-01", 60),
    ("Monsoon Offers",       "Email",      "2025-07-15", 30),
    ("Festive Season",       "Instagram",  "2025-09-15", 60),
    ("Product Demo Series",  "YouTube",    "2025-08-01", 70),
    ("Diwali Blast",         "Facebook",   "2025-10-10", 35),
    ("Year End Clearance",   "Email",      "2025-11-20", 40),
    ("Webinar Promotion",    "LinkedIn",   "2025-09-01", 60),
    ("Black Friday",         "Google Ads", "2025-11-15", 20),
]

rows = []
for name, ch, start, days in CAMPAIGNS:
    p = CHANNELS[ch]
    for d in pd.date_range(start, periods=days):
        weekend = 1.15 if d.weekday() >= 5 else 1.0
        impressions = int(rng.integers(*p["imp"]) * weekend)
        ctr = max(0.002, p["ctr"] * rng.normal(1, 0.15))
        clicks = int(rng.binomial(impressions, ctr))
        cvr = max(0.002, p["cvr"] * rng.normal(1, 0.20))
        conversions = int(rng.binomial(max(clicks, 1), cvr))
        spend = round(clicks * p["cpc"] * rng.normal(1, 0.08) + 20, 2)
        revenue = round(conversions * p["aov"] * rng.normal(1, 0.10), 2)
        reach = int(impressions * rng.uniform(0.60, 0.85))
        likes = int(impressions * p["social"] * rng.uniform(0.6, 1.2))
        shares = int(likes * rng.uniform(0.10, 0.25))
        comments = int(likes * rng.uniform(0.05, 0.15))
        sessions = int(clicks * rng.uniform(0.85, 0.97))
        rows.append([d.strftime("%Y-%m-%d"), name, ch, impressions, reach, clicks, conversions,
                     spend, revenue, likes, shares, comments, sessions,
                     round(rng.uniform(25, 65), 1), int(conversions * rng.uniform(0.6, 0.9))])

cols = ["date", "campaign", "channel", "impressions", "reach", "clicks", "conversions",
        "spend", "revenue", "likes", "shares", "comments", "website_sessions",
        "bounce_rate", "new_customers"]
df = pd.DataFrame(rows, columns=cols)

# ---- make the data MESSY on purpose so Step 2 has real work to do ----
n = len(df)
for col in ["clicks", "spend", "revenue", "likes"]:
    df.loc[rng.choice(n, int(n * 0.02), replace=False), col] = np.nan     # missing values
dups = df.sample(25, random_state=1)
df = pd.concat([df, dups], ignore_index=True)                            # duplicate rows
messy = {"Google Ads": ["google ads", "Google ads ", "GoogleAds"], "Facebook": ["FB", "facebook"],
         "Instagram": ["insta", "INSTAGRAM"]}
for good, bads in messy.items():
    idx = df.index[df["channel"] == good]
    pick = rng.choice(idx, int(len(idx) * 0.05), replace=False)
    df.loc[pick, "channel"] = rng.choice(bads, len(pick))                # inconsistent names
df.loc[rng.choice(n, 5, replace=False), "spend"] = -50                   # impossible negatives

df = df.sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv(DATA_DIR / "raw_marketing_data.csv", index=False)
print(f"Created data/raw_marketing_data.csv with {len(df)} rows")
