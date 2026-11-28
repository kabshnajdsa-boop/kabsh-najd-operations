const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const co of ['hlalna','alraqi'])for(const n of ['','_summary']){const p=await b.newPage({viewport:{width:756,height:800},deviceScaleFactor:2});
await p.goto('file:///tmp/pnl_html/'+co+'_day27'+n+'.html');await p.waitForTimeout(500);
await p.screenshot({path:'/home/user/kabsh-najd-operations/reports/pnl_'+co+'_2026-11-27'+(n?'_summary':'_full')+'.png',fullPage:true});await p.close();}await b.close();})();
