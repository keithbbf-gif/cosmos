"""JSON-RPC descriptors for an LSP session. No language server is started."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-lsp/1"
CLIENT_NAME: Final[str] = "cosmos"
CLIENT_VERSION: Final[str] = "1"
POSITION_CAP: Final[int] = 1_000_000
# A non-BMP character expands to 12 JSON characters. 16000 * 12 stays under the text bound.
TEXT_CAP: Final[int] = 16_000
URI_CAP: Final[int] = 4_096
METHOD_CAP: Final[int] = 64
ID_MAX: Final[int] = 2_147_483_647
VERSION_MAX: Final[int] = 1_000_000

_INITIALIZE: Final[str] = "initialize"
_DID_OPEN: Final[str] = "textDocument/didOpen"
_DEFINITION: Final[str] = "textDocument/definition"
_HOVER: Final[str] = "textDocument/hover"
_DIAGNOSTIC: Final[str] = "textDocument/diagnostic"

METHODS: Final[frozenset[str]] = frozenset(
    {_INITIALIZE, _DID_OPEN, _DEFINITION, _HOVER, _DIAGNOSTIC}
)
_NOTES: Final[frozenset[str]] = frozenset({_DID_OPEN})
_POSITIONED: Final[frozenset[str]] = frozenset({_DEFINITION, _HOVER})
_REQUEST_KEYS: Final[frozenset[str]] = frozenset({"id", "jsonrpc", "method", "params"})
_NOTE_KEYS: Final[frozenset[str]] = frozenset({"jsonrpc", "method", "params"})
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdefABCDEF")
_KEEP: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~/:"
)
_REJECT: Final[frozenset[str]] = frozenset("?#\\@[]")
_SEPARATORS: Final[tuple[str, str]] = (",", ":")
_FILE_PREFIX: Final[str] = "file://"

_BY_SUFFIX: Final[dict[str, str]] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescriptreact",
    ".js": "javascript",
    ".jsx": "javascriptreact",
    ".vue": "vue",
    ".svelte": "svelte",
    ".astro": "astro",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".sh": "shellscript",
    ".bash": "shellscript",
    ".zsh": "shellscript",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".lua": "lua",
    ".php": "php",
    ".dockerfile": "dockerfile",
    ".tf": "terraform",
    ".dart": "dart",
    ".hs": "haskell",
    ".jl": "julia",
    ".clj": "clojure",
    ".nix": "nix",
    ".zig": "zig",
    ".gleam": "gleam",
    ".ex": "elixir",
    ".exs": "elixir",
    ".prisma": "prisma",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".java": "java",
    ".ps1": "powershell",
    ".ml": "ocaml",
    ".mli": "ocaml",
}
_BASENAMES: Final[dict[str, str]] = {"dockerfile": "dockerfile"}

LANGUAGES: Final[MappingProxyType[str, str]] = MappingProxyType(_BY_SUFFIX)

__all__ = [
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


@dataclass(frozen=True, slots=True)
class _Held:
    path: str
    uri: str
    resolved: Path


def _jail(value: object) -> PathJail:
    if not isinstance(value, PathJail):
        raise Refuse("BAD_JAIL")
    return value


def _applied(value: object, policy: int) -> int:
    """Keep a lower positive cap. A request above the policy cap is ignored."""
    if value is None:
        return policy
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise Refuse("BAD_LIMIT")
    if value > policy:
        return policy
    return value


def _stored(value: object, policy: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > policy:
        raise Refuse("BAD_LIMIT")
    return value


def _dump(payload: dict[str, object]) -> str:
    try:
        rendered = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=_SEPARATORS,
            sort_keys=True,
        )
    except (TypeError, ValueError):
        raise Refuse("BAD_RPC") from None
    return bound_text(rendered)


def _pct_decode(text: str) -> str:
    raw = bytearray()
    index = 0
    size = len(text)
    while index < size:
        char = text[index]
        if char != "%":
            code = ord(char)
            if code < 33 or code > 126 or char in _REJECT:
                raise Refuse("BAD_URI")
            raw.append(code)
            index += 1
            continue
        if index + 2 >= size:
            raise Refuse("BAD_URI")
        pair = text[index + 1 : index + 3]
        if pair[0] not in _HEX or pair[1] not in _HEX:
            raise Refuse("BAD_URI")
        raw.append(int(pair, 16))
        index += 3
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse("BAD_URI") from None


def _pct_encode(text: str) -> str:
    parts: list[str] = []
    for char in text:
        if char in _KEEP:
            parts.append(char)
            continue
        encoded = char.encode("utf-8")
        for byte in encoded:
            parts.append(f"%{byte:02X}")
    return "".join(parts)


def _file_uri(resolved: Path) -> str:
    """Empty host. Nothing sits between file:// and the path slash."""
    return _FILE_PREFIX + "/" + _pct_encode(resolved.as_posix())


