"""Tests for the disabled-by-default X search plan and capped ingest."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from x_search import (
    BUDGET_CAP,
    CRED_CAP,
    HANDLE_CAP,
    INGEST_CAP,
    KIND,
    KINDS,
    QUERY_CAP,
    RETRY_CLASS,
    ROW_CAP,
    SCHEMA,
    TEXT_CAP,
    URL_CAP,
    Enabled,
    Hit,
    IngestResult,
    PlanStep,
    SearchPlan,
    accept,
    confirm_retry,
    emit,
    enable,
    ingest,
    query,
    rebuild,
)

_CRED = "cred-x"
_QUERY = "cone 6"
_FENCE = "studio-session"
_SECRET = "sk-livekeyvalue"
_BEARER = "Bearer abcdefghijk"


def _row(index: int, **override: object) -> dict[str, object]:
    base: dict[str, object] = {
        "url": f"https://x.com/maya_kiln/status/{index}",
        "handle": "maya_kiln",
        "text": f"note {index}",
    }
    base.update(override)
    return base


def _refuse(text: object = _QUERY, cred_id: object = None, limit: object = None) -> str:
    try:
        query(text, cred_id, limit)
    except Refuse as err:
        return err.code
    raise AssertionError("expected refuse")


def _step(plan: SearchPlan, index: int) -> PlanStep:
    steps = plan.steps
    if index < 0 or index >= len(steps):
        raise AssertionError("step")
    return steps[index]


def _hit_at(result: IngestResult, index: int) -> Hit:
    hits = result.hits
    if index < 0 or index >= len(hits):
        raise AssertionError("hit")
    return hits[index]


def _replace(record: tuple[object, ...], index: int, value: object) -> tuple[object, ...]:
    if index < 0 or index >= len(record):
        raise AssertionError("record")
    items = list(record)
    items[index] = value
    return tuple(items)


def _flip_hex(value: object) -> str:
    if type(value) is not str or len(value) != 64:
        raise AssertionError("hex")
    last = "0" if value[63] != "0" else "1"
    return value[:63] + last


def test_example_x_search() -> None:
    """Maya's card asks X for the cone-6 note. The studio light stays on for the session."""

    def once() -> tuple[object, ...]:
        plan = query(_QUERY, _CRED)
        missing = _refuse(_QUERY)
        bearer = _refuse(_QUERY, _BEARER)
        held = ingest(
            (
                {
                    "url": "https://x.com/maya_kiln/status/6",
                    "handle": "@maya_kiln",
                    "text": "Cone 6 card: slow fire, then a short hold.",
                },
                {
                    "url": "https://x.com/maya_kiln/status/7",
                    "handle": "maya_kiln",
                    "text": "Session note: the kiln holds at the peak.",
                },
                {
                    "url": "https://x.com/studio_light/status/2",
                    "handle": "studio_light",
                    "text": "Leave the studio light on until the cone drops.",
                },
            ),
            limit=plan.limit,
        )
        return (missing, bearer, plan, held, rebuild(emit(plan)))

    first = once()
    second = once()
    assert first == second
    assert first[0] == "DISABLED"
    assert first[1] == "SECRET"
    plan = query(_QUERY, _CRED)
    assert isinstance(plan, SearchPlan)
    assert plan.text == _QUERY
    assert plan.cred_id == _CRED
    assert plan.schema == SCHEMA
    assert plan.kind == KIND
    assert plan.cap == INGEST_CAP
    assert plan.limit == INGEST_CAP
    assert plan.limit <= plan.cap
    assert plan.clamped is False
    assert plan.retry_used == 0
    assert plan.fence == ""
    assert query(_QUERY, enable(_CRED)) == plan
    assert rebuild(emit(plan)) == plan
    assert emit(plan) == emit(query(_QUERY, _CRED))
    held = ingest(
        (
            {
                "url": "https://x.com/maya_kiln/status/6",
                "handle": "@maya_kiln",
                "text": "Cone 6 card: slow fire, then a short hold.",
            },
            {
                "url": "https://x.com/studio_light/status/2",
                "handle": "studio_light",
                "text": "Leave the studio light on until the cone drops.",
            },
        ),
        limit=plan.limit,
    )
    assert held.dropped == 0
    assert len(held.hits) == 2
    assert _hit_at(held, 0).handle == "maya_kiln"
    assert not secret_shape(repr(plan))
    assert not secret_shape(repr(held))
    assert not secret_shape(repr(_hit_at(held, 0)))
    assert not secret_shape(repr(enable(_CRED)))


