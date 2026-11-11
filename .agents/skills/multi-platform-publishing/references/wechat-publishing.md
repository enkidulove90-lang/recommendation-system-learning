# 微信公众号发布指南

> 本指南基于 `redbook/infrastructure/wechat_delivery.py`（browser-bridge 重写版，2026-08-06）
> 与 `clis/weixin/create-draft.js`（v1.8.6，被弃用的旧路径）源码逐条核对。
> 任何与源码冲突的描述以源码为准。

## 架构（重写版）

微信公众号发布使用「草稿先行」策略：**只创建草稿，不群发**。

```
路径 A：WeChatDraftDelivery（browser-bridge，自动化，需登录）★ 当前默认
  - 类：redbook/infrastructure/wechat_delivery.py::WeChatDraftDelivery
  - 驱动已登录 mp.weixin.qq.com 的 Chrome 会话（复用 opencli browser <session> 桥）
  - 单会话：打开编辑器 → 填标题(verified) → 填作者 → 注入正文(HTML innerHTML) → 传封面并设为封面
            → 填摘要 → 点「保存为草稿」→ 校验成功标记 → 关闭
  - 正文由 `render_wechat_html` 生成**微信安全的内联样式 HTML**（段标题色条、高亮框、编号列表、
    文末参考链接），经 `editor.innerHTML = <html>` 直接注入；无 Markdown 残留。
  - 标题/正文/封面/摘要 全部以浏览器真实事件写入，编辑器正常渲染
  - 草稿写入公众号后台草稿箱

路径 B：HTML 预览（fallback，无需登录）
  - 生成本地 HTML 文件 data/publish_preview/wechat/<title>.html（由 render_wechat_preview_doc 生成）
  - 文件即**完整 HTML 文章**（标题 h1 + 封面图 + 富文本正文 + 全部 5-7 张图），直接浏览器打开预览
  - 手动复制/上传到公众号后台编辑器（粘贴 HTML 即可保留样式）
  - 支持全部 5-7 张图（<img> 内联，file:/// 本地路径）
```

> **关键差异（与小红书不同）**：公众号不支持 PDF 附件、不支持多图自动上传、
> 正文**不渲染 Markdown**。所以「PDF 解析后的科研内容」指的是**解析出的摘要正文 + 提取图**，
> 而非 PDF 文件本身；PDF 以 arXiv 链接形式放在文末参考。

---

## 一、为什么弃用 `opencli weixin create-draft`（根因分析）

旧路径 `opencli weixin create-draft "<正文>" --title <t> --cover-image <单张>` 会**静默产出废稿**。
两个失败模式都在 OpenCLI 自身，wrapper 无法补救，所以新管线直接 bypass `create-draft`，
改用它内部同一套浏览器桥（`opencli browser <session> ...`），但用正确的命令（`fill` / `eval`）。

### 1.1 标题丢失（标题栏显示「请在这里输入标题」0/64）

`create-draft.js` 用 `HTMLTextAreaElement.prototype.value` setter + `InputEvent('input')` + `change`
写入 `textarea#title`。但公众号编辑器（UEditor 前端）**不订阅这个合成事件序列**，
React 状态保持空，所以即便 OpenCLI 回报 `"draft saved"`，草稿标题栏仍然是空的。

**修复**：用 `opencli browser <session> fill <selector> <text>` 写入。`fill` 走的是浏览器原生
focus → input → 真实键盘/IME 事件序列，UEditor 能正确感知。`fill` 回包 `{filled, verified, text, actual}`，
其中 `actual` 是 UEditor 实际在 DOM 中看到的值——新管线**断言** `verified` 且 `actual == title`，
标题没落进去就直接抛 `DeliveryError`，不会「假成功」。

### 1.2 正文不渲染 Markdown（正文像原始变更日志）

`create-draft.js` 的 `fillContent` 用 `document.execCommand('insertText', ...)` 把正文原样塞进
`contenteditable`。execCommand 把字符串当作纯文本，`**加粗**`、`## 标题`、`---` 都会原样显示成字面字符，
草稿看起来像 raw changelog，不是文章。

**修复**：正文改用 `render_wechat_html` 生成**微信安全的内联样式 HTML**（段标题色条、`📌` 高亮框、
编号列表、文末 arXiv/PDF 参考链接），再经 `editor.innerHTML = <html>` 直接注入——**不转义、不包 `<p>`**，
完整保留样式。兜底仍保留 `render_wechat_article` 的微信风味纯文本（走 `_fill_body` 按空行拆 `<p>`）。
`innerHTML` 注入后 UEditor 的 toolbar 与 DOM 保持同步（不同于 `execCommand('insertText')`），
正文按带样式的段落/区块正常显示。详见 §三 与 `references/wechat-body-template.md`。

