"""Rank order, the policy cap, unknown names, and empty queries."""

from __future__ import annotations

from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from tool_search import (
    MAX_CATALOG,
    POLICY_CAP,
    QUERY_BATCH_CAP,
    QUERY_LIMIT,
    REQUEST_LIMIT,
    SCHEMA,
    SearchResult,
    ToolHit,
    ToolRecord,
    freeze,
    lookup,
    search,
    search_many,
)


def _catalog() -> tuple[ToolRecord, ...]:
    return (
        ToolRecord("alphanum", "mountains"),
        ToolRecord("beta", "an alpha helper"),
        ToolRecord("alpha_extra", "extra work"),
        ToolRecord("alpha", "the alpha tool"),
        ToolRecord("gamma", "unrelated"),
        ToolRecord("alpha_zebra", "zzz"),
        ToolRecord("delta", "alpha zone"),
        ToolRecord("my_issue", "tickets"),
        ToolRecord("create_issue", "open a ticket"),
    )


def _first(hits: tuple[ToolHit, ...]) -> ToolHit:
    for hit in hits:
        return hit
    raise AssertionError("expected a hit")


def _group(rows: tuple[SearchResult, ...], index: int) -> SearchResult:
    seen = 0
    for row in rows:
        if seen == index:
            return row
        seen += 1
    raise AssertionError("missing group")


def test_schema_and_cap_constant() -> None:
    assert SCHEMA == "cosmos-hermes-tool_search/1"
    assert POLICY_CAP == 8
    assert REQUEST_LIMIT == 10_000
    assert QUERY_BATCH_CAP == 16


def test_rank_order() -> None:
    catalog = _catalog()
    result = search(catalog, "alpha")
    assert [hit.name for hit in result.hits] == [
        "alpha",
        "alpha_extra",
        "alpha_zebra",
        "alphanum",
        "beta",
        "delta",
    ]
    assert [hit.band for hit in result.hits] == [
        "exact",
        "prefix",
        "prefix",
        "prefix",
        "description",
        "description",
    ]
    assert result.matched == 6
    assert result.query == "alpha"
    assert search(list(reversed(catalog)), " alpha ") == result
    assert search(catalog, "Alpha").hits == ()
    issue = ToolRecord("create_issue", "open a ticket")
    assert search((issue,), "issue").hits == ()
    assert _first(search((issue,), "create").hits).band == "prefix"
    assert _first(search((issue,), "ticket").hits).band == "description"
    assert _first(search((issue,), "create_issue").hits).band == "exact"
    assert search((), "alpha").hits == ()
    late_exact = (
        ToolRecord("beta", "alpha words here"),
        ToolRecord("alpha", "unrelated"),
    )
    assert [hit.name for hit in search(late_exact, "alpha", limit=1).hits] == ["alpha"]


def test_cap_ignores_higher_request() -> None:
    tools = tuple(ToolRecord(f"tool_{index:02d}", "widget") for index in range(12))
    result = search(tools, "tool_", limit=100)
    assert POLICY_CAP == 8
    assert len(result.hits) == 8
    assert result.matched == 12
    assert result.cap == 8
    assert result.requested == 100
    assert result.applied == 8
    assert [hit.name for hit in result.hits] == [f"tool_{index:02d}" for index in range(8)]
    assert all(hit.band == "prefix" for hit in result.hits)
    short = search(tools, "tool_", limit=3)
    assert [hit.name for hit in short.hits] == ["tool_00", "tool_01", "tool_02"]
    assert short.applied == 3
    assert short.requested == 3
    assert short.cap == POLICY_CAP
    default = search(tools, "tool_")
    assert len(default.hits) == POLICY_CAP
    assert default.requested == POLICY_CAP
    assert default.applied == POLICY_CAP
    none = search(tools, "zzzz", limit=100)
    assert none.hits == ()
    assert none.matched == 0
    assert none.applied == POLICY_CAP
    assert none.requested == 100
    ranked = search(_catalog(), "alpha", limit=2)
    assert [hit.name for hit in ranked.hits] == ["alpha", "alpha_extra"]
    ceiling = search(tools, "tool_", limit=REQUEST_LIMIT)
    assert ceiling.requested == REQUEST_LIMIT
    assert ceiling.applied == POLICY_CAP
    assert len(ceiling.hits) == POLICY_CAP


def test_empty_query() -> None:
    catalog = _catalog()
    for query in ("", "   ", "\t", "\n"):
        with pytest.raises(Refuse) as caught:
            search(catalog, query)
        assert caught.value.code == "EMPTY_QUERY"


def test_oversize_query() -> None:
    with pytest.raises(Refuse) as caught:
        search(_catalog(), "q" * (QUERY_LIMIT + 1))
    assert caught.value.code == "OVERSIZE"


