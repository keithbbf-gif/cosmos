"""The harness loop, the hands, and the seating method.

No provider is called. Two runs with the same script and the same tree
return the same halt. A seating observation returns one SOP and a second
call with that SOP already applied does not ask again.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from cosmos_harness.checks import grade
from cosmos_harness.hooks import HOOK_ORDER, prompt_bound, verify
from cosmos_harness.jail import Jail
from cosmos_harness.job import probe, refuse_unsandboxed_retry, run_child
from cosmos_harness.law import ahead_of_claude_record
from cosmos_harness.layers import HANDS, Stack, bind, scrub_env
from cosmos_harness.learn import host_constants, remember, seat_proof, step, unmapped
from cosmos_harness.loop import Driver, Sample, ToolCall, _verdict_line, run
from cosmos_harness.oracle import Oracle
from cosmos_harness.pack import materialize
from cosmos_harness.refuse import Refuse
from cosmos_harness.tools import Hands, execute
from cosmos_harness.wire import body, load_tools, system_is_wrap

PASS = ("PASS", "PASS", "PASS", "PASS")
SOURCE = "def answer():\n    return 1\n"
GOOD = (
    "import math\n"
    "def constants() -> tuple:\n"
    "    return (math.pi, math.sqrt(2), math.e, math.log(1))\n"
)


class Script(Driver):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = list(samples)
        self.seen = 0

    def sample(self, messages: tuple[str, ...]) -> Sample:
        self.seen += 1
        return self.samples.pop(0)


def _stack(where: Path, mode: str = "act") -> Stack:
    return bind(Stack(
        role="CODER",
        model="anthropic/claude-opus-5.5",
        what="python",
        first_line="NONE",
        wrap="Role: CODER. You write python only.",
        style="No fence. No essay.",
        skills=(),
        where=where,
        task="Make answer() return 2.",
        oracle_argv=(
            sys.executable,
            "-c",
            "import bug; raise SystemExit(0 if bug.answer()==2 else 1)",
        ),
        mode=mode,
    ))


def _tree(path: Path, source: str = SOURCE, mode: str = "act") -> Stack:
    path.mkdir()
    (path / "bug.py").write_text(source, encoding="utf-8", newline="\n")
    return _stack(path, mode)


def _go(stack: Stack, samples: list[Sample], *, checks: tuple[str, ...] | None = PASS):
    jail = Jail(stack.where)
    oracle = Oracle(jail, stack.oracle_argv)
    hands = Hands(jail, oracle, mode=stack.mode)
    pack = stack.where / "_pack"
    materialize(stack, pack)
    driver = Script(samples)
    halt = run(stack, driver, oracle, hands, pack_dir=pack, checks=checks)
    return halt, driver


def test_eight_hooks_and_eight_hands():
    assert len(HOOK_ORDER) == 8
    assert HOOK_ORDER[0] == "prompt_in" and HOOK_ORDER[-1] == "done"
    assert HANDS == ("read", "glob", "grep", "edit", "write", "archive", "oracle", "worktree")
    assert "delete" not in HANDS and "bash" not in HANDS and "shell" not in HANDS


def test_same_script_same_halt(tmp_path: Path):
    """A latch does not depend on the model past the tool name. Two runs match."""
    root = tmp_path / "once"
    stack = _tree(root)
    call = [Sample(stack.model, "no", (ToolCall("1", "delete", {"path": "bug.py"}),))]
    first, driver_a = _go(stack, call)
    second, driver_b = _go(stack, call)
    assert first == second
    assert first.state == "HALT_GUARD_HELD"
    assert first.latch is True
    assert driver_a.seen == 1 and driver_b.seen == 1
    assert (root / "bug.py").is_file()


def test_edit_then_done_and_a_copy_traces_match(tmp_path: Path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    stack_a = _tree(left)
    shutil.copytree(left, right)
    stack_b = _stack(right)

    def samples(model: str) -> list[Sample]:
        return [
            Sample(model, "edit", (ToolCall("1", "edit", {"path": "bug.py", "old": "return 1", "new": "return 2"}),)),
            Sample(model, "done", ()),
        ]

    halt_a, _ = _go(stack_a, samples(stack_a.model))
    halt_b, _ = _go(stack_b, samples(stack_b.model))
    assert halt_a.state == "DONE" and halt_b.state == "DONE"
    assert halt_a.trace == halt_b.trace
    assert halt_a.turns == halt_b.turns == 2
    assert halt_a.bundle is not None and halt_b.bundle is not None
    assert halt_a.bundle["diff_hash"] == halt_b.bundle["diff_hash"]
    assert halt_a.bundle["cmd_hash"] == halt_b.bundle["cmd_hash"]
    assert "return 2" in (left / "bug.py").read_text(encoding="utf-8")


def test_pack_hash_ignores_the_journal(tmp_path: Path):
    from cosmos_harness.bundle import make
    from cosmos_harness.hooks import done

    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "TASK.md").write_text("task\n", encoding="utf-8")
    (pack / "seat.jsonl").write_text('{"seated": false}\n', encoding="utf-8")
    argv = ("py", "-c", "raise SystemExit(1)")
    first = make(patches=["p"], oracle_argv=argv, oracle_log_hash="a", pack_dir=pack)
    (pack / "seat.jsonl").write_text('{"seated": false, "n": 2}\n', encoding="utf-8")
    second = make(patches=["p"], oracle_argv=argv, oracle_log_hash="a", pack_dir=pack)
    assert first.pack_hash == second.pack_hash
    assert first.pack_hash
    empty = make(patches=["p"], oracle_argv=argv, oracle_log_hash="a", pack_dir=tmp_path / "missing")
    assert empty.pack_hash == ""
    refused = done(empty.as_dict())
    assert refused.allow is False and refused.reason == "INCOMPLETE_BUNDLE"


def test_a_second_edit_of_the_same_line_still_grades(tmp_path: Path):
    root = tmp_path / "twice"
    stack = _tree(root)
    edit = ToolCall("1", "edit", {"path": "bug.py", "old": "return 1", "new": "return 2"})
    again = ToolCall("2", "edit", {"path": "bug.py", "old": "return 1", "new": "return 2"})
    halt, driver = _go(stack, [
        Sample(stack.model, "edit", (edit,)),
        Sample(stack.model, "again", (again,)),
        Sample(stack.model, "NONE\n", ()),
    ])
    assert halt.state == "DONE"
    assert halt.latch is False
    assert driver.seen == 3
    assert halt.reason == "bundle"
    assert "return 2" in (root / "bug.py").read_text(encoding="utf-8")


def test_turn_cap_stops_at_eight(tmp_path: Path):
    root = tmp_path / "cap"
    stack = _tree(root)
    calls = [Sample(stack.model, "read", (ToolCall(str(i), "read", {"path": "bug.py"}),)) for i in range(8)]
    halt, driver = _go(stack, calls, checks=None)
    assert halt.state == "HALT_MAX_TURNS"
    assert halt.turns == 8
    assert driver.seen == 8


def test_contract_names_the_allowed_set():
    judge = Stack(
        role="JUDGE",
        model="qwen/qwen3.8-27b:free",
        what="text",
        first_line="UNMEASURED",
        wrap="role = JUDGE\n",
        style="",
        skills=("none extra",),
        where=Path("."),
        task="grade",
        oracle_argv=("py", "-c", "raise SystemExit(1)"),
        mode="plan",
    )
    assert judge.contract_line() == (
        "CONTRACT role=JUDGE what=text "
        "first_line=KEEP|DROP|NONE|HOLD|UNMEASURED "
        "model=qwen/qwen3.8-27b:free"
    )


def test_verdict_line_peels_a_leading_token():
    coder = ("NONE", "diff --git")
    assert _verdict_line("diff --git a/bug.py b/bug.py\n", coder) == "diff --git"
    assert _verdict_line("NONE\n", coder) == "NONE"
    assert _verdict_line("MAYBE no\n", ("KEEP", "DROP", "NONE", "HOLD", "UNMEASURED")) == "MAYBE no"
    judge = ("KEEP", "DROP", "NONE", "HOLD", "UNMEASURED")
    assert _verdict_line("DROP. The file returns 1 instead of 2.", judge) == "DROP"
    assert _verdict_line("**DROP**\n", judge) == "DROP"
    assert _verdict_line("**DROP** Rather than producing incorrect results.", judge) == "DROP"
    assert _verdict_line("- UNMEASURED\n", judge) == "UNMEASURED"
    assert _verdict_line("NONETHELESS\n", judge) == "NONETHELESS"


def test_plan_judge_closes_on_the_verdict(tmp_path: Path):
    root = tmp_path / "judge"
    root.mkdir()
    (root / "bug.py").write_text(SOURCE, encoding="utf-8", newline="\n")
    stack = bind(Stack(
        role="JUDGE",
        model="openai/gpt-5.6-luna:floor",
        what="text",
        first_line="UNMEASURED",
        wrap="role = JUDGE\npen = none\n",
        style="Findings first.",
        skills=("none extra",),
        where=root,
        task="Grade bug.py. answer() must return 2.",
        oracle_argv=(sys.executable, "-c", "raise SystemExit(1)"),
        mode="plan",
    ))
    halt, driver = _go(stack, [
        Sample(stack.model, "", (ToolCall("1", "read", {"path": "bug.py"}),)),
        Sample(stack.model, "DROP\nanswer() returns 1.\n", ()),
    ])
    assert halt.state == "VERDICT"
    assert halt.reason == "DROP"
    assert halt.latch is False
    assert halt.bundle is None
    assert driver.seen == 2
    assert "return 1" in (root / "bug.py").read_text(encoding="utf-8")
    refused, _idle = _go(stack, [Sample(stack.model, "MAYBE\nno\n", ())])
    assert refused.state == "FIRST_LINE"
    assert refused.reason == "MAYBE"
    glued, _glued = _go(stack, [
        Sample(stack.model, "DROP The file returns 1 instead of 2.\n", ()),
    ])
    assert glued.state == "VERDICT"
    assert glued.reason == "DROP"


def test_act_coder_without_a_fix_stays_red(tmp_path: Path):
    root = tmp_path / "still-red"
    stack = _tree(root)
    halt, driver = _go(stack, [Sample(stack.model, "NONE\n", ())])
    assert halt.state == "GATE_FAILED"
    assert halt.reason == "ORACLE_STILL_RED"
    assert driver.seen == 1
    assert "return 1" in (root / "bug.py").read_text(encoding="utf-8")


def test_plan_mode_refuses_the_edit(tmp_path: Path):
    root = tmp_path / "plan"
    stack = _tree(root, mode="plan")
    halt, driver = _go(stack, [
        Sample(stack.model, "edit", (ToolCall("1", "edit", {"path": "bug.py", "old": "return 1", "new": "return 2"}),)),
    ])
    assert halt.state == "HALT_GUARD_HELD"
    assert halt.reason == "PLAN_MODE"
    assert driver.seen == 1
    assert "return 1" in (root / "bug.py").read_text(encoding="utf-8")


def test_pin_swap_halts(tmp_path: Path):
    root = tmp_path / "pin"
    stack = _tree(root)
    halt, _driver = _go(stack, [Sample("other-model", "swap", ())])
    assert halt.state == "PIN_SWAP"


def test_codex_door_binds_and_grok_does_not(tmp_path: Path):
    root = tmp_path / "doors"
    stack = _tree(root)
    codex = replace(stack, door="codex")
    bound = prompt_bound(codex)
    assert bound.allow is True and bound.reason == stack.model
    halt, driver = _go(codex, [Sample(stack.model, "hold", ())])
    assert halt.state != "DOOR"
    assert driver.seen == 1
    grok = replace(stack, door="grok")
    refused = prompt_bound(grok)
    assert refused.allow is False and refused.reason == "DOOR"
    halted, idle = _go(grok, [Sample(stack.model, "no", ())])
    assert halted.state == "DOOR"
    assert idle.seen == 0


def test_floor_suffix_matches_the_served_id(tmp_path: Path):
    root = tmp_path / "flex"
    stack = replace(_tree(root), model="openai/gpt-6-luna:floor", door="codex")
    halt, driver = _go(stack, [Sample("openai/gpt-6-luna", "HOLD", ())])
    assert halt.state != "PIN_SWAP"
    assert driver.seen == 1


def test_one_scar_confirms_once_and_journals(tmp_path: Path):
    """A provider detail is one journal line and one confirming sample."""
    root = tmp_path / "scar"
    stack = _tree(root)
    detail = "empty keys=content,reasoning,refusal,role"
    halt, driver = _go(stack, [
        Sample(stack.model, "", provider_detail=detail),
        Sample(stack.model, "NONE", ()),
        Sample(stack.model, "third", ()),
    ])
    assert driver.seen == 2
    assert len(driver.samples) == 1
    assert halt.state != "PIN_SWAP"
    journal = root / "_pack" / "seat.jsonl"
    rows = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["sop"] == "effort_low"
    assert rows[0]["seated"] is False


def test_a_second_scar_does_not_sample_again(tmp_path: Path):
    root = tmp_path / "twice"
    stack = _tree(root)
    detail = "empty keys=content,reasoning,refusal,role"
    halt, driver = _go(stack, [
        Sample(stack.model, "", provider_detail=detail),
        Sample(stack.model, "", provider_detail=detail),
        Sample(stack.model, "", provider_detail=detail),
    ])
    assert driver.seen == 2
    assert len(driver.samples) == 1
    assert halt.state == "stop"
    rows = [json.loads(line) for line in (root / "_pack" / "seat.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [row["sop"] for row in rows] == ["effort_low", "stop"]
    assert all(row["seated"] is False for row in rows)


def test_already_green_does_not_sample(tmp_path: Path):
    root = tmp_path / "green"
    stack = _tree(root, "def answer():\n    return 2\n")
    driver = Script([Sample(stack.model, "no", ())])
    jail = Jail(stack.where)
    halt = run(
        stack, driver, Oracle(jail, stack.oracle_argv), Hands(jail, Oracle(jail, stack.oracle_argv)),
        pack_dir=stack.where, checks=PASS,
    )
    # Hands was built with a different Oracle than run's oracle. prove_red is on run's oracle.
    assert halt.state == "ORACLE_ALREADY_GREEN"
    assert driver.seen == 0


def test_hands_archive_and_jail(tmp_path: Path):
    root = tmp_path / "hands"
    stack = _tree(root)
    jail = Jail(root)
    oracle = Oracle(jail, stack.oracle_argv)
    oracle.prove_red()
    hands = Hands(jail, oracle, oracle_red=True)
    assert "return 1" in execute(hands, "read", {"path": "bug.py"}).text
    assert "bug.py" in execute(hands, "grep", {"text": "return 1"}).text
    assert execute(hands, "glob", {"pattern": "*.py"}).text.strip() == "bug.py"
    execute(hands, "write", {"path": "note.txt", "content": "kept"})
    archived = execute(hands, "archive", {"path": "note.txt"})
    assert not (root / "note.txt").exists()
    assert (root / archived.text).is_file()
    with pytest.raises(Refuse) as exc:
        jail.resolve("../outside")
    assert exc.value.reason == "PATH"
    with pytest.raises(Refuse):
        execute(hands, "bash", {"cmd": "whoami"})


def test_style_stays_off_the_system_turn(tmp_path: Path):
    root = tmp_path / "wire"
    stack = _tree(root)
    payload = body(stack, load_tools(Path(__file__).resolve().parents[1] / "pack" / "L6_TOOLS.json"))
    assert system_is_wrap(payload, stack)
    assert stack.style in payload["messages"][1]["content"]
    assert payload["provider"] == {"allow_fallbacks": False}
    assert payload["model"] == stack.model


def test_floor_on_free_and_live_are_refused(tmp_path: Path):
    root = tmp_path / "bind"
    root.mkdir()
    with pytest.raises(Refuse) as exc:
        bind(Stack(
            role="CODER", model="google/gemma:free:floor", what="python", first_line="NONE",
            wrap="Role: CODER.", style="", skills=(), where=root, task="x",
            oracle_argv=(sys.executable, "-c", "raise SystemExit(1)"),
        ))
    assert exc.value.reason == "FLOOR_ON_FREE"
    live = root / "live"
    live.mkdir()
    with pytest.raises(Refuse) as exc:
        bind(Stack(
            role="CODER", model="anthropic/claude-opus-5.5", what="python", first_line="NONE",
            wrap="Role: CODER.", style="", skills=(), where=live, task="x",
            oracle_argv=(sys.executable, "-c", "raise SystemExit(1)"),
        ))
    assert exc.value.reason == "LIVE_TREE"


def test_seating_learns_one_sop_and_records_the_stop(tmp_path: Path):
    pcm = "Unsupported value: 'audio.format' does not support 'wav'. Supported values are: 'pcm16'."
    taken = step("openai/gpt-audio", http=400, detail=pcm, form="audio")
    assert taken.sop == "audio_pcm16" and taken.again is True
    again = step("openai/gpt-audio", http=400, detail=pcm, form="audio", applied=("audio_pcm16",))
    assert again.again is False
    opus = step(
        "anthropic/claude-opus-5.5",
        http=200,
        detail="empty keys=content,reasoning,refusal,role",
        mouth="",
    )
    assert opus.sop == "effort_low" and opus.again is True
    waiting = step(
        "anthropic/claude-opus-5.5:batch",
        http=200,
        detail="in_progress batch_id=batch-1790818271-Def65LfNlMJNTTabjiru",
    )
    assert waiting.sop == "batch_open" and waiting.again is False
    journal = tmp_path / "seat.jsonl"
    remember(journal, waiting, method="batch_submit", http=200)
    remember(journal, taken, method="audio_pcm16", http=400)
    stops = unmapped(journal)
    assert [row["sop"] for row in stops] == ["batch_open"]
    assert seat_proof("inference-net/schematron-v2-turbo", "inference-net/schematron-v2-turbo", GOOD)["seated"] is True
    foreign = seat_proof("openrouter/auto-beta", "openai/gpt-5.6-sol", GOOD)
    assert foreign["seated"] is False and foreign["scar"] == "MOUTH_FOREIGN"
    assert host_constants("User Safety: safe")["ok"] is False


def test_upstream_stop_is_listed(tmp_path: Path):
    taken = step("nvidia/nemotron-3-ultra-550b-a55b:free", http=500, detail="Upstream error")
    assert taken.sop == "upstream" and taken.again is False
    journal = tmp_path / "seat.jsonl"
    remember(journal, taken, method="upstream", http=500)
    assert [row["sop"] for row in unmapped(journal)] == ["upstream"]


def test_checker_child_drops_a_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from cosmos_harness import checks

    captured: dict[str, str] = {}

    def capture(*_args, **kwargs):
        captured.update(kwargs["env"])

        class Proc:
            returncode = 0
            stdout = ""
            stderr = ""

        return Proc()

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setattr(checks.subprocess, "run", capture)
    code, out, err = checks._run([sys.executable, "-c", "pass"], tmp_path)
    assert (code, out, err) == (0, "", "")
    assert "OPENROUTER_API_KEY" not in captured
    assert captured["PYTHONDONTWRITEBYTECODE"] == "1"


def test_job_is_not_wipe_proof_and_unsandboxed_retry_raises():
    enclosure = probe()
    assert enclosure.wipe_proof is False
    assert enclosure.reason == "policy_only"
    with pytest.raises(Refuse) as exc:
        refuse_unsandboxed_retry()
    assert exc.value.reason == "UNSANDBOXED_RETRY"


def test_recorded_law_is_ahead_of_claude_zeros():
    assert ahead_of_claude_record()


def _pytest_status(root: Path) -> str:
    return next(row["status"] for row in grade(root) if row["tool"] == "pytest")


def test_pytest_executes(tmp_path: Path):
    ok = tmp_path / "ok"
    ok.mkdir()
    (ok / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    assert _pytest_status(ok) == "PASS"
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "test_bad.py").write_text("def test_bad():\n    assert False\n", encoding="utf-8")
    assert _pytest_status(bad) == "FAIL"
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "mod.py").write_text("x = 1\n", encoding="utf-8")
    assert _pytest_status(plain) == "NO_TESTS"


def test_scar_with_calls_is_orphaned_debt(tmp_path: Path):
    root = tmp_path / "debt"
    stack = _tree(root)
    halt, driver = _go(stack, [
        Sample(
            stack.model,
            "",
            (ToolCall("1", "read", {"path": "bug.py"}),),
            provider_detail="empty keys=content,reasoning,refusal,role",
        ),
    ])
    assert halt.state == "ORPHANED_DEBT"
    assert driver.seen == 1
    assert not (root / "_pack" / "seat.jsonl").exists()


def test_empty_error_model_is_classified_before_the_pin(tmp_path: Path):
    root = tmp_path / "empty-model"
    stack = _tree(root)
    detail = "empty keys=content,reasoning,refusal,role"
    halt, driver = _go(stack, [
        Sample("", "", provider_detail=detail),
        Sample(stack.model, "NONE", ()),
    ])
    assert halt.state != "PIN_SWAP"
    assert driver.seen == 2
    rows = [json.loads(line) for line in (root / "_pack" / "seat.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["sop"] == "effort_low"
    assert rows[0]["seated"] is False


def test_http_404_is_slug_dead(tmp_path: Path):
    root = tmp_path / "dead"
    stack = _tree(root)
    halt, driver = _go(stack, [
        Sample(stack.model, "", provider_detail="gone", provider_http=404),
    ])
    assert driver.seen == 1
    assert halt.state == "stop"
    rows = [json.loads(line) for line in (root / "_pack" / "seat.jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows[0]["scar"] == "SLUG_DEAD"
    assert rows[0]["http"] == 404
    assert rows[0]["seated"] is False


def test_write_cap_reserved_paths_and_hand_args(tmp_path: Path):
    root = tmp_path / "bounded"
    stack = _tree(root)
    jail = Jail(root)
    oracle = Oracle(jail, stack.oracle_argv)
    oracle.prove_red()
    hands = Hands(jail, oracle, oracle_red=True)
    with pytest.raises(Refuse) as exc:
        execute(hands, "write", {"path": "big.txt", "content": "x" * 256_001})
    assert exc.value.reason == "TOO_LARGE"
    with pytest.raises(Refuse) as exc:
        execute(hands, "write", {"path": "_pack/note.txt", "content": "no"})
    assert exc.value.reason == "RESERVED_PATH"
    with pytest.raises(Refuse) as exc:
        execute(hands, "edit", {"path": "_delme/bug.py", "old": "a", "new": "b"})
    assert exc.value.reason == "RESERVED_PATH"
    (root / "_pack").mkdir()
    (root / "_pack" / "note.txt").write_text("x\n", encoding="utf-8")
    with pytest.raises(Refuse) as exc:
        execute(hands, "archive", {"path": "_pack/note.txt"})
    assert exc.value.reason == "RESERVED_PATH"
    assert (root / "_pack" / "note.txt").is_file()
    execute(hands, "write", {"path": "note.txt", "content": "kept"})
    archived = execute(hands, "archive", {"path": "note.txt"})
    assert (root / archived.text).is_file()
    with pytest.raises(Refuse) as exc:
        execute(hands, "read", ["bug.py"])
    assert exc.value.reason == "HAND_ARGS"


def test_verify_accepts_only_four_passes():
    assert verify(oracle_green=True, checks=PASS).allow is True
    short = verify(oracle_green=True, checks=("PASS", "OK"))
    assert short.allow is False and short.reason == "OK"
    length = verify(oracle_green=True, checks=("PASS",) * 3)
    assert length.allow is False and length.reason == "CHECKS"
    failed = verify(oracle_green=True, checks=("PASS", "FAIL", "PASS", "PASS"))
    assert failed.allow is False and failed.reason == "FAIL"


def test_run_child_returns_the_exit_code(tmp_path: Path):
    env = scrub_env(dict(os.environ)) | {"PYTHONDONTWRITEBYTECODE": "1"}
    code, _out, _err = run_child(
        [sys.executable, "-c", "raise SystemExit(3)"],
        cwd=tmp_path,
        env=env,
        timeout=15,
    )
    assert code == 3
    slow, _out, err = run_child(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        cwd=tmp_path,
        env=env,
        timeout=0.8,
    )
    assert slow == 124
    assert "timeout" in err
    enclosure = probe()
    assert enclosure.wipe_proof is False
    assert enclosure.reason == "policy_only"
