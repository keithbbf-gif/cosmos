# CORE :8770 — DIAGNOSIS (probe agent, 2026-08-30)

**Assignment:** diagnose why `cosmos.py serve` is not up on the real root `:8770`; establish
whether the two `docs/BACKLOG.md` "Owed — LIVE CORE" entries share a root cause; propose a patch
for COW to dispose. **Diagnose, do not fix** — `cosmos/` is outside this agent's write fence.

**Fence honored.** Nothing under `cosmos/`, `live/`, `tests/`, `kdash/` or governance was written.
The only files created are `builds/probe/CORE_8770_DIAGNOSIS.md` and
`builds/probe/core8770_dryrun.py`. **No server was started on :8770** (see §6).

---

## 1. VERDICT — one sentence

`cosmos.py serve` does **not** refuse on the real root. It has **never been asked to run**: the
sole launcher in the tree is `serve.bat` — a foreground, interactive, `pause`-terminated batch file
that canon forbids ("**No bats**") and that no Windows Scheduled Task invokes. Every one of the 13
registered COSMOS clocks is a supervised `schtasks` + Python daemon; **Core itself is the one
component with no clock**. The failure kind is **`NO_LAUNCHER` (operational), not a code refusal.**

The two backlog entries are **NOT the same root cause**, and only one is still real (§4).

---

## 2. What was measured (evidence, each bound to an emitted artifact)

### 2.1 Port :8770 is closed; :8791 is up
```
py -3.14 -c "socket.connect_ex(('127.0.0.1',p))"
8770 closed rc=10035
8791 OPEN
```

### 2.2 The port is NOT the problem — 8770 binds freely
Ruling out the Windows `winnat`/Hyper-V excluded-port-range failure mode (`WSAEACCES 10013`):
```
8770 BIND OK
8791 BIND OK
8792 BIND OK
```
`8770` is bindable by this user right now. Not a reservation, not a firewall, not a permission.

### 2.3 The live root boots clean, read-only
`py -3.14 cosmos/cosmos.py status --root V:/A/Ai/COSMOS/live`
```json
{"ready": true, "root": "V:\\A\\Ai\\COSMOS\\live", "tree_id": "KMesh-COSMOS-live",
 "ledger_head": {"seq": 668, "event": "PROBE_RESULT"}}
```
Sentinel content verified, install key present, **full ledger chain verified at open** (`Ledger`
verifies or REFUSES — `cosmos_kernel.py:69`). Nothing in the resolver or ledger is refusing.

### 2.4 The full writing-boot path works — proven twice

**(a) On a scratch root** (`cosmos.py install --root builds/probe/_repro_root`), the exact
production path `Kernel(...)` → `compose_rails()` → `Service(...)`:
```
KERNEL READY True
dispatcher: Dispatcher
adapters: ['claude-cli','codex-cli','cursor-api','firecrawl-web','gem-api','gw-api','oa-api','playwright-dom','sgh-api']
composed: ['node_rails','cursor-api','codex-cli','playwright-dom','firecrawl-web','claude-cli','dispatcher','prove_nodes']
warnings: {}
SERVE OK scheme=http port=59066
```

**(b) On the LIVE root**, zero-write dry-run (`builds/probe/core8770_dryrun.py`) — read-only
Kernel + a faithful replay of `compose_rails` minus every ledger write, then `Service()` on an
**ephemeral** port:
```json
{"root": "V:/A/Ai/COSMOS/live",
 "read_only_boot": {"ready": true, "tree_id": "KMesh-COSMOS-live",
                    "rails_compose": null, "dispatcher": null},
 "dryrun_compose": {"composed": ["node_rails","cursor-api","codex-cli",
                                 "playwright-dom","firecrawl-web","claude-cli"],
                    "warnings": {},
                    "adapters": ["claude-cli","codex-cli","cursor-api","firecrawl-web",
                                 "gem-api","gw-api","oa-api","playwright-dom","sgh-api"]},
 "dispatcher_constructs": "Dispatcher",
 "service_constructs": {"scheme": "http", "ephemeral_port": 59307},
 "service_closed": true}
```
**All six rails compose against live paths with `warnings: {}`. The Dispatcher constructs. The
Service constructs.** There is no refusal to capture, because there is none.

