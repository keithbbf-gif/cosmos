# PROPOSAL (out of fence) — update two suites for the supervise default flip

**From:** the F-33/F-34 agent. **Fence:** `cosmos/` + `builds/health/`.
`tests/` is held by another writer, so per `docs/AGENT_BOUNDARIES.md` (P10) these are
**proposals**, not edits. Each is **proven to work** by a patched copy in this folder.

## Why anything changed
`cosmos/cosmos_health_clock.py` now defaults `--supervise` **ON** (see
`docs/CORE_SERVE_SUPERVISOR.md`). Two suites pin the old opt-in contract and now fail:

| suite | before | after fix | after this proposal |
|---|---|---|---|
| `tests/test_core_supervisor.py`   | 31/31 | 18/31 | **31/31** (measured) |
| `tests/test_health_clock_optin.py`| 18/18 | 11/18 | **18/18** (measured) |
| `tests/test_own_clocks.py`        | 66/66 | **66/66** | unaffected |

**None of the 20 failures is a functional regression.** Proven by
`builds/health/test_cascade_isolation.py` (11/11): every "functional-looking" failure
(`SPAWNED`, the three `argv` checks, `DISABLED`, `ALREADY_UP`) passes on a *clean* root.
They failed only because `poll_once(str(root))` in section 1 now legitimately spawns and
writes `logs/core_serve.json` with a future `next_attempt_epoch`, so the next call
correctly returns `BACKOFF` and `CALLS` is empty → `IndexError`. The harness demonstrates
that cascade directly rather than asserting it.

## Proposal 1 — `tests/test_core_supervisor.py` (ONE line)

Line 91. Section 1 is titled *"OFF is inert"*; it relied on OFF being the **default**.
Make it **ask** for OFF. This restores the section's meaning and removes the state
pollution that cascaded into 7 later assertions.

```diff
@@ -89,7 +89,7 @@
     # ---- 1. OFF is inert. The live fleet runs this path right now. -----------
     del CALLS[:]
-    r = hc.poll_once(str(root))
+    r = hc.poll_once(str(root), supervise=False)
```

Also worth updating the section comment: the live fleet now runs the **ON** path.
Verified: `builds/health/patched_test_core_supervisor.py` → **31/31 passed**.

## Proposal 2 — `tests/test_health_clock_optin.py` (4 edits)

The inertness checks stay valuable; they just have to *ask* for OFF now.

```diff
@@ -68 +68
-    rc, out = run_cli("--root", str(off), "--once")
+    rc, out = run_cli("--root", str(off), "--once", "--no-supervise")
@@ -82 +82
-    rc2, out2 = run_cli("--root", str(off), "--once")
+    rc2, out2 = run_cli("--root", str(off), "--once", "--no-supervise")
@@ -109 +109
-          and "Default OFF" in help_out)
+          and "--no-supervise" in help_out and "DEFAULT ON" in help_out)
@@ -114,2 +114,2
-        check(f"{name}(supervise=) defaults to False",
-              lambda s=sig: s.parameters["supervise"].default is False)
+        check(f"{name}(supervise=) defaults to True",
+              lambda s=sig: s.parameters["supervise"].default is True)
```

Note the third hunk: `--supervise` **is** still documented — `--help` renders
`--supervise, --no-supervise` with the full help text. That assertion failed only on the
literal string `"Default OFF"`, which is the contract that moved.

Consider renaming the file (`test_health_clock_supervise_default.py`) — "optin" now
describes the opt-**out**. Left as the holder's call.
Verified: `builds/health/patched_test_health_clock_optin.py` → **18/18 passed**.

## Reproduce
```
py -3.14 builds/health/make_patched_tests.py     # regenerates both patched copies
py -3.14 builds/health/patched_test_core_supervisor.py
py -3.14 builds/health/patched_test_health_clock_optin.py
py -3.14 builds/health/test_cascade_isolation.py
```
`make_patched_tests.py` fails loudly (`ANCHOR MISSING`) if `tests/` has moved under it, so
a stale proposal cannot silently appear to pass.
