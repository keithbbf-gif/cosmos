"""Read panels, gated mutations, and loopback bind. No listener."""

from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from web_dashboard import (
    APPROVED,
    DEFAULT_PORT,
    DISPLAY,
    LOOPBACK,
    PANELS,
    ROW_CAP,
    SCHEMA,
    VALUE_CAP,
    WIDGET_CAP,
    BindPlan,
    Dashboard,
    Display,
    Grant,
    Mutation,
    Panel,
    PanelView,
    Policy,
    Projection,
    Reading,
    Widget,
    add_widget,
    check_bind,
    mutate,
    panel,
    panels,
    read,
    records,
    reset,
    screen,
)

NONCE = "nonce-0123456789abcdef"
OTHER = "other-0123456789abcdef"
FRESH = "fresh-0123456789abcdef"


def _code(caught: pytest.ExceptionInfo[Refuse]) -> str:
    err = caught.value
    assert secret_shape(str(err)) is False
    assert secret_shape(repr(err)) is False
    return err.code


def _row(view: PanelView, index: int) -> Reading:
    return view.rows[index]


def _refuse_panel(name: str) -> str:
    try:
        panel(name)
    except Refuse as err:
        assert secret_shape(str(err)) is False
        return err.code
    raise AssertionError(name)


def _refuse_screen(body: str) -> str:
    try:
        screen(body)
    except Refuse as err:
        assert secret_shape(str(err)) is False
        return err.code
    raise AssertionError(body)


def _imports_and_calls(source: str) -> tuple[set[str], set[tuple[str, str]]]:
    tree = ast.parse(source)
    modules: set[str] = set()
    calls: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(("", func.id))
            elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                calls.add((func.value.id, func.attr))
    return modules, calls


def test_schema_catalog_and_reads_take_no_nonce() -> None:
    assert SCHEMA == "cosmos-hermes-web_dashboard/1"
    described = panels()
    assert len(described) == len(PANELS) == 18
    assert described[0].name == "status"
    assert described[0].schema == SCHEMA
    assert "version" in described[0].fields
    assert described[-3].name == "spend"
    assert described[-2].name == "queue"
    assert described[-1].name == "leases"
    again = panels()
    assert again == described
    status = panel("status")
    assert isinstance(status, Panel)
    assert status == described[0]
    for fn in (panels, panel, Dashboard.read, Dashboard.records, screen):
        assert "nonce" not in inspect.signature(fn).parameters
    source = Path(inspect.getfile(check_bind)).read_text(encoding="utf-8")
    modules, calls = _imports_and_calls(source)
    banned_modules = {
        "pty",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "http",
        "asyncio",
        "threading",
        "multiprocessing",
        "importlib",
        "os",
    }
    assert modules.isdisjoint(banned_modules)
    banned_calls = {"exec", "eval", "compile", "__import__", "open", "system", "popen", "spawn", "Popen"}
    for owner, name in calls:
        if name in banned_calls:
            assert owner == "re" and name == "compile"
        assert owner not in banned_modules


def test_read_success_profile_and_unmeasured() -> None:
    dash = Dashboard()
    assert "measured=False" in repr(dash)
    with pytest.raises(Refuse) as missing:
        dash.read("status")
    assert _code(missing) == "UNMEASURED"
    with pytest.raises(Refuse) as cold_rows:
        dash.records()
    assert _code(cold_rows) == "UNMEASURED"
    first = dash.rebuild(
        (
            Reading("status", "version", "1.2.3"),
            Reading("status", "gateway", "stopped", "worker"),
            Reading("sessions", "title", "hello", "default"),
        )
    )
    assert isinstance(first, Projection)
    assert first.schema == SCHEMA
    assert first.count == 3
    assert first.cap == ROW_CAP
    view = dash.read("status")
    assert isinstance(view, PanelView)
    assert view.schema == SCHEMA
    assert view.cap == ROW_CAP
    assert view.limit == ROW_CAP
    assert view.capped is False
    assert len(view.rows) == 1
    assert view.rows[0].value == "1.2.3"
    assert view.rows[0].profile == "default"
    worker = dash.read("status", profile="worker")
    assert tuple(row.key for row in worker.rows) == ("gateway",)
    assert dash.read("logs").rows == ()
    assert dash.records() == (
        Reading("status", "version", "1.2.3"),
        Reading("status", "gateway", "stopped", "worker"),
        Reading("sessions", "title", "hello", "default"),
    )
    empty = dash.rebuild(())
    assert empty.count == 0
    assert dash.records() == ()
    assert dash.read("status").rows == ()
    assert "measured=True" in repr(dash)


