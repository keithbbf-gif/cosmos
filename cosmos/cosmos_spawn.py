#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANON spawn layers — Role, Wrapper, Skills, Tools, Params.

Smallest functions. One spec, filled layers, visible fills. Never a silent
skip. Work-order runner calls apply() before any model argv. Extra grok.exe
/ grok --single as a WO worker is REFUSED (fail_xfer). GET never mkdir.

    from cosmos_spawn import (
        SpawnSpec, SpawnError, defaults, apply, apply_order,
        preflight_session, refuse, require_context_list, fail_xfer,
    )
    py -3.14 cosmos\\cosmos_spawn.py --selftest
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
WRAP_DIR = HERE / "WRAP"
STYLES_DIR = HERE / "STYLES"
DEFAULT_ROLE = "CODER"
CCR_SESSION = "f47bad79"
CCR_ROLE = "CCR"
CTX_CONCAT = " · "
SCHEMA = "cosmos-spawn/1"
ROLE_SKILLS = {
    "CODER": ("AGENT_BRIEF", "AGENT_BOUNDARIES", "CODER_BRIEF"),
    "CCR": ("AGENT_BRIEF", "AGENT_BOUNDARIES", "CCR", "CODER_BRIEF"),
}


class SpawnError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, NO_CONTEXT, MISSING_LAYER}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        if kind in ("REFUSED", "NO_CONTEXT", "MISSING_LAYER"):
            try:
                from cosmos_warn import warn3
                warn3(kind, detail)
            except Exception:  # noqa: BLE001
                pass
        super().__init__(f"[{kind}] {detail}")


@dataclass
class SpawnSpec:
    """Role + Wrapper + Skills + Tools + Params. Empty fields are missing."""

    role: str = ""
    model: str = ""
    wrapper_paths: list = field(default_factory=list)
    skill_names: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    params: dict = field(default_factory=dict)
    filled: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA,
            "role": self.role,
            "model": self.model,
            "wrapper_paths": list(self.wrapper_paths),
            "skill_names": list(self.skill_names),
            "tools": list(self.tools),
            "params": dict(self.params),
            "filled": list(self.filled),
        }


def _as_spec(spec) -> SpawnSpec:
    if spec is None:
        return SpawnSpec()
    if isinstance(spec, SpawnSpec):
        return spec
    if not isinstance(spec, dict):
        raise SpawnError("BAD_INPUT", "SpawnSpec must be an object")
    return SpawnSpec(
        role=str(spec.get("role") or "").strip(),
        model=str(spec.get("model") or "").strip(),
        wrapper_paths=list(spec.get("wrapper_paths") or []),
        skill_names=list(spec.get("skill_names") or []),
        tools=list(spec.get("tools") or []),
        params=dict(spec.get("params") or {}),
    )