def _local_path(raw: str) -> str:
    if secret_shape(raw):
        raise Refuse("SECRET")
    if not raw.startswith(_FILE_PREFIX):
        raise Refuse("BAD_URI")
    after = raw[len(_FILE_PREFIX) :]
    if after == "" or after[0] != "/":
        raise Refuse("BAD_URI" if after == "" else "BAD_HOST")
    rest = after[1:]
    if rest == "" or rest.startswith("/"):
        raise Refuse("BAD_URI")
    decoded = _pct_decode(rest)
    if decoded == "":
        raise Refuse("BAD_URI")
    path = bound_text(decoded)
    if secret_shape(path):
        raise Refuse("SECRET")
    if any(ord(char) < 32 or ord(char) == 127 or char == "\\" for char in path):
        raise Refuse("BAD_URI")
    return path


def _hold(jail: PathJail, uri: object) -> _Held:
    raw = bound_text(uri, URI_CAP)
    resolved = jail.contain(_local_path(raw))
    path = str(resolved)
    canonical = _file_uri(resolved)
    return _Held(path=path, uri=canonical, resolved=resolved)


def _language(resolved: Path) -> str:
    name = resolved.name.lower()
    if name.endswith(".blade.php"):
        return "blade"
    base = _BASENAMES.get(name)
    if base is not None:
        return base
    found = _BY_SUFFIX.get(resolved.suffix.lower())
    if found is None:
        raise Refuse("BAD_LANGUAGE")
    return found


def _folder_name(resolved: Path) -> str:
    name = resolved.name
    if name == "" or name in {".", ".."}:
        raise Refuse("BAD_URI")
    return name


def _capabilities() -> dict[str, object]:
    definition: dict[str, object] = {"dynamicRegistration": False}
    diagnostic: dict[str, object] = {"dynamicRegistration": False}
    hover: dict[str, object] = {"dynamicRegistration": False}
    text_document: dict[str, object] = {
        "definition": definition,
        "diagnostic": diagnostic,
        "hover": hover,
    }
    return {"textDocument": text_document}


def _request(request_id: int, method: str, params: dict[str, object]) -> dict[str, object]:
    return {"id": request_id, "jsonrpc": "2.0", "method": method, "params": params}


def _note(method: str, params: dict[str, object]) -> dict[str, object]:
    return {"jsonrpc": "2.0", "method": method, "params": params}


def _body_initialize(request_id: int, uri: str, name: str) -> str:
    # processId stays null. This module does not own a process.
    folder: dict[str, object] = {"name": name, "uri": uri}
    params: dict[str, object] = {
        "capabilities": _capabilities(),
        "clientInfo": {"name": CLIENT_NAME, "version": CLIENT_VERSION},
        "processId": None,
        "rootUri": uri,
        "workspaceFolders": [folder],
    }
    return _dump(_request(request_id, _INITIALIZE, params))


def _body_open(uri: str, language_id: str, version: int, text: str) -> str:
    document: dict[str, object] = {
        "languageId": language_id,
        "text": text,
        "uri": uri,
        "version": version,
    }
    params: dict[str, object] = {"textDocument": document}
    return _dump(_note(_DID_OPEN, params))


def _body_at(method: str, request_id: int, uri: str, line: int, character: int) -> str:
    position: dict[str, object] = {"character": character, "line": line}
    document: dict[str, object] = {"uri": uri}
    params: dict[str, object] = {"position": position, "textDocument": document}
    return _dump(_request(request_id, method, params))


