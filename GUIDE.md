# Step-by-Step Guide: Marketing Performance Dashboard (25 days)

All code is already written in this folder. This guide tells you what to do each day, what each file does, and how to explain it.

---
## PART 0 - Setup (Day 1)

1. Install Python 3.10+ from python.org (tick "Add Python to PATH"), VS Code, and Git.
2. Unzip this folder, open it in VS Code, open a terminal and run:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
```

---
## PART 1 - Requirement analysis & dataset (Days 1-3)

**Write down (this becomes Chapter 1 of your report):**
- Problem: businesses spend money on many channels but cannot easily see which ones earn money.
- Users: marketing manager, business owner, analyst.
- Questions to answer: Which campaign is best? Which channel converts most? Is engagement growing? Where should budget move?
- KPIs: CTR, CVR, CPC, CPA, ROAS, ROI, Reach, Engagement Rate.

**Dataset:** run

```bash
python src/step1_generate_data.py
```

This creates `data/raw_marketing_data.csv` (14 campaigns, 6 channels, ~700 daily rows) with deliberate problems: missing values, duplicates, inconsistent channel names ("FB", "insta"), negative spend.

Want real data instead? Download a Kaggle "marketing campaign performance" CSV and rename its columns to: date, campaign, channel, impressions, reach, clicks, conversions, spend, revenue, likes, shares, comments, website_sessions, bounce_rate, new_customers. (Rename columns with `df.rename(columns={...})`. If your dataset lacks some columns, create them or remove them from `SUM_COLS` in `src/kpis.py`.)

---
## PART 2 - Data cleaning & preprocessing (Days 4-7)

```bash
python src/step2_clean_data.py
```

What the code does (explain each in your viva):

| # | Action | Why |
|---|--------|-----|
| 1 | Standardise channel names with a mapping dictionary | "FB", "facebook", "Facebook" are one channel |
| 2 | Convert `date` to datetime | enables monthly/weekly grouping |
| 3 | `drop_duplicates()` | duplicates inflate totals |
| 4 | Negative spend/revenue/clicks to NaN | impossible values |
| 5 | Impute missing values with channel-wise medians (clicks = impressions x median CTR, spend = clicks x median CPC, revenue = conversions x median revenue/conversion) | keeps rows, uses realistic numbers |
| 6 | Enforce clicks <= impressions, conversions <= clicks | funnel logic |
| 7 | Add `month`, `weekday` columns | used by dashboard |

Outputs: `data/clean_marketing_data.csv` and the SQLite database `data/marketing.db` (table `marketing`).

**Check the database yourself:**
```bash
python -c "import sqlite3,pandas as pd; c=sqlite3.connect('data/marketing.db'); print(pd.read_sql('SELECT channel, ROUND(SUM(revenue)) rev, ROUND(SUM(spend)) spend FROM marketing GROUP BY channel', c))"
```
Take a screenshot of the "BEFORE vs AFTER" output for your report.

---
## PART 3 - KPI analysis (Days 8-12)

File: `src/kpis.py`. Formulas:

| KPI | Formula | Meaning |
|-----|---------|---------|
| CTR | clicks / impressions | how appealing the ad is |
| Conversion rate | conversions / clicks | how well the landing page sells |
| CPC | spend / clicks | cost of one visit |
| CPA | spend / conversions | cost of one customer |
| ROAS | revenue / spend | revenue per $1 spent (1.0 = break-even) |
| ROI % | (revenue - spend) / spend x 100 | profit percentage |
| Reach | unique people reached | audience size |
| Engagement rate | (likes+shares+comments) / impressions | social interaction |

Important idea to mention: **ratios must be computed from summed totals, never by averaging daily ratios.** That is why `summarize()` sums first and then calls `add_ratios()`.

Explore in a notebook (optional, good for report screenshots):
```python
import pandas as pd
from src.kpis import summarize, overall
df = pd.read_csv("data/clean_marketing_data.csv", parse_dates=["date","month"])
print(overall(df))
print(summarize(df, "channel").sort_values("roi_pct", ascending=False))
print(summarize(df, "campaign").sort_values("roas", ascending=False))
```

Matplotlib chart for your report (optional):
```python
import matplotlib.pyplot as plt
ch = summarize(df, "channel").sort_values("roi_pct")
plt.barh(ch["channel"], ch["roi_pct"], color="#4b2bd6")
plt.xlabel("ROI %"); plt.title("ROI by Channel"); plt.tight_layout()
plt.savefig("reports/roi_by_channel.png", dpi=150)
```

---
## PART 4 - Dashboard development (Days 13-17)

```bash
streamlit run app.py
```
Opens at http://localhost:8501. Tabs inside `app.py`:

1. **Overview** - 12 KPI cards with arrows vs the previous period, monthly spend vs revenue + ROI line, conversion funnel
2. **Channels** - ROI, conversion rate, revenue share, spend-vs-revenue bubble chart, scorecard table
3. **Campaigns** - top-N bar chart, ROAS chart with break-even line, campaign table
4. **Engagement Trends** - weekly/monthly engagement, CTR, conversion, sessions, channel x weekday heatmap
5. **Insights** - automatic recommendations
6. **Reports** - download HTML report and filtered CSV

Sidebar filters (date range, channels, campaigns) update every chart.

**Daily plan:** Day 13 layout + filters, Day 14 KPI cards, Day 15 channel charts, Day 16 campaign + trends, Day 17 polish and screenshots.

### Optional: Power BI version (the brief lists Power BI)
1. Power BI Desktop - Get Data - Text/CSV - `data/clean_marketing_data.csv` - Load.
2. Home - Enter data / or New measure. Create these DAX measures:

```DAX
Total Spend       = SUM(clean_marketing_data[spend])
Total Revenue     = SUM(clean_marketing_data[revenue])
Total Clicks      = SUM(clean_marketing_data[clicks])
Total Impressions = SUM(clean_marketing_data[impressions])
Total Conversions = SUM(clean_marketing_data[conversions])
CTR   = DIVIDE([Total Clicks], [Total Impressions])
CVR   = DIVIDE([Total Conversions], [Total Clicks])
CPA   = DIVIDE([Total Spend], [Total Conversions])
ROAS  = DIVIDE([Total Revenue], [Total Spend])
ROI % = DIVIDE([Total Revenue] - [Total Spend], [Total Spend])
Engagement Rate = DIVIDE(SUM(clean_marketing_data[likes]) + SUM(clean_marketing_data[shares]) + SUM(clean_marketing_data[comments]), [Total Impressions])
```
3. Visuals: Cards (Revenue, Spend, ROI %, ROAS), Clustered column (channel vs ROI %), Line chart (month vs revenue/spend), Donut (revenue by channel), Table (campaign KPIs), Funnel (impressions, clicks, conversions). Add slicers for date, channel, campaign.
4. Save as `dashboard.pbix`, export screenshots (File - Export - PDF). Add the pbix to GitHub too.

---
## PART 5 - Business insights & reports (Days 18-21)

- `src/insights.py` generates text insights (best/worst ROI channel, highest converting channel, top campaign, loss-making campaigns, cheapest CPA, monthly trend, best weekday, recommendation).
- `src/report.py` builds Campaign, Summary and Monthly HTML reports. Generate sample files:
```bash
python -m src.report        # writes reports/*.html
```
- Open an HTML report in Chrome, press Ctrl+P, Save as PDF for the "Project Report" appendix.

**Write your own insights too.** Open the dashboard, look at the charts, and write 5-8 findings in this format: *Observation - Reason - Recommendation*. Example: "LinkedIn has a ROAS of X but the highest CPA; it is suited to B2B leads, not mass sales. Keep it for webinars, cut broad targeting."

---
## PART 6 - Testing & validation (Days 22-24)

```bash
python -m src.step4_validate
```
It checks: no missing values, no duplicates, no negatives, clicks <= impressions, conversions <= clicks, reach <= impressions, 6 clean channels, CTR within 0-1, channel totals equal grand total.

Manual tests (put in a table in your report): filter by a single channel and confirm the totals match the scorecard; select an empty combination and confirm the warning appears; change the date range and confirm the arrows change; download both files and open them.

Day 24: remove unused imports, re-run all steps from scratch on a clean virtual environment, and fix anything that breaks.

---
## PART 7 - GitHub (Day 24-25)

```bash
git init
git add .
git commit -m "Marketing Performance Dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/marketing-performance-dashboard.git
git push -u origin main
```
(Create the empty repository on github.com first. Keep `data/` committed - the app needs `marketing.db` / the CSV when deployed.)

---
## PART 8 - Deployment (Day 25)

**Streamlit Community Cloud (free, easiest):**
1. Go to share.streamlit.io, log in with GitHub.
2. Create app - choose your repo, branch `main`, main file `app.py`.
3. Deploy. In 2-3 minutes you get a link like `https://yourname-marketing-dashboard.streamlit.app` - this is your **Deployment Link**.

