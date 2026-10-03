"""Genera precache.json para el service worker."""

import json
from pathlib import Path

SITE = Path("site")

VALID_SUFFIXES = {
    ".html",
    ".css",
    ".js",
    ".webp",
    ".png",
    ".svg",
    ".json",
}

urls = [
    "/" + p.relative_to(SITE).as_posix()
    for p in sorted(SITE.rglob("*"))
    if p.is_file() and p.suffix in VALID_SUFFIXES
]
(SITE / "precache.json").write_text(json.dumps(urls), encoding="utf-8")
