# Core serve supervisor — F-33 / F-34 (why :8770 was never served)

**Measured and fixed 2026-08-31.** Consumer: Keith (operator) + the health fleet.
Code: `cosmos/cosmos_health_clock.py`. Tests: `builds/health/test_serve_supervisor.py`.

## The fault — two halves, both measured

**Half 1 — the green task that watched the wrong tree (the rc=0 scar).**
The only scheduled task that starts Core is `\COSMOS_Serve_Watchdog` (every 2 min,
`Last Result: 0`). Its action is **out of tree**:

    py -3.14 V:\Ai\BTS_MESH\cosmos_watchdog.py

and that script hard-codes `ROOT = V:\A\Ai\COSMOS\trylive`, `PORT = 8791`. It has been
faithfully keeping the **trial** Core alive and reporting success, while the **real**
root went unserved. Both were up when measured, and they are different systems:

| port | root | tree_id | ledger head at measure |
|------|------|---------|------------------------|
| 8791 | `V:\A\Ai\COSMOS\trylive` | `KMesh-COSMOS-try`  | seq 2290 |
| 8770 | `V:\A\Ai\COSMOS\live`    | `KMesh-COSMOS-live` | seq 687  |

A task returning rc=0 for months is not evidence that the right thing is running.
It also violates **no hard-coded paths** and lives outside the repo tree.

**Half 2 — the supervisor written but never switched on.**
`cosmos_health_clock._supervise_serve` is the in-tree fix and was already complete.
It was gated behind an opt-in `--supervise` flag, and the registered task action is:

    ...\pythonw.exe V:\A\Ai\COSMOS\cosmos\cosmos_health_clock.py --root V:\A\Ai\COSMOS\live --loop

— no `--supervise`. So it returned `DISABLED` on every poll. The heartbeat recorded
**89,082 polls, verdict `RED x1`, `serve_supervisor: null`, zero spawns.**

## The fix (code, in tree)

`--supervise` now **defaults ON** (`argparse.BooleanOptionalAction`; `--no-supervise`
opts out). This was chosen deliberately over a config toggle so the fix needs **no
SCHTASKS re-registration** — the existing `COSMOS Health` action supervises as soon as
the process reloads the file. `standup()` now also writes the flag into the task action
*explicitly* (`--supervise` / `--no-supervise`) rather than relying on the default,
because a registration that omits the flag is exactly how this stayed dormant.

Safety is unchanged and still enforced: single-supervisor spawn lock, persisted backoff
ladder 15→30→60→120→300s, `CHILD_ALIVE` refusal so a second writer can never start, and
`PAUSED_HOLD` on a HOLD pause.

### Activation is automatic — but requires the process to restart
Editing the file does not change a *running* clock (Python has already loaded it). The
`COSMOS Health` task repeats every 1 minute and self-heals, so killing the stale process
is enough; it relaunches on the unchanged action with the new code.

---

## Half 3 — the stale task was not just watching the wrong tree. It was serving it to the LAN.

**Measured 2026-08-31 02:20–02:30.** Everything below is an emitted value, re-measured
in this session; nothing is inherited on trust.

## The bind addresses, verified by socket

`netstat -ano`, the two LISTENING rows:

    TCP    0.0.0.0:8791      0.0.0.0:0    LISTENING    4244
    TCP    127.0.0.1:8770    0.0.0.0:0    LISTENING    28484

A listening row is a claim about a socket, not about reachability, so both were also
dialled from this machine's real interface addresses (`socket.connect`, 2 s timeout):

| target | :8770 | :8791 |
|--------|-------|-------|
| `192.168.1.107` (house LAN) | `TimeoutError` | **CONNECT OK** |
| `100.103.9.112` (tailnet)   | `TimeoutError` | **CONNECT OK** |
| `192.168.56.1` (VM host-only) | `TimeoutError` | **CONNECT OK** |

`:8770` is loopback-only as intended. `:8791` answers on **every** interface — the
house wifi included. "The tailnet is the access control" was true of the tailnet and
of nothing else.

## What is on the exposed port — this tree's own code

`Win32_Process` command line for pid 4244:

    ...\python.exe V:\A\Ai\COSMOS\cosmos\cosmos.py serve
        --root V:\A\Ai\COSMOS\trylive --port 8791 --remote --no-auth --insecure-http

That matters twice over: the exposure is `--remote --no-auth`, **and** the binary is
`V:\A\Ai\COSMOS\cosmos\cosmos.py` — *this* tree. The in-tree fix below therefore
governs the exposed process directly, on its next restart.

