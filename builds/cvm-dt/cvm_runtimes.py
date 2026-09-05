#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What model runtimes are ACTUALLY on this machine — measured, not assumed.

F-21 (local STT model inference) shipped on VOSK (`cvm_stt_vosk.py`, A5). Every
question that came after it — "should the ear move to whisper on the 3070?",
"can Piper give desk and road one voice?", "is a GPU runtime even reachable for
`py -3.14`?" — has been answered in the backlog with the word OVERFLOW, which
is a guess wearing a label. `docs/CVM_ARCH.md` §4 classes whisper as OVERFLOW
"until measured". This is the measurement.

Three facts are kept strictly apart, because conflating them is how a machine
gets reported as having a runtime it cannot load:

  INSTALLED   importable by a CLEAN run of an interpreter — probed in a
              SUBPROCESS under `-I` (isolated: no PYTHONPATH, no user site, no
              inherited `sys.path`). An in-process check would be answered by
              the process that already opted in, which is exactly the trap
              `test_cvm_stt_vosk.py::vosk_is_not_importable_without_opting_in`
              was written for.
  VENDORED    importable only when this repo's `vendor/site` is put on the
              path — what COSMOS carries, not what the box has.
  REACHABLE   not present, but a wheel matching THIS interpreter's tags exists
              upstream, at a measured byte cost for the whole dependency
              closure. "Reachable" is a wheel filename and a number, never an
              impression.

Hardware is measured from `nvidia-smi`, never from `torch.cuda.is_available()`
— a box with a 3070 and no torch has a GPU, and asking torch would report it as
having neither.

    py -3.14 builds\\cvm-dt\\cvm_runtimes.py
    py -3.14 builds\\cvm-dt\\cvm_runtimes.py --no-net    # local inventory only

