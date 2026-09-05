#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""longpath_census - measure Windows MAX_PATH exposure, and prove what each walker does with it.

Two verbs, both measurement-only. Nothing here writes the live tree.

    census   walk trees through the \\?\ extended-length prefix (ground truth) and
             count files whose LOGICAL absolute path exceeds MAX_PATH; report the
             deepest example, and how many of them a plain (unprefixed) walk cannot
             even SEE versus merely cannot stat().

    behave   run the two real walkers against a scratch tree that contains one
             genuinely deep file, and report what each one does with it. Bound to
             emitted values (file counts, refusal kinds), never to reading code.

MAX_PATH is 260 INCLUDING the terminating NUL, so 259 is the last length a plain
Win32 call accepts for a file. Both thresholds are reported; neither is rounded.

    py -3.14 builds/probe/longpath_census.py census --root V:\Ai --root V:\A
    py -3.14 builds/probe/longpath_census.py behave --scratch %TEMP%\lp_probe
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

EXT_PREFIX = "\\\\?\\"
MAX_PATH_WITH_NUL = 260          # the documented constant
MAX_PATH_USABLE = 259            # the longest file path a plain Win32 call accepts
DEFAULT_EXCLUDE_DIRS = ("__pycache__",)


class ProbeRefusal(RuntimeError):
    """kind in {NOT_WINDOWS, ROOT_MISSING, IMPORT_FAILED, SCRATCH_UNSAFE,
    BAD_EXCLUDES}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# ---------------------------------------------------------------- the prefix

def extended(p) -> str:
    r"""Extended-length form of an absolute path. Mirrors cosmos_paths.extended.

    Non-Windows: unchanged. Never double-prefixes. UNC gets \\?\UNC\.
    """
    s = str(p)
    if os.name != "nt":
        return s
    if s.startswith(EXT_PREFIX):
        return s
    if s.startswith("\\\\"):
        return EXT_PREFIX + "UNC" + s[1:]
    return EXT_PREFIX + os.path.abspath(s)


def logical(p: str) -> str:
    """Strip the extended prefix back off, so lengths are measured as Win32 sees them."""
    s = str(p)
    if s.startswith(EXT_PREFIX + "UNC\\"):
        return "\\" + s[len(EXT_PREFIX) + 3:]
    if s.startswith(EXT_PREFIX):
        return s[len(EXT_PREFIX):]
    return s


# ---------------------------------------------------------------- census

def _is_windows() -> bool:
    """Isolated so a test can claim a POSIX host without patching os.name globally."""
    return os.name == "nt"


def _require_windows() -> None:
    """MAX_PATH / `\\\\?\\` is a Win32 measurement. A POSIX walk is not that census."""
    if not _is_windows():
        raise ProbeRefusal(
            "NOT_WINDOWS",
            "MAX_PATH census is a Win32 measurement; os.name is not nt")


def _long_paths_enabled() -> object:
    """The registry switch that would make the prefix unnecessary. None if unreadable."""
    if not _is_windows():
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\FileSystem") as k:
            return int(winreg.QueryValueEx(k, "LongPathsEnabled")[0])
    except (OSError, ValueError, ImportError):
        return None


def census_one(root: str, exclude_dirs=DEFAULT_EXCLUDE_DIRS, sample: int = 5) -> dict:
    """Walk root TWICE - once prefixed (ground truth), once plain - and diff them."""
    _require_windows()
    rp = Path(root)
    if not rp.is_dir():
        raise ProbeRefusal("ROOT_MISSING", f"{root} is not a directory")
    if (isinstance(exclude_dirs, (str, bytes))
            or not isinstance(exclude_dirs, (list, tuple, set, frozenset))):
        # set("git") is {'g','i','t'} — silent character exclusion.
        # An int TypeErrors. Bite `_bite_unpinned_round8.json`.
        raise ProbeRefusal(
            "BAD_EXCLUDES",
            f"exclude_dirs is {type(exclude_dirs).__name__}, not a list of names")
    ex = set(exclude_dirs)
    t0 = time.time()

    # --- ground truth: prefix the ROOT, and every descendant inherits it.
    ext_root = extended(rp)
    ext_files: set[str] = set()
    over_260: list[tuple[int, str]] = []
    walk_errors: list[str] = []
    total_bytes = 0
    for dirpath, dirnames, filenames in os.walk(ext_root,
                                                onerror=lambda e: walk_errors.append(repr(e))):
        dirnames[:] = [d for d in dirnames if d not in ex]
        for name in filenames:
            full_ext = os.path.join(dirpath, name)
            lg = logical(full_ext)
            ext_files.add(lg.lower())
            n = len(lg)
            if n > MAX_PATH_USABLE:
                over_260.append((n, lg))
            try:
                total_bytes += os.stat(full_ext).st_size
            except OSError:
                pass

    # --- what a plain walker sees. os.walk swallows scandir errors by default;
    #     capture them so "silently skipped" is a number, not an adjective.
    plain_files: set[str] = set()
    plain_errors: list[str] = []
    for dirpath, dirnames, filenames in os.walk(str(rp),
                                                onerror=lambda e: plain_errors.append(repr(e))):
        dirnames[:] = [d for d in dirnames if d not in ex]
        for name in filenames:
            plain_files.add(os.path.join(dirpath, name).lower())

    # --- of the long ones, which can a plain stat() still reach, and which CLASS?
    #     class A - parent directory listable, file path too long  -> name comes back
    #               from the walk, stat()/open() then fails. Path.is_file() SWALLOWS
    #               that and returns False, so a walker filtering on is_file() drops
    #               the file without ever raising.
    #     class B - parent directory itself too long -> scandir cannot descend and
    #               os.walk(onerror=None) swallows it. The subtree is never seen.
    stat_ok = stat_fail = 0
    class_a = class_b = 0
    a_is_file_false = 0
    a_sample: list[str] = []
    winerrors: dict[str, int] = {}
    for _n, lg in over_260:
        parent_listable = len(os.path.dirname(lg)) <= MAX_PATH_USABLE
        if parent_listable:
            class_a += 1
            if not Path(lg).is_file():
                a_is_file_false += 1
            if len(a_sample) < sample:
                a_sample.append(lg)
        else:
            class_b += 1
        try:
            os.stat(lg)
            stat_ok += 1
        except OSError as e:
            stat_fail += 1
            key = f"winerror={getattr(e, 'winerror', None)}"
            winerrors[key] = winerrors.get(key, 0) + 1

    over_260.sort(reverse=True)
    invisible = sorted(ext_files - plain_files)
    return {
        "root": str(rp),
        "files_extended_walk": len(ext_files),
        "files_plain_walk": len(plain_files),
        "invisible_to_plain_walk": len(invisible),
        "invisible_sample": invisible[:sample],
        "total_bytes": total_bytes,
        "over_259_usable": len(over_260),
        "over_260_constant": sum(1 for n, _ in over_260 if n > MAX_PATH_WITH_NUL),
        "max_len": over_260[0][0] if over_260 else max(
            (len(logical(f)) for f in ext_files), default=0),
        "deepest": over_260[0][1] if over_260 else None,
        "deepest_sample": [{"len": n, "path": p} for n, p in over_260[:sample]],
        "long_stat_ok_unprefixed": stat_ok,
        "long_stat_fail_unprefixed": stat_fail,
        "long_stat_winerrors": winerrors,
        "class_a_dir_listable": class_a,
        "class_a_is_file_returns_false": a_is_file_false,
        "class_a_sample": a_sample,
        "class_b_dir_too_long": class_b,
        "walk_errors_extended": len(walk_errors),
        "walk_errors_plain": len(plain_errors),
        "walk_errors_plain_sample": plain_errors[:sample],
        "elapsed_s": round(time.time() - t0, 1),
    }


# ---------------------------------------------------------------- behaviour

def _write_deep(path: Path, payload: bytes) -> None:
    os.makedirs(extended(path.parent), exist_ok=True)
    with open(extended(path), "wb") as fh:
        fh.write(payload)


def _stat_ok(p: Path) -> bool:
    try:
        os.stat(str(p))
        return True
    except OSError:
        return False


def _make_deep_tree(scratch: Path) -> dict:
    r"""Build a scratch tree with THREE files - and two DIFFERENT long-path failures.

    The distinction is the whole finding, and collapsing it would hide half the gap:

      class A - the containing directory is short enough for scandir to list, but
                the FILE path is past MAX_PATH. The name comes back from the walk;
                stat()/open() on it then fails winerror=3. A walker sees a file it
                cannot read.
      class B - the DIRECTORY path is itself past the limit. scandir cannot descend
                at all, and os.walk's default onerror=None SWALLOWS that. The walker
                never learns the subtree exists.

    Everything is created THROUGH the prefix, because mkdir refuses past 248 chars
    without it - which is why the fixture is proof, not a mock.
    """
    scratch = Path(scratch).resolve()
    shutil.rmtree(extended(scratch), ignore_errors=True)
    os.makedirs(extended(scratch), exist_ok=True)

    shallow = scratch / "shallow.txt"
    shallow.write_bytes(b"shallow - every walker sees this one\n")

    # class A: pad the FILENAME, keep the directory listable.
    a_dir = scratch / ("a" * 40)
    a_name = ("n" * (300 - len(str(a_dir)) - 1 - len(".txt"))) + ".txt"
    class_a = a_dir / a_name
    _write_deep(class_a, b"class A - long file name, listable directory\n")

    # class B: pad the DIRECTORY past the limit.
    seg = "b" * 40
    b_dir = scratch
    while len(str(b_dir)) + 1 + len(seg) < 300:
        b_dir = b_dir / seg
    class_b = b_dir / "deep.txt"
    _write_deep(class_b, b"class B - directory itself past MAX_PATH\n")

    files = {}
    for key, p in (("shallow", shallow), ("class_a", class_a), ("class_b", class_b)):
        files[key] = {
            "path": str(p),
            "len": len(str(p)),
            "bytes": len(open(extended(p), "rb").read()),
            "stat_ok_unprefixed": _stat_ok(p),
            "exists_prefixed": os.path.exists(extended(p)),
        }
    return {"scratch": str(scratch), "files": files,
            "files_on_disk": sum(len(f) for _d, _s, f in os.walk(extended(scratch)))}


class _StubLedger:
    """Duck-types cosmos_ledger.Ledger.append so the REAL Backup class can run."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def append(self, kind, payload):
        self.events.append((kind, payload))
        return {"kind": kind}


