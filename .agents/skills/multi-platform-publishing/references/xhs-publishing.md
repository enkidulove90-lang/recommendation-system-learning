# 小红书发布指南（OpenCLI 单会话 CDP 模式 · 唯一写入路径 · 全链路）

> ⚠️ **历史文档（2026-11-11）**：本文只保留作 OpenCLI / CDP / Cookie / 草稿箱底层排查参考。
> 论文帖的规范入口已改为 `python -m redbook.cli note <slug>`，规则见
> `.agents/skills/xhs-paper-draft/SKILL.md`、`redbook/docs/xhs-content-spec.md`
> 与 `config/xhs_content_rules.yaml`（单一事实源）。
> 下文 §8.0 / §8.1 的 `build_xhs_draft.py`、`render_note`、`cli stage --paper paper_card.json`
> 以及 §9 的 300–700 字模板均已作废，相关脚本已归档到 `archive/xhs_drafts/`，勿执行。

> 项目已从 `xhs-cli` 逆向 API 切到 **OpenCLI**（`redbook/config/opencli.yaml` 中 `legacy_xhs_cli.enabled: false`）。
> 本文件描述**从「文档选择」到「存草稿」的完整链路**，并**极度细化三个最易错环节**：
> **① 话题 CDP 上传　② PDF 文档 CDP 上传　③ 草稿保存真实链路**。
> 代码实现见 `redbook/infrastructure/xiaohongshu_delivery.py`
> （`OpenCliXiaohongshuDelivery._compose_and_save`）。

---

## 1. 全链路总览（一条持久 CDP 会话贯穿）

```
[文档选择] 选 PDF + 选图(figures) + 派生话题 + 生成标题/正文
   │
   ▼  opencli browser <session> open <creator_url> --window foreground
[打开编辑器]  （立即进入，不做长 wait）
   │
   ▼  upload input.upload-input <img1..img9>      ← 一次传全部
[上传图片]  wait time 4 → wait selector div.tiptap  ← 标题/正文框此时才渲染
   │
   ▼  fill input[placeholder="填写标题会有更多赞哦"] <title>   (≤20字)
[填标题]
   │
   ▼  type div.tiptap <body>                       ← ProseMirror 键入
[填正文]
   │
   ▼  ┌─ 每话题循环 ─────────────────────────────┐
   │  │ focus body 末尾 → execCommand 插入 #话题名  │
   │  │ → wait div.items div.item 建议下拉          │
   │  │ → click 最佳匹配项 → #文本被替换为实体       │
   │  └───────────────────────────────────────────┘
[★绑定话题]  （真实话题实体，可点击跳转）
   │
   ▼  upload input[type="file"][accept*=".pdf"] <paper.pdf>  ← 保存前完成
[★传PDF]   wait text <pdf文件名> 确认附件可见
   │
   ▼  触发 <xhs-publish-btn> 的 _onSave()           ← 最后一步
[★存草稿]  （方法调用 → 文本匹配 → leave-and-save → 自动保存 兜底链）
   │
   ▼  xiaohongshu drafts 前后比对：恰好 1 条新草稿、标题匹配、图片数==上传数
[核验]     （不一致则删草稿并报错）
```

**铁律（用户明确要求）**
1. 整篇笔记在**同一个未保存的编辑器会话**内完成：图片→标题→正文→话题→**PDF**→**最后才存草稿**。
2. **严禁「先 `publish --draft true` 存草稿再回草稿箱补附件」**：旧路径会先存盘关闭编辑器，回草稿箱点「添加组件→文件」时 CDP 上下文已丢失 → 语义定位失败（即用户报告的"CDP 附件步骤的语义定位失败"）。
3. **保存草稿必须是链路最后一步**。PDF 入口 `input[type="file"][accept*=".pdf"]` 始终在编辑器 DOM 中，不需要去草稿箱点「添加组件→文件」。

---

## 1.5 两种发布形态对照：带 PDF（CDP 全链路） vs 不带 PDF（opencli 纯 CLI）

代码里 `XhsPublisher._publish_opencli` 依据 `metadata.pdf_path` 是否为空，**二选一**走不同通道（见 `redbook/automation/publishing.py`）：

