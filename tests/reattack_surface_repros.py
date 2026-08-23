#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REATTACK surface-cluster repros. Each finding is a MEASURED run, not a reading.

A finding REPRODUCED means the defect is still open on main after the stage-7 merge.
A finding CLOSED means this reattack could not reproduce it (prior fix held).

Run:
    PYTHONPATH=cosmos python3 tests/reattack_surface_repros.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_ingress import IngressGate, write_envelope
from cosmos_ledger import Ledger
from cosmos_mail import Mailbox
from cosmos_runner import Runner
from cosmos_sched import Scheduler
from cosmos_surfaces import Surfaces

RESULTS = []


def finding(fid, title, fn):
    try:
        reproduced, detail = fn()
        RESULTS.append((fid, title, bool(reproduced), str(detail), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((fid, title, False, "", f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_reattack_surf_"))
    KEY = b"reattack-surface-key"
    print(f"workdir {td}")

    # =====================================================================
    # S-R1  KNOWN residual: ingress envelope_id traversal
    # Stage-7 closed role()/backup-manifest traversal (K2/K3). Ingress still
    # joins envelope_id onto the payload path with no confinement.
    # =====================================================================
    def r1():
        led = Ledger(td / "ing_r1.jsonl", KEY, "core")
        ingress = td / "ingress_r1"
        ingress.mkdir()
        secret_dir = td / "outside_r1"
        secret_dir.mkdir()
        secret = secret_dir / "leaked.payload"
        blob = b"TRAVERSAL-SECRET-BYTES"
        secret.write_bytes(blob)
        eid = "../outside_r1/leaked"
        env = {
            "envelope_id": eid,
            "sender": "sandbox",
            "kind": "job",
            "payload_len": len(blob),
            "payload_sha": hashlib.sha256(blob).hexdigest(),
        }
        (ingress / "attack.envelope.json").write_text(json.dumps(env), encoding="utf-8")
        gate = IngressGate(led, ingress)
        out = gate.accept_all()
        accepted = out["accepted"]
        if not accepted:
            return False, f"refused={out['refused']}"
        body = accepted[0]
        escaped = Path(str(ingress / (eid + ".payload"))).resolve()
        under = escaped.is_relative_to(ingress.resolve())
        return (body["payload"] == blob and not under,
                f"accepted_payload={body['payload']!r} resolved={escaped} "
                f"under_ingress={under} accepted={len(accepted)} refused={out['refused']}")

    finding("S-R1", "KNOWN residual: ingress envelope_id `../` reads a payload "
            "OUTSIDE the ingress dir and ACCEPTs it", r1)

    def r1b():
        led = Ledger(td / "ing_r1b.jsonl", KEY, "core")
        ingress = td / "ingress_r1b"
        ingress.mkdir()
        abs_payload = td / "abs_secret.payload"
        blob = b"ABS-PATH-SECRET"
        abs_payload.write_bytes(blob)
        eid = str(td / "abs_secret")          # absolute; Path join replaces
        env = {
            "envelope_id": eid,
            "sender": "sandbox",
            "kind": "return",
            "payload_len": len(blob),
            "payload_sha": hashlib.sha256(blob).hexdigest(),
        }
        (ingress / "abs.envelope.json").write_text(json.dumps(env), encoding="utf-8")
        gate = IngressGate(led, ingress)
        out = gate.accept_all()
        if not out["accepted"]:
            return False, f"refused={out['refused']}"
        payload_path = ingress / (eid + ".payload")
        return (out["accepted"][0]["payload"] == blob and payload_path.is_absolute()
                and not str(payload_path).startswith(str(ingress)),
                f"payload_path={payload_path} accepted={out['accepted'][0]['payload']!r}")

    finding("S-R1b", "KNOWN residual sibling: absolute envelope_id replaces the "
            "ingress root (pathlib absolute-join)", r1b)

    def r1c():
        led = Ledger(td / "ing_r1c.jsonl", KEY, "core")
        ingress = td / "ingress_r1c"
        ingress.mkdir()
        target = td / "symlink_secret.txt"
        blob = b"SYMLINK-READ-SECRET"
        target.write_bytes(blob)
        eid = "honest"
        (ingress / (eid + ".payload")).symlink_to(target)
        env = {
            "envelope_id": eid,
            "sender": "sandbox",
            "kind": "message",
            "payload_len": len(blob),
            "payload_sha": hashlib.sha256(blob).hexdigest(),
        }
        (ingress / "sym.envelope.json").write_text(json.dumps(env), encoding="utf-8")
        out = IngressGate(led, ingress).accept_all()
        if not out["accepted"]:
            return False, f"refused={out['refused']}"
        return (out["accepted"][0]["payload"] == blob,
                f"accepted bytes from symlink -> {target}: {out['accepted'][0]['payload']!r}")

    finding("S-R1c", "NEW: ingress follows a payload symlink and ACCEPTs foreign "
            "file bytes (arbitrary readable-file exfil)", r1c)

    # =====================================================================
    # S-R2  KNOWN residual: argv: runner confinement bypass
    # K4 confines py:<path> to tools_root. argv: json.loads the rest and execs
    # that list with no confinement and no argv-only policy.
    # =====================================================================
    def r2():
        work = td / "work_r2"
        tools = work / "cosmos"
        tools.mkdir(parents=True)
        s = Scheduler(td / "q_r2", KEY, "F5")
        runner = Runner(s, work, "F5")
        runner.tools_root = tools
        # negative control: K4 still holds for py:
        outside = td / "evil_r2.py"
        outside.write_text("open(%r,'w').write('py-ran')\n" % str(td / "py_ran.txt"),
                           encoding="utf-8")
        s.submit(f"py:{outside}", "normal")
        k4 = runner.run_one()
        k4_held = k4["outcome"] == "BROKE" and k4.get("traversal_refused") and \
            not (td / "py_ran.txt").exists()
        # the residual: argv: runs an interpreter/binary with no tools_root check
        marker = td / "argv_pwned.txt"
        cmd = "argv:" + json.dumps([sys.executable, "-c",
                                    "open(%r,'w').write('ARGV-BYPASS')" % str(marker)])
        s.submit(cmd, "normal")
        r = runner.run_one()
        ran = marker.exists() and marker.read_text(encoding="utf-8") == "ARGV-BYPASS"
        return (k4_held and ran and r["outcome"] == "CLEAN",
                f"K4_held={k4_held} argv_ran={ran} argv_outcome={r} "
                f"marker={marker.exists()}")

    finding("S-R2", "KNOWN residual: argv: bypasses K4 tools_root confinement and "
            "executes an arbitrary argv list (RCE)", r2)

    def r2b():
        """Product surfaces accept the argv: form with no policy."""
        from cosmos_kernel import Kernel, install
        from cosmos_command import Commander
        from cosmos_mcp import MCPServer
        from cosmos_service import Service
        import urllib.request
        root = td / "kr2"
        install(root, tree_id="r2")
        k = Kernel(root, worker="core")
        cmd = "argv:" + json.dumps([sys.executable, "-c", "print(1)"])
        # command seam
        c = Commander(k).handle("submit normal " + cmd)
        # MCP
        mcp = MCPServer(k)
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": "cosmos_submit",
                                      "arguments": {"command": cmd}}})
        mcp_out = json.loads(mcp.handle(line))
        # HTTP API
        svc = Service(k, host="127.0.0.1", port=0)
        svc.serve_background()
        req = urllib.request.Request(
            f"http://127.0.0.1:{svc.port}/api/v1/jobs",
            data=json.dumps({"command": cmd, "priority": "low"}).encode("utf-8"),
            headers={"Authorization": "Bearer " + svc.token,
                     "Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            http = json.loads(resp.read().decode("utf-8"))
        svc.shutdown()
        st = k.sched._state()
        argv_jobs = [j for j, v in st.items() if v["m"]["command"].startswith("argv:")]
        mcp_text = mcp_out.get("result", {}).get("content", [{}])[0].get("text", "")
        mcp_job = json.loads(mcp_text).get("job_id") if mcp_text else None
        return (c.get("ok") is True and bool(mcp_job) and bool(http.get("job_id"))
                and len(argv_jobs) >= 3,
                f"command_job={c.get('job_id')} mcp_job={mcp_job} "
                f"http_job={http.get('job_id')} argv_jobs={len(argv_jobs)}")

    finding("S-R2b", "KNOWN residual delivery: command/MCP/HTTP surfaces accept "
            "argv: with no confinement policy", r2b)

    def r2c():
        """Popen FileNotFoundError leaks; job stays RUNNING (never done)."""
        s = Scheduler(td / "q_r2c", KEY, "F5")
        runner = Runner(s, td / "work_r2c", "F5")
        jid = s.submit('argv:["/no/such/cosmos-bin-r2c"]', "normal")
        leaked = None
        try:
            runner.run_one()
            leaked = False
        except FileNotFoundError as e:
            leaked = True
            err = str(e)
        st = s._state()[jid]["st"]
        return (leaked is True and st == "RUNNING",
                f"leaked_FileNotFoundError={leaked} job_state={st} err={err!r}")

    finding("S-R2c", "NEW: runner launch failure raises FileNotFoundError and "
            "leaves the job RUNNING (no worded outcome, no done())", r2c)

    # =====================================================================
    # S-R3  KNOWN residual: worker-id spoofing (touches ingress + mail surfaces)
    # =====================================================================
    def r3():
        led = Ledger(td / "ing_r3.jsonl", KEY, "core")
        ingress = td / "ingress_r3"
        write_envelope(ingress, "core", "job", b'{"command":"i am core"}')
        out = IngressGate(led, ingress).accept_all()
        accepted = out["accepted"]
        evs = [e for e in led.verify() if e["event"] == "INGRESS_ACCEPTED"]
        return (accepted and accepted[0]["sender"] == "core"
                and evs and evs[0]["payload"]["sender"] == "core",
                f"claimed_sender={accepted[0]['sender'] if accepted else None} "
                f"ledgered_sender={evs[0]['payload']['sender'] if evs else None} "
                f"(no identity check)")

    finding("S-R3", "KNOWN residual: ingress sender is an unauthenticated claim; "
            "sender='core' is ACCEPTED and ledgered as identity", r3)

    def r3b():
        mail_root = td / "mail_r3b"
        escape = Mailbox(mail_root, "../escaped_worker")
        escape.register()
        escaped_inbox = (td / "escaped_worker" / "inbox")
        # also: send() to a traversing recipient writes outside the mail root
        victim = Mailbox(mail_root, "honest")
        victim.register()
        attacker = Mailbox(mail_root, "attacker")
        attacker.register()
        mid = attacker.send("../escaped_worker", "hi", "path-injection")
        landed = list((td / "escaped_worker" / "inbox").glob("*.json"))
        return (escaped_inbox.is_dir()
                and not escaped_inbox.resolve().is_relative_to(mail_root.resolve())
                and len(landed) == 1,
                f"register_inbox={escaped_inbox} resolve={escaped_inbox.resolve()} "
                f"under_mail={escaped_inbox.resolve().is_relative_to(mail_root.resolve())} "
                f"send_landed={landed} mid={mid}")

    finding("S-R3b", "KNOWN residual: mailbox worker-id is a path component; "
            "`../escaped_worker` register()+send() escape the mail root", r3b)

    def r3c():
        """K5 compares worker STRINGS. Anyone who constructs Scheduler(worker='A')
        is A. The claimant guard is a name check, not a credential."""
        sA = Scheduler(td / "q_r3c", KEY, "A")
        jid = sA.submit("work", "normal")
        sA.claim_next()
        spoof = Scheduler(td / "q_r3c", KEY, "A")     # same name, no proof
        spoof.done(jid, "CLEAN", "spoofed completion")
        st = sA._state()[jid]
        return (st["st"] == "CLEAN" and st["by"] == "A",
                f"state={st['st']} by={st['by']} (spoof Scheduler(worker='A') completed "
                f"A's job; K5 held against worker='B' but identity is a string)")

    finding("S-R3c", "KNOWN residual: worker-id is a constructor string; a spoofed "
            "Scheduler(worker='A') defeats the K5 claimant guard", r3c)

    # =====================================================================
    # S-N1  NEW: qualify_backup_target never checks ROLE
    # Module docstring: "a PUBLISH kind in a BACKUP role is exactly the
    # 'publishing is not backup' trap" — and claims the two are checked
    # against each other at qualification. They are not. A CLOUD+PUBLISH
    # surface QUALIFIES.
    # =====================================================================
    def n1():
        fake = [1000.0]
        led = Ledger(td / "surf_n1.jsonl", KEY, "F5", clock=lambda: fake[0])
        sf = Surfaces(led, clock=lambda: fake[0])
        sf.register("r2-publish", "CLOUD", "r2://bucket/public", "PUBLISH")
        sf.attach_probe("r2-publish", lambda: (True, 900_000_000_000, "publish bucket"))
        sf.measure("r2-publish")
        q = sf.qualify_backup_target("r2-publish", min_free_bytes=50_000_000_000)
        return (q["qualified"] is True and q["reasons"] == [],
                f"CLOUD+PUBLISH qualified={q['qualified']} reasons={q['reasons']}")

    finding("S-N1", "NEW: qualify_backup_target ignores role; a CLOUD PUBLISH "
            "surface QUALIFIES as a backup target (publishing-is-not-backup still open)", n1)

    # =====================================================================
    # S-N2  NEW: mesh-addressability is answered from the KIND CLAIM, not
    # a measurement. Register a local directory as LAN; it QUALIFIES.
    # The G: / SABRENT-USB-labelled-NAS scar.
    # =====================================================================
    def n2():
        fake = [1000.0]
        led = Ledger(td / "surf_n2.jsonl", KEY, "F5", clock=lambda: fake[0])
        sf = Surfaces(led, clock=lambda: fake[0])
        local_path = str(td / "this-machine-usb")
        sf.register("labelled-nas", "LAN", local_path, "BACKUP")
        sf.attach_probe("labelled-nas",
                        lambda: (True, 9_000_000_000_000, "labelled NAS, actually USB"))
        sf.measure("labelled-nas")
        q = sf.qualify_backup_target("labelled-nas", min_free_bytes=1_000_000_000)
        return (q["qualified"] is True,
                f"kind=LAN path={local_path!r} (on this box) qualified={q['qualified']} "
                f"reasons={q['reasons']}")

    finding("S-N2", "NEW: off-machine is a registration sticker; a LOCAL directory "
            "registered as LAN QUALIFIES (G:/SABRENT scar still open)", n2)

    # =====================================================================
    # S-N3  NEW: report() holds last SURFACE_QUALIFIED verdict. After the
    # measurement goes stale, age_s is live but qualified stays True until
    # someone re-asks. Frozen-dashboard / green-log-over-nothing.
    # =====================================================================
    def n3():
        fake = [1000.0]
        led = Ledger(td / "surf_n3.jsonl", KEY, "F5", clock=lambda: fake[0])
        sf = Surfaces(led, clock=lambda: fake[0])
        sf.register("odx", "CLOUD", "onedrive://x", "BACKUP")
        sf.attach_probe("odx", lambda: (True, 900_000_000_000, "odx"))
        sf.measure("odx")
        q0 = sf.qualify_backup_target("odx", min_free_bytes=50_000_000_000)
        fake[0] += 90_000                         # past 24h window; do NOT re-qualify
        live = sf.qualify_backup_target("odx", min_free_bytes=50_000_000_000)
        # rewind the last qualify so report sees only the first verdict:
        # actually the call above appended a False. Demonstrate the hole
        # with a FRESH pair: qualify once, age past window, report without
        # a second qualify.
        fake2 = [1000.0]
        led2 = Ledger(td / "surf_n3b.jsonl", KEY, "F5", clock=lambda: fake2[0])
        sf2 = Surfaces(led2, clock=lambda: fake2[0])
        sf2.register("odx2", "CLOUD", "onedrive://y", "BACKUP")
        sf2.attach_probe("odx2", lambda: (True, 900_000_000_000, "odx"))
        sf2.measure("odx2")
        q_ok = sf2.qualify_backup_target("odx2", min_free_bytes=50_000_000_000)
        fake2[0] += 90_000
        # a re-run NOW would fail (same as test_surfaces stale check)
        would = sf2.qualify_backup_target("odx2", min_free_bytes=50_000_000_000)
        # but report() AFTER only the first qualify + aging, before a second
        # ask, is the defect. Recreate that:
        fake3 = [1000.0]
        led3 = Ledger(td / "surf_n3c.jsonl", KEY, "F5", clock=lambda: fake3[0])
        sf3 = Surfaces(led3, clock=lambda: fake3[0])
        sf3.register("odx3", "CLOUD", "onedrive://z", "BACKUP")
        sf3.attach_probe("odx3", lambda: (True, 900_000_000_000, "odx"))
        sf3.measure("odx3")
        q3 = sf3.qualify_backup_target("odx3", min_free_bytes=50_000_000_000)
        fake3[0] += 90_000
        rep = {r["id"]: r for r in sf3.report()}["odx3"]
        # live re-decide without appending? qualify always appends; the point
        # is report() did not re-decide. Contrasted with what qualify would say
        # if asked (we already measured that as `would` above).
        return (q3["qualified"] is True and rep["qualified"] is True
                and rep["age_s"] == 90_000 and would["qualified"] is False,
                f"first_qualify={q3['qualified']} report_after_stale qualified="
                f"{rep['qualified']} age_s={rep['age_s']} "
                f"re_ask_qualify={would['qualified']} "
                f"(report stayed green; a re-ask is red)")

    finding("S-N3", "NEW: report() keeps the last qualified=True after the "
            "measurement is stale (age live, verdict frozen)", n3)

    # ----- print -----
    print()
    n_repro = 0
    for fid, title, reproduced, detail, err in RESULTS:
        tag = "REPRODUCED" if reproduced else ("ERROR   " if err else "CLOSED  ")
        if reproduced:
            n_repro += 1
        print(f"  {tag}  {fid}  {title}")
        if detail:
            print(f"           {detail}")
        if err:
            print(f"           [{err}]")
    print()
    print(f"REATTACK surface: {n_repro}/{len(RESULTS)} findings REPRODUCED "
          f"on main@stage-7")
    # critic script: success means we measured defects (or honestly closed them).
    # fail only on unexpected exceptions with no classification.
    errors = [r for r in RESULTS if r[4]]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
