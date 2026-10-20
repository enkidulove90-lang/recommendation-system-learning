from __future__ import annotations

import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Local single-paper intake control desk")
    parser.add_argument("command", nargs="?", default="serve", choices=("serve", "remote-worker"))
    parser.add_argument("--host", default=os.getenv("PAPER_INTAKE_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PAPER_INTAKE_PORT", "8765")))
    args = parser.parse_args()

    if args.command == "remote-worker":
        try:
            remote_worker_command()
        except RuntimeError as exc:
            parser.error(str(exc))
        return

    import uvicorn
    uvicorn.run(
        "paper_intake.web:build_default_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=False,
    )


def remote_worker_command() -> int:
    from pathlib import Path

    from dotenv import load_dotenv

    from .remote import RemoteGatewayClient
    from .remote_worker import build_remote_worker

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env", override=False)
    required = {
        "PAPER_INTAKE_API_BASE": os.getenv("PAPER_INTAKE_API_BASE", ""),
        "PAPER_INTAKE_WORKER_TOKEN": os.getenv("PAPER_INTAKE_WORKER_TOKEN", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing local configuration: " + ", ".join(missing) + ".")
    client = RemoteGatewayClient(
        required["PAPER_INTAKE_API_BASE"],
        required["PAPER_INTAKE_WORKER_TOKEN"],
    )
    worker = build_remote_worker(client)
    try:
        worker.run_forever()
    except KeyboardInterrupt:
        worker.stop()
    finally:
        client.close()
        repository = getattr(worker, "repository", None)
        if repository is not None:
            repository.close()
    return 0


if __name__ == "__main__":
    main()
