#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summon an OpenRouter :free HERO: legend PREFIX + TASK tail, named pin only."""
from __future__ import annotations

import argparse
import json
import os
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, r"V:\A\Ai\COSMOS\cosmos")
from cosmos_openrouter_rail import OpenRouterRail  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402


def _cat(pack: Path, name: str) -> str:
    p = pack / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


NEED = ("AGENTS.md", "WRAP.md", "STYLE.md", "SKILL.md", "TASK.md")


def verify_pack(pack: Path, duds_path: Path, model: str) -> dict:
    """Full outfit before any model call. Incomplete refuses. No HTTP."""
    from cosmos_duds import require_duds
    if not duds_path.is_file():
        raise SystemExit("REFUSED no duds file " + str(duds_path))
    rec = json.loads(duds_path.read_text(encoding="utf-8"))
    duds = require_duds(rec, repo=Path(r"V:\A\Ai\COSMOS"))
    if duds["l2_model"] != model:
        raise SystemExit(
            "REFUSED model " + model + " != pack l2_model " + duds["l2_model"])
    harness = duds["l3_harness"].lower()
    if "openrouter" not in harness and "summon_or_hero" not in harness:
        raise SystemExit("REFUSED harness is not this script: " + duds["l3_harness"])
    missing = [name for name in NEED if not (pack / name).is_file()
               or not (pack / name).read_text(encoding="utf-8").strip()]
    if missing:
        raise SystemExit("REFUSED pack files missing: " + ",".join(missing))
    return duds


WRITE_TOOL = {
    "type": "function",
    "function": {
        "name": "write",
        "description": "Write one file inside this worktree. path is a file name, not an absolute path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
}


def _safe_write(pack: Path, path: str, content: str) -> str:
    from hero_unify import jail_write
    try:
        dest = jail_write(pack, path, content)
    except Exception as e:
        return "REFUSED path " + type(e).__name__ + ": " + str(e).splitlines()[-1][:160]
    name = dest.name
    bad = _check_written(dest)
    if bad:
        return "Error: " + bad
    return "wrote " + name


def _check_math(dest: Path, text: str) -> str:
    """Sample bar: compute e, pi, sqrt(2), stdev, and variance. A typed constant is not a calculation."""
    import math
    import re
    low = text.lower()
    if re.search(r"3\.14159\d*", text) and "math.pi" not in low and "atan" not in low:
        return dest.name + " pi is a typed constant; compute it"
    if re.search(r"1\.41421\d*", text) and "math.sqrt" not in low and "**0.5" not in text and "**(1/2)" not in text:
        return dest.name + " sqrt(2) is a typed constant; compute it"
    if re.search(r"\b(e|pi|s2|sqrt2)\s*=", text) and "math.e" not in low and "math.pi" not in low:
        ns: dict = {}
        try:
            exec(compile(text, str(dest), "exec"), ns)
        except Exception as e:
            return dest.name + " " + type(e).__name__ + ": " + str(e).splitlines()[-1][:160]
        want = {"e": math.e, "pi": math.pi, "s2": math.sqrt(2), "sqrt2": math.sqrt(2)}
        for key, target in want.items():
            fn = ns.get(key)
            if fn is None:
                continue
            got = fn() if callable(fn) else fn
            if isinstance(got, (int, float)) and abs(float(got) - target) > 1e-6:
                return dest.name + " " + key + " got " + str(got) + " want " + str(target)
    if "statistics" in low or "stdev" in low or "variance" in low or "stat" in dest.name.lower():
        calls_sd = re.search(r"\b(stdev|pstdev)\s*\(", text)
        calls_var = re.search(r"\b(variance|pvariance)\s*\(", text)
        if not calls_sd or not calls_var:
            return dest.name + " imports only; call stdev and variance on a set"
    return ""


def _check_written(dest: Path) -> str:
    """Reject a write that does not run, or a fib file with the wrong values."""
    text = dest.read_text(encoding="utf-8")
    math_bad = _check_math(dest, text)
    if math_bad:
        return math_bad
    if "fib" in dest.name.lower():
        import importlib.util
        try:
            spec = importlib.util.spec_from_file_location("fibcheck", dest)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            fn = getattr(mod, "fib", None) or getattr(mod, "f", None)
            if fn is None:
                return dest.name + " has no fib function"
            got = [fn(i) for i in range(6)]
        except Exception as e:
            return dest.name + " " + type(e).__name__ + ": " + str(e).splitlines()[-1][:160]
        if got != [0, 1, 1, 2, 3, 5]:
            return dest.name + " fib got " + str(got) + " want [0, 1, 1, 2, 3, 5]"
    import subprocess
    try:
        proc = subprocess.run(
            [sys.executable, str(dest)],
            capture_output=True, text=True, timeout=2,
            creationflags=0x08000000 if os.name == "nt" else 0,
        )
    except subprocess.TimeoutExpired:
        return dest.name + " did not finish in 2s"
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "failed").strip().splitlines()
        return dest.name + " " + (err[-1] if err else "failed")
    return ""


