{%- if cookiecutter.cli_framework == "typer" %}
import typer

app = typer.Typer(help="{{ cookiecutter.description }}")


@app.callback()
def main():
    """{{ cookiecutter.description }}"""


@app.command()
def hello(name: str):
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


{{ cookiecutter.name }} = app
{%- else %}
import click


@click.group(help="{{ cookiecutter.description }}")
def app():
    pass


@app.command()
@click.argument("name")
def hello(name):
    """Say hello to NAME."""
    click.echo(f"Hello {name}!")


{{ cookiecutter.name }} = app
{%- endif %}
