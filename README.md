# reCocina

Recetario de cocina casera generado con **MkDocs** y el tema **Material**.

## Estructura

```bash
.
├── AGENTS.md               # Contexto del proyecto
├── mkdocs.yml              # Configuración de MkDocs
├── theme/                  # Overrides del tema Material
│   └── partials/
│       └── copyright.html
├── docs/
│   ├── index.md            # Página de entrada
│   ├── assets/fotos/       # Fotos de recetas
│   └── recetas/            # Recetas organizadas por categoría
│       ├── aperitivos/
│       ├── arroz/
│       ├── carne/
│       ├── pasta/
│       ├── pescado-mariscos/
│       ├── postres/
│       ├── salsas/
│       ├── sopas-cremas/
│       └── verduras-legumbres/
├── commands.py             # Script de comandos del proyecto
├── .gitignore
└── README.md
```

## Comandos principales

```powershell
python commands.py serve    # Vista previa en http://localhost:8000
python commands.py build    # Genera el sitio en site/
python commands.py clean    # Borra site/
python commands.py setup    # Crea venv e instala dependencias
python commands.py fmt      # Formatea con ruff
python commands.py lint     # Lint con ruff
```

## Cómo añadir recetas

Añade directamente los archivos `.md` en `docs/recetas/<categoria>/`. La foto se muestra con la ruta relativa `../../assets/fotos/<nombre>.jpg`.

Las categorías disponibles son:

- `aperitivos`
- `arroz`
- `pasta`
- `carne`
- `pescado-mariscos`
- `verduras-legumbres`
- `sopas-cremas`
- `salsas`
- `postres`

Ejemplo mínimo de receta:

```markdown
# Nombre de la receta

![Nombre de la receta](../../assets/fotos/foto.jpg)

## Ingredientes

- 100 g de algo

## Preparación

1. Paso uno
2. Paso dos
```

## Notas

- El tema Material está personalizado en `theme/partials/copyright.html`.
- La interfaz está en español (`language: es` en `mkdocs.yml`).
- Añade recetas directamente en `docs/recetas/<categoria>/`.
