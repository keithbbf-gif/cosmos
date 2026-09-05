#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: stage-7 runtime-binding gate (pipeline C1-C5).

A GATE IS SOMETHING THAT RUNS. rc=0 is not the gate. The live_value object
is. GitLab / default (no --live) MUST keep live_gate_closed=false and MUST
NOT print GATE_CLOSED.

    py -3.14 -B tests/test_runtime_binding.py
        C1 echo positives + negatives + C4 children. headline=L1_ONLY.

    py -3.14 -B tests/test_runtime_binding.py --live --root <handed-in>
        C1 task read-back + C2 counts + C3 pairs + C4 + C5a.
        GATE_CLOSED only if all five pass on this machine, including
        machine_count == registry_count and reds==0.

Does not write live/. Does not schtasks /create /delete /change. Does not
import Kernel / Ledger / Sched / Service to decide the live gate. Does not
standup. Optional --live-run may schtasks /run existing names (not a tree
write). Optional --live-rehearse --backup --scratch adds C5b/C5c.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

RESULTS: list[tuple[str, bool, str]] = []
LIVE_VALUE: dict = {}
SCHEMA = "cosmos-runtime-bind-gate/1"
ECHO_SCHEMA = "cosmos-runtime-bind-echo/1"
ECHO_NAME = "runtime_bind_echo.py"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
SENTINEL_NAME = ".cosmos-root.json"
TREE_ID = "KMesh-COSMOS-live"
CHILD_TIMEOUT_S = 180

FORBIDDEN_TR = (
    r"\live\cosmos\adapter_jobs",
    r"\live\cosmos\dispatch_jobs",
    r"\_delme\\",
    r"\trylive\\",
    r"\work\orders\\",
    r"\AppData\Roaming\Claude\\",
)

C4_CHILDREN = (
    "tests/test_v1.py",
    "tests/test_wave3.py",
    "tests/test_wave4.py",
    "tests/test_kernel.py",
    "tests/test_core.py",
    "tests/test_own_clocks.py",
    "tests/test_live_write_fence.py",
)


