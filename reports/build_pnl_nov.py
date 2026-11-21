"""Builds Nov 1-20 2026 P&L workbook for kabsh / alraqi / hlalna from Joud finance.pnl.daily data."""
import json, glob, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
TR="/root/.claude/projects/-home-user-kabsh-najd-operations/ed4d844e-41fc-50e8-b945-b9c23bf14713/tool-results/"
SCR="/tmp/claude-0/-home-user-kabsh-najd-operations/ed4d844e-41fc-50e8-b945-b9c23bf14713/scratchpad/hlalna_pnl.json"
OP, WA = 14576.0, 500.0   # owner-approved daily estimates (Joud finance policy); used for kabsh only
DAYS=[f"2026-11-{i:02d}" for i in range(1,21)]
def row(state,sales=None,cogs=None,ship=None,inst=None,ads=None,ads_known=None,orders=None,note=""):
    return dict(state=state,sales=sales,cogs=cogs,ship=ship,inst=inst,ads=ads,ads_known=ads_known,orders=orders,note=note)
def from_file(f):
    d=json.load(open(f)); r=d["result"]; p=r["payload"]
    tabs={t["title"]:t for t in p.get("tables",[])}
    det={x["item"]:x["current"] for x in tabs.get("تفاصيل الربح والخسارة",{}).get("rows",[])}
    sm={x["البند"]:x["القيمة"] for x in tabs.get("الملخص",{}).get("rows",[])}
    kn=sm.get("known advertising spend sar")
    return d["tenant"],r["day"],row(r["state"],det.get("صافي المبيعات"),det.get("تكلفة البضاعة"),det.get("الشحن"),det.get("رسوم التقسيط"),det.get("الإعلانات"),float(kn) if kn else None,sm.get("الطلبات المؤهلة"))
data={"kabsh":{},"alraqi":{},"hlalna":{}}
for f in glob.glob(TR+"mcp-838c94c5*report_read*.txt")+glob.glob(TR+"toolu_*.json"):
    try:
        if f.endswith(".json"): 
            raw=json.load(open(f)); open("/tmp/_x.json","w").write(raw[0]["text"]); t,day,rw=from_file("/tmp/_x.json")
        else: t,day,rw=from_file(f)
    except Exception: continue
    data[t][day]=rw
# kabsh days 6,7 returned blocked (no data)
for dd in ("2026-11-06","2026-11-07"): data["kabsh"][dd]=row("blocked",note="التقرير فشل في جود (blocked) - لا بيانات")
# alraqi days read inline
A=data["alraqi"]
A["2026-11-01"]=row("complete",471.26,356.59,0,8.88,337.17,337.17,2)
A["2026-11-04"]=row("complete",1562.75,1281.57,0,15.0,412.83,412.83,3)
A["2026-11-06"]=row("complete",1369.03,1101.32,0,26.10,430.42,430.42,3)
A["2026-11-07"]=row("partial",1674.0,1327.8,25.0,24.0,None,332.02,3,"سناب غير مؤكد")
A["2026-11-09"]=row("complete",464.0,412.36,0,8.16,460.86,460.86,2)
A["2026-11-10"]=row("partial",831.08,670.98,0,6.21,None,360.06,2,"سناب غير مؤكد")
A["2026-11-12"]=row("complete",529.34,393.17,0,0.0,446.13,446.13,2)
A["2026-11-13"]=row("complete",1167.78,967.19,25.0,8.25,427.36,427.36,2)
A["2026-11-14"]=row("complete",1254.56,881.93,25.0,23.07,308.24,308.24,2)
A["2026-11-15"]=row("pending",1171.61,897.33,0,22.6,None,None,3,"بيانات الإعلانات لم تُجمع")
A["2026-11-16"]=row("pending",0,0,0,0,300.60,300.60,0,"لا طلبات مؤهلة (طلب واحد قيد التنفيذ)")
A["2026-11-17"]=row("partial",0,0,0,0,238.04,238.04,0,"لا طلبات")
A["2026-11-18"]=row("blocked",note="التقرير فشل في جود - لا بيانات")
A["2026-11-19"]=row("blocked",note="التقرير فشل في جود - لا بيانات")
A["2026-11-20"]=row("complete",738.39,512.8,0,10.29,None,None,2,"إعلانات غير متاحة في جود")
# hlalna
H=json.load(open(SCR))
for day,v in H.items():
    if not v.get("has_tables"): data["hlalna"][day]=row(v["state"],note="التقرير فشل في جود - لا بيانات"); continue
    p=v["pnl"]; s=v["summary"]; kn=s.get("known advertising spend sar")
    data["hlalna"][day]=row(v["state"],p["صافي المبيعات"],p["تكلفة البضاعة"],p["الشحن"],p["رسوم التقسيط"],p["الإعلانات"],float(kn) if kn else None,s.get("الطلبات المؤهلة"),"; ".join(v.get("source_gaps") or []))
