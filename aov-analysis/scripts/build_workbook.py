#!/usr/bin/env python3
"""Build output/kabsh_aov_analysis.xlsx from output/*.csv plus evidence/gap registers."""
import csv, os, glob, openpyxl
from openpyxl.styles import Font, PatternFill
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out = os.path.join(root, 'output')
wb = openpyxl.Workbook(); wb.remove(wb.active)
def sheet(name, rows):
    ws = wb.create_sheet(name[:31]); ws.sheet_view.rightToLeft = False
    for r in rows: ws.append(r)
    for c in ws[1]: c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDEBF7')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = min(60, max(12, max(len(str(c.value or '')) for c in col)+2))
def from_csv(name, fn): sheet(name, list(csv.reader(open(os.path.join(out, fn), encoding='utf-8-sig'))))
sheet('README', [
 ['item','value'],
 ['company','kabsh — كبش نجد (Salla merchant 1562055600, verified via JOUD salla_connection_status)'],
 ['extracted_at','2026-11-09 07:36–07:39 UTC (10:36–10:39 Asia/Riyadh)'],
 ['analysis window requested','2026-10-10 .. 2026-11-08 (30 complete days, Asia/Riyadh)'],
 ['window actually covered','2026-10-25 .. 2026-11-08 (Salla reports service returns zeros before 10-25 although orders exist -> NOT AVAILABLE, not zero)'],
 ['last 7 days','2026-11-02 .. 2026-11-08'], ['previous 7 days','2026-10-26 .. 2026-11-01'],
 ['AOV definition (primary, matches Salla report)','sales (incl. 15% VAT + shipping fee, after discounts) / sales_count (qualified orders; excludes pending-payment/cancelled etc. per Salla reports service)'],
 ['source','JOUD gateway -> joud-salla-full-v1 -> salla_full_read_reports_sales_over_time (grain=day) and reports_sales_summary(compare=previous_period)'],
 ['scripts','scripts/analyze_daily.py (metrics, comparison, decomposition), scripts/extract_orders_page.py (order-level, pending), scripts/build_workbook.py'],
 ['update 2026-11-09 12:15 Riyadh','gateway back: added channel split, full dashboard order pull (660 orders), product report; sequential calls only'],
 ['status','PARTIAL — JOUD gateway stopped responding at ~07:40 UTC; order-level, GA4, Clarity, Odoo reads not completed. See 07_data_gaps.'],
])
from_csv('01_daily_metrics', '01_daily_metrics.csv')
from_csv('02_period_comparison', '02_period_comparison.csv')
from_csv('03_decomp_daytype', '03_decomposition_daytype.csv')
from_csv('04_bridge_components', '04_bridge_components.csv')
from_csv('05_weekday_pairs', '05_weekday_pairs.csv')
from_csv('06_recommendations', '06_recommendations.csv')
from_csv('07_data_gaps', '07_data_gaps.csv')
from_csv('08_reconciliation', '08_reconciliation.csv')
from_csv('09_clarity_ux_log', '09_clarity_ux_log.csv')
for n in ('10_decomp_channel','11_dashboard_summary','12_dashboard_value_bands','13_dashboard_decomp_family','14_dashboard_lead_items','15_dashboard_cancellations','16_contribution_summary'):
    from_csv(n, n + '.csv')
fn = os.path.join(out, 'kabsh_aov_analysis.xlsx'); wb.save(fn); print(fn)
