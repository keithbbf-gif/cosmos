# COSMOS WALLETS & MODEL GOVERNANCE INDEX
**Sanitized Operational Spec & Model Rules of Engagement**
*Canonical Master (with vault pointers + covenant): `V:\Research4\.secrets\WALLETS_AND_ACCOUNTS.md` — Protocol `COSMOS-WALLET-GOVERNANCE/1`, Effective 2026-10-16*
*This mirror contains NO key bytes. Key `.txt` files live only in `V:\Research4\.secrets\` (safe by location, never under R2 publish tree). If in conflict, the canonical file wins.*

## 1. GOVERNANCE (summary — normative text in canonical Part I)
- **H1 No Upgrade/Activation:** never Activate/Upgrade trial billing (destroys $300 grant). On `NEEDS_UPGRADE`/`ACTIVATE_BILLING` → HALT, ask human.
- **H2 Endpoint isolation:** `AQ.*` → only `aiplatform.googleapis.com`. Never `generativelanguage.googleapis.com` (403 / retail failover). `AIza.*` → only AI Studio.
- **H3 Zero exfiltration:** never echo/log/commit raw keys. Pointers + `{env:...}` only. `.txt` stays single-line.
- **H4 Wallet confinement:** coding lanes (`gem-api`/`vertex-coding`) bind to active wallet; fallback only via rotation sequence.
- **H5 Spend brake:** single session projecting >$5 pauses without operator approval.
- **Soft:** S1 flash-by-default (`gemini-3.8-flash`/`2.5-flash`, pro only when flash fails); S2 stable prefixes for 50% cache discount; S3 pre-stage standby at <$10 or <14d to expiry.
- **Pre-flight handshake (required):** agent emits `{"protocol":"COSMOS-WALLET-GOVERNANCE/1","acceptance_assertion":{...will_not_activate_billing, target_wallet, target_project...}}` before use; 5-point test (assertion, GREEN ping on target only, no upgrade call, no key in logs, spend≤$5 or paused) must pass.
- **Legal note:** prompt file alone can't bind vendors; liability attaches via (a) operator↔deployer license incorporating this protocol by reference, (b) §1.4 assertion + proxy logs as prima facie evidence of exceeding authorized access (CFAA / agency), (c) deterministic dual-lock enforcement (`cosmos_vertex_rail.py` + `spendguard_state.json` → intercept/record/halt to `COSMOS_KB.json`), (d) countersigned enterprise addendum for true vendor liability. Drop-in clause in canonical §1.5.

## 2. THUNDERBIRD-VERIFIED BILLING IDENTITIES (twoa502i.default-release)
| Gmail | Finding | Billing ID | Key dates |
|---|---|---|---|
| `joanna.bbf@gmail.com` | Trial → upgraded to paid | `01E6F9-170031-470024` / profile `5288-4928-3167` | Onboard 2026-07-20; **paid 2026-09-04** ($10 prepay); cap notices Oct 2026 |
| `keith.bbf@gmail.com` | Past-due → prepaid → closed + $8.83 refund | `0142FE-A0C041-4BE7E3` / profile `1377-7493-6818` | Project `project-af3277c0-5279-4670-86c`; closed 2026-07-15 02:59 UTC |
| `DeltaTherapeutics@gmail.com` | Pre-existing Cloud/Firebase access | — | MFA 2025-02-05; billing/IAM re-auth 2025-06-13 |
| `sales.bbf@gmail.com` | No Cloud; legacy AdWords promos | — | 2017 AdWords $300 mails |
| `dchamberss@gmail.com` | No Cloud; pipeline identity | — | Target Jan 2027 trial |

## 3. $300 FLEET (clocks — Google sends no activation email; dates from manifests)
| Priority | Identity | Project ID | Number | Expiry | Status |
|---|---|---|---|---|---|
| 1 Dead | `orders.ggn@gmail.com` (Kelly) | `project-10b3a132-ec5b-41e9-a2c` | `684238616165` | trial over 2026-10-16 | DEAD `BILLING_DISABLED` — archive only, do NOT upgrade |
| 2 Active | `medicineman.mme@gmail.com` | `project-cc5302c9-190c-4cdf-87d` | `456875530590` | **2026-12-18** | $299.93 left (console 2026-10-19, 60d) — GREEN |
| 3 Standby GREEN | `fruitaholics.com@gmail.com` | `project-cbef203a-6f27-43be-811` | `953760228233` | ~2026-12-19 | $300 intact |
| 4 Standby GREEN | `patriotfuelstop.com@gmail.com` | `project-3cce004b-198c-45f3-81a` | `571047330544` | ~2026-12-19 | $300 intact |
| 5 Reserved | `ranny.bbf@gmail.com` (Jack) | `project-5c0bf0ae-c45a-4d2c-bab` | `249427005764` | — | Jack activates own; do not wire |
| 6 Dead | `joanna.bbf@gmail.com` | `project-5a33f910-1251-4d6a-bf9` | — | **2026-10-13** | EXPIRED — archive only |
| 7 Free | `keith.bbf@gmail.com` | `project-af3277c0-5279-4670-86c` | `475026348209` | closed | AI Studio free limits |
| 8 Pipeline | `dchamberss@gmail.com` | (new at rotation) | — | ~Apr 2027 | Queued Jan 2027 |

Per-key when/how + endpoints + rotation: see canonical Part IV–V. Zero-2SV ping: `python V:\a\ai\cosmos\work_orders\ccr\vertex_ping.py`. Rotation updates env (`GOOGLE_VERTEX_API_KEY/PROJECT/LOCATION`), `live/config/vertex.json`, OpenWork Settings → Environment, picker `Vertex → gemini-3.8-flash`.

## 4. MULTI-MODEL PROVIDERS
- **OpenRouter** (`openrouter-api`): Gemma-4 free pins + $50 budget (`live/config/openrouter_rail.json`).
- **OpenAI** (`oa-api`): GPT-5.6 Terra/Luna (`live/config/openai.json`), ~$30.
- **Groq** (`groq-api`): `openai/gpt-oss-20b` free tier (`live/config/groq_rail.json`).
- **Cursor** (`cursor-api`): `composer-2.5` Ultra (`live/config/cursor_rail.json`).
- **xAI Grok / GitLab / YouTube**: via vault filenames only (see canonical Part IV); legacy AI Studio `AIza.*` → AI Studio only.

## 5. FILE MAP (consolidation contract)
Canonical `WALLETS_AND_ACCOUNTS.md` wins. This file = sanitized mirror. `COSMOS_KB.json#/keys` (14 entries) = runtime mirror. `live/config/*.json` = runtime pointers + budgets (`do_not_activate:true`). `.secrets/*.txt` = secrets only, single-line, never committed. `HOWTO_SWITCH_VERTEX_KEYS.md` / `README_DO_NOT_PUBLISH.md` = deep-dives.