Artifact: `builds/cvm-dt/RUNTIMES.json` (`schema cvm-dt-runtimes/1`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import time
import urllib.request
from pathlib import Path
from typing import Callable, Optional

_HERE = Path(__file__).resolve().parent

WIRE = "cvm-dt-runtimes/1"
ARTIFACT = "RUNTIMES.json"
VENDOR_SITE = _HERE / "vendor" / "site"
VENDOR_MODELS = _HERE / "vendor" / "models"

NET_TIMEOUT_S = 60.0
PYPI_JSON = "https://pypi.org/pypi/%s/json"

# Every module here is a LOCAL inference runtime or a direct dependency of one.
# The value of a name in this list is that its absence is a measurement too.
PROBE_MODULES: tuple[tuple[str, str], ...] = (
    ("vosk", "kaldi STT — the shipped F-21 ear"),
    ("faster_whisper", "whisper via CTranslate2 — the named B3 upgrade"),
    ("ctranslate2", "faster-whisper's native engine; carries the GPU path"),
    ("whisper", "openai-whisper reference implementation (needs torch)"),
    ("pywhispercpp", "whisper.cpp bindings"),
    ("torch", "GPU tensor runtime"),
    ("onnxruntime", "ONNX inference — Piper's engine, and a whisper-ONNX path"),
    ("openvino", "Intel inference runtime"),
    ("transformers", "HF model loading"),
    ("tokenizers", "HF tokenizers — faster-whisper dependency"),
    ("huggingface_hub", "model download — faster-whisper dependency"),
    ("llama_cpp", "llama.cpp bindings"),
    ("piper", "Piper TTS — CVM_ARCH §6.3's named voice"),
    ("soundfile", "audio I/O"),
    ("sounddevice", "audio capture"),
    ("numpy", "array math — required by every runtime above"),
    ("scipy", "signal processing"),
    ("comtypes", "COM — one route to SAPI"),
    ("win32com", "pywin32 COM — the other route to SAPI"),
)

# Candidate stacks. `roots` are the packages a human would actually install;
# the closure is measured from their own published metadata, not from a guess.
STACKS: dict[str, dict] = {
    "faster-whisper-cpu": {
        "roots": ("faster-whisper",),
        "why": "CVM_BACKLOG B3's named next step if real-mic recall is poor. "
               "CPU only — no CUDA libraries in the closure.",
        "unblocks": "an ear that can beat VOSK's 0.80 recall without SAPI",
    },
    "piper-tts": {
        "roots": ("piper-tts",),
        "why": "CVM_ARCH §6.3 — desk and road sounding like one assistant "
               "(CVM_BACKLOG B4).",
        "unblocks": "B4's download half; the voice-family question stays open",
    },
    "onnxruntime-directml": {
        "roots": ("onnxruntime-directml",),
        "why": "the only GPU route on this box that needs no CUDA toolkit — "
               "DirectML runs on the installed display driver.",
        "unblocks": "GPU inference without a 2 GB CUDA download",
    },
    "gpu-cuda-libs": {
        "roots": ("nvidia-cublas-cu12", "nvidia-cudnn-cu12",
                  "nvidia-cuda-runtime-cu12"),
        "why": "MEASURED, not guessed: CTranslate2 enumerates 1 CUDA device on "
               "this box and then refuses to load with 'Library "
               "cublas64_12.dll is not found or cannot be loaded' "
               "(`F21B_STT_WHISPER.json:cuda_attempt`). These are the "
               "libraries that refusal names.",
        "unblocks": "GPU whisper on the RTX 3070 — at the byte cost below, "
                    "which is the point of measuring it",
    },
    "torch-pypi-default": {
        "roots": ("torch",),
        "why": "openai-whisper's requirement. Named for what it IS, not for "
               "what it is wanted for: whether the default PyPI Windows wheel "
               "carries CUDA is a question this closure ANSWERS "
               "(`cuda_in_closure`), so the stack must not assert it.",
        "unblocks": "openai-whisper and any HF pipeline — on whatever device "
                    "the measured closure turns out to support",
    },
}

# Bounded, NAMED locations. Not a disk scan: an unbounded search that finds
# nothing proves nothing about the places it did not reach, and one that finds
# something takes minutes to say so.
def _disk_candidates() -> list[tuple[str, Path]]:
    home = Path(os.path.expanduser("~"))
    lad = Path(os.environ.get("LOCALAPPDATA") or (home / "AppData/Local"))
    pf = Path(os.environ.get("ProgramFiles") or "C:/Program Files")
    return [
        ("ollama", lad / "Programs/Ollama/ollama.exe"),
        ("lm-studio", lad / "Programs/lm-studio"),
        ("whisper-model-cache", home / ".cache/whisper"),
        ("huggingface-hub-cache", home / ".cache/huggingface/hub"),
        ("cuda-toolkit", pf / "NVIDIA GPU Computing Toolkit/CUDA"),
        ("cosmos-vendor-site", VENDOR_SITE),
        ("cosmos-vendor-models", VENDOR_MODELS),
    ]


# --------------------------------------------------------------------------
# wheel tags — which wheels THIS interpreter could actually load
# --------------------------------------------------------------------------

def interpreter_tags(*, impl: str = "cp", major: int = None, minor: int = None,
                     platform: str = None, gil: bool = None) -> dict:
    """The (python, abi, platform) triples this interpreter accepts.

    Derived from the running interpreter by default. Freethreaded ABIs
    (`cp314t`) are accepted ONLY by a freethreaded build — a GIL build that
    loaded one would crash, so reporting it as installable is worse than
    reporting nothing.
    """
    major = sys.version_info[0] if major is None else int(major)
    minor = sys.version_info[1] if minor is None else int(minor)
    if platform is None:
        platform = sysconfig.get_platform().replace("-", "_").replace(".", "_")
    if gil is None:
        gil = not bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    cp = "%s%d%d" % (impl, major, minor)
    pys = {cp, "py%d" % major, "py%d%d" % (major, minor)}
    abis = {cp if gil else cp + "t", "none"}
    if not gil:
        abis.add(cp)                      # a freethreaded build loads both
    # abi3 is forward compatible: a cp39-abi3 wheel loads on 3.14.
    abi3_from = {"%s%d%d" % (impl, major, m) for m in range(2, minor + 1)}
    plats = {platform, "any"}
    return {"cp": cp, "pys": sorted(pys), "abis": sorted(abis),
            "abi3_from": sorted(abi3_from), "plats": sorted(plats),
            "gil": bool(gil), "platform": platform}


def parse_wheel(filename: str) -> Optional[dict]:
    """Split a wheel filename into its dot-expanded tag sets."""
    if not filename.endswith(".whl"):
        return None
    parts = filename[:-4].split("-")
    if len(parts) < 5:
        return None
    py, abi, plat = parts[-3], parts[-2], parts[-1]
    return {"name": parts[0], "version": parts[1],
            "py": py.split("."), "abi": abi.split("."), "plat": plat.split(".")}


def wheel_matches(filename: str, tags: dict) -> bool:
    """True when this interpreter could load that wheel. Rejects, too."""
    w = parse_wheel(filename)
    if not w:
        return False
    if not (set(w["plat"]) & set(tags["plats"])):
        return False
    for py in w["py"]:
        for abi in w["abi"]:
            if abi == "abi3":
                if py in tags["abi3_from"]:
                    return True
                continue
            if py in tags["pys"] and abi in tags["abis"]:
                return True
    return False


# --------------------------------------------------------------------------
# local inventory — every claim comes back from a separate process
# --------------------------------------------------------------------------

_PROBE_SRC = (
    "import sys, json, importlib.util as u\n"
    "extra = json.loads(sys.argv[1])\n"
    "sys.path[:0] = [p for p in extra if p]\n"
    "names = json.loads(sys.argv[2])\n"
    "found = {}\n"
    "for n in names:\n"
    "    try:\n"
    "        found[n] = u.find_spec(n) is not None\n"
    "    except Exception:\n"
    "        found[n] = False\n"
    "print(json.dumps({'exe': sys.executable, 'ver': sys.version.split()[0],\n"
    "                  'found': found,\n"
    "                  'isolated': bool(sys.flags.isolated)}))\n"
)


def probe_interpreter(exe: str, names: list[str], *,
                      extra_path: Optional[list[str]] = None,
                      isolated: bool = True, timeout: float = 120.0) -> dict:
    """Ask ANOTHER process what it can import. Never `find_spec` in-process.

    `-I` drops PYTHONPATH, the user site directory and the script directory, so
    what comes back is what a cold run of that interpreter can load — which is
    the only meaning of "installed" worth writing down.
    """
    argv = [exe] + (["-I"] if isolated else []) + [
        "-c", _PROBE_SRC, json.dumps(list(extra_path or [])), json.dumps(names)]
    try:
        r = subprocess.run(argv, capture_output=True, text=True,
                           timeout=timeout)
    except Exception as e:                                        # noqa: BLE001
        return {"ok": False, "kind": "PROBE_FAILED", "exe": exe,
                "detail": "%s: %s" % (type(e).__name__, e)}
    if r.returncode != 0:
        return {"ok": False, "kind": "PROBE_RC", "exe": exe, "rc": r.returncode,
                "detail": (r.stderr or "").strip()[:400]}
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:                                        # noqa: BLE001
        return {"ok": False, "kind": "PROBE_UNPARSED", "exe": exe,
                "detail": "%s: %s" % (type(e).__name__, e)}
    out["ok"] = True
    out["extra_path"] = list(extra_path or [])
    return out


def interpreters() -> dict:
    """Every interpreter the launcher knows, plus the one running this."""
    found: list[dict] = []
    exe = shutil.which("py")
    raw = ""
    if exe:
        try:
            r = subprocess.run([exe, "--list-paths"], capture_output=True,
                               text=True, timeout=60)
            raw = r.stdout or ""
            for line in raw.splitlines():
                m = re.match(r"\s*-V:([0-9.]+[^\s]*)\s+(\*?)\s*(.+\.exe)\s*$",
                             line, re.I)
                if m:
                    found.append({"tag": m.group(1),
                                  "default": m.group(2) == "*",
                                  "path": m.group(3).strip()})
        except Exception:                                         # noqa: BLE001
            pass
    have = {Path(f["path"]).resolve().as_posix().lower() for f in found}
    mine = Path(sys.executable).resolve()
    if mine.as_posix().lower() not in have:
        found.append({"tag": "%d.%d" % sys.version_info[:2], "default": False,
                      "path": str(mine), "from": "sys.executable"})
    return {"launcher": exe, "list_paths_raw": raw.strip(), "found": found}


def gpu() -> dict:
    """nvidia-smi, not a framework. A GPU exists whether or not torch does."""
    smi = shutil.which("nvidia-smi")
    if not smi:
        return {"ok": False, "kind": "NO_NVIDIA_SMI",
                "detail": "nvidia-smi is not on PATH; no NVIDIA GPU is "
                          "claimed either way"}
    try:
        r = subprocess.run(
            [smi, "--query-gpu=name,memory.total,driver_version,compute_cap",
             "--format=csv,noheader"], capture_output=True, text=True,
            timeout=60)
    except Exception as e:                                        # noqa: BLE001
        return {"ok": False, "kind": "SMI_FAILED",
                "detail": "%s: %s" % (type(e).__name__, e)}
    if r.returncode != 0 or not r.stdout.strip():
        return {"ok": False, "kind": "SMI_RC", "rc": r.returncode,
                "detail": (r.stderr or "").strip()[:300]}
    devs = []
    for line in r.stdout.strip().splitlines():
        f = [x.strip() for x in line.split(",")]
        if len(f) >= 4:
            devs.append({"name": f[0], "memory_total": f[1],
                         "driver": f[2], "compute_cap": f[3]})
    return {"ok": bool(devs), "kind": "ok" if devs else "SMI_EMPTY",
            "devices": devs, "raw": r.stdout.strip()}


def accelerator_libs() -> dict:
    """Is a CUDA TOOLKIT here, separate from the driver nvidia-smi proves."""
    dll_hits = []
    for d in (os.environ.get("PATH") or "").split(os.pathsep):
        if not d:
            continue
        try:
            for f in os.scandir(d):
                n = f.name.lower()
                if n.startswith(("cudart64", "cublas64", "cudnn64")):
                    dll_hits.append(os.path.join(d, f.name))
        except OSError:
            continue
    return {"CUDA_PATH": os.environ.get("CUDA_PATH"),
            "nvcc": shutil.which("nvcc"),
            "cuda_dlls_on_path": sorted(set(dll_hits))[:12],
            "toolkit_present": bool(os.environ.get("CUDA_PATH")
                                    or shutil.which("nvcc") or dll_hits)}


def on_disk() -> list[dict]:
    out = []
    for label, path in _disk_candidates():
        try:
            exists = path.exists()
        except OSError:
            exists = False
        out.append({"label": label, "path": str(path), "exists": bool(exists),
                    "kind": ("dir" if exists and path.is_dir()
                             else "file" if exists else "absent")})
    return out


# --------------------------------------------------------------------------
# reachability — a wheel filename and a byte count, or a named refusal
# --------------------------------------------------------------------------

def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=NET_TIMEOUT_S) as r:
        return json.loads(r.read().decode("utf-8"))


