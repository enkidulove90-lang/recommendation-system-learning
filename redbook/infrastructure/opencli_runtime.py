"""Locate and invoke the OpenCLI binary reliably on Windows/MinGW.

Why this module exists
----------------------
``shutil.which("opencli")`` returns ``None`` in this environment even though
OpenCLI 1.8.6 is installed, because the npm shim lives in a Node distribution
directory that is not on ``PATH``.  The MinGW ``opencli`` bash wrapper is also
broken: it mangles ``/c/Users/...`` into ``c:\\c\\Users\\...`` and fails with
``MODULE_NOT_FOUND``.

The only invocation that works from Python is calling the Node entry point
directly::

    <node.exe> <.../@jackwener/opencli/dist/src/main.js> <args...>

This module resolves that pair once and caches it.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess

#: Relative path of the OpenCLI entry point inside a Node installation.
_MAIN_REL = Path("node_modules/@jackwener/opencli/dist/src/main.js")

#: Directories that may contain a Node distribution shipping OpenCLI.
_NODE_HINTS: tuple[Path, ...] = (
    Path.home() / "nodejs" / "node-v24.18.0-win-x64",
    Path.home() / "nodejs",
    Path.home() / "AppData" / "Roaming" / "npm",
)


class OpenCliUnavailable(RuntimeError):
    """OpenCLI could not be located, or its daemon/extension is not connected."""


@dataclass(frozen=True)
class OpenCliRuntime:
    """A resolved, directly-invocable OpenCLI installation."""

    node: Path
    main: Path

    @property
    def base_command(self) -> list[str]:
        return [str(self.node), str(self.main)]

    def command(self, *parts: str) -> list[str]:
        return [*self.base_command, *parts]

    def run(
        self,
        *parts: str,
        timeout: int = 300,
        check: bool = False,
        browser_timeout: int | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run an OpenCLI subcommand and capture its output as UTF-8 text.

        OpenCLI applies its own 60s ceiling to every browser-backed command.
        Creator-center automation (image upload, topic pickers, PDF attachment)
        routinely exceeds that, so the per-command budget is raised via
        ``OPENCLI_BROWSER_COMMAND_TIMEOUT`` and kept below the subprocess
        ``timeout`` so OpenCLI reports a clean error instead of being killed.
        """
        env = dict(os.environ)
        env["OPENCLI_BROWSER_COMMAND_TIMEOUT"] = str(
            browser_timeout if browser_timeout is not None else max(30, timeout - 30)
        )
        result = subprocess.run(
            self.command(*parts),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=env,
        )
        if check and result.returncode:
            raise OpenCliUnavailable(
                f"opencli {' '.join(parts[:3])} failed (rc={result.returncode}): "
                f"{(result.stderr or result.stdout or '').strip()[:400]}"
            )
        return result

    def run_json(
        self, *parts: str, timeout: int = 300, browser_timeout: int | None = None
    ) -> dict | list:
        """Run a subcommand with ``-f json`` and parse stdout.

        OpenCLI emits YAML-ish error envelopes (``ok: false``) on failure even
        when JSON was requested, so a parse failure is surfaced verbatim.
        """
        result = self.run(*parts, "-f", "json", timeout=timeout, browser_timeout=browser_timeout)
        stdout = (result.stdout or "").strip()
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as error:
            detail = stdout or (result.stderr or "").strip()
            raise OpenCliUnavailable(
                f"opencli {' '.join(parts[:3])} did not return JSON: {detail[:400]}"
            ) from error


def _iter_candidate_nodes() -> list[Path]:
    """Yield plausible Node installation roots, most specific first."""
    roots: list[Path] = []
    override = os.environ.get("OPENCLI_HOME")
    if override:
        roots.append(Path(override))
    roots.extend(_NODE_HINTS)

    # Also consider the directory of any `node` already on PATH.
    node_on_path = shutil.which("node")
    if node_on_path:
        roots.append(Path(node_on_path).parent)

    expanded: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        expanded.append(root)
        # One level down catches `~/nodejs/node-v24.18.0-win-x64`.
        expanded.extend(child for child in root.iterdir() if child.is_dir())
    return expanded