### 2.5 COSMOS's own health clock has been reporting this, unheard
`live/state/health/board.json`, measured `2026-08-30T21:58:17-05:00`:
```json
{"schema": "cosmos-health-clock/1", "verdict": "RED x1", "reds": ["serve_8770"],
 "rows": {"sentinel": {"ok": true}, "ledger_file": {"ok": true},
          "install_key": {"ok": true}, "queue": {"ok": true},
          "serve_8770": {"ok": false, "detail": "TimeoutError: timed out", "rtt_s": 0.2693}}}
```
`live/logs/health_clock_heartbeat.json` → `"polls": 82971`, `"serve_8770": false`.

**This is the finding in miniature.** `cosmos_health_clock.py` has *measured* `serve_8770` red
~83,000 consecutive times and **acts on it exactly zero times** — it probes (`_probe_port`,
`cosmos_health_clock.py:160`) and reports, and there is no supervisor anywhere that starts Core.
Every other subsystem has a clock that restarts it; Core has an observer.

### 2.6 The only launcher is a bat, and it is manual
Exhaustive search for anything that execs serve (`serve --root`, `cosmos.py serve`,
`serve_forever(`) outside `tests/` and `work/`:

| Hit | What it is |
|---|---|
| `serve.bat:17` | `py -3.14 "%~dp0cosmos\cosmos.py" serve --root "%~dp0live" --port 8770` — **the only launcher in the tree** |
| `CLAUDE.md:34` | documentation of the manual command |
| `cosmos/cosmos.py:127` | `svc.httpd.serve_forever()` — the callee, not a launcher |
| `tests/*`, `builds/cvm-dt/*` | `serve_background()` in test fixtures, ephemeral ports |

`serve.bat` is `@echo off` … `title COSMOS serve` … `pause` (lines 1–21): it holds a console
window and blocks on a keypress at exit. It is (a) a bat — **canon: "No bats"**; (b) foreground
and interactive, so it cannot be a service; (c) **not registered as a Scheduled Task**, unlike the
13 clocks in `docs/ORCHESTRATION.md`. Contrast the thing that *is* up:
`docs/SELFTEST_2026-08-25.md:116` records PID 24808 = `cosmos.py serve --root …\trylive --port 8791
--remote --no-auth --insecure-http` — **a human typed that**. `:8791` is up because someone ran it
by hand; `:8770` is down because nobody has.

This was already measured once and lost: `docs/SELFTEST_2026-08-25.md:21` — *"No `python` process
has `--root V:\A\Ai\COSMOS\live --port 8770`"*, and `docs/research/COSMOS/RESEARCH_3.md:575` —
*"scm-registered launcher that execs `py -3.14 cosmos.py serve …`. **None of** …"*.

---

## 3. Why it is not any of the other candidates

| Candidate | Ruled out by |
|---|---|
| Port reserved / firewalled | §2.2 — raw `bind('127.0.0.1', 8770)` **OK** |
| Something already on :8770 | §2.1 — connect refused; nothing listening |
| Resolver / sentinel refusal | §2.3 — `ready: true`, `tree_id=KMesh-COSMOS-live` |
| Ledger chain corrupt (fail-closed REFUSE) | §2.3 — chain verified at open, head `seq=668` |
| `TOKEN_MISSING` / `BLANK_TOKEN` (`cosmos_service.py:401-420`) | §2.4b — `Service()` constructed against live `config/api_token.txt`; loopback bind mints only if absent |
| `REMOTE_CLEARTEXT` (`cosmos_service.py:1503-1517`) | Only fires when `_is_remote_bind(host)`; the documented command has no `--remote`, so `host=127.0.0.1` |
| `CERT_NOT_FOUND` (`cosmos_service.py:1469-1482`) | Only fires with `--cert`/`--key`; documented command passes neither |
| A rail crashing the boot | §2.4b — `warnings: {}`, and `compose_rails` is **fail-OPEN** by design (`cosmos_kernel.py:163-166`) — a dead rail is logged and skipped, never aborts READY |
| Two-writer lock contention with the fleet | Ledger is OS-lock serialized (`cosmos_kernel.py:44-47`); the live ledger already carries **17 `BOOT_VERIFIED`** events, the last at `2026-08-30T16:37:56` (seq 649) — writing kernels boot on this root routinely and succeed |

