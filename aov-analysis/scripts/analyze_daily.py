#!/usr/bin/env python3
"""AOV analysis from Salla reports_sales_over_time (daily). Reproducible: python3 -I scripts/analyze_daily.py"""
import json, os, math, csv, statistics as st
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(root, 'data', 'salla_sales_over_time_day.json')))
R = [dict(zip(d['columns'], r)) for r in d['rows']]
for r in R:
    n = r['sales_count']
    r['goods_net'] = r['sales'] - r['tax'] - r['sales_shipping_cost']          # goods after discount, ex VAT, ex shipping
    r['aov'] = r['sales'] / n
    r['aov_ex_vat'] = (r['sales'] - r['tax']) / n
    r['goods_per_order'] = r['goods_net'] / n
    r['tax_per_order'] = r['tax'] / n
    r['ship_per_order'] = r['sales_shipping_cost'] / n
    r['disc_per_order'] = r['discount'] / n
    r['gross_margin'] = (r['goods_net'] - r['sales_cost_price']) / r['goods_net']
    r['margin_per_order'] = (r['goods_net'] - r['sales_cost_price'] - r['sales_epayment_fee']) / n
    r['qualified_share'] = n / r['orders']
out = os.path.join(root, 'output'); os.makedirs(out, exist_ok=True)
cols = ['date','orders','sales_count','qualified_share','sales','tax','sales_shipping_cost','discount','goods_net','sales_cost_price','aov','aov_ex_vat','goods_per_order','tax_per_order','ship_per_order','disc_per_order','gross_margin','margin_per_order']
# 7-day moving AOV (sum/sum, not mean of means)
for i, r in enumerate(R):
    w = R[max(0, i-6):i+1]
    r['aov_ma7'] = sum(x['sales'] for x in w)/sum(x['sales_count'] for x in w) if len(w) == 7 else None
with open(os.path.join(out, '01_daily_metrics.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(cols+['aov_ma7'])
    for r in R: wr.writerow([round(r[c],4) if isinstance(r[c], float) else r[c] for c in cols]+[round(r['aov_ma7'],2) if r['aov_ma7'] else ''])
def agg(rows):
    n = sum(r['sales_count'] for r in rows); o = sum(r['orders'] for r in rows)
    s = {k: sum(r[k] for r in rows) for k in ['sales','tax','sales_shipping_cost','discount','goods_net','sales_cost_price','sales_epayment_fee']}
    return dict(days=len(rows), orders_all=o, orders_q=n, sales=s['sales'], aov=s['sales']/n, aov_ex_vat=(s['sales']-s['tax'])/n,
                goods=s['goods_net']/n, tax=s['tax']/n, ship=s['sales_shipping_cost']/n, disc=s['discount']/n,
                gm=(s['goods_net']-s['sales_cost_price'])/s['goods_net'], margin_per_order=(s['goods_net']-s['sales_cost_price']-s['sales_epayment_fee'])/n,
                margin_total=s['goods_net']-s['sales_cost_price']-s['sales_epayment_fee'], aov_all_orders=s['sales']/o)
P = lambda a, b: [r for r in R if a <= r['date'] <= b]
cur, prev = P('2026-11-02','2026-11-08'), P('2026-10-26','2026-11-01')
A, B = agg(cur), agg(prev)
rows = []
for k in A: rows.append([k, round(B[k],2), round(A[k],2), round(A[k]-B[k],2), (round((A[k]/B[k]-1)*100,2) if B[k] else '')])
with open(os.path.join(out, '02_period_comparison.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['metric','prev_2026-10-26..11-01','last_2026-11-02..11-08','diff','pct']); wr.writerows(rows)
# component bridge of AOV change (additive identity aov = goods + tax + shipping)
bridge = [['goods_after_discount_ex_vat', B['goods'], A['goods']], ['vat', B['tax'], A['tax']], ['shipping_fee', B['ship'], A['ship']]]
# day-type decomposition. The current week has NO peak day (>=250 orders), so a symmetric
# mix/rate split is degenerate. Use: within-effect = change of AOV on normal days only;
# peak-day (calendar) effect = total change - within-effect.
def dtype(r): return 'peak' if r['orders'] >= 250 else 'normal'
def seg(rows_, t):
    rr = [r for r in rows_ if dtype(r) == t]; n = sum(r['sales_count'] for r in rr)
    return n, (sum(r['sales'] for r in rr)/n if n else None), [r['date'] for r in rr]
pn, pa, pd_ = seg(prev,'peak'); nn0, na0, _ = seg(prev,'normal'); nn1, na1, _ = seg(cur,'normal'); cn, ca, _ = seg(cur,'peak')
within = na1 - na0; total = A['aov'] - B['aov']; peak_effect = total - within
seg_rows = [['peak_days(prev: '+' '.join(pd_)+')', pn, round(pa,2), cn, ca], ['normal_days', nn0, round(na0,2), nn1, round(na1,2)]]
with open(os.path.join(out, '03_decomposition_daytype.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['segment','prev_qualified_orders','prev_aov','cur_qualified_orders','cur_aov'])
    wr.writerows(seg_rows)
    wr.writerow(['effect: absence of peak days (calendar/payday)', '', '', '', round(peak_effect,2)])
    wr.writerow(['effect: lower AOV on comparable normal days', '', '', '', round(within,2)])
    wr.writerow(['TOTAL change', '', '', '', round(total,2)])
mix, value = peak_effect, within
with open(os.path.join(out, '04_bridge_components.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['component','prev_per_order','cur_per_order','contribution_sar'])
    for c, b, a in bridge: wr.writerow([c, round(b,2), round(a,2), round(a-b,2)])
    wr.writerow(['TOTAL (= AOV change)', round(B['aov'],2), round(A['aov'],2), round(A['aov']-B['aov'],2)])
# Welch-style daily check: daily AOV sd
da, db = [r['aov'] for r in cur], [r['aov'] for r in prev]
se = math.sqrt(st.variance(da)/len(da) + st.variance(db)/len(db))
print(json.dumps({'prev': {k: round(v,2) for k,v in B.items()}, 'cur': {k: round(v,2) for k,v in A.items()},
  'aov_diff': round(A['aov']-B['aov'],2), 'aov_pct': round((A['aov']/B['aov']-1)*100,2),
  'daily_aov_diff_mean': round(st.mean(da)-st.mean(db),2), 'se_daily': round(se,2), 't': round((st.mean(da)-st.mean(db))/se,2),
  'mix_effect_peak_days': round(mix,2), 'within_effect': round(value,2), 'segments': seg_rows,
  'bridge': [[c, round(a-b,2)] for c,b,a in bridge],
  'needed_to_800_from_cur_pct': round((800/A['aov']-1)*100,2)}, ensure_ascii=False, indent=1))