NAMES={"kabsh":"كبش نجد","alraqi":"الراقي","hlalna":"حلالنا"}
def calc(co,day):
    r=data[co].get(day) or row("missing")
    has=r["sales"] is not None
    gp=r["sales"]-r["cogs"] if has else None
    pre=gp-(r["ship"] or 0)-(r["inst"] or 0) if has else None   # before ads / opex
    ops=(OP+WA) if (co=="kabsh" and has) else 0
    net=(pre-r["ads"]-ops) if (has and r["ads"] is not None) else None
    return r,gp,pre,ops,net
HEAD=["التاريخ","الحالة في جود","الطلبات","صافي المبيعات","تكلفة البضاعة","الربح الإجمالي","الشحن","رسوم التقسيط","الإعلانات","الربح قبل الإعلانات والتشغيل","مصروفات التشغيل (تقدير)","واتساب (تقدير)","صافي الربح","ملاحظات"]
wb=Workbook(); wb.remove(wb.active)
hf=PatternFill("solid",fgColor="1F4E78"); 
def style(ws,n):
    for c in ws[1]: c.font=Font(bold=True,color="FFFFFF"); c.fill=hf; c.alignment=Alignment(horizontal="center",wrap_text=True)
    ws.sheet_view.rightToLeft=True
    for i in range(1,n+1): ws.column_dimensions[chr(64+i)].width=18
    ws.column_dimensions[chr(64+n)].width=45
totals={}
def sheet(co):
    ws=wb.create_sheet(NAMES[co]); ws.append(HEAD)
    T=dict(sales=0,cogs=0,gp=0,ship=0,inst=0,ads_all=0,ads_known_days=0,pre=0,ops=0,net=0,net_days=0,data_days=0,ads_gap_days=[],nodata=[],orders=0,pre_net_days=0)
    for d in DAYS:
        r,gp,pre,ops,net=calc(co,d); has=r["sales"] is not None
        ws.append([d,r["state"],r["orders"],r["sales"],r["cogs"],gp,r["ship"],r["inst"],r["ads"] if r["ads"] is not None else ("غير متاح" if has else None),pre,
                   (OP if co=="kabsh" and has else None),(WA if co=="kabsh" and has else None),net if net is not None else ("غير متاح" if has else "لا بيانات"),r["note"]])
        if not has: T["nodata"].append(d); continue
        T["data_days"]+=1; T["orders"]+=r["orders"] or 0
        for k,v in (("sales",r["sales"]),("cogs",r["cogs"]),("gp",gp),("ship",r["ship"] or 0),("inst",r["inst"] or 0),("pre",pre),("ops",ops)): T[k]+=v
        if r["ads"] is not None:
            T["ads_all"]+=r["ads"]; T["net"]+=net; T["net_days"]+=1
            T["pre_net_days"]+=pre
        else: T["ads_gap_days"].append(d)
    ws.append([]); 
    ws.append(["الإجمالي (أيام فيها بيانات)",None,T["orders"],round(T["sales"],2),round(T["cogs"],2),round(T["gp"],2),round(T["ship"],2),round(T["inst"],2),None,round(T["pre"],2),round(T["ops"],2) if co=="kabsh" else None,None,None,f'{T["data_days"]} يوم'])
    ws.append(["إنفاق الإعلانات المؤكد (أيام مكتملة الإعلانات فقط)",None,None,None,None,None,None,None,round(T["ads_all"],2)])
    ws.append(["صافي الربح للأيام التي اكتملت فيها الإعلانات",None,None,None,None,None,None,None,None,None,None,None,round(T["net"],2),f'{T["net_days"]} يوم من {T["data_days"]}'])
    ws.append(["أيام بلا إعلانات مؤكدة: "+("، ".join(x[-2:] for x in T["ads_gap_days"]) or "-")])
    ws.append(["أيام بلا بيانات: "+("، ".join(x[-2:] for x in T["nodata"]) or "-")])
    style(ws,len(HEAD)); totals[co]=T
