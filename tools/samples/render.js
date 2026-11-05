// 디자인 예시 화면 캡처: node tools/samples/render.js [파일...]
// 1440x900 첫 화면 → ../../img/samples/<이름>.webp 로 저장 (python으로 webp 변환)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const dir = __dirname, out = path.join(dir, 'out');
  fs.mkdirSync(out, { recursive: true });
  const files = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(dir).filter(f => /^\d\d-.*\.html$/.test(f));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  for (const f of files) {
    await p.goto('file://' + path.join(dir, path.basename(f)));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(out, path.basename(f, '.html') + '.png') });
  }
  await b.close();
})();
