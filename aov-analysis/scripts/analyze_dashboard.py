#!/usr/bin/env python3
"""Dashboard-source (manually entered) orders, last 7d vs previous 7d: AOV, distribution,
product-family mix/rate decomposition, cancellations. Inputs: data/orders_dashboard/w44_*.json, w45_*.json"""
import json, glob, os, re, csv, statistics as st, math, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decompose import decompose
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out = os.path.join(root, 'output')
W = {w: [o for f in sorted(glob.glob(os.path.join(root, 'data', 'orders_dashboard', f'{w}_p*.json'))) for o in json.load(open(f))['orders']] for w in ('w44', 'w45')}
EXCL = {'canceled', 'deleted', 'payment_pending', 'request_quote'}
# typical unit price per item = median total of single-item, qty-1 orders (both weeks); used only to pick the lead item
single = defaultdict(list)
for O in W.values():
    for o in O:
        if len(o['items']) == 1 and o['items'][0]['qty'] == 1 and o['status_slug'] not in EXCL: single[o['items'][0]['name']].append(o['total'])
typ = {k: st.median(v) for k, v in single.items()}
def family(name):
    if re.search('مع الرز|مفطح', name): return 'B_cooked_with_rice'
    if 'الجوهر' in name: return 'A_jawhar_value_sheep'
    if re.search('بوكس|مكس|box', name, re.I): return 'C_boxes_bundles'
    if re.search('حاشي|عجل', name) and typ.get(name, 0) >= 300: return 'E_camel_veal_large'
    if re.search('خروف|جذع|لباني|هرفي|رفيدي|سواكني|ناهي|نعيمي كشميري جذع', name) and typ.get(name, 0) >= 250: return 'D_fresh_sheep_whole_half'
    return 'F_small_cuts_addons'
def lead(o):
    return max(o['items'], key=lambda i: typ.get(i['name'], 0) * 1)['name'] if o['items'] else ''
def band(x):
    for lim, lab in ((300, 'a <300'), (500, 'b 300-499'), (700, 'c 500-699'), (800, 'd 700-799'), (1000, 'e 800-999')):
        if x < lim: return lab
    return 'f 1000+'
res = {}; rows_band = []; fam_rows = {}
for w, O in W.items():
    Q = [o for o in O if o['status_slug'] not in EXCL]; t = sorted(o['total'] for o in Q)
    q = lambda p: t[int(p*(len(t)-1))]
    sd = st.pstdev(t)
    res[w] = dict(all=len(O), canceled=sum(o['status_slug'] == 'canceled' for o in O), pending=sum(o['status_slug'] == 'payment_pending' for o in O),
                  qualified=len(Q), sales=sum(t), aov=sum(t)/len(t), ci95=1.96*sd/math.sqrt(len(t)), median=st.median(t), p25=q(.25), p75=q(.75),
                  share_800plus=sum(x >= 800 for x in t)/len(t), items_per_order=sum(sum(i['qty'] for i in o['items']) for o in Q)/len(Q),
                  lines_per_order=sum(len(o['items']) for o in Q)/len(Q),
                  pickup_share=sum(o['status_custom'] == 'تم التسليم من المعمل' for o in Q)/len(Q),
                  cod_share=sum(o['payment_method'] in ('cod', 'waiting') for o in Q)/len(Q))
    b = Counter(band(x) for x in t); rows_band.append((w, b, len(t), {k: sum(x for x in t if band(x) == k) for k in b}))
    fr = defaultdict(lambda: [0, 0.0])
    for o in Q: f = family(lead(o)); fr[f][0] += 1; fr[f][1] += o['total']
    fam_rows[w] = fr
    # outlier sensitivity: drop top 1% orders
    k = max(1, len(t)//100); res[w]['aov_trim_top1pct'] = sum(t[:-k])/len(t[:-k])
# write summary
with open(os.path.join(out, '11_dashboard_summary.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['metric', 'prev_2026-10-26..11-01', 'last_2026-11-02..11-08', 'diff'])
    for k in res['w44']:
        a, b = res['w44'][k], res['w45'][k]; wr.writerow([k, round(a, 4), round(b, 4), round(b-a, 4)])
with open(os.path.join(out, '12_dashboard_value_bands.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['band', 'prev_orders', 'prev_share', 'cur_orders', 'cur_share'])
    for lab in sorted(set(rows_band[0][1]) | set(rows_band[1][1])):
        wr.writerow([lab, rows_band[0][1][lab], round(rows_band[0][1][lab]/rows_band[0][2], 4), rows_band[1][1][lab], round(rows_band[1][1][lab]/rows_band[1][2], 4)])
fams = sorted(set(fam_rows['w44']) | set(fam_rows['w45']))
segs = [(f, fam_rows['w44'][f][0], fam_rows['w44'][f][1], fam_rows['w45'][f][0], fam_rows['w45'][f][1]) for f in fams]
rows, A0, A1, M, V = decompose(segs)
with open(os.path.join(out, '13_dashboard_decomp_family.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['lead_product_family', 'prev_orders', 'prev_share', 'prev_aov', 'cur_orders', 'cur_share', 'cur_aov', 'mix_effect_sar', 'within_effect_sar'])
    wr.writerows(rows); wr.writerow(['TOTAL', '', '', round(A0, 2), '', '', round(A1, 2), round(M, 2), round(V, 2)])
# top lead items change
lc = {w: Counter(lead(o) for o in O if o['status_slug'] not in EXCL) for w, O in W.items()}
with open(os.path.join(out, '14_dashboard_lead_items.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['lead_item', 'family', 'typical_price', 'prev_orders', 'cur_orders', 'diff'])
    for n in sorted(set(lc['w44']) | set(lc['w45']), key=lambda n: -(lc['w44'][n]+lc['w45'][n])):
        wr.writerow([n, family(n), typ.get(n, ''), lc['w44'][n], lc['w45'][n], lc['w45'][n]-lc['w44'][n]])
# cancellations by family (all orders)
cr = {w: Counter(family(lead(o)) for o in O if o['status_slug'] == 'canceled') for w, O in W.items()}
ca = {w: Counter(family(lead(o)) for o in O) for w, O in W.items()}
with open(os.path.join(out, '15_dashboard_cancellations.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['family', 'prev_all', 'prev_canceled', 'prev_cancel_rate', 'cur_all', 'cur_canceled', 'cur_cancel_rate', 'cur_canceled_value'])
    for fm in fams:
        cv = sum(o['total'] for o in W['w45'] if o['status_slug'] == 'canceled' and family(lead(o)) == fm)
        wr.writerow([fm, ca['w44'][fm], cr['w44'][fm], round(cr['w44'][fm]/ca['w44'][fm], 3) if ca['w44'][fm] else '', ca['w45'][fm], cr['w45'][fm], round(cr['w45'][fm]/ca['w45'][fm], 3) if ca['w45'][fm] else '', round(cv, 2)])
print(json.dumps({w: {k: round(v, 3) for k, v in r.items()} for w, r in res.items()}, indent=1, ensure_ascii=False))
for fn in ('12_dashboard_value_bands.csv', '13_dashboard_decomp_family.csv', '15_dashboard_cancellations.csv'): print(open(os.path.join(out, fn), encoding='utf-8-sig').read())
print(open(os.path.join(out, '14_dashboard_lead_items.csv'), encoding='utf-8-sig').read()[:2500])
