"""Duplex session. One mic, one speaker, no Send button.

``feed`` takes a microphone frame. ``pull`` returns the next speaker frame.
Barge-in clears the playback queue before the rail is told, so the stop does
not wait on the network. Cloud rails are refused when the spend hook denies
them; the caller can reopen on the local rail.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from cosmos_voice_duplex.config import VoiceConfig, trim_spoken
from cosmos_voice_duplex.confirm import ConfirmGate, VoiceHandle
from cosmos_voice_duplex.pcm import silence
from cosmos_voice_duplex.playback import Playback
from cosmos_voice_duplex.rails.base import Rail, RailEvent
from cosmos_voice_duplex.spend import AllowSpend, SpendHook
from cosmos_voice_duplex.tools import ToolRegistry
from cosmos_voice_duplex.turn import TurnMachine
from cosmos_voice_duplex.vad import EnergyVad

HostText = Callable[[str], None]


@dataclass
class Caption:
    role: str
    text: str
    final: bool = True


@dataclass
class DuplexSession:
    cfg: VoiceConfig
    rail: Rail
    tools: ToolRegistry = field(default_factory=ToolRegistry)
    spend: SpendHook = field(default_factory=AllowSpend)
    voice: VoiceHandle | None = None
    on_user: HostText | None = None
    on_assistant: HostText | None = None

    def __post_init__(self) -> None:
        self.turn = TurnMachine(push_to_talk=self.cfg.push_to_talk)
        self.play = Playback(self.cfg.sample_rate, cap_ms=300)
        self.ear = EnergyVad(
            sample_rate=self.cfg.sample_rate,
            threshold=self.cfg.local_rms,
            silence_ms=self.cfg.silence_ms,
            prefix_ms=self.cfg.prefix_padding_ms,
        )
        self.gate = ConfirmGate(self.voice, session_id="duplex")
        self.captions: list[Caption] = []
        self.opened = False
        self.closed_reason = ""
        self.barge_count = 0
        self.last_error = ""
        self._ms = 0
        self._drop_audio = False
        self._await_continue = False
        self._item_id = ""

    @property
    def state(self) -> str:
        return self.turn.state

    def open(self) -> bool:
        decision = self.spend.before_open(self.rail.name)
        if not decision.allow:
            self.last_error = decision.reason
            self.closed_reason = decision.reason
            self.opened = False
            return False
        if self.closed_reason:
            self.turn = TurnMachine(push_to_talk=self.cfg.push_to_talk)
            self.closed_reason = ""
        self._apply(self.rail.open(self.cfg))
        self.opened = True
        if self.turn.state == "idle":
            self.turn.on("session_ready")
        return True

    def close(self, reason: str = "closed") -> None:
        if self.closed_reason:
            return
        self.closed_reason = reason
        self.opened = False
        self.rail.close()

    def set_mute(self, on: bool) -> None:
        self.cfg.mute = on

    def set_ptt(self, held: bool) -> None:
        self.cfg.ptt_held = held
        if not self.cfg.push_to_talk:
            return
        if held and self.turn.state == "listening":
            self.turn.on("ptt_down")
        elif not held and self.turn.state == "user_speaking":
            self.turn.on("ptt_up")

    def feed(self, pcm: bytes) -> None:
        if not self.opened or not pcm:
            return
        samples = len(pcm) // 2
        self._ms += int(samples * 1000 / self.cfg.sample_rate)
        if self._ms >= self.cfg.max_session_s * 1000:
            self.close("max_session")
            return
        self.spend.on_audio_ms(int(samples * 1000 / self.cfg.sample_rate))
        gated = self._gate_mic(pcm)
        if self.cfg.barge_in and not self.cfg.mute and gated is pcm:
            for ev in self.ear.push(pcm):
                if ev.kind == "start" and self.turn.state == "assistant_speaking":
                    self._barge()
        events = list(self.rail.push_audio(gated))
        events.extend(self.rail.poll())
        self._apply(events)

    def pull(self, n: int | None = None) -> bytes:
        size = self.cfg.frame_bytes if n is None else n
        data = self.play.read(size)
        if self.opened and not self.play.pending and self.turn.state == "assistant_speaking":
            self.turn.on("playback_drained")
            if self._await_continue:
                self._await_continue = False
                self._apply(self.rail.continue_after_playback())
        return data

    def _gate_mic(self, pcm: bytes) -> bytes:
        if self.cfg.mute:
            return silence(len(pcm))
        if self.cfg.push_to_talk and not self.cfg.ptt_held:
            return silence(len(pcm))
        if self.cfg.half_duplex and self.turn.state == "assistant_speaking":
            return silence(len(pcm))
        return pcm

    def _barge(self) -> None:
        if self.turn.state != "assistant_speaking":
            return
        played = self.play.played_ms()
        self.play.clear()
        self._drop_audio = True
        self.barge_count += 1
        self.turn.on("barge_local")
        self._apply(self.rail.barge(self._item_id, played))

    def _apply(self, events: list[RailEvent]) -> None:
        for ev in events:
            self._one(ev)

    def _one(self, ev: RailEvent) -> None:
        if ev.kind == "error":
            self.last_error = ev.text
            return
        if ev.kind == "speech_started":
            if self.turn.state == "assistant_speaking" and self.cfg.barge_in:
                self._barge()
            elif self.turn.state != "barge":
                self.turn.on("speech_start")
            return
        if ev.kind == "speech_stopped" and self.turn.state == "user_speaking":
            self.turn.on("speech_stop")
            return
        if ev.kind == "response_created":
            self.play.reset_played()
            self._drop_audio = False
            if self.turn.state == "listening":
                self.turn.on("response_created")
            return
        if ev.kind == "audio":
            if ev.item_id:
                self._item_id = ev.item_id
            if self._drop_audio or not ev.pcm:
                return
            self.play.write(ev.pcm)
            if self.turn.state in {"thinking", "listening"}:
                self.turn.on("audio_delta")
            elif self.turn.state == "assistant_speaking":
                self.turn.on("audio_delta")
            return
        if ev.kind == "assistant_transcript" and ev.text and self.cfg.captions:
            text = trim_spoken(ev.text) if ev.final else ev.text
            self.captions.append(Caption("assistant", text, ev.final))
            if ev.final and self.on_assistant is not None:
                self.on_assistant(text)
            return
        if ev.kind == "user_transcript" and ev.final:
            self._on_user(ev.text)
            return
        if ev.kind == "tool_call":
            self._on_tool(ev)
            return
        if ev.kind == "response_done":
            self._drop_audio = False
            self.turn.on("response_done")
            if self._await_continue and not self.play.pending:
                self._await_continue = False
                self._apply(self.rail.continue_after_playback())
            return

    def _on_user(self, text: str) -> None:
        if not text or text.startswith("(local capture"):
            self.captions.append(Caption("user", text or "(silence)"))
            return
        result = self.gate.on_user_text(text)
        shown = result.transcript or text
        if self.cfg.captions:
            self.captions.append(Caption("user", shown))
        if result.action == "pass":
            if self.on_user is not None:
                self.on_user(shown)
            return
        if result.action == "hold":
            self._apply(self.rail.force_say(result.spoken))
            return
        if result.action == "refuse":
            self._apply(self.rail.force_say(result.spoken))
            return
        if result.action == "cancel":
            self._apply(self.rail.force_say(result.spoken or "Cancelled."))
            if result.transcript and self.on_user is not None:
                self.on_user(result.transcript)
            return
        if result.action == "confirm" and result.tool_name:
            output = self.tools.call(result.tool_name, result.tool_args)
            self.rail.submit_tool_result(result.call_id, output)
            self._await_continue = True
            return
        if result.action == "confirm" and result.spoken:
            self._apply(self.rail.force_say(result.spoken))

    def _on_tool(self, ev: RailEvent) -> None:
        tool = self.tools.tools.get(ev.name)
        if tool is not None and tool.confirm:
            held = self.gate.hold_tool(ev.name, ev.arguments, ev.call_id)
            self._apply(self.rail.force_say(held.spoken))
            return
        output = self.tools.call(ev.name, ev.arguments)
        self.rail.submit_tool_result(ev.call_id, output)
        self._await_continue = True
