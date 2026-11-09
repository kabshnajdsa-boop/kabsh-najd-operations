"""Build the Halalna AOV workbook from the pseudonymised order extract.

Usage:  python3 build_workbook.py <analysis_dir>
Inputs (in <analysis_dir>/data): orders.csv, order_items.csv, products.csv,
         external_inputs.json (GA4 / ads / Salla report figures captured via JOUD).
Output: <analysis_dir>/hlalna_aov_analysis_2026-11-09.xlsx

Metric definition (primary):
  AOV = SUM(order.total) / COUNT(DISTINCT qualified orders)
  order.total = Salla final order amount (products after discount + shipping + COD fee + VAT).
  Qualified = status NOT IN {canceled, deleted, payment_pending, request_quote, restored}
              AND total > 0 (zero-value dashboard orders excluded as internal/test).
  Dates = order creation date, Asia/Riyadh.
"""
import json, sys, os, itertools, collections
import numpy as np, pandas as pd

BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, 'data')
df = pd.read_csv(os.path.join(D, 'orders.csv'), parse_dates=['created', 'cust_created'])
it = pd.read_csv(os.path.join(D, 'order_items.csv'))
pr = pd.read_csv(os.path.join(D, 'products.csv'))
ext = json.load(open(os.path.join(D, 'external_inputs.json'), encoding='utf-8'))

NONQ = {'canceled', 'deleted', 'payment_pending', 'request_quote', 'restored'}
df['day'] = df.created.dt.normalize()
df['is_zero'] = df.total <= 0
df['qualified'] = (~df.status.isin(NONQ)) & (~df.is_zero)

def chan(s):
    s = str(s)
    if s == 'store': return 'الموقع'
    if s.startswith('mini-mobile') or s == 'mobile': return 'تطبيق الجوال'
    if s.startswith('mini-twilight'): return 'متجر مصغّر/رابط'
    if s == 'api': return 'API/تكامل'
    if s == 'dashboard': return 'لوحة التحكم (يدوي)'
    if s in ('buy_now', 'one-click', 'complete_order', 'reorder', 'buy_as_gift'): return 'شراء سريع/إعادة طلب/هدية'
    return 'أخرى'
df['channel'] = df.source.map(chan)

pr['rank'] = pr.status.map({'sale': 0, 'out': 1, 'hidden': 2})
pm = pr.sort_values('rank').drop_duplicates('name').copy()
def cat(r):
    n, c = r['name'], str(r.get('cats', ''))
    if 'مطبخ حلالنا' in c or 'محمر' in n or 'مفطح' in n: return 'مطبخ حلالنا (مطبوخ)'
    if n.startswith('الباقة'): return 'باقات خدمة/إضافات'
    if 'ذبائح كاملة' in c or n in ('نصف حاشي محلي', 'حاشي كامل', 'ربع حاشي محلي'): return 'ذبائح كاملة (نيء)'
    if 'بوكس' in n: return 'بوكسات'
    if 'نصف خروف' in n: return 'نصف خروف جذع'
    return 'قطعيات ومفروم'
pm['category'] = pm.apply(cat, axis=1)
it = it.merge(pm[['name', 'price', 'cost', 'category', 'weight']], on='name', how='left')
it['est_value'] = it.qty * it.price
ag = it.groupby(['order_id', 'category']).est_value.sum().unstack(fill_value=0)
df = df.merge(ag.idxmax(axis=1).rename('primary_cat'), left_on='order_id', right_index=True, how='left')
wt = it.assign(w=np.where(it.weight > 0.2, it.qty * it.weight, np.nan)).groupby('order_id').w.sum(min_count=1)
df = df.merge(wt.rename('est_kg'), left_on='order_id', right_index=True, how='left')