---

## 4. The two backlog entries: TWO causes, and one is already dead

`docs/BACKLOG.md:44-45`:
> - [ ] `cosmos.py serve` not up on real root `:8770` (only trylive:8791).
> - [ ] `Kernel.__init__` never calls `register_node_rails` — Dispatcher not composed on normal boot.

**Entry A — REAL.** Root cause `NO_LAUNCHER` (§1). Operational, not a code defect.

**Entry B — STALE. Already fixed in the working tree; close it.**
- `cosmos_kernel.py:137-138` — `self.rails_compose = (None if read_only else self.compose_rails(...))`
  on **every writing boot**.
- `cosmos_kernel.py:178` — `("node_rails", "cosmos_node_rails", "register_node_rails", False)` is
  the first entry in the compose table.
- `cosmos_kernel.py:235` — `_try("dispatcher", _disp)`, and `_disp` sets `self.dispatcher = Dispatcher(...)`.
- Runtime proof, §2.4a/b: `dispatcher: Dispatcher`, `composed: [node_rails, …, dispatcher, prove_nodes]`.
- `cosmos_node_rails.py:143` carries the fix note in-band: *"CONTRACT (corrected 2026-08-30 — the
  prior docstring described a design that was changed and cost an audit a regression)"*.

**Why the entry was written and why it never got closed** — the decisive artifact:
```
git show HEAD:cosmos/cosmos_kernel.py | grep -n "compose_rails\|register_node_rails\|dispatcher"
(no matches)
```
The **committed** kernel has no `compose_rails` at all. The fix lives **only in the uncommitted
working tree** (`git status` shows `M cosmos/cosmos_kernel.py`, `M cosmos/cosmos_node_rails.py`).
So entry B accurately described `HEAD`, was fixed in the working tree, and **was never runtime-bound
— because runtime binding for Core is `:8770`, and `:8770` has never come up.**

**Relationship:** distinct causes, one dependency. **A blocks the verification of B, not B's fix.**
Entry B is closable today on the evidence in §2.4b; it needs no code. Entry A needs a launcher.

> ⚠ Flagged for COW, outside this agent's fence: **the Core fix for entry B is uncommitted.**
> A `git checkout`/`stash` of `cosmos/cosmos_kernel.py` would silently un-compose the Dispatcher.

---

## 5. PROPOSED PATCH (for COW to dispose — NOT applied)

**Target: `cosmos/cosmos_health_clock.py`** — *not* a new module.

Rationale (canon: *improvement is not bloat — subtract as well as add*): the clock that must
supervise Core is the one **already measuring the exact condition every 2 s**. It already owns the
`_probe_port` result, the exclusive OS lock, the heartbeat, the board, and `spawn_detached` /
`pythonw_exe` / `atomic_json` — all already imported at `cosmos_health_clock.py:31-35`. Supervision
costs **~45 lines and zero new imports and zero new files**; a standalone `cosmos_core_clock.py`
would cost ~300 lines duplicating lock/heartbeat/standup machinery that exists. The observer becomes
a supervisor.

**Safety properties** (all fail-closed, all typed):
- **Opt-in.** `--supervise` defaults **off**. Without the flag behavior is byte-identical — the live
  fleet cannot be disturbed by landing this (keep-her-afloat).
