#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_porosity — pairwise orthogonal porosity tensor.

Porosity of a coder is a VECTOR on named axes, measured against another
model. Pair magnitude = disagreement_frequency × error_magnitude.
More disagreement → more orthogonal that pair. Tensor grid T[i,j,a]
seats models for token efficiency and error discovery.

JSONL is the observation log (authority for this measurement). SQLite is
a rebuildable projection, never authority. GET never mkdir. GET never
invents a score. UNMEASURED until observed. Rotators refused.

    py -3.14 cosmos\\cosmos_porosity.py --selftest
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-porosity-tensor/2"
OBS_NAME = "obs.jsonl"
DB_NAME = "porosity.sqlite"
ROTATING = frozenset({
    "openrouter/free", "openrouter/auto", "openrouter/free:free",
    "openrouter/pareto-code",
})
PROFILE_AXES = {
    "forge": ("coding", "spec", "security", "tests", "tool_use"),
    "crucible": ("law", "facts", "procedure"),
    "diligence": ("bull", "bear", "risk"),
    "differentiator": ("diagnosis", "plan"),
    "docket": ("novelty", "enablement", "prior_art"),
    "website": ("copy", "layout", "a11y"),
}
DEFAULT_AXES = ("task",)
WHO_OK = frozenset({"", "a", "b", "both", "none", "unknown"})
SRC_OK = frozenset({"local", "federation"})


class PorosityError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _f(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def store_dir(paths) -> Path:
    return paths.role("state", "porosity")


def obs_path(paths) -> Path:
    return store_dir(paths) / OBS_NAME


def db_path(paths) -> Path:
    return store_dir(paths) / DB_NAME


def axes_for(profile: str) -> tuple[str, ...]:
    p = str(profile or "").strip().lower()
    return PROFILE_AXES.get(p) or DEFAULT_AXES


def _pin(model) -> str:
    m = str(model or "").strip()
    if not m:
        raise PorosityError("BAD_INPUT", "model is required")
    if m.lower() in ROTATING:
        raise PorosityError("REFUSED", f"rotator id {m!r} is not assignable")
    return m


def _pair(a: str, b: str) -> tuple[str, str]:
    if a == b:
        raise PorosityError("REFUSED", "pair requires two distinct models")
    lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
    return lo, hi


def _who_cell(model_a: str, model_b: str, who: str, lo: str, hi: str):
    """Map who_erred (relative to model_a/b) onto lo/hi. None = unscored."""
    w = str(who or "").strip().lower()
    if w in ("", "unknown"):
        return None
    if w == "none":
        return "none"
    if w == "both":
        return "both"
    if w == "a":
        erred = model_a
    elif w == "b":
        erred = model_b
    else:
        return None
    if erred == lo:
        return "lo"
    if erred == hi:
        return "hi"
    return None


def _axis(axis, profile: str) -> str:
    a = str(axis or "").strip().lower()
    if not a:
        a = axes_for(profile)[0]
    return a[:80]


def empty_snapshot() -> dict:
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "n_obs": 0,
        "n_pairs": 0,
        "pairs": [],
        "tensor": {},
        "complement": {},
        "complement_kind": "UNMEASURED",
        "axes": list(DEFAULT_AXES),
        "note": (
            "T[i,j,a] |v| = disagreement_frequency × error_magnitude. "
            "C[i,j,a] complement = rescue / co-failure / XOR-error from who_erred. "
            "Unsigned mag does not split help vs hurt. Complement UNMEASURED until "
            "who_erred is scored (a|b|both|none). Does not invent scores."
        ),
    }


def load_obs(paths) -> list[dict]:
    p = obs_path(paths)
    if not p.is_file():
        return []
    out = []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("model_a") and rec.get("model_b"):
            out.append(rec)
    return out


