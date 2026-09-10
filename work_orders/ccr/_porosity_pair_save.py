#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Save input:output:judge:judgement for every TEAM_TABS pair.

    py -3.14 work_orders\\ccr\\_porosity_pair_save.py

Does not invent who_erred. judgement=UNMEASURED unless a scored row exists.
DS/Muse inputs are house (no patent body). Fat inputs store prefix sha + item.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LIVE = ROOT / "live"
TABS_IN = ROOT / "work_orders" / "ccr" / "CREW" / "IN" / "TABS"
MOUTH = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "TEAM_TABS"
sys.path.insert(0, str(ROOT / "cosmos"))
sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_session import require_bootup  # noqa: E402
from _crew_tab_teams import TABS  # noqa: E402
from itertools import combinations  # noqa: E402
from _pair_pack import seat_pack, system_texts, user_cached_texts  # noqa: E402

JUDGE_ID = "g46-ccr"
JUDGE_MODEL = "grok-4.6"
CRITERIA_ID = "forge-coding-v1"
PAIR_WINDOW_S = 180

# Prior scored round (do not invent new who_erred).
SCORED = {
    ("skins", "gf38-143.json", "glm-139.json"): ("a", 6, "GF38 ES-export vs GLM IIFE"),
    ("recents", "gf38-142.json", "qwen-007.json"): ("b", 7, "Qwen fetch() in pane"),
    ("spend", "gf38-140.json", "mistral-008.json"): ("b", 8, "Codestral no-op TODO"),
    ("voice", "gemini31pro-140.json", "nemo-004.json"): ("b", 9, "Nemo invented voice APIs"),
}


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _mouths(tab: str, seat: str) -> list:
    d = MOUTH / tab
    if not d.is_dir():
        return []
    files = sorted(
        (p for p in d.glob(f"{seat}-*.json") if not p.name.startswith("_")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:24]
    out = []
    for p in files:
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(rec, dict) or "schema" not in rec:
            continue
        rec["_path"] = p
        rec["_mtime"] = p.stat().st_mtime
        out.append(rec)
    out.sort(key=lambda r: r["_mtime"])
    return out


def _pair_greedy(aa: list, bb: list) -> list[tuple]:
    used_b = set()
    pairs = []
    for a in aa:
        best = None
        best_dt = PAIR_WINDOW_S + 1
        for i, b in enumerate(bb):
            if i in used_b:
                continue
            dt = abs(a["_mtime"] - b["_mtime"])
            if dt < best_dt:
                best, best_dt = i, dt
        if best is None or best_dt > PAIR_WINDOW_S:
            continue
        used_b.add(best)
        pairs.append((a, bb[best]))
    return pairs


def _fail(rec: dict) -> str:
    if rec.get("ok") is False:
        if rec.get("http") == 429:
            return "429"
        if rec.get("http") == 404:
            return "404"
        text = rec.get("text") or rec.get("detail") or ""
        if not str(text).strip():
            return "empty-text"
        return "fail"
    return ""


_PACK_CACHE: dict[str, tuple[str, str]] = {}


def _prefix(kind: str, tab: str) -> tuple[str, str]:
    ck = kind + ":" + (tab or "")
    hit = _PACK_CACHE.get(ck)
    if hit:
        return hit
    sys_t = "\n\n".join(system_texts())
    user_t = "\n\n".join(user_cached_texts(kind, tab))
    prefix = sys_t + "\n\n" + user_t
    rec = (prefix, _sha(prefix))
    _PACK_CACHE[ck] = rec
    return rec


def _input_pack(seat: str, tab: str) -> dict:
    kind = seat_pack(seat)
    item = (TABS_IN / f"{tab}.md").read_text(encoding="utf-8") if (TABS_IN / f"{tab}.md").is_file() else ""
    prefix, prefix_sha = _prefix(kind, tab)
    # Fat patent is recoverable from pack files + sha. Do not copy 407k into every row.
    body = item if kind == "fat" else (prefix + "\n\n--- TASK ---\n\n" + item)
    return {
        "pack": kind,
        "item": item,
        "item_sha256": _sha(item),
        "prefix_sha256": prefix_sha,
        "input": body,
        "input_sha256": _sha(body if kind == "house" else prefix + "\n\n--- TASK ---\n\n" + item),
        "patent_in_input": kind == "fat",
    }


def main() -> int:
    paths = CosmosPaths(str(LIVE))
    require_bootup(paths, stream="Cm")
    store = paths.role("state", "porosity")
    tdir = store / "trials"
    tdir.mkdir(parents=True, exist_ok=True)
    idx_path = store / "pair_index.json"
    seen = set()
    if idx_path.is_file():
        try:
            seen = set(json.loads(idx_path.read_text(encoding="utf-8")).get("ids") or [])
        except json.JSONDecodeError:
            seen = set()
    wrote = 0
    skipped = 0
    combos = list(TABS)
    for tab_dir in MOUTH.iterdir():
        if not tab_dir.is_dir():
            continue
        seats = sorted({p.name.split("-")[0] for p in tab_dir.glob("*.json")
                        if "-" in p.name and not p.name.startswith("_")})
        for sa, sb in combinations(seats, 2):
            rec = (tab_dir.name, sa, sb)
            if rec not in combos and (tab_dir.name, sb, sa) not in combos:
                combos.append(rec)
    for tab, sa, sb in combos:
        pairs = _pair_greedy(_mouths(tab, sa), _mouths(tab, sb))
        for a, b in pairs:
            na = a["_path"].name
            nb = b["_path"].name
            pid = f"{tab}:{na}:{nb}"
            if pid in seen:
                skipped += 1
                continue
            inp_a = _input_pack(sa, tab)
            inp_b = _input_pack(sb, tab)
            out_a = a.get("text") or a.get("detail") or ""
            out_b = b.get("text") or b.get("detail") or ""
            scored = SCORED.get((tab, na, nb))
            if scored:
                who, mag, why = scored
                judgement = {"who_erred": who, "error_mag": mag, "note": why, "kind": "SCORED"}
            else:
                who, mag, why = "unknown", None, "UNMEASURED — I/O saved, not scored"
                judgement = {"who_erred": "unknown", "error_mag": None, "note": why, "kind": "UNMEASURED"}
            trial_id = f"{tab}-{na.replace('.json','')}-{nb.replace('.json','')}"
            pack = {
                "schema": "cosmos-porosity-pair/2",
                "trial_id": trial_id,
                "tab": tab,
                "axis": "coding",
                "judge": {"id": JUDGE_ID, "model": JUDGE_MODEL, "criteria_id": CRITERIA_ID},
                "judgement": judgement,
                "input_a": inp_a,
                "input_b": inp_b,
                "output_a": out_a,
                "output_b": out_b,
                "output_a_sha256": _sha(out_a),
                "output_b_sha256": _sha(out_b),
                "model_a": a.get("model"),
                "model_b": b.get("model"),
                "http_a": a.get("http"),
                "ok_a": a.get("ok"),
                "fail_a": _fail(a),
                "http_b": b.get("http"),
                "ok_b": b.get("ok"),
                "fail_b": _fail(b),
                "usd_a": a.get("usd"),
                "usd_b": b.get("usd"),
                "mouth_a": str(a["_path"]),
                "mouth_b": str(b["_path"]),
            }
            (tdir / f"{trial_id}.json").write_text(
                json.dumps(pack, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            seen.add(pid)
            wrote += 1
    idx_path.write_text(json.dumps({"ids": sorted(seen), "n": len(seen)}, indent=1) + "\n",
                        encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": wrote, "skipped": skipped, "n_index": len(seen),
                      "trials": str(tdir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