- **Single supervisor.** An exclusive OS lock (`acquire_lock`) gates the spawn. A second clock gets
  `SUPERVISOR_BUSY` and does not spawn. *This is the guard for the double-claim scar — a stale
  daemon and a one-shot both acting on one job.*
- **Honors PAUSE.** A `mode=hold` PAUSE flag → `PAUSED_HOLD`, no spawn.
- **Backoff, not a respawn storm.** A 2 s loop must never hammer a failing exec: 15→30→60→120→300 s,
  persisted to `logs/core_serve.json` so a clock restart does not reset it.
- **Never invents a new RED.** `serve_supervisor` is added to the excluded set at line 187.
- **Typed kinds:** `ALREADY_UP · DISABLED · PAUSED_HOLD · BACKOFF · SUPERVISOR_BUSY · SPAWNED · SPAWN_FAILED`.
- **No hard-coded paths.** Root comes from `--root` via `CosmosPaths`; the script path from the
  existing `repo_tree()` (`cosmos_health_clock.py:65`).

```diff
--- a/cosmos/cosmos_health_clock.py
+++ b/cosmos/cosmos_health_clock.py
@@ -45,6 +45,10 @@
 DEFAULT_INTERVAL_S = 2.0
 FRESH_S = 8.0
 SERVE_PORT = 8770
+SERVE_LOCK_NAME = "core_serve.lock"
+SERVE_STATE_NAME = "core_serve.json"
+# 2s loop: a failing exec must back off, never storm.
+SERVE_BACKOFF_S = (15, 30, 60, 120, 300)
 
 PEER_HEARTBEATS = (
     "watchdog2_heartbeat.json",
@@ -85,6 +89,54 @@
     return {"ok": ok, "host": host, "port": port,
             "rtt_s": round(time.time() - t0, 4), "error": err}
 
 
+def _supervise_serve(paths, up: bool, supervise: bool, pause_mode) -> dict:
+    """Start Core if it is down. THE fix for BACKLOG 'serve not up on real root':
+    this clock has probed :8770 ~83k times and never started it. Opt-in, single-
+    supervisor, backed off, PAUSE-aware. Typed refusal on every non-spawn path.
+    """
+    if not supervise:
+        return {"kind": "DISABLED", "detail": "--supervise not set"}
+    if up:
+        return {"kind": "ALREADY_UP", "detail": "port %d listening" % SERVE_PORT}
+    if pause_mode == "hold":
+        return {"kind": "PAUSED_HOLD", "detail": "PAUSE mode=hold - no spawn"}
+    st_path = paths.logs(SERVE_STATE_NAME)
+    try:
+        st = json.loads(st_path.read_text(encoding="utf-8"))
+    except (OSError, ValueError):
+        st = {}
+    now = time.time()
+    if now < float(st.get("next_attempt_epoch") or 0):
+        return {"kind": "BACKOFF", "detail": "next attempt in %.0fs"
+                % (float(st["next_attempt_epoch"]) - now),
+                "fails": st.get("fails", 0)}
+    pid = int(st.get("pid") or 0)
+    if pid and pid_alive(pid):
+        # Child is alive but the port is not answering yet - give it the window.
+        return {"kind": "BACKOFF", "detail": "child pid=%d starting" % pid,
+                "pid": pid}
+    fd = acquire_lock(paths.logs(SERVE_LOCK_NAME))
+    if fd is None:
+        return {"kind": "SUPERVISOR_BUSY",
+                "detail": "another supervisor holds the Core spawn lock"}
+    try:
+        argv = [pythonw_exe(), str(repo_tree() / "cosmos" / "cosmos.py"), "serve",
+                "--root", str(paths.root), "--port", str(SERVE_PORT)]
+        rec = spawn_detached(argv, str(repo_tree()), paths.logs("core_serve.out"))
+        fails = 0 if rec.get("ok") else int(st.get("fails") or 0) + 1
+        back = SERVE_BACKOFF_S[min(fails, len(SERVE_BACKOFF_S) - 1)]
+        atomic_json(st_path, {"pid": rec.get("pid"), "ok": bool(rec.get("ok")),
+                              "argv": argv, "fails": fails,
+                              "attempted_epoch": now,
+                              "next_attempt_epoch": now + back})
+        return {"kind": "SPAWNED" if rec.get("ok") else "SPAWN_FAILED",
+                "detail": str(rec.get("detail") or rec.get("error") or "")[:200],
+                "pid": rec.get("pid"), "fails": fails, "backoff_s": back}
+    finally:
+        os.close(fd)
+
+
 def poll_once(root: str, polls: int = 0,
-              interval_s: float = DEFAULT_INTERVAL_S) -> dict:
+              interval_s: float = DEFAULT_INTERVAL_S,
+              supervise: bool = False) -> dict:
     paths = CosmosPaths(root)
     logs = paths.logs()
@@ -160,6 +212,11 @@
     sock = _probe_port("127.0.0.1", SERVE_PORT)
     rows["serve_8770"] = {
         "ok": sock["ok"],
         "detail": ("listening rtt_s=%s" % sock["rtt_s"] if sock["ok"]
                    else sock.get("error") or "not listening"),
         "rtt_s": sock["rtt_s"],
     }
+    sup = _supervise_serve(paths, sock["ok"], supervise, pause_mode)
+    rows["serve_supervisor"] = {"ok": True, "detail": "%s %s"
+                               % (sup["kind"], sup.get("detail") or ""),
+                                "kind": sup["kind"]}
 
@@ -186,7 +243,8 @@
     reds = {n: r for n, r in rows.items()
-            if n not in ("pause_flag", "peer_heartbeats", "serve_8770")
+            if n not in ("pause_flag", "peer_heartbeats", "serve_8770",
+                         "serve_supervisor")
             and not r.get("ok")}
@@ -228,7 +286,7 @@
-def loop(root: str, interval_s: float) -> int:
+def loop(root: str, interval_s: float, supervise: bool = False) -> int:
@@ -256,1 +314,1 @@
-                poll_once(root, polls=polls, interval_s=interval_s)
+                poll_once(root, polls=polls, interval_s=interval_s,
+                          supervise=supervise)
@@ -331,6 +389,8 @@
     ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
+    ap.add_argument("--supervise", action="store_true",
+                    help="START Core on :8770 when it is down (single-supervisor, "
+                         "backed off, PAUSE-aware). Default OFF: observe only.")
     a = ap.parse_args()
@@ -345,5 +405,6 @@
     if a.once:
-        r = poll_once(a.root, interval_s=a.interval)
+        r = poll_once(a.root, interval_s=a.interval, supervise=a.supervise)
         print(json.dumps({k: r[k] for k in r if k != "rows"},
                          indent=1, default=str))
         return 0
-    return loop(a.root, a.interval)
+    return loop(a.root, a.interval, supervise=a.supervise)
```

