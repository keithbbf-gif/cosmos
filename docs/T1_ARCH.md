# T1 ARCH — gbridge: synchronous GrokBot-team ⇄ COW tool

**Stage:** Motif 6 runtime-binding (satellite). **Authors:** F5 (arch) · G46 (code + gate). **Date:** 2026-08-25 / gated 2026-08-26.
**Inputs:** `docs/research/T1_SYNC_GBOT_COW/research_{grok,openai,gemini}.md` (vendor-plural,
all three families returned; no mid-run failures to report).

---

## 1. Decision rubric (stated first, per Motif stage 2)

A candidate surface is scored against these, in priority order:

- **R1 — Identity.** Does the call reach the *actual persistent grok.com team* (its memory,
  files, configuration), not merely a Grok model behind the same brand?
- **R2 — Synchronous at COW.** One blocking call returns a structured answer **or a typed
  refusal**. No silent waits, no "check the file later."
- **R3 — Supported surface only.** Documented endpoints and mechanisms we own. No cookie
  replay, no headless-browser automation of grok.com, no guessed `team_id` endpoints —
  Motif rule: *write UNKNOWN rather than guess*.
- **R4 — Canon fit.** The primary path must depend on **nothing that can run out** (no
  credit, quota, key expiry) — the DOM-first principle applied to transports. Fail-closed
  with visible typed refusals. No hard-coded paths — one root, handed in. Installable by a
  peer on a cold machine.
- **R5 — Buildable today.** The smallest slice must run against what already exists (the
  file mailbox exists; the team already reads/writes files).
- **R6 — Swap-ready.** If xAI ships a real Teams/Agents API, swapping it in must not change
  COW's call site. Transport is an injected interface, the ask() surface is the contract.

## 2. Research consensus (asserted before reasoning — packets contain what they claim)

All three families independently conclude:

| Question | grok | openai | gemini |
|---|---|---|---|
| Public API addressing a persistent grok.com team | **UNKNOWN / almost certainly no** | **not documented** | **not exposed** |
| Documented synchronous path | `POST api.x.ai/v1/chat/completions` (model, not team) | same | same |
| Honest sync-to-team architecture today | blocking facade over the mailbox | shim/bridge | shim service over the mailbox |
| Browser automation of grok.com | brittle, ToS risk | "not recommended" | "highly discouraged" |

No disagreement to put on the board — **no CONTESTED item**. The one open watch-item:
re-check https://docs.x.ai and xai-org GitHub periodically for a Teams/Agents API; if it
ships, it becomes a third transport (see R6).

## 3. Decision — the chosen integration surface

**Build `gbridge`: a synchronous ask() facade with injected transports.**

```
COW ──(blocking call / CLI, later MCP)──> GBridge.ask(text, timeout)
                                             │  Transport (injected)
                       ┌─────────────────────┼──────────────────────┐
                 MailboxTransport      XaiApiTransport        (future: TeamsApiTransport
                 PRIMARY — real GBt    FALLBACK — Grok model,   when xAI documents one)
                 identity via files    NOT team identity
```

- **COW's surface** is one blocking call: `ask(text, context, timeout_s)` → structured
  `Answer` or a **typed refusal** (`TIMEOUT`, `TORN_REPLY`, `BAD_STATUS`, `ROOT_MISSING`).
  Sync at the orchestrator. That is the contract; everything behind it is swappable (R6).
- **Primary transport — `MailboxTransport`** (R1, R4, R5): a dedicated request/reply file
  mailbox under **one handed-in root** — `to_gbot/` and `from_gbot/`. gbridge writes an
  immutable request file (atomic tmp→replace, send-side read-back, sha256 — `cosmos_mail`
  scar lineage) and **blocking-polls** for the matching reply until a hard deadline.
  Synchronous at COW, still asynchronous at grok.com — grok's research names this "the
  honest architecture until an Agents API appears." It reaches the *real* team (the team
  keeps its persistent identity and simply answers files, as it does today), and files
  depend on nothing that can run out.
- **Fallback transport — `XaiApiTransport`** (R2 fully, R1 no): documented
  `POST https://api.x.ai/v1/chat/completions`, true sync, same Grok *model family* but a
  fresh session — explicitly **not** the team. API-second, per canon. Present in slice 1 as
  a non-networked stub; wired live only when Keith provides the key.
