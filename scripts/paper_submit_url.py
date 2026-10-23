from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.paper_intake_diagnose import config, make_http_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit one public paper URL through the machine intake API")
    parser.add_argument("url")
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    values = config()
    base = values["PAPER_INTAKE_API_BASE"].rstrip("/")
    token = values["PAPER_INTAKE_WORKER_TOKEN"]
    if not base or not token:
        parser.error("PAPER_INTAKE_API_BASE and PAPER_INTAKE_WORKER_TOKEN are required")
    session = make_http_session()
    last_error = ""
    for attempt in range(1, max(args.attempts, 1) + 1):
        try:
            response = session.post(
                base + "/v1/worker/intake/url",
                headers={"Authorization": "Bearer " + token},
                json={"url": args.url},
                timeout=(60, 30),
            )
            payload = response.json()
            payload["http_status"] = response.status_code
            payload["client_attempt"] = attempt
            print(json.dumps(payload, ensure_ascii=False))
            return 0 if response.status_code in {200, 202} else 1
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_error = type(exc).__name__
            if attempt < args.attempts:
                time.sleep(min(2 ** (attempt - 1), 4))
    print(json.dumps({"ok": False, "code": "network_unreachable", "exception_type": last_error}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
