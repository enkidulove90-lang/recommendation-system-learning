# Paper-to-draft operating procedure

## Authority

Run only in `draft_only`. “Publish” means save a Creator draft, never click a
public publish control. A public release requires separate authorization and a
separate release/recovery design.

## 1. Discover and queue

```powershell
python -m redbook.automation.cli --data-root data discover-daily --config redbook/config/daily_draft.yaml
python -m redbook.automation.cli --data-root data run-daily --duration-hours 24
python -m redbook.automation.cli --data-root data run-daily --duration-hours 24 --interval-hours 6
python -m redbook.automation.cli --data-root data run-daily --duration-hours 24 --interval-minutes 90
```

The default cadence is 18 hours. Read `data/discovery/<date>/manifest.json`
and `data/review_queue/`; discovery is not qualification and must not create a
platform draft. If arXiv fails, record the route/error and retry next cycle;
never use a search snippet as paper evidence.

## 2. Qualify a candidate

| Gate | Proof | If it fails |
|---|---|---|
| Status | Official venue/proceedings or trusted preprint plus author/affiliation check | Skip and record reason |
| PDF | Canonical public PDF at `data/papers/<id>.pdf` | Retry canonical source once, then skip |
| Code | Official author/project/venue GitHub | No official code: do not post this round |
| Parse | Local MinerU Markdown/images | Fix credentials/retry; never write from abstract alone |
| Figures | 4–9 distinct readable architecture/result/case/method panels | Replace weak panel; fewer than four: skip; more than nine: rank down to nine |
| Claims | Dataset/setting/result traceable to paper | Rewrite or skip |

Persist links, local paths, figure roles, and each outcome in
`data/workflow_state/<id>/selection_manifest.json`.

## 3. Parse and select figures

Require `MINERU_API_KEY`, parse to `data/parsed/<id>/`, then prefer author
LaTeX assets and fall back to high-DPI PDF/MinerU originals:

```powershell
python -m redbook.cli prepare-figures --paper-id <id> --markdown <mineru.md> --images <image-dir> --pdf data/papers/<id>.pdf --arxiv-id <id> --max-images 9
```

If LaTeX retrieval fails, preserve the error and use only qualified local
fallbacks. Never pad with a cover, unreadable crop, or duplicate figure.

## 4. Compose

Use `xiaohongshu-paper-brief` or an explicitly chosen persona. Include arXiv,
PDF, and official GitHub links; only write evidence-supported claims. Save JSON
with title/body/topics/comment prompt. Use real concrete topics, no hashtag
fallback. Give a readiness test a unique title of at most 20 characters.

## 5. Deliver the draft

```powershell
python -m redbook.cli save-xhs-draft --draft <draft.json> --title <unique-title> --image <figure-1> --image <figure-2> --image <figure-3> --image <figure-4> [--image <figure-5> ... --image <figure-9>] --pdf data/papers/<id>.pdf --output data/workflow_state/<id>/delivery_receipt.json
```

Required ordering in one persistent editor: images/text → native topic query →
click exact suggestion → native Enter → verify `a.tiptap-topic[data-topic]`
by JSON `name` → PDF upload and visible filename → save draft → draft-list
receipt.

If a topic is unresolved, skip; do not use a hashtag. If PDF is not visible,
stop before save. If auto-save occurs, resume only with
`--resume-prepared-editor --resume-draft-id <exact-id>`; never touch another
same-title draft. If ID/image count mismatches, record failure and do not claim
success.

## 6. Accept

Receipt must contain draft ID, at least four images, requested topics, and the
local PDF filename. Update manifest with receipt path,
`topics_entity_bound: true`, `pdf_attachment_verified: true`, and
`status: saved_draft_only`. Creator resetting to a blank composer after save is
normal; rely on pre-save attachment verification and the local receipt.
