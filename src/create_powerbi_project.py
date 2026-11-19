"""Generate the complete Power BI Project (.pbip), Template (.pbit), and theme for Marketing Performance Dashboard."""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBI_DIR = ROOT / "powerbi"
DATA_DIR = ROOT / "data"
CSV_PATH = (DATA_DIR / "clean_marketing_data.csv").resolve()

# ------------------------------------------------------------------ 1. Theme JSON
THEME_JSON = {
    "name": "MarketingPerformanceTheme",
    "dataColors": [
        "#4B2BD6",  # Primary Accent / Purple
        "#10B981",  # Green / High ROI / Success
        "#F59E0B",  # Amber / Warning / Medium
        "#0EA5E9",  # Sky Blue / LinkedIn
        "#EF4444",  # Red / Negative / Low
        "#8B5CF6",  # Violet / Facebook
        "#6366F1",  # Indigo
        "#EC4899"   # Pink
    ],
    "background": "#FFFFFF",
    "foreground": "#0F172A",
    "tableAccent": "#4B2BD6",
    "visualStyles": {
        "*": {
            "*": {
                "fontFamily": [{"fontFamily": "Segoe UI"}],
                "title": [
                    {"fontSize": 12, "fontColor": {"solid": {"color": "#0F172A"}}}
                ],
                "labels": [
                    {"fontSize": 10, "fontColor": {"solid": {"color": "#475569"}}}
                ]
            }
        },
        "card": {
            "*": {
                "labels": [{"fontSize": 24, "fontColor": {"solid": {"color": "#0F172A"}}}],
                "categoryLabels": [{"fontSize": 10, "fontColor": {"solid": {"color": "#475569"}}}]
            }
        }
    }
}

# ------------------------------------------------------------------ 2. Semantic Model (TMSL / model.bim)
MODEL_BIM = {
    "name": "Marketing_Performance_Dashboard",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {
            "legacyRedirects": True,
            "returnErrorValuesAsNull": True
        },
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "tables": [
            {
                "name": "clean_marketing_data",
                "columns": [
                    {"name": "date", "dataType": "dateTime", "formatString": "yyyy-mm-dd", "sourceColumn": "date"},
                    {"name": "campaign", "dataType": "string", "sourceColumn": "campaign"},
                    {"name": "channel", "dataType": "string", "sourceColumn": "channel"},
                    {"name": "impressions", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "impressions"},
                    {"name": "reach", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "reach"},
                    {"name": "clicks", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "clicks"},
                    {"name": "conversions", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "conversions"},
                    {"name": "spend", "dataType": "double", "formatString": "₹#,##0.00", "sourceColumn": "spend"},
                    {"name": "revenue", "dataType": "double", "formatString": "₹#,##0.00", "sourceColumn": "revenue"},
                    {"name": "likes", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "likes"},
                    {"name": "shares", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "shares"},
                    {"name": "comments", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "comments"},
                    {"name": "website_sessions", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "website_sessions"},
                    {"name": "bounce_rate", "dataType": "double", "formatString": "0.00%", "sourceColumn": "bounce_rate"},
                    {"name": "new_customers", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "new_customers"},
                    {"name": "month", "dataType": "dateTime", "formatString": "yyyy-mm", "sourceColumn": "month"},
                    {"name": "weekday", "dataType": "string", "sourceColumn": "weekday"}
                ],
                "partitions": [
                    {
                        "name": "clean_marketing_data-Partition",
                        "mode": "import",
                        "source": {
                            "type": "m",
                            "expression": [
                                'let',
                                f'    Source = Csv.Document(File.Contents("{str(CSV_PATH).replace(chr(92), "/")}").[Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"date", type date}, {"campaign", type text}, {"channel", type text}, {"impressions", Int64.Type}, {"reach", Int64.Type}, {"clicks", Int64.Type}, {"conversions", Int64.Type}, {"spend", type number}, {"revenue", type number}, {"likes", Int64.Type}, {"shares", Int64.Type}, {"comments", Int64.Type}, {"website_sessions", Int64.Type}, {"bounce_rate", type number}, {"new_customers", Int64.Type}, {"month", type date}, {"weekday", type text}})',
                                'in',
                                '    #"Changed Type"'
                            ]
                        }
                    }
                ],
                "measures": [
                    {
                        "name": "Total Revenue",
                        "expression": "SUM('clean_marketing_data'[revenue])",
                        "formatString": "₹#,##0"
                    },
                    {
                        "name": "Total Ad Spend",
                        "expression": "SUM('clean_marketing_data'[spend])",
                        "formatString": "₹#,##0"
                    },
                    {
                        "name": "Total Clicks",
                        "expression": "SUM('clean_marketing_data'[clicks])",
                        "formatString": "#,##0"
                    },
                    {
                        "name": "Total Impressions",
                        "expression": "SUM('clean_marketing_data'[impressions])",
                        "formatString": "#,##0"
                    },
                    {
                        "name": "Total Conversions",
                        "expression": "SUM('clean_marketing_data'[conversions])",
                        "formatString": "#,##0"
                    },
                    {
                        "name": "Net Profit",
                        "expression": "[Total Revenue] - [Total Ad Spend]",
                        "formatString": "₹#,##0"
                    },
                    {
                        "name": "Average CTR",
                        "expression": "DIVIDE([Total Clicks], [Total Impressions], 0)",
                        "formatString": "0.00%"
                    },
                    {
                        "name": "Conversion Rate",
                        "expression": "DIVIDE([Total Conversions], [Total Clicks], 0)",
                        "formatString": "0.00%"
                    },
                    {
                        "name": "Cost Per Acquisition (CPA)",
                        "expression": "DIVIDE([Total Ad Spend], [Total Conversions], 0)",
                        "formatString": "₹#,##0.00"
                    },
                    {
                        "name": "Cost Per Click (CPC)",
                        "expression": "DIVIDE([Total Ad Spend], [Total Clicks], 0)",
                        "formatString": "₹#,##0.00"
                    },
                    {
                        "name": "ROAS",
                        "expression": "DIVIDE([Total Revenue], [Total Ad Spend], 0)",
                        "formatString": "0.00"
                    },
                    {
                        "name": "ROI %",
                        "expression": "DIVIDE([Total Revenue] - [Total Ad Spend], [Total Ad Spend], 0)",
                        "formatString": "0.0%"
                    },
                    {
                        "name": "Engagement Rate",
                        "expression": "DIVIDE(SUM('clean_marketing_data'[likes]) + SUM('clean_marketing_data'[shares]) + SUM('clean_marketing_data'[comments]), [Total Impressions], 0)",
                        "formatString": "0.00%"
                    }
                ]
            }
        ]
    }
}

