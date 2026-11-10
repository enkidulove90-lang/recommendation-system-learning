> **归档说明（2026-11-10）**：本文件是 WorkBuddy 用户级 skill `xhs-latest-paper-draft` 的原文，
> 上架到仓库供其它 IDE 参考历史踩坑细节。其中 `Read` / `Skill` / `ViewImage` / `present_files`
> 是 WorkBuddy 专有工具名，`C:/Users/xu.yan1/...` 是原机器绝对路径，需按当前 IDE 与机器映射。
> **规范以 `../SKILL.md` + `config/xhs_content_rules.yaml` + `redbook/docs/xhs-content-spec.md` 为准**：
> 内容生成已统一到 `render_post`，不要再按本文的「手写 `build_xhs_draft_*.py`」路径新建脚本。

---
name: xhs-latest-paper-draft
description: >
  MUST USE when the user asks to 找一篇最新的论文并按小红书发布要求做成草稿（选题→论文原图→标题/正文→stage→推草稿箱→核验）。
  触发词：小红书论文草稿、最新论文发小红书、用论文原图发小红书、arxiv 发小红书、小红书链路发文、
  XHS paper draft、latest paper to Xiaohongshu、论文速递草稿。

  NOT for: 微信公众号 / 知乎发布（用 multi-platform-publishing）；纯论文摘要无发布意图（用 paper-summary-log）。
  与 multi-platform-publishing 的关系：本 skill 负责「选题 + 素材 + 内容规格」，发布细节（CDP 选择器/话题绑定/PDF 附件）
  仍以 multi-platform-publishing/references/xhs-publishing.md 为准。
agent_created: true
---

# 最新论文 → 小红书草稿（可复用全链路）

## 何时用
用户说「找一篇 XX 年 X 月最新的（大模型/推荐系统/Agent）论文，参考小红书发布要求做草稿」，
并通常附带格式约束（正文 ≤N 字、标题 ≤20 字、风格配比、要用论文原图/高质量图）。

## 0. 先加载发布 skill
`Skill(multi-platform-publishing)` — 里面有 XHS 的 CDP 链路、话题绑定、PDF 附件、保存草稿的全部细节与选择器。
本 skill 不重复这些，只补「选题 + 原图 + 人工 payload + 落盘位置」链路。

## 1. 选题：抓最新批次
```bash
# arXiv API（注意：周末无批次；周一早间批次常尚未索引 → 最新日期通常落后 1-2 天）
#   http://export.arxiv.org/api/query?search_query=cat:cs.CL+OR+cat:cs.AI
#        &start=0&max_results=80&sortBy=submittedDate&sortOrder=descending
```
- 先用 WebFetch 问：**最新 distinct published date 是哪天 + 列出 25 篇（id/标题/日期/一句话）**。
- 选题三准则：① 主题要与读者相关（编码 Agent / Agent 记忆 / 效率 / 安全）；② **原图要多**；③ 数字要具体。
- 用源文件快速探测原图存量（比下 PDF 更快）：
```bash
# 列出 e-print 里的图文件数量与名字（>=8 张才好挑；含 qualitative/before-after 更佳）
GET https://arxiv.org/e-print/<id>  → tar 列出 *.png/*.pdf/*.eps
```

### 1.5 变体：用户给了一份候选清单，要求"挑配图观赏性最高的"
1. **先定位**：用**短名**（作品名/缩写）查 arXiv，别用整句短语——`all:"cross-domain sequential recommendation"` 这类短语查询常常 0 命中，而 `all:ACE` / `all:GraphLoRA` 能命中。
2. **再筛图**（按图库判断，不用先读全文）：批量拉 e-print 源包，列出图文件数量 + 文件大小。
   - 判据：**3D 嵌入/降维可视化、qualitative 前后对比、大尺寸多面板图** > 常规折线/柱状图 > 框图。
   - 实测对比（2026-10 那次）：ACE（8 图，含 3 张彩色 3D 嵌入散点）胜出；DIGER（8 图但以折线漂移图+热力图为主）、GenCDSR（4 图）、UniPinRec（3 图）、GraphLoRA（6 图，框图为主）次之。