def _body_diagnostic(request_id: int, uri: str) -> str:
    document: dict[str, object] = {"uri": uri}
    params: dict[str, object] = {"textDocument": document}
    return _dump(_request(request_id, _DIAGNOSTIC, params))


def _positions(line: object, character: object, cap: int) -> tuple[int, int]:
    if line is None or character is None:
        raise Refuse("BAD_POSITION")
    return bound_int(line, 0, cap), bound_int(character, 0, cap)


def _shape(
    method: str,
    request_id: int | None,
    line: int | None,
    character: int | None,
    version: int | None,
    cap: int,
) -> tuple[int | None, int | None, int | None, int | None]:
    if method == _DID_OPEN:
        if request_id is not None:
            raise Refuse("BAD_RPC")
        if line is not None or character is not None:
            raise Refuse("BAD_POSITION")
        if version is None:
            raise Refuse("BAD_BODY")
        return None, None, None, bound_int(version, 0, VERSION_MAX)
    if request_id is None:
        raise Refuse("BAD_RPC")
    identity = bound_int(request_id, 0, ID_MAX)
    if method in _POSITIONED:
        if line is None or character is None:
            raise Refuse("BAD_POSITION")
        if version is not None:
            raise Refuse("BAD_BODY")
        return identity, bound_int(line, 0, cap), bound_int(character, 0, cap), None
    if line is not None or character is not None:
        raise Refuse("BAD_POSITION")
    if version is not None:
        raise Refuse("BAD_BODY")
    return identity, None, None, None


@dataclass(frozen=True, slots=True)
class RpcRequest:
    """One JSON-RPC descriptor. `cap` and `text_cap` are the caps that were applied."""

    schema: str
    method: str
    request_id: int | None
    uri: str
    path: str
    language_id: str
    version: int | None
    text: str
    line: int | None
    character: int | None
    cap: int
    policy_cap: int
    text_cap: int
    policy_text: int
    body: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        method = bound_text(self.method, METHOD_CAP)
        if secret_shape(method):
            raise Refuse("SECRET")
        if method not in METHODS:
            raise Refuse("BAD_METHOD")
        if self.policy_cap != POSITION_CAP or self.policy_text != TEXT_CAP:
            raise Refuse("BAD_LIMIT")
        position_cap = _stored(self.cap, POSITION_CAP)
        text_cap = _stored(self.text_cap, TEXT_CAP)
        if method == _DID_OPEN:
            if position_cap != POSITION_CAP:
                raise Refuse("BAD_LIMIT")
        elif method in _POSITIONED:
            if text_cap != TEXT_CAP:
                raise Refuse("BAD_LIMIT")
        elif position_cap != POSITION_CAP or text_cap != TEXT_CAP:
            raise Refuse("BAD_LIMIT")
        uri = bound_text(self.uri, URI_CAP)
        path = bound_text(self.path)
        language_id = bound_text(self.language_id, METHOD_CAP)
        text = bound_text(self.text, text_cap)
        if secret_shape(path) or secret_shape(text) or secret_shape(language_id):
            raise Refuse("SECRET")
        held = Path(path)
        if not held.is_absolute():
            raise Refuse("RELATIVE_PATH")
        canonical = _file_uri(held)
        if str(held) != path or uri != canonical:
            if secret_shape(uri):
                raise Refuse("SECRET")
            raise Refuse("BAD_URI")
        identity, line, character, version = _shape(
            method, self.request_id, self.line, self.character, self.version, position_cap
        )
        if method == _DID_OPEN:
            if version is None:
                raise Refuse("BAD_BODY")
            if language_id != _language(held):
                raise Refuse("BAD_LANGUAGE")
            rendered = _body_open(uri, language_id, version, text)
        elif method == _DEFINITION or method == _HOVER:
            if language_id != "" or text != "" or version is not None:
                raise Refuse("BAD_BODY")
            if line is None or character is None or identity is None:
                raise Refuse("BAD_POSITION")
            rendered = _body_at(method, identity, uri, line, character)
        elif method == _DIAGNOSTIC:
            if language_id != "" or text != "" or version is not None:
                raise Refuse("BAD_BODY")
            if identity is None:
                raise Refuse("BAD_RPC")
            rendered = _body_diagnostic(identity, uri)
        elif method == _INITIALIZE:
            if language_id != "" or text != "" or version is not None:
                raise Refuse("BAD_BODY")
            if identity is None:
                raise Refuse("BAD_RPC")
            rendered = _body_initialize(identity, uri, _folder_name(held))
        else:
            raise Refuse("BAD_METHOD")
        if self.body != rendered:
            raise Refuse("BAD_BODY")

    def __repr__(self) -> str:
        return (
            "RpcRequest("
            f"method={self.method!r}, request_id={self.request_id!r}, "
            f"path={self.path!r}, language_id={self.language_id!r}, "
            f"version={self.version!r}, line={self.line!r}, "
            f"character={self.character!r}, cap={self.cap!r}, text_cap={self.text_cap!r})"
        )


