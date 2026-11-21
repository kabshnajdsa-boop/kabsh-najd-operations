"""Renders monthly P&L (+summary) images for alraqi and hlalna in the Kabsh report layout. Data: Joud finance.pnl.daily (full_<co>.json)."""
import json, base64, datetime, sys
SCR="/tmp/claude-0/-home-user-kabsh-najd-operations/ed4d844e-41fc-50e8-b945-b9c23bf14713/scratchpad/"
OUT="/home/user/kabsh-najd-operations/reports/"
DAYS=[f"2026-11-{i:02d}" for i in range(1,21)]
WA_MSGS={"alraqi":9700,"hlalna":18600}; WA_RATE=0.25; WA={k:v*WA_RATE for k,v in WA_MSGS.items()}  # Meta WhatsApp Manager insights (Marketing Messages API) 1-20 Nov, delivered; rounded to 0.1K
PROV=[("google_ads","إعلانات جوجل"),("meta","إعلانات ميتا"),("snap","إعلانات سناب"),("tiktok","إعلانات تيك توك")]
f=lambda x:float(x) if x not in (None,"") else 0.0
def fmt(x,sign=False):
    s=f"{abs(x):,.2f}"; 
    return ("-" if x<-0.004 else "")+s
def days_data(co):
    raw=json.load(open(SCR+f"full_{co}.json")); out={}
    manual={"alraqi":{"2026-11-16":dict(google_ads=89.63,snap=78.81,meta=91.96,tiktok=40.20),"2026-11-17":dict(google_ads=124.44,snap=11.27,meta=60.91,tiktok=41.42)}}.get(co,{})
    for d in DAYS:
        v=raw.get(d,{}); 
        if not v.get("pnl"):
            if d in manual:   # no eligible orders, ads known
                ads=manual[d]; out[d]=dict(has=True,orders=0,products=0,disc=0,shipc=0,shipd=0,wallet=0,cod=0,net=0,cogs=0,inst=0,tabby=0,tamara=0,deliv=0,ads=ads,ads_complete=True,state=v.get("state"))
            else: out[d]=dict(has=False,state=v.get("state"))
            continue
        p=v["pnl"]; a=v["amounts"]; pm=v.get("payment_methods") or {}
        tabby=pm.get("tabby_installment",{}).get("installment_fees_sum",0); tamara=pm.get("tamara_installment",{}).get("installment_fees_sum",0)
        ads={x["provider"]:(float(x["spend_sar"]) if x.get("spend_sar") not in (None,"") else None) for x in (v.get("ads") or [])}
        out[d]=dict(has=True,orders=v["summary"].get("الطلبات المؤهلة") or 0,products=f(a["products before discount tax"]),disc=f(a["discounts before tax"]),
            shipc=f(a["shipping collected before tax"]),shipd=f(a["shipping discount before tax"]),wallet=f(a["wallet before tax"]),cod=f(a["cod reserve"]),net=f(a["net revenue"]),
            cogs=p["تكلفة البضاعة"],inst=p["رسوم التقسيط"] or 0,tabby=tabby,tamara=tamara,deliv=p["الشحن"] or 0,ads=ads,
            ads_complete=all(ads.get(k) is not None for k,_ in PROV),state=v["state"])
    return out
def agg(D,co):
    T=dict(orders=0,products=0,disc=0,shipc=0,shipd=0,wallet=0,cod=0,net=0,cogs=0,inst=0,tabby=0,tamara=0,deliv=0,res=0,adsum={k:0 for k,_ in PROV},adst=0,incomplete=[],nodata=[],excl=[])
    rows=[]
    for d in DAYS:
        x=D[d]
        if not x["has"]: T["nodata"].append(d); rows.append((d,None)); continue
        if all(x["ads"].get(k) is None for k,_ in PROV):
            T["excl"].append(d); rows.append((d,dict(exc=True,orders=x["orders"],net=x["net"]))); continue
        for k in ("orders","products","disc","shipc","shipd","wallet","cod","net","cogs","inst","tabby","tamara","deliv"): T[k]+=x[k]
        adsd=0
        for k,_ in PROV:
            v=x["ads"].get(k)
            if v is not None: T["adsum"][k]+=v; adsd+=v
        T["adst"]+=adsd
        res=x["net"]-x["cogs"]-x["inst"]-adsd-x["deliv"]; T["res"]+=res
        if not x["ads_complete"]: T["incomplete"].append(d)
        rows.append((d,dict(orders=x["orders"],net=x["net"],ads=adsd,res=res,inc=not x["ads_complete"])))
    return T,rows
