#!/usr/bin/env python3
"""Stage the PRE-ear cvm_dt_voice.py under _disposal/, per never-delete canon.

`builds/` is untracked (`git status` -> `?? builds/`), so git holds no copy of
the file this job edited and there was nothing to `git show`. The pre-edit
content is therefore REBUILT by reverse-applying this job's six recorded
edits, and then PROVEN: re-applying them forward must reproduce the live file
byte-for-byte (sha256 compared). If it does not, nothing is written and the
script refuses — a staged file that is not actually the predecessor is worse
than no staged file.

Staged inside the fence (`builds/cvm-dt/_disposal/`) rather than the tree-root
`_delme/`, which this job is fenced out of.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent / "cvm_dt_voice.py"

# (new_text_in_live_file, old_text_before_this_job) -- six edits, in file order.
EDITS = [
    (
        """    FakeBackend, RefusalKind, make_dt,
)
from cvm_dt_stt import (  # noqa: E402
    SapiTranscriber, default_ear, probe_ear, probe_sapi,
)""",
        """    FakeBackend, RefusalKind, make_dt,
)""",
    ),
    (
        '''def default_transcriber() -> Optional[Transcriber]:
    """The bound ear: VOSK when a model is handed in, else on-box SAPI.

    `probe_vosk` alone answered None on any box without the vosk wheel AND
    COSMOS_VOSK_MODEL — which is this box, and every cold peer. See
    cvm_dt_stt.probe_ear.
    """
    return default_ear()''',
        """def default_transcriber() -> Optional[Transcriber]:
    p = probe_vosk()
    return VoskTranscriber(str(p["model"])) if p.get("ok") else None""",
    ),
    (
        '''    def _bind_stt(self) -> dict:
        """VOSK if a model is handed in, else the on-box Windows recognizer.

        Was: VOSK or nothing. On a box with neither the `vosk` wheel nor
        `COSMOS_VOSK_MODEL` that meant `transcriber=None` forever, so EVERY
        utterance answered `STT_NONE` and the desktop client had no ear at
        all. `cvm_dt_stt.probe_ear` keeps VOSK first (same engine as the
        phone) and falls back to SAPI, which needs nothing installed.
        """
        ear = probe_ear()
        if self.transcriber is None and ear.get("ok"):
            self.transcriber = default_ear()
        return ear

    def _transcribe(self, pcm: bytes, rate: int) -> dict:
        stt = self.transcriber
        if stt is None:
            raise CvmDtError(
                RefusalKind.STT_NONE,
                "no local transcriber bound (%s)" % probe_ear().get("detail"))''',
        '''    def _bind_stt(self) -> dict:
        vosk = probe_vosk()
        if self.transcriber is None and vosk.get("ok"):
            self.transcriber = VoskTranscriber(str(vosk["model"]))
        return vosk

    def _transcribe(self, pcm: bytes, rate: int) -> dict:
        stt = self.transcriber
        if stt is None:
            raise CvmDtError(
                RefusalKind.STT_NONE,
                "no local transcriber bound (vosk OVERFLOW until COSMOS_VOSK_MODEL)")''',
    ),
    (
        '''        ear = self._bind_stt()
        extra: dict[str, Any] = {
            "ok": True, "tick": "idle", "state": "RUNNING", "wire": WIRE,
            "route": VOICE_ROUTE, "clock_id": PULL_CLOCK_ID,
            "mic_state": MIC_IDLE, "core_kind": None,
            "stt_kind": ear.get("kind"), "stt_engine": ear.get("engine"),
            "ticket_clock_id": None,
            "audio_owner": None, "session_id": None, "spoken": None,
            "device_name": None, "capture_name": None, "device_id": None,
            "voice_state": (
                VOICE_UNAVAILABLE if (self.transcriber is None and not ear.get("ok"))
                else VOICE_READY),
        }''',
        '''        vosk = self._bind_stt()
        extra: dict[str, Any] = {
            "ok": True, "tick": "idle", "state": "RUNNING", "wire": WIRE,
            "route": VOICE_ROUTE, "clock_id": PULL_CLOCK_ID,
            "mic_state": MIC_IDLE, "core_kind": None,
            "stt_kind": vosk.get("kind"), "ticket_clock_id": None,
            "audio_owner": None, "session_id": None, "spoken": None,
            "device_name": None, "capture_name": None, "device_id": None,
            "voice_state": (
                VOICE_UNAVAILABLE if (self.transcriber is None and not vosk.get("ok"))
                else VOICE_READY),
        }''',
    ),
    (
        '''        for k in ("mic_state", "core_kind", "stt_kind", "stt_engine", "tick",
                  "ok", "kind",
                  "ticket_clock_id", "audio_owner", "voice_state") + _DEV_KEYS:''',
        '''        for k in ("mic_state", "core_kind", "stt_kind", "tick", "ok", "kind",
                  "ticket_clock_id", "audio_owner", "voice_state") + _DEV_KEYS:''',
    ),
    (
        '''    ear_probe = probe_ear()
    ear_kind = ear_probe["kind"]
    win = probe_windows_default()''',
        '''    vosk_kind = probe_vosk()["kind"]
    win = probe_windows_default()''',
    ),
    (
        '''        and idle["stt_kind"] == ear_kind
        and idle.get("device_name") == "Headphones (FAKE HT3)"
        and (ear_kind == "STT_NONE" or probe_ear().get("ok") is True)''',
        '''        and idle["stt_kind"] == vosk_kind
        and idle.get("device_name") == "Headphones (FAKE HT3)"
        and (vosk_kind == "STT_NONE" or probe_vosk().get("ok") is True)''',
    ),
    (
        '''            "mic_state": idle.get("mic_state"), "stt_kind": ear_kind,
            "stt_engine": ear_probe.get("engine"),
            "stt_recognizer": ear_probe.get("recognizer"),
            "device_name": win.get("device_name"),''',
        '''            "mic_state": idle.get("mic_state"), "stt_kind": vosk_kind,
            "device_name": win.get("device_name"),''',
    ),
]


def main() -> int:
    live = LIVE.read_text(encoding="utf-8")
    live_sha = hashlib.sha256(live.encode("utf-8")).hexdigest()
    old = live
    for new_t, old_t in EDITS:
        if new_t and old.count(new_t) != 1:
            print("REFUSE: edit anchor not unique (%d) for %r"
                  % (old.count(new_t), new_t[:60]))
            return 2
        old = old.replace(new_t, old_t, 1)

    # Prove it: forward-apply the same edits to the reconstruction.
    fwd = old
    for new_t, old_t in EDITS:
        if old_t:
            if fwd.count(old_t) != 1:
                print("REFUSE: reverse anchor not unique for %r" % old_t[:60])
                return 2
            fwd = fwd.replace(old_t, new_t, 1)
        else:
            print("REFUSE: pure-insert edit cannot be replayed forward")
            return 2
    fwd_sha = hashlib.sha256(fwd.encode("utf-8")).hexdigest()
    if fwd_sha != live_sha:
        print("REFUSE: round trip %s != live %s" % (fwd_sha[:16], live_sha[:16]))
        return 2

    ts = time.strftime("%Y%m%d-%H%M%S")
    out = HERE / ("predispose_cvm_dt_voice_%s" % ts)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "cvm_dt_voice.py"
    dest.write_text(old, encoding="utf-8", newline="")
    rec = {
        "staged": str(dest), "staged_at": ts, "reason": "pre-ear predecessor",
        "live_sha256": live_sha, "live_bytes": len(live.encode("utf-8")),
        "pre_edit_sha256": hashlib.sha256(old.encode("utf-8")).hexdigest(),
        "pre_edit_bytes": len(old.encode("utf-8")),
        "round_trip_reproduces_live": True, "edits": len(EDITS),
        "note": "builds/ is untracked; rebuilt by reverse-applying the recorded "
                "edits, verified by replaying them forward to the live sha256.",
    }
    (out / "PREDISPOSE.json").write_text(
        json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