## Route enumeration — no `Authorization` header, dialled from `192.168.1.107`

Every route was probed from the LAN address with no credentials. POST routes were sent
a deliberately invalid body, so a `400` (a *body* complaint) proves the request got
**past** the auth gate without mutating anything; a `401` would have proved the gate held.

| route | unauth result | reads | MUTATES |
|-------|---------------|-------|---------|
| `GET /api/v1/status` | 200 | root, tree_id, ledger head | |
| `GET /api/v1/audit` | 200 | chain verdict, record count | |
| `GET /api/v1/events` | 200 | **the ledger itself** | |
| `GET /api/v1/health` | 200 | full health board | |
| `GET /api/v1/spend` | 200 | caps, settled, headroom | |
| `GET /api/v1/jobs` · `/tools` · `/makers` | 200 | queue, contracts, maker map | |
| `GET /api/v1/control` | 200 | control channel state | |
| `GET /` | 200 | KDash Mobile app shell | |
| `GET /api/v1/cvm/pull` | 400 `CLIENT_ID_REQUIRED` | past auth | |
| `POST /api/v1/jobs` | 400 `BAD_REQUEST: 'command'` | past auth | **submits jobs** |
| `POST /api/v1/makers` | 400 `BAD_ENTRY` | past auth | **writes the maker map** |
| `POST /api/v1/voice` | 400 `BAD_INPUT: empty transcript` | past auth | **drives the voice brain** |
| `POST /api/v1/command` | 400 `BAD_REQUEST: 'text'` | past auth | **runs commands** |
| `POST /api/v1/crucible` | 501 `CRUCIBLE_NOT_RUNNABLE` | past auth | |
| `POST /api/v1/control/resume` | **200 `resumed: true`** | | **YES — observed** |
| `POST /api/v1/kill` | **200 `killed: true`** | | **YES — observed** |

Path traversal was tried and **held**: `/../config/api_token.txt`,
`/..%2fconfig%2fapi_token.txt`, `/config/api_token.txt` all `404`. The static allowlist
is doing its job. That is the one control on this port that worked.

### Two of these mutations are not inferred — they were performed

Reaching `400` proves the gate is open without side effects, but the control-channel
routes returned `200` and **changed persisted state**. Reading `GET /api/v1/control`
immediately after, from the same unauthenticated LAN connection:

    "global": { "pause": false, "mic_off": true, "clear_queue": true,
                "updated_epoch": 1788160844.806584 }

`mic_off` and `clear_queue` were flipped by an anonymous request. This was the audit's
own probe and **the state was restored** in the next call (`resumed: true`, back to
`mic_off: false, clear_queue: false, updated_epoch 1788160863.01`). It is recorded here
rather than smoothed over, because it is the proof: an unauthenticated host on the house
wifi can silence Keith's microphone and clear his queue.

### The whole ledger is drainable by anyone on the subnet

`GET /api/v1/events` caps a page at 100 records but takes a `since_seq` cursor, so the
cap is a page size, not a limit. Paging it from `192.168.1.107` with no credentials:

    events retrieved : 2349 of head_seq 2349
    CONVO_TURN       : 208
    VOICE_BRAIN      : 101
    transcript chars : 33264

**All 2,349 records**, including 208 conversation turns carrying a verbatim `text`
field. The transcript content was counted, not printed, and is not reproduced here.

## Does the trial Core hold real data or credentials? — MEASURED

**Yes to both. The trial tree is not a scratch sandbox.**

**Real data — measured.** `trylive/ledger/authority.jsonl` is **1,000,770 bytes /
2,349 records**, chain `VERIFIED`. It is not synthetic: 208 `CONVO_TURN` (33,264 chars
of real transcript), 101 `VOICE_BRAIN`, 12 `VOICE_TELEMETRY`, 9 `CONVO_OPENED`,
8 `COMMAND_HANDLED`, 6 `MAKER_ADDED`, 1,925 `HEALTH_BOARD`. Every one of those records
is readable by any host on the LAN, as measured above.

**Real model calls — measured.** `VOICE_BRAIN` payloads name the brain that actually
answered: **`opus` × 67, `grok` × 30, `local` × 4**. Ninety-seven real vendor calls have
completed through this process, so the credentials those rails need are live in its
address space. `GET /api/v1/spend` reports rail `sgh-api` with 34 settled calls, every
one `provenance: "UNPRICED"` — which means `settled_usd` stays `0.0` and `headroom_usd`
stays the full `10.0` no matter how many are made. **The USD breaker does not bound
this rail.** An unauthenticated caller that reaches `POST /api/v1/voice` with a valid
transcript enters that path. This audit did **not** send one — driving a rail spends
Keith's prepaid capacity, and that is his call, not an auditor's. So: the path is open
and the breaker is measured not to bound it; the spend itself is untested by design.

