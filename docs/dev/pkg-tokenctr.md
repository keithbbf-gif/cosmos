# Token Center

COSMOS is not finished, and this page is not a completion claim. Token Center
is the pay package at `V:\A\Ai\COSMOS\tokenctr` (`pyproject.toml` name
`tokenctr`). It is a stdlib gateway, two SQLite books, and a set of supply
rails. It is not a finished multi-provider resale desk. A green checker does
not change that.

The package README says the direct-run scripts are complete. `HANDOFF.md`
section 3 still has its definition-of-done boxes unchecked. Read the code and
the boxes, not the word "complete."

Nothing under `cosmos/` imports `cosmos_pay`. This package does not import
`cosmos_spend`. Core stays on its own port. Do not restart port 8770 to work
on Token Center.

## What a reader can run

Python 3.11 or newer. No third-party runtime. Optional dev tools are pytest,
ruff, and mypy. The gateway process is `py -3 cosmos_pay_gateway.py` from the
package directory. Default listen address is `127.0.0.1:8787` in
`cosmos_pay_config.py` (`gateway.host`, `gateway.port`). That is not Core's
serve port.

`install.ps1` is a manual Windows installer. It creates the pay root and
copies modules. Running it, or not running it, is not a launch.

There is no buyer GUI in this package. `cosmos_pay_wizard.py` is the CLI
client. Its docstring defers cDeck panels to a later GUI. `builds/cdeck` does
not call this package and does not sell credits.
`cloudflare_worker_tokenctr.js` is an edge proxy script, not a desk.

## Modules

| File | Role |
|---|---|
| `cosmos_pay_config.py` | Pay root, `config.json`, `models.json`, secrets load. |
| `cosmos_pay_gateway.py` | HTTP surface, `Store` (`keys.db`), rail dispatch. |
| `cosmos_pay_meter.py` | `meter.db`, schema `cosmos-meter/1`. |
| `cosmos_pay_vertex_rail.py` | Vertex adapter. Attaches only when configured. |
| `cosmos_pay_bedrock_rail.py` | Bedrock adapter. Does not sign. |
| `cosmos_pay_openrouter_rail.py` | OpenRouter adapter. Unset stays unset. |
| `cosmos_pay_azure_rail.py` | Azure adapter. Unset stays unset. |
| `cosmos_pay_runpod_rail.py` | RunPod adapter. Default only for rail `runpod` or an omitted rail. |
| `cosmos_pay_pricing.py` | Manufactured price rule and pass-through surcharge. |
| `cosmos_pay_toll.py` | Lane B marginal brackets. |
| `cosmos_pay_nightly.py` | Rewrites `models.json` prices; optional monthly toll fold. |
| `cosmos_pay_entitlement.py` | HMAC entitlement token. Not a database row. |
| `cosmos_pay_founding.py` | Cap, plan, face grant. Meter emit is a later commit. |
| `cosmos_pay_processors.py` | Stripe, PayPal, and a BankProc stub that always refuses. |
| `cosmos_pay_webhooks.py` | Verify-first receiver. Idempotency is `webhooks.db`. |
| `cosmos_pay_wizard.py` | BYOK CLI. Bedrock check is format-only. |
| `cosmos_pay_cloudflare.py` | Zone, DNS, Turnstile helpers. |
| `cosmos_pay_smoke.py` | Offline self-test and an optional live gateway probe. |
| `gcp_billing_breaker.py` | Cloud Function sketch. Not wired to the gateway or to SpendGate. |
| `models.seed.json` | Starter registry. Copy is the operator's `models.json`. |
| `tests/` | Direct-run pay scripts, plus a subprocess wrapper. |
| `V:\A\Ai\COSMOS\tests\test_tokenctr_rails.py` | Dispatch tests. Fakes only. No vendor network. |

`HANDOFF.md` in the package is an apply order, not a second architecture.
Upstream formula and deploy notes it names are not this chapter.

