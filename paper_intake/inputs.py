from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

import httpx


class InputValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class CanonicalSource:
    normalized_url: str
    canonical_id: str = ""


@dataclass(frozen=True, slots=True)
class SavedInput:
    path: Path
    sha256: str
    size: int
    original_name: str = ""


_ARXIV_PATH = re.compile(
    r"^/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?/?$",
    re.IGNORECASE,
)
_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]")


def canonicalize_url(raw_url: str) -> CanonicalSource:
    value = raw_url.strip()
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise InputValidationError("invalid_url", "Paper URL must use http or https.")

    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    arxiv_match = _ARXIV_PATH.fullmatch(parsed.path)
    if host in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"} and arxiv_match:
        paper_id = arxiv_match.group(1)
        return CanonicalSource(
            normalized_url=f"https://arxiv.org/pdf/{paper_id}.pdf",
            canonical_id=paper_id,
        )

    normalized = urlunsplit((scheme, host, parsed.path or "/", parsed.query, ""))
    return CanonicalSource(normalized_url=normalized)


def sanitize_filename(filename: str) -> str:
    basename = PurePosixPath(filename.replace("\\", "/")).name.strip()
    if not basename:
        basename = "source.pdf"
    stem = Path(basename).stem or "source"
    safe_stem = _UNSAFE_FILENAME.sub("_", stem)[:100].strip(".") or "source"
    return f"{safe_stem}.pdf"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_pdf(data_prefix: bytes, size: int, max_file_bytes: int) -> None:
    if size > max_file_bytes:
        raise InputValidationError(
            "file_too_large",
            f"PDF exceeds the {max_file_bytes} bytes upload limit.",
        )
    if not data_prefix.startswith(b"%PDF-"):
        raise InputValidationError("invalid_pdf", "Uploaded content is not a valid PDF.")


class PaperInputStore:
    def __init__(self, root: str | Path, *, max_file_bytes: int = 100 * 1024 * 1024):
        self.root = Path(root)
        self.max_file_bytes = max_file_bytes

    def store_upload(self, job_id: str, filename: str, content: bytes) -> SavedInput:
        _validate_pdf(content[:8], len(content), self.max_file_bytes)
        job_dir = self.root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        target = job_dir / sanitize_filename(filename)
        target.write_bytes(content)
        return SavedInput(
            path=target,
            sha256=sha256_file(target),
            size=len(content),
            original_name=filename,
        )

    def download_url(
        self,
        job_id: str,
        url: str,
        *,
        client=None,
    ) -> SavedInput:
        source = canonicalize_url(url)
        job_dir = self.root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        target = job_dir / "source.pdf"
        owns_client = client is None
        http_client = client or httpx.Client(follow_redirects=True, timeout=120.0)
        digest = hashlib.sha256()
        size = 0
        prefix = b""
        try:
            with http_client.stream("GET", source.normalized_url) as response:
                response.raise_for_status()
                with target.open("wb") as handle:
                    for chunk in response.iter_bytes():
                        if not chunk:
                            continue
                        size += len(chunk)
                        if size > self.max_file_bytes:
                            raise InputValidationError(
                                "file_too_large",
                                f"PDF exceeds the {self.max_file_bytes} bytes upload limit.",
                            )
                        if len(prefix) < 8:
                            prefix += chunk[: 8 - len(prefix)]
                        digest.update(chunk)
                        handle.write(chunk)
            _validate_pdf(prefix, size, self.max_file_bytes)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        finally:
            if owns_client:
                http_client.close()
        return SavedInput(
            path=target,
            sha256=digest.hexdigest(),
            size=size,
            original_name=PurePosixPath(urlsplit(source.normalized_url).path).name,
        )
