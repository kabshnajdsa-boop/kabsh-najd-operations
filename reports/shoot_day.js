const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const co of ['hlalna','alraqi']){const p=await b.newPage({viewport:{width:756,height:800},deviceScaleFactor:2});
await p.goto('file:///tmp/pnl_html/'+co+'_day27.html');await p.waitForTimeout(500);
await p.screenshot({path:'/home/user/kabsh-najd-operations/reports/pnl_'+co+'_2026-11-27.png',fullPage:true});await p.close();}await b.close();})();