def initialize(
    jail: object,
    uri: object,
    *,
    request_id: object = 1,
    line: object = None,
    character: object = None,
) -> RpcRequest:
    """Return an initialize request for a jailed root. Nothing is started."""
    if line is not None or character is not None:
        raise Refuse("BAD_POSITION")
    held_jail = _jail(jail)
    identity = bound_int(request_id, 0, ID_MAX)
    held = _hold(held_jail, uri)
    name = _folder_name(held.resolved)
    body = _body_initialize(identity, held.uri, name)
    return RpcRequest(
        schema=SCHEMA,
        method=_INITIALIZE,
        request_id=identity,
        uri=held.uri,
        path=held.path,
        language_id="",
        version=None,
        text="",
        line=None,
        character=None,
        cap=POSITION_CAP,
        policy_cap=POSITION_CAP,
        text_cap=TEXT_CAP,
        policy_text=TEXT_CAP,
        body=body,
    )


def did_open(
    jail: object,
    uri: object,
    text: object,
    *,
    version: object = 1,
    cap: object = None,
    line: object = None,
    character: object = None,
) -> RpcRequest:
    """Return a didOpen notification. `cap` bounds the document text."""
    if line is not None or character is not None:
        raise Refuse("BAD_POSITION")
    applied = _applied(cap, TEXT_CAP)
    document = bound_text(text, applied)
    revision = bound_int(version, 0, VERSION_MAX)
    held_jail = _jail(jail)
    held = _hold(held_jail, uri)
    language_id = _language(held.resolved)
    body = _body_open(held.uri, language_id, revision, document)
    return RpcRequest(
        schema=SCHEMA,
        method=_DID_OPEN,
        request_id=None,
        uri=held.uri,
        path=held.path,
        language_id=language_id,
        version=revision,
        text=document,
        line=None,
        character=None,
        cap=POSITION_CAP,
        policy_cap=POSITION_CAP,
        text_cap=applied,
        policy_text=TEXT_CAP,
        body=body,
    )


def _positioned(
    method: str,
    jail: object,
    uri: object,
    line: object,
    character: object,
    request_id: object,
    cap: object,
) -> RpcRequest:
    applied = _applied(cap, POSITION_CAP)
    row, column = _positions(line, character, applied)
    identity = bound_int(request_id, 0, ID_MAX)
    held_jail = _jail(jail)
    held = _hold(held_jail, uri)
    body = _body_at(method, identity, held.uri, row, column)
    return RpcRequest(
        schema=SCHEMA,
        method=method,
        request_id=identity,
        uri=held.uri,
        path=held.path,
        language_id="",
        version=None,
        text="",
        line=row,
        character=column,
        cap=applied,
        policy_cap=POSITION_CAP,
        text_cap=TEXT_CAP,
        policy_text=TEXT_CAP,
        body=body,
    )


def definition(
    jail: object,
    uri: object,
    *,
    line: object = None,
    character: object = None,
    request_id: object = 1,
    cap: object = None,
) -> RpcRequest:
    """Return a textDocument/definition request. `cap` bounds the position."""
    return _positioned(_DEFINITION, jail, uri, line, character, request_id, cap)


def hover(
    jail: object,
    uri: object,
    *,
    line: object = None,
    character: object = None,
    request_id: object = 1,
    cap: object = None,
) -> RpcRequest:
    """Return a textDocument/hover request. `cap` bounds the position."""
    return _positioned(_HOVER, jail, uri, line, character, request_id, cap)


