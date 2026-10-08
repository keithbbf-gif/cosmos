"""Output size. MAX is the API cap. OPTIMUM is the aim. Neither is a made-up 2k/4k/8k."""

from __future__ import annotations

from dataclasses import dataclass

from g47.refuse import Refuse

MARGIN = 0.20


def approx_tokens(text: str) -> int:
    """Rough count used only when the caller has not measured a tokenizer. Labeled as an estimate."""
    return max(1, len(text) // 4)


@dataclass(frozen=True)
class Size:
    window: int
    cached_tokens: int
    prompt_tokens: int
    margin: int
    max_tokens: int
    optimum: int | str  # positive int, or the string "float"
    estimate: bool
    keep_under: int | None = None


def compute(
    window: int | None,
    cached_tokens: int,
    prompt_tokens: int,
    optimum: int | str = "float",
    keep_under: int | None = None,
    estimate: bool = False,
) -> Size:
    if window is None or window <= 0:
        raise Refuse("WINDOW_UNMEASURED", "pass a measured context window")
    if cached_tokens < 0 or prompt_tokens < 0:
        raise Refuse("BAD_TOKEN_COUNT")
    if keep_under is not None and cached_tokens + prompt_tokens > keep_under:
        raise Refuse(
            "KEEP_UNDER",
            f"input {cached_tokens + prompt_tokens} exceeds {keep_under}",
        )
    margin = int(MARGIN * window)
    max_tokens = window - cached_tokens - prompt_tokens - margin
    if max_tokens <= 0:
        raise Refuse("MAX_LE_ZERO", "preload ate the window; start a new session")
    if optimum == "float" or optimum is None:
        aim: int | str = "float"
    else:
        if not isinstance(optimum, int) or optimum <= 0:
            raise Refuse("OPTIMUM_ZERO", "optimum is a positive int or the string float")
        # Caller passes the aim (expected output plus headroom). Clamp to MAX.
        aim = optimum if optimum <= max_tokens else max_tokens
    return Size(
        window=window,
        cached_tokens=cached_tokens,
        prompt_tokens=prompt_tokens,
        margin=margin,
        max_tokens=max_tokens,
        optimum=aim,
        estimate=estimate,
        keep_under=keep_under,
    )
