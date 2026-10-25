# reCocina

Recetario de cocina casera generado con **Zensical**.

## Guía rápida

```bash
# Prepara el entorno (primera vez o tras cambiar dependencias)
uv tool install poethepoet
uv sync
# Previsualiza en http://localhost:8000 (recarga en vivo)
uv run zensical serve
# Genera el sitio estático en site/
uv run zensical build
# Cuando añadas o modifiques una receta
poe check
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

Copia y pega en el nuevo `.md` (`title`, `people`, `time` y `date` son obligatorios;
`source` y `tags` solo si la receta los necesita — nunca dejes claves vacías):

```markdown
---
title:
people:
time:
date:
# source:
# tags:
---

## Ingredientes

- 100 g de algo
- 1 unidad de algo más

## Preparación

Describe el primer paso.

Describe el segundo paso.
```

- `title`: nombre de la receta.
- `people`: número de comensales de la receta (entero positivo).
- `time`: tiempo, en minutos, aproximado de elaboración (entero positivo).
- `date`: fecha en que se añade la receta (`AAAA-MM-DD`, no futura).
- `source`: fuente de la que se obtuvo la receta (opcional, requiere sección homónima en `docs/fuentes.md`).
- `tags`: lista de etiquetas (opcional, cada etiqueta requiere entrada homónima en `docs/etiquetas.md`).

> Quita el `#` de `source` y `tags` solo si vas a utilizarlos.
