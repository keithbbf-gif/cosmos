#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rail_base.py -- the shared rail seam.

PHASE 3.1, docs/CORE_RESTRUCTURE.md.

Before this module, `_ledger_is_authority` existed as a BYTE-IDENTICAL copy in
four rails (codex, cursor, firecrawl, playwright -- md5 57319397...), while
`cosmos_claude_rail` imported it from `cosmos_codex_rail`. So a vendor rail had
become the utility library for four other modules: `cosmos_claude_rail`,
`cosmos_dispatch`, `cosmos_rails_prober` and `cosmos_work_order_run` all import
from `cosmos_codex_rail`.

Two costs, both real:

  * Coupling by accident. The claude rail breaks if the codex rail is refactored,
    for reasons that have nothing to do with either vendor.
  * Drift with no gate. Four copies of one guard is four places for one of them
    to quietly diverge -- and this codebase has already paid for prose and code
    disagreeing about rail registration (see docs/contracts/rails.toml).

The move is deliberately ADDITIVE: `cosmos_codex_rail` re-exports these names, so
every existing importer keeps working unchanged. Rails migrate to importing from
here one at a time, each migration gated.

SECOND PASS (2026-08-31) -- `_real_which`, `_real_run` and `write_probe_record`.
These three were the reason `cosmos_claude_rail`, `cosmos_rails_prober` and the
work-order runner imported a VENDOR rail as their utility library. The blocker
recorded in docs/CHANGELOG_2026-08-30_CC_AUDIT.md was that `_real_run` raised
`CodexRailError`, so a generic process helper carried a vendor-specific type.
Resolved by inverting the hierarchy instead of duplicating the helper:
`RailError` is defined HERE and `CodexRailError` subclasses it, so the helper
raises the generic type while every existing `except CodexRailError` still
catches every refusal the codex rail itself raises. Pinned by
tests/test_rail_base.py, not by prose.

NAME NOTE: `cosmos_rails.RailError` is a DIFFERENT, older class (kinds
NO_LIVE_LINK / RAIL_FAILED / NOT_PERMITTED) belonging to the Dispatcher. It is
deliberately left alone -- unifying the two is PHASE 5 (one refusal taxonomy),
and doing it here would change what `except RailError` catches inside the live
dispatch path while the fleet is running. Modules that need both import one
under an alias.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

# Windows: never flash a console when a rail shells out.
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# Redacted out of every probe/gate record before it is written. The UNION of
# what the individual rails each popped, because a record is written to
# live/config/ and a rail that forgot one of these names was one copy-paste
# away. Fail-closed: an extra pop costs nothing, a missed one leaks a key.
SECRET_FIELDS = (
    "api_key", "key",
    "openai_api_key", "OPENAI_API_KEY", "CODEX_API_KEY",
    "anthropic_api_key", "ANTHROPIC_API_KEY",
    "cursor_api_key", "CURSOR_API_KEY",
    "firecrawl_api_key", "FIRECRAWL_API_KEY",
    "groq_api_key", "GROQ_API_KEY",
    "github_agent_token", "GITHUB_TOKEN", "GH_TOKEN",
    "COPILOT_GITHUB_TOKEN",
)


class RailError(RuntimeError):
    """The rail-seam typed refusal. `kind` is machine-readable; branch on it.

    kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, REFUSED}.

    Vendor rails subclass this and keep their own name, so a caller may catch
    the narrow type (`except CodexRailError`) or the seam-wide one
    (`except RailError`) and the shared helpers below can raise without
    importing any vendor module.
    """

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def ledger_is_authority(kernel) -> bool:
    """True when this kernel's ledger IS the authority ledger.

    The guard behind "attach_to_kernel refuses authority LINK_REGISTERED unless
    boot_compose=True". An isolated --gate run writes its own ledger and may
    attach freely; the live tree may not.

    Fail-closed by shape: anything it cannot positively identify as the authority
    ledger returns False, because claiming authority you do not have is the worse
    error. Contract: docs/contracts/rails.toml -> rails.attach_refuses_authority_
    without_boot_compose.
    """
    paths = getattr(kernel, "paths", None)
    led = getattr(kernel, "ledger", None)
    if paths is None or led is None:
        return False
    try:
        auth = Path(paths.ledger("authority.jsonl")).resolve()
    except Exception:                                                # noqa: BLE001
        return False
    led_path = getattr(led, "_path", None)
    if led_path is None:
        return False
    try:
        return Path(led_path).resolve() == auth
    except OSError:
        return Path(led_path) == Path(auth)


