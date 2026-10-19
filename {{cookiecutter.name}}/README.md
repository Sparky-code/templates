# {{ cookiecutter.name }}
By: {{ cookiecutter.authors }}

## Overview
This template is designed for CLI heavy projects.
Ideally the workflow looks something like this
--> ideate as bash > refine into python > build cli command
--> tests written at python stage
--> update --help to include details
```
<command> <o> options (curious if i can get away with single letter vars without flagging)

``` 

## Build & Troubleshoot

```
poetry install            # create venv and install deps
poetry run python -m src --help
poetry run pytest
```

Database (when a db framework is selected):

```
poetry run alembic init alembic
# set sqlalchemy.url in alembic.ini, e.g. sqlite:///app.db
poetry run alembic revision --autogenerate -m "Initial migration"
poetry run alembic upgrade head
```

## Dependencies

## Goals
