"""Slow end-to-end checks: generate each shape with bin/new-project, install it,
and run the generated project's own lint, typecheck, tests and build.

    uv run pytest -m slow              # all shapes
    uv run pytest -m slow -k python    # one family
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import NEW_PROJECT, ROOT, have, run, tool_env

pytestmark = pytest.mark.slow

CHECKS = {
    "ts-library": [["pnpm", "run", "lint"], ["pnpm", "run", "typecheck"], ["pnpm", "run", "test"],
                   ["pnpm", "run", "build"]],
    "ts-cli": [["pnpm", "run", "lint"], ["pnpm", "run", "typecheck"], ["pnpm", "run", "test"],
               ["pnpm", "start", "run", "--dry-run"]],
    "react-web": [["pnpm", "run", "lint"], ["pnpm", "run", "typecheck"], ["pnpm", "run", "test"],
                  ["pnpm", "run", "build"]],
    "python-cli": [["uv", "run", "ruff", "format", "--check"], ["uv", "run", "ruff", "check"],
                   ["uv", "run", "mypy"], ["uv", "run", "pytest"],
                   ["uv", "run", "demo-app", "run", "--dry-run"]],
    "python-service": [["uv", "run", "ruff", "format", "--check"], ["uv", "run", "ruff", "check"],
                       ["uv", "run", "mypy"], ["uv", "run", "pytest"]],
}  # fmt: skip


def generate(tmp_path: Path, shape: str, *extra: str) -> Path:
    dest = tmp_path / "demo-app"
    env = tool_env() | {"TEMPLATES_SRC": str(ROOT), "TEMPLATES_REF": "HEAD"}
    run([str(NEW_PROJECT), shape, str(dest), *extra], cwd=tmp_path, env=env)
    return dest


@pytest.mark.parametrize("uses_claude", [True, False], ids=["full", "plain"])
@pytest.mark.parametrize("shape", list(CHECKS))
def test_generated_project_passes_its_own_checks(
    tmp_path: Path, shape: str, uses_claude: bool
) -> None:
    if not uses_claude and shape not in {"ts-cli", "python-cli", "react-web"}:
        pytest.skip("only the CLI shapes have the Claude option (react-web: no API)")
    extra = ["--data", f"uses_claude={str(uses_claude).lower()}"]
    if shape == "react-web" and not uses_claude:
        extra = ["--data", "with_api=false"]
    project = generate(tmp_path, shape, *extra)
    for cmd in CHECKS[shape]:
        run(cmd, cwd=project, env=tool_env())


@pytest.mark.skipif(not have("lefthook"), reason="needs lefthook")
def test_hooks_enforce_the_commit_convention(tmp_path: Path) -> None:
    project = generate(tmp_path, "python-cli")
    run(["git", "add", "-A"], cwd=project)
    bad = subprocess.run(
        ["git", "commit", "-m", "Initial commit"], cwd=project, capture_output=True, text=True
    )
    assert bad.returncode != 0
    assert "must start with a type" in bad.stdout + bad.stderr
    run(["git", "commit", "-m", "chore: Scaffold from templates"], cwd=project)
