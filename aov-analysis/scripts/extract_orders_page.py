#!/usr/bin/env python3
"""Extract a compact, pseudonymised record per order from one saved Salla orders_list page.
Usage: python3 -I extract_orders_page.py <tool_result_file> <day YYYY-MM-DD> <page>
Writes data/orders/<day>_p<page>.json  (no names / phones kept; customer id hashed)."""
import json, sys, hashlib, os
src, day, page = sys.argv[1], sys.argv[2], int(sys.argv[3])
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(src))
data = d.get('data', d)
sc = data.get('structuredContent')
if sc is None:
    txt = data['content'][0]['text']
    txt = txt.split('<<UNTRUSTED_STORE_DATA>>')[-1].split('<</UNTRUSTED_STORE_DATA>>')[0]
    sc = json.loads(txt)
def h(x):
    return None if x is None else hashlib.sha256(('kabsh-aov-'+str(x)).encode()).hexdigest()[:12]
out = []
for o in sc['data']:
    c = o.get('customer') or {}
    pa = (o.get('payment_actions') or {}).get('refund_action') or {}
    out.append({
        'order_id': o['id'], 'reference_id': o.get('reference_id'),
        'created_at': o['date']['date'][:19], 'tz': o['date'].get('timezone'),
        'total': o['total']['amount'], 'currency': o['total'].get('currency'),
        'source': o.get('source'),
        'status_slug': o['status'].get('slug'), 'status_name': o['status'].get('name'),
        'status_custom': (o['status'].get('customized') or {}).get('name'),
        'payment_method': o.get('payment_method'),
        'providers': [p.get('provider') for p in (o.get('payment_methods') or [])],
        'is_pending_payment': o.get('is_pending_payment'), 'draft': o.get('draft'),
        'duplicated': (o.get('features') or {}).get('duplicated'),
        'suspicious': (o.get('features') or {}).get('has_suspicious_alert'),
        'paid_amount': (pa.get('paid_amount') or {}).get('amount'),
        'refund_amount': (pa.get('refund_amount') or {}).get('amount'),
        'items': [{'name': i.get('name'), 'qty': i.get('quantity')} for i in (o.get('items') or [])],
        'cust': h(c.get('id')), 'cust_city': c.get('city'),
        'cust_created': ((c.get('created_at') or {}).get('date') or '')[:19] or None,
    })
pg = sc.get('pagination') or {}
res = {'day': day, 'page': page, 'observed_at': d.get('observed_at'),
       'pagination': {k: pg.get(k) for k in ('count', 'total', 'perPage', 'currentPage', 'totalPages')},
       'orders': out}
os.makedirs(os.path.join(root, 'data', 'orders'), exist_ok=True)
fn = os.path.join(root, 'data', 'orders', f'{day}_p{page}.json')
json.dump(res, open(fn, 'w'), ensure_ascii=False)
print(fn, 'orders', len(out), 'pagination', res['pagination'])
