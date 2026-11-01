"""The shared task board (#97): exclusive claims, recorded forcing, one locked file."""

from __future__ import annotations

import json
import threading
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "board.py"
spec = spec_from_file_location("acs_board", SCRIPT)
board_mod = module_from_spec(spec)
spec.loader.exec_module(board_mod)

A = "agent:codex/11111111-1111-4111-8111-111111111111"
B = "agent:workbuddy/22222222-2222-4222-8222-222222222222"


@pytest.fixture
def board(tmp_path):
    b = board_mod.Board(tmp_path / ".coord" / "board.json")
    b.add("T-1", "Fix release notes", A, "P1")
    return b


def test_a_claim_is_exclusive(board):
    board.claim("T-1", A)
    with pytest.raises(board_mod.BoardError, match="claimed by " + A):
        board.claim("T-1", B)
    with pytest.raises(board_mod.BoardError, match="not " + B):
        board.release("T-1", B)
    assert board.read()["tasks"]["T-1"]["owner"] == A


def test_forcing_is_allowed_and_recorded(board):
    board.claim("T-1", A)
    task = board.claim("T-1", B, force=True)
    assert task["owner"] == B
    assert task["history"][-1] == {**task["history"][-1], "agent": B, "action": "claim", "forced": True}
    assert "_forced" not in board.read()["tasks"]["T-1"]


def test_an_unforced_change_is_not_marked_forced(board):
    task = board.claim("T-1", A)
    assert "forced" not in task["history"][-1]


def test_release_frees_or_finishes_the_task(board):
    board.claim("T-1", A)
    assert board.release("T-1", A, "blocked", "waiting on CI")["owner"] is None
    board.claim("T-1", B)
    done = board.release("T-1", B, "done", "PR #40")
    assert (done["status"], done["owner"]) == ("done", B)
    with pytest.raises(board_mod.BoardError, match="done"):
        board.claim("T-1", A)


def test_every_change_is_in_history_and_the_event_log(board):
    board.claim("T-1", A)
    board.release("T-1", A, "done", "PR #40")
    actions = [h["action"] for h in board.read()["tasks"]["T-1"]["history"]]
    assert actions == ["add", "claim", "release:done"]
    events = [json.loads(line) for line in board.events.read_text().splitlines()]
    assert [(e["task"], e["action"]) for e in events] == [("T-1", "add"), ("T-1", "claim"), ("T-1", "release:done")]


def test_bad_input_is_refused_without_writing(board, tmp_path):
    before = board.path.read_text()
    for call in (
        lambda: board.add("", "x", A),
        lambda: board.add("T-1", "again", A),
        lambda: board.claim("T-9", A),
        lambda: board.claim("T-1", ""),
        lambda: board.release("T-1", A, "merged"),
    ):
        with pytest.raises(board_mod.BoardError):
            call()
    assert board.path.read_text() == before


def test_a_corrupt_board_is_reported_not_overwritten(board):
    board.path.write_text("{not json")
    with pytest.raises(board_mod.BoardError, match="not valid JSON"):
        board.claim("T-1", A)
    assert board.path.read_text() == "{not json"


def test_concurrent_claims_leave_exactly_one_owner(tmp_path):
    b = board_mod.Board(tmp_path / "board.json")
    b.add("T-1", "race", A)
    agents = [f"agent:codex/{i:08d}-0000-4000-8000-000000000000" for i in range(8)]
    wins, barrier = [], threading.Barrier(len(agents))

    def go(agent):
        barrier.wait()
        try:
            b.claim("T-1", agent)
            wins.append(agent)
        except board_mod.BoardError:
            pass

    threads = [threading.Thread(target=go, args=(a,)) for a in agents]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(wins) == 1
    assert b.read()["tasks"]["T-1"]["owner"] == wins[0]


def test_a_stale_lock_from_a_crashed_writer_is_cleared(board):
    board.lock.write_text("123")
    old = board.lock.stat().st_mtime - board_mod.LOCK_STALE - 5
    import os

    os.utime(board.lock, (old, old))
    board.claim("T-1", A)
    assert not board.lock.exists()


def test_the_command_line_round_trip(tmp_path, capsys):
    path = str(tmp_path / "b.json")
    assert board_mod.main(["--board", path, "add", "T-2", "Write docs", "--agent", A]) == 0
    assert board_mod.main(["--board", path, "claim", "T-2", "--agent", A]) == 0
    assert board_mod.main(["--board", path, "claim", "T-2", "--agent", B]) == 1
    assert "claimed by" in capsys.readouterr().err
    assert board_mod.main(["--board", path, "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["T-2"]["owner"] == A
