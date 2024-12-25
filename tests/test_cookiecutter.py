
from cookiecutter.main import cookiecutter
import pathlib

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)

def test_template_generation(tmpdir):
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "name": "test_repo",
            "authors": "Test Author",
        },
    )
    # Assert that expected files are created
    assert (tmpdir / "test_repo" / "README.md").exists()