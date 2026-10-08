"""OpenCode door. No provider is called. The binary is not started.

A missing binary raises. A job refusal does not start a second process.
Seated is true only when the stream names this pin and the host runs the file.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from cosmos_harness.job import _ACTIVE_LIMIT, probe, run_child
from cosmos_harness.layers import scrub_env
from cosmos_harness.opencode_door import (
    OPENCODE_PINS,
    argv_for,
    guard,
    model_arg,
    prompt_for,
    seat,
    seats_on_opencode,
    served_for_run,
    served_from_stream,
    write_pack,
)
from cosmos_harness.refuse import Refuse

GOOD = (
    "import math\n"
    "def constants() -> tuple:\n"
    "    return (math.pi, math.sqrt(2), math.e, math.log(1))\n"
)
PIN = "thinkingmachines/inkling:free"
KEY = "sk-testsecret"


def test_model_arg_prefixes_once():
    assert model_arg(PIN) == "openrouter/" + PIN
    assert model_arg("openrouter/" + PIN) == "openrouter/" + PIN
    assert model_arg(model_arg(PIN)) == model_arg(PIN)
    with pytest.raises(Refuse) as missing:
        model_arg("openrouter/free")
    assert missing.value.reason == "NOT_A_PIN"
    with pytest.raises(Refuse) as both:
        model_arg("thinkingmachines/inkling:free:floor")
    assert both.value.reason == "FLOOR_ON_FREE"


def test_these_pins_use_the_opencode_door():
    assert seats_on_opencode("thinkingmachines/inkling:free")
    assert seats_on_opencode("thinkingmachines/inkling-small:free")
    assert seats_on_opencode("openrouter/inclusionai/ling-3.0-flash")
    assert "inclusionai/ling-3.0-flash" in OPENCODE_PINS
    assert seats_on_opencode("inclusionai/ling-3.0-flash-sante:free") is False
    assert seats_on_opencode("openai/gpt-5.6-luna:floor") is False
    assert seats_on_opencode("google/gemma-4-26b-a4b-it:free") is False


def test_argv_is_the_measured_spawn_without_auto(tmp_path: Path):
    prompt = prompt_for(PIN, "Write constants.py.\n")
    built = argv_for(PIN, tmp_path, prompt)
    assert built[:3] == ["opencode.cmd", "--pure", "run"]
    assert built[3:5] == ["--format", "json"]
    assert "--dir" in built
    assert built[built.index("-m") + 1] == "openrouter/" + PIN
    assert "--" in built
    assert "--auto" not in built
    assert "--system-prompt" not in built
    assert "--fallback-model" not in built
    guard(built)
    guard(["opencode.cmd", "run", "--", "do not pass --auto"])
    with pytest.raises(Refuse) as exc:
        guard(["opencode.cmd", "--auto", "run", "--", "stay"])
    assert exc.value.reason == "FORBID_FLAG"


def test_a_long_mission_stays_on_disk(tmp_path: Path):
    task = "stay\n" + ("word " * 400)
    prompt = prompt_for(PIN, task)
    assert len(prompt) <= 1200
    assert "TASK.md" in prompt
    assert "Stay in this directory." in prompt
    root = write_pack(tmp_path, pin=PIN, task=task)
    assert task.strip().splitlines()[0] in (root / "TASK.md").read_text(encoding="utf-8")
    assert len(prompt) < len(task)


def test_pack_leaves_an_existing_agents_file_and_denies_the_leave(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("OLD\n", encoding="utf-8")
    root = write_pack(tmp_path, pin=PIN)
    assert (root / "AGENTS.md").read_text(encoding="utf-8") == "OLD\n"
    body = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    assert body["permission"]["external_directory"] == "deny"
    assert body["permission"]["edit"] == "allow"
    assert "auto" not in json.dumps(body)
    assert KEY not in json.dumps(body)
    with pytest.raises(Refuse) as exc:
        write_pack(tmp_path / "live" / "attempt", pin=PIN)
    assert exc.value.reason == "LIVE_TREE"


def test_served_id_comes_from_the_stream_only():
    assert served_from_stream('{"model":"thinkingmachines/inkling:free"}') == PIN
    line = json.dumps({"type": "step_finish", "part": {"modelID": PIN}})
    assert served_from_stream(line) == PIN
    both = '{"model":"alpha/one"}\n{"modelID":"beta/two"}\n'
    assert served_from_stream(both) == ""
    assert served_from_stream("the model was " + PIN) == ""
    assert served_from_stream("") == ""


def test_session_row_supplies_the_id_the_stream_omits(tmp_path: Path):
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE session (id TEXT, model TEXT)")
    con.execute(
        "INSERT INTO session (id, model) VALUES (?, ?)",
        ("ses_abc", '{"id":"thinkingmachines/inkling:free","providerID":"openrouter"}'),
    )
    con.execute(
        "INSERT INTO session (id, model) VALUES (?, ?)",
        ("ses_other", '{"id":"other/pin","providerID":"openrouter"}'),
    )
    con.commit()
    con.close()
    stream = '{"type":"step_start","sessionID":"ses_abc"}\n'
    assert served_for_run(stream, db) == PIN
    conflict = '{"model":"other/pin","sessionID":"ses_abc"}\n'
    assert served_for_run(conflict, db) == ""
    both = '{"sessionID":"ses_abc"}\n{"sessionID":"ses_other"}\n'
    assert served_for_run(both, db) == ""


def test_missing_binary_is_a_refusal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cosmos_harness.opencode_door.shutil.which", lambda _name: None)

    def boom(*_args, **_kwargs):
        raise AssertionError("spawned")

    monkeypatch.setattr("cosmos_harness.opencode_door.run_child", boom)
    with pytest.raises(Refuse) as exc:
        seat(PIN, tmp_path, key=KEY)
    assert exc.value.reason == "NO_BINARY"
    rows = (tmp_path / "seat.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(rows[-1])["seated"] is False


def test_assign_failure_does_not_continue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    calls = {"n": 0}
    monkeypatch.setattr("cosmos_harness.opencode_door.shutil.which", lambda _name: "opencode.cmd")

    def once(*_args, **_kwargs):
        calls["n"] += 1
        raise Refuse("UNENCLOSED_CHILD", "assign")

    monkeypatch.setattr("cosmos_harness.opencode_door.run_child", once)
    with pytest.raises(Refuse) as exc:
        seat(PIN, tmp_path, key=KEY)
    assert exc.value.reason == "UNENCLOSED_CHILD"
    assert calls["n"] == 1
    assert json.loads((tmp_path / "seat.jsonl").read_text(encoding="utf-8").splitlines()[-1])["seated"] is False


def test_empty_served_id_does_not_seat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cosmos_harness.opencode_door.shutil.which", lambda _name: "opencode.cmd")

    def fake(argv, *, cwd, env, timeout, active_limit):
        del argv, timeout
        assert active_limit is None
        assert env["OPENROUTER_API_KEY"] == KEY
        (cwd / "constants.py").write_text(GOOD, encoding="utf-8")
        return 0, '{"type":"step_finish","part":{"cost":0}}\n', ""

    monkeypatch.setattr("cosmos_harness.opencode_door.run_child", fake)
    row = seat(PIN, tmp_path, key=KEY)
    assert (tmp_path / "constants.py").read_text(encoding="utf-8") == GOOD
    assert row.served == ""
    assert row.seated is False
    assert row.scar == "SKU_UNBOUND"
    assert row.wipe_proof is False
    assert row.journal_seated == (False,)
    assert KEY not in (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert all(KEY not in arg for arg in row.argv)


def test_matching_stream_and_host_seats(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cosmos_harness.opencode_door.shutil.which", lambda _name: "opencode.cmd")

    def fake(argv, *, cwd, env, timeout, active_limit):
        del timeout
        assert active_limit is None
        assert "--auto" not in argv
        assert env["OPENROUTER_API_KEY"] == KEY
        assert all(KEY not in arg for arg in argv)
        (cwd / "constants.py").write_text(GOOD, encoding="utf-8")
        leaked = json.dumps({"model": PIN, "note": KEY}) + "\n"
        return 0, leaked, ""

    monkeypatch.setattr("cosmos_harness.opencode_door.run_child", fake)
    row = seat(PIN, tmp_path, key=KEY)
    assert row.seated is True
    assert row.matched is True
    assert row.host_ok is True
    assert row.enclosed is True
    assert row.wipe_proof is False
    assert row.scar == ""
    assert row.journal_seated == (False,)
    saved = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert KEY not in saved
    assert "sk-redacted" in saved


def test_a_pool_hold_does_not_seat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cosmos_harness.opencode_door.shutil.which", lambda _name: "opencode.cmd")

    def fake(argv, *, cwd, env, timeout, active_limit):
        del argv, env, timeout, active_limit
        (cwd / "constants.py").write_text(GOOD, encoding="utf-8")
        event = {
            "type": "error",
            "error": {"data": {"message": "429 rate limit"}},
            "model": PIN,
        }
        return 1, json.dumps(event) + "\n", ""

    monkeypatch.setattr("cosmos_harness.opencode_door.run_child", fake)
    row = seat(PIN, tmp_path, key=KEY)
    assert row.seated is False
    assert row.scar == "UPSTREAM_POOL"
    assert row.matched is True


def test_process_cap_defaults_to_four_and_none_still_encloses(tmp_path: Path):
    assert _ACTIVE_LIMIT == 4
    assert run_child.__kwdefaults__["active_limit"] == 4
    with pytest.raises(Refuse) as exc:
        run_child(
            [sys.executable, "-c", "print(1)"],
            cwd=tmp_path,
            env=scrub_env(dict(os.environ)) | {"PYTHONDONTWRITEBYTECODE": "1"},
            timeout=15,
            active_limit=0,
        )
    assert exc.value.reason == "UNENCLOSED_CHILD"
    env = scrub_env(dict(os.environ)) | {"PYTHONDONTWRITEBYTECODE": "1"}
    code, out, _err = run_child(
        [sys.executable, "-c", "print(3)"],
        cwd=tmp_path,
        env=env,
        timeout=15,
        active_limit=None,
    )
    assert code == 0
    assert out.strip() == "3"
    enclosure = probe()
    assert enclosure.wipe_proof is False
    assert enclosure.reason == "policy_only"