**Render (alternative):** New - Web Service - connect repo - Build command `pip install -r requirements.txt` - Start command `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

---
## PART 9 - Deliverables checklist

| Deliverable | What to include |
|-------------|-----------------|
| Source code | this folder |
| GitHub repo | with README, screenshots folder |
| Dashboard screenshots | each of the 6 tabs, filters in use |
| Deployment link | Streamlit Cloud URL |
| Project report | see outline below |
| PPT | see outline below |
| Demo video | see script below |

### Project report outline (~20-25 pages)
1. Title page, certificate, acknowledgement, abstract
2. Introduction - problem, objectives, scope (mention scope limits: no real-time, no AI prediction, no CRM, no cloud pipelines)
3. Literature / industry relevance - how agencies and e-commerce use dashboards
4. System design - workflow diagram (Collection - Cleaning - KPI - Dashboard - Insights - Report), database table, tech stack
5. Data description - columns table, sample rows, source
6. Data cleaning - issues found, fixes, before/after counts
7. KPI analysis - formulas, results tables
8. Dashboard - screenshot and explanation of each tab
9. Business insights and recommendations
10. Testing and validation - validation table, manual test cases
11. Deployment - steps and link
12. Conclusion, limitations, future scope (real-time APIs, forecasting, CRM integration)
13. References, appendix (code listings)

### PPT outline (12 slides)
1 Title | 2 Problem | 3 Objectives | 4 Architecture/workflow | 5 Dataset | 6 Cleaning (before/after) | 7 KPIs | 8-9 Dashboard screenshots | 10 Insights and recommendations | 11 Testing and deployment | 12 Conclusion and future scope, Q&A

### Demo video script (3-4 min)
- 0:00 Introduce yourself and the project
- 0:20 Show GitHub repo and structure
- 0:40 Show raw vs cleaned data
- 1:10 Open the live link, explain the KPI cards
- 1:50 Change filters, show Channels and Campaigns tabs
- 2:40 Show Insights and download a report
- 3:20 Summarise the learning and close
(Record with OBS Studio or Zoom screen recording.)

---
## PART 10 - Likely viva questions
- Why compute ratios from sums instead of averages? (Averaging daily ratios gives equal weight to small and big days and is wrong.)
- Difference between ROI and ROAS? (ROAS = revenue/spend; ROI = profit/spend.)
- How did you handle missing values? (Channel-wise median logic, not a blanket mean.)
- Why SQLite? (Zero setup, a single file, SQL-compatible, fine for this scale; MySQL would be used for multi-user production.)
- Why cache data in Streamlit? (`@st.cache_data` avoids re-reading the database on every click.)
- What would you add next? (Live API ingestion, forecasting, A/B test analysis, alerts.)

## Using your own data
Replace `data/raw_marketing_data.csv` with your file (same column names), delete step 1 from your workflow, and re-run steps 2 and 4. The dashboard needs no code changes as long as the columns match.
