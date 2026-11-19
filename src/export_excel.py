"""Export marketing datasets to styled Excel (.xlsx) workbooks."""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.kpis import summarize

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def style_sheet(ws, df, is_currency_cols=None, is_pct_cols=None, is_int_cols=None):
    ws.views.sheetView[0].showGridLines = True
    header_fill = PatternFill(start_color="4B2BD6", end_color="4B2BD6", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    regular_font = Font(name="Segoe UI", size=10)
    border_side = Side(style="thin", color="E2E8F0")
    border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)

    # Header row
    for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    # Data rows
    for row_idx, row in enumerate(df.itertuples(index=False), 2):
        ws.row_dimensions[row_idx].height = 20
        for col_idx, value in enumerate(row, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = regular_font
            cell.border = border
            col_name = df.columns[col_idx - 1]
            if is_currency_cols and col_name in is_currency_cols:
                cell.number_format = "₹#,##0.00"
                cell.alignment = Alignment(horizontal="right")
            elif is_pct_cols and col_name in is_pct_cols:
                cell.number_format = "0.00%"
                cell.alignment = Alignment(horizontal="right")
            elif is_int_cols and col_name in is_int_cols:
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right")
            elif col_name == "date":
                cell.alignment = Alignment(horizontal="center")
            else:
                cell.alignment = Alignment(horizontal="left")

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


def export_all():
    clean_csv = DATA_DIR / "clean_marketing_data.csv"
    raw_csv = DATA_DIR / "raw_marketing_data.csv"
    if not clean_csv.exists():
        raise FileNotFoundError(f"{clean_csv} not found.")

    df_clean = pd.read_csv(clean_csv)
    df_raw = pd.read_csv(raw_csv) if raw_csv.exists() else None

    curr_cols = ["spend", "revenue"]
    pct_cols = ["bounce_rate"]
    int_cols = [
        "impressions", "reach", "clicks", "conversions", "likes",
        "shares", "comments", "website_sessions", "new_customers"
    ]

    # 1. Clean dataset standalone workbook
    wb_clean = Workbook()
    ws_clean = wb_clean.active
    ws_clean.title = "Clean Marketing Data"
    style_sheet(ws_clean, df_clean, curr_cols, pct_cols, int_cols)
    clean_path = DATA_DIR / "clean_marketing_data.xlsx"
    wb_clean.save(clean_path)
    print(f"Exported: {clean_path}")

    # 2. Multi-sheet comprehensive workbook
    wb_full = Workbook()
    ws1 = wb_full.active
    ws1.title = "Clean Data"
    style_sheet(ws1, df_clean, curr_cols, pct_cols, int_cols)

    if df_raw is not None:
        ws2 = wb_full.create_sheet("Raw Data")
        style_sheet(ws2, df_raw, curr_cols, pct_cols, int_cols)

    df_ch = summarize(df_clean, "channel").sort_values("revenue", ascending=False)
    ws3 = wb_full.create_sheet("Channel Summary")
    style_sheet(
        ws3, df_ch,
        is_currency_cols=["spend", "revenue", "profit", "cpc", "cpa"],
        is_pct_cols=["ctr", "cvr", "engagement_rate"],
        is_int_cols=int_cols,
    )

    df_camp = summarize(df_clean, ["campaign", "channel"]).sort_values("revenue", ascending=False)
    ws4 = wb_full.create_sheet("Campaign Summary")
    style_sheet(
        ws4, df_camp,
        is_currency_cols=["spend", "revenue", "profit", "cpc", "cpa"],
        is_pct_cols=["ctr", "cvr", "engagement_rate"],
        is_int_cols=int_cols,
    )

    full_path = DATA_DIR / "marketing_performance_dataset.xlsx"
    wb_full.save(full_path)
    print(f"Exported: {full_path}")


if __name__ == "__main__":
    export_all()