3. **必须真的看图**：下载 top-2 候选的图，用 `Read` 目视确认观感（是否彩色、是否自解释、能否撑封面），再定选稿——不要只看文件名和小大。
4. **诚实报告缺口**：工业界论文（Pinterest/淘宝等）和部分期刊（如 ACM TORS）常常**查不到 arXiv 版本** → 直接说明"这几篇无公开源文件，无法取原图"，不要编造图或拿别的论文顶替。
5. ⭐ **若用户强调「要有算法架构图 / 图片质量要高」，筛选标准要升级为"矢量框架图优先"**：
   - 在源包里找 `figures/`、`Figure/`、`figs/` 下的 **framework / model / overview / arch 之类 .pdf**——矢量图用 PyMuPDF 3x 渲染可达 **3000–4500px、500KB+**，是清晰度天花板。
   - 实测：DIGER（`figs/Framework_simplified_main.pdf` → 4107×1859）优于 GenCDSR（4 图）/UniPinRec（3 图）/GraphLoRA（6 图）；**ACE 属反例**——通篇没有架构图、只有 620×580 光栅小图，被用户退回。
   - 判据排序（要架构图时）：**有矢量框架图 + 另有大数据结果图** > 只有光栅小图 > 完全没有架构图（需自绘，见 §2.6）。
   - 渲染命令：`fitz.open(pdf)[0].get_pixmap(matrix=fitz.Matrix(3.0,3.0), alpha=False).save(png)`。

### 1.6 ⭐ 判断「论文有没有开源代码」——别只搜论文名（踩过坑）
**踩坑记录（2026-10-13，SIHG-Rec）**：只按论文名搜 GitHub（`q=SIHG-Rec`）返回 0，就下了"未见公开代码"的结论；
实际论文第 4 页脚注写着 `Code is available at: https://github.com/Jinfeng-Xu/Multimodal-Recommendation-Library`
——作者的代码放在**自己的「模型库/合集」仓库**里，不在同名仓库。结论写进 deliverable 后才被用户质疑，返工。

**正确流程（三步都要做）**：
1. **扫 PDF 全文找 URL 与开源声明**——不要只看摘要区；`Code is available at` / `github.com` 常出现在
   **首页脚注或方法节脚注**：
   ```python
   import fitz, re
   for i, p in enumerate(fitz.open(pdf)):
       for m in re.finditer(r"https?://[^\s\)\]\}>,]+", p.get_text()):
           print(i+1, m.group(0))
   ```
2. **查作者本人的 GitHub 账号下全部仓库**（`https://api.github.com/users/<user>/repos?per_page=100&sort=updated`）。
   高产作者会把多个工作的代码放在 `X-Library` / `Awesome-X` 这类合集仓库里，并按 `[会议'年]` 标注在 description 上。
3. **确认"目标实现"是否真的已经在库里**——区分**声明开源**与**已发布**：
   查 `src/models/`（有没有 `<model>.py`）、`src/configs/model/`（有没有 `<MODEL>.yaml`）、README 的模型清单与分支列表。
   合集仓库常见状态是"论文已标注、实现待补"（作者通常会随后补上）。

**怎么写进内容**：如实分档——`已开源（给出仓库）` / `声明开源但实现待补（给出声明地址 + 截至日期）` /
`未开源`。**永远不要**把"论文名搜不到仓库"直接写成"没有开源代码"。

## 2. 素材：优先论文原图
```bash
# 下 PDF（做附件）与源包（做图）
https://arxiv.org/pdf/<id>      → data/parsed/<id>/<id>_origin.pdf
https://arxiv.org/e-print/<id>  → data/parsed/<id>/source/src.tar.gz  然后 tarfile.extractall
```
- **PDF 矢量图 → PNG**（PyMuPDF，不要装 poppler）：
```python
import fitz
pix = fitz.open(pdf_path)[0].get_pixmap(matrix=fitz.Matrix(2.6, 2.6), alpha=False)
pix.save(out_png)
```
- **源包里已经是 PNG 的**（teaser、qualitative、before/after）直接 copy，质量最高。
- 选图顺序：① 系统总览/架构图（封面）→ ② 结果大图（多面板）→ ③ before/after 视觉对比（社交平台最吃）→ ④ 机制流程图。
- 用 `Read` 工具**逐张目视**再定稿（确认可读、不是公式截图、不是纯文字表）。
- 只有原图不足 5 张时才自制要点卡（PIL + `C:/Windows/Fonts/msyh.ttc`），并在 figures.json 注明「自制」。