**Credential material at rest — measured, and NOT reachable over the port.**
`trylive/config/` holds four secret-class files: `api_token.txt` (6 B — a real bearer,
inert while `--no-auth` is set), `cosmos_key.pem` (1,679 B — TLS private key),
`cosmos_cert.pem` (1,143 B), and `install_key.bin` (32 B — the ledger/SEED signing key).
**None was read, printed or copied by this audit** — the inventory is names, sizes and
`config/install_record.json` only. None is reachable through the API: the traversal
probes above all `404`. The exposure is that the service **uses** these credentials on
behalf of anonymous callers, not that it hands them out.

## The fix in this tree — `REMOTE_OPEN_ACCESS`

`cosmos_service.Service.__init__` now refuses a non-loopback bind with `open_access`
(`--no-auth`) as a typed `ServiceError`, **checked first — before the socket is bound
and before any token is touched**. There is no flag past it: `--tls` does not open it
and neither does `--insecure-http`. Encryption is not authentication.

Deliberately **not** over-removed, because both are Keith's and both are legitimate:

- **loopback + `--no-auth` still works** — the local mic trial is untouched.
- **remote + bearer + `--insecure-http` still works** — but its original justification
  ("paired with `--no-auth`, so there is no bearer to capture") is now dead, and the
  docstring says so: on a remote bind it puts a *real* bearer on the wire in the clear.
  It trades confidentiality in transit. It can no longer trade away authentication.

`cosmos.py serve` catches `ServiceError` and prints `REFUSED [KIND] …` to stderr with
`rc=2`, so a supervisor log names the door that was shut instead of showing a traceback.

### Proof, bound to the running system

    $ py -3.14 cosmos\cosmos.py serve --root <tmp> --port 0 --remote --no-auth --insecure-http
    rc = 2
    REFUSED [REMOTE_OPEN_ACCESS] refusing to serve a non-loopback bind ('0.0.0.0') with
    bearer auth disabled - every host that can reach this port would be a full operator
    of Core (drain the ledger, submit jobs, spend money, flip the control channel); bind
    loopback for the no-auth trial, or drop open_access/--no-auth and serve the bearer
    over TLS

That is the **exact argv the exposed pid 4244 is running**, refused by the tree.

`cosmos/test_remote_bind_gate.py` — **11/11 scored assertions pass**, and it proves the
regression by running the same six assertions against the staged pre-fix module in
`_delme/predispose_cosmos_service_20260831_022243/`: **the 4 gate assertions FAIL there
and pass against the tree**, while the 2 "still builds" assertions pass on both (no
over-removal). It also asserts the refusal happens *before* `ThreadingHTTPServer` is
constructed, by trapping that constructor — a refusal that binds first has already
opened the port for the length of the check.

Regression suite, re-run after the change: `test_tls · test_wave3 · test_v1 ·
test_makers · test_cvm_push · test_surfaces · test_rest_surface · test_core ·
test_boot_rails · test_concurrency` — **10/10 rc=0**.

### ⚠ Consequence the operator must know before the next restart

The stale watchdog restarts pid 4244 every 2 minutes on that exact argv. **The next
restart after the tree is reloaded will REFUSE, and the trial Core on :8791 will stay
down.** That is fail-closed working as designed and it closes the exposure without any
operator action — but it is a visible change in behaviour, not a silent one, and the
watchdog's `Last Result` will stop being `0`. Choose an action below deliberately.

:8770 is **not** affected: it binds loopback with bearer auth, a path this change does
not touch, and the running pid 28484 is unaffected regardless.

---

## OPERATOR ACTIONS

**Run these yourself. An agent must not register, change or disable scheduled tasks,
and none of the commands below were executed by this audit.** Items 1 and 2 are the
LAN exposure and are the urgent ones; 3 and 4 are the original supervisor items.

### 1. Close the LAN exposure now — do not wait for the code path

The in-tree refusal only takes effect when the process restarts. To end the exposure
immediately, stop the stale task and the process it is keeping alive:

    schtasks /Change /TN "COSMOS_Serve_Watchdog" /DISABLE
    taskkill /PID 4244 /F

Re-verify with a socket, not with an exit code — this must return **no** `8791` row:

    netstat -ano | findstr ":8791"

(Confirm the pid first — `4244` was measured at 02:20 and the watchdog replaces it
every 2 minutes: `netstat -ano | findstr "0.0.0.0:8791"`.)

