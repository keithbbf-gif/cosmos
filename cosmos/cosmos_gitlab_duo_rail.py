#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_gitlab_duo_rail — GitLab Duo COM rail (glab + trigger tokens).

B29. CI is the execute-the-gate; this rail is identity + trigger roster, not
a green badge. Probe binds a value only live GitLab emits (pipeline trigger
id + description from GET …/triggers). dispatch REFUSES pipeline/duo run
unless payload execute=True (Keith permission). Trigger token lives in
live/config/gitlab_trigger_token.txt (existence only for hands; never printed).

    py -3.14 cosmos\\cosmos_gitlab_duo_rail.py --selftest
    py -3.14 cosmos\\cosmos_gitlab_duo_rail.py --root … --probe
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
from html import escape as esc
from pathlib import Path

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(text: str) -> str:
    return _ANSI.sub("", text or "")


sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import (  # noqa: E402
    RailError as RailSeamError,
    ledger_is_authority,
    _real_run,
    _real_which,
    write_probe_record,
)

SCHEMA = "cosmos-gitlab-duo-com-rail/1"
WORKER = "cosmos-gitlab-duo-com-rail"
LINK_ID = "gitlab-duo-com"
SPEC_NAME = "gitlab_duo_com_rail.json"
PROBE_NAME = "gitlab_duo_com_probe.json"
TRIGGER_TOKEN_NAME = "gitlab_trigger_token.txt"
SRC, DST = "core", "com"
PROJECT_PATH = "keithbbf-gif/cosmos"
PROJECT_ENC = urllib.parse.quote(PROJECT_PATH, safe="")
TRIGGERS_PATH = f"projects/{PROJECT_ENC}/triggers"
PROBE_TIMEOUT_S = 45
DISPATCH_TIMEOUT_S = 120

# CI / Duo workflow verbs that burn minutes or credits. Identity GET is not among them.
_EXECUTE_NEEDLES = (
    "trigger/pipeline", "ci run", "ci trigger", "ci run-trig",
    "pipeline run", "pipeline trigger", "duo workflow", "duo cli run",
    "duo run",
)

# cDeck / Model Rater map (System rails pane paints link_id; via is the hand).
CDECK_SYSTEM_PANE = "system_rails"
CDECK_MODEL_RATER_VIA = LINK_ID
FARM_SEAT = {"profile": "motif", "seat": "critic_duo"}


class GitlabDuoComRailError(RailSeamError):
    """kind in {BAD_SPEC, BAD_ROOT, UNREACHABLE, REFUSED, NO_HANDS}."""


def _lift_trigger(doc: dict) -> str:
    """Vendor-emitted trigger identity (id + description)."""
    tid = doc.get("id")
    desc = str(doc.get("description") or doc.get("token") or "").strip()
    if tid is None:
        raise GitlabDuoComRailError("UNREACHABLE", "trigger reply has no .id")
    if not desc:
        desc = "(no description)"
    return f"trigger_id={tid} description={desc}"


def default_spec() -> dict:
    return _pin_origin({
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "CLI",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "project": PROJECT_PATH,
        "triggers_path": TRIGGERS_PATH,
        "trigger_token_file": TRIGGER_TOKEN_NAME,
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "note": (
            "GitLab Duo COM: glab api triggers + CI trigger token on disk. "
            "CI is execute-the-gate (dispatch with execute=True only). "
            "Probe never starts a pipeline. dst=com (not forge)."
        ),
        "cdeck": {
            "system_pane": CDECK_SYSTEM_PANE,
            "model_rater_via": CDECK_MODEL_RATER_VIA,
            "farm_seat": FARM_SEAT,
        },
    })


def _pin_origin(spec: dict) -> dict:
    spec["schema"] = SCHEMA
    spec["link_id"] = str(spec.get("link_id") or LINK_ID)
    spec["rail_type"] = "CLI"
    spec["src"] = str(spec.get("src") or SRC) or SRC
    dst = str(spec.get("dst") or DST) or DST
    if dst in ("code", "models", "read", "interact", "papers", "forge"):
        spec["route_note"] = f"coerced dst={dst!r} to {DST} (COM rail)"
        dst = DST
    spec["dst"] = dst
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["probe_timeout_s"] = int(spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
    proj = str(spec.get("project") or PROJECT_PATH)
    spec["project"] = proj
    spec["triggers_path"] = str(
        spec.get("triggers_path")
        or f"projects/{urllib.parse.quote(proj, safe='')}/triggers")
    kn = str(spec.get("trigger_token_file") or TRIGGER_TOKEN_NAME)
    if kn != TRIGGER_TOKEN_NAME:
        raise GitlabDuoComRailError(
            "BAD_SPEC", f"trigger_token_file {kn!r} != {TRIGGER_TOKEN_NAME!r}")
    spec["trigger_token_file"] = TRIGGER_TOKEN_NAME
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay:
        if not isinstance(overlay, dict):
            raise GitlabDuoComRailError(
                "BAD_SPEC", f"overlay must be dict, got {type(overlay).__name__}")
        spec.update(overlay)
        spec = _pin_origin(spec)
    return spec


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).is_file():
        return merge_spec(None)
    try:
        return merge_spec(json.loads(Path(path).read_text(encoding="utf-8")))
    except json.JSONDecodeError as e:
        raise GitlabDuoComRailError("BAD_SPEC", f"{path}: {e}") from e