### 5.1 The SUBTRACT half (canon: net complexity trends down)
**Stage `serve.bat` → `_delme/`.** It is a bat (canon forbids), it is the reason the failure looked
like a code problem, and once the clock supervises Core it is a second, unsupervised way to start a
second writer. `CLAUDE.md:34` already documents the manual command for a cold peer; nothing is lost.
```
PROPOSAL {target_path: "serve.bat", action: "stage",
          dest: "_delme/delme__2026-08-30__serve.bat", rationale: "canon: No bats;
          sole launcher was manual+foreground; superseded by the health-clock supervisor"}
```
Net: **+45 lines, −21 lines, −1 file, 0 new modules, 0 new imports.**

### 5.2 Runtime binding (the gate this patch must pass — Keith's call to run)
```
py -3.14 cosmos\cosmos_health_clock.py --root V:\A\Ai\COSMOS\live --once --supervise
py -3.14 -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8770/api/v1/health').read())"
```
Binding value = a **fresh** `BOOT_VERIFIED` at `seq > 668` in `live/ledger/authority.jsonl` **plus**
a `/api/v1/health` body from `:8770` — neither of which any exit code or green log can fabricate.
Then `live/state/health/board.json` must flip `verdict` from `RED x1` to `GREEN`, which is the
projection proving it, not a claim about it.