THEMES={
 "alraqi":dict(name="الراقي",file="alraqi",logo="/tmp/hlb/arlogo.png",bg="#F2EDE3",head="#111111",headtxt="#C5A04A",accent="#C3142D",hl="#EBD9A3",hltxt="#111111",final="#C3142D",finaltxt="#fff",
   pos="#14532d",neg="#C3142D",alt="#F8F5EE",alt2="#EFE9DC",title="#C3142D",sub="#111111",total="#111111",totaltxt="#C5A04A"),
 "hlalna":dict(name="حلالنا",file="hlalna",logo="/tmp/hlb/og.png",bg="#F1E4CF",head="#5B2A12",headtxt="#F6E9D3",accent="#7A3B17",hl="#E6C48F",hltxt="#3B1A08",final="#5B2A12",finaltxt="#F6E9D3",
   pos="#256029",neg="#A3241B",alt="#FBF4E8",alt2="#F4E8D2",title="#5B2A12",sub="#3B1A08",total="#5B2A12",totaltxt="#F6E9D3"),
}
def css(t):
    ff="".join(f"@font-face{{font-family:C;font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode(open(f'/tmp/fonts/cairo-{w}.woff2','rb').read()).decode()}) format('woff2');unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF,U+200C-200F;}}@font-face{{font-family:C;font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode(open(f'/tmp/fonts/cairol-{w}.woff2','rb').read()).decode()}) format('woff2');unicode-range:U+0000-00FF,U+2000-206F;}}" for w in (400,700,800))
    return ff+f"""*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:C,'DejaVu Sans',sans-serif;background:{t['bg']};width:720px;direction:rtl;padding:18px;color:#222}}
.hd{{background:#fff;border-radius:22px;padding:16px 22px;display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}}
.hd h1{{font-size:27px;font-weight:800;color:{t['title']}}}.hd h2{{font-size:19px;font-weight:700;color:{t['sub']};margin-top:2px}}.hd p{{font-size:12px;color:#777;margin-top:4px}}.hd img{{height:92px}}
table{{width:100%;border-collapse:collapse}}th{{background:{t['head']};color:{t['headtxt']};font-weight:700;font-size:14px;padding:11px 14px}}td{{padding:11px 14px;font-size:14px}}
.items td:nth-child(1){{text-align:right;font-weight:700}}.items td:nth-child(2){{text-align:center;color:#888;font-size:11.5px}}.items td:nth-child(3){{text-align:left;font-weight:800;direction:ltr}}
.items tr:nth-child(odd) td{{background:{t['alt']}}}.items tr:nth-child(even) td{{background:{t['alt2']}}}
.items tr.hl td{{background:{t['hl']}!important;color:{t['hltxt']}}}.items tr.fin td{{background:{t['final']}!important;color:{t['finaltxt']}!important;font-size:17px;font-weight:800}}.items tr.fin td:nth-child(2){{color:{t['finaltxt']}!important;opacity:.85}}
.pos{{color:{t['pos']}}}.neg{{color:{t['neg']}}}
h3{{font-size:21px;color:{t['title']};margin:20px 4px 8px;font-weight:800}}
.day td{{font-size:13px;text-align:center}}.day td:nth-child(1){{text-align:right;font-weight:700}}.day td:nth-child(n+2){{direction:ltr}}.day td:last-child{{font-weight:800}}
.day tr:nth-child(odd) td{{background:{t['alt']}}}.day tr:nth-child(even) td{{background:{t['alt2']}}}.day tr.tot td{{background:{t['total']}!important;color:{t['totaltxt']}!important;font-weight:800;font-size:14px}}
.notes{{margin-top:14px;font-size:11.5px;color:#666;line-height:1.9;padding:0 6px}}
.big{{background:{t['hl']};border-radius:26px;text-align:center;padding:26px 10px;margin-bottom:14px}}.big .l{{font-size:22px;font-weight:800;color:{t['title']}}}.big .v{{font-size:58px;font-weight:800;color:{t['hltxt']}}}
.cnt{{text-align:center;font-weight:800;font-size:15px;margin:12px 0}}"""
def build(co):
    t=THEMES[co]; D=days_data(co); T,rows=agg(D,co); T["wa"]=WA[co]; T["res_day"]=T["res"]; T["res"]=T["res"]-T["wa"]
    now=datetime.datetime.utcnow()+datetime.timedelta(hours=3)
    stamp=f"الاستخراج: {now.day} نوفمبر 2026 | {now:%H:%M} بتوقيت السعودية"
    logo="data:image/png;base64,"+base64.b64encode(open(t["logo"],"rb").read()).decode()
    cls=lambda v:"neg" if v<0 else ""
    L=[]  # (label, detail, value, kind)
    L.append(("مبيعات المنتجات","قبل الخصومات والضريبة",T["products"],""))
    L.append(("الكوبونات والعروض","خصومات قبل الضريبة",-T["disc"],""))
    if co=="hlalna":
        L.append(("الشحن المحصل","رسوم الشحن قبل الضريبة (بعد خصم الشحن)",T["shipc"]-T["shipd"],""))
        L.append(("المحفظة","خصم إداري وفق نموذج جود",-T["wallet"],""))
        L.append(("مخصص الدفع عند الاستلام","تقدير وفق النموذج الإداري",-T["cod"],""))
        diff=T["net"]-(T["products"]-T["disc"]+T["shipc"]-T["shipd"]-T["wallet"]-T["cod"])
        L.append(("فروقات مطابقة الإيراد","فرق بين نموذج جود والبنود أعلاه",diff,""))
    L.append(("صافي الإيرادات الإدارية","مجموع الأيام",T["net"],"hl"))
    cp="71% من أساس المنتج وفق نموذج جود" if co=="hlalna" else "تكلفة المنتج المرجعية + هدر وتغليف (سياسة الراقي)"
    L.append(("المنتج والتغليف والهدر",cp,-T["cogs"],""))
    oth=T["inst"]-T["tabby"]-T["tamara"]
    L.append(("عمولة تابي","وفق النموذج المعتمد",-T["tabby"],""))
    L.append(("عمولة تمارا","وفق النموذج المعتمد",-T["tamara"],""))
    if abs(oth)>0.5: L.append(("عمولات تقسيط أخرى","وفق النموذج المعتمد",-oth,""))
    L.append(("إجمالي عمولات التقسيط","توضيحي: لا يخصم مرة ثانية",-T["inst"],"hl"))
    for k,lab in PROV:
        miss=sum(1 for d in DAYS if D[d]["has"] and D[d]["ads"].get(k) is None)
        L.append((lab,"جود: دولار × 3.75"+(f" — غير متاح في {miss} أيام" if miss else ""),-T["adsum"][k],""))
    L.append(("إجمالي الإعلانات (المتاح)","توضيحي: لا يخصم مرة ثانية",-T["adst"],"hl"))
    L.append(("رسائل حملات واتساب",f"ميتا: {WA_MSGS[co]:,} رسالة واصلة (تقريبًا) × 0.25",-T["wa"],""))
    nd=sum(1 for d in DAYS if D[d]["has"] and D[d]["deliv"]>0)
    L.append(("مصاريف التوصيل","وفق سياسة جود (25 ريال للطلب المؤهل)" if co=="hlalna" else "وفق سياسة الراقي (25 ر.س لطلب غير مستلم > 800)",-T["deliv"],""))
    L.append(("الربح الإداري التقديري","إجمالي %d يومًا محتسبًا"%(20-len(T["nodata"])-len(T["excl"])),T["res"],"fin"))
    # items table: skip rows that are 'توضيحي' from summing check - just display
    def tr(l,d,v,k):
        c="" if k=="fin" else cls(v) if v<0 else "pos" if l in("مبيعات المنتجات","الشحن المحصل") else ""
        return f'<tr class="{k}"><td>{l}</td><td>{d}</td><td class="{c}">{fmt(v)}</td></tr>'
    items="".join(tr(*x) for x in L)
    drows=""
    for d,r in rows:
        dl=f"{int(d[-2:])} نوفمبر"
        if r is not None and r.get("exc"): drows+=f'<tr style="color:#999"><td>{dl}</td><td>{r["orders"]}</td><td>{fmt(r["net"])}</td><td>غير متاح</td><td>غير متاح</td></tr>'; continue
        if r is None: drows+=f'<tr><td>{dl}</td><td colspan="4" style="color:#999">لا بيانات (تقرير غير مكتمل في جود)</td></tr>'
        else: drows+=f'<tr><td>{dl}</td><td>{r["orders"]}</td><td>{fmt(r["net"])}</td><td>{fmt(r["ads"])}{"*" if r["inc"] else ""}</td><td class="{cls(r["res"]) or "pos"}">{fmt(r["res"])}</td></tr>'
    drows+=f'<tr style="font-weight:700"><td>رسائل واتساب (إجمالي الفترة)</td><td>—</td><td>—</td><td>—</td><td class="neg">{fmt(-T["wa"])}</td></tr>'
    drows+=f'<tr class="tot"><td>إجمالي الأيام المحتسبة</td><td>{T["orders"]}</td><td>{fmt(T["net"])}</td><td>{fmt(T["adst"])}</td><td>{fmt(T["res"])}</td></tr>'
    good=sum(1 for d,r in rows if r and not r.get("exc") and r["res"]>0); best=max((x for x in rows if x[1] and not x[1].get("exc")),key=lambda x:x[1]["res"]); worst=min((x for x in rows if x[1] and not x[1].get("exc")),key=lambda x:x[1]["res"])
    inc=("، ".join(str(int(x[-2:])) for x in T["incomplete"]))
    nod=("، ".join(str(int(x[-2:])) for x in T["nodata"]))
    notes=[f"الفترة: 1–20 نوفمبر 2026 بتوقيت الرياض. المصدر: تقارير جود اليومية (finance.pnl.daily) لـ{t['name']} — الإجماليات تخص {20-len(T['nodata'])-len(T['excl'])} يومًا محتسبًا ({T['orders']} طلبًا مؤهلاً).",
      (f"أيام لم تُحتسب لعدم توفر أي إنفاق إعلاني في جود ({'، '.join(str(int(x[-2:])) for x in T['excl'])}): تظهر مبيعاتها في الجدول فقط وليست ضمن الإجماليات، ولا يُعدّ إنفاقها صفرًا." if T['excl'] else ""),
      (f"أيام بلا بيانات في جود (فشل التجهيز): {nod} — غير محتسبة ولا تُعدّ أصفارًا." if nod else ""),
      f"* أيام إنفاق إعلانات غير مكتمل في جود ({inc}): يظهر فيها المتاح فقط، وربح هذه الأيام أعلى من الواقع بقدر الإنفاق الناقص.",
      "لا تشمل مصاريف التشغيل (غير مطبقة على "+t['name']+"). رسائل واتساب محتسبة لإجمالي الفترة من إحصاءات ميتا (تقريبية لأنها بالآلاف) ولا توزَّع على الأيام.",
      f"أيام بربح: {good} من {20-len(T['nodata'])}. أفضل يوم: {int(best[0][-2:])} نوفمبر ({fmt(best[1]['res'])}) وأضعف يوم: {int(worst[0][-2:])} نوفمبر ({fmt(worst[1]['res'])}).",
      "تقرير إداري تقديري وليس إقفالًا محاسبيًا."]
    nh="".join(f"<p>{n}</p>" for n in notes if n)
    head=lambda title,sub:f'<div class="hd"><div><h1>{title}</h1><h2>{sub}</h2><p>{stamp}</p></div><img src="{logo}"></div>'
    main=f'<html><head><meta charset="utf-8"><style>{css(t)}</style></head><body>{head("تقرير الربح والخسارة الشهري","نوفمبر 2026: من 1 إلى 20 نوفمبر — "+t["name"])}<table class="items"><tr><th style="text-align:right">البند</th><th>تفاصيل الاحتساب</th><th style="text-align:left">المبلغ بالريال</th></tr>{items}</table><h3>نتيجة كل يوم</h3><table class="day"><tr><th>اليوم</th><th>الطلبات</th><th>صافي الإيراد</th><th>الإعلانات</th><th>النتيجة</th></tr>{drows}</table><div class="notes">{nh}</div></body></html>'
    keep=("رسائل حملات واتساب","مبيعات المنتجات","صافي الإيرادات الإدارية","المنتج والتغليف والهدر","إجمالي عمولات التقسيط","إجمالي الإعلانات (المتاح)","مصاريف التوصيل","الربح الإداري التقديري")
    sitems="".join(tr(*x) for x in L if x[0] in keep)
    sm=f'<html><head><meta charset="utf-8"><style>{css(t)}</style></head><body>{head("ملخص الربح والخسارة",f"{t["name"]} — نوفمبر 2026 (1-20 نوفمبر)")}<div class="big"><div class="l">الربح الإداري التقديري</div><div class="v" style="direction:ltr">{fmt(T["res"])}</div></div><div class="cnt">{T["orders"]} طلبًا مؤهلاً | {20-len(T["nodata"])-len(T["excl"])} يومًا محتسبًا</div><table class="items">{sitems}</table><div class="notes">{nh}</div></body></html>'
    return main,sm,T

import os
os.makedirs("/tmp/pnl_html",exist_ok=True)
for co in ("alraqi","hlalna"):
    main,sm,T=build(co)
    open(f"/tmp/pnl_html/{co}_monthly.html","w").write(main); open(f"/tmp/pnl_html/{co}_summary.html","w").write(sm)
    print(co,{k:(round(v,2) if isinstance(v,float) else v) for k,v in T.items() if k in("orders","products","disc","net","cogs","inst","deliv","adst","res","incomplete","nodata")})
