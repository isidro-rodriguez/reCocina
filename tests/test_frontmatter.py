"""Tests del frontmatter de las recetas.

Cada ``docs/recetas/*.md`` debe empezar con un bloque ``---`` que declare:

* ``title``: obligatorio, cadena no vacía, sin caracteres no UTF-8.
* ``people``: obligatorio, entero positivo.
* ``time``: obligatorio, entero positivo.
* ``date``: obligatorio, formato ``YYYY-MM-DD`` con fecha de calendario válida.
* ``source``: opcional, cadena; error si está presente y vacío o si no tiene
  un ``##`` homónimo en ``docs/fuentes.md``.
* ``tags``: opcional, lista de cadenas; error si está presente y vacía o si
  algún tag no tiene un ``###`` homónimo en ``docs/etiquetas.md``.

Además, cada sección ``##`` de ``docs/fuentes.md`` debe estar usada por al
menos un ``source`` de receta (sin secciones huérfanas), y cada etiqueta
``###`` de ``docs/etiquetas.md`` debe estar usada por al menos un ``tags``
de receta (sin etiquetas huérfanas).

El análisis es intencionalmente sin dependencias (solo stdlib) y tolera la
marca BOM (``utf-8-sig``), presente en varias recetas.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RECIPES_DIR = PROJECT_DIR / "docs" / "recetas"
SOURCES_FILE = PROJECT_DIR / "docs" / "fuentes.md"
TAGS_FILE = PROJECT_DIR / "docs" / "etiquetas.md"

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INT_RE = re.compile(r"^[0-9]+$")
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def _unquote(value: str) -> str:
    """Quita las comillas simples o dobles que envuelven un valor."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def _has_non_utf8(value: str) -> bool:
    """Indica si una cadena contiene caracteres no codificables en UTF-8."""
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return True
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)


Frontmatter = dict[str, str | list[str] | None]


def _load_frontmatter(path: Path) -> tuple[Frontmatter, list[str]]:
    """Lee el frontmatter de una receta.

    Devuelve una tupla ``(datos, errores)`` donde ``datos`` mapea claves a su
    valor en bruto (cadena, lista de cadenas o ``None`` si está vacío) y
    ``errores`` describe problemas de codificación o estructura del bloque.
    """
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return {}, [f"{path.name}: no es UTF-8 válido ({exc})"]
    lines = text.splitlines()
    if len(lines) < 2 or lines[0].strip() != "---":
        return {}, [f"{path.name}: sin frontmatter (falta '---' inicial)"]
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, [f"{path.name}: sin frontmatter (falta '---' de cierre)"]
    data: dict[str, str | list[str] | None] = {}
    errors: list[str] = []
    current_list_key: str | None = None
    for raw in lines[1:end]:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            item = _unquote(stripped[1:].strip())
            if current_list_key is None:
                errors.append(
                    f"{path.name}: elemento de lista sin clave ('{raw.strip()}')"
                )
                continue
            previous = data.get(current_list_key)
            if previous is None:
                data[current_list_key] = [item]
            elif isinstance(previous, list):
                previous.append(item)
            else:
                errors.append(f"{path.name}: '{current_list_key}' mezcla valor y lista")
            continue
        if ":" not in raw:
            errors.append(f"{path.name}: línea malformada ('{raw.strip()}')")
            current_list_key = None
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            errors.append(f"{path.name}: clave vacía ('{raw.strip()}')")
            current_list_key = None
            continue
        if key in data:
            errors.append(f"{path.name}: clave duplicada ('{key}')")
            current_list_key = None
            continue
        if value == "":
            data[key] = None
            current_list_key = key
        elif value == "[]":
            data[key] = []
            current_list_key = None
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_unquote(part) for part in inner.split(",")] if inner else []
            current_list_key = None
        else:
            data[key] = _unquote(value)
            current_list_key = None
    return data, errors