df = df.sort_values('created')
first_q = df[df.qualified].groupby('cust').created.transform('min')
df.loc[df.qualified, 'first_in_window'] = df.loc[df.qualified, 'created'].eq(first_q)
df['acct_age_days'] = (df.created - df.cust_created).dt.total_seconds() / 86400
df['customer_type'] = np.where((df.first_in_window == False) | (df.acct_age_days > 2), 'عائد', 'جديد')
BANDS = [-1, 500, 700, 900, 1200, 1e9]; BL = ['<500', '500-699', '700-899', '900-1199', '1200+']
df['band'] = pd.cut(df.total, BANDS, right=False, labels=BL)

q = df[df.qualified].copy()
WIN = {
    'L7: 2–8 نوفمبر': ('2026-11-02', '2026-11-08'),
    'P7: 26 أكتوبر–1 نوفمبر': ('2026-10-26', '2026-11-01'),
    'Prior23: 10 أكتوبر–1 نوفمبر': ('2026-10-10', '2026-11-01'),
    'Last30: 10 أكتوبر–8 نوفمبر': ('2026-10-10', '2026-11-08'),
    'Prev30: 10 سبتمبر–9 أكتوبر': ('2026-09-10', '2026-10-09'),
    'نفس مرحلة الشهر السابق قبل: 26 سبتمبر–1 أكتوبر': ('2026-09-26', '2026-10-01'),
    'نفس مرحلة الشهر السابق بعد: 2–8 أكتوبر': ('2026-10-02', '2026-10-08'),
}
sel = lambda d, w: d[(d.day >= WIN[w][0]) & (d.day <= WIN[w][1])]

def summ(x, allx=None):
    o = dict(
        orders=len(x), sales_sar=round(x.total.sum(), 2), aov=round(x.total.mean(), 1),
        median=round(x.total.median(), 1), p25=round(x.total.quantile(.25), 1), p75=round(x.total.quantile(.75), 1),
        share_ge_900=round((x.total >= 900).mean(), 3), lines_per_order=round(x.n_lines.mean(), 2),
        units_per_order=round(x.units.mean(), 2), est_kg_per_order=round(x.est_kg.mean(), 2),
        returning_share=round((x.customer_type == 'عائد').mean(), 3),
        aov_trim_top2pct=round(x.total[x.total <= x.total.quantile(.98)].mean(), 1),
        aov_ex_top5_orders=round(x.total.sort_values().iloc[:-5].mean(), 1) if len(x) > 10 else None)
    if allx is not None:
        o['canceled_orders'] = int((allx.status == 'canceled').sum())
        o['cancel_rate'] = round((allx.status == 'canceled').mean(), 3)
        o['returned_orders'] = int((allx.status == 'restored').sum())
    return o

allnz = df[~df.is_zero]
periods = pd.DataFrame({w: summ(sel(q, w), sel(allnz, w)) for w in WIN}).T
rng = np.random.default_rng(7)
def boot(a, b, n=5000):
    d = [rng.choice(b.total, len(b)).mean() - rng.choice(a.total, len(a)).mean() for _ in range(n)]
    return np.percentile(d, [2.5, 97.5]).round(1)
ci1 = boot(sel(q, 'P7: 26 أكتوبر–1 نوفمبر'), sel(q, 'L7: 2–8 نوفمبر'))
ci2 = boot(sel(q, 'Prior23: 10 أكتوبر–1 نوفمبر'), sel(q, 'L7: 2–8 نوفمبر'))

# daily table
g = q[q.day >= '2026-09-10'].groupby('day')
daily = pd.DataFrame({
    'orders': g.size(), 'sales_sar': g.total.sum().round(2), 'aov': g.total.mean().round(1),
    'median': g.total.median().round(1), 'p25': g.total.quantile(.25).round(1), 'p75': g.total.quantile(.75).round(1),
    'share_ge_900': g.total.apply(lambda s: (s >= 900).mean()).round(3),
    'lines_per_order': g.n_lines.mean().round(2), 'units_per_order': g.units.mean().round(2),
    'est_kg_per_order': g.est_kg.mean().round(2),
    'returning_share': g.customer_type.apply(lambda s: (s == 'عائد').mean()).round(3)})
