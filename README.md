# reCocina

Recetario de cocina casera generado con **Zensical**.
Cada receta incluye foto, ingredientes y preparación, organizada por categorías en el menú lateral,
con etiquetas de aparatos y dieta, fuentes enlazadas, un par de recetas destacadas cada día en la
portada y funcionamiento sin conexión.

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
2. **Copia la foto** en `docs/fotos` (WebP de 900x600)
3. **Regístrala en el menú**: abre `zensical.toml` y añade la ruta dentro de la categoría
   correspondiente del bloque `nav`:

```toml
nav = [
    { "Arroz" = [
        "recetas/arroz-a-banda-con-sepia.md",
        "recetas/mi-receta-nueva.md", # <- añade esta línea
    ] },
]
```

### Plantilla de receta

Copia y pega en el nuevo `.md` (`title`, `people`, `time` y `date` son obligatorios):

```markdown
---
title:
people:
time:
date:
source: 
tags:
---

## Ingredientes

- 100 g de algo
- 1 unidad de algo más

## Preparación

Describe el primer paso.

Describe el segundo paso.
```

- `people` y `time`: enteros positivos (`time` en minutos). `date`: `YYYY-MM-DD` no futura.
- `source` (opcional): debe tener una sección `##` homónima en `docs/fuentes.md`.
- `tags` (opcional): lista no vacía; cada etiqueta debe tener un `###` homónimo en
  `docs/etiquetas.md`. Sin claves vacías (`source:` sin valor) ni duplicadas.
- La foto no se enlaza en el Markdown: la plantilla la genera a partir del nombre de la
  página (`docs/fotos/<slug>.webp`, WebP de 900x600).
- Secciones opcionales ya usadas en el recetario: `## Opcional`, `## Alternativas`,
  `## Preparación en robot de cocina`.

### Categorías del menú

Además de `Entrada`, `Etiquetas` y `Fuentes`, las recetas se reparten en:

`Aperitivos` · `Arroz` · `Pasta` · `Carne` · `Pollo` · `Pescado y Mariscos` ·
`Verduras, Legumbres y Potajes` · `Sopas y Cremas` · `Salsas` · `Postres`

### Checklist rápida

- [ ] Documento `.md` creado en `docs/recetas/` con frontmatter válido
- [ ] Imagen `.webp` copiada en `docs/fotos` (WebP de 900x600).
- [ ] Ruta añadida al `nav` en `zensical.toml`
- [ ] `source` con su `##` en `docs/fuentes.md` y `tags` con su `###` en `docs/etiquetas.md`
- [ ] Validación con `uv run pytest`
- [ ] Ejecutar `uv run zensical serve` y comprobar que aparece en el menú.

## Validación

Un conjunto de tests comprueba que **recetas ↔ menú ↔ fotos** y los **recursos del sitio** están
sincronizados:

```bash
uv run pytest   # 0 tests fallidos = todo OK
```

`tests/test_frontmatter.py` detecta:

- Frontmatter ausente, YAML inválido o con claves duplicadas.
- `title` vacío, `people`/`time` no enteros positivos o `date` futura o inválida.
- Claves presentes pero vacías (`source:` sin valor) o desconocidas (erratas).
- `source` sin sección `##` homónima en `docs/fuentes.md`.
- `tags` sin entrada `###` homónima en `docs/etiquetas.md`, o títulos de receta repetidos.

`tests/test_recipes.py` detecta:

- Recetas en disco que **no** están en el `nav` (aviso: no se verían en el sitio).
- Entradas del `nav` que apuntan a ficheros inexistentes (error: rompe el build).
- Recetas sin su foto `docs/fotos` (error: la plantilla la genera
  a partir de la dirección de la página).
- Fotos en `docs/fotos` que:
    - No corresponden a ninguna receta (aviso: huérfanas).
    - **Vacías o corruptas** (imágenes muertas).
    - Que **no son WebP** o no miden **900x600**.

`tests/test_theme.py` detecta:

- Favicons del set **ausentes** en `docs/assets/images/`.
- `theme.favicon` sin declarar o apuntando a un fichero inexistente.
- `theme/page.html` sin enlazar algún icono o el manifiesto.
- `site.webmanifest` inválido (JSON roto, rutas no portátiles o iconos inexistentes).

`tests/test_spelling.py` detecta:

- Palabras no reconocidas por el diccionario español `es_ES` (ortografía), fuera de la allowlist.

## Favicon e iconos del sitio

Los iconos viven en `docs/assets/images/` (separados de las fotos de recetas):

- `theme.favicon: assets/images/favicon.ico` en `zensical.toml` fija el `<link rel="icon">`
  principal.
- `theme/page.html` inyecta en el `<head>` el resto (apple-touch-icon, PNG 16/32 y el
  manifiesto).

Para cambiarlos, sustituye los ficheros manteniendo los nombres y ajusta `site.webmanifest` si
cambian los iconos.

## Etiquetas

Las recetas se clasifican en `docs/etiquetas.md` con dos grupos: **aparatos**
(`Batidora`, `Horno`, `Mortero`, `Paellera`, `Wok`) y **dieta** (`Pescetariano`, `Vegano`,
`Vegetariano`). Cada etiqueta del `frontmatter` debe tener su `###` homónimo en ese fichero.

La plantilla `theme/partials/tags.html` las muestra al pie de cada receta y enlaza a
`etiquetas#<slug>`. Los iconos se asignan en `zensical.toml` (`[project.extra.tags]` y
`[project.theme.icon.tag]`).

## Fuentes