_MARKER_TRUE = ("win32", "windows", "nt")


def marker_admits(marker: str) -> dict:
    """Would this requirement apply to THIS box? Conservative on doubt.

    Extras are excluded (an extra is opt-in, so it is not part of the cost of
    installing the package). Platform markers are read for the three names that
    actually differ here. Anything else is INCLUDED and flagged, because an
    unread marker that silently drops a 300 MB dependency would understate the
    number this whole function exists to produce.
    """
    m = (marker or "").strip()
    if not m:
        return {"include": True, "why": "no marker"}
    low = m.lower()
    if "extra ==" in low:
        return {"include": False, "why": "extra"}
    for key in ("sys_platform", "platform_system", "os_name"):
        if key in low:
            quoted = [q.lower() for q in re.findall(r"['\"]([^'\"]+)['\"]", m)]
            hits = [q for q in quoted if q in _MARKER_TRUE]
            if "!=" in low or " not in " in low:
                return {"include": not hits,
                        "why": "%s negative marker" % key}
            return {"include": bool(hits), "why": "%s marker" % key}
    if "python_version" in low or "python_full_version" in low:
        return {"include": True, "why": "python_version marker assumed true",
                "flagged": True}
    return {"include": True, "why": "unread marker included conservatively",
            "flagged": True}