| 维度 | ① 带 PDF（CDP 全链路） | ② 不带 PDF（opencli 纯 CLI） |
|---|---|---|
| 触发条件 | `xhs.json` 的 `metadata.pdf_path` 为**非空**本地绝对路径 | `metadata.pdf_path` 为空 `""` |
| 底层实现 | `OpenCliXiaohongshuDelivery.deliver`（`_compose_and_save(attach_pdf=True)`） | `opencli xiaohongshu publish <body> --title … --images … --topics … --draft true` |
| 是否开浏览器 CDP | 是（一个持久会话贯穿：图→标题→正文→话题→PDF→存草稿） | 否（纯 CLI 子进程，无浏览器自动化） |
| 话题绑定 | 真实话题实体：`#话题` → 下拉 `div.items div.item` → click（§4） | `--topics a,b,c` 参数传入，由 opencli 内部处理，不跑 CDP 话题点击 |
| 本地 PDF 校验 | `DraftPayload.validate()` **强制** PDF 存在且后缀 `.pdf` | 不校验（根本不读 PDF 字段） |
| `topics` 是否必填 | **必填**（`validate` 缺则 `DeliveryError("real topic binding is mandatory")`） | 非必填（不跑 `DraftPayload.validate()`） |
| 图片 | 1–9 张本地图，存在性由 `validate` 校验 | `--images a,b,c`，1–9 张 |
| 标题 | ≤20 字（CDP 截断 + `validate` 双重卡） | `--title` 截断到 20 字 |
| 典型产物 | 图文笔记 **+ 可下载 PDF 附件** | 纯图文笔记（无附件） |
| 幂等性 | 每次**新建**一条草稿（**不幂等**） | 每次**新建**一条草稿（**不幂等**） |

### 何时用哪种
- **要附论文 PDF → 走 ① 带 PDF**：先把 PDF 拉到本地
  `data/parsed/<id>/<id>_origin.pdf`（arXiv 论文直接 `urllib` 下
  `https://arxiv.org/pdf/<id>` 即可），在 `xhs.json` 写 `metadata.pdf_path` 绝对路径，
  再 `publish`。**本环境已验证通过**（2026-08-20 OSWorld，`36.8MB` PDF 成功挂附件 +
  5 个话题实体全部绑定，新帖 `s:a4599a1a-…`）。
- **只发图文、无本地 PDF → 走 ② 不带 PDF**：`metadata.pdf_path` 留空 `""` 即可，
  不必下 PDF，发布更快、不占 CDP 会话。话题仍经 `--topics` 传入。

### 关键操作铁律
1. **两条路都不幂等**：同一 `staged_id` 重复 `publish` 会再建一条同名草稿。
   若想把「无 PDF 旧帖」升级成「带 PDF 帖」：先
   `OpenCliXiaohongshuDelivery()._delete('<旧 draft_id>')` 删旧，再走 ① 新建，
   避免草稿箱里出现两份同名帖。（本次 OSWorld 即：先建无 PDF 帖 `s:28bf401e-…`，
   验证带 PDF 路径成功后删旧、保留带 PDF 帖 `s:a4599a1a-…`。）
2. **带 PDF 必须本地先有文件**：`metadata.pdf_path` 指向的 `.pdf` 不存在 →
   `DraftPayload.validate()` 直接 `DeliveryError("missing local delivery assets: …")`，
   **不会降级到「不带 PDF」**——这是有意设计，不容忍「想附却没附上」的静默失败。
3. **草稿列表 API 不暴露 PDF 字段**：`xiaohongshu drafts` 返回的每条只有 `images` 数，
   看不到 PDF 是否真的附上。带 PDF 发布后，建议在创作者后台**点开该帖目测 PDF 卡片**做最终确认
   （`_attach_pdf` 已 `wait text <pdf文件名>` 等到附件卡出现、回执带 `pdf_name`，但列表 API 侧无法二次核验）。

### 复用已登录会话
两种形态都经 `resolve_runtime()` 复用已登录 Chrome；无需设 `OPENCLI_NODE/MAIN` 环境变量
（运行时自动从本机 nodejs 目录定位 `node.exe`）。

---

## 2. 第零步：文档选择（资产从哪来）

`paper_to_xhs.render_note(assets, image_limit=5)` 产出 `DraftPayload`，其资产来源：

