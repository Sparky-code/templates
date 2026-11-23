"""The commit-msg hook script accepts the convention and rejects everything else."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import ROOT

SCRIPT = ROOT / "baseline/.lefthook/commit-msg/check-message.sh"


def check(message: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text(message)
    # /bin/bash on macOS is 3.2: the script must work there.
    return subprocess.run(["bash", str(SCRIPT), str(msg)], capture_output=True, text=True)


@pytest.mark.parametrize(
    "message",
    [
        "fix: Reject UTC-13 offsets",
        "feat(stops)!: Add isThrough option",
        "docs: Explain the vendoring step\n\nApps without a build load the copy directly.\n",
        "ci: Pin Node 24",
        "fix: Handle empty input\n# a comment git would strip\n",
        "Merge branch 'main' into feature",
        'Revert "fix: Reject offsets"',
        "fixup! fix: Reject offsets",
    ],
)
def test_accepts(message: str, tmp_path: Path) -> None:
    result = check(message, tmp_path)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("message", "reason"),
    [
        ("Fix the parser", "must start with a type"),
        ("feature: Add x", "must start with a type"),
        ("fix: reject offsets", "capital letter"),
        ("fix: Reject offsets.", "trailing period"),
        ("fix: Fixed offsets", "imperative"),
        ("chore: " + "A" * 70, "keep it to 72"),
        ("fix: Add x\nbody without blank line", "blank line"),
        ("fix: Add x\n\nCo-Authored-By: Someone <a@b.c>", "Co-Authored-By"),
        ("fix: Add x\n\nGenerated with Claude Code", "generated-by"),
        ("fix: Add x\n\nhttps://claude.ai/code/session_0123456789", "session"),
        ("", "empty"),
    ],
)
def test_rejects(message: str, reason: str, tmp_path: Path) -> None:
    result = check(message, tmp_path)
    assert result.returncode == 1
    assert reason in result.stderr
