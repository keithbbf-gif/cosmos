"""Spotify descriptors: off until a credential id, no token, no socket."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from spotify import (
    BATCH_CAP,
    CHAR_BUDGET,
    CRED_CAP,
    GENESIS,
    INPUT_CAP,
    PAGE_CAP,
    QUERY_CAP,
    RETRY_CLASS,
    ROW_CAP,
    SCHEMA,
    SEARCH_TYPES,
    TOOLS,
    Note,
    Packed,
    Play,
    Row,
    Snapshot,
    Spotify,
    classify_status,
    rebuild,
    run,
)

_TRACK = "11dFghVXANMlKmJXsNCbNl"
_ALBUM = "4aawyAB9vmqN3uQ7FjRGTy"
_LIST = "3cEYpjA9oz9GiPac4AsH4n"
_URI = "spotify:track:" + _TRACK


def _armed(tier: str = "premium") -> Spotify:
    room = Spotify()
    room.enable("cred-music", tier=tier, now=1)
    return room


def _row(rows: tuple[Row, ...], index: int) -> Row:
    if index < 0 or index >= len(rows):
        raise AssertionError(index)
    return rows[index]


def _ident(index: int) -> str:
    return f"{index:022d}"


def _blocked(room: Spotify) -> str:
    try:
        room.play(_TRACK, now=1_700_000_000)
    except Refuse as refusal:
        return refusal.code
    return ""


def _story() -> tuple[str, Play, str, tuple[str, ...], tuple[str, ...], Snapshot, Snapshot]:
    room = Spotify()
    blocked = _blocked(room)
    room.enable("cred-music", now=1_700_000_000)
    plan = room.play(_TRACK, device_id="kitchen-speaker", now=1_700_000_030)
    found = room.search("miles davis", now=1_700_000_040)
    packed = room.pack(
        ("Kind of Blue", "A Love Supreme (Complete Edition)", "So What"),
        budget=40,
        now=1_700_000_050,
    )
    room.note_failure(RETRY_CLASS, confirm=True, now=1_700_000_060)
    view = room.snapshot()
    again = rebuild(room.records())
    return (blocked, plan, found.subject, packed.kept, packed.skipped, view, again)


def test_schema_starts_disabled() -> None:
    assert SCHEMA == "cosmos-hermes-spotify/1"
    assert QUERY_CAP == 200
    assert PAGE_CAP == 50
    assert BATCH_CAP == 20
    assert "playback" in TOOLS
    assert "track" in SEARCH_TYPES
    room = Spotify()
    assert room.enabled is False
    assert room.credential_id == ""
    assert room.tier == ""
    assert room.snapshot() == rebuild(())
    assert not hasattr(room, "disable")
    assert not hasattr(Spotify, "off")
    assert not hasattr(Spotify, "yolo")
    assert "token" not in Spotify.__slots__
    assert "access_token" not in Spotify.__slots__
    assert "socket" not in Spotify.__slots__


def test_example_spotify() -> None:
    first = _story()
    second = _story()
    assert first == second
    blocked, plan, query, kept, skipped, view, again = first
    assert blocked == "DISABLED"
    assert plan.credential_id == "cred-music"
    assert plan.tier == "unverified"
    assert plan.track_id == _TRACK
    assert plan.uri == _URI
    assert plan.device_id == "kitchen-speaker"
    assert plan.position_ms == 0
    assert plan.cap == QUERY_CAP
    assert plan.premium is True
    assert plan.executes is False
    assert query == "miles davis"
    assert kept == ("Kind of Blue", "So What")
    assert skipped == ("A Love Supreme (Complete Edition)",)
    assert view == again
    assert view.enabled is True
    assert view.credential_id == "cred-music"
    assert not secret_shape(repr(plan))
    assert not secret_shape(repr(view))
    assert "sk-" not in repr(plan)


def test_enable_credential_and_raw_token() -> None:
    fresh = Spotify()
    with pytest.raises(Refuse) as missing:
        fresh.enable("   ", now=1)
    assert missing.value.code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as blank:
        fresh.enable("", now=1)
    assert blank.value.code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as shaped:
        fresh.enable(" has space", now=1)
    assert shaped.value.code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as dotted:
        fresh.enable("..cred", now=1)
    assert dotted.value.code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as kind:
        fresh.enable(None, now=1)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as secret_key:
        fresh.enable("sk-livekeyvalue", now=1)
    assert secret_key.value.code == "SECRET"
    assert "sk-" not in str(secret_key.value)
    with pytest.raises(Refuse) as bearer:
        fresh.enable("Bearer abcdefghijk", now=1)
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        fresh.enable("api_key=supersecret", now=1)
    assert assigned.value.code == "SECRET"
    with pytest.raises(Refuse) as tier:
        fresh.enable("cred-music", tier="yolo", now=1)
    assert tier.value.code == "BAD_TIER"
    with pytest.raises(Refuse) as off_tier:
        fresh.enable("cred-music", tier="off", now=1)
    assert off_tier.value.code == "BAD_TIER"
    with pytest.raises(Refuse) as over:
        fresh.enable("a" * (CRED_CAP + 1), now=1)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(CRED_CAP)
    room = Spotify()
    room.enable("a" * CRED_CAP, now=1)
    room.enable("a" * CRED_CAP, now=1)
    assert len(room.records()) == 1
    with pytest.raises(Refuse) as locked:
        room.enable("cred-other", now=2)
    assert locked.value.code == "CRED_LOCKED"
    assert room.credential_id == "a" * CRED_CAP
    with pytest.raises(Refuse) as stale:
        room.enable("a" * CRED_CAP, now=0)
    assert stale.value.code == "STALE"


def test_play_descriptor_and_cap() -> None:
    room = _armed()
    plan = room.play(_URI, device_id="kitchen-speaker", position_ms=15, cap=10_000, now=2)
    assert plan.track_id == _TRACK
    assert plan.uri == _URI
    assert plan.cap == QUERY_CAP
    assert plan.executes is False
    again = room.play(_TRACK, now=3)
    assert again.track_id == _TRACK
    assert again.device_id == ""
    with pytest.raises(FrozenInstanceError):
        plan.__setattr__("track_id", "other")
    with pytest.raises(Refuse) as tight:
        room.play(_TRACK, cap=10, now=4)
    assert tight.value.code == "OVERSIZE"
    assert tight.value.detail == "10"
    short = room.play(_TRACK, cap=QUERY_CAP, now=5)
    assert short.cap == QUERY_CAP
    with pytest.raises(Refuse) as flag:
        room.play(_TRACK, cap=True, now=6)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text_cap:
        room.play(_TRACK, cap="200", now=6)
    assert text_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        room.play(_TRACK, cap=0, now=6)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        room.play(_TRACK, position_ms=-1, now=6)
    assert negative.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as early:
        room.play(_TRACK, now=5)
    assert early.value.code == "STALE"
    assert len(room.records()) == 4
    for bad in ("nope", "spotify:album:" + _TRACK, "spotify:track:" + _TRACK + ":x", "only:two"):
        with pytest.raises(Refuse) as caught:
            room.play(bad, now=6)
        assert caught.value.code == "BAD_TRACK"
    with pytest.raises(Refuse) as blank:
        room.play("   ", now=6)
    assert blank.value.code == "MISSING_SUBJECT"
    with pytest.raises(Refuse) as device:
        room.play(_TRACK, device_id="../speaker", now=6)
    assert device.value.code == "BAD_DEVICE"
    with pytest.raises(Refuse) as spaced:
        room.play(_TRACK, device_id="kitchen speaker", now=6)
    assert spaced.value.code == "BAD_DEVICE"
    with pytest.raises(Refuse) as secret:
        room.play("sk-livekeyvalue", now=6)
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as number:
        room.play(12, now=6)
    assert number.value.code == "NOT_TEXT"


def test_catalog_actions_and_batch_cap() -> None:
    room = _armed()
    room.act("playback", "get_state", cap=10_000, now=2)
    room.act("playback", "get_currently_playing", now=3)
    paused = room.pause(device_id="kitchen-speaker", now=4)
    assert paused.action == "pause"
    assert paused.premium is True
    assert paused.executes is False
    assert paused.cap == QUERY_CAP
    room.act("playback", "next", now=5)
    room.act("playback", "previous", now=6)
    room.act("playback", "seek", number=1_250, now=7)
    room.act("playback", "set_repeat", flag="off", now=8)
    room.act("playback", "set_shuffle", flag="true", now=9)
    quiet = room.act("playback", "set_volume", number=40, now=10)
    assert quiet.number == 40
    recent = room.act(
        "playback",
        "recently_played",
        limit=10_000,
        flag="after",
        number=1_700_000_000,
        now=11,
    )
    assert recent.limit == PAGE_CAP
    assert recent.cap == PAGE_CAP
    room.act("devices", "list", now=12)
    moved = room.act(
        "devices",
        "transfer",
        device_id="kitchen-speaker",
        flag="true",
        now=13,
    )
    assert moved.device_id == "kitchen-speaker"
    room.act("queue", "get", now=14)
    room.act("queue", "add", subject=_TRACK, now=15)
    found = room.search(
        "  miles davis  ",
        types=("track", "artist"),
        limit=10_000,
        market="US",
        cap=10_000,
        now=16,
    )
    assert found.subject == "miles davis"
    assert found.extra == ("track", "artist")
    assert found.limit == PAGE_CAP
    assert found.cap == QUERY_CAP
    room.act("playlists", "list", limit=10, now=17)
    room.act("playlists", "get", subject=_LIST, now=18)
    created = room.act("playlists", "create", subject="Late Night Jazz", flag="public", now=19)
    assert created.subject == "Late Night Jazz"
    ids = tuple(_ident(index) for index in range(BATCH_CAP + 5))
    added = room.act(
        "playlists",
        "add_items",
        subject=_LIST,
        items=ids,
        limit=10_000,
        now=20,
    )
    assert added.cap == BATCH_CAP
    assert added.limit == BATCH_CAP
    assert len(added.extra) == BATCH_CAP
    assert len(added.skipped) == 5
    assert added.extra[0] == _ident(0)
    room.act("playlists", "remove_items", subject=_LIST, items=(_TRACK,), flag="abc123", now=21)
    room.act("playlists", "update_details", subject=_LIST, flag="private", now=22)
    album = room.act("albums", "get", subject=_ALBUM, now=23)
    assert album.subject == _ALBUM
    room.act("albums", "tracks", subject=_ALBUM, limit=10, offset=5, now=24)
    room.act("library", "list", flag="tracks", now=25)
    room.act("library", "save", flag="albums", items=(_ALBUM,), now=26)
    room.act("library", "remove", flag="tracks", items=(_TRACK,), now=27)
    assert room.snapshot() == rebuild(room.records())
    with pytest.raises(Refuse) as run_plan:
        run(added)
    assert run_plan.value.code == "NOT_RUN"
    with pytest.raises(Refuse) as run_text:
        run("play")
    assert run_text.value.code == "BAD_PLAN"


def test_pack_skips_large_and_keeps_later() -> None:
    room = _armed()
    packed = room.pack(("x" * 80, "Miles & Trane", "So What, Take Two"), budget=10_000, now=2)
    assert packed.cap == CHAR_BUDGET
    assert packed.budget == CHAR_BUDGET
    assert packed.skipped == ("x" * 80,)
    assert packed.kept == ("Miles & Trane", "So What, Take Two")
    assert packed.executes is False
    assert rebuild(room.records()) == room.snapshot()
    tight = room.pack(("Kind of Blue", "A Love Supreme (Complete Edition)", "So What"), budget=40, now=3)
    assert tight.kept == ("Kind of Blue", "So What")
    assert tight.skipped == ("A Love Supreme (Complete Edition)",)
    with pytest.raises(Refuse) as empty:
        room.pack((), now=4)
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as text:
        room.pack("Kind of Blue", now=4)
    assert text.value.code == "BAD_ITEMS"
    with pytest.raises(Refuse) as dup:
        room.pack(("So What", "So What"), now=4)
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as low:
        room.pack(("So What",), budget=0, now=4)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flag:
        room.pack(("So What",), budget=True, now=4)
    assert flag.value.code == "NOT_INT"
    wide = tuple(f"t{index:03d}" for index in range(INPUT_CAP + 1))
    with pytest.raises(Refuse) as over:
        room.pack(wide, now=4)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(INPUT_CAP)


def test_free_tier_blocks_playback() -> None:
    room = _armed("free")
    before = room.records()
    found = room.search("miles davis", now=2)
    assert found.premium is False
    with pytest.raises(Refuse) as played:
        room.play(_TRACK, now=3)
    assert played.value.code == "PREMIUM"
    with pytest.raises(Refuse) as paused:
        room.pause(now=3)
    assert paused.value.code == "PREMIUM"
    with pytest.raises(Refuse) as moved:
        room.act("devices", "transfer", device_id="kitchen-speaker", flag="false", now=3)
    assert moved.value.code == "PREMIUM"
    listed = room.act("devices", "list", now=3)
    assert listed.action == "list"
    assert room.records() != before
    assert _row(room.records(), 0).kind == "enable"


def test_failures_and_one_retry() -> None:
    fresh = Spotify()
    with pytest.raises(Refuse) as early:
        fresh.note_failure(RETRY_CLASS, confirm=True, now=1)
    assert early.value.code == "DISABLED"
    room = _armed()
    with pytest.raises(Refuse) as rate:
        room.note_failure("HTTP_429", confirm=True, now=2)
    assert rate.value.code == "NOT_RETRYABLE"
    with pytest.raises(Refuse) as plain:
        room.note_failure(RETRY_CLASS, confirm=False, now=2)
    assert plain.value.code == "NOT_RETRYABLE"
    with pytest.raises(Refuse) as flag:
        room.note_failure(RETRY_CLASS, confirm="yes", now=2)
    assert flag.value.code == "BAD_FLAG"
    note = room.note_failure("HTTP_401", confirm=True, now=2)
    assert note.code == RETRY_CLASS
    assert note.attempt == 1
    assert note.executes is False
    with pytest.raises(Refuse) as spent:
        room.note_failure(RETRY_CLASS, confirm=True, now=3)
    assert spent.value.code == "RETRY_SPENT"
    assert len(room.snapshot().notes) == 1
    assert classify_status(204) == "empty"
    assert classify_status(401) == "refresh"
    assert classify_status(403) == "forbidden"
    assert classify_status(429) == "rate"
    with pytest.raises(Refuse) as unknown:
        classify_status(200)
    assert unknown.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as boolean:
        classify_status(True)
    assert boolean.value.code == "NOT_INT"


def test_malformed_actions() -> None:
    room = _armed()
    with pytest.raises(Refuse) as tool:
        room.act("radio", "list", now=2)
    assert tool.value.code == "BAD_TOOL"
    for name in ("play", "off", "yolo"):
        with pytest.raises(Refuse) as action:
            room.act("playback", name, now=2)
        assert action.value.code == "BAD_ACTION"
    with pytest.raises(Refuse) as kind:
        room.search("miles", types=("song",), now=2)
    assert kind.value.code == "BAD_TYPE"
    with pytest.raises(Refuse) as dup:
        room.search("miles", types=("track", "track"), now=2)
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as market:
        room.search("miles", market="usa", now=2)
    assert market.value.code == "BAD_MARKET"
    with pytest.raises(Refuse) as empty:
        room.search("   ", now=2)
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as newline:
        room.search("miles\ndavis", now=2)
    assert newline.value.code == "BAD_TEXT"
    with pytest.raises(Refuse) as nul:
        room.search("miles\x00davis", now=2)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as huge:
        room.search("q" * (QUERY_CAP + 1), now=2)
    assert huge.value.code == "OVERSIZE"
    assert huge.value.detail == str(QUERY_CAP)
    with pytest.raises(Refuse) as secret:
        room.search("api_key=supersecret", now=2)
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as text:
        room.search(12, now=2)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as shuffle:
        room.act("playback", "set_shuffle", flag="yes", now=2)
    assert shuffle.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as seek:
        room.act("playback", "seek", now=2)
    assert seek.value.code == "MISSING_SUBJECT"
    with pytest.raises(Refuse) as device:
        room.act("devices", "transfer", flag="true", now=2)
    assert device.value.code == "MISSING_DEVICE"
    with pytest.raises(Refuse) as album:
        room.act("albums", "get", subject="nope", now=2)
    assert album.value.code == "BAD_ID"
    with pytest.raises(Refuse) as extra:
        room.act("search", "search", subject="miles", device_id="kitchen-speaker", now=2)
    assert extra.value.code == "UNEXPECTED"
    with pytest.raises(Refuse) as limited:
        room.act("playback", "pause", limit=1, now=2)
    assert limited.value.code == "UNEXPECTED"
    with pytest.raises(Refuse) as items:
        room.act("playlists", "add_items", subject=_LIST, items=(_TRACK, _TRACK), now=2)
    assert items.value.code == "DUPLICATE"
    assert len(room.records()) == 1


def test_records_rebuild_and_hand_built() -> None:
    room = _armed()
    room.play(_TRACK, now=2)
    rows = room.records()
    assert _row(rows, 0).prev == GENESIS
    assert _row(rows, 1).prev == _row(rows, 0).digest
    assert rebuild(rows) == room.snapshot()
    with pytest.raises(Refuse) as tail:
        rebuild((_row(rows, 1),))
    assert tail.value.code == "CHAIN"
    with pytest.raises(Refuse) as junk:
        rebuild(("nope",))
    assert junk.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as listed:
        rebuild([_row(rows, 0)])
    assert listed.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as digest:
        Row(
            schema=SCHEMA,
            seq=0,
            kind="enable",
            body="cred=cred-music&tier=premium",
            prev=GENESIS,
            digest="1" * 64,
            at=1,
        )
    assert digest.value.code == "CHAIN"
    with pytest.raises(Refuse) as schema:
        Play(
            schema="other",
            credential_id="cred-music",
            tier="premium",
            track_id=_TRACK,
            uri=_URI,
            device_id="",
            position_ms=0,
            cap=QUERY_CAP,
            premium=True,
            executes=False,
            at=2,
        )
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as secret_schema:
        Play(
            schema="sk-livekeyvalue",
            credential_id="cred-music",
            tier="premium",
            track_id=_TRACK,
            uri=_URI,
            device_id="",
            position_ms=0,
            cap=QUERY_CAP,
            premium=True,
            executes=False,
            at=2,
        )
    assert secret_schema.value.code == "SECRET"
    with pytest.raises(Refuse) as cap:
        Play(
            schema=SCHEMA,
            credential_id="cred-music",
            tier="premium",
            track_id=_TRACK,
            uri=_URI,
            device_id="",
            position_ms=0,
            cap=QUERY_CAP + 1,
            premium=True,
            executes=False,
            at=2,
        )
    assert cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as live:
        Play(
            schema=SCHEMA,
            credential_id="cred-music",
            tier="premium",
            track_id=_TRACK,
            uri=_URI,
            device_id="",
            position_ms=0,
            cap=QUERY_CAP,
            premium=True,
            executes=True,
            at=2,
        )
    assert live.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as note:
        Note(
            schema=SCHEMA,
            credential_id="cred-music",
            code="HTTP_429",
            attempt=1,
            executes=False,
            at=2,
        )
    assert note.value.code == "NOT_RETRYABLE"
    with pytest.raises(Refuse) as packed:
        Packed(
            schema=SCHEMA,
            credential_id="cred-music",
            titles=("So What",),
            kept=(),
            skipped=(),
            budget=CHAR_BUDGET,
            cap=CHAR_BUDGET,
            executes=False,
            at=2,
        )
    assert packed.value.code == "BAD_PLAN"


def test_row_cap_and_source_has_no_socket() -> None:
    room = _armed()
    for index in range(ROW_CAP - 1):
        room.play(_TRACK, now=index + 2)
    with pytest.raises(Refuse) as over:
        room.play(_TRACK, now=ROW_CAP + 2)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(ROW_CAP)
    text = Path(__file__).with_name("spotify.py").read_text(encoding="utf-8")
    for banned in (
        "import socket",
        "import urllib",
        "import requests",
        "import subprocess",
        "import pickle",
        "http.server",
    ):
        assert banned not in text
    assert "exec(" not in text
    assert "eval(" not in text


def test_disabled_does_not_inspect_play() -> None:
    room = Spotify()
    with pytest.raises(Refuse) as secret:
        room.play("sk-livekeyvalue", now="soon")
    assert secret.value.code == "DISABLED"
    with pytest.raises(Refuse) as tool:
        room.act("radio", "list", cap=True, now=1)
    assert tool.value.code == "DISABLED"
    with pytest.raises(Refuse) as packed:
        room.pack(("So What",), now=1)
    assert packed.value.code == "DISABLED"