## 2.5 变体：论文来自 OpenReview / 无 arXiv 源包
OpenReview 的 `openreview.net/pdf?id=XXX` **直连会被 JS 挑战拦成 ~4KB HTML**（换 UA/Referer 也无效）。
此时**优先找官方代码仓库**（forum 页里的 Code 链接）——论文源与 figures 通常都在里面：

```bash
# 1) 拿身份信息（标题/作者/venue/abstract/Code 链接）：WebFetch forum 页
https://openreview.net/forum?id=<id>
# 2) 克隆官方仓库（本环境 raw.githubusercontent.com 可能 DNS 不可解析，但 git clone 可用）
git clone --depth 1 https://github.com/<org>/<repo>
#    典型内容：paper/main.pdf（当附件 PDF）+ paper/main.tex（图注与精确数字）+ figures/*.png（原图）
#    raw 不通时的备选：api.github.com/repos/<o>/<r>/contents/<path>（<1MB 文件返回 base64）
```
**关键**：仓库 figures 的命名（如 `difficulty_gradient_unified.png`）与论文图号无关，
必须用 `main.tex` 的 `caption{}` 反查每张图的准确含义，别凭文件名猜（否则图注/文案会写错）。
拿到的 `paper/main.pdf` 直接当本地附件（`metadata.pdf_path` 指向它）即可。

## 2.6 论文没有架构图 / 图太小怎么办（用户明确要求过）
用户曾直接批评："**这个文章没有算法架构图是不对的，图片质量也不高，文本根本看不出来在干什么**"。
很多方法类论文（尤其「改一步预处理」型）**通篇没有 pipeline 图**——只有动机可视化 + 曲线 + 表格。这时：

1. **先确认真的没有**：查源包全部图文件 + `grep -rn includegraphics` 所有 tex（含 `Figures_tex/*.tex`）；再去官方仓库 `git clone` 找 README 里的图（**可能真的没有**）。
2. **自绘架构图**（合法且必须）：
   - 依据论文**方法节**逐步骤复现（读 `sec-model.tex` 之类，把公式/模块名落到图上），不要凭摘要想象。
   - 用 PIL 画横排模块 + 箭头 + 一个机制 inset，输出 ≥1800px 宽（手机上看要清晰）。
   - **图上与 figures.json 都要标注"示意图 · 依据论文 §N 绘制"**，不能冒充论文原图。若论文/仓库确实无图，也在 footer 注明。
3. **低分辨率小图（<800px）不要单张发**：把同一组对比面板（如 620×580 ×3）**合成一张纵向对比大图**（每面板放大到 1040px 宽 + 中文小标题 + 彩色边框），观感远好于 3 张糊图；也省图位。
4. **正文必须能"看出在干什么"**：写清 ① 输入是什么 ② 中间加了一步什么 ③ 输出给了谁 ④ 不改什么；并**显式引用图号**（"看图 1 的流程图""看图 2 第一张"）。自绘架构图应放**封面第 1 张**。
5. ⚠️ **PIL 排版坑**：自己写的自动换行函数遇 `\n` 会被当普通字符 → 文字溢出框外并互相重叠。
   → 宁可**手工把每行写死成短字符串列表**，逐行 `d.text`；画完**必须用 `Read` 看图**确认无溢出/重叠再发布。

## 2.7 变体：期刊论文（ACM DL 等）——CC-BY PDF 拿不到时走真实浏览器
**症状**：`dl.acm.org/doi/pdf/<doi>` 对 Python/curl 一律 **403**（Cloudflare）；Unpaywall/OpenAlex 说 `is_oa: true / license: cc-by`，但 `pdf_url` 是 `None`、只给 DOI → 说明是**出版商侧 OA**，没有仓库镜像。fatcat/web.archive.org 在本网络可能超时。

