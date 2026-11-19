from __future__ import annotations

import subprocess

import pytest

from redbook.infrastructure.opencli_runtime import OpenCliClient


class FakeRuntime:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.calls: list[tuple[str, ...]] = []

    def run(self, *parts: str, **_kwargs):
        self.calls.append(parts)
        return subprocess.CompletedProcess(parts, self.returncode, self.stdout, "bridge failed")


def test_client_unwraps_opencli_v2_data_envelope() -> None:
    client = OpenCliClient(FakeRuntime('{"ok":true,"data":[{"id":"s:1"}]}'))
    assert client.run_json("xiaohongshu", "drafts") == [{"id": "s:1"}]


def test_client_maps_failed_envelope_to_structured_error() -> None:
    client = OpenCliClient(FakeRuntime('{"ok":false,"error":{"message":"extension stale"}}'))
    with pytest.raises(Exception) as error:
        client.run_json("xiaohongshu", "drafts")
    assert getattr(error.value, "code", None) == "E_RESPONSE_SHAPE"


def test_client_parses_doctor_version_and_outdated_flag() -> None:
    client = OpenCliClient(FakeRuntime(
        '{"ok":true,"data":{"daemonRunning":true,"extensionConnected":true,'
        '"extensionVersion":"1.0.25","extensionOutdated":true}}'
    ))
    assert client.doctor()["extension_outdated"] is True
