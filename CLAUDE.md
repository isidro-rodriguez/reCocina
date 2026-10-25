# CLAUDE.md

Operational rules for AI agents and contributors working **on** this repo.
`README.md` is the source of truth for **usage** (quick start, recipe template) — don't
duplicate it here. Quality and build commands live in this file.

## Agent behavior

- **No retry loops:** don't re-run a failing command more than twice. Stop, state the root cause,
  ask.
- **Be concise:** no filler, no long intros, no repetition. Batch independent edits/commands.
- **Surgical edits:** change only what's needed; never rewrite a whole recipe or file for a small
  fix.
- **Self-contained:** prefer one-shot commands and complete diffs over exploratory back-and-forth.
- Don't run state-changing or destructive git commands unless explicitly asked.

## Code style & language

- Python 3.12+. Package manager: **uv only** (`uv run`, `uv add`, `uv sync`) — never raw `pip`
  (unless inside an isolated venv).
- **Code:** English identifiers and structure.
- **Human-facing text:** Spanish — docstrings, comments, user/UI output, and the recipes themselves.
- Idiomatic Python: PEP 8, `pathlib` over `os.path`.
- **Strict type hints** on every signature; `ty check` must pass.
- **Docstrings** Google-style: complete for public functions, one line for private/nested ones.
  A public docstring lists in `Raises` the exceptions raised by the private functions it calls.
- **Comments** explain the _why_, never the _what_.
- **ruff is the boss:** `target-version = py312`, `line-length = 88`, rules
  `E, F, I, UP, B, D, SIM, PTH`, pydocstyle `google`; excludes `site/` and `docs_templates/`.

## Web assets (CSS/JS/HTML)

- `docs/assets/stylesheets/*.css`, `docs/assets/javascripts/*.js`, `docs/sw.js`: **LF, trailing
  newline**. No auto-formatter configured — match the existing style by hand.
- `docs_templates/*.html` (Jinja): no formatter configured — keep partials aligned manually (LF).
- Line endings are forced to LF per extension by `.gitattributes` (canonical file + reCocina
  section); a new text file type needs its own `eol=lf` rule. Don't rely on `core.autocrlf`.
- New JS/CSS must be registered in `zensical.toml` (`extra_javascript` / `extra_css`), e.g.
  `daily-recipe.js` (recetas del día de la portada), `kitchen-mode.js` (modo cocina) and
  `recipe-steps.js` (ingredientes que se tachan y paso actual; estado en `sessionStorage`).
  `daily-recipe.js` reads `assets/recetas.json`, produced by `scripts/build_recipe_index.py` —
  never hand-edit that JSON.

## Quality policy — Definition of Done

Nothing is "done" until every applicable gate is green:

| Gate          | Command                                                                                                                                      | When                                        |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Python lint   | `uv run ruff check .`                                                                                                                        | any `.py` change                            |
| Python format | `uv run ruff format --check .`                                                                                                               | any `.py` change                            |
| Type check    | `uv run ty check`                                                                                                                            | any `.py` change                            |
| Tests         | `uv run pytest`                                                                                                                              | any change                                  |
| Strict build  | `uv run zensical build --strict` (+ `scripts/build_recipe_index.py` before, `scripts/build_precache.py` after — full chain in `vercel.json`) | any `zensical.toml`/`docs/`/`docs_templates/` change |
| Everything    | `uv run pre-commit run --all-files` (ruff check, ruff format --check, pytest)                                                                | before finishing                            |

CI (`.github/workflows/ci.yml`) runs on push/PR (ubuntu + windows): `pre-commit run --all-files`,
`ty check` and the full strict build chain — keep `main` green.

**Poe shortcuts** (optional; `poe` installed globally with `uv tool install poethepoet`, tasks in
`pyproject.toml` `[tool.poe]`). `uv run …` stays the canonical form; never add poe as a dependency.

| Task         | Equivalent                                                                |
| ------------ | ------------------------------------------------------------------------- |
| `poe check`  | ruff format --check, ruff check, ty check, pytest                         |
| `poe fix`    | ruff format, ruff check --fix                                             |
| `poe build`  | `build_recipe_index.py` → `zensical build --strict` → `build_precache.py` |
| `poe serve`  | `build_recipe_index.py` → `zensical serve`                                |
| `poe backup` | `scripts/backup.py` (`<name>-<timestamp>.bundle` in the repo root)        |

