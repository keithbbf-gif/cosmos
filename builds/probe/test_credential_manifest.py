#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_credential_manifest.py -- pins the ONE property that makes this tool safe:
it names a missing credential without ever handling one.

The manifest's whole job is to be passed around -- committed, mailed, pasted into a
chat window -- so the ask actually reaches Keith. That is only true if a key can never
leak into it. The central test plants a fake secret at a real config path in a THROWAWAY
root, generates the manifest and the doc, and asserts the planted string appears in
neither. That is runtime binding, not a promise: a manifest that echoed a key would
fail here, loudly.

Offline and deterministic: a temp root with its own sentinel, no network, no live tree,
no real key ever opened.

    py -3.14 builds\\probe\\test_credential_manifest.py
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel                 # noqa: E402
from credential_manifest import (                                    # noqa: E402
    ASK_STATES, NEEDS, STATES, CredentialManifestError, Need, build,
    check_need, door_url, guard, main, open_doors, presence, render_md,
    _write,
)

RESULTS = []
PLANTED = "sk-PLANTED-SECRET-DO-NOT-LEAK-9f4c2a"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _root(td: Path) -> Path:
    """A throwaway COSMOS root: sentinel plus the roles this tool resolves."""
    root = td / "live"
    write_sentinel(root, "KMesh-COSMOS-test")
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)
    return root


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except CredentialManifestError as e:
        return e.kind == kind
    return False


