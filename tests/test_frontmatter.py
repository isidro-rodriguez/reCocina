"""Tests del frontmatter de las recetas.

Cada ``docs/recetas/*.md`` debe empezar con un bloque ``---`` que cumpla el
esquema ``support.Recipe``:

* ``title``: obligatorio, cadena no vacía.
* ``people`` y ``time``: obligatorios, enteros positivos.
* ``date``: obligatorio, ``YYYY-MM-DD``, fecha válida y no futura.
* ``source``: opcional; si existe, debe tener un ``##`` homónimo en
  ``docs/fuentes.md``.
* ``tags``: opcional, lista no vacía; cada tag debe tener un ``###`` homónimo
  en ``docs/etiquetas.md``.

Además, no puede haber secciones ni etiquetas huérfanas, ni títulos repetidos.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
from support import (
    RECIPE_PATHS,
    SOURCES_FILE,
    TAGS_FILE,
    all_recipes,
    headings,
    load_frontmatter,
)

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