> **微信 HTML 约束**：编辑器会清洗注入的 HTML——保留 `style` 内联样式，但剥离 `<style>`/`<script>`/
> `class`/`id` 以及 `position`/`float` 等布局属性。因此 `render_wechat_html` 全部用内联 `style`
> （`color`/`font-size`/`font-weight`/`background-color`/`border-left`/`border-radius`/`line-height`/
> `padding`/`margin`），并只用 `<section>`/`<p>`/`<span>`/`<a>` 这类会被保留的标签。
> 配色集中在 `paper_to_wechat.py` 的 `_ACCENT`/`_ACCENT_BG`/`_TEXT`/`_MUTED` 常量，改一处即可换肤。

> 旧路径的实测契约（仅作历史参考，路径 A 已不再使用）：无 `--images`/`--pdf` 参数；仅 1 张封面；
> 正文不渲染 Markdown；`columns: ['status','detail']` 成功返回 `draft saved` 但不返回 media_id。

---

## 二、新管线：WeChatDraftDelivery browser-bridge（序列与要点）

`WeChatDraftDelivery.deliver(payload)` 在一个持久会话（`session="redbook-wechat-draft"`）中按顺序执行：

| 步骤 | 方法 | 关键动作 | 失败处理 |
|------|------|----------|----------|
| 0 | `_open_editor` | `browser open` home → `eval` 提取 `token` → `open` editor URL → `wait selector textarea#title` | 无 token → `DeliveryError`（未登录） |
| 1 | `_fill_title` | `browser fill textarea#title` → 断言 `verified` 且 `actual==title` | 未 verified → `DeliveryError` |
| 2 | `_fill_author` | `browser fill input#author`（≤8 字，截断） | 非致命 |
| 3 | `_fill_body` | `eval` `_BODY_INNERHTML_JS`：按空行切 `<p>` 段，`editor.innerHTML=...` + `InputEvent('input')` | `ok:false` → `DeliveryError` |
| 4 | `_upload_cover` | 点 `#js_editor_insertimage` → 下拉首项 → `upload` 文件 → 等 CDN(`mmbiz`) → 从正文选择 → 第一步/确认 | **非致命**：无封面仍可存稿 |
| 5 | `_fill_summary` | `browser fill textarea#js_description`（≤120 字） | 非致命 |
| 6 | `_save_draft` | `click 保存为草稿`（按 label）→ 轮询 `#js_save_success` / body 含「已保存」8×2s | 未出现 → 返回 `saved=False` |
| 7 | `_close` | `browser close`（best-effort） | 永不阻断 |

**选择器**（取自 create-draft.js，已在新管线验证可解析）：

```
TITLE_SELECTOR      = "textarea#title"
AUTHOR_SELECTOR     = "input#author"
SUMMARY_SELECTOR    = "textarea#js_description"
BODY_SELECTORS      = ('div[contenteditable="true"]',)   # 取 document order 最后一个
COVER_IMAGE_TRIGGER = "#js_editor_insertimage"
COVER_DROPDOWN_ITEM = ".js_img_dropdown_menu .tpl_dropdown_menu_item"
COVER_FILE_INPUT    = 'input[type="file"][name="file"]'
SAVE_DRAFT_LABEL    = "保存为草稿"
SAVE_SUCCESS_SELECTOR = "#js_save_success"
```

**JS 注入要点**（`_BODY_INNERHTML_JS`）：
```js
(function(paragraphs){
  var editors=document.querySelectorAll('div[contenteditable="true"]');
  var editor=editors[editors.length-1];          // UEditor body 是最后一个 contenteditable
  editor.focus();
  var html=paragraphs.map(function(p){
    return '<p>'+p.split('\n').map(escape).join('<br/>')+'</p>';
  }).join('');
  editor.innerHTML=html;                          // 关键：innerHTML 让 UEditor 同步 toolbar
  editor.dispatchEvent(new InputEvent('input',{bubbles:true,data:...}));
  return JSON.stringify({ok:true,...});
})(__PAYLOAD__)                                   // __PAYLOAD__ = JSON.stringify(paragraphs[])
```

