"""Local Delivery Simulator: emulate Xiaohongshu/WeChat delivery responses.

This simulator produces deterministic receipts without touching real platforms.
It is used for end-to-end validation during development and testing.

Rules:
- Xiaohongshu: simulated draft_id must be stable for same input
- WeChat: simulated draft_id should be based on content hash
- All simulated receipts are JSON-serializable
"""
from pathlib import Path
from typing import Optional
import json


class LocalDeliverySimulator:
    """Simulate platform delivery without network access."""

    def __init__(self, dry_run: bool = True, simulate_success: bool = True):
        self.dry_run = dry_run
        self.simulate_success = simulate_success

    # === 小红书模拟 ===
    def simulate_xhs_delivery(self, note_yaml: Path, input_data: dict) -> dict:
        """Simulate Xiaohongshu delivery.

        Returns:
            {
                "compiled": True,
                "compiled_path": str(note_yaml),
                "staged": True,  # if simulation indicates staged state
                "staged_id": str,  # staged hash or file path
                "drafted": False,  # only true if mock platform says so
                "draft_id": Optional[str],
                "reopened_verified": False,
                "reopened_url": Optional[str],
                "title_verified": bool,
                "body_verified": bool,
                "cover_verified": bool,
                "pdf_verified": bool,
                "topics_verified": bool,
                "reason": str if error else "",
            }
        """
        result = {
            "compiled": True,
            "compiled_path": str(note_yaml),
            "staged": self.simulate_success and not self.dry_run,
            "staged_id": f"xhs-staged-{input_data.get('paper_id', 'unknown')}",
            "drafted": False,
            "draft_id": None,
            "reopened_verified": False,
            "reopened_url": None,
            "title_verified": True,
            "body_verified": True,
            "cover_verified": True,
            "pdf_verified": True,
            "topics_verified": True,
            "reason": "",
        }

        if self.dry_run:
            result["reason"] = "dry_run: no real delivery"
            return result

        if not self.simulate_success:
            result["reason"] = "SIMULATED_FAILURE"
            return result

        # === 模拟成功交付 ===
        # 生成稳定的 draft_id
        paper_id = input_data.get("paper_id", "unknown")
        draft_id = f"xhs-draft-{paper_id}-{self.simulate_success}"
        result["drafted"] = True
        result["draft_id"] = draft_id

        # 模拟重开验证通过
        result["reopened_verified"] = True
        result["reopened_url"] = f"https://www.xiaohongshu.com/discovery/item/{paper_id}"

        return result

    # === 微信公众号模拟 ===
    def simulate_wechat_delivery(self, wechat_package: Path, input_data: dict) -> dict:
        """Simulate WeChat Official Account delivery.

        Returns:
            {
                "compiled": True,
                "compiled_path": str(wechat_package),
                "staged": True,
                "staged_id": str,  # staged hash
                "drafted": False,  # only if mock platform says so
                "draft_id": Optional[str],
                "reopened_verified": False,
                "reopened_url": Optional[str],
                "title_verified": bool,
                "body_verified": bool,
                "cover_verified": bool,
                "reason": str if error else "",
            }
        """
        result = {
            "compiled": True,
            "compiled_path": str(wechat_package),
            "staged": self.simulate_success and not self.dry_run,
            "staged_id": f"wechat-staged-{input_data.get('paper_id', 'unknown')}",
            "drafted": False,
            "draft_id": None,
            "reopened_verified": False,
            "reopened_url": None,
            "title_verified": True,
            "body_verified": True,
            "cover_verified": True,
            "reason": "",
        }

        if self.dry_run:
            result["reason"] = "dry_run: no real delivery"
            return result

        if not self.simulate_success:
            result["reason"] = "SIMULATED_FAILURE"
            return result

        # === 模拟成功交付 ===
        paper_id = input_data.get("paper_id", "unknown")
        draft_id = f"wechat-draft-{paper_id}-{self.simulate_success}"
        result["drafted"] = True
        result["draft_id"] = draft_id

        # === 模拟重开验证 ===
        # 需要从 wechat_package 中读取 title, body, cover 图
        package_data = json.loads(wechat_package.read_text(encoding="utf-8"))
        # 模拟 title 和正文验证
        title = package_data.get("title", "")
        body = package_data.get("body_markdown", "")
        cover = package_data.get("metadata", {}).get("cover_image", "")

        # 重开验证检查标题、正文、封面
        title_verified = bool(title)
        body_verified = bool(body)
        cover_verified = bool(cover)

        result["reopened_verified"] = title_verified and body_verified and cover_verified
        if result["reopened_verified"]:
            # 生成模拟的重开 URL
            result["reopened_url"] = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=appmsg_edit&draft_id={draft_id}"

        return result

    # === Notion 模拟 ===
    def simulate_notion_delivery(self, canonical_id: str, input_data: dict) -> dict:
        """Simulate Notion delivery.

        Notion 目前禁止写入，返回 blocked.
        """
        return {
            "compiled": False,
            "staged": False,
            "drafted": False,
            "draft_id": None,
            "reopened_verified": False,
            "reopened_url": None,
            "title_verified": False,
            "body_verified": False,
            "reason": "Notion integration not implemented; requires explicit NOTION_WRITE_AUTH",
        }

    def simulate_end_to_end(self, canonical_id: str, fact_pack_path: Path, parsed_dir: Path, pdf_path: Path | None) -> dict:
        """Simulate full end-to-end flow for one paper."""
        # 加载 fact_pack
        with open(fact_pack_path, "r", encoding="utf-8") as f:
            fact_pack = json.load(f)

        paper_id = canonical_id.rsplit(":", 1)[-1]

        # 模拟小红书
        note_yaml = Path(f"redbook/notes/{paper_id}.yaml")
        xhs_receipt = self.simulate_xhs_delivery(note_yaml, {
            "paper_id": paper_id,
            "fact_pack": fact_pack,
        })

        # 模拟微信公众号
        wechat_package = Path(f"publish_queue/{paper_id}/wechat.json")
        wechat_receipt = self.simulate_wechat_delivery(wechat_package, {
            "paper_id": paper_id,
            "fact_pack": fact_pack,
        })

        # 模拟 Notion
        notion_receipt = self.simulate_notion_delivery(canonical_id, {
            "paper_id": paper_id,
            "fact_pack": fact_pack,
        })

        return {
            "canonical_id": canonical_id,
            "platforms": {
                "xhs": xhs_receipt,
                "wechat": wechat_receipt,
                "notion": notion_receipt,
            },
            "summary": {
                "all_platforms_ok": (
                    xhs_receipt["compiling"] and xhs_receipt["reopened_verified"]
                    and wechat_receipt["compiled"] and wechat_receipt["reopened_verified"]
                ),
                "xhs": "ready" if xhs_receipt["reopened_verified"] else "blocked",
                "wechat": "ready" if wechat_receipt["reopened_verified"] else "blocked",
                "notion": "blocked" if self.dry_run or not self.simulate_success else "ready",
            },
        }
