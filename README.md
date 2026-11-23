# templates

[Copier](https://copier.readthedocs.io/) templates for every project shape, so
each new project starts with the same tooling, conventions and checks, and
existing projects can pull in later improvements with `copier update`.

## Shapes

| Shape | What you get |
|---|---|
| `ts-library` | TypeScript library: ESM, subpath exports, no runtime dependencies, tsc build, Vitest, vendor script, CHANGELOG |
| `ts-cli` | TypeScript CLI or scheduled job: commander, Node runs the `.ts` source directly, Prisma on SQLite (libsql/Turso), job runner (lock, run records, dry run, caps, ntfy alert), launchd schedule, optional Claude CLI wrapper |
| `python-cli` | Python CLI or scheduled job: uv, Typer, sqlite3 with numbered migrations, the same job runner, launchd schedule, optional Claude CLI wrapper |
| `python-service` | Python HTTP service: FastAPI, pydantic-settings, SQLAlchemy 2 + Alembic on Postgres, compose for local Postgres, Dockerfile |
| `react-web` | React web app: Vite, Tailwind v4, shadcn/ui on Radix, design tokens, optional Hono API with zod validation and a typed client |
| `expo`, `next` | Start from the official generator (`create-expo-app`, `create-next-app`), then apply the baseline |
| `other` | Baseline only |

Every project also gets the **baseline**: lefthook hooks (format and lint on
commit, typecheck and tests on push, commit message check), GitHub Actions CI,
README and CLAUDE.md skeletons, `.env.example`, `.gitignore`, the Node or
Python version pin, Renovate config and, for UIs, the shared design tokens.

Toolchains: Node 24, pnpm, TypeScript 7 (strict), Biome, Vitest; Python 3.14,
uv, ruff, mypy (strict), pytest.

## Use

Needs [uv](https://docs.astral.sh/uv/) (Copier runs through `uvx`), lefthook
and, for TypeScript shapes, Node 24 with corepack.

```bash
# from a clone of this repo
bin/new-project python-cli ~/code/my-tool
bin/new-project ts-cli ~/code/my-job --data uses_claude=true
bin/new-project react-web ~/code/my-app --data with_api=false

# framework apps: generator first, then the baseline on top
pnpm create expo-app ~/code/my-mobile && bin/new-project expo ~/code/my-mobile
```

`bin/new-project` applies the shape and the baseline, runs `git init`,
installs dependencies and installs the hooks. Without the script:

```bash
uvx copier copy gh:Sparky-code/templates my-tool --data layer=shape --data shape=python-cli -a .copier-answers.shape.yml
uvx copier copy gh:Sparky-code/templates my-tool --data layer=baseline --data shape=python-cli -a .copier-answers.baseline.yml
```

### Updating an existing project

Each layer records its answers and template version in its own file:

```bash
uvx copier update -a .copier-answers.baseline.yml
uvx copier update -a .copier-answers.shape.yml
```

Copier applies the template's changes since the recorded version as a merge,
keeping local edits. Review the diff before committing.

To bring a project that predates these templates in line, apply the baseline
in a terminal (Copier asks before overwriting each existing file; without a
terminal it stops instead):

```bash
cd existing-project && git switch -c baseline
uvx copier copy gh:Sparky-code/templates . --data layer=baseline --data shape=<shape> -a .copier-answers.baseline.yml
```

Then move its tooling to the standard one layer per commit.

## Develop

```bash
uv sync
uv run pytest              # fast: rendering, commit-msg hook, copier update
uv run pytest -m slow      # generate, install and check every shape (minutes)
```

Layout: `copier.yml` holds the questions; `baseline/` and each shape directory
are the templates; `shared/` holds files included by several templates
(design tokens, Biome config, Claude CLI wrapper, launchd files).

Release by tagging (`v0.2.0`); `copier update` moves projects to the latest tag.

## History

Started as plate, a cookiecutter template for a Python CLI (Poetry, Click or
Typer, SQLAlchemy). Rebuilt on Copier in 2026 to cover every project shape and
to support `copier update`; the cookiecutter version is in the git history.

Plate had absorbed the goals of the earlier `devTool` project (2024), a
Click-based CLI whose first feature was generating local project folders from
templates, and `cli_template` (2024), an earlier cookiecutter with the same
aim.
