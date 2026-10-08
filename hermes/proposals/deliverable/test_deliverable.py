"""Hash check for one relative deliverable. Upload stays refused."""

from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from deliverable import NAME_CAP, POLICY_CAP, SCHEMA, Deliverable, expect, upload


def _digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _code(func: object) -> str:
    assert callable(func)
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def test_schema() -> None:
    assert SCHEMA == "cosmos-hermes-deliverable/1"
    assert POLICY_CAP == 1_048_576
    assert NAME_CAP == 240


def test_match_returns_frozen_record() -> None:
    payload = b"artifact-bytes"
    digest = _digest(payload)
    samples = (
        ("charts/q3.png", "image", "inline", "png"),
        ("clip.mp4", "video", "inline", "mp4"),
        ("note.wav", "audio", "voice", "wav"),
        ("report.pdf", "document", "file", "pdf"),
        ("sheet.csv", "data", "file", "csv"),
        ("route.gpx", "geospatial", "file", "gpx"),
        ("deck.pptx", "presentation", "file", "pptx"),
        ("pack.zip", "archive", "file", "zip"),
        ("page.html", "web", "file", "html"),
        ("./.hidden.png", "image", "inline", "png"),
    )
    for name, media, disposition, extension in samples:
        got = expect(name, media, digest, {name: payload})
        assert got == Deliverable(
            name=name,
            media=media,
            extension=extension,
            disposition=disposition,
            sha256=digest,
            size=len(payload),
            cap=POLICY_CAP,
            schema=SCHEMA,
        )
        assert got.schema == SCHEMA
        assert not secret_shape(repr(got))
        assert "artifact-bytes" not in repr(got)
    again = expect("charts/q3.png", "image", digest, {"charts/q3.png": payload})
    assert again == expect("charts/q3.png", "image", digest, {"charts/q3.png": payload})
    with pytest.raises(FrozenInstanceError):
        setattr(again, "name", "other.png")


def test_extensions_and_exact_key() -> None:
    blob = b"x"
    digest = _digest(blob)
    pairs = (
        ("photo.jpg", "image", "jpg"),
        ("photo.jpeg", "image", "jpeg"),
        ("anim.gif", "image", "gif"),
        ("pic.webp", "image", "webp"),
        ("pic.bmp", "image", "bmp"),
        ("pic.tiff", "image", "tiff"),
        ("icon.svg", "image", "svg"),
        ("Photo.PNG", "image", "png"),
        ("v.mov", "video", "mov"),
        ("v.avi", "video", "avi"),
        ("v.mkv", "video", "mkv"),
        ("v.webm", "video", "webm"),
        ("v.3gp", "video", "3gp"),
        ("a.mp3", "audio", "mp3"),
        ("a.m2a", "audio", "m2a"),
        ("a.ogg", "audio", "ogg"),
        ("a.opus", "audio", "opus"),
        ("a.m4a", "audio", "m4a"),
        ("a.flac", "audio", "flac"),
        ("d.docx", "document", "docx"),
        ("d.doc", "document", "doc"),
        ("d.odt", "document", "odt"),
        ("d.rtf", "document", "rtf"),
        ("d.txt", "document", "txt"),
        ("d.md", "document", "md"),
        ("d.epub", "document", "epub"),
        ("t.xlsx", "data", "xlsx"),
        ("t.xls", "data", "xls"),
        ("t.ods", "data", "ods"),
        ("t.tsv", "data", "tsv"),
        ("t.json", "data", "json"),
        ("t.xml", "data", "xml"),
        ("t.yaml", "data", "yaml"),
        ("t.yml", "data", "yml"),
        ("g.kmz", "geospatial", "kmz"),
        ("g.kml", "geospatial", "kml"),
        ("g.geojson", "geospatial", "geojson"),
        ("p.ppt", "presentation", "ppt"),
        ("p.odp", "presentation", "odp"),
        ("p.key", "presentation", "key"),
        ("z.tar", "archive", "tar"),
        ("z.tar.gz", "archive", "gz"),
        ("z.tgz", "archive", "tgz"),
        ("z.bz2", "archive", "bz2"),
        ("z.xz", "archive", "xz"),
        ("z.7z", "archive", "7z"),
        ("z.rar", "archive", "rar"),
        ("z.apk", "archive", "apk"),
        ("z.ipa", "archive", "ipa"),
        ("w.htm", "web", "htm"),
    )
    for name, media, extension in pairs:
        got = expect(name, media, digest, {name: blob, "other.png": b"side"})
        assert got.media == media
        assert got.extension == extension
        assert got.name == name
    nested = expect("./charts/q3.png", "image", digest, {"./charts/q3.png": blob})
    assert nested.name == "./charts/q3.png"
    assert _code(lambda: expect("charts/q3.png", "image", digest, {"./charts/q3.png": blob})) == "INCOMPLETE"


