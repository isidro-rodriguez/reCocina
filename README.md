# reCocina

Recetario de cocina casera generado con **Zensical** (variante `classic`, con la estética de Material for MkDocs).
Cada receta incluye foto, ingredientes y preparación, organizada por categorías en el menú lateral.

## Guía rápida

```bash
uv sync                 # 1. Prepara el entorno (primera vez o tras cambiar dependencias)
uv run zensical serve   # 2. Previsualiza en http://localhost:8000 (recarga en vivo)
uv run zensical build   # 3. Genera el sitio estático en site/
```

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12+ (uv lo gestiona solo).

## Añadir una receta

Tres pasos:

1. **Crea el archivo** `docs/recetas/<nombre-en-kebab-case>.md`
2. **Copia la foto** en `docs/img/fotos/<mismo-nombre>.webp` (WebP de 900x600)
3. **Regístrala en el menú**: abre `zensical.toml` y añade la ruta dentro de la categoría correspondiente del bloque `nav`:

```toml
nav = [
  { "Arroz" = [
    "recetas/arroz-a-banda-con-sepia.md",
    "recetas/mi-receta-nueva.md",   # <- añade esta línea
  ] },
]
```

### Plantilla de receta

Copia y pega en el nuevo `.md`:

```markdown
# Nombre de la receta

![Nombre de la receta](../img/fotos/nombre-de-la-receta.webp)

## Ingredientes

- 100 g de algo
- 1 unidad de algo más

## Preparación

Describe el primer paso.

Describe el segundo paso.
```

- La ruta de la foto es siempre `../img/fotos/<slug>.webp` (las recetas están planas en `docs/recetas/`). Las fotos son WebP de 900x600.
- Secciones opcionales ya usadas en el recetario: `## Opcional`, `## Alternativas`, `## Preparación en robot de cocina`.

### Categorías del menú

`Aperitivos` · `Arroz` · `Pasta` · `Carne y Pollo` · `Pescado y Mariscos` · `Verduras, Legumbres y Potajes` · `Sopas y Cremas` · `Salsas` · `Postres`

### Checklist rápida

- [ ] Documento `.md` creado en `docs/recetas/`
- [ ] Imagen `.webp` copiada en `docs/img/fotos/` (WebP de 900x600).
- [ ] Ruta añadida al `nav` en `zensical.toml`
- [ ] Validación con `uv run pytest`
- [ ] Ejecutar `uv run zensical serve` y comprobar que aparece en el menú.

## Validación

Un conjunto de tests comprueba que **recetas ↔ menú ↔ fotos** y los **recursos del sitio** están sincronizados:

```bash
uv run pytest   # 0 tests fallidos = todo OK
```

`tests/test_recipes.py` detecta:

- recetas en disco que **no** están en el `nav` (aviso: no se verían en el sitio).
- entradas del `nav` que apuntan a ficheros inexistentes (error: rompe el build).
- imágenes enlazadas desde una receta que **no existen** (error).
- fotos en `docs/img/fotos/` que:
    - Ninguna receta usa (aviso: huérfanas).
    - **Vacías o corruptas** (imágenes muertas).
    - Que **no son WebP** o no miden **900x600**.

`tests/test_theme.py` detecta:

- Favicons del set **ausentes** en `docs/img/favicon/`.
- `theme.favicon` sin declarar o apuntando a un fichero inexistente.
- `theme/main.html` sin enlazar algún icono o el manifiesto.
- `site.webmanifest` inválido (JSON roto, rutas no portátiles o iconos inexistentes).

`tests/test_spelling.py` detecta:

- palabras no reconocidas por el diccionario español `es_ES` (ortografía), fuera de la allowlist.

## Favicon e iconos del sitio

Los iconos viven en `docs/img/favicon/` (separados de las fotos de recetas):

- `theme.favicon: img/favicon/favicon.ico` en `zensical.toml` fija el `<link rel="icon">` principal.
- `theme/main.html` inyecta en el `<head>` el resto (apple-touch-icon, PNG 16/32 y el manifiesto).

Para cambiarlos, sustituye los ficheros manteniendo los nombres y ajusta `site.webmanifest` si cambian los iconos.

## Linteo y formato de Markdown

El Markdown (recetas y este README) se formatea con **mdformat** y el plugin
**mdformat-mkdocs** (que entiende la sintaxis de MkDocs/Material: admoniciones, pestañas…).
La configuración vive en `.mdformat.toml`.