def write_spec(path: Path, overlay=None) -> dict:
    spec = merge_spec(overlay)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    return spec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def trigger_token_path_for(paths, spec: dict | None = None) -> Path:
    sp = merge_spec(spec) if spec else default_spec()
    return paths.config(sp["trigger_token_file"])


def hands_configured(paths, spec: dict | None = None) -> bool:
    """Existence only — never reads token bytes."""
    sp = load_spec(spec_path_for(paths) if paths else None)
    if spec:
        sp = merge_spec(spec)
    return (spec_path_for(paths).exists()
            and trigger_token_path_for(paths, sp).exists())


def cdeck_map(spec: dict | None = None) -> dict:
    """Escaped strings for cDeck System rails / Model Rater via."""
    sp = merge_spec(spec)
    cd = sp.get("cdeck") if isinstance(sp.get("cdeck"), dict) else {}
    seat = cd.get("farm_seat") if isinstance(cd.get("farm_seat"), dict) else FARM_SEAT
    return {
        "link_id": esc(LINK_ID),
        "system_pane": esc(str(cd.get("system_pane") or CDECK_SYSTEM_PANE)),
        "model_rater_via": esc(str(cd.get("model_rater_via") or CDECK_MODEL_RATER_VIA)),
        "farm_profile": esc(str(seat.get("profile") or "")),
        "farm_seat": esc(str(seat.get("seat") or "")),
        "role": esc("CI is the execute-the-gate. Duo proposes."),
    }


def _is_execute(argv_tail: tuple[str, ...]) -> bool:
    joined = " ".join(argv_tail).lower()
    return any(n in joined for n in _EXECUTE_NEEDLES)


