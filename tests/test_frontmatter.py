"""Tests del frontmatter de las recetas.

Cada ``docs/recetas/*.md`` debe empezar con un bloque ``---`` que cumpla el
esquema ``support.Recipe``:

* ``title``: obligatorio, cadena no vacía.
* ``people`` y ``time``: obligatorios, enteros positivos.
* ``date``: obligatorio, ``YYYY-MM-DD``, fecha válida y no futura.
* ``category``: obligatorio; debe coincidir con el ``title`` de una página
  ``docs/categoria/*.md``, que a su vez está en la sección "Categorías" del
  ``nav``.
* ``source``: opcional; si existe, debe tener un ``##`` homónimo en
  ``docs/fuentes.md``.
* ``tags``: opcional, lista no vacía; cada tag debe tener un ``###`` homónimo
  en ``docs/etiquetas.md``.

Además, no puede haber secciones, etiquetas ni categorías huérfanas, ni
títulos repetidos.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import tomllib
from collections import Counter
from pathlib import Path

import pytest
from support import (
    CATEGORY_PATHS,
    DOCS_DIR,
    RECIPE_PATHS,
    SOURCES_FILE,
    TAGS_FILE,
    ZENSICAL_FILE,
    all_recipes,
    headings,
    load_frontmatter,
    page_meta,
)

NAV_CATEGORIES = "Categorías"

per_recipe = pytest.mark.parametrize("path", RECIPE_PATHS, ids=lambda p: p.stem)


@per_recipe
def test_frontmatter_cumple_esquema(path: Path) -> None:
    """El frontmatter es YAML válido y cumple el esquema."""
    load_frontmatter(path)


@per_recipe
def test_source_existe_en_fuentes(path: Path) -> None:
    """El ``source`` tiene sección ``##`` en ``docs/fuentes.md``."""
    source = load_frontmatter(path).source
    if source is not None:
        assert source in headings(SOURCES_FILE, 2), (
            f"'{source}' sin sección '##' en docs/fuentes.md"
        )


@per_recipe
def test_tags_existen_en_etiquetas(path: Path) -> None:
    """Cada tag tiene un ``###`` en ``docs/etiquetas.md``."""
    unknown = set(load_frontmatter(path).tags or []) - headings(TAGS_FILE, 3)
    assert not unknown, f"tags sin '###' en docs/etiquetas.md: {sorted(unknown)}"


def test_titulos_unicos() -> None:
    """No hay dos recetas con el mismo título."""
    counts = Counter(recipe.title.casefold() for recipe in all_recipes())
    repeated = sorted(title for title, count in counts.items() if count > 1)
    assert not repeated, f"Títulos repetidos: {repeated}"


def test_fuentes_sin_secciones_huerfanas() -> None:
    """Toda sección ``##`` de ``docs/fuentes.md`` la usa algún ``source``."""
    used = {recipe.source for recipe in all_recipes()}
    orphans = sorted(headings(SOURCES_FILE, 2) - used)
    assert not orphans, f"Secciones sin usar en docs/fuentes.md: {orphans}"


def test_etiquetas_sin_tags_huerfanos() -> None:
    """Toda etiqueta ``###`` de ``docs/etiquetas.md`` la usa algún ``tags``."""
    used = {tag for recipe in all_recipes() for tag in recipe.tags or []}
    orphans = sorted(headings(TAGS_FILE, 3) - used)
    assert not orphans, f"Etiquetas sin usar en docs/etiquetas.md: {orphans}"


def _category_titles() -> set[str]:
    """Títulos de las páginas ``docs/categoria/*.md``."""
    return {page_meta(path)["title"] for path in CATEGORY_PATHS}


@per_recipe
def test_categoria_tiene_pagina(path: Path) -> None:
    """La ``category`` coincide con el ``title`` de una página de categoría."""
    category = load_frontmatter(path).category
    assert category in _category_titles(), f"'{category}' sin página en docs/categoria/"


def test_categorias_sin_paginas_huerfanas() -> None:
    """Toda página de categoría la usa alguna receta."""
    used = {recipe.category for recipe in all_recipes()}
    orphans = sorted(_category_titles() - used)
    assert not orphans, f"Categorías sin recetas en docs/categoria/: {orphans}"


def test_categoria_en_el_nav() -> None:
    """Toda página de categoría está en la sección "Categorías" del ``nav``."""
    nav = tomllib.loads(ZENSICAL_FILE.read_text(encoding="utf-8"))["project"]["nav"]
    section = next(
        (entry[NAV_CATEGORIES] for entry in nav if NAV_CATEGORIES in entry), []
    )
    listed = {page for item in section for page in item.values()}
    missing = sorted(
        path.relative_to(DOCS_DIR).as_posix()
        for path in CATEGORY_PATHS
        if path.relative_to(DOCS_DIR).as_posix() not in listed
    )
    assert not missing, f"Categorías fuera de '{NAV_CATEGORIES}' en el nav: {missing}"
