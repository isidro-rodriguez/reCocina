"""Tests de consistencia del recetario.

Comprueban que recetas, menú (``nav`` de ``zensical.toml``) y fotos están
sincronizados:

* Cada receta está en el ``nav`` y cada entrada ``recetas/...`` del ``nav``
  apunta a un fichero existente.
* El slug de cada receta es válido para una URL.
* Cada receta tiene su ``docs/fotos/<slug>.webp`` y cada foto tiene receta.
* Cada foto es una imagen WebP decodificable de 900x600.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterator
from pathlib import Path

import pytest
from PIL import Image
from support import DOCS_DIR, PHOTOS_DIR, RECIPE_PATHS, ZENSICAL_FILE

NAV_PREFIX = "recetas/"
PHOTO_SIZE = (900, 600)
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _flatten_nav(node: object) -> Iterator[str]:
    """Recorre el ``nav`` y emite cada ruta de página."""
    match node:
        case str():
            yield node
        case list():
            for item in node:
                yield from _flatten_nav(item)
        case dict():
            for value in node.values():
                yield from _flatten_nav(value)


def _nav_recipes() -> list[str]:
    """Rutas ``recetas/...`` declaradas en el ``nav``."""
    config = tomllib.loads(ZENSICAL_FILE.read_text(encoding="utf-8"))
    pages = _flatten_nav(config.get("project", {}).get("nav", []))
    return sorted(page for page in pages if page.startswith(NAV_PREFIX))


NAV_RECIPES = _nav_recipes()
PHOTO_PATHS = sorted(path for path in PHOTOS_DIR.iterdir() if path.is_file())
RECIPE_SLUGS = {path.stem for path in RECIPE_PATHS}

per_recipe = pytest.mark.parametrize("path", RECIPE_PATHS, ids=lambda p: p.stem)
per_photo = pytest.mark.parametrize("photo", PHOTO_PATHS, ids=lambda p: p.name)


@per_recipe
def test_receta_en_el_nav(path: Path) -> None:
    """Toda receta está en el ``nav`` (si no, no se ve en el sitio)."""
    assert f"{NAV_PREFIX}{path.name}" in NAV_RECIPES


@pytest.mark.parametrize("entry", NAV_RECIPES)
def test_entrada_del_nav_existe(entry: str) -> None:
    """Toda entrada del ``nav`` apunta a un fichero existente."""
    assert (DOCS_DIR / entry).is_file()


@per_recipe
def test_slug_valido(path: Path) -> None:
    """El slug (nombre del fichero) es minúsculas, ASCII y guiones."""
    assert _SLUG.match(path.stem), f"slug inválido: {path.stem}"


@per_recipe
def test_receta_tiene_foto(path: Path) -> None:
    """Toda receta tiene su ``docs/fotos/<slug>.webp``."""
    assert (PHOTOS_DIR / f"{path.stem}.webp").is_file()


@per_photo
def test_foto_tiene_receta(photo: Path) -> None:
    """Toda foto corresponde a una receta existente."""
    assert photo.stem in RECIPE_SLUGS, "foto huérfana (sin receta)"


@per_photo
def test_foto_webp_900x600(photo: Path) -> None:
    """La foto es un WebP válido, íntegro y de 900x600."""
    assert photo.suffix == ".webp", f"extensión {photo.suffix!r}, se esperaba .webp"
    with Image.open(photo) as image:
        assert image.format == "WEBP"
        assert image.size == PHOTO_SIZE, f"{image.size}, se esperaba {PHOTO_SIZE}"
        image.load()  # decodifica entera: detecta ficheros truncados o corruptos