**解法：用项目自带的 OpenCLI 真实 Chrome（`opencli browser` 通用桥）过挑战后 fetch 字节**——不用新装 Chromium：
```bash
opencli browser <session> open "https://dl.acm.org/doi/<doi>" --window background   # 首次会显示"正在进行安全验证"
# 轮询等挑战自行放行（真实浏览器通常几秒内过）：eval 取 document.title，不再是验证页即可
opencli browser <session> eval "<js>"        # 在页面上下文里 fetch 官方 PDF
```
- 现成脚本：`fetch_acm_pdf.py <doi> <out.pdf> [session]`（已含 probe → fetch → 分块 base64 回传 → 落盘；`SKIP_OPEN=1` 可复用已放行的会话，避免重新触发挑战）+ `acm_wait_pass.py`（轮询挑战是否放行）。
- 关键实现点：把 PDF 字节挂到 `window.__pdf`，再**分块**（≤2MB 原始字节/次）eval 取 base64，避免单次返回过大。
- 铁律：**先 open 页面过挑战，再在同会话里 fetch**；直接 open PDF URL 会被 PDF viewer 接管、拿不到字节。

**期刊 PDF 的配图（重点）**：这类排版论文的图**多为矢量**（`page.get_images()` 只返回每页重复的模板底图，别被误导），不能 `extract_image`。做法是**按图注定位裁剪 + 高倍渲染**：
- 现成脚本：`extract_sihg_assets.py`（模板可复用）——用 `page.search_for(<图注短语>)` 定到图注行，再在"图注上方 + 该栏 x 范围"内对 `get_drawings()` 与 `get_image_info()` 取并集 bbox，最后 `matrix=Matrix(4,4)`（≈288 DPI）clip 渲染 → 1800px 级高清 PNG。
- ⚠️ **必须把上界卡在"上一个图注的下边"**：否则同一页两张图会被连在一起裁进去（实测 Fig.11 把 Fig.10 的尾巴带进来了）。实现：收集本页所有以 `Fig./Figure/Table` 开头的文本行作为锚点，取"位于目标图注之上且最靠下的锚点 bottom"当上界。
- 表格（Table N）通常是纯文本、**没有 drawings** → 自动裁剪会退化成空/极小框。**建议不要直接发学术表格截图**（手机上不可读），改为**自制数字卡**（PIL，把表里关键数字重排成大字号 + 强调色），并在 figures.json 标注"自制"/正文注明来源表号。
- ⚠️ 期刊 PDF 的字体连字可能损坏（`confirms`→`conirms`），`search_for` 用**不含连字的短语**更稳。

## 2.8 从 PDF 里裁内联图（tikz/pgfplots 之类"没导出成文件"的图）
有些图（尤其 pgfplots 画的曲线图）在源包里**没有独立文件**，只存在于编译后的 PDF 里，需要裁。
现成通用脚本：`crop_pdf_figure.py <pdf> <页码> <图注定位短语> <输出png> [最大高度pt] [zoom]`

```bash
python crop_pdf_figure.py paper.pdf 8 "Hit@3 vs" out/fig_scaling.png 300 6.0
```
原理：`page.search_for(<图注短语>)` 定位图注 → 在"图注上方"收集 `get_drawings()` + `get_image_info()` 求并集 bbox → 高倍 clip 渲染（矢量图放大无损）。
- ⚠️ **上界必须卡在"本页上一个图注的下边"**，否则同页两张图会连在一起被裁进来。
- ⚠️⚠️ **横向不能只用矢量 bbox**：坐标轴刻度/label 是**文本、不属于 drawings**，会被切掉（实测图框左沿 94pt、刻度起点 ~70pt，裁在 84pt 就把 `0.104` 切成了 `4`）。
  → 脚本做法：`x0 = max(页边距, min(bbox.x0, 图注.x0) - 48)`、`x1 = min(页右边距, max(bbox.x1, 图注.x1) + 14)`。
- **裁完必须 `Read` 看图**，确认刻度/label/图例都在框内再进 carousel。
- 单栏图矢量放大到 6x 可达 1200–1600px，足够小红书；别停在 3–4x。