Cada `source` del `frontmatter` debe tener una sección `##` homónima en `docs/fuentes.md` con
los datos de la obra o el sitio. La plantilla `theme/main.html` muestra la fuente en los
metadatos de la receta y enlaza a `fuentes#<slug>` (nombre en minúsculas, sin espacios ni
acentos).

## Receta del día

La portada (`docs/index.md`) muestra dos tarjetas diarias en `<div id="daily-recipe">`:

- `scripts/build_recipe_index.py` genera `docs/assets/recetas.json` con `slug`, `title`,
  `people` y `time` de cada receta.
- `docs/assets/javascripts/daily-recipe.js` elige dos recetas con sorteo diario fijo (misma
  selección durante todo el día) y dibuja las tarjetas con foto, comensales y tiempo.

## PWA y modo sin conexión

El sitio se puede instalar como aplicación y sirve las páginas visitadas sin conexión:

- `docs/sw.js`: trabajador de servicio que sirve de la caché y actualiza en segundo plano;
  al instalar la aplicación pide la carga inicial completa (`PRECACHE`).
- `docs/site.webmanifest`: nombre, colores e iconos de la aplicación.
- `scripts/build_precache.py`: tras la construcción genera `site/precache.json` con las
  direcciones a precargar.
- `vercel.json` sirve `/sw.js` con `Cache-Control: no-cache` para que las actualizaciones
  lleguen siempre.

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

Un hook ejecuta la validación **automáticamente antes de cada commit**: si el lint (`ruff check`),
el formato Python (`ruff format --check`) o los tests (`pytest`) fallan, el commit se cancela.

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

| Comando                                       | Qué hace                                                    |
|-----------------------------------------------|-------------------------------------------------------------|
| `uv sync`                                     | Instala o actualiza dependencias de proyecto                |
| `uv run zensical serve`                       | Previsualiza en <http://localhost:8000> con recarga en vivo |
| `uv run python scripts/build_recipe_index.py` | Genera `docs/assets/recetas.json` para la receta del día    |
| `uv run zensical build --strict`              | Genera el sitio en `site/`; aborta ante avisos de build     |
| `uv run python scripts/build_precache.py`     | Genera `site/precache.json` para el service worker          |
| `uv run pytest`                               | Valida frontmatter, recetas, `nav`, fotos y ortografía      |
| `uv run pre-commit install`                   | Activa el hook de pre-commit (una sola vez)                 |
| `uv run pre-commit run --all-files`           | Ejecuta lint + formato + tests sobre todo el repo           |
| `uv run ruff format .`                        | Formatea el código Python                                   |
| `uv run ruff check .`                         | Analiza (lint) el código Python                             |

## Estructura

```
.
├── docs/
│   ├── assets/
│   │   ├── icons/            # Iconos SVG
│   │   ├── images/           # Imágenes de interfaz web
│   │   ├── javascripts/      # Scripts
│   │   └── stylesheets/      # Hojas de estilo
│   ├── fotos/                # Fotos de recetas (WebP 900x600, mismo nombre que el .md)
│   ├── recetas/              # Recetas (.md con frontmatter)
│   ├── etiquetas.md          # Taxonomía de etiquetas (aparatos y dieta)
│   ├── fuentes.md            # Fuentes citadas por las recetas
│   ├── index.md              # Portada (con receta del día)
│   ├── site.webmanifest      # Manifiesto PWA
│   └── sw.js                 # Service worker (modo sin conexión)
├── scripts/
│   ├── build_precache.py     # Genera site/precache.json tras el build
│   └── build_recipe_index.py # Genera docs/assets/recetas.json antes del build
├── theme/                    # Overrides de plantillas (custom_dir de Zensical)
│   ├── partials/
│   │   ├── header.html       # Cabecera sin el bloque "source"
│   │   ├── tags.html         # Etiquetas con iconos y enlaces a etiquetas.md
│   │   └── copyright.html    # Pie: "Creado con Zensical"
│   ├── main.html             # Recetas: foto, metadatos, fuente y etiquetas
│   └── page.html             # Base: favicons, manifiesto, SW y nav sin TOC lateral
├── tests/
│   ├── spelling/             # Diccionario es_ES + allowlist + licencias
│   ├── support.py            # Rutas y esquema del frontmatter (pydantic)
│   ├── test_frontmatter.py   # Valida frontmatter ↔ fuentes ↔ etiquetas
│   ├── test_recipes.py       # Valida recetas ↔ nav ↔ fotos (pytest)
│   ├── test_spelling.py      # Corrección ortográfica es_ES (pytest)
│   └── test_theme.py         # Valida favicons y recursos del sitio (pytest)
├── .pre-commit-config.yaml   # Hooks de pre-commit (lint + formato + tests)
├── pyproject.toml            # Dependencias y configuración de ruff/pytest
├── vercel.json               # Configuración de despliegue
└── zensical.toml             # Configuración del sitio y del menú (nav)
```

## Despliegue

Vercel despliega automáticamente desde la rama `main`. `vercel.json` encadena el pipeline
completo y publica el contenido de `site/`:

```bash
uv run python scripts/build_recipe_index.py # índice para la receta del día
uv run zensical build --strict              # build estricto (aborta ante avisos)
uv run python scripts/build_precache.py     # precache para el service worker
```

## Notas

- Interfaz en español (`language = "es"` en `zensical.toml`).
- Plantillas personalizadas en `theme/`: al actualizar Zensical, compararlas con las nuevas.
- Paleta de colores centralizada en `docs/assets/stylesheets` (variables `--rc-*` en
  `:root`).
- Nombres de archivo en kebab-case y sin acentos (ej. `sopa-de-melon.md`).