def test_row_cap_is_recorded_and_not_raised() -> None:
    rows = tuple(
        Reading("sessions", "title", f"s{i}", "default") for i in range(ROW_CAP + 5)
    )
    dash = Dashboard()
    dash.rebuild(rows)
    high = dash.read("sessions", limit=ROW_CAP + 100)
    assert high.cap == ROW_CAP
    assert high.limit == ROW_CAP
    assert high.asked_limit == ROW_CAP + 100
    assert high.capped is True
    assert len(high.rows) == ROW_CAP
    assert high.rows[0].value == "s0"
    assert high.rows[-1].value == f"s{ROW_CAP - 1}"
    narrow = dash.read("sessions", limit=3)
    assert narrow.limit == 3
    assert narrow.asked_limit == 3
    assert narrow.capped is False
    assert len(narrow.rows) == 3
    assert narrow.cap == ROW_CAP


def test_failed_rebuild_keeps_prior_and_refuses_secrets() -> None:
    dash = Dashboard()
    kept = Reading("status", "version", "kept")
    dash.rebuild((kept,))
    secret = "sk-livekeyvalue"
    with pytest.raises(Refuse) as bad:
        dash.rebuild((kept, Reading("env", "preview", secret)))
    assert _code(bad) == "SECRET"
    assert dash.read("status").rows == (kept,)
    assert dash.records() == (kept,)
    assert secret not in repr(dash)
    with pytest.raises(Refuse) as shape:
        dash.rebuild("nope")
    assert _code(shape) == "BAD_ROW"
    with pytest.raises(Refuse) as item:
        dash.rebuild((kept, object()))
    assert _code(item) == "BAD_ROW"
    assert dash.read("status").rows[0].value == "kept"
    with pytest.raises(Refuse) as blank:
        Reading("status", "version", "")
    assert _code(blank) == "BAD_ROW"


def test_bind_loopback_public_grant_and_insecure_noop() -> None:
    local = check_bind(LOOPBACK)
    assert isinstance(local, BindPlan)
    assert local.host == "127.0.0.1"
    assert local.port == DEFAULT_PORT
    assert local.loopback is True
    assert local.auth_required is False
    assert local.public_grant is False
    assert local.insecure_ignored is False
    assert local.schema == SCHEMA
    custom = check_bind("127.0.0.1", port=8080)
    assert custom.port == 8080
    assert custom.loopback is True
    for host in ("0.0.0.0", "localhost", "::1", "10.0.0.8", "127.0.0.2"):
        with pytest.raises(Refuse) as caught:
            check_bind(host)
        assert _code(caught) == "PUBLIC_BIND"
    with pytest.raises(Refuse) as ignored:
        check_bind("0.0.0.0", insecure=True)
    assert _code(ignored) == "PUBLIC_BIND"
    opened = check_bind("0.0.0.0", public_grant=True, insecure=True)
    assert opened.loopback is False
    assert opened.auth_required is True
    assert opened.public_grant is True
    assert opened.insecure_ignored is True
    named = check_bind("10.1.2.3", "dash-public")
    assert named.public_grant is True
    assert named.auth_required is True
    with pytest.raises(Refuse) as empty_grant:
        check_bind("10.0.0.8", "")
    assert _code(empty_grant) == "BAD_GRANT"
    with pytest.raises(Refuse) as empty_local:
        check_bind(LOOPBACK, "")
    assert _code(empty_local) == "BAD_GRANT"
    still = check_bind("127.0.0.1", insecure=True)
    assert still.loopback is True
    assert still.auth_required is False
    assert still.insecure_ignored is True


