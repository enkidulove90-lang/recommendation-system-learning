"""Select the strongest MinerU-extracted figures for the four draft notes."""
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MINERU = ROOT / "data" / "parsed" / "mineru_july_2026"
PREVIOUS = ROOT / "redbook" / "assets" / "direct_paper_assets"
OUT = ROOT / "redbook" / "assets" / "mineru_selected_assets"
OUT.mkdir(parents=True, exist_ok=True)


def copy(source: Path, slug: str, index: int) -> None:
    shutil.copy2(source, OUT / f"{slug}-{index:02d}.jpg")


# GPT-Red's OpenAI PDF URL is rejected by MinerU's regional fetcher.  Keep the
# high-resolution source-PDF figure crops rather than degrade to a low-res image.
for i in range(1, 6):
    copy(PREVIOUS / f"openai-gpt-red-{i:02d}.jpg", "openai-gpt-red", i)

# Four direct, high-resolution MinerU figures, followed by the reading index.
for i, filename in enumerate([
    "eaf97b8cf91fe9d06143cb26fac89365176df58c83ebad25e0b51aae8c7c0f96.jpg",  # Fig. 1
    "cce40cb5ecb3f26c5d8754fce73a15b9213ea64df2e3a72eb7f2c2af8ddfffbb.jpg",  # Fig. 2
    "b12109ebd920e182dfcec2af496448aa937f047da48c698b7328179a5f9c0eba.jpg",  # Fig. 5 case
    "9f58b31d8b4739cbe3785095b301addcb6ba92e502b904f7581dbfb68815c2f4.jpg",  # prompt
], 1):
    copy(MINERU / "meta-ra-rft" / "images" / filename, "meta-ra-rft", i)
copy(PREVIOUS / "meta-ra-rft-05.jpg", "meta-ra-rft", 5)

# HiLS has two vector diagrams extracted by MinerU; pair them with two
# high-resolution source-PDF result crops to retain architecture and evidence.
copy(MINERU / "tencent-hils" / "images" / "c26755e653b5e823ef06c8b00781efdf9640a8cf2afa80a86d3201bcbafbe400.jpg", "tencent-hils", 1)
copy(MINERU / "tencent-hils" / "images" / "884a9ebc02bcf28c56b6b7e989a32b78b456465b07430ad082c98ff26e229aa3.jpg", "tencent-hils", 2)
copy(PREVIOUS / "tencent-hils-01.jpg", "tencent-hils", 3)
copy(PREVIOUS / "tencent-hils-04.jpg", "tencent-hils", 4)
copy(PREVIOUS / "tencent-hils-05.jpg", "tencent-hils", 5)

for i, filename in enumerate([
    "98edc660de228c64ca9f1fa89d330eb2d5da132f1ae5e3f3e3c4828baaf36ad2.jpg",  # Fig. 1
    "e02c05bb31ecbd466fc7f94c9a49f7785e8ae293062b7743720b68da8ba8c48d.jpg",  # Fig. 2
    "6edeb0db2c0c406203dfaedcd9eec722c9dafc14ce5c2be420b0b8ad8b6675aa.jpg",  # Fig. 3 case
    "2c78718cef0428c9eb986d573dae74271c7b03fea7751776f47efe9aa04ced9b.jpg",  # Fig. 6
], 1):
    copy(MINERU / "mmeacr" / "images" / filename, "mmeacr", i)
copy(PREVIOUS / "mmeacr-05.jpg", "mmeacr", 5)

print(f"Selected assets written to {OUT}")
