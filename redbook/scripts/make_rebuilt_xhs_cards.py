"""Build readable 2100x2996 Xiaohongshu cards from paper figures.

Each image is a re-laid-out information card: a short Chinese takeaway,
one enlarged source figure, and a source footer.  It deliberately avoids
uploading raw PDF page screenshots.
"""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "redbook" / "assets" / "rebuilt_cards"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 2100, 2996
FONT = "C:/Windows/Fonts/msyh.ttc"


def font(size, bold=False):
    # Microsoft YaHei supports both Chinese and Latin text.
    return ImageFont.truetype(FONT, size, index=0)


def crop_pdf(pdf, page_no, box):
    doc = fitz.open(pdf)
    page = doc[page_no]
    rect = page.rect
    clip = fitz.Rect(rect.width * box[0], rect.height * box[1],
                     rect.width * box[2], rect.height * box[3])
    pix = page.get_pixmap(matrix=fitz.Matrix(2.4, 2.4), clip=clip, alpha=False)
    doc.close()
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def fit_image(im, max_w, max_h):
    im = im.convert("RGB")
    # Most parser exports carry a large white margin.  Remove it before
    # scaling so that the actual architecture/chart remains readable on phone.
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L")
    diff = diff.point(lambda p: 255 if p > 18 else 0)
    bbox = diff.getbbox()
    if bbox:
        pad = 12
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
        im = im.crop(bbox)
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return im


def multiline(draw, xy, text, fnt, fill, width, spacing=20):
    x, y = xy
    lines, current = [], ""
    for ch in text:
        trial = current + ch
        if draw.textlength(trial, font=fnt) > width and current:
            lines.append(current)
            current = ch
        else:
            current = trial
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def card(slug, idx, lab, title, subtitle, takeaway, figure, caption, palette):
    bg, ink, accent, soft = palette
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((96, 95, 650, 185), 45, fill=accent)
    d.text((132, 111), lab, font=font(38), fill=(255, 255, 255))
    d.text((W - 360, 112), f"{idx}/5", font=font(36), fill=soft)
    y = 290
    y = multiline(d, (110, y), title, font(105), ink, W - 220, 22)
    y += 30
    y = multiline(d, (110, y), subtitle, font(44), soft, W - 220, 14)
    y += 72
    d.rounded_rectangle((92, y, W - 92, y + 330), 50, fill=(250, 250, 250) if bg[0] > 80 else (36, 44, 58))
    d.text((135, y + 48), "一句话读图", font=font(40), fill=accent)
    multiline(d, (135, y + 118), takeaway, font(52), ink, W - 270, 16)
    y += 440
    # Wide architecture diagrams and charts should not sit in an oversized
    # portrait-shaped white box.  Size the figure panel to its real aspect
    # ratio and use the remaining space for a readable caption panel.
    raw = fit_image(figure, 3000, 3000)
    figure_h = min(1320, max(820, int((W - 284) * raw.height / raw.width + 150)))
    frame = (92, y, W - 92, y + figure_h)
    d.rounded_rectangle(frame, 48, fill=(255, 255, 255), outline=accent, width=8)
    im = fit_image(figure, frame[2] - frame[0] - 100, frame[3] - frame[1] - 100)
    x = (W - im.width) // 2
    iy = frame[1] + ((frame[3] - frame[1]) - im.height) // 2
    canvas.paste(im, (x, iy))
    cap_top = frame[3] + 65
    cap_bottom = H - 225
    d.rounded_rectangle((92, cap_top, W - 92, cap_bottom), 42,
                        fill=(255, 255, 255) if bg[0] > 80 else (36, 44, 58))
    d.text((135, cap_top + 42), "图解重点", font=font(42), fill=accent)
    multiline(d, (135, cap_top + 110), caption, font(48), ink, W - 270, 16)
    d.text((110, H - 115), "论文解析图 · 仅作学术信息分享", font=font(32), fill=soft)
    canvas.save(OUT / f"{slug}-{idx:02d}.jpg", quality=94, subsampling=0)


LIGHT = ((250, 247, 242), (24, 30, 42), (225, 74, 75), (93, 102, 118))
BLUE = ((244, 249, 255), (20, 36, 64), (45, 111, 211), (82, 110, 149))
PURPLE = ((250, 247, 255), (44, 31, 70), (121, 80, 195), (110, 94, 138))
GREEN = ((246, 252, 247), (24, 53, 41), (35, 151, 98), (82, 119, 99))


def build_pdf_series(slug, pdf_rel, lab, title, subtitle, items, palette):
    pdf = ROOT / pdf_rel
    for idx, (page, box, takeaway, caption) in enumerate(items, 1):
        card(slug, idx, lab, title, subtitle, takeaway, crop_pdf(pdf, page, box), caption, palette)