def test_bytearray_is_hashed_from_the_original_bytes() -> None:
    buf = bytearray(b"png-bytes")
    snap = cast(dict[str, bytes], {"a.png": buf})
    got = expect("a.png", "image", _digest(b"png-bytes"), snap)
    buf[0] = 0
    assert got.sha256 == _digest(b"png-bytes")
    assert got.size == len(b"png-bytes")


def test_bad_names() -> None:
    blob = b"x"
    digest = _digest(blob)
    samples = (
        "/etc/a.png",
        "//a.png",
        "///",
        "/",
        "//",
        "../a.png",
        "foo/../../a.png",
        "foo/../a.png",
        "foo//a.png",
        "foo/a.png/",
        "foo\\a.png",
        "\\\\server\\a.png",
        "C:/a.png",
        "C:a.png",
        "~/a.png",
        "foo/%2e%2e/a.png",
        "ok/%2fhidden.png",
        "ok/%5Cetc.png",
        "",
        ".",
        "..",
        "./",
        "../",
        "...",
        ".../a.png",
        ".png",
        "dir/.png",
        "..png",
        "a.png ",
        " a.png",
        "foo/./../a.png",
        "a.png/.",
    )
    for name in samples:
        assert _code(lambda name=name: expect(name, "image", digest, {name: blob})) == "BAD_NAME"


def test_missing_name_is_incomplete() -> None:
    blob = b"abc"
    digest = _digest(blob)
    assert _code(lambda: expect("a.png", "image", digest, {})) == "INCOMPLETE"
    assert _code(lambda: expect("a.png", "image", digest, {"b.png": blob})) == "INCOMPLETE"


def test_hash_mismatch() -> None:
    blob = b"abc"
    claimed = "0" * 64
    assert _digest(blob) != claimed
    with pytest.raises(Refuse) as caught:
        expect("a.png", "image", claimed, {"a.png": blob})
    assert caught.value.code == "HASH"
    assert caught.value.detail == ""
    assert _digest(blob) not in str(caught.value)


def test_upload_raises_no_upload() -> None:
    assert _code(lambda: upload()) == "NO_UPLOAD"
    assert _code(lambda: upload("a.png")) == "NO_UPLOAD"
    assert _code(lambda: upload(name="a.png", snapshot={})) == "NO_UPLOAD"


def test_cap_is_policy() -> None:
    blob = b"abc"
    digest = _digest(blob)
    got = expect("a.png", "image", digest, {"a.png": blob}, cap=POLICY_CAP * 10)
    assert got.cap == POLICY_CAP
    huge = b"z" * (POLICY_CAP + 1)
    with pytest.raises(Refuse) as caught:
        expect("a.png", "image", "0" * 64, {"a.png": huge}, cap=POLICY_CAP * 10)
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == str(POLICY_CAP)
    exact = b"q" * POLICY_CAP
    held = expect("blob.png", "image", _digest(exact), {"blob.png": exact})
    assert held.size == POLICY_CAP
    assert held.cap == POLICY_CAP
    tight = expect("a.png", "image", digest, {"a.png": blob}, cap=3)
    assert tight.cap == 3
    assert tight.size == 3
    with pytest.raises(Refuse) as caught:
        expect("a.png", "image", digest, {"a.png": b"abcd"}, cap=3)
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == "3"


def test_bad_cap() -> None:
    blob = b"a"
    digest = _digest(blob)
    assert _code(lambda: expect("a.png", "image", digest, {"a.png": blob}, cap=True)) == "BAD_LIMIT"
    assert (
        _code(lambda: expect("a.png", "image", digest, {"a.png": blob}, cap=cast(int, "256")))
        == "BAD_LIMIT"
    )
    assert _code(lambda: expect("a.png", "image", digest, {"a.png": blob}, cap=0)) == "OUT_OF_RANGE"
    assert _code(lambda: expect("a.png", "image", digest, {"a.png": blob}, cap=-3)) == "OUT_OF_RANGE"


