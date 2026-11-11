#!/usr/bin/env python3
"""One-day order analysis (2026-11-10) vs baselines. Usage: python3 -I scripts/analyze_day.py"""
import json, glob, os, re, statistics as st, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = {'canceled', 'deleted', 'payment_pending', 'request_quote'}
O = [o for f in glob.glob(os.path.join(root, 'data', 'orders_1110', '*.json')) for o in json.load(open(f))['orders']]
Q = [o for o in O if o['status_slug'] not in EX]
def band(x):
    for lim, lab in ((300, 'a <300'), (500, 'b 300-499'), (700, 'c 500-699'), (800, 'd 700-799'), (1000, 'e 800-999')):
        if x < lim: return lab
    return 'f 1000+'
SRC = lambda s: 'dashboard' if s == 'dashboard' else 'website' if s in ('store','complete_order','buy_as_gift') else 'app' if s and ('mobile' in s or 'mini' in s) else 'api' if s == 'api' else (s or 'other')
t = sorted(o['total'] for o in Q)
r = {'all_orders': len(O), 'status': Counter(o['status_slug'] for o in O), 'qualified': len(Q), 'sales': round(sum(t), 2), 'aov': round(sum(t)/len(t), 2),
     'median': st.median(t), 'p25': t[len(t)//4], 'p75': t[3*len(t)//4], 'share_800plus': round(sum(x >= 800 for x in t)/len(t), 3),
     'bands': sorted(Counter(band(x) for x in t).items()),
     'lines_per_order': round(sum(len(o['items']) for o in Q)/len(Q), 3), 'units_per_order': round(sum(sum(i['qty'] for i in o['items']) for o in Q)/len(Q), 3),
     'source': {}, 'payment': Counter(o['payment_method'] for o in Q).most_common(),
     'pending_payment_value': round(sum(o['total'] for o in O if o['status_slug'] == 'payment_pending'), 2),
     'canceled_value': round(sum(o['total'] for o in O if o['status_slug'] == 'canceled'), 2),
     'big_canceled_or_pending': sorted([o['total'] for o in O if o['status_slug'] in ('canceled', 'payment_pending') and o['total'] >= 800], reverse=True)}
by = defaultdict(list)
for o in Q: by[SRC(o['source'])].append(o['total'])
r['source'] = {k: (len(v), round(sum(v)/len(v), 1), sum(x >= 1000 for x in v), sum(x < 500 for x in v)) for k, v in by.items()}
# lead items in qualified orders, and single-box family
items = Counter(i['name'] for o in Q for i in o['items'])
r['top_items'] = items.most_common(15)
r['small_orders_lt500'] = Counter(i['name'] for o in Q if o['total'] < 500 for i in o['items']).most_common(10)
r['new_account_share'] = round(sum(1 for o in Q if o['cust_created'] and o['cust_created'][:10] >= o['created_at'][:10])/len(Q), 3)
r['hour_profile'] = sorted(Counter(int(o['created_at'][11:13])//6*6 for o in Q).items())
r['aov_trim_top1'] = round(sum(t[:-2])/len(t[:-2]), 1)
r['orders_1000_plus'] = sum(x >= 1000 for x in t)
r['orders_ge_800'] = sum(x >= 800 for x in t)
# dashboard baseline from last week pull
W = [o for f in glob.glob(os.path.join(root, 'data', 'orders_dashboard', 'w45_p*.json')) for o in json.load(open(f))['orders'] if o['status_slug'] not in EX]
r['dash_baseline_w45'] = (len(W), round(sum(o['total'] for o in W)/len(W), 1), round(sum(o['total'] >= 1000 for o in W)/len(W), 3))
json.dump(r, open(os.path.join(root, 'output', '20_day_2026-11-10.json'), 'w'), ensure_ascii=False, indent=1, default=list)
print(json.dumps(r, ensure_ascii=False, indent=1, default=list))