def test_refusal_codes() -> None:
    catalog = _catalog()
    with pytest.raises(Refuse) as caught:
        search(catalog, 3)
    assert caught.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        search(catalog, "a\x00b")
    assert caught.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        search(catalog, "sk-abcdefghij")
    assert caught.value.code == "SECRET_SHAPE"
    assert "sk-" not in str(caught.value)
    with pytest.raises(Refuse) as caught:
        search(catalog, "alpha", limit=True)
    assert caught.value.code == "NOT_INT"
    with pytest.raises(Refuse) as caught:
        search(catalog, "alpha", limit=0)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        search(catalog, "alpha", limit=REQUEST_LIMIT + 1)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        search("alpha", "alpha")
    assert caught.value.code == "BAD_CATALOG"
    with pytest.raises(Refuse) as caught:
        search(("alpha",), "alpha")
    assert caught.value.code == "BAD_CATALOG"
    with pytest.raises(Refuse) as caught:
        search(bytearray(b"alpha"), "alpha")
    assert caught.value.code == "BAD_CATALOG"
    with pytest.raises(Refuse) as caught:
        ToolRecord("bad name", "ok")
    assert caught.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as caught:
        ToolRecord("alpha", "api_key=supersecret")
    assert caught.value.code == "SECRET_SHAPE"
    assert "supersecret" not in str(caught.value)
    duplicate = (ToolRecord("alpha", "one"), ToolRecord("alpha", "two"))
    with pytest.raises(Refuse) as caught:
        search(duplicate, "alpha")
    assert caught.value.code == "DUPLICATE_NAME"
    too_many = tuple(ToolRecord(f"n{index}", "d") for index in range(MAX_CATALOG + 1))
    with pytest.raises(Refuse) as caught:
        search(too_many, "n0")
    assert caught.value.code == "CATALOG_CAP"
    with pytest.raises(Refuse) as caught:
        ToolHit("alpha", "desc", "nope")
    assert caught.value.code == "BAD_BAND"
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", (), 0, 9, 9, 8)
    assert caught.value.code == "BAD_CAP"


def test_unknown_tool() -> None:
    catalog = _catalog()
    assert lookup(catalog, "alpha").description == "the alpha tool"
    assert lookup(freeze(catalog), "gamma").description == "unrelated"
    with pytest.raises(Refuse) as caught:
        lookup(catalog, "spotify_play")
    assert caught.value.code == "UNKNOWN_TOOL"
    with pytest.raises(Refuse) as caught:
        lookup(catalog, "Alpha")
    assert caught.value.code == "UNKNOWN_TOOL"
    with pytest.raises(Refuse) as caught:
        lookup((), "alpha")
    assert caught.value.code == "UNKNOWN_TOOL"
    with pytest.raises(Refuse) as caught:
        lookup(catalog, "bad name")
    assert caught.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as caught:
        lookup(catalog, "sk-abcdefghij")
    assert caught.value.code == "SECRET_SHAPE"
    assert "sk-" not in str(caught.value)
    duplicate = (ToolRecord("alpha", "one"), ToolRecord("alpha", "two"))
    with pytest.raises(Refuse) as caught:
        lookup(duplicate, "alpha")
    assert caught.value.code == "DUPLICATE_NAME"


def test_whitespace_phrase() -> None:
    catalog = (ToolRecord("delta", "alpha   zone"),)
    hit = search(catalog, "alpha   zone")
    assert hit.query == "alpha zone"
    assert _first(hit.hits).name == "delta"
    assert _first(hit.hits).band == "description"
    assert search(catalog, "alpha zone") == hit
    assert search(catalog, "\talpha\tzone\n") == hit


def test_search_many() -> None:
    catalog = _catalog()
    queries = ("alpha", "ticket", "create_issue")
    batch = search_many(catalog, queries, limit=2)
    assert batch == tuple(search(catalog, query, limit=2) for query in queries)
    assert _group(batch, 0).applied == 2
    assert [hit.name for hit in _group(batch, 0).hits] == ["alpha", "alpha_extra"]
    assert _first(_group(batch, 1).hits).band == "description"
    assert _first(_group(batch, 2).hits).band == "exact"
    with pytest.raises(Refuse) as caught:
        search_many(catalog, "alpha")
    assert caught.value.code == "BAD_QUERIES"
    with pytest.raises(Refuse) as caught:
        search_many(catalog, ())
    assert caught.value.code == "EMPTY_QUERY"
    with pytest.raises(Refuse) as caught:
        search_many(catalog, ("alpha", "  "))
    assert caught.value.code == "EMPTY_QUERY"
    with pytest.raises(Refuse) as caught:
        search_many(catalog, ("alpha", "sk-abcdefghij"))
    assert caught.value.code == "SECRET_SHAPE"
    duplicate = (ToolRecord("alpha", "one"), ToolRecord("alpha", "two"))
    with pytest.raises(Refuse) as caught:
        search_many(duplicate, ("alpha", "alpha"))
    assert caught.value.code == "DUPLICATE_NAME"
    with pytest.raises(Refuse) as caught:
        search_many(catalog, tuple("alpha" for _ in range(QUERY_BATCH_CAP + 1)))
    assert caught.value.code == "QUERY_CAP"
    edge = search_many(catalog, tuple("alpha" for _ in range(QUERY_BATCH_CAP)), limit=1)
    assert len(edge) == QUERY_BATCH_CAP
    assert all(_first(row.hits).name == "alpha" for row in edge)


