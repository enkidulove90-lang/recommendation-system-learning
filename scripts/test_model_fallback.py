"""Test SHUSHENG Agents-A1 -> DeepSeek fallback mechanism."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI
from config import settings
from paper_intake.fact_pack import (
    FACT_PACK_PROMPT_VERSION,
    build_fact_pack_prompt,
    parse_fact_pack_response,
)
from paper_intake.model_gateway import ModelCallGatewayWithFallback
from paper_intake.asset_manifest import ContentAssetManifest
from paper_intake.catalog_store import CatalogRepository

DEFAULT_DB = ROOT / "data" / "paper_catalog" / "catalog.sqlite3"

def test_agents_a1_direct() -> Optional[str]:
    """Test direct Agents-A1 call."""
    if not settings.SHUSHENG_API_KEY:
        return "SHUSHENG_API_KEY not configured"

    client = OpenAI(
        api_key=settings.SHUSHENG_API_KEY,
        base_url=settings.SHUSHENG_API_BASE
    )
    try:
        response = client.chat.completions.create(
            model=settings.SHUSHENG_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please respond with a single word: OK"},
            ],
            temperature=0.1,
            max_tokens=10,
        )
        return f"✅ Agents-A1 works: {response.choices[0].message.content.strip()}"
    except Exception as e:
        return f"❌ Agents-A1 error: {e}"

def test_deepseek_direct() -> Optional[str]:
    """Test direct DeepSeek call."""
    if not settings.DEEPSEEK_API_KEY:
        return "DEEPSEEK_API_KEY not configured"

    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    try:
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please respond with a single word: OK"},
            ],
            temperature=0.1,
            max_tokens=10,
        )
        return f"✅ DeepSeek works: {response.choices[0].message.content.strip()}"
    except Exception as e:
        return f"❌ DeepSeek error: {e}"

def test_fallback_mechanism_with_dataframe():
    """Test the fallback mechanism using a test message that produces structured output."""
    # Create a minimal test markdown file that includes a simple table
    test_markdown = ROOT / "data" / "test_agents_a1.md"
    test_markdown.write_text(
        """# Test Paper

Authors: From Agents-A1 team

## Abstract
This paper proposes a novel method that outperforms others on standard benchmarks.

## Table: Results
| Method | Accuracy | F1 Score |
|--------|----------|----------|
| Our   | 0.85     | 0.82     |
| Baseline | 0.78   | 0.75     |

## Conclusion
The method is effective."""
    )

    try:
        repository = CatalogRepository(DEFAULT_DB)
        repository.close()
        manifest = ContentAssetManifest(DEFAULT_DB)

        gateway = ModelCallGatewayWithFallback(
            manifest, ROOT, use_shusheng_cache=True)

        print("\n=== Testing Agents-A1 -> DeepSeek Fallback ===\n")
        print("1. Attempting to generate fact_pack with fallback mechanism...")

        # Test with enabled SHUSHENG and forced to allow fallback
        result_path = gateway.ensure(
            canonical_id="test:agentsa1-2026",
            purpose="fact_pack",
            source=test_markdown,
            prompt_version=FACT_PACK_PROMPT_VERSION,
            model_id=settings.SHUSHENG_MODEL,
            build_prompt=build_fact_pack_prompt,
            parse_response=lambda raw: parse_fact_pack_response(raw, "test:agentsa1-2026"),
            use_shusheng_first=True,
        )

        print(f"2. FactPack generated successfully at: {result_path.relative_to(ROOT)}")
        print("3. Key outputs from Agents-A1 (or fallback):")

        import json
        content = json.loads(result_path.read_text(encoding="utf-8"))
        facts = content.get("facts", {})
        print(f"   - one_line: {facts.get('one_line', 'N/A')}")
        print(f"   - method: {facts.get('method', 'N/A')}")
        print(f"   - table interpretation: {facts.get('experiments', ['N/A'])[0] if facts.get('experiments') else 'N/A'}")
        print(f"   - model_id used: {content.get('model_id', 'N/A')}")

        print("\n✅ Agents-A1 fallback test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Fallback test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if test_markdown.exists():
            test_markdown.unlink()

def main():
    import sys
    parser = argparse.ArgumentParser(description="Test Agents-A1 -> DeepSeek fallback")
    parser.add_argument("--test-agents", action="store_true", help="Test direct Agents-A1 API call")
    parser.add_argument("--test-deepseek", action="store_true", help="Test direct DeepSeek API call")
    parser.add_argument("--test-fallback", action="store_true", help="Test full fallback mechanism")
    args = parser.parse_args()

    print(f"Current default SHUSHENG_MODEL: {settings.SHUSHENG_MODEL}")
    print(f"SHUSHENG_API_BASE: {settings.SHUSHENG_API_BASE}")
    print()

    if args.test_agents:
        print("=== Testing Direct Agents-A1 Call ===\n")
        result = test_agents_a1_direct()
        print(result + "\n")

    if args.test_deepseek:
        print("=== Testing Direct DeepSeek Call ===\n")
        result = test_deepseek_direct()
        print(result + "\n")

    if args.test_fallback:
        print("=== Testing Full Fallback Mechanism ===\n")
        success = test_fallback_mechanism_with_dataframe()
        if success:
            print("\n✅ All tests PASSED")
        else:
            print("\n❌ All tests FAILED")
            sys.exit(1)

if __name__ == "__main__":
    raise SystemExit(main())
