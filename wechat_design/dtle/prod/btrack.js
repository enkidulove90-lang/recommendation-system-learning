#!/usr/bin/env node
/**
 * DTLE 生产环境 B 轨渲染器（Satori + @resvg/resvg-js）。
 *
 * 输入（stdin, JSON）：{ element, width, height, fontPath }
 *   - element: Satori/React 风格节点树（由 Python 适配器 renderers/card_satori.py 生成）
 *   - fontPath: CJK 字体 ttf/otf 路径（Satori 必须显式提供字体）
 * 输出：把 PNG 写入 argv[2] 指定路径。
 *
 * 流程：Satori(JSX→SVG) → @resvg/resvg-js(SVG→PNG)，确定性、无浏览器、边缘可跑。
 * 图片：内联 data-URL 直接渲染；远程 http(s) 由 images 回调 fetch。
 */
'use strict';
const fs = require('fs');
const path = require('path');
// satori / @resvg/resvg-js 在不同版本下可能以「函数直接导出」或「{default: fn}」形式暴露，
// 这里统一兼容 CommonJS（require）与 ESM（default）两种形态。
const _satoriMod = require('satori');
const satori = (typeof _satoriMod === 'function') ? _satoriMod
  : (_satoriMod.default || _satoriMod.defaultRender || _satoriMod.render);
const _resvgMod = require('@resvg/resvg-js');
const Resvg = _resvgMod.Resvg || (_resvgMod.default && _resvgMod.default.Resvg)
  || _resvgMod.default;

function loadImage(src) {
  // 本地文件 → data URL
  if (/^(https?:)?\/\//.test(src) === false && fs.existsSync(src)) {
    const ext = path.extname(src).slice(1).toLowerCase();
    const mime = ext === 'png' ? 'image/png' : ext === 'jpg' || ext === 'jpeg'
      ? 'image/jpeg' : ext === 'webp' ? 'image/webp' : 'image/png';
    const b64 = fs.readFileSync(src).toString('base64');
    return `data:${mime};base64,${b64}`;
  }
  return src; // 远程 URL 交给 Satori 的 images 回调 fetch
}

async function main() {
  const outPath = process.argv[2];
  if (!outPath) {
    console.error('用法: node btrack.js <out.png>  （JSON 经 stdin）');
    process.exit(2);
  }
  const input = JSON.parse(fs.readFileSync(0, 'utf-8'));
  const { element, width = 1242, height = 1656, fontPath } = input;
  if (!fontPath || !fs.existsSync(fontPath)) {
    console.error('缺少 CJK 字体 fontPath:', fontPath);
    process.exit(3);
  }
  const fontData = fs.readFileSync(fontPath);
  const fonts = [
    { name: 'RecSys', data: fontData, weight: 400, style: 'normal' },
    { name: 'RecSys', data: fontData, weight: 700, style: 'normal' },
  ];

  const svg = await satori(element, {
    width, height, fonts,
    images: {
      async fetch(url) {
        if (url.startsWith('data:')) return url;
        try {
          const r = await fetch(url);
          if (!r.ok) throw new Error('http ' + r.status);
          const buf = Buffer.from(await r.arrayBuffer());
          const ct = r.headers.get('content-type') || 'image/png';
          if (!ct.startsWith('image/')) throw new Error('not image: ' + ct);
          return `data:${ct};base64,${buf.toString('base64')}`;
        } catch (e) {
          // 远程图不可达/非图像：返回 1x1 透明 PNG，避免整页渲染崩溃（布局用显式宽高兜底）
          process.stderr.write('[img] 远程图降级为透明占位: ' + String(e) + '\n');
          const png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC';
          return 'data:image/png;base64,' + png;
        }
      },
    },
  });

  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: width },
    font: { loadSystemFonts: false },
  });
  const png = resvg.render().asPng();
  fs.writeFileSync(outPath, png);
  console.error('✅ 生产 B 轨 PNG 已写出:', outPath, `(${png.length} B)`);
}

main().catch((e) => { console.error('SATORI/RESVG 渲染失败:', e); process.exit(1); });