def test_freeze_reproduces() -> None:
    catalog = _catalog()
    frozen = freeze(catalog)
    assert frozen == catalog
    assert freeze(frozen) == frozen
    assert freeze(list(catalog)) == catalog
    assert search(frozen, "alpha") == search(catalog, "alpha")
    assert search_many(frozen, ("alpha", "ticket")) == search_many(catalog, ("alpha", "ticket"))


def test_malformed_result() -> None:
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", (), 0, POLICY_CAP, 100, 3)
    assert caught.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", (), 4, POLICY_CAP, POLICY_CAP, POLICY_CAP)
    assert caught.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", (), -1, POLICY_CAP, POLICY_CAP, POLICY_CAP)
    assert caught.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as caught:
        SearchResult(
            "alpha",
            (),
            0,
            POLICY_CAP,
            cast(int, True),
            POLICY_CAP,
        )
    assert caught.value.code == "BAD_CAP"
    scrambled = (
        ToolHit("beta", "one", "prefix"),
        ToolHit("alpha", "two", "exact"),
    )
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", scrambled, 2, POLICY_CAP, 2, 2)
    assert caught.value.code == "BAD_ORDER"
    dupes = (
        ToolHit("alpha", "one", "exact"),
        ToolHit("alpha", "two", "prefix"),
    )
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", dupes, 2, POLICY_CAP, 2, 2)
    assert caught.value.code == "DUPLICATE_NAME"
    with pytest.raises(Refuse) as caught:
        SearchResult("alpha", cast(tuple[ToolHit, ...], ("nope",)), 1, POLICY_CAP, 1, 1)
    assert caught.value.code == "BAD_HIT"
    with pytest.raises(Refuse) as caught:
        SearchResult(
            "alpha",
            cast(tuple[ToolHit, ...], []),
            0,
            POLICY_CAP,
            POLICY_CAP,
            POLICY_CAP,
        )
    assert caught.value.code == "BAD_CAP"
    ordered = (
        ToolHit("alpha", "the alpha tool", "exact"),
        ToolHit("beta", "an alpha helper", "description"),
    )
    built = SearchResult("alpha", ordered, 2, POLICY_CAP, 2, 2)
    assert built.query == "alpha"
    assert built.applied == 2
    assert _first(built.hits).band == "exact"


def test_repr_has_no_secret() -> None:
    result = search(_catalog(), "alpha", limit=2)
    assert secret_shape(repr(result)) is False
    assert secret_shape(repr(_first(result.hits))) is False
    assert secret_shape(repr(ToolRecord("alpha", "plain"))) is False
    assert secret_shape(repr(lookup(_catalog(), "alpha"))) is False


def _story_catalog() -> tuple[ToolRecord, ...]:
    return (
        ToolRecord("kanban_move_card", "Move the review card across the board"),
        ToolRecord("memory_write_note", "Store a note for the next session"),
        ToolRecord("home_assistant_light", "Turn the porch light on"),
        ToolRecord("session_search", "Recall the session where the light was set"),
    )


def _story(catalog: tuple[ToolRecord, ...], light_query: str) -> tuple[SearchResult, ...]:
    return search_many(catalog, (light_query, "session", "session_search"), limit=100)


def _three(
    rows: tuple[SearchResult, ...],
) -> tuple[SearchResult, SearchResult, SearchResult]:
    if len(rows) != 3:
        raise AssertionError("expected three query groups")
    return (_group(rows, 0), _group(rows, 1), _group(rows, 2))


def test_example_tool_search() -> None:
    catalog = _story_catalog()
    first = _story(catalog, "light")
    second = _story(catalog, "light")
    assert first == second
    assert _story(catalog, " light ") == first
    assert _story(tuple(reversed(catalog)), "light") == first
    light, session, exact = _three(first)
    assert light.query == "light"
    assert light.requested == 100
    assert light.applied == POLICY_CAP
    assert light.cap == POLICY_CAP
    assert [hit.name for hit in light.hits] == ["home_assistant_light", "session_search"]
    assert [hit.band for hit in light.hits] == ["description", "description"]
    assert [hit.name for hit in session.hits] == ["session_search", "memory_write_note"]
    assert [hit.band for hit in session.hits] == ["prefix", "description"]
    assert [hit.name for hit in exact.hits] == ["session_search"]
    assert _first(exact.hits).band == "exact"
    card = lookup(catalog, "kanban_move_card")
    assert card.description == "Move the review card across the board"
    assert search(freeze(catalog), "light") == search(catalog, "light")
    assert lookup(catalog, "kanban_move_card") == lookup(catalog, "kanban_move_card")
