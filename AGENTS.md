# AGENTS.md

Instructions for AI agents working on **reCocina**: Recetario de cocina casera generado con
Zensical.

The shared sections below are the same in every project. Project-specific rules are at the
end, under **Project rules**, and take precedence when they differ.

<!-- shared:start — managed by assistant-skills/new-python-project (scaffold.py sync). Edit there, not here. -->
## Shared rules

**Language.** Code and identifiers in English. Docstrings, comments, README, `docs/`,
CHANGELOG, commits and user-facing messages in Spanish. This file stays in English.

**Tools.** `uv` only, never `pip install`; run everything from the project root.
Quality gate: `uv run ruff format --check .`, `uv run ruff check .`, `uv run ty check`,
`uv run pytest`. The same gate as `poe check`, if Poe the Poet is installed globally; poe is
never a project dependency, and everything must also work with plain `uv run`.

**Workflow.**

1. Read `README.md`, `pyproject.toml`, this file and the related tests before changing code.
2. Make the smallest change that solves the task: no unrelated refactors, no formatting of
   untouched files, no new dependency without a reason (prefer the standard library).
3. Don't change CI, tool configuration or project structure unless the task needs it.
4. Don't run a failing command more than twice: stop, give the root cause and the exact error,
   propose the minimal fix and ask.
5. Don't run state-changing git commands (commit, push, tag, reset, rebase) unless the user
   asks or the commit policy in **Project rules** allows it. Never `--no-verify`.
6. Leave no secrets, temporary files or TODOs without context. Never hand-edit `uv.lock`.

**Code.** Strict type hints on every signature. Google-style docstrings: complete for public
identifiers, one line for private ones; a public docstring's `Raises` also lists the
exceptions raised by the private functions it calls. Comments explain the *why*. Prefer
simple, explicit code; `pathlib` over `os.path`. Ruff and ty enforce the rest; don't fight
them with ignores.

**Tests.** `pytest` in `tests/`. Cover relevant logic and every fixed bug; they must pass on
Linux and Windows.

**Commits.** Conventional Commits in Spanish (`feat:`, `fix:`, `docs:`, `test:`,
`refactor:`, `chore:`), one intent per commit, explaining the *why*.

**Releases.** Only for versioned projects (a real version and `CHANGELOG.md`). Before
pushing changes to the package, use the `python-release` skill. Without it: SemVer bump,
`## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`, `uv lock`, then
`chore: bump versión a X.Y.Z`. Never tag without confirmation.

**Done** when the quality gate and any extra gate in **Project rules** pass, and the README
and docs reflect any change in usage.

Project rules below take precedence over these. Shared rules change in assistant-skills
(`scaffold.py sync`), not by hand here.
<!-- shared:end -->

## Project rules

`README.md` is the source of truth for **usage** (quick start, recipe template); don't
duplicate it here. Quality and build commands live in this file.

### Agent style

- **Be concise:** no filler, no long intros, no repetition. Batch independent edits/commands.
- **Self-contained:** prefer one-shot commands and complete diffs over exploratory
  back-and-forth.

### Code

- Python 3.12+ (ruff `target-version = py312`; configuration in `pyproject.toml`).
- **Human-facing text** in Spanish includes UI output and the recipes themselves.

### Web assets (CSS/JS/HTML)

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

### Extra quality gates

| Gate         | Command                                                                                                                                      | When                                                 |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Strict build | `uv run zensical build --strict` (+ `scripts/build_recipe_index.py` before, `scripts/build_precache.py` after — full chain in `vercel.json`) | any `zensical.toml`/`docs/`/`docs_templates/` change |
| Everything   | `uv run pre-commit run --all-files` (ruff check, ruff format --check, pytest)                                                                | before finishing                                     |

The shared quality gate applies to any change (tests included). CI
(`.github/workflows/ci.yml`) runs on push/PR (ubuntu + windows): `pre-commit run --all-files`,
`ty check` and the full strict build chain — keep `main` green.

Other Poe shortcuts (same rules as `poe check`):

| Task         | Equivalent                                                                |
| ------------ | ------------------------------------------------------------------------- |
| `poe fix`    | ruff format, ruff check --fix                                             |
| `poe build`  | `build_recipe_index.py` → `zensical build --strict` → `build_precache.py` |
| `poe serve`  | `build_recipe_index.py` → `zensical serve`                                |
| `poe backup` | `scripts/backup.py` (`<name>-<timestamp>.bundle` in the repo root)        |

Checklist before handing off:

- [ ] `poe check` (or `uv run pre-commit run --all-files` + `uv run ty check`) passes.
- [ ] `poe build` (or the chain in `vercel.json`) has no errors.
- [ ] Legit new words (dishes, brands, proper nouns, tech terms used in prose) added to
      `tests/spelling/allowlist.txt` (code spans and fenced blocks are skipped by the test).

### Content conventions (recipes)