def _probe_running_backup(tree: dict, scratch: Path, src_file: Path, label: str) -> dict:
    """Run the SCHEDULED backup (cosmos/cosmos_backup.Backup.run) on the deep tree."""
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo / "cosmos"))
    try:
        running = _load_by_path("_running_cosmos_backup_" + label, src_file)
    except Exception as e:                                    # noqa: BLE001
        return {"module": label, "state": "UNMEASURED",
                "kind": "IMPORT_FAILED", "detail": f"{type(e).__name__}: {e}"}
    led = _StubLedger()
    dest_parent = Path(scratch).parent / (Path(scratch).name + "_running_dest")
    shutil.rmtree(extended(dest_parent), ignore_errors=True)
    os.makedirs(extended(dest_parent), exist_ok=True)
    src = Path(tree["scratch"])
    out: dict = {"module": label, "scheduled": True, "entry": "Backup.run"}
    try:
        r = running.Backup(led).run(src, dest_parent)
        out["state"] = "RETURNED"
        out["files_reported"] = r["files"]
    except Exception as e:                                    # noqa: BLE001
        out["state"] = "RAISED"
        out["kind"] = getattr(e, "kind", type(e).__name__)
        out["detail"] = str(e)[:300]
    out["ledger_events"] = [k for k, _ in led.events]
    stamps = sorted(os.listdir(extended(dest_parent))) if os.path.isdir(extended(dest_parent)) else []
    landed = Path(dest_parent) / stamps[-1] if stamps else None
    out["covered"] = {k: (_bytes_landed(landed, tree, k) if landed else False)
                      for k in tree["files"]}
    return out


