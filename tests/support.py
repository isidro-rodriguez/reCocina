"""Rutas, esquema del frontmatter y utilidades compartidas por los tests."""

from __future__ import annotations

import datetime as dt
import re
from functools import cache
from pathlib import Path
from typing import Annotated, Any, Final

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

PROJECT_DIR: Final = Path(__file__).resolve().parent.parent
DOCS_DIR: Final = PROJECT_DIR / "docs"
RECIPES_DIR: Final = DOCS_DIR / "recetas"
PHOTOS_DIR: Final = DOCS_DIR / "fotos"
SOURCES_FILE: Final = DOCS_DIR / "fuentes.md"
TAGS_FILE: Final = DOCS_DIR / "etiquetas.md"
ZENSICAL_FILE: Final = PROJECT_DIR / "zensical.toml"

RECIPE_PATHS: Final = sorted(RECIPES_DIR.glob("*.md"))

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
StrictPositiveInt = Annotated[int, Field(strict=True, gt=0)]


class Recipe(BaseModel):
    """Esquema del frontmatter de una receta."""

    # `forbid` detecta erratas en las claves (p. ej. `peoples`).
    model_config = ConfigDict(extra="forbid")

    title: Text
    people: StrictPositiveInt
    time: StrictPositiveInt
    date: dt.date
    source: Text | None = None
    tags: Annotated[list[Text], Field(min_length=1)] | None = None

    @model_validator(mode="before")
    @classmethod
    def _reject_empty_values(cls, data: Any) -> Any:
        """Una clave presente sin valor (`source:`) es un error."""
        if isinstance(data, dict):
            empty = sorted(str(key) for key, value in data.items() if value is None)
            if empty:
                msg = f"claves presentes pero vacías: {', '.join(empty)}"
                raise ValueError(msg)
        return data

    @field_validator("date")
    @classmethod
    def _not_in_future(cls, value: dt.date) -> dt.date:
        """Detecta erratas de año como `2062-10-05`."""
        if value > dt.date.today():
            msg = f"fecha futura ({value})"
            raise ValueError(msg)
        return value


class _UniqueKeyLoader(yaml.SafeLoader):
    """Loader YAML que rechaza claves duplicadas en un mismo mapa."""

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        duplicated = sorted({str(key) for key in keys if keys.count(key) > 1})
        if duplicated:
            msg = f"claves duplicadas: {', '.join(duplicated)}"
            raise yaml.YAMLError(msg)
        return super().construct_mapping(node, deep=deep)


def read_text(path: Path) -> str:
    """Lee un fichero UTF-8 estricto (tolera BOM)."""
    return path.read_text(encoding="utf-8-sig")


def _frontmatter_block(text: str, name: str) -> str:
    """Extrae el YAML entre los ``---`` iniciales."""
    match = _FRONTMATTER.match(text)
    if match is None:
        msg = f"{name}: sin frontmatter (falta '---' inicial o de cierre)"
        raise ValueError(msg)
    return match.group(1)


@cache
def load_frontmatter(path: Path) -> Recipe:
    """Lee y valida el frontmatter de una receta.

    Raises:
        ValueError: Si falta el bloque ``---`` o el YAML no es un mapa.
        yaml.YAMLError: Si el YAML es inválido o repite claves.
        pydantic.ValidationError: Si algún campo incumple el esquema.
    """
    block = _frontmatter_block(read_text(path), path.name)
    meta = yaml.load(block, Loader=_UniqueKeyLoader)
    if not isinstance(meta, dict):
        msg = f"{path.name}: el frontmatter debe ser un mapa clave: valor"
        raise ValueError(msg)
    return Recipe.model_validate(meta)


def all_recipes() -> list[Recipe]:
    """Frontmatter validado de todas las recetas.

    Raises:
        ValueError: Si algún frontmatter no es válido (ver `load_frontmatter`).
    """
    return [load_frontmatter(path) for path in RECIPE_PATHS]


@cache
def headings(path: Path, level: int) -> frozenset[str]:
    """Títulos Markdown de un nivel (``##`` → 2) de un fichero."""
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", re.MULTILINE)
    return frozenset(pattern.findall(read_text(path)))