| 资产 | 来源 | 约束 |
|---|---|---|
| `pdf_path` | `data/parsed/<id>/<id>_origin.pdf`（或 `_vlm.pdf`）| 必须是 `.pdf` 文件，存在性由 `DraftPayload.validate()` 强校验 |
| `image_paths` | `data/parsed/<id>/images/*.jpg` + `figures` 精选（架构图→对比表→效果图→Case）| 1–9 张；jpg/png/webp；跳过公式密集图、文字截图、小图标 |
| `title` | 渲染模板生成 | **≤20 字**，超长直接 `DeliveryError` |
| `body` | 渲染模板生成 | 300–700 字；含 emoji 段标题 |
| `topics` | 基类 `论文分享/人工智能`（来自 `_BASE_TOPICS`）+ 内容派生（大模型/智能体/AI编程/图神经网络/对比学习…）| **≥1 个**；真实话题实体，禁止正文死文本 `#foo` |

> ⚠️ **话题不再强制「推荐系统」**：`_BASE_TOPICS` 已改为 `("论文分享","人工智能")`，
> `derive_topics` 按 `_TOPIC_KEYWORDS` 从摘要正文扫描派生（如 LoopsBench 派生出
> `大模型/智能体/AI编程`）。此前曾把 `推荐系统` 写死进基类，导致非推荐系统论文
> （coding-agent/LLM 类）话题失真——该 bug 已修复。派生只看论文内容，不看固定标签。

> 文档选择 = 在 `data/parsed/<id>/` 下挑 PDF 与 N 张图、由 11 维摘要派生话题与标题。
> 任何本地资产缺失 → `DraftPayload.validate()` 抛 `DeliveryError("missing local delivery assets: ...")`，不降级、不静默跳过。

---

## 3. 选择器 / 命令速查表（实测对齐本账号 DOM）

| 步骤 | 选择器 / 命令 | 备注 |
|------|--------------|------|
| 打开编辑器 | `opencli browser <session> open https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image --window foreground` | `<session>` 跨多条 `browser` 命令保持同一标签页 |
| 上传图片 | `upload input.upload-input <img1> <img2> ...` | 一次传全部；accept=.jpg/.jpeg/.png/.webp；≤9 张 |
| 标题框 | `input[placeholder="填写标题会有更多赞哦"]` | **标题/正文框在上传第一张图之后才渲染**，上传前等待会找不到 |
| 正文框 | `div.tiptap` | 同上渲染时机；`type` 触发 ProseMirror 键入 |
| 话题按钮 | `button#topicBtn` | 点击展开推荐标签面板（不含搜索框）；话题搜索入口是正文里打 `#text` |
| 话题下拉项 | `div.items div.item` | 正文出现 `#text` 时弹出；文本形如 `#论文分享1829.5万浏览`；按归一化文本匹配 |
| PDF 附件 | `input[type="file"][accept*=".pdf"]` | 编辑器 DOM 内已存在，无需去草稿箱 |
| **保存草稿** | `<xhs-publish-btn>` 的 `_onSave()` / `_onSaveDraft()` / `_onDraft()` | 见 §6；**没有独立可见「存草稿」按钮** |

- `wait selector` 的 CSS 引擎**不支持 `*=` 子串选择器**：用精确占位符或 `div.tiptap`。
- 点击侧边栏「发布笔记」会**跳转到 `target=video` 视频发布页**（错误目标），不是保存。

---

## 4. ★ 话题 CDP 上传（极易错 · 最详细）

### 4.1 核心机制
小红书的「话题」是**可点击跳转的实体**。获取方式：在正文里打出 `#话题名` → XHS 弹出搜索建议下拉（`div.items div.item`）→ 点选最佳匹配项 → `#话题名` 被替换为 `<a class="tiptap-topic" data-topic="{...}">` 实体。

> 关键：下拉**仅在正文出现 `#text` 时才会弹出**。`button#topicBtn` 只展开推荐标签面板（不含搜索框），不是话题搜索入口。正文 `#text` 才是触发搜索下拉的唯一路径。

### 4.2 真实命令序列（每话题一次）
```
# 1) 光标移到正文末尾（聚焦 contentEditable 区，collapse 到末尾）
eval: (_focus_body_end_js)
     → querySelector('div.tiptap[contenteditable]')，focus，Selection 选末尾

# 2) 往正文里插入 #话题名（会触发搜索建议下拉）
eval: document.execCommand('insertText', false, '#论文分享')
      → 触发 input 事件 + keyup，让 XHS 过滤下拉

# 3) 等下拉出现
wait selector div.items div.item --timeout 15000

# 4) 点击最佳匹配项
eval: (_click_suggestion_js(topic))
     → 在 [div.items div.item, [class*="topic-item"], ...] 中
       按 norm(text) 精确匹配 → 否则 includes 匹配 → 否则取首项
     → target.click()
```