## 3. 内容：标题/正文硬约束
- **标题 ≤20 字**（`len()` 按字符数，中英混排每个字母算 1；写完必须 assert）。
- **正文 ≤1000 字**（项目内 `paper_to_xhs.BODY_MAX` 也是 1000）；结构：🎓一句话 → 🧠问题 → ✨机制 → 📊数字 → 💡启示/看点 → ⚠️局限 → 📄链接 → ✨关注语。
- 30% 人性化（开头钩子 + 「给做 X 的人」落地建议段）+ 70% 严谨（**只用论文里的精确数字**）。
- **只引用最终摘要/正文里的主张**：源码里被 `%` 注释掉的废弃草稿措辞不要用（曾遇到 `crutch/amplifier` 只存在于注释、正文 0 次）。

### 3.1 文风铁律（用户明确反馈过，务必遵守）
用户曾直接否掉一版文案：**「这个写法太生硬了不知道在写什么」**。踩雷点与改法：

| ❌ 生硬写法（翻译腔/行话） | ✅ 平实写法 |
|---|---|
| 直接搬英文分类名：`silent bypass / self-correction / error propagation` | 「干脆无视那处改动 / 自己纠回来 / 跟着错的算下去」，英文缩写最多放括号里 |
| 论文黑话当动词/名词：**「承重区」「载重性」「方差分解」「解释偏差」「判官提示」** | 「题目够难时才管用」「谁的差异更大：难度解释了 98.8%，改法只占 0.8%」「同一个裁判换个问法」 |
| 先抛结论再解释，句子长、多重定语 | **先讲"怎么做的"（像讲一个小实验），再给数字**；一句一个意思，短句 |
| 「continuation-based causal testing」式方法论名 | 「扰动一步 → 截断 → 让它接着写 → 看答案会不会跑偏」 |

- 标题也不要用论文黑话：`CoT 从装饰到承重：越难越关键` → 改 `题目越难，CoT 越决定答案`（更直白、同样 20 字内）。
- 数字一个不能少（严谨度不减），但**包装成口语**：「误差传播涨 16 倍」→「被带跑偏的比例涨了 16 倍」。
- 自检：写完通读一遍，问自己「不做研究的普通读者能不能看懂每一句」。

## 4. 组装：绕过 render_note，手工构造 payload
`paper_to_xhs.render_note` 是 RecSys 调性（结果段硬编码 MSCA、结尾固定「推荐系统与多模态」话术），
**非 RecSys 论文必须绕过**：自己写 `PublicationPackage`，再走同一个 stage/publish 通道。

```python
from pathlib import Path
from redbook.automation.publishing import PublicationPackage, XhsPublisher
ROOT = Path('.')
pkg = PublicationPackage(
    paper_id='<id>', platform='xhs',
    canonical_url='https://arxiv.org/abs/<id>',
    title=TITLE, body_markdown=BODY,
    image_paths=[str(p) for p in image_paths],          # 1-9 张
    links={'paper': ..., 'pdf': ..., 'code': ''},
    metadata={
        'topics': ['论文分享','人工智能','大模型','智能体', <领域词>],   # 必须是平台真实话题
        'pdf_path': str(ROOT/'data/parsed/<id>/<id>_origin.pdf'),       # 非空 → 自动走带 PDF CDP 全链路
        'author': '', 'source_attribution': '图表摘自论文，仅作学术解读。',
    },
    review_status='pending',
)
print(XhsPublisher(root=ROOT).stage(pkg))        # → staged_id
```
同时写两份记录（供复用与检索）：
- `data/parsed/<id>/<id>_figures.json`（figures: image_file/figure_type/description）
- `data/summaries/<id>_summary.json`（11 维摘要；本路径不渲染它，但要留档）

**落盘位置铁律**：`XhsPublisher(root=ROOT).stage()` 写到 **`ROOT/publish_queue/<前32位>/xhs.json`**，
**不是** `data/publish_queue/`（那是历史归档）。`XhsPublisher.__init__` 只接受 `root=`，没有 `data_root`/`draft_dir`。