def test_disabled_does_not_read_the_query() -> None:
    assert _refuse(_SECRET) == "DISABLED"
    assert _refuse(_SECRET, limit=True) == "DISABLED"
    assert _refuse(12) == "DISABLED"
    assert _refuse("", limit=0) == "DISABLED"
    with pytest.raises(Refuse) as off:
        query(_SECRET, "off")
    assert off.value.code == "BAD_CRED"
    assert _SECRET not in str(off.value)


def test_credentials_kinds_and_text_bounds() -> None:
    assert SCHEMA == "cosmos-hermes-x_search/1"
    assert KINDS == ("posts", "profiles", "threads")
    assert KIND == "posts"
    for blank in ("", "   ", "\n\t"):
        with pytest.raises(Refuse) as caught:
            enable(blank)
        assert caught.value.code == "NO_CRED"
        with pytest.raises(Refuse) as queried:
            query(_QUERY, blank)
        assert queried.value.code == "NO_CRED"
    for banned in ("off", "yolo", "OFF", "Yolo"):
        with pytest.raises(Refuse) as caught:
            enable(banned)
        assert caught.value.code == "BAD_CRED"
    with pytest.raises(Refuse) as spaced:
        enable(" has space")
    assert spaced.value.code == "BAD_CRED"
    with pytest.raises(Refuse) as kind:
        enable(None)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as flag:
        enable(True)
    assert flag.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        enable("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        enable("a" * (CRED_CAP + 1))
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(CRED_CAP)
    armed = enable("a" * CRED_CAP)
    assert armed.cred_id == "a" * CRED_CAP
    assert armed.cap == QUERY_CAP
    with pytest.raises(Refuse) as secret_key:
        enable(f"prefix {_SECRET} suffix")
    assert secret_key.value.code == "SECRET"
    assert secret_key.value.detail == ""
    assert _SECRET not in str(secret_key.value)
    with pytest.raises(Refuse) as bearer:
        enable(_BEARER)
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        enable("api_key=abcd")
    assert assigned.value.code == "SECRET"
    with pytest.raises(Refuse) as empty:
        query("   ", _CRED)
    assert empty.value.code == "EMPTY_QUERY"
    with pytest.raises(Refuse) as secret_query:
        query(f"prefix {_SECRET} suffix", _CRED)
    assert secret_query.value.code == "SECRET"
    with pytest.raises(Refuse) as query_kind:
        query(12, _CRED)
    assert query_kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as query_nul:
        query("a\x00b", _CRED)
    assert query_nul.value.code == "NULL_BYTE"
    kept = query("a" * QUERY_CAP, _CRED)
    assert kept.text == "a" * QUERY_CAP
    with pytest.raises(Refuse) as too_long:
        query("a" * (QUERY_CAP + 1), _CRED)
    assert too_long.value.code == "OVERSIZE"
    assert too_long.value.detail == str(QUERY_CAP)
    folded = query("  cone   6\n", _CRED)
    assert folded.text == _QUERY
    assert folded == query(_QUERY, _CRED)
    posts = query(_QUERY, _CRED)
    threads = query(_QUERY, _CRED, kind="threads")
    profiles = query(_QUERY, _CRED, kind="profiles")
    assert posts.kind == "posts"
    assert threads.kind == "threads"
    assert profiles.kind == "profiles"
    assert len({posts.digest, threads.digest, profiles.digest}) == 3
    assert query(_QUERY, _CRED, kind=None) == posts
    with pytest.raises(Refuse) as bad_kind:
        query(_QUERY, _CRED, kind="likes")
    assert bad_kind.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as kind_type:
        query(_QUERY, _CRED, kind=3)
    assert kind_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as kind_secret:
        query(_QUERY, _CRED, kind="sk-abcdefgh")
    assert kind_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as direct_cap:
        Enabled(_CRED, 1)
    assert direct_cap.value.code == "BAD_CAP"
    with pytest.raises(FrozenInstanceError):
        Enabled.__setattr__(armed, "cred_id", "other")


def test_result_cap_is_policy() -> None:
    tight = query(_QUERY, _CRED, limit=1)
    assert tight.text == _QUERY
    assert tight.limit == 1
    assert tight.cap == INGEST_CAP
    assert tight.clamped is False
    raised = query(_QUERY, _CRED, limit=10_000)
    assert raised.limit == INGEST_CAP
    assert raised.cap == INGEST_CAP
    assert raised.clamped is True
    assert raised != query(_QUERY, _CRED)
    long_text = "a" * QUERY_CAP
    still = query(long_text, _CRED, limit=1)
    assert still.text == long_text
    assert still.limit == 1
    with pytest.raises(Refuse) as low:
        query(_QUERY, _CRED, limit=0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flag:
        query(_QUERY, _CRED, limit=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as bad_cap:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 1, INGEST_CAP + 1, False, "", 0)
    assert bad_cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as bad_limit:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 0, INGEST_CAP, False, "", 0)
    assert bad_limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as lied:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 1, INGEST_CAP, True, "", 0)
    assert lied.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as schema:
        SearchPlan("nope", _QUERY, _CRED, KIND, 1, INGEST_CAP, False, "", 0)
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as messy:
        SearchPlan(SCHEMA, " cone 6", _CRED, KIND, 1, INGEST_CAP, False, "", 0)
    assert messy.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as retry:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 1, INGEST_CAP, False, "", 2)
    assert retry.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as flag_clamp:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 1, INGEST_CAP, cast(bool, 1), "", 0)
    assert flag_clamp.value.code == "NOT_BOOL"
    with pytest.raises(Refuse) as fence:
        SearchPlan(SCHEMA, _QUERY, _CRED, KIND, 1, INGEST_CAP, False, "has space", 0)
    assert fence.value.code == "BAD_FENCE"
    with pytest.raises(FrozenInstanceError):
        SearchPlan.__setattr__(tight, "text", "other")


