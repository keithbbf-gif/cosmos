#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_surfaces - STORAGE SURFACES as first-class registered resources, MEASURED not
assumed (F5 builder). The incumbent knew ITC/R2, GDX/Google Drive, ODX/OneDrive and the
local disks only as prose in a control document; here every surface is a registered
entity, and a backup target earns the name by answering three questions with a dated
measurement, never with a label.

Registry-reality reconciliation (same authority pattern as cosmos_registry): register()
records a CLAIM; only measure() records a MEASUREMENT; qualification is a function of the
last measurement plus the claim, and it is re-decided each time it is asked.

SCARS THIS CLOSES:
  * "publishing is not backup" - the R2 nightly ran green for weeks and saved seven of the
    eight directories the sweep took ZERO times, because "published" got read as "backed
    up." A PUBLISH surface is registered as a PUBLISH surface; it never silently answers a
    backup question. Off-machine reach is the test, and a mirror of the readable half is
    not a backup of the irreplaceable half.
  * "a labelled NAS is not necessarily a reachable one" - G: was labelled NAS1 and was in
    fact a SABRENT USB enclosure on this same box (Get-PhysicalDisk: BusType=USB), later
    in a drawer. The label claimed LAN; the hardware was LOCAL and then gone. A surface is
    qualified by what a probe MEASURES today, never by the sticker on it.
  * "off-machine or it does not count" - one copy on one machine is zero; two aging drives
    in one box on one PSU is one surge from nothing. mesh-addressability (LAN/CLOUD) is a
    hard question, not a nicety - a LOCAL surface cannot qualify as a backup target while
    require_offmachine holds.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Callable, Optional

from cosmos_ledger import Ledger

# cDeck Surfaces pane canon rows (GET /api/v1/surfaces ids, upper case).
CANON_SURFACE_IDS = ("ROLD", "ITC", "GDX", "ODX", "TB1")

_CANON_CLAIMS: dict[str, tuple[str, str, str]] = {
    "ROLD": ("LOCAL", "ARCHIVE", "rold://operator/ROLD"),
    "ITC": ("PUBLISH", "PUBLISH", "https://ai.dchambers.com"),
    "GDX": ("CLOUD", "BACKUP", "gdrive://BTS_SGH_Handoff"),
    "ODX": ("CLOUD", "BACKUP", "onedrive://operator/ODX"),
    "TB1": ("LOCAL", "ARCHIVE", "local://TB1"),
}

_BACKUP_TARGETS_NAME = "backup_targets.json"
_BUCKET_WORKER_NAMES = ("bucket_worker.json", "node_bucket_worker.json")

# A surface's PHYSICAL/reach class - where the bytes actually live and whether reaching
# them leaves this machine. LOCAL never leaves; LAN/CLOUD do; PUBLISH is a read mirror.
SURFACE_KINDS = {"LOCAL", "LAN", "CLOUD", "PUBLISH"}
# A surface's INTENDED job. The kind is physics; the role is intent, and the two are
# checked against each other at qualification time (a PUBLISH kind in a BACKUP role is
# exactly the "publishing is not backup" trap).
SURFACE_ROLES = {"ARCHIVE", "BACKUP", "SCRATCH", "PUBLISH"}


class SurfaceError(RuntimeError):
    """kind in {UNKNOWN_SURFACE, UNREACHABLE, UNQUALIFIED, DUPLICATE}.

    UNKNOWN_SURFACE - asked about an id that was never registered.
    UNREACHABLE     - a measurement recorded the surface as not reachable (the vocabulary
                      of a measured-dead surface; measure() RECORDS it rather than raising,
                      so this is the word qualification and callers use for that state).
    UNQUALIFIED     - a structural precondition is missing: a bad kind/role at register, or
                      a measure() on a surface with no probe attached.
    DUPLICATE       - re-registering an id that already exists.
    """

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# A probe is CODE, not prose: () -> (reachable, free_bytes_or_None, detail). free_bytes is
# None when the surface answers "reachable" but cannot report capacity - which is itself a
# disqualifier for a backup target, never silently treated as zero or as infinite.
Probe = Callable[[], "tuple[bool, Optional[int], str]"]


