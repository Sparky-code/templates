"""The job runner: every scheduled job goes through run_job, which

- holds a lock file so two runs can't overlap,
- records the run (start, end, outcome) in the database,
- sends a push notification (ntfy) when a run fails,
- reports failure so the CLI exits non-zero.
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import httpx


class LockedError(RuntimeError):
    pass


@dataclass
class JobContext:
    dry_run: bool
    max_items: int
    log: Callable[[str], None] = field(default=print)


Notifier = Callable[[str], None]


@contextmanager
def run_lock(path: Path) -> Iterator[None]:
    """Exclusive lock file holding our pid; a lock left by a dead process is taken over."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        pid = int(path.read_text() or 0)
        if pid and _alive(pid):
            raise LockedError(f"another run (pid {pid}) holds {path}") from None
        path.unlink(missing_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def run_job(
    name: str,
    fn: Callable[[JobContext], str | None],
    *,
    conn: sqlite3.Connection,
    lock_path: Path,
    dry_run: bool,
    max_items: int,
    notify: Notifier | None = None,
    log: Callable[[str], None] = print,
) -> bool:
    """Run `fn` as job `name`; return True on success."""
    with run_lock(lock_path):
        cur = conn.execute("INSERT INTO runs (job, dry_run) VALUES (?, ?)", (name, int(dry_run)))
        run_id = cur.lastrowid
        conn.commit()
        try:
            detail = fn(JobContext(dry_run=dry_run, max_items=max_items, log=log))
        except Exception as exc:
            message = str(exc) or type(exc).__name__
            _finish(conn, run_id, ok=False, detail=message)
            log(f"{name} failed: {message}")
            if notify is not None:
                try:
                    notify(f"{name} failed: {message}")
                except httpx.HTTPError:
                    log("failure notification could not be sent")
            return False
        _finish(conn, run_id, ok=True, detail=detail)
        return True


def _finish(conn: sqlite3.Connection, run_id: int | None, *, ok: bool, detail: str | None) -> None:
    conn.execute(
        "UPDATE runs SET finished_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), ok = ?, detail = ?"
        " WHERE id = ?",
        (int(ok), detail, run_id),
    )
    conn.commit()


def ntfy_notifier(url: str | None = None, client: httpx.Client | None = None) -> Notifier | None:
    """Push notification via ntfy (https://ntfy.sh) if NTFY_URL is set."""
    target = url if url is not None else os.environ.get("NTFY_URL", "")
    if not target:
        return None
    http = client or httpx.Client(timeout=10)

    def send(message: str) -> None:
        http.post(target, content=message, headers={"Title": "Job failed"}).raise_for_status()

    return send
