# reCocina

Recetario de cocina casera generado con **MkDocs** y el tema **Material**.
Cada receta incluye foto, ingredientes y preparación, organizada por categorías en el menú lateral.

> **¿Hace mucho que no añades recetas?** Ve directo a [Guía rápida](#guía-rápida) y [Añadir una receta](#añadir-una-receta).

## Guía rápida

```bash
uv sync                 # 1. Prepara el entorno (primera vez o tras cambiar dependencias)
uv run mkdocs serve     # 2. Previsualiza en http://localhost:8000 (recarga en vivo)
uv run mkdocs build     # 3. Genera el sitio estático en site/
```

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12+ (uv lo gestiona solo).

## Añadir una receta

Tres pasos:

1. **Crea el archivo** `docs/recetas/<nombre-en-kebab-case>.md`
2. **Copia la foto** en `docs/img/fotos/<mismo-nombre>.jpg`
3. **Regístrala en el menú**: abre `mkdocs.yml` y añade la ruta dentro de la categoría correspondiente del bloque `nav`:

```yaml
nav:
- Arroz:
  - recetas/arroz-a-banda-con-sepia.md
  - recetas/mi-receta-nueva.md   # <- añade esta línea
```

> ⚠️ El paso 3 es el que más se olvida: si la receta no está en el `nav`, no aparecerá en la barra lateral aunque el archivo exista. Los [tests](#validación) lo detectan por ti.

### Plantilla de receta

Copia y pega en el nuevo `.md`:

```markdown
# Nombre de la receta

![Nombre de la receta](../img/fotos/nombre-de-la-receta.jpg)

## Ingredientes

- 100 g de algo
- 1 unidad de algo más

## Preparación

Describe el primer paso.

Describe el segundo paso.
```

- La ruta de la foto es siempre `../img/fotos/<slug>.jpg` (las recetas están planas en `docs/recetas/`).
- Secciones opcionales ya usadas en el recetario: `## Opcional`, `## Alternativas`, `## Preparación en robot de cocina`.

### Categorías del menú

`Aperitivos` · `Arroz` · `Pasta` · `Carne y Pollo` · `Pescado y Mariscos` · `Verduras, Legumbres y Potajes` · `Sopas y Cremas` · `Salsas` · `Postres`

### Checklist rápida

- [ ] `.md` creado en `docs/recetas/`
- [ ] `.jpg` copiado en `docs/img/fotos/`
- [ ] ruta añadida al `nav` en `mkdocs.yml`
- [ ] validación en verde (`uv run pytest`)
- [ ] `uv run mkdocs serve` y comprobar que aparece en el menú

## Validación

Un único test comprueba que **recetas ↔ menú ↔ fotos** están sincronizados:

```bash
uv run pytest   # 0 tests fallidos = todo OK
```

Detecta:

- recetas en disco que **no** están en el `nav` (aviso: no se verían en el sitio)
- entradas del `nav` que apuntan a ficheros inexistentes (error: rompe el build)
- imágenes enlazadas desde una receta que **no existen** (error)
- fotos en `docs/img/fotos/` que ninguna receta usa (aviso: huérfanas)
- fotos en `docs/img/fotos/` **vacías o corruptas** (imágenes muertas)

## Hook pre-commit

Un hook ejecuta la validación **automáticamente antes de cada commit**: si el lint
(`ruff check`), el formato (`ruff format --check`) o los tests (`pytest`) fallan, el
commit se cancela.

Instálalo una sola vez (tras `uv sync`):

```bash
uv run pre-commit install
```

A partir de ahí, cada `git commit` lanza los hooks. Para ejecutarlos a mano sobre todo el
repositorio:

```bash
uv run pre-commit run --all-files
```

> Si necesitas saltarte el hook puntualmente (no recomendado): `git commit --no-verify`.

## Comandos

| Comando | Qué hace |
| --- | --- |
| `uv sync` | Instala/actualiza dependencias desde `pyproject.toml` + `uv.lock` |
| `uv run mkdocs serve` | Previsualiza en http://localhost:8000 con recarga en vivo |
| `uv run mkdocs build --strict` | Genera el sitio en `site/`; falla ante enlaces internos rotos |
| `uv run pytest` | Valida que recetas, `nav` y fotos están sincronizados |
| `uv run pre-commit install` | Activa el hook de pre-commit (una sola vez) |
| `uv run pre-commit run --all-files` | Ejecuta lint + formato + tests sobre todo el repo |
| `uv run ruff format .` | Formatea el código Python |
| `uv run ruff check .` | Analiza (lint) el código Python |

## Estructura

```
.
├── mkdocs.yml              # Configuración del sitio y del menú (nav)
├── pyproject.toml          # Dependencias y configuración de ruff/pytest
├── uv.lock                 # Versiones fijadas (no editar a mano)
├── .pre-commit-config.yaml # Hooks de pre-commit (lint + formato + tests)
├── vercel.json             # Configuración de despliegue
├── AGENTS.md               # Contexto del proyecto
├── theme/                  # Overrides del tema Material
│   └── partials/copyright.html
├── tests/
│   └── test_recipes.py     # Valida recetas ↔ nav ↔ fotos (pytest)
└── docs/
    ├── index.md            # Portada
    ├── recetas/            # Recetas (archivos .md planos)
    └── img/
        ├── fotos/          # Fotos de las recetas (mismo nombre que el .md)
        └── ...             # Favicons del sitio
```

## Despliegue

Vercel despliega automáticamente desde la rama `main`: `vercel.json` ejecuta `uv sync` e `uv run mkdocs build --strict`, y publica el contenido de `site/`.

## Notas

- Interfaz en español (`language: es` en `mkdocs.yml`).
- Tema Material personalizado en `theme/partials/copyright.html`.
- Nombres de archivo en kebab-case y sin acentos (ej. `sopa-de-melon.md`).
