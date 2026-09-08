#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_forge_bg — background CLI free-coders for Forge MOTIF steps.

Research / ARCH / CONSENSUS only. Named OpenRouter :free pins, not the
rotator. Worker is a detached CLI process. Does not write the live tree.
Does not start IMPLEMENT. Consensus uses the bar saved on the Forge skin.

    py -3.14 cosmos\\cosmos_forge_bg.py --selftest
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-forge-bg/1"
BG_STAGES = frozenset({"research", "arch", "consensus1", "consensus2"})
MAX_N = 5
FALLBACK_FREE = (
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
)


class ForgeBgError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def bg_dir(paths, stage: str) -> Path:
    return paths.state("profiles", "forge", "bg", stage)


def pick_free_coders(paths, n: int = 3, http=None) -> list[str]:
    n = max(1, min(int(n or 3), MAX_N))
    ids = []
    try:
        from cosmos_model_rater import snapshot
        rec = snapshot(paths, sort="coding", type_name="free", limit=40)
        for m in rec.get("models") or []:
            mid = str(m.get("id") or "")
            if ":free" not in mid.lower():
                continue
            if "openrouter/free" in mid.lower() or mid.lower() == "openrouter/auto":
                continue
            ids.append(mid)
            if len(ids) >= n:
                break
    except Exception:  # noqa: BLE001
        ids = []
    for pin in FALLBACK_FREE:
        if pin not in ids:
            ids.append(pin)
        if len(ids) >= n:
            break
    return ids[:n]


def _setup(engine: dict, stage: str) -> dict:
    src = engine.get("step_setup") if isinstance(engine.get("step_setup"), dict) else {}
    raw = src.get(stage) if isinstance(src.get(stage), dict) else {}
    bar = str(raw.get("bar") or "majority").strip().lower()
    if bar not in ("plurality", "majority", "complete"):
        bar = "majority"
    choice = str(raw.get("arch_choice") or "auto").strip().lower()
    if choice not in ("auto", "hitl"):
        choice = "auto"
    try:
        n_free = int(raw.get("n_free") or 3)
    except (TypeError, ValueError):
        n_free = 3
    n_free = max(1, min(n_free, MAX_N))
    return {"bar": bar, "arch_choice": choice, "n_free": n_free, "via": "cli"}


