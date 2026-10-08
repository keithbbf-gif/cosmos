"""Seat loop. One scar, one SOP, then stop.

Hardcoded from the measured notes, not from a fresh theory:

- SCAR_HERO_SUMMON_20260923 classes 1–7
- SCAR_CCREW_PACK_SMOKE: no `:floor` on `:free`, class-6 CoT. Pi, Codex, and OpenCode stay choosable doors. prepare does not move a seat onto them.
- SUMMON_BY_HARNESS and SOP_CCREW_PACK_SMOKE: the what-to-do column
- This catalog run: a leading fence is class-6; a pin-gate refusal is not an empty mouth

Claude Code 2.1.88 runs `while (true)` and clears `hasAttemptedReactiveCompact`
on the next turn (`query.ts`, transition `next_turn`) and on a token-budget
continuation. This loop does neither. It places at most two calls: the
attempt, and one confirming call after a single SOP. A provider sentence that
names the legal shape (pcm16, the batch adapter, reasoning left on, the image
endpoint, Relace apply XML) is that one call. The SOP stays on `applied`.

The 2026-10-01 catalog pass added stop SOPs and one confirming shape.
An open batch and a refused batch are not dead slugs. Empty Claude keys
take effort low, once. A foreign mouth, a nameless 400, a safety label,
a task question, an unemitted file, and a free-pool 429 do not get another
call.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path

from g47.refuse import Refuse
from g47.scars import classify, same_pin

POST_SOPS = frozenset({
    "prefill",
    "agentic_door",
    "paid_slug",
    "direct_named",
    "native_door",
    "audio_pcm16",
    "batch_endpoint",
    "reasoning_on",
    "effort_low",
    "image_endpoint",
    "apply_xml",
})

_PAID = re.compile(r"use this slug instead:\s*([A-Za-z0-9_./:+-]+)", re.IGNORECASE)


@dataclass(frozen=True)
class Attempt:
    pin: str
    door: str
    form: str
    what: str = "python"
    prefill: str = ""
    applied: tuple[str, ...] = ()
    catalog_form: str = ""
    direct: bool = False
    shape: str = ""


@dataclass(frozen=True)
class Action:
    sop: str
    pin: str
    door: str
    form: str
    prefill: str
    again: bool
    reason: str
    direct: bool = False
    shape: str = ""


def _stop(attempt: Attempt, sop: str, reason: str) -> Action:
    return Action(
        sop, attempt.pin, attempt.door, attempt.form, attempt.prefill,
        False, reason, attempt.direct,
    )


def _once(attempt: Attempt, sop: str, shape: str, reason: str) -> Action:
    """One confirming call whose body is the shape the provider named."""
    return Action(
        sop, attempt.pin, attempt.door, attempt.form, attempt.prefill,
        True, reason, attempt.direct, shape,
    )


def _provider_shape(attempt: Attempt, kind: str, detail: str) -> Action | None:
    """The error text or the pin's documented call. None when nothing was named."""
    low = (detail or "").lower()
    pin = attempt.pin.lower()
    if "lyria" in pin:
        return _stop(
            attempt, "stop",
            "Lyria generates music. Chat audio is the wrong endpoint. Do not repeat it.",
        )
    if "batchadapter" in low or "cannot be used with the chat/completions endpoint" in low:
        return _once(
            attempt, "batch_endpoint", "batch",
            "Batch adapter. One POST /api/v1/batches. Do not repeat chat/completions.",
        )
    if kind == "REJECTED" and ("pcm16" in low or "audio.format" in low):
        return _once(
            attempt, "audio_pcm16", "pcm16",
            "Streamed audio rejects wav. The error names pcm16. One shape change.",
        )
    if kind == "EMPTY" and "claude" in pin and "empty keys" in low:
        return _once(
            attempt, "effort_low", "effort_low",
            "Mouth keys are empty. One call with reasoning effort low and a larger cap. Do not send effort none.",
        )
    if "reasoning is mandatory" in low or (kind == "EMPTY" and "claude" in pin):
        return _once(
            attempt, "reasoning_on", "reasoning_on",
            "Reasoning stays on. Do not send effort none. One budget call.",
        )
    if kind == "REJECTED" and pin.startswith("relace/"):
        return _once(
            attempt, "apply_xml", "apply_xml",
            "Relace Apply wants one user message: instruction, code, update. No system turn.",
        )
    return None


def _paid_slug(detail: str) -> str | None:
    """Only a slug the provider named. Never invent one."""
    match = _PAID.search(detail or "")
    if match is None:
        return None
    slug = match.group(1).strip(".,'\"")
    low = slug.lower()
    if "/" not in slug or ":free" in low or ":floor" in low:
        return None
    return slug


