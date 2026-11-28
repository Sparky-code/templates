"""The only place this project calls Claude: through the Claude CLI (`claude -p`),
never an API SDK. Responses are cached in the database by a hash of
model + system prompt + prompt, so re-runs don't repeat calls.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import subprocess


class ClaudeError(RuntimeError):
    pass


def ask_claude(
    prompt: str,
    *,
    conn: sqlite3.Connection,
    model: str | None = None,
    system: str | None = None,
    timeout: float = 120,
    binary: str | None = None,
    fresh: bool = False,
) -> str:
    """Return Claude's reply to `prompt`, from the cache unless `fresh`."""
    model = model or os.environ.get("CLAUDE_MODEL") or "sonnet"
    binary = binary or os.environ.get("CLAUDE_BIN") or "claude"
    key = hashlib.sha256(f"{model}\n{system or ''}\n{prompt}".encode()).hexdigest()

    if not fresh:
        row = conn.execute("SELECT response FROM claude_cache WHERE key = ?", (key,)).fetchone()
        if row is not None:
            return str(row[0])

    args = [binary, "-p", prompt, "--model", model, "--output-format", "text"]
    if system:
        args += ["--append-system-prompt", system]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ClaudeError(f"Claude CLI failed: {exc}") from exc
    response = result.stdout.strip()
    if not response:
        raise ClaudeError("Claude CLI returned no output")

    conn.execute(
        "INSERT INTO claude_cache (key, model, response) VALUES (?, ?, ?)"
        " ON CONFLICT(key) DO UPDATE SET response = excluded.response,"
        " created_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')",
        (key, model, response),
    )
    conn.commit()
    return response
