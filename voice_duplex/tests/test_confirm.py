from __future__ import annotations

from cosmos_voice_duplex.confirm import ConfirmGate


class _Voice:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    def handle(
        self,
        session_id: str,
        transcript: str,
        mode: str = "voice",
        confirm_id: str | None = None,
    ) -> dict[str, object]:
        del session_id, mode
        self.calls.append((transcript, confirm_id))
        if confirm_id is None:
            return {"ok": True, "confirm_id": "nonce-1", "spoken": "Say yes to submit."}
        return {"ok": True, "spoken": "Submitted.", "confirm_id": confirm_id}


def test_yes_replays_the_original_transcript() -> None:
    voice = _Voice()
    gate = ConfirmGate(voice, session_id="duplex")
    first = gate.on_user_text("submit the nightly job")
    assert first.action == "hold"
    assert first.confirm_id == "nonce-1"
    second = gate.on_user_text("yes")
    assert second.action == "confirm"
    assert second.spoken == "Submitted."
    assert voice.calls == [
        ("submit the nightly job", None),
        ("submit the nightly job", "nonce-1"),
    ]


def test_other_words_cancel() -> None:
    voice = _Voice()
    gate = ConfirmGate(voice)
    gate.on_user_text("session close")
    cancelled = gate.on_user_text("not now")
    assert cancelled.action == "cancel"
    assert len(voice.calls) == 1


def test_destructive_is_refused_locally() -> None:
    gate = ConfirmGate()
    result = gate.on_user_text("delete the ledger")
    assert result.action == "refuse"
    assert gate.pending is None


def test_local_confirm_does_not_invent_a_nonce() -> None:
    gate = ConfirmGate()
    held = gate.on_user_text("submit the job")
    assert held.action == "hold"
    assert held.confirm_id is None
    assert "not run" in held.spoken
    done = gate.on_user_text("do it")
    assert done.action == "confirm"
    assert done.spoken == "Confirmed."
    assert done.transcript == "submit the job"


def test_tool_yes_returns_the_held_call() -> None:
    gate = ConfirmGate()
    held = gate.hold_tool("propose", '{"text": "x"}', "call-7")
    assert held.action == "hold"
    yes = gate.on_user_text("go ahead")
    assert yes.action == "confirm"
    assert yes.tool_name == "propose"
    assert yes.call_id == "call-7"
    assert yes.tool_args == '{"text": "x"}'


def test_oversized_transcript_is_refused() -> None:
    gate = ConfirmGate()
    result = gate.on_user_text("word " * 2000)
    assert result.action == "refuse"
