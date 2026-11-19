from __future__ import annotations

import subprocess
import sys

import json
import pytest

import redbook.cli as cli
from redbook.infrastructure.delivery_errors import DeliveryError, E_AUTH


def test_note_help_exposes_draft_only_save_alias() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "redbook.cli", "note", "--help"],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert "--save-draft" in result.stdout
    assert "--publish" in result.stdout
    assert "deprecated alias of --save-draft" in result.stdout
    assert "never publishes publicly" in result.stdout


def test_note_help_exposes_read_only_verify() -> None:
    result = subprocess.run([sys.executable, "-m", "redbook.cli", "note", "--help"], text=True, capture_output=True)
    assert result.returncode == 0
    assert "--verify" in result.stdout
    assert "--draft-id" in result.stdout


def test_save_xhs_draft_emits_retryable_error_envelope(monkeypatch, tmp_path, capsys) -> None:
    draft = tmp_path / "draft.json"
    image = tmp_path / "figure.png"
    pdf = tmp_path / "paper.pdf"
    draft.write_text(json.dumps({"title": "title", "body": "body", "topics": ["AI"]}), encoding="utf-8")
    image.write_bytes(b"png")
    pdf.write_bytes(b"%PDF-")
    monkeypatch.setattr(
        cli.OpenCliXiaohongshuDelivery, "deliver",
        lambda *_: (_ for _ in ()).throw(DeliveryError("login expired", E_AUTH)),
    )
    monkeypatch.setattr(sys, "argv", [
        "redbook.cli", "save-xhs-draft", "--draft", str(draft), "--image", str(image), "--pdf", str(pdf),
    ])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 3
    result = json.loads(capsys.readouterr().out)
    assert result["code"] == E_AUTH
    assert result["retryable"] is True
    assert result["owner"] == "human"


def test_note_save_draft_maps_result_error_code_to_retryable_envelope(monkeypatch, capsys) -> None:
    class FailedWorkflow:
        def __init__(self, *_args) -> None:
            pass

        def publish_note(self, *_args, **_kwargs):
            return {"ok": False, "error": "login expired", "error_code": E_AUTH}

    monkeypatch.setattr(cli, "PaperCreationWorkflow", FailedWorkflow)
    monkeypatch.setattr(sys, "argv", ["redbook.cli", "note", "paper", "--save-draft"])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 3
    result = json.loads(capsys.readouterr().out)
    assert result["code"] == E_AUTH
    assert result["retryable"] is True