class GitlabDuoComRail:
    """One COM link: glab triggers list + optional gated CI trigger."""

    kind = "CLI"

    def __init__(self, spec: dict, paths=None, run=None, which=None):
        self.spec = merge_spec(spec)
        self.paths = paths
        self.link_id = self.spec["link_id"]
        self._run = run or _real_run
        self._which = which or _real_which
        self._last_probe: dict = {}
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)

    def last_identity(self) -> dict:
        return dict(self._last_probe)

    def _exec(self, argv_tail: tuple[str, ...], timeout_s: int) -> dict:
        found = self._which("glab")
        if not found:
            rec = {"binary": None, "rc": None, "bound": None}
            self._last_probe = rec
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": "UNREACHABLE: glab ABSENT on PATH", **rec}
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        env["CLICOLOR"] = "0"
        r = self._run([found, *argv_tail], timeout_s=timeout_s, env=env)
        rec = {"binary": found, "rc": r.get("rc"),
               "timed_out": bool(r.get("timed_out")), "bound": None}
        self._last_probe = rec
        if r.get("timed_out"):
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": "UNREACHABLE: glab TIMEOUT", **rec}
        out = _strip_ansi(r.get("out") or "")
        err = _strip_ansi(r.get("err") or "")
        if r.get("rc") != 0:
            snippet = (err + out).strip()[:200]
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"UNREACHABLE: glab rc={r.get('rc')} {snippet}".strip(),
                    **rec, "out": out, "err": err}
        rec["out"] = out
        rec["err"] = err
        self._last_probe = rec
        return {"ok": True, "kind": "CLI", "detail": "", **rec}

    def probe(self):
        """List pipeline triggers; bind first trigger id + description."""
        if self.paths is not None and not hands_configured(self.paths, self.spec):
            return False, "UNMEASURED: spec or trigger token file absent (no hands)"
        timeout = min(PROBE_TIMEOUT_S,
                      int(self.spec.get("probe_timeout_s") or PROBE_TIMEOUT_S))
        rec = self._exec(("api", self.spec["triggers_path"]), timeout)
        if not rec["ok"]:
            return False, rec["detail"]
        try:
            payload = json.loads(rec.get("out") or "[]")
        except json.JSONDecodeError as e:
            return False, f"UNREACHABLE: unparseable glab triggers: {e}"
        rows = payload if isinstance(payload, list) else []
        if not rows:
            return False, "UNREACHABLE: GitLab triggers list is empty"
        first = rows[0] if isinstance(rows[0], dict) else {}
        try:
            bound = _lift_trigger(first)
        except GitlabDuoComRailError as e:
            return False, str(e)
        self._last_probe = {
            "binary": rec.get("binary"), "rc": rec.get("rc"),
            "timed_out": rec.get("timed_out"), "bound": bound,
            "model_source": "GET /triggers id+description",
        }
        return True, f"{self.link_id} live binary={rec['binary']} {bound}"

    def dispatch(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        extra = payload.get("argv")
        execute = bool(payload.get("execute"))
        if extra is None:
            tail = ("api", self.spec["triggers_path"])
            identity = True
        else:
            if isinstance(extra, str):
                raise GitlabDuoComRailError(
                    "BAD_SPEC", "argv must be a list, never a shell string")
            tail = tuple(str(x) for x in extra)
            identity = False
        if _is_execute(tail) and not execute:
            raise GitlabDuoComRailError(
                "REFUSED",
                "CI/Duo execute refused without execute=True (would burn minutes/credits)")
        timeout = int(payload.get("timeout_s") or DISPATCH_TIMEOUT_S)
        rec = self._exec(tail, timeout)
        if not rec["ok"]:
            return {"ok": False, "rc": rec.get("rc"), "body": "",
                    "text": rec["detail"], "model": "", "kind": rec["kind"],
                    "link_id": self.link_id, "detail": rec["detail"]}
        body = rec.get("out") or ""
        model = ""
        if identity:
            try:
                payload_json = json.loads(body or "[]")
                rows = payload_json if isinstance(payload_json, list) else []
                if not rows:
                    return {"ok": False, "rc": rec.get("rc"), "body": body,
                            "text": "empty triggers", "model": "", "kind": "UNREACHABLE",
                            "link_id": self.link_id,
                            "detail": "UNREACHABLE: empty triggers list"}
                model = _lift_trigger(rows[0] if isinstance(rows[0], dict) else {})
            except (json.JSONDecodeError, GitlabDuoComRailError) as e:
                return {"ok": False, "rc": rec.get("rc"), "body": body,
                        "text": str(e), "model": "", "kind": "UNREACHABLE",
                        "link_id": self.link_id,
                        "detail": f"UNREACHABLE: {e}"}
            self._last_probe = {
                "binary": rec.get("binary"), "rc": rec.get("rc"),
                "timed_out": rec.get("timed_out"), "bound": model,
            }
            body = model
        return {"ok": True, "rc": rec.get("rc"), "body": body, "text": body,
                "model": model or body[:80], "kind": "CLI",
                "link_id": self.link_id, "detail": "",
                "model_source": "GET /triggers id+description" if model else ""}


def register_gitlab_duo_com_rail(registry, adapters: dict, spend_gate=None, *,
                                 paths=None, spec=None, run=None, which=None) -> dict:
    spec = load_spec(spec_path_for(paths)) if (spec is None and paths is not None) else merge_spec(spec)
    rail = GitlabDuoComRail(spec, paths=paths, run=run, which=which)
    if rail.link_id not in registry.state():
        registry.register(rail.link_id, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(rail.link_id, rail.probe)
    adapters[rail.link_id] = rail
    out = {"link_id": rail.link_id, "rail": rail, "src": spec["src"], "dst": spec["dst"],
           "cdeck": cdeck_map(spec)}
    if spend_gate is not None and float(spec["metered_usd"]) > 0:
        spend_gate.set_budget(rail.link_id, float(spec["budget_usd"] or spec["metered_usd"]))
    return out


def attach_to_kernel(kernel, adapters: dict | None = None, run=None, which=None, *,
                     boot_compose: bool = False) -> dict:
    if ledger_is_authority(kernel) and not boot_compose:
        raise GitlabDuoComRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED outside Kernel "
            "boot. Pass boot_compose=True only from Kernel.compose_rails.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_gitlab_duo_com_rail(
        kernel.registry, adapters,
        spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, run=run, which=which)


def live_call_shape(paths) -> dict:
    """Prove-shaped call for cosmos_rails_prober / Registry.prove."""
    spec = load_spec(spec_path_for(paths) if paths else None)
    rail = GitlabDuoComRail(spec, paths=paths)
    ok, detail = rail.probe()
    ident = rail.last_identity()
    bound = str(ident.get("bound") or "")
    live = bool(ok and bound)
    body = f"{LINK_ID} {bound}" if live else ""
    return {
        "ok": live,
        "rc": 0 if live else 2,
        "body": body,
        "body_bytes": len(body.encode("utf-8")),
        "model": bound if live else "",
        "model_source": ident.get("model_source") or "GET /triggers id+description",
        "detail": str(detail)[:300],
        "via": "glab",
    }


def _probe_standalone(root: str, run=None, which=None) -> dict:
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rail = GitlabDuoComRail(spec, paths=paths, run=run, which=which)
    ok, detail = rail.probe()
    ident = rail.last_identity()
    rec = {
        "schema": SCHEMA,
        "tree_id": paths.sentinel.tree_id,
        "link_id": LINK_ID,
        "ok": ok,
        "detail": detail,
        "hands": hands_configured(paths, spec),
        "binary": ident.get("binary"),
        "rc": ident.get("rc"),
        "bound": ident.get("bound"),
        "dst": spec["dst"],
        "cdeck": cdeck_map(spec),
    }
    write_probe_record(probe_path_for(paths), rec)
    return rec


def _expect_kind(fn, kind: str) -> bool:
    try:
        fn()
    except GitlabDuoComRailError as e:
        return e.kind == kind
    except Exception:  # noqa: BLE001
        return False
    return False


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import Kernel, install

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    trig_body = json.dumps([{"id": 7, "description": "cosmos-gate"}])

    def which(name):
        return "/fake/glab" if name == "glab" else None

    def run(argv, **_k):
        if Path(argv[0]).stem.lower() == "glab" and tuple(argv[1:3]) == ("api", TRIGGERS_PATH):
            return {"rc": 0, "out": trig_body, "err": "", "timed_out": False}
        if "trigger" in " ".join(argv).lower() or "duo" in " ".join(argv).lower():
            return {"rc": 0, "out": "STARTED", "err": "", "timed_out": False}
        return {"rc": 2, "out": "", "err": "unexpected", "timed_out": False}

    spec = merge_spec(None)
    check("default dst is com, never forge/code",
          lambda: spec["dst"] == DST and spec["src"] == SRC)
    coerced = merge_spec({"dst": "forge"})
    check("overlay dst=forge is coerced to com",
          lambda: coerced["dst"] == DST and "route_note" in coerced)
    m = cdeck_map({"cdeck": {"system_pane": "system&rails",
                              "farm_seat": {"profile": "motif", "seat": "a<b"}}})
    check("cdeck_map applies esc() on all data text",
          lambda: m["system_pane"] == "system&amp;rails"
          and m["farm_seat"] == "a&lt;b")

    td = Path(tempfile.mkdtemp(prefix="cosmos_gitlab_duo_"))
    root = install(td / "live", tree_id="gitlab-duo-com-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    write_spec(spec_path_for(paths))
    paths.config(TRIGGER_TOKEN_NAME).write_text("PLACEHOLDER\n", encoding="utf-8")

    rail = GitlabDuoComRail(spec, paths=paths, run=run, which=which)
    ok, detail = rail.probe()
    check("probe binds trigger_id from live JSON",
          lambda: ok and "trigger_id=7" in detail
          and rail.last_identity().get("bound", "").startswith("trigger_id=7"))

    refused = False
    try:
        rail.dispatch({"argv": ["ci", "run"]})
    except GitlabDuoComRailError as e:
        refused = e.kind == "REFUSED"
    check("ci run without execute=True is REFUSED", lambda: refused)

    shape = {
        "ok": ok,
        "model": rail.last_identity().get("bound") or "",
        "detail": detail,
    }
    check("prove-shaped result carries vendor model string",
          lambda: shape.get("ok") and shape.get("model", "").startswith("trigger_id=7"))
    check("proof record never echoes placeholder token",
          lambda: "PLACEHOLDER" not in json.dumps(shape))

    k = Kernel(root, worker="core")
    check("kernel compose attaches gitlab-duo-com adapter",
          lambda: LINK_ID in k.adapters
          and k.adapters[LINK_ID].spec.get("dst") == DST)
    check("attach did not claim capability without live prove",
          lambda: k.registry.live_nodes().get(LINK_ID) is None
          or k.registry.live_nodes()[LINK_ID].get("verified") is not True)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gitlab-duo-com; CI execute gated)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_gitlab_duo_rail")
    ap.add_argument("--root")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--write-spec", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.root and args.write_spec:
        from cosmos_paths import CosmosPaths
        paths = CosmosPaths(args.root)
        write_spec(spec_path_for(paths))
        print(json.dumps({"ok": True, "spec": str(spec_path_for(paths))}))
        return 0
    if args.root and args.probe:
        rec = _probe_standalone(args.root)
        print(json.dumps(rec, indent=2))
        return 0 if rec.get("ok") else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
