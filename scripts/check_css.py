#!/usr/bin/env python3
"""Check CSS formatting with cssbeautifier."""

import sys
from pathlib import Path
from typing import Any

import cssbeautifier


def check_file(path: str, opts: Any) -> tuple[str, str]:
    """Return formatted and original content of a CSS file."""
    formatted = cssbeautifier.beautify_file(path, opts)
    with Path(path).open(encoding="utf-8") as f:
        original = f.read()
    return formatted, original


def main() -> int:
    """Check if CSS files are properly formatted."""
    opts = cssbeautifier.default_options()
    opts.indent_size = 2
    opts.eol = "\n"

    files = ["docs/css/extra.css", "docs/css/print.css"]
    failed = False

    for path in files:
        formatted, original = check_file(path, opts)
        if formatted != original:
            print(f"{path} is not formatted")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
