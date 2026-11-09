"""Record the non-order inputs captured through the JOUD unified connection (2026-11-09).

Sources (company=hlalna):
  - joud-salla-full-v1 / reports_sales_over_time (day grain), reports_carts_summary, reports_sales_by
  - joud040-google / google_daily_report (website property 518259549, view=summary)
  - joud-direct-marketing-v1 / joud_google_ads_report (customer 9428309303), joud_meta_report (act 1404070251077899)
Values below are transcribed from those tool responses; None = not returned (missing, not zero).
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'salla_reports_daily_raw.py'), encoding='utf-8').read())  # defines `rows`

rep = [dict(date=r[0], orders=r[1], sales=r[2], discount=r[3], tax=r[4], sales_count=r[5], cost_price=r[6],
            products_total=r[7], shipping=r[8], avg_amount=r[11]) for r in rows]
for d in ['2026-10-%02d' % i for i in range(10, 25)]:
    rep.append(dict(date=d, orders=None, sales=None, discount=None, tax=None, sales_count=None, cost_price=None,
                    products_total=None, shipping=None, avg_amount=None))

GA = """2026-10-26 1473 1601 1366 167 112 21
2026-10-27 1169 1274 1048 122 108 14
2026-10-28 1612 1743 1473 220 187 22
2026-10-29 1734 1896 1621 177 146 22
2026-10-30 1294 1419 1285 184 142 23
2026-10-31 1403 1493 1249 161 115 17
2026-11-01 1501 1658 1503 295 185 27
2026-11-02 1515 1667 1526 280 173 22
2026-11-03 1592 1736 1576 224 154 19
2026-11-04 1247 1398 1273 206 159 21
2026-11-05 1846 1978 1793 224 153 15
2026-11-06 1354 1487 1357 176 145 16
2026-11-07 1583 1730 1508 167 134 17
2026-11-08 1717 1850 1649 207 134 18"""
ga = [dict(zip(['date', 'users', 'sessions', 'item_views', 'add_to_carts', 'checkouts', 'purchases'],
               [l.split()[0]] + list(map(int, l.split()[1:])))) for l in GA.splitlines()]

ads = [
    dict(platform='Google Ads', campaign='Sales-Search-hlalna- نعيمي وحري بلدي', currency='SAR', spend_P7=1107.35, spend_L7=787.11),
    dict(platform='Google Ads', campaign='Shopping_1_7', currency='SAR', spend_P7=1219.78, spend_L7=1004.63),
    dict(platform='Google Ads', campaign='Sales-Search-hlalna - M1 - 1/1', currency='SAR', spend_P7=631.34, spend_L7=648.57),
    dict(platform='Google Ads', campaign='PMax-Halalna-Store-All', currency='SAR', spend_P7=354.98, spend_L7=459.02),
    dict(platform='Google Ads', campaign='Local-Halalna-StoreGoals-Riyadh', currency='SAR', spend_P7=97.19, spend_L7=106.32),
    dict(platform='Meta', campaign='Sales | Hlalna -cataloge | M7 | 23/7 - منتجات مطبخ فقط', currency='USD', spend_P7=80.3, spend_L7=139.7),
    dict(platform='Meta', campaign='Sales | hlalna -cataloge منتجات جديدة | M7 | 25/7 – CPA', currency='USD', spend_P7=110.4, spend_L7=139.4),
    dict(platform='Meta', campaign='Sales | hlalna -عروض جديدة | M6 | 27/6 - CPA', currency='USD', spend_P7=157.0, spend_L7=157.5),
    dict(platform='Meta', campaign='Sales | hlalna -video ai | M10 | 18/10', currency='USD', spend_P7=194.1, spend_L7=225.5),
    dict(platform='Snapchat / TikTok', campaign='لم تُقرأ تكاليفها في هذه الجولة', currency='', spend_P7=None, spend_L7=None),
]
for a in ads:
    a['change_pct'] = round(a['spend_L7'] / a['spend_P7'] - 1, 3) if a['spend_P7'] else None

carts = {'P7': dict(carts=1213, cart_value=756737.17, average_cart_value=742.68, abandoned_carts=338, abandoned_value=235328.38, recovered_carts=34, recovered_rate=10.06),
         'L7': dict(carts=1290, cart_value=648045.51, average_cart_value=651.79, abandoned_carts=332, abandoned_value=229429.84, recovered_carts=24, recovered_rate=7.23)}
for v in carts.values():
    v['avg_abandoned_cart'] = round(v['abandoned_value'] / v['abandoned_carts'], 1)

defs = [
    dict(item='المؤشر الأساسي', definition='AOV = مجموع total.amount للطلبات المؤهلة ÷ عدد الطلبات الفريدة المؤهلة (ليس متوسط المتوسطات اليومية)'),
    dict(item='قيمة الطلب', definition='المبلغ النهائي في سلة (منتجات بعد الخصم + الشحن + رسوم الدفع عند الاستلام + ضريبة 15%)'),
    dict(item='الحالات المشمولة', definition='تم التوصيل، تم التنفيذ، جاري التوصيل، قيد التنفيذ، بانتظار المراجعة'),
    dict(item='المستبعد', definition='ملغي (يُحلَّل منفصلاً)، محذوف، بانتظار الدفع، طلب عرض سعر، مسترجع (1 طلب)، الطلبات بقيمة 0 من لوحة التحكم (6 طلبات، تُعامل كداخلية/تجريبية)'),
    dict(item='الدفع عند الاستلام', definition='مشمول إذا لم يُلغَ؛ يُعتمد total وليس المبلغ المدفوع لأن COD يُحصَّل عند التسليم'),
    dict(item='الخصومات', definition='مطروحة داخل total؛ إجمالي الخصم في L7 ≈ 835 ريال (0.7% من المبيعات) وفق تقرير مصادر الخصم'),
    dict(item='الاسترداد', definition='refund_amount = 0 لجميع الطلبات المؤهلة في النافذة؛ طلب مسترجع واحد مستبعد'),
    dict(item='المنطقة الزمنية', definition='Asia/Riyadh كما تعيدها سلة؛ اليوم الجاري 9 نوفمبر مستبعد'),
    dict(item='الفئة الرئيسية للطلب', definition='الفئة ذات أعلى قيمة تقديرية (الكمية × سعر الكتالوج الحالي) داخل الطلب — تصنيف غير متداخل'),
    dict(item='عميل عائد', definition='له طلب مؤهل سابق داخل نافذة 60 يوماً أو حسابه أُنشئ قبل الطلب بأكثر من يومين (تقريب: لا يوجد سجل طلبات قبل 10 سبتمبر)'),
    dict(item='الوزن', definition='تقديري = الكمية × وزن المنتج في الكتالوج؛ يُستبعد ما وزنه ≤0.2 كجم (ذبائح مسجلة بوزن 0.1 غير حقيقي)'),
    dict(item='التفكيك', definition='Shift-share متماثل: أثر المزيج = Δحصة × (متوسط الفئة − المتوسط العام)؛ الأثر الداخلي = متوسط الحصة × Δمتوسط الفئة؛ المجموع = ΔAOV بالضبط'),
]
dq = [
    dict(check='اكتمال الصفحات', result='68/68 صفحة، 1009 طلب فريد (10 سبت–8 نوف)، لا تكرار', status='ناجح'),
    dict(check='مطابقة Prev30 مع تقارير سلة', result='مبيعات 262,792.01 مقابل 262,792 — مطابقة تامة؛ العدد 365 مقابل 368 (سلة تحتسب 3 طلبات بقيمة صفر)', status='مطابق'),
    dict(check='مطابقة Last30 مع تقارير سلة', result='555 طلب/395,613 مقابل 554/393,902؛ فرق 1 طلب و1,711 ريال (تأخر تقارير سلة لطلبات حديثة)', status='فرق صغير مفتوح'),
    dict(check='تعريف AOV في لوحة سلة', result='سلة تعرض 719 = المبيعات ÷ sales_count (طلبات محتسبة) وليس ÷ orders؛ 393,902÷554 = 711', status='موثّق'),
    dict(check='تقرير سلة اليومي', result='صفوف 10–24 أكتوبر = صفر رغم وجود 166 طلباً فعلياً — فجوة في خدمة التقارير وليست صفراً حقيقياً', status='قيمة مفقودة'),
    dict(check='قمع سلة (conversion_funnel)', result='P7 يظهر 2,184 زيارة و33 طلباً فقط مقابل 153 طلباً فعلياً — تغطية ناقصة؛ غير صالح للمقارنة', status='مستبعد'),
    dict(check='تغطية GA4 للمشتريات', result='GA4 (موقع) يسجل 146/128 شراء في P7/L7 مقابل 111/113 طلب موقع في سلة؛ الربط بمعرف المعاملة غير منفذ', status='جزئي'),
    dict(check='BigQuery', result='تصدير يومي متاح منذ 20 أكتوبر (analytics_518259549)؛ لا معرفات مكررة في عينة 5 نوفمبر', status='متاح'),
    dict(check='العملة', result='جميع الطلبات SAR بسعر صرف 1', status='ناجح'),
    dict(check='التكاليف', result='أودو: standard_price = 0 لجميع منتجات اللحوم (مفقود وليس صفراً)؛ سلة: cost_price متاح لعدد محدود (ذبائح، مفروم، بعض القطعيات)', status='ناقص'),
    dict(check='الأسعار الفعلية', result='سعر الوحدة الفعلي من تقرير سلة ثابت تقريباً للمنتجات الرئيسية بين P7 وL7 (مثلاً بوكس حري كبير 903→890 صافي)', status='لا تغيير سعري مثبت'),
]
gaps = [
    dict(gap='Microsoft Clarity', impact='لا يمكن إثبات/نفي مشكلات تجربة المستخدم (السلة، الوزن، الكوبونات، الجوال)', affected='فرضيات تجربة المستخدم كلها', how_to_fill='إضافة موصل Clarity لحلالنا داخل جود (Data Export API) أو منح وصول قراءة للمشروع'),
    dict(gap='تكلفة البوكسات والأطباق المطبوخة', impact='لا يمكن حساب هامش المساهمة للتوصيات R1–R3 بدقة', affected='الربحية', how_to_fill='إدخال standard_price في أودو حلالنا أو cost_price في سلة، ووصفات/تكاليف مطبخ حلالنا'),
    dict(gap='تفاصيل الطلب (خصم/شحن/ضريبة لكل طلب)', impact='التفصيل متاح كمجاميع يومية فقط ولـ 25 أكتوبر فما بعد', affected='تحليل الشحن المجاني على مستوى الطلب', how_to_fill='سحب orders_get لكل طلب أو تصدير الطلبات من لوحة سلة'),
    dict(gap='ربط الحملة بالطلب', impact='لا يوجد معرف موثوق يربط الطلب بالحملة/صفحة الهبوط؛ 100% من الطلبات غير منسوبة على مستوى الطلب', affected='تفسير أثر التسويق (فرضية)', how_to_fill='ربط transaction_id في BigQuery مع reference_id في سلة'),
    dict(gap='سجل تاريخي للأسعار والمخزون والعروض', impact='updated_at فقط؛ لا يوجد سجل تغييرات', affected='الخط الزمني للتغييرات', how_to_fill='لقطة يومية للكتالوج والمخزون على جود'),
    dict(gap='تطبيق GA4/Firebase (517544923)', impact='لم يُقرأ في هذه الجولة؛ طلبات التطبيق 5 فقط في L7', affected='ضعيف', how_to_fill='google_daily_report source=app'),
    dict(gap='إنفاق Snapchat/TikTok', impact='لم يُقرأ', affected='تقييم مزيج الإنفاق', how_to_fill='joud_snap_report / joud_tiktok_report'),
    dict(gap='الجهاز (جوال/سطح مكتب)', impact='تقرير سلة device يعيد قناة الإنشاء فقط', affected='تحليل الجوال', how_to_fill='GA4 deviceCategory عبر BigQuery'),
]
ux = [
    dict(id='UX-0', page='—', device='—', period='—', cases=0, behaviour='لم تُراجع أي تسجيلات: لا يوجد موصل Clarity لحلالنا ضمن ربط جود الحالي (21 موصلاً مفحوصاً)', evidence='joud2_coverage hlalna 2026-11-09', supporting_data='—', status='فجوة بيانات'),
    dict(id='UX-1', page='السلة', device='الكل', period='P7→L7', cases=None, behaviour='متوسط قيمة السلة انخفض 743→652 مع ثبات عدد السلات المتروكة (338→332)', evidence='salla reports_carts_summary', supporting_data='الانخفاض يبدأ قبل الدفع — يرجّح مزيج الطلب لا عطل الدفع', status='مثبت رقمياً'),
    dict(id='UX-2', page='السلة المتروكة', device='الكل', period='L7', cases=332, behaviour='متوسط السلة المتروكة 691 > متوسط الطلب المكتمل 650؛ معدل الاسترداد هبط 10.1%→7.2%', evidence='salla reports_carts_summary', supporting_data='فرصة استرداد سلات مرتفعة', status='مثبت رقمياً'),
    dict(id='UX-3', page='القمع', device='موقع', period='P7→L7', cases=None, behaviour='مشاهدة منتج/جلسة 0.86→0.90، إضافة/جلسة 0.120→0.125، دفع/إضافة 0.75→0.71، شراء/دفع 0.147→0.122؛ إيراد/جلسة للموقع 7.23→6.39 ريال', evidence='GA4 518259549 يومي', supporting_data='مشتريات GA4 هبطت 146→128 بينما طلبات الموقع في سلة 111→113 — التراجع في GA4 غير مؤكد في سلة؛ يحتاج مطابقة transaction_id', status='مثبت رقمياً / سببه غير محسوم'),
    dict(id='UX-4', page='الدفع', device='الكل', period='60 يوم', cases=205, behaviour='إلغاء COD = 21.5% مقابل 1–4% للدفع الإلكتروني؛ إلغاء L7 أقل من P7 (5.9% مقابل 9.5%)', evidence='orders_list', supporting_data='لا يفسر انخفاض L7', status='مثبت رقمياً'),
    dict(id='UX-P', page='البوكسات/نصف ذبيحة محمر/السلة/الدفع', device='جوال أولاً', period='P7 وL7', cases='30–50 جلسة', behaviour='خطة العينة: 10 شراء <900، 10 شراء ≥900، 10 ترك سلة ≥900، 10 خروج من صفحة بوكس/مطبخ، 5–10 جلسات دفع', evidence='بعد توفير Clarity', supporting_data='تصنيف قيمة السلة من قيمة مسجلة فقط', status='مخطط'),
]
exps = [
    dict(id='E1', hypothesis='إضافة مكمّلة (قطعيات 1 كجم/كبدة) داخل السلة ترفع AOV دون خفض التحويل', eligible='طلبات أحادية المنتج (بوكسات، نصف ذبيحة محمر)', change='وحدة «يُشترى معاً» بثلاثة منتجات من أزواج الشراء المشترك الفعلية؛ A بدون خصم، B بخصم 5% على المجموعة', control='تقسيم 50/50 حسب الجلسة', sample='σ≈435 ريال (406 بعد قص أعلى 2%): رصد +40 يحتاج ≈1,600 طلب/ذراع (غير عملي)، ورصد +80 ≈400/ذراع (≈4–5 أسابيع). المقياس الرئيسي خلال 14 يوماً: نسبة التبنّي × قيمة الإضافة (قابلة للقياس مباشرة من سطور الطلب) مع حارس التحويل', success='AOV +30 ريال أو أكثر، تحويل/جلسة لا يقل >3%، هامش/زيارة أعلى', stop='انخفاض التحويل >5% لمدة 5 أيام أو ارتفاع الإلغاء >2 نقطة', owner='مدير المتجر + التسويق'),
    dict(id='E2', hypothesis='إبراز الحجم الأكبر في صفحة البوكس يرفع حصة الوسط/الكبير', eligible='زوار صفحات البوكس الصغير/الوسط', change='مقارنة «سعر الكيلو» + شارة الأكثر طلباً + عرض الكمية القائم على البوكس الكبير', control='تبديل أسبوعي مع مقارنة بنفس مرحلة الشهر', sample='14 يوماً كحد أدنى', success='+5 نقاط في حصة الوسط/الكبير من طلبات البوكسات', stop='انخفاض طلبات البوكسات >10%', owner='مدير المنتجات'),
    dict(id='E3', hypothesis='توصيل مجاني ≥750 يدفع سلات 500–749 للأعلى', eligible='سلات 500–749', change='شريط تقدم «باقي X ريال للتوصيل المجاني»', control='50/50 أو مدن بالتناوب', sample='21 يوماً (الشريحة ~25% من الطلبات)', success='حصة 750+ ترتفع ≥4 نقاط وصافي الإيراد/زيارة بعد تكلفة الشحن أعلى', stop='تكلفة الشحن الصافية > الزيادة في الهامش', owner='المالية + التشغيل'),
    dict(id='E4', hypothesis='إعادة الإنفاق إلى بحث النعيمي/الحري والتسوق ترفع حصة ≥1200', eligible='حملات Google/Meta', change='إعادة ميزانية بحث نعيمي/حري إلى مستوى P7 وسقف لحملة «منتجات مطبخ فقط»', control='قبل/بعد معدّل لمرحلة الشهر + هولد-آوت جغرافي إن أمكن', sample='14 يوماً', success='حصة ≥1200 ≥12% مع ثبات CPA', stop='ارتفاع CPA >25%', owner='التسويق المدفوع'),
    dict(id='E5', hypothesis='حملة «تموين الشهر» أيام 1–10 تخفف الهبوط الدوري', eligible='كل الزوار أيام 1–10', change='بانر وواتساب لبوكس الثلاجة الشهرية/البوكسات الكبيرة', control='مقارنة مع أيام 1–10 أكتوبر ونوفمبر', sample='دورة شهرية', success='AOV أيام 1–10 ≥740', stop='—', owner='CRM'),
]
out = dict(extracted_at='2026-11-09T07:40Z–08:36Z (UTC)', salla_reports_daily=rep, ga4_website_daily=ga, ads_spend=ads,
           salla_carts_summary=carts, definitions=defs, data_quality=dq, data_gaps=gaps, ux_evidence_log=ux, experiments=exps)
json.dump(out, open(os.path.join(os.path.dirname(HERE), 'data', 'external_inputs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
