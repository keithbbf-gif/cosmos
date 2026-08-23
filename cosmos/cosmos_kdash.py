#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_kdash - the KDash CREATE panel contract (pure API client).

KDash is a browser page, not a capability claim. This module is the executable
gate for that page: the CREATE panel calls GET /api/v1/makers?kind=... and
renders matching makers as cards. An unknown kind REFUSES (UNKNOWN_KIND) rather
than fetching and treating a typo as "none of those exist". A remote script or
stylesheet is CDN_FORBIDDEN - the dashboard is stdlib-era: no CDNs.

The page is inspected as bytes on disk. Rendering helpers here are the same
card/invoke shape the page paints, so a test can fail the HTML and the client
on the same axis.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

CREATE_KINDS = ("AGENT", "TOOL", "CONNECTOR", "SKILL")
KIND_LABELS = (("AGENT", "Agent"), ("TOOL", "Tool"),
               ("CONNECTOR", "Connector"), ("SKILL", "Skill"))
REQUIRED_CARD_FIELDS = ("id", "kind", "location", "function", "access",
                        "potential_sources", "tags")
def _find_kdash_index() -> Path:
    """The page lives at kdash/index.html beside the cosmos/ package in the repo
    layout, or flat beside this module (kdash_index.html) in a spike checkout.
    A hard-coded single layout is the class of bug that succeeds into the wrong
    universe - resolve, in order, and fall back to the repo-canonical path."""
    here = Path(__file__).resolve().parent
    for cand in (here / "kdash" / "index.html",
                 here.parent / "kdash" / "index.html",
                 here / "kdash_index.html"):
        if cand.is_file():
            return cand
    return here.parent / "kdash" / "index.html"


KDASH_INDEX = _find_kdash_index()

# Any remote script/link is a CDN for this page. The dashboard ships its own CSS/JS.
_REMOTE_RE = re.compile(r"^(https?:)?//", re.I)


