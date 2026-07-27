"""
Publish a paper-sharing post to Xiaohongshu using xiaohongshu-cli API.

Usage:
    python publish_paper.py --arxiv 2607.07108 --title "标题" --topic "推荐系统" --topic "LLM"

The script:
1. Reads paper summary from data/summaries/<arxiv>_*_summary.md
2. Formats body with emoji + line breaks + arxiv/github links
3. Calls `xhs post` with --topic for clickable tags
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMMARIES_DIR = os.path.join(PROJECT_ROOT, "data", "summaries")
PARSED_DIR = os.path.join(PROJECT_ROOT, "data", "parsed")


def find_summary(arxiv_id: str) -> str | None:
    """Find summary markdown by arxiv ID."""
    for f in os.listdir(SUMMARIES_DIR):
        if f.startswith(arxiv_id) and f.endswith("_summary.md"):
            return os.path.join(SUMMARIES_DIR, f)
    return None


def find_images(arxiv_id: str, count: int = 5) -> list[str]:
    """Find architecture images (prefer Figure 1-3, skip formula-heavy pages)."""
    paper_dirs = [d for d in os.listdir(PARSED_DIR) if d.startswith(arxiv_id)]
    if not paper_dirs:
        return []
    images_dir = os.path.join(PARSED_DIR, paper_dirs[0], "images")
    if not os.path.isdir(images_dir):
        return []

    all_images = sorted(os.listdir(images_dir))
    # Return first N images (adjust logic based on content.json for production)
    return [os.path.join(images_dir, img) for img in all_images[:count]]


def format_body(summary_text: str, arxiv_id: str, github_url: str = "") -> str:
    """
    Format paper summary into XHS-optimized post body with emoji headers.
    """
    # Strip metadata header and footer
    text = re.sub(r'^# .*?\n\n', '', summary_text)  # title line
    text = re.sub(r'\*\*英文标题\*\*: .*?\n', '', text)
    text = re.sub(r'\*\*arXiv ID\*\*: .*?\n', '', text)
    text = re.sub(r'\*\*生成时间\*\*: .*?\n', '', text)
    text = re.sub(r'\n---\n.*$', '', text.strip(), flags=re.DOTALL) + '\n'

    # Section mapping: (keyword, emoji_header, char_limit)
    section_map = [
        ('主要贡献', '🌟  核心贡献', 500),
        ('创新点', '🔍 关键创新', 500),
        ('方法论', '🧠 核心设计', 600),
        ('Benchmark', '📊 实验设置', 300),
        ('实验效果', '📊 实验效果', 400),
        ('对推荐系统', '💡 借鉴价值', 400),
    ]

    # Split by ## headers and collect content
    parts = re.split(r'\n## ', text)
    body_sections = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Find which section this is
        matched = False
        for keyword, emoji, limit in section_map:
            if part.startswith(keyword):
                # Remove the header line, get content
                content_lines = part.split('\n', 1)
                content = content_lines[1] if len(content_lines) > 1 else ''
                # Clean: remove list markers, join
                content = re.sub(r'^\d+\.\s*创新点\d+[：:]', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'^\d+\)\s*', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'^- ', '• ', content, flags=re.MULTILINE)
                content = re.sub(r'\*\*', '', content)
                # Compact whitespace
                content = re.sub(r'\n{2,}', '\n', content).strip()
                content = content[:limit]

                if content:
                    body_sections.append(f'{emoji}\n{content}')
                matched = True
                break

    body = '\n\n'.join(body_sections)

    # Append links
    body += f'\n\narxiv \U0001f517：https://arxiv.org/abs/{arxiv_id}'
    if github_url:
        body += f'\ngithub \U0001f517：{github_url}'

    return body


def main():
    parser = argparse.ArgumentParser(description='Publish paper to Xiaohongshu')
    parser.add_argument('--arxiv', required=True, help='arXiv ID (e.g. 2607.07108)')
    parser.add_argument('--title', required=True, help='Post title (≤20 chars)')
    parser.add_argument('--github', default='', help='GitHub URL (optional)')
    parser.add_argument('--topic', action='append', default=[], help='Topic tags (repeatable)')
    parser.add_argument('--images', action='append', default=[], help='Image paths (repeatable)')
    parser.add_argument('--image-count', type=int, default=5, help='Number of images to auto-select')
    parser.add_argument('--dry-run', action='store_true', help='Print body only, do not publish')
    args = parser.parse_args()

    # Find summary
    summary_path = find_summary(args.arxiv)
    if not summary_path:
        print(f"ERROR: No summary found for arXiv {args.arxiv}")
        sys.exit(1)

    with open(summary_path, 'r', encoding='utf-8') as f:
        summary_text = f.read()

    body = format_body(summary_text, args.arxiv, args.github)

    # Find images if not provided
    images = args.images
    if not images:
        images = find_images(args.arxiv, args.image_count)
    images = [img for img in images if os.path.exists(img)]

    if args.dry_run:
        print(f"Title: {args.title}")
        print(f"Body ({len(body)} chars):")
        print(body)
        print(f"Images: {len(images)}")
        print(f"Topics: {args.topic}")
        return

    if not images:
        print("ERROR: No images found or provided")
        sys.exit(1)

    # Set default topics if none provided
    topics = args.topic or ["推荐系统", "LLM", "论文分享", "AI"]

    # Build xhs post command
    cmd = ["xhs", "post", "--title", args.title, "--body", body]
    for img in images:
        cmd.extend(["--images", img])
    for t in topics:
        cmd.extend(["--topic", t])

    print(f"Publishing: {args.title}")
    print(f"  Body: {len(body)} chars")
    print(f"  Images: {len(images)}")
    print(f"  Topics: {topics}")

    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