def _structure_errors() -> list[str]:
    """Errores de codificación o estructura del bloque frontmatter."""
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        _, parse_errors = _load_frontmatter(path)
        errors.extend(parse_errors)
    return sorted(errors)


def _title_errors() -> list[str]:
    """Recetas con ``title`` ausente, vacío o con caracteres no UTF-8."""
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        value = data.get("title")
        if value is None:
            errors.append(f"{path.name}: 'title' obligatorio ausente o vacío")
        elif isinstance(value, list):
            errors.append(f"{path.name}: 'title' debe ser string, no lista")
        elif not value.strip():
            errors.append(f"{path.name}: 'title' no debe estar vacío")
        elif _has_non_utf8(value):
            errors.append(f"{path.name}: 'title' contiene caracteres no UTF-8")
    return sorted(errors)


def _positive_int_errors(field: str) -> list[str]:
    """Recetas con ``field`` ausente o que no es entero positivo."""
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        value = data.get(field)
        if value is None:
            errors.append(f"{path.name}: '{field}' obligatorio ausente o vacío")
        elif isinstance(value, list):
            errors.append(f"{path.name}: '{field}' debe ser entero positivo, no lista")
        elif not _INT_RE.match(value.strip()) or int(value.strip()) <= 0:
            errors.append(
                f"{path.name}: '{field}' debe ser entero positivo ('{value}')"
            )
    return sorted(errors)


def _date_errors() -> list[str]:
    """Recetas con ``date`` ausente o fuera del formato ``YYYY-MM-DD``."""
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        value = data.get("date")
        if value is None:
            errors.append(f"{path.name}: 'date' obligatorio ausente o vacío")
        elif isinstance(value, list):
            errors.append(
                f"{path.name}: 'date' debe tener formato YYYY-MM-DD, no lista"
            )
        elif not _DATE_RE.match(value.strip()):
            errors.append(
                f"{path.name}: 'date' debe tener formato YYYY-MM-DD ('{value}')"
            )
        else:
            try:
                datetime.date.fromisoformat(value.strip())
            except ValueError:
                errors.append(f"{path.name}: 'date' no es una fecha válida ('{value}')")
    return sorted(errors)


def _source_errors() -> list[str]:
    """Recetas con ``source`` vacío o sin sección en ``docs/fuentes.md``."""
    known = _fuentes_sections()
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        if "source" not in data:
            continue
        value = data["source"]
        if value is None:
            errors.append(f"{path.name}: 'source' presente pero vacío")
        elif isinstance(value, list):
            errors.append(f"{path.name}: 'source' debe ser string, no lista")
        elif not value.strip():
            errors.append(f"{path.name}: 'source' presente pero vacío")
        elif _has_non_utf8(value):
            errors.append(f"{path.name}: 'source' contiene caracteres no UTF-8")
        elif value.strip() not in known:
            errors.append(
                f"{path.name}: 'source' ('{value.strip()}') "
                "sin sección '##' en docs/fuentes.md"
            )
    return sorted(errors)


def _fuentes_sections() -> set[str]:
    """Títulos de sección ``##`` declarados en ``docs/fuentes.md``."""
    text = SOURCES_FILE.read_bytes().decode("utf-8-sig")
    return set(_H2_RE.findall(text))


def _used_sources() -> set[str]:
    """Valores ``source`` no vacíos usados por al menos una receta."""
    used: set[str] = set()
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        value = data.get("source")
        if isinstance(value, str) and value.strip():
            used.add(value.strip())
    return used


def _orphan_fuentes_sections() -> list[str]:
    """Secciones ``##`` de ``docs/fuentes.md`` sin receta que las use."""
    return sorted(_fuentes_sections() - _used_sources())


def _etiquetas_tags() -> set[str]:
    """Etiquetas ``###`` declaradas en ``docs/etiquetas.md``."""
    text = TAGS_FILE.read_bytes().decode("utf-8-sig")
    return set(_H3_RE.findall(text))


