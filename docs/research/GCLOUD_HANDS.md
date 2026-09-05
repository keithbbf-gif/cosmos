# GCLOUD HANDS — G46 scout return (Google Cloud CLI groups)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25 (local `gcloud <group> --help` on this machine + docs fetched live).
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim except where a COSMOS artifact or a local CLI probe is named.
**No COSMOS core code was edited.** Maker-docs sweep (DHx): each maker's hands → `docs/research/<MAKER>_HANDS.md`. Sibling Gemini/Studio inventory: `docs/research/GOOGLE_GEMINI_HANDS.md`.

**Already on the mesh (do not re-add as "new"):** Dispatcher rail **`gem-api`** (`bts_gem`) — Gemini via **Vertex / Agent Platform**, drawing the **$300 Google Cloud Welcome credit** on account **`joanna.bbf@gmail.com`**, MESH expiry **2026-10-13**, spend-gate budget **$300** (`cosmos/cosmos_node_rails.py`, `docs/MESH_ADDITIONS.md`). This file inventories the **`gcloud` CLI groups** that COSMOS can fire against that same wallet.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: a `gcloud` subcommand, the REST/SDK call that subcommand wraps, or a DOM fallback when the CLI cannot mint/consent. Chat-only Cloud Console chrome is out except as AUTH_REQUIRED / billing fallback.

**Rank key:** FREE / prepaid ($300 credit + Always Free) + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Metered GPU/VM/partner-MaaS sits **below** Always Free + credit-covered Vertex even when the box is bigger. **`gcloud ai-platform` (legacy ML Engine) is ranked last among the named groups** — it is not Vertex.

**Name collisions (do not mix):**

