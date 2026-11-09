const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/recommendations.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: __dirname + '/kabsh_aov_800_recommendations.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await p.setViewportSize({ width: 820, height: 1160 });
  await p.screenshot({ path: __dirname + '/preview.png', fullPage: true });
  console.log('fonts:', await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length));
  await b.close();
})();