def _fold_rows(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    acc: dict[tuple[str, str, str], dict] = {}
    for o in rows:
        a = str(o.get("model_a") or "")
        b = str(o.get("model_b") or "")
        if not a or not b or a == b:
            continue
        lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
        axis = str(o.get("axis") or "task")
        key = (lo, hi, axis)
        slot = acc.get(key)
        if slot is None:
            slot = {"n": 0, "disagree_n": 0, "err_sum": 0.0, "err_n": 0,
                    "tokens_sum": 0.0, "tokens_n": 0,
                    "scored_n": 0, "none_n": 0, "both_n": 0,
                    "xor_n": 0, "style_n": 0,
                    "rescue_lo_hi": 0, "rescue_hi_lo": 0}
            acc[key] = slot
        slot["n"] += 1
        disc = o.get("disagree") in (True, 1, "1", "true", "yes")
        if disc:
            slot["disagree_n"] += 1
        em = _f(o.get("error_mag"))
        if em is not None:
            slot["err_sum"] += em
            slot["err_n"] += 1
        for tok in (_f(o.get("tokens_a")), _f(o.get("tokens_b"))):
            if tok is not None:
                slot["tokens_sum"] += tok
                slot["tokens_n"] += 1
        who = str(o.get("who_erred") or "").strip().lower()
        cell = _who_cell(a, b, who, lo, hi)
        if cell is not None:
            slot["scored_n"] += 1
            if cell == "none":
                slot["none_n"] += 1
                if disc:
                    slot["style_n"] += 1
            elif cell == "both":
                slot["both_n"] += 1
            elif cell == "lo":
                slot["xor_n"] += 1
                slot["rescue_lo_hi"] += 1
            elif cell == "hi":
                slot["xor_n"] += 1
                slot["rescue_hi_lo"] += 1
    out = {}
    for key, s in acc.items():
        n = s["n"]
        freq = None if n == 0 else round(s["disagree_n"] / n, 6)
        mean_err = None if s["err_n"] == 0 else round(s["err_sum"] / s["err_n"], 4)
        mag = None if freq is None or mean_err is None else round(freq * mean_err, 6)
        mean_tok = None if s["tokens_n"] == 0 else round(
            s["tokens_sum"] / s["tokens_n"], 2)
        scored = s["scored_n"]
        lo_wrong = s["rescue_lo_hi"] + s["both_n"]
        hi_wrong = s["rescue_hi_lo"] + s["both_n"]
        rescue_hi_given_lo = (
            None if lo_wrong == 0 else round(s["rescue_lo_hi"] / lo_wrong, 6))
        rescue_lo_given_hi = (
            None if hi_wrong == 0 else round(s["rescue_hi_lo"] / hi_wrong, 6))
        cofail = None if scored == 0 else round(s["both_n"] / scored, 6)
        xor_r = None if scored == 0 else round(s["xor_n"] / scored, 6)
        style_r = None if scored == 0 else round(s["style_n"] / scored, 6)
        signed = None
        if xor_r is not None and cofail is not None:
            w = 1.0 if mean_err is None else mean_err
            signed = round((xor_r - cofail) * w, 6)
        ckind = "UNMEASURED" if scored == 0 else "MEASURED"
        out[key] = {
            "model_a": key[0], "model_b": key[1], "axis": key[2],
            "n": n,
            "disagree_n": s["disagree_n"],
            "freq": freq,
            "mean_err": mean_err,
            "mag": mag,
            "orthogonality": mag,
            "mean_tokens": mean_tok,
            "kind": "UNMEASURED" if mag is None else "MEASURED",
            "scored_n": scored,
            "rescue_hi_given_lo": rescue_hi_given_lo,
            "rescue_lo_given_hi": rescue_lo_given_hi,
            "cofail": cofail,
            "xor_err": xor_r,
            "style_fight": style_r,
            "signed": signed,
            "complement_kind": ckind,
        }
    return out


def snapshot(paths, *, profile: str = "") -> dict:
    """GET fold. Never mkdir. Never invents."""
    rows = load_obs(paths)
    rec = empty_snapshot()
    rec["axes"] = list(axes_for(profile)) if profile else list(DEFAULT_AXES)
    if not rows:
        return rec
    folds = _fold_rows(rows)
    pairs = [folds[k] for k in sorted(folds)]
    tensor: dict[str, dict] = {}
    complement: dict[str, dict] = {}
    for f in pairs:
        pk = "%s|%s" % (f["model_a"], f["model_b"])
        tensor.setdefault(pk, {})[f["axis"]] = {
            "n": f["n"], "freq": f["freq"], "mean_err": f["mean_err"],
            "mag": f["mag"], "kind": f["kind"],
        }
        complement.setdefault(pk, {})[f["axis"]] = {
            "scored_n": f["scored_n"],
            "rescue_hi_given_lo": f["rescue_hi_given_lo"],
            "rescue_lo_given_hi": f["rescue_lo_given_hi"],
            "cofail": f["cofail"],
            "xor_err": f["xor_err"],
            "style_fight": f["style_fight"],
            "signed": f["signed"],
            "kind": f["complement_kind"],
        }
    rec.update({
        "kind": "MEASURED" if any(p["mag"] is not None for p in pairs)
        else "FREQ_ONLY" if pairs else "UNMEASURED",
        "complement_kind": (
            "MEASURED" if any(p["complement_kind"] == "MEASURED" for p in pairs)
            else "UNMEASURED"),
        "n_obs": len(rows),
        "n_pairs": len(pairs),
        "pairs": pairs,
        "tensor": tensor,
        "complement": complement,
        "db": "PRESENT" if db_path(paths).is_file() else "NO_HOST",
    })
    return rec


def _rebuild_sqlite(paths, rows: list[dict]) -> None:
    d = store_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    fp = db_path(paths)
    con = sqlite3.connect(str(fp))
    try:
        con.execute("DROP TABLE IF EXISTS obs")
        con.execute(
            "CREATE TABLE obs ("
            "seq INTEGER PRIMARY KEY AUTOINCREMENT,"
            "at TEXT, trial_id TEXT, profile TEXT, stage TEXT, axis TEXT,"
            "model_a TEXT, model_b TEXT, pair_lo TEXT, pair_hi TEXT,"
            "disagree INTEGER, error_mag REAL, tokens_a REAL, tokens_b REAL,"
            "who_erred TEXT, source TEXT, note TEXT)"
        )
        con.execute(
            "CREATE INDEX idx_pair_axis ON obs(pair_lo, pair_hi, axis)")
        con.execute("DROP TABLE IF EXISTS pair_fold")
        con.execute(
            "CREATE TABLE pair_fold ("
            "pair_lo TEXT NOT NULL, pair_hi TEXT NOT NULL, axis TEXT NOT NULL,"
            "n INTEGER, disagree_n INTEGER, freq REAL, mean_err REAL, mag REAL,"
            "kind TEXT,"
            "scored_n INTEGER, rescue_hi_given_lo REAL, rescue_lo_given_hi REAL,"
            "cofail REAL, xor_err REAL, style_fight REAL, signed REAL,"
            "complement_kind TEXT,"
            "PRIMARY KEY (pair_lo, pair_hi, axis))"
        )
        for o in rows:
            a = str(o.get("model_a") or "")
            b = str(o.get("model_b") or "")
            if not a or not b:
                continue
            lo, hi = (a, b) if a.lower() <= b.lower() else (b, a)
            em = _f(o.get("error_mag"))
            con.execute(
                "INSERT INTO obs (at, trial_id, profile, stage, axis, "
                "model_a, model_b, pair_lo, pair_hi, disagree, error_mag, "
                "tokens_a, tokens_b, who_erred, source, note) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    o.get("at"), o.get("trial_id"), o.get("profile"),
                    o.get("stage"), o.get("axis"), a, b, lo, hi,
                    1 if o.get("disagree") in (True, 1, "1", "true") else 0,
                    em, _f(o.get("tokens_a")), _f(o.get("tokens_b")),
                    o.get("who_erred") or "", o.get("source") or "local",
                    (o.get("note") or "")[:240],
                ),
            )
        for f in _fold_rows(rows).values():
            con.execute(
                "INSERT INTO pair_fold (pair_lo, pair_hi, axis, n, disagree_n, "
                "freq, mean_err, mag, kind, scored_n, rescue_hi_given_lo, "
                "rescue_lo_given_hi, cofail, xor_err, style_fight, signed, "
                "complement_kind) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    f["model_a"], f["model_b"], f["axis"], f["n"],
                    f["disagree_n"], f["freq"], f["mean_err"], f["mag"],
                    f["kind"], f["scored_n"], f["rescue_hi_given_lo"],
                    f["rescue_lo_given_hi"], f["cofail"], f["xor_err"],
                    f["style_fight"], f["signed"], f["complement_kind"],
                ),
            )
        con.commit()
    finally:
        con.close()


