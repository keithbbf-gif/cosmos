#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_itc - THE ITC RESOURCE BROKER (F5 builder).

THE PROBLEM THIS CLOSES: chat apps lose resources. A file uploaded three turns ago,
a paper behind an index nobody can list, an R2 bucket that serves NO directory -
each is reachable only through knowledge that lives in one conversation and dies
with it. COSMOS is the durable side of that channel: it fetches and indexes the
public object index (GrokDex.csv - the CSV IS the directory; the bucket lists
nothing by construction) plus the LOCAL corpus, so a phone/voice client can search
and resolve resources THROUGH COSMOS instead of through a chat turn.

PRINCIPLES CARRIED (load-bearing, not decoration):
  * PROVENANCE, MEASURED NOT ASSUMED - every refresh appends ITC_REFRESHED
    {url, fetch_epoch, content_hash (sha256 of the raw CSV text), row_count} to
    the signed ledger, and EVERY search hit carries "index_hash": the hash of the
    exact index version it came from. A result that cannot name its index version
    is an assumed result.
  * INJECTED FETCHER - ITC(ledger, fetcher=callable(url)->str). Production passes
    a real https fetcher; tests pass a fake. This module NEVER opens the network
    itself, so no code path a test exercises can silently depend on reachability.
    A fetcher that raises (or was never provided) is UNREACHABLE - the failure is
    reported, never papered over with a fabricated success, and NOTHING is
    appended to the ledger for a fetch that did not happen.
  * TYPED ERRORS ONLY - ItcError.kind in {UNREACHABLE, STALE, NOT_FOUND,
    BAD_INDEX}. STALE means "you asked the index a question before it existed
    (or after max_age)" - an empty answer there would be a silent lie.
  * DISSEMINATION IS THE GOAL (project canon) - the ITC index and the user's own
    corpus are brokered freely: no access caveats, no copyright friction, no
    paywall warnings on metadata. The one hard line kept: this module indexes the
    object INDEX and LOCAL paths only - it never scrapes paywalled full text.
  * NEVER DELETE - the corpus registry only accumulates; the ledger only appends.

STALENESS (stated, as required): search()/get() accept max_age (seconds). When
given, the last refresh's fetch_epoch is checked against clock(); an index older
than max_age raises STALE instead of answering from a version the caller said is
too old. With max_age=None (default) any refreshed index answers, but the
index_hash on every hit still lets the caller audit WHICH version answered.

Depends on cosmos_ledger + stdlib only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import time
from typing import Callable, Optional

DEFAULT_INDEX_URL = "https://ai.dchambers.com/GrokDex.csv"

# The documented GrokDex.csv shape. Extra columns are tolerated (carried through);
# a missing required column is BAD_INDEX - a directory missing its keys is not a
# directory with fewer features, it is not the directory.
REQUIRED_COLUMNS = ("object_key", "url", "area", "type", "size_bytes", "descriptor")

# Index-derived fields are UNTRUSTED DATA (2026-08-23 final hardening): the CSV
# is fetched from a public URL, and its cell contents flow into voice replies
# and UIs. Every field is sanitized on parse - control characters stripped,
# length capped - so a hostile or corrupted index cannot inject terminal
# escapes, fake reply lines, or megabyte cells into anything downstream.
# Results remain DATA: nothing in a row is ever interpreted as an instruction.
FIELD_MAX = 500           # chars per field after sanitization

EV_REFRESHED = "ITC_REFRESHED"
EV_CORPUS = "CORPUS_REGISTERED"


def _sanitize_field(v) -> str:
    """One field, made safe to embed: control chars (C0 + DEL) stripped,
    length capped at FIELD_MAX. The value stays data; it just stops being able
    to pretend it is anything else."""
    s = "".join(ch for ch in str(v) if ch >= " " and ch != "\x7f")
    return s[:FIELD_MAX]


