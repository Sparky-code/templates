from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from {{ package_name }}.claude import ClaudeError, ask_claude

FAKE = str(Path(__file__).parent / "fixtures" / "fake-claude.sh")


@pytest.fixture
def cache() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE claude_cache (key TEXT PRIMARY KEY, model TEXT NOT NULL,"
        " response TEXT NOT NULL, created_at TEXT)"
    )
    return conn


def test_passes_prompt_model_and_system_prompt(cache: sqlite3.Connection) -> None:
    out = ask_claude("hello", conn=cache, binary=FAKE, model="haiku", system="be brief")
    assert out == "-p hello --model haiku --output-format text --append-system-prompt be brief"


def test_caches_by_model_and_prompt(
    cache: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    count = tmp_path / "count"
    monkeypatch.setenv("FAKE_CLAUDE_COUNT", str(count))
    ask_claude("same", conn=cache, binary=FAKE)
    ask_claude("same", conn=cache, binary=FAKE)
    ask_claude("same", conn=cache, binary=FAKE, fresh=True)
    assert count.read_text().splitlines() == ["call", "call"]


def test_reports_a_failing_cli(cache: sqlite3.Connection) -> None:
    with pytest.raises(ClaudeError):
        ask_claude("x", conn=cache, binary="/nonexistent/claude")
