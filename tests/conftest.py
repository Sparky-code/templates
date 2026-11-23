from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NEW_PROJECT = ROOT / "bin" / "new-project"
CODE_SHAPES = ["ts-library", "ts-cli", "python-cli", "python-service", "react-web"]


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        cmd, cwd=cwd, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{' '.join(cmd)} failed in {cwd}:\n{result.stdout[-4000:]}\n{result.stderr[-4000:]}"
        )
    return result.stdout


def copier_copy(dest: Path, layer: str, shape: str, **data: str | bool) -> None:
    """Render one layer from the working tree (uncommitted changes included)."""
    args = [
        "uvx", "copier", "copy", "--quiet", "--defaults", "--vcs-ref", "HEAD",
        "--data", f"layer={layer}", "--data", f"shape={shape}",
        "--data", f"project_name={dest.name}",
        "-a", f".copier-answers.{layer}.yml",
    ]  # fmt: skip
    for key, value in data.items():
        args += ["--data", f"{key}={str(value).lower() if isinstance(value, bool) else value}"]
    run([*args, str(ROOT), str(dest)], cwd=ROOT)


@pytest.fixture
def render(tmp_path: Path):
    """render(shape, **data) -> path of a project with baseline + shape applied (no install)."""

    def _render(shape: str, name: str = "demo-app", **data: str | bool) -> Path:
        dest = tmp_path / name
        if shape in CODE_SHAPES:
            copier_copy(dest, "shape", shape, **data)
        copier_copy(dest, "baseline", shape, **data)
        return dest

    return _render


def tool_env() -> dict[str, str]:
    env = dict(os.environ, COREPACK_ENABLE_DOWNLOAD_PROMPT="0", CI="1")
    return env


def have(tool: str) -> bool:
    return shutil.which(tool) is not None
