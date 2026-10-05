"""Genera `docs/assets/recetas.json` con los metadatos de cada receta."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

import yaml

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "docs" / "recetas"
OUTPUT = ROOT / "docs" / "assets" / "recetas.json"

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", re.DOTALL)


class RecipeEntry(TypedDict):
    """Datos mínimos que necesita la tarjeta de la portada."""

    slug: str
    title: str
    people: int | None
    time: int | None


def _read_frontmatter(path: Path) -> dict[str, object]:
    """Lee el frontmatter YAML de una receta (vacío si no existe)."""
    # utf-8-sig descarta el BOM que algunos editores añaden.
    match = _FRONTMATTER.match(path.read_text(encoding="utf-8-sig"))
    return (yaml.safe_load(match.group(1)) or {}) if match else {}


def _positive_int(value: object) -> int | None:
    """Devuelve `value` si es un entero positivo; si no, `None`."""
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return None


def _parse_recipe(path: Path) -> RecipeEntry:
    """Lee una receta y devuelve sus metadatos.

    Raises:
        ValueError: Si falta `title` en el frontmatter.
    """
    meta = _read_frontmatter(path)
    title = meta.get("title")
    if not isinstance(title, str) or not title.strip():
        msg = f"{path.name}: falta 'title' en el frontmatter"
        raise ValueError(msg)
    return RecipeEntry(
        slug=path.stem,
        title=title.strip(),
        people=_positive_int(meta.get("people")),
        time=_positive_int(meta.get("time")),
    )


def build_recipe_index(*, strict: bool = False) -> int:
    """Escribe el índice JSON y devuelve el número de recetas indexadas.

    Las recetas inválidas se omiten con un aviso por stderr.

    Raises:
        ValueError: Si `strict` es `True` y alguna receta no tiene título.
    """
    entries: list[RecipeEntry] = []
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        try:
            entries.append(_parse_recipe(path))
        except ValueError as exc:
            errors.append(str(exc))

    for error in errors:
        print(f"AVISO {error}", file=sys.stderr)
    if strict and errors:
        msg = f"{len(errors)} receta(s) sin título"
        raise ValueError(msg)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict", action="store_true", help="falla si hay recetas inválidas"
    )
    args = parser.parse_args()
    count = build_recipe_index(strict=args.strict)
    print(f"{count} recetas indexadas en {OUTPUT.relative_to(ROOT)}")