class Surfaces:
    """Backed by the ledger: every registration, every measurement and every qualification
    decision is an event; current state is a projection. Nothing holds a qualified status
    that a re-run of qualify_backup_target would not reproduce from the recorded facts."""

    # A measurement older than this is STALE - reachable "then" is not reachable "now,"
    # and a target qualified on a week-old probe is the green-log-over-nothing defect wearing
    # a timestamp. Override per call; the default is a day.
    STALE_AFTER_S = 24 * 3600

    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock
        self._probes: dict[str, Probe] = {}

    # ---------------- claims ----------------
    def register(self, surface_id: str, kind: str, path_or_url: str, role: str) -> None:
        """Record the CLAIM that a surface exists, with its reach class and its intended
        job. This asserts nothing about reachability - registration is not reachability."""
        if kind not in SURFACE_KINDS:
            raise SurfaceError(
                "UNQUALIFIED",
                f"kind {kind!r} not in {sorted(SURFACE_KINDS)} - a surface must declare "
                f"whether reaching it leaves this machine, because off-machine is the whole "
                f"question a backup target has to answer")
        if role not in SURFACE_ROLES:
            raise SurfaceError(
                "UNQUALIFIED",
                f"role {role!r} not in {sorted(SURFACE_ROLES)} - a surface must declare its "
                f"job; a PUBLISH mirror standing in for a BACKUP is the exact scar 'publishing "
                f"is not backup' was written to stop")
        if surface_id in self.state():
            raise SurfaceError(
                "DUPLICATE",
                f"{surface_id!r} already registered - two entries for one surface let a "
                f"stale claim shadow a live one; update by measuring, not by re-registering")
        self.ledger.append(
            "SURFACE_REGISTERED",
            {"surface_id": surface_id, "kind": kind, "path_or_url": path_or_url,
             "role": role})

    def attach_probe(self, surface_id: str, fn: Probe) -> None:
        """A probe is a runnable reachability+capacity check: () -> (reachable, free_bytes
        or None, detail). It is code so that 'reachable' is measured, not asserted."""
        self._probes[surface_id] = fn

    # ---------------- measurements ----------------
    def measure(self, surface_id: str) -> dict:
        """Run the attached probe NOW and ledger the result. UNREACHABLE is recorded, never
        assumed and never raised - a surface that is dead today is a fact to write down, and
        the caller decides what an unreachable target means for a qualification."""
        if surface_id not in self.state():
            raise SurfaceError("UNKNOWN_SURFACE", surface_id)
        if surface_id not in self._probes:
            raise SurfaceError(
                "UNQUALIFIED",
                f"{surface_id!r}: no probe attached - a surface nobody can measure cannot "
                f"be a qualified target")
        try:
            reachable, free_bytes, detail = self._probes[surface_id]()
        except Exception as e:                                            # noqa: BLE001
            reachable, free_bytes, detail = False, None, f"probe raised {type(e).__name__}: {e}"
        t = self._clock()
        measurement = {
            "surface_id": surface_id,
            "reachable": bool(reachable),
            "free_bytes": (int(free_bytes) if free_bytes is not None else None),
            "detail": str(detail)[:300],
            "t": t,
        }
        self.ledger.append("SURFACE_MEASURED", measurement)
        return measurement

    # ---------------- qualification ----------------
    def qualify_backup_target(self, surface_id: str, min_free_bytes: int,
                              require_offmachine: bool = True,
                              max_age_s: Optional[float] = None) -> dict:
        """THE THREE QUESTIONS a backup target must pass, decided from the last measurement:

          (1) REACHABILITY  - the last measurement says reachable AND is fresh. Never
                              measured, measured-unreachable, or measured-but-stale all fail.
          (2) CAPACITY      - measured free_bytes >= min_free_bytes. Unknown free space fails
                              (a target of unknown size is not a qualified size).
          (3) MESH-ADDRESSABILITY - when require_offmachine, the kind must be LAN or CLOUD; a
                              LOCAL surface on this same box is one surge from nothing, and
                              one copy on one machine is zero.

        Every failing question appends a plain-language reason. The decision is ledgered so a
        later reader can see WHY a surface was or was not trusted, not just the verdict."""
        st = self.state()
        if surface_id not in st:
            raise SurfaceError("UNKNOWN_SURFACE", surface_id)
        window = self.STALE_AFTER_S if max_age_s is None else max_age_s
        claim = st[surface_id]["claim"]
        m = st[surface_id]["measurement"]
        now = self._clock()
        reasons: list[str] = []

        # (1) reachability - measured, reachable, and fresh
        if m is None:
            reasons.append("reachability: never measured - registration is not reachability, "
                           "and an unmeasured target is an intention, not a backup")
        elif not m["reachable"]:
            reasons.append(f"reachability: last measurement UNREACHABLE ({m['detail']})")
        else:
            age = now - m["t"]
            if age > window:
                reasons.append(f"reachability: measurement is stale ({age:.0f}s old > "
                               f"{window:.0f}s window) - reachable then is not reachable now")

        # (2) capacity - measured free space large enough
        if m is None or m["free_bytes"] is None:
            reasons.append(f"capacity: free space unknown - a target that cannot report its "
                           f"size cannot be shown to hold {min_free_bytes} bytes")
        elif m["free_bytes"] < min_free_bytes:
            reasons.append(f"capacity: free {m['free_bytes']} < required {min_free_bytes} bytes")

        # (3) mesh-addressability - off this machine when required
        if require_offmachine and claim["kind"] not in {"LAN", "CLOUD"}:
            reasons.append(f"mesh-addressability: kind {claim['kind']} is on this machine - "
                           f"one copy on one machine is zero; off-machine or it does not count")

        qualified = not reasons
        self.ledger.append("SURFACE_QUALIFIED",
                           {"surface_id": surface_id, "qualified": qualified,
                            "reasons": reasons})
        return {"qualified": qualified, "reasons": reasons}

    # ---------------- projection ----------------
    def state(self) -> dict:
        def fold(s, rec):
            p, e = rec["payload"], rec["event"]
            if e == "SURFACE_REGISTERED":
                s[p["surface_id"]] = {"claim": p, "measurement": None, "qualified": None}
            elif e == "SURFACE_MEASURED" and p.get("surface_id") in s:
                s[p["surface_id"]]["measurement"] = {
                    "reachable": p["reachable"], "free_bytes": p["free_bytes"],
                    "detail": p["detail"], "t": p["t"]}
            elif e == "SURFACE_QUALIFIED" and p.get("surface_id") in s:
                s[p["surface_id"]]["qualified"] = p["qualified"]
            return s
        return self.ledger.project(fold, {})

    def report(self) -> list[dict]:
        """Every surface with claim + last measurement + AGE + last verdict. A never-measured
        surface reports reachable=None (UNKNOWN) - never True, because registration measured
        nothing. free_gb and age_s are None until a probe has actually run."""
        now = self._clock()
        rows = []
        for sid, v in sorted(self.state().items()):
            m = v["measurement"]
            rows.append({
                "id": sid,
                "kind": v["claim"]["kind"],
                "role": v["claim"]["role"],
                "path_or_url": v["claim"].get("path_or_url"),
                "reachable": (m["reachable"] if m else None),
                "free_gb": (round(m["free_bytes"] / 1e9, 2)
                            if (m and m["free_bytes"] is not None) else None),
                "age_s": ((now - m["t"]) if m else None),
                "qualified": v["qualified"],
                "detail": (m["detail"] if m else None),
            })
        return rows


