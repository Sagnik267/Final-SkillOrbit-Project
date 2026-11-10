"""STEP 4 - Data validation / testing. Run:  python -m src.step4_validate"""
import pandas as pd
from pathlib import Path
from src.kpis import overall, summarize

df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "clean_marketing_data.csv", parse_dates=["date"])
checks = {
    "No missing values": df.isna().sum().sum() == 0,
    "No duplicate rows": not df.duplicated().any(),
    "No negative spend/revenue/clicks": (df[["spend", "revenue", "clicks"]] >= 0).all().all(),
    "clicks <= impressions": (df["clicks"] <= df["impressions"]).all(),
    "conversions <= clicks": (df["conversions"] <= df["clicks"]).all(),
    "reach <= impressions": (df["reach"] <= df["impressions"]).all(),
    "Exactly 6 clean channels": df["channel"].nunique() == 6,
    "CTR between 0 and 1": 0 < overall(df)["ctr"] < 1,
    "Channel sums equal grand total": abs(summarize(df, "channel")["revenue"].sum() - df["revenue"].sum()) < 1e-6,
}
for name, ok in checks.items():
    print(("PASS  " if ok else "FAIL  ") + name)
assert all(checks.values()), "Some validation checks failed!"
print("\nAll checks passed.")