daily = daily.reindex(pd.date_range('2026-09-10', '2026-11-08'))
daily['orders'] = daily.orders.fillna(0)  # a day with no qualified orders = 0 orders (true zero)
daily['sales_sar'] = daily.sales_sar.fillna(0)
daily['aov_ma7_weighted'] = (daily.sales_sar.rolling(7).sum() / daily.orders.rolling(7).sum()).round(1)
ca = allnz.groupby('day').status.apply(lambda s: (s == 'canceled').sum())
daily['canceled_orders'] = ca.reindex(daily.index).fillna(0).astype(int)
daily['weekday'] = daily.index.day_name()
rep = pd.DataFrame(ext['salla_reports_daily']).set_index('date')
rep.index = pd.to_datetime(rep.index)
daily = daily.join(rep.add_prefix('salla_report_'))
daily.index.name = 'date'

# decomposition helper (symmetric shift-share; exact)
def decomp(a, b, col):
    A0, A1 = a.total.mean(), b.total.mean(); Ab = (A0 + A1) / 2
    g0 = a.groupby(col, observed=True).total.agg(['count', 'mean']); g1 = b.groupby(col, observed=True).total.agg(['count', 'mean'])
    t = g0.join(g1, lsuffix='_P', rsuffix='_L', how='outer')
    t[['count_P', 'count_L']] = t[['count_P', 'count_L']].fillna(0)
    t['share_P'] = t.count_P / t.count_P.sum(); t['share_L'] = t.count_L / t.count_L.sum()
    aP = t.mean_P.fillna(t.mean_L); aL = t.mean_L.fillna(t.mean_P)
    t['mix_effect_sar'] = (t.share_L - t.share_P) * ((aP + aL) / 2 - Ab)
    t['within_effect_sar'] = (t.share_P + t.share_L) / 2 * (aL - aP)
    t['total_effect_sar'] = t.mix_effect_sar + t.within_effect_sar
    t = t.round(2)
    tot = pd.DataFrame([{**{c: None for c in t.columns}, 'mix_effect_sar': round(t.mix_effect_sar.sum(), 2),
                         'within_effect_sar': round(t.within_effect_sar.sum(), 2),
                         'total_effect_sar': round(A1 - A0, 2)}], index=['الإجمالي (=ΔAOV)'])
    return pd.concat([t, tot])
P7 = sel(q, 'P7: 26 أكتوبر–1 نوفمبر'); L7 = sel(q, 'L7: 2–8 نوفمبر'); E23 = sel(q, 'Prior23: 10 أكتوبر–1 نوفمبر')
dec = {}
for col, nm in [('primary_cat', 'الفئة الرئيسية للطلب'), ('band', 'شريحة القيمة'), ('channel', 'قناة الإنشاء'),
                ('payment_method', 'طريقة الدفع'), ('customer_type', 'جديد/عائد')]:
    dec[nm + ' | P7→L7'] = decomp(P7, L7, col)
dec['الفئة الرئيسية للطلب | Prior23→L7'] = decomp(E23, L7, 'primary_cat')

# product mix by period
qq = q.assign(per=np.select([(q.day >= '2026-11-02'), (q.day >= '2026-10-26'), (q.day >= '2026-10-10')], ['L7', 'P7', 'E16'], 'Prev30'))
x = it.merge(qq[['order_id', 'per']], on='order_id')
pmix = x.pivot_table(index=['category', 'name'], columns='per', values='order_id', aggfunc='nunique', fill_value=0)
n = qq.per.value_counts()
for c in ['Prev30', 'E16', 'P7', 'L7']: pmix[c + ' % of orders'] = (pmix[c] / n[c] * 100).round(1)
pmix = pmix.merge(pm.set_index('name')[['price', 'cost']], left_on='name', right_index=True, how='left').reset_index()
pmix['margin_pct_if_cost_known'] = np.where(pd.to_numeric(pmix.cost, errors='coerce') > 0,
                                            (1 - pd.to_numeric(pmix.cost, errors='coerce') / pmix.price).round(3), np.nan)

