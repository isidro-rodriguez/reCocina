# AGENTS.md

Operational rules for AI agents and contributors working **on** this repo.
`README.md` is the source of truth for **usage** (setup, recipe template, commands) — don't duplicate it here.

## Agent behavior

- **No retry loops:** don't re-run a failing command more than twice. Stop, state the root cause, ask.
- **Be concise:** no filler, no long intros, no repetition. Batch independent edits/commands.
- **Surgical edits:** change only what's needed; never rewrite a whole recipe or file for a small fix.
- **Self-contained:** prefer one-shot commands and complete diffs over exploratory back-and-forth.
- Don't run state-changing or destructive git commands unless explicitly asked.

## Code style & language

- Python 3.12+. Package manager: **uv only** (`uv run`, `uv add`, `uv sync`) — never raw `pip` (unless inside an isolated venv).
- **Code:** English identifiers and structure.
- **Human-facing text:** Spanish — docstrings, comments, user/UI output, and the recipes themselves.
- Idiomatic Python: type hints, PEP 8, `pathlib` over `os.path`, `from __future__ import annotations`.
- **ruff is the boss:** `target-version = py312`, `line-length = 88`, rules `E, F, I, UP, B, D`; excludes `site/` and `theme/`.

## Quality policy — Definition of Done

Nothing is "done" until every applicable gate is green:

| Gate            | Command                                  | When                                     |
| --------------- | ---------------------------------------- | ---------------------------------------- |
| Python lint     | `uv run ruff check .`                    | any `.py` change                         |
| Python format   | `uv run ruff format --check .`           | any `.py` change                         |
| Markdown format | `uv run mdformat --check docs README.md` | any `.md` change                         |
| Tests           | `uv run pytest`                          | any change                               |
| Strict build    | `uv run mkdocs build --strict`           | any `mkdocs.yml`/`docs/`/`theme/` change |
| Everything      | `uv run pre-commit run --all-files`      | before finishing                         |

Checklist before handing off:

- [ ] `uv run pre-commit run --all-files` passes (runs ruff check, ruff format --check, pytest, mdformat --check).
- [ ] `uv run mkdocs build --strict` has no errors.
- [ ] New Markdown is formatted (`uv run mdformat docs README.md`).
- [ ] Legit new words (dishes, brands, proper nouns) added to `tests/spelling/allowlist.txt`.
- [ ] No `git commit --no-verify` unless the user explicitly asks.

## Content conventions (recipes)

- One recipe = `docs/recetas/<kebab-case-no-accents>.md` + `docs/img/fotos/<slug>.webp` (WebP de 900x600) + an entry in `mkdocs.yml` `nav`. Missing any of the three fails the tests.
- Title in Title Case **with accents** (`# Sopa De Ajo`); file name kebab-case **without** accents.
- Sections: `## Ingredientes`, `## Preparación`. Optional ones already in use: `## Opcional`, `## Alternativas`, `## Preparación en robot de cocina`. No frontmatter.
- Image always `../img/fotos/<slug>.webp` (WebP de 900x600).
- Nav categories: Aperitivos · Arroz · Pasta · Carne y Pollo · Pescado y Mariscos · Verduras, Legumbres y Potajes · Sopas y Cremas · Salsas · Postres.
- **Units:** prefer ISO 80000 (`g`, `l`, `ml`, space before unit: `100 g de …`). Don't rewrite existing recipes just to normalize this.

## Tests contract

- `tests/test_recipes.py` — recipes ⇄ nav ⇄ photos in sync; no broken/dead/orphan images; photos must be 900x600 WebP.
- `tests/test_theme.py` — favicon set complete; `theme.favicon`, `theme/main.html` links and `site.webmanifest` valid.
- `tests/test_spelling.py` — Spanish spelling (spylls + vendored `es_ES`); unknown words must be in `tests/spelling/allowlist.txt`.

## Don't touch

- `uv.lock` (regenerate with uv, never hand-edit). `tests/spelling/es_ES.*` + `LICENSE/` (vendored dictionary).
- Respect `.gitignore` (`.venv/`, `site/`, `.idea/`, `.kilo/`, `nul`, …). Don't commit build output.

## Commits

Conventional Commits, Spanish: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`. One intent per commit.

## Deploy

Vercel auto-deploys from `main` via `vercel.json` (`uv sync` + `uv run mkdocs build --strict`, output `site/`). Keep it working.
