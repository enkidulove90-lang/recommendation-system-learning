"""Quota-safe acquisition of the MMSSL Amazon-Baby image and text features.

This utility accepts a reviewed, per-file Google Drive manifest, validates a
complete staging bundle, then atomically installs it into
``data/amazon-baby-mmssl``. It intentionally never crawls the HKUDS parent
folder, which avoids unnecessary Drive requests and partial overwrites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_DESTINATION = ROOT / "data" / "amazon-baby-mmssl"
SOURCE_FOLDER_ID = "1AB1RsnU-ETmubJgWLpJrXd8TjaK_eTp0"
REQUIRED_FILES = ("train.json", "val.json", "test.json", "image_feat.npy", "text_feat.npy")


class FetchError(RuntimeError):
    """Raised before an incomplete or unverified bundle can be installed."""


def _load_split(path: Path) -> dict[str, list[int]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid split file: {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"split must be a user-to-items object: {path}")
    normalized: dict[str, list[int]] = {}
    for user, items in value.items():
        if not isinstance(items, list) or not items:
            raise ValueError(f"split has an empty or invalid sequence for user {user!r}: {path}")
        try:
            normalized[str(user)] = [int(item) for item in items]
        except (TypeError, ValueError) as error:
            raise ValueError(f"split has a non-integer item for user {user!r}: {path}") from error
    return normalized


def validate_source_bundle(source: Path) -> dict[str, Any]:
    """Validate every split and both feature arrays before changing data."""
    missing = [name for name in REQUIRED_FILES if not (source / name).is_file()]
    if missing:
        raise ValueError(f"missing required source files: {', '.join(missing)}")

    max_item = -1
    split_users: dict[str, int] = {}
    for split in ("train", "val", "test"):
        rows = _load_split(source / f"{split}.json")
        split_users[split] = len(rows)
        max_item = max(max_item, *(max(items) for items in rows.values()))
    n_items = max_item + 1
    image = np.load(source / "image_feat.npy", mmap_mode="r")
    text = np.load(source / "text_feat.npy", mmap_mode="r")
    if image.ndim != 2 or text.ndim != 2:
        raise ValueError("feature arrays must be rank-2")
    if image.shape[0] != n_items or text.shape[0] != n_items:
        raise ValueError(
            "item-count mismatch: "
            f"splits imply {n_items}, image rows={image.shape[0]}, text rows={text.shape[0]}"
        )
    return {
        "n_items": n_items,
        "image_shape": list(image.shape),
        "text_shape": list(text.shape),
        "split_users": split_users,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _split_semantic_hash(path: Path) -> str:
    """Hash grouped splits independent of Windows versus Unix line endings."""
    rows: list[tuple[int, list[int]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) < 2:
            raise FetchError(f"invalid grouped split row: {path}")
        try:
            rows.append((int(fields[0]), [int(item) for item in fields[1:]]))
        except ValueError as error:
            raise FetchError(f"non-integer grouped split row: {path}") from error
    rows.sort(key=lambda row: row[0])
    canonical = "".join(f"{user} {' '.join(map(str, items))}\n" for user, items in rows)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_grouped_split(source: Path, destination: Path) -> None:
    rows = _load_split(source)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for user in sorted(rows, key=int):
            handle.write(f"{user} {' '.join(map(str, rows[user]))}\n")


def install_bundle(source: Path, destination: Path) -> dict[str, Any]:
    """Install a verified bundle through a sibling staging directory."""
    summary = validate_source_bundle(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="amazon-baby-mmssl-install-", dir=destination.parent))
    try:
        for source_name, destination_name in (("train.json", "train.txt"), ("val.json", "valid.txt"), ("test.json", "test.txt")):
            _write_grouped_split(source / source_name, staging / destination_name)
        for feature in ("image_feat.npy", "text_feat.npy"):
            shutil.copy2(source / feature, staging / feature)
        hashes = {name: _sha256(staging / name) for name in ("train.txt", "valid.txt", "test.txt", "image_feat.npy", "text_feat.npy")}
        split_semantic_hashes = {name: _split_semantic_hash(staging / name) for name in ("train.txt", "valid.txt", "test.txt")}
        manifest = {
            "source_folder_id": SOURCE_FOLDER_ID,
            "summary": summary,
            "sha256": hashes,
            "split_semantic_sha256": split_semantic_hashes,
        }
        (staging / "fetch_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not destination.exists():
            os.replace(staging, destination)
            return manifest
        required_splits = ("train.txt", "valid.txt", "test.txt")
        missing_splits = [name for name in required_splits if not (destination / name).is_file()]
        if missing_splits:
            raise FetchError(f"existing destination lacks split files: {', '.join(missing_splits)}")
        changed_splits = [
            name for name in required_splits
            if _split_semantic_hash(destination / name) != split_semantic_hashes[name]
        ]
        if changed_splits:
            raise FetchError(
                "refusing to replace a non-identical existing split bundle: "
                f"{', '.join(changed_splits)}"
            )
        existing_features = [name for name in ("image_feat.npy", "text_feat.npy") if (destination / name).exists()]
        if existing_features:
            raise FetchError(f"refusing to overwrite existing features: {', '.join(existing_features)}")
        for feature in ("image_feat.npy", "text_feat.npy"):
            os.replace(staging / feature, destination / feature)
        for name in required_splits:
            hashes[name] = _sha256(destination / name)
        (staging / "fetch_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(staging / "fetch_manifest.json", destination / "fetch_manifest.json")
        shutil.rmtree(staging, ignore_errors=True)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _read_manifest(path: Path) -> dict[str, str]:
    try:
        files = json.loads(path.read_text(encoding="utf-8"))["files"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise FetchError(f"invalid manifest: {path}") from error
    if not isinstance(files, dict) or set(files) != set(REQUIRED_FILES):
        raise FetchError(f"manifest must list exactly: {', '.join(REQUIRED_FILES)}")
    if not all(isinstance(url, str) and url.startswith("https://drive.google.com/") for url in files.values()):
        raise FetchError("manifest entries must be Google Drive HTTPS URLs")
    return {name: str(url) for name, url in files.items()}


def download_manifest(manifest_path: Path, output: Path) -> None:
    """Download five reviewed files once each; never crawl a Drive parent folder."""
    try:
        import gdown
    except ImportError as error:
        raise FetchError("gdown is required; install it in the experiment environment before rerunning") from error
    files = _read_manifest(manifest_path)
    output.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FILES:
        target = output / name
        result = gdown.download(url=files[name], output=str(target), quiet=False, fuzzy=True, resume=True)
        if not result or not target.is_file() or target.stat().st_size == 0:
            raise FetchError(f"download failed or returned an empty file: {name}")


def write_plan(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "blocked_access_required",
        "source_folder_id": SOURCE_FOLDER_ID,
        "required_files": list(REQUIRED_FILES),
        "instructions": "Grant viewer access, obtain only the five Amazon-Baby file URLs, save them in a reviewed manifest, then rerun with --manifest.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a quota-safe MMSSL Amazon-Baby feature bundle")
    parser.add_argument("--manifest", type=Path, help="reviewed five-file Google Drive manifest")
    parser.add_argument("--source-dir", type=Path, help="already downloaded source bundle; no network request")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--plan", type=Path, help="write an access plan and exit")
    args = parser.parse_args()
    if args.plan:
        write_plan(args.plan)
        print(f"[fetch] wrote access plan: {args.plan}")
        return 0
    if bool(args.manifest) == bool(args.source_dir):
        parser.error("provide exactly one of --manifest or --source-dir")
    if args.source_dir:
        source = args.source_dir
        network_mode = False
    else:
        source = Path(tempfile.mkdtemp(prefix="amazon-baby-mmssl-download-"))
        network_mode = True
        try:
            download_manifest(args.manifest, source)
        except Exception:
            shutil.rmtree(source, ignore_errors=True)
            raise
    try:
        result = install_bundle(source, args.destination)
    finally:
        if network_mode:
            shutil.rmtree(source, ignore_errors=True)
    print(json.dumps({"status": "installed", "destination": str(args.destination), **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FetchError as error:
        print(f"[fetch] ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
