"""Consolidated Nov 1-20 2026 P&L for the 3 stores. Kabsh = owner-supplied approved figures (report image 21 Nov 17:42); Alraqi/Hlalna = Joud finance.pnl.daily."""
import base64, datetime
src=open("/home/user/kabsh-najd-operations/reports/render_pnl_images.py").read().split("import os\nos.makedirs")[0]
exec(src)
from PIL import Image
Image.open("/tmp/claude-0/-home-user-kabsh-najd-operations/ed4d844e-41fc-50e8-b945-b9c23bf14713/images/2.webp").convert("RGBA").crop((72,58,292,275)).save("/tmp/hlb/kabsh_logo.png")
b64=lambda p:"data:image/png;base64,"+base64.b64encode(open(p,"rb").read()).decode()
# ---- Kabsh (from the approved report image) ----
K=dict(orders=2751,net=1769742.28,cogs=1249601.33,inst=52840.81,ads=90252.52,wa=9464.09,op=291520.0,deliv=64675.0,res=11388.53,
 products=1800378.76,disc=18357.32,shipc=32269.50,wallet=4651.46,cod=40522.06,diff=624.86)
Kd=[(289,188282.37,4720.00,21777.96),(219,136693.82,4713.77,11187.64),(156,98183.61,4138.54,3401.81),(158,97135.62,5051.42,1519.21),(136,87326.87,5108.76,-7.25),(100,61700.75,4490.08,-5239.37),(110,69608.21,5035.76,-4027.54),(143,88258.24,4869.82,-365.94),(129,85183.30,4782.97,-247.28),(174,102894.33,4965.81,658.70),(147,92143.96,4563.50,1316.10),(115,75496.77,4754.12,-2112.35),(102,67464.81,4758.63,-4225.75),(114,74368.23,4346.02,-2050.80),(113,78261.44,4609.91,-2624.55),(112,75452.75,4514.87,-1471.03),(109,83656.31,4006.70,1021.65),(114,75433.08,4076.57,-1238.22),(117,77369.56,3790.44,-333.82),(94,54828.25,2954.83,-5550.64)]
assert abs(sum(x[3] for x in Kd)-K["res"])<0.05 and abs(sum(x[1] for x in Kd)-K["net"])<0.05 and sum(x[0] for x in Kd)==K["orders"] and abs(sum(x[2] for x in Kd)-K["ads"])<0.05
chk=K["net"]-K["cogs"]-K["inst"]-K["ads"]-K["wa"]-K["op"]-K["deliv"]; assert abs(chk-K["res"])<0.05,chk
C={}
for co in ("alraqi","hlalna"):
    D=days_data(co); T,rows=agg(D,co); C[co]=(D,T,rows)
A,H=C["alraqi"][1],C["hlalna"][1]
def col(T): return dict(orders=T["orders"],net=T["net"],cogs=T["cogs"],inst=T["inst"],ads=T["adst"],wa=0,op=0,deliv=T["deliv"],res=T["res"])
cols=[("كبش نجد",K),("الراقي",col(A)),("حلالنا",col(H))]
tot={k:sum(c[1][k] for c in cols) for k in K if k in cols[0][1] and k in ("orders","net","cogs","inst","ads","wa","op","deliv","res")}
for _,c in cols:
    assert abs(c["net"]-c["cogs"]-c["inst"]-c["ads"]-c["wa"]-c["op"]-c["deliv"]-c["res"])<0.05
T_=dict(brand="#1B1B1F",gold="#C9A24B",bg="#EFE9DD")
heads={"كبش نجد":("#9B1C20","#F4E3C0"),"الراقي":("#111111","#C5A04A"),"حلالنا":("#5B2A12","#F6E9D3")}
cls=lambda v:"neg" if v<-0.004 else ""
def rowc(label,key,neg=False,cls_="",strong=False):
    vals=[c[1][key]*(-1 if neg else 1) for c in cols]; tt=tot[key]*(-1 if neg else 1)
    cells="".join(f'<td class="{cls(v)}">{fmt(v)}</td>' if key!="orders" else f"<td>{int(abs(v)):,}</td>" for v in vals)
    ttc=f'<td class="t {cls(tt)}">{fmt(tt)}</td>' if key!="orders" else f'<td class="t">{int(tt):,}</td>'
    return f'<tr class="{cls_}"><td>{label}</td>{cells}{ttc}</tr>'
head_cells="".join(f'<th style="background:{heads[n][0]};color:{heads[n][1]}">{n}</th>' for n,_ in cols)
tbl=f'<table class="m"><tr><th style="text-align:right;background:#1B1B1F;color:#C9A24B">البند</th>{head_cells}<th style="background:#1B1B1F;color:#C9A24B">الإجمالي</th></tr>'
tbl+=rowc("الطلبات المؤهلة","orders")+rowc("صافي الإيرادات الإدارية","net",cls_="hl")+rowc("المنتج والتغليف والهدر","cogs",True)+rowc("عمولات التقسيط","inst",True)+rowc("الإعلانات (المتاح)","ads",True)+rowc("رسائل واتساب","wa",True)+rowc("مصاريف التشغيل (تقدير)","op",True)+rowc("مصاريف التوصيل","deliv",True)+rowc("الربح الإداري التقديري","res",cls_="fin")+"</table>"
# daily
def d_res(co,i):
    r=C[co][2][i][1]
    return None if (r is None or r.get("exc")) else r["res"]
