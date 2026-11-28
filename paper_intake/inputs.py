from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from .pacing import GLOBAL_ARXIV_PACER, OFFICIAL_ARXIV_HOSTS, ArxivPacer


class InputValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class CanonicalSource:
    normalized_url: str
    canonical_id: str = ""
    version: int | None = None


@dataclass(frozen=True, slots=True)
class SavedInput:
    path: Path
    sha256: str
    size: int
    original_name: str = ""
    manifest_path: Path | None = None


_ARXIV_PATH = re.compile(
    r"^/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v(\d+))?(?:\.pdf)?/?$",
    re.IGNORECASE,
)
_ARXIV_BARE = re.compile(r"^(\d{4}\.\d{4,5})(?:v(\d+))?(?:\.pdf)?$", re.IGNORECASE)
_ACL_PDF_PATH = re.compile(r"^/(\d{4}\.[a-z0-9-]+\.\d+)\.pdf$", re.IGNORECASE)
_ACL_PDF_NO_EXT = re.compile(r"^/(\d{4}\.[a-z0-9-]+\.\d+)$", re.IGNORECASE)
_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]")
# 匹配 ACM DOI URL，路径格式：/doi/10.xxxx/xxxx 或 /doi/pdf/10.xxxx/xxxx
_ACLMDOI_PATH = re.compile(r"^/doi(?:/pdf)?/(10\.\d+/.+)$", re.IGNORECASE)


def canonicalize_url(raw_url: str) -> CanonicalSource:
    value = raw_url.strip()
    bare_match = _ARXIV_BARE.fullmatch(value)
    if bare_match:
        paper_id = bare_match.group(1)
        return CanonicalSource(
            normalized_url=f"https://arxiv.org/pdf/{paper_id}.pdf",
            canonical_id=paper_id,
            version=int(bare_match.group(2)) if bare_match.group(2) else None,
        )
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise InputValidationError("invalid_url", "Paper URL must use http or https.")

    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    arxiv_match = _ARXIV_PATH.fullmatch(parsed.path)
    if host in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"} and arxiv_match:
        paper_id = arxiv_match.group(1)
        return CanonicalSource(
            normalized_url=f"https://arxiv.org/pdf/{paper_id}.pdf",
            canonical_id=paper_id,
            version=int(arxiv_match.group(2)) if arxiv_match.group(2) else None,
        )

    acl_match = _ACL_PDF_PATH.fullmatch(parsed.path)
    if host == "aclanthology.org" and acl_match:
        return CanonicalSource(normalized_url=f"https://aclanthology.org/{acl_match.group(1)}.pdf", canonical_id=acl_match.group(1))

    # 处理 ACM DOI URL
    acmdoi_match = _ACLMDOI_PATH.fullmatch(parsed.path)
    if host in {"dl.acm.org", "www.dl.acm.org"} and acmdoi_match:
        doi = acmdoi_match.group(1)
        return CanonicalSource(
            normalized_url=f"https://dl.acm.org/doi/{doi}",
            canonical_id=doi,
        )

    if parsed.username or parsed.password:
        raise InputValidationError("url_userinfo_forbidden", "Paper URLs must not contain user credentials.")
    netloc = host + (f":{parsed.port}" if parsed.port else "")
    normalized = urlunsplit((scheme, netloc, parsed.path or "/", parsed.query, ""))
    return CanonicalSource(normalized_url=normalized)


def sanitize_filename(filename: str) -> str:
    basename = PurePosixPath(filename.replace("\\", "/")).name.strip()
    if not basename:
        basename = "source.pdf"
    stem = Path(basename).stem or "source"
    safe_stem = _UNSAFE_FILENAME.sub("_", stem)[:100].strip(".") or "source"
    return f"{safe_stem}.pdf"


def redact_url(value: str) -> str:
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if not host:
        return value.split("?", 1)[0].split("#", 1)[0]
    port = f":{parsed.port}" if parsed.port else ""
    return urlunsplit((parsed.scheme, host + port, parsed.path, "", ""))


