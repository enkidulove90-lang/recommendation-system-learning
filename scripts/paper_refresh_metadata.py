from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paper_intake.remote import RemoteGatewayClient


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Queue a metadata-only refresh for one published paper job."
    )
    parser.add_argument("job_id")
    parser.add_argument("--operation-key", default="")
    parser.add_argument("--status", action="store_true", help="Only query --operation-key.")
    args = parser.parse_args()

    project_root = PROJECT_ROOT
    load_dotenv(project_root / ".env", override=False)
    base_url = os.getenv("PAPER_INTAKE_API_BASE", "").strip()
    token = os.getenv("PAPER_INTAKE_WORKER_TOKEN", "").strip()
    if not base_url or not token:
        parser.error("PAPER_INTAKE_API_BASE and PAPER_INTAKE_WORKER_TOKEN are required")

    operation_root = project_root / ".paper-work" / "metadata-refresh-operations"
    operation_root.mkdir(parents=True, exist_ok=True)
    key_path = operation_root / f"{args.job_id}.key"
    operation_key = args.operation_key.strip()
    if not operation_key and key_path.is_file():
        operation_key = key_path.read_text(encoding="utf-8").strip()
    if not operation_key:
        operation_key = str(uuid.uuid4())
        key_path.write_text(operation_key, encoding="utf-8")

    client = RemoteGatewayClient(base_url, token)
    try:
        payload = (
            client.get_metadata_refresh(operation_key)
            if args.status
            else client.enqueue_metadata_refresh(args.job_id, operation_key)
        )
    finally:
        client.close()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