def _run_tools(pack: Path, calls: list) -> list[dict]:
    rows = []
    for tc in calls:
        fn = tc.get("function") if isinstance(tc, dict) else {}
        if not isinstance(fn, dict):
            continue
        name = str(fn.get("name") or "")
        raw_args = fn.get("arguments") or {}
        if isinstance(raw_args, dict):
            args = raw_args
        else:
            try:
                args = json.loads(raw_args or "{}")
            except json.JSONDecodeError:
                args = {}
        if name != "write":
            detail = "REFUSED unknown tool"
        else:
            detail = _safe_write(pack, str(args.get("path") or ""), str(args.get("content") or ""))
        rows.append({
            "role": "tool",
            "tool_call_id": tc.get("id") or "",
            "content": detail,
        })
    return rows


def _sha(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:16]


def _wire(pack: Path, system_instruction: str, task: str, model: str, allow: dict) -> dict:
    """What this call put on the wire. Hashes, not a second engine."""
    offered = ["write"] if "write" in (allow.get("allow") or []) else []
    forbid = [str(x) for x in (allow.get("forbid") or [])]
    rec = {
        "runner": "_summon_or_hero.py",
        "model_requested": model,
        "system_sha": _sha(system_instruction),
        "system_is_wrap": system_instruction == _cat(pack, "WRAP.md"),
        "style_in_system": _cat(pack, "STYLE.md") in system_instruction and bool(_cat(pack, "STYLE.md")),
        "skill_in_system": _cat(pack, "SKILL.md") in system_instruction and bool(_cat(pack, "SKILL.md")),
        "user_sha": _sha(task),
        "user_is_task": task == _cat(pack, "TASK.md"),
        "tools_offered": offered,
        "forbid_offered": [name for name in forbid if name in offered],
        "writes_serial": True,
        "call_order": "system=WRAP, user=TASK, tools, then tool-result loop",
    }
    (pack / "wire.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def _py_first(line: str) -> bool:
    return line.startswith(("```", "'''", "#", "import ", "from ", "def ", "class "))


def _is_ping_reply(mouth: str) -> bool:
    """A ping reply: NONE then HERO_OK <slug>."""
    lines = mouth.splitlines()
    return bool(lines) and lines[0].strip() == "NONE" and len(lines) >= 2 and lines[1].strip().startswith("HERO_OK")


def grade_pack(pack: Path, mouth: str, model_returned: str) -> dict:
    """CPU grade after the call. Does not trust hero_ok. Not a layer tracker."""
    wire = {}
    wire_path = pack / "wire.json"
    if wire_path.is_file():
        wire = json.loads(wire_path.read_text(encoding="utf-8"))
    first = (mouth.splitlines() or [""])[0]
    wrote = [
        p.name for p in pack.iterdir()
        if p.is_file() and p.suffix == ".py" and p.name != "mouth.py"
    ]
    inside = not bool(wrote) or all(
        (pack / name).resolve().is_relative_to(pack.resolve()) for name in wrote
    )
    # Missing wire is not a pass. The runner's own ok flag is not read here.
    is_ping = _is_ping_reply(mouth)
    layers = {
        "l1_role": _py_first(first) or (first.strip() == "NONE" and is_ping),
        "l2_model": bool(wire) and model_returned == wire.get("model_requested"),
        "l3_harness": wire.get("runner") == "_summon_or_hero.py",
        "l4_wrapper": wire.get("system_is_wrap") is True and wire.get("style_in_system") is False,
        "l5_skills": bool(wire) and wire.get("skill_in_system") is False,
        "l6_tools": wire.get("tools_offered") == ["write"] and not wire.get("forbid_offered"),
        "l7_enviro": inside,
        "l8_mission": wire.get("user_is_task") is True and (_py_first(first) or is_ping),
    }
    applied = all(layers.values())
    rec = {
        "applied": applied,
        "layers": layers,
        "first_line": first[:80],
        "model_returned": model_returned,
        "note": "applied is the bound call plus a reply that obeyed it. HTTP ok is not this.",
    }
    (pack / "grade.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--duds", required=True,
                    help="JSON outfit. require_duds must pass before HTTP.")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--routing", default=None,
                    help="off|floor|nitro|exacto. :free defaults to off (no :floor).")
    ap.add_argument("--ping", default=None,
                    help="Replace TASK.md with NONE / HERO_OK <slug> ping.")
    ap.add_argument("--prefill-none", action="store_true",
                    help="Assistant prefill NONE newline (class-6 CoT mouths).")
    ap.add_argument("--max-tokens", type=int, default=2048,
                    help="Visible+reasoning budget. 256 starves reasoning models.")
    ap.add_argument("--reasoning-effort", default=None,
                    help="none|low|medium|high|max — OpenRouter reasoning.effort")
    ap.add_argument("--reasoning-max-tokens", type=int, default=None,
                    help="Cap reasoning so visible tokens remain (NVIDIA/Anthropic).")
    a = ap.parse_args()
    pack = Path(a.pack)
    duds = verify_pack(pack, Path(a.duds), a.model)
    # Call order: wrapper is the system instruction. Mission is the user
    # turn. Tools are the next layer, not a later sentence in the prompt.
    # STYLE must not follow the wrapper; it was canceling the tool call.
    task = _cat(pack, "TASK.md")
    if a.ping:
        task = "Reply with exactly two lines:\nNONE\nHERO_OK " + a.ping + "\n"
    system_instruction = _cat(pack, "WRAP.md") or _cat(pack, "AGENTS.md")
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": task},
    ]
    text = system_instruction + "\n\n" + task
    root = Path(r"V:\A\Ai\COSMOS\live")
    key = CosmosPaths(root).config("openrouter_api_key.txt")
    rail = OpenRouterRail(key)
    routing = a.routing
    if routing is None and ":free" in a.model:
        routing = "off"
    trace_id = str(duds.get("l2_model") or a.model).split("/")[-1][:40]
    trace_id = "hero-" + trace_id + "-" + str(pack.name)
    payload = {
        "model": a.model,
        "messages": messages,
        "max_tokens": int(a.max_tokens),
        "session_id": trace_id[:256],
        "trace": {
            "trace_id": trace_id[:256],
            "trace_name": "HERO " + str(a.model),
            "span_name": "tool-loop",
        },
    }
    rsn = {}
    if a.reasoning_effort:
        rsn["effort"] = a.reasoning_effort
    if a.reasoning_max_tokens:
        rsn["max_tokens"] = int(a.reasoning_max_tokens)
    if rsn:
        payload["reasoning"] = rsn
    if routing is not None:
        payload["routing"] = routing
    allow = duds.get("l6_tools") or {}
    if "write" in (allow.get("allow") or []):
        payload["tools"] = [WRITE_TOOL]
        if "write" in task.lower():
            payload["tool_choice"] = "required"
            payload["require_tool_provider"] = True
    if a.prefill_none:
        payload["messages"] = [
            {"role": "user", "content": text},
            {"role": "assistant", "content": "NONE\n"},
        ]
    paths = CosmosPaths(root)
    wire = _wire(pack, system_instruction, task, a.model, allow)
    if a.prefill_none:
        wire["system_is_wrap"] = False
        wire["prefill_dropped_system"] = True
        (pack / "wire.json").write_text(json.dumps(wire, indent=1) + "\n", encoding="utf-8")
    log_path = pack / "harness_log.jsonl"
    wrote = []
    rec = rail.dispatch(payload, paths=paths)
    detail = str(rec.get("detail") or "")
    if rec.get("http") == 404 and "tool_choice" in detail:
        payload.pop("tool_choice", None)
        payload.pop("require_tool_provider", None)
        rec = rail.dispatch(payload, paths=paths)
        detail = str(rec.get("detail") or "")
    max_loops = 6
    for step in range(1, max_loops + 1):
        calls = rec.get("tool_calls") or []
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "step": step,
                "http": rec.get("http"),
                "n_tools": len(calls),
                "detail": detail[:180],
            }) + "\n")
        if not calls:
            break
        messages.append({
            "role": "assistant",
            "content": rec.get("text") or None,
            "tool_calls": calls,
        })
        results = _run_tools(pack, calls)
        for row in results:
            if str(row.get("content") or "").startswith("wrote "):
                wrote.append(row["content"][6:])
        messages.extend(results)
        follow = dict(payload)
        follow.pop("text", None)
        follow["tool_choice"] = "auto"
        follow["messages"] = messages
        rec = rail.dispatch(follow, paths=paths)
        detail = str(rec.get("detail") or "")
    out = Path(a.out)
    mouth = rec.get("text") or rec.get("content") or rec.get("detail") or ""
    if not isinstance(mouth, str):
        mouth = json.dumps(rec, default=str)[:4000]
    out.write_text(str(mouth), encoding="utf-8", newline="\n")
    ok = bool(rec.get("ok"))
    model = rec.get("model") or rec.get("model_requested")
    first = (str(mouth).splitlines() or [""])[0]
    graded = grade_pack(pack, str(mouth), str(model or ""))
    print(json.dumps({
        "ok": ok, "kind": rec.get("kind"), "model": model,
        "first_line": first[:80], "out": str(out),
        "pack_verified": True,
        "applied": graded["applied"],
        "layers": graded["layers"],
        "hero_ok": _py_first(first),
        "session_model": duds["l2_model"],
        "tools_sent": "write" in (allow.get("allow") or []),
        "wrote": wrote,
        "call_order": "system=WRAP, user=TASK, tools, then tool-result loop",
    }))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