def test_widget_shape_and_cap() -> None:
    dash = Dashboard()
    added = dash.add_widget("status-rail")
    assert isinstance(added, Widget)
    assert added.name == "status-rail"
    assert added.count == 1
    assert added.cap == WIDGET_CAP
    assert added.capped is False
    assert added.schema == SCHEMA
    assert dash.widgets() == ("status-rail",)
    assert dash.add_widget("a" * 32).name == "a" * 32
    for bad in ("", "Bad", "a" * 33, "has_under", "a/b", "ab c", "-ok".upper()):
        with pytest.raises(Refuse) as caught:
            dash.add_widget(bad)
        assert _code(caught) == "BAD_WIDGET"
    with pytest.raises(Refuse) as again:
        dash.add_widget("status-rail")
    assert _code(again) == "ALREADY"
    high = Dashboard(widget_cap=WIDGET_CAP + 50)
    recorded = high.policy()
    assert isinstance(recorded, Policy)
    assert recorded.widget_cap == WIDGET_CAP
    assert recorded.asked_widget_cap == WIDGET_CAP + 50
    assert recorded.applied_widget_cap == WIDGET_CAP
    assert recorded.widget_capped is True
    assert recorded.row_cap == ROW_CAP
    for index in range(WIDGET_CAP):
        high.add_widget(f"w-{index}")
    assert high.widgets()[-1] == f"w-{WIDGET_CAP - 1}"
    with pytest.raises(Refuse) as full:
        high.add_widget("overflow")
    assert _code(full) == "AT_CAP"
    assert len(high.widgets()) == WIDGET_CAP
    low = Dashboard(widget_cap=2)
    assert low.policy().applied_widget_cap == 2
    assert low.policy().widget_cap == WIDGET_CAP
    assert low.policy().widget_capped is False
    low.add_widget("one")
    low.add_widget("two")
    with pytest.raises(Refuse) as tight:
        low.add_widget("three")
    assert _code(tight) == "AT_CAP"
    assert low.widgets() == ("one", "two")


def test_mutate_needs_nonce_then_approves_once() -> None:
    dash = Dashboard()
    with pytest.raises(Refuse) as empty:
        dash.mutate("config.save", "")
    assert _code(empty) == "NEED_APPROVAL"
    with pytest.raises(Refuse) as omitted:
        dash.mutate("chat.open")
    assert _code(omitted) == "NEED_APPROVAL"
    with pytest.raises(Refuse) as missing:
        dash.mutate("env.set", NONCE)
    assert _code(missing) == "UNGRANTED"
    issued = dash.grant("chat.open", NONCE)
    assert isinstance(issued, Grant)
    assert issued.action == "chat.open"
    assert issued.schema == SCHEMA
    assert NONCE not in issued.nonce_sha
    assert NONCE not in repr(issued)
    approved = dash.mutate("chat.open", NONCE)
    assert isinstance(approved, Mutation)
    assert approved.code == APPROVED
    assert approved.schema == SCHEMA
    assert approved.action == "chat.open"
    assert approved.nonce_sha == issued.nonce_sha
    assert NONCE not in repr(approved)
    assert NONCE not in repr(dash)
    with pytest.raises(Refuse) as replay:
        dash.mutate("chat.open", NONCE)
    assert _code(replay) == "REPLAY"
    with pytest.raises(Refuse) as spent:
        dash.grant("chat.open", NONCE)
    assert _code(spent) == "REPLAY"
    with pytest.raises(Refuse) as other:
        dash.mutate("env.set", NONCE)
    assert _code(other) == "UNGRANTED"


