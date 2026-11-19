"""Export marketing datasets to styled Excel (.xlsx) workbooks at high speed."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.kpis import summarize

DATA_DIR = ROOT / "data"


def export_all():
    clean_csv = DATA_DIR / "clean_marketing_data.csv"
    raw_csv = DATA_DIR / "raw_marketing_data.csv"
    if not clean_csv.exists():
        raise FileNotFoundError(f"{clean_csv} not found.")

    print("Loading datasets for Excel export...")
    df_clean = pd.read_csv(clean_csv)
    df_raw = pd.read_csv(raw_csv) if raw_csv.exists() else None

    # 1. Clean dataset standalone workbook
    clean_path = DATA_DIR / "clean_marketing_data.xlsx"
    print(f"Writing {clean_path} ({len(df_clean):,} rows)...")
    with pd.ExcelWriter(clean_path, engine="openpyxl") as writer:
        df_clean.to_excel(writer, sheet_name="Clean Marketing Data", index=False)
    print(f"Exported: {clean_path}")

    # 2. Multi-sheet comprehensive workbook
    full_path = DATA_DIR / "marketing_performance_dataset.xlsx"
    print(f"Writing {full_path}...")
    with pd.ExcelWriter(full_path, engine="openpyxl") as writer:
        df_clean.to_excel(writer, sheet_name="Clean Data", index=False)
        if df_raw is not None:
            df_raw.to_excel(writer, sheet_name="Raw Data", index=False)
        summarize(df_clean, "channel").sort_values("revenue", ascending=False).to_excel(writer, sheet_name="Channel Summary", index=False)
        summarize(df_clean, ["campaign", "channel"]).sort_values("revenue", ascending=False).to_excel(writer, sheet_name="Campaign Summary", index=False)
        if "location" in df_clean.columns:
            summarize(df_clean, "location").sort_values("revenue", ascending=False).to_excel(writer, sheet_name="Location Summary", index=False)
        if "device_type" in df_clean.columns:
            summarize(df_clean, "device_type").sort_values("conversions", ascending=False).to_excel(writer, sheet_name="Device Summary", index=False)

    print(f"Exported: {full_path}")


if __name__ == "__main__":
    export_all()