@lru_cache(maxsize=1)
def resolve_runtime() -> OpenCliRuntime:
    """Find a working ``(node, main.js)`` pair, or raise :class:`OpenCliUnavailable`.

    Set ``OPENCLI_NODE`` and ``OPENCLI_MAIN`` to bypass discovery entirely.
    """
    node_override = os.environ.get("OPENCLI_NODE")
    main_override = os.environ.get("OPENCLI_MAIN")
    if node_override and main_override:
        node, main = Path(node_override), Path(main_override)
        if node.is_file() and main.is_file():
            return OpenCliRuntime(node=node, main=main)
        raise OpenCliUnavailable(
            f"OPENCLI_NODE/OPENCLI_MAIN point at missing files: {node}, {main}"
        )

    searched: list[str] = []
    for root in _iter_candidate_nodes():
        main = root / _MAIN_REL
        if not main.is_file():
            searched.append(str(root))
            continue
        node = root / "node.exe"
        if not node.is_file():
            fallback = shutil.which("node")
            if not fallback:
                searched.append(f"{root} (main.js found, node.exe missing)")
                continue
            node = Path(fallback)
        return OpenCliRuntime(node=node, main=main)

    raise OpenCliUnavailable(
        "OpenCLI entry point not found. Searched: "
        + (", ".join(searched[:8]) or "<no candidate node roots>")
        + ". Set OPENCLI_NODE and OPENCLI_MAIN to override."
    )


def is_available() -> bool:
    """Return True when OpenCLI can be invoked (does not check the daemon)."""
    try:
        resolve_runtime()
    except OpenCliUnavailable:
        return False
    return True


def check_bridge(timeout: int = 60) -> dict[str, object]:
    """Run ``opencli doctor`` and summarise daemon/extension connectivity."""
    runtime = resolve_runtime()
    result = runtime.run("doctor", timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    return {
        "ok": result.returncode == 0 and "[OK] Daemon" in output,
        "daemon": "[OK] Daemon" in output,
        "extension": "[OK] Extension" in output,
        "output": output.strip()[:1000],
    }


def whoami(site: str, timeout: int = 120) -> dict[str, object]:
    """Return the login state for an OpenCLI site adapter (e.g. ``xiaohongshu``)."""
    runtime = resolve_runtime()
    try:
        payload = runtime.run_json(site, "whoami", "--window", "background", timeout=timeout)
    except OpenCliUnavailable as error:
        return {"logged_in": False, "site": site, "error": str(error)}
    if isinstance(payload, dict):
        return payload
    return {"logged_in": False, "site": site, "error": "unexpected whoami payload"}


#: A cheap authenticated read per site, used instead of ``whoami`` as the gate.
#:
#: ``xiaohongshu whoami`` renders the creator profile page, which intermittently
#: stalls ``Runtime.evaluate`` ("blocked by a native dialog") even when the
#: session is perfectly valid -- ``drafts`` on the same session returns instantly.
#: Gating delivery on ``whoami`` therefore produces false negatives.
_LOGIN_PROBES: dict[str, tuple[str, ...]] = {
    "xiaohongshu": ("xiaohongshu", "drafts"),
    "weixin": ("weixin", "drafts"),
}


def probe_login(site: str, timeout: int = 240) -> dict[str, object]:
    """Confirm a site session is usable by performing a real authenticated read.

    Returns ``{"logged_in": bool, "site": str, ...}``.  ``AUTH_REQUIRED`` in the
    OpenCLI error envelope is reported as a clean logged-out state; anything
    else is surfaced verbatim so genuine breakage is not mistaken for logout.
    """
    probe = _LOGIN_PROBES.get(site)
    if probe is None:
        return whoami(site, timeout=timeout)

    try:
        runtime = resolve_runtime()
    except OpenCliUnavailable as error:
        return {"logged_in": False, "site": site, "error": str(error)}

    result = runtime.run(*probe, "--window", "background", "-f", "json", timeout=timeout)
    stdout = (result.stdout or "").strip()
    if result.returncode == 0 and stdout.startswith(("[", "{")):
        return {"logged_in": True, "site": site, "probe": " ".join(probe)}
    detail = (stdout or result.stderr or "").strip()
    if "AUTH_REQUIRED" in detail:
        return {"logged_in": False, "site": site, "error_code": "AUTH_REQUIRED", "error": detail[:300]}
    return {"logged_in": False, "site": site, "error": detail[:300]}
