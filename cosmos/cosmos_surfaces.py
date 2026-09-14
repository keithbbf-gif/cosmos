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

import json
import shutil
import time
from pathlib import Path
from typing import Callable, Optional

from cosmos_ledger import Ledger

# Five canon storage names on GET /api/v1/surfaces (cDeck Surfaces pane).
CANON_STORAGE_IDS = ("ROLD", "ITC", "GDX", "ODX", "TB1")
STORAGE_SURFACES_CONFIG = "storage_surfaces.json"
BACKUP_TARGETS_CONFIG = "backup_targets.json"
TB1_NOMINAL_BYTES = 30_000_000_000  # TeraBox 30GB plan — capacity claim, not a live probe

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


def _read_json_object(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return doc if isinstance(doc, dict) else None


def _backup_target_dest(root: Path, kind: str) -> str | None:
    """GDX/ODX dest from backup_targets.json when the operator named one."""
    doc = _read_json_object(root / "config" / BACKUP_TARGETS_CONFIG)
    if not doc:
        return None
    targets = doc.get("targets")
    if not isinstance(targets, dict):
        return None
    row = targets.get(kind.lower())
    if not isinstance(row, dict):
        return None
    dest = str(row.get("dest") or "").strip()
    return dest or None


def publish_url_probe(url: str) -> Probe:
    """HEAD/GET reachability for a PUBLISH mirror — no invented success on DNS alone."""

    def _probe():
        import urllib.error
        import urllib.request

        u = str(url or "").strip()
        if not u:
            return False, None, "empty publish URL"
        req = urllib.request.Request(u, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:  # noqa: S310
                ok = 200 <= int(resp.status) < 400
                return ok, None, f"HEAD {resp.status} {u}"
        except urllib.error.HTTPError as e:
            if e.code in (405, 501):
                try:
                    with urllib.request.urlopen(u, timeout=12) as resp:  # noqa: S310
                        ok = 200 <= int(resp.status) < 400
                        return ok, None, f"GET {resp.status} {u}"
                except Exception as e2:  # noqa: BLE001
                    return False, None, f"GET failed {u}: {type(e2).__name__}"
            return False, None, f"HEAD {e.code} {u}"
        except Exception as e:  # noqa: BLE001
            return False, None, f"unreachable {u}: {type(e).__name__}"

    return _probe


def tb1_terabox_probe(root: Path, evidence_rel: str,
                      read_evidence_rel: str | None = None) -> Probe:
    """TeraBox 30GB (TB1). CoW write evidence may exist; READ stays unproven until filed.

    Does not call vendor DOM/API routes — only reads operator-supplied evidence under
    the runtime root. reachable=False with an explicit detail when write is proven
    but read is not; reachable=None only when measure() has not run.
    """

    def _probe():
        ev = (root / evidence_rel).resolve()
        try:
            ev.relative_to(root.resolve())
        except ValueError:
            return False, None, "TB1 evidence path escapes runtime root"
        if not ev.is_file():
            return False, None, "TB1: CoW write not proven on this host"
        free_bytes: int | None = TB1_NOMINAL_BYTES
        detail_extra = ""
        try:
            doc = json.loads(ev.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                if doc.get("free_bytes") is not None:
                    free_bytes = int(doc["free_bytes"])
                elif doc.get("free_gb") is not None:
                    free_bytes = int(float(doc["free_gb"]) * 1e9)
                detail_extra = str(doc.get("detail") or "").strip()
        except (OSError, ValueError, TypeError):
            pass
        read_path = None
        if read_evidence_rel:
            read_path = (root / read_evidence_rel).resolve()
            try:
                read_path.relative_to(root.resolve())
            except ValueError:
                read_path = None
        if read_path and read_path.is_file():
            try:
                rd = json.loads(read_path.read_text(encoding="utf-8"))
                if isinstance(rd, dict) and rd.get("read_proven") is True:
                    fb = free_bytes
                    if rd.get("free_bytes") is not None:
                        fb = int(rd["free_bytes"])
                    return True, fb, (
                        detail_extra or "TB1 — TeraBox 30GB; CoW write and READ proven"
                    )[:300]
            except (OSError, ValueError, TypeError):
                pass
        msg = "TB1 — TeraBox 30GB; CoW write proven, READ unproven"
        if detail_extra:
            msg = f"{msg} ({detail_extra})"[:300]
        return False, free_bytes, msg

    return _probe


def _probe_for_spec(root: Path, sid: str, spec: dict) -> Probe | None:
    probe_kind = str(spec.get("probe") or "").strip().lower()
    path_or_url = str(spec.get("path_or_url") or "").strip()
    if probe_kind in ("", "local", "local_disk"):
        if not path_or_url:
            path_or_url = _backup_target_dest(root, sid) or ""
        if not path_or_url:
            return None
        return local_disk_probe(path_or_url)
    if probe_kind == "publish":
        if not path_or_url:
            return None
        return publish_url_probe(path_or_url)
    if probe_kind == "tb1":
        ev = str(spec.get("cow_write_evidence") or "state/tb1_cow_write.json").strip()
        rev = spec.get("read_evidence")
        read_rel = str(rev).strip() if rev else "state/tb1_read_proven.json"
        return tb1_terabox_probe(root, ev, read_evidence_rel=read_rel)
    return None


def seed_canon_storage_surfaces(sf: "Surfaces", root: Path | str) -> list[str]:
    """Register five canon rows from config/storage_surfaces.json when the operator filed it.

    Absent config → no canon rows (hermetic tests stay cosmos-live only). Never invents
    V:\\ / X:\\ paths. TB1 uses evidence files, not invented TeraBox reachability.
    """
    root_p = Path(root)
    cfg = _read_json_object(root_p / "config" / STORAGE_SURFACES_CONFIG)
    if not cfg:
        return []
    surfaces = cfg.get("surfaces")
    if not isinstance(surfaces, dict):
        return []
    seeded: list[str] = []
    for sid in CANON_STORAGE_IDS:
        spec = surfaces.get(sid)
        if not isinstance(spec, dict):
            continue
        kind = str(spec.get("kind") or "").strip().upper()
        role = str(spec.get("role") or "").strip().upper()
        path_or_url = str(spec.get("path_or_url") or "").strip()
        if not path_or_url and sid in ("GDX", "ODX"):
            path_or_url = _backup_target_dest(root_p, sid) or ""
        if not kind or not role:
            continue
        if sid not in sf.state():
            sf.register(sid, kind, path_or_url or f"config:{sid}", role)
        probe = _probe_for_spec(root_p, sid, spec)
        if probe is not None:
            sf.attach_probe(sid, probe)
            if sf.state().get(sid, {}).get("measurement") is None:
                sf.measure(sid)
        seeded.append(sid)
    return seeded


def seed_host_surfaces(sf: "Surfaces", root: Path | str) -> list[str]:
    """Idempotent: register + probe + measure the COSMOS runtime root.

    One LOCAL SCRATCH surface so GET /api/v1/surfaces is never an empty
    catalog on a writing boot. Canon storage (ROLD/ITC/GDX/ODX/TB1) loads
    only from config/storage_surfaces.json — never invented in tests.
    """
    sid = "cosmos-live"
    root_s = str(Path(root))
    if sid not in sf.state():
        sf.register(sid, "LOCAL", root_s, "SCRATCH")
    sf.attach_probe(sid, local_disk_probe(root_s))
    if sf.state().get(sid, {}).get("measurement") is None:
        sf.measure(sid)
    out = [sid]
    out.extend(seed_canon_storage_surfaces(sf, root))
    return out