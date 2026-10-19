## (Tem)Plate

To create a template

`cookiecutter <path/to/template>`
TO DO 
- install this to make it available wherever, plug in current dir
- variable option for template types (cli, webdev, data; each with testing wired in)
- option for the target language, not just Python
- expand pre_gen and post_gen

## Notes

Build using
- [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/index.html)
- poetry
- sqlalchemy
- alembic?

## What a generated project contains

- `src/` with `cli.py` (Typer or Click hello command), `config.py`, `log.py`,
  `db.py` (SQLAlchemy), and `file_mgmt.py`
- `test/test_cli.py` using the CLI runner
- `notes.md` for working notes, `.env.example`, `.gitignore`, an empty
  `Dockerfile`, and a GitHub Actions CI workflow

## History

Absorbed the goals of the earlier `devTool` project (2024), a Click-based CLI
whose first feature was generating local project folders from templates. That
need is met by this cookiecutter, so devTool was retired and its roadmap items
were merged into the TO DO list above.

Also absorbed `cli_template` (2024), an earlier cookiecutter with the same
aim: its config, logging, db, and file-management modules, CI workflow,
`.gitignore`, and alembic notes now live in this template.
