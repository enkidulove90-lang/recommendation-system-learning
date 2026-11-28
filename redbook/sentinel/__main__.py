"""Module entry point for the Windows Task Scheduler sentinel command."""
from __future__ import annotations

import sys


def main() -> None:
    """Forward only sentinel arguments to the supported repository CLI."""
    from redbook.cli import main as cli_main

    sys.argv = ["redbook.cli", "sentinel", *sys.argv[1:]]
    cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