for co in ("kabsh","alraqi","hlalna"): sheet(co)
# consolidated
ws=wb.create_sheet("الشامل",0)
ws.append(["البند","كبش نجد","الراقي","حلالنا","الإجمالي (3 متاجر)"])
def line(label,key,nd=2):
    vals=[round(totals[c][key],nd) for c in ("kabsh","alraqi","hlalna")]; ws.append([label]+vals+[round(sum(vals),nd)])
line("عدد الطلبات المؤهلة","orders",0); line("صافي المبيعات","sales"); line("تكلفة البضاعة","cogs"); line("الربح الإجمالي","gp")
line("الشحن","ship"); line("رسوم التقسيط","inst"); line("الربح قبل الإعلانات والتشغيل","pre")
ws.append(["مصروفات التشغيل + واتساب (تقدير المالك – كبش فقط)",round(totals["kabsh"]["ops"],2),0,0,round(totals["kabsh"]["ops"],2)])
line("الإعلانات المؤكدة (أيام مكتملة)","ads_all"); line("صافي الربح – الأيام المكتملة الإعلانات فقط","net")
ws.append(["عدد أيام البيانات / أيام اكتمال الإعلانات"]+[f'{totals[c]["data_days"]} / {totals[c]["net_days"]}' for c in ("kabsh","alraqi","hlalna")])
ws.append(["أيام بلا بيانات"]+["، ".join(x[-2:] for x in totals[c]["nodata"]) or "-" for c in ("kabsh","alraqi","hlalna")])
ws.append(["أيام بلا إعلانات مؤكدة"]+["، ".join(x[-2:] for x in totals[c]["ads_gap_days"]) or "-" for c in ("kabsh","alraqi","hlalna")])
style(ws,5); ws.column_dimensions["A"].width=55
# notes
n=wb.create_sheet("ملاحظات المنهجية")
for t in ["المصدر: تقرير جود finance.pnl.daily لكل شركة (نموذج إداري تقديري؛ ليس إقفالاً محاسبياً؛ financial_approved=false).",
"المدة: 1–20 نوفمبر 2026 بتوقيت الرياض. المنهج: صافي المبيعات − تكلفة البضاعة (71% للكبش وحلالنا، سياسة الراقي المرجعية) = الربح الإجمالي، ثم خصم الشحن ورسوم التقسيط والإعلانات.",
"كبش نجد: خُصم تقدير المالك المعتمد في جود (تشغيل 14,576 + واتساب 500 يومياً) لأن جود لم تطبّقه لوجود قيود أودو (mapping_required). هذا تقدير وليس قيداً فعلياً.",
"الراقي وحلالنا: أُلغي بند التشغيل والواتساب حسب التعليمات (جود تضيفهما افتراضياً ضمن تقدير المالك، حُذفا هنا).",
"القيم غير المتاحة ليست صفراً: الأيام التي لم يُجمع فيها إنفاق إعلاني كامل لا يُحسب لها صافي ربح (يظهر 'غير متاح')، وإجمالي الصافي يخص الأيام المكتملة فقط.",
"أيام blocked في جود (فشل التجهيز) مستثناة بالكامل ولا تُعتبر صفراً. الأيام pending/partial تُعرض كما وردت مع ملاحظتها.",
"بعض بيانات الأيام الأخيرة أُخذت من نسخ محفوظة قديمة (stale) في جود؛ تُراجع بعد اكتمال الجمع."]:
    n.append([t])
n.sheet_view.rightToLeft=True; n.column_dimensions["A"].width=150
wb.save("/home/user/kabsh-najd-operations/reports/pnl_nov_1-20_2026.xlsx")
for c in totals: print(c,{k:(round(v,2) if isinstance(v,float) else v) for k,v in totals[c].items()})
