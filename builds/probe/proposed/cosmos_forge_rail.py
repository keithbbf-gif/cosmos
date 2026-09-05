#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_forge_rail.py -- the two forge hands, gitlab-forge + github-forge.

PROPOSAL (staged in builds/probe/proposed/, NOT live). Target path on acceptance:
`cosmos/cosmos_forge_rail.py`. Written by the maker-hands shortlist pass; cosmos/ is
outside that pass's write-fence, so this file is proposed, not installed.

WHY ONE MODULE FOR TWO RAILS. `glab` and `gh` differ in exactly three values: the
binary, the identity verb, and how the identity is lifted out of the reply. Everything
else -- spec load, authority refusal, registration, probe-record write -- is identical.
Two 800-line vendor modules would be two places for one guard to drift, which is the
cost `cosmos_rail_base` was created to stop. One table-driven module, two link_ids.

WHY THESE TWO FIRST. Both are already authenticated on this machine and neither needs
a credential from Keith: `gh` and `glab` hold their tokens in the OS keyring, so this
is the first COSMOS rail with NO COSMOS-held secret. There is no `read_key`, so the
NO_KEY refusal that keeps `codex-cli` and `claude-cli` dark cannot apply here.

PROBE BINDS AUTH, NOT PRESENCE. `--version` proves a binary; it does not prove a hand.
The probe runs an authenticated REST verb and requires a value only the live forge can
emit -- GitHub `rate_limit.limit`, GitLab `user.id` -- and requires rc==0 as well. A
non-zero exit is never a pass: a CLI that prints the token we grep for while failing
would otherwise score green, which is the fabricated-pass class this tree has paid for.

$0. GitHub REST is 5000/hr authenticated; `glab api user` is unmetered. Neither verb
starts a pipeline, so neither burns CI minutes. metered_usd=0 -> no spend-gate budget.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import (  # noqa: E402
    RailError as RailSeamError,
    _real_run,
    _real_which,
    ledger_is_authority,
    write_probe_record,
)

SCHEMA = "cosmos-forge-rail/1"
SPEC_NAME = "forge_rail.json"
PROBE_NAME = "forge_rail_probe.json"
SRC, DST = "core", "code"
PROBE_TIMEOUT_S = 45


class ForgeRailError(RailSeamError):
    """Typed refusal for the forge seam. kind in {BAD_SPEC, UNREACHABLE, REFUSED}."""


def _lift_github(doc: dict) -> str:
    """A value only a live, authenticated GitHub can emit."""
    core = doc.get("resources", {}).get("core", doc)
    if "limit" not in core:
        raise ForgeRailError("UNREACHABLE", "rate_limit reply has no .limit")
    return f"rest_limit={core['limit']} remaining={core.get('remaining')}"


def _lift_gitlab(doc: dict) -> str:
    """A value only a live, authenticated GitLab can emit."""
    if not doc.get("id") or not doc.get("username"):
        raise ForgeRailError("UNREACHABLE", "user reply has no .id/.username")
    return f"user_id={doc['id']} username={doc['username']}"


# link_id -> (binary, identity argv tail, lifter). The ONLY per-vendor knowledge.
FORGES: dict[str, tuple[str, tuple[str, ...], object]] = {
    "gitlab-forge": ("glab", ("api", "user"), _lift_gitlab),
    "github-forge": ("gh", ("api", "rate_limit"), _lift_github),
}


def default_spec() -> dict:
    """Instance-free defaults. Live overlay is live/config/forge_rail.json."""
    return {
        "schema": SCHEMA,
        "rail_type": "CLI",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "links": sorted(FORGES),
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "note": (
            "Forge hands. Auth lives in the OS keyring (gh/glab), NOT in "
            "live/config -- this rail holds no COSMOS secret and has no NO_KEY "
            "refusal. Probe runs an authenticated REST verb and binds a "
            "forge-only value (github rate_limit.limit / gitlab user.id); rc==0 "
            "is required but is never itself the pass. $0: no pipeline is "
            "started, so no CI minutes are spent. metered_usd=0 -> unspend-gated."
        ),
    }


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay:
        if not isinstance(overlay, dict):
            raise ForgeRailError("BAD_SPEC", f"overlay must be a dict, got {type(overlay).__name__}")
        spec.update(overlay)
    bad = [l for l in spec["links"] if l not in FORGES]
    if bad:
        raise ForgeRailError("BAD_SPEC", f"unknown link_id(s): {bad}")
    if not spec["links"]:
        raise ForgeRailError("BAD_SPEC", "links is empty - a rail with no link is not a rail")
    return spec


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).is_file():
        return merge_spec(None)
    try:
        return merge_spec(json.loads(Path(path).read_text(encoding="utf-8")))
    except json.JSONDecodeError as e:
        raise ForgeRailError("BAD_SPEC", f"{path}: {e}") from e