def status(paths, stage: str = "") -> dict:
    stages = [stage] if stage in BG_STAGES else sorted(BG_STAGES)
    out = {}
    for sid in stages:
        d = bg_dir(paths, sid)
        runs = []
        if d.is_dir():
            for fp in sorted(d.glob("run-*.json")):
                try:
                    rec = json.loads(fp.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    rec = {"kind": "BROKE", "path": fp.name}
                if isinstance(rec, dict):
                    runs.append({
                        "id": rec.get("id") or fp.stem,
                        "model": rec.get("model"),
                        "ok": rec.get("ok"),
                        "kind": rec.get("kind"),
                        "pid": rec.get("pid"),
                        "saved_at": rec.get("saved_at"),
                        "ballot": rec.get("ballot"),
                    })
        fac = None
        facp = d / "consensus.json"
        if facp.is_file():
            try:
                fac = json.loads(facp.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                fac = {"kind": "BROKE"}
        out[sid] = {"n": len(runs), "runs": runs[-12:], "consensus": fac}
    return {"schema": SCHEMA, "ok": True, "stages": out}


def facilitate(paths, stage: str, engine: dict) -> dict:
    if stage not in BG_STAGES:
        raise ForgeBgError("REFUSED", f"bg CLI not for stage {stage!r}")
    setup = _setup(engine, stage)
    from cosmos_studio import bar_met
    rows = status(paths, stage)["stages"].get(stage, {}).get("runs") or []
    done = [r for r in rows if r.get("ok") is True and r.get("ballot")]
    ballots = {}
    for r in done:
        b = str(r.get("ballot") or "")
        ballots[b] = ballots.get(b, 0) + 1
    ranked = sorted(ballots.items(), key=lambda kv: (-kv[1], kv[0]))
    winner_n = ranked[0][1] if ranked else 0
    second = ranked[1][1] if len(ranked) > 1 else 0
    n = max(len(done), 1)
    met = bool(ranked) and bar_met(winner_n, n, setup["bar"], second)
    rec = {
        "schema": SCHEMA,
        "stage": stage,
        "bar": setup["bar"],
        "arch_choice": setup["arch_choice"],
        "n_done": len(done),
        "n_runs": len(rows),
        "winner": ranked[0][0] if ranked else None,
        "winner_n": winner_n,
        "met": met,
        "kind": "OK" if met else "CONTESTED",
        "via": "cli",
        "saved_at": _iso(),
        "note": "HITL if arch_choice=hitl — this fold does not pick ARCH.",
    }
    d = bg_dir(paths, stage)
    d.mkdir(parents=True, exist_ok=True)
    try:
        from cosmos_porosity import hook_trial
        axis = str((setup.get("axis") or "coding")).strip() or "coding"
        hooked = hook_trial(
            paths,
            [{"model": r.get("model"), "ballot": r.get("ballot"),
              "tokens": r.get("n_chars")} for r in done],
            profile="forge", stage=stage, axis=axis,
            trial_id=str(rec.get("saved_at") or ""),
        )
        rec["porosity"] = hooked
    except Exception as e:  # noqa: BLE001
        rec["porosity"] = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    (d / "consensus.json").write_text(
        json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return rec


def start(paths, stage: str, *, n: int | None = None, http=None) -> dict:
    if stage not in BG_STAGES:
        raise ForgeBgError("REFUSED",
                           "background free CLI is RESEARCH / ARCH / CONSENSUS only")
    from cosmos_profiles import load_engine
    engine = load_engine(paths, "forge")
    text = str((engine.get("define") or {}).get("text") or "").strip()
    if not text:
        raise ForgeBgError("REFUSED",
                           "PROBLEM STATEMENT / STATED GOAL empty — RESEARCH does not start")
    setup = _setup(engine, stage)
    n_free = n if n is not None else setup["n_free"]
    models = pick_free_coders(paths, n_free, http=http)
    note = str((engine.get("stages") or {}).get(stage) or "")
    prompt = (
        "FORGE MOTIF stage %s. CLI background. Named free coder. "
        "Do not write the COSMOS live tree. Return one short ballot line "
        "then your answer.\n\nSTATEMENT:\n%s\n\nSETUP:\n%s\n"
        % (stage, text[:8000], note[:4000])
    )
    d = bg_dir(paths, stage)
    d.mkdir(parents=True, exist_ok=True)
    prompt_fp = d / "prompt.txt"
    prompt_fp.write_text(prompt, encoding="utf-8")
    spawned = []
    from cosmos_clock import pythonw_exe, spawn_detached, repo_tree
    worker = str(Path(__file__).resolve())
    root = str(paths.root)
    for i, model in enumerate(models, 1):
        out = d / ("run-%s-%d.json" % (stage, int(time.time()) + i))
        argv = [pythonw_exe(), worker, "--worker",
                "--root", root, "--stage", stage,
                "--model", model, "--prompt", str(prompt_fp),
                "--out", str(out)]
        rec = spawn_detached(argv, str(repo_tree()), d / "worker.out")
        spawned.append({
            "model": model, "via": "cli",
            "pid": rec.get("pid"), "ok": bool(rec.get("ok")),
            "out": str(out.name),
        })
    return {
        "schema": SCHEMA,
        "ok": True,
        "stage": stage,
        "setup": setup,
        "spawned": spawned,
        "does_not_write_live_tree": True,
        "does_not_start_implement": True,
    }


def worker_main(argv: list[str]) -> int:
    import argparse
    from cosmos_paths import CosmosPaths
    from cosmos_openrouter_rail import OpenRouterRail, KEY_NAME, model_refused

    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--root", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if ns.stage not in BG_STAGES:
        return 2
    why = model_refused(ns.model)
    rec = {
        "schema": SCHEMA, "id": Path(ns.out).stem, "stage": ns.stage,
        "model": ns.model, "via": "cli", "saved_at": _iso(),
    }
    if why:
        rec.update({"ok": False, "kind": "REFUSED", "detail": why})
    else:
        prompt = Path(ns.prompt).read_text(encoding="utf-8", errors="replace")
        paths = CosmosPaths(ns.root)
        rail = OpenRouterRail(paths.config(KEY_NAME))
        ans = rail.dispatch({"model": ns.model, "text": prompt, "max_tokens": 800})
        text = str(ans.get("text") or "")
        ballot = (text.strip().splitlines() or [""])[0][:200]
        rec.update({
            "ok": bool(ans.get("ok")),
            "kind": ans.get("kind") or ("OK" if ans.get("ok") else "BROKE"),
            "http": ans.get("http"),
            "model_bound": ans.get("model"),
            "ballot": ballot,
            "n_chars": len(text),
        })
    Path(ns.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return 0 if rec.get("ok") else 1


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_profiles import save_engine

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_forge_bg_"))
    root = install(td / "live", tree_id="spike-forge-bg")
    paths = CosmosPaths(root)
    refused = False
    try:
        start(paths, "research")
    except ForgeBgError as e:
        refused = e.kind == "REFUSED"
    check("empty statement REFUSED before RESEARCH", lambda: refused)
    save_engine(paths, {"profile": "forge",
                        "define": {"text": "WHAT: bg free CLI. WHY: test."},
                        "step_setup": {"research": {"bar": "majority", "n_free": 2}}})
    build = False
    try:
        start(paths, "build")
    except ForgeBgError as e:
        build = e.kind == "REFUSED"
    check("BUILD is not a bg free-CLI stage", lambda: build)
    models = pick_free_coders(paths, 2)
    check("picker returns named :free pins, not the rotator",
          lambda: len(models) >= 2
          and all(":free" in m or m in FALLBACK_FREE for m in models)
          and "openrouter/free" not in models)
    d = bg_dir(paths, "consensus1")
    d.mkdir(parents=True, exist_ok=True)
    models = ("google/gemma-4-26b-a4b-it:free",
              "google/gemma-4-31b-it:free",
              "qwen/qwen3-32b:free")
    for i, (b, m) in enumerate(zip(("A", "A", "B"), models, strict=True), 1):
        (d / ("run-x-%d.json" % i)).write_text(json.dumps({
            "id": "r%d" % i, "ok": True, "ballot": b, "model": m,
        }), encoding="utf-8")
    from cosmos_profiles import load_engine
    fac = facilitate(paths, "consensus1", load_engine(paths, "forge"))
    check("majority 2/3 meets the Forge bar; rotator never sat",
          lambda: fac["met"] is True and fac["winner"] == "A"
          and fac["bar"] == "majority")
    check("facilitate writes orthogonal porosity pairs (UNMEASURED mag until error)",
          lambda: isinstance(fac.get("porosity"), dict)
          and fac["porosity"].get("n_written") == 3
          and fac["porosity"].get("kind") == "OK")

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Forge bg free CLI; no IMPLEMENT)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--worker" in sys.argv:
        raise SystemExit(worker_main(sys.argv[1:]))
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    raise SystemExit(2)