def test_fence_retry_and_rebuild() -> None:
    plan = query(_QUERY, _CRED, fence=_FENCE)
    assert plan.fence == _FENCE
    assert accept(plan, _FENCE) is plan
    assert rebuild(emit(plan)) == plan
    assert emit(rebuild(emit(plan))) == emit(plan)
    arm = _step(plan, 0)
    ask = _step(plan, 1)
    assert arm.op == "arm"
    assert arm.ordinal == 0
    assert arm.prev_sha == "0" * 64
    assert ask.op == "ask"
    assert ask.prev_sha == arm.sha
    assert plan.digest == ask.sha
    assert len(plan.digest) == 64
    bare = query(_QUERY, _CRED)
    with pytest.raises(Refuse) as bare_fence:
        accept(bare, _FENCE)
    assert bare_fence.value.code == "STALE"
    with pytest.raises(Refuse) as wrong:
        accept(plan, "studio-other")
    assert wrong.value.code == "STALE"
    with pytest.raises(Refuse) as empty_fence:
        accept(plan, "")
    assert empty_fence.value.code == "STALE"
    with pytest.raises(Refuse) as bad_fence:
        query(_QUERY, _CRED, fence="has space")
    assert bad_fence.value.code == "BAD_FENCE"
    with pytest.raises(Refuse) as secret_fence:
        query(_QUERY, _CRED, fence=_SECRET)
    assert secret_fence.value.code == "SECRET"
    with pytest.raises(Refuse) as not_plan:
        accept("plan", _FENCE)
    assert not_plan.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as no_retry:
        confirm_retry(plan, "TIMEOUT")
    assert no_retry.value.code == "NO_RETRY"
    with pytest.raises(Refuse) as retry_type:
        confirm_retry(plan, 3)
    assert retry_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as retry_secret:
        confirm_retry(plan, _BEARER)
    assert retry_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as retry_plan:
        confirm_retry("plan", RETRY_CLASS)
    assert retry_plan.value.code == "BAD_PLAN"
    retried = confirm_retry(plan, RETRY_CLASS)
    assert retried.retry_used == 1
    assert retried.text == plan.text
    assert retried.cred_id == plan.cred_id
    assert retried.fence == plan.fence
    assert retried.clamped is plan.clamped
    assert retried.limit == plan.limit
    again = _step(retried, 2)
    assert again.op == "again"
    assert again.prev_sha == _step(retried, 1).sha
    assert retried.digest == again.sha
    assert retried.digest != plan.digest
    assert rebuild(emit(retried)) == retried
    assert accept(retried, _FENCE) is retried
    with pytest.raises(Refuse) as capped:
        confirm_retry(retried, RETRY_CLASS)
    assert capped.value.code == "RETRY_CAP"
    clamped = query(_QUERY, _CRED, limit=50, fence=_FENCE)
    again_clamped = confirm_retry(clamped, RETRY_CLASS)
    assert again_clamped.clamped is True
    assert again_clamped.limit == INGEST_CAP
    record = emit(plan)
    with pytest.raises(Refuse) as bad_record:
        rebuild(record + ("x",))
    assert bad_record.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as not_tuple:
        rebuild("nope")
    assert not_tuple.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as bad_schema:
        rebuild(_replace(record, 0, "nope"))
    assert bad_schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as bad_bool:
        rebuild(_replace(record, 6, 1))
    assert bad_bool.value.code == "NOT_BOOL"
    with pytest.raises(Refuse) as bad_int:
        rebuild(_replace(record, 4, True))
    assert bad_int.value.code == "NOT_INT"
    with pytest.raises(Refuse) as bad_retry:
        rebuild(_replace(record, 8, 2))
    assert bad_retry.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as bad_text:
        rebuild(_replace(record, 1, "  cone 6"))
    assert bad_text.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as empty_text:
        rebuild(_replace(record, 1, "   "))
    assert empty_text.value.code == "EMPTY_QUERY"
    digest = record[10]
    with pytest.raises(Refuse) as bad_digest:
        rebuild(_replace(record, 10, _flip_hex(digest)))
    assert bad_digest.value.code == "BAD_DIGEST"
    with pytest.raises(Refuse) as digest_type:
        rebuild(_replace(record, 10, "zz"))
    assert digest_type.value.code == "BAD_DIGEST"
    steps = record[9]
    assert type(steps) is tuple and len(steps) > 0
    first = steps[0]
    assert type(first) is tuple and len(first) == 4
    flipped = (first[0], first[1], first[2], _flip_hex(first[3]))
    tampered = _replace(record, 9, (flipped,) + steps[1:])
    with pytest.raises(Refuse) as chain:
        rebuild(tampered)
    assert chain.value.code == "CHAIN"
    with pytest.raises(Refuse) as duplicate:
        rebuild(_replace(record, 9, (first, first)))
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as short_step:
        rebuild(_replace(record, 9, ((0, "arm", "0" * 64),)))
    assert short_step.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as bad_step:
        PlanStep(0, "search", "0" * 64, "0" * 64)
    assert bad_step.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as bad_hex:
        PlanStep(0, "arm", "zz", "aa")
    assert bad_hex.value.code == "CHAIN"
    with pytest.raises(Refuse) as bad_ordinal:
        PlanStep(True, "arm", "0" * 64, "0" * 64)
    assert bad_ordinal.value.code == "NOT_INT"
    with pytest.raises(Refuse) as emit_type:
        emit("plan")
    assert emit_type.value.code == "BAD_PLAN"