def prepare(attempt: Attempt, *, catalog_form: str | None = None) -> Attempt:
    """Apply the pre-call SOPs. Known-bad doors are not fired."""
    pin = (attempt.pin or "").strip()
    low = pin.lower()
    if low in {"openrouter/free", "free", ":free"} or low.endswith("/free"):
        raise Refuse("NOT_A_PIN", pin)
    if ":free" in low and ":floor" in low:
        raise Refuse("FLOOR_ON_FREE", "catalog id only")
    if low.endswith(("-latest",)) or pin.startswith("~"):
        raise Refuse("NOT_A_PIN", pin)
    applied = attempt.applied
    door = attempt.door
    # The caller's door is the route. It is not the one post-call SOP.
    # Codex, OpenCode, and Pi remain installed. Naming one keeps it.
    # This function does not move a cosmos-harness or openrouter seat onto them.
    if door == "grok":
        raise Refuse("GROK_NOT_A_WORKER", "grok.exe is not a CCrew worker")
    form = catalog_form or attempt.catalog_form or attempt.form
    if form != attempt.form and "match_form" not in applied:
        applied = applied + ("match_form",)
    return replace(
        attempt,
        pin=pin,
        door=door,
        form=form,
        catalog_form=form,
        applied=applied,
    )


def _october(attempt: Attempt, kind: str, detail: str) -> Action:
    """Named outcome from the 2026-10-01 pass. sop `stop` means this detail is not one of them."""
    low = (detail or "").lower()
    if kind == "BATCH_OPEN" or ("in_progress" in low and "batch_id=" in low):
        return _stop(
            attempt, "batch_open",
            "Batch is still in progress. Keep the batch id. Do not stamp a seat. "
            "Poll only when status is completed, the served id is this pin, and the host passes.",
        )
    if kind == "BATCH_UNSUPPORTED" or "not supported by the batch api" in low or (
        "failed" in low and "batch_id=" in low
    ):
        return _stop(
            attempt, "batch_unsupported",
            "Batch API refused this model. Keep the failed batch id. Do not stamp a seat and do not return to chat.",
        )
    if kind == "BATCH_DOOR":
        return _once(
            attempt, "batch_endpoint", "batch",
            "Batch adapter. One POST /api/v1/batches. Do not repeat chat/completions.",
        )
    if kind == "MOUTH_FOREIGN":
        return _stop(
            attempt, "foreign_mouth",
            "The constants file came from another served id. Do not bind this pin.",
        )
    if kind == "NO_SHAPE":
        return _stop(
            attempt, "no_shape",
            "The raw 400 names no parameter. Stop. Do not invent a body.",
        )
    if kind == "NOT_CODE":
        return _stop(
            attempt, "not_code",
            "A safety label or a story is not the math file. Do not stamp a pass.",
        )
    if kind == "TASK_ASK":
        return _stop(
            attempt, "task_ask",
            "The door asked what the task is. The mission was already sent. Do not write the file for it.",
        )
    return _stop(attempt, "stop", "")


def action_for(attempt: Attempt, scar: str, detail: str = "") -> Action:
    """The one SOP for this scar. A second post-call SOP does not fire."""
    if any(name in attempt.applied for name in POST_SOPS):
        return _stop(attempt, "stop", "one SOP already applied")
    kind = scar or ""
    if kind == "UPSTREAM_POOL":
        return _stop(
            attempt, "pool_hold",
            "Shared free pool. A 45-second wait is the same pool. Do not hammer this pin. Wait, another pin, or BYOK.",
        )
    if kind == "UPSTREAM":
        return _stop(
            attempt, "upstream",
            "Provider server error. Do not stamp a seat and do not hammer this pin.",
        )
    if kind in {"BATCH_OPEN", "BATCH_UNSUPPORTED", "BATCH_DOOR", "MOUTH_FOREIGN", "NO_SHAPE", "NOT_CODE", "TASK_ASK"}:
        return _october(attempt, kind, detail)
    if kind == "PIN_GATE":
        if attempt.direct:
            return _stop(attempt, "stop", "Named id was already called. Do not invent a second route.")
        return Action(
            "direct_named", attempt.pin, attempt.door, attempt.form, attempt.prefill,
            True, "Call the named catalog id. The allow-list refusal is not a mouth.", True,
        )
    if kind == "SLUG_DEAD":
        named = _october(attempt, kind, detail)
        if named.sop != "stop":
            return named
        shaped = _provider_shape(attempt, kind, detail)
        if shaped is not None and shaped.sop == "batch_endpoint":
            return shaped
        paid = _paid_slug(detail)
        if paid and paid != attempt.pin:
            return Action(
                "paid_slug", paid, attempt.door, attempt.form, attempt.prefill,
                True, "Provider named the paid id. Do not invent a suffix.", attempt.direct,
            )
        return _stop(attempt, "stop", "Dead slug with no named replacement.")
    if kind == "HARNESS_GATE":
        return _stop(
            attempt, "stop",
            "COSMOS harness recorded the gate. OpenCode stays available. It is not applied.",
        )
    if kind in {"MOUTH_FORM", "FENCE"}:
        if attempt.prefill:
            return _stop(attempt, "stop", "Prefill already applied. Mouth still failed form.")
        prefill = "signature" if attempt.what == "python" else "ping"
        return Action(
            "prefill", attempt.pin, attempt.door, attempt.form, prefill,
            True, "Class-6 CoT or a fence. One prefill of the contract line.", attempt.direct,
        )
    if kind == "SKU_UNBOUND":
        return _stop(attempt, "stop", "Empty served model is not ACTIVE. Do not append :floor.")
    if kind == "MIXED_VIA":
        return _stop(
            attempt, "stop",
            "COSMOS harness keeps the caller's door. Pi stays available. It is not applied.",
        )
    if kind == "WRONG_VIA":
        return _stop(
            attempt, "stop",
            "COSMOS harness keeps the caller's door. Codex stays available. It is not applied.",
        )
    if kind == "FORM_MISS" and attempt.form != attempt.catalog_form and "match_form" not in attempt.applied:
        return Action(
            "match_form", attempt.pin, attempt.door, attempt.catalog_form, attempt.prefill,
            True, "Probe the catalog output form, not a text task.", attempt.direct,
        )
    if kind == "FORM_MISS" and attempt.form == "image":
        return _once(
            attempt, "image_endpoint", "images",
            "Image models seat on POST /api/v1/images. Chat modalities returned no bytes.",
        )
    if kind == "LOOKS_SHAPED":
        return _stop(attempt, "grade", "Shape is not a seat. Grade the contract and the SKU.")
    if kind == "HOST_FAIL":
        return _stop(
            attempt, "unemitted",
            "The model did not emit the constants file. Do not add a header around a line it did not write.",
        )
    shaped = _provider_shape(attempt, kind, detail)
    if shaped is not None:
        return shaped
    return _stop(attempt, "stop", "No second call for " + (kind or "unknown"))


