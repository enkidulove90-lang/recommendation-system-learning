"""Regression tests for the quota-safe MMSSL feature fetch preflight."""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest


MODULE_PATH = Path(__file__).with_name("fetch_mm_data.py")
SPEC = importlib.util.spec_from_file_location("fetch_mm_data", MODULE_PATH)
fetch_mm_data = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(fetch_mm_data)


def _write_split(path: Path, rows: dict[int, list[int]]) -> None:
    path.write_text(json.dumps({str(user): items for user, items in rows.items()}), encoding="utf-8")


def test_validate_source_bundle_accepts_matching_features_and_all_three_splits(tmp_path: Path) -> None:
    _write_split(tmp_path / "train.json", {0: [0, 1], 1: [2]})
    _write_split(tmp_path / "val.json", {0: [3]})
    _write_split(tmp_path / "test.json", {1: [4]})
    np.save(tmp_path / "image_feat.npy", np.zeros((5, 4096), dtype=np.float32))
    np.save(tmp_path / "text_feat.npy", np.zeros((5, 384), dtype=np.float32))

    summary = fetch_mm_data.validate_source_bundle(tmp_path)

    assert summary["n_items"] == 5
    assert summary["image_shape"] == [5, 4096]
    assert summary["text_shape"] == [5, 384]


def test_validate_source_bundle_rejects_feature_rows_that_miss_test_only_item(tmp_path: Path) -> None:
    _write_split(tmp_path / "train.json", {0: [0, 1]})
    _write_split(tmp_path / "val.json", {0: [2]})
    _write_split(tmp_path / "test.json", {0: [3]})
    np.save(tmp_path / "image_feat.npy", np.zeros((3, 4096), dtype=np.float32))
    np.save(tmp_path / "text_feat.npy", np.zeros((3, 384), dtype=np.float32))

    with pytest.raises(ValueError, match="item-count mismatch"):
        fetch_mm_data.validate_source_bundle(tmp_path)


def test_install_bundle_accepts_existing_identical_mmssl_splits(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write_split(source / "train.json", {0: [0, 1], 1: [2]})
    _write_split(source / "val.json", {0: [3]})
    _write_split(source / "test.json", {1: [1]})
    np.save(source / "image_feat.npy", np.zeros((4, 4096), dtype=np.float32))
    np.save(source / "text_feat.npy", np.zeros((4, 384), dtype=np.float32))
    destination = tmp_path / "amazon-baby-mmssl"
    destination.mkdir()
    (destination / "train.txt").write_text("0 0 1\n1 2\n", encoding="utf-8")
    (destination / "valid.txt").write_text("0 3\n", encoding="utf-8")
    (destination / "test.txt").write_text("1 1\n", encoding="utf-8")

    fetch_mm_data.install_bundle(source, destination)

    assert np.load(destination / "image_feat.npy").shape == (4, 4096)
    assert (destination / "fetch_manifest.json").is_file()
    manifest = json.loads((destination / "fetch_manifest.json").read_text(encoding="utf-8"))
    assert manifest["sha256"]["train.txt"] == hashlib.sha256((destination / "train.txt").read_bytes()).hexdigest()
