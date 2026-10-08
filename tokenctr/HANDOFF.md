# HANDOFF — Grok47 apply guide

*Everything needed to take this module from files-on-disk to live. Read top to bottom, execute in order. No decisions left open except the ones marked KEITH.*

---

## 0. What this is

**TokenCenter** — the COSMOS payment engine: gateway, meter, credits, toll curve, entitlement, Founding offer. The money model is `02_THE_FORMULA.md`; the offer is `04_LAUNCH.md`; the deploy is `10_RUNPOD_DEPLOY.md`. This file is the *apply order*.

**House rules (violating any of these is a launch-blocking bug):**
- Fail-closed: missing secrets refuse; quota/balance checks deny before the call
- Provenance on every number: `estimate | measured | billed` — estimates never bill
- UNPRICED ≠ zero
- Privacy structural: no content in meter events (the validator rejects it)
- No echo: keys/card data never in logs, errors, responses, git
- One ledger: dashboard = meter DB = statement

---

## 1. Files (what each is)

```
cosmos_pay_config.py       paths, config, secrets (fail-closed, auto-discovery)
cosmos_pay_toll.py         Lane B brackets + statement fold
cosmos_pay_pricing.py      min(OR − ε, 5× COGS) + recompute  ← THE WIN-WIN-WIN JOB
cosmos_pay_meter.py        cosmos-meter/1 events, SQLite, thread-safe, idempotent sync,
                           account-filtered queries (privacy), idempotent account hashing
cosmos_pay_entitlement.py  SEED-MAC token: mint/verify/grace
cosmos_pay_runpod_rail.py  RunPod serverless adapter (runsync + SSE + health)
cosmos_pay_vertex_rail.py  Google Cloud Vertex AI adapter (Gemini streaming + exact tokens)
cosmos_pay_processors.py   registry + Stripe/PayPal adapters + BankProc stub
cosmos_pay_founding.py     Founding engine: 500 cap, two-tier grants
cosmos_pay_webhooks.py     processor-agnostic receiver (verify-first, idempotent, raw body)
cosmos_pay_gateway.py      api.cosmos…/v1 — ALL endpoints (chat + UI API), account-
                           filtered queries, rate-limited, CORS-enabled, SSE streaming
cosmos_pay_cloudflare.py   Cloudflare server-side: DNS, Zone, Turnstile, Edge IP & headers
cloudflare_worker_tokenctr.js Cloudflare Edge relay, edge caching, edge rate limit
cosmos_pay_nightly.py      nightly COGS/price recompute + monthly toll
cosmos_pay_smoke.py        offline self-test (fresh-machine safe) + live gateway test
cosmos_pay_wizard.py       BYOK wizards (OR / Google / Bedrock)
install.ps1                fresh-machine installer
models.seed.json           the starter registry (copy → models.json)
tests/                     12 suites, 190 checks — ALL MUST PASS before any deploy
```

---

## 2. Apply order

### Step 1 — Verify the baseline (no config needed)
```
py -3 tests\test_pay_toll.py
py -3 tests\test_pay_pricing.py
py -3 tests\test_pay_meter.py
py -3 tests\test_pay_entitlement.py
py -3 tests\test_pay_founding.py
py -3 tests\test_pay_webhooks.py
py -3 tests\test_pay_gateway_integration.py
py -3 tests\test_pay_privacy.py
py -3 tests\test_pay_cloudflare.py
py -3 tests\test_pay_bulletproof.py
py -3 tests\test_pay_money_safety.py
py -3 tests\test_pay_vertex_rail.py
```
**All must exit 0 (190 checks).** If any fail: STOP — report, do not patch silently.

