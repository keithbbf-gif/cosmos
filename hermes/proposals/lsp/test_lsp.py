"""Refusal and success coverage for LSP JSON-RPC descriptors."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest

from cosmos_hermes import PathJail, Refuse, secret_shape
from lsp import (
    CLIENT_NAME,
    CLIENT_VERSION,
    ID_MAX,
    LANGUAGES,
    METHOD_CAP,
    METHODS,
    POSITION_CAP,
    SCHEMA,
    TEXT_CAP,
    URI_CAP,
    VERSION_MAX,
    RpcRequest,
    definition,
    diagnostic,
    did_open,
    hover,
    initialize,
    parse,
    rebuild,
)
from lsp import __all__ as PUBLIC


@pytest.fixture
def workspace() -> Iterator[Path]:
    """System temp directory. pytest basetemp is not used."""
    root = Path(tempfile.mkdtemp(prefix="lsp_"))
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def refused(exc: object) -> Refuse:
    assert isinstance(exc, Refuse)
    assert secret_shape(str(exc)) is False
    assert secret_shape(repr(exc)) is False
    return exc


def _jail(root: Path) -> tuple[PathJail, Path]:
    grant = root / "grant"
    grant.mkdir()
    return PathJail([str(grant)]), grant


def _uri(path: Path) -> str:
    return "file:///" + path.resolve().as_posix().replace(" ", "%20")


def _wire(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _obj(payload: str) -> dict[str, object]:
    loaded: object = json.loads(payload)
    assert isinstance(loaded, dict)
    out: dict[str, object] = {}
    for key, value in loaded.items():
        assert isinstance(key, str)
        out[key] = value
    return out


def _as_dict(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    out: dict[str, object] = {}
    for key, item in value.items():
        assert isinstance(key, str)
        out[key] = item
    return out


def test_schema_surface_and_no_spawn() -> None:
    assert SCHEMA == "cosmos-hermes-lsp/1"
    assert CLIENT_NAME == "cosmos"
    assert CLIENT_VERSION == "1"
    assert METHODS == frozenset(
        {
            "initialize",
            "textDocument/didOpen",
            "textDocument/definition",
            "textDocument/hover",
            "textDocument/diagnostic",
        }
    )
    assert LANGUAGES[".py"] == "python"
    assert ".exe" not in LANGUAGES
    assert list(PUBLIC) == [
        "CLIENT_NAME",
        "CLIENT_VERSION",
        "ID_MAX",
        "LANGUAGES",
        "METHOD_CAP",
        "METHODS",
        "POSITION_CAP",
        "SCHEMA",
        "TEXT_CAP",
        "URI_CAP",
        "VERSION_MAX",
        "RpcRequest",
        "definition",
        "diagnostic",
        "did_open",
        "hover",
        "initialize",
        "parse",
        "rebuild",
    ]
    source = Path(__file__).with_name("lsp.py").read_text(encoding="utf-8")
    for banned in ("subprocess", "socket", "urllib", "requests", "pickle", "Popen"):
        assert banned not in source


def test_example_lsp(workspace: Path) -> None:
    """A Northwind checkout card opens inside the grant. Escapes refuse."""
    grant = workspace / "northwind"
    grant.mkdir()
    jail = PathJail([str(grant)])
    card = grant / "card.py"
    uri = _uri(card)
    note = "light = 3\n\ndef price(card: int) -> int:\n    return card + light\n"

    def story() -> tuple[RpcRequest, RpcRequest, RpcRequest]:
        opened = did_open(jail, uri, note, version=4)
        asked = definition(jail, uri, line=2, character=4, request_id=11)
        started = initialize(jail, _uri(grant), request_id=1)
        return opened, asked, started

    first = story()
    second = story()
    assert first == second
    opened, asked, started = first
    assert not card.exists()
    assert opened.method == "textDocument/didOpen"
    assert opened.language_id == "python"
    assert opened.request_id is None
    assert opened.version == 4
    assert opened.path == str(card.resolve())
    assert opened.uri == uri
    assert "def price" in opened.text
    assert "light = 3" not in repr(opened)
    assert secret_shape(repr(opened)) is False
    wire = _obj(opened.body)
    assert "id" not in wire
    assert wire["method"] == "textDocument/didOpen"
    assert asked.method == "textDocument/definition"
    assert asked.line == 2
    assert asked.character == 4
    assert asked.request_id == 11
    assert started.method == "initialize"
    assert started.request_id == 1
    assert "northwind" in started.body
    assert '"processId":null' in started.body
    assert "executeCommand" not in started.body
    assert parse(jail, opened.body) == opened
    assert parse(jail, asked.body) == asked
    assert parse(jail, started.body) == started
    assert rebuild(jail, opened) == opened
    assert rebuild(jail, asked) == asked
    assert rebuild(jail, started) == started
    with pytest.raises(Refuse) as escape:
        did_open(jail, "file:///" + "file:///" + card.resolve().as_posix(), note)
    assert refused(escape.value).code == "FILE_URL"
    with pytest.raises(Refuse) as dotted:
        did_open(jail, _uri(grant) + "/../card.py", note)
    assert refused(dotted.value).code == "DOTDOT"


def test_success_methods(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    target = grant / "mod.py"
    uri = _uri(target)
    assert not target.exists()
    defined = definition(jail, uri, line=8, character=4, request_id=9)
    assert not target.exists()
    assert defined.schema == SCHEMA
    assert defined.cap == POSITION_CAP
    assert defined.policy_cap == POSITION_CAP
    assert defined.text_cap == TEXT_CAP
    assert defined.policy_text == TEXT_CAP
    assert defined.path == str(target.resolve())
    assert defined.uri == uri
    assert defined == definition(jail, defined.uri, line=8, character=4, request_id=9)
    assert defined.body == _wire(
        {
            "id": 9,
            "jsonrpc": "2.0",
            "method": "textDocument/definition",
            "params": {
                "position": {"character": 4, "line": 8},
                "textDocument": {"uri": defined.uri},
            },
        }
    )
    hovered = hover(jail, uri, line=0, character=0, request_id=0)
    assert hovered.method == "textDocument/hover"
    assert hovered.request_id == 0
    assert hovered.body != defined.body
    assert parse(jail, hovered.body) == hovered
    pulled = diagnostic(jail, uri)
    assert pulled.line is None
    assert pulled.character is None
    assert pulled.request_id == 1
    loaded = _obj(pulled.body)
    assert set(loaded) == {"id", "jsonrpc", "method", "params"}
    params = _as_dict(loaded["params"])
    assert set(params) == {"textDocument"}
    assert params["textDocument"] == {"uri": pulled.uri}
    spaced = grant / "my file.py"
    encoded = _uri(spaced)
    opened = did_open(jail, encoded, "x = 1\n", version=2)
    assert opened.path == str(spaced.resolve())
    assert " " not in opened.uri
    assert "%20" in opened.uri
    assert "%20" in opened.body
    assert parse(jail, "\n" + opened.body + "\n") == opened
    assert rebuild(jail, opened) == opened
    nested = diagnostic(jail, f"file:///{grant.resolve().as_posix()}/./mod.py")
    assert nested.path == str((grant / "mod.py").resolve())
    assert "/./" not in nested.uri
    plain = grant / "notes.txt"
    listed = definition(jail, _uri(plain), line=0, character=0)
    assert listed.language_id == ""
    with pytest.raises(AttributeError):
        setattr(defined, "method", "initialize")


def test_initialize_shape(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    started = initialize(jail, _uri(grant), request_id=3)
    loaded = _obj(started.body)
    assert loaded["jsonrpc"] == "2.0"
    assert loaded["id"] == 3
    assert loaded["method"] == "initialize"
    params = _as_dict(loaded["params"])
    assert set(params) == {
        "capabilities",
        "clientInfo",
        "processId",
        "rootUri",
        "workspaceFolders",
    }
    assert params["processId"] is None
    assert params["rootUri"] == started.uri
    assert params["clientInfo"] == {"name": CLIENT_NAME, "version": CLIENT_VERSION}
    caps = _as_dict(params["capabilities"])
    text_document = _as_dict(caps["textDocument"])
    assert set(text_document) == {"definition", "diagnostic", "hover"}
    for key in ("definition", "diagnostic", "hover"):
        assert text_document[key] == {"dynamicRegistration": False}
    folders = params["workspaceFolders"]
    assert isinstance(folders, list)
    assert len(folders) == 1
    folder = _as_dict(folders[0])
    assert folder == {"name": grant.name, "uri": started.uri}
    assert parse(jail, started.body) == started
    assert rebuild(jail, started) == started


def test_caps(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    uri = _uri(grant / "mod.py")
    clamped = hover(jail, uri, line=POSITION_CAP, character=0, cap=10**18)
    assert clamped.cap == POSITION_CAP
    assert clamped.policy_cap == POSITION_CAP
    assert clamped.line == POSITION_CAP
    assert str(10**18) not in clamped.body
    exact = definition(jail, uri, line=0, character=POSITION_CAP, cap=POSITION_CAP)
    assert exact.character == POSITION_CAP
    with pytest.raises(Refuse) as past:
        definition(jail, uri, line=POSITION_CAP + 1, character=0, cap=10**18)
    assert refused(past.value).code == "OUT_OF_RANGE"
    assert refused(past.value).detail == f"0..{POSITION_CAP}"
    lowered = definition(jail, uri, line=2, character=2, cap=2)
    assert lowered.cap == 2
    assert lowered.policy_cap == POSITION_CAP
    assert rebuild(jail, lowered) == lowered
    parsed = parse(jail, lowered.body)
    assert parsed.body == lowered.body
    assert parsed.cap == POSITION_CAP
    assert parsed != lowered
    with pytest.raises(Refuse) as tight:
        hover(jail, uri, line=3, character=0, cap=2)
    assert refused(tight.value).code == "OUT_OF_RANGE"
    assert refused(tight.value).detail == "0..2"
    note = "light = 1\n"
    wide = did_open(jail, uri, note, cap=10**18)
    assert wide.text_cap == TEXT_CAP
    assert wide.policy_text == TEXT_CAP
    assert wide.cap == POSITION_CAP
    assert str(10**18) not in wide.body
    short = did_open(jail, uri, "ab", cap=4)
    assert short.text_cap == 4
    assert short.policy_text == TEXT_CAP
    assert rebuild(jail, short) == short
    with pytest.raises(Refuse) as over_text:
        did_open(jail, uri, "abcde", cap=4)
    assert refused(over_text.value).code == "OVERSIZE"
    assert refused(over_text.value).detail == "4"
    full = did_open(jail, uri, "a" * TEXT_CAP)
    assert full.text_cap == TEXT_CAP
    assert parse(jail, full.body) == full
    with pytest.raises(Refuse) as over_policy:
        did_open(jail, uri, "b" * (TEXT_CAP + 1), cap=10**18)
    assert refused(over_policy.value).code == "OVERSIZE"
    assert refused(over_policy.value).detail == str(TEXT_CAP)


def test_malformed_rpc(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    uri = _uri(grant / "card.py")
    opened = did_open(jail, uri, "light = 1\n", version=1)
    for raw in (
        "",
        "{",
        "[]",
        "null",
        "42",
        '"initialize"',
        "{}",
        '{"jsonrpc":"1.0","id":1,"method":"initialize","params":{}}',
        '{"jsonrpc":"2.0","id":1,"result":{}}',
        "Content-Length: 2\r\n\r\n{}",
        opened.body.replace('"jsonrpc":"2.0"', '"jsonrpc":"2.0","extra":1', 1),
    ):
        with pytest.raises(Refuse) as bad:
            parse(jail, raw)
        assert refused(bad.value).code == "BAD_RPC", raw
    framed = opened.body[:-1] + ',"id":1}'
    with pytest.raises(Refuse) as noted:
        parse(jail, framed)
    assert refused(noted.value).code == "BAD_RPC"
    defined = definition(jail, uri, line=0, character=1, request_id=2)
    missing_id = defined.body.replace('"id":2,', "", 1)
    with pytest.raises(Refuse) as no_id:
        parse(jail, missing_id)
    assert refused(no_id.value).code == "BAD_RPC"
    for method in (
        "shutdown",
        "exit",
        "initialized",
        "textDocument/didChange",
        "textDocument/didClose",
        "textDocument/references",
        "textDocument/completion",
        "textDocument/codeAction",
        "workspace/executeCommand",
        "workspace/applyEdit",
        "textDocument/publishDiagnostics",
        "TextDocument/Hover",
        "",
    ):
        raw = _wire({"id": 1, "jsonrpc": "2.0", "method": method, "params": {}})
        with pytest.raises(Refuse) as bad_method:
            parse(jail, raw)
        assert refused(bad_method.value).code == "BAD_METHOD", method
    changed = _obj(opened.body)
    params = _as_dict(changed["params"])
    document = _as_dict(params["textDocument"])
    document["languageId"] = "javascript"
    params["textDocument"] = document
    changed["params"] = params
    with pytest.raises(Refuse) as language:
        parse(jail, _wire(changed))
    assert refused(language.value).code == "BAD_LANGUAGE"
    started = _obj(initialize(jail, _uri(grant)).body)
    started_params = _as_dict(started["params"])
    started_params["processId"] = 4
    started["params"] = started_params
    with pytest.raises(Refuse) as pid:
        parse(jail, _wire(started))
    assert refused(pid.value).code == "BAD_BODY"
    client = _as_dict(started_params["clientInfo"])
    client["name"] = "other"
    started_params["processId"] = None
    started_params["clientInfo"] = client
    started["params"] = started_params
    with pytest.raises(Refuse) as client_name:
        parse(jail, _wire(started))
    assert refused(client_name.value).code == "BAD_BODY"
    dotted = diagnostic(jail, f"file:///{grant.resolve().as_posix()}/./mod.py")
    raw_dotted = dotted.body.replace(dotted.uri, f"file:///{grant.resolve().as_posix()}/./mod.py", 1)
    with pytest.raises(Refuse) as canon:
        parse(jail, raw_dotted)
    assert refused(canon.value).code == "BAD_URI"


def test_bad_uri_and_host(workspace: Path) -> None:
    jail, _grant = _jail(workspace)
    samples = (
        "https://example.com/mod.py",
        "http://127.0.0.1/mod.py",
        "C:/mod.py",
        "",
        "file:/C:/mod.py",
        "file://",
        "FILE:///C:/mod.py",
        "file:///C:/mod.py?x=1",
        "file:///C:/mod.py#L1",
        "file:///C:/mod.py ",
        "file:///C:/my file.py",
        "file:///C:\\mod.py",
        "file:///",
        "file:////server/share/a.py",
        "file:///C:/mod.py\n",
        "file:///%",
        "file:///%2",
        "file:///%ZZ",
        "file:///%GG",
        "file:///%FF",
        "file:///%5Cmod.py",
    )
    for uri in samples:
        with pytest.raises(Refuse) as bad:
            diagnostic(jail, uri)
        assert refused(bad.value).code == "BAD_URI", uri
    for uri in (
        "file://localhost/C:/mod.py",
        "file://127.0.0.1/C:/mod.py",
        "file://C:/mod.py",
    ):
        with pytest.raises(Refuse) as host:
            diagnostic(jail, uri)
        assert refused(host.value).code == "BAD_HOST"


def test_bad_position(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    uri = _uri(grant / "mod.py")
    with pytest.raises(Refuse) as missing_both:
        definition(jail, uri)
    assert refused(missing_both.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as missing_character:
        hover(jail, uri, line=0)
    assert refused(missing_character.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as missing_line:
        hover(jail, uri, character=0)
    assert refused(missing_line.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as extra_line:
        diagnostic(jail, uri, line=0)
    assert refused(extra_line.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as extra_both:
        diagnostic(jail, uri, line=0, character=0)
    assert refused(extra_both.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as extra_character:
        diagnostic(jail, uri, character=1)
    assert refused(extra_character.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as open_line:
        did_open(jail, uri, "x = 1\n", line=0)
    assert refused(open_line.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as init_character:
        initialize(jail, _uri(grant), character=1)
    assert refused(init_character.value).code == "BAD_POSITION"


def test_limits_and_types(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    uri = _uri(grant / "mod.py")
    note = "x = 1\n"
    for cap in (True, False, 0, -3, "9", 1.5, b"4"):
        with pytest.raises(Refuse) as bad_cap:
            hover(jail, uri, line=0, character=0, cap=cap)
        assert refused(bad_cap.value).code == "BAD_LIMIT"
        with pytest.raises(Refuse) as bad_text:
            did_open(jail, uri, note, cap=cap)
        assert refused(bad_text.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as not_int_line:
        hover(jail, uri, line=True, character=0)
    assert refused(not_int_line.value).code == "NOT_INT"
    with pytest.raises(Refuse) as not_int_character:
        hover(jail, uri, line=0, character="0")
    assert refused(not_int_character.value).code == "NOT_INT"
    with pytest.raises(Refuse) as not_int_id:
        diagnostic(jail, uri, request_id=None)
    assert refused(not_int_id.value).code == "NOT_INT"
    with pytest.raises(Refuse) as float_id:
        diagnostic(jail, uri, request_id=1.0)
    assert refused(float_id.value).code == "NOT_INT"
    with pytest.raises(Refuse) as bool_version:
        did_open(jail, uri, note, version=True)
    assert refused(bool_version.value).code == "NOT_INT"
    with pytest.raises(Refuse) as low_line:
        definition(jail, uri, line=-1, character=0)
    assert refused(low_line.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as low_version:
        did_open(jail, uri, note, version=-1)
    assert refused(low_version.value).code == "OUT_OF_RANGE"
    assert refused(low_version.value).detail == f"0..{VERSION_MAX}"
    top_version = did_open(jail, uri, note, version=VERSION_MAX)
    assert top_version.version == VERSION_MAX
    with pytest.raises(Refuse) as high_version:
        did_open(jail, uri, note, version=VERSION_MAX + 1)
    assert refused(high_version.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as low_id:
        diagnostic(jail, uri, request_id=-1)
    assert refused(low_id.value).code == "OUT_OF_RANGE"
    assert refused(low_id.value).detail == f"0..{ID_MAX}"
    with pytest.raises(Refuse) as high_id:
        diagnostic(jail, uri, request_id=ID_MAX + 1)
    assert refused(high_id.value).code == "OUT_OF_RANGE"
    top = diagnostic(jail, uri, request_id=ID_MAX)
    assert top.request_id == ID_MAX
    with pytest.raises(Refuse) as not_text_uri:
        diagnostic(jail, 12)
    assert refused(not_text_uri.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as not_text_body:
        parse(jail, b"{}")
    assert refused(not_text_body.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as not_text_doc:
        did_open(jail, uri, None)
    assert refused(not_text_doc.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        diagnostic(jail, "file:///C:/a.py\x00")
    assert refused(nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as encoded_nul:
        diagnostic(jail, "file:///C:/a%00.py")
    assert refused(encoded_nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as nul_text:
        did_open(jail, uri, "x\x00")
    assert refused(nul_text.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as over_uri:
        diagnostic(jail, "u" * (URI_CAP + 1))
    assert refused(over_uri.value).code == "OVERSIZE"
    assert refused(over_uri.value).detail == str(URI_CAP)
    long_method = "m" * (METHOD_CAP + 1)
    raw = _wire({"id": 1, "jsonrpc": "2.0", "method": long_method, "params": {}})
    with pytest.raises(Refuse) as over_method:
        parse(jail, raw)
    assert refused(over_method.value).code == "OVERSIZE"
    assert refused(over_method.value).detail == str(METHOD_CAP)
    with pytest.raises(Refuse) as bad_jail:
        diagnostic(object(), uri)
    assert refused(bad_jail.value).code == "BAD_JAIL"
    with pytest.raises(Refuse) as path_jail:
        diagnostic(grant, uri)
    assert refused(path_jail.value).code == "BAD_JAIL"
    with pytest.raises(Refuse) as parse_jail:
        parse(None, "{}")
    assert refused(parse_jail.value).code == "BAD_JAIL"


def test_jail_paths(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    posix = grant.resolve().as_posix()
    with pytest.raises(Refuse) as outside:
        diagnostic(jail, _uri(workspace / "other.py"))
    assert refused(outside.value).code == "OUTSIDE_GRANT"
    with pytest.raises(Refuse) as dotted:
        diagnostic(jail, f"file:///{posix}/../out.py")
    assert refused(dotted.value).code == "DOTDOT"
    with pytest.raises(Refuse) as encoded_dot:
        diagnostic(jail, f"file:///{posix}/%2e%2e/out.py")
    assert refused(encoded_dot.value).code == "DOTDOT"
    with pytest.raises(Refuse) as double_encoded:
        diagnostic(jail, f"file:///{posix}/%252e%252e/out.py")
    assert refused(double_encoded.value).code == "ENCODED_DOTDOT"
    with pytest.raises(Refuse) as relative:
        diagnostic(jail, "file:///grant/mod.py")
    assert refused(relative.value).code == "RELATIVE_PATH"
    with pytest.raises(Refuse) as drive_root:
        diagnostic(jail, "file:///C:/")
    assert refused(drive_root.value).code == "DRIVE_ROOT"
    with pytest.raises(Refuse) as drive_relative:
        diagnostic(jail, "file:///C:foo")
    assert refused(drive_relative.value).code == "DRIVE_RELATIVE"
    with pytest.raises(Refuse) as stream:
        diagnostic(jail, f"file:///{posix}/name:stream")
    assert refused(stream.value).code == "ALT_STREAM"
    with pytest.raises(Refuse) as trailing:
        diagnostic(jail, f"file:///{posix}/name.")
    assert refused(trailing.value).code == "TRAILING_DOT"
    with pytest.raises(Refuse) as file_url:
        diagnostic(jail, "file:///file:///C:/Windows")
    assert refused(file_url.value).code == "FILE_URL"
    with pytest.raises(Refuse) as encoded_file:
        diagnostic(jail, "file:///%66%69%6c%65%3a%2f%2f%2fC%3a/Windows")
    assert refused(encoded_file.value).code == "FILE_URL"
    with pytest.raises(Refuse) as unc:
        diagnostic(jail, "file:///%2F%2Fserver%2Fshare%2Fa.py")
    assert refused(unc.value).code == "UNC"
    with pytest.raises(Refuse) as rebuild_outside:
        rebuild(jail, diagnostic(jail, _uri(grant / "mod.py")).__class__)
    assert refused(rebuild_outside.value).code == "BAD_RECORD"


def test_languages(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    note = "x = 1\n"
    opened = did_open(jail, _uri(grant / "Card.PY"), note)
    assert opened.language_id == "python"
    blade = did_open(jail, _uri(grant / "page.blade.php"), "<p></p>")
    assert blade.language_id == "blade"
    php = did_open(jail, _uri(grant / "page.php"), "<?php\n")
    assert php.language_id == "php"
    docker = did_open(jail, _uri(grant / "Dockerfile"), "FROM scratch\n")
    assert docker.language_id == "dockerfile"
    with pytest.raises(Refuse) as unknown:
        did_open(jail, _uri(grant / "notes.txt"), "hello\n")
    assert refused(unknown.value).code == "BAD_LANGUAGE"
    with pytest.raises(Refuse) as secret_lang:
        raw = _obj(opened.body)
        params = _as_dict(raw["params"])
        document = _as_dict(params["textDocument"])
        document["languageId"] = "sk-livekey12"
        params["textDocument"] = document
        raw["params"] = params
        parse(jail, _wire(raw))
    assert refused(secret_lang.value).code == "SECRET"
    assert "livekey12" not in str(secret_lang.value)


def test_secrets(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    posix = grant.resolve().as_posix()
    with pytest.raises(Refuse) as raw_key:
        hover(jail, f"file:///{posix}/sk-livekey12.py", line=0, character=0)
    assert refused(raw_key.value).code == "SECRET"
    assert "livekey12" not in str(raw_key.value)
    assert "livekey12" not in repr(raw_key.value)
    with pytest.raises(Refuse) as encoded_key:
        diagnostic(jail, f"file:///{posix}/sk-%6civekey12.py")
    assert refused(encoded_key.value).code == "SECRET"
    assert "livekey12" not in str(encoded_key.value)
    with pytest.raises(Refuse) as assignment:
        diagnostic(jail, f"file:///{posix}/x.py?api_key=abcdef")
    assert refused(assignment.value).code == "SECRET"
    assert "abcdef" not in str(assignment.value)
    with pytest.raises(Refuse) as bearer:
        diagnostic(jail, f"file:///{posix}/Bearer%20abcdefgh.py")
    assert refused(bearer.value).code == "SECRET"
    assert "abcdefgh" not in str(bearer.value)
    with pytest.raises(Refuse) as document:
        did_open(jail, _uri(grant / "card.py"), "token = 'sk-livekey12'\n")
    assert refused(document.value).code == "SECRET"
    assert "livekey12" not in repr(document.value)
    with pytest.raises(Refuse) as body:
        parse(jail, '{"jsonrpc":"sk-livekey12"}')
    assert refused(body.value).code == "SECRET"
    with pytest.raises(Refuse) as method:
        parse(
            jail,
            _wire({"id": 1, "jsonrpc": "2.0", "method": "sk-livekey12", "params": {}}),
        )
    assert refused(method.value).code == "SECRET"


def test_record_integrity(workspace: Path) -> None:
    jail, grant = _jail(workspace)
    uri = _uri(grant / "card.py")
    note = "light = 3\n"
    opened = did_open(jail, uri, note, version=2)
    pulled = diagnostic(jail, uri, request_id=4)
    with pytest.raises(Refuse) as bad_schema:
        replace(opened, schema="cosmos-hermes-lsp/2")
    assert refused(bad_schema.value).code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as bad_body:
        replace(opened, body=opened.body + " ")
    assert refused(bad_body.value).code == "BAD_BODY"
    with pytest.raises(Refuse) as bad_method:
        replace(pulled, method="shutdown")
    assert refused(bad_method.value).code == "BAD_METHOD"
    with pytest.raises(Refuse) as secret_method:
        replace(pulled, method="sk-livekey12")
    assert refused(secret_method.value).code == "SECRET"
    with pytest.raises(Refuse) as raised_cap:
        replace(pulled, cap=POSITION_CAP + 1)
    assert refused(raised_cap.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as policy:
        replace(pulled, policy_cap=POSITION_CAP - 1)
    assert refused(policy.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as text_policy:
        replace(opened, policy_text=TEXT_CAP - 1)
    assert refused(text_policy.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as position_cap:
        replace(opened, cap=2)
    assert refused(position_cap.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as text_cap:
        replace(pulled, text_cap=4)
    assert refused(text_cap.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as moved:
        replace(pulled, line=0, character=0)
    assert refused(moved.value).code == "BAD_POSITION"
    with pytest.raises(Refuse) as noted:
        replace(opened, request_id=1)
    assert refused(noted.value).code == "BAD_RPC"
    with pytest.raises(Refuse) as bad_language:
        replace(opened, language_id="javascript")
    assert refused(bad_language.value).code == "BAD_LANGUAGE"
    with pytest.raises(Refuse) as bad_uri:
        replace(pulled, uri="file:///C:/elsewhere.py")
    assert refused(bad_uri.value).code == "BAD_URI"
    with pytest.raises(Refuse) as not_record:
        rebuild(jail, {"method": "initialize"})
    assert refused(not_record.value).code == "BAD_RECORD"
    sibling = workspace / "other"
    sibling.mkdir()
    with pytest.raises(Refuse) as other_grant:
        rebuild(PathJail([str(sibling)]), opened)
    assert refused(other_grant.value).code == "OUTSIDE_GRANT"
