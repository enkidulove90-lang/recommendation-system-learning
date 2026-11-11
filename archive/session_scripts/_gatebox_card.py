# -*- coding: utf-8 -*-
"""Render a phone-readable numbers card for the GateBoxGCN post (self-made, not a paper figure)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440
BG = (250, 246, 240)
INK = (32, 32, 36)
MUTED = (110, 108, 104)
ACCENT = (176, 62, 50)
GREEN = (36, 118, 88)

FONT = "C:/Windows/Fonts/msyh.ttc"
f_title = ImageFont.truetype(FONT, 60)
f_sub = ImageFont.truetype(FONT, 34)
f_head = ImageFont.truetype(FONT, 40)
f_cell = ImageFont.truetype(FONT, 36)
f_small = ImageFont.truetype(FONT, 28)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.text((70, 80), "换成负偏移之后", font=f_title, fill=INK)
d.text((70, 165), "四个数据集、R@20 / N@20 的提升", font=f_sub, fill=MUTED)
d.line((70, 230, W - 70, 230), fill=(214, 208, 198), width=3)

rows = [
    ("Yelp", "0.0789", "0.0500", "+5.76%", "+6.16%"),
    ("Amazon", "0.0733", "0.0457", "+6.39%", "+8.04%"),
    ("MovieLens", "0.1142", "0.1235", "+6.63%", "+13.20%"),
    ("KuaiRec", "0.1190", "0.3671", "+33.11%", "+35.56%"),
]
y = 290
d.text((70, y), "数据集", font=f_head, fill=MUTED)
d.text((330, y), "R@20", font=f_head, fill=MUTED)
d.text((520, y), "N@20", font=f_head, fill=MUTED)
d.text((700, y), "R 提升", font=f_head, fill=MUTED)
d.text((880, y), "N 提升", font=f_head, fill=MUTED)
y += 66
d.line((70, y - 12, W - 70, y - 12), fill=(214, 208, 198), width=2)
for name, r, n, gdr, gdn in rows:
    d.text((70, y), name, font=f_cell, fill=INK)
    d.text((330, y), r, font=f_cell, fill=INK)
    d.text((520, y), n, font=f_cell, fill=INK)
    d.text((700, y), gdr, font=f_cell, fill=GREEN)
    d.text((880, y), gdn, font=f_cell, fill=GREEN)
    y += 84

y += 30
d.line((70, y, W - 70, y), fill=(214, 208, 198), width=2)
y += 44
d.text((70, y), "负偏移真的被用起来了", font=f_head, fill=INK)
y += 66
d.text((70, y), "• Yelp 19.86% 的偏移维度 < 0", font=f_cell, fill=INK)
y += 60
d.text((70, y), "• Amazon 12.45% 的偏移维度 < 0", font=f_cell, fill=INK)
y += 90
d.text((70, y), "消融（Yelp R@20）", font=f_head, fill=INK)
y += 66
ab = [("完整模型", "0.0789"), ("去掉软门控", "0.0774"), ("强制正偏移", "0.0769"), ("体积打分", "0.0744")]
for name, v in ab:
    d.text((70, y), name, font=f_cell, fill=INK)
    d.text((560, y), v, font=f_cell, fill=ACCENT if name == "完整模型" else INK)
    y += 58

d.text((70, H - 90), "数据来源：论文 Table 1 / Table 2 / Table 3 ｜ 自制图表，非论文原图", font=f_small, fill=MUTED)

out = "data/parsed/gateboxgcn/images/card_numbers.png"
img.save(out)
print("saved", out)