## Pay root

`COSMOS_PAY_ROOT` overrides the root. The default is `~/.cosmos_pay`.

| Path | Holds |
|---|---|
| `config.json` | Host, port, free-tier face, toll brackets, pricing eps and cap, founding numbers. Not secrets. |
| `models.json` | Supply registry. Absent or empty is legal. Chat then has nothing to route. |
| `keys.db` | Accounts, key hashes, plan, `credits_face_usd`, daily counters, settings, founding slot count. |
| `meter.db` | Meter events. |
| `secrets.json` | Key material. Never in git. Never in this book. Never echoed in logs, errors, or responses. |
| `webhooks.db` | Processor event ids already claimed. Not the credit balance and not the meter. |

`load_secrets` refuses when a required field is missing or empty. This page
does not list values, show a template, or name a vault file. Do not paste
secrets into a doc, a test fixture that is committed, or a meter event.

Mesh API keys are stored as SHA-256 hashes. A newly issued key is returned
once. Later account views show a truncated hash, not the key.

## Two databases, not one transaction

`keys.db` and `meter.db` are two connections and two commits. They are not
one transaction. They are not Core SpendGate.

`Store` in `cosmos_pay_gateway.py` opens `keys.db` with WAL and an `RLock`.
`credits_face_usd` is a mutable column on `accounts`. `reserve` subtracts a
worst-case face amount and commits. `settle_refund_unused` adds back
`reserved - measured` and commits. `grant` adds face and commits. Nothing in
this package rebuilds `credits_face_usd` by folding `CREDIT_*` events minus
draws. A meter row is not the balance. A balance is not the meter.

`Meter` opens `meter.db` with its own lock. `emit` validates, then
`INSERT OR IGNORE` on `event_id`, then commits. Replay of the same
`event_id` does not add a second row. The meter rejects content keys
(`prompt`, `messages`, `output`, and the rest of `FORBIDDEN_KEYS`) at any
depth. Account ids are stored as `h:` plus a hash. An id that already starts
with `h:` is kept, so the store hash and the meter account can match. Prompts
stay out of the meter.

`PayGateway.chat` can commit the credit settle and then call `meter.emit`.
`MeterError` on that path is swallowed. The call can succeed with a debit
and no meter row, or the process can die between the two commits. Either
shape is a split book. Do not "fix" it by binding both writes to SpendGate
in the same change. A later single-transaction design needs a crash between
the two writes, on a temp database, before anyone treats them as one book.

`Founding.grant` holds `store.lock` across the slot, the face grant, and the
plan update, and commits `keys.db`. It then emits `CREDIT_GRANTED` on
`meter.db` outside that lock. The cap check is atomic with the grant. The
meter line is not.

Webhook routing does the same split. Signature verify runs on the raw body
before any grant. `checkout.session.completed` calls `store.grant` and then
`meter.emit`, or emits `CREDIT_PURCHASED` and then `Founding.grant` (which
emits again). `webhooks.db` commits the idempotency claim on its own
connection. Three files, three commits. A duplicate delivery is a no-op only
after the claim lands.

`POST /v1/credits/purchase` with neither a Stripe secret nor a PayPal client
id returns 503 `no_processor`. The click does not grant credits. The webhook
does, after verify. `BankProcAdapter` raises `UNSUPPORTED` until a processor
exists. No webhook, no checkout.

## Not Core SpendGate

Core SpendGate is `cosmos/cosmos_spend.py`. It fences mesh spend on the Core
ledger. Token Center spends `credits_face_usd` and appends `meter.db`.

`Store.reserve` says it mirrors SpendGate and that the on-tree code should
bind SpendGate directly. That sentence is a comment. There is no import and
no call. A comment is not a bind.