# ------------------------------------------------------------------ 3. Report Layout JSON
REPORT_LAYOUT = {
    "config": json.dumps({"version": "5.58", "theme": {"name": "MarketingPerformanceTheme", "type": 0}}),
    "layoutOptimization": 0,
    "publicCustomVisuals": [],
    "sections": [
        {
            "name": "ExecutiveOverview",
            "displayName": "Executive Overview",
            "displayOption": 1,
            "height": 720.0,
            "width": 1280.0,
            "filters": "[]",
            "config": "{}",
            "visualContainers": [
                # Card 1: Total Revenue
                {
                    "x": 24.0, "y": 80.0, "z": 0.0, "width": 290.0, "height": 110.0,
                    "config": json.dumps({
                        "name": "kpi_revenue",
                        "singleVisual": {"visualType": "card"},
                        "layouts": [{"id": 0, "position": {"x": 24.0, "y": 80.0, "z": 0.0, "width": 290.0, "height": 110.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "card"
                },
                # Card 2: Total Ad Spend
                {
                    "x": 334.0, "y": 80.0, "z": 1.0, "width": 290.0, "height": 110.0,
                    "config": json.dumps({
                        "name": "kpi_spend",
                        "singleVisual": {"visualType": "card"},
                        "layouts": [{"id": 0, "position": {"x": 334.0, "y": 80.0, "z": 1.0, "width": 290.0, "height": 110.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "card"
                },
                # Card 3: Average CTR
                {
                    "x": 644.0, "y": 80.0, "z": 2.0, "width": 290.0, "height": 110.0,
                    "config": json.dumps({
                        "name": "kpi_ctr",
                        "singleVisual": {"visualType": "card"},
                        "layouts": [{"id": 0, "position": {"x": 644.0, "y": 80.0, "z": 2.0, "width": 290.0, "height": 110.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "card"
                },
                # Card 4: Total Conversions
                {
                    "x": 954.0, "y": 80.0, "z": 3.0, "width": 300.0, "height": 110.0,
                    "config": json.dumps({
                        "name": "kpi_conversions",
                        "singleVisual": {"visualType": "card"},
                        "layouts": [{"id": 0, "position": {"x": 954.0, "y": 80.0, "z": 3.0, "width": 300.0, "height": 110.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "card"
                },
                # Visual 1: 1. Revenue by Marketing Channel (horizontal bar chart)
                {
                    "x": 24.0, "y": 210.0, "z": 4.0, "width": 520.0, "height": 240.0,
                    "config": json.dumps({
                        "name": "visual_ch_rev",
                        "singleVisual": {"visualType": "barChart"},
                        "layouts": [{"id": 0, "position": {"x": 24.0, "y": 210.0, "z": 4.0, "width": 520.0, "height": 240.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "barChart"
                },
                # Visual 3: 3. Monthly Revenue Trends (combo line + bar)
                {
                    "x": 564.0, "y": 210.0, "z": 5.0, "width": 690.0, "height": 240.0,
                    "config": json.dumps({
                        "name": "visual_monthly_trends",
                        "singleVisual": {"visualType": "lineClusteredColumnComboChart"},
                        "layouts": [{"id": 0, "position": {"x": 564.0, "y": 210.0, "z": 5.0, "width": 690.0, "height": 240.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "lineClusteredColumnComboChart"
                },
                # Visual 2: 2. Campaign Performance Comparison
                {
                    "x": 24.0, "y": 470.0, "z": 6.0, "width": 620.0, "height": 230.0,
                    "config": json.dumps({
                        "name": "visual_camp_perf",
                        "singleVisual": {"visualType": "clusteredBarChart"},
                        "layouts": [{"id": 0, "position": {"x": 24.0, "y": 470.0, "z": 6.0, "width": 620.0, "height": 230.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "clusteredBarChart"
                },
                # Visual 5: 5. ROI Comparison
                {
                    "x": 664.0, "y": 470.0, "z": 7.0, "width": 590.0, "height": 230.0,
                    "config": json.dumps({
                        "name": "visual_roi_comp",
                        "singleVisual": {"visualType": "barChart"},
                        "layouts": [{"id": 0, "position": {"x": 664.0, "y": 470.0, "z": 7.0, "width": 590.0, "height": 230.0}}]
                    }),
                    "filters": "[]",
                    "visualType": "barChart"
                }
            ]
        }
    ]
}


def build_powerbi_project():
    PBI_DIR.mkdir(exist_ok=True)
    report_dir = PBI_DIR / "Marketing_Performance_Dashboard.Report"
    model_dir = PBI_DIR / "Marketing_Performance_Dashboard.SemanticModel"
    def_dir = report_dir / "definition"

    report_dir.mkdir(exist_ok=True)
    model_dir.mkdir(exist_ok=True)
    def_dir.mkdir(exist_ok=True)

    # 1. PBIP file
    pbip_data = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Marketing_Performance_Dashboard.Report"
                }
            }
        ],
        "settings": {
            "enableAutoRecovery": True
        }
    }
    (PBI_DIR / "Marketing_Performance_Dashboard.pbip").write_text(json.dumps(pbip_data, indent=2), encoding="utf-8")

    # 2. definition.pbir
    pbir_data = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": "../Marketing_Performance_Dashboard.SemanticModel"
            }
        }
    }
    (report_dir / "definition.pbir").write_text(json.dumps(pbir_data, indent=2), encoding="utf-8")

    # 3. definition/report.json
    (def_dir / "report.json").write_text(json.dumps(REPORT_LAYOUT, indent=2), encoding="utf-8")

    # 4. definition.pbidataset
    pbidataset_data = {"version": "4.0"}
    (model_dir / "definition.pbidataset").write_text(json.dumps(pbidataset_data, indent=2), encoding="utf-8")

    # 5. model.bim
    (model_dir / "model.bim").write_text(json.dumps(MODEL_BIM, indent=2), encoding="utf-8")

    # 6. Theme JSON
    (PBI_DIR / "marketing_dashboard_theme.json").write_text(json.dumps(THEME_JSON, indent=2), encoding="utf-8")

    # 7. Generate a standalone .pbit (Power BI Template) zip archive
    pbit_path = PBI_DIR / "Marketing_Performance_Dashboard.pbit"
    with zipfile.ZipFile(pbit_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Override PartName="/Version" ContentType="" />
  <Override PartName="/Settings" ContentType="" />
  <Override PartName="/Metadata" ContentType="" />
  <Override PartName="/DataModelSchema" ContentType="" />
  <Override PartName="/Report/Layout" ContentType="" />
</Types>"""
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("Version", "1.28".encode("utf-16-le"))
        zf.writestr("Settings", "{}".encode("utf-16-le"))
        metadata = {"version": "1.0", "name": "Marketing_Performance_Dashboard"}
        zf.writestr("Metadata", json.dumps(metadata).encode("utf-16-le"))
        zf.writestr("DataModelSchema", json.dumps(MODEL_BIM).encode("utf-16-le"))
        zf.writestr("Report/Layout", json.dumps(REPORT_LAYOUT).encode("utf-16-le"))

    print(f"Generated Power BI Project (.pbip) at: {PBI_DIR / 'Marketing_Performance_Dashboard.pbip'}")
    print(f"Generated Power BI Template (.pbit) at: {pbit_path}")
    print(f"Generated Power BI Theme JSON at: {PBI_DIR / 'marketing_dashboard_theme.json'}")


if __name__ == "__main__":
    build_powerbi_project()