def record_pair(paths, model_a, model_b, *, axis="", disagree=True,
                error_mag=None, profile="forge", stage="", trial_id="",
                tokens_a=None, tokens_b=None, who_erred="", source="local",
                note="") -> dict:
    """Append one pair observation. Does not invent a score."""
    a = _pin(model_a)
    b = _pin(model_b)
    lo, hi = _pair(a, b)
    ax = _axis(axis, profile)
    src = str(source or "local").strip().lower()
    if src not in SRC_OK:
        raise PorosityError("BAD_INPUT", f"unknown source {source!r}")
    who = str(who_erred or "").strip().lower()
    if who not in WHO_OK:
        raise PorosityError("BAD_INPUT", f"unknown who_erred {who_erred!r}")
    em = _f(error_mag)
    if em is not None and (em < 1 or em > 10):
        raise PorosityError("BAD_INPUT", "error_mag must be 1–10 or omitted")
    disc = bool(disagree)
    rec = {
        "schema": SCHEMA,
        "at": _iso(),
        "trial_id": str(trial_id or "")[:120],
        "profile": str(profile or "forge").strip().lower()[:40],
        "stage": str(stage or "").strip().lower()[:40],
        "axis": ax,
        "model_a": a,
        "model_b": b,
        "pair_lo": lo,
        "pair_hi": hi,
        "disagree": disc,
        "error_mag": em,
        "tokens_a": _f(tokens_a),
        "tokens_b": _f(tokens_b),
        "who_erred": who,
        "source": src,
        "note": str(note or "")[:240],
    }
    d = store_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    with obs_path(paths).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    rows = load_obs(paths)
    _rebuild_sqlite(paths, rows)
    snap = snapshot(paths, profile=rec["profile"])
    snap["last"] = rec
    key = (lo, hi, ax)
    snap["fold"] = _fold_rows(rows).get(key)
    return snap


