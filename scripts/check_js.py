#!/usr/bin/env python3
"""Comprueba el formato de docs/sw.js con jsbeautifier."""

import sys
from pathlib import Path

import jsbeautifier

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "sw.js"


def main() -> int:
    """Devuelve 1 si docs/sw.js no está formateado."""
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    opts.eol = "\n"
    opts.end_with_newline = True

    original = TARGET.read_text(encoding="utf-8")
    formatted = jsbeautifier.beautify(original, opts)

    if formatted != original:
        print(f"{TARGET.relative_to(ROOT).as_posix()} no está formateado")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