### 4.3 关键 JS 片段（来自 `_type_topic_js` / `_click_suggestion_js`）
```js
// 插入 #话题名（execCommand，不用 browser type——后者对 ProseMirror 间歇性 selector_not_found）
(function(topicName){
  const text = '#topicName';
  document.execCommand('insertText', false, text);
  const a = document.activeElement;
  if (a) { a.dispatchEvent(new Event('input', {bubbles: true}));
           a.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true, key: text.slice(-1)})); }
})('论文分享')

// 选取（归一化匹配，点击）
(function(topicName){
  const norm = v => (v||'').replace(/^#/,'').replace(/\s+/g,'').trim();
  const want = norm(topicName);
  const SUG = ["div.items div.item","[class*=\"topic-item\"]", ...];
  // 收集可见项 → 精确 → includes → 首项 → click
  ...
})('论文分享')
```

### 4.4 失败模式与对策
| 现象 | 根因 | 对策 |
|---|---|---|
| `wait selector div.items div.item` 报 Selector not found | 正文还没有 `#text`（没触发搜索下拉），或打字后 editor 未获焦点 | 确保① `focus_body_end_js` 聚焦到 contentEditable ② `execCommand('insertText')` 插入了 `#text` ③触发 input/keyup 事件 |
| `_click_suggestion_js` 返回 `{ok:false,count:0}` | 用了 OpenCLI 源码的 `[class*="topic-item"]` 作首选 | `div.items div.item` 为本账号下拉项格式，排在选择器列表首位 |
| 下拉不出现 / 命中错误话题 | 没做归一化匹配，或 topicName 带了 `#` | `norm` 去 `#`/空白后精确匹配 → includes 兜底 → 首项兜底 |

---

## 5. ★ PDF 文档 CDP 上传（极易错 · 最详细）

### 5.1 为什么必须在保存前、同会话内完成
PDF 附件入口 `input[type="file"][accept*=".pdf"]` **始终存在于编辑器 DOM**（不是草稿箱里的「添加组件」）。一旦先 `save` 关闭编辑器，再回草稿箱点「添加组件→文件」，CDP 上下文已丢失，文件 input 无法定位 → 用户反馈的"语义定位失败"。所以 PDF 必须在 `_save_draft()` **之前**、`_compose_and_save` 的同一会话里上传。

### 5.2 真实命令序列
```
# 1) 上传 PDF 到专用 file input（注意：不是图片 input）
upload input[type="file"][accept*=".pdf"] <paper.pdf>

# 2) 等文件卡片出现（上传被确认后才渲染附件卡）
wait text <pdf文件名> --timeout 40000
```
对应代码：
```python
def _attach_pdf(self, pdf_path: Path) -> None:
    self._must("upload pdf",
        self._browser("upload", PDF_INPUT_SELECTOR, str(pdf_path)))
    self._must("wait pdf visible",
        self._browser("wait", "text", pdf_path.name, "--timeout", "40000"))
```
`PDF_INPUT_SELECTOR = 'input[type="file"][accept*=".pdf"]'`

### 5.3 失败模式与对策
| 现象 | 根因 | 对策 |
|---|---|---|
| 附件没附上 / 草稿无 PDF | 先 save 后补 PDF（旧路径）| 严格 `_attach_pdf` 在 `_save_draft` 之前调用 |
| `wait text` 超时 | 文件名含特殊字符 / 上传失败 | 用 `pdf_path.name` 精确等待；确认 PDF 文件存在（`validate()` 已校验）|
| 上传到图片 input | 选错 selector | PDF 用 `input[type="file"][accept*=".pdf"]`，图片用 `input.upload-input`，二者不同 |

---

## 6. ★ 草稿保存真实链路（最容易踩坑 · 最详细）

### 6.1 关键事实：没有可见「存草稿」按钮
小红书创作中心的「保存草稿」**不是独立可见按钮**。发布动作封装在一个 web component `<xhs-publish-btn>` 里：
- 保存草稿 = 调用它的方法 `_onSave()`（草稿）/ `_onSaveDraft()` / `_onDraft()`
- 发布 = `_onPublish()`
实测通过「Path 1: 方法调用」稳定成功。点击侧边栏「发布笔记」会跳视频页，不是保存。