class ForgeRail:
    """One forge link. Stateless apart from the last probe record."""

    def __init__(self, link_id: str, spec: dict, run=None, which=None):
        if link_id not in FORGES:
            raise ForgeRailError("BAD_SPEC", f"unknown link_id {link_id!r}")
        self.link_id = link_id
        self.spec = spec
        self.binary, self._argv_tail, self._lift = FORGES[link_id]
        self._run = run or _real_run
        self._which = which or _real_which
        self._last_probe: dict = {}

    def probe(self):
        """Cheapest AUTHENTICATED liveness. Fail-closed on every branch."""
        found = self._which(self.binary)
        if not found:
            self._last_probe = {"binary": None, "rc": None}
            return False, f"UNREACHABLE: {self.binary} ABSENT on PATH"
        timeout = min(PROBE_TIMEOUT_S, int(self.spec.get("probe_timeout_s") or PROBE_TIMEOUT_S))
        r = self._run([found, *self._argv_tail], timeout_s=timeout)
        self._last_probe = {"binary": found, "rc": r.get("rc"),
                            "timed_out": bool(r.get("timed_out"))}
        if r.get("timed_out"):
            return False, f"UNREACHABLE: {self.binary} {' '.join(self._argv_tail)} TIMEOUT"
        # rc is RECORDED and REQUIRED, but the bound value below is the pass.
        if r.get("rc") != 0:
            err = ((r.get("err") or "") + (r.get("out") or "")).strip()[:200]
            return False, f"UNREACHABLE: {self.binary} rc={r.get('rc')} {err}".strip()
        try:
            bound = self._lift(json.loads(r.get("out") or "{}"))
        except (json.JSONDecodeError, ForgeRailError, AttributeError, TypeError) as e:
            return False, f"UNREACHABLE: unparseable {self.binary} reply: {e}"
        self._last_probe["bound"] = bound
        return True, f"{self.link_id} live binary={found} {bound}"


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_forge_rails(registry, adapters: dict, spend_gate=None, *,
                         paths=None, spec=None, run=None, which=None) -> dict:
    """Register every configured forge link. Missing binary -> still registered;
    the probe records UNREACHABLE. Registration is not capability."""
    spec = load_spec(spec_path_for(paths)) if (spec is None and paths is not None) else merge_spec(spec)
    out: dict = {"links": {}, "spec": spec}
    for lid in spec["links"]:
        rail = ForgeRail(lid, spec, run=run, which=which)
        if lid not in registry.state():
            registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                              policy_rank=int(spec["policy_rank"]))
        registry.attach_probe(lid, rail.probe)
        adapters[lid] = rail
        out["links"][lid] = {"rail": rail, "binary": rail.binary}
    # metered_usd == 0.0 by design: no budget is set, so the Dispatcher never
    # spend-gates a $0 forge verb. Kept explicit so a future metered forge verb
    # (Actions minutes, Duo credits) has an obvious place to declare itself.
    if spend_gate is not None and float(spec["metered_usd"]) > 0:
        for lid in spec["links"]:
            spend_gate.set_budget(lid, float(spec["budget_usd"] or spec["metered_usd"]))
    return out


def attach_to_kernel(kernel, adapters: dict | None = None, run=None, which=None, *,
                     boot_compose: bool = False) -> dict:
    """Additive compose onto an already-built Kernel. Same authority refusal as
    every other rail: no LINK_REGISTERED on the authority ledger unless this is
    Kernel boot."""
    if ledger_is_authority(kernel) and not boot_compose:
        raise ForgeRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED outside Kernel "
            "boot. Isolated --gate ledger only. Pass boot_compose=True only "
            "from Kernel.compose_rails.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_forge_rails(kernel.registry, adapters,
                                spend_gate=getattr(kernel, "spend", None),
                                paths=kernel.paths, run=run, which=which)


def _probe_all(root: str) -> dict:
    """Standalone satellite probe: no Kernel, no registry, no ledger write."""
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rec = {"schema": SCHEMA, "tree_id": paths.sentinel.tree_id, "links": {}}
    ok_all = True
    for lid in spec["links"]:
        rail = ForgeRail(lid, spec)
        ok, detail = rail.probe()
        ok_all = ok_all and ok
        rec["links"][lid] = {"ok": ok, "detail": detail, **rail._last_probe}
    rec["ok"] = ok_all
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_forge_rail")
    ap.add_argument("--root", required=True)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--write-probe", action="store_true",
                    help="persist the probe record to live/config/" + PROBE_NAME)
    a = ap.parse_args()
    if not a.probe:
        print(json.dumps({"ok": False, "detail": "nothing to do: pass --probe"}))
        return 2
    try:
        rec = _probe_all(a.root)
    except (ForgeRailError, RailSeamError) as e:
        print(json.dumps({"ok": False, "detail": f"{e.kind}: {e}"}, indent=1))
        return 2
    if a.write_probe:
        from cosmos_paths import CosmosPaths
        write_probe_record(probe_path_for(CosmosPaths(a.root)), rec)
    print(json.dumps(rec, indent=1))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