def _require_file(path: Path, layer: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise SpawnError("MISSING_LAYER", f"{layer} missing: {p}")
    return str(p)


def _load_wrap(role: str) -> str:
    name = str(role or "").strip() or DEFAULT_ROLE
    return _require_file(WRAP_DIR / name, f"WRAP/{name}")


def _load_style(model: str) -> str:
    name = str(model or "").strip()
    if name:
        pinned = STYLES_DIR / name
        if pinned.is_file():
            return str(pinned)
    return _require_file(STYLES_DIR / "_TEMPLATE", "STYLES/_TEMPLATE")


def defaults(role: str = "", model: str = "") -> SpawnSpec:
    """Load WRAP/{role}, STYLES/{model} or _TEMPLATE, default skills.

    CCr session f47bad79 is always preloaded as an Agent Roles wrapper.
    Missing WRAP/STYLES is MISSING_LAYER — never a silent skip.
    """
    r = str(role or "").strip() or DEFAULT_ROLE
    m = str(model or "").strip()
    skills = ROLE_SKILLS.get(r)
    if skills is None:
        raise SpawnError(
            "MISSING_LAYER",
            f"no default skills for role {r!r} (want {sorted(ROLE_SKILLS)})")
    wrap_role = _load_wrap(r)
    wrap_ccr = _load_wrap(CCR_ROLE)
    style = _load_style(m)
    wrappers = [wrap_role]
    if wrap_ccr not in wrappers:
        wrappers.append(wrap_ccr)
    return SpawnSpec(
        role=r,
        model=m,
        wrapper_paths=wrappers,
        skill_names=list(skills),
        tools=[],
        params={
            "ccr_session": CCR_SESSION,
            "style_path": style,
        },
    )


def apply(spec) -> SpawnSpec:
    """Fill missing layers from defaults. Never silent-skip a hole."""
    cur = _as_spec(spec)
    filled = []
    role = cur.role
    if not role:
        role = DEFAULT_ROLE
        filled.append("role")
    model = cur.model
    if not model:
        filled.append("model")
    base = defaults(role, model)
    wrappers = [str(p).strip() for p in (cur.wrapper_paths or []) if str(p).strip()]
    if not wrappers:
        wrappers = list(base.wrapper_paths)
        filled.append("wrapper_paths")
    for p in wrappers:
        _require_file(Path(p), "wrapper_paths")
    skills = [str(s).strip() for s in (cur.skill_names or []) if str(s).strip()]
    if not skills:
        skills = list(base.skill_names)
        filled.append("skill_names")
    tools = [str(t).strip() for t in (cur.tools or []) if str(t).strip()]
    if not list(cur.tools or []):
        tools = list(base.tools)
        filled.append("tools")
    params = dict(cur.params) if cur.params else {}
    if not cur.params:
        params = dict(base.params)
        filled.append("params")
    if "ccr_session" not in params:
        params["ccr_session"] = CCR_SESSION
        filled.append("params.ccr_session")
    return SpawnSpec(
        role=role,
        model=model,
        wrapper_paths=wrappers,
        skill_names=skills,
        tools=tools,
        params=params,
        filled=filled,
    )


def require_context_list(value) -> list:
    """Context source must be a list. Concat string with ' · ' is NO_CONTEXT."""
    if isinstance(value, str) and CTX_CONCAT in value:
        raise SpawnError(
            "NO_CONTEXT",
            "concatenated Context source refused "
            f"(string contains {CTX_CONCAT!r})")
    if not isinstance(value, list):
        raise SpawnError("NO_CONTEXT", "Context source must be a list")
    return value


def spec_from_order(order: dict) -> SpawnSpec:
    raw = order if isinstance(order, dict) else {}
    require_context_list(raw.get("Context source"))
    extra = raw.get("spawn") or raw.get("_spawn") or {}
    if not isinstance(extra, dict):
        extra = {}
    role = extra.get("role") or raw.get("role") or raw.get("Role") or ""
    model = extra.get("model") or ""
    agent = raw.get("_agent")
    if not model and isinstance(agent, dict):
        model = agent.get("version") or ""
    return SpawnSpec(
        role=str(role or "").strip(),
        model=str(model or "").strip(),
        wrapper_paths=list(extra.get("wrapper_paths") or []),
        skill_names=list(extra.get("skill_names") or []),
        tools=list(extra.get("tools") or []),
        params=dict(extra.get("params") or {}),
    )


def apply_order(order: dict) -> SpawnSpec:
    """Fill spawn layers on a work order. Concat CTX refuses here."""
    return apply(spec_from_order(order))


def _bu_says_resume(text: str) -> bool:
    low = str(text or "").lower()
    if "resume" in low:
        return True
    if "[tasks]" in low or "task_list" in low:
        return True
    return False


def _seed_says_resume(obj) -> bool:
    if not isinstance(obj, dict):
        return False
    if obj.get("kind") == "COSMOS_SEED":
        return True
    if obj.get("resume") in (True, "true", "all", "resume"):
        return True
    facts = obj.get("facts")
    watchers = obj.get("watchers")
    if isinstance(facts, dict) and facts:
        return True
    if isinstance(watchers, dict) and watchers:
        return True
    return False


def preflight_session(paths) -> dict:
    """If SEED/BU says resume, return {need_resume: true}. GET never mkdir.

    Caller runs session start. This fold only reads existing files.
    """
    state = paths.role("state")
    seed = state / "SEED.json"
    bu = state / "BUCm.toml"
    seed_present = seed.is_file()
    bu_present = bu.is_file()
    need = False
    if seed_present:
        try:
            raw = json.loads(seed.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            raw = None
        need = _seed_says_resume(raw) or raw is None
    if not need and bu_present:
        try:
            text = bu.read_text(encoding="utf-8")
        except OSError:
            text = ""
        need = _bu_says_resume(text)
    return {
        "schema": SCHEMA,
        "need_resume": bool(need),
        "seed": "PRESENT" if seed_present else "ABSENT",
        "bu": "PRESENT" if bu_present else "ABSENT",
        "note": "GET never mkdir. Caller runs session start when need_resume.",
    }


def refuse(argv) -> None:
    """Refuse extra grok.exe / grok --single as a work-order worker."""
    parts = [str(a) for a in (argv or [])]
    names = [Path(p).name.lower() for p in parts]
    if any("grok.exe" in p.lower().replace("\\", "/") for p in parts):
        raise SpawnError(
            "REFUSED",
            "extra grok.exe as WO worker")
    if "grok" in names and "--single" in parts:
        raise SpawnError(
            "REFUSED",
            "grok --single as WO worker")


def fail_xfer(paths, rec: dict, kind: str, detail: str) -> dict:
    """Move a work order to failed/. Append the attempt. Do not spawn.

    Partner autopsy is recorded on the corpse. A miss is UNMEASURED.
    GAC_RESEAT drops one follow-up JSON. It does not start a scheduler.
    The corpse is copied to the attempt archive and left in failed/.
    """
    from cosmos_work_order import order_file, work_order_dirs

    dirs = work_order_dirs(paths)
    oid = str((rec or {}).get("order_id") or "order")
    out = dict(rec or {})
    out["order_id"] = oid
    out["state"] = "FAILED"
    out["fail_kind"] = kind
    out["fail_detail"] = detail
    try:
        from cosmos_judge_run import autopsy_fail
        out.update(autopsy_fail(paths, out, kind, detail))
    except Exception as e:  # noqa: BLE001 — the move still happens
        out["wo_partner"] = {
            "partner_id": None,
            "partner_state": "UNMEASURED",
            "kind": "UNMEASURED",
        }
        out["partner_id"] = None
        out["partner_state"] = "UNMEASURED"
        out["xfer"] = "superseded"
        out["follow_up_oid"] = None
        out["attempt_kind"] = "UNMEASURED"
        out["autopsy_error"] = "%s: %s" % (type(e).__name__, e)[:200]
    dest = order_file(dirs["failed"], oid)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    tmp.replace(dest)
    for name in ("picked", "bucket"):
        stale = order_file(dirs[name], oid)
        if stale.is_file() and stale.resolve() != dest.resolve():
            try:
                stale.unlink()
            except OSError:
                pass
    try:
        from cosmos_judge_run import archive_corpse
        out["archive"] = archive_corpse(paths, out)
    except Exception as e:  # noqa: BLE001
        out["archive"] = {"ok": False, "kind": type(e).__name__, "detail": str(e)[:200]}
    return out


def _selftest() -> int:
    """3 VERIFY: missing role → CODER; concat CTX refuses; grok argv refuses."""
    import tempfile

    from cosmos_paths import CosmosPaths, write_sentinel

    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    filled = apply(SpawnSpec())
    check("VERIFY 1 missing role fills default CODER",
          lambda: filled.role == DEFAULT_ROLE
          and "role" in filled.filled
          and any(Path(p).name == DEFAULT_ROLE for p in filled.wrapper_paths)
          and any(Path(p).name == CCR_ROLE for p in filled.wrapper_paths)
          and filled.params.get("ccr_session") == CCR_SESSION)

    concat_kind = None
    try:
        require_context_list(
            "docs/AGENT_BRIEF.md · docs/AGENT_BOUNDARIES.md")
    except SpawnError as e:
        concat_kind = e.kind
    check("VERIFY 2 concat CTX refuses NO_CONTEXT",
          lambda: concat_kind == "NO_CONTEXT")

    grok_kind = None
    try:
        refuse(["grok", "--single", "task", "-m", "grok-4.6"])
    except SpawnError as e:
        grok_kind = e.kind
    exe_kind = None
    try:
        refuse([r"C:\Users\Papa\.grok\bin\grok.exe", "--cwd", "x"])
    except SpawnError as e:
        exe_kind = e.kind
    check("VERIFY 3 grok argv refuses",
          lambda: grok_kind == "REFUSED" and exe_kind == "REFUSED")

    td = Path(tempfile.mkdtemp(prefix="cosmos_spawn_"))
    live = td / "live"
    write_sentinel(live, tree_id="spawn-selftest")
    paths = CosmosPaths(live)
    state = paths.role("state")
    before = list(state.glob("*")) if state.exists() else []
    snap0 = preflight_session(paths)
    after = list(state.glob("*")) if state.exists() else []
    check("preflight GET never mkdir",
          lambda: snap0["need_resume"] is False
          and snap0["seed"] == "ABSENT"
          and snap0["bu"] == "ABSENT"
          and before == after
          and not (state / "SEED.json").exists()
          and not (state / "BUCm.toml").exists())

    state.mkdir(parents=True, exist_ok=True)
    (state / "SEED.json").write_text(json.dumps({
        "kind": "COSMOS_SEED",
        "schema": "cosmos-session-seed/1",
        "facts": {"carry": "1"},
    }), encoding="utf-8")
    snap1 = preflight_session(paths)
    check("SEED carry-over is need_resume",
          lambda: snap1["need_resume"] is True and snap1["seed"] == "PRESENT")

    listed = require_context_list(["docs/AGENT_BRIEF.md"])
    check("list Context source accepted",
          lambda: listed == ["docs/AGENT_BRIEF.md"])

    order_kind = None
    try:
        apply_order({
            "Context source": "docs/A.md · docs/B.md",
            "Task": "x",
        })
    except SpawnError as e:
        order_kind = e.kind
    check("apply_order concat CTX is typed NO_CONTEXT",
          lambda: order_kind == "NO_CONTEXT")

    applied = apply_order({
        "Context source": ["docs/AGENT_BRIEF.md"],
        "Task": "x",
        "_agent": {"version": "glm-5.3-flash"},
    })
    check("apply_order missing role is CODER and records the fill",
          lambda: applied.role == "CODER"
          and "role" in applied.filled
          and applied.model == "glm-5.3-flash")

    hole = None
    try:
        apply(SpawnSpec(role="CODER", wrapper_paths=["/no/such/WRAP"]))
    except SpawnError as e:
        hole = e.kind
    check("missing wrapper is MISSING_LAYER not a silent skip",
          lambda: hole == "MISSING_LAYER")

    ok_codex = True
    try:
        refuse(["codex", "exec", "--sandbox", "workspace-write"])
    except SpawnError:
        ok_codex = False
    check("codex argv is not a grok WO refuse", lambda: ok_codex)

    bad = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(results) - len(bad)}/{len(results)} passed")
    return 1 if bad else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return _selftest()
    print("usage: py -3.14 cosmos\\cosmos_spawn.py --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