_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9._-]+)")


def parse_requires(requires_dist: Optional[list]) -> dict:
    """Requirement strings -> {names to follow, skipped, flagged}."""
    names, skipped, flagged = [], [], []
    for req in (requires_dist or []):
        base, _, marker = str(req).partition(";")
        m = _REQ_NAME.match(base)
        if not m:
            continue
        name = m.group(1)
        verdict = marker_admits(marker)
        if verdict.get("flagged"):
            flagged.append({"req": str(req), "why": verdict["why"]})
        if verdict["include"]:
            names.append(name)
        else:
            skipped.append({"req": str(req), "why": verdict["why"]})
    return {"names": names, "skipped": skipped, "flagged": flagged}


def package_reach(name: str, tags: dict, fetch: Callable[[str], dict],
                  *, scan_releases: int = 12) -> dict:
    """The newest release with a wheel THIS interpreter can load, and its size."""
    try:
        meta = fetch(PYPI_JSON % name)
    except Exception as e:                                        # noqa: BLE001
        return {"name": name, "ok": False, "kind": "PYPI_UNREACHABLE",
                "detail": "%s: %s" % (type(e).__name__, e)}
    latest = (meta.get("info") or {}).get("version")
    releases = meta.get("releases") or {}

    def _match(version: str) -> Optional[dict]:
        for f in releases.get(version) or []:
            fn = f.get("filename") or ""
            if f.get("packagetype") == "bdist_wheel" and wheel_matches(fn, tags):
                return {"filename": fn, "bytes": int(f.get("size") or 0),
                        "version": version}
        return None

    hit = _match(latest) if latest else None
    scanned = [latest] if latest else []
    if not hit:
        # Newest-first by upload time: PyPI does not order releases, and
        # version strings cannot be compared without `packaging`, which this
        # interpreter does not have. Upload time is a fact in the response.
        def _when(v):
            fs = releases.get(v) or []
            return max([str(f.get("upload_time_iso_8601") or "") for f in fs]
                       or [""])
        for v in sorted(releases, key=_when, reverse=True)[:scan_releases]:
            scanned.append(v)
            hit = _match(v)
            if hit:
                break
    sdist = any((f.get("packagetype") == "sdist")
                for f in (releases.get(latest) or []))
    reqs = parse_requires((meta.get("info") or {}).get("requires_dist"))
    return {"name": name, "ok": bool(hit), "latest": latest,
            "kind": "ok" if hit else ("SDIST_ONLY" if sdist else "NO_WHEEL"),
            "wheel": hit, "versions_scanned": len(set(scanned)),
            "requires": reqs["names"], "requires_skipped": reqs["skipped"],
            "requires_flagged": reqs["flagged"],
            "requires_dist_raw": (meta.get("info") or {}).get("requires_dist")}


