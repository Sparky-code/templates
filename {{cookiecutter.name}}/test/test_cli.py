{%- if cookiecutter.cli_framework == "typer" %}
from typer.testing import CliRunner
{%- else %}
from click.testing import CliRunner
{%- endif %}

from src.cli import app

runner = CliRunner()


def test_hello():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output
