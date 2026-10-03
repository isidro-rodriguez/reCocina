"""Tests de consistencia del recetario.

Comprueban que las recetas, el menú (``nav`` de ``zensical.toml``) y las fotos
están sincronizados:

* Cada receta ``docs/recetas/*.md`` está listada en el ``nav``.
* Cada entrada ``recetas/...`` del ``nav`` apunta a un fichero existente.
* Cada imagen enlazada desde una receta existe en disco.
* Cada foto de ``docs/img/fotos`` está referenciada por alguna receta.
* Ninguna foto de ``docs/img/fotos`` está vacía o corrupta (imagen muerta).
* Cada foto de ``docs/img/fotos`` es WebP de 900x600.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
import struct
import tomllib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "docs"
RECIPES_DIR = DOCS_DIR / "recetas"
PHOTOS_DIR = DOCS_DIR / "img" / "fotos"
ZENSICAL_FILE = PROJECT_DIR / "zensical.toml"

# Enlaces de imagen en Markdown: ![alt](ruta) o ![alt](ruta "título")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(\s*([^)\s]+)")
NAV_PREFIX = "recetas/"


def _flatten_nav(node: object) -> list[str]:
    """Aplana recursivamente la estructura del ``nav`` de Zensical."""
    if isinstance(node, list):
        return [page for item in node for page in _flatten_nav(item)]
    if isinstance(node, dict):
        return [page for value in node.values() for page in _flatten_nav(value)]
    if isinstance(node, str):
        return [node]
    return []


def _nav_recipes() -> set[str]:
    """Rutas de recetas (relativas a ``docs``) declaradas en el ``nav``."""
    config = tomllib.loads(ZENSICAL_FILE.read_text(encoding="utf-8"))
    project = config.get("project") or {}
    pages = _flatten_nav(project.get("nav", []))
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
            header = handle.read(32)
        if not header:
            dead.append(f"{photo.name}: fichero vacío (0 bytes)")
        elif not _looks_like_image(header):
            dead.append(f"{photo.name}: contenido no reconocido como imagen")
    return dead


# Formato exigido a las fotos de recetas: WebP de 900x600.
EXPECTED_EXTENSION = ".webp"
EXPECTED_WIDTH = 900
EXPECTED_HEIGHT = 600


def _webp_dimensions(header: bytes) -> tuple[int, int] | None:
    """Dimensiones (ancho, alto) de una cabecera WebP (VP8, VP8L o VP8X)."""
    if len(header) < 30 or header[:4] != b"RIFF" or header[8:12] != b"WEBP":
        return None
    fourcc = header[12:16]
    if fourcc == b"VP8 ":
        if header[23:26] != b"\x9d\x01\x2a" or len(header) < 30:
            return None
        width = struct.unpack("<H", header[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", header[28:30])[0] & 0x3FFF
        return (width, height)
    if fourcc == b"VP8L":
        if header[20] != 0x2F or len(header) < 25:
            return None
        bits = struct.unpack("<I", header[21:25])[0]
        return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    if fourcc == b"VP8X":
        width = int.from_bytes(header[24:27], "little") + 1
        height = int.from_bytes(header[27:30], "little") + 1
        return (width, height)
    return None


def _non_webp_photos() -> list[str]:
    """Fotos de ``docs/img/fotos`` que no son WebP (por extensión o contenido)."""
    non_webp: list[str] = []
    for photo in sorted(PHOTOS_DIR.glob("*")):
        if not photo.is_file():
            continue
        with photo.open("rb") as handle:
            header = handle.read(32)
        is_webp = photo.suffix.lower() == EXPECTED_EXTENSION
        if not is_webp or _webp_dimensions(header) is None:
            non_webp.append(f"{photo.name}: no es WebP ({EXPECTED_EXTENSION})")
    return non_webp


def _wrongly_sized_photos() -> list[str]:
    """Fotos WebP de ``docs/img/fotos`` que no miden 900x600."""
    wrong_size: list[str] = []
    for photo in sorted(PHOTOS_DIR.glob(f"*{EXPECTED_EXTENSION}")):
        if not photo.is_file():
            continue
        with photo.open("rb") as handle:
            header = handle.read(32)
        dimensions = _webp_dimensions(header)
        if dimensions is None:
            continue
        width, height = dimensions
        if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
            wrong_size.append(
                f"{photo.name}: {width}x{height} "
                f"(se esperaban {EXPECTED_WIDTH}x{EXPECTED_HEIGHT})"
            )
    return wrong_size


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


def test_fotos_en_webp() -> None:
    """Toda foto de ``docs/img/fotos`` debe ser WebP."""
    assert _non_webp_photos() == [], "Fotos que no son WebP:\n" + "\n".join(
        _non_webp_photos()
    )


def test_fotos_con_resolucion_900x600() -> None:
    """Toda foto WebP de ``docs/img/fotos`` debe medir 900x600."""
    assert _wrongly_sized_photos() == [], (
        "Fotos con resolución incorrecta:\n" + "\n".join(_wrongly_sized_photos())
    )
