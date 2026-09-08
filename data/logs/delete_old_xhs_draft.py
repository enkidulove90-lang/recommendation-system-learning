"""Delete an old XHS draft from the box via OpenCliXiaohongshuDelivery."""
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(".").resolve()))

from redbook.infrastructure.xiaohongshu_delivery import OpenCliXiaohongshuDelivery

OLD_DRAFT_ID = "s:387d66f3-711d-4c5f-a8ae-f5bab4b6bd95"

delivery = OpenCliXiaohongshuDelivery()
try:
    delivery._delete(OLD_DRAFT_ID)
    print(f"deleted draft {OLD_DRAFT_ID}")
except Exception as e:
    print(f"DELETE ERROR: {type(e).__name__}: {e}")
    sys.exit(1)