drows="";S=[0,0,0,0]
for i,d in enumerate(DAYS):
    a=d_res("alraqi",i); h=d_res("hlalna",i); k=Kd[i][3]; t=k+(a or 0)+(h or 0)
    S[0]+=k;S[1]+=a or 0;S[2]+=h or 0;S[3]+=t
    def cell(v): return '<td style="color:#999">—</td>' if v is None else f'<td class="{cls(v) or "pos"}">{fmt(v)}</td>'
    inc="" if (a is not None and h is not None) else "†"
    drows+=f'<tr><td>{i+1} نوفمبر</td>{cell(k)}{cell(a)}{cell(h)}<td class="{cls(t) or "pos"}"><b>{fmt(t)}{inc}</b></td></tr>'
drows+=f'<tr class="tot"><td>الإجمالي</td><td>{fmt(S[0])}</td><td>{fmt(S[1])}</td><td>{fmt(S[2])}</td><td>{fmt(S[3])}</td></tr>'
assert abs(S[3]-tot["res"])<0.05
now=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=3)
stamp=f"الاستخراج: {now.day} نوفمبر 2026 | {now:%H:%M} بتوقيت السعودية"
logos="".join(f'<img src="{b64(p)}">' for p in ("/tmp/hlb/kabsh_logo.png","/tmp/hlb/arlogo.png","/tmp/hlb/og.png"))
t=dict(THEMES["alraqi"]); t.update(bg=T_["bg"],head="#1B1B1F",headtxt="#C9A24B",title="#1B1B1F",sub="#333",alt="#FAF7F0",alt2="#F1EBDD",hl="#E3CF98",final="#1B1B1F",finaltxt="#C9A24B",total="#1B1B1F",totaltxt="#C9A24B",hltxt="#1B1B1F",pos="#14532d",neg="#B3261E")
extra=f""".hd img{{height:70px;margin-right:6px}}.m td{{padding:11px 10px;font-size:14px;text-align:center;direction:ltr}}.m td:first-child{{text-align:right;font-weight:700;direction:rtl}}.m td.t{{font-weight:800;background:#EFE6CF}}
.m tr:nth-child(odd) td{{background:{t['alt']}}}.m tr:nth-child(even) td{{background:{t['alt2']}}}.m tr.hl td{{background:{t['hl']}!important}}.m tr.fin td{{background:#1B1B1F!important;color:#C9A24B!important;font-size:16px;font-weight:800}}
.m td.neg{{color:{t['neg']}}}.m tr.fin td.neg{{color:#ff9d93!important}}.m th{{font-size:14px;padding:11px 8px}}"""
big=f'<div class="big" style="background:#E3CF98"><div class="l">إجمالي الربح الإداري التقديري للشركة (3 متاجر)</div><div class="v" style="direction:ltr;color:{"#B3261E" if tot["res"]<0 else "#1B1B1F"}">{fmt(tot["res"])}</div></div>'
notes=["الفترة: 1–20 نوفمبر 2026 بتوقيت الرياض. كبش نجد: أرقام التقرير المعتمد (21 نوفمبر 17:42). الراقي وحلالنا: تقارير جود اليومية (finance.pnl.daily).",
 "كبش نجد يتضمن مصاريف تشغيل (14,576 يوميًا — تقدير معتمد) وواتساب؛ الراقي وحلالنا بلا تشغيل ولا واتساب، فالمقارنة بين المتاجر غير متكافئة في هذين البندين.",
 f"الراقي: {len(C['alraqi'][1]['nodata'])+len(C['alraqi'][1]['excl'])} أيام غير محتسبة (فشل تجهيز جود: {'، '.join(str(int(x[-2:])) for x in C['alraqi'][1]['nodata'])}؛ وبلا إعلانات: {'، '.join(str(int(x[-2:])) for x in C['alraqi'][1]['excl'])}). حلالنا: {len(C['hlalna'][1]['nodata'])+len(C['hlalna'][1]['excl'])} أيام غير محتسبة (فشل تجهيز: {'، '.join(str(int(x[-2:])) for x in C['hlalna'][1]['nodata'])}؛ بلا إعلانات: {'، '.join(str(int(x[-2:])) for x in C['hlalna'][1]['excl'])}). † = اليوم لا يشمل متجرًا أو أكثر.",
 "إعلانات الراقي وحلالنا هي المتاح في جود فقط؛ في عدة أيام ناقصة (سناب/تيك توك) فربحهما أعلى من الواقع بقدر الإنفاق الناقص.",
 "تقرير إداري تقديري وليس إقفالًا محاسبيًا."]
nh="".join(f"<p>{n}</p>" for n in notes)
html=f'<html><head><meta charset="utf-8"><style>{css(t)}{extra}body{{width:760px}}</style></head><body><div class="hd"><div><h1>التقرير الشامل للربح والخسارة</h1><h2>كبش نجد + الراقي + حلالنا — 1 إلى 20 نوفمبر 2026</h2><p>{stamp}</p></div><div style="display:flex">{logos}</div></div>{big}{tbl}<h3>نتيجة كل يوم (إجمالي المتاجر)</h3><table class="day"><tr><th>اليوم</th><th style="background:#9B1C20;color:#F4E3C0">كبش نجد</th><th style="background:#111;color:#C5A04A">الراقي</th><th style="background:#5B2A12;color:#F6E9D3">حلالنا</th><th>الإجمالي</th></tr>{drows}</table><div class="notes">{nh}</div></body></html>'
import os; os.makedirs("/tmp/pnl_html",exist_ok=True); open("/tmp/pnl_html/all.html","w").write(html)
print({k:round(v,2) for k,v in tot.items()},[round(x,2) for x in S])