### 2. If the trial Core is still wanted, restart it WITHOUT the open door

Pick one. Both are safe; the first is the smaller change.

**2a — keep it local** (loopback; `--no-auth` is still allowed there):

    py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos.py serve --root V:\A\Ai\COSMOS\trylive --port 8791 --no-auth

**2b — keep it reachable, with auth and TLS** (drop `--no-auth`, add `--tls`; clients
send the bearer from `trylive\config\api_token.txt`):

    py -3.14 V:\A\Ai\COSMOS\cosmos\cosmos.py serve --root V:\A\Ai\COSMOS\trylive --port 8791 --remote --tls

Do **not** re-add `--no-auth` to a `--remote` bind — the tree now refuses it, by design.

### 3. Retire or repoint the stale out-of-tree serve watchdog — OPERATOR ONLY

`\COSMOS_Serve_Watchdog` runs `py -3.14 V:\Ai\BTS_MESH\cosmos_watchdog.py`, which is
**outside this fence and outside the repo tree**, so it was **not** modified. Measured
this session: `Scheduled Task State: Enabled`, `Status: Ready`, `Last Result: 0`,
`Repeat: Every 2 Minute(s)` — green for months while serving the LAN. It is now
redundant for the real root (the in-tree supervisor covers :8770). Either:

- **Retire it** (also does item 1):

      schtasks /Change /TN "COSMOS_Serve_Watchdog" /DISABLE

- **Or edit `V:\Ai\BTS_MESH\cosmos_watchdog.py`** to drop `--no-auth` from its argv, so
  it keeps the trial alive on a bind the tree will actually accept.

Do **not** repoint it at `--root ...\live --port 8770`: that would create a second,
uncoordinated supervisor for the same root and defeat the single-writer lock.

### 4. Pin the :8770 supervisor intent explicitly (recommended, not required)
This makes the registration self-documenting and survives any future default flip.
**Run as the operator; do not let an agent register tasks.**

    schtasks /Change /TN "COSMOS Health" /TR "\"C:\Users\Papa\AppData\Local\Programs\Python\Python314\pythonw.exe\" \"V:\A\Ai\COSMOS\cosmos\cosmos_health_clock.py\" --root \"V:\A\Ai\COSMOS\live\" --loop --supervise"

To opt out instead, substitute `--no-supervise`.

> **SUPERSEDED 2026-08-31 02:30 — the earlier version of this item is retained only to
> record that it was wrong.** It offered "**Keep the trial alive** (no action) — it
> continues serving `trylive` on :8791" as a safe default. It is not safe: :8791 binds
> `0.0.0.0` with `--no-auth --insecure-http`, and "no action" leaves an unauthenticated
> Core on the house wifi. See **item 3** above, and Half 3 for the measurement. The
> original text assumed the trial's *root* was the only thing wrong with that task; the
> socket was wrong too, and nobody had dialled it.

## Proof this is bound to the running system (2026-08-31)

- Stale clock pid 18636 killed at **89,217 polls**; task relaunched pid **21028** on the
  **unchanged** action → heartbeat `verdict: "GREEN"`, `serve_8770: true`,
  `serve_supervisor: {"kind": "ALREADY_UP"}` — the row that was `null` for 89k polls.
- Kill test: Core pid 11916 killed → port dead → supervisor spawned pid **28484**,
  **recovered in 2.4 s**.
- `live/logs/core_serve.json` records the spawn argv (`cosmos.py serve --root
  V:\A\Ai\COSMOS\live --port 8770`), `pid: 28484`, `fails: 0` — and 28484 is the pid
  `netstat` shows listening on 8770.
- `GET /api/v1/status` on :8770 → HTTP 200,
  `root: V:\A\Ai\COSMOS\live`, `tree_id: KMesh-COSMOS-live`,
  `ledger_head: {seq: 688, event: "BOOT_VERIFIED"}` — the supervisor-started Core wrote a
  new ledger event. A value only the live tree can emit.
- `builds/health/test_serve_supervisor.py`: **6 of 9 assertions FAIL** against the staged
  pre-fix copy in `_delme/predispose_cosmos_health_clock_20260831_015230/`, **9/9 pass**
  against the fixed module.

## Unblocks
F-17 (CVM stage-6 gate), F-15 (CVM latency measurement — operator's stated #1), and the
cDeck panel measurement that needs a live :8770 on the real root.

## No credential was missing
This was not a secrets problem. Nothing here required a key, token or payment. The only
operator-gated items are the two SCHTASKS commands above.
