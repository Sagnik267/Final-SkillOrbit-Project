# 📊 Microsoft Power BI Final Project Guide & Files

This folder contains the complete Power BI solution for the **Marketing Performance Dashboard**, matching the Streamlit executive layout, DAX formulas, Indian Rupee (`₹`) formatting, and color palettes.

---

## 📁 1. Power BI Project Files Provided

All files are located in the [`powerbi/`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/powerbi) folder:

| File / Folder | Format | Description |
| :--- | :--- | :--- |
| **[`Marketing_Performance_Dashboard.pbip`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/powerbi/Marketing_Performance_Dashboard.pbip)** | **PBIP (Power BI Project)** | Microsoft's modern, text-based project format. Double-click to launch in Power BI Desktop. |
| **[`Marketing_Performance_Dashboard.pbit`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/powerbi/Marketing_Performance_Dashboard.pbit)** | **PBIT (Power BI Template)** | Self-contained Power BI Template with all visual containers, measures, and Power Query scripts. |
| **[`marketing_dashboard_theme.json`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/powerbi/marketing_dashboard_theme.json)** | **Theme JSON** | Official custom theme palette (Purple `#4B2BD6`, Green `#10B981`, Sky `#0EA5E9`, Amber `#F59E0B`, Segoe UI typography). |
| **[`clean_marketing_data.csv`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/data/clean_marketing_data.csv)** | **CSV Dataset** | 680 preprocessed marketing records (Jan–Dec 2025, 6 channels, 14 campaigns). |
| **[`clean_marketing_data.xlsx`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/data/clean_marketing_data.xlsx)** | **Excel Dataset** | Formatted Excel workbook version with styled headers and currency formats. |

---

## 🚀 2. How to Open & Save as `.pbix`

### Option A: Open the Project Directly (Instant)
1. Open Power BI Desktop.
2. Go to **File > Open report > Browse reports** and select:
   👉 **`powerbi/Marketing_Performance_Dashboard.pbip`** (or double-click it in Windows File Explorer).
3. Power BI Desktop will automatically load the model, measures, and layout.
4. Click **Home > Refresh** to pull the latest numbers from `clean_marketing_data.csv`.
5. To save as a standalone `.pbix` file:
   - Click **File > Save As**.
   - In the "Save as type" dropdown, select **Power BI files (*.pbix)**.
   - Save as `Marketing_Performance_Dashboard.pbix`.

---

## 🛠️ 3. Complete DAX Measure Library (Copy & Paste)

If building or demonstrating from scratch in Power BI Desktop, click **Modeling > New Measure** (or right-click the table and choose **New Measure**) and use these exact DAX formulas:

### Core Volume & Financial Measures
```DAX
Total Spend = SUM(clean_marketing_data[spend])
```
*(Format as Currency: `₹#,##0`)*

```DAX
Total Revenue = SUM(clean_marketing_data[revenue])
```
*(Format as Currency: `₹#,##0`)*

```DAX
Total Clicks = SUM(clean_marketing_data[clicks])
```
*(Format as Whole Number: `#,##0`)*

```DAX
Total Impressions = SUM(clean_marketing_data[impressions])
```
*(Format as Whole Number: `#,##0`)*

```DAX
Total Conversions = SUM(clean_marketing_data[conversions])
```
*(Format as Whole Number: `#,##0`)*

```DAX
Net Profit = [Total Revenue] - [Total Spend]
```
*(Format as Currency: `₹#,##0`)*

---

### Efficiency & Ratio Measures
> **Important DAX Practice:** Always use `DIVIDE(Numerator, Denominator, 0)` rather than `/` to safeguard against division by zero errors on filtered slices.

```DAX
Average CTR = DIVIDE([Total Clicks], [Total Impressions], 0)
```
*(Format as Percentage: `0.00%`)*

```DAX
Conversion Rate = DIVIDE([Total Conversions], [Total Clicks], 0)
```
*(Format as Percentage: `0.00%`)*

```DAX
CPA = DIVIDE([Total Spend], [Total Conversions], 0)
```
*(Format as Currency: `₹#,##0.00`)*

```DAX
CPC = DIVIDE([Total Spend], [Total Clicks], 0)
```
*(Format as Currency: `₹#,##0.00`)*