# Historical name. The leading underscore said "private to this rail" back when
# every rail owned a copy; it is shared API now. Kept so the four rails that
# already call `_ledger_is_authority` migrate without a rename in the same step.
_ledger_is_authority = ledger_is_authority


def _real_which(name: str):
    """PATH lookup. Injectable in rails so --gate never needs the real binary."""
    return shutil.which(name)


def _real_run(argv, cwd=None, timeout_s=60, env=None, stdin=None) -> dict:
    """The one process helper. argv list only. Never a shell string.

    Returns a record, never raises for a failed child: {rc, out, err,
    timed_out, elapsed_s}. rc is RECORDED, never the predicate -- a rail binds
    "done" to an artifact the run emitted. The single raise is a programmer
    error (a string argv implies a shell), and it is a typed RailError so the
    helper carries no vendor type.
    """
    if isinstance(argv, str):
        raise RailError(
            "BROKE", "run() takes an argv LIST - a string implies a shell")
    t0 = time.time()
    kw = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": float(timeout_s),
        "cwd": str(cwd) if cwd is not None else None,
        "env": env,
        "shell": False,
        "creationflags": CREATE_NO_WINDOW,
    }
    if stdin is not None:
        kw["input"] = stdin
    try:
        p = subprocess.run(argv, **kw)
        return {
            "rc": p.returncode,
            "out": p.stdout or "",
            "err": p.stderr or "",
            "timed_out": False,
            "elapsed_s": round(time.time() - t0, 1),
        }
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else ""
        err = e.stderr if isinstance(e.stderr, str) else ""
        return {
            "rc": None,
            "out": out or "",
            "err": err or "",
            "timed_out": True,
            "elapsed_s": round(time.time() - t0, 1),
        }
    except FileNotFoundError as e:
        return {
            "rc": -1,
            "out": "",
            "err": f"FileNotFoundError: {e}",
            "timed_out": False,
            "elapsed_s": round(time.time() - t0, 1),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "rc": -1,
            "out": "",
            "err": f"{type(e).__name__}: {e}",
            "timed_out": False,
            "elapsed_s": round(time.time() - t0, 1),
        }


