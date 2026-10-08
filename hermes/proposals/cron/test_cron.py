"""Parser refusals and vehicles for the cron proposal."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import cron
from cosmos_hermes import Refuse


def test_schema_and_floor() -> None:
    assert cron.SCHEMA == "cosmos-hermes-cron/1"
    assert cron.FLOOR_S == 60.0
    assert cron.POLICY_CAP == 256
    assert "schtasks" in cron.MODES
    assert "detached_daemon" in cron.MODES
    assert "onlogon" in cron.MODES


def test_hourly_every_day_weekly_and_minutes() -> None:
    hourly = cron.parse("hourly")
    assert hourly.mode == "schtasks"
    assert hourly.paused is False
    assert hourly.interval_s == 3600.0
    assert hourly.schtasks == cron.Schedule("HOURLY", None, None, None)
    assert hourly.tr_extra == ("--once",)
    assert hourly == cron.parse("  Every   hour ")
    assert hourly == cron.parse("once an hour")
    assert hourly == cron.parse("every 60 minutes")
    assert hourly == cron.parse("every 1 hour")
    daily = cron.parse("every day at 09:30")
    assert daily.mode == "schtasks"
    assert daily.interval_s is None
    assert daily.schtasks == cron.Schedule("DAILY", None, "09:30", None)
    assert daily == cron.parse("every day at 9:30")
    assert daily == cron.parse("0 9 * * *".replace("0 9", "30 9"))
    weekly = cron.parse("weekly")
    assert weekly.mode == "schtasks"
    assert weekly.interval_s == 604800.0
    assert weekly.schtasks == cron.Schedule("WEEKLY", None, None, None)
    assert weekly == cron.parse("every week")
    minutes = cron.parse("every 5 minutes")
    assert minutes.mode == "schtasks"
    assert minutes.interval_s == 300.0
    assert minutes.schtasks == cron.Schedule("minute", 5, None, None)
    assert minutes == cron.parse("every 5m")
    assert cron.parse("every 120 minutes").schtasks == cron.Schedule("HOURLY", 2, None, None)
    assert cron.parse("every 24 hours").schtasks == cron.Schedule("DAILY", None, None, None)
    assert cron.parse("every 24 hours").interval_s == 86400.0


def test_every_two_days_and_long_exact_periods() -> None:
    two = cron.parse("every 48 hours")
    assert two.mode == "schtasks"
    assert two.schtasks == cron.Schedule("DAILY", 2, None, None)
    assert two.interval_s == 172800.0
    year = cron.parse("every 8760 hours")
    assert year.schtasks == cron.Schedule("DAILY", 365, None, None)
    assert year.interval_s == float(cron.MAX_INTERVAL_S)


def test_on_logon_and_cron_expressions() -> None:
    logon = cron.parse("on logon")
    assert logon.mode == "onlogon"
    assert logon.interval_s is None
    assert logon.schtasks == cron.Schedule("onlogon", None, None, None)
    assert logon.tr_extra == ("--loop",)
    assert logon == cron.parse("ON-LOGON")
    assert logon == cron.parse("at login")
    assert cron.parse("every day at 9:00") == cron.parse("0 9 * * *")
    assert cron.parse("0 * * * *") == cron.parse("hourly")
    stepped = cron.parse("*/5 * * * *")
    assert stepped.schtasks == cron.Schedule("minute", 5, None, None)
    assert stepped.interval_s == 300.0
    assert cron.parse("* * * * *") == cron.parse("every 1 minutes")
    assert cron.parse("every 60 seconds") == cron.parse("* * * * *")
    half_hour = cron.parse("30 * * * *")
    assert half_hour.schtasks == cron.Schedule("HOURLY", None, "00:30", None)
    assert cron.parse("0 */6 * * *").schtasks == cron.Schedule("HOURLY", 6, None, None)
    weekly = cron.parse("30 8 * * 1")
    assert weekly.schtasks == cron.Schedule("WEEKLY", None, "08:30", "MON")
    assert weekly.interval_s is None
    assert cron.parse("0 9 * * sun") == cron.parse("0 9 * * 0")
    assert cron.parse("0 9 * * 7") == cron.parse("0 9 * * sunday")
    weekdays = cron.parse("every weekday at 09:00")
    assert weekdays.mode == "schtasks"
    assert weekdays.interval_s is None
    assert weekdays.tr_extra == ("--once",)
    assert weekdays.schtasks == cron.Schedule("WEEKLY", None, "09:00", "MON,TUE,WED,THU,FRI")
    assert weekdays == cron.parse("weekdays at 9:00")
    assert weekdays == cron.parse("0 9 * * 1-5")
    assert weekdays == cron.parse("0 9 * * MON-FRI")
    assert weekdays == cron.parse("0 9 * * mon,tue,wed,thu,fri")
    assert cron.parse("30 9 * * fri,mon").schtasks == cron.Schedule("WEEKLY", None, "09:30", "MON,FRI")
    monthly = cron.parse("30 8 1 * *")
    assert monthly.schtasks == cron.Schedule("MONTHLY", None, "08:30", "1")
    assert monthly.interval_s is None


def test_subminute_is_detached_and_does_not_sleep() -> None:
    short = cron.parse("every 15 seconds")
    assert short.mode == "detached_daemon"
    assert short.interval_s == 15.0
    assert short.schtasks is None
    assert short.tr_extra == ("--loop",)
    assert short == cron.parse("every 15s")
    assert short == cron.parse("every 0.25 minutes")
    assert cron.parse("every 59 seconds").mode == "detached_daemon"
    assert cron.parse("every 59 seconds").interval_s == 59.0
    floor = cron.parse("every 60 seconds")
    assert floor.mode == "schtasks"
    assert floor.interval_s == 60.0
    assert floor.schtasks == cron.Schedule("minute", 1, None, None)
    source = Path(__file__).with_name("cron.py").read_text(encoding="utf-8")
    assert "sleep" not in source
    assert "subprocess" not in source
    assert "threading" not in source


def test_pause_and_resume_flip_the_flag() -> None:
    record = cron.parse("hourly")
    held = cron.pause(record)
    assert record.paused is False
    assert held.paused is True
    assert held.mode == record.mode
    assert held.schtasks == record.schtasks
    assert cron.pause(held).paused is True
    released = cron.resume(held)
    assert released.paused is False
    assert cron.resume(record).paused is False
    assert released == record


def test_unrecognized_rather_than_guessing() -> None:
    phrases = (
        "",
        "   ",
        "every",
        "daily",
        "every day",
        "every day at",
        "every day at 9",
        "every day at 9am",
        "every day at 24:00",
        "every 15",
        "soon",
        "in 30m",
        "logon",
        "weekly at 09:00",
        "every weekday",
        "every weekday at",
        "every weekday at 9",
        "every weekday at 9am",
        "every weekday at 24:00",
        "every weekday at 09:60",
        "weekends at 09:00",
        "0 9 * * mon,mon",
        "0 9 * * fri-mon",
        "0 9 * * 1-8",
        "0 9 * * mon-fri-sat",
        "0 9 1 * 1",
        "0 9 * * 8",
        "* * * *",
        "0 0 9 * * *",
        "every 90 seconds",
        "every 1.5 minutes",
        "every 25 hours",
        "every 0 minutes",
        "every 5 minutes and hourly",
        "on logon hourly",
        "@hourly",
        "2026-03-15T09:00:00",
    )
    for phrase in phrases:
        with pytest.raises(Refuse) as caught:
            cron.parse(phrase)
        assert caught.value.code == "UNRECOGNIZED"


def test_bounds_secret_and_cap() -> None:
    with pytest.raises(Refuse) as not_text:
        cron.parse(None)
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as raw_bytes:
        cron.parse(b"hourly")
    assert raw_bytes.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        cron.parse("hourly\x00")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as bad:
        cron.parse("hourly", cap=0)
    assert bad.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flag:
        cron.parse("hourly", cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as huge:
        cron.parse("every 1000000 minutes")
    assert huge.value.code == "OUT_OF_RANGE"
    secret = "every 5 minutes sk-abcdefgh"
    with pytest.raises(Refuse) as hidden:
        cron.parse(secret)
    assert hidden.value.code == "SECRET"
    assert "abcdefgh" not in hidden.value.detail
    assert "sk-" not in str(hidden.value)
    for raw in ("Bearer abcdefghijk", "api_key=supersecret"):
        with pytest.raises(Refuse) as caught:
            cron.parse(raw)
        assert caught.value.code == "SECRET"
        assert "supersecret" not in str(caught.value)
        assert "abcdefghijk" not in str(caught.value)
    raised = cron.POLICY_CAP * 10
    rec = cron.parse("hourly", cap=raised)
    assert rec.cap == cron.POLICY_CAP
    assert rec.cap < raised
    with pytest.raises(Refuse) as over:
        cron.parse("h" * (cron.POLICY_CAP + 1), cap=raised)
    assert over.value.code == "OVERSIZE"
    tight = cron.parse("hourly", cap=6)
    assert tight.cap == 6
    with pytest.raises(Refuse) as tighter:
        cron.parse("hourly", cap=5)
    assert tighter.value.code == "OVERSIZE"


def test_bad_record_and_repr() -> None:
    with pytest.raises(Refuse) as paused:
        cron.pause("hourly")
    assert paused.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as resumed:
        cron.resume(None)
    assert resumed.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as fired:
        cron.run("hourly")
    assert fired.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as snapped:
        cron.snapshot(None)
    assert snapped.value.code == "BAD_RECORD"
    for mode in ("off", "yolo"):
        with pytest.raises(Refuse) as caught:
            cron.Cadence(
                mode=mode,
                interval_s=None,
                schtasks=None,
                paused=False,
                cap=cron.POLICY_CAP,
                tr_extra=("--once",),
            )
        assert caught.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as below:
        cron.Cadence(
            mode="schtasks",
            interval_s=15.0,
            schtasks=cron.Schedule("minute", 1, None, None),
            paused=False,
            cap=cron.POLICY_CAP,
            tr_extra=("--once",),
        )
    assert below.value.code == "BAD_RECORD"
    record = cron.parse("every day at 09:00")
    text = repr((record, cron.pause(record), cron.resume(record), cron.snapshot(record)))
    assert "sk-" not in text
    assert "Bearer" not in text
    assert "api_key=" not in text


def test_parser_source_has_no_scheduler() -> None:
    source = Path(__file__).with_name("cron.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: set[str] = set()
    names: set[str] = set()
    attrs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                attrs.add(func.attr)
    assert modules.isdisjoint(
        {
            "subprocess",
            "threading",
            "asyncio",
            "socket",
            "urllib",
            "requests",
            "pickle",
            "sched",
            "time",
            "http",
            "multiprocessing",
            "ctypes",
        }
    )
    assert names.isdisjoint({"sleep", "exec", "eval", "compile", "system"})
    assert attrs.isdisjoint(
        {
            "sleep",
            "Popen",
            "system",
            "create_task",
            "Thread",
            "Timer",
            "check_output",
            "popen",
            "fork",
            "spawn",
            "urlopen",
            "run_schtasks",
        }
    )


def test_same_input_same_record() -> None:
    left = cron.parse("every 5 minutes")
    right = cron.parse("Every  5  minutes")
    assert left == right
    assert cron.parse("*/15 * * * *") == cron.parse("every 15 minutes")


def test_snapshot_rebuild_and_stale() -> None:
    phrases = ("hourly", "on logon", "every 15 seconds", "every weekday at 09:00")
    for phrase in phrases:
        record = cron.parse(phrase)
        assert cron.rebuild(cron.snapshot(record)) == record
        held = cron.pause(record)
        assert cron.rebuild(cron.snapshot(held)) == held
        assert cron.snapshot(record) == cron.snapshot(record)
    base = cron.snapshot(cron.parse("hourly"))
    stale = cron.Emitted(
        schema="cosmos-hermes-cron/0",
        mode=base.mode,
        interval_s=base.interval_s,
        sc="HOURLY",
        mo=None,
        st=None,
        day=None,
        paused=False,
        cap=base.cap,
        tr_extra=base.tr_extra,
    )
    with pytest.raises(Refuse) as stale_err:
        cron.rebuild(stale)
    assert stale_err.value.code == "STALE"
    drifted = cron.Emitted(
        schema=cron.SCHEMA,
        mode="schtasks",
        interval_s=15.0,
        sc="minute",
        mo=1,
        st=None,
        day=None,
        paused=False,
        cap=cron.POLICY_CAP,
        tr_extra=("--once",),
    )
    with pytest.raises(Refuse) as drifted_err:
        cron.rebuild(drifted)
    assert drifted_err.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as missing:
        cron.rebuild(None)
    assert missing.value.code == "BAD_RECORD"


def test_in_process_refuses() -> None:
    record = cron.parse("every 5 minutes")
    with pytest.raises(Refuse) as fired:
        cron.run(record)
    assert fired.value.code == "IN_PROCESS"
    assert "sk-" not in str(fired.value)
    for phrase in ("run the porch light in this process", "register a task", "start"):
        with pytest.raises(Refuse) as caught:
            cron.parse(phrase)
        assert caught.value.code == "IN_PROCESS"
    with pytest.raises(Refuse) as hidden:
        cron.parse("run sk-abcdefghij")
    assert hidden.value.code == "SECRET"
    assert "abcdefgh" not in str(hidden.value)


def _at(story: tuple[object, ...], index: int) -> object:
    return story[index]


def test_example_cron() -> None:
    """Mira pins the porch light, a weekday note, and the morning session."""

    def story() -> tuple[object, ...]:
        porch_light = cron.parse("every weekday at 09:00", cap=4096)
        assert porch_light.cap == cron.POLICY_CAP
        assert porch_light.mode == "schtasks"
        assert porch_light.interval_s is None
        assert porch_light.schtasks == cron.Schedule(
            "WEEKLY",
            None,
            "09:00",
            "MON,TUE,WED,THU,FRI",
        )
        note = cron.pause(porch_light)
        card = cron.snapshot(note)
        session = cron.rebuild(card)
        assert session == note
        assert session.paused is True
        with pytest.raises(Refuse) as phrase:
            cron.parse("run the porch light in this process")
        with pytest.raises(Refuse) as fired:
            cron.run(session)
        return (porch_light, note, card, session, phrase.value.code, fired.value.code)

    first = story()
    second = story()
    assert first == second
    assert _at(first, 4) == "IN_PROCESS"
    assert _at(first, 5) == "IN_PROCESS"