def _served_id(observed: dict[str, object]) -> str:
    """The id the call reported. Blank, None, and null are empty."""
    raw = observed.get("served")
    if raw is None:
        return ""
    text = str(raw).strip()
    if text in {"", "None", "null"}:
        return ""
    return text


def _http_code(observed: dict[str, object]) -> int | None:
    raw = observed.get("http")
    return raw if isinstance(raw, int) else None


def _journal(
    path: Path | None,
    attempt: Attempt,
    *,
    scar: str,
    sop: str,
    again: bool,
    shape: str,
    reason: str,
    http: int | None,
    served: str,
) -> None:
    """One fail-closed line. The line never says the pin is seated."""
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "again": again,
        "http": http,
        "pin": attempt.pin,
        "reason": reason,
        "scar": scar,
        "seated": False,
        "served": served,
        "shape": shape,
        "sop": sop,
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def run(
    attempt: Attempt,
    call,
    *,
    catalog_form: str | None = None,
    journal: Path | None = None,
) -> dict[str, object]:
    """Drive prepare → call → one SOP → optional confirming call → stop.

    A caller flag is not a seat. ``seated`` is true only when that flag is
    boolean true and ``same_pin`` matches the served id. An empty served id
    is ``SKU_UNBOUND``. A different id is ``MOUTH_FOREIGN``. Neither gets a
    second call. The journal line, when ``journal`` is set, keeps
    ``seated`` false.
    """
    current = prepare(attempt, catalog_form=catalog_form)
    observed: dict[str, object] = {}
    scar = ""
    served = ""
    action = _stop(current, "stop", "no call")
    turn = 0
    for turn in range(1, 3):
        observed = call(current)
        served = _served_id(observed)
        http = _http_code(observed)
        detail = str(observed.get("detail") or "")
        if observed.get("seated") is True:
            if same_pin(current.pin, served):
                _journal(
                    journal, current, scar="", sop="", again=False, shape=current.shape,
                    reason="same_pin", http=http, served=served,
                )
                return {
                    "seated": True,
                    "turns": turn,
                    "sop": None,
                    "pin": current.pin,
                    "door": current.door,
                    "form": current.form,
                    "prefill": current.prefill,
                    "shape": current.shape,
                    "scar": None,
                    "served": served,
                }
            scar = "SKU_UNBOUND" if not served else "MOUTH_FOREIGN"
            action = action_for(current, scar, detail)
            _journal(
                journal, current, scar=scar, sop=action.sop, again=False, shape=action.shape,
                reason=action.reason, http=http, served=served,
            )
            break
        served_raw = observed.get("served")
        scar = str(classify(
            http=http,
            detail=detail,
            mouth=str(observed.get("mouth") or ""),
            served_model=None if served_raw is None else str(served_raw),
        )["class"])
        if observed.get("scar"):
            scar = str(observed["scar"])
        action = action_for(current, scar, detail)
        _journal(
            journal, current, scar=scar, sop=action.sop, again=bool(action.again),
            shape=action.shape, reason=action.reason, http=http, served=served,
        )
        if not action.again or turn == 2:
            break
        current = replace(
            current,
            pin=action.pin,
            door=action.door,
            form=action.form,
            prefill=action.prefill,
            direct=action.direct,
            shape=action.shape,
            applied=current.applied + (action.sop,),
        )
    return {
        "seated": False,
        "turns": turn,
        "sop": action.sop,
        "again": action.again and turn == 1,
        "pin": current.pin,
        "door": current.door,
        "form": current.form,
        "prefill": current.prefill,
        "shape": current.shape,
        "scar": scar,
        "reason": action.reason,
        "served": served,
    }
