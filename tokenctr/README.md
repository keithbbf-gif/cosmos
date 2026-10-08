Applied 2026-10-08 from `V:\streams\tokenctr\code`. This folder is the copy on the COSMOS tree.

# cosmos_pay — TokenCenter: the payment engine codebase

*Python 3.11+, stdlib only (urllib, sqlite3, hmac, json, hashlib). No pip deps — same rails as COSMOS. Windows-first. **Status: complete, 190/190 checks green — see `HANDOFF.md` for the apply order.***

---

## Modules

| File | What it is | Tests |
|---|---|---|
| `cosmos_pay_config.py` | Paths, config, secrets discipline (fail-closed, auto-discovery) | import-time |
| `cosmos_pay_toll.py` | Lane B declining bracket curve + statement fold | `test_pay_toll.py` 20/20 |
| `cosmos_pay_pricing.py` | `min(OR − ε, 5× COGS)` + nightly recompute + **the sourcing rule in code** (`stocked`/`refer_to_or`) | `test_pay_pricing.py` 16/16 |
| `cosmos_pay_meter.py` | `cosmos-meter/1` events, SQLite (thread-safe), privacy structural, idempotent sync | `test_pay_meter.py` 12/12 |
| `cosmos_pay_entitlement.py` | SEED-MAC token: mint/verify/grace; free core never expires | `test_pay_entitlement.py` 11/11 |
| `cosmos_pay_runpod_rail.py` | RunPod serverless adapter (runsync + SSE stream + health) | integration |
| `cosmos_pay_vertex_rail.py` | Google Cloud Vertex AI adapter (Gemini streaming + exact tokens) | `test_pay_vertex_rail.py` 10/10 |
| `cosmos_pay_processors.py` | Registry + Stripe/PayPal adapters + BankProc stub (fail-closed) | via webhooks |
| `cosmos_pay_founding.py` | Founding engine: 500 cap, two-tier grants ($20 paid / $11 verified) | `test_pay_founding.py` 12/12 |
| `cosmos_pay_webhooks.py` | Processor-agnostic receiver: verify-first on raw bytes, idempotent, refund clawback | `test_pay_webhooks.py` 11/11 |
| `cosmos_pay_gateway.py` | `api.cosmos…/v1` — ALL endpoints: chat, models, usage, account, keys, logs, statement, founding, export, webhooks, settings, credits purchase, CORS, rate-limiting, SSE streaming, multi-rail dispatch | `test_pay_gateway_integration.py` 22/22 |
| `cosmos_pay_cloudflare.py` | Cloudflare server-side: zone verification, DNS automation, Turnstile verification, Edge headers | `test_pay_cloudflare.py` 16/16 |
| `cloudflare_worker_tokenctr.js` | Cloudflare Edge Worker: proxying, edge caching (/v1/models), edge rate-limiting, CORS | edge deploy |
| `cosmos_pay_nightly.py` | The nightly job: COGS/price recompute + monthly toll (**the Win-Win-Win job**) | smoke |
| `cosmos_pay_smoke.py` | Offline self-test (fresh-machine safe) + live gateway test | 9/9 |
| `cosmos_pay_wizard.py` | BYOK wizards: OpenRouter / Google AI Studio / Bedrock (guide → paste → test → save) | manual |
| `install.ps1` | Fresh-machine installer (Python check, modules, config/secrets templates) | manual |
| `models.seed.json` | The starter registry (manufactured + pass-through rails) | — |
| `HANDOFF.md` | **The Grok47 apply guide**: apply order, definition of done, do-NOT list, known gaps | — |
| `tests/` | 12 suites, **190 checks, all green** (incl. `test_pay_privacy.py`, `test_pay_cloudflare.py`, `test_pay_bulletproof.py`, `test_pay_money_safety.py`, `test_pay_vertex_rail.py`) | — |

Run: `py -3 tests\test_pay_toll.py` (direct-run, house style) — or all at once per `HANDOFF.md` §2 step 1.

---

## What pulls from where (upstream map)

| Piece | Upstream source | What we took |
|---|---|---|
| Secrets/config separation | **Hermes Agent** (`~/.hermes/.env` vs `config.yaml`) | secrets.json ≠ config.json; the right value goes to the right file |
| Provider registry shape | **Hermes** provider table (40+ providers, env-var-per-provider, OAuth rows) | `models.json` + the provider ladder in the gateway docs; the OAuth "ride existing subscriptions" step is the v1.1 add (Hermes's `hermes model` OAuth handlers are the reference implementation to diff) |
| Provider-agnostic config | **OpenCode** (75+ providers, Models.dev registry) | model ids as slugs, per-model config block, price/COGS fields |
| Auth-type selection | **Gemini CLI** (Google login / API key / Vertex ADC) | the ladder order in `cosmos setup --mesh`: existing-identity OAuth → our proxy key → BYOK paste |
| Event-sourced fold | **COSMOS tree** `cosmos_ledger.py` | the meter is a tail on the ledger; aggregates are folds, never a second book |
| Reserve→deny→settle | **COSMOS tree** `cosmos_spend.py` | `Wallet.reserve/settle` mirrors SpendGate semantics; on the tree, bind `SpendGate` directly |
| Signed-local-verification | **COSMOS tree** SEED MAC (`hmac.compare_digest`, refuse-loud) | entitlement token mint/verify |
| Fill-first pools | **COSMOS tree** `cosmos_cred_kit.py` | free-proxy key-pool rotation (v1.1 — the proxy v1 runs on a single pool) |
| Response-header quota discipline | **OpenRouter/Groq** | `x-cosmos-quota-remaining/reset`, `x-cosmos-credit-balance` on every response |

---

## Deliberately NOT here yet (v1.1+)

- OAuth ladder (ride Claude/ChatGPT/Copilot/SuperGrok subscriptions) — diff against Hermes's `hermes model` OAuth handlers
- Free-proxy key-pool rotation across multiple OR/Gemini accounts — fill_first exists in-tree; wire it
- MoR webhook receiver (Lemon Squeezy `payment.paid` → entitlement mint) — needs the live MoR account
- Streaming relay hardening (SSE backpressure, client disconnect mid-stream)
- ModelRater aggregation queries (reads the meter DB; schema is stable)
- University research export (aggregated rollups; same shape)

---

## House rules honored

- **Fail-closed:** missing secrets refuse at import; quota/balance checks deny before the call
- **Provenance:** `estimate | measured | billed` on every cost; estimates never bill
- **UNPRICED ≠ zero:** unknown cost holds worst case against the cap
- **Privacy structural:** the meter rejects content keys (`prompt`, `messages`, `output`, …); account ids are hashes; `source_sha` is a hash
- **No echo:** key material never appears in logs, errors, or responses
- **One ledger:** dashboard = meter DB = statement; the reconciliation invariant is testable
