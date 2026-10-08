"""Wizard order, refusals, and the rule that a pasted key never reaches repr."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pytest

from cosmos_federation import DEFAULT_CAP_USD_MICROS, MAX_CAP_USD_MICROS, Refuse, secret_shape
from wizard import (
    RECOMMENDED_CAP_USD_MICROS,
    SCHEMA,
    Wizard,
    accept_key,
    begin,
    ready,
    submit,
)

_NOW = 1_700_000_000
_KEY = "sk-fakefakefake1234"
_CRED = "cred-openrouter-1"


def _code(err: BaseException) -> str:
    assert isinstance(err, Refuse)
    return err.code


def _assert_no_key(wiz: Wizard, raw: str) -> None:
    assert raw not in repr(wiz)
    assert "[REDACTED]" not in repr(wiz)
    for item in fields(wiz):
        assert getattr(wiz, item.name) != raw


def _at_key(now: int = _NOW) -> Wizard:
    wiz = begin(now)
    wiz = submit(wiz, "root", "peer", now)
    wiz = submit(wiz, "tree_id", "PeerOne", now)
    wiz = submit(wiz, "name", "Ada", now)
    return submit(wiz, "door", "openrouter", now)


def _at_bind(now: int = _NOW) -> Wizard:
    wiz = accept_key(_at_key(now), _KEY, _CRED, now)
    return submit(wiz, "cap", str(RECOMMENDED_CAP_USD_MICROS), now)


def test_schema_and_recommendation_are_not_autofilled() -> None:
    assert SCHEMA == "cosmos-federation-wizard/1"
    assert RECOMMENDED_CAP_USD_MICROS == DEFAULT_CAP_USD_MICROS
    assert RECOMMENDED_CAP_USD_MICROS <= MAX_CAP_USD_MICROS
    wiz = begin(_NOW)
    assert wiz.cap_usd_micros is None
    assert wiz.step == "root"
    assert ready(wiz) is False


def test_happy_order_records_caller_epochs() -> None:
    wiz = begin(10)
    assert wiz.started_epoch == 10
    wiz = submit(wiz, "root", "peer", 11)
    assert wiz.step == "tree_id"
    assert wiz.root == "peer"
    assert wiz.started_epoch == 10
    assert wiz.updated_epoch == 11
    first = wiz
    wiz = submit(wiz, "tree_id", "PeerOne", 12)
    assert first.step == "tree_id"
    assert wiz.step == "name"
    wiz = submit(wiz, "name", "Ada Lovelace", 13)
    assert wiz.step == "door"
    wiz = submit(wiz, "door", "OpenRouter", 14)
    assert wiz.step == "key"
    assert wiz.door == "openrouter"
    assert wiz.credential_id is None
    assert ready(wiz) is False


def test_out_of_order_is_step() -> None:
    wiz = begin(_NOW)
    for field in ("tree_id", "name", "door", "cap", "bind", "tls", "key", "confirm"):
        with pytest.raises(Refuse) as caught:
            submit(wiz, field, "peer", _NOW)
        assert _code(caught.value) == "STEP"
    assert wiz.step == "root"
    with pytest.raises(Refuse) as caught:
        accept_key(wiz, _KEY, _CRED, _NOW)
    assert _code(caught.value) == "STEP"
    _assert_no_key(wiz, _KEY)


def test_cap_before_key_is_step() -> None:
    wiz = _at_key()
    assert wiz.step == "key"
    with pytest.raises(Refuse) as caught:
        submit(wiz, "cap", str(DEFAULT_CAP_USD_MICROS), _NOW)
    assert _code(caught.value) == "STEP"
    held = accept_key(wiz, _KEY, _CRED, _NOW)
    assert held.step == "cap"
    with pytest.raises(Refuse) as caught:
        accept_key(held, _KEY, "cred-openrouter-2", _NOW)
    assert _code(caught.value) == "STEP"
    assert held.credential_id == _CRED


def test_repr_omits_pasted_key() -> None:
    # The fake key is the paste. It has to be accepted and then absent.
    raw = _KEY
    before = _at_key()
    wiz = accept_key(before, raw, _CRED, _NOW)
    assert before is not wiz
    assert before.credential_id is None
    assert wiz.credential_id == _CRED
    _assert_no_key(wiz, raw)
    assert _CRED in repr(wiz)
    done = submit(wiz, "cap", str(RECOMMENDED_CAP_USD_MICROS), _NOW)
    done = submit(done, "bind", "loopback", _NOW)
    _assert_no_key(done, raw)
    assert ready(done) is True


def test_key_must_be_secret_shaped() -> None:
    wiz = _at_key()
    with pytest.raises(Refuse) as caught:
        accept_key(wiz, "paste-your-key-here", _CRED, _NOW)
    assert _code(caught.value) == "KEY"
    assert wiz.credential_id is None
    assert wiz.step == "key"


def test_credential_id_cannot_be_the_key() -> None:
    with pytest.raises(Refuse) as caught:
        accept_key(_at_key(), _KEY, _KEY, _NOW)
    assert _code(caught.value) == "KEY"
    assert _KEY not in str(caught.value)


def test_anthropic_key_refused_via_check_door() -> None:
    raw = "sk-ant-fakefakefake1234"
    wiz = _at_key()
    with pytest.raises(Refuse) as caught:
        accept_key(wiz, raw, _CRED, _NOW)
    assert _code(caught.value) == "ANTHROPIC_OFF"
    assert raw not in str(caught.value)
    _assert_no_key(wiz, raw)


@pytest.mark.parametrize(
    "raw",
    [
        " sk-ant-fakefakefake1234",
        "\tsk-ant-fakefakefake1234",
        "Bearer sk-ant-fakefakefake1234",
        "xxsk-ant-fakefakefake1234",
        "sk-ant-" + ("a" * 520),
    ],
)
def test_wrapped_anthropic_paste_is_refused(raw: str) -> None:
    # Each one matches secret_shape. The short ones do not start with sk-ant-.
    assert secret_shape(raw) is True
    wiz = _at_key()
    with pytest.raises(Refuse) as caught:
        accept_key(wiz, raw, _CRED, _NOW)
    assert _code(caught.value) == "ANTHROPIC_OFF"
    assert raw not in str(caught.value)
    assert wiz.step == "key"
    assert wiz.credential_id is None
    _assert_no_key(wiz, raw)


def test_credential_id_with_anthropic_marker_is_refused() -> None:
    # Shorter than secret_shape, so only the marker check keeps it out of repr.
    cid = "pad-sk-ant-abc"
    assert secret_shape(cid) is False
    wiz = _at_key()
    with pytest.raises(Refuse) as caught:
        accept_key(wiz, _KEY, cid, _NOW)
    assert _code(caught.value) == "ANTHROPIC_OFF"
    assert cid not in str(caught.value)
    assert wiz.credential_id is None
    assert cid not in repr(wiz)


def test_anthropic_and_unknown_doors() -> None:
    wiz = begin(_NOW)
    wiz = submit(wiz, "root", "peer", _NOW)
    wiz = submit(wiz, "tree_id", "PeerOne", _NOW)
    wiz = submit(wiz, "name", "Ada", _NOW)
    for door in ("anthropic", "Anthropic", "claude", "vendor-claude-3"):
        with pytest.raises(Refuse) as caught:
            submit(wiz, "door", door, _NOW)
        assert _code(caught.value) == "ANTHROPIC_OFF"
    with pytest.raises(Refuse) as caught:
        submit(wiz, "door", "openai", _NOW)
    assert _code(caught.value) == "DOOR"
    assert wiz.step == "door"


def test_xai_door_keeps_id_not_key() -> None:
    wiz = begin(_NOW)
    wiz = submit(wiz, "root", "peer", _NOW)
    wiz = submit(wiz, "tree_id", "PeerTwo", _NOW)
    wiz = submit(wiz, "name", "Grace", _NOW)
    wiz = submit(wiz, "door", "XAI", _NOW)
    assert wiz.door == "xai"
    raw = "xai-fakefakefake"
    wiz = accept_key(wiz, raw, "cred-xai-1", _NOW)
    _assert_no_key(wiz, raw)
    assert wiz.credential_id == "cred-xai-1"
    assert wiz.step == "cap"


@pytest.mark.parametrize(
    "tree_id",
    ["GMesh", "KMesh-COSMOS-live", "COSMOS", "live", "main", "x", "1Peer"],
)
def test_bad_tree_id(tree_id: str) -> None:
    wiz = submit(begin(_NOW), "root", "peer", _NOW)
    with pytest.raises(Refuse) as caught:
        submit(wiz, "tree_id", tree_id, _NOW)
    assert _code(caught.value) == "TREE_ID"
    assert tree_id not in str(caught.value)


@pytest.mark.parametrize(
    "label",
    [
        "C:/cosmos",
        "C:\\cosmos",
        "\\\\server\\share",
        "/etc/peer",
        "peer/child",
        "..",
        ".",
        ".peer",
        "V:\\A\\Ai\\COSMOS",
    ],
)
def test_root_label_is_not_a_path(label: str) -> None:
    wiz = begin(_NOW)
    with pytest.raises(Refuse) as caught:
        submit(wiz, "root", label, _NOW)
    assert _code(caught.value) == "ROOT"
    assert wiz.root is None
    assert wiz.step == "root"


def test_empty_and_secret_text() -> None:
    with pytest.raises(Refuse) as caught:
        submit(begin(_NOW), "root", "   ", _NOW)
    assert _code(caught.value) == "BOUND"
    with pytest.raises(Refuse) as caught:
        submit(begin(_NOW), "root", _KEY, _NOW)
    assert _code(caught.value) == "SECRET"
    assert _KEY not in str(caught.value)
    named = submit(begin(_NOW), "root", "peer", _NOW)
    named = submit(named, "tree_id", "PeerOne", _NOW)
    with pytest.raises(Refuse) as caught:
        submit(named, "name", "  ", _NOW)
    assert _code(caught.value) == "BOUND"
    with pytest.raises(Refuse) as caught:
        submit(named, "name", _KEY, _NOW)
    assert _code(caught.value) == "SECRET"


def test_cap_integer_string_and_policy() -> None:
    wiz = accept_key(_at_key(), _KEY, _CRED, _NOW)
    ok = submit(wiz, "cap", str(MAX_CAP_USD_MICROS), _NOW)
    assert ok.cap_usd_micros == MAX_CAP_USD_MICROS
    assert ok.step == "bind"
    low = submit(wiz, "cap", "1", _NOW)
    assert low.cap_usd_micros == 1
    for bad in ("0", str(MAX_CAP_USD_MICROS + 1), "250_000", "", "nope", "1.5"):
        with pytest.raises(Refuse) as caught:
            submit(wiz, "cap", bad, _NOW)
        assert _code(caught.value) == "CAP"


def test_loopback_skips_tls_and_is_ready() -> None:
    wiz = _at_bind()
    assert wiz.step == "bind"
    assert ready(wiz) is False
    done = submit(wiz, "bind", "loopback", _NOW)
    assert done.step == "confirm"
    assert done.bind == "loopback"
    assert done.tls is None
    assert ready(done) is True
    with pytest.raises(Refuse) as caught:
        submit(done, "tls", "yes", _NOW)
    assert _code(caught.value) == "STEP"
    _assert_no_key(done, _KEY)


def test_remote_then_tls_then_confirm() -> None:
    wiz = _at_bind()
    with pytest.raises(Refuse) as caught:
        submit(wiz, "tls", "yes", _NOW)
    assert _code(caught.value) == "STEP"
    remote = submit(wiz, "bind", "remote", _NOW)
    assert remote.step == "tls"
    assert remote.bind == "remote"
    assert remote.tls is None
    assert ready(remote) is False
    with pytest.raises(Refuse) as caught:
        submit(remote, "tls", "no", _NOW)
    assert _code(caught.value) == "REMOTE_PLAIN"
    assert remote.tls is None
    with pytest.raises(Refuse) as caught:
        submit(remote, "tls", "YES", _NOW)
    assert _code(caught.value) == "REMOTE_PLAIN"
    done = submit(remote, "tls", "yes", _NOW + 3)
    assert done.step == "confirm"
    assert done.tls == "yes"
    assert done.started_epoch == _NOW
    assert done.updated_epoch == _NOW + 3
    assert ready(done) is True
    _assert_no_key(done, _KEY)
    with pytest.raises(Refuse) as caught:
        submit(done, "tls", "yes", _NOW)
    assert _code(caught.value) == "STEP"


def test_bind_vocabulary() -> None:
    wiz = _at_bind()
    with pytest.raises(Refuse) as caught:
        submit(wiz, "bind", "0.0.0.0", _NOW)
    assert _code(caught.value) == "BIND"
    assert wiz.bind is None


def test_ready_requires_confirm_and_every_answer() -> None:
    missing_id = Wizard(
        step="confirm",
        root="peer",
        tree_id="PeerOne",
        name="Ada",
        door="openrouter",
        credential_id=None,
        cap_usd_micros=DEFAULT_CAP_USD_MICROS,
        bind="loopback",
        tls=None,
        started_epoch=_NOW,
        updated_epoch=_NOW,
    )
    assert ready(missing_id) is False
    remote_plain = Wizard(
        step="confirm",
        root="peer",
        tree_id="PeerOne",
        name="Ada",
        door="openrouter",
        credential_id=_CRED,
        cap_usd_micros=DEFAULT_CAP_USD_MICROS,
        bind="remote",
        tls=None,
        started_epoch=_NOW,
        updated_epoch=_NOW,
    )
    assert ready(remote_plain) is False
    not_confirm = Wizard(
        step="tls",
        root="peer",
        tree_id="PeerOne",
        name="Ada",
        door="openrouter",
        credential_id=_CRED,
        cap_usd_micros=DEFAULT_CAP_USD_MICROS,
        bind="remote",
        tls="yes",
        started_epoch=_NOW,
        updated_epoch=_NOW,
    )
    assert ready(not_confirm) is False


def test_negative_epoch_is_bound() -> None:
    with pytest.raises(Refuse) as caught:
        begin(-1)
    assert _code(caught.value) == "BOUND"


def test_module_does_not_touch_disk_or_clock() -> None:
    source = Path(__file__).with_name("wizard.py").read_text(encoding="utf-8")
    for banned in (
        "pathlib",
        "time.time",
        "datetime",
        "subprocess",
        "socket",
        "urllib",
        "os.urandom",
        "eval(",
        "exec(",
        "pickle",
        "open(",
    ):
        assert banned not in source
