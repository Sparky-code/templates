"""ops/state.sh: SQLite state kept on a git branch, against a local bare repo."""

from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest
from conftest import ROOT, run

SCRIPT = ROOT / "shared/ops/state.sh"


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    run(["git", "init", "--quiet", "--bare", str(origin)], cwd=tmp_path)
    run(["git", "init", "--quiet", "-b", "main", str(work)], cwd=tmp_path)
    run(["git", "remote", "add", "origin", str(origin)], cwd=work)
    return work


def state(clone: Path, *args: str) -> str:
    env = dict(os.environ, GITHUB_RUN_ID="7")
    return run(["bash", str(SCRIPT), *args], cwd=clone, env=env)


def log(clone: Path) -> list[str]:
    out = run(["git", "log", "--format=%s", "origin/state"], cwd=clone)
    return out.splitlines()


def test_round_trip(clone: Path) -> None:
    db = clone / "data/app.db"
    assert "no state branch yet" in state(clone, "restore", "data/app.db")
    assert not db.exists()

    db.parent.mkdir()
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE seen (key TEXT PRIMARY KEY)")
    conn.execute("INSERT INTO seen VALUES ('a')")
    conn.commit()
    conn.close()
    assert "saved" in state(clone, "save", "data/app.db")
    assert "state unchanged" in state(clone, "save", "data/app.db")

    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO seen VALUES ('b')")
    conn.commit()
    conn.close()
    state(clone, "save", "data/app.db")
    run(["git", "fetch", "--quiet", "origin", "state"], cwd=clone)
    assert log(clone) == ["chore(state): Update after run 7"] * 2

    db.unlink()
    assert "restored" in state(clone, "restore", "data/app.db")
    rows = sqlite3.connect(db).execute("SELECT key FROM seen ORDER BY key").fetchall()
    assert rows == [("a",), ("b",)]


def test_save_without_a_database_fails(clone: Path) -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "save", "data/missing.db"], cwd=clone, capture_output=True
    )
    assert result.returncode == 1
