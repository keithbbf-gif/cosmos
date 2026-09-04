# groq-api Kernel compose — how the satellite attaches without making the Kernel a second writer

**Work order:** WO: groq-api Kernel compose (Lane B Cursor), 2026-09-04 · **Lane:** Cursor Cloud Agent (Opus 5; Composer 2.5 / Auto refused) · **Model:** claude-opus-5

**Status: PROPOSE only (P10).** `cosmos/cosmos_kernel.py` is **not edited by this PR** — the patch appears only as a diff inside this file. The satellite `cosmos/cosmos_groq_rail.py` is **not rewritten**: it is GATE PASS as of 2026-09-04 and this proposal treats that as settled. No live `--gate` was re-run; every test here is fake-HTTP and opens no socket. `V:\Ai` was not written. **Do not merge.** CCr writes the live tree.

**Answer in one line:** compose at boot is **four lines in the Kernel and one new `attach_groq_rail()`**, and the whole difficulty is a single distinction — **composing is not registering**. Building the adapter is memory; registering the link and setting its budget are *ledger appends*. Do those unconditionally at boot and you reopen the B1 scar on read-only kernels **and**, worse, you silently unroute every rail on writing ones.

---

## 0. Evidence ledger — what I could and could not read

`cosmos/cosmos_groq_rail.py` **is not in this repository.** Neither is `firecrawl`, nor a `cursor` rail, nor `boot_compose`, nor `GROQ_API_KEY`, nor `service_tier`. This is not a stale checkout:

| Check | Result |
|---|---|
| `cosmos/cosmos_groq_rail.py` on `main` (`14addfc`) | absent |
| `firecrawl`, `groq`, `boot_compose`, `service_tier`, `GROQ_API_KEY` across **all 60+ refs and every commit tree** | **0 hits** |
| `Kernel.__init__` signature here | `(root, worker="core", clock=time.time, read_only=False)` — no `boot_compose` |
| Only rail-attach function that exists | `cosmos_node_rails.register_node_rails()` — four `bts_*` rails |

