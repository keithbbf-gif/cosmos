#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P10 RTB: dispatch a FRESH GEM + OA critique of the CVM desktop clock.

Does not edit COSMOS core or the live tree. Dispatch goes through
cosmos_dispatch.py (the applied execute_handoff worker path). Artifacts
and BIND.json land in this directory.

Proof is nonempty model text, not rc=0.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LIVE = ROOT / "live"
HERE = Path(__file__).resolve().parent
DISPATCH = ROOT / "cosmos" / "cosmos_dispatch.py"
CLOCK = ROOT / "builds" / "cvm-dt" / "cvm_dt_clock.py"
TEST = ROOT / "builds" / "cvm-dt" / "test_cvm_dt_clock.py"
README = ROOT / "builds" / "cvm-dt" / "README.md"
ARCH = ROOT / "docs" / "CVM_ARCH.md"
CRIT_DIR = ROOT / "docs" / "critique"
CF = 0x08000000 if os.name == "nt" else 0
WAIT_S = 900.0
POLL_S = 5.0


def _iso() -> str:
    return datetime.now().astimezone().isoformat()


def _clip(p: Path, n: int = 24000) -> str:
    if not p.exists():
        return f"(MISSING {p})"
    t = p.read_text(encoding="utf-8", errors="replace")
    if len(t) <= n:
        return t
    return t[:n] + f"\n\n…[truncated {len(t) - n} bytes of {p.name}]"


def critique_task(agent: str, link_id: str, dest_name: str) -> str:
    """API rails cannot read the tree — the packet carries the source."""
    return (
        f"You are {agent} performing a MOTIF STAGE-5 CRITIQUE for COSMOS — a "
        f"DIFFERENT-FAMILY review (the builder was G46/Grok; your value is that "
        f"you can DISAGREE, not restate). Target: the CVM DESKTOP CLOCK "
        f"(builds/cvm-dt/cvm_dt_clock.py) — the windowless own-clock that drives "
        f"CvmDtClient.cycle_once on a Windows Task Scheduler / pythonw --loop, "
        f"NOT the voice client itself and NOT the phone clock.\n\n"
        f"PROPOSE-ONLY (P10): do NOT write any files. Your entire reply IS the "
        f"markdown critique that COSMOS will file to docs/critique/{dest_name}. "
        f"Start with heading '# cvmdt - Motif stage-5 critique ({link_id})'. "
        f"No JSON wrapper, no preamble about being an AI.\n\n"
        f"GRADE HARD against the clock's own contract and CVM_ARCH H-constraints:\n"
        f"- H2 satellite: heartbeat + projection only; never a second scheduler/SEED/ledger/HTTP authority\n"
        f"- H3 typed refusal (UNREACHABLE / AUDIO_NONE) — never a silent fail; heartbeat still advances\n"
        f"- H5 keep-her-afloat: no Core edit; Core :8770 stays up\n"
        f"- H6 exactly ONE AUDIO_OWNER; DT never writes the owner file as authority\n"
        f"- H10 real OS clock: schtasks floor 1 min; faster = detached daemon + 1-min self-heal; logged-on only; CLOCK_ID in source is 17 (own_clocks next was 15 — flag drift)\n"
        f"- Runtime-binding named in the module docstring: heartbeat last_run_epoch advances across two native ticks AND state/cvm/pull.json cursor advances under THIS clock with NO human turn and NO Claude process. rc=0 is not the gate.\n"
        f"- Pause contract: HOLD / RESUME-GATE same as runners (idle the cycle, keep heartbeat; paused != dead). --once drain even while paused.\n"
        f"- register() EMITS schtasks /Create and must NOT run it.\n"
        f"- skip_alive by unique clock_id so a second launch no-ops.\n"
        f"- P8 elegance: reuse one HTTP stack (core_get/pull_url), one heartbeat writer, one pause contract. Flag dead code, duplication, hot-path cost.\n\n"
        f"For EACH finding: PASS/FAIL + exact file:line or missing surface. "
        f"HIGH/MED/LOW. End with a GATE-READINESS verdict: is the desktop clock "
        f"ready for stage-6 runtime-binding, or what must change first. Bind every "
        f"claim to a real artifact; UNKNOWN is allowed, fabricated compliance is not.\n\n"
        f"LIVE OBSERVATIONS at dispatch (quote, do not invent):\n"
        f"- live/logs/ has cvm_clock_heartbeat.json (clock id 15/16 family) but NO cvm_dt_clock_heartbeat.json — the DT own-clock is not ticking natively.\n"
        f"- live/state/cvm/pull.json audio_owner='none', core_kind='UNREACHABLE', clock_id=16 (not 17).\n"
        f"- PAUSE.flag state=RUNNING (COW auto-resume 2026-08-27T01:50).\n"
        f"- test_cvm_dt_clock.py is loopback (fake Core); rc=0 there is a green log.\n\n"
        f"SOURCE PACKET follows.\n\n"
        f"===== builds/cvm-dt/cvm_dt_clock.py =====\n"
        f"{_clip(CLOCK, 28000)}\n\n"
        f"===== builds/cvm-dt/test_cvm_dt_clock.py =====\n"
        f"{_clip(TEST, 16000)}\n\n"
        f"===== builds/cvm-dt/README.md (first 80 lines; this README is the VOICE CLIENT, not the clock) =====\n"
        f"{_clip(README, 4000)}\n\n"
        f"===== docs/CVM_ARCH.md H-constraints excerpt =====\n"
        f"{_clip(ARCH, 5000)}\n"
    )


