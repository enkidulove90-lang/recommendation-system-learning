# 组件库（recsys-blue 主题）

每个组件是一段**合规的 `<section>` 片段**：样式全内联、中文文字节点用 `<span leaf="">` 包裹、
无 `<div>` / `<style>` / `class` / `id`。直接拷贝到文章对应位置即可。
校验：`python ../scripts/validate_gzh_html.py <你的文件>`。

> 本文件里的 HTML 都包在 ```` ```html ```` 代码块中（供 `component_lint.py` 扫描）；
> 实际使用时去掉围栏，把 `<section>…</section>` 粘进文章。

---

## 1. 钩子标题 hook-title

```html
<section style="text-align:center;margin:0 0 6px;">
  <h1 style="font-size:20px;line-height:1.45;margin:0;color:#1a1a1a;font-weight:700;"><span leaf="">标题放这里</span></h1>
</section>
<section style="text-align:center;margin:0 0 18px;">
  <p style="font-size:13px;color:#8a94a6;line-height:1.6;margin:0;"><span leaf="">副标题一句话钩子放这里</span></p>
</section>
```

## 2. 封面图 cover

```html
<section style="margin:0 0 18px;">
  <img src="图片URL或本地路径" style="width:100%;border-radius:8px;display:block;">
</section>
```

## 3. 一句话高亮框 one-liner（📌）

```html
<section style="background:#eef3ff;border-left:4px solid #3a5fcd;padding:12px 16px;border-radius:6px;margin:0 0 16px;">
  <p style="margin:0;line-height:1.8;color:#2c3e50;font-size:15px;"><span leaf="">📌 一句话：</span><span leaf="">核心结论放这里，一句话讲清价值。</span></p>
</section>
```

## 4. 色条小标题 section-header

```html
<section style="border-left:4px solid #3a5fcd;padding-left:10px;margin:24px 0 12px;">
  <h2 style="font-size:17px;font-weight:700;color:#1a1a1a;line-height:1.45;margin:0;"><span leaf="">小标题文字</span></h2>
</section>
```

## 5. 正文段落 body-para（含关键词下划线示例）

```html
<section style="margin:0 0 14px;">
  <p style="margin:0;line-height:1.8;color:#3f3f3f;font-size:15px;"><span leaf="">普通叙述句。把</span><span leaf="" style="border-bottom:1px solid #3a5fcd;color:#3a5fcd;font-weight:700;">关键短语</span><span leaf="">用主色下划线标记，每段 1–3 处。</span></p>
</section>
```

## 6. 数据表格 rr-table

```html
<section style="margin:6px 0 16px;">
  <table style="width:100%;border-collapse:collapse;font-size:14px;">
    <thead><tr style="background:#3a5fcd;color:#ffffff;">
      <th style="border:1px solid #e3e8f0;padding:9px 8px;text-align:left;"><span leaf="">列1</span></th>
      <th style="border:1px solid #e3e8f0;padding:9px 8px;"><span leaf="">列2</span></th>
      <th style="border:1px solid #e3e8f0;padding:9px 8px;"><span leaf="">列3</span></th>
    </tr></thead>
    <tbody>
      <tr><td style="border:1px solid #e3e8f0;padding:9px 8px;"><span leaf="">单元格</span></td><td style="border:1px solid #e3e8f0;padding:9px 8px;text-align:center;"><span leaf="">12.3%</span></td><td style="border:1px solid #e3e8f0;padding:9px 8px;text-align:center;color:#1a9e57;font-weight:700;"><span leaf="">+1.2</span></td></tr>
    </tbody>
  </table>
</section>
```

## 7. KPI 卡片组 kpi-cards

```html
<section style="display:flex;gap:10px;margin:0 0 16px;flex-wrap:wrap;">
  <section style="flex:1;min-width:90px;background:#f5f8ff;border:1px solid #dce6ff;border-radius:8px;padding:10px 8px;text-align:center;">
    <p style="margin:0;font-size:18px;font-weight:700;color:#3a5fcd;line-height:1.2;"><span leaf="">+8.04</span></p>
    <p style="margin:2px 0 0;font-size:12px;color:#6b7280;"><span leaf="">指标说明</span></p>
  </section>
</section>
```

## 8. 带图注图 figure

```html
<section style="margin:0 0 18px;">
  <img src="图片URL" style="width:100%;border-radius:6px;border:1px solid #f0f0f0;display:block;">
  <p style="font-size:13px;color:#999;line-height:1.6;margin:6px 0 0;text-align:center;"><span leaf="">图 N｜说明文字（只有真有说明才写）</span></p>
</section>
```

## 9. 警示 / 诚实备注 limitation（⚠️）

```html
<section style="background:#fff7ec;border-left:4px solid #f0a020;padding:12px 16px;border-radius:6px;margin:0 0 16px;">
  <p style="margin:0;line-height:1.8;color:#5a4a2a;font-size:14px;"><span leaf="">⚠️ 备注：</span><span leaf="">局限或需要诚实说明的点放这里。</span></p>
</section>
```

## 10. 互动引导 cta

```html
<section style="background:#f0f7ff;border-radius:8px;padding:14px 16px;margin:18px 0;">
  <p style="margin:0;font-size:14px;color:#2c3e3a;line-height:1.7;"><span leaf="">💬 互动一下：</span><span leaf="">抛一个让读者想评论的问题。</span></p>
</section>
```

## 11. 参考文献 references

```html
<section style="margin:0 0 12px;">
  <p style="margin:0 0 14px;line-height:1.8;color:#3f3f3f;font-size:15px;"><span leaf="">· 论文：</span><a href="https://arxiv.org/abs/XXXX" style="color:#3a5fcd;text-decoration:none;"><span leaf="">https://arxiv.org/abs/XXXX</span></a></p>
  <p style="margin:0;font-size:13px;color:#8a94a6;line-height:1.7;"><span leaf="">图表摘自论文，仅作学术解读。</span></p>
</section>
```
