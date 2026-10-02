"""Tests de consistencia del recetario.

Comprueban que las recetas, el menú (``nav`` de ``mkdocs.yml``) y las fotos
están sincronizados:

* Cada receta ``docs/recetas/*.md`` está listada en el ``nav``.
* Cada entrada ``recetas/...`` del ``nav`` apunta a un fichero existente.
* Cada imagen enlazada desde una receta existe en disco.
* Cada foto de ``docs/img/fotos`` está referenciada por alguna receta.
* Ninguna foto de ``docs/img/fotos`` está vacía o corrupta (imagen muerta).

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "docs"
RECIPES_DIR = DOCS_DIR / "recetas"
PHOTOS_DIR = DOCS_DIR / "img" / "fotos"
MKDOCS_FILE = PROJECT_DIR / "mkdocs.yml"

# Enlaces de imagen en Markdown: ![alt](ruta) o ![alt](ruta "título")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(\s*([^)\s]+)")
NAV_PREFIX = "recetas/"


def _flatten_nav(node: object) -> list[str]:
    """Aplana recursivamente la estructura del ``nav`` de MkDocs."""
    if isinstance(node, list):
        return [page for item in node for page in _flatten_nav(item)]
    if isinstance(node, dict):
        return [page for value in node.values() for page in _flatten_nav(value)]
    if isinstance(node, str):
        return [node]
    return []


def _nav_recipes() -> set[str]:
    """Rutas de recetas (relativas a ``docs``) declaradas en el ``nav``."""
    config = yaml.safe_load(MKDOCS_FILE.read_text(encoding="utf-8"))
    pages = _flatten_nav(config.get("nav", []))
    return {page for page in pages if page.startswith(NAV_PREFIX)}


def _recipes_on_disk() -> set[str]:
    """Rutas de recetas (relativas a ``docs``) presentes en el disco."""
    return {f"{NAV_PREFIX}{path.name}" for path in RECIPES_DIR.glob("*.md")}


def _linked_images(recipe: Path) -> list[str]:
    """Rutas de imagen enlazadas dentro de una receta (excluye URLs externas)."""
    text = recipe.read_text(encoding="utf-8")
    return [
        link
        for link in IMAGE_PATTERN.findall(text)
        if not link.startswith(("http://", "https://"))
    ]


def _missing_in_nav() -> list[str]:
    """Recetas en disco que no están registradas en el ``nav``."""
    return sorted(_recipes_on_disk() - _nav_recipes())


def _nav_without_file() -> list[str]:
    """Entradas del ``nav`` que apuntan a ficheros inexistentes."""
    return sorted(_nav_recipes() - _recipes_on_disk())


def _broken_images() -> list[str]:
    """Imágenes enlazadas desde recetas que no existen en disco."""
    broken: list[str] = []
    for recipe in sorted(RECIPES_DIR.glob("*.md")):
        for link in _linked_images(recipe):
            if not (recipe.parent / link).resolve().is_file():
                broken.append(f"{recipe.name}: {link}")
    return broken


def _orphan_photos() -> list[str]:
    """Fotos de ``docs/img/fotos`` que ninguna receta referencia."""
    referenced = {
        (recipe.parent / link).resolve()
        for recipe in RECIPES_DIR.glob("*.md")
        for link in _linked_images(recipe)
    }
    return sorted(
        str(photo.relative_to(PROJECT_DIR))
        for photo in PHOTOS_DIR.glob("*")
        if photo.is_file() and photo.resolve() not in referenced
    )


# Firmas (magic bytes) de los formatos de imagen admitidos en el recetario.
_IMAGE_SIGNATURES = (
    b"\xff\xd8\xff",  # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"GIF87a",  # GIF
    b"GIF89a",  # GIF
    b"BM",  # BMP
)


def _looks_like_image(header: bytes) -> bool:
    """¿El encabezado corresponde a un formato de imagen conocido?"""
    if header.startswith(_IMAGE_SIGNATURES):
        return True
    # WebP: contenedor RIFF con la etiqueta "WEBP" a partir del offset 8.
    return header[:4] == b"RIFF" and header[8:12] == b"WEBP"


def _dead_photos() -> list[str]:
    """Fotos vacías o cuyo contenido no es una imagen válida (imágenes muertas)."""
    dead: list[str] = []
    for photo in sorted(PHOTOS_DIR.glob("*")):
        if not photo.is_file():
            continue
        with photo.open("rb") as handle:
            header = handle.read(16)
        if not header:
            dead.append(f"{photo.name}: fichero vacío (0 bytes)")
        elif not _looks_like_image(header):
            dead.append(f"{photo.name}: contenido no reconocido como imagen")
    return dead


def test_todas_las_recetas_estan_en_el_nav() -> None:
    """Toda receta en disco debe estar en el ``nav`` (si no, no se ve en el sitio)."""
    assert _missing_in_nav() == [], "Recetas sin registrar en el nav:\n" + "\n".join(
        _missing_in_nav()
    )


def test_nav_sin_entradas_rotas() -> None:
    """Toda entrada del ``nav`` debe apuntar a un fichero existente."""
    assert _nav_without_file() == [], "Entradas del nav sin fichero:\n" + "\n".join(
        _nav_without_file()
    )


def test_imagenes_existen() -> None:
    """Toda imagen enlazada desde una receta debe existir."""
    assert _broken_images() == [], "Imágenes no encontradas:\n" + "\n".join(
        _broken_images()
    )


def test_sin_fotos_huerfanas() -> None:
    """Toda foto de ``docs/img/fotos`` debe estar referenciada por una receta."""
    assert _orphan_photos() == [], "Fotos sin usar:\n" + "\n".join(_orphan_photos())


def test_sin_imagenes_muertas() -> None:
    """Ninguna foto de ``docs/img/fotos`` debe estar vacía o corrupta."""
    assert _dead_photos() == [], "Imágenes muertas:\n" + "\n".join(_dead_photos())
