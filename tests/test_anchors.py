"""Tests de los enlaces internos a fuentes y etiquetas.

Las plantillas (`theme/main.html`, `theme/partials/tags.html`) construyen los
enlaces `fuentes#<slug>` y `etiquetas#<slug>` slugificando a mano (minúsculas,
guiones, tildes → vocal). Estos tests comprueban que el slug enlazado existe
como sección (`##` / `###`) en el fichero destino.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest
from support import RECIPE_PATHS, SOURCES_FILE, TAGS_FILE, headings, load_frontmatter


def _slugify(text: str) -> str:
    """Réplica en Python del slugificado de las plantillas Jinja."""
    slug = unicodedata.normalize("NFD", text.casefold())
    slug = "".join(char for char in slug if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", "-", slug)


def _used_sources() -> set[str]:
    """Valores `source` usados por las recetas."""
    return {
        recipe.source
        for path in RECIPE_PATHS
        if (recipe := load_frontmatter(path)).source is not None
    }


def _used_tags() -> set[str]:
    """Valores `tags` usados por las recetas."""
    return {tag for path in RECIPE_PATHS for tag in (load_frontmatter(path).tags or [])}


@pytest.mark.parametrize("source", sorted(_used_sources()))
def test_source_resuelve_a_seccion(source: str) -> None:
    """El enlace `fuentes#<slug>` apunta a una sección `##` existente."""
    assert _slugify(source) in {
        _slugify(heading) for heading in headings(SOURCES_FILE, 2)
    }, f"'{source}' no resuelve a ninguna sección '##' de docs/fuentes.md"


@pytest.mark.parametrize("tag", sorted(_used_tags()))
def test_tag_resuelve_a_seccion(tag: str) -> None:
    """El enlace `etiquetas#<slug>` apunta a una sección `###` existente."""
    assert _slugify(tag) in {_slugify(heading) for heading in headings(TAGS_FILE, 3)}, (
        f"'{tag}' no resuelve a ninguna sección '###' de docs/etiquetas.md"
    )


def test_slugify_cubre_plantillas() -> None:
    """El slugificado Python coincide con el de las plantillas para lo usado.

    Las plantillas solo sustituyen `ñ` y vocales con tilde; si aparece un
    carácter fuera de ese conjunto (p. ej. `ç`), el enlace se rompería en
    silencio. Este test lo detecta comparando contra la normalización Unicode
    completa.
    """
    template_chars = set("ñáéíóúü")
    for name in _used_sources() | _used_tags():
        lowered = name.casefold()
        extras = {
            char
            for char in lowered
            if unicodedata.category(char).startswith("L")
            and not char.isascii()
            and char not in template_chars
        }
        assert not extras, (
            f"'{name}' usa {sorted(extras)}: no cubiertos por las plantillas"
        )


def _base_theme_files() -> frozenset[str]:
    """Ficheros del tema base Zensical (`templates/` del paquete instalado)."""
    try:
        from importlib.resources import as_file, files

        traversable = files("zensical") / "templates"
        with as_file(traversable) as templates:
            if templates.is_dir():
                return frozenset(
                    path.relative_to(templates).as_posix()
                    for path in templates.rglob("*")
                    if path.is_file()
                )
    except (ImportError, ModuleNotFoundError, FileNotFoundError):
        pass
    return frozenset()


def test_plantillas_no_referencian_ficheros_inexistentes() -> None:
    """Los `include` de `theme/main.html` existen (propios o del tema base)."""
    theme_dir = Path(__file__).resolve().parent.parent / "theme"
    own_files = {
        path.relative_to(theme_dir).as_posix()
        for path in theme_dir.rglob("*")
        if path.is_file()
    }
    available = own_files | _base_theme_files()
    missing = {
        match
        for match in re.findall(
            r'{%\s*include\s+"([^"]+)"\s*%}', (theme_dir / "main.html").read_text()
        )
        if match not in available
    }
    assert not missing, f"includes sin parcial: {sorted(missing)}"
