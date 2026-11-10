# Marketing Performance Dashboard

Data analytics capstone: tracks, analyses and visualises marketing campaign performance across channels.

## Features
- Data generation, cleaning (duplicates, missing values, inconsistent names) and SQLite storage
- KPIs: CTR, conversion rate, CPC, CPA, ROAS, ROI, reach, engagement rate
- Interactive Streamlit dashboard with filters, period-over-period deltas, 6 tabs
- Automated business insights and downloadable HTML reports

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python src/step1_generate_data.py
python src/step2_clean_data.py
python -m src.step4_validate
streamlit run app.py
```

## Tech stack
Python, Pandas, NumPy, Plotly, Matplotlib, SQLite, Streamlit (deployed on Streamlit Community Cloud).

## Project structure
```
app.py                    dashboard
src/step1_generate_data.py   creates raw dataset
src/step2_clean_data.py      cleaning + SQLite
src/kpis.py                  KPI formulas
src/step4_validate.py        data validation tests
src/insights.py              auto insights
src/report.py                HTML reports
data/                        raw csv, clean csv, marketing.db
reports/                     sample generated reports
```
