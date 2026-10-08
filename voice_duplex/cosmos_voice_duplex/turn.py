"""Turn state. Events only. The default path has no push-to-talk.

States: idle, listening, user_speaking, thinking, assistant_speaking, barge.
Mic capture is the caller's job and stays open in every state except idle.
"""

from __future__ import annotations

STATES = (
    "idle",
    "listening",
    "user_speaking",
    "thinking",
    "assistant_speaking",
    "barge",
)

EVENTS = (
    "session_ready",
    "speech_start",
    "speech_stop",
    "response_created",
    "audio_delta",
    "response_done",
    "playback_drained",
    "barge_local",
    "interrupted",
    "ptt_down",
    "ptt_up",
)


class TurnMachine:
    def __init__(self, *, push_to_talk: bool = False) -> None:
        self.state = "idle"
        self.push_to_talk = push_to_talk
        self.response_open = False
        self.playback_open = False

    def on(self, event: str) -> str:
        if event not in EVENTS:
            raise ValueError(f"unknown turn event {event}")
        nxt = self._next(event)
        self.state = nxt
        if event == "response_created":
            self.response_open = True
        elif event in {"response_done", "interrupted"}:
            self.response_open = False
        elif event == "audio_delta":
            self.playback_open = True
        elif (
            event in {"playback_drained", "barge_local", "speech_start"}
            and self.state != "assistant_speaking"
        ):
            if event in {"barge_local", "playback_drained"}:
                self.playback_open = False
        return self.state

    def _next(self, event: str) -> str:
        state = self.state
        if state == "idle" and event == "session_ready":
            return "listening"
        if state == "listening":
            if event == "speech_start" or (self.push_to_talk and event == "ptt_down"):
                return "user_speaking"
            if event == "response_created":
                return "thinking"
        if state == "user_speaking":
            if event in {"speech_stop", "ptt_up"}:
                return "thinking"
        if state == "thinking":
            if event == "audio_delta":
                return "assistant_speaking"
            if event == "response_done":
                return "listening"
            if event in {"speech_start", "barge_local"}:
                return "barge"
        if state == "assistant_speaking":
            if event == "audio_delta":
                return "assistant_speaking"
            if event == "response_done" and not self.playback_open:
                return "listening"
            if event == "playback_drained" and not self.response_open:
                return "listening"
            if event == "response_done":
                return "assistant_speaking"
            if event in {"barge_local", "speech_start", "interrupted"}:
                return "barge"
        if state == "barge":
            return "user_speaking"
        return state
