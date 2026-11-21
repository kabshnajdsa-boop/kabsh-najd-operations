const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:796,height:800},deviceScaleFactor:2});
await p.goto('file:///tmp/pnl_html/all.html');await p.waitForTimeout(500);await p.screenshot({path:'/home/user/kabsh-najd-operations/reports/pnl_all_stores_nov_1-20.png',fullPage:true});await b.close();})();
