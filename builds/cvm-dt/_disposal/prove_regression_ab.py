#!/usr/bin/env python3
"""Prove the ear regression row FAILS against the predecessor.

A regression test nobody watched fail is a green log. This runs the SAME
question against two isolated copies of the fence, in two subprocesses:

  arm OLD : the staged pre-ear cvm_dt_voice.py, with cvm_dt_stt.py absent
            (faithful: that module did not exist before this job)
  arm NEW : the fence exactly as it stands now

Question: does the desktop voice client bind an ear on this box, and what
does its selftest report for `stt_kind` / `voice_state`?

Neither arm touches the live tree: each is a `tempfile.mkdtemp` copy, and the
fence's own suites already build throwaway roots. Nothing is written back.

    py -3.14 builds/cvm-dt/_disposal/prove_regression_ab.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FENCE = Path(__file__).resolve().parents[1]
COSMOS = FENCE.parents[1] / "cosmos"

DRIVER = '''
import json, sys
sys.path.insert(0, r"{fence}")
sys.path.insert(0, r"{cosmos}")
out = {{"arm": "{arm}"}}
try:
    import cvm_dt_voice as V
    out["has_cvm_dt_stt"] = "cvm_dt_stt" in sys.modules or _has()
except Exception as e:
    out["import_error"] = "%s: %s" % (type(e).__name__, e)
    print(json.dumps(out)); raise SystemExit(0)
try:
    t = V.default_transcriber()
    out["transcriber"] = None if t is None else type(t).__name__
except Exception as e:
    out["transcriber_error"] = "%s: %s" % (type(e).__name__, e)
try:
    lv = V.run_selftest()["live_value"]
    out["stt_kind"] = lv.get("stt_kind")
    out["stt_engine"] = lv.get("stt_engine")
    out["stt_recognizer"] = lv.get("stt_recognizer")
except Exception as e:
    out["selftest_error"] = "%s: %s" % (type(e).__name__, e)
try:
    v = V.CvmDtVoice.__init__ and 1
except Exception:
    pass
print(json.dumps(out, sort_keys=True))
'''

HAS = '''
def _has():
    import importlib.util
    return importlib.util.find_spec("cvm_dt_stt") is not None
'''


def stage(arm: str, pre_ear: Path | None) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="cvm_ear_ab_%s_" % arm))
    dst = tmp / "cvm-dt"
    shutil.copytree(FENCE, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "_disposal", "*.json"))
    if pre_ear is not None:
        shutil.copy2(pre_ear, dst / "cvm_dt_voice.py")
        (dst / "cvm_dt_stt.py").unlink(missing_ok=True)
        (dst / "test_cvm_dt_stt.py").unlink(missing_ok=True)
    src = HAS + DRIVER.format(fence=dst, cosmos=COSMOS, arm=arm)
    drv = tmp / "drive.py"
    drv.write_text(src, encoding="utf-8")
    p = subprocess.run([sys.executable, str(drv)], capture_output=True,
                       text=True, timeout=900)
    line = [ln for ln in (p.stdout or "").splitlines() if ln.startswith("{")]
    got = json.loads(line[-1]) if line else {
        "arm": arm, "no_json": (p.stdout or "")[-300:],
        "stderr": (p.stderr or "")[-300:]}
    got["rc"] = p.returncode
    got["tree"] = str(dst)
    shutil.rmtree(tmp, ignore_errors=True)
    return got


def main() -> int:
    staged = sorted(Path(__file__).resolve().parent.glob(
        "predispose_cvm_dt_voice_*/cvm_dt_voice.py"))
    if not staged:
        print("REFUSE: no staged pre-ear file to compare against")
        return 2
    old = stage("OLD", staged[-1])
    new = stage("NEW", None)
    verdict = {
        "staged_predecessor": str(staged[-1]),
        "OLD": old, "NEW": new,
        "regression_row_would_fail_against_OLD": (
            old.get("transcriber") is None
            and new.get("transcriber") is not None),
        "ear_gained": {"old_stt_kind": old.get("stt_kind"),
                       "new_stt_kind": new.get("stt_kind"),
                       "new_engine": new.get("stt_engine"),
                       "new_recognizer": new.get("stt_recognizer")},
    }
    print(json.dumps(verdict, indent=1, sort_keys=True))
    return 0 if verdict["regression_row_would_fail_against_OLD"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
