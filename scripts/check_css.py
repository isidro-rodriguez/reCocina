#!/usr/bin/env python3
"""Comprueba el formato de docs/css con cssbeautifier."""

import sys
from pathlib import Path

import cssbeautifier

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "docs" / "css" / "extra.css",
    ROOT / "docs" / "css" / "print.css",
)


def main() -> int:
    """Devuelve 1 si algún CSS no está formateado."""
    opts = cssbeautifier.default_options()
    opts.indent_size = 4
    opts.eol = "\n"
    opts.end_with_newline = True

    failed = False
    for path in TARGETS:
        original = path.read_text(encoding="utf-8")
        if cssbeautifier.beautify(original, opts) != original:
            print(f"{path.relative_to(ROOT).as_posix()} no está formateado")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