**Owed to Keith (elevated, one line):** the schtasks registration so it survives logon. The existing
`standup()` already builds this; it needs `--supervise` in the `tr` string:
```
schtasks /create /tn "COSMOS Health" /tr "<pythonw> ...\cosmos_health_clock.py --root <root> --loop --supervise" /sc minute /mo 1 /f
```

---

## 6. What this agent did NOT do, and why

1. **Did not start a server on :8770.** Requirement (1) asked for the real refusal; there is no
   refusal to capture, so the honest substitute was §2.4b — the full boot path replayed against the
   **live** root with every ledger write removed, and `Service()` bound to an **ephemeral** port and
   closed immediately. A competing server was never created.
2. **Did not boot a *writing* Kernel on the live root.** That appends `BOOT_VERIFIED` to
   `live/ledger/authority.jsonl`, and `live/ledger` is core state — Orchestrator-only under
   `docs/AGENT_BOUNDARIES.md:18`. §2.4b gets the same evidence with zero live writes. The one
   remaining unknown a writing boot would settle — whether `prove_nodes` → `Registry.file_runtime`
   succeeds on live — is **already answered by the fleet's own artifact**:
   `live/registry/nodes.json` reads `count: 4, nodes: [claude-cli, gem-api, oa-api, sgh-api],
   measured_at: 2026-08-30T21:57:02`, and `live/ledger` carries 252 `PROBE_RESULT` events, the last
   three at `21:08` with real model ids (`grok-4.6`, `gemini-2.5-flash`, `gpt-5.6-terra`).
3. **Did not edit `cosmos/`.** Out of fence — §5 is a proposal, unapplied.
4. **Could not enumerate Scheduled Tasks directly.** `schtasks /query` and `netstat -ano` were both
   denied by the permission layer. The launcher conclusion therefore rests on the *tree-side*
   exhaustive search in §2.6 (no task-creating call anywhere names `serve`; `cosmos_own_clocks.py`
   contains **zero** matches for `serve` or `8770`) plus the recorded process census in
   `docs/SELFTEST_2026-08-25.md:21,112,116`. **COW should confirm with one host-side line:**
   `schtasks /query /fo LIST /v | findstr /i "cosmos serve"`.

## 7. Files this agent wrote
- `builds/probe/CORE_8770_DIAGNOSIS.md` (this file)
- `builds/probe/core8770_dryrun.py` (the zero-write reproduction, re-runnable)
- `builds/probe/_repro_root/` (throwaway installed root for §2.4a) — **staged, not deleted**, to
  `_delme/delme__2026-08-30__probe_repro_root`. It carried its own generated `install_key.bin`;
  the live key was never copied or read.

## 8. Gate
`py -3.14 builds/selftest_clock/cosmos_selftest_clock.py --root V:/A/Ai/COSMOS --once`

Before this agent's writes (baseline):
```json
{"ok": true, "total": 78, "passed": 78, "flaky": 0, "failed": 0,
 "ts": "2026-08-31T03:01:04Z", "elapsed_s": 152.4}
```
After (final):
```json
{"ok": true, "schema": "cosmos-selftest-clock/1", "ts": "2026-08-31T03:06:42Z",
 "total": 80, "passed": 80, "flaky": 0, "failed": 0,
 "flaky_names": [], "failing": [], "elapsed_s": 158.6, "repo": "V:\\A\\Ai\\COSMOS"}
```
Total rose 78 → 80 between the two runs; **this agent added no tests** (it wrote only
`builds/probe/`), so the two new cases came from a concurrent fence. Nothing reddened.
