#!/usr/bin/env python3
"""Check JS formatting with jsbeautifier."""

import sys
from pathlib import Path

import jsbeautifier


def main() -> int:
    """Check if docs/sw.js is properly formatted."""
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    opts.eol = "\n"

    formatted = jsbeautifier.beautify_file("docs/sw.js", opts)
    with Path("docs/sw.js").open(encoding="utf-8") as f:
        original = f.read()

    if formatted != original:
        print("docs/sw.js is not formatted")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