**关键设计决策**：
1. **单会话**：整个调用只保持一个 tab（镜像 xiaohongshu_delivery），避免重复开 editor 丢 token。
2. **标题 verified 断言**：`fill` 的 `actual` 必须 == 请求值，杜绝「假保存」。
3. **innerHTML 而非 insertText**：正文按 `<p>` 渲染（修复 1.2）。
4. **封面非致命**：传封面失败仍有正文草稿；`receipt.cover_applied` 标记是否成功。
5. **保存标记轮询**：`#js_save_success` 可见 或 body 含「已保存」才认 `saved=True`。
6. **超时 270s**：`OPENCLI_BROWSER_COMMAND_TIMEOUT` 显式抬高（creator 自动化常超 60s 默认上限）。

---

## 三、内容格式：WeChat 风味纯文本（render_wechat_article）

公众号编辑器（UEditor）**不渲染 Markdown**，所以正文必须是不含 `**`/`##`/`---` 的纯文本。
`redbook/automation/paper_to_wechat.py::render_wechat_article(assets)` 复用与
`render_article_body`（Markdown 源）相同的 11 维摘要字段，但产出编辑器能看懂的结构：

- **emoji 分段标记**：`🔹` 行动/方法段、`🔸` 背景/约束段、`💡` 关键结果、`📚` 参考文献
- **空行分段**：每个标题/段前后用空行制造视觉留白（层级靠空行+emoji，不靠 Markdown）
- **项目符号**：`·` 无序、`1.` `2.` 有序（不用 `-`/`*` 以避免被当成未渲染语法）
- **行内强调**：`「」` 替代 `**加粗**`
- **不用分隔线**：`---` 会被渲染成字面短横，改用 `——————————————`
- **字数**：200–2,000 字（下限 200，上限截断）
- **零幻觉**：所有内容逐字源自 11 维摘要；实践启发由 `_derive_insights` 从 `innovations` 派生

完整可复用骨架见 `references/wechat-body-template.md`。

**两种 body 的关系**（`build_package` 同时携带）：
| 字段 | 内容 | 用途 |
|------|------|------|
| `body_markdown` | `render_wechat_article` 微信风味纯文本 | `WeChatDraftDelivery` 注入正文 |
| `metadata["markdown_source"]` | `render_article_body` Markdown 源 | 审计轨迹 / HTML 预览 fallback |

---

## 四、前置条件与登录链路

| 条件 | 路径 A (browser-bridge) | 路径 B (HTML) |
|------|--------------------------|---------------|
| opencli | 二进制可解析（`opencli_runtime.resolve_runtime`） | 不需要 |
| Chrome | **已登录 mp.weixin.qq.com** | 不需要 |
| 公众号 | 已认证的订阅号/服务号 | 不需要 |

browser-bridge 复用 Chrome 里已有的 mp.weixin.qq.com 登录态（不单独存账号密码）。
`_open_editor` 无法从 URL/cookie 提取 `token` 即抛 `DeliveryError("not logged in")`，
上层 `WeChatPublisher.publish` 捕获后回退 HTML 预览，**不硬失败**。

**登录步骤（人工，一次性）**：
1. Chrome 打开 https://mp.weixin.qq.com 并扫码/账密登录公众号后台。
2. 保持该 Chrome 会话（不退出、不清 Cookie）。
3. 校验：`opencli weixin drafts --window background -f json` 返回草稿列表即已登录。

---

## 五、发布命令

### 推荐：从 11 维摘要直接投递

```bash
# 自动 load_assets → 渲染微信风味正文(200-2000字) → stage → browser-bridge 投递
# 未登录时回退到 HTML 预览（data/publish_preview/wechat/*.html）
python -m redbook.automation.paper_to_wechat --paper-id 2302.08191
```

### 备选：先 stage 审核包，人工确认后再 publish

```bash
python -m redbook.automation.cli --data-root data stage \
  --platform wechat --paper data/paper_card.json --canonical-url https://arxiv.org/abs/XXXX
python -m redbook.automation.cli --data-root data publish \
  --platform wechat --staged-id <content_hash>
```

### 手动发布（路径 B）

1. 打开 `data/publish_preview/wechat/<title>.html`
2. 复制内容到公众号后台编辑器（图片为 `file:///` 本地路径，需逐张上传或先传图床）
3. 预览 → 保存草稿 → 人工审核后发布

---

## 六、代码入口（重写版）

