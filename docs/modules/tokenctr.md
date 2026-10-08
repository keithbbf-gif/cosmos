# Token Center

## What it is

`cosmos_pay`: the Token Center payment-engine copy. Stdlib only (Python 3.11+). It holds a local gateway, a meter buffer, a face-credit balance, a Lane B toll fold, entitlement checks, and a founding cap. Config and secrets stay under `COSMOS_PAY_ROOT` (default `~/.cosmos_pay`): `config.json`, `secrets.json`, `models.json`, `keys.db`, `meter.db`. The default gateway bind in config is `127.0.0.1` port 8787. Meter schema is `cosmos-meter/1`. Pricing for a manufactured model is `price_per_m`: `min(OR retail minus epsilon, 5 times COGS)`. Pass-through uses `passthrough_price`. Provenance on a cost is `estimate`, `measured`, or `billed`. An estimate does not bill. Unknown cost is `RUN_UNPRICED`, not zero.

`Store.reserve` / `settle_refund_unused` change `credits_face_usd` in `keys.db`. `Meter.emit` writes `meter.db` in a later call. Those two writes are not one transaction. This package is not wired to Core `SpendGate`. `gcp_billing_breaker.halt_vertex_rail` is a separate cloud-function sketch, not that wire.

## Where it lives

Repo path: `V:\A\Ai\COSMOS\tokenctr`. Applied 2026-10-08 from `V:\streams\tokenctr\code`. Package name: `tokenctr`. The streams original stays in place. `HANDOFF.md` is the apply guide. It is not a license to treat the README's "190/190" line as the 4C grade below.

## Entry points

Scripts: `cosmos_pay_gateway.main`, `cosmos_pay_nightly.main` (`recompute_prices`, `monthly_toll`), `cosmos_pay_wizard.main` / `run_wizard`, `cosmos_pay_smoke.main` / `offline_self_test`, `cosmos_pay_cloudflare.main`.

Gateway: `PayGateway.chat`, `PayGateway.chat_stream`, `make_handler`, `attach_rails`. Store: `Store.create_account`, `credits`, `reserve`, `settle_refund_unused`, `grant`. Meter: `validate`, `hash_account`, `Meter.emit`, `Meter.tail`. Toll: `toll_usd`, `effective_rate`, `statement_line`. Pricing: `price_per_m`, `passthrough_price`, `recompute_model`, `recompute_models`. Entitlement: `mint`, `verify`, `free_core_claims`, `founding_claims`. Config: `load_config`, `load_secrets`, `load_models`, `write_default_config`. Processors: `StripeAdapter`, `PayPalAdapter`, `BankProcAdapter`. Webhooks: `WebhookRouter`. Founding: `Founding`. Rails: `RunPodRail`, `VertexAIRail`, `BedrockRail`, `OpenRouterRail`, `AzureRail`.

`_resolve_rail` returns the matching object for `vertex`, `bedrock`, `openrouter`, and `azure`. It returns the default rail for `runpod` or a missing rail name. Any other name returns `None`, and `chat` answers 503 `no_supply` with no meter event. That path does not call RunPod. `attach_rails` builds Vertex only when the config has a project id and a credential. It builds Bedrock, OpenRouter, and Azure only when both a key and an endpoint are present. Bedrock stores a secret for a later signer and raises `NoSupply` unless a transport was injected. OpenRouter and Azure can POST through urllib when a key and an endpoint are present and no transport was injected. The dispatch tests blocked the network. Seed rows still lack an endpoint, so stock `chat` returns 503 before a rail runs. This is not a live multi-provider sale.

House tests include direct-run modules (`py -3 tests\test_pay_toll.py` and the other `tests/test_pay_*.py` files). `tests/test_suites_pytest.py` runs twelve of those scripts in subprocesses. That wrapper is the later pytest count. It is not `HANDOFF.md` section 3.

## What it refuses

The COSMOS `live/` tree and a second Core ledger. Pay files stay under `COSMOS_PAY_ROOT`. Missing or empty required secrets raise `ConfigError` (`BAD_SECRET` / `MISSING`). The meter rejects content keys (`FORBIDDEN_CONTENT`), a bad schema (`BAD_SCHEMA`), and a measured cost with no `measured_usd`. Account ids stored on events are hashes from `hash_account`. Key material is not returned by `keys_for` (a short hash prefix only). A failed `reserve` denies before the rail call (`insufficient_credits`). Tampered entitlements raise `EntitlementError` (`BAD_MAC`). Founding enforces its cap. `BankProcAdapter` is fail-closed. The gateway does not echo key material in the response objects it builds for credits and keys.

It does not refuse by folding `credits_face_usd` and the meter into one transaction. That fold is not built. Do not treat the two databases as one book.

## What it is not

Not Core `SpendGate`. Not the Core ledger. Not a live-tree writer. Not an OAuth subscription ladder, and not free-proxy key-pool rotation (both named as later work in the README). Not a claim that `credits_face_usd` and `Meter.emit` already reconcile. The README's direct-run "190/190" count is not this tree's 4C result. Not a finished resale desk. A checker grade does not check the boxes in `HANDOFF.md` section 3.

SpendGate is not bound. The jury record is `docs/modules/JURY_SPENDGATE.md`. Tally: BIND_NOW 1, BIND_READ_ONLY 1, DO_NOT_BIND 3. Chair: DO_NOT_BIND. No merge of `credits_face_usd` and `meter.db`.

## Grade

On main `501fdee2` (2026-10-08): `py_compile` PASS, `ruff` FAIL 379, `mypy` FAIL 34 errors in 21 files, `pytest` exit 3 because the test modules call `sys.exit` at import.

A later package run from `tokenctr`, recorded in `C:\Users\Papa\AppData\Local\Temp\c4-rails2-result.md`, reported `ruff` 0, `mypy` 0 (19 source files), `pytest` 12 passed, and `compileall` 0. A separate run of `tests\test_tokenctr_rails.py` reported 8 passed. A later run of that same file reported 10 passed, including rail `google` and unset Bedrock, OpenRouter, and Azure (`C:\Users\Papa\AppData\Local\Temp\c4-h25-result.md`). That is the checker grade. This note did not re-run it. It is not a finished resale desk.

`HANDOFF.md` section 3 stays open. On the prior read, every box under "Definition of done" was still unchecked (seven empty boxes, from "All 7 test suites exit 0" through the nightly dashboard price). The rails pass did not check those boxes.

The 12 package tests are the subprocess wrappers. The 8 dispatch tests are the rail map: named rails do not fall through to RunPod, missing key or endpoint is 503 `no_supply` with an empty meter, and a fake priced transport can settle face credits without calling RunPod. SpendGate is not bound. The two databases are still separate commits.