def test_nonce_mismatch_retries_once() -> None:
    dash = Dashboard()
    dash.grant("skill.toggle", NONCE)
    with pytest.raises(Refuse) as first:
        dash.mutate("skill.toggle", OTHER)
    assert _code(first) == "BAD_NONCE"
    done = dash.mutate("skill.toggle", NONCE)
    assert done.code == APPROVED
    dash.grant("cron.create", NONCE)
    with pytest.raises(Refuse) as miss:
        dash.mutate("cron.create", OTHER)
    assert _code(miss) == "BAD_NONCE"
    with pytest.raises(Refuse) as second:
        dash.mutate("cron.create", FRESH)
    assert _code(second) == "RETRY_CAP"
    with pytest.raises(Refuse) as later:
        dash.mutate("cron.create", NONCE)
    assert _code(later) == "RETRY_CAP"
    renewed = dash.grant("cron.create", FRESH)
    assert renewed.nonce_sha != done.nonce_sha
    assert dash.mutate("cron.create", FRESH).action == "cron.create"


def test_shape_mismatch_does_not_burn_the_grant() -> None:
    dash = Dashboard()
    dash.grant("config.save", NONCE)
    with pytest.raises(Refuse) as short:
        dash.mutate("config.save", "short")
    assert _code(short) == "BAD_NONCE"
    assert dash.mutate("config.save", NONCE).code == APPROVED


def test_closed_actions_and_remaining_codes() -> None:
    dash = Dashboard()
    for action in ("",):
        with pytest.raises(Refuse) as bad:
            dash.mutate(action, NONCE)
        assert _code(bad) == "BAD_ACTION"
    for action in ("off", "yolo", "config.write", "Widget"):
        with pytest.raises(Refuse) as unknown:
            dash.mutate(action, NONCE)
        assert _code(unknown) == "UNCLASSIFIED"
    with pytest.raises(Refuse) as secret_action:
        dash.mutate("sk-livekeyvalue", NONCE)
    assert _code(secret_action) == "SECRET"
    with pytest.raises(Refuse) as secret_nonce:
        dash.grant("env.set", "sk-livekeyvalue")
    assert _code(secret_nonce) == "SECRET"
    with pytest.raises(Refuse) as secret_widget:
        dash.add_widget("sk-abcdefgh")
    assert _code(secret_widget) == "SECRET"
    with pytest.raises(Refuse) as secret_host:
        check_bind("sk-abcdefghij")
    assert _code(secret_host) == "SECRET"
    with pytest.raises(Refuse) as secret_grant:
        check_bind("10.0.0.8", "sk-abcdefghij")
    assert _code(secret_grant) == "SECRET"
    with pytest.raises(Refuse) as secret_profile:
        dash.rebuild((Reading("status", "version", "1"),))
        dash.read("status", profile="sk-abcdefgh")
    assert _code(secret_profile) == "SECRET"
    with pytest.raises(Refuse) as panel_name:
        panel("missing")
    assert _code(panel_name) == "UNKNOWN_PANEL"
    with pytest.raises(Refuse) as bad_key:
        Reading("status", "nope", "x")
    assert _code(bad_key) == "BAD_KEY"
    sample = panel("status")
    with pytest.raises(Refuse) as bad_panel:
        Panel(name=sample.name, fields=("version",), schema=SCHEMA)
    assert _code(bad_panel) == "BAD_PANEL"
    with pytest.raises(Refuse) as bad_schema:
        Panel(name=sample.name, fields=sample.fields, schema="cosmos-hermes-web_dashboard/2")
    assert _code(bad_schema) == "BAD_SCHEMA"
    with pytest.raises(Refuse) as bad_code:
        Mutation(
            action="config.save",
            nonce_sha="ab" * 32,
            code="NEED_APPROVAL",
            schema=SCHEMA,
        )
    assert _code(bad_code) == "BAD_CODE"
    with pytest.raises(Refuse) as bad_grant:
        check_bind("10.0.0.8", 1)
    assert _code(bad_grant) == "BAD_GRANT"
    with pytest.raises(Refuse) as bad_host:
        check_bind("127.0.0.1/admin")
    assert _code(bad_host) == "BAD_HOST"
    with pytest.raises(Refuse) as spaced:
        check_bind("not a host")
    assert _code(spaced) == "BAD_HOST"
    with pytest.raises(Refuse) as flag:
        check_bind(LOOPBACK, insecure="off")
    assert _code(flag) == "NOT_BOOL"
    with pytest.raises(Refuse) as cap:
        Dashboard(widget_cap=0)
    assert _code(cap) == "BAD_LIMIT"
    with pytest.raises(Refuse) as flagged:
        Dashboard(widget_cap=True)
    assert _code(flagged) == "NOT_INT"
    with pytest.raises(Refuse) as port_type:
        check_bind(LOOPBACK, port=True)
    assert _code(port_type) == "NOT_INT"
    with pytest.raises(Refuse) as port_low:
        check_bind(LOOPBACK, port=0)
    assert _code(port_low) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as port_high:
        check_bind(LOOPBACK, port=70000)
    assert _code(port_high) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as limit_type:
        dash.read("status", limit=True)
    assert _code(limit_type) == "NOT_INT"
    with pytest.raises(Refuse) as limit_low:
        dash.read("status", limit=0)
    assert _code(limit_low) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as profile:
        dash.read("status", profile="Worker")
    assert _code(profile) == "BAD_PROFILE"
    with pytest.raises(Refuse) as text:
        check_bind(3)
    assert _code(text) == "NOT_TEXT"
    with pytest.raises(Refuse) as widget_type:
        dash.add_widget(3)
    assert _code(widget_type) == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        check_bind("127.0.0.1\x00")
    assert _code(nul) == "NULL_BYTE"
    with pytest.raises(Refuse) as over_host:
        check_bind("a" * (253 + 1))
    assert _code(over_host) == "OVERSIZE"
    with pytest.raises(Refuse) as over_value:
        Reading("logs", "line", "m" * (VALUE_CAP + 1))
    assert _code(over_value) == "OVERSIZE"
    with pytest.raises(Refuse) as over_widget:
        dash.add_widget("b" * 65)
    assert _code(over_widget) == "OVERSIZE"
    with pytest.raises(Refuse) as bad_projection:
        Projection(schema=SCHEMA, count=0, cap=ROW_CAP + 1)
    assert _code(bad_projection) == "BAD_LIMIT"
    with pytest.raises(Refuse) as empty_grant:
        dash.grant("env.delete", "")
    assert _code(empty_grant) == "BAD_NONCE"
    issued = dash.grant("env.delete", NONCE)
    assert secret_shape(repr(issued)) is False
    replaced = dash.grant("env.delete", OTHER)
    assert replaced.nonce_sha != issued.nonce_sha
    assert dash.mutate("env.delete", OTHER).code == APPROVED
    with pytest.raises(Refuse) as stale:
        dash.mutate("env.delete", NONCE)
    assert _code(stale) == "UNGRANTED"