build_pdf_series(
    "openai-gpt-red", "data/parsed/gpt-red/gpt-red.pdf", "OPENAI · 2026.07", "GPT-Red：让攻击者与防御者一起进化", "自动化红队 × 自博弈 · 论文图解", [
        (0, (.49, .25, .96, .54), "攻击模型越强，越能持续挖出提示注入等真实失败模式。", "图 1｜随着测试计算量增加，GPT-Red 的攻击成功率持续提升。"),
        (2, (.05, .14, .95, .86), "把“可疑指令”放进真实工具链，安全问题才会暴露出来。", "图 2｜论文中的攻击样例：伪装推理文本诱导模型偏离任务。"),
        (4, (.05, .16, .95, .86), "防御者不是只做拒答，而是要在任务完成与安全之间取得平衡。", "图 3｜攻击者与防御者在工具调用环境中持续对抗。"),
        (7, (.05, .15, .95, .85), "评测覆盖真实的浏览、文件与工具场景，而不只是一组静态提示词。", "图 8｜论文构造的安全强化学习环境。"),
        (11, (.05, .12, .95, .88), "直接提示注入仍然有效，系统要在长期迭代中保持稳健。", "图 13｜不同训练方式在直接提示注入上的鲁棒性比较。"),
    ], LIGHT)

build_pdf_series(
    "meta-ra-rft", "data/parsed/ra-rft/ra-rft.pdf", "META AI · 2026.07", "RA-RFT：把“类比”变成可训练的推理能力", "检索增强 × 强化学习 · 论文图解", [
        (1, (.05, .12, .95, .84), "先找到相似题，再迁移解题结构：类比推理被显式写进训练目标。", "图 1｜RA-RFT 的动机：从直接解题走向检索支持的类比推理。"),
        (2, (.05, .10, .95, .88), "检索器提供候选案例，策略模型学习何时参考、如何迁移。", "图 2｜RA-RFT 框架：检索、推理与奖励信号共同闭环。"),
        (6, (.05, .12, .95, .88), "训练曲线显示：更好的类比样例能把奖励信号转化为更稳定的推理。", "图 3｜训练过程中的性能变化。"),
        (7, (.05, .12, .95, .88), "同一道题，关键不是复述案例，而是抽取可迁移的解题关系。", "图 4｜带与不带类比检索的回答对比。"),
        (13, (.05, .10, .95, .90), "案例分析能看到模型把检索到的结构映射回当前问题。", "图 5｜RA-RFT 的类比推理案例。"),
    ], PURPLE)

build_pdf_series(
    "tencent-hils", "data/parsed/2607.02980/2607.02980.pdf", "TENCENT HUNYUAN · 2026.07", "HiLS Attention：长上下文不必全量注意力", "分层稀疏注意力 · 论文图解", [
        (0, (.05, .19, .95, .86), "长序列里，模型先筛出真正相关的块，再投入精细计算。", "图 1｜HiLS 在长上下文任务上的结果概览。"),
        (1, (.05, .14, .95, .89), "检索关键事实时，稀疏结构要做到“找得到”，而不是只省计算。", "图 2｜上下文检索实验展示不同注意力策略的差异。"),
        (3, (.05, .10, .95, .89), "层级路由把粗筛与细读拆开：先定位，再聚焦。", "图 3｜HiLS 的层级稀疏注意力架构。"),
        (13, (.05, .10, .95, .89), "同看长文本，比较的不只是困惑度，还有真实检索能力。", "图 5｜语言建模与 RULER 长上下文评测。"),
        (15, (.05, .10, .95, .89), "效率指标必须和效果一起看，才知道长上下文是否可落地。", "图 6｜不同序列长度下的延迟与效率比较。"),
    ], BLUE)


mme_dir = next((ROOT / "data" / "parsed").glob("2607.07108*")) / "images"
mme_images = sorted(mme_dir.glob("*"))
want = ["98edc", "e02c", "6edeb", "2c787", "fb670"]
selected = [next(p for p in mme_images if p.name.startswith(prefix)) for prefix in want]
mme_text = [
    ("把用户、商品和图片一起写入记忆，推荐智能体才不止会读文本。", "图 1｜传统推荐 Agent 与 MMEACR 的多模态协作对比。"),
    ("双轨记忆分别保留用户偏好与商品线索，再由协作机制统一决策。", "图 2｜MMEACR 的总体架构。"),
    ("记忆不是静态日志：每次交互都会补充、修正或淘汰信息。", "图 3｜用户与物品记忆随交互演化的案例。"),
    ("把自然语言意图转换为结构化查询，减少推荐链路里的信息损失。", "图 6｜结构化查询模板。"),
    ("提示词负责约束协作角色，让不同智能体围绕同一推荐目标工作。", "图 8｜论文使用的协作提示模板。"),
]
for idx, (path, (takeaway, caption)) in enumerate(zip(selected, mme_text), 1):
    card("mmeacr", idx, "RECOMMENDER SYSTEM · 2026.07", "MMEACR：多模态记忆推荐智能体", "用户记忆 × 商品记忆 × 协作决策", takeaway, Image.open(path), caption, GREEN)

print(f"wrote {len(list(OUT.glob('*.jpg')))} cards to {OUT}")
