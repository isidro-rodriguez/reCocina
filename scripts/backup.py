"""Copia de seguridad manual de reCocina.

Limpia cachés `__pycache__` y comprime el código fuente en un zip
ubicado en `local/backup.zip`.

Uso:
    uv run python scripts/backup.py
"""

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "local"
BACKUP_PATH = BACKUP_DIR / "recocina.zip"

# Directorios cuya estructura se incluye completa.
DIRS = [".github", "docs", "scripts", "tests", "theme"]

# Patrones de ficheros sueltos de raíz a incluir.
ROOT_PATTERNS = [
    ".gitattributes",
    ".gitignore",
    "*.json",
    "*.lock",
    "*.md",
    "*.py",
    "*.toml",
    "*.yaml",
]


def _limpiar_pycache() -> int:
    """Borra todos los directorios `__pycache__` bajo `ROOT`. Devuelve el count."""
    eliminados = 0
    for ruta in ROOT.rglob("__pycache__"):
        if ruta.is_dir():
            for hijo in sorted(ruta.rglob("*"), reverse=True):
                hijo.unlink(missing_ok=True)
            ruta.rmdir()
            eliminados += 1
    return eliminados


def _crear_zip() -> None:
    """Crea el zip con los directorios y los ficheros de raíz seleccionados."""
    with zipfile.ZipFile(BACKUP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for nombre_dir in DIRS:
            dir_path = ROOT / nombre_dir
            if not dir_path.exists():
                continue
            for archivo in dir_path.rglob("*"):
                if archivo.is_file():
                    zf.write(archivo, archivo.relative_to(ROOT))

        for patron in ROOT_PATTERNS:
            for archivo in ROOT.glob(patron):
                if archivo.is_file():
                    zf.write(archivo, archivo.relative_to(ROOT))


def main() -> None:
    """Limpia las cachés, crea la copia de seguridad e informa del resultado."""
    print("Limpiando cachés __pycache__...")
    n_cache = _limpiar_pycache()
    print(f"  {n_cache} directorios __pycache__ eliminados")

    print("Creando copia de seguridad...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if BACKUP_PATH.exists():
        BACKUP_PATH.unlink()
    _crear_zip()

    size = BACKUP_PATH.stat().st_size
    print(f"  {BACKUP_PATH} ({size:,} bytes)")


if __name__ == "__main__":
    main()
