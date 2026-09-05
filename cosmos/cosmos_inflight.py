#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_inflight.py -- OWNED in-flight state, with leases that expire.

Why this exists (scar 2026-08-30): the motif driver decided "is this slug already
moving?" by DERIVING it -- scanning queue filenames, 343 unpruned manifests, and
regex-scraping a human-readable COLLECTOR.md summary. Every one of those sources
records COMPLETED work and nothing ever removed a name, so the set was append-only
by construction: cdeck and gbridge blocked themselves with their own stage-6 result
files, and each later success would have foreclosed its own slug the same way. All
ten deliverables were reported inflight while the queue was empty.

The lesson is not "filter receipts better". It is that in-flight is STATE and must
be OWNED, not inferred from artifacts that outlive the work they describe.

Two properties do the work:

  1. EXPLICIT. A claim is written when work starts and released when it ends.
     Nothing is guessed from a filename.
  2. EXPIRING. Every lease carries a TTL. A worker that dies without releasing
     stops blocking on its own, without a human pruning anything. This is the
     property that makes a permanent wedge structurally impossible -- the worst
     case is a stale lease for `ttl_s`, never forever.

Append-only JSONL, matching the ledger idiom already used across COSMOS
(authority.jsonl, sched_ledger.jsonl). State is a fold over events, so the file is
an audit trail as well as a store, and never-delete holds: a release is a new
event, never an edit or a truncation.

Typed refusals only -- InflightError carries a `kind`, never a bare string.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

SCHEMA = "cosmos-inflight/1"
DEFAULT_TTL_S = 1800.0


class InflightError(Exception):
    """Typed refusal. `kind` is the machine-readable reason."""

    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}" if detail else f"[{kind}]")


class Inflight:
    """Append-only lease store. Tokens are opaque; the caller owns their meaning."""

    def __init__(self, path, ttl_s: float = DEFAULT_TTL_S, clock=time.time) -> None:
        self.path = Path(path)
        self.ttl_s = float(ttl_s)
        self._clock = clock

    # ---------- write ----------

    def _append(self, rec: dict) -> dict:
        """One line, one event. O_APPEND so concurrent workers cannot interleave."""
        rec = {"schema": SCHEMA, "at": self._clock(), **rec}
        line = json.dumps(rec, sort_keys=True) + "\n"
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                os.write(fd, line.encode("utf-8"))
            finally:
                os.close(fd)
        except OSError as e:
            raise InflightError("WRITE_FAILED", f"{self.path}: {e}") from e
        return rec

    def claim(self, token: str, *, slug: str = "", stage: int | None = None,
              worker: str = "", lane: str = "", job_file: str = "",
              ttl_s: float | None = None) -> dict:
        """Record that `token` is now in flight. Re-claiming refreshes the lease."""
        if not token:
            raise InflightError("NO_TOKEN", "claim requires a non-empty token")
        return self._append({
            "event": "CLAIM", "token": token, "slug": slug, "stage": stage,
            "worker": worker, "lane": lane, "job_file": job_file,
            "ttl_s": float(ttl_s if ttl_s is not None else self.ttl_s),
        })

    def release(self, token: str, *, outcome: str = "done",
                detail: str = "") -> dict:
        """Record that `token` is finished. Releasing an unknown token is not an
        error -- a result can legitimately outlive the process that claimed it."""
        if not token:
            raise InflightError("NO_TOKEN", "release requires a non-empty token")
        return self._append({"event": "RELEASE", "token": token,
                             "outcome": outcome, "detail": detail})

    # ---------- read ----------

    def _events(self) -> list[dict]:
        """A corrupt LINE is skipped, never fatal; a corrupt FILE raises. Partial
        readability must not silently look like an empty store -- that would read
        as 'nothing is running' and green-light a duplicate dispatch."""
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        except OSError as e:
            raise InflightError("READ_FAILED", f"{self.path}: {e}") from e
        out = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and rec.get("token"):
                out.append(rec)
        return out

    def state(self) -> dict[str, dict]:
        """Fold events into per-token latest status. Includes expired + released."""
        cur: dict[str, dict] = {}
        for rec in self._events():
            cur[rec["token"]] = rec
        return cur

    def active(self, now: float | None = None) -> dict[str, dict]:
        """Tokens genuinely in flight: claimed, not released, not expired."""
        t = self._clock() if now is None else now
        out = {}
        for token, rec in self.state().items():
            if rec.get("event") != "CLAIM":
                continue
            ttl = float(rec.get("ttl_s") or self.ttl_s)
            if t - float(rec.get("at") or 0.0) >= ttl:
                continue                      # expired: it stops blocking itself
            out[token] = rec
        return out

    def expired(self, now: float | None = None) -> list[dict]:
        """Claims that aged out without a release -- a worker died. Visible, not
        silently swallowed: an expiring lease is a fact worth reporting."""
        t = self._clock() if now is None else now
        out = []
        for rec in self.state().values():
            if rec.get("event") != "CLAIM":
                continue
            ttl = float(rec.get("ttl_s") or self.ttl_s)
            if t - float(rec.get("at") or 0.0) >= ttl:
                out.append(rec)
        return out

    def tokens(self, now: float | None = None) -> set[str]:
        """Lowercased active tokens, shaped for the driver's name haystack."""
        return {t.lower() for t in self.active(now)}


def selftest() -> int:
    """Bind every claim to a real emitted value. rc=0 is not the proof; the
    printed live_value is."""
    import tempfile
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:                                        # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_inflight_"))
    now = [1000.0]
    f = Inflight(td / "inflight.jsonl", ttl_s=100.0, clock=lambda: now[0])

    check("empty store has no active tokens", lambda: f.active() == {})
    f.claim("motif_cdeck_s6", slug="cdeck", stage=6, worker="g46")
    check("claim shows active", lambda: "motif_cdeck_s6" in f.active())
    check("claim carries its slug",
          lambda: f.active()["motif_cdeck_s6"]["slug"] == "cdeck")

    f.release("motif_cdeck_s6", outcome="done")
    check("release clears active", lambda: f.active() == {})
    check("release is append-only, not an edit",
          lambda: len(f._events()) == 2)

    # THE property: a worker that dies without releasing stops blocking itself.
    f.claim("motif_gbridge_s6", slug="gbridge", stage=6, worker="dead-worker")
    check("claim active before TTL", lambda: "motif_gbridge_s6" in f.active())
    now[0] += 101.0
    check("expired lease is NOT active (no permanent wedge)",
          lambda: f.active() == {})
    check("expired lease is visible, not silently dropped",
          lambda: [r["token"] for r in f.expired()] == ["motif_gbridge_s6"])

    # A receipt-shaped name can never leak in: only explicit claims count.
    check("nothing is inferred from artifacts",
          lambda: "motif_cdeck_s6_result.json" not in f.tokens())

    now[0] += 10.0
    f.claim("motif_cvm_s5", slug="cvm", stage=5)
    check("re-claim after expiry works", lambda: "motif_cvm_s5" in f.tokens())
    check("corrupt line is skipped, not fatal",
          lambda: (f.path.open("a", encoding="utf-8").write("{not json\n"),
                   "motif_cvm_s5" in f.tokens())[1])

    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [r for r in results if not r[1]]
    live = {"active_now": sorted(f.tokens()),
            "expired_seen": [r["token"] for r in f.expired()],
            "events_on_disk": len(f._events())}
    print("live_value: " + json.dumps(live, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(selftest())
