// Renders overview.html to ../SPM-420_Project_Overview.pdf (A4, page numbers in the footer).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'overview.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const fonts = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  const broken = await p.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src));
  await p.pdf({
    path: path.join(__dirname, '..', 'SPM-420_Project_Overview.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font:7px Arial;color:#56656d;padding:0 16mm;display:flex;justify-content:space-between"><span>SPM-420 project overview · rev P1 · preliminary design, not released for manufacture</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  console.log('fonts loaded:', [...new Set(fonts)].join(', ') || 'none (fallback)', '| broken images:', broken);
  await b.close();
})();
