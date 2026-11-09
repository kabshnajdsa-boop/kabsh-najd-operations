import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
df=pd.read_csv('orders.csv',parse_dates=['created','cust_created'])
it=pd.read_csv('order_items.csv'); pr=pd.read_csv('products.csv')
# product map: prefer status sale/out over hidden for duplicates
pr['rank']=pr.status.map({'sale':0,'out':1,'hidden':2})
pm=pr.sort_values('rank').drop_duplicates('name')
def cat(row):
    n=row['name']; c=str(row.get('cats',''))
    if 'مطبخ حلالنا' in c or 'محمر' in n or 'مفطح' in n: return 'مطبخ حلالنا (مطبوخ)'
    if n.startswith('الباقة'): return 'باقات خدمة/إضافات'
    if 'ذبائح كاملة' in c or n in ('نصف حاشي محلي','حاشي كامل','ربع حاشي محلي'): return 'ذبائح كاملة (نيء)'
    if 'بوكس' in n: return 'بوكسات'
    if 'نصف خروف' in n: return 'نصف خروف جذع'
    return 'قطعيات ومفروم'
pm['category']=pm.apply(cat,axis=1)
it=it.merge(pm[['name','price','cost','category','weight']],on='name',how='left')
it['category']=it.category.fillna('غير مطابق للكتالوج')
it['est_value']=it.qty*it.price
it['est_weight']=np.where(it.weight>0.2, it.qty*it.weight, np.nan)
it.to_csv('items_enriched.csv',index=False)
# order flags
NONQ={'canceled','deleted','payment_pending','request_quote','restored'}
df['day']=df.created.dt.normalize()
df['is_zero']=df.total<=0
df['qualified']=(~df.status.isin(NONQ))&(~df.is_zero)
# channel
def chan(s):
    if s=='store': return 'الموقع'
    if str(s).startswith('mini-mobile') or s=='mobile': return 'تطبيق الجوال'
    if str(s).startswith('mini-twilight'): return 'متجر مصغّر/رابط (twilight)'
    if s=='api': return 'API/تكامل'
    if s=='dashboard': return 'لوحة التحكم (يدوي)'
    if s in ('buy_now','one-click','complete_order','reorder','buy_as_gift'): return 'شراء سريع/إعادة طلب/هدية'
    return 'أخرى'
df['channel']=df.source.map(chan)
# new vs returning: first order ever within data? use customer created date + order history in data
df=df.sort_values('created')
df['cust_order_n']=df[df.qualified].groupby('cust').cumcount()+1
df['cust_order_n']=df['cust_order_n'].fillna(0)
df['acct_age_days']=(df.created-df.cust_created).dt.total_seconds()/86400
# returning if prior qualified order in dataset OR account created >2 days before order (likely earlier history pre-window)
df['returning']=(df.cust_order_n>1)|(df.acct_age_days>2)
# per-order category mix
ag=it.groupby(['order_id','category']).est_value.sum().unstack(fill_value=0)
ag['_tot']=ag.sum(axis=1)
prim=ag.drop(columns='_tot').idxmax(axis=1)
df=df.merge(prim.rename('primary_cat'),left_on='order_id',right_index=True,how='left')
w=it.groupby('order_id').agg(est_weight=('est_weight','sum'),est_list_value=('est_value','sum'),unmatched=('price',lambda s:s.isna().sum()))
df=df.merge(w,left_on='order_id',right_index=True,how='left')
df['mixed_cats']=df.order_id.map((ag.drop(columns='_tot')>0).sum(axis=1))
df['period30']=np.select([ (df.day>='2026-10-10')&(df.day<='2026-11-08'), (df.day>='2026-09-10')&(df.day<='2026-10-09')],['آخر 30 يوم','الـ30 السابقة'],'')
df['wk']=np.select([(df.day>='2026-11-02')&(df.day<='2026-11-08'),(df.day>='2026-10-26')&(df.day<='2026-11-01'),(df.day>='2026-10-10')&(df.day<='2026-10-25')],['L7','P7','early'],'')
df.to_pickle('orders_enriched.pkl')
