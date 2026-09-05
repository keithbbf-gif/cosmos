#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_stub_agent.py  --  a fake `claude` for exercising cosmos_cc_driver's outcome paths.

Not a test itself (the name is deliberately not `test_*` so the selftest clock
does not collect it). It is the agent side of the driver's contract: it takes the
same argv shape as `claude -p <task>` and behaves like an agent that finishes,
that finishes-then-hangs, that hangs producing nothing, that refuses, or that
crashes -- selected by STUB_MODE.

This exists because F-59 survived for exactly one reason: the driver's timeout
path had never been executed by a test. Driving the real `claude` costs money and
40 minutes; driving this costs 3 seconds, and it is a REAL subprocess killed by a
REAL wall clock, so `TimeoutExpired.stdout` recovery is measured, not assumed.

STUB_MODE:
  complete              write deliverable, print report line, exit 0
  timeout_with_output   write deliverable, print report line, flush, then hang
  timeout_no_output     hang immediately, print nothing
  refuse                print a typed refusal + refusal report, exit 0
  crash                 print a traceback-ish line, exit 3
STUB_FENCE   directory the deliverable is written into (the job's write-fence)
STUB_HANG    seconds to hang in the timeout modes (default 60)
"""
import os
import sys
import time
from pathlib import Path

REPORT = ('{"status":"%s","files":["%s"],"gate_passed":%d,'
          '"gate_flaky":0,"blocked":[]}')


def main() -> int:
    argv = sys.argv[1:]
    prompt = ""
    if "-p" in argv:
        i = argv.index("-p")
        if i + 1 < len(argv):
            prompt = argv[i + 1]

    # Preflight probe from cosmos_cc_driver.claude_ready().
    if "CC-READY" in prompt:
        print("CC-READY", flush=True)
        return 0
    if argv[:1] == ["--version"]:
        print("0.0.0-stub (COSMOS cc_driver test stub)", flush=True)
        return 0

    mode = os.environ.get("STUB_MODE", "complete")
    fence = Path(os.environ.get("STUB_FENCE", "."))
    hang = float(os.environ.get("STUB_HANG", "60"))

    def deliver(name: str, body: str) -> str:
        fence.mkdir(parents=True, exist_ok=True)
        p = fence / name
        p.write_text(body, encoding="utf-8")
        # Report paths the way a real agent does: relative to the cwd it was
        # launched in, so the driver's claim-verification has to resolve them.
        return os.path.relpath(str(p), os.getcwd()).replace("\\", "/")

    if mode == "timeout_no_output":
        time.sleep(hang)
        return 0

    if mode == "crash":
        print("stub: exploding on purpose", flush=True)
        print("Traceback (most recent call last): StubError", file=sys.stderr, flush=True)
        return 3

    if mode == "refuse":
        print("REFUSE: [FENCE] the order asks for a write outside the declared fence",
              flush=True)
        print(REPORT % ("REFUSED", "", 0), flush=True)
        return 0

    # complete / timeout_with_output both DO the work first.
    name = deliver("stub_deliverable.txt",
                   "the agent really wrote this, at %s\n" % time.time())
    print("stub: measured the thing", flush=True)
    print("stub: wrote %s" % name, flush=True)
    print(REPORT % ("ok", name, 93), flush=True)
    sys.stdout.flush()

    if mode == "timeout_with_output":
        # The exact F-59 shape: the work is DONE and on disk, the report is
        # already emitted, and then the process is still alive when the driver's
        # wall clock fires and kills it.
        time.sleep(hang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
