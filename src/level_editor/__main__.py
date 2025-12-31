"""Console entrypoint for ``python -m level_editor``."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .app import editor_main


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the level editor")
    parser.add_argument("width", nargs="?", type=int, default=22, help="Grid width in tiles")
    parser.add_argument("height", nargs="?", type=int, default=14, help="Grid height in tiles")
    parser.add_argument(
        "template",
        nargs="?",
        type=Path,
        default=None,
        help="Optional path to a template JSON/TMX to load",
    )
    args = parser.parse_args(argv)

    editor_main(args.width, args.height, args.template)


if __name__ == "__main__":
    main()