| Name | What it actually is | What it is not |
|------|---------------------|----------------|
| **`gcloud ai`** | Vertex AI / **Gemini Enterprise Agent Platform** (renamed Cloud Next 2026). This is `gem-api`'s wallet. | Gemini Developer API (AI Studio). Partner MaaS (Claude/Llama managed APIs) — **$300 credit cannot pay those**. |
| **`gcloud ai-platform`** | **Legacy** AI Platform / ML Engine (`cloud.google.com/ml`). Jobs / models / `predict`. | Vertex. Do not deploy new work here. |
| **`gcloud gemini`** | Org settings for **Gemini Code Assist** and **Gemini Cloud Assist**. Docs: *"not associated with Gemini CLI"*. | `gemini -p`, AI Studio, Vertex `generateContent`. |
| **Gemini CLI** (`gemini`) | OSS agent terminal. Auth = Studio key **or** Vertex ADC. | `gcloud gemini`. |
| **`$300 Welcome credit`** | Cloud Billing credit on the GCP project. Pays Vertex + Run + Storage + Compute + Functions + Scheduler + Tasks + Pub/Sub (and other GCP SKUs). | Gemini Developer API / AI Studio prepay. Official: credit **cannot** pay Studio API; **cannot** pay partner models offered as managed APIs. |
| **Claude on Agent Platform (Keith 2026-09-05 URL)** | Model Garden **`claude-sonnet-5`** on **Joanna** `project-5a33f910-1251-4d6a-bf9` (`authuser=3`). Partner MaaS: `…/publishers/anthropic/models/claude-sonnet-5:rawPredict`. Anthropic approval form + recommended request-response logging (BigQuery). | **Not** Gemini `generateContent`. **Not** `orders.ggn` coding. **Not** `api.anthropic.com`. **Not** paid by Joanna’s remaining credit. This TUI does not click Next / Set up logging. |
| **Meta / Llama on Agent Platform (Keith 2026-09-05 shot)** | Model Garden, provider **Meta**, same **My First Project** (Joanna). Banner: *Enable APIs to access full platform capabilities.* **Serverless:** Llama **4** API Service, Llama **3.3** API Service. **Self-deployed:** Llama 4, 3.3, 3.2, 3.1, 3, 2, Code Llama, Llama Guard, Prompt Guard, Segment Anything, ImageBind, NLLB, … Partner models count **21**. | **Not** Gemini. **Not** DeepSeek. **Not** Bedrock Llama (still owed as the AWS pin). Serverless = partner **MaaS** (credit **cannot** pay, same class as Claude). Self-deploy = **your** GPUs in-region (US if you pick US). This TUI does **not** click **Enable APIs**. **Maverick MaaS GATE PASS** via CLI (row below). |
| **Llama 4 Maverick MaaS card (Keith 2026-09-05 URL)** | Agent Platform Model Garden **`llama-4-maverick-17b-128e-instruct-maas`** on **Joanna** `project-5a33f910-1251-4d6a-bf9` (`authuser=3`). Meta filter. Partner **MaaS** (17B active / 128 experts). List ~$0.35 / $1.15 per 1M. | **Not** GFO. **Not** SSA. **Not** GF38. Credit **cannot** pay partner MaaS. Scout would be the Llama if adding a second brain later — still not this chair. Bedrock Llama still owed. This TUI does not click Enable / Next. |
| **Llama 4 Maverick CLI (Keith 2026-09-05)** | Call from CLI, not Console Enable: `gcloud auth print-access-token --account=joanna.bbf@gmail.com` → `POST https://us-east5-aiplatform.googleapis.com/v1beta1/projects/project-5a33f910-1251-4d6a-bf9/locations/us-east5/endpoints/openapi/chat/completions` model `meta/llama-4-maverick-17b-128e-instruct-maas`. | **GATE PASS** `LLAMA_MAVERICK_OK_20260905` `cosmos/_llama_maverick_cli_ping.json`: **http 200** `response_model` bound, text **PONG**, 19 tokens, `traffic_type=ON_DEMAND`. Not `gem-api` `generateContent`. Not Kelly. ON_DEMAND = partner SKU (Joanna billing), not Welcome credit. |
| **xAI Grok 4.1 Fast on Agent Platform (Keith 2026-09-05 URL)** | Model Garden **`grok-4.1-fast-reasoning`** publisher **xAI**. URL has **no** project/authuser. Partner MaaS. List ~$0.20 / $0.50 per 1M. Docs 2026-09-02: **Deprecated**; MaaS **shut down 2026-08-20**. Successor named: Grok 4.2 / **4.3**. | **Do not enable Vertex.** Dead garden card. |
| **Main Squeeze (Keith 2026-09-05)** | **`grok-4.1-fast-reasoning`** on **xAI Console** `api.x.ai`. **$0.20 / $0.50** per 1M. Context xAI **2M**. Best-value A-tier. Wallet = Console (`XAI_API_KEY` / `sgh-api`), **not** Heavy, **not** Vertex. | Tools / search / latency / supervisor / volume. **Not** GFO. **Not** CCr 4.6. **Not** SSA (Groq until moved). Do not put `XAI_API_KEY` on this TUI. |
| **Main Squeeze CLI ping (Keith 2026-09-05)** | `GET/POST https://api.x.ai/v1` with Research4 `Grok_API_Token-Key.txt` (`xai-`, len 84). | **Key live** `http_models=200`. **`grok-4.1-fast-reasoning` NOT IN CATALOG** (POST 400 `Model not found`). This key’s 12 ids: `grok-4.3` `grok-4.5` `grok-4.6` `grok-4.20-0309-*` `grok-build-0.1` + Imagine. Artifact `cosmos/_grok41_fast_cli_ping.json`. Closest Fast-class on this key: **`grok-4.3`**. Did not call 4.3. Did not export key into `grok` CLI. |
| **Codestral 2 on Agent Platform (Keith 2026-09-05 URL)** | Model Garden **`codestral-2`** publisher **mistralai**, Partner collection. FIM / code complete. Partner **MaaS**. List **$0.30 / $0.90** per 1M. 128k. Regions `us-central1` / `europe-west4`. | **Enable on Kelly** `orders.ggn@gmail.com` `project-10b3a132` (`vertex-coding` $300) — **not** Joanna. Credit **cannot** pay partner MaaS (same class as Claude/Llama; Llama ping was `ON_DEMAND`). This TUI does **not** click Enable. Not CCr 4.6. Not GFO. Not SSA. Not Main Squeeze. Dual-lane / FIM overflow after Keith Enables. |
| **Codestral 2 Marketplace agree (Keith 2026-09-05 shot)** | Console **Agreements / Purchase summary**. Project on screen: **My First Project** (Joanna `project-5a33f910`, not Kelly). Usage fee monthly. Input **USD 0.30 / 1M**. Page: *Most Google Cloud promotional credits don't apply to Google Cloud Marketplace purchases.* Google merchant of record; Marketplace ToS + Mistral ToS. Screen says switch project in the **top** selector. | **Do not Agree on My First Project.** That bills Joanna PAYG (OpenWork wallet). Switch to **Kelly** `orders.ggn` `project-10b3a132` first. This TUI does not click Agree / Purchase. |
| **Codestral 2 paid-billing gate (Keith 2026-09-05)** | Console: **Needs upgrade to paid billing account.** Marketplace partner MaaS will not attach on a trial/credit-only billing account. Kelly Upgrade was still on the home shot (2026-09-05). Joanna is Payment Activated for Gemini SKUs; Marketplace is a different merchant path. | **Codestral stays dark.** This TUI does **not** click Upgrade / Activate / Cloud Foundation / Set up billing. If Keith wants it: paid billing on **Kelly** (`orders.ggn`), then Enable on `project-10b3a132`. Do not upgrade Joanna for this. Spare GCP PARKED. |

---

## Local ground truth (this machine, 2026-08-25)

Probed with host-side `gcloud` (not a sandbox read). Binary:

`C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`

| fact | value |
|------|-------|
| SDK | **578.0.0** (core / beta **2026.07.24**). Latest available this probe: **582.0.0**. `gcloud components update` is Keith's call. |
| Installed extras | `gsutil` 5.37, `bq` 2.1.36, `gcloud-crc32c`, **beta**. Prefer **`gcloud storage`** over `gsutil`. |
| Active account | **`joanna.bbf@gmail.com`** (the Vertex-credit key named in the assignment) |
| Other credentialed | `keith.bbf@gmail.com` (present, **not** active) |
| Project | **`project-5a33f910-1251-4d6a-bf9`** · display name **My First Project** (Free Trial default name) · number `614387154970` |
| Billing | account display name **My Billing Account** (Free Trial default name) · `OPEN=True` · `billingEnabled: true` on the project |
| ADC | `%APPDATA%\gcloud\application_default_credentials.json` **exists**. `gcloud auth application-default print-access-token` → **OK**. `gcloud auth print-access-token` → **OK**. (Tokens not printed.) |
| Vertex live | `aiplatform.googleapis.com` **enabled**. `gcloud ai models list --region=us-central1 --limit=5` reached `https://us-central1-aiplatform.googleapis.com/` and listed **0** custom models (expected — publisher Gemini models are not this list). |
| Also enabled (selected) | `generativelanguage.googleapis.com` (Studio API on this project), `storage.googleapis.com`, `compute.googleapis.com`, `iam.googleapis.com`, `agentregistry.googleapis.com`, `modelarmor.googleapis.com`, `notebooks.googleapis.com`, `texttospeech.googleapis.com`, BigQuery family. |
| **Not yet enabled** | `run.googleapis.com`, `cloudfunctions.googleapis.com`, `cloudscheduler.googleapis.com`, `cloudtasks.googleapis.com`, `pubsub.googleapis.com`. Those groups' `--help` works locally; live deploy would first need `gcloud services enable …`. |