class BindError(RuntimeError):
    """kind names the snapshot class. Branch on kind, never on the message."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except BindError as e:
        RESULTS.append((label, False, f"{e.kind}: {e}"))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def echo_path() -> Path:
    return repo_root() / "tests" / ECHO_NAME


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_digest(nonce: str, source: Path) -> str:
    return sha256_bytes(nonce.encode("utf-8") + b"\n" + source.read_bytes())


def spawn_env(extra: dict | None = None) -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra:
        env.update(extra)
    return env


def plant_challenge(dirpath: Path) -> dict:
    nonce = secrets.token_hex(16)
    t0 = time.time()
    rec = {
        "schema": SCHEMA,
        "nonce": nonce,
        "planted_epoch": t0,
        "planted_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
    }
    path = dirpath / "challenge.json"
    path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    rec["path"] = str(path)
    return rec


def spawn_echo(nonce_file: Path, script: Path, root: Path | None = None,
               extra_py: list[str] | None = None) -> dict:
    """FRESH interpreter. -B is required so a pyc cache cannot answer."""
    cmd = [sys.executable, "-B", str(script), "--nonce-file", str(nonce_file)]
    if extra_py:
        cmd[1:1] = extra_py
    if root is not None:
        cmd.extend(["--root", str(root)])
    t0 = time.time()
    p = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=30, env=spawn_env(),
        stdin=subprocess.DEVNULL, creationflags=NO_WINDOW,
        cwd=str(repo_root()),
    )
    out = (p.stdout or "").strip()
    try:
        body = json.loads(out) if out else {}
        if not isinstance(body, dict):
            body = {"raw": out[:500], "error": "MALFORMED"}
    except json.JSONDecodeError:
        body = {"raw": out[:500], "error": "MALFORMED"}
    body["_spawn"] = {
        "rc": p.returncode,
        "cmd": cmd,
        "stderr": (p.stderr or "")[:800],
        "parent_pid": os.getpid(),
        "elapsed_s": round(time.time() - t0, 3),
    }
    return body


def verify_echo(rec: dict, challenge: dict, expected_file: Path,
                parent_pid: int) -> dict:
    """Return proof, or raise. Never green on missing fields."""
    spawn = rec.get("_spawn") or {}
    required = ("pid", "epoch", "nonce", "bind_digest", "file",
                "loaded_sha256", "executable", "dont_write_bytecode",
                "version_info")
    missing = [k for k in required if k not in rec or rec.get(k) in (None, "")]
    if missing:
        raise BindError("GREEN_LOG", f"echo missing {missing}")
    if rec.get("schema") != ECHO_SCHEMA:
        raise BindError("SNAPSHOT_OLD",
                        f"schema={rec.get('schema')!r} (want {ECHO_SCHEMA})")
    if rec.get("nonce") != challenge["nonce"]:
        raise BindError("SNAPSHOT_OLD", "nonce does not match the planted challenge")
    child_pid = rec["pid"]
    if not isinstance(child_pid, int) or child_pid == parent_pid:
        raise BindError("SNAPSHOT_INPROC",
                        f"child pid {child_pid!r} is parent {parent_pid}")
    if float(rec["epoch"]) <= float(challenge["planted_epoch"]):
        raise BindError("SNAPSHOT_STALE",
                        "emit epoch is not after the challenge plant")
    if not rec.get("dont_write_bytecode"):
        raise BindError("SNAPSHOT_PYC", "child ran without -B / dont_write_bytecode")
    got_file = Path(str(rec["file"])).resolve()
    want_file = expected_file.resolve()
    if got_file != want_file:
        raise BindError("SNAPSHOT_PATH",
                        f"child __file__={got_file} want {want_file}")
    want_digest = expected_digest(challenge["nonce"], want_file)
    if rec.get("bind_digest") != want_digest:
        raise BindError("SNAPSHOT_BYTES",
                        "bind_digest does not match nonce + this tree's echo bytes")
    if rec.get("loaded_sha256") != sha256_file(want_file):
        raise BindError("SNAPSHOT_BYTES",
                        "loaded_sha256 is not the on-disk echo in this tree")
    vi = rec.get("version_info") or []
    if not (isinstance(vi, list) and len(vi) >= 2 and vi[0] == 3 and vi[1] == 14):
        raise BindError("SNAPSHOT_INTERPRETER",
                        f"version_info={vi!r} want Python 3.14")
    if rec.get("ok") is not True:
        raise BindError("SNAPSHOT_OLD", f"echo ok={rec.get('ok')!r}")
    if spawn.get("rc") not in (0, None):
        raise BindError("SNAPSHOT_OLD", f"child rc={spawn.get('rc')}")
    return {
        "ok": True,
        "child_pid": child_pid,
        "bind_digest": rec["bind_digest"],
        "loaded_sha256": rec["loaded_sha256"],
        "file": str(got_file),
        "epoch": rec["epoch"],
        "nonce": rec["nonce"],
        "executable": rec["executable"],
        "version": rec.get("version"),
        "dont_write_bytecode": rec.get("dont_write_bytecode"),
        "version_info": vi,
    }


def win_compact(s: str) -> str:
    """Collapse ConvertTo-Json doubled backslashes so TR/WMI paths compare."""
    t = str(s).replace("/", "\\")
    while "\\\\" in t:
        t = t.replace("\\\\", "\\")
    return t


def classify_tr(tr: str, repo: Path, live_root: Path | None) -> str | None:
    """Return a SNAPSHOT_* kind if Task To Run is not this tree, else None."""
    if not tr or not str(tr).strip():
        return "SNAPSHOT_TASK"
    compact = win_compact(tr)
    for needle in FORBIDDEN_TR:
        if needle.lower() in compact.lower():
            return "SNAPSHOT_PATH"
    repo_s = str(repo.resolve())
    cosmos = str((repo / "cosmos").resolve())
    builds = str((repo / "builds").resolve())
    tests = str((repo / "tests").resolve())
    py_paths = re.findall(r"(?i)(?:[A-Z]:\\[^\s\"]+\.py)", compact)
    if not py_paths:
        py_paths = re.findall(r'(?i)"([A-Z]:\\[^"]+\.py)"', compact)
    if not py_paths:
        return "SNAPSHOT_TASK"
    ok_one = False
    for p in py_paths:
        p = p.strip().strip('"')
        try:
            rp = str(Path(p).resolve())
        except (OSError, ValueError):
            return "SNAPSHOT_PATH"
        low = rp.lower()
        if (low.startswith(cosmos.lower()) or low.startswith(builds.lower())
                or low.startswith(tests.lower())):
            ok_one = True
        elif not low.startswith(repo_s.lower()):
            return "SNAPSHOT_PATH"
    if not ok_one:
        return "SNAPSHOT_PATH"
    if live_root is not None and "--root" in compact:
        got = extract_root(compact)
        if not got:
            return "SNAPSHOT_SPLIT"
        try:
            if Path(got).resolve() != Path(live_root).resolve():
                return "SNAPSHOT_SPLIT"
        except (OSError, ValueError):
            return "SNAPSHOT_SPLIT"
    if not re.search(r"(?i)python(?:w)?\.exe", compact):
        if not re.search(r"(?i)(?:py\.exe|py)\s+-3\.14", compact):
            return "SNAPSHOT_INTERPRETER"
    if "Python314" not in compact and "python3.14" not in compact.lower():
        if not re.search(r"(?i)(?:py\.exe|py)\s+-3\.14", compact):
            return "SNAPSHOT_INTERPRETER"
    return None


def parse_schtasks_list(text: str) -> dict:
    name = None
    tr = None
    for line in (text or "").splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        k = key.strip().lower()
        v = val.strip()
        if k == "taskname":
            name = v
        elif k == "task to run":
            tr = v
    return {"name": name, "tr": tr}


def extract_root(tr: str) -> str | None:
    m = re.search(r"(?i)--root\s+(\"([^\"]+)\"|\S+)", win_compact(tr or ""))
    if not m:
        return None
    return (m.group(2) or m.group(1)).strip('"')


def reader_writer_split(writer_tr: str, reader_tr: str, repo: Path) -> str | None:
    w_root = extract_root(writer_tr)
    r_root = extract_root(reader_tr)
    if w_root and r_root:
        try:
            if Path(w_root).resolve() != Path(r_root).resolve():
                return "SNAPSHOT_SPLIT"
        except (OSError, ValueError):
            return "SNAPSHOT_SPLIT"
    wk = classify_tr(writer_tr, repo, Path(w_root) if w_root else None)
    rk = classify_tr(reader_tr, repo, Path(r_root) if r_root else None)
    if wk:
        return wk
    if rk:
        return rk
    return None


def clock_names(clocks) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for spec in clocks:
        bundle = [spec["task"]]
        if spec.get("logon"):
            bundle.append(spec["logon"])
        bundle.extend(spec.get("extra_tasks") or [])
        for n in bundle:
            if n and n not in seen:
                seen.add(n)
                names.append(n)
    return names


def spec_script_path(repo: Path, spec: dict) -> Path:
    script = spec.get("script") or ""
    cand = repo / "cosmos" / script
    if cand.is_file():
        return cand
    cand = repo / script
    return cand


def _wmi_process(pid: int) -> dict:
    if os.name != "nt":
        raise BindError("UNMEASURED", "WMI is a Windows live-gate probe")
    ps = (
        "Get-CimInstance Win32_Process -Filter \"ProcessId=%d\" | "
        "Select-Object ProcessId,ExecutablePath,CommandLine,CreationDate | "
        "ConvertTo-Json -Compress"
    ) % int(pid)
    p = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=NO_WINDOW,
    )
    raw = (p.stdout or "").strip()
    if not raw:
        return {"pid": pid, "missing": True, "rc": p.returncode}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"pid": pid, "missing": True, "raw": raw[:400]}
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {"pid": pid, "missing": True}


def _wmi_serve() -> dict:
    if os.name != "nt":
        return {"missing": True, "error": "not-windows"}
    ps = (
        "Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -and $_.CommandLine -match 'cosmos\\.py' "
        "-and $_.CommandLine -match '\\sserve(\\s|$)' } | "
        "Select-Object ProcessId,ExecutablePath,CommandLine,CreationDate | "
        "ConvertTo-Json -Compress"
    )
    p = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=NO_WINDOW,
    )
    raw = (p.stdout or "").strip()
    if not raw:
        return {"missing": True, "rc": p.returncode}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"missing": True, "raw": raw[:400]}
    if isinstance(data, list):
        if not data:
            return {"missing": True}
        for item in data:
            cl = str((item or {}).get("CommandLine") or "")
            if "--port" in cl or "serve" in cl:
                data = item
                break
        else:
            data = data[0]
    return data if isinstance(data, dict) else {"missing": True}


def _creation_epoch(wmi: dict) -> float | None:
    raw = wmi.get("CreationDate")
    if not raw:
        return None
    s = str(raw)
    m = re.match(r"/Date\((\d+)\)/", s)
    if m:
        n = int(m.group(1))
        return (n / 1000.0) if n > 10_000_000_000 else float(n)
    try:
        ts = time.strptime(s[:14], "%Y%m%d%H%M%S")
        return time.mktime(ts)
    except (ValueError, OverflowError):
        return None


def probe_status(live_root: Path) -> dict:
    import urllib.request
    token_path = live_root / "config" / "api_token.txt"
    token = ""
    if token_path.is_file():
        token = token_path.read_text(encoding="utf-8").strip()
    req = urllib.request.Request("http://127.0.0.1:8770/api/v1/status")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            body["http_status"] = resp.status
            body["ok"] = True
            return body
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def live_sentinel_ok(repo: Path) -> Path | None:
    root = repo / "live"
    p = root / SENTINEL_NAME
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("system") != "COSMOS":
        return None
    return root.resolve()


def under_live(path: Path, live_root: Path) -> bool:
    try:
        path.resolve().relative_to(live_root.resolve())
        return True
    except (ValueError, OSError):
        return False


def child_selftest_pass(rel: str, out: str, rc: int) -> bool:
    if "SELFTEST PASS" in out:
        return True
    if rel.endswith("test_live_write_fence.py"):
        return rc == 0 and "LIVE_VALUE" in out
    if rel.endswith("test_own_clocks.py"):
        if rc != 0:
            return False
        m = re.search(r"(?m)^(\d+)/(\d+) passed\s*$", out)
        return bool(m and m.group(1) == m.group(2))
    return False


def run_c1_echo() -> dict:
    repo = repo_root()
    echo = echo_path()
    if not echo.is_file():
        raise BindError("UNMEASURED", f"missing {echo} — echo harness not filed")
    td = Path(tempfile.mkdtemp(prefix="cosmos_rtb_"))
    ch = plant_challenge(td)
    parent = os.getpid()

    rec = spawn_echo(Path(ch["path"]), echo)
    proof = verify_echo(rec, ch, echo, parent)
    check("C1 POSITIVE: child pid is not the suite pid (not in-process)",
          lambda: proof["child_pid"] != parent)
    check("C1 POSITIVE: bind_digest matches nonce + this tree's echo bytes",
          lambda: proof["bind_digest"] == expected_digest(ch["nonce"], echo))
    check("C1 POSITIVE: loaded_sha256 is the on-disk tests/runtime_bind_echo.py",
          lambda: proof["loaded_sha256"] == sha256_file(echo))
    check("C1 POSITIVE: child __file__ is the repo tests/ copy",
          lambda: Path(proof["file"]) == echo.resolve())
    check("C1 POSITIVE: emit epoch is after the challenge plant",
          lambda: float(rec["epoch"]) > float(ch["planted_epoch"]))
    check("C1 POSITIVE: Python 3.14",
          lambda: (rec.get("version_info") or [0, 0])[:2] == [3, 14])
    check("C1 POSITIVE: dont_write_bytecode (no pyc answering)",
          lambda: rec.get("dont_write_bytecode") is True)

    stub = td / "old_snapshot_echo.py"
    stub.write_text(
        "import json,os,time,sys\n"
        "print(json.dumps({'ok': True, 'pid': os.getpid(), 'epoch': time.time(),"
        "'file': __file__, 'loaded_sha256': '00', 'executable': sys.executable,"
        "'dont_write_bytecode': True, 'bind_digest': 'dead', 'schema': 'old'}))\n",
        encoding="utf-8",
    )
    old = spawn_echo(Path(ch["path"]), stub)
    old_kind = None
    try:
        verify_echo(old, ch, echo, parent)
    except BindError as e:
        old_kind = e.kind
    check("C1 NEGATIVE: old stub without nonce -> SNAPSHOT_OLD (or PATH/BYTES/GREEN_LOG)",
          lambda: old_kind in {"SNAPSHOT_OLD", "SNAPSHOT_PATH", "SNAPSHOT_BYTES",
                               "GREEN_LOG"})
    check("C1 NEGATIVE: detector FIRING is required (UNMEASURED if stub passes)",
          lambda: old_kind is not None)

    copied = td / ECHO_NAME
    copied.write_bytes(echo.read_bytes())
    copy_rec = spawn_echo(Path(ch["path"]), copied)
    copy_kind = None
    try:
        verify_echo(copy_rec, ch, echo, parent)
    except BindError as e:
        copy_kind = e.kind
    check("C1 NEGATIVE: echo copied off-tree -> SNAPSHOT_PATH (or BYTES)",
          lambda: copy_kind in {"SNAPSHOT_PATH", "SNAPSHOT_BYTES"})
    check("C1 NEGATIVE: off-tree copy does not green",
          lambda: copy_kind is not None)

    fake = dict(rec)
    fake["pid"] = parent
    inproc_kind = None
    try:
        verify_echo(fake, ch, echo, parent)
    except BindError as e:
        inproc_kind = e.kind
    check("C1 NEGATIVE: same-pid record -> SNAPSHOT_INPROC",
          lambda: inproc_kind == "SNAPSHOT_INPROC")

    stale = dict(rec)
    stale["epoch"] = float(ch["planted_epoch"]) - 5
    stale_kind = None
    try:
        verify_echo(stale, ch, echo, parent)
    except BindError as e:
        stale_kind = e.kind
    check("C1 NEGATIVE: pre-plant epoch -> SNAPSHOT_STALE",
          lambda: stale_kind == "SNAPSHOT_STALE")

    pyc = dict(rec)
    pyc["dont_write_bytecode"] = False
    pyc_kind = None
    try:
        verify_echo(pyc, ch, echo, parent)
    except BindError as e:
        pyc_kind = e.kind
    check("C1 NEGATIVE: dont_write_bytecode false -> SNAPSHOT_PYC",
          lambda: pyc_kind == "SNAPSHOT_PYC")

    empty_kind = None
    try:
        verify_echo({"ok": True, "pid": parent + 1}, ch, echo, parent)
    except BindError as e:
        empty_kind = e.kind
    check("C1 NEGATIVE: ok-without-fields -> GREEN_LOG",
          lambda: empty_kind == "GREEN_LOG")

    good_tr = (
        r"C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe "
        + '"' + str((repo / "cosmos" / "hush.py").resolve()) + '" '
        + '"' + str((repo / "cosmos" / "cosmos_watchdog2.py").resolve()) + '" '
        + "--root " + str((repo / "live").resolve()) + " --loop"
    )
    old_tr = (
        r"C:\Python314\pythonw.exe P:\old\cosmos_watchdog2.py "
        r"--root V:\A\Ai\COSMOS\live --loop"
    )
    rel_tr = r"pythonw.exe cosmos_watchdog2.py --root live --loop"
    snap_tr = (
        r"C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe "
        r"V:\A\Ai\COSMOS\live\cosmos\adapter_jobs\audit_0713__t180.py"
    )
    live_root = repo / "live"
    check("C1 FIXTURE: repo cosmos\\ + Python314 TR classifies clean",
          lambda: classify_tr(good_tr, repo, live_root) is None)
    check("C1 FIXTURE: P:\\old snapshot TR -> SNAPSHOT_PATH",
          lambda: classify_tr(old_tr, repo, live_root) == "SNAPSHOT_PATH")
    check("C1 FIXTURE: relative TR -> SNAPSHOT_TASK",
          lambda: classify_tr(rel_tr, repo, live_root) == "SNAPSHOT_TASK")
    check("C1 FIXTURE: live\\cosmos\\adapter_jobs TR -> SNAPSHOT_PATH",
          lambda: classify_tr(snap_tr, repo, live_root) == "SNAPSHOT_PATH")

    feed_tr = good_tr.replace("cosmos_watchdog2.py", "cosmos_cdeck_feed.py")
    split_tr = good_tr.replace(str((repo / "live").resolve()),
                               r"V:\A\Ai\COSMOS\trylive")
    check("C1 FIXTURE: feed TR shares writer --root (no split)",
          lambda: reader_writer_split(good_tr, feed_tr, repo) is None)
    check("C1 FIXTURE: reader --root trylive vs writer live -> SNAPSHOT_SPLIT",
          lambda: reader_writer_split(good_tr, split_tr, repo) == "SNAPSHOT_SPLIT")

    listed = parse_schtasks_list(
        "TaskName:                             \\COSMOS Watchdog2\n"
        "Task To Run:                          " + old_tr + "\n"
    )
    check("C1 FIXTURE: schtasks LIST parser reads Task To Run",
          lambda: listed["name"] and "old" in (listed["tr"] or "").lower())

    return {
        "ok": True,
        "nonce": ch["nonce"],
        "planted_epoch": ch["planted_epoch"],
        "child_pid": proof["child_pid"],
        "bind_digest": proof["bind_digest"],
        "file": proof["file"],
        "epoch": proof["epoch"],
        "child": proof,
        "tasks": [],
        "negative_kinds": {
            "old_stub": old_kind,
            "off_tree_copy": copy_kind,
            "inproc": inproc_kind,
            "stale": stale_kind,
            "pyc": pyc_kind,
            "green_log": empty_kind,
        },
        "scratch": str(td),
        "echo_sha256": sha256_file(echo),
        "repo": str(repo),
        "challenge_path": ch["path"],
    }


def run_c1_live(echo_rec: dict, live_root: Path, do_run: bool = False) -> dict:
    from cosmos_own_clocks import CLOCKS
    from cosmos_clock import (
        query_task, run_task, read_heartbeat, heartbeat_age_s, wait_fresh,
        pid_alive,
    )
    from cosmos_paths import CosmosPaths

    live_root = live_root.resolve()
    paths = CosmosPaths(live_root)
    repo = repo_root()
    planted = float(echo_rec.get("planted_epoch") or 0)
    rows = []
    for spec in CLOCKS:
        bundle = [spec["task"]]
        if spec.get("logon"):
            bundle.append(spec["logon"])
        bundle.extend(spec.get("extra_tasks") or [])
        hb = read_heartbeat(paths.logs() / spec["heartbeat"])
        age = heartbeat_age_s(hb)
        wmi = None
        mem_kind = None
        cmdline_kind = None
        if hb and isinstance(hb.get("pid"), int):
            try:
                wmi = _wmi_process(int(hb["pid"]))
            except BindError:
                wmi = {"pid": hb["pid"], "missing": True}
            created = _creation_epoch(wmi) if wmi and not wmi.get("missing") else None
            src = spec_script_path(repo, spec)
            if created is not None and src.is_file() and src.stat().st_mtime > created:
                mem_kind = "SNAPSHOT_MEMORY"
            cmdline = (wmi or {}).get("CommandLine") or ""
            if cmdline:
                cmdline_kind = classify_tr(cmdline, repo, live_root)
        for name in bundle:
            q = query_task(name)
            parsed = parse_schtasks_list(q.get("out") or "")
            kind = None
            registered = bool(q.get("ok"))
            if not registered:
                kind = None  # C2 red, not a C1 invented marker
            else:
                kind = classify_tr(parsed.get("tr") or "", repo, live_root)
            if do_run and registered:
                run_task(name)
            row = {
                "name": name,
                "clock": spec["clock"],
                "registered": registered,
                "query_rc": q.get("rc"),
                "tr": (parsed.get("tr") or "")[:500],
                "kind": kind,
                "heartbeat": spec["heartbeat"],
                "heartbeat_age_s": age,
                "heartbeat_pid": (hb or {}).get("pid"),
                "last_run_epoch": (hb or {}).get("last_run_epoch"),
                "pid_alive": (
                    pid_alive(int(hb["pid"]))
                    if hb and isinstance(hb.get("pid"), int) else False
                ),
                "memory_kind": mem_kind,
                "cmdline_kind": cmdline_kind,
                "alive_without_registration": bool(
                    not registered and hb and isinstance(hb.get("pid"), int)
                    and pid_alive(int(hb["pid"]))
                ),
            }
            rows.append(row)

    stale = None
    wd_hb = paths.logs() / "watchdog2_heartbeat.json"
    if wd_hb.is_file() and planted:
        stale = wait_fresh(wd_hb, timeout_s=20.0, min_epoch=planted)

    registered_rows = [r for r in rows if r["registered"]]
    dirty = [r for r in registered_rows if r.get("kind")]
    mem = [r for r in rows if r.get("memory_kind")]
    cmd_dirty = [r for r in rows if r.get("cmdline_kind") and r.get("heartbeat_pid")]
    check("C1 LIVE: sentinel-verified live root (CONTENT, not existence)",
          lambda: paths.sentinel.system == "COSMOS")
    check("C1 LIVE: every REGISTERED task TR classifies clean",
          lambda: not dirty)
    check("C1 LIVE: every live heartbeat pid CommandLine classifies clean",
          lambda: not cmd_dirty)
    check("C1 LIVE: no SNAPSHOT_MEMORY (CLOCKS script mtime > pid CreationDate)",
          lambda: not mem)
    echo_rec["tasks"] = rows
    echo_rec["stale_control"] = {
        "wait_fresh_ok": bool((stale or {}).get("ok")),
        "age_s": (stale or {}).get("age_s"),
        "note": "last_run_epoch is STALE control, not bytes identity",
    }
    echo_rec["live_ok"] = not dirty and not mem and not cmd_dirty
    echo_rec["tree_id"] = paths.sentinel.tree_id
    echo_rec["live_root"] = str(live_root)
    return echo_rec


def run_c2(live_root: Path, c1_tasks: list[dict] | None = None) -> dict:
    from cosmos_own_clocks import CLOCKS
    from cosmos_clock import query_task
    from cosmos_paths import CosmosPaths

    live_root = live_root.resolve()
    paths = CosmosPaths(live_root)
    repo = repo_root()
    names = clock_names(CLOCKS)
    rows = []
    reds = []
    if c1_tasks:
        by_name = {t.get("name"): t for t in c1_tasks}
        for name in names:
            t = by_name.get(name) or {}
            registered = bool(t.get("registered"))
            kind = t.get("kind")
            if not registered:
                kind = "SNAPSHOT_COUNT"
            row = {
                "name": name,
                "clock": t.get("clock"),
                "registered": registered,
                "tr": (t.get("tr") or "")[:500],
                "kind": kind,
                "query_rc": t.get("query_rc"),
            }
            rows.append(row)
            if kind:
                reds.append(row)
    else:
        for spec in CLOCKS:
            bundle = [spec["task"]]
            if spec.get("logon"):
                bundle.append(spec["logon"])
            bundle.extend(spec.get("extra_tasks") or [])
            for name in bundle:
                q = query_task(name)
                parsed = parse_schtasks_list(q.get("out") or "")
                registered = bool(q.get("ok"))
                kind = None
                if not registered:
                    kind = "SNAPSHOT_COUNT"
                else:
                    kind = classify_tr(parsed.get("tr") or "", repo, live_root)
                row = {
                    "name": name,
                    "clock": spec["clock"],
                    "registered": registered,
                    "tr": (parsed.get("tr") or "")[:500],
                    "kind": kind,
                    "query_rc": q.get("rc"),
                }
                rows.append(row)
                if kind:
                    reds.append(row)

    machine_count = sum(1 for r in rows if r["registered"])
    registry_count = len(names)
    rec = {
        "ok": (not reds) and machine_count == registry_count,
        "machine_count": machine_count,
        "registry_count": registry_count,
        "reds": len(reds),
        "names": names,
        "red_rows": [
            {"name": r["name"], "kind": r["kind"], "registered": r["registered"]}
            for r in reds[:50]
        ],
        "tree_id": paths.sentinel.tree_id,
        "note": (
            "C2 quotes integers, not cosmos_own_clocks --status rc. "
            "The suite does not standup and does not schtasks /create."
        ),
    }
    check("C2: machine_count == registry_count (quoted integers, not rc)",
          lambda: machine_count == registry_count)
    check("C2: reds == 0", lambda: not reds)
    check("C2: registry_count is CLOCKS task+logon+extra_tasks",
          lambda: registry_count == len(names) and registry_count > 0)
    return rec


def _pair_tr(rows: list[dict], name: str) -> dict | None:
    return next((r for r in rows if r.get("name") == name or r.get("task") == name),
                None)


def run_c3(live_root: Path, c1_tasks: list[dict], c2: dict) -> dict:
    from cosmos_paths import CosmosPaths

    live_root = live_root.resolve()
    paths = CosmosPaths(live_root)
    repo = repo_root()
    rows = c1_tasks or []
    pairs = []
    reds = []

    def member(name: str) -> dict:
        hit = _pair_tr(rows, name)
        if hit is None:
            return {"name": name, "registered": False, "tr": "", "missing": True}
        return hit

    def add_pair(pid: str, writer_name: str, reader_name: str,
                 writer_tr: str | None, reader_tr: str | None,
                 extra: dict | None = None) -> dict:
        w_miss = not writer_tr
        r_miss = not reader_tr
        split = None
        if w_miss or r_miss:
            split = "SNAPSHOT_COUNT"
        else:
            split = reader_writer_split(writer_tr or "", reader_tr or "", repo)
        rec = {
            "id": pid,
            "writer": writer_name,
            "reader": reader_name,
            "writer_root": extract_root(writer_tr or ""),
            "reader_root": extract_root(reader_tr or ""),
            "split": split,
            "missing_writer": w_miss,
            "missing_reader": r_miss,
        }
        if extra:
            rec.update(extra)
        pairs.append(rec)
        if split or w_miss or r_miss:
            reds.append(rec)
        return rec

    wd = member("COSMOS Watchdog2")
    feed = member("COSMOS cDeck Feed")
    wd_logon = member("COSMOS Watchdog2 Logon")
    feed_logon = member("COSMOS cDeck Feed Logon")
    wd_tr = (wd.get("tr") if wd.get("registered") else "") or (
        wd_logon.get("tr") if wd_logon.get("registered") else "")
    feed_tr = (feed.get("tr") if feed.get("registered") else "") or (
        feed_logon.get("tr") if feed_logon.get("registered") else "")
    add_pair("wd2-cdeck", "COSMOS Watchdog2", "COSMOS cDeck Feed",
             wd_tr if wd.get("registered") else None,
             feed_tr if feed.get("registered") else None,
             {"note": "missing 1-min member is a C3 red even if Logon leftover exists"})

    serve = _wmi_serve()
    status = probe_status(live_root)
    serve_cl = (serve or {}).get("CommandLine") or ""
    serve_root = extract_root(serve_cl)
    status_root = status.get("root") if status.get("ok") else None
    serve_split = None
    if serve.get("missing") or not serve_cl:
        serve_split = "SNAPSHOT_COUNT"
    elif not status.get("ok"):
        serve_split = "SNAPSHOT_COUNT"
    else:
        try:
            if serve_root and Path(serve_root).resolve() != live_root:
                serve_split = "SNAPSHOT_SPLIT"
            elif status_root and Path(str(status_root)).resolve() != live_root:
                serve_split = "SNAPSHOT_SPLIT"
            elif status.get("tree_id") != paths.sentinel.tree_id:
                serve_split = "SNAPSHOT_SPLIT"
            elif paths.sentinel.tree_id != TREE_ID:
                serve_split = "SNAPSHOT_SPLIT"
        except (OSError, ValueError):
            serve_split = "SNAPSHOT_SPLIT"
        ck = classify_tr(serve_cl, repo, live_root) if serve_cl else "SNAPSHOT_TASK"
        if ck:
            serve_split = ck
    serve_pair = {
        "id": "serve-status",
        "writer": "live serve process (WMI cosmos.py serve)",
        "reader": "GET /api/v1/status root + tree_id",
        "writer_root": serve_root,
        "reader_root": status_root,
        "status_tree_id": status.get("tree_id"),
        "sentinel_tree_id": paths.sentinel.tree_id,
        "split": serve_split,
        "note": "tree_id is install identity, not bytes identity",
    }
    pairs.append(serve_pair)
    if serve_split:
        reds.append(serve_pair)

    coll = member("COSMOS Collector")
    idx = member("COSMOS Index")
    add_pair("collector-index", "COSMOS Collector", "COSMOS Index",
             coll.get("tr") if coll.get("registered") else None,
             idx.get("tr") if idx.get("registered") else None)

    runner = member("COSMOS Runner")
    pool = member("COSMOS Runner Pool")
    slots = sorted(paths.logs().glob("cosmos_runner.slot*_heartbeat.json"))
    runner_ok = bool(runner.get("registered") or pool.get("registered"))
    slot_ok = bool(slots)
    run_split = None
    if not runner_ok or not slot_ok:
        run_split = "SNAPSHOT_COUNT"
    else:
        rtr = runner.get("tr") if runner.get("registered") else pool.get("tr")
        if rtr:
            rr = extract_root(rtr)
            if rr:
                try:
                    if Path(rr).resolve() != live_root:
                        run_split = "SNAPSHOT_SPLIT"
                except (OSError, ValueError):
                    run_split = "SNAPSHOT_SPLIT"
    run_pair = {
        "id": "runner-slots",
        "writer": "COSMOS Runner / Runner Pool",
        "reader": "live/logs/cosmos_runner.slot*_heartbeat.json",
        "writer_root": extract_root(
            (runner.get("tr") if runner.get("registered") else "")
            or (pool.get("tr") if pool.get("registered") else "")
        ),
        "reader_root": str(live_root),
        "slot_count": len(slots),
        "split": run_split,
        "missing_writer": not runner_ok,
        "missing_reader": not slot_ok,
    }
    pairs.append(run_pair)
    if run_split:
        reds.append(run_pair)

    feed_ui_tr = feed.get("tr") if feed.get("registered") else (
        feed_logon.get("tr") if feed_logon.get("registered") else "")
    feed_dir = paths.role("state") / "cdeck"
    feed_files = list(feed_dir.glob("*.json")) if feed_dir.is_dir() else []
    ui_split = None
    if not feed.get("registered"):
        ui_split = "SNAPSHOT_COUNT"
    else:
        fr = extract_root(feed_ui_tr)
        if fr:
            try:
                if Path(fr).resolve() != live_root:
                    ui_split = "SNAPSHOT_SPLIT"
            except (OSError, ValueError):
                ui_split = "SNAPSHOT_SPLIT"
    ui_pair = {
        "id": "feed-ui",
        "writer": "cDeck feed.json writer (cosmos_cdeck_feed)",
        "reader": "cDeck UI / KDash projection of that feed",
        "writer_root": extract_root(feed_ui_tr),
        "reader_root": str(live_root),
        "feed_files": len(feed_files),
        "split": ui_split,
        "missing_writer": not feed.get("registered"),
        "note": "do not point the panel at trylive while the writer is live",
    }
    pairs.append(ui_pair)
    if ui_split:
        reds.append(ui_pair)

    rec = {
        "ok": not reds,
        "pairs": pairs,
        "reds": len(reds),
        "c2_machine_count": c2.get("machine_count"),
        "c2_registry_count": c2.get("registry_count"),
    }
    check("C3: declared pairs iterated (not the present-task subset)",
          lambda: len(pairs) == 5)
    check("C3: no SNAPSHOT_SPLIT / missing pair member",
          lambda: not reds)
    if status.get("ok"):
        check("C3: GET /status tree_id matches sentinel (install identity, recorded)",
              lambda: status.get("tree_id") == paths.sentinel.tree_id)
    else:
        check("C3: GET /status probed (KERNEL_OFFLINE is a finding, not a skip)",
              lambda: False)
        RESULTS[-1] = (RESULTS[-1][0], False,
                       f"KERNEL_OFFLINE: {status.get('error')}")
    rec["status"] = {
        "ok": status.get("ok"),
        "tree_id": status.get("tree_id"),
        "ready": status.get("ready"),
        "root": status.get("root"),
        "error": status.get("error"),
        "http_status": status.get("http_status"),
    }
    rec["serve"] = {
        "pid": serve.get("ProcessId") or serve.get("pid"),
        "missing": bool(serve.get("missing")),
        "root": serve_root,
    }
    return rec


def run_c4(require_fence: bool) -> dict:
    repo = repo_root()
    kids = []
    for rel in C4_CHILDREN:
        script = repo / rel
        if rel.endswith("test_live_write_fence.py") and not require_fence:
            if live_sentinel_ok(repo) is None:
                kids.append({
                    "script": rel,
                    "rc": None,
                    "pid": None,
                    "selftest_pass": False,
                    "rehearse_ok": True,
                    "elapsed_s": 0,
                    "unmeasured": True,
                    "note": "live sentinel absent (GitLab/CI); fence not a default skip of GATE_CLOSED",
                })
                continue
        t0 = time.time()
        timed_out = False
        child_pid = None
        try:
            proc = subprocess.Popen(
                [sys.executable, "-B", str(script)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                env=spawn_env(), stdin=subprocess.DEVNULL,
                creationflags=NO_WINDOW, cwd=str(repo),
            )
            child_pid = proc.pid
            try:
                stdout, stderr = proc.communicate(timeout=CHILD_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                timed_out = True
            out = (stdout or "") + (stderr or "")
            rc = -1 if timed_out else int(
                proc.returncode if proc.returncode is not None else 0
            )
        except OSError as e:
            out = f"{type(e).__name__}: {e}"
            rc = -1
            timed_out = False
        passed = child_selftest_pass(rel, out, rc)
        rehearse_ok = True
        if rel.endswith("test_v1.py"):
            rehearse_ok = (
                "RESTORE REHEARSAL" in out
                and "RESTORE REHEARSAL runs and passes" in out
                and "tampered backup -> REHEARSAL_FAILED" in out
            )
        kid = {
            "script": rel,
            "rc": rc,
            "pid": child_pid,
            "selftest_pass": passed,
            "rehearse_ok": rehearse_ok,
            "elapsed_s": round(time.time() - t0, 3),
            "timeout": timed_out,
            "unmeasured": False,
        }
        kids.append(kid)
        check(f"C4: {rel} child rc=0", lambda r=rc: r == 0)
        check(f"C4: {rel} printed SELFTEST PASS (or suite live_value.ok)",
              lambda s=passed: s)
        if rel.endswith("test_v1.py"):
            check("C4: test_v1 child printed RESTORE REHEARSAL (rollback ran)",
                  lambda ok=rehearse_ok: ok)
            check("C4: test_v1 stdout contains GET /status ready over the wire",
                  lambda: "GET /status: ready over the wire" in out)
        if rel.endswith("test_live_write_fence.py"):
            check("C4: test_live_write_fence child rc=0 (LIVE_WRITE_FENCE holds)",
                  lambda r=rc: r == 0)

    measured = [k for k in kids if not k.get("unmeasured")]
    rec = {
        "ok": all(
            k["rc"] == 0 and k["selftest_pass"] and k.get("rehearse_ok", True)
            for k in measured
        ) and bool(measured),
        "children": kids,
        "note": "children of THIS tree; not in-process imports; not GitLab-only",
    }
    check("C4: the set of children is the module-together set, not a single file",
          lambda: [k["script"] for k in kids] == list(C4_CHILDREN))
    return rec


def run_c5a(c4: dict) -> dict:
    v1 = next((k for k in c4.get("children") or []
               if str(k.get("script", "")).endswith("test_v1.py")), None)
    ok = bool(v1 and v1.get("rc") == 0 and v1.get("rehearse_ok")
              and v1.get("selftest_pass"))
    rec = {
        "c5a_ok": ok,
        "script": (v1 or {}).get("script"),
        "rc": (v1 or {}).get("rc"),
        "rehearse_ok": (v1 or {}).get("rehearse_ok"),
    }
    check("C5a: test_v1 child of THIS tree ran Backup.rehearse_restore + tamper negative",
          lambda: ok)
    return rec


def run_c5_live(live_root: Path, backup: Path, scratch: Path) -> dict:
    repo = repo_root()
    live_root = live_root.resolve()
    backup = backup.resolve()
    scratch = scratch.resolve()
    if under_live(scratch, live_root):
        raise BindError("GREEN_LOG", f"C5b scratch resolves under live/: {scratch}")
    if scratch.exists() and any(scratch.iterdir()):
        raise BindError("UNMEASURED",
                        f"C5b scratch is occupied ({scratch}); refuse rather than overwrite")
    mf = backup / "_MANIFEST.sha256.json"
    if not mf.is_file():
        raise BindError("REHEARSAL_FAILED", f"no manifest at {mf}")
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    n_files = len(manifest)
    cli = repo / "cosmos" / "cosmos.py"
    cmd = [sys.executable, "-B", str(cli), "rehearse",
           "--root", str(live_root), "--backup", str(backup),
           "--scratch", str(scratch)]
    t0 = time.time()
    p = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=CHILD_TIMEOUT_S, env=spawn_env(),
        stdin=subprocess.DEVNULL, creationflags=NO_WINDOW, cwd=str(repo),
    )
    out = (p.stdout or "") + (p.stderr or "")
    passed_line = "RESTORE REHEARSAL PASSED:" in out
    n_ok = False
    if passed_line:
        m = re.search(r"RESTORE REHEARSAL PASSED:\s+(\d+)\s+files", out)
        n_ok = bool(m and int(m.group(1)) == n_files)
    c5b = {
        "rc": p.returncode,
        "elapsed_s": round(time.time() - t0, 3),
        "stdout_has_passed": passed_line,
        "files": n_files,
        "files_match": n_ok,
        "scratch": str(scratch),
        "backup": str(backup),
        "tail": out[-800:],
    }
    check("C5b: live CLI printed RESTORE REHEARSAL PASSED: N files",
          lambda: passed_line and n_ok and p.returncode == 0)
    check("C5b: scratch is not under live/",
          lambda: not under_live(scratch, live_root))

    tamper_root = scratch.parent / "_tamper_c5c"
    if tamper_root.exists():
        raise BindError("UNMEASURED", f"C5c tamper dir already exists: {tamper_root}")
    shutil.copytree(backup, tamper_root)
    victim = None
    for rel in manifest:
        cand = tamper_root / rel
        if cand.is_file() and cand.name != "_MANIFEST.sha256.json":
            victim = cand
            break
    if victim is None:
        raise BindError("UNMEASURED", "C5c: no file in backup copy to tamper")
    raw = victim.read_bytes() or b"x"
    victim.write_bytes(bytes((raw[0] ^ 0xFF,)) + raw[1:])
    tamper_scratch = scratch.parent / "_tamper_scratch_c5c"
    if tamper_scratch.exists() and any(tamper_scratch.iterdir()):
        raise BindError("UNMEASURED", "C5c tamper scratch occupied")
    cmd_t = [sys.executable, "-B", str(cli), "rehearse",
             "--root", str(live_root), "--backup", str(tamper_root),
             "--scratch", str(tamper_scratch)]
    pt = subprocess.run(
        cmd_t, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=CHILD_TIMEOUT_S, env=spawn_env(),
        stdin=subprocess.DEVNULL, creationflags=NO_WINDOW, cwd=str(repo),
    )
    out_t = (pt.stdout or "") + (pt.stderr or "")
    fired = (
        pt.returncode != 0
        and "REHEARSAL_FAILED" in out_t
        and "RESTORE REHEARSAL PASSED" not in out_t
    )
    c5c = {
        "rc": pt.returncode,
        "fired": fired,
        "victim": str(victim),
        "tail": out_t[-800:],
    }
    check("C5c: tampered copy raises REHEARSAL_FAILED and does not print PASSED",
          lambda: fired)

    echo_in_backup = list(tamper_root.rglob(ECHO_NAME))
    c5d = {"ok": None, "unmeasured": True,
           "note": "backup src is the state role, not the repo tree"}
    if echo_in_backup:
        c5d["unmeasured"] = False
        td = Path(tempfile.mkdtemp(prefix="cosmos_rtb_c5d_"))
        ch = plant_challenge(td)
        old = spawn_echo(Path(ch["path"]), echo_in_backup[0])
        kind = None
        try:
            verify_echo(old, ch, echo_path(), os.getpid())
        except BindError as e:
            kind = e.kind
        c5d["kind"] = kind
        c5d["ok"] = kind in {"SNAPSHOT_PATH", "SNAPSHOT_BYTES"}
        check("C5d: old-tree echo in backup is distinguishable from this tree",
              lambda: c5d["ok"])

    return {
        "c5b": c5b,
        "c5c_fired": fired,
        "c5c": c5c,
        "c5d": c5d,
        "ok": bool(passed_line and n_ok and p.returncode == 0 and fired),
    }


def decide_headline(live: bool, c1: dict, c2: dict | None, c3: dict | None,
                    c4: dict, c5: dict, live_rehearse: bool) -> tuple[str, bool]:
    """GATE_CLOSED only when --live and C1-C5 pass. Counts disagree → refuse."""
    if not live:
        return "L1_ONLY", False
    if c2 is None or c3 is None:
        return "PARTIAL", False
    if c2.get("machine_count") != c2.get("registry_count") or c2.get("reds"):
        return "GATE_OPEN", False
    c5a = bool(c5.get("c5a_ok"))
    c5_live_ok = True
    if live_rehearse:
        c5_live_ok = bool(c5.get("ok"))
    closed = (
        bool(c1.get("ok")) and bool(c1.get("live_ok", True))
        and bool(c2.get("ok"))
        and bool(c3.get("ok"))
        and bool(c4.get("ok"))
        and c5a and c5_live_ok
    )
    if not closed:
        return "GATE_OPEN", False
    return "GATE_CLOSED", True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="test-runtime-binding")
    ap.add_argument("--live", action="store_true",
                    help="C1 read-back + C2 counts + C3 pairs against a handed-in live root")
    ap.add_argument("--root", default=None,
                    help="live runtime root (required with --live); never inferred")
    ap.add_argument("--live-run", action="store_true",
                    help="also schtasks /run existing COSMOS tasks (not a tree write)")
    ap.add_argument("--stage7", action="store_true",
                    help="kept for Keith's command; C4 already runs on the default path")
    ap.add_argument("--live-rehearse", action="store_true",
                    help="C5b/C5c live CLI rehearsal; requires --backup and --scratch")
    ap.add_argument("--backup", default=None,
                    help="verified backup set (required with --live-rehearse); never inferred")
    ap.add_argument("--scratch", default=None,
                    help="empty scratch dir outside live/ (required with --live-rehearse)")
    ap.add_argument("--proof", default=None,
                    help="write live_value JSON (scratch, never live/)")
    a = ap.parse_args(argv)

    LIVE_VALUE.clear()
    RESULTS.clear()
    LIVE_VALUE["schema"] = SCHEMA
    LIVE_VALUE["headline"] = "L1_ONLY"
    LIVE_VALUE["live_gate_closed"] = False
    LIVE_VALUE["did_not_write_live_tree"] = True
    LIVE_VALUE["did_not_touch_core"] = True
    LIVE_VALUE["did_not_touch_kernel_ledger_sched_service"] = True
    LIVE_VALUE["did_not_schtasks_create"] = True

    if a.live and not a.root:
        raise SystemExit("--live requires --root (handed in, never inferred)")
    if a.live_rehearse and not a.live:
        raise SystemExit("--live-rehearse requires --live --root")
    if a.live_rehearse and (not a.backup or not a.scratch):
        raise SystemExit("--live-rehearse requires --backup and --scratch (never inferred)")

    live_root = Path(a.root).resolve() if a.root else None
    if a.proof and live_root and under_live(Path(a.proof), live_root):
        raise SystemExit("--proof must not resolve under live/")

    c1 = run_c1_echo()
    c2 = None
    c3 = None
    if a.live:
        assert live_root is not None
        c1 = run_c1_live(c1, live_root, do_run=bool(a.live_run))
        c2 = run_c2(live_root, c1.get("tasks") or [])
        c3 = run_c3(live_root, c1.get("tasks") or [], c2)

    c4 = run_c4(require_fence=bool(a.live) or live_sentinel_ok(repo_root()) is not None)
    c5 = run_c5a(c4)
    if a.live_rehearse:
        assert live_root is not None
        try:
            live5 = run_c5_live(live_root, Path(a.backup), Path(a.scratch))
            c5.update(live5)
        except BindError as e:
            c5["ok"] = False
            c5["c5b_kind"] = e.kind
            c5["c5b_detail"] = str(e)
            check("C5b/C5c live rehearsal", lambda: False)
            RESULTS[-1] = (RESULTS[-1][0], False, f"{e.kind}: {e}")

    headline, closed = decide_headline(
        bool(a.live), c1, c2, c3, c4, c5, bool(a.live_rehearse))
    # Hard refuse: counts disagree never close the gate.
    if c2 is not None and (
            c2.get("machine_count") != c2.get("registry_count") or c2.get("reds")):
        headline = "GATE_OPEN"
        closed = False
    LIVE_VALUE["headline"] = headline
    LIVE_VALUE["live_gate_closed"] = bool(closed) and headline == "GATE_CLOSED"
    if LIVE_VALUE["headline"] != "GATE_CLOSED":
        LIVE_VALUE["live_gate_closed"] = False

    LIVE_VALUE["c1"] = {
        "nonce": c1.get("nonce"),
        "bind_digest": c1.get("bind_digest"),
        "child_pid": c1.get("child_pid"),
        "file": c1.get("file"),
        "epoch": c1.get("epoch"),
        "ok": c1.get("ok"),
        "live_ok": c1.get("live_ok"),
        "tasks": [
            {"name": t.get("name"), "registered": t.get("registered"),
             "tr": t.get("tr"), "kind": t.get("kind")}
            for t in (c1.get("tasks") or [])
        ],
        "negative_kinds": c1.get("negative_kinds"),
        "stale_control": c1.get("stale_control"),
    }
    if c2 is not None:
        LIVE_VALUE["c2"] = {
            "machine_count": c2.get("machine_count"),
            "registry_count": c2.get("registry_count"),
            "reds": c2.get("reds"),
            "red_rows": c2.get("red_rows"),
            "names": c2.get("names"),
            "ok": c2.get("ok"),
        }
    if c3 is not None:
        LIVE_VALUE["c3"] = {
            "pairs": c3.get("pairs"),
            "ok": c3.get("ok"),
            "status": c3.get("status"),
            "serve": c3.get("serve"),
        }
    LIVE_VALUE["c4"] = {
        "children": [
            {k: kid.get(k) for k in
             ("script", "rc", "pid", "selftest_pass", "rehearse_ok",
              "elapsed_s", "unmeasured", "timeout")}
            for kid in (c4.get("children") or [])
        ],
        "ok": c4.get("ok"),
    }
    LIVE_VALUE["c5"] = {
        "c5a_ok": c5.get("c5a_ok"),
        "c5b": c5.get("c5b"),
        "c5c_fired": c5.get("c5c_fired"),
        "c5d": c5.get("c5d"),
        "ok": c5.get("ok") if a.live_rehearse else c5.get("c5a_ok"),
    }

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    LIVE_VALUE["ok"] = not bad
    LIVE_VALUE["checks"] = len(RESULTS)
    LIVE_VALUE["failed"] = len(bad)
    LIVE_VALUE["failed_labels"] = [l for l, _e in bad]

    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    subset_keys = (
        "schema", "headline", "live_gate_closed", "ok", "checks", "failed",
        "did_not_write_live_tree", "did_not_touch_core",
    )
    subset = {k: LIVE_VALUE[k] for k in subset_keys if k in LIVE_VALUE}
    if c2 is not None:
        subset["c2_machine_count"] = c2.get("machine_count")
        subset["c2_registry_count"] = c2.get("registry_count")
        subset["c2_reds"] = c2.get("reds")
    print("live_value: " + json.dumps(subset, sort_keys=True))
    extra = ""
    if a.live:
        extra += " + C2/C3 live"
    extra += " + C4"
    print("SELFTEST %s - %d checks (runtime-binding C1%s)" % (
        "PASS" if not bad else "FAIL", len(RESULTS), extra,
    ))
    if a.proof:
        Path(a.proof).write_text(
            json.dumps(LIVE_VALUE, indent=1, default=str) + "\n",
            encoding="utf-8")
    return 0 if not bad else 1


def test_runtime_binding():
    assert main([]) == 0


if __name__ == "__main__":
    raise SystemExit(main())