def stack_reach(roots: tuple, tags: dict, fetch: Callable[[str], dict],
                *, max_packages: int = 60) -> dict:
    """Breadth-first over published metadata. Capped, and it says when it caps."""
    seen: dict[str, dict] = {}
    queue = list(roots)
    truncated = False
    while queue:
        name = queue.pop(0)
        key = name.lower().replace("_", "-")
        if key in seen:
            continue
        if len(seen) >= max_packages:
            truncated = True
            break
        rec = package_reach(name, tags, fetch)
        seen[key] = rec
        for dep in rec.get("requires") or []:
            if dep.lower().replace("_", "-") not in seen:
                queue.append(dep)
    pkgs = list(seen.values())
    blocked = [p["name"] for p in pkgs if not p.get("ok")]
    total = sum(int((p.get("wheel") or {}).get("bytes") or 0) for p in pkgs)
    # A GPU stack that ships no GPU library is a CPU stack. Say so from the
    # closure rather than from the stack's name.
    cuda = sorted(p["name"] for p in pkgs
                  if re.match(r"^(nvidia[-_]|cuda|cudnn|cublas)", p["name"], re.I))
    return {
        "roots": list(roots), "packages": pkgs, "package_count": len(pkgs),
        "cuda_in_closure": cuda,
        "device_support": ("cuda-packages-present" if cuda else
                           "no CUDA library in this closure — CPU unless the "
                           "runtime finds cuBLAS/cuDNN already on the box "
                           "(this box: see accelerator_libs.toolkit_present)"),
        "total_bytes": total,
        "total_mb": round(total / 1048576.0, 1),
        "blocked": blocked, "truncated": truncated,
        "ok": not blocked and not truncated,
        "verdict": ("REACHABLE" if (not blocked and not truncated)
                    else "TRUNCATED" if truncated else "BLOCKED"),
        "closure_method": "BFS over PyPI requires_dist; extras excluded; "
                          "sys_platform/platform_system/os_name markers "
                          "evaluated; everything else included conservatively "
                          "(overstates rather than understates)",
        "note": "bytes are WHEELS ONLY — model weights are not in this number",
    }


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------

