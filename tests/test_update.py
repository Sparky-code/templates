"""copier update pulls a template change into an existing project."""

from __future__ import annotations

import shutil
from pathlib import Path

from conftest import ROOT, run

IGNORE = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache")


def test_update_applies_a_baseline_change(tmp_path: Path) -> None:
    template = tmp_path / "template"
    shutil.copytree(ROOT, template, ignore=IGNORE)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    git += ["-c", "core.hooksPath=/dev/null"]
    run(["git", "init", "-q", "-b", "main"], cwd=template)
    run([*git, "add", "-A"], cwd=template)
    run([*git, "commit", "-qm", "v1"], cwd=template)
    run(["git", "tag", "v1"], cwd=template)

    project = tmp_path / "demo-tool"
    run(
        ["uvx", "copier", "copy", "--quiet", "--defaults", "--vcs-ref", "v1",
         "--data", "layer=baseline", "--data", "shape=python-cli",
         "--data", "project_name=demo-tool", "-a", ".copier-answers.baseline.yml",
         str(template), str(project)],
        cwd=tmp_path,
    )  # fmt: skip
    run(["git", "init", "-q", "-b", "main"], cwd=project)
    run([*git, "add", "-A"], cwd=project)
    run([*git, "commit", "-qm", "chore: Scaffold"], cwd=project)

    # A local edit in the project must survive the update.
    readme = project / "README.md"
    readme.write_text(readme.read_text() + "\nProject-specific notes.\n")
    run([*git, "commit", "-qam", "docs: Add notes"], cwd=project)

    renovate = template / "baseline" / "renovate.json"
    renovate.write_text(renovate.read_text().replace("before 6am on monday", "every weekend"))
    run([*git, "commit", "-qam", "v2"], cwd=template)
    run(["git", "tag", "v2"], cwd=template)

    run(
        ["uvx", "copier", "update", "--quiet", "--defaults", "-a", ".copier-answers.baseline.yml"],
        cwd=project,
    )
    assert "every weekend" in (project / "renovate.json").read_text()
    assert "Project-specific notes." in readme.read_text()
    assert "_commit: v2" in (project / ".copier-answers.baseline.yml").read_text()