| 模块 | 职责 |
|------|------|
| `redbook/infrastructure/wechat_delivery.py` | `WeChatDraftDelivery`（单会话 browser-bridge）、`WeChatDraftPayload`（校验：title≤64/body≥200/author≤8/封面存在）、`DeliveryReceipt`（title/cover_applied/body_chars/saved）、`DeliveryError` |
| `redbook/automation/paper_to_wechat.py` | `render_wechat_article`（微信风味纯文本）、`render_article_body`（Markdown 源）、`build_package`（同时带两种 body）、`deliver_article` |
| `redbook/automation/publishing.py::WeChatPublisher` | `validate`（title≤64/body≥200/图≤9）→ `stage` → `publish`（建 `WeChatDraftPayload` → `WeChatDraftDelivery().deliver`；`DeliveryError` 返回 `stage_error`；`not receipt.saved` 回退 HTML 预览 `save_unverified`） |
| `redbook/automation/validate_wechat_real_paper.py` | 真实论文端到端校验（LightGCL 2302.08191）：断言微信风味正文无 `**`/`##`/`---` 残留、含 emoji 标记、字数 200-2000、标题 21/64 |

**成功回包示例**：
```json
{
  "ok": true, "method": "browser-bridge",
  "title": "LightGCL：简单有效的图对比推荐学习",
  "cover_applied": true, "body_chars": 1437,
  "status": "draft saved",
  "detail": "\"LightGCL：简单有效的图对比推荐学习\" by 推荐系统研读 (with cover)"
}
```

---

## 七、发布记录

发布后记录到 `data/publish_results/wechat/`：
```json
{
  "paper_id": "arxiv:2302.08191",
  "platform": "wechat",
  "method": "browser-bridge" | "html_preview",
  "draft_id": "...",
  "staged_at": "2026-08-06T...",
  "published_at": null,
  "metrics": null
}
```

---

## 八、已知缺口 / 待办

- [ ] **草稿落库肉眼核验**：browser-bridge 已用 `#js_save_success` 标记判定 `saved`，但公众号后台
      `weixin drafts` 偶发 `EMPTY_RESULT`（解析器与后台布局不匹配）。以**后台草稿箱肉眼为准**，
      自动化 `saved` 标记仅作参考。
- [ ] **多图自动化**：当前仅 1 封面（取 `images[0]`）。多图深度图文需扩展正文 `upload` 多次，
      或走路径 B 手动上传。
- [ ] **临时草稿清理**：草稿箱已累积多次测试草稿（代码随想录 + 多轮 LightGCL）；
      `data/publish_queue/*/wechat.json` 有早期 buggy-run 残留。沙箱 safe-delete 拦截清理，
      需人工在后台删除测试草稿 / 手动移走残留队列文件。
- [ ] **`paper_to_wechat.py` 模块 docstring**：已随本重构更新，旧 `create-draft` 引用已清除。

---

## 九、风控

1. 所有草稿默认 `review_status=pending`，人工审核后才发布。
2. 同一论文只允许一个公众号草稿（`content_hash` 幂等）。
3. 草稿箱内容可在公众号后台修改后再发布。
4. 不使用任何非官方 API 或自动化群发；仅建草稿。

---

## 十、抓取能力验证 + 自动化发布工作流（2026-08-06 调研）

### 10.1 微信公众号抓取能力（实测结论）

OpenCLI `weixin` 提供 `search` / `download` / `drafts` 三个读命令，**抓取链路可用但有形态限制**：

| 命令 | 作用 | 实测可用性 |
|------|------|-----------|
| `weixin search <query> [--page --limit]` | 搜狗微信搜索公众号文章 | ✅ 返回 `rank/page/title/url/summary/publish_time` |
| `weixin download --url <mp.weixin.qq.com/s/SHORTID>` | 文章下载为 Markdown | ✅ 返回 `title/author/publish_time/status/size/saved` |
| `weixin drafts` | 列草稿箱 | ⚠️ 偶发 `EMPTY_RESULT`（解析器与后台布局不匹配） |

**关键限制（务必牢记）**：`search` 返回的 `url` 是 `weixin.sogou.com/link?url=...&src=11&signature=...`
形式的**会话绑定分享链接**。这种链接在微信外（普通浏览器 / WebFetch / OpenCLI download）**无法读取**——
`download` 报 `failed — no title`，浏览器打开只剩"微信公众平台"首页，`WebFetch` 报"参数错误"。
只有公众号内分享产生的**规范链接 `mp.weixin.qq.com/s/SHORTID`** 才能被 `download` 抓取。