## 5. 发布 + 核验
```bash
# 登录态探针（比 whoami 稳）：返回值是 CompletedProcess，必须解析 .stdout
rt.run('xiaohongshu','drafts','-f','json','--window','background','--site-session','ephemeral')
# 发布（pdf_path 非空 → CDP 全链路：图→标题→正文→话题→PDF→存草稿）
XhsPublisher(root=Path('.')).publish('<staged_id>')   # 回执含 draft_id/image_count/pdf_name
```
- 走 PowerShell 后台跑 + `Out-File -Encoding utf8` 落日志（一次约 60-70s）。
- 核验：`drafts` 列表条数 +1、按 `draft_id` 命中、`images == 上传图数`。
- PowerShell 控制台里中文标题乱码**只是显示问题**，实际写入正确；要确认就写文件再用 Python 解码。
- ⚠️⚠️ **中文乱码的真正根因（2026-10-12 定位）**：OpenCLI runtime 本身按 `utf-8, errors='replace'` 解码**没问题**；
  乱码出在 **PowerShell 5.1 捕获原生命令 stdout 时按系统 ANSI 代码页（简体中文=GBK）解读**——Python 侧把 stdout
  `reconfigure(encoding='utf-8')` 也救不了，而且一旦被 `errors='replace'` 处理过就**不可逆**（再 `encode('gbk')` 只会得到 `锟斤拷`）。
  → **铁律：让 Python 直接把结果写成 UTF-8 文件，再用 Read 工具看文件**；控制台只打印 ASCII 的 id/计数。
  → 需要"人看的中文输出"时，绝不要靠控制台回传（详见 §5.2 的 `verify_xhs_drafts.py` 做法）。
- ⚠️ **不要用 Python 的 `f"...{...}"` 写进 PowerShell `-c "..."`**：内层双引号会被 PowerShell 吞掉 → `SyntaxError: unterminated string literal`。
  复杂校验就**写一个 .py 脚本文件**再执行（推荐做法），或只用单引号字符串。

### 5.1 改稿/换稿：替换已有草稿（用户改过多次需求）
用户可能看完草稿后要求「换一篇论文」「文风太生硬重写」「要架构图」。流程固定：
1. **先重新 stage 出新 hash**（内容变了必须新 hash，见坑 7），**不要**直接改旧包。
2. **先 publish 新稿，成功后再删旧稿**——顺序不能反，否则新稿失败 + 旧稿已删 = 草稿箱两头空。
3. 删除旧稿：`OpenCliXiaohongshuDelivery()._delete('<s:uuid>')`
   - ⚠️ **`_delete` 静默成功**：返回 `None`、不报错也不回执 → **不能凭返回值判断**，必须重新 `drafts` 列表按 `draft_id` 子串核验「旧稿 hits=0 且新稿 hits=1、总数 -1」。实测删除确实生效（12→11）。
4. 换稿完成后**主动问用户旧稿是否要删**（若用户只说「换一篇」但没说删，先确认再动）。
5. 本地 stage 包（`publish_queue/<hash>/`）**永不删**——这是「删错了还能一键重发」的兜底。

### 5.3 改文案时的两个坑（2026-10-14 踩过）
用户常要求"这段话重写清楚点"/"删掉某段"。批量改 `build_xhs_draft_*.py` 里的 BODY 时：

1. ⚠️ **不要在 shell heredoc 里用 `\\n` 打补丁**：`python - <<'PY'` 里的 `\\n` 经多层传递会掉一层反斜杠，
   写回文件后变成**真实换行**，把 Python 源码里的字符串字面量截断 → `SyntaxError: unterminated string literal`。
   → 正确做法之一：正文用**三引号 + 真实换行**写成 `BODY = """..."""`，完全没有 `\n` 转义，最不容易出错；
   → 正确做法之二：用 Write 工具写一个一次性的 `_fix_body.py`（内容含 `\\n` 或三引号），再执行它去改目标脚本。
2. **正文压缩只能迭代逼近**：1000 字上限很硬，参考材料（用户常附一份很详细的笔记）通常 1400+ 字。
   节奏是「写 → DRY_RUN 看字数 → 按段落砍 → 再跑」，实测本例 1427→1231→1166→1023→**999**（4 轮）。
   砍的顺序：先删与开头重复的数字 > 合并两节 > 压机制描述为"一句一信息" > 最后才动"一句话/局限"（用户明确要保留的）。