def run_dispatch(agent: str, kind: str, task: str, label: str) -> dict:
    """Call cosmos_dispatch.dispatch in-process.

    Windows CreateProcess MAX_PATH/arg length rejects a CLI --task that
    carries the source packet (WinError 206). The CLI is argparse around
    this same function; label is the short DHx/filename, task is the body.
    """
    sys.path.insert(0, str(ROOT / "cosmos"))
    from cosmos_dispatch import DispatchError, dispatch  # noqa: E402

    t0 = time.time()
    rec = {
        "agent": agent,
        "kind": kind,
        "label": label,
        "task_chars": len(task),
        "via": "cosmos_dispatch.dispatch (in-process; CLI --task overflows Win32)",
        "stamp": _iso(),
        "stderr": "",
    }
    try:
        parsed = dispatch(
            agent, task, str(ROOT),
            lane="cm", kind=kind,
            runtime_root=str(LIVE),
            label=label,
        )
        rec["rc"] = 0
        rec["dispatch"] = parsed
    except DispatchError as e:
        rec["rc"] = 2
        rec["stderr"] = f"{e.kind}: {e}"
        rec["dispatch"] = {"ok": False, "kind": e.kind, "error": str(e)}
    except Exception as e:  # noqa: BLE001
        rec["rc"] = 2
        rec["stderr"] = f"{type(e).__name__}: {e}"
        rec["dispatch"] = None
    rec["secs"] = round(time.time() - t0, 3)
    return rec


def job_status(job_file: str) -> dict:
    cmd = [
        "py", "-3.14", str(DISPATCH),
        "--root", str(LIVE),
        "--status", job_file,
    ]
    p = subprocess.run(
        cmd, cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        creationflags=CF,
    )
    try:
        return json.loads(p.stdout or "")
    except ValueError:
        return {
            "ok": False,
            "rc_status": p.returncode,
            "stdout": (p.stdout or "")[-2000:],
            "stderr": (p.stderr or "")[-2000:],
        }


def wait_jobs(jobs: dict, timeout_s: float = WAIT_S) -> dict:
    deadline = time.time() + timeout_s
    last = {}
    while time.time() < deadline:
        all_term = True
        for key, rec in jobs.items():
            jf = ((rec.get("dispatch") or {}).get("job_file")
                  or rec.get("job_file"))
            if not jf:
                rec["wait_error"] = "no job_file from dispatch"
                last[key] = rec
                continue
            st = job_status(jf)
            rec["status"] = st
            last[key] = rec
            if not st.get("terminal"):
                all_term = False
        if all_term:
            break
        time.sleep(POLL_S)
    return last