def diagnostic(
    jail: object,
    uri: object,
    *,
    request_id: object = 1,
    line: object = None,
    character: object = None,
) -> RpcRequest:
    """Return a textDocument/diagnostic pull. A position is refused."""
    if line is not None or character is not None:
        raise Refuse("BAD_POSITION")
    held_jail = _jail(jail)
    identity = bound_int(request_id, 0, ID_MAX)
    held = _hold(held_jail, uri)
    body = _body_diagnostic(identity, held.uri)
    return RpcRequest(
        schema=SCHEMA,
        method=_DIAGNOSTIC,
        request_id=identity,
        uri=held.uri,
        path=held.path,
        language_id="",
        version=None,
        text="",
        line=None,
        character=None,
        cap=POSITION_CAP,
        policy_cap=POSITION_CAP,
        text_cap=TEXT_CAP,
        policy_text=TEXT_CAP,
        body=body,
    )


def _object(text: str) -> dict[str, object]:
    try:
        loaded: object = json.loads(text)
    except (ValueError, RecursionError):
        raise Refuse("BAD_RPC") from None
    if not isinstance(loaded, dict):
        raise Refuse("BAD_RPC")
    out: dict[str, object] = {}
    for key, value in loaded.items():
        if not isinstance(key, str):
            raise Refuse("BAD_RPC")
        out[key] = value
    return out


def _keys(loaded: dict[str, object]) -> frozenset[str]:
    return frozenset(loaded)


