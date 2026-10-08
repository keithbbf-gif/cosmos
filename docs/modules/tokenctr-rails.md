# Token Center rails

Read of `V:\A\Ai\COSMOS\tokenctr` on 2026-10-08, corrected after the rails pass. No live provider calls in the tests. `secrets.json` was not opened for this note.

Rail files on disk: `cosmos_pay_runpod_rail.py`, `cosmos_pay_vertex_rail.py`, `cosmos_pay_bedrock_rail.py`, `cosmos_pay_openrouter_rail.py`, `cosmos_pay_azure_rail.py`.

## What a successful call records

`PayGateway.chat` meters only after `_model_entry` accepts the model. That requires a registry row with a truthy `endpoint`. Otherwise the call is `503 no_supply` and nothing is emitted.

On `runsync` success, measured dollars are `(prompt_tokens + completion_tokens) * price_per_m_usd / 1_000_000`. If `usage.unpriced` is set, the event is `RUN_UNPRICED` and measured tokens are not billed. Otherwise a non-free account (plan other than `free`, or a free plan that still holds credits) settles that amount against the reserve (`settle_refund_unused`). A zero-credit free account does not spend credits; `free_add` books the same figure against the daily face quota. The success event is `RUN_SETTLED` (`cosmos-meter/1`, lane `A`, wallet `cosmos`). Its `rail` field is `entry["endpoint"]`, not the rail name. `chat` and `chat_stream` never emit lane `B`, never set wallet `byok`, and never read BYOK secrets. Lane B toll (`statement_line`) only folds lane `B` events, and nothing in this package emits one.

`_resolve_rail` (`cosmos_pay_gateway.py`):

```python
rail_type = str(entry.get("rail") or "runpod")
if rail_type == "vertex":
    return self.vertex_rail
if rail_type == "bedrock":
    return self.bedrock_rail
if rail_type == "openrouter":
    return self.openrouter_rail
if rail_type == "azure":
    return self.azure_rail
if rail_type == "runpod":
    return self.rail
return None
```

A missing rail name becomes `runpod` and uses the default rail. `vertex`, `bedrock`, `openrouter`, and `azure` return their own objects, including `None`. Any other name, including `google`, returns `None`. `chat` treats `None` as 503 `no_supply` and does not call RunPod.

`main()` still builds `RunPodRail` from `runpod_endpoint_id` / `runpod_api_key`, or `_UnconfiguredRail` if that constructor refuses. It then passes `**attach_rails(config, secrets)`. Vertex attaches when config has a project id and a credential (access token or API key). Bedrock, OpenRouter, and Azure attach only when both a key and an endpoint are present. Bedrock's `runsync` raises `NoSupply` unless a transport was injected. It does not sign. OpenRouter and Azure call urllib when a key and endpoint are present and no transport was injected. The dispatch tests blocked that network and passed a fake transport. A refused default RunPod rail still raises `RailError`, `chat` emits `RUN_FAILED`, and any reserve is refunded. The model `endpoint` string is the supply gate and the meter label. It is not the provider URL.

## Price book is not a charge

`recompute_model`: a `byok` row is forced to `price_per_m_usd` 0 and `price_rule` `byok_toll`. Else rule `passthrough+surcharge`, or rail `vertex` / `bedrock` / `azure`, sets price to OpenRouter retail times `1 + surcharge_pct/100` (default 5%), COGS to that retail, `stocked` true, `refer_to_or` false. Else the manufactured price is `min(OR retail minus epsilon, 5 times COGS)`, and `refer_to_or` is true only when margin is not positive. `chat` does not read `refer_to_or`. The flag does not send a call to OpenRouter.

Seed `gemini-flash-vertex` and `claude-sonnet-bedrock` have a rail and `passthrough+surcharge` but no `endpoint` and no `price_per_m_usd`. Stock `chat` returns `503` before dispatch. `qwen3-coder-30b-fp8` is rail `runpod`, with an endpoint placeholder and `price_per_m_usd` 0.297.

## Wizard