def hook_trial(paths, runs, *, profile="forge", stage="", axis="",
               trial_id="", error_mag=None, source="local") -> dict:
    """Record every distinct named-model pair in one adversarial trial."""
    rows = []
    for r in runs or []:
        if not isinstance(r, dict):
            continue
        m = str(r.get("model") or "").strip()
        if not m or m.lower() in ROTATING:
            continue
        rows.append({
            "model": m,
            "ballot": str(r.get("ballot") or ""),
            "tokens": _f(r.get("tokens") if r.get("tokens") is not None
                         else r.get("n_chars")),
        })
    written = []
    skipped = 0
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if a["model"] == b["model"]:
                skipped += 1
                continue
            disc = a["ballot"] != b["ballot"]
            snap = record_pair(
                paths, a["model"], b["model"],
                axis=axis, disagree=disc, error_mag=error_mag,
                profile=profile, stage=stage, trial_id=trial_id,
                tokens_a=a["tokens"], tokens_b=b["tokens"],
                who_erred="unknown" if disc else "none",
                source=source,
                note="hook_trial",
            )
            written.append(snap.get("last") or {})
    return {
        "schema": SCHEMA,
        "ok": True,
        "n_runs": len(rows),
        "n_written": len(written),
        "n_skipped_same": skipped,
        "kind": "UNMEASURED" if not written else "OK",
        "profile": str(profile or "forge"),
        "stage": str(stage or ""),
        "axis": _axis(axis, profile),
    }


