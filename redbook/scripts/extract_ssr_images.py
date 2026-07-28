"""Extract SSR paper images and create draft."""
import subprocess, sys, os

BASE = r"c:\Users\xu.yan1\papers\recommendation-system-learning"
SCRIPT = os.path.join(BASE, ".claude/skills/evil-read-arxiv/extract-paper-images/scripts/extract_images.py")
OUT_DIR = os.path.join(BASE, "data/parsed/2604.08011/images_hd")
os.makedirs(OUT_DIR, exist_ok=True)

# Step 1: Extract high-quality images
print("=== Extracting images ===")
result = subprocess.run(
    [sys.executable, SCRIPT, "2604.08011", OUT_DIR, f"{OUT_DIR}/index.md"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=120, cwd=BASE,
)
print(result.stdout[:2000])
if result.returncode != 0:
    print("STDERR:", result.stderr[:500])
    sys.exit(1)

# List images
print("\n=== Extracted images ===")
for f in sorted(os.listdir(OUT_DIR)):
    if f.endswith('.png') or f.endswith('.pdf'):
        size = os.path.getsize(os.path.join(OUT_DIR, f))
        print(f"  {f} ({size:,} bytes)")
