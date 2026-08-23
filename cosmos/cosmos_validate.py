#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_validate - VERIFIED I/O + THE RETURN-VALIDATION SUBSYSTEM (F5 builder).
Scar R1: bytes-declared-vs-consumed on critical reads (the mount's silent-corruption
signature). Scar R4: DOIs/quotes/paths machine-checked BEFORE a return is used - five
of seven citations from one rail were once fabricated; a fabricated quotation was once
attributed to a node. Validation is a GATE wired into acceptance, not a tool someone
remembers.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Callable, Optional

from cosmos_paths import extended
from cosmos_ledger import Ledger


class ValidateError(RuntimeError):
    """kind in {SHORT_READ, HASH_MISMATCH, FAILED_VALIDATION, NO_VALIDATOR,
    UNVALIDATED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# ---------------- verified I/O ----------------
def read_verified(path: Path, expect_len: Optional[int] = None,
                  expect_sha: Optional[str] = None) -> bytes:
    """Read with the declared-vs-consumed check. When a manifest declares length/hash,
    a disagreement is SHORT_READ/HASH_MISMATCH - never returned as content. This is the
    thirteen-mount-lies rule as a primitive."""
    with open(extended(path), "rb") as fh:
        data = fh.read()
        more = fh.read(1)                    # a read that stops early lies quietly
        while more:
            data += more
            more = fh.read(1 << 16)
    if expect_len is not None and len(data) != expect_len:
        raise ValidateError("SHORT_READ",
                            f"{path}: consumed {len(data)} bytes, declared {expect_len} "
                            f"- the mount's signature; refusing to hand back a lie")
    if expect_sha is not None:
        got = hashlib.sha256(data).hexdigest()
        if got != expect_sha:
            raise ValidateError("HASH_MISMATCH", f"{path}: sha {got[:12]} != declared "
                                                 f"{expect_sha[:12]}")
    return data


def write_declared(path: Path, content: bytes) -> dict:
    """Write + return the declaration (len, sha) the reader will verify against."""
    with open(extended(path), "wb") as fh:
        fh.write(content)
    return {"path": str(path), "len": len(content),
            "sha": hashlib.sha256(content).hexdigest()}


# ---------------- validators ----------------
_DOI_RX = re.compile(r"^10\.\d{4,9}/\S+$")


def v_path_exists(claim: dict) -> tuple[bool, str]:
    """A path a node CLAIMS exists is checked against disk - never believed."""
    p = Path(claim["path"])
    if not p.exists():
        return False, f"claimed path does not exist: {p}"
    return True, "on disk"


def v_doi_shape(claim: dict) -> tuple[bool, str]:
    """Offline shape gate. Shape-valid is NOT existence - Crossref is the authority and
    is a pluggable resolver (network); shape failure is a certain fabrication signal,
    shape success is only 'eligible for the Crossref check'."""
    doi = claim.get("doi", "")
    if not _DOI_RX.match(doi):
        return False, f"not a DOI shape: {doi!r}"
    return True, "shape ok - EXISTENCE UNPROVEN until the Crossref resolver runs"


def v_quote_in_source(claim: dict) -> tuple[bool, str]:
    """A quotation attributed to a source must appear IN that source (S-55: Cowork once
    fabricated a quotation and attributed it to a node). Whitespace-normalized
    containment."""
    src = Path(claim["source_path"])
    if not src.exists():
        return False, f"quoted source missing: {src}"
    body = " ".join(src.read_text(encoding="utf-8", errors="replace").split())
    quote = " ".join(str(claim["quote"]).split())
    if quote not in body:
        return False, f"quotation NOT FOUND in {src.name}: {quote[:80]!r}"
    return True, "verbatim in source"


class ReturnValidator:
    """The gate. accept() runs every validator the return names; failures are
    LEDGERED and the return is REFUSED - it never touches a projection."""

    BUILTIN: dict[str, Callable[[dict], tuple[bool, str]]] = {
        "path_exists": v_path_exists,
        "doi_shape": v_doi_shape,
        "quote_in_source": v_quote_in_source,
    }

    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self._extra: dict[str, Callable[[dict], tuple[bool, str]]] = {}

    def register(self, name: str, fn: Callable[[dict], tuple[bool, str]]) -> None:
        self._extra[name] = fn

    def accept(self, return_id: str, claims: list[dict]) -> dict:
        """claims: [{validator: name, ...args}]. ALL must pass or the whole return is
        REFUSED - a return with one fabricated citation is a fabricating return.
        An empty claims list is UNVALIDATED: a return that named no check never
        passed a gate, so it is refused rather than vacuously accepted."""
        if not claims:
            self.ledger.append("RETURN_REFUSED",
                               {"rid": return_id, "reason": "UNVALIDATED"})
            raise ValidateError(
                "UNVALIDATED",
                f"{return_id}: no validators named - an unvalidated return is refused")
        results = []
        for c in claims:
            name = c.get("validator", "")
            fn = self._extra.get(name) or self.BUILTIN.get(name)
            if fn is None:
                self.ledger.append("RETURN_REFUSED",
                                   {"rid": return_id, "reason": f"NO_VALIDATOR {name}"})
                raise ValidateError("NO_VALIDATOR", name)
            try:
                ok, detail = fn(c)
            except Exception as e:                                    # noqa: BLE001
                ok, detail = False, f"validator raised {type(e).__name__}: {e}"
            results.append({"validator": name, "ok": ok, "detail": str(detail)[:200]})
        bad = [r for r in results if not r["ok"]]
        if bad:
            self.ledger.append("RETURN_REFUSED", {"rid": return_id, "failures": bad})
            raise ValidateError("FAILED_VALIDATION",
                                f"{return_id}: {len(bad)} of {len(results)} failed - "
                                f"{bad[0]['detail']}")
        self.ledger.append("RETURN_VALIDATED", {"rid": return_id,
                                                "checks": len(results)})
        return {"rid": return_id, "checks": results}