# co-purchase & single line
oq = it[it.order_id.isin(q[q.day >= '2026-10-10'].order_id)].groupby('order_id').name.apply(lambda s: sorted(set(s)))
pairs = collections.Counter(p for l in oq for p in itertools.combinations(l, 2))
copur = pd.DataFrame([(a, b, c) for (a, b), c in pairs.most_common(25)], columns=['product_a', 'product_b', 'orders_together_last30'])
single = oq[oq.apply(len) == 1].apply(lambda l: l[0]).value_counts().rename('single_line_orders_last30').reset_index()

# segment tables
def seg(col):
    t = qq[qq.per.isin(['P7', 'L7'])].groupby([col, 'per'], observed=True).total.agg(['count', 'mean']).unstack('per').round(1)
    t.columns = [f'{a}_{b}' for a, b in t.columns]; return t.reset_index()
cust_tbl = seg('customer_type'); city_top = q.city.value_counts().head(6).index
qq['city_grp'] = np.where(qq.city.isin(city_top), qq.city, 'أخرى'); city_tbl = seg('city_grp')
chan_tbl = seg('channel'); pay_tbl = seg('payment_method')
w60 = allnz[allnz.day >= '2026-09-10']
canc_band = w60.groupby('band', observed=True).status.apply(lambda s: (s == 'canceled').mean()).round(3).rename('cancel_rate').to_frame().join(w60.groupby('band', observed=True).size().rename('orders_incl_canceled'))
canc_pay = w60.groupby('payment_method').status.apply(lambda s: (s == 'canceled').mean()).round(3).rename('cancel_rate').to_frame().join(w60.groupby('payment_method').size().rename('orders_incl_canceled'))
q60 = q[q.day >= '2026-09-10'].copy()
q60['dom_band'] = pd.cut(q60.day.dt.day, [0, 5, 10, 20, 25, 31], labels=['1-5', '6-10', '11-20', '21-25', '26-31'])
dom_tbl = q60.groupby('dom_band', observed=True).total.agg(['count', 'mean', 'median']).round(1).reset_index()
dow_tbl = q60.groupby(q60.day.dt.day_name()).total.agg(['count', 'mean', 'median']).round(1).reset_index()
band_tbl = qq[qq.per.isin(['P7', 'L7', 'Prev30'])].groupby(['band', 'per'], observed=True).total.agg(['count', 'mean']).unstack('per').round(1)
band_tbl.columns = [f'{a}_{b}' for a, b in band_tbl.columns]
for p in ['Prev30', 'P7', 'L7']: band_tbl[f'share_{p}'] = (band_tbl[f'count_{p}'] / band_tbl[f'count_{p}'].sum()).round(3)
band_tbl = band_tbl.reset_index()

# funnel (GA4 website, JOUD direct)
ga = pd.DataFrame(ext['ga4_website_daily'])
ga['week'] = np.where(ga.date >= '2026-11-02', 'L7', 'P7')
gw = ga.groupby('week')[['users', 'sessions', 'item_views', 'add_to_carts', 'checkouts', 'purchases']].sum()
gw['view_per_session'] = (gw.item_views / gw.sessions).round(3)
gw['atc_per_session'] = (gw.add_to_carts / gw.sessions).round(4)
gw['checkout_per_atc'] = (gw.checkouts / gw.add_to_carts).round(3)
gw['purchase_per_checkout'] = (gw.purchases / gw.checkouts).round(3)
gw['purchase_per_session'] = (gw.purchases / gw.sessions).round(4)
site = q[q.channel == 'الموقع']
gw['salla_site_orders'] = [len(site[(site.day >= '2026-11-02') & (site.day <= '2026-11-08')]) if w == 'L7' else len(site[(site.day >= '2026-10-26') & (site.day <= '2026-11-01')]) for w in gw.index]
gw['ga4_purchase_coverage_vs_salla_site'] = (gw.purchases / gw.salla_site_orders).round(3)
gw['salla_site_sales'] = [site[(site.day >= ('2026-11-02' if w == 'L7' else '2026-10-26')) & (site.day <= ('2026-11-08' if w == 'L7' else '2026-11-01'))].total.sum().round(0) for w in gw.index]
gw['revenue_per_session_site'] = (gw.salla_site_sales / gw.sessions).round(2)
gw = gw.reset_index()
carts = pd.DataFrame(ext['salla_carts_summary']).T.reset_index().rename(columns={'index': 'week'})
ads = pd.DataFrame(ext['ads_spend']).reset_index(drop=True)

