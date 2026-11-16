"""Shared pytest configuration for the ada platform.

The Windows sandbox in this environment forbids recursive directory deletion
(recycle-bin shim), which breaks pytest's built-in ``tmp_path`` cleanup.  We
override ``tmp_path`` with a create-only unique directory under
``baseline/ada/.tmp/``; stale dirs are ignored via .gitignore and can be
removed manually outside the sandbox.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

BASELINE_ADA = Path(__file__).resolve().parent.parent
CORE_DIR = BASELINE_ADA / "core"
SCRIPTS_DIR = BASELINE_ADA / "scripts"
BACKEND_DIR = BASELINE_ADA / "backend"

for p in (CORE_DIR, SCRIPTS_DIR, BACKEND_DIR, str(BASELINE_ADA)):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


@pytest.fixture
def tmp_path() -> Path:
    root = BASELINE_ADA / ".tmp" / "pytest" / uuid.uuid4().hex[:12]
    root.mkdir(parents=True, exist_ok=True)
    return root