def _as_dict(value: object, code: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise Refuse(code)
    out: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise Refuse(code)
        out[key] = item
    return out


def _need(obj: dict[str, object], key: str, code: str) -> object:
    if key not in obj:
        raise Refuse(code)
    return obj[key]


def _match(made: RpcRequest, raw_uri: str, loaded: dict[str, object]) -> RpcRequest:
    if made.uri != raw_uri:
        raise Refuse("BAD_URI")
    if _dump(loaded) != made.body:
        raise Refuse("BAD_BODY")
    return made


def _parse_initialize(
    jail: PathJail, request_id: int, params: dict[str, object], loaded: dict[str, object]
) -> RpcRequest:
    if "processId" not in params or params["processId"] is not None:
        raise Refuse("BAD_BODY")
    raw_uri = bound_text(_need(params, "rootUri", "BAD_BODY"), URI_CAP)
    made = initialize(jail, raw_uri, request_id=request_id)
    return _match(made, raw_uri, loaded)


def _parse_open(
    jail: PathJail, params: dict[str, object], loaded: dict[str, object]
) -> RpcRequest:
    if "position" in params:
        raise Refuse("BAD_POSITION")
    document = _as_dict(_need(params, "textDocument", "BAD_BODY"), "BAD_BODY")
    raw_uri = bound_text(_need(document, "uri", "BAD_BODY"), URI_CAP)
    language_id = bound_text(_need(document, "languageId", "BAD_BODY"), METHOD_CAP)
    if secret_shape(language_id):
        raise Refuse("SECRET")
    version = bound_int(_need(document, "version", "BAD_BODY"), 0, VERSION_MAX)
    text = bound_text(_need(document, "text", "BAD_BODY"), TEXT_CAP)
    preview = _hold(jail, raw_uri)
    if preview.uri != raw_uri:
        raise Refuse("BAD_URI")
    if language_id != _language(preview.resolved):
        raise Refuse("BAD_LANGUAGE")
    made = did_open(jail, raw_uri, text, version=version)
    return _match(made, raw_uri, loaded)


def _parse_at(
    method: str,
    jail: PathJail,
    request_id: int,
    params: dict[str, object],
    loaded: dict[str, object],
) -> RpcRequest:
    if "position" not in params:
        raise Refuse("BAD_POSITION")
    document = _as_dict(_need(params, "textDocument", "BAD_BODY"), "BAD_BODY")
    position = _as_dict(_need(params, "position", "BAD_POSITION"), "BAD_POSITION")
    raw_uri = bound_text(_need(document, "uri", "BAD_BODY"), URI_CAP)
    line = _need(position, "line", "BAD_POSITION")
    character = _need(position, "character", "BAD_POSITION")
    if method == _DEFINITION:
        made = definition(
            jail, raw_uri, line=line, character=character, request_id=request_id
        )
    else:
        made = hover(jail, raw_uri, line=line, character=character, request_id=request_id)
    return _match(made, raw_uri, loaded)


def _parse_diagnostic(
    jail: PathJail, request_id: int, params: dict[str, object], loaded: dict[str, object]
) -> RpcRequest:
    if "position" in params:
        raise Refuse("BAD_POSITION")
    document = _as_dict(_need(params, "textDocument", "BAD_BODY"), "BAD_BODY")
    raw_uri = bound_text(_need(document, "uri", "BAD_BODY"), URI_CAP)
    made = diagnostic(jail, raw_uri, request_id=request_id)
    return _match(made, raw_uri, loaded)


def parse(jail: object, raw: object) -> RpcRequest:
    """Accept one JSON-RPC object. A malformed envelope raises Refuse."""
    held_jail = _jail(jail)
    text = bound_text(raw)
    if secret_shape(text):
        raise Refuse("SECRET")
    loaded = _object(text)
    if loaded.get("jsonrpc") != "2.0":
        raise Refuse("BAD_RPC")
    method_value = loaded.get("method")
    if not isinstance(method_value, str):
        raise Refuse("BAD_RPC")
    method = bound_text(method_value, METHOD_CAP)
    if secret_shape(method):
        raise Refuse("SECRET")
    if method not in METHODS:
        raise Refuse("BAD_METHOD")
    keys = _keys(loaded)
    if method in _NOTES:
        if keys != _NOTE_KEYS:
            raise Refuse("BAD_RPC")
        request_id: int | None = None
    else:
        if keys != _REQUEST_KEYS:
            raise Refuse("BAD_RPC")
        request_id = bound_int(_need(loaded, "id", "BAD_RPC"), 0, ID_MAX)
    params = _as_dict(loaded.get("params"), "BAD_RPC")
    if method == _INITIALIZE:
        if request_id is None:
            raise Refuse("BAD_RPC")
        return _parse_initialize(held_jail, request_id, params, loaded)
    if method == _DID_OPEN:
        return _parse_open(held_jail, params, loaded)
    if method == _DEFINITION or method == _HOVER:
        if request_id is None:
            raise Refuse("BAD_RPC")
        return _parse_at(method, held_jail, request_id, params, loaded)
    if method == _DIAGNOSTIC:
        if request_id is None:
            raise Refuse("BAD_RPC")
        return _parse_diagnostic(held_jail, request_id, params, loaded)
    raise Refuse("BAD_METHOD")


def _identity(record: RpcRequest) -> int:
    request_id = record.request_id
    if request_id is None:
        raise Refuse("BAD_RPC")
    return request_id


def _again(jail: PathJail, record: RpcRequest) -> RpcRequest:
    method = record.method
    if method == _DID_OPEN:
        version = record.version
        if version is None:
            raise Refuse("BAD_BODY")
        return did_open(
            jail, record.uri, record.text, version=version, cap=record.text_cap
        )
    if method == _DEFINITION or method == _HOVER:
        line = record.line
        character = record.character
        if line is None or character is None:
            raise Refuse("BAD_POSITION")
        identity = _identity(record)
        if method == _DEFINITION:
            return definition(
                jail,
                record.uri,
                line=line,
                character=character,
                request_id=identity,
                cap=record.cap,
            )
        return hover(
            jail,
            record.uri,
            line=line,
            character=character,
            request_id=identity,
            cap=record.cap,
        )
    if method == _DIAGNOSTIC:
        return diagnostic(jail, record.uri, request_id=_identity(record))
    if method == _INITIALIZE:
        return initialize(jail, record.uri, request_id=_identity(record))
    raise Refuse("BAD_METHOD")


def rebuild(jail: object, record: object) -> RpcRequest:
    """Replay one emitted record through the jail. The result equals the record."""
    held_jail = _jail(jail)
    if not isinstance(record, RpcRequest):
        raise Refuse("BAD_RECORD")
    fresh = _again(held_jail, record)
    if fresh != record:
        raise Refuse("BAD_RECORD")
    return fresh