### 6.2 真实调用链（四层兜底，来自 `_save_draft`）
```
_save_draft():
  ① 方法调用：遍历可见的 <xhs-publish-btn>，依次试 _onSave / _onSaveDraft / _onDraft
      成功 → wait 4s → return {ok:true, via:'method'}
  ② 文本匹配：找 button/[role=button] 文本 == '暂存离开'|'存草稿'|'保存草稿' 且可见未禁用 → click
      成功 → wait 4s → return
  ③ leave-and-save：click '返回'|'关闭'|'取消'|'离开' → 再调一次 ①
      成功 → return
  ④ 自动保存检测：DOM 含 '草稿箱('|'保存于'|'编辑于' 标记 → 视为已自动保存
      成功 → return {ok:true, via:'auto-save'}
  全失败 → raise DeliveryError("could not trigger save-draft action")
```

### 6.3 保存后核验（防"假成功"）
```python
before = self._drafts()          # open 前快照
... 全程 ...
after  = self._drafts()           # save 后快照
draft  = _new_draft(before, after, title)   # 恰好 1 条 title 匹配的新草稿
if int(draft.get("images",0)) != len(payload.image_paths):
    self._delete(draft["id"])    # 图片数对不上 → 删掉重来
    raise DeliveryError("saved draft image count differs from verified manifest")
```
`drafts` 走 `xiaohongshu drafts -f json --window background --site-session ephemeral`。

### 6.4 失败模式与对策
| 现象 | 根因 | 对策 |
|---|---|---|
| 草稿创建成功但 PDF 没附 | 先 save 后补 PDF | 见 §5，PDF 在 save 前同会话上传 |
| 点击「发布笔记」跳视频页 | 那是菜单项不是保存 | 保存走 `<xhs-publish-btn>` 方法（§6.2）|
| 方法调用无响应 | 组件未挂载/不可见 | 走 ② 文本匹配 → ③ leave-and-save → ④ 自动保存 兜底链 |
| drafts 比对出 0 或多条 | 并发/时序 | `_new_draft` 要求**恰好 1 条** title 匹配，否则报错 |

---

## 7. 环境 / 配置

- **运行时**：OpenCLI 在 `C:/Users/xu.yan1/nodejs/node-v24.18.0-win-x64/`
  （`node.exe` + `node_modules/@jackwener/opencli/dist/src/main.js`）。Python 侧经
  `redbook/infrastructure/opencli_runtime.py` 的 `resolve_runtime()` 直接 `node <main.js>` 调用，
  **不要走 MinGW 的 `opencli` shim**（路径会被错转成 `c:\c\Users\...`）。
- **浏览器命令超时**：OpenCLI 默认 60s，创作中心自动化需更长。每次调用注入
  `OPENCLI_BROWSER_COMMAND_TIMEOUT=270~300`（见 `_run`）。
- **登录**：在 Chrome 登录 xiaohongshu.com 后无需额外操作；OpenCLI 复用已登录 Chrome 会话。
- **认证探针**：`xiaohongshu whoami` 偶发被原生对话框阻塞；改用 `xiaohongshu drafts` 作探针更可靠。
- **配置**：`redbook/config/opencli.yaml`（`delivery_order: [topics, pdf, draft]`、
  `limits.title_max_chars: 20`、`images_max: 9`、`safety.auto_publish: false`）。

---

## 8. 规范命令（canonical）

### 8.0 推荐入口：`build_xhs_draft.py`（自动派生话题 + 绑定 PDF）

这是新论文的规范构建器，封装了「`load_assets` → `render_note`（派生话题/绑定 PDF）→
`XhsPublisher.stage`」全链路，CLI 与 `paper_to_wechat.py` 对齐：

```bash
# stage（不发布）：话题/标题/正文/5图/PDF 全进审核包
python -m redbook.automation.build_xhs_draft \
  --paper-id 2608.00267 \
  --canonical-url https://arxiv.org/abs/2608.00267 \
  --code-url https://github.com/microsoft/Loopsbench \
  --project-url https://loopsbench.ai/

# 人工核对 data/publish_queue/<hash>/xhs.json 后，推送到草稿箱（需已登录会话）
python -m redbook.automation.build_xhs_draft --paper-id 2608.00267 --publish
```
- `--code-url` / `--project-url`：可选，写入 `links.code` / `links.project`（如 GitHub、项目页）。
- 话题来自 `render_note` 的内容派生（见 §2 警告），**不写死标签**。
- `deliver_draft` 先 `stage` 返回 `staged_id`；带 `--publish` 才调 `XhsPublisher.publish`。
- 旧 `cli stage --paper paper_card.json` 路径**不派生话题**，仅兼容保留。

