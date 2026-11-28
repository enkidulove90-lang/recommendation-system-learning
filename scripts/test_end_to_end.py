"""End-to-End Test Script for Paper Distribution Pipeline.

This script tests the complete flow:
1. Generate fact_pack from a test paper
2. Compile platform packages
3. Simulate delivery and collect receipts
4. Verify that all states are correctly reported
"""
from pathlib import Path
import json
import sys
import tempfile
import shutil

# Add root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.end_to_end_bridge import E2EResult, run_end_to_end
from scripts.local_delivery_simulator import LocalDeliverySimulator


def test_end_to_end_with_simulator(
    canonical_id: str,
    fact_pack_path: Path,
    parsed_dir: Path,
    pdf_path: Path | None,
    dry_run: bool = True,
    simulate_success: bool = True,
) -> E2EResult:
    """Run end-to-end flow with local delivery simulator."""

    # First run the bridge to compile platforms
    result = run_end_to_end(
        canonical_id=canonical_id,
        fact_pack_path=fact_pack_path,
        parsed_dir=parsed_dir,
        pdf_path=pdf_path,
    )

    # Then simulate delivery for each platform
    simulator = LocalDeliverySimulator(dry_run=dry_run, simulate_success=simulate_success)

    paper_id = canonical_id.rsplit(":", 1)[-1]

    # Simulate WeChat delivery if compiled
    if result.platforms["wechat"].compiled and result.platforms["wechat"].compiled_path:
        # We need to read the actual JSON package
        with open(result.platforms["wechat"].compiled_path, "r", encoding="utf-8") as f:
            wechat_package = json.load(f)
        wechat_receipt = simulator.simulate_wechat_delivery(
            Path(result.platforms["wechat"].compiled_path),
            {
                "paper_id": paper_id,
                "fact_pack": wechat_package,
            }
        )
        result.platforms["wechat"].drafted = wechat_receipt["drafted"]
        result.platforms["wechat"].draft_id = wechat_receipt["draft_id"]
        result.platforms["wechat"].reopened_verified = wechat_receipt["reopened_verified"]
        result.platforms["wechat"].reopened_url = wechat_receipt["reopened_url"]

    # Simulate Notion delivery
    notion_receipt = simulator.simulate_notion_delivery(canonical_id, {})
    result.platforms["notion"].compiled = notion_receipt.get("compiled", False)
    result.platforms["notion"].drafted = notion_receipt.get("drafted", False)
    result.platforms["notion"].draft_id = notion_receipt.get("draft_id")
    result.platforms["notion"].reopened_verified = notion_receipt.get("reopened_verified", False)

    return result


