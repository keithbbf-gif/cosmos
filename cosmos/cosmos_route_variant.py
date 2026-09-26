#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenRouter routing variants.

A routing suffix (:nitro, :floor, :exacto) changes provider order only.
It is not a catalog row. Prices and context stay on the base id, or on
the catalog variant (:free, :batch) when that is the one being called.

    https://openrouter.ai/docs/guides/routing/model-variants/overview

The cDeck setting stores one priority. The default is :floor.
Off sends the model id unchanged. A set priority is the last suffix, so it wins the sort.

    py -3.14 cosmos\\cosmos_route_variant.py --selftest
"""
from __future__ import annotations

import json
from datetime import datetime

SCHEMA = "cosmos-or-routing/1"
DEFAULT_PRIORITY = "floor"
NAME = "routing.json"
CATALOG_SUFFIXES = frozenset({"free", "batch", "thinking", "extended"})
ROUTING_SUFFIXES = frozenset({"nitro", "floor", "exacto", "online"})
ACTIVE = frozenset({"nitro", "floor", "exacto"})
PRIORITIES = ("", "floor", "nitro", "exacto")
CHOICES = (
    {"id": "", "suffix": "", "label": "off — provider order unchanged"},
    {"id": "floor", "suffix": ":floor",
     "label": "price, and flex-tier endpoints"},
    {"id": "nitro", "suffix": ":nitro",
     "label": "throughput, and priority-tier endpoints"},
    {"id": "exacto", "suffix": ":exacto",
     "label": "tool-calling quality"},
)
DOCS = (
    "https://openrouter.ai/docs/guides/routing/"
    "model-variants/overview#routing-variants"
)


class RouteVariantError(Exception):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def routing_path(paths):
    d = paths.role("state", "openrouter")
    d.mkdir(parents=True, exist_ok=True)
    return d / NAME


def catalog_id(model: str) -> str:
    """Metadata id. Keep :free/:batch. Drop routing suffixes."""
    raw = str(model or "").strip()
    if not raw:
        raise RouteVariantError("BAD_MODEL", "empty model")
    bits = raw.split(":")
    head = bits[0]
    catalog = None
    for suffix in bits[1:]:
        if suffix == "online":
            raise RouteVariantError(
                "DEPRECATED",
                ":online is retired — use the openrouter:web_search tool",
            )
        if suffix in CATALOG_SUFFIXES:
            if catalog is not None:
                raise RouteVariantError(
                    "BAD_SUFFIX", "a model id carries at most one catalog variant",
                )
            catalog = suffix
            continue
        if suffix in ROUTING_SUFFIXES:
            continue
        raise RouteVariantError("BAD_SUFFIX", f"unknown variant :{suffix}")
    if catalog:
        return head + ":" + catalog
    return head


def request_model(model: str, *, paths=None, priority=None) -> str:
    """Model string for the chat body. Saved priority is appended last."""
    raw = str(model or "").strip()
    cid = catalog_id(raw)
    if priority is None and paths is not None:
        loaded = load_routing(paths).get("priority")
        priority = DEFAULT_PRIORITY if loaded is None else loaded
    if priority is None:
        priority = DEFAULT_PRIORITY
    pri = str(priority or "").strip().lower()
    if pri in ("", "off", "none"):
        return raw
    if pri not in ACTIVE:
        raise RouteVariantError("BAD_PRIORITY", f"routing {priority!r} is not a sort")
    return cid + ":" + pri


def load_routing(paths) -> dict:
    path = routing_path(paths)
    if not path.is_file():
        return {
            "schema": SCHEMA,
            "priority": DEFAULT_PRIORITY,
            "suffix": ":floor",
            "choices": list(CHOICES),
            "docs": DOCS,
        }
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise RouteVariantError("UNREADABLE", str(e)) from e
    if not isinstance(rec, dict):
        raise RouteVariantError("UNPARSEABLE", "routing file is not an object")
    return rec


def set_routing(paths, priority: str) -> dict:
    pri = str(priority or "").strip().lower()
    if pri in ("off", "none"):
        pri = ""
    if pri not in ("",) and pri not in ACTIVE:
        raise RouteVariantError(
            "BAD_PRIORITY",
            "priority is off, floor, nitro, or exacto",
        )
    rec = {
        "schema": SCHEMA,
        "priority": pri,
        "suffix": (":" + pri) if pri else "",
        "at": _iso_now(),
        "choices": list(CHOICES),
        "docs": DOCS,
        "note": (
            "Last sorting suffix wins. :nitro and :floor can bill the "
            "service-tier rate, which can differ from the base price row."
        ),
    }
    path = routing_path(paths)
    path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return rec


def _selftest() -> int:
    import tempfile
    from pathlib import Path

    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    check(
        "catalog id keeps :free and drops :nitro",
        catalog_id("google/gemma-4-26b-a4b-it:free:nitro")
        == "google/gemma-4-26b-a4b-it:free",
    )
    check(
        "batch catalog variant stays",
        catalog_id("z-ai/glm-5.3-flash:batch:floor")
        == "z-ai/glm-5.3-flash:batch",
    )
    bad = False
    try:
        catalog_id("openai/gpt-5.2:online")
    except RouteVariantError as e:
        bad = e.kind == "DEPRECATED"
    check(":online is refused", bad)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="route-variant-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        check("unset priority is :floor",
              load_routing(paths)["priority"] == "floor"
              and request_model("google/gemma-4-26b-a4b-it:free", paths=paths)
              == "google/gemma-4-26b-a4b-it:free:floor")
        saved = set_routing(paths, "floor")
        check("setting stores :floor",
              saved["priority"] == "floor" and saved["suffix"] == ":floor")
        check("floor is last, on the free catalog id",
              request_model("google/gemma-4-26b-a4b-it:free:nitro", paths=paths)
              == "google/gemma-4-26b-a4b-it:free:floor")
        check("one call can override the saved sort",
              request_model("z-ai/glm-5.3-flash", paths=paths, priority="exacto")
              == "z-ai/glm-5.3-flash:exacto")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_route_variant: --selftest", file=sys.stderr)
    raise SystemExit(2)