- One recipe = `docs/recetas/<kebab-case-no-accents>.md` + `docs/fotos/<slug>.webp` (WebP de
  900x600) + its `categories` + an entry in the "Recetas" section of the `zensical.toml` `nav`
  (alphabetical). Missing any of them fails the tests. `docs/recetas/index.md` is the listing
  page, not a recipe.
- Filename kebab-case **without** accents (ej. `sopa-de-melon.md`); `title` in frontmatter is the
  display name **with accents**.
- Mandatory frontmatter (`tests/support.py` schema): `title` (non-empty), `people`/`time`
  (strict positive ints, `time` in minutes), `date` (`YYYY-MM-DD`, not in the future),
  `categories` (list of 1–3, no repeats; each must match the `title` of a
  `docs/categoria/*.md`). Optional:
  `source` (must match a `##` in `docs/fuentes.md`), `tags` (non-empty list, each must match a
  `###` in `docs/etiquetas.md`). No empty values (`source:` with nothing), no duplicated keys,
  no unknown keys.
- Body sections: `## Ingredientes`, `## Preparación`. Optional ones already in use: `## Opcional`,
  `## Alternativas`.
- Image is auto-rendered by `docs_templates/main.html` from `fotos/<slug>.webp` — never link it in
  Markdown.
- Nav (the `nav` in `zensical.toml` is the source of truth for names and order): `Entrada`
  (`index.md`), `Recetas` (`recetas/index.md` + every recipe), `Categorías`, `Etiquetas`
  (`etiquetas.md`), `Fuentes` (`fuentes.md`), `Glosario` (`glosario.md`). Recipes stay in the
  `nav` because templates only see `nav` pages (`listado.html` walks it), but the menu draws
  `Recetas` as a plain link: `docs_templates/partials/nav-item.html` overrides Zensical's partial
  for that (review it when upgrading Zensical).
- Categories live in `docs/categoria/<slug>.md` (`template: listado.html`, `title`,
  `description`), alphabetical in the "Categorías" section of the `nav`. The slug is
  `slugify(title)` (commas dropped). A new one = file + line in "Categorías". On recipe pages
  they render as badges before the tags (`docs_templates/partials/categories.html`, green
  `.md-tag--categoria`); the menu marks the section with `.md-nav__item--categorias`
  (`nav-item.html`) for its own styling.
- Tags taxonomy lives in `docs/etiquetas.md`: aparatos (`Batidora`, `Horno`, `Mortero`,
  `Paellera`, `Wok`) + dieta (`Pescetariano`, `Vegano`, `Vegetariano`); icons mapped in
  `zensical.toml` (`[project.extra.tags]`, `[project.theme.icon.tag]`).
- **Units:** prefer ISO 80000 (`g`, `l`, `ml`, space before unit: `100 g de …`). Don't rewrite
  existing recipes just to normalize this.
- Never rewrite a whole recipe for a small fix.
- Generated artifacts are gitignored: `docs/assets/recetas.json` (from
  `scripts/build_recipe_index.py`), `site/` incl. `precache.json` (from
  `scripts/build_precache.py`), `*.bundle` (from `scripts/backup.py`).

### Tests contract

- `tests/support.py` — shared paths + frontmatter schema (`Recipe` pydantic model); single source
  of truth for `load_frontmatter` / `page_meta` / `headings`.
- `tests/test_frontmatter.py` — frontmatter valid; no orphans (every `source` → `##` in
  `docs/fuentes.md`, every tag → `###` in `docs/etiquetas.md`); no duplicated titles; every
  category has a page (`test_categorias_tienen_pagina`), every category page is used
  (`test_categorias_sin_paginas_huerfanas`) and listed under "Categorías"
  (`test_categoria_en_el_nav`).
- `tests/test_anchors.py` — template links resolve: `fuentes#…`, `etiquetas#…` and
  `categoria/<slug>/` (`test_categoria_resuelve_a_pagina`).
- `tests/test_recipes.py` — recipes ⇄ nav ⇄ photos in sync; no broken/dead/orphan images; photos
  must be 900x600 WebP.
- `tests/test_spelling.py` — Spanish spelling (spylls + vendored `es_ES`); unknown words must be in
  `tests/spelling/allowlist.txt`. Skips fenced/inline code, link targets and HTML tags.

### Don't touch

- `tests/spelling/es_ES.*` + `LICENSE/` (vendored dictionary).
- Respect `.gitignore` (`.venv/`, `site/`, `docs/assets/recetas.json`, `*.bundle`, …). Don't
  commit build output.

### Commit policy

Never commit automatically: no state-changing or destructive git command unless the user
explicitly asks. Report the result and wait for confirmation.

### Releases

Not versioned (`version = "0.0.0"`, deployed from `main`): the shared **Releases** rules don't
apply — no version bumps, `CHANGELOG.md` or tags.

### Deploy

Vercel auto-deploys from `main` via `vercel.json` (`uv sync` +
`uv run python scripts/build_recipe_index.py && uv run zensical build --strict &&
uv run python scripts/build_precache.py`, output `site/`; `Cache-Control: no-cache` on `/sw.js`).
Keep it working.
