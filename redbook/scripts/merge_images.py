"""Merge similar paper images into composite figures for XHS posting."""
from PIL import Image
import os

IMG_DIR = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\images_hd'
OUT_DIR = IMG_DIR  # save alongside originals

def merge_2x2(files, output_name):
    """Merge 4 images into a 2x2 grid."""
    images = [Image.open(os.path.join(IMG_DIR, f)) for f in files]
    # Resize all to the same size (use smallest as reference)
    w = min(img.width for img in images)
    h = min(img.height for img in images)
    images = [img.resize((w, h), Image.LANCZOS) for img in images]

    # Create 2x2 grid
    grid = Image.new('RGB', (w * 2, h * 2), (255, 255, 255))
    grid.paste(images[0], (0, 0))
    grid.paste(images[1], (w, 0))
    grid.paste(images[2], (0, h))
    grid.paste(images[3], (w, h))

    out_path = os.path.join(OUT_DIR, output_name)
    grid.save(out_path, quality=95)
    print(f"2x2 grid saved: {output_name} ({grid.width}x{grid.height})")
    return out_path

def merge_horizontal(files, output_name):
    """Merge 2 images side by side."""
    images = [Image.open(os.path.join(IMG_DIR, f)) for f in files]
    # Scale to same height
    h = min(img.height for img in images)
    scaled = []
    total_w = 0
    for img in images:
        ratio = h / img.height
        new_w = int(img.width * ratio)
        scaled.append(img.resize((new_w, h), Image.LANCZOS))
        total_w += new_w

    merged = Image.new('RGB', (total_w, h), (255, 255, 255))
    x = 0
    for img in scaled:
        merged.paste(img, (x, 0))
        x += img.width

    out_path = os.path.join(OUT_DIR, output_name)
    merged.save(out_path, quality=95)
    print(f"Horizontal merge: {output_name} ({merged.width}x{merged.height})")
    return out_path

# 1. ICS mechanism: 2x2 grid
merge_2x2(
    ['ics_a.jpg', 'ics_b.jpg', 'ics_c.jpg', 'ics_d.jpg'],
    'ICS_2x2_mechanism.jpg'
)

# 2. Layer sparsity: side by side
merge_horizontal(
    ['layer1.png', 'layer2.png'],
    'layer_sparsity_compare.png'
)

print("\nDone! Merged images saved to:", OUT_DIR)