Checklist before handing off:

- [ ] `poe check` (or `uv run pre-commit run --all-files` + `uv run ty check`) passes.
- [ ] `poe build` (or the chain in `vercel.json`) has no errors.
- [ ] Legit new words (dishes, brands, proper nouns, tech terms used in prose) added to
      `tests/spelling/allowlist.txt` (code spans and fenced blocks are skipped by the test).
- [ ] No `git commit --no-verify` unless the user explicitly asks.

## Content conventions (recipes)

- One recipe = `docs/recetas/<kebab-case-no-accents>.md` + `docs/fotos/<slug>.webp` (WebP de
  900x600) + an entry in `zensical.toml` `nav`. Missing any of the three fails the tests.
- Filename kebab-case **without** accents (ej. `sopa-de-melon.md`); `title` in frontmatter is the
  display name **with accents**.
- Mandatory frontmatter (`tests/support.py` schema): `title` (non-empty), `people`/`time`
  (strict positive ints, `time` in minutes), `date` (`YYYY-MM-DD`, not in the future). Optional:
  `source` (must match a `##` in `docs/fuentes.md`), `tags` (non-empty list, each must match a
  `###` in `docs/etiquetas.md`). No empty values (`source:` with nothing), no duplicated keys,
  no unknown keys.
- Body sections: `## Ingredientes`, `## Preparación`. Optional ones already in use: `## Opcional`,
  `## Alternativas`.
- Image is auto-rendered by `docs_templates/main.html` from `fotos/<slug>.webp` — never link it in
  Markdown.
- Nav categories (the `nav` in `zensical.toml` is the source of truth for names and order):
  `Entrada` (`index.md`), `Etiquetas` (`etiquetas.md`), `Fuentes` (`fuentes.md`), `Glosario`
  (`glosario.md`), then the recipe sections.
- Tags taxonomy lives in `docs/etiquetas.md`: aparatos (`Batidora`, `Horno`, `Mortero`,
  `Paellera`, `Wok`) + dieta (`Pescetariano`, `Vegano`, `Vegetariano`); icons mapped in
  `zensical.toml` (`[project.extra.tags]`, `[project.theme.icon.tag]`).
- **Units:** prefer ISO 80000 (`g`, `l`, `ml`, space before unit: `100 g de …`). Don't rewrite
  existing recipes just to normalize this.
- Generated artifacts are gitignored: `docs/assets/recetas.json` (from
  `scripts/build_recipe_index.py`), `site/` incl. `precache.json` (from
  `scripts/build_precache.py`), `*.bundle` (from `scripts/backup.py`).

## Tests contract

- `tests/support.py` — shared paths + frontmatter schema (`Recipe` pydantic model); single source
  of truth for `load_frontmatter` / `headings`.
- `tests/test_frontmatter.py` — frontmatter valid; no orphans (every `source` → `##` in
  `docs/fuentes.md`, every tag → `###` in `docs/etiquetas.md`); no duplicated titles.
- `tests/test_recipes.py` — recipes ⇄ nav ⇄ photos in sync; no broken/dead/orphan images; photos
  must be 900x600 WebP.
- `tests/test_spelling.py` — Spanish spelling (spylls + vendored `es_ES`); unknown words must be in
  `tests/spelling/allowlist.txt`. Skips fenced/inline code, link targets and HTML tags.

## Don't touch

- `uv.lock` (regenerate with uv, never hand-edit). `tests/spelling/es_ES.*` + `LICENSE/` (vendored
  dictionary).
- Respect `.gitignore` (`.venv/`, `site/`, `docs/assets/recetas.json`, `*.bundle`, …). Don't
  commit build output.

## Commits

Conventional Commits, Spanish: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`. One intent per
commit.

## Deploy

Vercel auto-deploys from `main` via `vercel.json` (`uv sync` +
`uv run python scripts/build_recipe_index.py && uv run zensical build --strict &&
uv run python scripts/build_precache.py`, output `site/`; `Cache-Control: no-cache` on `/sw.js`).
Keep it working.
