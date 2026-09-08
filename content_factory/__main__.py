"""支持 `python -m content_factory --paper-id ...` 直接运行。"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
