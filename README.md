# Marketing Performance Dashboard

Enterprise marketing analytics platform: tracks, analyses, and visualises marketing campaign performance across multi-channel campaigns with an expanded dataset of 50,000+ records.

## Features
- **Expanded Enterprise Dataset:** 50,000 clean records (55,000+ raw) covering 2024–2025 across 34 campaigns and 7 channels (Email, Google Ads, Facebook, Instagram, LinkedIn, YouTube, Website).
- **Rich Dimensions:** Campaign ID, Customer ID, Date, Marketing Channel, Campaign Type, Target Audience, Location, Device Type, Purchase Status, Engagements, and Sessions.
- **Relational SQLite Database:** Normalized tables (`marketing`, `dim_campaigns`, `dim_customers`, `dim_channels`) with primary keys, foreign keys, and 8 performance B-tree indexes.
- **KPI Engine:** Revenue, Ad Spend, Net Profit, CTR, Conversion Rate, CPC, CPA, ROAS, ROI %, Reach, and Customer Engagement Score.
- **Interactive Multi-Filter Dashboard:** Real-time dynamic slicing by Date Range, Marketing Channel, Campaign, Campaign Type, Location, Device Type, and Purchase Status.
- **Light & Dark Theme:** Full high-contrast dark/light mode toggle with Power BI executive aesthetic.
- **Automated Insights & Exporting:** Automated business insights, one-click HTML reports, multi-sheet formatted Excel workbooks (`.xlsx`), and Power BI Project files (`.pbip`, `.pbit`).

## Run locally
```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python src/step1_generate_data.py
python src/step2_clean_data.py
python -m src.step4_validate
streamlit run app.py
```

## Tech stack
Python 3.12, Pandas, NumPy, Plotly, SQLite, OpenPyXL, Streamlit, Microsoft Power BI Desktop.

## Project structure
```
app.py                    Streamlit executive dashboard
src/step1_generate_data.py   creates raw 55,000+ record dataset with realistic messiness
src/step2_clean_data.py      cleaning, imputation, and SQLite relational database schema
src/kpis.py                  KPI formulas and Indian Rupee (₹) formatting
src/step4_validate.py        15 data quality & integrity validation tests
src/insights.py              automated business intelligence & recommendations
src/report.py                HTML report builder (summary, campaign, monthly)
src/export_excel.py          multi-sheet Excel exporter (.xlsx)
src/create_powerbi_project.py Power BI project (.pbip) and template (.pbit) generator
data/                        clean_marketing_data.csv, clean_marketing_data.xlsx, marketing.db, raw_marketing_data.csv
powerbi/                     Marketing_Performance_Dashboard.pbip, .pbit, theme.json
reports/                     sample generated HTML reports
```
