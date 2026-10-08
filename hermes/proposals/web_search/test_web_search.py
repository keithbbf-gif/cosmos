"""Tests for bounded web search plans and capped ingest."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from web_search import (
    CRED_CAP,
    PAYLOAD_CAP,
    QUERY_CAP,
    RAIL,
    RAILS,
    RESULT_CAP,
    RETRY_CLASS,
    ROW_CAP,
    SCHEMA,
    SNIPPET_CAP,
    TERM_CAP,
    TERM_LEN,
    TITLE_CAP,
    URL_CAP,
    IngestResult,
    PlanStep,
    QueryPlan,
    SearchHit,
    Term,
    accept,
    confirm_retry,
    emit,
    ingest,
    query,
    rebuild,
)

_CRED = "cred.studio.kiln"
_QUERY = "kiln schedule cone 6"


def _row(index: int, **override: object) -> dict[str, object]:
    base: dict[str, object] = {
        "url": f"https://example.com/{index}",
        "title": f"title {index}",
        "snippet": f"snippet {index}",
    }
    base.update(override)
    return base


def _first(hits: tuple[SearchHit, ...]) -> SearchHit:
    if len(hits) == 0:
        raise AssertionError("empty hits")
    return hits[0]


def _step(steps: tuple[PlanStep, ...], index: int) -> PlanStep:
    if index < 0 or index >= len(steps):
        raise AssertionError("step")
    return steps[index]


def _texts(plan: QueryPlan) -> tuple[str, ...]:
    return tuple(term.text for term in plan.terms)


def _record_at(record: tuple[object, ...], index: int) -> object:
    if index < 0 or index >= len(record):
        raise AssertionError("record")
    return record[index]


def _with(record: tuple[object, ...], index: int, value: object) -> tuple[object, ...]:
    items = list(record)
    if index < 0 or index >= len(items):
        raise AssertionError("record")
    items[index] = value
    return tuple(items)


def test_example_web_search() -> None:
    """Maya's studio card asks for the cone-6 kiln note. The same plan twice."""

    def once() -> tuple[QueryPlan, IngestResult]:
        plan = query(_QUERY, cred_id=_CRED)
        held = ingest(
            (
                {
                    "url": "https://kiln.example.com/cone-6",
                    "title": "Cone 6 schedule",
                    "snippet": "Maya's card: slow fire to cone 6, then a short hold.",
                },
                {
                    "url": "https://notes.example.com/kiln-session",
                    "title": "Kiln session note",
                    "snippet": "Drop the temperature after the peak.",
                },
            ),
            limit=plan.limit,
        )
        return plan, held

    first = once()
    second = once()
    assert first == second
    plan = first[0]
    held = first[1]
    assert plan.text == _QUERY
    assert plan.cred_id == _CRED
    assert plan.rail == RAIL
    assert plan.schema == SCHEMA
    assert plan.limit <= RESULT_CAP
    assert plan.clamped is False
    assert plan.retry_used == 0
    assert plan.fence == ""
    assert _texts(plan) == ("kiln", "schedule", "cone", "6")
    assert len(plan.terms) <= TERM_CAP
    assert len(plan.digest) == 64
    assert len(plan.cache_key) == 64
    bind = _step(plan.steps, 0)
    search = _step(plan.steps, 1)
    assert isinstance(bind, PlanStep)
    assert bind.op == "bind"
    assert bind.prev_sha == "0" * 64
    assert search.op == "search"
    assert search.prev_sha == bind.sha
    assert isinstance(_step(plan.steps, 0), PlanStep)
    assert isinstance(plan.terms[0], Term)
    assert rebuild(emit(plan)) == plan
    assert emit(plan) == emit(second[0])
    assert held.dropped == 0
    assert len(held.hits) == 2
    assert held.limit == plan.limit
    assert not secret_shape(repr(plan))
    assert not secret_shape(repr(held))
    assert not secret_shape(repr(_first(held.hits)))


def test_empty_query_refuses() -> None:
    for blank in ("", "   ", "\n\t"):
        with pytest.raises(Refuse) as caught:
            query(blank, _CRED)
        assert caught.value.code == "EMPTY_QUERY"