class ItcError(RuntimeError):
    """kind in {UNREACHABLE, STALE, NOT_FOUND, BAD_INDEX}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _norm_path(p: str) -> str:
    """One comparable spelling per path: forward slashes, no trailing slash.
    Case is PRESERVED in the stored record (the path is data); matching is
    case-insensitive separately, so Windows spellings still find themselves."""
    s = str(p).replace("\\", "/")
    while s.endswith("/") and len(s) > 1:
        s = s[:-1]
    return s


class ITC:
    """The resource broker. All durable facts go through the injected Ledger;
    the in-memory row cache is a disposable projection of the last refresh."""

    def __init__(self, ledger, fetcher: Optional[Callable[[str], str]] = None,
                 clock=time.time):
        self._ledger = ledger
        self._fetcher = fetcher
        self._clock = clock
        # projections (rebuildable; the ledger is the authority)
        self._rows: dict[str, dict] = {}      # object_key -> row dict
        self._index_hash: Optional[str] = None
        self._fetch_epoch: Optional[float] = None
        self._row_count: int = 0
        self._index_url: Optional[str] = None
        self._corpus: list[str] = []          # normalized registered paths, in order
        # CONSTRUCTION-TIME PROVENANCE (2026-08-23): replay the ledger NOW so a
        # torn/forged chain refuses at composition, and rebuild the last-refresh
        # record + corpus. The ROWS of a prior refresh are deliberately NOT
        # rebuilt - the ledger holds the refresh's hash, not the CSV body, so a
        # new process cannot reproduce them; search()/get() therefore stay
        # STALE until a refresh in THIS process. That keeps the invariant that
        # index_hash on every hit equals the content_hash of the refresh whose
        # rows are actually in memory - this instance never claims a hash it
        # cannot reproduce.
        self.state()                          # verifies the chain; raises if torn

        def _fold_corpus(paths, rec):
            if rec.get("event") == EV_CORPUS:
                for p in rec.get("payload", {}).get("paths", []):
                    if isinstance(p, str) and p not in paths:
                        paths.append(p)
            return paths
        # corpus registrations rebuilt in ledger order - a reconnecting process
        # can search_corpus without re-registering anything.
        self._corpus = self._ledger.project(_fold_corpus, [])

    # ---------------- refresh ----------------
    def refresh(self, url: str = DEFAULT_INDEX_URL) -> dict:
        """Fetch the index via the INJECTED fetcher, parse, hash, ledger, cache.

        Order matters and is deliberate: fetch -> parse -> ledger -> cache.
        UNREACHABLE and BAD_INDEX both happen BEFORE the append, so the ledger
        never records a refresh that did not truthfully complete - no fabricated
        success, ever. Returns {row_count, content_hash, fetch_epoch}."""
        if self._fetcher is None:
            raise ItcError("UNREACHABLE",
                           f"no fetcher injected - cannot reach {url}; refusing to "
                           f"fabricate an index")
        try:
            text = self._fetcher(url)
        except Exception as e:                                        # noqa: BLE001
            raise ItcError("UNREACHABLE",
                           f"fetcher failed for {url}: {type(e).__name__}: {e}") from e
        if not isinstance(text, str):
            raise ItcError("UNREACHABLE",
                           f"fetcher for {url} returned {type(text).__name__}, "
                           f"not str - not a CSV body")

        rows = self._parse(text, url)

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        fetch_epoch = float(self._clock())
        row_count = len(rows)

        # PROVENANCE: the measured facts of this refresh, signed into the chain.
        self._ledger.append(EV_REFRESHED, {
            "url": url,
            "fetch_epoch": fetch_epoch,
            "content_hash": content_hash,
            "row_count": row_count,
        })

        # cache only AFTER the ledger accepted the record - a refresh the ledger
        # refused is a refresh that did not happen.
        self._rows = {r["object_key"]: r for r in rows}
        self._index_hash = content_hash
        self._fetch_epoch = fetch_epoch
        self._row_count = row_count
        self._index_url = url
        return {"row_count": row_count, "content_hash": content_hash,
                "fetch_epoch": fetch_epoch}

    def _parse(self, text: str, url: str) -> list[dict]:
        """CSV -> list of row dicts. Missing required column -> BAD_INDEX.
        Extra columns are carried through SANITIZED like every other field
        (control chars stripped, FIELD_MAX cap - see _sanitize_field: index
        cells are untrusted data headed for replies and UIs). Rows with an
        empty object_key are skipped (a directory entry with no key resolves
        nothing). A DUPLICATE object_key is BAD_INDEX: two rows claiming one
        key means get() would silently answer with whichever row won the dict,
        and row_count would overstate the resolvable set - the index is not the
        directory it claims to be, so it is refused whole."""
        try:
            reader = csv.DictReader(io.StringIO(text))
            fields = reader.fieldnames
        except csv.Error as e:
            raise ItcError("BAD_INDEX", f"{url}: CSV does not parse: {e}") from e
        if not fields:
            raise ItcError("BAD_INDEX", f"{url}: empty document - no header row")
        missing = [c for c in REQUIRED_COLUMNS if c not in fields]
        if missing:
            raise ItcError("BAD_INDEX",
                           f"{url}: header missing required column(s) "
                           f"{missing} - got {list(fields)}")
        rows: list[dict] = []
        seen: set[str] = set()
        try:
            for rec in reader:
                key = _sanitize_field(rec.get("object_key") or "").strip()
                if not key:
                    continue
                if key in seen:
                    raise ItcError(
                        "BAD_INDEX",
                        f"{url}: duplicate object_key {key!r} - one key must "
                        f"resolve one object; refusing the whole index rather "
                        f"than letting a dict decide which row wins")
                seen.add(key)
                row = {k: _sanitize_field(v if v is not None else "")
                       for k, v in rec.items() if k is not None}
                row["object_key"] = key
                rows.append(row)
        except csv.Error as e:
            raise ItcError("BAD_INDEX", f"{url}: CSV body torn mid-read: {e}") from e
        return rows

    # ---------------- query ----------------
    def _require_fresh(self, max_age: Optional[float]) -> None:
        if self._index_hash is None:
            raise ItcError("STALE",
                           "no index loaded - refresh() has never succeeded this "
                           "session; refusing to answer from nothing (an empty "
                           "result would be a silent lie)")
        if max_age is not None:
            age = float(self._clock()) - float(self._fetch_epoch or 0.0)
            if age > max_age:
                raise ItcError("STALE",
                               f"index is {age:.0f}s old > max_age {max_age:.0f}s "
                               f"- refresh() before trusting this answer")

    def search(self, query: str, area: Optional[str] = None,
               type: Optional[str] = None, limit: int = 50,   # noqa: A002
               max_age: Optional[float] = None) -> list[dict]:
        """Case-insensitive substring match of query against object_key AND
        descriptor; optional EXACT filters on area/type. Every hit carries
        index_hash (provenance) and source='itc'. Never refreshed -> STALE."""
        self._require_fresh(max_age)
        q = (query or "").lower()
        out: list[dict] = []
        for row in self._rows.values():
            if q and q not in row.get("object_key", "").lower() \
                    and q not in row.get("descriptor", "").lower():
                continue
            if area is not None and row.get("area") != area:
                continue
            if type is not None and row.get("type") != type:
                continue
            hit = dict(row)
            hit["index_hash"] = self._index_hash
            hit["source"] = "itc"
            out.append(hit)
            if len(out) >= limit:
                break
        return out

    def get(self, object_key: str, max_age: Optional[float] = None) -> dict:
        """Resolve one object_key to its full row (incl. url) - how a client
        turns a hit into something fetchable. Unknown key -> NOT_FOUND.
        (Never refreshed -> STALE, same as search: 'not found' would claim we
        looked, and we had nothing to look in.)"""
        self._require_fresh(max_age)
        row = self._rows.get(object_key)
        if row is None:
            raise ItcError("NOT_FOUND",
                           f"object_key {object_key!r} not in index version "
                           f"{self._index_hash[:12]} ({self._row_count} rows)")
        out = dict(row)
        out["index_hash"] = self._index_hash
        out["source"] = "itc"
        return out

    # ---------------- local corpus ----------------
    def register_corpus(self, paths: list[str]) -> dict:
        """Record local corpus paths (ledger: CORPUS_REGISTERED) and index them
        for path-substring search. Metadata only - file BYTES are never read
        here, so registration works on any path shape without touching disk.
        Registration only ACCUMULATES (never delete): re-registering a path is
        idempotent in the projection, and the ledger keeps every registration."""
        normed = [_norm_path(p) for p in paths]
        self._ledger.append(EV_CORPUS, {
            "paths": normed,
            "count": len(normed),
            "epoch": float(self._clock()),
        })
        for p in normed:
            if p not in self._corpus:
                self._corpus.append(p)
        return {"registered": len(normed), "corpus_size": len(self._corpus)}

    def search_corpus(self, query: str, limit: int = 50) -> list[dict]:
        """Case-insensitive substring match against the registered path (filename
        included - it is the path's tail). Hits are marked source='corpus' so a
        client can always tell a local file from an ITC object. An empty corpus
        returns [] - unlike ITC-STALE, an unregistered corpus is a legitimately
        empty set, not a missing index."""
        q = (query or "").lower()
        out: list[dict] = []
        for p in self._corpus:
            if q and q not in p.lower():
                continue
            name = p.rsplit("/", 1)[-1]
            out.append({"path": p, "name": name, "source": "corpus"})
            if len(out) >= limit:
                break
        return out

    # ---------------- projections ----------------
    def state(self) -> dict:
        """The last refresh + corpus census, REBUILT FROM THE LEDGER (not from
        this instance's memory) - the projection any new process would build."""
        def fold(st, rec):
            if rec.get("event") == EV_REFRESHED:
                p = rec.get("payload", {})
                st["last_refresh"] = {
                    "url": p.get("url"),
                    "fetch_epoch": p.get("fetch_epoch"),
                    "content_hash": p.get("content_hash"),
                    "row_count": p.get("row_count"),
                }
                st["refresh_count"] += 1
            elif rec.get("event") == EV_CORPUS:
                for p in rec.get("payload", {}).get("paths", []):
                    st["corpus_paths"].add(p)
            return st
        st = self._ledger.project(fold, {
            "last_refresh": None, "refresh_count": 0, "corpus_paths": set(),
        })
        return {
            "last_refresh": st["last_refresh"],
            "refresh_count": st["refresh_count"],
            "corpus_size": len(st["corpus_paths"]),
        }

    def report(self) -> str:
        """One human line - when, hash, row_count - from the ledger projection."""
        st = self.state()
        lr = st["last_refresh"]
        if lr is None:
            return ("ITC: no refresh on record - index STALE by definition; "
                    f"corpus={st['corpus_size']} paths")
        when = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(lr["fetch_epoch"]))
        return (f"ITC: index {lr['content_hash'][:12]} - {lr['row_count']} rows, "
                f"fetched {when} from {lr['url']} "
                f"({st['refresh_count']} refresh(es)); "
                f"corpus={st['corpus_size']} paths")