def _rescue_of(f: dict, candidate: str, seated: str):
    """P(candidate right | seated wrong). None if that conditional is UNMEASURED."""
    lo, hi = (f.get("model_a"), f.get("model_b"))
    if candidate == hi and seated == lo:
        return f.get("rescue_hi_given_lo")
    if candidate == lo and seated == hi:
        return f.get("rescue_lo_given_hi")
    return None


def recommend(paths, seated, candidates, *, axes=None, costs=None,
              profile="forge", mode="complement") -> list[dict]:
    """Rank candidates by complement (rescue − co-fail) per token, else |v|.

    mode=complement uses signed C[i,j,a] when who_erred was scored.
    Falls back to unsigned mag. UNMEASURED sorts last. Never zero-fills.
    """
    seated = [str(s).strip() for s in (seated or []) if str(s).strip()]
    candidates = [str(c).strip() for c in (candidates or []) if str(c).strip()]
    costs = costs if isinstance(costs, dict) else {}
    want = [str(a).strip() for a in (axes or axes_for(profile)) if str(a).strip()]
    folds = _fold_rows(load_obs(paths))
    use_c = str(mode or "complement").strip().lower() != "mag"
    ranked = []
    for c in candidates:
        if c.lower() in ROTATING:
            continue
        score = 0.0
        n_term = 0
        unmeasured = True
        used = "none"
        for s in seated:
            if not s or s == c:
                continue
            lo, hi = (c, s) if c.lower() <= s.lower() else (s, c)
            for ax in want:
                f = folds.get((lo, hi, ax))
                if not f:
                    continue
                if use_c and f.get("complement_kind") == "MEASURED":
                    rsc = _rescue_of(f, c, s)
                    cf = f.get("cofail")
                    if rsc is None and cf is None:
                        continue
                    w = f.get("mean_err")
                    if w is None:
                        w = 1.0
                    term = ((0.0 if rsc is None else rsc) - (0.0 if cf is None else cf)) * w
                    unmeasured = False
                    score += term
                    n_term += 1
                    used = "complement"
                    continue
                if f.get("mag") is None:
                    continue
                unmeasured = False
                score += float(f["mag"])
                n_term += 1
                if used == "none":
                    used = "mag"
        cost = _f(costs.get(c))
        if cost is not None and cost > 0 and n_term:
            per = score / cost
        else:
            per = score
        ranked.append({
            "model": c,
            "score": round(per, 6),
            "n_terms": n_term,
            "kind": "UNMEASURED" if unmeasured else "MEASURED",
            "via_tensor": used,
            "cost": cost,
        })
    ranked.sort(key=lambda r: (r["kind"] != "MEASURED", -r["score"], r["model"]))
    return ranked


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_porosity_"))
    root = install(td / "live", tree_id="spike-porosity")
    paths = CosmosPaths(root)

    snap0 = snapshot(paths)
    check("empty store is UNMEASURED and GET does not mkdir",
          lambda: snap0["kind"] == "UNMEASURED" and snap0["n_obs"] == 0
          and snap0["complement_kind"] == "UNMEASURED"
          and snap0["complement"] == {}
          and snap0["schema"] == SCHEMA
          and not store_dir(paths).exists())

    refused = False
    try:
        record_pair(paths, "openrouter/free", "google/gemma-4-26b-a4b-it:free")
    except PorosityError as e:
        refused = e.kind == "REFUSED"
    check("rotator pair REFUSED", lambda: refused)

    same = False
    try:
        record_pair(paths, "google/gemma-4-26b-a4b-it:free",
                    "google/gemma-4-26b-a4b-it:free")
    except PorosityError as e:
        same = e.kind == "REFUSED"
    check("same-model pair REFUSED", lambda: same)

    rec = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, profile="forge", stage="consensus1",
    )
    check("disagree without error_mag leaves mag UNMEASURED; freq measured",
          lambda: rec["fold"]["freq"] == 1.0
          and rec["fold"]["mag"] is None
          and rec["fold"]["kind"] == "UNMEASURED"
          and rec["n_obs"] == 1)

    rec2 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=8,
        profile="forge", stage="consensus1",
    )
    check("mag = disagreement_freq × error_magnitude (1.0 × 8)",
          lambda: rec2["fold"]["mag"] == 8.0
          and rec2["fold"]["orthogonality"] == 8.0
          and rec2["kind"] == "MEASURED")
    check("complement stays UNMEASURED until who_erred is scored",
          lambda: rec2["complement_kind"] == "UNMEASURED"
          and rec2["fold"]["complement_kind"] == "UNMEASURED"
          and rec2["fold"]["signed"] is None)

    rec3 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=8, who_erred="a",
        profile="forge", stage="consensus1",
    )
    # lo=gemma, hi=llama; who=a → lo wrong, hi right → rescue of llama.
    check("who_erred=a folds rescue of hi given lo wrong; xor not cofail",
          lambda: rec3["fold"]["complement_kind"] == "MEASURED"
          and rec3["fold"]["rescue_hi_given_lo"] == 1.0
          and rec3["fold"]["cofail"] == 0.0
          and rec3["fold"]["xor_err"] == 1.0
          and rec3["complement_kind"] == "MEASURED")

    rec4 = record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding", disagree=True, error_mag=9, who_erred="both",
        profile="forge", stage="consensus1",
    )
    check("who_erred=both raises co-failure and cuts signed complement",
          lambda: rec4["fold"]["cofail"] is not None
          and rec4["fold"]["cofail"] > 0
          and rec4["fold"]["signed"] is not None
          and rec4["fold"]["signed"] < rec3["fold"]["signed"])

    check("sqlite projection exists after POST, not after GET-empty",
          lambda: db_path(paths).is_file())

    def _sqlite_holds_c():
        con = sqlite3.connect(str(db_path(paths)))
        try:
            cols = [r[1] for r in con.execute("PRAGMA table_info(pair_fold)")]
            n = list(con.execute("SELECT COUNT(*) FROM pair_fold"))[0][0]
            kinds = [r[0] for r in con.execute(
                "SELECT complement_kind FROM pair_fold")]
            return (
                "signed" in cols and "xor_err" in cols and "cofail" in cols
                and "mag" in cols and n >= 1
                and "MEASURED" in kinds
            )
        finally:
            con.close()

    check("sqlite pair_fold holds T mag and C complement in the same dbase",
          _sqlite_holds_c)

    hook = hook_trial(
        paths,
        [
            {"model": "google/gemma-4-31b-it:free", "ballot": "A"},
            {"model": "qwen/qwen3-32b:free", "ballot": "B"},
            {"model": "openrouter/auto", "ballot": "C"},
        ],
        profile="forge", stage="research", axis="spec", error_mag=5,
    )
    check("hook_trial writes distinct pairs and skips rotator",
          lambda: hook["n_written"] == 1 and hook["n_runs"] == 2)

    ranked = recommend(
        paths,
        seated=["google/gemma-4-26b-a4b-it:free"],
        candidates=[
            "meta-llama/llama-3.3-70b-instruct:free",
            "some/unseen-model",
        ],
        axes=["coding"],
        costs={"meta-llama/llama-3.3-70b-instruct:free": 1.0},
        profile="forge",
    )
    check("recommend ranks measured pair first; unseen stays UNMEASURED",
          lambda: ranked[0]["model"].startswith("meta-llama")
          and ranked[0]["kind"] == "MEASURED"
          and ranked[-1]["kind"] == "UNMEASURED")
    ranked_c = recommend(
        paths,
        seated=["google/gemma-4-26b-a4b-it:free"],
        candidates=["meta-llama/llama-3.3-70b-instruct:free"],
        axes=["coding"],
        costs={"meta-llama/llama-3.3-70b-instruct:free": 1.0},
        profile="forge",
        mode="complement",
    )
    check("recommend complement uses signed rescue−cofail, not unsigned mag alone",
          lambda: ranked_c[0]["via_tensor"] == "complement"
          and ranked_c[0]["kind"] == "MEASURED")

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("porosity selftest", "%d/%d" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_porosity.py --selftest")
    raise SystemExit(2)
