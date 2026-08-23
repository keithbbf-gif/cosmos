#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos - the CLI entry point (F5 builder). Install / boot / status / submit / audit /
backup / rehearse / serve. Refuses unknown flags. This is what a peer runs on a cold
machine after cloning the repo.

    py -3.14 cosmos.py install --root D:\\Ai\\Cosmos --tree-id JMesh-1
    py -3.14 cosmos.py status  --root D:\\Ai\\Cosmos
    py -3.14 cosmos.py submit  --root ... --command "..." --priority high
    py -3.14 cosmos.py audit   --root ...
    py -3.14 cosmos.py backup  --root ... --target E:\\backups
    py -3.14 cosmos.py rehearse --root ... --backup <dest> --scratch <dir>
    py -3.14 cosmos.py serve   --root ... --port 8770
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("install"); p.add_argument("--root", required=True)
    p.add_argument("--tree-id", required=True)
    for name in ("status", "audit"):
        p = sub.add_parser(name); p.add_argument("--root", required=True)
    p = sub.add_parser("submit"); p.add_argument("--root", required=True)
    p.add_argument("--command", required=True); p.add_argument("--priority", default="normal")
    p = sub.add_parser("backup"); p.add_argument("--root", required=True)
    p.add_argument("--src", default=None); p.add_argument("--target", required=True)
    p = sub.add_parser("rehearse"); p.add_argument("--root", required=True)
    p.add_argument("--backup", required=True); p.add_argument("--scratch", required=True)
    p = sub.add_parser("serve"); p.add_argument("--root", required=True)
    p.add_argument("--port", type=int, default=8770)
    p.add_argument("--remote", action="store_true",
                   help="bind 0.0.0.0 for LAN/remote access (beta; bearer-auth; "
                        "HTTPS termination is a cutover item)")

    a = ap.parse_args()

    if a.cmd == "install":
        from cosmos_kernel import install
        root = install(a.root, tree_id=a.tree_id)
        print(f"installed COSMOS root at {root} (tree_id={a.tree_id})")
        return 0

    from cosmos_kernel import Kernel
    # status/audit are READS and boot a read-only kernel (B1: a read is not a write)
    k = Kernel(a.root, worker="cli", read_only=a.cmd in ("status", "audit"))

    if a.cmd == "status":
        last = k.ledger.last()
        print(json.dumps({"ready": k.ready, "root": str(k.paths.root),
                          "tree_id": k.paths.sentinel.tree_id,
                          "ledger_head": {"seq": last["seq"], "event": last["event"]}},
                         indent=1))
        return 0
    if a.cmd == "audit":
        print(json.dumps(k.audit(), indent=1))
        return 0
    if a.cmd == "submit":
        jid = k.sched.submit(a.command, a.priority)
        print(jid)
        return 0
    if a.cmd == "backup":
        from cosmos_backup import Backup
        src = Path(a.src) if a.src else k.paths.role("state")
        r = Backup(k.ledger).run(src, Path(a.target))
        print(f"BACKUP VERIFIED: {r['files']} files -> {r['dest']}")
        return 0
    if a.cmd == "rehearse":
        from cosmos_backup import Backup
        r = Backup(k.ledger).rehearse_restore(Path(a.backup), Path(a.scratch))
        print(f"RESTORE REHEARSAL PASSED: {r['files']} files -> {r['scratch']}")
        return 0
    if a.cmd == "serve":
        from cosmos_service import Service
        host = "0.0.0.0" if a.remote else "127.0.0.1"
        svc = Service(k, host=host, port=a.port)
        print(f"COSMOS API serving on {host}:{svc.port} "
              f"({'REMOTE beta - LAN clients use this machine\'s IP; ' if a.remote else ''}"
              f"bearer token in config/api_token.txt; KDash: open kdash/index.html)")
        try:
            svc.httpd.serve_forever()
        except KeyboardInterrupt:
            svc.shutdown()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