def test_spent_nonce_is_replay_and_does_not_burn_the_new_grant() -> None:
    dash = Dashboard()
    dash.grant("config.save", NONCE)
    assert dash.mutate("config.save", NONCE).code == APPROVED
    dash.grant("config.save", OTHER)
    with pytest.raises(Refuse) as spent:
        dash.mutate("config.save", NONCE)
    assert _code(spent) == "REPLAY"
    assert dash.mutate("config.save", OTHER).code == APPROVED


def test_pty_or_shell_is_import_or_call_not_a_substring() -> None:
    assert _refuse_panel("pty") == "BAD_PANEL"
    assert _refuse_panel("shell") == "BAD_PANEL"
    assert _refuse_panel("empty") == "UNKNOWN_PANEL"
    assert _refuse_panel("eggshell") == "UNKNOWN_PANEL"
    assert _refuse_panel("pty.spawn(argv)") == "BAD_PANEL"
    for body in (
        "import pty",
        "from pty import spawn",
        "import os, pty",
        "import subprocess",
        "from shell import run",
        "from os import system",
        "from os import path, popen",
        "pty.spawn(argv)",
        "shell(argv)",
        "os.system(cmd)",
        "subprocess.Popen(argv)",
    ):
        assert _refuse_screen(body) == "BAD_PANEL"
    for body in (
        "empty",
        "eggshell",
        "bankruptcy",
        "websocket.recv()",
        "empty()",
        "eggshell()",
        "import empty, eggshell",
        "the empty eggshell sat on the card",
        "def empty():\n    return eggshell\n",
    ):
        shown = screen(body)
        assert isinstance(shown, Display)
        assert shown.kind == DISPLAY
        assert shown.schema == SCHEMA
    with pytest.raises(Refuse) as forged:
        Display(kind="pty", schema=SCHEMA)
    assert _code(forged) == "BAD_PANEL"
    dash = Dashboard()
    assert dash.add_widget("empty").name == "empty"
    assert dash.add_widget("eggshell").name == "eggshell"


