"""声明式制卡与 MCP note tools 的回归测试。"""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from redbook.mcp import server as mcp_server
from redbook.services.cards import NumberCardSpec, render_card_from_mapping, render_number_card, upscale_image


def test_number_card_from_mapping_and_render(tmp_path):
    data = {
        "title": "同一个骨架，只换优化器",
        "subtitle": "Amazon 三个类目 · 数据来源：论文 Table 1",
        "columns": ["Beauty", "Sports", "Toys"],
        "rows": [
            {"label": "冷启动召回@10", "hint": "越高越好",
             "cells": [["0.326 → 0.619", "+89.9%"], ["0.282 → 0.567", "+101%"], ["0.365 → 0.705", "+93.2%"]]},
            {"label": "精度 NDCG@10", "hint": "持平微升",
             "cells": [["0.0550 → 0.0557", "+1.3%"], ["0.0317 → 0.0320", "+1.0%"], ["0.0581 → 0.0585", "+0.7%"]]},
        ],
        "footnotes": ["换成原生文本动作空间后精度再上一层", "消融结论见论文 Figure 5"],
    }
    output = tmp_path / "card.png"
    result = render_card_from_mapping(data, output)
    assert result["ok"] is True
    assert result["rows"] == 2 and result["columns"] == 3
    assert output.is_file() and output.stat().st_size > 1000
    with Image.open(output) as image:
        assert image.size == tuple(result["size"])
        assert image.getpixel((10, 7))[0] != 250  # 顶部蓝色条已绘制


def test_number_card_rejects_mismatched_columns(tmp_path):
    spec = NumberCardSpec.from_mapping({
        "title": "x", "subtitle": "", "columns": ["A", "B"],
        "rows": [{"label": "row", "cells": [["1", "+1%"]]}],
    })
    result = render_number_card(spec, tmp_path / "bad.png")
    assert result["ok"] is False
    assert not (tmp_path / "bad.png").exists()


def test_upscale_image(tmp_path):
    source = tmp_path / "small.png"
    Image.new("RGB", (100, 60), (200, 210, 220)).save(source)
    result = upscale_image(source, tmp_path / "large.png", factor=1.8)
    assert result["ok"] is True
    assert result["size"] == [180, 108]


def test_mcp_tools_list_includes_note_tools():
    names = {tool["name"] for tool in mcp_server.TOOLS}
    assert {"list_note_specs", "validate_note_spec", "stage_note_spec"} <= names
    assert "publish_note_spec" not in names
    response = mcp_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert len(response["result"]["tools"]) == len(mcp_server.TOOLS)


def test_mcp_list_and_validate_note_specs():
    listed = mcp_server.call_tool("list_note_specs", {})
    assert listed["ok"] is True
    assert len(listed["notes"]) == 14
    validated = mcp_server.call_tool("validate_note_spec", {"slug": "2601.21452"})
    assert validated["ok"] is True, validated
    assert validated["body_chars"] == 999
    missing = mcp_server.call_tool("validate_note_spec", {})
    assert missing["ok"] is False and "slug is required" in missing["error"]


def test_mcp_stage_refuses_published_archive(tmp_path):
    """历史已发布稿的回溯目检标记不能让 MCP 误重发。"""
    result = mcp_server.call_tool("stage_note_spec", {
        "slug": "2609.05339", "data_root": str(tmp_path / "queue"),
    })
    assert result["ok"] is False
    assert any("archived" in error for error in result["errors"])