def _read_json_file(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return raw if isinstance(raw, dict) else None


def _dest_from_backup_targets(cfg: dict | None, kind: str) -> Path | None:
    if not cfg:
        return None
    targets = cfg.get("targets")
    if not isinstance(targets, dict):
        return None
    row = targets.get(kind)
    if not isinstance(row, dict):
        return None
    dest = row.get("dest")
    if not isinstance(dest, str) or not dest.strip():
        return None
    return Path(dest.strip())


def _dest_from_bucket_worker(cfg: dict | None, key: str) -> Path | None:
    if not cfg:
        return None
    dest = cfg.get("dest")
    if not isinstance(dest, dict):
        return None
    val = dest.get(key) or dest.get(key.lower())
    if not isinstance(val, str) or not val.strip():
        return None
    return Path(val.strip())


def resolve_surface_paths(paths) -> dict[str, Path | None]:
    """Operator-configured roots only — never a well-known drive literal."""
    out: dict[str, Path | None] = {sid: None for sid in CANON_SURFACE_IDS}
    if paths is None:
        return out
    cfg_dir = paths.role("config")
    backup = _read_json_file(cfg_dir / _BACKUP_TARGETS_NAME)
    out["GDX"] = _dest_from_backup_targets(backup, "gdx")
    out["ODX"] = _dest_from_backup_targets(backup, "odx")
    out["TB1"] = _dest_from_backup_targets(backup, "tb1")
    bucket_cfg = None
    for name in _BUCKET_WORKER_NAMES:
        bucket_cfg = _read_json_file(cfg_dir / name)
        if bucket_cfg:
            break
    if out["GDX"] is None:
        out["GDX"] = _dest_from_bucket_worker(bucket_cfg, "GDX")
    if out["ODX"] is None:
        out["ODX"] = _dest_from_bucket_worker(bucket_cfg, "ODX")
    if out["TB1"] is None:
        out["TB1"] = _dest_from_bucket_worker(bucket_cfg, "TB1")
    rold = Path(r"V:\Ai\ROLD")
    out["ROLD"] = rold if rold.is_dir() else None
    return out


def exchange_put_verify_probe(root: Path) -> Probe:
    """GDX BTS_SGH_Handoff exchange: atomic put, read back, verify hash, remove probe file."""

    def _probe():
        p = Path(root)
        if not p.is_dir():
            return False, None, f"NO_DEST: not a directory ({p})"
        probe_dir = p / ".cosmos-gdx-probe"
        try:
            probe_dir.mkdir(exist_ok=True)
        except OSError as e:
            return False, None, f"probe dir: {type(e).__name__}"
        token = uuid.uuid4().hex
        payload = {"schema": "cosmos-gdx-probe/1", "token": token}
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        tmp = probe_dir / f".put-{token}.tmp"
        final = probe_dir / f"put-{token}.json"
        try:
            tmp.write_bytes(body)
            os.replace(tmp, final)
            read_back = final.read_bytes()
            if hashlib.sha256(read_back).hexdigest() != digest:
                return False, None, "readback hash mismatch"
            parsed = json.loads(read_back.decode("utf-8"))
            if parsed.get("token") != token:
                return False, None, "readback token mismatch"
            final.unlink(missing_ok=True)
        except OSError as e:
            return False, None, f"put+verify: {type(e).__name__}: {e}"
        try:
            free = int(shutil.disk_usage(p).free)
        except OSError:
            free = None
        return True, free, f"atomic put+verify ok ({p})"

    return _probe


def _itc_publish_probe(url: str) -> Probe:
    def _probe():
        try:
            import urllib.error
            import urllib.request

            req = urllib.request.Request(  # noqa: S310
                url, method="HEAD", headers={"User-Agent": "cosmos-surfaces/1"})
            with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
                code = int(resp.status)
            ok = 200 <= code < 400
            return ok, None, f"HEAD {url} -> {code}"
        except Exception as e:  # noqa: BLE001
            return False, None, f"HEAD {url}: {type(e).__name__}"

    return _probe


def _canon_probe(surface_id: str, dest: Path | None) -> Probe:
    if surface_id in ("GDX", "ODX"):
        if dest is None:
            return lambda: (False, None, "NO_DEST: not configured on this host")
        return exchange_put_verify_probe(dest)
    if surface_id == "ROLD":
        if dest is None:
            return lambda: (False, None, "NO_DEST: ROLD tree not present")
        return local_disk_probe(str(dest))
    if surface_id == "TB1":
        if dest is None:
            return lambda: (False, None, "NO_DEST: TB1 not configured")
        return local_disk_probe(str(dest))
    if surface_id == "ITC":
        return _itc_publish_probe("https://ai.dchambers.com")
    return lambda: (False, None, f"no probe for {surface_id}")


def local_disk_probe(path: str) -> Probe:
    """() -> (reachable, free_bytes, detail) for a filesystem root."""

    def _probe():
        p = Path(path)
        if not p.exists():
            return False, None, f"missing {path}"
        try:
            u = shutil.disk_usage(p)
        except OSError as e:
            return False, None, f"disk_usage {path}: {type(e).__name__}"
        return True, int(u.free), f"{path} free={u.free} total={u.total}"

    return _probe


def seed_host_surfaces(sf: "Surfaces", root: Path | str, paths=None) -> list[str]:
    """Idempotent: register + probe + measure the COSMOS runtime root.

    One LOCAL SCRATCH surface so GET /api/v1/surfaces is never an empty
    catalog on a writing boot. Five canon names (ROLD ITC GDX ODX TB1) are
    registered for cDeck; dest paths come from config only. reachable stays
    None until a probe runs (measure() or POST /api/v1/surfaces check).
    """
    touched: list[str] = []
    root_s = str(Path(root))
    sid = "cosmos-live"
    if sid not in sf.state():
        sf.register(sid, "LOCAL", root_s, "SCRATCH")
    sf.attach_probe(sid, local_disk_probe(root_s))
    if sf.state().get(sid, {}).get("measurement") is None:
        sf.measure(sid)
    touched.append(sid)

    resolved = resolve_surface_paths(paths)
    for canon_id in CANON_SURFACE_IDS:
        kind, role, claim_path = _CANON_CLAIMS[canon_id]
        if canon_id not in sf.state():
            sf.register(canon_id, kind, claim_path, role)
        dest = resolved.get(canon_id)
        sf.attach_probe(canon_id, _canon_probe(canon_id, dest))
        touched.append(canon_id)
    return touched


def measure_canon_surfaces(sf: "Surfaces", paths=None) -> list[dict]:
    """Run probes for canon rows whose dest is configured (or ITC HEAD)."""
    resolved = resolve_surface_paths(paths)
    out: list[dict] = []
    for canon_id in CANON_SURFACE_IDS:
        if canon_id not in sf.state():
            continue
        if canon_id != "ITC" and resolved.get(canon_id) is None:
            continue
        try:
            out.append(sf.measure(canon_id))
        except SurfaceError:
            continue
    return out