The recorded chair is `DO_NOT_BIND` in `docs/modules/JURY_SPENDGATE.md`
(2026-10-08: 3 `DO_NOT_BIND`, 1 `BIND_READ_ONLY`, 1 `BIND_NOW`). Do not merge
`credits_face_usd` with `meter.db`. Do not let both wallets deny the same
run. Do not debit, reserve, or treat a missing Token Center purchase as a
Core deny. If a later verdict allows a bind, Core's spend chain stays the
mesh authority and `meter.db` is a projection deduped on `event_id`. Until
that verdict is recorded, they stay apart.

`gcp_billing_breaker.py` describes a Google billing alert function. The
gateway does not import it. It is not SpendGate.

Entitlement tokens (`cosmos_pay_entitlement.py`) are local HMAC tokens, not
rows in either database. A bad MAC refuses. This page does not show a key or
a mint example.

Lane B toll is a fold of meter events in `cosmos_pay_toll.py`. It is not a
third wallet. Manufactured price is `min(OR retail minus eps, cap multiple
times COGS)` in `cosmos_pay_pricing.py`. Pass-through rows use a surcharge.
The nightly job rewrites `models.json`. The running gateway hot-reloads that
file when the mtime changes. A price card is not proof a rail can serve.

## Rails

`attach_rails` builds four objects from config and secrets. A missing field
leaves that object `None`. `main` always passes the dict into `PayGateway`.
The RunPod object is separate. It is built from the RunPod endpoint id and
API key. If those are missing, `RunPodRail` raises and `main` substitutes a
stub. Named rails are not that stub.

`PayGateway._resolve_rail` is the dispatch rule. Tests in
`tests/test_tokenctr_rails.py` lock it.

| Model field `rail` | Object used | RunPod |
|---|---|---|
| `vertex` | `vertex_rail` | Not called, even when the object is `None`. |
| `bedrock` | `bedrock_rail` | Not called. |
| `openrouter` | `openrouter_rail` | Not called. |
| `azure` | `azure_rail` | Not called. |
| `runpod`, or the field omitted | `self.rail` (the RunPod object or the startup stub) | This is the only fall-through, and only for these two cases. |
| Any other name, including `google` | `None` | Not called. |

A missing named rail is HTTP 503, body `error.code` = `no_supply`, message
`rail '<name>' is not configured`. No meter event. If a reserve already
happened, it is refunded before that return. Stock `PayGateway` leaves the
four named objects `None`, so a registry row whose `rail` is one of those
four names takes this path as soon as the row is eligible.

Attach rules, all fail-closed. None of them open a key file at attach time.

| Rail | `from_config` returns an object only when |
|---|---|
| Vertex | A project id (`vertex.project_id` or `vertex_project_id`) and a credential (access token or API key on the `vertex` block or in secrets). |
| Bedrock | Both a key and an endpoint. |
| OpenRouter | Both a key and an endpoint. |
| Azure | Both a key and an endpoint. |

One field without the other stays `None`. Empty config attaches nothing.

There is a second 503 before dispatch. `_model_entry` treats a model as
absent unless the registry row exists and `endpoint` is non-empty. The
message is `model '<id>' not in the registry`, still `no_supply`. Seed rows
`gemini-flash-vertex` and `claude-sonnet-bedrock` have a `rail` and no
`endpoint`, so stock chat returns that 503 and does not call RunPod.
`qwen3-coder-30b-fp8` is `rail: runpod` and has a placeholder `endpoint`
string, so it passes this gate and uses the RunPod object. The model
`endpoint` string is the gate and the meter rail label. It is not the RunPod
URL. RunPod's URL comes from the rail's own endpoint id.

Vertex, once attached, calls its own `runsync`. If the object is not
configured it raises `VertexNoSupply` (`no_supply` true). The gateway maps
that to the same 503 and does not bill it as `RUN_FAILED`. Stock `from_config`
does not load a service-account file and does not call the network.
`GoogleOAuthTokenProvider` can sign with a local OpenSSL binary when a caller
constructs it. `attach_rails` does not construct it. That helper is not a
Bedrock signer.