Remaining Welcome-credit **dollars** are **not** returned by `gcloud billing accounts list`. Watch them in [Cloud Billing reports](https://console.cloud.google.com/billing/reports) (DOM). **Credits page 2026-09-04/05 (Keith):** original FreeTrial **Expired** Jul 14–Sep 4 ($300 → $266 leftover); **FreeTrialUpgrade Available 100% $266.00** Sep 4–**Oct 13, 2026** on billing `010E47-824B53-7202F5`. Activate rolled the leftover; do not double-count. Official Free Trial is **90 days from signup, not pauseable/extendable**. After expiry or $0: Always Free tiers remain; anything over is **Paid** (this account is now Activated).

---

## How COSMOS reaches gcloud (reach column, one pattern)

Core stays sole ledger writer. Google Cloud is reached as:

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Native `gcloud` worker** | `gcloud <group> <verb> --format=json --quiet` inside an attempt-private workspace. Pin wallet with `--account=joanna.bbf@gmail.com --project=project-5a33f910-1251-4d6a-bf9`. | Preferred for resource CRUD (buckets, jobs, SA, enable APIs). Matches "no bats — in-app / COSMOS action." |
| **B. HTTP + ADC / user token** | `Authorization: Bearer $(gcloud auth application-default print-access-token)` (or `gcloud auth print-access-token`). Vertex: `POST https://{LOC}-aiplatform.googleapis.com/v1/projects/{P}/locations/{LOC}/publishers/google/models/{M}:generateContent`. Same `google-genai` SDK with `vertexai=True`. | **Already `gem-api`.** There is **no** `gcloud ai generate-content` verb — inference is REST/SDK; `gcloud` only mints the token and manages endpoints/jobs. |
| **C. Cloud CLI remote MCP** | Hosted MCP exposing `run_gcloud_command` / `run_bq_command`. OAuth + IAM. **Does not** support `gcloud auth`, `gcloud config`, `gcloud iam service-accounts`, `gcloud init`. | Agent brains that must speak gcloud. Core should still prefer a scoped native worker over giving itself a shell. |
| **D. DOM** | [Cloud Console](https://console.cloud.google.com/) — first OAuth, billing Activate, remaining-credit watch, API enable, Model Garden click-deploy, IAM consent. | Fallback only. Canon: DOM first when the API depends on something that can run out (credit expiry 2026-10-13, Free Trial close). |

Keith owns credentials and money. Store SA JSON under `live/config/` (git-ignored). Never hard-code. Never print a token or key in full. Fenced commit still gates any tree write. `--quiet` for unattended; `--format=json` for runtime-binding (bind claims to the JSON the CLI actually emitted).

---

## Auth primer (all rows inherit this unless overridden)

| method | command / env | COSMOS use |
|--------|---------------|------------|
| **User login (CLI)** | `gcloud auth login` → active account `joanna.bbf@gmail.com` | Human/Keith bootstrap. Pin with `--account=` so `keith.bbf@gmail.com` cannot silently take the wallet. |
| **Application Default Credentials** | `gcloud auth application-default login` · file `%APPDATA%\gcloud\application_default_credentials.json` · `GOOGLE_APPLICATION_CREDENTIALS` | **Production `gem-api`.** Client libraries (`google-genai` with `vertexai=True`, google-cloud-\*) pick this up. **Unset `GEMINI_API_KEY` / `GOOGLE_API_KEY`** or ADC is skipped (Studio key wins). Env: `GOOGLE_CLOUD_PROJECT=project-5a33f910-1251-4d6a-bf9`, `GOOGLE_CLOUD_LOCATION=global` (or a region), `GOOGLE_GENAI_USE_VERTEXAI=true`. |
| **Print bearer** | `gcloud auth print-access-token` (user) · `gcloud auth application-default print-access-token` (ADC) | HTTP spend-gate. Do not log the token. |
| **Service account** | `gcloud iam service-accounts create` + `gcloud iam service-accounts keys create` + `gcloud auth activate-service-account --key-file=` · role **Vertex AI User** (`roles/aiplatform.user`) at minimum for `gem-api` | Headless / CI. Keith holds the JSON. Prefer **Workload Identity Federation** (no long-lived key) if a GitHub Action or Cloud Run job is the caller. |
| **Impersonate** | `--impersonate-service-account=SA_EMAIL` (needs `roles/iam.serviceAccountTokenCreator`) | Worker acts as a scoped SA without a key file. |
| **Quota project** | `gcloud auth application-default set-quota-project PROJECT` | Required for some user-ADC calls so quota/billing hit the Vertex project, not "no project". |

---

## Cost floor (one wallet — the $300 on `joanna.bbf@gmail.com`)

Mixing Studio prepaid with this Cloud Billing account is how `gem-api` gets burned by accident. Official ([Free Trial features](https://docs.cloud.google.com/free/docs/free-cloud-features), fetched 2026-08-25):

| Wallet | Pays for | Does **not** pay for |
|--------|----------|----------------------|
| **$300 Welcome credit** (this project; MESH expiry **2026-10-13**) | Vertex / Agent Platform **Google** models, Cloud Run, Cloud Run functions, Cloud Storage overage, Compute (no GPUs until Paid), Scheduler, Tasks, Pub/Sub, BigQuery, logging… any Free-Trial-covered GCP SKU. | **Gemini Developer API / AI Studio.** **Partner models as managed APIs (MaaS).** Marketplace. Windows Server images. GPU attach **while still a non-billable Free Trial account**. |
| **Always Free tier** (no end date; 30-day notice if Google changes it; does **not** roll over) | Caps below. Usage inside the cap **does not consume the $300**. | Anything over the cap — credit then Paid. |
| **Paid billing** (after Activate, or after credit dies) | Everything. | — |

**Always Free caps that matter to these groups** (per billing account unless noted; official table 2026-08-11):

| product | Always Free |
|---------|-------------|
| **Cloud Storage** | 5 GB-months Standard in `us-east1`/`us-west1`/`us-central1`; 5k Class A + 50k Class B ops; 100 GB egress from North America (excl. China/Australia) |
| **Cloud Run** (request-based) | 2 million requests/mo; 360k GB-s memory; 180k vCPU-s; 1 GB egress NA. Jobs/instance-based: 240k vCPU-s + 450k GiB-s (us-central1-equivalent) |
| **Cloud Run functions** | 2 million invocations/mo; 400k GB-s + 200k GHz-s; 5 GB egress |
| **Pub/Sub** | 10 GiB messages/mo |
| **Cloud Tasks** | first **1 million** billable operations/mo ($0.40/M after) |
| **Cloud Scheduler** | **3 jobs/mo per billing account** (not per project). Then $0.10/job/month. Executions themselves are not billed. |
| **Compute Engine** | 1 non-preemptible **e2-micro** in `us-west1`/`us-central1`/`us-east1`; 30 GB-months standard PD; 1 GB egress NA. **GPUs/TPUs never free.** |
| **Cloud Build** (used by `gcloud run deploy --source` / functions) | 2,500 build-minutes/mo on `e2-standard-2` |
| **Secret Manager** | 6 active versions; 10k access ops; 3 rotation notifications |
| **Agent Runtime** (Agent Platform) | first 50 vCPU-hours + 100 GiB-hours RAM/mo |
| **IAM / `gcloud auth`** | **$0** |
| **Vertex Gemini tokens** | **not** Always Free. **This is what `gem-api` / `vertex-coding` burns.** Credit covers it until the wallet’s date (Joanna **2026-10-13**, `orders.ggn` **2026-12-04**). Batch/Flex ≈ 50%. 4xx/5xx **not** billed. Pricing Keith-paste **2026-09-05** (Global; non-global ~10% higher): |

**Gemini 3 Flash list price (Keith 2026-09-05, promotional through 2026-12-31, Global):**

| Model | Input / 1M | Output / 1M | Notes |
|---|---|---|---|
| Gemini 3.8 Flash | $0.75 | $3.75 | Global promo |
| Gemini 3.7 Flash | $0.75 | $3.75 | Global promo |
| Gemini 3.6 Flash | $0.75 | $3.75 | Global promo |
| Gemini 3 Flash Preview | $0.50 | — | Text/image/video only |
| Gemini 3.5 Flash | $1.50 | $9.00 | Reference (not this promo) |
| Gemini 3.5 Flash-Lite | $0.30 | $2.50 | Reference |

**From 2027-01-01 (standard):** Gemini 3.8 / 3.7 / 3.6 Flash **$1.50 / $7.50** per 1M (Global) — **2× input, 2× output**. COSMOS live default is still **`gemini-2.5-flash`** until CCr names a migrate. Do not silently retarget. Promo window covers remaining Joanna credit (Oct 13) and `orders.ggn` credit (Dec 4); after those credits $0 or those dates, this table is **real money** (Joanna already Activated). Prefer **global**. Prefer Flash over Pro. Prefer Always Free infra so credit is tokens, not idle VMs. Drive/AI **chatbot** subscription is a different meter (DOM); this table is API `generateContent`.

Spend-gate `gem-api` / `vertex-coding` at $300 per wallet. After the credit date the rail is **real money** unless Keith stops it.

---

## Group map (the twelve named HANDs)

Local `--help` (SDK 578) matches current [gcloud reference](https://docs.cloud.google.com/sdk/gcloud/reference) for these groups. Web docs last-updated 2026-05-27 → 2026-08-18.

| group | local `--help` one-liner | COSMOS job | enable API (this project) |
|-------|--------------------------|------------|---------------------------|
| **`ai`** | Manage entities in Vertex AI | `gem-api` sibling: endpoints, Model Garden, tuning, indexes, custom jobs. **Does not generate text.** | **on** (`aiplatform.googleapis.com`) |
| **`ai-platform`** | Manage AI Platform jobs and models | **Legacy. Skip for new work.** | n/a (do not enable for COSMOS) |
| **`gemini`** | Gemini Code Assist + Cloud Assist **settings** | Org policy for Console/IDE assist. Not inference. | n/a for `gem-api` |
| **`run`** | Manage Cloud Run applications | Serverless HTTP + **jobs** (batch to completion). Highest-power Always Free compute. | **off** — `run.googleapis.com` |
| **`functions`** | Manage Google Cloud Functions | Source-zip HTTP / bucket / Pub/Sub / Eventarc triggers. gen2 **is** Cloud Run underneath (`detach` / `upgrade`). | **off** — `cloudfunctions.googleapis.com` |
| **`scheduler`** | Cloud Scheduler jobs | Google-side cron → HTTP / Pub/Sub / App Engine. **3 free jobs.** Complements (does not replace) Windows clocks. | **off** — `cloudscheduler.googleapis.com` |
| **`tasks`** | Cloud Tasks queues and tasks | Deferred HTTP with retries/rate. 1M ops free. | **off** — `cloudtasks.googleapis.com` |
| **`pubsub`** | Topics, subscriptions, snapshots | Event bus. 10 GiB free. Vertex batch notifications, function triggers. | **off** — `pubsub.googleapis.com` |
| **`storage`** | Buckets and objects | `gs://` for Vertex batch JSONL, function zips, Run source. 5 GB Always Free. `cp`/`ls`/`hash`/`rsync`/`sign-url`. | **on** |
| **`compute`** | Compute Engine VMs | e2-micro Always Free only. GPU/VM clusters burn the $300 fast. Not a COSMOS Core host. | **on** |
| **`iam`** | Service accounts, keys, roles, WIF | Headless identity for `gem-api` / Run / Functions. **Free.** | **on** |
| **`auth`** | OAuth2 for the CLI + ADC | The bootstrap every other row uses. **Free.** **Already live.** | n/a |

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **`gcloud auth application-default` + `print-access-token`** | CLI (auth) | Mint ADC for client libraries; print a Bearer for REST. `login` / `print-access-token` / `revoke` / `set-quota-project`. Without this, `gem-api` has no Vertex identity. | `joanna.bbf@gmail.com` user OAuth (already done; ADC file present) | **free** | **highest** (unlocks the wallet) | Native worker, once. Core/workers inherit ADC. Never a `.bat`. Do not log tokens. Pin `--account=joanna.bbf@gmail.com`. |
| 2 | **Vertex `generateContent` (REST / `google-genai`)** | REST + SDK (uses `gcloud` auth) | The actual Gemini call `gem-api` already fires: `POST https://{loc}-aiplatform.googleapis.com/v1/projects/{p}/locations/{loc}/publishers/google/models/{m}:generateContent` (+ stream). Multimodal, tools, JSON schema. **No `gcloud ai generate` verb exists.** | ADC / SA / `gcloud auth print-access-token` | **$300 credit** until **2026-10-13**, then PAYG (Flash 3.7 global $0.75/$3.75 per 1M through 2026-12-31). 4xx/5xx not billed. | **highest** (already `gem-api`) | Existing rail `bts_gem` through the spend gate. SDK: `genai.Client(vertexai=True, project="project-5a33f910-1251-4d6a-bf9", location="global")`. Bind the response `model` + usage, not an exit code. |
| 3 | **`gcloud storage` (`cp` `ls` `hash` `cat` `rm` `rsync` `sign-url`)** | CLI + GCS | Create/list buckets; upload/download; content-address (`hash` is the GEM cousin on GCS); rsync; time-limited `sign-url`. Vertex **batch** in/out is JSONL on `gs://`. Functions `--stage-bucket` is GCS. | ADC / user | **Always Free 5 GB** US regions; overage from $300 then PAYG. CLI itself $0. | **highest** (artifact rail + Vertex batch) | Native `gcloud storage cp FILE gs://bucket/hash --format=json`. Ledger holds the `gs://` pointer; GEM still owns local hashes. Prefer this over `gsutil`. Enable already on. |
| 4 | **`gcloud run deploy` + `run services`** | CLI (serverless HTTP) | Deploy a container (or `--source .` via Cloud Build) to a URL. Scale-to-zero. Revisions, IAM invoker, traffic split. | ADC + enable `run.googleapis.com` | **Always Free 2M req + CPU/RAM caps**; overage from $300. Build minutes from Cloud Build free 2,500. | **highest** (off-box worker that costs $0 at COSMOS volume) | Native worker after Keith enables the API. Public URL or `--no-allow-unauthenticated` + OIDC. Point Cloud Scheduler / Tasks at it. **Not** a second Core — overflow job runner only. |
| 5 | **`gcloud run jobs` (`create` `deploy` `execute`)** | CLI (batch) | Run-to-completion workers (no HTTP). Parallel tasks. `executions` + `logs`. | same as Run | Jobs billed instance-based; **Always Free 240k vCPU-s + 450k GiB-s** (us-central1-eq). Min 1 minute. | **highest** (batch critique / port-backlog) | `gcloud run jobs execute NAME --wait --format=json`. Pair with Scheduler (row 8) for cron. Spend-cap CPU. |
| 6 | **`gcloud functions deploy` + `call`** | CLI (source functions) | Deploy Python/Node/… from a directory or `gs://` zip. Triggers: `--trigger-http`, `--trigger-topic`, `--trigger-bucket`, Eventarc filters. `call` invokes now. gen2 sits on Cloud Run; `detach` / `upgrade` (web; local 578 may lack `upgrade`) move to native Run. | ADC + enable `cloudfunctions.googleapis.com` | **Always Free 2M invocations** + GB-s/GHz-s. gen2 also counts as Run SKUs — don't double-count in the head. | **high** (event glue: GCS → HTTP, Pub/Sub → worker) | Native `gcloud functions deploy NAME --gen2 --runtime=python312 --trigger-http --no-allow-unauthenticated --format=json` then `gcloud functions call`. Prefer gen2. Max timeout gen2 = 3600s. |
| 7 | **`gcloud pubsub` topics / subscriptions** | CLI (bus) | `topics create` `publish`; `subscriptions create` `pull` `seek`; snapshots; schemas. Functions `--trigger-topic` and Scheduler `--pubsub` land here. | ADC + enable `pubsub.googleapis.com` | **Always Free 10 GiB/mo** then PAYG. | **high** (event bus) | Native `gcloud pubsub topics publish TOPIC --message=… --format=json`. Pull from a worker; don't poll Core. Emulator: `gcloud emulators pubsub` (local $0). |
| 8 | **`gcloud scheduler jobs create http` / `pubsub`** | CLI (cron) | Unix-cron (min grain **1 minute**) that POSTs HTTP or publishes Pub/Sub. `pause` `resume` `run` (on-demand). 3 jobs free **per billing account**. | ADC + enable `cloudscheduler.googleapis.com` | **3 jobs free**; then $0.10/job/month. Executions not billed. Target's Run/Functions/HTTP still bill their own SKU. | **high** (off-machine clock) | Native `gcloud scheduler jobs create http NAME --schedule="*/5 * * * *" --uri=https://… --oidc-service-account-email=…`. Target = Cloud Run **or** Tailscale `cosmos up` URL. **Does not replace** Windows schtasks + Core scheduler (canon: the OS runs the machine). Use as a **backup ping** / GCP-side trigger only. |
| 9 | **`gcloud tasks` (`queues` + `create-http-task` + `run`)** | CLI (deferred work) | Create a queue; enqueue HTTP (or App Engine) tasks with `scheduleTime`, retries, rate. `buffer` for queue-built-in buffering. Force `run`. | ADC + enable `cloudtasks.googleapis.com` | **first 1M ops/mo free**; then $0.40/M (32 KB chunks). HTTP targets add network $. | **high** (retrying outbound) | Native `gcloud tasks create-http-task --queue=… --url=… --schedule-time=…`. Overflow when Core must not block on a slow webhook. Not a second ledger. |
| 10 | **`gcloud iam service-accounts` + keys + WIF** | CLI (identity) | `create` `list` `add-iam-policy-binding`; `keys create` (JSON); `sign-jwt` `sign-blob`; `workload-identity-pools` for keyless GitHub/GitLab OIDC. | user with IAM Admin | **free** | **high** (headless `gem-api` / Run invoker) | Keith-run once: SA `cosmos-gem@project-….iam.gserviceaccount.com` + `roles/aiplatform.user` + (optional) `roles/run.invoker`. JSON in `live/config/`. Prefer WIF over keys for forge CI. |
| 11 | **`gcloud auth login` / `list` / `revoke` / `activate-service-account`** | CLI (auth) | Human login; list accounts (joanna active, keith present); revoke; activate a SA key for the CLI itself. `configure-docker` for Artifact Registry pushes. | user Google | **free** | **high** (infra) | Keith. COSMOS workers must **not** `auth login` interactively. Use ADC or `--account=`. |
| 12 | **`gcloud services enable` / `list`** | CLI (API gate) | Enable `run` / `cloudfunctions` / `cloudscheduler` / `cloudtasks` / `pubsub` (currently **off**). `services list --enabled` is the probe this scout used. | user with serviceusage | enable is $0; the product then bills | **high** (prerequisite) | Native `gcloud services enable run.googleapis.com cloudfunctions.googleapis.com cloudscheduler.googleapis.com cloudtasks.googleapis.com pubsub.googleapis.com --project=project-5a33f910-1251-4d6a-bf9`. Keith-owned; don't enable GPUs/partner APIs by accident. |
| 13 | **`gcloud ai model-garden models list` / `list-deployment-config`** | CLI (Vertex) | List publisher models in Model Garden; show verified machine specs. **Browse is $0.** `deploy` stands up a **dedicated endpoint** (GPU/VM $). | ADC; API already on | **$0 to list**; deploy = instance $ (burns credit; GPUs need Paid if still Free Trial) | **high** (vendor-plural catalog) | Native `gcloud ai model-garden models list --format=json`. Do **not** `deploy` partner Claude/Llama without a spend cap — MaaS **cannot** use the $300 credit; self-deploy GPUs may be blocked until Activate. |
| 14 | **`gcloud ai endpoints predict` / `raw-predict` / `direct-predict` + stream** | CLI (Vertex online) | Call a **deployed** endpoint (custom / Garden), not the publisher Gemini URL. `explain` for feature attributions. | ADC | token or instance $ | **high** (only after a model is deployed) | Native `gcloud ai endpoints predict ENDPOINT --json-request=file.json`. For Gemini publisher models prefer row 2 (SDK/REST). |
| 15 | **`gcloud ai models` upload / list / delete** | CLI (Vertex registry) | Register a custom model artifact; list (this project: **0** on 2026-08-25). | ADC | storage $ for artifacts | **med-high** | Only if COSMOS trains/tunes. Publisher Gemini does not appear here. |
| 16 | **`gcloud ai tuning-jobs create`** | CLI (SFT) | Supervised fine-tune a foundation model → tuned model. `list` `describe` `cancel`. | ADC | token + training $ from credit | **med-high** | Spend-gated worker. Don't tune on the $300 without a Keith go — irreversible spend. |
| 17 | **`gcloud ai custom-jobs` / `hp-tuning-jobs` / `persistent-resources`** | CLI (training) | Launch custom training containers; hyperparameter search; keep a warm cluster. | ADC | **VM/GPU $** — credit killer | **med** | Avoid until credit plan is explicit. Persistent resources idle-bill. |
| 18 | **`gcloud ai indexes` + `index-endpoints`** | CLI (Vector Search) | Build/query vector indexes (Matching Engine). Overlaps `gcloud vector-search`. | ADC | index + query $ | **med-high** (RAG) | Alternative to local embeddings + SQLite / Studio File Search. Needs a corpus on GCS. |
| 19 | **Cloud CLI remote MCP (`run_gcloud_command`)** | MCP | Natural-language → allowlisted `gcloud`/`bq` on this project. **Blocks** `auth` / `config` / `iam service-accounts` / `init`. | OAuth + IAM | **free** protocol; underlying SKUs bill | **high** (agent-shaped gcloud) | MCP-client in a worker, not Core. Complements native `gcloud`. Docs: [Use the Cloud CLI remote MCP server](https://docs.cloud.google.com/sdk/use-gcloud-mcp). |
| 20 | **`gcloud compute instances` e2-micro only** | CLI (VM) | Always Free **one** e2-micro in us-central1/west1/east1 + 30 GB PD. `ssh` `scp` `config-ssh`. | ADC; compute API **on** | **Always Free e2-micro**; anything else (esp. GPU) burns credit / needs Paid for GPUs | **med** (tiny always-on box) | Only if Keith wants a GCP sidecar. **Do not move COSMOS Core here.** `gcloud compute tpus` / GPUs: fail-closed until a spend cap. |
| 21 | **`gcloud storage sign-url` + `hmac`** | CLI | Time-boxed anonymous GET/PUT of a GCS object; HMAC keys for S3-compat clients. | ADC / SA | ops $ (inside Always Free at COSMOS volume) | **med-high** | Hand a worker a 15-min URL instead of a key. |
| 22 | **`gcloud run compose` / `worker-pools` / `domain-mappings`** | CLI | Compose-on-Run; always-on worker pools (no scale-to-zero — **bills idle**); custom domains. | ADC | worker-pools ≈ instance $ | **med** | Skip worker-pools on the $300. Compose is convenience. |
| 23 | **`gcloud functions logs` / `event-types` / `runtimes` / `regions`** | CLI | Read function logs; list trigger types and runtimes before deploy. | ADC | logs: first 50 GiB/project Always Free | **med** | Preflight + return-watcher evidence. |
| 24 | **`gcloud beta ai` extras** | CLI (beta) | Local 578 beta adds `semantic-governance-policies`, tensorboard experiments/runs/time-series. Web GA `ai` now lists semantic-governance too (docs 2026-08-18; local GA tree may lag). | ADC | policy $0; tensorboard storage $ | **med** | Only if Keith wants Vertex governance/TB. Don't depend on beta flags in Core. |
| 25 | **`gcloud gemini` (Code Assist / Cloud Assist settings)** | CLI | CRUD: `code-repository-indexes`, `code-tools-settings`, `data-sharing-with-google-settings`, `gemini-gcp-enablement-settings`, `logging-settings`, `release-channel-settings`, observability. **Explicitly not Gemini CLI.** | Cloud user + org | Code Assist is a **license** (Standard/Enterprise), not the $300 token pool | **low-med** | Only if Keith enables Gemini in Cloud Console / IDE against this project. Do **not** confuse with `gem-api`. |
| 26 | **`gcloud ai-platform` (legacy ML Engine)** | CLI | `jobs` `models` `versions` `local` `predict` against **old** AI Platform. | ADC | training/prediction $ on a sunset surface | **low** (do not use) | **Skip.** New work = `gcloud ai` + REST generateContent. |
| 27 | **`gcloud compute` beyond e2-micro** (MIG, GPUs, TPU, LB, firewalls) | CLI | Full IaaS. Free Trial **cannot add GPUs** until Paid Activate. | ADC | **metered**; idle VM = silent credit drain | **low** for COSMOS (wrong shape) | Refuse by default. Visible refusal is correct. |
| 28 | **Cloud Console DOM (billing, APIs, Model Garden, IAM consent)** | DOM | Remaining-credit graph, Activate Paid, enable APIs, first OAuth, org policy that rejects API keys. | Keith Google login | console $0 | **high as fallback** | `cosmos_browser` when AUTH_REQUIRED / credit watch / Activate. Canon: DOM first when quota/billing can run out. Credit-expiry watch **before 2026-10-13**. |

---

## What `gcloud ai` does **not** do (trap)

Local and docs agree: `gcloud ai` manages **entities** (jobs, endpoints, models, indexes, Model Garden, tensorboards, tuning). **Gemini text generation is not a gcloud subcommand.** COSMOS already does that via `bts_gem` + ADC. Wiring a second path that shells `gcloud` to "ask Vertex" will fail looking for a verb that does not exist.

Correct split:

```
gcloud auth application-default login          # identity (once)
gcloud services enable aiplatform.googleapis.com
# inference:
python -c "from google import genai; … vertexai=True … generate_content"
# or REST Bearer from:
gcloud auth application-default print-access-token
```

---

## Enable-before-use (this project, measured)

Already on: Vertex (`aiplatform`), Storage, Compute, IAM, Studio (`generativelanguage`), Agent Registry, Model Armor, Notebooks, TTS, BigQuery.

Must enable before rows 4–9 can actually deploy:

```
gcloud services enable ^
  run.googleapis.com ^
  cloudfunctions.googleapis.com ^
  cloudscheduler.googleapis.com ^
  cloudtasks.googleapis.com ^
  pubsub.googleapis.com ^
  --project=project-5a33f910-1251-4d6a-bf9 ^
  --account=joanna.bbf@gmail.com
```

(`^` is cmd.exe continuation; PowerShell uses `` ` ``. Prefer a COSMOS native worker, never a `.bat`.)

---

## COSMOS fit / anti-fit

**Fit (free/prepaid first):** keep burning the $300 on **Vertex tokens** (`gem-api`); use Always Free **Storage** for batch JSONL; use Always Free **Run / Functions / Scheduler(3) / Tasks(1M) / Pub/Sub(10 GiB)** as GCP-side overflow — not as a second Core.

**Anti-fit:** replacing COSMOS scheduler with Cloud Scheduler; hosting Core on Compute Engine; `gcloud ai-platform`; `gcloud gemini` as an inference rail; Model Garden **partner MaaS** on this credit; GPU VMs; idle `run worker-pools`.

**Clock canon:** Windows Scheduled Tasks + Python daemons run the machine. Cloud Scheduler is allowed as a **Google-side HTTP ping** (3 free jobs) if COSMOS is reachable (`cosmos up` / Cloud Run). It is not the system clock.

**Vendor-plural:** this whole file is **one wallet** (joanna / Vertex). Studio free Flash is a *different* wallet (`GOOGLE_GEMINI_HANDS.md`). Do not let a worker with `GOOGLE_API_KEY` set silently bill Studio while ADC was intended, or the reverse.

---

## Sources (official, fetched 2026-08-25)

Local: `gcloud --version` → 578.0.0; `gcloud <group> --help` for `ai`, `ai-platform`, `gemini`, `run`, `functions`, `scheduler`, `tasks`, `pubsub`, `storage`, `compute`, `iam`, `auth` plus nested `ai model-garden`, `ai endpoints`, `ai models`, `ai custom-jobs`, `ai tuning-jobs`, `auth application-default`, `run jobs`, `run services`, `scheduler jobs`, `tasks queues`, `pubsub topics`, `storage cp`, `iam service-accounts`, `beta ai`. `gcloud auth list`, `config list`, `projects list`, `billing accounts list`, `billing projects describe`, `services list --enabled`, ADC token probe, `gcloud ai models list --region=us-central1`.

| what | URL |
|------|-----|
| gcloud reference (all groups) | https://docs.cloud.google.com/sdk/gcloud/reference |
| `gcloud ai` | https://docs.cloud.google.com/sdk/gcloud/reference/ai |
| `gcloud ai-platform` | https://docs.cloud.google.com/sdk/gcloud/reference/ai-platform |
| `gcloud gemini` | https://docs.cloud.google.com/sdk/gcloud/reference/gemini |
| `gcloud run` / `jobs` | https://docs.cloud.google.com/sdk/gcloud/reference/run · `/run/jobs` |
| `gcloud functions` / `deploy` | https://docs.cloud.google.com/sdk/gcloud/reference/functions · `/functions/deploy` |
| `gcloud scheduler` / `jobs` / `create` | https://docs.cloud.google.com/sdk/gcloud/reference/scheduler · `/scheduler/jobs` · `/scheduler/jobs/create` |
| `gcloud tasks` | https://docs.cloud.google.com/sdk/gcloud/reference/tasks |
| `gcloud pubsub` / `topics` | https://docs.cloud.google.com/sdk/gcloud/reference/pubsub · `/pubsub/topics` |
| `gcloud storage` | https://docs.cloud.google.com/sdk/gcloud/reference/storage |
| `gcloud compute` | https://docs.cloud.google.com/sdk/gcloud/reference/compute |
| `gcloud iam` | https://docs.cloud.google.com/sdk/gcloud/reference/iam |
| `gcloud auth` / ADC | https://docs.cloud.google.com/sdk/gcloud/reference/auth · `/auth/application-default` |
| `gcloud services` | https://docs.cloud.google.com/sdk/gcloud/reference/services |
| Model Garden CLI | https://docs.cloud.google.com/sdk/gcloud/reference/ai/model-garden/models |
| Free Trial + Always Free | https://docs.cloud.google.com/free/docs/free-cloud-features |
| Cloud Scheduler pricing | https://cloud.google.com/scheduler/pricing |
| Cloud Tasks pricing | https://cloud.google.com/tasks/pricing |
| Cloud Run pricing | https://cloud.google.com/run/pricing |
| Vertex / Agent Platform gen pricing | https://docs.cloud.google.com/vertex-ai/generative-ai/pricing · https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing |
| Agent Platform (ex-Vertex) | https://cloud.google.com/products/gemini-enterprise-agent-platform |
| Cloud CLI remote MCP | https://docs.cloud.google.com/sdk/use-gcloud-mcp |
| Scheduler vs Tasks | https://docs.cloud.google.com/tasks/docs/comp-tasks-sched |
| Sibling Gemini hands | `docs/research/GOOGLE_GEMINI_HANDS.md` |

---

## Host bind (additive, 2026-08-27 s6) — M6 not expanded

This MOTIF row does **not** become a GCP rewrite (M6). Sibling bind: Gemini CLI `selectedAuthType=vertex-ai` (same `$300` Vertex wallet, MESH-expires **2026-10-13**). Remaining dollars still **UNKNOWN** (U8, Billing DOM / Keith). Partner MaaS cannot draw the welcome credit.