# recommendations & simulation
last30 = sel(q, 'Last30: 10 أكتوبر–8 نوفمبر'); base = last30.total.mean()
single_share = (last30.n_lines == 1).mean()
small_med_box_share = last30.order_id.isin(it[it.name.isin(['بوكس حري بلدي صغير', 'بوكس حري بلدي وسط', 'بوكس نعيمي بلدي صغير', 'بوكس نعيمي بلدي وسط'])].order_id).mean()
band_500_749 = ((last30.total >= 500) & (last30.total < 750)).mean()
share_1200 = (last30.total >= 1200).mean(); mean_1200 = last30.total[last30.total >= 1200].mean(); mean_lt500 = last30.total[last30.total < 500].mean()
recs = [
    dict(id='R1', name='إضافة مكمّلة داخل السلة للطلبات أحادية المنتج', eligible_share=single_share, adopt_cons=0.08, adopt_like=0.15, net_add_cons=95, net_add_like=130,
         evidence=f'{single_share:.0%} من طلبات آخر 30 يومًا تحتوي منتجًا واحدًا؛ أكثر الأزواج شراءً معًا قطعيات نعيمي 1 كجم (كتف+موزات يد، ريش+كتف) والكبدة'),
    dict(id='R2', name='سلّم الحجم في البوكسات (صغير→وسط→كبير) وعرض الكمية الحالي على البوكس الكبير', eligible_share=small_med_box_share, adopt_cons=0.06, adopt_like=0.12, net_add_cons=300, net_add_like=320,
         evidence=f'{small_med_box_share:.0%} من الطلبات تحتوي بوكس صغير/وسط؛ الفرق السعري الحالي 324/300 ريال؛ انخفاض بوكس حري وسط ونعيمي كبير في L7'),
    dict(id='R3', name='حد توصيل مجاني عند 750 ريال (اختبار)', eligible_share=band_500_749, adopt_cons=0.10, adopt_like=0.20, net_add_cons=110, net_add_like=150,
         evidence=f'{band_500_749:.0%} من الطلبات بين 500 و749؛ رسوم التوصيل المحصّلة ≈ 27.5 ريال/طلب (تقارير سلة)'),
    dict(id='R4', name='إعادة توازن الإنفاق نحو نية الذبائح والبوكسات الكبيرة (بحث Google نعيمي/حري + Shopping)', eligible_share=None, adopt_cons=None, adopt_like=None, net_add_cons=None, net_add_like=None,
         evidence='Google: −29% بحث نعيمي/حري و−18% Shopping؛ Meta +22% منها حملة «منتجات مطبخ فقط» +74%؛ حصة طلبات ≥1200 هبطت من 14% إلى 9%'),
    dict(id='R5', name='تقويم شهري: إبراز «الثلاجة الشهرية» والبوكسات الكبيرة في أيام 1–10', eligible_share=None, adopt_cons=None, adopt_like=None, net_add_cons=None, net_add_like=None,
         evidence='متوسط أيام 6–10 = أدنى نقطة في الشهر؛ نفس النمط في أكتوبر (745→698)'),
]
rows = []
for r in recs:
    if r['eligible_share'] is not None:
        r['aov_lift_cons'] = round(r['eligible_share'] * r['adopt_cons'] * r['net_add_cons'], 1)
        r['aov_lift_like'] = round(r['eligible_share'] * r['adopt_like'] * r['net_add_like'], 1)
    rows.append(r)