def _used_tags() -> set[str]:
    """Tags no vacíos usados por al menos una receta."""
    used: set[str] = set()
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        value = data.get("tags")
        if isinstance(value, list):
            used.update(item.strip() for item in value if item.strip())
    return used


def _orphan_etiquetas_tags() -> list[str]:
    """Etiquetas ``###`` de ``docs/etiquetas.md`` sin receta que las use."""
    return sorted(_etiquetas_tags() - _used_tags())


def _tags_errors() -> list[str]:
    """Recetas con ``tags`` vacío, inválido o sin etiqueta en ``etiquetas.md``."""
    known = _etiquetas_tags()
    errors: list[str] = []
    for path in sorted(RECIPES_DIR.glob("*.md")):
        data, parse_errors = _load_frontmatter(path)
        if parse_errors:
            continue
        if "tags" not in data:
            continue
        value = data["tags"]
        if value is None:
            errors.append(f"{path.name}: 'tags' presente pero vacío")
        elif isinstance(value, str):
            errors.append(f"{path.name}: 'tags' debe ser lista de strings, no string")
        elif not value:
            errors.append(f"{path.name}: 'tags' presente pero vacío")
        else:
            for item in value:
                if not item.strip():
                    errors.append(f"{path.name}: 'tags' contiene un elemento vacío")
                elif _has_non_utf8(item):
                    errors.append(
                        f"{path.name}: 'tags' contiene caracteres no UTF-8 ('{item}')"
                    )
                elif item.strip() not in known:
                    errors.append(
                        f"{path.name}: 'tags' ('{item.strip()}') "
                        "sin etiqueta '###' en docs/etiquetas.md"
                    )
    return sorted(errors)


def test_frontmatter_bien_formado() -> None:
    """Todo frontmatter debe ser UTF-8 válido y estar entre ``---``."""
    assert _structure_errors() == [], "Frontmatter mal formado:\n" + "\n".join(
        _structure_errors()
    )


def test_title_obligatorio() -> None:
    """Todo ``title`` debe ser string no vacío sin caracteres no UTF-8."""
    assert _title_errors() == [], "Títulos inválidos:\n" + "\n".join(_title_errors())


def test_people_entero_positivo() -> None:
    """Todo ``people`` debe ser entero positivo."""
    errors = _positive_int_errors("people")
    assert errors == [], "'people' inválido:\n" + "\n".join(errors)


def test_time_entero_positivo() -> None:
    """Todo ``time`` debe ser entero positivo."""
    errors = _positive_int_errors("time")
    assert errors == [], "'time' inválido:\n" + "\n".join(errors)


def test_date_formato_yyyy_mm_dd() -> None:
    """Todo ``date`` debe tener formato ``YYYY-MM-DD`` con fecha válida."""
    assert _date_errors() == [], "Fechas inválidas:\n" + "\n".join(_date_errors())


def test_source_no_vacio_si_presente() -> None:
    """Si ``source`` está presente debe ser string no vacío con sección."""
    assert _source_errors() == [], "'source' inválido:\n" + "\n".join(_source_errors())


def test_fuentes_sin_secciones_huerfanas() -> None:
    """Toda sección ``##`` de ``docs/fuentes.md`` debe usarse en un ``source``."""
    orphans = _orphan_fuentes_sections()
    assert orphans == [], "Secciones sin usar en docs/fuentes.md:\n" + "\n".join(
        orphans
    )


def test_tags_lista_no_vacia_si_presente() -> None:
    """Si ``tags`` está presente debe ser lista válida con etiqueta."""
    assert _tags_errors() == [], "'tags' inválido:\n" + "\n".join(_tags_errors())


def test_etiquetas_sin_tags_huerfanos() -> None:
    """Toda etiqueta ``###`` de ``docs/etiquetas.md`` debe usarse en un ``tags``."""
    orphans = _orphan_etiquetas_tags()
    assert orphans == [], "Etiquetas sin usar en docs/etiquetas.md:\n" + "\n".join(
        orphans
    )