### 8.1 编程式（同底层）

```python
from pathlib import Path
from redbook.automation.paper_to_xhs import load_assets, render_note, deliver_note
ROOT = Path(".")
assets = load_assets("<paper_id>", ROOT)          # 读 11 维摘要 + figures + PDF
note   = render_note(assets, image_limit=5)        # 标题≤20字/正文300-700字/5话题/5图
receipt = deliver_note(note, attach_pdf=True)      # 单会话 CDP：话题→PDF→存草稿
# receipt = {'draft_id','title','image_count','topics','pdf_name'}
```

或走 CLI 调试：
```bash
python -m redbook.cli save-xhs-draft \
  --draft data/publish_queue/<paper_id>/xhs.json \
  --image data/parsed/<paper_id>/images/a.jpg \
  --pdf   data/parsed/<paper_id>/<paper_id>_origin.pdf
```
两者底层都是 `OpenCliXiaohongshuDelivery`，顺序一致：**话题 → PDF → 存草稿（最后）**。

---

## 9. 帖子格式模板（沿用）

```
🎓 [论文标题/一句话背景]
一句话：xxx
🧠 解决什么问题：xxx
✨ 三个关键设计：1. ... 2. ... 3. ...
📊 效果：最亮眼数字
⚠️ 局限：xxx
💡 完整 11 维度精读已整理成 PDF，附在笔记里，可直接翻。
📄 arXiv: <paper_id>
```
- 段标题用 emoji：🎓 ✨ 🧠 📊 💡 ⚠️
- 标题 ≤20 字；正文 300–700 字；图片 5 张；话题 5 个
- 图片格式 jpg/png；跳过公式密集图、文字截图、小图标

---

## 10. 常见问题（实测更新）

- **Q: `wait selector input[placeholder*="标题"]` Selector not found？**
  `wait selector` 不支持 `*=`；用精确占位符 `input[placeholder="填写标题会有更多赞哦"]` 或 `div.tiptap`。

- **Q: 上传图片报 "element may not exist or may be hidden"？**
  标题/正文框在**上传第一张图之后**才出现；上传前长 `wait` 会让上传 input detached。**上传紧跟 `open` 立即执行**，不前置长 wait。

- **Q: 话题下拉命中 0 项？**
  创作中心已于 2026-08 改版，`div.items div.item`、正文 `#topic` chip、`button#topicBtn` 搜索框**全部失效**。改用 §4 的“点击推荐 `.tag` 芯片 + 正文关键词兜底行”机制：列出可见 `.tag` 芯片 → 点击归一化后落在学术白名单里的芯片 → 末尾追加 `🏷 关键词：#...` 行。

- **Q: 草稿创建成功但 PDF 没附上？**
  必须在**同一编辑器会话内、save 之前** `upload` 到 `input[type="file"][accept*=".pdf"]`，并 `wait text <pdf文件名>` 确认可见后再保存。绝不可先存草稿再回草稿箱补。

- **Q: 点「发布笔记」后跳到视频发布页？**
  那是侧边栏菜单项，不是保存。保存走 `<xhs-publish-btn>` 的 `_onSave()`（见 §6）。

- **Q: 到底走「带 PDF」还是「不带 PDF」？**
  看 `xhs.json` 的 `metadata.pdf_path`：
  - **非空（指向真实本地 `.pdf`）** → 自动走 ① CDP 全链路（`OpenCliXiaohongshuDelivery`），图文 + PDF 附件一次性建好，话题绑真实实体。
  - **空 `""`** → 自动走 ② `opencli xiaohongshu publish` 纯 CLI，只发图文、无附件、无浏览器自动化。
  两者都不幂等；要把「无 PDF 旧帖」升级成「带 PDF」必须先 `_delete` 旧帖再重发（详见 §1.5）。

---

## 11. 手工精挑「好看」的图（覆盖视觉回退）