def _bytes_landed(dest_root: Path, tree: dict, key: str) -> bool:
    """Did this file's BYTES actually reach the destination? Read them back and size them."""
    rec = tree["files"][key]
    rel = Path(rec["path"]).relative_to(Path(tree["scratch"]))
    cand = extended(Path(dest_root) / rel)
    if not os.path.exists(cand):
        return False
    with open(cand, "rb") as fh:
        return len(fh.read()) == rec["bytes"]


def _load_by_path(alias: str, path: Path):
    """Import a file under an explicit alias.

    Both walkers are named `cosmos_backup`. A plain `import cosmos_backup` returns
    whichever tree reached sys.modules first - so the probe would silently measure
    the same module twice and call it two results. Load by path, keyed by alias.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(alias, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"no spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def _probe_builds_backup(tree: dict) -> dict:
    """Run builds/backup/cosmos_backup.build_manifest on the same deep tree."""
    repo = Path(__file__).resolve().parents[2]
    try:
        builds_bk = _load_by_path("_builds_cosmos_backup",
                                  repo / "builds" / "backup" / "cosmos_backup.py")
    except Exception as e:                                    # noqa: BLE001
        return {"module": "builds/backup/cosmos_backup.py", "state": "UNMEASURED",
                "kind": "IMPORT_FAILED", "detail": f"{type(e).__name__}: {e}"}
    out: dict = {"module": "builds/backup/cosmos_backup.py", "scheduled": False,
                 "entry": "build_manifest", "walker": "iter_files (os.walk)"}
    keys: set[str] = set()
    try:
        m = builds_bk.build_manifest(Path(tree["scratch"]))
        out["state"] = "RETURNED"
        out["files_reported"] = m["file_count"]
        keys = set(m["files"])
    except Exception as e:                                    # noqa: BLE001
        out["state"] = "RAISED"
        out["kind"] = getattr(e, "kind", type(e).__name__)
        out["detail"] = str(e)[:300]
    out["covered"] = {
        k: Path(rec["path"]).relative_to(Path(tree["scratch"])).as_posix() in keys
        for k, rec in tree["files"].items()}
    return out


def _probe_clock_copier(tree: dict, scratch: Path, src_file: Path, label: str) -> dict:
    """Run the scheduled clock's stager (cosmos_backup_clock._copy_tree_files)."""
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo / "cosmos"))
    try:
        clk = _load_by_path("_clock_" + label, src_file)
    except Exception as e:                                    # noqa: BLE001
        return {"module": label, "state": "UNMEASURED",
                "kind": "IMPORT_FAILED", "detail": f"{type(e).__name__}: {e}"}
    stage = Path(scratch).parent / (Path(scratch).name + "_clock_stage_" + label)
    shutil.rmtree(extended(stage), ignore_errors=True)
    out: dict = {"module": label, "scheduled": True, "entry": "_copy_tree_files"}
    try:
        n = clk._copy_tree_files(Path(tree["scratch"]), stage)
        out["state"] = "RETURNED"
        # the proposal returns a record instead of a bare int, so the hole is nameable
        out["returned"] = n if isinstance(n, dict) else {"copied": n}
    except Exception as e:                                    # noqa: BLE001
        out["state"] = "RAISED"
        out["kind"] = getattr(e, "kind", type(e).__name__)
        out["detail"] = str(e)[:300]
    out["covered"] = {k: _bytes_landed(stage, tree, k) for k in tree["files"]}
    return out


