#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_makers (the maker map). WHERE agents/tools/connectors/skills can
be made. Refusals BY KIND; seed catalog loaded through the ledger (each add is an
event; state is a projection); unknown kind REFUSES rather than returning empty;
GET is a read (B1); POSITIVE and NEGATIVE controls on the same axes."""
from __future__ import annotations
import json, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_makers import DEFAULT_TOML, MAKER_KINDS, MakerError, MakerMap
from cosmos_kernel import Kernel, install
from cosmos_service import Service

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


SEED_IDS = {
    "cursor-cloud-agent", "claude-agent-tool", "grokbot-team",
    "mcp-registry", "save-skill", "scheduled-task",
}

GOOD_ENTRY = {
    "id": "local-lab-agent",
    "kind": "AGENT",
    "location": "local lab",
    "function": "run a lab agent against a checked-out tree",
    "access": "lab dispatch desk",
    "potential_sources": ["lab roster"],
    "tags": ["lab", "local"],
}


def _toml(dest: Path, body: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    return dest


def _good_toml_row(mid="ok-one", kind="AGENT") -> str:
    return (
        "[[makers]]\n"
        f'id = "{mid}"\n'
        f'kind = "{kind}"\n'
        'location = "test bench"\n'
        'function = "a planted catalog row"\n'
        'access = "test only"\n'
        'potential_sources = ["selftest"]\n'
        'tags = ["planted"]\n'
    )


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_mk_"))
    KEY = b"k"

    # ================= POSITIVE PATH: seed catalog =================
    led = Ledger(td / "makers.jsonl", KEY, "F5")
    mm = MakerMap(led)
    rows = {r["id"]: r for r in mm.list()}
    check("seed makers.toml loads the six known makers",
          lambda: set(rows) == SEED_IDS)
    check("seed file on disk is the same six (catalog and projection agree)",
          lambda: DEFAULT_TOML.is_file() and len(SEED_IDS) == 6)
    check("every seed row carries kind/location/function/access/sources/tags",
          lambda: all(r["kind"] in MAKER_KINDS
                      and r["location"] and r["function"] and r["access"]
                      and isinstance(r["potential_sources"], list)
                      and isinstance(r["tags"], list)
                      for r in rows.values()))
    check("list(kind=AGENT) is Cursor Cloud Agent + GrokBot team",
          lambda: {r["id"] for r in mm.list("AGENT")}
          == {"cursor-cloud-agent", "grokbot-team"})
    check("list(kind=TOOL) is Claude Agent tool + scheduled task",
          lambda: {r["id"] for r in mm.list("TOOL")}
          == {"claude-agent-tool", "scheduled-task"})
    check("list(kind=CONNECTOR) is mcp-registry",
          lambda: [r["location"] for r in mm.list("CONNECTOR")] == ["mcp-registry"])
    check("list(kind=SKILL) is save_skill",
          lambda: [r["location"] for r in mm.list("SKILL")] == ["save_skill"])
    check("find(tag='mcp') hits the connector",
          lambda: [r["id"] for r in mm.find(tag="mcp")] == ["mcp-registry"])
    check("find(text='Cursor Cloud') hits the cloud agent",
          lambda: [r["id"] for r in mm.find(text="Cursor Cloud")]
          == ["cursor-cloud-agent"])
    check("find(kind=SKILL, text='save') is the AND of both filters",
          lambda: [r["id"] for r in mm.find(kind="SKILL", text="save")]
          == ["save-skill"])
    check("each seed add landed as MAKER_ADDED (ledger is the authority)",
          lambda: sum(1 for x in led.verify() if x["event"] == "MAKER_ADDED") == 6)

    # idempotent re-seed: a second map on the same ledger does not re-declare
    mm2 = MakerMap(led)
    check("re-seed is idempotent - still exactly six MAKER_ADDED events",
          lambda: sum(1 for x in led.verify() if x["event"] == "MAKER_ADDED") == 6)
    check("reload with seed=False reconstructs the same projection from the ledger",
          lambda: set(MakerMap(led, seed=False).state()) == SEED_IDS)

    # runtime add
    added = mm.add(GOOD_ENTRY)
    check("add() returns the normalized entry",
          lambda: added["id"] == "local-lab-agent" and added["kind"] == "AGENT")
    check("add() is a MAKER_ADDED event; state is a projection",
          lambda: any(x["event"] == "MAKER_ADDED"
                      and x["payload"]["id"] == "local-lab-agent"
                      for x in led.verify())
          and "local-lab-agent" in MakerMap(led, seed=False).state())

    # ================= NEGATIVE CONTROLS BY KIND =================
    check("unknown kind on add -> UNKNOWN_KIND (the planted refusal)",
          expect(MakerError, "UNKNOWN_KIND")(
              lambda: mm.add({**GOOD_ENTRY, "id": "telepath", "kind": "TELEPATHY"})))
    check("list() of an unknown kind REFUSES - empty would hide the typo",
          expect(MakerError, "UNKNOWN_KIND")(lambda: mm.list("TELEPATHY")))
    check("find(kind=unknown) REFUSES the same way",
          expect(MakerError, "UNKNOWN_KIND")(lambda: mm.find(kind="VIBES")))
    check("duplicate add -> DUPLICATE (a second declaration is a drift)",
          expect(MakerError, "DUPLICATE")(lambda: mm.add(GOOD_ENTRY)))
    check("duplicate of a seed id -> DUPLICATE",
          expect(MakerError, "DUPLICATE")(
              lambda: mm.add({**GOOD_ENTRY, "id": "mcp-registry",
                              "kind": "CONNECTOR"})))
    check("missing required field -> BAD_ENTRY",
          expect(MakerError, "BAD_ENTRY")(
              lambda: mm.add({"id": "x", "kind": "AGENT"})))
    check("empty id -> BAD_ENTRY",
          expect(MakerError, "BAD_ENTRY")(
              lambda: mm.add({**GOOD_ENTRY, "id": "   "})))
    check("tags as a string -> BAD_ENTRY",
          expect(MakerError, "BAD_ENTRY")(
              lambda: mm.add({**GOOD_ENTRY, "id": "bad-tags", "tags": "lab"})))
    check("seed=True with no toml_path -> UNREADABLE",
          expect(MakerError, "UNREADABLE")(
              lambda: MakerMap(Ledger(td / "nopath.jsonl", KEY, "F5"),
                               toml_path=None, seed=True)))

    # planted UNREADABLE / UNKNOWN_KIND catalogs (negative controls that can fail)
    missing = td / "never-written.toml"
    check("load of a missing file -> UNREADABLE",
          expect(MakerError, "UNREADABLE")(
              lambda: MakerMap(Ledger(td / "miss.jsonl", KEY, "F5"),
                               toml_path=missing, seed=True)))
    torn = _toml(td / "torn.toml", "{ torn")
    torn_led = Ledger(td / "torn.jsonl", KEY, "F5")
    check("torn makers.toml -> UNREADABLE",
          expect(MakerError, "UNREADABLE")(
              lambda: MakerMap(torn_led, toml_path=torn, seed=True)))
    check("...and the torn catalog ledgered NOTHING (nothing was measured)",
          lambda: list(torn_led.verify()) == [])

    planted = _toml(td / "planted.toml",
                    _good_toml_row("ok-one", "AGENT")
                    + _good_toml_row("bad-one", "TELEPATHY"))
    plant_led = Ledger(td / "plant.jsonl", KEY, "F5")
    check("catalog with a planted unknown kind -> UNKNOWN_KIND (does not half-apply)",
          expect(MakerError, "UNKNOWN_KIND")(
              lambda: MakerMap(plant_led, toml_path=planted, seed=True)))
    check("...NEGATIVE CONTROL: the good row was not silently added either",
          lambda: "ok-one" not in MakerMap(plant_led, seed=False).state()
          and list(plant_led.verify()) == [])

    # refusals must not have appended a MAKER_ADDED for the refused ids
    check("refused unknown-kind add left no MAKER_ADDED for telepath",
          lambda: not any(x["payload"].get("id") == "telepath"
                          for x in led.verify() if x["event"] == "MAKER_ADDED"))

    # ================= KERNEL COMPOSITION (seed only when not read_only) =================
    root = td / "Cosmos"
    install(root, tree_id="makers")
    k = Kernel(root, worker="core")
    check("writing kernel composes the maker map and seeds the six",
          lambda: set(k.makers.state()) == SEED_IDS)
    seed_events = sum(1 for x in k.ledger.verify() if x["event"] == "MAKER_ADDED")
    check("writing kernel seed is six MAKER_ADDED events",
          lambda: seed_events == 6)
    head_after_write = k.ledger.head_seq()
    kr = Kernel(root, worker="reader", read_only=True)
    check("read-only kernel COMPOSES makers (composition is not a write)",
          lambda: kr.makers is not None)
    check("read-only kernel projects the six without reseeding",
          lambda: set(kr.makers.state()) == SEED_IDS)
    check("read-only kernel appended NOTHING (B1 / REST-2: a reader is not a writer)",
          lambda: kr.ledger.head_seq() == head_after_write
          and sum(1 for x in kr.ledger.verify() if x["event"] == "MAKER_ADDED") == 6)

    # ================= SERVICE (GET is a read; POST writes) =================
    head_before = k.ledger.head_seq()
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def get(path, tok=None):
        req = urllib.request.Request(base + path)
        if tok:
            req.add_header("Authorization", "Bearer " + tok)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def post(path, obj, tok=None):
        req = urllib.request.Request(base + path,
                                     data=json.dumps(obj).encode("utf-8"),
                                     method="POST")
        if tok:
            req.add_header("Authorization", "Bearer " + tok)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    code, body = get("/api/v1/makers")
    check("GET /makers without a token -> 401",
          lambda: code == 401 and body.get("error") == "UNAUTHORIZED")
    code, body = get("/api/v1/makers", svc.token)
    check("GET /makers serves the six known makers over the wire",
          lambda: code == 200 and {m["id"] for m in body["makers"]} == SEED_IDS)
    check("GET /makers carries served_at + measured_at (panel age exists)",
          lambda: body.get("served_at") and body.get("measured_at"))
    check("GET /makers is a read - ledger head did not move",
          lambda: k.ledger.head_seq() == head_before)

    code, body = get("/api/v1/makers?kind=AGENT", svc.token)
    check("GET /makers?kind=AGENT filters to the two agent makers",
          lambda: code == 200 and {m["id"] for m in body["makers"]}
          == {"cursor-cloud-agent", "grokbot-team"})
    code, body = get("/api/v1/makers?tag=mcp", svc.token)
    check("GET /makers?tag=mcp finds mcp-registry",
          lambda: code == 200 and [m["id"] for m in body["makers"]] == ["mcp-registry"])
    code, body = get("/api/v1/makers?text=GrokBot", svc.token)
    check("GET /makers?text=GrokBot finds the team bot",
          lambda: code == 200 and [m["id"] for m in body["makers"]] == ["grokbot-team"])

    code, body = get("/api/v1/makers?kind=TELEPATHY", svc.token)
    check("GET /makers?kind=TELEPATHY -> 400 UNKNOWN_KIND",
          lambda: code == 400 and body.get("error") == "UNKNOWN_KIND")

    held = k.makers
    k.makers = None
    code, body = get("/api/v1/makers", svc.token)
    k.makers = held
    check("GET /makers on an uncomposed kernel -> 503 (not an empty catalog)",
          lambda: code == 503 and body.get("error") == "MAKERS_NOT_COMPOSED")
    check("...and the 503 did not write (head still unmoved)",
          lambda: k.ledger.head_seq() == head_before)

    code, body = post("/api/v1/makers", GOOD_ENTRY)
    check("POST /makers without a token -> 401",
          lambda: code == 401 and body.get("error") == "UNAUTHORIZED")
    code, body = post("/api/v1/makers", GOOD_ENTRY, svc.token)
    check("POST /makers adds the entry (201) and returns it",
          lambda: code == 201 and body["maker"]["id"] == "local-lab-agent")
    code, body = get("/api/v1/makers", svc.token)
    check("GET after POST sees the new maker in the projection",
          lambda: code == 200 and "local-lab-agent" in {m["id"] for m in body["makers"]})
    wcode, wbody = post("/api/v1/makers",
                        {**GOOD_ENTRY, "id": "wire-telepath", "kind": "TELEPATHY"},
                        svc.token)
    check("POST TELEPATHY -> 400 UNKNOWN_KIND and nothing named wire-telepath",
          lambda: wcode == 400 and wbody.get("error") == "UNKNOWN_KIND"
          and "wire-telepath" not in k.makers.state())
    dcode, dbody = post("/api/v1/makers",
                        {**GOOD_ENTRY, "id": "mcp-registry", "kind": "CONNECTOR"},
                        svc.token)
    check("POST duplicate seed id -> 400 DUPLICATE",
          lambda: dcode == 400 and dbody.get("error") == "DUPLICATE")

    svc.shutdown()

    # GET against a READ-ONLY kernel must still not write (B1 over the wire)
    ro_head = kr.ledger.head_seq()
    ro_svc = Service(kr, host="127.0.0.1", port=0)
    ro_svc.serve_background()
    ro_base = f"http://127.0.0.1:{ro_svc.port}"
    req = urllib.request.Request(ro_base + "/api/v1/makers")
    req.add_header("Authorization", "Bearer " + ro_svc.token)
    with urllib.request.urlopen(req, timeout=10) as resp:
        ro_body = json.loads(resp.read().decode("utf-8"))
    check("GET /makers on a read-only kernel projects seed plus the POST add",
          lambda: {m["id"] for m in ro_body["makers"]}
          == SEED_IDS | {"local-lab-agent"})
    check("GET /makers on a read-only kernel does not move the ledger head",
          lambda: kr.ledger.head_seq() == ro_head)
    ro_svc.shutdown()

    # second writing kernel on the same root: last event is this boot, seed does not re-declare
    k2 = Kernel(root, worker="core-b")
    check("restarted kernel last event is BOOT_VERIFIED (seed does not rewrite)",
          lambda: k2.ledger.last()["event"] == "BOOT_VERIFIED")
    check("restarted kernel still projects the seed plus the POST add",
          lambda: SEED_IDS.issubset(k2.makers.state())
          and "local-lab-agent" in k2.makers.state())

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (maker map: seed is a ledger projection; "
          "unknown kind REFUSES; GET is a read)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_makers():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())