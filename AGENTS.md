# AGENTS.md

Operational rules for AI agents and contributors working **on** this repo.
`README.md` is the source of truth for **usage** (setup, recipe template, commands) — don't
duplicate it here.

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
- Idiomatic Python: type hints, PEP 8, `pathlib` over `os.path`,
  `from __future__ import annotations`.
- **ruff is the boss:** `target-version = py312`, `line-length = 88`, rules
  `E, F, I, UP, B, D, SIM, PTH`, pydocstyle `google`; excludes `site/` and `theme/`.

## Web assets (CSS/JS/HTML)

- `docs/assets/stylesheets/*.css`, `docs/assets/javascripts/*.js`, `docs/sw.js`: **4-space indent,
  LF, trailing newline**. No auto-formatter configured — match the existing style by hand.
- `theme/*.html` (Jinja): no formatter configured — keep partials aligned manually (4-space indent,
  LF).
- Line endings are forced to LF by `.gitattributes` (`* text=auto eol=lf`); don't rely on
  `core.autocrlf`.
- New JS/CSS must be registered in `zensical.toml` (`extra_javascript` / `extra_css`), e.g.
  `daily-recipe.js` (recetas del día de la portada) and `kitchen-mode.js` (modo cocina).
  `daily-recipe.js` reads `assets/recetas.json`, produced by `scripts/build_recipe_index.py` —
  never hand-edit that JSON.

## Quality policy — Definition of Done

Nothing is "done" until every applicable gate is green:

| Gate          | Command                                                                                                                                      | When                                        |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| Python lint   | `uv run ruff check .`                                                                                                                        | any `.py` change                            |
| Python format | `uv run ruff format --check .`                                                                                                               | any `.py` change                            |
| Type check    | `uv run ty check`                                                                                                                            | any `.py` change                            |
| Tests         | `uv run pytest`                                                                                                                              | any change                                  |
| Strict build  | `uv run zensical build --strict` (+ `scripts/build_recipe_index.py` before, `scripts/build_precache.py` after — full chain in `vercel.json`) | any `zensical.toml`/`docs/`/`theme/` change |
| Everything    | `uv run pre-commit run --all-files` (ruff check, ruff format --check, pytest)                                                                | before finishing                            |

CI (`.github/workflows/ci.yml`) runs `uv run pre-commit run --all-files` on push/PR (ubuntu +
windows) — keep `main` green.

Checklist before handing off:

- [ ] `uv run pre-commit run --all-files` passes.
- [ ] `uv run ty check` passes.
- [ ] `uv run zensical build --strict` has no errors (with recipe index generated before and
  precache after, per `vercel.json`).
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
- Image is auto-rendered by `theme/main.html` from `fotos/<slug>.webp` — never link it in Markdown.
- Nav categories (same order as the `nav` in `zensical.toml` — see the list in `README.md`):
  `Entrada` (`index.md`), `Etiquetas` (`etiquetas.md`), `Fuentes` (`fuentes.md`), then the recipe
  sections.
- Tags taxonomy lives in `docs/etiquetas.md`: aparatos (`Batidora`, `Horno`, `Mortero`,
  `Paellera`, `Wok`) + dieta (`Pescetariano`, `Vegano`, `Vegetariano`); icons mapped in
  `zensical.toml` (`[project.extra.tags]`, `[project.theme.icon.tag]`).
- **Units:** prefer ISO 80000 (`g`, `l`, `ml`, space before unit: `100 g de …`). Don't rewrite
  existing recipes just to normalize this.
- Generated artifacts are gitignored: `docs/assets/recetas.json` (from
  `scripts/build_recipe_index.py`), `site/` incl. `precache.json` (from
  `scripts/build_precache.py`), `local/` (backup zip from `scripts/backup.py`).

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
- Respect `.gitignore` (`.venv/`, `site/`, `docs/assets/recetas.json`, `local/`, `nul`, …). Don't
  commit build output.

## Commits

Conventional Commits, Spanish: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`. One intent per
commit.

## Deploy

Vercel auto-deploys from `main` via `vercel.json` (`uv sync` +
`uv run python scripts/build_recipe_index.py && uv run zensical build --strict &&
uv run python scripts/build_precache.py`, output `site/`; `Cache-Control: no-cache` on `/sw.js`).
Keep it working.
