from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Callable

import requests


def _download(url: str) -> bytes:
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, timeout=(10, 120))
    response.raise_for_status()
    return response.content


def bootstrap_snapshot(
    manifest_path: Path,
    cache_root: Path,
    *,
    downloader: Callable[[str], bytes] = _download,
) -> Path:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("enabled", True) is not True:
        raise ValueError("snapshot manifest is disabled")
    revision = str(manifest.get("revision", "")).strip()
    expected = str(manifest.get("sha256", "")).strip().casefold()
    source_url = str(manifest.get("source_url", "")).strip()
    filename = str(manifest.get("filename", "")).strip()
    if not revision or revision.casefold() in {"main", "master", "latest"}:
        raise ValueError("snapshot revision must be pinned")
    if not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("snapshot checksum must be a SHA256")
    if not source_url.startswith("https://") or not filename or Path(filename).name != filename:
        raise ValueError("snapshot source or filename is invalid")

    payload = downloader(source_url)
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        raise ValueError("snapshot checksum mismatch")
    root = Path(cache_root)
    root.mkdir(parents=True, exist_ok=True)
    output = root / filename
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a pinned Papers with Code snapshot")
    parser.add_argument("--manifest", type=Path, default=Path("config/pwc-snapshot.json"))
    parser.add_argument("--cache-root", type=Path, default=Path(".paper-work/cache/pwc"))
    args = parser.parse_args()
    output = bootstrap_snapshot(args.manifest, args.cache_root)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
