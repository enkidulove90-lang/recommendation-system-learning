# 小红书 RecMem 草稿修复会话审计

生成时间：2026-11-19（Asia/Shanghai）  
范围：本会话中与以下 5 条用户消息直接相关的技能、工具、PowerShell / Python / OpenCLI 命令及结果。  
草稿：`s:93a910ec-4bf2-4011-8a7a-e410146bdbbe`（仅草稿，未公开发布）

> 说明：这是依据本会话可见执行记录整理的可读审计，而不是桌面应用的原始逐字 JSONL 导出。未在可见记录中出现的参数、Cookie、令牌、浏览器内容均未补写或推测。命令内不含密钥。

## 用户消息原文

1. `创造中西是可以提供真是话题实体的的`
2. `打开了不需要发布笔记按照已有skill上传草稿就行`
3. `保留了`
4. `我要保存草稿，之前上传草稿功能一直正常，但现在出现了很多问题。请按照已有的发布链路通过浏览器自动操作来完成草稿保存，先定位出错的具体环节（如页面元素加载、按钮定位或接口响应），再修复并验证草稿能成功保存，确保整个流程恢复正常。`
5. `你为什么不按照我的已有skill走呢 现在之上传了这一个#算法没有具体内容`

## 使用的技能

| 技能 | 读取位置 | 用途 | 结论 |
|---|---|---|---|
| `xhs-paper-draft` | `.agents/skills/xhs-paper-draft/SKILL.md` | 强制的论文→小红书草稿流程 | 使用唯一入口 `python -m redbook.cli note <slug> --validate/--stage/--publish`；`--publish` 在该仓库语义中只写草稿箱。 |
| 仓库规则 | `AGENTS.md`、`redbook/docs/xhs-content-spec.md`、`config/xhs_content_rules.yaml` | 话题、PDF、正文、图片与回读硬门槛 | 正文纯文本、≤1000 字、真实话题实体、PDF 同草稿附件、只存草稿。 |
| `web-access` | `C:\Users\lkshpc\.agents\skills\web-access\SKILL.md` | 核验 OpenCLI 官方发布版本 | 确认扩展 1.0.27 是官方修复版本。 |
| `systematic-debugging` | 本机已安装技能 | 定位“只有 #算法、正文为空”的根因 | 发现正文、话题、PDF 曾被拆分到不同草稿记录；不能视为成功。 |
| `test-driven-development`、`verification-before-completion` | 本机已安装技能 | 为投递修复补回归并保存后回读 | `redbook/tests/test_xiaohongshu_delivery.py` 最终为 13 passed；草稿保存后再次独立回读。 |

## 调用的工具 / MCP 记录

| 工具或接口 | 调用目的 | 结果 |
|---|---|---|
| Codex shell 工具（PowerShell） | 读取仓库规则、执行 CLI、测试、检查工作流状态 | 成功；下方列出命令。 |
| OpenCLI Browser Bridge（通过 `opencli` CLI，而非直接 MCP） | 打开 Creator Center、上传图片/PDF、写入正文、绑定真实话题、保存草稿、读取 IndexedDB | 最终成功。 |
| OpenCLI `xiaohongshu drafts` 接口 | 保存前后确认新增草稿、最后只读列出目标草稿 | OpenCLI 2.x 返回 `{ok,data}` 包装，已在投递器与清点脚本兼容。 |
| OpenCLI 浏览器 `eval` / IndexedDB | 检查已保存草稿的 `draftStore.desc`、`hashTag`、`fileRelate` | `body_ok=true`、`topics_ok=true`、`pdf_ok=true`。 |
| Web 搜索 / 官方 GitHub Release 页面 | 核验更新包来源与发行说明 | 官方 v2.0.3 Release 对应扩展 1.0.27，包含 native keyboard input / browser window recovery 修复说明。 |

本范围内没有调用 `mcp__cua_repl`、没有调用平台公开发布接口，也没有调用删除历史草稿的命令。

## PowerShell / Python / OpenCLI 命令记录

以下按工作流阶段整理。所有命令在工作树 `D:\recommendation-system-learning\.worktrees\sab-anc-design`（分支 `experiments`）或为其服务的浏览器环境中执行。

### 1. 环境与扩展诊断

```powershell
node C:\Users\lkshpc\.agents\skills\web-access\scripts\check-deps.mjs
opencli doctor
```

结果：Chrome 调试端口和代理可用；更新前扩展为 1.0.25 且过期，更新后 `opencli doctor` 返回 `extensionVersion: 1.0.27`、`extensionOutdated: false`、`connectivity.ok: true`。

```powershell
opencli browser open 'https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image' --window foreground --session xhs-diagnose
opencli browser type 103 '可见性诊断文本' --session xhs-diagnose
```

结果：旧链路报错 `Native input requires a visible browser page; input was not dispatched.`。这证明问题在原生键盘输入路径，不是文章内容为空或登录失效。

### 2. 规范、素材与草稿包校验

```powershell
Get-Content -Raw '.agents\skills\xhs-paper-draft\SKILL.md'
Get-Content -Raw 'redbook\docs\xhs-content-spec.md'
Get-Content -Raw 'config\xhs_content_rules.yaml'
python -m redbook.cli note 2611.17921 --validate
python -m redbook.cli note 2611.17921 --stage
```

