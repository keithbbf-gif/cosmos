"""Projection of quota shapes that are not one USD window.

Guides name a 5-hour window, a weekly cap, a separate weekly opus cap,
monthly pools, and credits. This stores the operator's label and figure.
A figure without source and observed is UNMEASURED and pauses.

This is not a ledger. It does not reduce spend and it does not change
quota rows.
"""

from __future__ import annotations

from clusters.refuse import Refuse
from clusters.store import Store
from clusters.verify import judge

SHAPES = ("five-hour", "weekly", "weekly-opus", "monthly", "credits")

_LABEL_MAX = 80


def set_shape(
    store: Store,
    *,
    provider: str,
    shape: str,
    limit_label: str,
    source: str,
    observed: str,
) -> dict:
    """Store one operator label. Refuse PROVIDER, SHAPE, or LABEL."""
    text = _provider(provider)
    named = _shape(shape)
    label = _label(limit_label)
    evidence = _evidence(source, observed)
    row = store.append(
        "quota_shape",
        {
            "id": f"qshape-{text.casefold()}-{named}",
            "provider": text,
            "shape": named,
            "limit_label": label,
        },
        evidence,
        claim="quota-shape",
    )
    verdict = str(row["verdict"])
    return {
        "provider": text,
        "shape": named,
        "verdict": verdict,
        "counted": verdict == "VERIFIED",
    }


def shape_gate(store: Store, *, provider: str, shape: str) -> dict:
    """Pause unless the last row for this id is VERIFIED.

    A missing row is Refuse("SHAPE", "missing"). The label is not a
    remainder and nothing is subtracted from spend.
    """
    text = _provider(provider)
    named = _shape(shape)
    wanted = f"qshape-{text.casefold()}-{named}"
    found: dict | None = None
    for row in store.fold("quota_shape"):
        if str(row["body"].get("id") or "") == wanted:
            found = row
    if found is None:
        raise Refuse("SHAPE", "missing")
    if found["verdict"] != "VERIFIED":
        return {"decision": "pause", "code": "UNMEASURED"}
    return {"decision": "allow", "code": "OK"}


def _evidence(source: object, observed: object) -> dict[str, str] | None:
    # Evidence rule: judge("quota-shape") runs only when source and observed
    # are both non-empty strings. Otherwise evidence is None, the figure is
    # UNMEASURED, and the gate pauses. Counted is true only on VERIFIED.
    if isinstance(source, str) and isinstance(observed, str) and source and observed:
        evidence = {"source": source, "observed": observed}
        judge("quota-shape", evidence)
        return evidence
    return None


def _provider(provider: object) -> str:
    if not isinstance(provider, str):
        raise Refuse("PROVIDER", "empty")
    if "\n" in provider or "\r" in provider or not provider.strip():
        raise Refuse("PROVIDER", "empty")
    return provider.strip()


def _shape(shape: object) -> str:
    if not isinstance(shape, str) or shape not in SHAPES:
        raise Refuse("SHAPE")
    return shape


def _label(limit_label: object) -> str:
    if (
        not isinstance(limit_label, str)
        or "\n" in limit_label
        or "\r" in limit_label
        or not 1 <= len(limit_label) <= _LABEL_MAX
    ):
        raise Refuse("LABEL")
    return limit_label
