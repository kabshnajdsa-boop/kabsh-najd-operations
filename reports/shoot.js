const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const co of ['alraqi','hlalna'])for(const n of ['monthly','summary']){
 const p=await b.newPage({viewport:{width:756,height:800},deviceScaleFactor:2});
 await p.goto('file:///tmp/pnl_html/'+co+'_'+n+'.html');await p.waitForTimeout(500);
 await p.screenshot({path:'/home/user/kabsh-najd-operations/reports/pnl_'+co+'_nov_1-20_'+n+'.png',fullPage:true});await p.close();}
await b.close();})();