def run(*, net: bool = True, fetch: Optional[Callable[[str], dict]] = None,
        stacks: Optional[dict] = None) -> dict:
    t0 = time.perf_counter()
    tags = interpreter_tags()
    names = [n for n, _ in PROBE_MODULES]
    interp = interpreters()

    per_interp = []
    for it in interp["found"]:
        clean = probe_interpreter(it["path"], names)
        row = {"tag": it["tag"], "path": it["path"],
               "default": it.get("default", False), "clean": clean}
        if Path(it["path"]).resolve() == Path(sys.executable).resolve():
            row["with_vendor_site"] = probe_interpreter(
                it["path"], names, extra_path=[str(VENDOR_SITE)])
        per_interp.append(row)

    installed = sorted({n for row in per_interp
                        for n, ok in ((row["clean"].get("found") or {})).items()
                        if ok})
    vendored = sorted({
        n for row in per_interp
        if row.get("with_vendor_site", {}).get("ok")
        for n, ok in (row["with_vendor_site"].get("found") or {}).items()
        if ok and not (row["clean"].get("found") or {}).get(n)})

    reach: dict[str, dict] = {}
    stacks = STACKS if stacks is None else stacks
    if net:
        f = fetch or _fetch_json
        for label, spec in stacks.items():
            r = stack_reach(tuple(spec["roots"]), tags, f)
            r.update({"why": spec.get("why"), "unblocks": spec.get("unblocks")})
            reach[label] = r
    else:
        for label, spec in stacks.items():
            reach[label] = {"ok": False, "verdict": "NOT_MEASURED_OFFLINE",
                            "roots": list(spec["roots"]),
                            "why": spec.get("why"),
                            "detail": "--no-net was passed; nothing upstream "
                                      "was contacted and nothing is inferred"}

    g = gpu()
    dev = (g.get("devices") or [{}])[0]
    rec = {
        "wire": WIRE, "ok": True,
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "epoch": time.time(),
        "python": sys.version.split()[0],
        "tags": tags,
        "probe_modules": [{"name": n, "role": r} for n, r in PROBE_MODULES],
        "interpreters": interp,
        "per_interpreter": per_interp,
        "installed": installed,
        "vendored_only": vendored,
        "gpu": g,
        "accelerator_libs": accelerator_libs(),
        "on_disk": on_disk(),
        "reachability": reach,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 1),
    }
    rec["emitted"] = (
        "runtimes:py%s:%s:installed=%d of %d local model runtimes%s"
        ":vendored_only=%s:gpu=%s:cuda_toolkit=%s:reachable=%s" % (
            rec["python"], tags["cp"] + "-" + tags["platform"],
            len(installed), len(names),
            " (" + ",".join(installed) + ")" if installed else "",
            ",".join(vendored) or "none",
            ("%s/%s/cc%s/driver %s" % (dev.get("name"), dev.get("memory_total"),
                                       dev.get("compute_cap"), dev.get("driver"))
             if g.get("ok") else g.get("kind")),
            rec["accelerator_libs"]["toolkit_present"],
            ",".join("%s=%s%s" % (k, v.get("verdict"),
                                  ("@%sMB" % v["total_mb"]) if v.get("total_mb")
                                  else "")
                     for k, v in reach.items()) or "not measured"))
    return rec


def write_artifact(rec: dict, out_dir: Optional[Path] = None) -> Path:
    out = (Path(out_dir) if out_dir else _HERE) / ARTIFACT
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return out


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-net", action="store_true",
                    help="local inventory only; contact nothing upstream")
    ap.add_argument("--out", default=None, help="artifact directory")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    rec = run(net=not a.no_net)
    path = write_artifact(rec, Path(a.out) if a.out else None)
    if not a.quiet:
        print(json.dumps(rec, indent=1))
    print(rec["emitted"])
    print(str(path))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