# R4: share of >=1200 orders replacing <500 orders
r4c, r4l = 0.015, 0.03
recs[3]['aov_lift_cons'] = round(r4c * (mean_1200 - mean_lt500), 1); recs[3]['aov_lift_like'] = round(r4l * (mean_1200 - mean_lt500), 1)
recs[3]['eligible_share'] = f'نقل {r4c:.1%}/{r4l:.0%} من الطلبات من <500 إلى ≥1200'
recs[4]['aov_lift_cons'] = 5.0; recs[4]['aov_lift_like'] = 15.0
recs[4]['eligible_share'] = 'طلبات أيام 1–10 (~37%)'
rec_df = pd.DataFrame(rows)
overlap = 0.85  # haircut for interactions between levers acting on the same baskets
sim = pd.DataFrame([
    dict(scenario='محافظ', base_aov_last30=round(base, 1), gross_lift=rec_df.aov_lift_cons.sum(), overlap_haircut=1 - overlap,
         net_lift=round(rec_df.aov_lift_cons.sum() * overlap, 1), expected_aov=round(base + rec_df.aov_lift_cons.sum() * overlap, 1)),
    dict(scenario='مرجّح', base_aov_last30=round(base, 1), gross_lift=rec_df.aov_lift_like.sum(), overlap_haircut=1 - overlap,
         net_lift=round(rec_df.aov_lift_like.sum() * overlap, 1), expected_aov=round(base + rec_df.aov_lift_like.sum() * overlap, 1)),
    dict(scenario='المطلوب للوصول إلى 900', base_aov_last30=round(base, 1), gross_lift=None, overlap_haircut=None, net_lift=round(900 - base, 1), expected_aov=900),
])
need_share_1200 = (900 - base) / (mean_1200 - mean_lt500)
sim['note'] = ['', '', f'يعادل نقل ~{need_share_1200:.0%} من كل الطلبات من شريحة <500 إلى ≥1200 مع ثبات الباقي']

dq = pd.DataFrame(ext['data_quality'])
gaps = pd.DataFrame(ext['data_gaps'])
ux = pd.DataFrame(ext['ux_evidence_log'])
exps = pd.DataFrame(ext['experiments'])
defs = pd.DataFrame(ext['definitions'])

head = pd.DataFrame([
    ('AOV آخر 30 يوم مكتمل (10 أكت–8 نوف)', periods.loc['Last30: 10 أكتوبر–8 نوفمبر', 'aov']),
    ('AOV الـ30 يوم السابقة (10 سبت–9 أكت)', periods.loc['Prev30: 10 سبتمبر–9 أكتوبر', 'aov']),
    ('AOV آخر 7 أيام (2–8 نوف)', periods.loc['L7: 2–8 نوفمبر', 'aov']),
    ('AOV الأسبوع السابق (26 أكت–1 نوف)', periods.loc['P7: 26 أكتوبر–1 نوفمبر', 'aov']),
    ('فرق L7−P7 (ريال)', round(periods.loc['L7: 2–8 نوفمبر', 'aov'] - periods.loc['P7: 26 أكتوبر–1 نوفمبر', 'aov'], 1)),
    ('فترة ثقة 95% (Bootstrap) للفرق L7−P7', f'{ci1[0]} إلى {ci1[1]}'),
    ('فرق L7−Prior23 (ريال)', round(periods.loc['L7: 2–8 نوفمبر', 'aov'] - periods.loc['Prior23: 10 أكتوبر–1 نوفمبر', 'aov'], 1)),
    ('فترة ثقة 95% للفرق L7−Prior23', f'{ci2[0]} إلى {ci2[1]}'),
    ('أدنى متوسط متحرك 7 أيام خلال 60 يوماً', daily.aov_ma7_weighted.min()),
    ('متوسط/انحراف المتوسط المتحرك 60 يوماً', f"{daily.aov_ma7_weighted.mean():.1f} / {daily.aov_ma7_weighted.std():.1f}"),
    ('وقت الاستخراج (UTC)', ext['extracted_at']),
], columns=['المؤشر', 'القيمة'])

