"""Lessons from seating the OpenRouter roster (2026-09-23 through 2026-10-01).

A 429, a 404, a 403, an empty model field, and a preamble are different
failures. So are an open batch job, a batch the API refuses, a mouth that
belongs to another pin, a 400 that names no parameter, a safety label, and
a door that asks for the task again. G47 names the class and does not retry
the same pin. It does not keep a frozen list of who was unpinned that week:
Laguna was refused on Monday and seated on Tuesday once the rail's pin table
caught up.
"""

from __future__ import annotations

from g47.refuse import Refuse


def check_slug(door_id: str, model: str) -> None:
    """Refuse the slug shapes that measured as a dead call, before any HTTP."""
    slug = (model or "").strip()
    low = slug.lower()
    if low in {"openrouter/free", "free", ":free"} or low.endswith("/free"):
        raise Refuse("NOT_A_PIN", slug)
    if ":free" in low and ":floor" in low:
        raise Refuse("FLOOR_ON_FREE", "catalog id only; :floor on :free returned response_model=None")
    if "ling-3.0-flash-vl:free" in low:
        raise Refuse("SLUG_DEAD", "use the paid inclusionai/ling-3.0-flash-vl")
    if door_id == "openrouter" and ("gpt-6-luna" in low or low.endswith("luna:floor")):
        raise Refuse("WRONG_VIA", "Luna flex is codex -m <sku>:floor, not OpenRouter chat")
    if door_id == "openrouter" and ("glm" in low or low.startswith("z-ai/")):
        raise Refuse("MIXED_VIA", "GLM's seated via is pi -p, not the chat rail")
    if door_id == "openrouter" and "inkling" in low and low.endswith(":free"):
        raise Refuse("HARNESS_GATE", "Inkling :free is agentic-only; chat ping never goes ACTIVE")


def same_pin(pin: str, served: object) -> bool:
    """True when `served` is this pin.

    Equal ids match. A pin that keeps a suffix on the served id matches
    (`anthropic/claude-sonnet-5.5:batch` served as that id, or served with
    the suffix stripped). An empty id does not match. A different model
    does not match, including a dated snapshot the batch field named while
    the job was still open.
    """
    left = (pin or "").strip()
    right = str(served or "").strip()
    if not left or right in {"", "None", "null"}:
        return False
    if left == right:
        return True
    return len(left) > len(right) and left.startswith(right) and left[len(right)] in ":/-"


def classify(
    *,
    http: int | None = None,
    detail: str = "",
    mouth: str = "",
    served_model: str | None = None,
) -> dict[str, object]:
    """Name the failure class. retry_same is always false. G47 does not re-fire."""
    low = (detail or "").lower()
    mouth_low = (mouth or "").lower()
    if "not a pinned" in low or "rotating/unpinned" in low:
        return _row(
            "PIN_GATE",
            "The live allow-list refused the catalog id before HTTP. That is not an empty mouth.",
        )
    if "not supported by the batch api" in low or (low.startswith("failed") and "batch_id=" in low):
        return _row(
            "BATCH_UNSUPPORTED",
            "The Batch API refused this model. Chat is the wrong door too. Keep the failed batch id. Do not stamp a seat.",
        )
    if "in_progress" in low and "batch_id=" in low:
        return _row(
            "BATCH_OPEN",
            "The batch id stays on the record. Do not call the job dead and do not stamp a seat. "
            "A later poll seats only when status is completed, the served id is this pin, and the host passes.",
        )
    if "batchadapter" in low or "cannot be used with the chat/completions endpoint" in low:
        return _row(
            "BATCH_DOOR",
            "Chat/completions is the wrong door. One POST /api/v1/batches. Do not repeat chat.",
        )
    if "reused a mouth" in low or "calls served" in low:
        return _row(
            "MOUTH_FOREIGN",
            "The file belonged to another served id. Do not bind this pin.",
        )
    if "what is the task" in low or "what is the task" in mouth_low:
        return _row(
            "TASK_ASK",
            "The door asked for the task. The mission was already in the prompt. Do not write the file for it.",
        )
    if http == 429 or "upstream_provider_shared_pool" in low:
        return _row(
            "UPSTREAM_POOL",
            "Shared free pool (Google AI Studio / ModelRun). Not the weekly cap. "
            "A 45-second wait still returned 429. Do not hammer this pin. Wait, another pin, or BYOK.",
        )
    if http == 404:
        return _row("SLUG_DEAD", "Slug is gone. Use the paid catalog id or skip. Do not invent a suffix.")
    if http == 403:
        return _row(
            "HARNESS_GATE",
            "Chat dispatch refused this pin. Record the gate. Do not hand the seat to another harness.",
        )
    if http == 400 and "bad request" in low and "pcm16" not in low and "audio.format" not in low:
        return _row(
            "NO_SHAPE",
            "The raw 400 names no parameter. Stop. Do not invent a body shape.",
        )
    if http == 400:
        return _row("REJECTED", "Provider rejected the pin. Do not append :floor or :free to force it.")
    if http is not None and http >= 500:
        return _row(
            "UPSTREAM",
            "Provider server error. Do not stamp a seat. Do not hammer this pin.",
        )
    if served_model is not None and str(served_model).strip() in {"", "None", "null"}:
        return _row("SKU_UNBOUND", "HTTP 200 and an empty response model. Not ACTIVE.")
    body = mouth or ""
    if not body.strip():
        return _row("EMPTY", "Empty mouth is not ACTIVE.")
    if body.lstrip().startswith("```"):
        return _row("FENCE", "A leading fence is a fail.")
    if "user safety" in mouth_low or mouth_low.strip().startswith("unsafe"):
        return _row(
            "NOT_CODE",
            "A safety label is not constants(). Do not wrap it into the math file and do not stamp a pass.",
        )
    first = body.strip().splitlines()[0].strip()
    shaped = first in {
        "NONE", "diff --git", "ITEM", "KEEP", "DROP", "HOLD", "UNMEASURED",
    } or first.startswith(("def ", "import ", "from ", "class ", "#"))
    if not shaped:
        return _row(
            "MOUTH_FORM",
            "HTTP 200 can still be preamble or CoT. Pack on is not coder-ACTIVE.",
        )
    return _row("LOOKS_SHAPED", "Grade the contract and the served SKU. Shape alone is not applied.")


def _row(kind: str, next_step: str) -> dict[str, object]:
    return {"class": kind, "retry_same": False, "next": next_step}
