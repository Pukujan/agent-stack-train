#!/usr/bin/env python3
"""Task board for several agents on one repository: add, claim, release, list.

The hotload pack had a seat protocol for the boss and no board for the work
itself, so every adopter wrote its own; one copy broke twice in a day (#97).
This is the shared one. It keeps one file, ``.coord/board.json`` at the top of
the checkout (``--board`` to move it), changed only under a lock, and appends
each change to the task's history and to ``.coord/board-events.jsonl``.

A claim is exclusive: a task another agent holds cannot be claimed or released
without ``--force``, and every forced change is recorded as one. Name agents as
``agent:<harness>/<session id>`` so a claim says which session holds it.

The board coordinates the work; it does not log it. Issue logs are GitHub
issues filed with the repository's form, and their machine record comes from
OIO's ``oio_record.py``. Nothing here talks to GitHub.

    python board.py add T-12 "Fix release notes" --priority P1 --agent agent:codex/<id>
    python board.py claim T-12 --agent agent:codex/<id>
    python board.py release T-12 --agent agent:codex/<id> --status done --note "PR #40"
    python board.py list [--json]

Stdlib only; Windows-safe (a lock file, not ``fcntl``).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "acs.board.v1"
BOARD_REL = Path(".coord/board.json")
EVENTS_NAME = "board-events.jsonl"
STATUSES = ("open", "claimed", "blocked", "done")
RELEASE_STATUSES = ("done", "blocked", "open")
LOCK_WAIT = 10.0  # seconds to wait for another writer
LOCK_STALE = 60.0  # a lock older than this was left by a crashed writer


class BoardError(Exception):
    pass


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def default_board() -> Path:
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        top = ""
    return Path(top or os.getcwd()) / BOARD_REL


class Board:
    def __init__(self, path: Path):
        self.path = path
        self.lock = path.with_name(path.name + ".lock")
        self.events = path.with_name(EVENTS_NAME)

    @contextlib.contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + LOCK_WAIT
        while True:
            try:
                fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError:
                try:
                    if time.time() - self.lock.stat().st_mtime > LOCK_STALE:
                        self.lock.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() > deadline:
                    raise BoardError(f"the board is locked by another writer ({self.lock})") from None
                time.sleep(0.05)
        try:
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            yield
        finally:
            with contextlib.suppress(FileNotFoundError):
                self.lock.unlink()

    def read(self) -> dict:
        if not self.path.exists():
            return {"schema": SCHEMA, "tasks": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise BoardError(f"{self.path} is not valid JSON ({exc}); fix or remove it") from None
        if data.get("schema") != SCHEMA or not isinstance(data.get("tasks"), dict):
            raise BoardError(f"{self.path} is not an {SCHEMA} board")
        return data

    def _write(self, data: dict) -> None:
        data["updated_at"] = now()
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def _change(self, task_id: str, agent: str, action: str, apply, note: str = "") -> dict:
        if not str(agent or "").strip():
            raise BoardError(f"{action} needs --agent")
        with self._locked():
            data = self.read()
            task = apply(data["tasks"])
            forced = task.pop("_forced", False)
            entry = {"ts": now(), "agent": agent, "action": action}
            if note:
                entry["note"] = note
            if forced:
                entry["forced"] = True
            task.setdefault("history", []).append(entry)
            self._write(data)
            with open(self.events, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"task": task_id, **entry}) + "\n")
        return task

    def _task(self, tasks: dict, task_id: str) -> dict:
        if task_id not in tasks:
            raise BoardError(f"no task {task_id} on the board")
        return tasks[task_id]

    def add(self, task_id: str, title: str, agent: str, priority: str = "P2") -> dict:
        if not str(task_id or "").strip() or not str(title or "").strip():
            raise BoardError("add needs a task id and a title")

        def apply(tasks):
            if task_id in tasks:
                raise BoardError(f"task {task_id} is already on the board")
            tasks[task_id] = {"title": title, "priority": priority, "status": "open", "owner": None}
            return tasks[task_id]

        return self._change(task_id, agent, "add", apply)

    def claim(self, task_id: str, agent: str, force: bool = False) -> dict:
        def apply(tasks):
            task = self._task(tasks, task_id)
            if task["status"] == "done":
                raise BoardError(f"{task_id} is done; add a new task instead")
            if task["owner"] not in (None, agent):
                if not force:
                    raise BoardError(f"{task_id} is claimed by {task['owner']}")
                task["_forced"] = True
            task.update(status="claimed", owner=agent, claimed_at=now())
            return task

        return self._change(task_id, agent, "claim", apply)

    def release(self, task_id: str, agent: str, status: str = "done", note: str = "", force: bool = False) -> dict:
        if status not in RELEASE_STATUSES:
            raise BoardError(f"release status must be one of {', '.join(RELEASE_STATUSES)}")
        def apply(tasks):
            task = self._task(tasks, task_id)
            if task["owner"] not in (None, agent):
                if not force:
                    raise BoardError(f"{task_id} is claimed by {task['owner']}, not {agent}")
                task["_forced"] = True
            # A done task keeps who finished it; an open or blocked one is free to claim.
            task.update(status=status, owner=agent if status == "done" else None, released_at=now())
            return task

        return self._change(task_id, agent, f"release:{status}", apply, note=note)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, help=f"board file (default: {BOARD_REL.as_posix()} at the checkout's top)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list", help="show the tasks")
    ls.add_argument("--json", action="store_true")
    ls.add_argument("--status", choices=STATUSES)
    add = sub.add_parser("add", help="put a task on the board")
    add.add_argument("task")
    add.add_argument("title")
    add.add_argument("--priority", default="P2")
    claim = sub.add_parser("claim", help="take a task")
    claim.add_argument("task")
    claim.add_argument("--force", action="store_true", help="take it from the agent holding it (recorded)")
    rel = sub.add_parser("release", help="finish, block or hand back a task")
    rel.add_argument("task")
    rel.add_argument("--status", choices=RELEASE_STATUSES, default="done")
    rel.add_argument("--note", default="")
    rel.add_argument("--force", action="store_true", help="release a task another agent holds (recorded)")
    for p in (add, claim, rel):
        p.add_argument("--agent", required=True, help="agent:<harness>/<session id>, or a GitHub login")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    board = Board(args.board or default_board())
    try:
        if args.cmd == "list":
            tasks = board.read()["tasks"]
            if args.status:
                tasks = {k: t for k, t in tasks.items() if t["status"] == args.status}
            if args.json:
                print(json.dumps(tasks, indent=2))
            else:
                for key, t in sorted(tasks.items()):
                    print(f"{key:10} {t['priority']:4} {t['status']:8} {(t['owner'] or '-'):40} {t['title']}")
        elif args.cmd == "add":
            board.add(args.task, args.title, args.agent, args.priority)
            print(f"board: added {args.task}")
        elif args.cmd == "claim":
            board.claim(args.task, args.agent, args.force)
            print(f"board: {args.agent} claimed {args.task}")
        else:
            board.release(args.task, args.agent, args.status, args.note, args.force)
            print(f"board: {args.task} -> {args.status}")
    except BoardError as exc:
        print(f"board: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