out = os.path.join(BASE, 'hlalna_aov_analysis_2026-11-09.xlsx')
with pd.ExcelWriter(out, engine='openpyxl') as xw:
    head.to_excel(xw, sheet_name='00_الخلاصة', index=False)
    defs.to_excel(xw, sheet_name='01_التعريفات', index=False)
    periods.reset_index(names='period').to_excel(xw, sheet_name='02_مقارنة_الفترات', index=False)
    daily.reset_index().to_excel(xw, sheet_name='03_المؤشرات_اليومية', index=False)
    band_tbl.to_excel(xw, sheet_name='04_شرائح_القيمة', index=False)
    r = 0
    for k, t in dec.items():
        pd.DataFrame([[k]]).to_excel(xw, sheet_name='05_تفكيك_التغير', startrow=r, index=False, header=False)
        t.reset_index(names='segment').to_excel(xw, sheet_name='05_تفكيك_التغير', startrow=r + 1, index=False); r += len(t) + 4
    pmix.to_excel(xw, sheet_name='06_المنتجات', index=False)
    copur.to_excel(xw, sheet_name='07_الشراء_المشترك', index=False)
    single.to_excel(xw, sheet_name='07_الشراء_المشترك', startcol=5, index=False)
    r = 0
    for nm, t in [('العملاء جديد/عائد', cust_tbl), ('المدن', city_tbl), ('قناة الإنشاء', chan_tbl), ('طريقة الدفع', pay_tbl),
                  ('أيام الشهر (60 يوم)', dom_tbl), ('أيام الأسبوع (60 يوم)', dow_tbl),
                  ('الإلغاء حسب الشريحة (60 يوم)', canc_band.reset_index()), ('الإلغاء حسب الدفع (60 يوم)', canc_pay.reset_index())]:
        pd.DataFrame([[nm]]).to_excel(xw, sheet_name='08_العملاء_والقنوات', startrow=r, index=False, header=False)
        t.to_excel(xw, sheet_name='08_العملاء_والقنوات', startrow=r + 1, index=False); r += len(t) + 4
    gw.to_excel(xw, sheet_name='09_مسار_الشراء', index=False)
    carts.to_excel(xw, sheet_name='09_مسار_الشراء', startrow=len(gw) + 3, index=False)
    ads.to_excel(xw, sheet_name='10_الإعلانات', index=False)
    ux.to_excel(xw, sheet_name='11_سجل_كلارتي_والتجربة', index=False)
    rec_df.to_excel(xw, sheet_name='12_التوصيات', index=False)
    sim.to_excel(xw, sheet_name='13_محاكاة_الأثر', index=False)
    exps.to_excel(xw, sheet_name='14_خطة_التجارب', index=False)
    dq.to_excel(xw, sheet_name='15_جودة_البيانات', index=False)
    gaps.to_excel(xw, sheet_name='16_نواقص_البيانات', index=False)
json.dump(dict(periods=periods.reset_index(names='period').to_dict('records'), ci_L7_P7=list(ci1), ci_L7_prior23=list(ci2),
               sim=sim.to_dict('records'), recs=rec_df.drop(columns=['evidence']).to_dict('records'),
               dec_cat=dec['الفئة الرئيسية للطلب | P7→L7'].reset_index(names='seg').to_dict('records'),
               dec_band=dec['شريحة القيمة | P7→L7'].reset_index(names='seg').to_dict('records'),
               funnel=gw.to_dict('records'), single_share=single_share, need_share_1200=need_share_1200),
          open(os.path.join(BASE, 'data', 'computed_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('written', out)