**实测范例（代码随想录）**：
- `weixin search "再见Superpowers"` 命中《再见Superpowers!恭喜还没用这些skill的朋友们!现在不用学了!》
  （代码随想录，2026-7-28）。
- 其 Sogou 分享链接无法外部抓取 → 改用同文公开镜像 kamacoder
  （`notes.kamacoder.com/llm/news/gpt-5-6-no-superpowers.html`）还原全文结构。
- 产出：`data/weixin_crawl/代码随想录_再见Superpowers_结构.md` + `references/wechat-post-template.md`。

> 抓取策略：用 `search` 选题/找竞品 → 拿得到规范 `/s/SHORTID` 则 `download`；否则用公开镜像/转载还原。
> **不要依赖 Sogou 分享链接做自动化抓取**。

### 10.2 自动化公众号发布工作流（端到端设计）

```
阶段0  素材准备（已有 paper pipeline）
       11 维摘要 JSON + figures(架构图/对比表/效果图) + PDF
            │
阶段1  [可选] 抓取/选题参考
       weixin search <主题> → 找竞品/模板
       weixin download <规范/s链接> → 拉参考文（Sogou 分享链接不行）
            │
阶段2  渲染（paper_to_wechat.render_wechat_article）
       微信风味纯文本（emoji 标记 + 空行分段 + 「」强调，无 Markdown 语法）
       1,200-2,000 字深度图文 + 选 1 张封面（架构图优先）
       + title(≤64) / author(≤8) / summary(≤120)
            │
阶段3  建草稿（WeChatPublisher.publish → WeChatDraftDelivery）
       ├─ opencli 可用且已登录 → 路径A: browser-bridge（fill标题[verified] + innerHTML正文 + 封面 + 保存）
       └─ 未登录(DeliveryError: not logged in) → 路径B: HTML 预览
            │
阶段4  核验
       weixin drafts 比对 title（⚠️ 可能 EMPTY_RESULT，以后台肉眼为准）
            │
阶段5  发布（人工）
       后台审核 → 群发（自动化不群发）
```

### 10.3 失败 / 兜底矩阵

| 环节 | 失败信号 | 兜底 |
|------|----------|------|
| 阶段1 抓取 | Sogou 分享链接无法读 | 改用公开镜像/转载；或仅用 `search` 摘要 |
| 阶段3 登录 | `_open_editor` 提取不到 token → `DeliveryError` | `WeChatPublisher` 捕获 → 回退 HTML 预览（路径B） |
| 阶段3 标题 | `fill` 未 verified / `actual!=title` | `DeliveryError` → 回退 HTML 预览 |
| 阶段3 封面 | 上传/CDN/选图失败 | **非致命**：正文草稿照存，`cover_applied=False` |
| 阶段3 保存 | `#js_save_success` 未出现 → `saved=False` | 回退 HTML 预览 + `save_unverified:True` |
| 阶段4 核验 | `weixin drafts` 返回 `EMPTY_RESULT` | **以公众号后台草稿箱肉眼确认为准** |

### 10.4 关键设计决策（重写版）

1. **草稿优先、绝不群发**：自动化只建草稿，发布由人工在后台完成（合规 + 风控）。
2. **弃用 create-draft**：其标题丢失 + 正文不渲染 Markdown 两个 bug 在 OpenCLI 内部，
   wrapper 无法补救；新管线 bypass 它，改用同一 browser 桥的 `fill`/`eval`。
3. **标题 verified 断言**：杜绝「OpenCLI 报 draft saved 但标题为空」的假成功。
4. **innerHTML 注入正文**：修复正文像 changelog 的问题，按 `<p>` 段落正常渲染。
5. **auth 错误优雅回退**：未登录不报错中断，自动产出 HTML 预览，登录后即可用同包重发。
6. **模板驱动渲染**：正文严格按 `wechat-body-template.md` 骨架（微信风味纯文本），内容源自 11 维摘要，无幻觉。
7. **单封面约束**：路径 A 仅 1 封面；多图富文本走路径 B。

### 10.5 仍待解决

- [ ] Sogou 分享链接无法外部抓取（需规范 `/s/SHORTID` 或镜像）。
- [ ] `weixin drafts` 偶发 `EMPTY_RESULT`，落库核验需后台肉眼兜底。
- [ ] 路径 A 仅 1 封面——多图/富文本需扩展 browser-bridge 正文 `upload` 或走路径 B。
