"""video_gen plans, duration bounds, price, and the refusal to render."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import NamedTuple, cast

import pytest

import video_gen
from cosmos_hermes import Refuse, secret_shape
from video_gen import (
    ASK_CEILING,
    MAX_CENTS,
    MIN_SECONDS,
    MODELS,
    POLICY_SECONDS,
    PROMPT_CAP,
    SCHEMA,
    VideoPlan,
    VideoRequest,
    apply_duration,
    apply_prompt_cap,
    duration_hi,
    duration_lo,
    plan,
    rebuild,
    request,
    run,
)


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def _table() -> dict[str, int]:
    return {"grok-video": 40, "local-noop": 0}


def _kiln(seconds: object, cap: object = None) -> VideoPlan:
    return plan(
        "grok-video",
        "kiln door opens",
        seconds,
        _table(),
        "cred-video",
        cap=cap,
    )


def _zero_kiln() -> VideoPlan:
    return _kiln(0)


def _run_kiln() -> None:
    run(_kiln(6))


def _first(rows: tuple[VideoPlan, ...]) -> VideoPlan:
    return rows[0]


class _Story(NamedTuple):
    made: VideoPlan
    capped: VideoPlan
    rebuilt: tuple[VideoPlan, ...]
    zero_code: str
    run_code: str


def _story() -> _Story:
    """Ada prices a six-second kiln-door clip on cred-video. Nothing renders."""
    made = _kiln(6, PROMPT_CAP * 3)
    capped = _kiln(POLICY_SECONDS + 4)
    rebuilt = rebuild((made, capped))
    return _Story(
        made=made,
        capped=capped,
        rebuilt=rebuilt,
        zero_code=_code(_zero_kiln),
        run_code=_code(_run_kiln),
    )


def test_example_video_gen() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.made.seconds == 6
    assert first.made.prompt == "kiln door opens"
    assert first.made.credential_id == "cred-video"
    assert first.made.prompt_cap == PROMPT_CAP
    assert first.made.duration_cap == duration_hi()
    assert first.made.duration_cap == POLICY_SECONDS
    assert first.made.capped is False
    assert first.made.renders is False
    assert first.made.spend_required is True
    assert first.made.cents == 40
    assert first.made.schema == SCHEMA
    assert first.capped.seconds == POLICY_SECONDS
    assert first.capped.requested_seconds == POLICY_SECONDS + 4
    assert first.capped.duration_cap == POLICY_SECONDS
    assert first.capped.capped is True
    assert first.capped.cents == first.made.cents
    assert first.capped.renders is False
    assert first.rebuilt == (first.made, first.capped)
    assert _first(first.rebuilt) == first.made
    assert first.zero_code == "OUT_OF_RANGE"
    assert first.run_code == "NOT_RENDER"
    assert "kiln door opens" not in repr(first.made)
    assert "6000" not in repr(first.made)
    assert secret_shape(repr(first.made)) is False
    assert secret_shape(repr(first.capped)) is False


def test_schema_bounds_and_public_names() -> None:
    assert SCHEMA == "cosmos-hermes-video_gen/1"
    assert video_gen.SCHEMA == SCHEMA
    assert MODELS == ("grok-video", "local-noop")
    assert PROMPT_CAP == 2000
    assert MIN_SECONDS == 1
    assert duration_lo() == MIN_SECONDS
    assert duration_hi() == POLICY_SECONDS
    assert apply_duration(duration_lo()) == (MIN_SECONDS, MIN_SECONDS, False)
    assert apply_duration(duration_hi()) == (POLICY_SECONDS, POLICY_SECONDS, False)
    assert apply_duration(duration_hi() + 1) == (POLICY_SECONDS, POLICY_SECONDS + 1, True)
    assert apply_prompt_cap(None) == PROMPT_CAP
    assert apply_prompt_cap(PROMPT_CAP * 3) == PROMPT_CAP
    assert apply_prompt_cap(1) == PROMPT_CAP
    assert video_gen.__all__ == [
        "ASK_CEILING",
        "MAX_CENTS",
        "MIN_SECONDS",
        "MODELS",
        "POLICY_SECONDS",
        "PROMPT_CAP",
        "SCHEMA",
        "VideoPlan",
        "VideoRequest",
        "apply_duration",
        "apply_prompt_cap",
        "duration_hi",
        "duration_lo",
        "plan",
        "rebuild",
        "request",
        "run",
    ]
    plan_names = tuple(inspect.signature(plan).parameters)
    assert plan_names == ("model", "prompt", "seconds", "prices", "credential_id", "cap")
    assert inspect.signature(plan).parameters["cap"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(inspect.signature(run).parameters) == ("plan",)
    assert "lambda" not in Path(video_gen.__file__ or "").read_text(encoding="utf-8")


def test_success_flat_cents_and_noop() -> None:
    prices = _table()
    made = _kiln(6)
    row = request("grok-video", "kiln door opens", 6, prices, cap=PROMPT_CAP * 2)
    assert isinstance(row, VideoRequest)
    assert row.seconds == 6
    assert row.requested_seconds == 6
    assert row.cents == 40
    assert row.prompt_cap == PROMPT_CAP
    assert row.duration_cap == POLICY_SECONDS
    assert row.capped is False
    assert row.spend_required is True
    assert made.seconds == row.seconds
    assert made.cents == row.cents
    full = plan("grok-video", "kiln door opens", POLICY_SECONDS, prices, "cred-video")
    assert full.seconds == POLICY_SECONDS
    assert full.capped is False
    assert full.cents == made.cents
    edge = plan("grok-video", "kiln door opens", duration_lo(), prices, "cred-video")
    assert edge.seconds == MIN_SECONDS
    assert edge.capped is False
    assert edge.cents == made.cents
    free = plan("local-noop", "hold", 4, {"local-noop": 0}, "cred-video")
    assert free.model == "local-noop"
    assert free.cents == 0
    assert free.spend_required is True
    assert free.renders is False
    top = plan("grok-video", "hello", 4, {"grok-video": MAX_CENTS}, "cred-video")
    assert top.cents == MAX_CENTS
    ceiling = plan("grok-video", "hello", ASK_CEILING, {"grok-video": 4}, "cred-video")
    assert ceiling.seconds == POLICY_SECONDS
    assert ceiling.requested_seconds == ASK_CEILING
    assert ceiling.duration_cap == POLICY_SECONDS
    assert ceiling.capped is True
    assert ceiling.cents == 4
    again = _kiln(6)
    assert made == again
    assert made.plan_id == again.plan_id
    assert len(made.plan_id) == 64
    assert hash(made) == hash(again)
    manual = VideoPlan(
        model=made.model,
        prompt=made.prompt,
        seconds=made.seconds,
        requested_seconds=made.requested_seconds,
        duration_cap=made.duration_cap,
        capped=made.capped,
        cents=made.cents,
        prompt_cap=made.prompt_cap,
        credential_id=made.credential_id,
        plan_id="",
    )
    assert manual == made
    body = "b" * PROMPT_CAP
    wide = plan("grok-video", body, 8, {"grok-video": 6}, "cred-video", cap=1)
    assert wide.prompt == body
    assert wide.prompt_cap == PROMPT_CAP
    assert "kiln door opens" not in repr(row)
    assert secret_shape(repr(free)) is False


def _below() -> tuple[int, int, bool]:
    return apply_duration(duration_lo() - 1)


def _negative() -> VideoPlan:
    return _kiln(-4)


def _over_ask() -> VideoPlan:
    return _kiln(ASK_CEILING + 1)


def _bool_seconds() -> VideoPlan:
    return _kiln(True)


def _float_seconds() -> VideoPlan:
    return _kiln(4.0)


def _text_seconds() -> VideoPlan:
    return _kiln("8")


def _secret_seconds() -> VideoPlan:
    return _kiln("sk-abcdefghij")


def _secret_prompt_at_zero() -> VideoPlan:
    return plan("grok-video", "sk-abcdefghij", 0, _table(), "cred-video")


def _secret_cred_at_zero() -> VideoPlan:
    return plan("grok-video", "kiln door opens", 0, _table(), "sk-abcdefghij")


def test_duration_bounds() -> None:
    assert _code(_below) == "OUT_OF_RANGE"
    assert _code(_zero_kiln) == "OUT_OF_RANGE"
    assert _code(_negative) == "OUT_OF_RANGE"
    assert _code(_over_ask) == "OUT_OF_RANGE"
    assert _code(_bool_seconds) == "NOT_INT"
    assert _code(_float_seconds) == "NOT_INT"
    assert _code(_text_seconds) == "NOT_INT"
    assert _code(_secret_seconds) == "SECRET"
    assert _code(_secret_prompt_at_zero) == "SECRET"
    assert _code(_secret_cred_at_zero) == "SECRET"
    for seconds in (duration_lo(), 4, 6, 8, duration_hi()):
        made = _kiln(seconds)
        assert made.seconds == seconds
        assert made.capped is False
        assert made.duration_cap == POLICY_SECONDS


def _unknown_model() -> VideoPlan:
    return plan("fal", "hello", 6, {"fal": 4}, "cred-video")


def _empty_model() -> VideoPlan:
    return plan("", "hello", 6, {"": 4}, "cred-video")


def _imagine() -> VideoPlan:
    return plan("grok-imagine-video", "hello", 6, {"grok-imagine-video": 4}, "cred-video")


def _unpriced_empty() -> VideoPlan:
    return plan("local-noop", "hello", 4, {}, "cred-video")


def _unpriced_other() -> VideoPlan:
    return plan("local-noop", "hello", 4, {"grok-video": 4}, "cred-video")


def _secret_model() -> VideoPlan:
    return plan("sk-abcdefghij", "hello", 6, {"sk-abcdefghij": 4}, "cred-video")


def _secret_prompt() -> VideoPlan:
    return plan("grok-video", "sk-abcdefghij", 6, _table(), "cred-video")


def _bearer_prompt() -> VideoPlan:
    return plan("grok-video", "Bearer abcdefghij", 6, _table(), "cred-video")


def _assigned_prompt() -> VideoPlan:
    return plan("grok-video", "api_key=kiln-raw-secret", 6, _table(), "cred-video")


def _secret_key() -> VideoPlan:
    return plan(
        "grok-video",
        "hello",
        6,
        {"sk-abcdefghij": 1, "grok-video": 4},
        "cred-video",
    )


def _secret_value() -> VideoPlan:
    return plan(
        "grok-video",
        "hello",
        6,
        {"grok-video": "api_key=kiln-raw-secret"},
        "cred-video",
    )


def _secret_cap() -> VideoPlan:
    return _kiln(6, "sk-abcdefghij")


def _secret_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), "sk-abcdefghij")


def _blank_prompt() -> VideoPlan:
    return plan("grok-video", "", 6, _table(), "cred-video")


def _space_prompt() -> VideoPlan:
    return plan("grok-video", "   \n", 6, _table(), "cred-video")


def _list_prices() -> VideoPlan:
    return plan("grok-video", "hello", 6, [], "cred-video")


def _int_key() -> VideoPlan:
    return plan("grok-video", "hello", 6, {1: 2}, "cred-video")


def _blank_key() -> VideoPlan:
    return plan("grok-video", "hello", 6, {"  ": 2}, "cred-video")


def _bool_cents() -> VideoPlan:
    return plan("grok-video", "hello", 6, {"grok-video": True}, "cred-video")


def _low_cents() -> VideoPlan:
    return plan("grok-video", "hello", 6, {"grok-video": -1}, "cred-video")


def _high_cents() -> VideoPlan:
    return plan("grok-video", "hello", 6, {"grok-video": MAX_CENTS + 1}, "cred-video")


def _nul_prompt() -> VideoPlan:
    return plan("grok-video", "a\x00b", 6, _table(), "cred-video")


def _none_model() -> VideoPlan:
    return plan(None, "hello", 6, _table(), "cred-video")


def _none_prompt() -> VideoPlan:
    return plan("grok-video", None, 6, _table(), "cred-video")


def _surrogate() -> VideoPlan:
    return plan("grok-video", "a\ud800", 6, _table(), "cred-video")


def _oversize() -> VideoPlan:
    return plan("grok-video", "d" * (PROMPT_CAP + 1), 6, _table(), "cred-video")


def _oversize_cap() -> VideoPlan:
    return plan(
        "grok-video",
        "e" * (PROMPT_CAP + 1),
        6,
        _table(),
        "cred-video",
        cap=PROMPT_CAP * 9,
    )


def _bool_cap() -> VideoPlan:
    return _kiln(6, True)


def _neg_cap() -> VideoPlan:
    return _kiln(6, -3)


def _missing_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), "")


def _blank_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), "   ")


def _bad_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), "not a token")


def _dot_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), "../keys")


def _none_cred() -> VideoPlan:
    return plan("grok-video", "hello", 6, _table(), None)


def _wide_prices() -> VideoPlan:
    table = {f"extra-{index}": 1 for index in range(32)}
    table["grok-video"] = 4
    return plan("grok-video", "hello", 6, table, "cred-video")


def _price_text() -> VideoPlan:
    return plan("grok-video", "hello", 6, "grok-video", "cred-video")


def _secret_price_text() -> VideoPlan:
    return plan("grok-video", "hello", 6, "api_key=kiln-raw-secret", "cred-video")


def test_refusal_codes() -> None:
    assert _code(_unknown_model) == "UNKNOWN_MODEL"
    assert _code(_empty_model) == "UNKNOWN_MODEL"
    assert _code(_imagine) == "UNKNOWN_MODEL"
    assert _code(_unpriced_empty) == "UNPRICED"
    assert _code(_unpriced_other) == "UNPRICED"
    assert _code(_secret_model) == "SECRET"
    assert _code(_secret_prompt) == "SECRET"
    assert _code(_bearer_prompt) == "SECRET"
    assert _code(_assigned_prompt) == "SECRET"
    assert _code(_secret_key) == "SECRET"
    assert _code(_secret_value) == "SECRET"
    assert _code(_secret_cap) == "SECRET"
    assert _code(_secret_cred) == "SECRET"
    assert _code(_secret_price_text) == "SECRET"
    assert _code(_blank_prompt) == "EMPTY"
    assert _code(_space_prompt) == "EMPTY"
    assert _code(_list_prices) == "BAD_PRICES"
    assert _code(_int_key) == "BAD_PRICES"
    assert _code(_blank_key) == "BAD_PRICES"
    assert _code(_wide_prices) == "BAD_PRICES"
    assert _code(_price_text) == "BAD_PRICES"
    assert _code(_bool_cents) == "NOT_INT"
    assert _code(_low_cents) == "OUT_OF_RANGE"
    assert _code(_high_cents) == "OUT_OF_RANGE"
    assert _code(_nul_prompt) == "NULL_BYTE"
    assert _code(_none_model) == "NOT_TEXT"
    assert _code(_none_prompt) == "NOT_TEXT"
    assert _code(_surrogate) == "NOT_TEXT"
    assert _code(_oversize) == "OVERSIZE"
    assert _code(_oversize_cap) == "OVERSIZE"
    assert _code(_bool_cap) == "NOT_INT"
    assert _code(_neg_cap) == "OUT_OF_RANGE"
    assert _code(_missing_cred) == "MISSING_CREDENTIAL"
    assert _code(_blank_cred) == "MISSING_CREDENTIAL"
    assert _code(_bad_cred) == "BAD_CREDENTIAL"
    assert _code(_dot_cred) == "BAD_CREDENTIAL"
    assert _code(_none_cred) == "NOT_TEXT"


def _base() -> VideoPlan:
    return plan("grok-video", "owl in rain", 8, {"grok-video": 6}, "cred-video")


def _cap_low() -> VideoPlan:
    return replace(_base(), prompt_cap=1)


def _cap_bool() -> VideoPlan:
    return replace(_base(), prompt_cap=cast(int, True))


def _duration_cap() -> VideoPlan:
    return replace(_base(), duration_cap=POLICY_SECONDS + 1)


def _schema() -> VideoPlan:
    return replace(_base(), schema="cosmos-hermes-video_gen/2")


def _seconds_mismatch() -> VideoPlan:
    return replace(_base(), seconds=5)


def _seconds_bool() -> VideoPlan:
    return replace(_base(), seconds=cast(int, True))


def _model_swap() -> VideoPlan:
    return replace(_base(), model="fal")


def _empty_swap() -> VideoPlan:
    return replace(_base(), prompt="")


def _secret_swap() -> VideoPlan:
    return replace(_base(), prompt="sk-abcdefghij")


def _cents_low() -> VideoPlan:
    return replace(_base(), cents=-1)


def _cents_bool() -> VideoPlan:
    return replace(_base(), cents=cast(int, True))


def _nul_swap() -> VideoPlan:
    return replace(_base(), prompt="a\x00b")


def _model_none() -> VideoPlan:
    return replace(_base(), model=cast(str, None))


def _prompt_long() -> VideoPlan:
    return replace(_base(), prompt="x" * (PROMPT_CAP + 1))


def _capped_flag() -> VideoPlan:
    return replace(_base(), capped=cast(bool, 1))


def _renders_flag() -> VideoPlan:
    return replace(_base(), renders=cast(bool, 1))


def _spend_flag() -> VideoPlan:
    return replace(_base(), spend_required=cast(bool, 1))


def _bad_id() -> VideoPlan:
    return replace(_base(), plan_id="ab")


def _id_none() -> VideoPlan:
    return replace(_base(), plan_id=cast(str, None))


def _id_secret() -> VideoPlan:
    return replace(_base(), plan_id="sk-abcdefghij")


def _cred_blank() -> VideoPlan:
    return replace(_base(), credential_id="")


def _zero_requested() -> VideoPlan:
    return replace(_base(), requested_seconds=0)


def test_forged_record_stays_closed() -> None:
    base = _base()
    params = getattr(VideoPlan, "__dataclass_params__")
    assert params.frozen is True
    assert params.slots is True
    request_params = getattr(VideoRequest, "__dataclass_params__")
    assert request_params.frozen is True
    assert request_params.slots is True
    with pytest.raises(FrozenInstanceError):
        setattr(base, "cents", 1)
    with pytest.raises(FrozenInstanceError):
        setattr(base, "spend_required", False)
    with pytest.raises(FrozenInstanceError):
        setattr(base, "renders", True)
    forced = replace(base, spend_required=False)
    assert forced.spend_required is True
    assert forced == base
    opened = replace(base, renders=True)
    assert opened.renders is False
    assert opened == base
    row = request("grok-video", "owl in rain", 8, {"grok-video": 6})
    assert replace(row, spend_required=False).spend_required is True
    assert _code(_cap_low) == "BAD_CAP"
    assert _code(_cap_bool) == "NOT_INT"
    assert _code(_duration_cap) == "BAD_CAP"
    assert _code(_schema) == "BAD_SCHEMA"
    assert _code(_seconds_mismatch) == "BAD_CAP"
    assert _code(_seconds_bool) == "NOT_INT"
    assert _code(_model_swap) == "UNKNOWN_MODEL"
    assert _code(_empty_swap) == "EMPTY"
    assert _code(_secret_swap) == "SECRET"
    assert _code(_cents_low) == "OUT_OF_RANGE"
    assert _code(_cents_bool) == "NOT_INT"
    assert _code(_nul_swap) == "NULL_BYTE"
    assert _code(_model_none) == "NOT_TEXT"
    assert _code(_prompt_long) == "OVERSIZE"
    assert _code(_capped_flag) == "BAD_FLAG"
    assert _code(_renders_flag) == "BAD_FLAG"
    assert _code(_spend_flag) == "BAD_FLAG"
    assert _code(_bad_id) == "BAD_PLAN"
    assert _code(_id_none) == "NOT_TEXT"
    assert _code(_id_secret) == "SECRET"
    assert _code(_cred_blank) == "MISSING_CREDENTIAL"
    assert _code(_zero_requested) == "OUT_OF_RANGE"


def _empty_rebuild() -> tuple[VideoPlan, ...]:
    return rebuild(())


def _text_rebuild() -> tuple[VideoPlan, ...]:
    return rebuild("plan")


def _dict_rebuild() -> tuple[VideoPlan, ...]:
    return rebuild({"plan": 1})


def _mixed_rebuild() -> tuple[VideoPlan, ...]:
    return rebuild((_base(), "nope"))


def _replay() -> tuple[VideoPlan, ...]:
    made = _base()
    return rebuild((made, made))


def _too_many() -> tuple[VideoPlan, ...]:
    return rebuild([None] * 65)


def _not_a_plan() -> None:
    run("nope")


def _run_request() -> None:
    run(request("grok-video", "hello", 6, _table()))


def test_rebuild_and_run() -> None:
    made = _base()
    other = plan("local-noop", "hold", 4, {"local-noop": 0}, "cred-video")
    assert rebuild((made,)) == (made,)
    assert rebuild(rebuild((made, other))) == (made, other)
    assert made.plan_id != other.plan_id
    assert _code(_empty_rebuild) == "EMPTY"
    assert _code(_text_rebuild) == "BAD_PLAN"
    assert _code(_dict_rebuild) == "BAD_PLAN"
    assert _code(_mixed_rebuild) == "BAD_PLAN"
    assert _code(_replay) == "REPLAY"
    assert _code(_too_many) == "BAD_PLAN"
    assert _code(_not_a_plan) == "BAD_PLAN"
    assert _code(_run_request) == "BAD_PLAN"
    assert _code(_run_kiln) == "NOT_RENDER"


def test_no_network_and_no_key_material() -> None:
    file_name = video_gen.__file__
    assert file_name is not None
    source = Path(file_name).read_text(encoding="utf-8")
    for banned in (
        "urllib",
        "requests",
        "subprocess",
        "socket",
        "http.client",
        "pickle",
        "eval(",
        "exec(",
        "lambda",
    ):
        assert banned not in source
