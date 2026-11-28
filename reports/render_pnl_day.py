"""Single-day P&L image (default 2026-11-27) for alraqi / hlalna from Joud day JSONs. Ads unavailable -> net profit shown as unavailable."""
import json, base64, datetime, os, sys
src=open("/home/user/kabsh-najd-operations/reports/render_pnl_images.py").read().split("import os\nos.makedirs")[0]
exec(src)
SCR2=SCR; DAY="2026-11-27"; DAY_AR="27 نوفمبر 2026"; RATE=0.25
def build_day(co):
    t=THEMES[co]; d=json.load(open(SCR2+f"day27_{co}.json")); p=d["pnl"]; a=d["amounts"]; pm=d["payment_methods"]; wa=d["whatsapp"]
    prod=f(a["products before discount tax"]); disc=f(a.get("discounts before tax")); shipc=f(a.get("shipping collected before tax")); shipd=f(a.get("shipping discount before tax")); wal=f(a.get("wallet before tax")); cod=f(a.get("cod reserve")); net=f(a["net revenue"])
    cogs=p["تكلفة البضاعة"]; inst=p["رسوم التقسيط"]; deliv=p["الشحن"]
    tabby=pm.get("tabby_installment",{}).get("installment_fees_sum",0); tamara=pm.get("tamara_installment",{}).get("installment_fees_sum",0)
    wamsg=wa["delivered"]; wacost=wamsg*RATE
    pre=net-cogs-inst-deliv-wacost
    L=[("مبيعات المنتجات","قبل الخصومات والضريبة",prod,""),("الكوبونات والعروض","خصومات قبل الضريبة",-disc,"")]
    if co=="hlalna":
        L+= [("الشحن المحصل","رسوم الشحن قبل الضريبة",shipc-shipd,""),("المحفظة","خصم إداري وفق نموذج جود",-wal,""),("مخصص الدفع عند الاستلام","تقدير وفق النموذج الإداري",-cod,""),("فروقات مطابقة الإيراد","فرق بين نموذج جود والبنود أعلاه",net-(prod-disc+shipc-shipd-wal-cod),"")]
    L.append(("صافي الإيرادات الإدارية","اليوم",net,"hl"))
    L.append(("المنتج والتغليف والهدر","71% من أساس المنتج وفق نموذج جود" if co=="hlalna" else "تكلفة المنتج المرجعية + هدر وتغليف (سياسة الراقي)",-cogs,""))
    L+= [("عمولة تابي","وفق النموذج المعتمد",-tabby,""),("عمولة تمارا","وفق النموذج المعتمد",-tamara,""),("إجمالي عمولات التقسيط","توضيحي: لا يخصم مرة ثانية",-inst,"hl")]
    ad_rows="".join(f'<tr><td>{lab}</td><td>غير متاح في جود</td><td style="color:#999">غير متاح</td></tr>' for lab in ("إعلانات جوجل","إعلانات ميتا","إعلانات سناب","إعلانات تيك توك"))
    L2=[("رسائل حملات واتساب",f"كرزون عبر جود: {wamsg} رسالة واصلة × 0.25",-wacost,""),("مصاريف التوصيل","وفق سياسة جود (25 ريال للطلب المؤهل)" if co=="hlalna" else "وفق سياسة الراقي",-deliv,""),("الربح قبل الإعلانات","بدون الإعلانات (غير متاحة)",pre,"hl")]
    def tr(l,dd,v,k):
        c="neg" if v<-0.004 else ("pos" if l in("مبيعات المنتجات","الشحن المحصل","الربح قبل الإعلانات") else "")
        return f'<tr class="{k}"><td>{l}</td><td>{dd}</td><td class="{c}">{fmt(v)}</td></tr>'
    items="".join(tr(*x) for x in L)+ad_rows+"".join(tr(*x) for x in L2)+f'<tr class="fin"><td>الربح الإداري التقديري</td><td>ينتظر إنفاق الإعلانات</td><td>غير متاح</td></tr>'
    now=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=3)
    stamp=f"الاستخراج: {now.day} نوفمبر 2026 | {now:%H:%M} بتوقيت السعودية"
    logo="data:image/png;base64,"+base64.b64encode(open(t["logo"],"rb").read()).decode()
    notes=[f"اليوم: {DAY_AR} بتوقيت الرياض. المصدر: تقرير جود اليومي (finance.pnl.daily) لـ{t['name']} — حالة التقرير: {'مكتمل' if d['state']=='complete' else 'جزئي'}، {d['summary'].get('الطلبات المؤهلة')} طلبًا مؤهلاً.",
      "إنفاق الإعلانات (جوجل وميتا وسناب وتيك توك) غير متوفر في جود لهذا اليوم، لذلك لا يُحسب صافي الربح ولا يُعدّ الإنفاق صفرًا. الرقم المعروض هو الربح قبل الإعلانات.",
      f"رسائل واتساب: {wamsg} واصلة من {wa['sent']} مرسلة (سجل كرزون اليومي) بسعر 0.25"+(" — السجل غير مكتمل لهذا اليوم." if co=="alraqi" else "."),
      "لا تشمل مصاريف التشغيل (غير مطبقة على "+t['name']+").",
      ("طلب واحد من الطلبات غير مؤهل بعد (بنود الفاتورة ناقصة)." if co=="alraqi" else ""),"تقرير إداري تقديري وليس إقفالًا محاسبيًا."]
    nh="".join(f"<p>{n}</p>" for n in notes if n)
    big=f'<div class="big"><div class="l">الربح قبل الإعلانات</div><div class="v" style="direction:ltr">{fmt(pre)}</div><div style="font-size:14px;margin-top:6px;color:#666">الربح الإداري الصافي غير متاح (إنفاق الإعلانات ناقص)</div></div>'
    keep=("صافي الإيرادات الإدارية","المنتج والتغليف والهدر","إجمالي عمولات التقسيط","رسائل حملات واتساب","مصاريف التوصيل","الربح قبل الإعلانات")
    sitems="".join(tr(*x) for x in (L+L2) if x[0] in keep and x[0]!="إجمالي عمولات التقسيط") 
    sitems=tr("صافي الإيرادات الإدارية","اليوم",net,"hl")+tr("المنتج والتغليف والهدر",L[-4][1],-cogs,"")+tr("عمولات التقسيط (تابي وتمارا)","وفق النموذج المعتمد",-inst,"")+'<tr><td>الإعلانات (4 منصات)</td><td>غير متاح في جود</td><td style="color:#999">غير متاح</td></tr>'+tr(*L2[0])+tr(*L2[1])+tr(*L2[2])+'<tr class="fin"><td>الربح الإداري التقديري</td><td>ينتظر إنفاق الإعلانات</td><td>غير متاح</td></tr>'
    snh="".join(f"<p>{n}</p>" for n in (notes[1],notes[2],notes[5]) if n)
    summ=f'<html><head><meta charset="utf-8"><style>{css(t)}</style></head><body><div class="hd"><div><h1>ملخص الربح والخسارة</h1><h2>{t["name"]} — {DAY_AR}</h2><p>{stamp}</p></div><img src="{logo}"></div>{big}<div class="cnt">{d["summary"].get("الطلبات المؤهلة")} طلبًا مؤهلاً</div><table class="items">{sitems}</table><div class="notes">{snh}</div></body></html>'
    return f'<html><head><meta charset="utf-8"><style>{css(t)}</style></head><body><div class="hd"><div><h1>تقرير الربح والخسارة اليومي</h1><h2>{t["name"]} — {DAY_AR}</h2><p>{stamp}</p></div><img src="{logo}"></div>{big}<table class="items"><tr><th style="text-align:right">البند</th><th>تفاصيل الاحتساب</th><th style="text-align:left">المبلغ بالريال</th></tr>{items}</table><div class="notes">{nh}</div></body></html>', summ, dict(net=net,cogs=cogs,inst=inst,deliv=deliv,wa=wacost,pre=pre)
os.makedirs("/tmp/pnl_html",exist_ok=True)
for co in ("hlalna","alraqi"):
    h,sm,s=build_day(co); open(f"/tmp/pnl_html/{co}_day27.html","w").write(h); open(f"/tmp/pnl_html/{co}_day27_summary.html","w").write(sm); print(co,{k:round(v,2) for k,v in s.items()})
