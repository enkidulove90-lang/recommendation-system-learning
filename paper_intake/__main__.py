from __future__ import annotations

import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Local single-paper intake control desk")
    parser.add_argument("command", nargs="?", default="serve", choices=("serve",))
    parser.add_argument("--host", default=os.getenv("PAPER_INTAKE_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PAPER_INTAKE_PORT", "8765")))
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "paper_intake.web:build_default_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