def realscope(root: str) -> dict:
    """Run the real walkers' FILE-SELECTION step over a real subtree and count the hole.

    The fixture in `behave` proves the mechanism; this proves it on Keith's own bytes.
    Selection only - no hashing, no copying, nothing written.
    """
    _require_windows()
    rp = Path(root)
    if not rp.is_dir():
        raise ProbeRefusal("ROOT_MISSING", f"{root} is not a directory")
    repo = Path(__file__).resolve().parents[2]
    truth = {logical(os.path.join(d, n)).lower()
             for d, _s, f in os.walk(extended(rp)) for n in f}
    out = {"kind": "LONGPATH_REALSCOPE", "root": str(rp),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "files_ground_truth": len(truth),
           "long_in_scope": sum(1 for p in truth if len(p) > MAX_PATH_USABLE)}

    builds_bk = _load_by_path("_builds_cosmos_backup",
                              repo / "builds" / "backup" / "cosmos_backup.py")
    seen, raised = set(), None
    try:
        for rel in builds_bk.iter_files(rp.resolve(), frozenset((".git",))):
            seen.add(str(rp.resolve() / rel).lower())
    except Exception as e:                                    # noqa: BLE001
        raised = f"{getattr(e, 'kind', type(e).__name__)}: {str(e)[:200]}"
    missed = sorted(truth - seen)
    out["builds_backup_iter_files"] = {
        "selected": len(seen), "raised": raised, "omitted": len(missed),
        "omitted_sample": missed[:3],
        "verdict": "COVERS_LONG_PATHS" if not missed else
                   "REFUSES_LOUDLY" if raised else "SILENTLY_OMITS"}
    return out


