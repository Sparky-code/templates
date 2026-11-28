"""Fast checks: every shape renders, with no leftover template syntax."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml
from conftest import CODE_SHAPES, ROOT, copier_copy

LEFTOVER = re.compile(r"\{\{|\{%|%\}|\}\}")
# Files that legitimately contain braces (GitHub expressions, lefthook placeholders).
ALLOWED = {"ci.yml", "lefthook.yml"}


def files(project: Path) -> list[Path]:
    return [p for p in project.rglob("*") if p.is_file() and ".git" not in p.parts]


@pytest.mark.parametrize("shape", [*CODE_SHAPES, "expo", "next", "other"])
def test_renders_without_leftover_template_syntax(render, shape: str) -> None:
    project = render(shape, uses_claude=True)
    names = {p.name for p in files(project)}
    assert {"README.md", "CLAUDE.md", "lefthook.yml", ".gitignore", "renovate.json"} <= names
    for path in files(project):
        assert "{" not in path.name and "%" not in path.name, path
        if path.name in ALLOWED or path.suffix in {".png", ".db"}:
            continue
        text = path.read_text()
        assert not LEFTOVER.search(text), f"template syntax left in {path}"


@pytest.mark.parametrize("shape", CODE_SHAPES)
def test_config_files_parse(render, shape: str) -> None:
    project = render(shape, uses_claude=True)
    for path in files(project):
        if path.suffix == ".json":
            json.loads(path.read_text())
        elif path.suffix == ".toml":
            tomllib.loads(path.read_text())
        elif path.suffix in {".yml", ".yaml"}:
            yaml.safe_load(path.read_text())


def test_version_pins_follow_the_language(render) -> None:
    assert (render("ts-cli", name="a").joinpath(".nvmrc")).read_text().strip() == "24"
    assert (
        render("python-cli", name="b").joinpath(".python-version")
    ).read_text().strip() == "3.14"
    other = render("other", name="c", language="none")
    assert not (other / ".nvmrc").exists() and not (other / ".python-version").exists()


def test_ci_runs_on_the_default_branch(render) -> None:
    def push_branches(project: Path) -> list[str]:
        ci = yaml.safe_load((project / ".github/workflows/ci.yml").read_text())
        return ci[True]["push"]["branches"]  # PyYAML reads the `on:` key as True

    assert push_branches(render("python-cli", name="new-repo")) == ["main"]
    assert push_branches(render("python-cli", name="old-repo", default_branch="master")) == [
        "master"
    ]
    answers = yaml.safe_load(
        (render("ts-cli", name="x") / ".copier-answers.baseline.yml").read_text()
    )
    assert answers["default_branch"] == "main"


def test_optional_parts_follow_the_answers(render) -> None:
    plain = render("python-cli", name="plain-tool", uses_claude=False, is_job=False)
    assert not (plain / "src/plain_tool/claude.py").exists()
    assert not (plain / "ops").exists()
    full = render("python-cli", name="full-tool", uses_claude=True, is_job=True)
    assert (full / "src/full_tool/claude.py").exists()
    assert (full / "ops/launchd/install.sh").stat().st_mode & 0o111
    web = render("react-web", name="static-web", with_api=False)
    assert not (web / "src/server").exists()
    assert "hono" not in (web / "package.json").read_text()


def test_ui_shapes_get_the_design_tokens(render) -> None:
    shared = (ROOT / "shared/tokens.css").read_text()
    assert (render("react-web", name="w").joinpath("src/styles/tokens.css")).read_text() == shared
    expo = render("expo", name="e")
    assert (expo / "design/tokens.css").read_text() == shared
    assert (expo / "design/tokens.ts").exists() and (expo / "design/check-tokens.ts").exists()
    assert not (render("ts-cli", name="t") / "design").exists()


def test_rejects_bad_names_and_codeless_shapes(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="slug"):
        copier_copy(tmp_path / "Bad_Name", "baseline", "ts-cli")
    with pytest.raises(AssertionError, match="no shape template"):
        copier_copy(tmp_path / "an-app", "shape", "expo")


def test_shellcheck_clean() -> None:
    scripts = [
        ROOT / "bin/new-project",
        ROOT / "baseline/.lefthook/commit-msg/check-message.sh",
        ROOT / "shared/fake-claude.sh",
    ]
    subprocess.run(["shellcheck", *map(str, scripts)], check=True)


@pytest.mark.skipif(shutil.which("plutil") is None, reason="macOS only")
@pytest.mark.parametrize("shape", ["ts-cli", "python-cli"])
def test_launchd_plist_is_valid(render, shape: str) -> None:
    plist = next((render(shape) / "ops/launchd").glob("*.plist"))
    subprocess.run(["plutil", "-lint", str(plist)], check=True, capture_output=True)