def test_query_plan_normalizes_and_clamps() -> None:
    assert SCHEMA == "cosmos-hermes-web_search/1"
    assert RAILS == ("dom", "firecrawl")
    clamped = query("  KILN   schedule cone 6  ", _CRED, limit=50)
    plain = query(_QUERY, _CRED)
    tight = query(_QUERY, _CRED, limit=2)
    fired = query(_QUERY, _CRED, rail="firecrawl")
    assert clamped.text == "KILN schedule cone 6"
    assert clamped.limit == RESULT_CAP
    assert clamped.clamped is True
    assert plain.limit == RESULT_CAP
    assert plain.clamped is False
    assert plain.cache_key == clamped.cache_key
    assert plain != clamped
    assert tight.limit == 2
    assert tight.clamped is False
    assert tight.cache_key != plain.cache_key
    assert fired.rail == "firecrawl"
    assert fired != plain
    assert rebuild(emit(fired)) == fired
    assert query(_QUERY, _CRED) == plain
    with pytest.raises(FrozenInstanceError):
        QueryPlan.__setattr__(plain, "text", "other")


def test_query_refusals() -> None:
    with pytest.raises(Refuse) as missing:
        query(_QUERY)
    assert missing.value.code == "NO_CRED"
    with pytest.raises(Refuse) as blank_cred:
        query(_QUERY, "   ")
    assert blank_cred.value.code == "NO_CRED"
    with pytest.raises(Refuse) as bad_cred:
        query(_QUERY, "bad cred")
    assert bad_cred.value.code == "BAD_CRED"
    secret = "sk-livekeyvalue"
    with pytest.raises(Refuse) as secret_cred:
        query(_QUERY, secret)
    assert secret_cred.value.code == "SECRET"
    assert secret_cred.value.detail == ""
    assert secret not in str(secret_cred.value)
    with pytest.raises(Refuse) as secret_query:
        query(f"prefix {secret} suffix", _CRED)
    assert secret_query.value.code == "SECRET"
    with pytest.raises(Refuse) as kind:
        query(12, _CRED)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        query("a\x00b", _CRED)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        query("a" * (QUERY_CAP + 1), _CRED)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(QUERY_CAP)
    with pytest.raises(Refuse) as cred_over:
        query(_QUERY, "c" * (CRED_CAP + 1))
    assert cred_over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as rail:
        query(_QUERY, _CRED, rail="keyless")
    assert rail.value.code == "BAD_RAIL"
    with pytest.raises(Refuse) as folded_rail:
        query(_QUERY, _CRED, rail="DOM")
    assert folded_rail.value.code == "BAD_RAIL"
    with pytest.raises(Refuse) as flag:
        query(_QUERY, _CRED, limit=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        query(_QUERY, _CRED, limit=0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as term:
        query("a" * (TERM_LEN + 1), _CRED)
    assert term.value.code == "BAD_TERM"
    with pytest.raises(Refuse) as url_term:
        query("see https://kiln.example/cone", _CRED)
    assert url_term.value.code == "BAD_TERM"
    with pytest.raises(Refuse) as many:
        query(" ".join(["aa"] * (TERM_CAP + 1)), _CRED)
    assert many.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as fence:
        query(_QUERY, _CRED, fence="has space")
    assert fence.value.code == "BAD_FENCE"


def test_plan_integrity_retry_and_fence() -> None:
    plan = query(_QUERY, _CRED, fence="fence.session.kiln")
    assert accept(plan, "fence.session.kiln") == plan
    assert accept(plan, "fence.session.kiln") == accept(plan, "fence.session.kiln")
    bare = query(_QUERY, _CRED)
    with pytest.raises(Refuse) as bare_fence:
        accept(bare, "fence.session.kiln")
    assert bare_fence.value.code == "STALE"
    with pytest.raises(Refuse) as wrong:
        accept(plan, "fence.session.other")
    assert wrong.value.code == "STALE"
    with pytest.raises(Refuse) as empty_fence:
        accept(plan, "")
    assert empty_fence.value.code == "STALE"
    retried = confirm_retry(plan, RETRY_CLASS)
    assert retried.retry_used == 1
    assert retried.text == plan.text
    assert retried.cred_id == plan.cred_id
    assert retried.fence == plan.fence
    assert retried.limit == plan.limit
    assert _step(retried.steps, 2).op == "retry"
    assert confirm_retry(plan, RETRY_CLASS) == retried
    assert rebuild(emit(retried)) == retried
    assert retried != plan
    with pytest.raises(Refuse) as again:
        confirm_retry(retried, RETRY_CLASS)
    assert again.value.code == "RETRY_CAP"
    with pytest.raises(Refuse) as other:
        confirm_retry(plan, "TIMEOUT")
    assert other.value.code == "NO_RETRY"
    with pytest.raises(Refuse) as secret_failure:
        confirm_retry(plan, "Bearer abcdefghijk")
    assert secret_failure.value.code == "SECRET"
    with pytest.raises(Refuse) as not_plan:
        confirm_retry("nope", RETRY_CLASS)
    assert not_plan.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as bad_schema:
        replace(plan, schema="cosmos-hermes-web_search/2")
    assert bad_schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as bad_bool:
        replace(plan, clamped=cast(bool, 0))
    assert bad_bool.value.code == "NOT_BOOL"
    with pytest.raises(Refuse) as bad_limit:
        replace(plan, limit=RESULT_CAP + 1)
    assert bad_limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as bad_key:
        replace(plan, cache_key="ab" * 32)
    assert bad_key.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as bad_digest:
        replace(plan, digest="0" * 64)
    assert bad_digest.value.code == "BAD_DIGEST"
    record = emit(plan)
    assert rebuild(record) == plan
    assert rebuild(record) == rebuild(record)
    with pytest.raises(Refuse) as bad_record:
        rebuild(None)
    assert bad_record.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as short:
        rebuild(("short",))
    assert short.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as schema:
        rebuild(_with(record, 0, "cosmos-hermes-other/1"))
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as digest:
        rebuild(_with(record, 10, "cd" * 32))
    assert digest.value.code == "BAD_DIGEST"
    steps = _record_at(record, 9)
    assert type(steps) is tuple
    step_row = cast(tuple[object, ...], steps)
    first = step_row[0]
    assert type(first) is tuple
    step = cast(tuple[object, ...], first)
    broken = (step[0], step[1], step[2], "ab" * 32)
    with pytest.raises(Refuse) as chain:
        rebuild(_with(record, 9, (broken, step_row[1])))
    assert chain.value.code == "CHAIN"
    with pytest.raises(Refuse) as duplicate:
        rebuild(_with(record, 9, (first, first)))
    assert duplicate.value.code == "DUPLICATE"


def test_ingest_skips_over_budget_and_keeps_later() -> None:
    rows = [
        _row(0, snippet="x" * 100),
        _row(1, snippet="y" * 50),
        _row(2, snippet="z" * 40),
        _row(3, snippet="ok"),
    ]
    result = ingest(rows, budget=80)
    assert result.budget == 80
    assert result.limit == RESULT_CAP
    assert tuple(hit.snippet for hit in result.hits) == ("y" * 50, "ok")
    assert result.dropped == 2
    wide = ingest(tuple(_row(index, snippet="n") for index in range(10)), limit=100, budget=10**9)
    assert wide.limit == RESULT_CAP
    assert wide.budget == PAYLOAD_CAP
    assert len(wide.hits) == RESULT_CAP
    assert wide.dropped == 2
    tight = ingest(tuple(_row(index, snippet="n") for index in range(10)), limit=3)
    assert tight.limit == 3
    assert len(tight.hits) == 3
    assert tight.dropped == 7
    empty = ingest(())
    assert empty.hits == ()
    assert empty.dropped == 0
    assert empty.limit == RESULT_CAP
    assert empty.budget == PAYLOAD_CAP
    assert ingest(rows[:2]) == ingest(rows[:2])


def test_row_shape_and_field_caps() -> None:
    good = ingest(
        [
            {
                "url": "HTTP://Example.com/A",
                "title": "t" * TITLE_CAP,
                "snippet": "s" * SNIPPET_CAP,
            }
        ]
    )
    assert _first(good.hits) == SearchHit("HTTP://Example.com/A", "t" * TITLE_CAP, "s" * SNIPPET_CAP)
    assert not secret_shape(repr(good))
    http = ingest([_row(0, url="http://example.com/x")])
    assert _first(http.hits).url == "http://example.com/x"
    bare = ingest([_row(0, url="https://example.com")])
    assert _first(bare.hits).url == "https://example.com"
    ip = ingest([_row(0, url="https://8.8.8.8/a")])
    assert _first(ip.hits).url == "https://8.8.8.8/a"
    v6 = ingest([_row(0, url="https://[2606:4700:4700::1111]:443/a")])
    assert _first(v6.hits).url == "https://[2606:4700:4700::1111]:443/a"
    with pytest.raises(Refuse) as title:
        ingest([_row(0, title="t" * (TITLE_CAP + 1))])
    assert title.value.code == "OVERSIZE"
    assert title.value.detail == str(TITLE_CAP)
    with pytest.raises(Refuse) as snippet:
        ingest([_row(0, snippet="s" * (SNIPPET_CAP + 1))])
    assert snippet.value.code == "OVERSIZE"
    assert snippet.value.detail == str(SNIPPET_CAP)
    with pytest.raises(Refuse) as url_len:
        ingest([_row(0, url="https://example.com/" + ("a" * URL_CAP))])
    assert url_len.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as missing:
        ingest([{"url": "https://example.com/", "title": "t"}])
    assert missing.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as extra:
        ingest([_row(0, rank=1)])
    assert extra.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as kind:
        ingest([("url", "https://example.com/")])
    assert kind.value.code == "BAD_ROW"
    with pytest.raises(Refuse) as rows_type:
        ingest("https://example.com/")
    assert rows_type.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as mapping:
        ingest({"url": "https://example.com/", "title": "t", "snippet": "s"})
    assert mapping.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as not_text:
        ingest([_row(0, title=7)])
    assert not_text.value.code == "NOT_TEXT"
    hit = _first(ingest([_row(0)]).hits)
    with pytest.raises(Refuse) as count:
        IngestResult(schema=SCHEMA, hits=(hit,), dropped=-1, limit=RESULT_CAP, budget=PAYLOAD_CAP)
    assert count.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as budget:
        IngestResult(schema=SCHEMA, hits=(hit,), dropped=0, limit=RESULT_CAP, budget=0)
    assert budget.value.code == "BAD_BUDGET"
    with pytest.raises(Refuse) as flag:
        IngestResult(
            schema=SCHEMA,
            hits=(),
            dropped=cast(int, True),
            limit=RESULT_CAP,
            budget=PAYLOAD_CAP,
        )
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low_budget:
        ingest([_row(0)], budget=-1)
    assert low_budget.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as many:
        ingest(tuple(_row(index) for index in range(ROW_CAP + 1)))
    assert many.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as hits:
        IngestResult(
            schema=SCHEMA,
            hits=cast(tuple[SearchHit, ...], [hit]),
            dropped=0,
            limit=RESULT_CAP,
            budget=PAYLOAD_CAP,
        )
    assert hits.value.code == "BAD_ROWS"
    with pytest.raises(Refuse) as schema:
        IngestResult(schema="nope", hits=(), dropped=0, limit=RESULT_CAP, budget=PAYLOAD_CAP)
    assert schema.value.code == "BAD_SCHEMA"


def test_bad_url_private_host_and_secret_rows() -> None:
    refused = [
        "ftp://example.com/a",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "ws://example.com/socket",
        "https:///missing-host",
        "http://user:secret@example.com/a",
        "example.com",
        "",
        "https://example.com:0/",
        "https://example.com:65536/",
        "https://example.com/../secret",
        "https://example.com/%00",
    ]
    for url in refused:
        with pytest.raises(Refuse) as caught:
            ingest([_row(0, url=url)])
        assert caught.value.code == "BAD_URL"
    private = [
        "https://127.0.0.1/a",
        "https://10.1.2.3/a",
        "https://192.168.0.5/a",
        "https://172.16.5.5/a",
        "https://169.254.1.1/a",
        "https://localhost/a",
        "https://printer.local/a",
        "https://printer/a",
        "https://[::1]/a",
        "https://224.0.0.1/a",
    ]
    for url in private:
        with pytest.raises(Refuse) as caught:
            ingest([_row(0, url=url)], budget=0)
        assert caught.value.code == "PRIVATE_URL"
    extra_bad = [_row(index) for index in range(RESULT_CAP)]
    extra_bad.append(_row(RESULT_CAP, url="ftp://example.com/dropped"))
    with pytest.raises(Refuse) as past_cap:
        ingest(extra_bad)
    assert past_cap.value.code == "BAD_URL"
    with pytest.raises(Refuse) as secret:
        ingest([_row(0, snippet="Authorization: Bearer abcdefghijk")])
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        ingest([_row(0, url="https://example.com/?api_key=abcdefghij")])
    assert assigned.value.code == "SECRET"
    with pytest.raises(Refuse) as nul:
        ingest([_row(0, snippet="a\x00b")])
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as built:
        SearchHit("ftp://example.com/a", "title", "snippet")
    assert built.value.code == "BAD_URL"


def test_module_does_not_import_network_stacks() -> None:
    source = Path(__file__).with_name("web_search.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    banned_calls = {"exec", "eval", "compile", "open", "__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in banned_calls
    banned = {
        "socket",
        "urllib",
        "requests",
        "http",
        "subprocess",
        "pickle",
        "asyncio",
        "threading",
        "ctypes",
    }
    assert imported.isdisjoint(banned)