class KdashError(RuntimeError):
    """kind in {UNKNOWN_KIND, BAD_ENTRY, MISSING_PANEL, CDN_FORBIDDEN,
    BAD_PAGE, UNAUTHORIZED, NOT_FOUND, UNREACHABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def makers_path(kind: str) -> str:
    """Build GET /api/v1/makers?kind=... Unknown kind REFUSES here so a typo
    never leaves the client as an empty list."""
    if not isinstance(kind, str) or not kind.strip():
        raise KdashError("UNKNOWN_KIND",
                         f"{kind!r} is not a CREATE kind - want one of {list(CREATE_KINDS)}")
    k = kind.strip().upper()
    if k not in CREATE_KINDS:
        raise KdashError("UNKNOWN_KIND", f"{kind!r} not in {list(CREATE_KINDS)}")
    return "/api/v1/makers?" + urlencode({"kind": k})


def _as_str_list(value, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise KdashError("BAD_ENTRY",
                         f"{field} must be a list of strings, got {type(value).__name__}")
    return list(value)


def card_from_maker(entry: dict) -> dict:
    """Normalize one maker into a card. Missing fields are BAD_ENTRY; an
    unknown kind is UNKNOWN_KIND (the card set is the same closed set as the
    buttons)."""
    if not isinstance(entry, dict):
        raise KdashError("BAD_ENTRY",
                         f"maker is not an object, got {type(entry).__name__}")
    missing = [f for f in REQUIRED_CARD_FIELDS if f not in entry]
    if missing:
        raise KdashError("BAD_ENTRY", f"missing field(s): {', '.join(missing)}")
    out = {}
    for field in ("id", "kind", "location", "function", "access"):
        val = entry[field]
        if not isinstance(val, str) or not val.strip():
            raise KdashError("BAD_ENTRY",
                             f"{field} must be a non-empty string, got {val!r}")
        out[field] = val.strip()
    if out["kind"] not in CREATE_KINDS:
        raise KdashError("UNKNOWN_KIND",
                         f"{out['kind']!r} not in {list(CREATE_KINDS)}")
    out["potential_sources"] = _as_str_list(entry["potential_sources"],
                                            "potential_sources")
    out["tags"] = _as_str_list(entry["tags"], "tags")
    return out


def cards_from_payload(body: dict) -> list[dict]:
    """Turn a GET /makers body into cards. An empty makers list is valid (none
    of that kind exist). A missing or non-list makers field is BAD_ENTRY."""
    if not isinstance(body, dict):
        raise KdashError("BAD_ENTRY",
                         f"payload is not an object, got {type(body).__name__}")
    rows = body.get("makers")
    if rows is None:
        raise KdashError("BAD_ENTRY", "payload has no makers array")
    if not isinstance(rows, list):
        raise KdashError("BAD_ENTRY",
                         f"makers is not an array, got {type(rows).__name__}")
    return [card_from_maker(r) for r in rows]


def invoke_instructions(maker: dict) -> list[tuple[str, str]]:
    """How to invoke this maker. The page shows these under 'open maker'.
    where / do / how / sources - access is the invoke path, not a capability
    claim that the place is reachable today."""
    rec = card_from_maker(maker)
    sources = rec["potential_sources"]
    src = " · ".join(sources) if sources else "—"
    return [
        ("where", rec["location"]),
        ("do", rec["function"]),
        ("how", rec["access"]),
        ("sources", src),
    ]


def parse_makers_response(code: int, body: dict) -> list[dict]:
    """Map HTTP+JSON to cards or a typed refusal. The page surfaces
    body.error as the panel kind (UNKNOWN_KIND, UNAUTHORIZED, NOT_FOUND)."""
    if code == 200:
        return cards_from_payload(body)
    if not isinstance(body, dict):
        raise KdashError("UNREACHABLE", f"HTTP {code} with a non-object body")
    kind = str(body.get("error") or f"HTTP_{code}")
    detail = str(body.get("detail") or f"HTTP {code}")
    if kind not in ("UNKNOWN_KIND", "UNAUTHORIZED", "NOT_FOUND", "BAD_ENTRY",
                    "UNREACHABLE"):
        # Keep the server's kind if it is one of ours; otherwise wrap.
        if code == 401:
            kind = "UNAUTHORIZED"
        elif code == 404:
            kind = "NOT_FOUND"
        elif code == 400 and "KIND" in str(body.get("error", "")).upper():
            kind = "UNKNOWN_KIND"
        else:
            kind = "UNREACHABLE"
    raise KdashError(kind, detail)


def fetch_makers(base: str, token: str, kind: str, timeout: float = 8.0) -> list[dict]:
    """Pure API client: GET {base}/api/v1/makers?kind=... Bearer optional.
    Local unknown-kind REFUSES before the wire. Transport failure is
    UNREACHABLE."""
    path = makers_path(kind)
    url = str(base).rstrip("/") + path
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            code = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        code = e.code
    except urllib.error.URLError as e:
        raise KdashError("UNREACHABLE", f"{url}: {e}") from e
    try:
        body = json.loads(raw) if raw else {}
    except ValueError as e:
        raise KdashError("BAD_ENTRY", f"response is not JSON: {e}") from e
    return parse_makers_response(code, body)


class _Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.data_kinds: list[str] = []
        self.remote: list[str] = []
        self._btn_kind: Optional[str] = None
        self.kind_labels: dict[str, str] = {}
        self._capture = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = {k: (v or "") for k, v in attrs}
        if d.get("id"):
            self.ids.add(d["id"])
        if tag == "button" and d.get("data-kind"):
            self.data_kinds.append(d["data-kind"])
            self._btn_kind = d["data-kind"]
            self._capture = True
            self._buf = []
        src = d.get("src") or ""
        href = d.get("href") or ""
        if tag == "script" and src and _REMOTE_RE.match(src):
            self.remote.append(src)
        if tag == "link" and href and _REMOTE_RE.match(href):
            self.remote.append(href)

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "button" and self._capture and self._btn_kind:
            self.kind_labels[self._btn_kind] = "".join(self._buf).strip()
            self._capture = False
            self._btn_kind = None


def inspect_page(html: str) -> dict:
    """Verify a KDash HTML document carries the CREATE panel contract.
    Missing structure is MISSING_PANEL; a remote script/link is CDN_FORBIDDEN;
    a document that is not HTML we can parse is BAD_PAGE."""
    if not isinstance(html, str) or "<" not in html:
        raise KdashError("BAD_PAGE", "not an HTML document")
    p = _Page()
    try:
        p.feed(html)
        p.close()
    except Exception as e:                                            # noqa: BLE001
        raise KdashError("BAD_PAGE", f"unparseable HTML: {e}") from e
    if p.remote:
        raise KdashError("CDN_FORBIDDEN",
                         "remote script/link is a CDN - KDash ships its own "
                         f"CSS/JS, found {p.remote!r}")
    need = ("panel-create", "age-create", "bd-create", "create-kinds",
            "create-cards")
    missing = [i for i in need if i not in p.ids]
    if missing:
        raise KdashError("MISSING_PANEL",
                         f"CREATE panel missing id(s): {', '.join(missing)}")
    if "/api/v1/makers?kind=" not in html:
        raise KdashError("MISSING_PANEL",
                         "CREATE client does not call GET /api/v1/makers?kind=")
    if "open maker" not in html:
        raise KdashError("MISSING_PANEL",
                         "CREATE cards have no 'open maker' action")
    if "create:" not in html and 'create :' not in html:
        # per-panel age lives in the panels{} map
        if re.search(r"\bcreate\s*:", html) is None:
            raise KdashError("MISSING_PANEL",
                             "CREATE is not in the per-panel age map")
    for kind, label in KIND_LABELS:
        if kind not in p.data_kinds:
            raise KdashError("MISSING_PANEL",
                             f"CREATE is missing the {label} button (data-kind={kind})")
        got = p.kind_labels.get(kind, "")
        if got != label:
            raise KdashError("MISSING_PANEL",
                             f"button {kind} is labeled {got!r}, want {label!r}")
    for field in ("where", "do", "how", "sources"):
        if f"<dt>{field}</dt>" not in html and f"'<dt>{field}</dt>'" not in html:
            # JS builds these with string concat; accept either form
            if f'"{field}"' not in html and f"'{field}'" not in html:
                raise KdashError("MISSING_PANEL",
                                 f"invoke instructions missing {field!r}")
    return {
        "ids": sorted(p.ids),
        "kinds": list(p.data_kinds),
        "labels": dict(p.kind_labels),
    }


def inspect_kdash_file(path: Optional[str | Path] = None) -> dict:
    """Read kdash/index.html from disk and inspect it. Unreadable is BAD_PAGE."""
    p = Path(path) if path is not None else KDASH_INDEX
    try:
        html = p.read_text(encoding="utf-8")
    except OSError as e:
        raise KdashError("BAD_PAGE", f"{p}: {e}") from e
    return inspect_page(html)