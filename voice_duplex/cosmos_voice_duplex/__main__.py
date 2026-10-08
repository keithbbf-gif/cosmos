"""``cosmos-voice`` command. Prints config. Does not print a key. Does not dial out.

``--desktop`` checks that the audio extra imports. ``--seconds N`` runs the
local rail on the shared-mode sound card for N seconds. ``--connect`` is
refused unless the key variable is set, and even then this command does not
open a socket. Attach a transport to ``XaiRealtimeRail`` for a live session.
"""

from __future__ import annotations

import argparse
import importlib
import time

from cosmos_voice_duplex import __version__
from cosmos_voice_duplex.config import RAILS, VoiceConfig
from cosmos_voice_duplex.desktop.loop import SoundDeviceLoop
from cosmos_voice_duplex.desktop.runner import build_session
from cosmos_voice_duplex.rails.xai_realtime import api_key_from_env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cosmos-voice")
    parser.add_argument("--rail", default="auto", choices=list(RAILS))
    parser.add_argument("--voice", default="eve")
    parser.add_argument("--desktop", action="store_true")
    parser.add_argument("--connect", action="store_true")
    parser.add_argument("--seconds", type=int, default=0)
    args = parser.parse_args(argv)
    cfg = VoiceConfig(rail=args.rail, voice=args.voice)
    key_set = bool(api_key_from_env(cfg))
    print(f"cosmos-voice {__version__}")
    print(
        f"rail={cfg.rail} voice={cfg.voice} rate={cfg.sample_rate} "
        f"ptt={cfg.push_to_talk} barge_in={cfg.barge_in}"
    )
    print(f"model={cfg.model}")
    print("api_key=" + ("set" if key_set else "missing"))
    if args.connect and not key_set:
        print("Cloud connect refused: the API key variable is empty.")
        return 2
    if args.connect and key_set:
        print("Key is present. This command does not open a socket.")
    if not args.desktop:
        print("Desktop loop is off. Pass --desktop to use the sound card.")
        return 0
    try:
        importlib.import_module("sounddevice")
    except ImportError:
        print("sounddevice is not installed. Install the audio extra.")
        return 2
    if args.seconds <= 0:
        print("Pass --seconds N to run the local duplex loop.")
        return 0
    local = VoiceConfig(rail="local", voice=args.voice)
    session = build_session(local)
    if not session.open():
        print(session.last_error or "open refused")
        return 1
    loop = SoundDeviceLoop(session)
    try:
        loop.start()
    except Exception as exc:
        print(f"Audio device did not open: {type(exc).__name__}")
        session.close("audio")
        return 2
    deadline = time.monotonic() + args.seconds
    try:
        while time.monotonic() < deadline:
            loop.pump()
            time.sleep(0.02)
    finally:
        loop.stop()
        session.close("cli")
    print("state=" + session.state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
