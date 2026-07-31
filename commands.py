import shutil
import subprocess
import sys
from pathlib import Path

UV = Path.home() / ".local" / "bin" / "uv.exe"
PROJECT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run([str(UV)] + list(args), cwd=PROJECT, check=True)


def cmd_serve():
    """Vista previa en http://localhost:8000"""
    run("run", "mkdocs", "serve")


def cmd_build():
    """Genera el sitio en site/"""
    run("run", "mkdocs", "build")


def cmd_clean():
    """Borra site/"""
    site = PROJECT / "site"
    if site.exists():
        shutil.rmtree(site)
        print("site/ eliminado.")
    else:
        print("site/ no existe.")


def cmd_setup():
    """Crea venv e instala dependencias"""
    run("venv")
    run("pip", "install", "mkdocs", "mkdocs-material", "pymdown-extensions")
    print("Venv creado y dependencias instaladas.")


def cmd_fmt():
    """Formatea con ruff"""
    run("run", "ruff", "format", ".")


def cmd_lint():
    """Lint con ruff"""
    run("run", "ruff", "check", ".")


COMMANDS = {
    "serve": cmd_serve,
    "build": cmd_build,
    "clean": cmd_clean,
    "setup": cmd_setup,
    "fmt": cmd_fmt,
    "lint": cmd_lint,
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print("Uso: python commands.py <comando>\n")
        print("Comandos:")
        for name, func in COMMANDS.items():
            desc = func.__doc__ or name
            print(f"  {name:<8} {desc}")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()