def parse_retry_after(value: str, *, now: datetime | None = None) -> int | None:
    if value.isdigit():
        return int(value)
    try:
        target = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if target is None:
        return None
    current = now or datetime.now(timezone.utc)
    return max(0, math.ceil((target - current).total_seconds()))


@contextmanager
def _paced_stream(client, url: str, pacer: ArxivPacer, source: CanonicalSource, on_start=None, on_span=None):
    current = url
    chain: list[dict[str, str]] = []
    total_wait = 0.0
    official_source = urlsplit(url).hostname in OFFICIAL_ARXIV_HOSTS
    for _ in range(6):
        with pacer.request(current) as waited:
            total_wait += waited
            started = pacer.clock()
            if on_start:
                on_start(started, total_wait)
            try:
                with client.stream("GET", current) as response:
                    chain.append({"domain": urlsplit(current).hostname or "", "path": urlsplit(current).path})
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location", "")
                        destination = urljoin(current, location)
                        parsed = urlsplit(destination)
                        if not location or parsed.scheme != "https" or (official_source and parsed.hostname not in OFFICIAL_ARXIV_HOSTS):
                            raise InputValidationError("pdf_redirect_invalid", "PDF source redirected outside the official HTTPS endpoints.")
                        if source.version:
                            target = canonicalize_url(destination)
                            if target.canonical_id != source.canonical_id or target.version != source.version:
                                raise InputValidationError("pdf_version_mismatch", "PDF redirect changed the arXiv version.")
                    else:
                        final_url = str(response.url) if getattr(response, "url", None) else ""
                        if final_url and final_url != current:
                            chain.append({"domain": urlsplit(final_url).hostname or "", "path": urlsplit(final_url).path})
                        yield response, chain, total_wait
                        return
            finally:
                if on_span:
                    on_span({
                        "domain": urlsplit(current).hostname or "",
                        "start_monotonic": started,
                        "end_monotonic": pacer.clock(),
                        "wait_before_request": waited,
                    })
        current = destination
    raise InputValidationError("pdf_redirect_loop", "PDF source redirected too many times.")


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
    def __init__(
        self, root: str | Path, *, max_file_bytes: int = 100 * 1024 * 1024,
        pacer: ArxivPacer | None = None,
    ):
        self.root = Path(root)
        self.max_file_bytes = max_file_bytes
        self.pacer = pacer or GLOBAL_ARXIV_PACER

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
        manifest_path = job_dir / "download_manifest.json"
        primary_url = (
            f"https://arxiv.org/pdf/{source.canonical_id}v{source.version}"
            if source.canonical_id and source.version else source.normalized_url
        )
        cache_path = self.root / "_cache" / "arxiv" / f"{source.canonical_id}v{source.version}.pdf" if source.canonical_id and source.version else None
        cache_manifest = cache_path.with_suffix(".json") if cache_path else None
        checks = {
            "pdf_exists": bool(cache_path and cache_path.is_file()),
            "manifest_exists": bool(cache_manifest and cache_manifest.is_file()),
            "identity_matches": False, "sha256_matches": False,
            "size_matches": False, "magic_matches": False,
        }
        if cache_path and cache_manifest and cache_path.is_file() and cache_manifest.is_file():
            try:
                cached = json.loads(cache_manifest.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cached = {}
            with cache_path.open("rb") as cached_pdf:
                cached_prefix = cached_pdf.read(5)
            checks.update({
                "identity_matches": cached.get("arxiv_id") == source.canonical_id and cached.get("version") == source.version,
                "sha256_matches": cached.get("sha256") == sha256_file(cache_path),
                "size_matches": cached.get("byte_size") == cache_path.stat().st_size,
                "magic_matches": cached_prefix == b"%PDF-",
            })
            if all(checks.values()):
                (job_dir / "cache_validation_report.json").write_text(
                    json.dumps({"hit": True, "checks": checks}, indent=2), encoding="utf-8",
                )
                shutil.copy2(cache_path, target)
                manifest = {
                    **cached, "attempt_count": 0, "attempts": [], "attempt_timeline": [],
                    "redirect_chain": [], "cache_hit": True,
                }
                manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                (job_dir / "pacing_log.json").write_text("[]", encoding="utf-8")
                return SavedInput(target, cached["sha256"], cached["byte_size"],
                                  PurePosixPath(urlsplit(primary_url).path).name, manifest_path)
        (job_dir / "cache_validation_report.json").write_text(
            json.dumps({"hit": False, "checks": checks}, indent=2), encoding="utf-8",
        )
        owns_client = client is None
        http_client = client or httpx.Client(follow_redirects=False, timeout=120.0, trust_env=False)
        candidates = [primary_url] * 3
        if source.canonical_id and urlsplit(source.normalized_url).hostname == "arxiv.org":
            suffix = f"v{source.version}" if source.version else ""
            candidates[-1] = f"https://export.arxiv.org/pdf/{source.canonical_id}{suffix}"
        last_failure = ""
        rate_limited = False
        server_unavailable_url = ""
        prefer_mirror = False
        attempted_hosts: list[str] = []
        attempts: list[dict] = []
        request_spans: list[dict] = []
        response_status: int | None = None
        content_type = ""
        retry_after_seconds: int | None = None
        retry_not_before = ""
        pdf_eof_present = False
        redirect_chain: list[dict[str, str]] = []

        def record(candidate: str, error_type: str, status: int | None = None, *, retry_after_honored: bool = False) -> None:
            attempts.append({"domain": urlsplit(candidate).hostname, "error_type": error_type,
                             "status_code": status, "retry_after_honored": retry_after_honored,
                             "cleaned": not target.exists() if error_type else False,
                             "pacing_wait_seconds": attempt_clock[1],
                             "start_monotonic": attempt_clock[0],
                             "end_monotonic": self.pacer.clock()})

        def save_manifest(*, status: str, final_domain: str = "", digest: str = "", byte_size: int = 0) -> dict:
            manifest = {"arxiv_id": source.canonical_id, "version": source.version,
                        "attempt_count": len(attempts), "attempts": attempts,
                        "final_domain": final_domain, "http_status": response_status,
                        "content_type": content_type, "sha256": digest, "byte_size": byte_size,
                        "first_5_bytes": "%PDF-" if status == "success" else "",
                        "cache_hit": False, "status": status,
                        "retry_after_seconds": retry_after_seconds,
                        "retry_not_before": retry_not_before,
                        "manual_retry_required": status == "rate_limited_manual_retry",
                        "manual_retry_endpoint": f"/api/jobs/{job_id}/retry" if status == "rate_limited_manual_retry" else "",
                        "pdf_eof_present": pdf_eof_present,
                        "redirect_chain": redirect_chain,
                        "attempt_timeline": [
                            {"domain": item["domain"], "start_monotonic": item["start_monotonic"],
                             "end_monotonic": item["end_monotonic"],
                             "wait_before": item["pacing_wait_seconds"],
                             "error_type": item["error_type"], "status": item["status_code"],
                             "cache_hit": False}
                            for item in attempts
                        ]}
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            (job_dir / "pacing_log.json").write_text(
                json.dumps(request_spans, indent=2), encoding="utf-8",
            )
            return manifest
        try:
            for attempt, candidate in enumerate(candidates, start=1):
                if rate_limited:
                    candidate = rate_limited_url
                elif server_unavailable_url:
                    candidate = server_unavailable_url
                elif prefer_mirror:
                    candidate = candidates[-1]
                host = urlsplit(candidate).hostname or "unknown"
                if host not in attempted_hosts:
                    attempted_hosts.append(host)
                digest = hashlib.sha256()
                size = 0
                prefix = b""
                response_status = None
                content_type = ""
                final_host = host
                pacing_wait = 0.0
                attempt_clock = [self.pacer.clock(), 0.0]
                def note_request_start(started: float, waited: float) -> None:
                    attempt_clock[:] = [started, waited]
                wait_seconds = 3 * (2 ** (attempt - 1))
                try:
                    with _paced_stream(
                        http_client, candidate, self.pacer, source,
                        on_start=note_request_start, on_span=request_spans.append,
                    ) as (response, redirect_chain, pacing_wait):
                        response.raise_for_status()
                        response_status = response.status_code
                        content_type = response.headers.get("content-type", "")
                        if getattr(response, "url", None):
                            final_host = urlsplit(str(response.url)).hostname or host
                        if content_type.split(";", 1)[0].strip().lower() in {"text/html", "application/json"}:
                            raise InputValidationError("invalid_pdf", "PDF source returned an error document.")
                        if source.version and getattr(response, "url", None):
                            final_source = canonicalize_url(str(response.url))
                            if final_source.canonical_id != source.canonical_id or final_source.version != source.version:
                                raise InputValidationError("pdf_version_mismatch", "PDF redirect changed the arXiv version.")
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
                    with target.open("rb") as completed:
                        completed.seek(max(0, size - 1024))
                        pdf_eof_present = b"%%EOF" in completed.read()
                    record(candidate, "", response_status)
                    manifest = save_manifest(status="success", final_domain=final_host, digest=digest.hexdigest(), byte_size=size)
                    if cache_path and cache_manifest:
                        cache_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target, cache_path)
                        if sha256_file(cache_path) == digest.hexdigest() and cache_path.stat().st_size == size:
                            cache_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                        else:
                            cache_path.unlink(missing_ok=True)
                            cache_manifest.unlink(missing_ok=True)
                    return SavedInput(
                        path=target,
                        sha256=digest.hexdigest(),
                        size=size,
                        original_name=PurePosixPath(urlsplit(primary_url).path).name,
                        manifest_path=manifest_path,
                    )
                except httpx.HTTPStatusError as exc:
                    target.unlink(missing_ok=True)
                    status = exc.response.status_code
                    response_status = status
                    record(candidate, "RetryableHTTP" if status == 429 or status >= 500 else "PermanentHTTP", status)
                    if status != 429 and status < 500:
                        save_manifest(status="permanent_failure")
                        raise InputValidationError(f"pdf_http_{status}", f"PDF source returned HTTP {status}.") from exc
                    last_failure = f"HTTP {status}"
                    retry_after_seconds = parse_retry_after(exc.response.headers.get("Retry-After", ""))
                    if retry_after_seconds is not None:
                        if retry_after_seconds > 30:
                            retry_not_before = (
                                datetime.now(timezone.utc) + timedelta(seconds=retry_after_seconds)
                            ).isoformat().replace("+00:00", "Z")
                            save_manifest(status="rate_limited_manual_retry" if status == 429 else "download_exhausted")
                            raise InputValidationError(
                                "pdf_rate_limited_manual_retry" if status == 429 else "pdf_retry_later",
                                "PDF source requested a longer retry delay; retry later.",
                            ) from exc
                        wait_seconds = max(wait_seconds, retry_after_seconds)
                        attempts[-1]["retry_after_honored"] = True
                    if status == 429:
                        rate_limited = True
                        rate_limited_url = candidate
                        if retry_after_seconds is None:
                            wait_seconds = [5, 15][attempt - 1] if attempt < 3 else 0
                    elif status == 503:
                        server_unavailable_url = candidate
                except httpx.TransportError as exc:
                    target.unlink(missing_ok=True)
                    last_failure = type(exc).__name__
                    record(candidate, type(exc).__name__)
                except InputValidationError as exc:
                    target.unlink(missing_ok=True)
                    if exc.code != "invalid_pdf":
                        record(candidate, type(exc).__name__, response_status)
                        save_manifest(status="permanent_failure")
                        raise
                    last_failure = exc.code
                    prefer_mirror = True
                    record(candidate, "NonPDFResponse", response_status)
                except Exception:
                    target.unlink(missing_ok=True)
                    record(candidate, "InternalError", response_status)
                    save_manifest(status="internal_failure")
                    raise
                if attempt < len(candidates):
                    time.sleep(wait_seconds)
            hosts = ", ".join(attempted_hosts)
            save_manifest(status="rate_limited" if rate_limited else "download_exhausted")
            raise InputValidationError(
                "pdf_rate_limited" if rate_limited else "pdf_download_unavailable",
                f"PDF download failed after {len(candidates)} attempts across {hosts}; last failure: {last_failure}.",
            )
        finally:
            (job_dir / "pacing_log.json").write_text(
                json.dumps(request_spans, indent=2), encoding="utf-8",
            )
            if owns_client:
                http_client.close()