3. **别用 Write 新建日志/产物前，先确认文件不存在**（曾把当天已有的 `memory/YYYY-MM-DD.md` 覆盖掉）。

### 5.2 清理草稿箱里的历史重复稿
用户偶尔会要求清理箱内早期重复试验稿。现成工具：`verify_xhs_drafts.py`
```bash
python verify_xhs_drafts.py --dump                                # 导出全量到 xhs_drafts_dump.{json,txt}
python verify_xhs_drafts.py --delete "s:uid1" "s:uid2" --yes      # 删除 + 自动复核
```
- **先列清单再删**（把 dump 表给用户看），不要凭记忆删。
- 反复试验的典型三层痕迹：① 标题含「测试」或图数=1 的测试稿 → 删；② 图数=1 的不完整稿 → 删；③ 同标题前缀 + 同图数的成对稿 → 保留较新（rank 小）的一条。
- ⚠️ **`draft-open <id>` 不返回正文**（`content` 为空），与 `drafts` 摘要等价 → **无法逐字比对两条同标题稿**，只能按「标题前缀 + 图数 + rank」推定，并在回报里**写明这个假设**，让用户去创作者后台确认保留的是哪一条。
- 批量删除**逐条复核**：可能某条遇 `Navigation rejected` 静默失败（`_delete` 无回执）→ 原样重试一次即成功。
- `opencli xiaohongshu` 可用子命令（v1.8.6）：`drafts / draft-open / draft-delete / draft-clear / publish / delete-note / creator-note-detail / creator-notes / creator-stats / note / whoami` 等，`--help` 一览。

## 坑清单（都踩过）
1. `render_note` 不适合非 RecSys 论文（硬编码 MSCA 结果段 + 推荐系统结尾）→ 手工 payload。
2. stage 路径在 `ROOT/publish_queue/`，不在 `data/publish_queue/`。
3. 探针/列表返回 `CompletedProcess`，要读 `.stdout` 再 `json.loads`。
4. arXiv 周末不更新，周一早间索引滞后 → 「最新」通常是上周五批次，别误判。
5. 图片 ≤9 张；标题 20 字上限由 `validate()` 强卡。
6. 话题必须**平台真实存在的实体**（论文分享/人工智能/大模型/智能体/AI编程/AI绘画 这些稳），
   自造冷门标签会导致绑定失败。
7. 发布不幂等：同一 staged_id 重复 publish 会多建草稿；改内容要重新 stage（新 hash）。
8. 中文路径/编码：图与 PDF 路径建议全 ASCII；控制台乱码不代表写入错误。
9. **`{'ok': False, 'error': 'Navigation rejected.'}`（exitCode 1）= 瞬时窗口/导航状态问题（典型触发：用户自己正开着创作中心发布页，或上次会话残留标签页）。
   → **先原样重试一次**（实测第二次 46s 成功）。仍失败才让用户关掉创作中心那页再试。
   注意：失败时**没有产生草稿**，重试不会造成重复（真正会造成重复的是成功后再 publish 同一 staged_id）。
10. **正文是纯文本**：不要用 Markdown 语法（`**加粗**`、`##`）——小红书编辑器会原样显示星号/井号。
11. **`drafts` 探针偶发返回空 stdout（rc=0）**：`json.loads` 会报 `Expecting value: line 1 column 1`。
    → 这是瞬时问题，直接重试；脚本里建议先判 `if not r.stdout: 重试/报错`，不要当成登录失效。
12. **草稿列表的 JSON 若被提前按 GBK 解码，标题会变成乱码且不可逆**（`encode('gbk')` 补救只会得到 `锟斤拷`）。
    → 核验时**只用 ASCII 的 id 做子串匹配**，不要依赖返回里的中文标题；中文一律以本地 stage 包 `xhs.json` 为准。

## 交付话术
回报：论文 id/标题/日期 → 草稿 id + 图数 + PDF 名 → 标题字数/正文字数 → 图片清单（哪张是封面/哪张是 before-after）→ 提醒用户在创作者后台目测 PDF 卡片（列表 API 不暴露）。