```bash
uv run mdformat docs README.md          # aplica el formato (bullets -, etc.)
uv run mdformat --check docs README.md  # comprueba sin modificar (falla si no está formateado)
```

> El hook de pre-commit ya ejecuta `mdformat --check`, así que basta con formatear antes de commitear.

## Corrección ortográfica

El recetario se revisa con **spylls**, una implementación en Python de Hunspell, y el
diccionario español `es_ES` incluido en `tests/spelling/`. El test `tests/test_spelling.py`
lo ejecuta junto al resto de la suite:

```bash
uv run pytest   # incluye la comprobación ortográfica
```

- Las palabras que el diccionario no conoce (términos culinarios, marcas, préstamos,
    formas verbales con pronombre…) se aceptan desde `tests/spelling/allowlist.txt`.
- Para permitir una palabra válida, añádela a ese fichero (una por línea; `#` para comentarios).

## Hook pre-commit

Un hook ejecuta la validación **automáticamente antes de cada commit**: si el lint
(`ruff check`), el formato Python (`ruff format --check`), el formato Markdown
(`mdformat --check`) o los tests (`pytest`) fallan, el commit se cancela.

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

| Comando                                  | Qué hace                                                          |
| ---------------------------------------- | ----------------------------------------------------------------- |
| `uv sync`                                | Instala/actualiza dependencias desde `pyproject.toml` + `uv.lock` |
| `uv run zensical serve`                  | Previsualiza en <http://localhost:8000> con recarga en vivo       |
| `uv run zensical build --strict`         | Genera el sitio en `site/`; aborta ante avisos de build           |
| `uv run pytest`                          | Valida que recetas, `nav` y fotos están sincronizados             |
| `uv run mdformat docs README.md`         | Formatea el Markdown (recetas y README)                           |
| `uv run mdformat --check docs README.md` | Comprueba el formato del Markdown sin modificar                   |
| `uv run pre-commit install`              | Activa el hook de pre-commit (una sola vez)                       |
| `uv run pre-commit run --all-files`      | Ejecuta lint + formato + tests sobre todo el repo                 |
| `uv run ruff format .`                   | Formatea el código Python                                         |
| `uv run ruff check .`                    | Analiza (lint) el código Python                                   |

## Estructura

```
.
├── docs/
│   ├── css/extra.css       # Paleta de colores (--rc-*) y maquetación
│   ├── img/
│   │   ├── fotos/          # Fotos de las recetas (mismo nombre que el .md)
│   │   └── favicon/        # Favicons e iconos del sitio
│   ├── recetas/            # Recetas (archivos .md planos)
│   └── index.md            # Portada
├── theme/                  # Overrides de plantillas (custom_dir de Zensical)
│   ├── partials/
│   │   ├── header.html     # Cabecera sin el bloque "source"
│   │   └── copyright.html  # Pie: "Creado con Zensical"
│   └── main.html           # <head>: favicons; bloque site_nav sin TOC lateral
├── tests/
│   ├── spelling/           # Diccionario es_ES + allowlist + licencias
│   ├── test_recipes.py     # Valida recetas ↔ nav ↔ fotos (pytest)
│   ├── test_spelling.py    # Corrección ortográfica es_ES (pytest)
│   └── test_theme.py       # Valida favicons y recursos del sitio (pytest)
├── .pre-commit-config.yaml # Hooks de pre-commit (lint + formato + tests)
├── .mdformat.toml          # Configuración de mdformat (formato de Markdown)
├── pyproject.toml          # Dependencias y configuración de ruff/pytest
├── vercel.json             # Configuración de despliegue
└── zensical.toml           # Configuración del sitio y del menú (nav)
```

## Despliegue

Vercel despliega automáticamente desde la rama `main`: `vercel.json` ejecuta `uv sync` e `uv run zensical build --strict`, y publica el contenido de `site/`.

## Notas

- Interfaz en español (`language = "es"` en `zensical.toml`).
- Plantillas personalizadas en `theme/`: son copias de las de Zensical v0.0.67 (marcadas con su versión de origen); al actualizar Zensical, compararlas con las nuevas.
- Paleta de colores centralizada en `docs/css/extra.css` (variables `--rc-*` en `:root`).
- Nombres de archivo en kebab-case y sin acentos (ej. `sopa-de-melon.md`).