`cosmos_pay_wizard.py` accepts `openrouter`, `google` (AI Studio `generativelanguage.googleapis.com`), and `bedrock`. It can save `{provider}_api_key` and a models row `{rail: provider, byok: true}` with no `endpoint`. `chat` never loads those keys.

`test_bedrock` is format validation only. Its docstring says it does not call the bedrock rail or SigV4. The rail file exists and still does not sign.

## Providers

| Provider | Track | Sell | Resell status |
|---|---|---|---|
| Google Vertex | Only when attached and the model row has an endpoint. `from_config` needs a project id and a credential. A seed row with no endpoint is 503 and no meter event. An injected rail with a fake priced transport emits `RUN_SETTLED`. | Face credits settle on that fake priced path. Pass-through recompute (retail × 1.05) is not itself a sale. No live Vertex call was made. | Own rail. Missing config stays `None` and does not call RunPod. |
| Google AI Studio | No. `test_google` is a wizard probe, not a meter emit. Rail `google` is not a named branch, so `_resolve_rail` returns `None` and `chat` is 503 `no_supply`. `test_google_is_not_a_named_rail` checks that, with the RunPod spy at 0 calls. | No. A `byok` recompute forces price 0. | BYOK wizard only. No AI Studio rail file. It does not fall through to RunPod. |
| Amazon Bedrock | A key and an endpoint can attach `BedrockRail`. `runsync` still raises `NoSupply` unless a transport was injected. No signer. Seed `claude-sonnet-bedrock` has no endpoint, so stock `chat` is 503 with no event. A fake priced transport emits `RUN_SETTLED` and does not call RunPod. | Face credits settle only on that injected priced path. Pricing can mark rail `bedrock` at retail × 1.05. Nothing signed a request. | Own rail. Missing key, endpoint, or transport is `no_supply`, not RunPod. |
| OpenRouter | `from_config` attaches when a key and an endpoint are both set. With no injected transport, `runsync` can POST through urllib. Tests blocked the network. `refer_to_or` is still not a call. A fake priced transport emits `RUN_SETTLED` and skips RunPod. | Face credits settle on that fake path. BYOK price stays 0. | Own rail. A missing key or endpoint is `no_supply`, not RunPod. |
| Azure | Same attach rule as OpenRouter: key and endpoint, or `None`. urllib is the default transport. Tests blocked the network. A fake priced transport emits `RUN_SETTLED` and skips RunPod. | Face credits settle on that fake path. `recompute_model` can price rail `azure` as pass-through. No live Azure call was made. | Own rail. A missing key or endpoint is `no_supply`, not RunPod. |
| RunPod | Yes, when the default rail is a configured `RunPodRail`, the model has an `endpoint`, and `runsync` returns a usage dict: `RUN_SETTLED` with those tokens. A missing usage dict is `unpriced`. `_UnconfiguredRail` is `RUN_FAILED`, not a successful-call meter. | Yes on the non-free path: measured face credits at `price_per_m_usd` (seed Qwen 0.297 per million). A zero-credit free plan spends daily face, not credits. | Own rail (`cosmos_pay_runpod_rail.py`). It is `self.rail` in `main()`. |

## Dispatch test

`tests/test_tokenctr_rails.py` imports `cosmos_pay_gateway` with `COSMOS_PAY_ROOT` set to an empty temp directory, so the import does not open a live `secrets.json`. Import is not fail-closed: `load_secrets` runs in `main()`, not at import. The rails receipt records 8 passed: each named rail resolves to its own object, a stock `None` rail does not call RunPod, attach requires the config fields, seed rows without an endpoint do not call RunPod, Bedrock without a transport refuses, and a fake priced transport settles like RunPod while the RunPod spy stays at zero calls. An earlier run of this file reported 1 passed. That count is the pre-rail test. The 8-passed run is the one in `C:\Users\Papa\AppData\Local\Temp\c4-rails2-result.md`. Judge H21 also recorded `8 passed` for this file. A later run, `C:\Users\Papa\AppData\Local\Temp\c4-h25-result.md`, reported 10 passed and ruff 0. The two added tests cover rail `google` and unset Bedrock, OpenRouter, and Azure. None of these runs is a live provider sale.