@dataclass(frozen=True, slots=True)
class _Story:
    built: Projection
    rebuilt: Projection
    spend: PanelView
    queue: PanelView
    leases: PanelView
    spend_again: PanelView
    queue_again: PanelView
    leases_again: PanelView
    pty: str
    shell: str
    imported: str
    called: str
    display: str
    widget: str
    eggshell: str


def test_example_web_dashboard() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.built == first.rebuilt
    assert first.built.count == 9
    assert first.spend == first.spend_again
    assert first.queue == first.queue_again
    assert first.leases == first.leases_again
    assert first.spend.name == "spend"
    assert first.queue.name == "queue"
    assert first.leases.name == "leases"
    assert _row(first.spend, 0).value == "ada-lamp"
    assert _row(first.spend, 1).value == "porch light on"
    assert _row(first.queue, 0).value == "dusk-sweep"
    assert _row(first.leases, 0).value == "ada-session"
    assert first.pty == "BAD_PANEL"
    assert first.shell == "BAD_PANEL"
    assert first.imported == "BAD_PANEL"
    assert first.called == "BAD_PANEL"
    assert first.display == DISPLAY
    assert first.widget == "empty"
    assert first.eggshell == "eggshell"
    assert secret_shape(repr(first.spend)) is False
    assert secret_shape(repr(first.queue)) is False
    assert secret_shape(repr(first.leases)) is False


def _story() -> _Story:
    dash = Dashboard()
    rows = (
        Reading("spend", "card", "ada-lamp", "hall"),
        Reading("spend", "note", "porch light on", "hall"),
        Reading("spend", "amount", "4.50", "hall"),
        Reading("queue", "name", "dusk-sweep", "hall"),
        Reading("queue", "note", "queue the hall card", "hall"),
        Reading("queue", "state", "paused", "hall"),
        Reading("leases", "session", "ada-session", "hall"),
        Reading("leases", "holder", "ada", "hall"),
        Reading("leases", "note", "lease the porch light", "hall"),
    )
    built = dash.rebuild(rows)
    spend = dash.read("spend", profile="hall")
    queue = dash.read("queue", profile="hall")
    leases = dash.read("leases", profile="hall")
    clone = Dashboard()
    rebuilt = clone.rebuild(dash.records())
    return _Story(
        built=built,
        rebuilt=rebuilt,
        spend=spend,
        queue=queue,
        leases=leases,
        spend_again=clone.read("spend", profile="hall"),
        queue_again=clone.read("queue", profile="hall"),
        leases_again=clone.read("leases", profile="hall"),
        pty=_refuse_panel("pty"),
        shell=_refuse_panel("shell"),
        imported=_refuse_screen("import pty"),
        called=_refuse_screen("shell(argv)"),
        display=screen("empty = eggshell").kind,
        widget=dash.add_widget("empty").name,
        eggshell=dash.add_widget("eggshell").name,
    )


def test_module_surface_resets() -> None:
    reset()
    with pytest.raises(Refuse) as bare:
        mutate("session.delete", "")
    assert _code(bare) == "NEED_APPROVAL"
    with pytest.raises(Refuse) as cold:
        read("skills")
    assert _code(cold) == "UNMEASURED"
    added = add_widget("side-rail")
    assert added.name == "side-rail"
    reset()
    with pytest.raises(Refuse) as cleared:
        read("skills")
    assert _code(cleared) == "UNMEASURED"
    from web_dashboard import widgets

    assert widgets() == ()
    with pytest.raises(Refuse) as cold_rows:
        records()
    assert _code(cold_rows) == "UNMEASURED"
