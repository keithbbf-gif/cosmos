"""Majority over caller-supplied model texts. No model call."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-mixture/1"
POLICY_MIN: Final[int] = 2
POLICY_CAP: Final[int] = 5
OUTPUT_CAP: Final[int] = 8_192
MODEL_ID_CAP: Final[int] = 128
_REQUEST_HI: Final[int] = 1_000_000_000
_MODEL_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def _plain(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if type(text) is not str:
        raise Refuse("NOT_TEXT")
    if secret_shape(text):
        raise Refuse("SECRET")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None
    return text


def _model_id(value: object) -> str:
    text = _plain(value, MODEL_ID_CAP)
    if text == "" or ".." in text or _MODEL_ID.fullmatch(text) is None:
        raise Refuse("BAD_MODEL")
    return text


def _output(value: object) -> str:
    return _plain(value, OUTPUT_CAP)


def _plain_int(value: object) -> int:
    if type(value) is not int:
        raise Refuse("NOT_INT")
    return value


def _applied(requested: int) -> int:
    if requested > POLICY_CAP:
        return POLICY_CAP
    return requested


def _caps(requested: object) -> tuple[int, int]:
    if requested is None:
        return POLICY_CAP, POLICY_CAP
    asked = _plain_int(requested)
    asked = bound_int(asked, POLICY_MIN, _REQUEST_HI)
    return asked, _applied(asked)


def _rows(value: object, applied: int) -> tuple[object, ...]:
    if type(value) is tuple:
        rows = cast(tuple[object, ...], value)
        count = len(rows)
        if count < POLICY_MIN or count > applied:
            raise Refuse("BAD_COUNT", str(count))
        return rows
    if type(value) is list:
        items = cast(list[object], value)
        count = len(items)
        if count < POLICY_MIN or count > applied:
            raise Refuse("BAD_COUNT", str(count))
        return tuple(items)
    raise Refuse("BAD_COUNT")


@dataclass(frozen=True, slots=True)
class _Pick:
    ids: tuple[str, ...]
    texts: tuple[str, ...]
    text: str
    model_id: str
    index: int
    votes: int


def _collect(raw_ids: tuple[object, ...], raw_texts: tuple[object, ...]) -> _Pick:
    count = len(raw_ids)
    other = len(raw_texts)
    if count != other:
        raise Refuse("MISMATCH", f"{count}:{other}")
    if count < POLICY_MIN or count > POLICY_CAP:
        raise Refuse("BAD_COUNT", str(count))
    ids: list[str] = []
    texts: list[str] = []
    seen: set[str] = set()
    votes: dict[str, int] = {}
    first: dict[str, int] = {}
    for index in range(count):
        ident = _model_id(raw_ids[index])
        body = _output(raw_texts[index])
        if ident in seen:
            raise Refuse("BAD_MODEL")
        seen.add(ident)
        ids.append(ident)
        texts.append(body)
        if body not in votes:
            votes[body] = 1
            first[body] = index
        else:
            votes[body] += 1
    best = 0
    chosen = ""
    leaders = 0
    for body, tally in votes.items():
        if tally > best:
            best = tally
            chosen = body
            leaders = 1
        elif tally == best:
            leaders += 1
    slot = first.get(chosen)
    if leaders != 1 or slot is None or slot < 0 or slot >= count:
        raise Refuse("TIE")
    return _Pick(
        ids=tuple(ids),
        texts=tuple(texts),
        text=chosen,
        model_id=ids[slot],
        index=slot,
        votes=best,
    )


@dataclass(frozen=True, slots=True)
class Verdict:
    """Majority text. `spend_count` is the number of models. `cap` is policy."""

    schema: str
    text: str
    model_id: str
    model_ids: tuple[str, ...]
    texts: tuple[str, ...]
    index: int
    votes: int
    spend_count: int
    cap: int
    applied_cap: int
    requested_cap: int

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        body = _output(self.text)
        winner = _model_id(self.model_id)
        spend = _plain_int(self.spend_count)
        votes = _plain_int(self.votes)
        index = _plain_int(self.index)
        cap = _plain_int(self.cap)
        applied = _plain_int(self.applied_cap)
        requested = _plain_int(self.requested_cap)
        if cap != POLICY_CAP:
            raise Refuse("BAD_CAP")
        if requested < POLICY_MIN or requested > _REQUEST_HI:
            raise Refuse("OUT_OF_RANGE", f"{POLICY_MIN}..{_REQUEST_HI}")
        if _applied(requested) != applied:
            raise Refuse("BAD_CAP")
        if spend < POLICY_MIN or spend > applied:
            raise Refuse("BAD_COUNT")
        if votes < 1 or votes > spend:
            raise Refuse("BAD_COUNT")
        if index < 0 or index >= spend:
            raise Refuse("BAD_COUNT")
        if type(self.model_ids) is not tuple or type(self.texts) is not tuple:
            raise Refuse("BAD_COUNT")
        if len(self.model_ids) != spend or len(self.texts) != spend:
            raise Refuse("BAD_COUNT")
        pick = _collect(self.model_ids, self.texts)
        if votes != pick.votes or spend != len(pick.ids):
            raise Refuse("BAD_COUNT")
        if index != pick.index or not const_eq(winner, pick.model_id):
            raise Refuse("BAD_MODEL")
        if body != pick.text:
            raise Refuse("MISMATCH")

    def __repr__(self) -> str:
        shown = redact(self.text)
        if len(shown) > 80:
            shown = shown[:80]
        return (
            "Verdict("
            f"model_id={self.model_id!r}, "
            f"index={self.index}, "
            f"votes={self.votes}, "
            f"spend_count={self.spend_count}, "
            f"cap={self.cap}, "
            f"applied_cap={self.applied_cap}, "
            f"text={shown!r})"
        )


def aggregate(
    model_ids: object,
    outputs: object,
    *,
    requested_cap: object = None,
) -> Verdict:
    """Return the unique most frequent text. A tie refuses. No model is called."""
    requested, applied = _caps(requested_cap)
    id_rows = _rows(model_ids, applied)
    text_rows = _rows(outputs, applied)
    if len(id_rows) != len(text_rows):
        raise Refuse("MISMATCH", f"{len(id_rows)}:{len(text_rows)}")
    pick = _collect(id_rows, text_rows)
    return Verdict(
        schema=SCHEMA,
        text=pick.text,
        model_id=pick.model_id,
        model_ids=pick.ids,
        texts=pick.texts,
        index=pick.index,
        votes=pick.votes,
        spend_count=len(pick.ids),
        cap=POLICY_CAP,
        applied_cap=applied,
        requested_cap=requested,
    )


def rebuild(record: object) -> Verdict:
    """Re-tally a verdict. The same panel returns an equal verdict."""
    if type(record) is not Verdict:
        raise Refuse("BAD_SCHEMA")
    again = aggregate(record.model_ids, record.texts, requested_cap=record.requested_cap)
    if again != record:
        raise Refuse("MISMATCH")
    return again


__all__ = [
    "MODEL_ID_CAP",
    "OUTPUT_CAP",
    "POLICY_CAP",
    "POLICY_MIN",
    "SCHEMA",
    "Verdict",
    "aggregate",
    "rebuild",
]
