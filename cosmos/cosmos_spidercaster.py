"""SpiderCaster as a Cosmos motif plugin.

The package at SPIDERCASTER_HOME (or the working tree) is the standalone
product. Cosmos and Cosmos Code read plugin/cosmos.json. cDeck edits labels,
models, and workflow order on the website profile. Hands stay the package
hands. Nothing here publishes.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROLE_IDS = (
    "architect", "content", "frontend", "graphics", "visual", "seo", "deployer",
)
_MODEL = re.compile(r"^[A-Za-z0-9_.:/@+-]{1,80}$")
_HANDS = {
    "architect": ("brief_read", "frame_pick", "mold_pick", "library_bind"),
    "content": ("copy_read", "copy_gap"),
    "frontend": ("plan_offline", "render"),
    "graphics": ("asset_list", "vault_photos"),
    "visual": ("check_site",),
    "seo": ("uniqueness", "meta_basics"),
    "deployer": ("ticket_write",),
}
_LABELS = {
    "architect": "Architect",
    "content": "Content",
    "frontend": "Frontend",
    "graphics": "Graphics",
    "visual": "Visual critic",
    "seo": "SEO",
    "deployer": "Deployer",
}
_MODELS = {
    "architect": "upstage/solar-pro4",
    "content": "upstage/solar-pro4",
    "frontend": "upstage/solar-pro4",
    "graphics": "google/gemma-4-31b-it",
    "visual": "google/gemma-4-31b-it",
    "seo": "deepseek/deepseek-v4-flash",
    "deployer": "deepseek/deepseek-v4-flash",
}


def _baked() -> dict:
    return {
        "schema": "cosmos-plugin/1",
        "id": "spidercaster",
        "title": "SpiderCaster",
        "module": "motif",
        "hosts": ["standalone", "cosmos", "cosmos-code"],
        "cdeck": {"tab": "website", "label": "Spidercaster", "sidebar": "left"},
        "publish": "human",
        "roles": [
            {"id": rid, "label": _LABELS[rid], "model": _MODELS[rid],
             "hands": list(_HANDS[rid])}
            for rid in ROLE_IDS
        ],
        "workflow": list(ROLE_IDS),
    }


def manifest_path() -> Path | None:
    env = os.environ.get("SPIDERCASTER_HOME")
    candidates = []
    if env:
        candidates.append(Path(env) / "plugin" / "cosmos.json")
    candidates.append(Path(r"V:\a\Ai\spidercaster\working\plugin\cosmos.json"))
    for path in candidates:
        if path.is_file():
            return path
    return None


def base_manifest() -> dict:
    path = manifest_path()
    if path is None:
        return _baked()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _baked()
    if not isinstance(data, dict) or data.get("id") != "spidercaster":
        return _baked()
    if data.get("module") != "motif":
        return _baked()
    return data


class SpiderError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def public_plugin(raw=None) -> dict:
    """Validated setup. Hands always come from the package, never the editor."""
    base = base_manifest()
    base_roles = {}
    for row in base.get("roles") or []:
        if isinstance(row, dict) and row.get("id") in _HANDS:
            base_roles[row["id"]] = row
    src = raw if isinstance(raw, dict) else {}
    incoming = {}
    for row in src.get("roles") or []:
        if isinstance(row, dict) and row.get("id") in _HANDS:
            incoming[str(row["id"])] = row
    roles = []
    for rid in ROLE_IDS:
        got = incoming.get(rid) or {}
        baked = base_roles.get(rid) or {}
        label = str(got.get("label") or baked.get("label") or _LABELS[rid]).strip()[:48]
        model = str(got.get("model") or baked.get("model") or _MODELS[rid]).strip()
        if not label:
            raise SpiderError("BAD_INPUT", f"role {rid} needs a label")
        if not _MODEL.fullmatch(model):
            raise SpiderError("BAD_INPUT", f"model for {rid} is not a model id")
        roles.append({
            "id": rid,
            "label": label,
            "model": model,
            "hands": list(_HANDS[rid]),
        })
    wf = src.get("workflow")
    if not isinstance(wf, list) or not wf:
        wf = list(ROLE_IDS)
    wf = [str(x).strip() for x in wf]
    if len(wf) != len(ROLE_IDS) or set(wf) != set(ROLE_IDS):
        raise SpiderError("BAD_INPUT", "workflow must be the seven seats, once each")
    return {
        "schema": "cosmos-plugin/1",
        "id": "spidercaster",
        "module": "motif",
        "hosts": ["standalone", "cosmos", "cosmos-code"],
        "cdeck": {"tab": "website", "label": "Spidercaster", "sidebar": "left"},
        "publish": "human",
        "roles": roles,
        "workflow": wf,
    }


def _selftest() -> int:
    base = public_plugin(None)
    assert base["hosts"] == ["standalone", "cosmos", "cosmos-code"]
    assert base["cdeck"]["sidebar"] == "left"
    assert base["publish"] == "human"
    assert [r["id"] for r in base["roles"]] == list(ROLE_IDS)
    edited = public_plugin({
        "roles": [
            {"id": "architect", "label": "Lead", "model": "upstage/solar-pro4",
             "hands": ["ticket_write", "publish"]},
        ],
        "workflow": ["deployer", "seo", "visual", "graphics", "frontend", "content", "architect"],
    })
    arch = next(r for r in edited["roles"] if r["id"] == "architect")
    assert arch["label"] == "Lead"
    assert arch["hands"] == ["brief_read", "frame_pick", "mold_pick", "library_bind"]
    assert edited["workflow"][0] == "deployer"
    bad = False
    try:
        public_plugin({"workflow": ["architect"]})
    except SpiderError as exc:
        bad = exc.kind == "BAD_INPUT"
    if not bad:
        raise SystemExit("short workflow was accepted")
    print("spidercaster plugin selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
