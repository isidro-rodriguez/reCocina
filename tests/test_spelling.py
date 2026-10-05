"""Tests de corrección ortográfica en español.

Revisa las palabras del recetario (``docs/`` y ``README.md``) contra el
diccionario Hunspell vendorizado en ``tests/spelling/es_ES`` con ``spylls``.
Las palabras desconocidas que no figuren en ``tests/spelling/allowlist.txt``
se reportan como errores.

Ejecutar con::

    uv run pytest
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import pytest
from spylls.hunspell import Dictionary
from support import DOCS_DIR, PROJECT_DIR, read_text

SPELLING_DIR = Path(__file__).resolve().parent / "spelling"
DICTIONARY = SPELLING_DIR / "es_ES"
ALLOWLIST_FILE = SPELLING_DIR / "allowlist.txt"

MD_FILES = [*sorted(DOCS_DIR.rglob("*.md")), PROJECT_DIR / "README.md"]

# Fragmentos que no son prosa y no deben revisarse.
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")  # quita el destino de [texto](destino)
_HTML_TAG = re.compile(r"<[^>]+>")
_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,}")


def _strip_non_prose(text: str) -> str:
    """Elimina código, destinos de enlaces y etiquetas HTML."""
    for pattern, replacement in (
        (_FENCED_CODE, " "),
        (_INLINE_CODE, " "),
        (_LINK_TARGET, "] "),
        (_HTML_TAG, " "),
    ):
        text = pattern.sub(replacement, text)
    return text


@cache
def _allowlist() -> frozenset[str]:
    """Palabras permitidas (minúsculas), ignorando comentarios con ``#``."""
    if not ALLOWLIST_FILE.is_file():
        return frozenset()
    lines = ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines()
    words = (line.split("#", 1)[0].strip().lower() for line in lines)
    return frozenset(word for word in words if word)


@pytest.fixture(scope="module")
def dictionary() -> Dictionary:
    """Diccionario Hunspell cargado una sola vez por módulo."""
    return Dictionary.from_files(str(DICTIONARY))


@pytest.mark.parametrize(
    "path", MD_FILES, ids=lambda p: str(p.relative_to(PROJECT_DIR))
)
def test_ortografia(path: Path, dictionary: Dictionary) -> None:
    """El fichero no tiene faltas fuera de la allowlist."""
    words = set(_WORD.findall(_strip_non_prose(read_text(path))))
    unknown = sorted(
        word
        for word in words
        if word.lower() not in _allowlist() and not dictionary.lookup(word)
    )
    assert not unknown, (
        "Palabras no reconocidas por es_ES. Si son correctas (términos "
        "culinarios, marcas, nombres propios), añádelas a "
        f"tests/spelling/allowlist.txt: {', '.join(unknown)}"
    )