def run_all_tests():
    """Run a comprehensive test suite."""

    # Define test data paths first
    test_canonical_id = "test:echo_mllm"
    test_fact_pack = ROOT / "data" / "summaries" / "echo_mllm_summary.json"
    test_parsed_dir = ROOT / "data" / "parsed" / "EchoMLLM"
    test_pdf = ROOT / "data" / "papers" / "echo_mllm.pdf"

    # Always ensure basic parsed data structure exists
    print(f"Ensuring minimal parsed data at {test_parsed_dir}...")
    images_dir = test_parsed_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    manifest = [
        {"path": "images/fig1.png", "type": "architecture", "caption": "图1：整体架构", "figure_id": "1"},
        {"path": "images/fig2.png", "type": "result", "caption": "图2：实验结果", "figure_id": "2"},
    ]
    with open(test_parsed_dir / "figure_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    img1 = images_dir / "fig1.png"
    img2 = images_dir / "fig2.png"
    if not img1.exists():
        img1.write_bytes(b"")
    if not img2.exists():
        img2.write_bytes(b"")

    # Synthetic fact pack if missing
    if not test_fact_pack.exists():
        print(f"Creating synthetic fact pack: {test_fact_pack}")
        # Create synthetic test data
        synthetic_fact_pack = {
            "schema_version": "fact-pack/v2",
            "canonical_id": str(test_canonical_id),
            "source_hash": "abc123",
            "model_id": "test-model",
            "prompt_version": "fact-pack-2.1",
            "facts": {
                "one_line": "EchoMLLM: A multimodal language model for recommendation systems",
                "problem": "Current multimodal recommendation systems lack efficient visual extraction",
                "method": "A novel encoder-decoder architecture for cross-modal alignment",
                "experiments": [
                    "ImageNet: ACC=75.2% top-1",
                    "RecSys: NDCG@10=0.45"
                ],
                "novelty": "Introduces a new cross-modal attention mechanism",
                "takeaway": "Cross-modal models can improve recommendation accuracy",
                "code_url": "https://github.com/echo-mllm/echo-mllm",
                "paper_link": "https://arxiv.org/abs/2410.07761",
                "pdf_link": "https://arxiv.org/pdf/2410.07761.pdf",
                "venue_name": "arXiv",
                "year": "2024",
                "authors": [
                    {"name": "Author One", "affiliations": [{"institution": "University A"}]}
                ],
                "source": "arxiv",
                "verification_status": "verified"
            },
            "platform_hints": {
                "xhs": {"hook": "Cross-modal recommendation", "topic_candidates": ["论文分享"]},
                "wechat": {"lead": "跨模态推荐新进展"},
                "homepage": {"summary_1line": "EchoMLLM introduces cross-modal recommendation"},
            },
            "xhs_draft": {
                "title_literary": "2026 | EchoMLLM: 跨模态推荐的视觉之翼",
                "title_question": "如何让推荐系统看懂图片？",
                "opening": "Visual modality breakthrough: EchoMLLM——EchoMLLM论文导读",
                "pain_point": "核心痛点：现有推荐模型难以有效提取视觉特征",
                "seed": 42,
                "sections": {
                    "contribution": "① 首次提出跨模态注意力机制\n② 在ImageNet上达到75.2% accuracy\n③ 在RecSys任务上NDCG@10提升5.2%",
                    "method": "① 特征提取器：ResNet-101编码器\n② 对齐模块：跨模态自注意力\n③ 解码器：多任务学习",
                    "experiment": "数据集：ImageNet + Amazon\n算力：8xV100 GPUs\n指标：Accuracy, NDCG@10",
                    "result": "在ImageNet上达到75.2% top-1 accuracy。在RecSys任务上，NDCG@10从0.39提升至0.45，F1提升8.1%。",
                },
                "topics": ["论文分享", "人工智能", "推荐系统"],
                "figure_intents": [
                    {"order": 1, "intent": "overview", "description": "图1：EchoMLLM 整体架构"},
                    {"order": 2, "intent": "architecture", "description": "图2：跨模态注意力模块细节"},
                ]
            },
            "wechat_draft": {
                "lead": "深度学习领域，跨模态推荐是新的研究方向",
                "body": "长文章正文，包含多个段落和图表引用...",
            },
            "homepage_draft": {
                "summary_1line": "EchoMLLM 是一个跨模态推荐系统模型",
                "summary_para": "本文介绍了 EchoMLLM 模型，它解决了跨模态信息对齐的问题...",
            },
        }
        test_fact_pack.parent.mkdir(parents=True, exist_ok=True)
        test_fact_pack.write_text(json.dumps(synthetic_fact_pack, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Created synthetic fact pack: {test_fact_pack}")

    if not test_parsed_dir.exists():
        print(f"Creating minimal test parsed data: {test_parsed_dir}")
        images_dir = test_parsed_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        # Create a synthetic figure_manifest.json with correct 'path' format
        manifest = [
            {"path": "images/fig1.png", "type": "architecture", "caption": "图1：整体架构", "figure_id": "1"},
            {"path": "images/fig2.png", "type": "result", "caption": "图2：实验结果", "figure_id": "2"},
        ]
        with open(test_parsed_dir / "figure_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        # Create empty placeholder images (binary)
        (images_dir / "fig1.png").write_bytes(b"")
        (images_dir / "fig2.png").write_bytes(b"")

    result1 = test_end_to_end_with_simulator(
        canonical_id=test_canonical_id,
        fact_pack_path=test_fact_pack,
        parsed_dir=test_parsed_dir,
        pdf_path=None,
        dry_run=True,
        simulate_success=True,
    )

    print("Result for dry run:", result1.to_dict())

    # Check assertions
    assert result1.platforms["xhs"].compiled == True, "XHS should compile in dry run"
    assert result1.platforms["wechat"].compiled == True, "WeChat should compile in dry run"
    assert result1.platforms["notion"].compiled == False, "Notion should not compile"
    assert result1.platforms["xhs"].drafted == False, "XHS should not be drafted in dry run"
    assert result1.platforms["wechat"].drafted == False, "WeChat should not be drafted in dry run"
    assert result1.platforms["xhs"].reopened_verified == False, "XHS should not be verified in dry run"
    print("✓ TEST 1 PASSED: Dry run correctly does not mark drafted/verified")

    print("\n" + "=" * 60)
    print("TEST 2: Simulated delivery (success)")
    print("=" * 60)

    result2 = test_end_to_end_with_simulator(
        canonical_id=test_canonical_id,
        fact_pack_path=test_fact_pack,
        parsed_dir=test_parsed_dir,
        pdf_path=None,
        dry_run=False,  # Not dry run
        simulate_success=True,  # Success
    )

    print("Result for success simulation:", result2.to_dict())

    # Check assertions
    assert result2.platforms["xhs"].drafted == True, "XHS should be drafted in success simulation"
    assert result2.platforms["wechat"].drafted == True, "WeChat should be drafted in success simulation"
    assert result2.platforms["xhs"].reopened_verified == True, "XHS should be reopened_verified in success simulation"
    assert result2.platforms["wechat"].reopened_verified == True, "WeChat should be reopened_verified in success simulation"
    print("✓ TEST 2 PASSED: Success simulation correctly marks drafted and reopened_verified")

    print("\n" + "=" * 60)
    print("TEST 3: Simulated delivery (failure)")
    print("=" * 60)

    result3 = test_end_to_end_with_simulator(
        canonical_id=test_canonical_id,
        fact_pack_path=test_fact_pack,
        parsed_dir=test_parsed_dir,
        pdf_path=None,
        dry_run=False,
        simulate_success=False,  # Failure
    )

    print("Result for failure simulation:", result3.to_dict())

    # Check assertions
    assert result3.platforms["xhs"].drafted == False, "XHS should not be drafted in failure simulation"
    assert result3.platforms["wechat"].drafted == False, "WeChat should not be drafted in failure simulation"
    assert result3.platforms["xhs"].reopened_verified == False, "XHS should not be reopened_verified in failure simulation"
    print("✓ TEST 3 PASSED: Failure simulation correctly does not mark drafted/verified")

    print("\n" + "=" * 60)
    print("TEST 4: Verify platform receipts are independent")
    print("=" * 60)

    result4 = test_end_to_end_with_simulator(
        canonical_id=test_canonical_id,
        fact_pack_path=test_fact_pack,
        parsed_dir=test_parsed_dir,
        pdf_path=None,
        dry_run=False,
        simulate_success=True,
    )

    # Check that each platform reports independent receipts
    assert result4.platforms["xhs"]["compiled_path"] is not None, "XHS compiled path should exist"
    assert result4.platforms["wechat"]["compiled_path"] is not None, "WeChat compiled path should exist"
    assert result4.platforms["xhs"] != result4.platforms["wechat"], "XHS and WeChat results should be separate"
    print("✓ TEST 4 PASSED: Platform receipts are independent")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)

    return result1, result2, result3, result4


if __name__ == "__main__":
    results = run_all_tests()
    for i, r in enumerate(results, 1):
        print(f"\n{'='*60}")
        print(f"Results from Test {i}:")
        print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