def collect_body(rec: dict) -> dict:
    """Find the real model text, wherever execute_handoff landed it."""
    st = rec.get("status") or {}
    result = st.get("result") if isinstance(st.get("result"), dict) else {}
    returns_path = (
        (rec.get("dispatch") or {}).get("returns_path")
        or st.get("returns_path")
        or result.get("returns_path")
        or result.get("stdout_full")
    )
    found = {
        "returns_path": returns_path,
        "stdout_full": result.get("stdout_full") or st.get("stdout_full"),
        "worker_packet": result.get("worker_packet"),
        "worker_result": result.get("worker_result"),
        "done": result.get("done"),
        "done_why": result.get("done_why"),
        "rc": st.get("rc") if st.get("rc") is not None else result.get("rc"),
        "secs": result.get("secs") or result.get("elapsed_s"),
        "model": result.get("model") or (result.get("rail") or {}).get("model"),
        "link_id": result.get("link_id") or (result.get("rail") or {}).get("link_id"),
        "error": result.get("error") or rec.get("stderr"),
        "text": "",
        "text_bytes": 0,
        "text_source": None,
    }
    candidates = []
    if found["stdout_full"]:
        candidates.append(("stdout_full", Path(found["stdout_full"])))
    if returns_path:
        rp = Path(str(returns_path))
        candidates.append(("returns.stdout.txt", Path(str(rp) + ".stdout.txt")))
        candidates.append(("returns.json", rp))
    wr = result.get("worker_result")
    if wr:
        candidates.append(("worker_result", Path(str(wr))))
    text = ""
    src = None
    for label, p in candidates:
        if not p or not p.exists() or not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix == ".json" or p.name.endswith(".json"):
            try:
                obj = json.loads(raw)
            except ValueError:
                obj = None
            if isinstance(obj, dict):
                rail = obj.get("rail") or {}
                blob = (rail.get("text") or obj.get("stdout_tail")
                        or obj.get("text") or "")
                if blob and str(blob).strip():
                    text, src = str(blob), label + ":rail.text"
                    found["model"] = found["model"] or obj.get("model") or rail.get("model")
                    found["link_id"] = found["link_id"] or obj.get("link_id") or rail.get("link_id")
                    break
            continue
        if raw.strip():
            text, src = raw, str(p)
            break
    # last-ditch: result.stdout_tail / rail.text already in status json
    if not text.strip():
        tail = result.get("stdout_tail") or (result.get("rail") or {}).get("text") or ""
        if str(tail).strip():
            text, src = str(tail), "status.result.stdout_tail"
    found["text"] = text
    found["text_bytes"] = len(text.encode("utf-8")) if text else 0
    found["text_source"] = src
    found["nonempty"] = bool(text.strip())
    return found


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    gem_task = critique_task("GEM (Gemini)", "gem-api", "cvmdt_CRITIQUE_gem-api.md")
    oa_task = critique_task("OAi (OpenAI)", "oa-api", "cvmdt_CRITIQUE_oa-api.md")
    (HERE / "GEM_TASK.txt").write_text(gem_task, encoding="utf-8")
    (HERE / "OA_TASK.txt").write_text(oa_task, encoding="utf-8")

    pre = {
        "ts": _iso(),
        "crit_gem_exists": (CRIT_DIR / "cvmdt_CRITIQUE_gem-api.md").exists(),
        "crit_oa_exists": (CRIT_DIR / "cvmdt_CRITIQUE_oa-api.md").exists(),
        "oa_bucket_exists": (LIVE / "buckets" / "oa").exists(),
        "gem_bucket_exists": (LIVE / "buckets" / "gem").exists(),
    }
    (HERE / "pre_state.json").write_text(json.dumps(pre, indent=1), encoding="utf-8")

    print("DISPATCH GEM", flush=True)
    gem = run_dispatch(
        "GEM", "gem", gem_task,
        "cvmdt clock motif stage-5 critique gem-api")
    (HERE / "dispatch_gem.json").write_text(json.dumps(gem, indent=1, default=str),
                                            encoding="utf-8")
    print(json.dumps({
        "gem_rc": gem.get("rc"),
        "gem_job": (gem.get("dispatch") or {}).get("job_file"),
        "gem_timeout": (gem.get("dispatch") or {}).get("timeout_s"),
        "gem_error": gem.get("stderr", "")[:400],
        "gem_parse": bool(gem.get("dispatch")),
    }, indent=1), flush=True)

    print("DISPATCH OA", flush=True)
    oa = run_dispatch(
        "OAi", "oa", oa_task,
        "cvmdt clock motif stage-5 critique oa-api")
    (HERE / "dispatch_oa.json").write_text(json.dumps(oa, indent=1, default=str),
                                           encoding="utf-8")
    print(json.dumps({
        "oa_rc": oa.get("rc"),
        "oa_job": (oa.get("dispatch") or {}).get("job_file"),
        "oa_timeout": (oa.get("dispatch") or {}).get("timeout_s"),
        "oa_error": oa.get("stderr", "")[:400],
        "oa_parse": bool(oa.get("dispatch")),
    }, indent=1), flush=True)

    jobs = {"gem": gem, "oa": oa}
    print("WAIT", flush=True)
    waited = wait_jobs(jobs, WAIT_S)
    (HERE / "wait_status.json").write_text(
        json.dumps(waited, indent=1, default=str), encoding="utf-8")

    bodies = {k: collect_body(v) for k, v in waited.items()}
    (HERE / "bodies.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "text"}
                    | {"text_head": (v.get("text") or "")[:400],
                       "text_len": len(v.get("text") or "")}
                    for k, v in bodies.items()}, indent=1, default=str),
        encoding="utf-8")

    summary = {
        "ts": _iso(),
        "gem": {
            "dispatch_rc": gem.get("rc"),
            "dispatch_stderr": (gem.get("stderr") or "")[:1500],
            "job_file": (gem.get("dispatch") or {}).get("job_file"),
            "timeout_s": (gem.get("dispatch") or {}).get("timeout_s"),
            "kind": (gem.get("dispatch") or {}).get("kind"),
            "terminal": (gem.get("status") or {}).get("terminal"),
            "state": (gem.get("status") or {}).get("state"),
            "rc": (gem.get("status") or {}).get("rc"),
            **{k: bodies["gem"].get(k) for k in (
                "done", "done_why", "model", "link_id", "text_bytes",
                "text_source", "nonempty", "returns_path", "stdout_full",
                "worker_packet", "error", "secs")},
        },
        "oa": {
            "dispatch_rc": oa.get("rc"),
            "dispatch_stderr": (oa.get("stderr") or "")[:1500],
            "job_file": (oa.get("dispatch") or {}).get("job_file"),
            "timeout_s": (oa.get("dispatch") or {}).get("timeout_s"),
            "kind": (oa.get("dispatch") or {}).get("kind"),
            "terminal": (oa.get("status") or {}).get("terminal"),
            "state": (oa.get("status") or {}).get("state"),
            "rc": (oa.get("status") or {}).get("rc"),
            **{k: bodies["oa"].get(k) for k in (
                "done", "done_why", "model", "link_id", "text_bytes",
                "text_source", "nonempty", "returns_path", "stdout_full",
                "worker_packet", "error", "secs")},
        },
        "pre": pre,
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1, default=str),
                                       encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str), flush=True)

    # Copy bodies into the RTB dir (never fabricate). Landing docs/critique
    # is done by the parent after this script if nonempty.
    for key, dest in (("gem", "cvmdt_CRITIQUE_gem-api.md"),
                      ("oa", "cvmdt_CRITIQUE_oa-api.md")):
        text = bodies[key].get("text") or ""
        if text.strip():
            (HERE / dest).write_text(text, encoding="utf-8")
        else:
            (HERE / (dest + ".MISSING.txt")).write_text(
                json.dumps(bodies[key], indent=1, default=str), encoding="utf-8")

    ok = bodies["gem"]["nonempty"] and bodies["oa"]["nonempty"]
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
