# templates

Copier templates for every project shape. See README.md for what each shape contains.

## Commands

- Fast tests: `uv run pytest` · End-to-end (installs every shape): `uv run pytest -m slow`
- Lint: `uv run ruff check` · `shellcheck bin/new-project baseline/.lefthook/commit-msg/check-message.sh shared/*.sh`
- Try a shape from the working tree: `TEMPLATES_SRC=$PWD TEMPLATES_REF=HEAD bin/new-project <shape> /tmp/x`

## Layout

- `copier.yml` questions; `_subdirectory` picks `baseline/` or the shape directory
- `baseline/` files every project gets; `ts-library/`, `ts-cli/`, `python-cli/`, `python-service/`, `react-web/` shape code
- `shared/` files several templates include with `{% include 'shared/...' %}` (tokens, biome.json, Claude wrapper, launchd)
- `tests/` pytest for the templates themselves

## Rules

- Generated projects must pass their own lint, typecheck and tests (`pytest -m slow`) before a release. After editing a template, generate it and port formatter output back rather than hand-formatting.
- Files ending `.jinja` are rendered; others are copied as-is (file names are always rendered). Include wrappers have no trailing newline.
- Scripts must run on macOS's bash 3.2 (no `mapfile`, no associative arrays).
- Keep content generic: this repo is public. No personal names, emails, paths or private project names.
- Commits follow `type(scope): Imperative subject`; no Co-Authored-By trailers or session IDs.
- Release by tagging; note changes in CHANGELOG.md.
