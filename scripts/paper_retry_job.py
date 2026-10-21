from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_intake.control_client import ControlPlaneClient, load_or_create_operation_key
from scripts.paper_intake_diagnose import config


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely retry one paper job with persistent idempotency")
    parser.add_argument("job_id")
    args = parser.parse_args()
    values = config()
    key_path = ROOT / ".paper-work" / "retry-operations" / f"{args.job_id}.key"
    operation_key = load_or_create_operation_key(key_path)
    client = ControlPlaneClient(
        values["PAPER_INTAKE_API_BASE"],
        values["PAPER_INTAKE_WORKER_TOKEN"],
        network_mode=os.getenv("PAPER_INTAKE_NETWORK_MODE", "direct"),
        proxy_url=os.getenv("PAPER_INTAKE_PROXY_URL", ""),
    )
    result = client.retry_job(args.job_id, operation_key)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
