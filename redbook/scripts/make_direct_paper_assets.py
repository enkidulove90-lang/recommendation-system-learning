"""Prepare direct paper figures plus one final knowledge-map/details image.

The first four images in every note are untouched paper figure crops.  Only
the fifth image is a compact reader aid with the knowledge map and links.
"""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "redbook" / "assets" / "direct_paper_assets"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "C:/Windows/Fonts/msyh.ttc"


def f(size):
    return ImageFont.truetype(FONT, size, index=0)


def render_crop(pdf_rel, page_no, box):
    doc = fitz.open(ROOT / pdf_rel)
    page = doc[page_no]
    r = page.rect
    clip = fitz.Rect(r.width * box[0], r.height * box[1], r.width * box[2], r.height * box[3])
    pix = page.get_pixmap(matrix=fitz.Matrix(3.2, 3.2), clip=clip, alpha=False)
    doc.close()
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def save_raw(im, slug, index):
    # No title bar, caption, frame or re-layout: these are paper figures.
    if im.width > 2800:
        im.thumbnail((2800, 2800), Image.Resampling.LANCZOS)
    im.convert("RGB").save(OUT / f"{slug}-{index:02d}.jpg", quality=96, subsampling=0)


def wrap(d, text, x, y, width, font, fill, line_gap=18):
    line = ""
    for char in text:
        candidate = line + char
        if d.textlength(candidate, font=font) > width and line:
            d.text((x, y), line, font=font, fill=fill)
            y += font.size + line_gap
            line = char
        else:
            line = candidate
    if line:
        d.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def details(slug, title, lab, nodes, pdf, code, color):
    W, H = 1242, 1660
    bg, ink = (255, 255, 255), (25, 33, 46)
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 22), fill=color)
    d.text((72, 75), "论文知识图谱", font=f(38), fill=color)
    y = wrap(d, title, 72, 135, W - 144, f(66), ink, 16)
    d.text((72, y + 12), lab, font=f(30), fill=(105, 116, 132))
    cy = 625
    # Compact, deliberately plain knowledge graph: one central claim and four nodes.
    center = (W // 2, cy)
    d.rounded_rectangle((center[0] - 165, center[1] - 58, center[0] + 165, center[1] + 58), 28, fill=color)
    d.text((center[0] - 112, center[1] - 22), "核心方法", font=f(34), fill=(255, 255, 255))
    pos = [(130, 410), (820, 410), (130, 805), (820, 805)]
    for (x, yy), node in zip(pos, nodes):
        tx, ty = x + 145, yy + 64
        d.line((center[0], center[1], tx, ty), fill=(173, 183, 196), width=4)
        d.rounded_rectangle((x, yy, x + 290, yy + 128), 25, outline=color, width=4)
        wrap(d, node, x + 25, yy + 28, 240, f(29), ink, 6)
    d.line((72, 1015, W - 72, 1015), fill=(225, 230, 237), width=3)
    d.text((72, 1060), "论文详情", font=f(42), fill=ink)
    y = 1135
    d.text((72, y), "PDF", font=f(30), fill=color); y += 48
    y = wrap(d, pdf, 72, y, W - 144, f(27), ink, 10) + 30
    d.text((72, y), "代码 / 复现", font=f(30), fill=color); y += 48
    wrap(d, code, 72, y, W - 144, f(27), ink, 10)
    d.text((72, H - 65), "图 1–4 为论文原始解析图；本页为阅读索引。", font=f(23), fill=(120, 130, 145))
    im.save(OUT / f"{slug}-05.jpg", quality=95, subsampling=0)


def series(slug, pdf, crops, title, lab, nodes, link_pdf, code, color):
    for i, (page, box) in enumerate(crops, 1):
        save_raw(render_crop(pdf, page, box), slug, i)
    details(slug, title, lab, nodes, link_pdf, code, color)


series("openai-gpt-red", "data/parsed/gpt-red/gpt-red.pdf", [
    (0, (.50, .25, .96, .54)), (2, (.06, .06, .94, .60)),
    (4, (.06, .08, .94, .72)), (7, (.06, .08, .94, .75)),
], "GPT-Red：自动化红队自博弈", "OpenAI · 2026-07", ["攻击者生成新攻击", "防御者迭代加固", "真实工具环境", "鲁棒性评测"],
       "https://cdn.openai.com/pdf/gpt-red-automated-red-teaming-via-self-play-at-scale.pdf", "暂无官方代码 · https://github.com/openai", (225, 74, 75))

series("meta-ra-rft", "data/parsed/ra-rft/ra-rft.pdf", [
    (1, (.05, .08, .95, .70)), (2, (.05, .08, .95, .76)),
    (6, (.05, .08, .95, .82)), (7, (.05, .08, .95, .82)),
], "RA-RFT：检索增强的类比推理", "Meta AI · 2026-07", ["相似案例检索", "关系结构迁移", "强化学习奖励", "复杂推理评测"],
       "https://arxiv.org/pdf/2606.13680", "暂无官方代码 · https://github.com/facebookresearch", (121, 80, 195))

series("tencent-hils", "data/parsed/2607.02980/2607.02980.pdf", [
    (0, (.05, .16, .95, .82)), (1, (.05, .08, .95, .82)),
    (3, (.05, .08, .95, .84)), (13, (.05, .08, .95, .84)),
], "HiLS Attention：分层稀疏长上下文", "Tencent Hunyuan · 2026-07", ["粗粒度路由", "相关块精读", "长文检索", "效率与效果"],
       "https://arxiv.org/pdf/2607.02980", "https://github.com/Tencent-Hunyuan/HiLS-Attention", (45, 111, 211))

mme_dir = next((ROOT / "data" / "parsed").glob("2607.07108*")) / "images"
prefixes = ["98edc", "e02c", "6edeb", "2c787"]
for i, prefix in enumerate(prefixes, 1):
    source = next(p for p in mme_dir.glob("*") if p.name.startswith(prefix))
    save_raw(Image.open(source), "mmeacr", i)
details("mmeacr", "MMEACR：多模态记忆推荐智能体", "推荐系统 · 2026-07", ["用户多模态记忆", "商品多模态记忆", "记忆更新与协作", "RRF 推荐排序"],
        "https://arxiv.org/pdf/2607.07108", "暂无官方代码 · RecBole：https://github.com/RUCAIBox/RecBole", (35, 151, 98))

print("direct paper assets created")