- **Rejected:** browser automation of grok.com (fails R3, unanimous across families);
  guessed teams endpoints (R3); touching `cosmos/` core (hard rule — gbridge is a
  standalone tool under `builds/`, promoted only through the normal pipeline).

## 4. Auth

- **MailboxTransport:** filesystem only. The mail root is install-configured and handed in
  (no drive literal, no fallback ladder). No secrets in request/reply files, ever.
- **XaiApiTransport:** `Authorization: Bearer $XAI_API_KEY`, read from the **environment**
  at call time — never from repo, config file, or CLI argument. Keith does credentials.

## 5. Request/response wire shape (versioned, `"gbridge": 1`)

Request — `to_gbot/<request_id>.json`, immutable, atomically installed:

```json
{
  "gbridge": 1,
  "request_id": "1756150000000-a1b2c3d4e5f6",
  "from": "COW", "to": "GBOT",
  "epoch": 1756150000.0, "utc_offset_s": -21600,
  "text": "Review builds/gbridge for X...",
  "context": "optional supporting material",
  "timeout_s": 120,
  "body_sha256": "<sha256 of text>"
}
```

Reply — `from_gbot/<request_id>.json`, written by the team (its project instructions gain
one line: *answer request files in `to_gbot/` by writing this shape to `from_gbot/`*):

```json
{
  "gbridge": 1,
  "request_id": "1756150000000-a1b2c3d4e5f6",
  "status": "ok",
  "answer": "…the team's structured answer…",
  "body_sha256": "<sha256 of answer>"
}
```

`status ∈ {ok, needs_input, blocked, error}` (OA research enum). Validation is fail-closed:
version must be 1, `request_id` must match both filename and field, hash must verify,
status must be in the enum. Because the bot's write may not be atomic, a reply that does
not yet parse/verify is treated as **"not yet"** until the deadline; at deadline, a present
-but-invalid file is `TORN_REPLY`, absence is `TIMEOUT`. On timeout the request file is
left in place — a late reply remains collectible (slice 2: `collect` verb); the refusal is
still raised, visibly. Refusals are correct behavior, not faults to route around.

## 6. Smallest buildable slice (this is what CODE builds now)

`builds/gbridge/` — standalone, zero third-party deps, Python 3.14 stdlib only:

1. `gbridge.py` — one module (repo spike style): wire-shape dataclasses, `Transport`
   protocol, `MailboxTransport` (real, filesystem), `XaiApiTransport` (stub, refuses
   without key; live wiring deferred), `GBridge.ask()` with deadline + typed refusals,
   and a CLI: `ask` (blocks on the mailbox) and `selftest` (loopback transport — proves
   the slice runs with **no external network** and emits a live value only the running
   code can produce: the round-tripped sha256).
2. `test_gbridge.py` — repo-style selftest: happy path via injected fake transport,
   mailbox round-trip in a temp dir (filesystem only, no network), and each refusal
   asserted **by kind**.
3. `README.md` — run lines.

Not in this slice (deferred, in order): MCP wrapper exposing `gbridge_ask` as a native COW
tool (thin layer over the same `GBridge`), the `collect` verb for late replies, live
`XaiApiTransport`, ledger-recorded ask/answer facts once gbridge is promoted toward Core.

CLI verbs now: `ask`, `selftest` (loopback green log), `gate` (stage-6 mailbox + sentinel).

---

## 7. Stage-5 critique (gem-api) → additive fixes kept

Source: `docs/critique/gbridge_CRITIQUE_gem-api.md`. HIGH/MED applied without
removing any slice-1 feature (`ask`, `selftest`, MailboxTransport, XaiApiTransport
stub, LoopbackTransport, typed refusals, fail-closed validation).