So I cannot copy "the same way firecrawl/cursor attach" literally. What I did instead: derive the attach from **the only attach in the tree** (`register_node_rails`) and give it the same signature, so the port is mechanical whichever shape the live one has. Claims are tagged **[CODE]** (read and, where it says MEASURED, executed here), **[VENDOR]** (Groq's own docs, read 2026-09-04), or **[ASSUMED]** with the command that settles it.

**What this buys you that a text proposal does not:** the Kernel-side invariants are checked against a **real `Kernel` booted on a temp root**, not a mock. `install()` → `Kernel(root, read_only=True)` → compose → count the ledger. That number is the proposal.

---

## 1. The finding that decides the design

`Registry.register()` appends `LINK_REGISTERED` [CODE: `cosmos_registry.py:44`]. `SpendGate.set_budget()` appends `BUDGET_SET` [CODE: `cosmos_spend.py:40`]. `register_node_rails()` calls both [CODE: `cosmos_node_rails.py:88,94`]. **A rail attach is two ledger writes.** Put that in `Kernel.__init__` and two separate things break.

### (a) The one the work order names: a read is a write

The Kernel already goes to real trouble not to write on read paths — `read_only=True` skips `BOOT_VERIFIED`, skips `mail.register()`, skips the ledger `mkdir`, and monkeypatches `arbiter._append` to refuse [CODE: `cosmos_kernel.py:38-98`]. The comment says why: *"every `Kernel()` appended `BOOT_VERIFIED`, so `cosmos status` while `serve` ran made a second writer."* An unconditional `boot_compose` puts two appends per boot straight back into `cosmos status`. That is the B1 scar, reopened by a rail.

### (b) The one nobody names, which also hits **writing** kernels

The Registry's fold replaces the whole row on registration [CODE: `cosmos_registry.py:86-88`]:

```python
if e == "LINK_REGISTERED":
    s[p["link_id"]] = {"claim": p, "last_probe": None, "ok": None}
```

**A second registration discards the last probe.** And `route()` filters on `ok` [CODE: `cosmos_registry.py:120`], so the link stops being dispatchable. Measured in this clone, with the real modules:

```
after probe  : verified=True   route candidates: ['groq-api']
after re-reg : verified=None   route candidates: []
```

A boot-time register with no `absent?` guard means **every composed rail is unroutable on every boot until something re-probes it**. On a box that boots Core often — and `README.md` says the predecessor's scar was a scheduler running for six days on the wrong tree, so boots are not rare here — the rails matrix reads UNKNOWN permanently and the Dispatcher raises `NO_LIVE_LINK` for a rail that is live. That is a *silent* capability loss, which is the worst kind this tree has.

### The rule that falls out

> **Compose always. Register only if you are a writer, and only if it would change something.**

```
compose (memory)              register (ledger)
─────────────────             ─────────────────
adapters[link_id] = rail      LINK_REGISTERED   ← writer only, only if absent
registry.attach_probe(...)    BUDGET_SET        ← writer only, only if the cap changed
                              PROBE_RESULT      ← never at boot; see §4
```

Everything else in this proposal is consequence.

---

## 2. The Kernel patch

Four lines, and **not one Groq fact among them** — no endpoint, no model id, no refusal list, no key. `cosmos_makers` states the house rule: *"A second declaration of the same id is a drift, not an update."* The satellite owns the Groq contract; the Kernel owns composition. There is a test that greps this very patch for those literals.

<!-- KERNEL-PATCH-BEGIN -->
```diff
--- a/cosmos/cosmos_kernel.py
+++ b/cosmos/cosmos_kernel.py
@@ class Kernel:
     def __init__(self, root: str | os.PathLike, worker: str = "core",
-                 clock=time.time, read_only: bool = False):
+                 clock=time.time, read_only: bool = False,
+                 boot_compose: bool = False):
@@ (end of the composition block, after ITC)
         self.convo = ConvoStore(self.ledger, clock=clock)
         self.itc = ITC(self.ledger, fetcher=_https_get, clock=clock)
+        # 6 - RAIL COMPOSITION (optional). A rail is NOT foundation: the kernel fails
+        # fast on resolver/key/ledger because a kernel without those is not a kernel,
+        # but a kernel without a model rail is a kernel with one fewer rail. Compose
+        # is in-memory; the two ledger appends inside are skipped for a reader (B1)
+        # and skipped again on a re-boot (re-registration discards the last probe).
+        self.adapters: dict = {}
+        if boot_compose:
+            from cosmos_groq_rail import compose_into_kernel
+            compose_into_kernel(self)
         self.ready = True
```
<!-- KERNEL-PATCH-END -->

In the live tree there is already a `boot_compose` block that attaches firecrawl and cursor **[ASSUMED — 0 hits here]**, so the real change is *one line* next to those two. The signature change above is only what this clone would need.

`compose_into_kernel()` is in `proposals/groq_compose_ref.py` and belongs in the satellite. It cannot raise past itself: a rail that explodes at compose time records `RAIL_COMPOSE_FAILED` on a writing kernel, records nothing on a reader, and Core still reaches `ready`. **Keep-her-afloat is a code path, not an intention** — there is a test that boots a Kernel with a deliberately exploding rail and asserts `k.ready`.

**Import placement matters.** The import is *inside* the `if`, like every other subsystem import in `__init__` [CODE: `cosmos_kernel.py:103-121`]. A module-level `import cosmos_groq_rail` would mean a missing or syntactically broken satellite makes the Kernel unimportable — Core `:8770` down because of a rail file. That is the exact failure mode "keep-her-afloat" is instructing against.

---

## 3. The attach

`attach_groq_rail(registry, adapters, *, ledger, spend_gate, transport, read_only)` — same shape as `register_node_rails(registry, adapters, spend_gate, src, dst)` [CODE: `cosmos_node_rails.py:74`].

| | Value | Why not something else |
|---|---|---|
| `link_id` | `groq-api` | from the WO |
| route | `core -> models` | the route the other four model rails are on. A private route (`core -> groq`) would make it invisible to the Dispatcher's fallback chain, which is the only reason to add a fourth model rail |
| `policy_rank` | `0` | `route()` sorts `(-policy_rank, pref[rail_type])` with `DOM < CLI < API` [CODE: `cosmos_registry.py:114,125`]. Rank 0 keeps DOM ahead of it. Any positive rank would quietly promote an API rail above the DOM lane, against the ratified *"DOM is the default, the API is the fallback"* |
| `metered_usd` | `0.002`, **nonzero** | `Dispatcher` only routes through the breaker when `getattr(adapter, "metered_usd", 0)` is truthy [CODE: `cosmos_rails.py:116`]. Set it to `0.0` for a free key and every Groq call becomes invisible to the breaker *and* absent from `spend.audit()`. Free is a price, not an absence of accounting |
| `budget_usd` | `5.0`, its own row | `guarded_call` raises `UNKNOWN_RAIL` for a rail with no budget [CODE: `cosmos_spend.py:75`], so the budget is not optional once metered |

**The registration race.** Two kernels booting at once both see "absent" and both register — the same check-then-act race `cosmos_makers.add()` closed as its FINDING #5. The attach therefore registers through `ledger.append_guarded()`, which holds the OS lock across replay → decide → append [CODE: `cosmos_ledger.py:189-201`], and appends *nothing* if a concurrent kernel already won.

That has one cost worth stating plainly: `Registry.register()` has no guarded variant, so the attach **restates the `LINK_REGISTERED` payload shape**. Restating a contract in a second place is precisely the drift this tree keeps closing. Two responses, and I did both: the test compares the restated payload **byte-for-byte** against what `Registry.register()` actually writes, so a Registry change turns it red; and the durable fix is a `register_once()` on the Registry itself, which I am **not** applying —

```python
# cosmos_registry.py — RECOMMENDED, NOT APPLIED IN THIS PR
def register_once(self, link_id, rail_type, src, dst, policy_rank=0) -> bool:
    """Register only if absent, atomically. A second LINK_REGISTERED discards the
    link's last measurement (see the fold), so 'register on every boot' is not
    idempotent - it is amnesia. Returns True if this call wrote."""
    if rail_type not in RAIL_TYPES:
        raise RegError("BAD_TYPE", f"{rail_type!r} not in {sorted(RAIL_TYPES)}")
    payload = {"link_id": link_id, "rail_type": rail_type, "src": src,
               "dst": dst, "policy_rank": policy_rank}

    def decide(recs):
        for rec in recs:
            if rec["event"] == "LINK_REGISTERED" and \
                    rec["payload"].get("link_id") == link_id:
                return None                       # someone else won; write nothing
        return ("LINK_REGISTERED", payload)
    return self.ledger.append_guarded(decide) is not None
```

---

## 4. Boot compose does **not** probe

A probe is a ledger write (`PROBE_RESULT`), so a reader cannot do one; and `Registry` is explicit that *"registration is not capability"*. So after boot, `groq-api` is **known and adaptable but not verified**, and `route()` will not select it until something probes. That is correct, and it is stated rather than worked around.

Which leaves **two** probes, deliberately, because they answer different questions and cost different things:

**Shallow — attached to the Registry, zero requests.** Is a credential resolvable, and is the configured default model permitted at this tier? Both can go **red**, which is the point: `ApiRail.probe()` returns a flat `True, "api adapter present"` [CODE: `cosmos_rails.py:82`], and copying that here would register a rail that is verified by construction — the *"health row that could never go red"* scar `cosmos_health` exists to close. A green shallow probe says *"liveness is per-call"* and does not claim the API is up.

**Deep — for the health board, not the Registry.** `GET /openai/v1/models` consumes no tokens, so it is a free check that the configured model is still in the live catalog. It belongs on a `cosmos_health` row and **not** on the Registry, because `Registry.probe_all()` is reached from status paths and a network fan-out there turns `cosmos status` into an egress event.

The deep probe is also the honest answer to the deny-list's structural weakness — see §5.

---

## 5. The two refusals, which are one fact

The work order gives two constraints that look unrelated. They are the same fact: **this key is not on a committed-spend contract.**

- **flex is paid-accounts-only.** Omitting `service_tier` *is* `on_demand` [VENDOR]. On this key, `flex` returns **498 `capacity_exceeded`**.
- **The Llama 3.x retirement is tier-scoped.** Groq's 2026-08-16 notice says it exactly: *"This deprecation applies to free and developer-tier usage; enterprise customers with a committed-spend contract are not affected."* [VENDOR] That is where the work order's phrase "Llama 3.x **Free/Dev** ids" comes from — and note the recommended replacement for `llama-3.1-8b-instant` is `openai/gpt-oss-20b`, which is exactly the satellite's default. The pieces fit.

So the design is **one declared tier driving both policies**, not two hard-coded lists that drift apart. A blanket refusal of `llama-3.3-70b-versatile` would be *wrong* for an enterprise key — it would refuse a model that key can still call.

### The second reason flex stays refused, which survives a paid upgrade

Flex's contract is *"fails fast with 498 — add jittered backoff and retries"* [VENDOR]. `cosmos_sched` is **report-never-retry**: *"a stale RUNNING job is REPORTED (JOB_STALE event) and never [retried]"* [CODE: `cosmos_sched.py:18`]. **A rail that requires client-side retry to meet its contract cannot be driven by a scheduler that refuses to retry.** Upgrade the key and this reason is still standing. So `service_tier` is never emitted with *any* value — not `"auto"`, not `"on_demand"`, not `null` — and a caller who supplies one gets a typed `PARAM_REFUSED` rather than a silent drop, because quietly discarding a parameter someone asked for is a lie about what was sent. The body is an allow-list for the same reason: nothing new reaches the wire unreviewed, including a re-spelled `Service-Tier`.

### The refusal table, and the hole in it

Fifteen ids, each with its **shutdown date, replacement, and the tiers it binds** — full table in `proposals/groq-api-kernel-compose.json`, sourced from `console.groq.com/docs/deprecations` read 2026-09-04. A refusal without a date is folklore, and a refusal that cannot name the replacement makes the caller go and look it up.

Refusal happens **before the key is read and before any socket opens** — the same reason `cosmos_spend` denies before it spends: *"denied BEFORE the call, which is the whole point."* A request that can only fail is not worth a round trip, and *"400 model_decommissioned"* from the wire tells you less than *"shut down 2025-03-20, use `openai/gpt-oss-120b`"* does.

**Now the hole, stated rather than hidden.** A dated table is a *cache* of the vendor's catalog. It goes stale silently, and stale means **fail-open** — an id retired after 2026-09-04 sails straight through. Three things close it, in order of cost:

1. **The family net (free).** On free/developer, *any* Llama 3.x or Mixtral spelling is refused whether or not it is in the table. `llama-3.9-imaginary-42b` is refused.
2. **The deep catalog probe (free).** `probe_deep()` goes red with `CATALOG_DRIFT` the moment the configured model leaves the live catalog. This is the check that tells you the table is stale.
3. **Binding `response.model` (free, and the one the WO asked for).** See below.

---

## 6. Binding `response.model` is what closes the loop

`SOP.md`: *"Read state back after every write. Never trust `rc=0`."* Groq answers with the id that actually served, which is not always the id asked for — Groq has shipped silent upgrades before (the 3.1 → 3.3 ids *"automatically upgrade"* during a transition window [VENDOR]).

So the served id is bound onto the result, and three things follow:

- **The served id is what gets carried and ledgered**, not the requested one. Drift is reported, never silently absorbed.
- **A 200 that will not name its model is `BAD_RESPONSE`.** A reply that cannot name its model cannot be bound, and an unbound reply is an assumed one — the same discipline as ITC's `index_hash` on every hit.
- **The served id is re-checked against the refusal table.** A request that was permitted on the way out and answered by a retired model comes back `MODEL_DRIFT`, not a clean success. That is the fail-open hole closing itself after exactly one call.

### One more accounting point, because `cosmos_spend` cares

*"An unpriced call is UNPRICED, never zero"* — but that rule is about a call that **happened** at an unknown price. A call refused locally **never left the process**, so it cost exactly `$0.00` and that is a *measurement*, not an assumption. Reporting refusals as UNPRICED would fill `spend.audit()["unpriced_calls"]` with events that were never requests. So:

| outcome | `usd` | provenance |
|---|---|---|
| refused locally (model, param, no key) | `0.0` | measured: no request was sent |
| request left the process (success or failure) | `None` | UNPRICED — Groq bills tokens, not dollars |

Both are asserted against a real `SpendGate` in the test.

---

## 7. Failure typing, and one interaction worth knowing

`Dispatcher` continues to the next live link **only** for `UNREACHABLE`, `SESSION_EXPIRED`, `AUTH_REQUIRED`, and records a `RAIL_FALLBACK` event when it does — *"explicit audited fallback"*, never silent [CODE: `cosmos_rails.py:131-138`]. So the status mapping is routing behaviour, not cosmetics, and it is written down:

| HTTP | kind | effect in the Dispatcher |
|---|---|---|
| 401 / 403 | `AUTH_REQUIRED` | audited fallback to the next live model rail |
| 5xx | `UNREACHABLE` | audited fallback |
| 429 | `RATE_LIMITED` | stops with `RAIL_FAILED` |
| 498 | `CAPACITY_EXCEEDED` | stops — **and if you ever see one, something re-enabled `service_tier`** |
| 400 `model_decommissioned` | `MODEL_REFUSED` | stops — and means the local table is stale |

**429 is arguably a fourth fallback kind** — a rate-limited free rail is exactly when you want the next live link. Widening that set changes routing for *every* rail in the tree, so I am naming it and not doing it.

And `dispatch()` **never raises**. If it did, `guarded_call` would release the reservation and re-raise, and the Dispatcher would wrap it as `RailError("NOT_PERMITTED")` [CODE: `cosmos_rails.py:118-124`] — a model refusal arriving as a budget denial, sending whoever reads the ledger to the wrong subsystem. A typed dict keeps the reason intact.

---

## 8. The credential, and why this one is not a footnote

The authority ledger is an **append-only hash chain**, and `cosmos_makers` states the house rule for the whole tree: *"There is no delete."* A secret written into it once is written into it forever, and redacting it afterwards **breaks the chain** — the one repair that is not available. Rotation is your only recourse, and rotation does not un-publish a distributed repo.

So: the key is resolved at **dispatch time**, never captured at import or construction; it travels in the `Authorization` header and nowhere else; and `redact()` runs over every detail string before it can reach a ledger, an error, or a result. That last one is not paranoia about Groq — it is about gateways and proxies that echo request headers into error bodies, and the ledger has no undo. The test plants the key in a 400 body and asserts it comes back `***REDACTED***`, and separately greps the whole authority ledger after an end-to-end dispatch.

---

## 9. Files, and how the evidence was produced

| File | |
|---|---|
| `proposals/groq-api-kernel-compose.md` | this proposal |
| `proposals/groq-api-kernel-compose.json` | machine-readable decision record, in `cosmos_port_plan.PORT_DECISIONS` shape, using the tree's own four dispositions |
| `proposals/groq_compose_ref.py` | reference implementation — the attach, the policy functions, and `conformance()`. **Not wired**; nothing under `cosmos/` imports it |
| `tests/test_groq_compose.py` | 78 checks, fake-HTTP throughout, plus a planted failure |

`README.md`: *"Every gate executable. A check that cannot fail is not a check, and a check that never ran is indistinguishable from one that passed."* A compose proposal whose invariants cannot be run is prose, so the seven invariants are executed:

- against a **real `Kernel`** booted on a temp root — the read-only ledger count, the idempotent re-boot, and the exploding-rail keep-her-afloat path are measured on the actual class, not a mock;
- against a **fake transport** that records every request — no socket is opened by this suite, ever;
- against the **JSON record itself** — dispositions validated against `cosmos_tools.DISPOSITIONS` rather than a vocabulary I invented, every `cosmos_*` successor checked to exist, and the refusal table and link facts **counted against the code** rather than quoted, so the document cannot drift from the harness.

It carries a planted failure per `cosmos_health`, and returns `BOARD-BROKEN` with exit 2 if that planted failure ever shows green.

**And the board was checked against seven mutations, because a green suite proves nothing until you have watched it go red.** Each mutation reintroduces one of the defects this proposal exists to prevent — a read-only kernel that writes at boot, an unguarded re-registration, `service_tier=flex` in the body, a served model taken on trust, a credential that reaches an error string, a compose that raises past itself, and the planted failure disabled. **All seven were detected**, the last one as `BOARD-BROKEN` exit 2.

One of them earned its keep immediately: the first version of the re-registration mutation was **missed**, because idempotence turned out to have two independent layers — the `state()` pre-check *and* the guarded append — and either alone was enough to hide the other. There is now a check that blinds the pre-check and exercises the guarded append on its own.

### `conformance()` — for the satellite I could not read

Since `cosmos_groq_rail.py` is not here, the transport-level invariants ship as a harness CCr can point at the **live** satellite:

```python
from cosmos_groq_rail import GroqRail
from groq_compose_ref import conformance
for row in conformance(lambda **kw: GroqRail(**kw)):
    print(row["id"], "PASS" if row["ok"] else "FAIL", row["detail"])
```

If the live satellite already satisfies I3–I7 — likely, given it passed its gate — the attach is all that is missing and §2 is the whole change. If it does not, the harness names which one, and the harness is itself proved able to fail: the suite runs it against a deliberately permissive rail and asserts it goes red.

---

## 10. Open questions I could not close from this clone

1. **Which tier is the live key on?** Everything above assumes free/developer and fails closed. An enterprise committed-spend key legitimately keeps `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`.
2. **Does the live satellite expose `probe()`/`dispatch()`, or `ask()` like the `bts_*` incumbents?** If `ask()`, the attach wraps it in a `NodeRail`-style shim and nothing else in this proposal changes.
3. **What shape is the live `boot_compose` block?** One attach call per rail (the firecrawl/cursor shape I assumed) or one combined `register_*_rails()`. The signature mirrors `register_node_rails` so either lands.
4. **Where does the live tree resolve the key?** Environment, `config/secrets`, or the `.secrets` file `cosmos_port_plan` names for `bts_cursor`.
5. **Own budget or shared ceiling?** It holds its own `$5` cap here, which makes it a separate row in `spend.audit()`. Sharing the model-rail ceiling is a one-line change and a different policy question.
6. **Is `firecrawl` a `DOM`-type or `API`-type link?** If firecrawl registered itself with a positive `policy_rank`, the DOM-first ordering may already be compromised tree-wide, and that is worth a look independent of this work order — `grep -n "policy_rank" cosmos/*.py` in the live tree settles it.