`select_images` 默认走 `vision_enhancer` 选核心图 + 缺失时按**文件大小**回退到 `images/`。
对论文类笔记来说，回退路径常挑出公式截图、YAML 配置、单色表格 ——「能用但不好看」。
要得到更适合小红书封面的配图（架构图/概览图/结果图），用下面这套手工精挑流程覆盖：

### 11.1 找出论文里真正的「图」+ 图注

MinerU 解析产物里，**image/chart 块**才对应论文作者标注的图；公式和表格是另外的块。
`data/parsed/<id>/<id>_content_full.json` 是带分块的版本，结构是 `list[block]`，
每块有 `type`、`img_path`（或块内嵌的 jpg 哈希）、以及 markdown 里的 caption。

```python
import json, re
d = json.load(open("data/parsed/2608.00267/2608.00267_content_full.json", encoding="utf-8"))
md = open("data/parsed/2608.00267/2608.00267.md", encoding="utf-8").read().splitlines()
for b in d:
    if isinstance(b, dict) and b.get("type") in ("image", "chart"):
        s = json.dumps(b, ensure_ascii=False)
        m = re.search(r"([0-9a-f]{64}\.jpg)", s)
        if not m: continue
        # 在 .md 里用前后两行作为图注
        for i, ln in enumerate(md):
            if m.group(1) in ln:
                capt = (md[i-1].strip() if i > 0 else "") + " | " + (md[i+1].strip() if i+1 < len(md) else "")
                print(f"[{b['type']}] {m.group(1)[:18]}  {capt[:160]}")
                break
```

### 11.2 用 Read 工具肉眼挑

候选图（如 architecture / framework / result / chart）通过 `Read` 看图选 5 张：
- 排除：纯公式、纯 YAML 配置、纯黑白表格、文字密度 >60% 的图。
- 优先：3-panel overview、polar/radar 性能对比图、colored DAG/runtime 流程图、彩色结果柱状图。

### 11.3 覆盖 `<id>_figures.json`（一行脚本）

`select_images` 按 `_FIGURE_PRIORITY = ("architecture","framework","model","result","table","chart","other")`
排序；把要展示的图按想要的封面顺序填进 `_figures.json` 的 `figures` 列表，
手赋 `figure_type`，再 `build_xhs_draft` 即可。

```python
# data/logs/curate_figures_2608.py —— 完整示例
import json, time
from pathlib import Path

p = Path("data/parsed/2608.00267/2608.00267_figures.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["figures"] = [
    # 1. 封面（架构/概览图）
    {"image_file": "images/<hash>.jpg", "figure_type": "architecture",
     "description": "Figure 2: Overview of the pipeline ..."},
    # 2. 头图（结果 chart / polar）
    {"image_file": "images/<hash>.jpg", "figure_type": "framework",
     "description": "Figure 1: Polar chart of model performance ..."},
    # 3-5. 方法图（framework / model / result / chart 顺次填）
    ...
]
data["figures_count"] = len(data["figures"])
data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
data["note"] = "精挑后覆盖；按 figure_type 排序决定封面顺序"
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
```

> ⚠️ **覆盖而非追加**：figures.json 改成 5 条 = 「仅用这 5 条」，不需要回退；
> 改成 5~9 条 = 视觉排序 + 末尾兜底。`select_images` 已按 type 优先级选前 5 张。

### 11.4 重新生成 + 发布 + 删旧草稿

```bash
# 重新 stage（新 staged_id）
python -m redbook.automation.build_xhs_draft --paper-id 2608.00267 ...

# 发布（CDP 链路；新 draft_id）
python -m redbook.automation.build_xhs_draft --paper-id 2608.00267 --publish

# 删旧草稿（用 OpenCliXiaohongshuDelivery._delete）
python -c "from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery as D; D()._delete('s:<old_draft_id>')"
```

### 11.5 失败模式
| 现象 | 根因 | 对策 |
|---|---|---|
| 精挑后图序仍按大小排 | 改完了 figures.json 但忘了重新跑 `build_xhs_draft` | 重新跑 stage，两次 `content_hash` 不同即代表覆盖生效 |
| 草稿箱里多一份旧的 | 没删旧 draft | 走 11.4 第三步；脚本化更稳 |
| MinerU 没把图注写进 caption 字段 | `_content_full.json` 直接无 caption | 从 `.md` 同行/上下行抓（§11.1 的回退抓法） |
| 视觉模型把图都判成 `other` | 公式/配置图被选为核心图 | 跳过 vision 选，直接手工精挑（§11.3）|