| sev | finding | additive fix |
|---|---|---|
| HIGH | `poll` can observe a bot mid-write (`write_text` not `os.replace`) | `poll` treats present-but-unparseable as "not yet" until deadline; deadline pass retries `_FINAL_PARSE_ATTEMPTS`; `write_reply()` is the atomic bot-side install (tmp→`os.replace`). Tests: `MidWriteBot`, `EmptyReplyBot`, `TornBot`. |
| MED | `GBridgeError.kind` was an untyped `str` | `RefusalKind` `StrEnum`; unknown kinds (`TIME_OUT`) fail-closed at construction. `kind == "TIMEOUT"` still holds. |
| MED | `ask` duplicated `_validated` (loop vs final) | single `_poll_validated` path for both. |
| MED | `body_sha256` name vs hashed field | documented + tested: hash of `text` (request) or `answer` (reply), not the JSON document. Send-side read-back compares that field hash. |
| LOW (applied) | `_now` used `time.timezone`+`tm_isdst` | `datetime.now().astimezone().utcoffset()`. |
| LOW (applied) | filename vs field `request_id` | `_parse_reply` requires `p.stem == field == ask.request_id`. |

Loopback `selftest` remains. It is a green log. It is not stage 6.

## 8. Stage-6 runtime-binding gate

`py -3.14 builds\gbridge\gbridge.py gate --root builds\gbridge\mail --live-root <runtime-root>`

The gate:

1. Reads the handed-in runtime sentinel (`.cosmos-root.json`). Missing / wrong
   `system` is a typed refusal — existence is not identity.
2. Hashes **the executing** `gbridge.py` (`Path(__file__)`).
3. Runs the **PRIMARY** mailbox (`MailboxTransport` + atomic `write_reply`), not
   LoopbackTransport, under `--root/happy`.
4. Negative control: empty mailbox under `--root/timeout` → `TIMEOUT`, request
   file left in place.
5. Writes `builds/gbridge/STAGE6_GATE.json` (and a copy beside the happy mailbox).

**Proof is `STAGE6_GATE.json` `live_value` / `emitted`.** `rc=0` is not the gate.
A loopback sha256 of the constant `"gbridge selftest"` is computable without this
tree; the gate's `emitted` is `gbridge:<tree_id>:<request_id>:<nonce>:<source_sha256>`
and the matching request/reply files on disk. An older snapshot that lacked
`write_reply` / `RefusalKind` / this gate cannot mint that record.

Quoted from a host-side re-read of `builds/gbridge/STAGE6_GATE.json` after
`py -3.14 builds\gbridge\gbridge.py gate --root builds\gbridge\mail --live-root V:\A\Ai\COSMOS\live`
(G46, Motif `motif_gbridge_s6`). Independent `sha256` of `builds/gbridge/gbridge.py`
and of the request/reply files matched the record. `rc=0` is not this table.

| field | live-tree value |
|---|---|
| **proof artifact** | `builds/gbridge/STAGE6_GATE.json` |
| **emitted** | `gbridge:KMesh-COSMOS-live:1787757729249-fb3b039745fc:2c62f031fd3e4be39e867847c1e22607:e3ee1134e65065c99a9f1077af5a3dd18de72b3dcf9ec54d8dec4db72ff323cd` |
| `live_tree_id` | `KMesh-COSMOS-live` (from `live/.cosmos-root.json`) |
| `request_id` | `1787757729249-fb3b039745fc` |
| `nonce` | `2c62f031fd3e4be39e867847c1e22607` |
| `source_sha256` | `e3ee1134e65065c99a9f1077af5a3dd18de72b3dcf9ec54d8dec4db72ff323cd` (`builds/gbridge/gbridge.py`) |
| `answer` | `gate:905c2ebfae49cc6f9acd7ba2be824735678f063d2deafb99eaa11fb4a15d2f8d:2c62f031fd3e4be39e867847c1e22607` |
| `request_file_sha256` | `956f295d1b86a6b1a937d7040e12165ecd5ac39c12c3ad9d542bc2570636fc2d` |
| `reply_file_sha256` | `5df5922e46c61cea1a88198431e684db54d30de0ee3ef8c522d10d4942166083` |
| timeout leftover | `builds/gbridge/mail/timeout/to_gbot/1787757729252-2375173cd10e.json` (`TIMEOUT`, file left) |

Mailbox files that only this run could write:

- `builds/gbridge/mail/happy/to_gbot/1787757729249-fb3b039745fc.json` (context carries `source_sha256` + `live_tree_id` + `nonce`)
- `builds/gbridge/mail/happy/from_gbot/1787757729249-fb3b039745fc.json`

`utc_offset_s` on this host at gate time: `-18000` (CDT). Python `3.14.0`.
