// 用 @resvg/resvg-js 把示例 SVG 栅格化为本地 PNG（供 Satori 生产 B 轨内联）
const fs = require('fs');
const path = require('path');
const { Resvg } = require(require('path').join(__dirname, '..', 'prod', 'node_modules', '@resvg', 'resvg-js'));

const OUT = __dirname;
const W = 1114, H = 600;

const coverSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b5fff"/><stop offset="1" stop-color="#0a3bbf"/></linearGradient></defs>
  <rect width="${W}" height="${H}" fill="url(#g)"/>
  <text x="64" y="270" font-family="sans-serif" font-size="84" font-weight="800" fill="#ffffff">LOOPSBENCH</text>
  <text x="66" y="340" font-family="sans-serif" font-size="34" fill="#dbe7ff">长上下文推荐的「记忆」评测</text>
  <text x="66" y="430" font-family="sans-serif" font-size="26" fill="#a9c4ff">22 万篇语料 · NDCG +8% · 幻觉率 −31%</text>
</svg>`;

const curveSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="#ffffff"/>
  <line x1="80" y1="60" x2="80" y2="${H-80}" stroke="#ccd" stroke-width="2"/>
  <line x1="80" y1="${H-80}" x2="${W-60}" y2="${H-80}" stroke="#ccd" stroke-width="2"/>
  <text x="40" y="60" font-family="sans-serif" font-size="22" fill="#555">NDCG</text>
  <text x="${W-150}" y="${H-50}" font-family="sans-serif" font-size="22" fill="#555">写入频率</text>
  <path d="M120 460 C 360 460, 430 180, 600 200 S 900 420, 1020 430" fill="none" stroke="#0b5fff" stroke-width="5"/>
  <circle cx="600" cy="200" r="9" fill="#0b5fff"/>
  <text x="560" y="170" font-family="sans-serif" font-size="22" fill="#0b5fff">最优 4–8 步/次</text>
</svg>`;

function render(name, svg) {
  const r = new Resvg(svg, { fitTo: { mode: 'width', value: W } });
  fs.writeFileSync(path.join(OUT, name), r.render().asPng());
  console.log('wrote', name);
}
render('loopsbench_cover.png', coverSvg);
render('loopsbench_curve.png', curveSvg);
