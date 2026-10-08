"""Vision spend-descriptor tests."""

from __future__ import annotations

import hashlib
import shutil
import stat
import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

import vision
from cosmos_hermes import PathJail, Refuse
from cosmos_hermes.bounds import MAX_BYTES, MAX_TEXT
from vision import (
    BYTE_CAP,
    CALL_CAP,
    COUNT_CAP,
    CRED_CAP,
    EMBED_CAP,
    MAX_CENTS,
    PATH_CAP,
    PROMPT_CAP,
    SCHEMA,
    LocalImage,
    VisionBatch,
    VisionRequest,
    assemble,
    choose_route,
    from_bytes,
    from_path,
    from_url,
    rebuild,
    request,
)

_PNG = b"\x89PNG\r\n\x1a\n"
_JPEG = b"\xff\xd8\xff"
_GIF87 = b"GIF87a"
_GIF89 = b"GIF89a"
_WEBP = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP"
_AT = 1_790_812_800
_CRED = "cred.mara.library"
_PROMPT = "Describe the front of Mara's library card."
_KEY = "sk-" + "livekeyvalue"
_BEARER = "Bearer " + "abcdefghij"
_ASSIGN = "api_key=" + "abcdefghij"
_MISSING: object = object()


def _code(call: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value.code


def _err(call: Callable[[], object]) -> Refuse:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value


def _sha(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _table() -> dict[str, int]:
    return {"describe": 12, "native": 40}


def _card() -> LocalImage:
    return from_bytes(_PNG + b"mara-library-card")


def _first(items: tuple[VisionRequest, ...]) -> VisionRequest:
    for item in items:
        return item
    raise AssertionError("expected a request")


def _second(items: tuple[VisionRequest, ...]) -> VisionRequest:
    found = False
    for item in items:
        if found:
            return item
        found = True
    raise AssertionError("expected two requests")


def _inside(call: Callable[[PathJail, Path], None]) -> None:
    root = Path(tempfile.mkdtemp(prefix="vision-"))
    try:
        grant = root / "attempt"
        grant.mkdir()
        call(PathJail([str(grant)]), grant)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _ask(
    image: object = _MISSING,
    *,
    credential_id: object = _CRED,
    prompt: object = _PROMPT,
    prices: object = _MISSING,
    mode: object = "text",
    vision_capable: object = False,
    auxiliary: object = False,
    byte_cap: object = None,
    embed_cap: object = None,
    call_cap: object = None,
    calls: object = None,
    at: object = _AT,
) -> VisionRequest:
    held: object = _card() if image is _MISSING else image
    table: object = _table() if prices is _MISSING else prices
    return request(
        held,
        credential_id,
        prompt,
        table,
        mode=mode,
        vision_capable=vision_capable,
        auxiliary=auxiliary,
        byte_cap=byte_cap,
        embed_cap=embed_cap,
        call_cap=call_cap,
        calls=calls,
        at=at,
    )


def _hand(
    *,
    image_id: str = "a" * 64,
    credential_id: str = _CRED,
    prompt: str = _PROMPT,
    route: str = "describe",
    cents: int = 12,
    priced: bool = True,
    nbytes: int = 8,
    byte_cap: int = BYTE_CAP,
    embed_cap: int = EMBED_CAP,
    call_cap: int = CALL_CAP,
    calls_used: int = 1,
    media_type: str = "image/png",
    source: str = "bytes",
    at: int = _AT,
    prompt_sha256: str = "",
    fits_embed: bool = True,
    spend_required: bool = True,
    schema: str = SCHEMA,
) -> VisionRequest:
    digest = _sha(prompt) if prompt_sha256 == "" else prompt_sha256
    return VisionRequest(
        image_id=image_id,
        credential_id=credential_id,
        prompt=prompt,
        route=route,
        cents=cents,
        priced=priced,
        nbytes=nbytes,
        byte_cap=byte_cap,
        embed_cap=embed_cap,
        call_cap=call_cap,
        calls_used=calls_used,
        media_type=media_type,
        source=source,
        at=at,
        prompt_sha256=digest,
        fits_embed=fits_embed,
        spend_required=spend_required,
        schema=schema,
    )


def test_exports_and_schema() -> None:
    assert SCHEMA == "cosmos-hermes-vision/1"
    assert vision.__all__ == [
        "BYTE_CAP",
        "CALL_CAP",
        "COUNT_CAP",
        "CRED_CAP",
        "EMBED_CAP",
        "LocalImage",
        "MAX_CENTS",
        "PATH_CAP",
        "PROMPT_CAP",
        "SCHEMA",
        "VisionBatch",
        "VisionRequest",
        "assemble",
        "choose_route",
        "from_bytes",
        "from_path",
        "from_url",
        "rebuild",
        "request",
    ]
    assert BYTE_CAP == 2_000_000
    assert EMBED_CAP == 262_144
    assert CALL_CAP == 3
    assert COUNT_CAP == 8


def test_module_imports_no_network() -> None:
    path = vision.__file__
    assert path is not None
    banned = ("socket", "urllib", "requests", "subprocess", "pickle", "http")
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            for name in banned:
                assert name not in stripped


def test_from_bytes_rasters() -> None:
    cases: tuple[tuple[bytes, str], ...] = (
        (_PNG, "image/png"),
        (_JPEG, "image/jpeg"),
        (_GIF87, "image/gif"),
        (_GIF89, "image/gif"),
        (_WEBP, "image/webp"),
    )
    for blob, media in cases:
        image = from_bytes(blob)
        assert image.media_type == media
        assert image.image_id == hashlib.sha256(blob).hexdigest()
        assert image.nbytes == len(blob)
        assert image.byte_cap == BYTE_CAP
        assert image.source == "bytes"
        assert image.schema == SCHEMA
        assert image == from_bytes(blob)
        assert "sk-" not in repr(image)


def test_from_bytes_bytearray_and_refusals() -> None:
    payload = _PNG + b"px"
    image = from_bytes(bytearray(payload))
    assert image.image_id == hashlib.sha256(payload).hexdigest()

    class _Raw(bytes):
        pass

    rejected: tuple[object, ...] = (None, "png", 1, 1.0, memoryview(_PNG), _Raw(_PNG))
    for item in rejected:
        def _bad(value: object = item) -> LocalImage:
            return from_bytes(value)

        assert _code(_bad) == "NOT_BYTES"
    for item in (b"", bytearray()):
        def _empty(value: object = item) -> LocalImage:
            return from_bytes(value)

        assert _code(_empty) == "EMPTY"
    for blob in (b"not-an-image", b"<svg></svg>", b"BM" + (b"\x00" * 16), b"\x00" * 16):
        def _format(value: object = blob) -> LocalImage:
            return from_bytes(value)

        err = _err(_format)
        assert err.code == "UNSUPPORTED_FORMAT"
        assert err.detail == "png-jpeg-gif-webp"


def test_byte_cap_exact_window_and_over() -> None:
    exact = _PNG + (b"\x00" * (BYTE_CAP - len(_PNG)))
    image = from_bytes(exact)
    assert image.nbytes == BYTE_CAP
    assert image.byte_cap == BYTE_CAP
    assert image.image_id == hashlib.sha256(exact).hexdigest()

    def _over() -> LocalImage:
        return from_bytes(exact + b"\x00")

    err = _err(_over)
    assert err.code == "OVERSIZE"
    assert err.detail == str(BYTE_CAP)
    wide = _PNG + (b"\x00" * (MAX_BYTES - len(_PNG) + 10))
    assert MAX_BYTES < len(wide) <= BYTE_CAP
    wide_image = from_bytes(wide)
    assert wide_image.nbytes == len(wide)
    assert wide_image.image_id == hashlib.sha256(wide).hexdigest()


def test_local_image_constructor() -> None:
    raised = _local_image(byte_cap=BYTE_CAP + 5)
    assert raised.byte_cap == BYTE_CAP
    assert _code(lambda: _local_image(byte_cap=3)) == "BAD_CAP"
    assert _code(lambda: _local_image(byte_cap=True)) == "NOT_INT"
    assert _code(lambda: _local_image(nbytes=0)) == "EMPTY"
    assert _code(lambda: _local_image(nbytes=True)) == "NOT_INT"
    assert _code(lambda: _local_image(nbytes=BYTE_CAP + 1)) == "OVERSIZE"
    assert _code(lambda: _local_image(image_id="ab")) == "BAD_DIGEST"
    assert _code(lambda: _local_image(image_id="A" * 64)) == "BAD_DIGEST"
    assert _code(lambda: _local_image(media_type="image/svg+xml")) == "BAD_MEDIA"
    assert _code(lambda: _local_image(source="url")) == "BAD_SOURCE"
    assert _code(lambda: _local_image(schema="other")) == "BAD_SCHEMA"


def _local_image(
    *,
    image_id: str = "b" * 64,
    nbytes: int = 8,
    byte_cap: int = BYTE_CAP,
    media_type: str = "image/png",
    source: str = "bytes",
    schema: str = SCHEMA,
) -> LocalImage:
    return LocalImage(
        image_id=image_id,
        nbytes=nbytes,
        byte_cap=byte_cap,
        media_type=media_type,
        source=source,
        schema=schema,
    )


def test_from_path_matches_bytes_and_hides_the_path() -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        payload = _PNG + b"pixels"
        target = grant / "library-card.png"
        target.write_bytes(payload)
        image = from_path(jail, str(target))
        assert image.source == "path"
        assert image.byte_cap == BYTE_CAP
        assert image.image_id == hashlib.sha256(payload).hexdigest()
        assert image.image_id == from_bytes(payload).image_id
        assert str(target) not in repr(image)
        assert image == from_path(jail, str(target))

    _inside(_run)


def test_from_path_cap_empty_missing_directory_and_format() -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        payload = _JPEG + (b"\x00" * (BYTE_CAP - len(_JPEG)))
        full = grant / "full.jpg"
        full.write_bytes(payload)
        image = from_path(jail, str(full))
        assert image.nbytes == BYTE_CAP
        over = grant / "over.jpg"
        with over.open("wb") as handle:
            handle.seek(BYTE_CAP)
            handle.write(b"\x00")

        def _over() -> LocalImage:
            return from_path(jail, str(over))

        err = _err(_over)
        assert err.code == "OVERSIZE"
        assert err.detail == str(BYTE_CAP)
        empty = grant / "empty.png"
        empty.write_bytes(b"")

        def _empty() -> LocalImage:
            return from_path(jail, str(empty))

        assert _code(_empty) == "EMPTY"

        def _missing() -> LocalImage:
            return from_path(jail, str(grant / "missing.png"))

        assert _code(_missing) == "NOT_FILE"
        folder = grant / "dir.png"
        folder.mkdir()

        def _dir() -> LocalImage:
            return from_path(jail, str(folder))

        assert _code(_dir) == "NOT_FILE"
        note = grant / "note.txt"
        note.write_bytes(b"hello vision")

        def _note() -> LocalImage:
            return from_path(jail, str(note))

        assert _code(_note) == "UNSUPPORTED_FORMAT"

    _inside(_run)


def test_from_path_bad_jail_bad_path_and_secret() -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        target = str(grant / "shot.png")
        for jail_value in (None, object(), "grant"):
            def _jail(value: object = jail_value) -> LocalImage:
                return from_path(value, target)

            assert _code(_jail) == "BAD_JAIL"
        for path_value in (None, 3, b"x"):
            def _path(value: object = path_value) -> LocalImage:
                return from_path(jail, value)

            assert _code(_path) == "BAD_PATH"

        def _long() -> LocalImage:
            return from_path(jail, "a" * (PATH_CAP + 1))

        assert _code(_long) == "BAD_PATH"
        secret = grant / (_KEY + ".png")
        assert secret.exists() is False

        def _secret() -> LocalImage:
            return from_path(jail, str(secret))

        err = _err(_secret)
        assert err.code == "SECRET"
        assert err.detail == ""
        assert _KEY not in str(err)
        assert str(secret) not in str(err)

    _inside(_run)


def test_from_path_jail_codes() -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        escapes = (
            "shot.png",
            str(grant / ".." / "outside.png"),
            str(grant.parent / "other" / "a.png"),
            "file:///etc/passwd",
            str(grant) + "%2e%2e",
            "C:foo",
            "C:\\",
            "\\\\server\\share\\x",
            str(grant / "shot.png:stream"),
            str(grant / "shot.png."),
            "",
            str(grant / "a.png") + "\x00",
        )
        codes: list[str] = []
        for raw in escapes:
            def _one(value: str = raw) -> LocalImage:
                return from_path(jail, value)

            codes.append(_code(_one))
        for expected in (
            "RELATIVE_PATH",
            "DOTDOT",
            "OUTSIDE_GRANT",
            "FILE_URL",
            "ENCODED_DOTDOT",
            "DRIVE_RELATIVE",
            "DRIVE_ROOT",
            "UNC",
            "ALT_STREAM",
            "TRAILING_DOT",
            "BAD_PATH",
            "NULL_BYTE",
        ):
            assert expected in codes

    _inside(_run)


def test_from_path_unreadable_retries_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        target = grant / "shot.png"
        target.write_bytes(_PNG + b"pixels")
        stats = [0]
        real_stat = Path.stat

        def _deny_stat(self: Path, *, follow_symlinks: bool = True) -> object:
            if self != target:
                return real_stat(self, follow_symlinks=follow_symlinks)
            stats[0] += 1
            raise PermissionError(13, "denied")

        monkeypatch.setattr(Path, "stat", _deny_stat)
        try:
            def _stat() -> LocalImage:
                return from_path(jail, str(target))

            assert _code(_stat) == "UNREADABLE"
            assert stats[0] == 1
        finally:
            monkeypatch.undo()
        opens = [0]

        def _deny_open(self: Path, *_args: object, **_kwargs: object) -> object:
            del _args, _kwargs
            if self != target:
                raise OSError(13, "other")
            opens[0] += 1
            raise OSError(13, "denied")

        monkeypatch.setattr(Path, "open", _deny_open)

        def _open() -> LocalImage:
            return from_path(jail, str(target))

        assert _code(_open) == "UNREADABLE"
        assert opens[0] == 2

    _inside(_run)


def test_from_path_rejects_a_short_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    def _run(jail: PathJail, grant: Path) -> None:
        target = grant / "shot.png"
        target.write_bytes(_PNG + b"pixels")

        class _Lie:
            st_mode = stat.S_IFREG
            st_size = 4

        real_stat = Path.stat

        def _lie(self: Path, *, follow_symlinks: bool = True) -> object:
            if self != target:
                return real_stat(self, follow_symlinks=follow_symlinks)
            return _Lie()

        monkeypatch.setattr(Path, "stat", _lie)

        def _short() -> LocalImage:
            return from_path(jail, str(target))

        assert _code(_short) == "UNREADABLE"

    _inside(_run)


def test_from_url_refuses_fetch_and_secrets() -> None:
    err = _err(lambda: from_url("https://cdn.example/card.png"))
    assert err.code == "NO_FETCH"
    assert err.detail == ""
    secret = _err(lambda: from_url("https://cdn.example/" + _KEY + ".png"))
    assert secret.code == "SECRET"
    assert secret.detail == ""
    assert _KEY not in str(secret)
    assert _code(lambda: from_url(None)) == "NOT_TEXT"
    assert _code(lambda: from_url("a\x00b")) == "NULL_BYTE"
    assert _err(lambda: from_url("u" * (MAX_TEXT + 1))).detail == str(MAX_TEXT)
    assert _code(lambda: from_url("u" * (MAX_TEXT + 1))) == "OVERSIZE"


def test_choose_route_matrix() -> None:
    assert choose_route("text", True, False) == "describe"
    assert choose_route("native", False, True) == "native"
    assert choose_route("auto", False, False) == "describe"
    assert choose_route("auto", True, False) == "native"
    assert choose_route("auto", True, True) == "describe"
    assert _code(lambda: choose_route("off", False, False)) == "BAD_MODE"
    assert _code(lambda: choose_route("yolo", False, False)) == "BAD_MODE"
    assert _code(lambda: choose_route("", False, False)) == "BAD_MODE"
    assert _code(lambda: choose_route(None, False, False)) == "BAD_MODE"
    assert _code(lambda: choose_route("text", 1, False)) == "BAD_FLAG"
    assert _code(lambda: choose_route("text", False, "yes")) == "BAD_FLAG"
    assert _code(lambda: choose_route(_KEY, False, False)) == "SECRET"


def test_request_describes_one_image() -> None:
    image = _card()
    made = _ask(image)
    assert made.image_id == image.image_id
    assert made.credential_id == _CRED
    assert made.prompt == _PROMPT
    assert made.route == "describe"
    assert made.cents == 12
    assert made.priced is True
    assert made.spend_required is True
    assert made.byte_cap == BYTE_CAP
    assert made.embed_cap == EMBED_CAP
    assert made.call_cap == CALL_CAP
    assert made.calls_used == 1
    assert made.fits_embed is True
    assert made.schema == SCHEMA
    assert made.at == _AT
    assert made.prompt_sha256 == _sha(_PROMPT)
    assert made == _ask(image)
    assert _KEY not in repr(made)
    assert "Bearer" not in repr(made)
    assert "api_key" not in repr(made)


def test_request_native_and_zero_quote() -> None:
    native = _ask(mode="auto", vision_capable=True, prices={"native": 0})
    assert native.route == "native"
    assert native.cents == 0
    assert native.priced is True
    assert native.spend_required is True
    text = _ask(mode="auto", vision_capable=True, auxiliary=True)
    assert text.route == "describe"
    assert text.cents == 12


def test_oversize_cap_is_recorded_not_raised() -> None:
    image = _card()
    made = _ask(
        image,
        byte_cap=BYTE_CAP + 400_000,
        embed_cap=EMBED_CAP + 9_000_000,
        call_cap=CALL_CAP + 40,
    )
    assert made.byte_cap == BYTE_CAP
    assert made.embed_cap == EMBED_CAP
    assert made.call_cap == CALL_CAP
    assert made == _ask(image)
    tight = _err(lambda: _ask(image, byte_cap=4))
    assert tight.code == "OVERSIZE"
    assert tight.detail == "4"


def test_embed_cap_is_not_raised_to_fit() -> None:
    blob = _PNG + (b"\x00" * (EMBED_CAP + 1 - len(_PNG)))
    image = from_bytes(blob)
    made = _ask(image, embed_cap=EMBED_CAP + 10)
    assert made.nbytes == EMBED_CAP + 1
    assert made.embed_cap == EMBED_CAP
    assert made.fits_embed is False
    assert made.spend_required is True


def test_missing_cred_bad_cred_and_secrets() -> None:
    assert _code(lambda: _ask(credential_id=None)) == "NO_CRED"
    assert _code(lambda: _ask(credential_id="")) == "NO_CRED"
    assert _code(lambda: _ask(credential_id="has space")) == "BAD_CRED"
    assert _code(lambda: _ask(credential_id="a" * (CRED_CAP + 1))) == "BAD_CRED"
    assert _code(lambda: _ask(credential_id=3)) == "BAD_CRED"
    for secret in (_KEY, _BEARER, _ASSIGN):
        def _cred(value: str = secret) -> VisionRequest:
            return _ask(credential_id=value)

        err = _err(_cred)
        assert err.code == "SECRET"
        assert err.detail == ""
        assert secret not in str(err)

        def _prompt(value: str = secret) -> VisionRequest:
            return _ask(prompt=value)

        err = _err(_prompt)
        assert err.code == "SECRET"
        assert secret not in str(err)


def test_prompt_prices_and_clock() -> None:
    assert _code(lambda: _ask(prompt=None)) == "NOT_TEXT"
    assert _code(lambda: _ask(prompt="a\x00b")) == "NULL_BYTE"
    assert _code(lambda: _ask(prompt="   ")) == "EMPTY"
    assert _err(lambda: _ask(prompt="p" * (PROMPT_CAP + 1))).detail == str(PROMPT_CAP)
    assert _code(lambda: _ask(prompt="p" * (PROMPT_CAP + 1))) == "OVERSIZE"
    assert _code(lambda: _ask(prices={})) == "UNPRICED"
    assert _code(lambda: _ask(prices={"native": 4})) == "UNPRICED"
    assert _code(lambda: _ask(prices=[])) == "BAD_PRICES"
    assert _code(lambda: _ask(prices=None)) == "BAD_PRICES"
    assert _code(lambda: _ask(prices={"nope": 1})) == "BAD_PRICES"
    assert _code(lambda: _ask(prices={1: 1})) == "BAD_PRICES"
    assert _code(lambda: _ask(prices={"describe": 1, "native": 2, "upscale": 3})) == "BAD_PRICES"
    assert _code(lambda: _ask(prices={"describe": True})) == "NOT_INT"
    assert _code(lambda: _ask(prices={"describe": -1})) == "OUT_OF_RANGE"
    assert _err(lambda: _ask(prices={_KEY: 1})).code == "SECRET"
    assert _code(lambda: _ask(at=-1)) == "OUT_OF_RANGE"
    assert _code(lambda: _ask(at=True)) == "NOT_INT"
    assert _code(lambda: _ask(at=4_102_444_801)) == "OUT_OF_RANGE"
    assert _code(lambda: _ask(byte_cap=True)) == "NOT_INT"
    assert _code(lambda: _ask(byte_cap=0)) == "OUT_OF_RANGE"
    assert _code(lambda: _ask(embed_cap=False)) == "NOT_INT"
    assert _code(lambda: _ask(call_cap=0)) == "OUT_OF_RANGE"


def test_calls_cap_and_bad_ledger() -> None:
    image = _card()
    made = _ask(image, calls={image.image_id: 2})
    assert made.calls_used == 3
    assert _code(lambda: _ask(image, calls={image.image_id: CALL_CAP})) == "CALLS"
    assert _code(lambda: _ask(calls=[])) == "BAD_CALLS"
    assert _code(lambda: _ask(calls={image.image_id: True})) == "NOT_INT"
    assert _code(lambda: _ask(calls={image.image_id: -1})) == "OUT_OF_RANGE"
    assert _code(lambda: _ask(calls={image.image_id: CALL_CAP + 1})) == "OUT_OF_RANGE"
    assert _code(lambda: _ask(calls={"zz": 1})) == "BAD_DIGEST"
    assert _code(lambda: _ask(calls={1: 1})) == "BAD_CALLS"
    assert _err(lambda: _ask(calls={_KEY: 1})).code == "SECRET"
    huge = {f"{index:064x}": 0 for index in range(COUNT_CAP + 1)}
    err = _err(lambda: _ask(calls=huge))
    assert err.code == "OVERSIZE"
    assert err.detail == str(COUNT_CAP)


def test_malformed_image_and_modes() -> None:
    assert _code(lambda: _ask(object())) == "BAD_IMAGE"
    assert _code(lambda: request("img-1", _CRED, _PROMPT, _table(), at=_AT)) == "BAD_IMAGE"
    assert _code(lambda: assemble("abc", _CRED, _PROMPT, _table(), at=_AT)) == "BAD_IMAGE"
    assert _code(lambda: assemble((), _CRED, _PROMPT, _table(), at=_AT)) == "EMPTY"
    assert _code(lambda: assemble([object()], _CRED, _PROMPT, _table(), at=_AT)) == "BAD_IMAGE"

    def _gen() -> VisionBatch:
        images = (_card() for _ in range(1))
        return assemble(images, _CRED, _PROMPT, _table(), at=_AT)

    assert _code(_gen) == "BAD_IMAGE"


def test_assemble_skips_what_does_not_fit() -> None:
    first = from_bytes(_PNG + (b"a" * 12))
    second = from_bytes(_PNG + (b"b" * 22))
    third = from_bytes(_PNG + (b"c" * 2))
    assert first.nbytes == 20
    assert second.nbytes == 30
    assert third.nbytes == 10
    batch = assemble(
        (first, second, third),
        _CRED,
        _PROMPT,
        _table(),
        byte_cap=30,
        at=_AT,
    )
    assert batch.byte_cap == 30
    assert _first(batch.requests).image_id == first.image_id
    assert _second(batch.requests).image_id == third.image_id
    assert batch.skipped_size == (second.image_id,)
    assert batch.skipped_calls == ()
    assert len(batch.requests) == 2
    calls = assemble(
        (first, second, third),
        _CRED,
        _PROMPT,
        _table(),
        calls={second.image_id: CALL_CAP},
        at=_AT,
    )
    assert _first(calls.requests).image_id == first.image_id
    assert _second(calls.requests).image_id == third.image_id
    assert calls.skipped_calls == (second.image_id,)
    assert _code(
        lambda: assemble((first, second), _CRED, _PROMPT, _table(), byte_cap=5, at=_AT)
    ) == "OVERSIZE"
    assert _err(
        lambda: assemble((first,), _CRED, _PROMPT, _table(), byte_cap=5, at=_AT)
    ).detail == "5"
    both = _err(
        lambda: assemble(
            (first, second),
            _CRED,
            _PROMPT,
            _table(),
            calls={first.image_id: CALL_CAP, second.image_id: CALL_CAP},
            at=_AT,
        )
    )
    assert both.code == "CALLS"
    mixed = _code(
        lambda: assemble(
            (first, second),
            _CRED,
            _PROMPT,
            _table(),
            byte_cap=5,
            calls={second.image_id: CALL_CAP},
            at=_AT,
        )
    )
    assert mixed == "EMPTY"
    assert _code(lambda: assemble((first, first), _CRED, _PROMPT, _table(), at=_AT)) == "DUPLICATE"
    crowd = tuple(from_bytes(_PNG + bytes([index + 1])) for index in range(COUNT_CAP + 1))
    err = _err(lambda: assemble(crowd, _CRED, _PROMPT, _table(), at=_AT))
    assert err.code == "OVERSIZE"
    assert err.detail == str(COUNT_CAP)
    listed = assemble([first], _CRED, _PROMPT, _table(), at=_AT)
    assert _first(listed.requests).image_id == first.image_id


def test_rebuild_replays_public_state() -> None:
    image = _card()
    other = from_bytes(_JPEG + b"back")
    batch = assemble((image, other), _CRED, _PROMPT, _table(), at=_AT)
    assert rebuild(batch) == batch
    assert rebuild(rebuild(batch)) == batch
    assert _code(lambda: rebuild(None)) == "BAD_RECORDS"
    assert _code(lambda: rebuild(batch.requests)) == "BAD_RECORDS"


def test_request_constructor_records_policy_and_refuses() -> None:
    clamped = _hand(byte_cap=BYTE_CAP + 99, embed_cap=EMBED_CAP + 5, call_cap=CALL_CAP + 8)
    assert clamped.byte_cap == BYTE_CAP
    assert clamped.embed_cap == EMBED_CAP
    assert clamped.call_cap == CALL_CAP
    forced = _hand(spend_required=False, fits_embed=False)
    assert forced.spend_required is True
    assert forced.fits_embed is True
    assert _code(lambda: _hand(byte_cap=True)) == "NOT_INT"
    assert _code(lambda: _hand(byte_cap=0)) == "OUT_OF_RANGE"
    assert _code(lambda: _hand(nbytes=True)) == "NOT_INT"
    assert _code(lambda: _hand(nbytes=0)) == "EMPTY"
    assert _code(lambda: _hand(nbytes=BYTE_CAP + 1)) == "OVERSIZE"
    assert _code(lambda: _hand(calls_used=0)) == "CALLS"
    assert _code(lambda: _hand(calls_used=CALL_CAP + 1)) == "CALLS"
    assert _code(lambda: _hand(call_cap=CALL_CAP + 9, calls_used=4)) == "CALLS"
    assert _code(lambda: _hand(cents=-1)) == "OUT_OF_RANGE"
    assert _code(lambda: _hand(cents=MAX_CENTS + 1)) == "OUT_OF_RANGE"
    assert _code(lambda: _hand(cents=True)) == "NOT_INT"
    assert _code(lambda: _hand(at=-1)) == "OUT_OF_RANGE"
    assert _code(lambda: _hand(schema="other")) == "BAD_SCHEMA"
    assert _code(lambda: _hand(route="pixels")) == "BAD_ROUTE"
    assert _code(lambda: _hand(media_type="image/svg+xml")) == "BAD_MEDIA"
    assert _code(lambda: _hand(source="url")) == "BAD_SOURCE"
    assert _code(lambda: _hand(image_id="ab")) == "BAD_DIGEST"
    assert _code(lambda: _hand(image_id="A" * 64)) == "BAD_DIGEST"
    assert _code(lambda: _hand(prompt_sha256="ab")) == "BAD_DIGEST"
    assert _code(lambda: _hand(credential_id="")) == "NO_CRED"
    assert _code(lambda: _hand(credential_id="has space")) == "BAD_CRED"
    assert _code(lambda: _hand(credential_id=_KEY)) == "SECRET"
    assert _code(lambda: _hand(prompt="   ")) == "EMPTY"
    assert _code(lambda: _hand(prompt=_BEARER)) == "SECRET"
    assert _code(lambda: _hand(priced=False)) == "UNPRICED"
    image = _hand()
    with pytest.raises(AttributeError):
        setattr(image, "spend_required", False)


def test_batch_records() -> None:
    made = _ask()
    other = _ask(from_bytes(_JPEG + b"back"))

    def _ok() -> VisionBatch:
        return VisionBatch(
            requests=(made, other),
            skipped_size=(),
            skipped_calls=(),
            byte_cap=made.byte_cap,
            embed_cap=made.embed_cap,
            call_cap=made.call_cap,
            credential_id=made.credential_id,
            route=made.route,
            cents=made.cents,
            priced=True,
            at=made.at,
        )

    assert _first(_ok().requests) == made
    assert _code(lambda: VisionBatch(
        requests=(),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "EMPTY"
    assert _code(lambda: VisionBatch(
        requests=(made, made),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "DUPLICATE"
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=made.byte_cap - 1,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "BAD_CAP"
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=("nope",),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "BAD_RECORDS"
    skip = "c" * 64
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=(skip, skip),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "DUPLICATE"
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=(made.image_id,),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "BAD_RECORDS"
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=False,
        at=made.at,
    )) == "UNPRICED"
    assert _code(lambda: VisionBatch(
        requests=(made,),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=True,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "NOT_INT"
    changed = _hand(prompt="Describe the back of the card.")
    assert _code(lambda: VisionBatch(
        requests=(made, changed),
        skipped_size=(),
        skipped_calls=(),
        byte_cap=made.byte_cap,
        embed_cap=made.embed_cap,
        call_cap=made.call_cap,
        credential_id=made.credential_id,
        route=made.route,
        cents=made.cents,
        priced=True,
        at=made.at,
    )) == "BAD_RECORDS"
    assert "sk-" not in repr(_ok())


def test_example_vision() -> None:
    """Mara describes one local library-card id. An oversize ask keeps the policy cap."""

    def _run(jail: PathJail, grant: Path) -> None:
        photo = grant / "library-card.png"
        photo.write_bytes(_PNG + b"mara-library-card")
        prices = {"describe": 12, "native": 40}

        def once() -> tuple[VisionRequest, VisionRequest]:
            image = from_path(jail, str(photo))
            inside = request(
                image,
                _CRED,
                _PROMPT,
                prices,
                mode="text",
                at=_AT,
            )
            over = request(
                image,
                _CRED,
                _PROMPT,
                prices,
                mode="text",
                byte_cap=BYTE_CAP + 400_000,
                embed_cap=EMBED_CAP + 400_000,
                call_cap=CALL_CAP + 4,
                at=_AT,
            )
            return inside, over

        first = once()
        second = once()
        assert first == second
        inside = first[0]
        over = first[1]
        assert inside == over
        assert inside.route == "describe"
        assert inside.image_id == hashlib.sha256(_PNG + b"mara-library-card").hexdigest()
        assert inside.byte_cap == BYTE_CAP
        assert over.byte_cap == BYTE_CAP
        assert over.embed_cap == EMBED_CAP
        assert over.call_cap == CALL_CAP
        assert inside.fits_embed is True
        assert inside.spend_required is True
        assert inside.priced is True
        assert inside.cents == 12
        assert inside.calls_used == 1
        assert inside.credential_id == _CRED
        assert str(photo) not in repr(inside)
        assert "sk-" not in repr(inside)

    _inside(_run)
