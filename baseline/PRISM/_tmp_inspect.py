import numpy as np, os  # numpy-only, no torch (torch segfaults under Git Bash)
base = "baseline/LightGCNpp/data/amazon-baby-mmssl"
for f in ["image_feat.npy", "text_feat.npy"]:
    a = np.load(os.path.join(base, f))
    print(f, "shape", a.shape, "dtype", a.dtype,
          "min", float(a.min()), "max", float(a.max()), "hasnan", bool(np.isnan(a).any()))

mins = 10**9; maxs = -1; nlines = 0
itemset = set(); nz_itemset = set(); zero_mid = 0
for split in ["train.txt", "valid.txt", "test.txt"]:
    with open(os.path.join(base, split)) as fh:
        for line in fh:
            parts = line.strip().split()
            if not parts:
                continue
            nlines += 1
            items = [int(x) for x in parts[1:]]
            if items:
                mins = min(mins, min(items)); maxs = max(maxs, max(items))
                for it in items:
                    itemset.add(it)
                    if it != 0:
                        nz_itemset.add(it)
                if 0 in items[1:]:
                    zero_mid += 1
print("txt: nlines", nlines, "gmin", mins, "gmax", maxs,
      "distinct", len(itemset), "distinct_nonzero", len(nz_itemset),
      "zero_midseq", zero_mid, "has0", (0 in itemset))
# feature row count vs item convention
img = np.load(os.path.join(base, "image_feat.npy"))
print("image rows", img.shape[0], "vs gmax", maxs, "vs distinct_nonzero", len(nz_itemset))
print("hypothesis check: rows==gmax -> 0-based incl 0 as a row? rows==distinct_nonzero -> 1-based features")