def main_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = _root(Path(td))
        cfg = root / "config"

        # -- THE point: a real secret at a real config path never reaches the output --
        (cfg / "openai_api_key.txt").write_text(PLANTED, encoding="utf-8")
        m = build(root, probe_dir=HERE)
        blob = json.dumps(m)
        doc = render_md(m)
        check("a planted secret does NOT appear in the manifest JSON",
              lambda: PLANTED not in blob)
        check("a planted secret does NOT appear in the rendered doc",
              lambda: PLANTED not in doc)
        check("not even the last 4 of a planted secret leak into the manifest",
              lambda: PLANTED[-4:] not in blob)
        row = {r["id"]: r for r in m["needs"]}
        check("a present, non-empty credential measures SATISFIED",
              lambda: row["openai-api-key"]["state"] == "SATISFIED")
        check("a satisfied credential is never in ask_now",
              lambda: "openai-api-key" not in m["ask_now"])

        # -- an EMPTY file is not a credential (cosmos_service.py:419's lesson) -------
        (cfg / "cursor_cosmos_key.txt").write_text("", encoding="utf-8")
        m2 = build(root, probe_dir=HERE)
        row2 = {r["id"]: r for r in m2["needs"]}
        check("an EMPTY credential file is BLOCKED, never SATISFIED",
              lambda: row2["cursor-api-key"]["state"] == "BLOCKED"
              and row2["cursor-api-key"]["present"] is True
              and row2["cursor-api-key"]["nonempty"] is False)
        check("the empty-file case says WHY in the row, not just a state",
              lambda: "EMPTY" in (row2["cursor-api-key"]["note"] or ""))

        # -- presence() reports two booleans and opens nothing ------------------------
        check("presence() returns presence only -- no content, bytes, digest or length",
              lambda: set(presence(cfg / "openai_api_key.txt")) == {"present", "nonempty"})
        # the CODE only -- everything after the closing docstring quote. The docstring
        # names the calls it forbids, so a scan over the whole source would flag its
        # own promise (and __doc__ is dedented, so it is not a substring of the source)
        code = inspect.getsource(presence).split('"""')[-1]
        check("presence()'s code contains no read of the file it measures",
              lambda: not any(t in code for t in ("read_text", "read_bytes", "open(")))
        check("presence() on a missing path is (False, False), not an exception",
              lambda: presence(cfg / "nope.txt") == {"present": False, "nonempty": False})

        # -- the fence: FORBIDDEN_PATH is a refusal, not a warning --------------------
        paths = CosmosPaths(root)
        check("the plaintext R2 key store is refused FORBIDDEN_PATH",
              lambda: _raises_kind(
                  lambda: guard(paths, Path(r"D:\R2Cloner\keys.txt")), "FORBIDDEN_PATH"))
        check("R2Cloner is refused case-insensitively and on either slash",
              lambda: _raises_kind(
                  lambda: guard(paths, Path("d:/r2cloner/Sub/k.json")), "FORBIDDEN_PATH"))
        check("any path outside the config role is refused FORBIDDEN_PATH",
              lambda: _raises_kind(
                  lambda: guard(paths, root / "state" / "k.txt"), "FORBIDDEN_PATH"))
        check("a config-role path passes the fence",
              lambda: guard(paths, paths.config("openai_api_key.txt")).name
              == "openai_api_key.txt")
        check("no manifest row ever records a path outside config/",
              lambda: all(r["place_at"] is None
                          or Path(r["place_at"]).parent == paths.config()
                          for r in m["needs"]))

        # -- a root that is not a COSMOS root is a typed refusal, not a guess ---------
        check("a non-COSMOS root refuses BAD_ROOT (never invents a tree)",
              lambda: _raises_kind(lambda: build(Path(td) / "nothing"), "BAD_ROOT"))

        # -- the doc is GENERATED from the manifest: no second source of truth --------
        asks = [r for r in m["needs"] if r["state"] in ASK_STATES]
        check("every ask carries its exact destination path into the doc",
              lambda: all(r["place_at"] in doc for r in asks))
        check("every ask carries a verify command into the doc",
              lambda: all(r["verify"]["argv"][-1] in doc for r in asks))
        check("every ask names what it unblocks in the doc",
              lambda: all(r["unblocks"][0] in doc for r in asks))
        check("the doc states the no-key-material policy where Keith will see it",
              lambda: "no key material" in doc and "R2Cloner" in doc)

        # -- manifest integrity ------------------------------------------------------
        check("ids are unique",
              lambda: len({n.id for n in NEEDS}) == len(NEEDS))
        check("every declared severity is a known state",
              lambda: all(n.severity in STATES for n in NEEDS))
        check("every measured state is a known state",
              lambda: all(r["state"] in STATES for r in m["needs"]))
        check("the tally accounts for every need, none double-counted",
              lambda: sum(m["tally"].values()) == len(m["needs"]) == len(NEEDS))
        check("ask_now holds exactly the BLOCKED and DEGRADED rows",
              lambda: m["ask_now"] == [r["id"] for r in m["needs"]
                                       if r["state"] in ASK_STATES])
        check("every need names at least one thing it unblocks",
              lambda: all(n.unblocks for n in NEEDS))
        check("every WIRED need names a consumer at file:line -- the binding",
              lambda: all(n.consumers and all(":" in c for c in n.consumers)
                          for n in NEEDS if n.wired))
        check("a need with no consumer wired is PLANNED, never an ask",
              lambda: all(n.severity == "PLANNED" for n in NEEDS if not n.wired))
        check("no NEEDS entry hard-codes a drive literal as its location",
              lambda: all(n.config_name is None or ":" not in n.config_name
                          for n in NEEDS))
        check("evidence is attached or explicitly UNMEASURED -- never silently green",
              lambda: all(r["evidence"]["state"] in ("MEASURED", "STATIC", "UNMEASURED")
                          for r in m["needs"]))
        check("the R2 row records the need without naming a readable source path",
              lambda: row["r2-credentials"]["place_at"].startswith(str(paths.config()))
              and row["r2-credentials"]["state"] == "BLOCKED")
        check("the R2 row is WIRED — the adapter reads the config path (F-49)",
              lambda: row["r2-credentials"]["wired"] is True
              and any("cosmos_backup_r2.py" in c for c in row["r2-credentials"]["consumers"]))
        check("the R2 verify command is the offsite clock preflight, not the stub rehearse",
              lambda: "cosmos_offsite_clock.py" in " ".join(row["r2-credentials"]["verify"]["argv"]))

        # -- F-50 open-window: injected opener, never a real browser, never a key --
        launched = []
        opened = open_doors(["openai-api-key", "r2-credentials"],
                            opener=launched.append)
        check("open_doors launches the public signup URL, not a file path",
              lambda: launched == ["https://platform.openai.com/api-keys"]
              and opened["opened"][0]["url"].startswith("https://"))
        check("a need with no URL is skipped NO_WINDOW, not invented",
              lambda: opened["skipped"] == [{"id": "r2-credentials", "reason": "NO_WINDOW"}])
        check("open_doors never emits the planted secret",
              lambda: PLANTED not in json.dumps(opened) and PLANTED not in "".join(launched))
        check("an unknown need id is UNKNOWN_NEED, not a guessed URL",
              lambda: _raises_kind(lambda: open_doors(["not-a-need"], opener=launched.append),
                                   "UNKNOWN_NEED"))
        blocked = Path(td) / "blocked_file"
        blocked.write_text("x", encoding="utf-8")
        check("a write whose parent is a file is UNWRITABLE, not an untyped OSError",
              lambda: _raises_kind(lambda: _write(blocked / "out.json", "{}"),
                                   "UNWRITABLE"))
        planted = Need(
            id="planted-bad", credential="x", config_name="ok.txt",
            severity="BANANAS", shape="hint", where_to_get="",
            unblocks=(), consumers=(), verify_argv=(), verify_expect="")
        check("a Need with severity outside STATES is BAD_SPEC",
              lambda: _raises_kind(lambda: check_need(planted), "BAD_SPEC"))
        path_need = Need(
            id="planted-path", credential="x",
            config_name=r"config\secret.txt",
            severity="BLOCKED", shape="hint", where_to_get="",
            unblocks=(), consumers=(), verify_argv=(), verify_expect="")
        check("a Need whose config_name is a path is BAD_SPEC, not a resolver walk",
              lambda: _raises_kind(lambda: check_need(path_need), "BAD_SPEC"))
        check("every live Need in NEEDS passes check_need",
              lambda: all(check_need(n) is n for n in NEEDS))
        check("door_url returns None for a minted-locally credential",
              lambda: door_url([n for n in NEEDS if n.id == "install-key"][0]) is None)
        check("door_url returns an https URL for the OpenAI key",
              lambda: (door_url([n for n in NEEDS if n.id == "openai-api-key"][0]) or "")
              .startswith("https://"))

        # -- --write-state lands in the state role, and only there --------------------
        out = Path(td) / "m.json"
        with contextlib.redirect_stdout(io.StringIO()):        # the CLI's own report
            rc = main(["--root", str(root), "--json-out", str(out), "--write-state"])
        state_file = paths.state("CREDENTIALS_NEEDED.json")
        check("--write-state writes the manifest to the runtime root's state role",
              lambda: rc == 0 and state_file.is_file()
              and json.loads(state_file.read_text(encoding="utf-8"))["schema"]
              == "cosmos-credentials-needed/1")
        check("the state manifest carries no planted secret either",
              lambda: PLANTED not in state_file.read_text(encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()):
            strict_rc = main(["--root", str(root), "--json-out", str(out), "--strict"])
        check("--strict exits 3 while anything is still an ask, 0 when none remain",
              lambda: strict_rc == (3 if json.loads(
                  out.read_text(encoding="utf-8"))["ask_now"] else 0))

    ok = all(r[1] for r in RESULTS)
    for label, passed, err in RESULTS:
        print(f"{'PASS' if passed else 'FAIL'}  {label}" + (f"  [{err}]" if err else ""))
    print(json.dumps({"ok": ok, "suite": "credential_manifest",
                      "passed": sum(1 for r in RESULTS if r[1]),
                      "total": len(RESULTS)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main_test())
