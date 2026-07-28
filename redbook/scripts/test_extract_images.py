"""Test extract-paper-images on MixRAGRec paper."""
import subprocess, sys, os

script = r".claude/skills/evil-read-arxiv/extract-paper-images/scripts/extract_images.py"
arxiv_id = "2605.28175"
out_dir = r"data/parsed/2605.28175/test_images"
os.makedirs(out_dir, exist_ok=True)

result = subprocess.run(
    [sys.executable, script, arxiv_id, out_dir, f"{out_dir}/index.md"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=120, cwd=r"c:\Users\xu.yan1\papers\recommendation-system-learning",
)
print("STDOUT:", result.stdout[:2000])
print("STDERR:", result.stderr[:1000])
print("RC:", result.returncode)

# List output
for f in os.listdir(out_dir):
    size = os.path.getsize(os.path.join(out_dir, f))
    print(f"  {f} ({size} bytes)")
