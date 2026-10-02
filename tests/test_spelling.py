"""Tests de corrección ortográfica en español.

Revisa las palabras del recetario (``docs/`` y ``README.md``) contra el
diccionario Hunspell español vendorizado en ``tests/spelling/es_ES`` usando
``spylls`` (port puro Python de Hunspell).

Las palabras que no están en el diccionario y no figuran en
``tests/spelling/allowlist.txt`` se reportan como errores.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
from pathlib import Path

from spylls.hunspell import Dictionary

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "docs"
SPELLING_DIR = Path(__file__).resolve().parent / "spelling"
DICTIONARY = SPELLING_DIR / "es_ES"
ALLOWLIST_FILE = SPELLING_DIR / "allowlist.txt"

# Ficheros Markdown a revisar (recetas, portada y README).
MD_FILES = [*sorted(DOCS_DIR.rglob("*.md")), PROJECT_DIR / "README.md"]

# Fragmentos que no son prosa y no deben revisarse.
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_TARGET = re.compile(r"\]\([^)]*\)")  # quita el destino de [texto](destino)
HTML_TAG = re.compile(r"<[^>]+>")
# Palabras con letras (incl. acentos y eñe).
WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


def _strip_non_prose(text: str) -> str:
    """Elimina código, destinos de enlaces y etiquetas HTML del texto."""
    text = FENCED_CODE.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = LINK_TARGET.sub("] ", text)
    text = HTML_TAG.sub(" ", text)
    return text


def _allowlist() -> set[str]:
    """Palabras permitidas (minúsculas), ignorando comentarios con ``#``."""
    if not ALLOWLIST_FILE.is_file():
        return set()
    allowed: set[str] = set()
    for line in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
        word = line.split("#", 1)[0].strip().lower()
        if word:
            allowed.add(word)
    return allowed


def _words_in(path: Path) -> set[str]:
    """Palabras de un fichero Markdown, ignorando las de una sola letra."""
    text = _strip_non_prose(path.read_text(encoding="utf-8"))
    return {word for word in WORD.findall(text) if len(word) > 1}


def _misspelled() -> dict[str, set[str]]:
    """Palabras no reconocidas por fichero (fuera de la allowlist)."""
    dictionary = Dictionary.from_files(str(DICTIONARY))
    allowed = _allowlist()
    result: dict[str, set[str]] = {}
    for path in MD_FILES:
        unknown = {
            word
            for word in _words_in(path)
            if word.lower() not in allowed and not dictionary.lookup(word)
        }
        if unknown:
            result[str(path.relative_to(PROJECT_DIR))] = unknown
    return result


def test_ortografia() -> None:
    """No debe haber faltas de ortografía fuera de la allowlist."""
    misspelled = _misspelled()
    if misspelled:
        report = "\n".join(
            f"  {path}: {', '.join(sorted(words))}"
            for path, words in sorted(misspelled.items())
        )
        raise AssertionError(
            "Palabras no reconocidas por el diccionario es_ES.\n"
            "Si son correctas (términos culinarios, marcas, nombres propios), "
            "añádelas a tests/spelling/allowlist.txt:\n" + report
        )
