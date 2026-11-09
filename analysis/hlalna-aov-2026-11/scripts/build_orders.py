import json,glob,hashlib,os,sys
import pandas as pd
S=sys.argv[1]
rows=[];items=[]
for f in sorted(glob.glob(S+'/raw/p*.json')):
    for o in json.load(open(f))['data']['structuredContent']['data']:
        cid=o.get('customer',{}).get('id')
        pseudo='C'+hashlib.sha256(f"hlalna-{cid}".encode()).hexdigest()[:8] if cid else None
        pm=o.get('payment_methods') or [{}]
        ra=(o.get('payment_actions') or {}).get('refund_action') or {}
        rows.append(dict(order_id=o['id'],ref=o.get('reference_id'),created=o['date']['date'][:19],
            total=float(o['total']['amount']),source=o.get('source'),status=o['status']['slug'],
            payment_method=o.get('payment_method'),provider=pm[0].get('provider'),
            paid=float(pm[0].get('amount') or 0) if pm else None,
            refund=float((ra.get('refund_amount') or {}).get('amount') or 0),
            cust=pseudo,city=(o.get('customer') or {}).get('city'),
            cust_created=((o.get('customer') or {}).get('created_at') or {}).get('date','')[:19],
            n_lines=len(o.get('items',[])),units=sum(i.get('quantity',0) for i in o.get('items',[]))))
        for i in o.get('items',[]):
            items.append(dict(order_id=o['id'],name=i['name'],qty=i.get('quantity')))
df=pd.DataFrame(rows); it=pd.DataFrame(items)
print(len(df), df.order_id.nunique()); 
df=df.drop_duplicates('order_id')
df.to_csv(S+'/work/orders.csv',index=False); it.to_csv(S+'/work/order_items.csv',index=False)
print(df.status.value_counts()); print(df.source.value_counts()); print(df.payment_method.value_counts())
print(df.created.min(), df.created.max())