def write_probe_record(path: Path, rec: dict) -> dict:
    """Write a probe/gate/launch record, secrets stripped, and return what was
    written. Atomic enough for a config-role artifact: one write, sorted keys,
    default=str so a Path or datetime never turns a gate into a crash.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = dict(rec)
    for k in SECRET_FIELDS:
        out.pop(k, None)
    path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return out


def selftest() -> int:
    """Bind the claim to an emitted value."""
    import json
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:                                        # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="rail_base_"))
    auth = td / "ledger" / "authority.jsonl"
    auth.parent.mkdir(parents=True)
    auth.write_text("", encoding="utf-8")

    class _Paths:
        def ledger(self, name):
            return td / "ledger" / name

    class _Led:
        def __init__(self, p):
            self._path = p

    class _K:
        def __init__(self, led):
            self.paths = _Paths()
            self.ledger = led

    check("authority ledger is recognised",
          lambda: ledger_is_authority(_K(_Led(auth))) is True)
    check("an isolated ledger is NOT authority",
          lambda: ledger_is_authority(_K(_Led(td / "ledger" / "n.jsonl"))) is False)
    check("a kernel with no ledger is not authority (fail-closed)",
          lambda: ledger_is_authority(_K(None)) is False)
    check("a ledger with no _path is not authority (fail-closed)",
          lambda: ledger_is_authority(_K(object())) is False)
    check("underscore alias is the same function",
          lambda: _ledger_is_authority is ledger_is_authority)
    check("CREATE_NO_WINDOW is 0 off Windows, flag on",
          lambda: CREATE_NO_WINDOW in (0, 0x08000000))

    # RailError -- the typed refusal the shared helpers raise.
    def _raises(fn, kind):
        try:
            fn()
        except RailError as e:
            return e.kind == kind and e.detail and f"[{kind}]" in str(e)
        return False

    check("RailError carries a machine-readable kind and detail",
          lambda: _raises(
              lambda: (_ for _ in ()).throw(RailError("REFUSED", "why")),
              "REFUSED"))
    check("a string argv is a typed BROKE refusal, never a shell",
          lambda: _raises(lambda: _real_run("echo hi"), "BROKE"))

    # _real_run -- bound to a value only a real child process can produce.
    import sys as _sys
    token = f"rail-base-{os.getpid()}"
    r_ok = _real_run([_sys.executable, "-c", f"print({token!r})"], timeout_s=60)
    check("_real_run records rc + real child stdout",
          lambda: r_ok["rc"] == 0 and token in r_ok["out"]
          and r_ok["timed_out"] is False)
    r_rc = _real_run([_sys.executable, "-c", "raise SystemExit(7)"], timeout_s=60)
    check("_real_run RECORDS a non-zero rc, it does not raise on it",
          lambda: r_rc["rc"] == 7 and r_rc["timed_out"] is False)
    r_in = _real_run(
        [_sys.executable, "-c", "import sys;sys.stdout.write(sys.stdin.read())"],
        timeout_s=60, stdin="on-stdin")
    check("_real_run pipes stdin to the child",
          lambda: "on-stdin" in r_in["out"])
    r_to = _real_run([_sys.executable, "-c", "import time;time.sleep(5)"],
                     timeout_s=0.5)
    check("_real_run reports a TIMEOUT as a record, rc=None",
          lambda: r_to["timed_out"] is True and r_to["rc"] is None)
    r_missing = _real_run(["cosmos-no-such-binary-xyz"], timeout_s=5)
    check("a missing binary is a record, not a crash",
          lambda: r_missing["rc"] == -1 and r_missing["timed_out"] is False)

    # _real_which -- resolves a binary that certainly exists on this host.
    check("_real_which finds the running interpreter's directory entry",
          lambda: bool(_real_which(Path(_sys.executable).name)))
    check("_real_which returns None for an absent binary",
          lambda: _real_which("cosmos-no-such-binary-xyz") is None)

    # write_probe_record -- the secret never reaches the artifact.
    prec = td / "probe.json"
    secret = "sk-" + "z" * 40
    written = write_probe_record(prec, {
        "ok": True, "api_key": secret, "OPENAI_API_KEY": secret,
        "ANTHROPIC_API_KEY": secret, "key": secret,
        "key_last4": "sk-…zzzz", "path": td,
    })
    on_disk = prec.read_text(encoding="utf-8")
    check("write_probe_record strips every secret field it knows",
          lambda: not any(k in written for k in SECRET_FIELDS))
    check("the secret is absent from the FILE, not just the return value",
          lambda: secret not in on_disk)
    check("the redacted last4 survives (it is not a secret)",
          lambda: '"key_last4": "sk-\\u2026zzzz"' in on_disk
          or "sk-…zzzz" in on_disk)
    check("a Path value serialises instead of crashing the write",
          lambda: json.loads(on_disk)["path"] == str(td))

    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [r for r in results if not r[1]]
    print("live_value: " + json.dumps(
        {"authority_path": str(auth), "create_no_window": CREATE_NO_WINDOW,
         "child_token": token, "child_stdout_head": (r_ok["out"] or "")[:40],
         "probe_record": str(prec)},
        sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(selftest())