def test_record_schema_and_int() -> None:
    assert (
        _code(
            lambda: Deliverable(
                name="a.png",
                media="image",
                extension="png",
                disposition="inline",
                sha256="ab" * 32,
                size=True,
                cap=4,
            )
        )
        == "NOT_INT"
    )
    assert (
        _code(
            lambda: Deliverable(
                name="a.png",
                media="image",
                extension="png",
                disposition="inline",
                sha256="ab" * 32,
                size=1,
                cap=POLICY_CAP + 1,
            )
        )
        == "BAD_LIMIT"
    )
    assert (
        _code(
            lambda: Deliverable(
                name="a.png",
                media="image",
                extension="png",
                disposition="inline",
                sha256="ab" * 32,
                size=1,
                cap=4,
                schema="cosmos-hermes-deliverable/9",
            )
        )
        == "BAD_SCHEMA"
    )


def test_media_digest_source_and_empty() -> None:
    blob = b"print\n"
    digest = _digest(blob)
    assert _code(lambda: expect("tool.py", "document", digest, {"tool.py": blob})) == "SOURCE"
    assert _code(lambda: expect("run.log", "document", digest, {"run.log": blob})) == "SOURCE"
    assert _code(lambda: expect("tool.PY", "document", digest, {"tool.PY": blob})) == "SOURCE"
    assert _code(lambda: expect("app.js", "document", digest, {"app.js": blob})) == "SOURCE"
    assert _code(lambda: expect("a.exe", "document", digest, {"a.exe": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("a.png", "audio", digest, {"a.png": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("a.png", "image/png", digest, {"a.png": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("a.png", "Image", digest, {"a.png": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("README", "document", digest, {"README": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("a.png", "", digest, {"a.png": blob})) == "BAD_MEDIA"
    assert _code(lambda: expect("a.png", "image", "A" * 64, {"a.png": blob})) == "BAD_DIGEST"
    assert _code(lambda: expect("a.png", "image", "abc", {"a.png": blob})) == "BAD_DIGEST"
    assert _code(lambda: expect("a.png", "image", "g" * 64, {"a.png": blob})) == "BAD_DIGEST"
    assert _code(lambda: expect("a.png", "image", digest, {"a.png": b""})) == "EMPTY"


def test_types_null_oversize_name() -> None:
    blob = b"x"
    digest = _digest(blob)
    assert _code(lambda: expect("a.png", "image", digest, cast(dict[str, bytes], None))) == "NOT_MAP"
    assert _code(lambda: expect("a.png", "image", digest, cast(dict[str, bytes], [("a.png", blob)]))) == "NOT_MAP"
    assert _code(lambda: expect(cast(str, 3), "image", digest, {"a.png": blob})) == "NOT_TEXT"
    assert _code(lambda: expect("a.png", cast(str, 3), digest, {"a.png": blob})) == "NOT_TEXT"
    assert _code(lambda: expect("a.png", "image", cast(str, b"ab"), {"a.png": blob})) == "NOT_TEXT"
    assert _code(lambda: expect("a\x00.png", "image", digest, {"a\x00.png": blob})) == "NULL_BYTE"
    assert _code(lambda: expect("a%00.png", "image", digest, {"a%00.png": blob})) == "NULL_BYTE"
    long_name = "n" * (NAME_CAP + 1)
    assert _code(lambda: expect(long_name, "image", digest, {long_name: blob})) == "OVERSIZE"
    assert (
        _code(lambda: expect("a.png", "image", digest, cast(dict[str, bytes], {"a.png": "x"})))
        == "NOT_BYTES"
    )
    assert (
        _code(lambda: expect("a.png", "image", digest, cast(dict[str, bytes], {"a.png": None})))
        == "NOT_BYTES"
    )


def test_secret_refuses_and_stays_out_of_repr() -> None:
    blob = b"safe-chart"
    digest = _digest(blob)
    assert _code(lambda: expect("sk-livekeyvalue.png", "image", "0" * 64, {"sk-livekeyvalue.png": blob})) == "SECRET"
    assert _code(lambda: expect("a.png", "sk-livekeyvalue", digest, {"a.png": blob})) == "SECRET"
    bodies = (
        b"sk-livekeyvalue",
        b"note Bearer abcdefghijk end",
        b"api_key=supersecret",
    )
    for raw in bodies:
        with pytest.raises(Refuse) as caught:
            expect("note.txt", "document", _digest(raw), {"note.txt": raw})
        assert caught.value.code == "SECRET"
        assert "livekeyvalue" not in str(caught.value)
        assert "abcdefghijk" not in str(caught.value)
        assert "supersecret" not in str(caught.value)
    got = expect("note.txt", "document", digest, {"note.txt": blob})
    shown = repr(got)
    assert "safe-chart" not in shown
    assert not secret_shape(shown)
    wrong = b"api_key=supersecret"
    assert _digest(wrong) != "0" * 64
    assert _code(lambda: expect("note.txt", "document", "0" * 64, {"note.txt": wrong})) == "SECRET"


def test_example_deliverable() -> None:
    assert _example_deliverable() == _example_deliverable()


def _example_deliverable() -> tuple[Deliverable, Deliverable, str]:
    name = "kiln/cone-6-schedule.md"
    note = b"cone 6 schedule\nSaturday kiln card, session glaze-b, light the ramp.\n"
    digest = _digest(note)
    record = expect(name, "document", digest, {name: note})
    flipped = bytearray(note)
    flipped[0] ^= 1
    changed = bytes(flipped)
    changed_digest = _digest(changed)
    assert changed_digest != digest
    with pytest.raises(Refuse) as caught:
        expect(name, "document", digest, {name: changed})
    assert caught.value.code == "HASH"
    assert caught.value.detail == ""
    assert digest not in str(caught.value)
    again = expect(name, "document", changed_digest, {name: changed})
    assert record.media == "document"
    assert record.extension == "md"
    assert record.disposition == "file"
    assert record.sha256 == digest
    assert record.size == len(note)
    assert record.cap == POLICY_CAP
    assert again.sha256 == changed_digest
    assert again != record
    assert not secret_shape(repr(record))
    return record, again, caught.value.code


def test_percent_encoding_and_malformed_types() -> None:
    blob = b"x"
    digest = _digest(blob)
    encoded = (
        "a%ZZ.png",
        "a%.png",
        "a%2.png",
        "a%ff.png",
        "a%c0%ae.png",
        "%2561.png",
        "charts/%2e%2e/q3.png",
    )
    for name in encoded:
        assert _code(lambda name=name: expect(name, "image", digest, {name: blob})) == "BAD_NAME"
    secret_name = "%73k-livekey12.png"
    with pytest.raises(Refuse) as caught:
        expect(secret_name, "image", "0" * 64, {secret_name: blob})
    assert caught.value.code == "SECRET"
    assert "livekey12" not in str(caught.value)

    class _Trap(dict[str, bytes]):
        def __contains__(self, key: object) -> bool:
            raise KeyError(key)

    assert _code(lambda: expect("a.png", "image", digest, cast(dict[str, bytes], _Trap()))) == "NOT_MAP"
    assert (
        _code(
            lambda: Deliverable(
                name="a.png",
                media=cast(str, ["image"]),
                extension="png",
                disposition="inline",
                sha256="ab" * 32,
                size=1,
                cap=4,
            )
        )
        == "NOT_TEXT"
    )
    assert (
        _code(
            lambda: Deliverable(
                name="a.png",
                media="image",
                extension="png",
                disposition="inline",
                sha256=cast(str, 3),
                size=1,
                cap=4,
            )
        )
        == "NOT_TEXT"
    )
    assert (
        _code(
            lambda: Deliverable(
                name="tool.py",
                media="document",
                extension="py",
                disposition="file",
                sha256="ab" * 32,
                size=1,
                cap=4,
            )
        )
        == "SOURCE"
    )


def test_long_extension_and_name_cap() -> None:
    blob = b"x"
    digest = _digest(blob)
    ext = "a" * 210
    name = "chart." + ext
    assert len(name) <= NAME_CAP
    assert _code(lambda: expect(name, "document", digest, {name: blob})) == "BAD_MEDIA"
    exact = ("n" * (NAME_CAP - 4)) + ".png"
    assert len(exact) == NAME_CAP
    held = expect(exact, "image", digest, {exact: blob})
    assert held.name == exact
    assert held.cap == POLICY_CAP
    longer = "n" * (NAME_CAP + 1)
    assert _code(lambda: expect(longer, "image", digest, {longer: blob})) == "OVERSIZE"