def test_ingest_count_budget_and_duplicates() -> None:
    rows = [_row(index) for index in range(12)]
    result = ingest(rows)
    assert isinstance(result, IngestResult)
    assert result.cap == INGEST_CAP
    assert result.limit == INGEST_CAP
    assert result.budget == BUDGET_CAP
    assert len(result.hits) == INGEST_CAP
    assert result.dropped == 2
    tighter = ingest(rows, limit=3)
    assert tighter.limit == 3
    assert tighter.cap == INGEST_CAP
    assert len(tighter.hits) == 3
    assert tighter.dropped == 9
    raised = ingest(rows, limit=50)
    assert raised.limit == INGEST_CAP
    assert raised.cap == INGEST_CAP
    assert len(raised.hits) == INGEST_CAP
    assert raised.dropped == 2
    high_budget = ingest(rows, budget=BUDGET_CAP + 50)
    assert high_budget.budget == BUDGET_CAP
    packed = [
        _row(1, text="n" * 40),
        _row(2, text="n" * 40),
        _row(3, text="n" * 10),
    ]
    skipped = ingest(packed, budget=50)
    assert skipped.budget == 50
    assert skipped.dropped == 1
    assert tuple(hit.url for hit in skipped.hits) == (
        "https://x.com/maya_kiln/status/1",
        "https://x.com/maya_kiln/status/3",
    )
    none = ingest(packed, budget=0)
    assert none.hits == ()
    assert none.dropped == 3
    assert none.budget == 0
    with pytest.raises(Refuse) as low:
        ingest(rows, limit=0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative_budget:
        ingest(rows, budget=-1)
    assert negative_budget.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flag:
        ingest(rows, limit=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as budget_flag:
        ingest(rows, budget=True)
    assert budget_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as many:
        ingest([_row(index) for index in range(ROW_CAP + 1)])
    assert many.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as duplicate:
        ingest([_row(1), _row(1, url="HTTPS://X.com/maya_kiln/status/1?s=20#top")])
    assert duplicate.value.code == "DUPLICATE"
    past = [_row(index) for index in range(INGEST_CAP)]
    past.append(_row(0, url="https://x.com/maya_kiln/status/0"))
    with pytest.raises(Refuse) as past_dup:
        ingest(past)
    assert past_dup.value.code == "DUPLICATE"
    same = ingest(rows[:4])
    assert same == ingest(tuple(rows[:4]))
    assert not secret_shape(repr(result))
    with pytest.raises(FrozenInstanceError):
        IngestResult.__setattr__(result, "dropped", 0)


def test_row_shape_handles_and_direct_results() -> None:
    good = ingest(
        [
            {
                "url": "HTTPS://X.com/A/status/1",
                "handle": "@Ab_12",
                "text": "t" * TEXT_CAP,
            }
        ]
    )
    assert _hit_at(good, 0) == Hit("HTTPS://X.com/A/status/1", "Ab_12", "t" * TEXT_CAP)
    assert len(_hit_at(good, 0).handle) <= HANDLE_CAP
    twitter = ingest([_row(1, url="https://twitter.com/xai/status/2", handle="xai")])
    assert _hit_at(twitter, 0).url == "https://twitter.com/xai/status/2"
    mobile = ingest([_row(1, url="https://mobile.twitter.com/xai")])
    assert _hit_at(mobile, 0).url == "https://mobile.twitter.com/xai"
    www = ingest([_row(1, url="https://www.x.com/xai/status/3?s=1#top")])
    assert _hit_at(www, 0).url == "https://www.x.com/xai/status/3?s=1#top"
    bare = ingest([_row(1, handle="a" * HANDLE_CAP)])
    assert _hit_at(bare, 0).handle == "a" * HANDLE_CAP
    with pytest.raises(Refuse) as handle:
        ingest([_row(1, handle="a" * (HANDLE_CAP + 1))])
    assert handle.value.code == "BAD_HANDLE"
    with pytest.raises(Refuse) as handle_over:
        ingest([_row(1, handle="a" * (_HANDLE_INPUT := HANDLE_CAP + 2))])
    assert handle_over.value.code == "OVERSIZE"
    assert handle_over.value.detail == str(HANDLE_CAP + 1)
    with pytest.raises(Refuse) as at:
        ingest([_row(1, handle="@")])
    assert at.value.code == "BAD_HANDLE"
    with pytest.raises(Refuse) as dashed:
        ingest([_row(1, handle="has-dash")])
    assert dashed.value.code == "BAD_HANDLE"
    with pytest.raises(Refuse) as handle_secret:
        ingest([_row(1, handle="sk-abcdefgh")])
    assert handle_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as text:
        ingest([_row(1, text="t" * (TEXT_CAP + 1))])
    assert text.value.code == "OVERSIZE"
    assert text.value.detail == str(TEXT_CAP)
    with pytest.raises(Refuse) as url_len:
        ingest([_row(1, url="https://x.com/" + ("a" * URL_CAP))])
    assert url_len.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as missing:
        ingest([{"url": "https://x.com/xai", "handle": "xai"}])
    assert missing.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as extra:
        ingest([_row(1, rank=1)])
    assert extra.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as key:
        ingest([{1: "https://x.com/xai", "handle": "xai", "text": "note"}])
    assert key.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as kind:
        ingest([("url", "https://x.com/xai")])
    assert kind.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as rows_type:
        ingest("https://x.com/xai")
    assert rows_type.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as raw:
        ingest(b"https://x.com/xai")
    assert raw.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as raw_array:
        ingest(bytearray(b"https://x.com/xai"))
    assert raw_array.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as mapping:
        ingest({"url": "https://x.com/xai", "handle": "xai", "text": "note"})
    assert mapping.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as not_text:
        ingest([_row(1, text=7)])
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as blank_text:
        ingest([_row(1, text="   ")])
    assert blank_text.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as marked:
        Hit("https://x.com/xai", "@xai", "hello")
    assert marked.value.code == "BAD_ROW"
    sample = Hit("https://x.com/maya_kiln/status/1", "maya_kiln", "hello")
    other = Hit("https://x.com/studio_light/status/2", "studio_light", "n" * 30)
    wide = Hit("https://x.com/maya_kiln/status/3", "maya_kiln", "n" * 30)
    with pytest.raises(Refuse) as count:
        IngestResult(SCHEMA, (sample,), -1, 1, INGEST_CAP, BUDGET_CAP)
    assert count.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as count_flag:
        IngestResult(SCHEMA, (), cast(int, True), 1, INGEST_CAP, BUDGET_CAP)
    assert count_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as limit:
        IngestResult(SCHEMA, (), 0, 0, INGEST_CAP, BUDGET_CAP)
    assert limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as high_limit:
        IngestResult(SCHEMA, (), 0, INGEST_CAP + 1, INGEST_CAP, BUDGET_CAP)
    assert high_limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as cap:
        IngestResult(SCHEMA, (), 0, 1, INGEST_CAP + 1, BUDGET_CAP)
    assert cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as schema:
        IngestResult("nope", (), 0, 1, INGEST_CAP, BUDGET_CAP)
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as budget:
        IngestResult(SCHEMA, (sample,), 0, 1, INGEST_CAP, 0)
    assert budget.value.code == "BAD_BUDGET"
    with pytest.raises(Refuse) as high_budget:
        IngestResult(SCHEMA, (), 0, 1, INGEST_CAP, BUDGET_CAP + 1)
    assert high_budget.value.code == "BAD_BUDGET"
    with pytest.raises(Refuse) as over_budget:
        IngestResult(SCHEMA, (other, wide), 0, 2, INGEST_CAP, 40)
    assert over_budget.value.code == "BAD_BUDGET"
    with pytest.raises(Refuse) as dup_hits:
        IngestResult(SCHEMA, (sample, sample), 0, 2, INGEST_CAP, BUDGET_CAP)
    assert dup_hits.value.code == "DUPLICATE"
    many_hits = tuple(
        Hit(f"https://x.com/maya_kiln/status/{index}", "maya_kiln", f"post {index}")
        for index in range(INGEST_CAP + 1)
    )
    with pytest.raises(Refuse) as too_many:
        IngestResult(SCHEMA, many_hits, 0, INGEST_CAP, INGEST_CAP, BUDGET_CAP)
    assert too_many.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as not_hit:
        IngestResult(SCHEMA, cast(tuple[Hit, ...], (sample, "x")), 0, 2, INGEST_CAP, BUDGET_CAP)
    assert not_hit.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as hits_type:
        IngestResult(SCHEMA, cast(tuple[Hit, ...], [sample]), 0, 1, INGEST_CAP, BUDGET_CAP)
    assert hits_type.value.code == "BAD_ROWS"
    with pytest.raises(FrozenInstanceError):
        Hit.__setattr__(sample, "text", "other")


def test_bad_url_and_secret_rows() -> None:
    refused = [
        "http://x.com/xai",
        "ftp://x.com/a",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "https://example.com/a",
        "https://x.com.evil.com/a",
        "https:///x.com",
        "https://user@x.com/a",
        "https://x.com:443/a",
        "x.com/xai",
        "https://x.com/a\\b",
        "https://x.com/%00",
        "",
    ]
    for url in refused:
        with pytest.raises(Refuse) as caught:
            ingest([_row(1, url=url)])
        assert caught.value.code == "BAD_URL"
    extra_bad = [_row(index) for index in range(INGEST_CAP)]
    extra_bad.append(_row(INGEST_CAP, url="https://example.com/dropped"))
    with pytest.raises(Refuse) as past_cap:
        ingest(extra_bad)
    assert past_cap.value.code == "BAD_URL"
    with pytest.raises(Refuse) as secret:
        ingest([_row(1, text=f"Authorization: {_BEARER}")])
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as secret_url:
        ingest([_row(1, url="https://x.com/a?token=abcdefghijkl")])
    assert secret_url.value.code == "SECRET"
    with pytest.raises(Refuse) as nul:
        ingest([_row(1, text="a\x00b")])
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as built:
        Hit("ftp://x.com/a", "xai", "hello")
    assert built.value.code == "BAD_URL"


def test_module_does_not_import_network_stacks() -> None:
    source = Path(__file__).with_name("x_search.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module.split(".", 1)[0])
    banned = {"socket", "urllib", "requests", "http", "subprocess", "pickle", "asyncio"}
    assert imported.isdisjoint(banned)
