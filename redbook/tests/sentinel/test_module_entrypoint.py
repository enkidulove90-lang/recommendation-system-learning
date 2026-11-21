from __future__ import annotations

import runpy
import sys

import pytest


def test_module_entrypoint_forwards_to_sentinel_cli(monkeypatch):
    captured: dict[str, list[str]] = {}

    def fake_main() -> None:
        captured["argv"] = list(sys.argv)

    monkeypatch.setattr("redbook.cli.main", fake_main)
    monkeypatch.setattr(
        sys, "argv",
        ["redbook.sentinel", "run-once", "--platform", "homepage", "--no-dispatch"],
    )

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("redbook.sentinel.__main__", run_name="__main__")

    assert exit_info.value.code is None
    assert captured["argv"] == [
        "redbook.cli", "sentinel", "run-once", "--platform", "homepage", "--no-dispatch",
    ]
