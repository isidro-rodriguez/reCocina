"""Genera `site/precache.json` para el service worker.

Debe ejecutarse desde la raíz del proyecto, tras `zensical build`.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

VALID_SUFFIXES = {
    ".css",
    ".html",
    ".ico",
    ".js",
    ".json",
    ".png",
    ".svg",
    ".webmanifest",
    ".webp",
}


def _cache_version() -> str:
    """Versión de la caché derivada del contenido (invalida al cambiar algo)."""
    digest = hashlib.sha256()
    for path in sorted(SITE.rglob("*")):
        if path.is_file() and path.suffix in VALID_SUFFIXES:
            digest.update(path.relative_to(SITE).as_posix().encode())
            digest.update(path.read_bytes())
    return f"recocina-{digest.hexdigest()[:12]}"


def build_precache() -> str:
    """Genera `precache.json` y devuelve la versión de la caché."""
    version = _cache_version()
    urls = [
        "/" + path.relative_to(SITE).as_posix()
        for path in sorted(SITE.rglob("*"))
        if path.is_file() and path.suffix in VALID_SUFFIXES
    ]

    payload = {"version": version, "urls": urls}
    (SITE / "precache.json").write_text(json.dumps(payload), encoding="utf-8")
    return version


if __name__ == "__main__":
    print(f"precache.json generado (caché: {build_precache()})")