```DAX
ROAS = DIVIDE([Total Revenue], [Total Spend], 0)
```
*(Format as Decimal Number: `0.00`)*

```DAX
ROI % = DIVIDE([Total Revenue] - [Total Spend], [Total Spend], 0)
```
*(Format as Percentage: `0.0%`)*

```DAX
Engagement Rate = 
DIVIDE(
    SUM(clean_marketing_data[likes]) + SUM(clean_marketing_data[shares]) + SUM(clean_marketing_data[comments]),
    [Total Impressions],
    0
)
```
*(Format as Percentage: `0.00%`)*

---

## 🎨 4. Step-by-Step Visual Layout Specification

To replicate the exact executive layout in Power BI Desktop:

### Page Setup
- **Canvas Size:** 16:9 (`1280 x 720` or `1920 x 1080`).
- **Theme:** Go to **View > Themes > Browse for themes**, select [`powerbi/marketing_dashboard_theme.json`](file:///d:/Project/marketing_dashboard_project/marketing_dashboard/powerbi/marketing_dashboard_theme.json).

### Top KPI Banner (4 Cards across the top)
1. **Card 1 (Left):** Measure `[Total Revenue]` (Callout value: `₹9,30,551`, Label: `Total Revenue`).
2. **Card 2:** Measure `[Total Spend]` (Callout value: `₹3,49,274`, Label: `Total Ad Spend`).
3. **Card 3:** Measure `[Average CTR]` (Callout value: `1.67%`, Label: `Average CTR`).
4. **Card 4 (Right):** Measure `[Total Conversions]` (Callout value: `13,074`, Label: `Conversions`).

### Row 1 Visuals
- **Left: 1. Revenue by Marketing Channel**
  - **Visual Type:** Clustered Bar Chart (Horizontal) or Donut Chart.
  - **Y-Axis:** `channel`
  - **X-Axis:** `[Total Revenue]`
  - **Data Labels:** On (`₹` values + percentage of total).
- **Right: 3. Monthly Revenue Trends**
  - **Visual Type:** Line and Clustered Column Chart.
  - **Shared X-Axis:** `month` (Date hierarchy: Month).
  - **Column Y-Axis:** `[Total Spend]` (Bar color: light violet `#A78BFA`).
  - **Line Y-Axis:** `[Total Revenue]` (Line color: deep purple `#4B2BD6`).
  - **Secondary Line Y-Axis (Optional):** `[ROI %]` (Line color: amber `#F59E0B`).

### Row 2 Visuals
- **Left: 2. Campaign Performance Comparison**
  - **Visual Type:** Clustered Bar Chart (Horizontal).
  - **Y-Axis:** `campaign`
  - **X-Axis:** `[Total Spend]` and `[Total Revenue]` (grouped bars).
- **Right: 4. Channel-wise Conversion Analysis**
  - **Visual Type:** Funnel Chart or Clustered Bar Chart.
  - **Category:** `channel`
  - **Values:** `[Total Conversions]`
  - **Tooltips:** `[Conversion Rate]`, `[CPA]`.

### Row 3 Visuals
- **Left: 5. ROI Comparison**
  - **Visual Type:** Clustered Bar Chart (Horizontal).
  - **Y-Axis:** `channel` (or `campaign`).
  - **X-Axis:** `[ROI %]`.
  - **Constant Reference Line:** Analytics pane > Constant Line at `1.0` (100% Target).
- **Right: Channel Scorecard**
  - **Visual Type:** Table or Matrix.
  - **Columns:** `channel`, `[Total Revenue]`, `[Total Spend]`, `[Average CTR]`, `[Conversion Rate]`, `[CPA]`, `[ROI %]`.

### Top Slicers
- **Slicer 1 (Date):** Field `date` (Between slider: `01/01/2025` to `31/12/2025`).
- **Slicer 2 (Channel):** Field `channel` (Dropdown or Tile style).
- **Slicer 3 (Campaign):** Field `campaign` (Dropdown).

---

## 📑 5. How to Export Report for Viva / Submission
1. In Power BI Desktop, click **File > Export > Export to PDF**.
2. Save the PDF report alongside your capstone documentation.
3. Commit and push the `powerbi/` folder to GitHub.
