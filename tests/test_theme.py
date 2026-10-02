"""Tests del tema y de los recursos del sitio (favicon e iconos).

Comprueban que el set de favicons de ``docs/img/favicon`` está completo y
debidamente enlazado:

* Los ficheros esperados existen.
* ``theme.favicon`` en ``mkdocs.yml`` apunta a un fichero existente.
* ``theme/main.html`` referencia los iconos y el manifiesto.
* ``site.webmanifest`` es JSON válido y sus iconos existen en disco.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "docs"
FAVICON_DIR = DOCS_DIR / "img" / "favicon"
THEME_MAIN = PROJECT_DIR / "theme" / "main.html"
MKDOCS_FILE = PROJECT_DIR / "mkdocs.yml"

# Ficheros que debe contener el set de favicons.
FAVICON_FILES = (
    "favicon.ico",
    "favicon-16x16.png",
    "favicon-32x32.png",
    "apple-touch-icon.png",
    "android-chrome-192x192.png",
    "android-chrome-512x512.png",
    "site.webmanifest",
)


def _missing_favicon_files() -> list[str]:
    """Ficheros del set de favicons que faltan en disco."""
    return [name for name in FAVICON_FILES if not (FAVICON_DIR / name).is_file()]


def _theme_favicon_file() -> str | None:
    """Ruta (relativa a ``docs``) del favicon declarado en ``mkdocs.yml``, si existe."""
    config = yaml.safe_load(MKDOCS_FILE.read_text(encoding="utf-8"))
    favicon = (config.get("theme") or {}).get("favicon")
    return str(favicon) if favicon else None


def _favicon_head_links() -> list[str]:
    """Referencias esperadas del ``<head>`` que faltan en ``theme/main.html``."""
    if not THEME_MAIN.is_file():
        return ["theme/main.html (no existe)"]
    text = THEME_MAIN.read_text(encoding="utf-8")
    expected = {
        "apple-touch-icon": "apple-touch-icon.png",
        "favicon-16x16": "favicon-16x16.png",
        "favicon-32x32": "favicon-32x32.png",
        "site.webmanifest": "site.webmanifest",
    }
    return [
        f"{label} ({target})"
        for label, target in expected.items()
        if target not in text
    ]


def _manifest_icon_problems() -> list[str]:
    """Problemas del ``site.webmanifest`` (JSON inválido o iconos inexistentes)."""
    manifest = FAVICON_DIR / "site.webmanifest"
    if not manifest.is_file():
        return ["site.webmanifest (no existe)"]
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"site.webmanifest: JSON inválido ({error})"]

    problems: list[str] = []
    if not data.get("name") or not data.get("short_name"):
        problems.append("site.webmanifest: 'name'/'short_name' vacíos")
    for icon in data.get("icons", []):
        src = icon.get("src", "")
        if src.startswith(("/", "http://", "https://")):
            problems.append(f"site.webmanifest: ruta absoluta no portátil '{src}'")
        elif not (FAVICON_DIR / src).is_file():
            problems.append(f"site.webmanifest: icono inexistente '{src}'")
    return problems


def test_set_de_favicons_completo() -> None:
    """El set de favicons debe estar completo en ``docs/img/favicon``."""
    assert _missing_favicon_files() == [], "Faltan ficheros de favicon:\n" + "\n".join(
        _missing_favicon_files()
    )


def test_theme_favicon_apunta_a_un_fichero() -> None:
    """``theme.favicon`` debe declararse y apuntar a un fichero existente."""
    favicon = _theme_favicon_file()
    assert favicon is not None, "Falta 'theme.favicon' en mkdocs.yml"
    target = DOCS_DIR / favicon
    assert target.is_file(), f"theme.favicon apunta a un fichero inexistente: {favicon}"


def test_theme_main_referencia_los_iconos() -> None:
    """``theme/main.html`` debe enlazar los iconos y el manifiesto."""
    assert _favicon_head_links() == [], (
        "Referencias ausentes en theme/main.html:\n" + "\n".join(_favicon_head_links())
    )


def test_webmanifest_valido() -> None:
    """``site.webmanifest`` debe ser JSON válido con iconos existentes."""
    assert _manifest_icon_problems() == [], (
        "Problemas en site.webmanifest:\n" + "\n".join(_manifest_icon_problems())
    )