结果：标题、756 字正文、5 张图片、PDF 路径、逐张目检记录和内容闸门均通过。暂存包最终为：

```text
data/publish_queue/0174757fe0efd78a1db40a8b4309eec3/xhs.json
staged_id=0174757fe0efd78a1db40a8b4309eec3df7ec86cfaaa8ec4ed4b84296f2a0757
```

### 3. 失败定位（未保存时即终止）

```powershell
python -m redbook.cli note 2611.17921 --publish
```

该仓库的 `--publish` 命名是历史兼容；实际动作是“保存草稿”，不是公开发布。早期重试的关键报错如下：

```text
Native input requires a visible browser page; input was not dispatched.
Creator Center did not offer exact topic chip; available=[...]
topic chip click failed: {'ok': False}
```

浏览器页内检查（只读或不保存操作）的 OpenCLI 命令包括：

```powershell
opencli browser open 'https://creator.xiaohongshu.com/publish/publish?from=menu_left&target=image' --window foreground --session redbook-topic-probe
opencli browser wait time 3 --session redbook-topic-probe
opencli browser eval "(()=>{const b=document.querySelector('button#topicBtn');if(!b||b.offsetParent===null)return JSON.stringify({ok:false});b.click();return JSON.stringify({ok:true});})()" --session redbook-topic-probe
opencli browser eval "(()=>{var out=[];for(var t of document.querySelectorAll('.tag-group .tag, .tag-group-popover-container .tag')){if(t.offsetParent===null)continue;var tx=(t.innerText||'').replace(/\s+/g,' ').trim();if(tx&&tx!=='更多')out.push(tx);}return JSON.stringify(out);})()" --session redbook-topic-probe
opencli browser close --session redbook-topic-probe
```

定位结论：Creator Center 给出的展示文本带 `#` 前缀，点选后面板会收起；旧实现同时错误依赖原生输入，并且没有在每次选完实体后重新读取/打开推荐面板。

### 4. 修复、测试与正式保存

修复位置：

- `redbook/infrastructure/xiaohongshu_delivery.py`
  - OpenCLI 2.x 的 `--session` 参数位置和 `{ok,data}` 响应解包；
  - 仅点击 Creator Center 的真实话题芯片，取消正文原生 `#topic` 输入；
  - 去除芯片文本 `#` 前缀；先读面板，只有为空时再展开；每个实体点选后重新读取；
  - 保存后以草稿 ID 从 IndexedDB 回读正文、话题实体与 PDF 元数据，失败即删除本次新建残缺稿。
- `redbook/notes/2611.17921.yaml`
  - 将候选标签收敛为当前页面可提供的实体：`论文分享`、`推荐系统`、`人工智能`。
- `redbook/scripts/xhs_drafts.py`
  - 兼容 OpenCLI 2.x 的 `{ok,data}` 草稿列表包装。

```powershell
python -m pytest redbook/tests/test_xiaohongshu_delivery.py -q
python -m redbook.cli note 2611.17921 --publish
```

结果：测试输出 `13 passed`；草稿保存成功：

```json
{
  "ok": true,
  "method": "opencli-cdp",
  "draft_id": "s:93a910ec-4bf2-4011-8a7a-e410146bdbbe",
  "topics": ["论文分享", "推荐系统", "人工智能"],
  "image_count": 5,
  "pdf_name": "2611.17921_RecMem.pdf"
}
```

### 5. 保存后独立回读与本地状态

```powershell
python -c "import json; from pathlib import Path; from redbook.infrastructure.xiaohongshu_delivery import DraftPayload, OpenCliXiaohongshuDelivery; d=json.loads(Path('data/publish_queue/0174757fe0efd78a1db40a8b4309eec3/xhs.json').read_text(encoding='utf-8')); p=DraftPayload(title=d['title'], body=d['body_markdown'], image_paths=tuple(Path(x) for x in d['image_paths']), topics=tuple(d['metadata']['topics']), pdf_path=Path(d['metadata']['pdf_path'])); print(json.dumps(OpenCliXiaohongshuDelivery()._verify_saved_draft('s:93a910ec-4bf2-4011-8a7a-e410146bdbbe', p), ensure_ascii=True))"
python -c "import json; from redbook.scripts.xhs_drafts import fetch_drafts; d=next(x for x in fetch_drafts() if x.get('id')=='s:93a910ec-4bf2-4011-8a7a-e410146bdbbe'); print(json.dumps({k:d.get(k) for k in ('id','title','images','rank')}, ensure_ascii=True))"
```

结果：

```json
{"ok": true, "body_ok": true, "topics_ok": true, "pdf_ok": true, "error": ""}
{"id": "s:93a910ec-4bf2-4011-8a7a-e410146bdbbe", "images": 5, "rank": 16}
```

本地交付记录已写入：

```text
data/workflow_state/2611.17921/checkpoint.json
```

其中状态为 `draft_saved`，并记录草稿 ID、3 个话题、5 张图片、PDF 文件名及 `pdf_attachment_verified: true`。

## 最终结果

本轮没有公开发布。新的草稿记录包含完整正文、5 张高清论文图、3 个平台真实话题实体与同一份本地 PDF 附件；旧的拆分草稿未被删除，以保留人工审计空间。