def behave(scratch: str) -> dict:
    _require_windows()
    scratch_p = Path(scratch).resolve()
    repo = Path(__file__).resolve().parents[2]
    try:
        scratch_p.relative_to(repo)
    except ValueError:
        pass
    else:
        raise ProbeRefusal("SCRATCH_UNSAFE",
                           f"{scratch_p} is inside the live tree {repo} - "
                           "a probe that writes the tree is not a probe")
    tree = _make_deep_tree(scratch_p)
    prop = repo / "builds" / "probe" / "proposed"
    walkers = [
        _probe_running_backup(tree, scratch_p,
                              repo / "cosmos" / "cosmos_backup.py",
                              "cosmos/cosmos_backup.py"),
        _probe_builds_backup(tree),
        _probe_clock_copier(tree, scratch_p,
                            repo / "cosmos" / "cosmos_backup_clock.py",
                            "cosmos/cosmos_backup_clock.py"),
    ]
    # The proposals target modules outside this fence. Nothing here writes them - but
    # a proposal nobody ran is a hope, so both are LOADED and put through the same
    # fixture, and their verdict is measured beside the live ones.
    if (prop / "cosmos_backup.py").is_file():
        walkers.append(_probe_running_backup(tree, scratch_p,
                                             prop / "cosmos_backup.py",
                                             "PROPOSED cosmos/cosmos_backup.py"))
    if (prop / "cosmos_backup_clock.py").is_file():
        walkers.append(_probe_clock_copier(tree, scratch_p,
                                           prop / "cosmos_backup_clock.py",
                                           "PROPOSED cosmos/cosmos_backup_clock.py"))
    for w in walkers:
        cov = w.get("covered", {})
        missed = sorted(k for k, v in cov.items() if not v)
        w["missed"] = missed
        # A walker that RAISED told the truth about the hole. One that RETURNED with a
        # file count lower than the disk claimed success over a gap - the green-log defect.
        w["verdict"] = ("COVERS_LONG_PATHS" if not missed else
                        "REFUSES_LOUDLY" if w.get("state") == "RAISED" else
                        "SILENTLY_OMITS")
    rec = {"kind": "LONGPATH_BEHAVIOUR",
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "fixture": tree,
           "long_paths_enabled_registry": _long_paths_enabled(),
           "walkers": walkers}
    # Fingerprint the walkers this measurement describes. Without this, a
    # later edit of cosmos_backup.py leaves FEATURE_MASTER citing a vanished
    # build (the 07:27Z artefact vs the 12:49Z F-43 edit).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import artifact_freshness as af                                    # noqa: WPS433
    af.stamp(rec, repo, [
        "cosmos/cosmos_backup.py",
        "cosmos/cosmos_backup_clock.py",
        "builds/backup/cosmos_backup.py",
    ])
    return rec


# ---------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(prog="longpath_census")
    sub = ap.add_subparsers(dest="verb", required=True)
    c = sub.add_parser("census")
    c.add_argument("--root", action="append", required=True)
    c.add_argument("--out")
    b = sub.add_parser("behave")
    b.add_argument("--scratch", required=True)
    b.add_argument("--out")
    rs = sub.add_parser("realscope")
    rs.add_argument("--root", required=True)
    rs.add_argument("--out")
    a = ap.parse_args()

    if a.verb == "census":
        roots = [census_one(r) for r in a.root]
        rep = {"kind": "LONGPATH_CENSUS",
               "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "platform": os.name,
               "long_paths_enabled_registry": _long_paths_enabled(),
               "max_path_usable": MAX_PATH_USABLE,
               "roots": roots,
               "totals": {
                   "files_extended_walk": sum(r["files_extended_walk"] for r in roots),
                   "files_plain_walk": sum(r["files_plain_walk"] for r in roots),
                   "invisible_to_plain_walk": sum(r["invisible_to_plain_walk"] for r in roots),
                   "over_259_usable": sum(r["over_259_usable"] for r in roots),
                   "long_stat_fail_unprefixed": sum(r["long_stat_fail_unprefixed"]
                                                    for r in roots),
                   "class_a_dir_listable": sum(r["class_a_dir_listable"] for r in roots),
                   "class_a_is_file_returns_false": sum(
                       r["class_a_is_file_returns_false"] for r in roots),
                   "class_b_dir_too_long": sum(r["class_b_dir_too_long"] for r in roots),
                   "max_len": max(r["max_len"] for r in roots),
               }}
    elif a.verb == "realscope":
        rep = realscope(a.root)
    else:
        rep = behave(a.scratch)
    text = json.dumps(rep, indent=1, default=str)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeRefusal as e:
        print(json.dumps({"ok": False, "kind": e.kind, "detail": str(e)}), file=sys.stderr)
        raise SystemExit(2)