### Bedrock does not sign

`cosmos_pay_bedrock_rail.py` stores a secret for a later signer. This pass
does not sign and does not call AWS. There is no SigV4 implementation and no
default network transport. `runsync` raises `NoSupply` unless a key, an
endpoint, and an injected transport are all present. The gateway maps
`NoSupply` to 503 `no_supply`, refunds any reserve, and writes no meter
event. An attached Bedrock object with no injected transport is still
`no_supply`. It is not RunPod.

`cosmos_pay_wizard.py` `test_bedrock` is a format check only. It does not
call the rail and it does not call SigV4. A wizard "pass" does not mean
Bedrock can serve chat.

OpenRouter and Azure, unlike Bedrock, will `urllib` POST when a key and an
endpoint are set and no transport was injected. That is a live call. Leave
them unset unless an operator has chosen to configure them. Dispatch tests
block the network. Unset rails do not fall through to RunPod.

The startup stub for a missing RunPod endpoint is different. It raises
`RailError`, not `NoSupply`. `chat` then refunds, emits `RUN_FAILED`, and
returns 502 `rail_error`. The `main` print that says the gateway serves 503
until the endpoint lands does not match that path. Named-rail `no_supply` is
503. The RunPod stub is 502. Do not paper over that by sending the named
rails at the stub.

On a real settle, `chat` reserves worst case for a paid balance, calls
`runsync`, and bills measured tokens times `price_per_m_usd`. Provenance
`measured` requires `measured_usd`. An `unpriced` usage block emits
`RUN_UNPRICED`, refunds the reserve, and does not bill the estimate as
measured. Free plan with a zero balance uses the daily face cap instead of
`credits_face_usd`. Estimates are the reserve bound only.

`models.seed.json` has no OpenRouter row and no Azure row. Vertex and Bedrock
rows are pass-through notes without endpoints. Stock chat does not resell
those providers.

## What a green checker is

Run pay scripts as programs from the package directory, for example
`py -3 tests\test_pay_toll.py`. Those modules call `sys.exit` at import. Do
not import them into another process. `tokenctr/tests/test_suites_pytest.py`
runs them in subprocesses so a collector does not die on the first script.
Rail dispatch is `tests/test_tokenctr_rails.py` at the repo root. It uses a
temp `COSMOS_PAY_ROOT` and does not open a live `secrets.json`.

The package README's "190/190" is that direct-run script count, as claimed
by the README. It is not the unchecked boxes in `HANDOFF.md` section 3. It
is not a configured Vertex, Bedrock, OpenRouter, or Azure resale path. It is
not a single transaction across `keys.db` and `meter.db`. It is not a
SpendGate bind. Checker green is not a finished resale desk.

Still out of this package, by its own README and `HANDOFF.md`: OAuth
subscription riding, multi-account key pools, a merchant-of-record webhook,
BankProc, streaming backpressure, and ModelRater or research rollups on the
meter. Do not improvise those into a "finished" claim.

## What not to do

- Do not describe Token Center, or COSMOS, as finished.
- Do not paste `secrets.json`, key bytes, webhook secrets, or a filled
  template into git, logs, errors, or this book.
- Do not put prompts or other forbidden content keys into a meter event.
- Do not route `vertex`, `bedrock`, `openrouter`, or `azure` to RunPod when
  the named object is missing. 503 `no_supply` is the correct refusal.
- Do not treat a Bedrock format check, a stored AWS secret, or an attached
  rail with no transport as a signed Bedrock call.
- Do not merge `keys.db` and `meter.db`, and do not bind either one to Core
  SpendGate, until a later recorded verdict says otherwise.
- Do not read `credits_face_usd` as a fold of the meter, or a meter total as
  the credit balance. They commit separately and can diverge.
- Do not take a passing script, ruff, or mypy run as a resale launch.
- Do not restart Core on port 8770 for this package.