**Audit record (2026-09-30 bulletproofing pass):** the audit found and fixed —
(1) a cross-account privacy leak (logs/export/statement/usage returned ALL accounts' events;
now account-filtered, regression-tested in `test_pay_privacy.py`);
(2) a double-hash mismatch between the store's account_hash and meter events (hash_account now idempotent);
(3) the Stripe raw-body signature bug in gateway.py (re-serialized JSON broke live webhook verify;
now passes exact raw bytes over the wire);
(4) the founding double-grant ($30 face for $10);
(5) the free-core expiry bug;
(6) SQLite thread-safety on the gateway path;
(7) PayPal webhook bytes/headers type mismatch resolved in processors & webhooks router;
(8) CORS preflight OPTIONS + headers added to gateway for browser portal on tokenctr.com;
(9) Key daily cap enforcement (/v1/keys/cap) and sliding window rate limiting;
(10) Server-side Cloudflare zone/DNS automation + Turnstile verification in `cosmos_pay_cloudflare.py`;
(11) Edge Worker script `cloudflare_worker_tokenctr.js` for edge caching & proxying.
(12) Gateway starts with unconfigured RunPod rail (503 no_supply, no startup crash);
(13) `POST /v1/meter/ingest` batch sync endpoint (idempotent, per-event validation);
(14) Stripe/PayPal/RunPod transport errors wrapped as ProcessorError/RailError (no raw 500s);
(15) Rate-limiter memory pruning, founding status lock, toll/meter/entitlement malformed-input hardening.
(16) Founding grant atomic under an RLock (check+slot+grant+plan) — concurrent
double-grants refuse; `Store.lock` is now reentrant.
(17) `POST /v1/meter/ingest` stamps the caller's account — keys cannot write
another account's book.
(18) Stripe `amount_total` / `amount_refunded` guarded as `BAD_PAYLOAD` (no raw 500s).
(19) Model reload runs after auth on `chat` / `chat_stream`.
(20) Streams without a usage block settle `RUN_UNPRICED` with full refund —
estimates never bill as measured. New suite `test_pay_money_safety.py` (14 checks).

### Step 2 — Configure (Keith's values, never yours)
Create `%USERPROFILE%\.cosmos_pay\secrets.json`:
```json
{ "runpod_api_key": "<Keith pastes>",
  "runpod_endpoint_id": "<after the endpoint deploys>",
  "mesh_hmac_key_hex": "<python -c \"import secrets;print(secrets.token_hex(32))\">",
  "setup_key": "<random — gates /v1/account/create>",
  "stripe_secret_key": "<when Stripe is live>",
  "stripe_webhook_secret": "<when the webhook endpoint is registered>",
  "paypal_client_id": "", "paypal_client_secret": "" }
```
Copy `models.seed.json` → `models.json`. Fill the RunPod endpoint id after step 4.

### Step 3 — Deploy the supply endpoint (10_RUNPOD_DEPLOY.md §9)
RunPod account → network volume (US-East) → FP8 weights → worker image (vLLM + handler, the `runpod-workers/vllm` pattern) → serverless endpoint (max-workers 4, queue timeout 60s) → direct smoke via the RunPod console.

### Step 4 — Start the gateway + smoke
```
py -3 cosmos_pay_gateway.py
py -3 cosmos_pay_smoke.py --live --key <key from /v1/account/create> --url http://127.0.0.1:8787
```
Then the REAL smoke: one genuine coding task through the work-order pipeline → 4C grades it → receipt in the logs → `RUN_SETTLED` in the meter.

### Step 5 — Nightly job
```
py -3 cosmos_pay_nightly.py            # prices (reads utilization.json if present)
py -3 cosmos_pay_nightly.py --toll 2026-10
```
Schedule it (schtasks, the house pattern — Windows carries the overhead).

### Step 6 — Founding offer live
Processor webhooks registered (Stripe: the endpoint URL + whsec into secrets) → `/v1/founding/purchase` returns a real checkout URL → the webhook grants the tier → **in the stream.**

---

## 3. Definition of done

- [ ] All 7 test suites exit 0
- [ ] Gateway serves /healthz, /v1/models, /v1/chat/completions
- [ ] One measured `RUN_SETTLED` from the manufactured rail
- [ ] Free-tier 429 carries the Founding offer (machine-readable)
- [ ] Webhook signature verify passes on raw bytes through the real HTTP layer
- [ ] Founding cap enforced (sold-out refuses)
- [ ] Nightly job recomputes prices; the dashboard shows the new price

---

## 4. The do-NOT list

1. **No secrets in git, logs, errors, or responses** — `live/config/` only, referenced by filename
2. **No content in meter events** — the validator rejects it; do not bypass
3. **No silent downgrades** — tampered entitlements/tokens refuse loud
4. **No estimates billed** — provenance `measured`/`billed` only
5. **No new payment method without a webhook** — no webhook, no checkout
6. **No feature gates on the essentials** — the core never gates, in every state
7. **No pricing changes outside the rule** — `min(OR − ε, 5× COGS)` + the bracket table; the Win-Win-Win split is policy, recomputed from COGS

---

## 5. Known gaps (v1.1 — do not improvise at launch)

- OAuth subscription-riding (Codex/Grok/Copilot/Qwen) — diff Hermes `hermes model` handlers
- Free-proxy multi-account key-pool rotation — wire the in-tree fill_first
- BankProc adapter — waits on the Commercial Bank & Trust processor rates email
- LiteLLM adoption — when rails > ~5
- Venmo — via Braintree, when the vibe-coder segment arrives
- SSE streaming relay hardening (backpressure, mid-stream disconnect)
