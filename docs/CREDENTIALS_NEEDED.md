# CREDENTIALS NEEDED -- the open-window handoff, one list

**Generated** by `builds/probe/credential_manifest.py` (do not hand-edit; re-run it).
**Measured** 2026-08-31T11:00:59Z  ·  root `V:\A\Ai\COSMOS\live`  ·  tree `KMesh-COSMOS-live`

Keith owns money and credentials; COSMOS opens the door and never a bat. This file exists because a missing key used to surface as one rail's typed refusal buried in one agent's return -- an ask that never arrived, and a build that stalled silently. Every row below names WHAT it unblocks, WHERE the file goes, and HOW to prove it landed.

**This file contains no key material and never will.** The generator measures presence with `stat()` and never opens a credential file; it refuses any path outside the runtime root's `config/` role, including the plaintext store at `D:\R2Cloner`, which it does not read, list or touch.

**Ask now: 3**  ·  blocked 2 · degraded 1 · optional 2 · planned (do not ask yet) 1 · satisfied 3 · unmeasured 1

| state | credential | put it here | it unblocks |
|---|---|---|---|
| **BLOCKED** | OpenAI API key (Codex CLI) | `openai_api_key.txt` | the `codex-cli` node rail: probe, dispatch, and any coder/vetter job on it |
| **BLOCKED** | Cloudflare R2 credentials (backup target) | `r2_credentials.json` | the R2 offsite push (`builds/backup/cosmos_backup_r2.py`) and its scheduled clock (`cosmos_offsite_clock.py`) |
| **DEGRADED** | Anthropic API key (Claude Code CLI) | `anthropic_api_key.txt` | `ClaudeRail.dispatch` -- the keyed Claude rail, which refuses NO_KEY today |
| **OPTIONAL** | Firecrawl API key | `firecrawl_api_key.txt` | higher Firecrawl rate limits and the authenticated endpoints |
| **OPTIONAL** | COSMOS kill-channel token | `kill_token.txt` | gating the service off-switch: while this file is absent the kill/control channel is ungated behind the bearer token alone |
| **UNMEASURED** | Tailscale login (an interactive session, NOT a file) | *(no file -- login)* | `cosmos up` -- phone/remote reach over the tailnet |
| **SATISFIED** | Groq (GroqCloud) API key -- NOT xAI Grok | `groq_api_key.txt` | Bound 2026-09-04. **Expires 2027-09-01.** `groq-api` satellite GATE PASS (chat-create). Kernel attach BACKLOG. |
| **SATISFIED** | COSMOS Core bearer token | `api_token.txt` | every authenticated call to COSMOS Core: KDash, the mobile client, voice |
| **SATISFIED** | Cursor COSMOS API key | `cursor_cosmos_key.txt` | `cosmos_dispatch --kind cursor` -- the Cursor agent lane |
| **SATISFIED** | ledger HMAC install key | `install_key.bin` | every ledger write, and therefore every spend-gated worker dispatch |

Every path below is `V:\A\Ai\COSMOS\live\config\<name>` -- resolved through the role, never typed by hand.

## OpenAI API key (Codex CLI) -- BLOCKED

**Put it here:** `V:\A\Ai\COSMOS\live\config\openai_api_key.txt`

**Shape:** sk-... (one line; never printed, never committed)  ·  **Get it:** https://platform.openai.com/api-keys

**Unblocks:**

* the `codex-cli` node rail: probe, dispatch, and any coder/vetter job on it
* `cosmos_dispatch --kind codex` -- the whole Codex agent lane refuses NO_KEY before it writes a job
* Codex work orders through `cosmos_work_order_run`
* a future `codex-cli` row in `cosmos_rails_prober.WIRED_NODES` (the key is necessary, not sufficient -- see note)

**Verify it landed:**

```
py -3.14 cosmos/cosmos_codex_rail.py --root V:\A\Ai\COSMOS\live --probe
expect:     "ok": true
expect NOT: NO_KEY
```

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_codex_rail.py:79 -- KEY_NAME; read_key() raises NO_KEY`
* `cosmos/cosmos_dispatch.py:2003 -- DispatchError NO_KEY before job creation`
* `cosmos/cosmos_work_order_run.py:159 -- key_path_for(paths) on the codex path`

**Evidence** (MEASURED, builds/probe/MESH_STATUS.json, measured 2026-08-30T21:18:47.285497-05:00):

```
UNREACHABLE: NO_KEY: [NO_KEY] OpenAI key missing at V:\A\Ai\COSMOS\live\config\openai_api_key.txt (never hard-code; redact to sk-…last4)
```

> Placing the key clears the refusal but does NOT put codex-cli in the registry: it is also absent from cosmos_rails_prober.WIRED_NODES, so nothing asks it for a proof. Two independent blockers, one link_id.

## Cloudflare R2 credentials (backup target) -- BLOCKED

**Put it here:** `V:\A\Ai\COSMOS\live\config\r2_credentials.json`

**Shape:** account id + access key id + secret (S3-compatible)  ·  **Get it:** Keith already holds these; COSMOS has no copy and reads none

**Unblocks:**

* the R2 offsite push (`builds/backup/cosmos_backup_r2.py`) and its scheduled clock (`cosmos_offsite_clock.py`)
* a copy whose failure is uncorrelated with this machine (WISHLIST: survives total tree DELETION)

**Verify it landed:**

```
py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --preflight
expect:     "status": "READY"
expect NOT: NO_CREDENTIALS
```

**What refuses without it** (each is a typed refusal in the tree):

* `builds/backup/cosmos_backup_r2.py:137 -- load_credentials raises NO_CREDENTIALS`
* `builds/backup/cosmos_offsite_clock.py:256 -- tick() heartbeats the same refusal`

**Evidence** (STATIC):

```
no probe artifact for this one; the consumers listed are the binding (each raises a typed refusal without it)
```

> The adapter landed 2026-08-31 (F-45, 29 tests) and the clock (F-47, 35/35) registers nothing. Keith places a copy at the config path; nothing automated goes near D:\R2Cloner. The credential is the only remaining blocker for a real push.

## Anthropic API key (Claude Code CLI) -- DEGRADED

**Put it here:** `V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt`

**Shape:** sk-ant-... (one line; never printed, never committed)  ·  **Get it:** https://console.anthropic.com/settings/keys

**Unblocks:**

* `ClaudeRail.dispatch` -- the keyed Claude rail, which refuses NO_KEY today
* keyed (non-seat) Claude jobs, so seat exhaustion stops being a single point of failure for the whole core->code route

**Verify it landed:**

```
py -3.14 cosmos/cosmos_claude_rail.py --root V:\A\Ai\COSMOS\live --probe
expect:     "ok": true
expect NOT: NO_KEY
```

**What answers meanwhile:** the prepaid SEAT answers now: cosmos_rails_prober._claude_live_call runs `claude -p` with ANTHROPIC_API_KEY UNSET (cosmos_rails_prober.py:158-190), which is why claude-cli carries a registry proof while ClaudeRail.probe() refuses NO_KEY. Not blocking; single-pathed.

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_claude_rail.py:81 -- KEY_NAME; read_key() raises NO_KEY`
* `cosmos/cosmos_claude_rail.py:391 -- the child env's ANTHROPIC_API_KEY`
* `cosmos/cosmos_rails_prober.py:239 -- presence check on the keyed path`

**Evidence** (MEASURED, builds/probe/MESH_STATUS.json, measured 2026-08-30T21:18:47.285497-05:00):

```
UNREACHABLE: NO_KEY: [NO_KEY] Anthropic key missing at V:\A\Ai\COSMOS\live\config\anthropic_api_key.txt (never hard-code; redact to sk-ant-…last4)
```

## Firecrawl API key -- OPTIONAL

**Put it here:** `V:\A\Ai\COSMOS\live\config\firecrawl_api_key.txt`

**Shape:** fc-...  ·  **Get it:** https://www.firecrawl.dev/app/api-keys

**Unblocks:**

* higher Firecrawl rate limits and the authenticated endpoints

**Verify it landed:**

```
py -3.14 cosmos/cosmos_firecrawl_rail.py --root V:\A\Ai\COSMOS\live --probe
expect:     "ok": true
```

**What answers meanwhile:** the rail runs KEYLESS and answered on the last measured run (http=200) with key_present=false.

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_firecrawl_rail.py:48 -- KEY_NAME; read_key() returns None when absent (keyless is a supported mode, not a refusal)`

**Evidence** (MEASURED, builds/probe/MESH_STATUS.json, measured 2026-08-30T21:18:47.285497-05:00):

```
firecrawl-web papers primaryId=arxiv:gr-qc/9504041 http=200 success=True date=Mon, 31 Aug 2026 02:18:45 GMT
```

## COSMOS kill-channel token -- OPTIONAL

**Put it here:** `V:\A\Ai\COSMOS\live\config\kill_token.txt`

**Shape:** a secret Keith chooses (one line)  ·  **Get it:** Keith invents it -- no vendor, no account

**Unblocks:**

* gating the service off-switch: while this file is absent the kill/control channel is ungated behind the bearer token alone

**Verify it landed:**

```
py -3.14 cosmos/cosmos.py status --root V:\A\Ai\COSMOS\live
expect:     (service starts; the kill endpoint then demands the token)
```

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_service.py:474 -- kill_token.txt, when present, gates /kill`

**Evidence** (STATIC):

```
no probe artifact for this one; the consumers listed are the binding (each raises a typed refusal without it)
```

## Tailscale login (an interactive session, NOT a file) -- UNMEASURED

**No file.** This is an interactive login; nothing lands in the tree.

**Shape:** n/a -- device auth in the Tailscale app; no key lands in the tree  ·  **Get it:** https://login.tailscale.com/ (or the Tailscale tray app)

**Unblocks:**

* `cosmos up` -- phone/remote reach over the tailnet
* `tailscale cert <fqdn>` -- the browser-trusted cert `cosmos serve --cert` wants, instead of a self-signed one

**Verify it landed:**

```
tailscale status
expect:     (a tailnet name and this machine listed)
expect NOT: Logged out
```

**What answers meanwhile:** LAN / localhost reach is unaffected; only off-LAN and the trusted cert depend on it.

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_up.py:49 -- UpError kinds NO_TAILSCALE / NOT_LOGGED_IN`
* `cosmos/cosmos_up.py:106 -- detect_tailscale() locates the binary`

**Evidence** (STATIC):

```
no probe artifact for this one; the consumers listed are the binding (each raises a typed refusal without it)
```

> No credential file is created for this one -- do not invent a path.

## Groq (GroqCloud) API key -- NOT xAI Grok -- SATISFIED 2026-09-04

**Put it here:** `V:\A\Ai\COSMOS\live\config\groq_api_key.txt`  *(git-ignored; never print the value)*

**Shape:** gsk_...  ·  **Get it:** https://console.groq.com/keys
**Expires:** **2027-09-01** (Keith 2026-09-04). Remint before that date; do not wait for a 401.

**Unblocks:** `groq-api` mesh addition (`docs/arch/meshadditions_ARCH.md` §4.3 E). Default model `openai/gpt-oss-20b`. Not xAI Grok. Not Bedrock Llama. Cookbook [github.com/groq/groq-api-cookbook](https://github.com/groq/groq-api-cookbook) is a research pointer, not a COSMOS rewrite. Rate limits [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits) — org-wide; live cap is [settings/limits](https://console.groq.com/settings/limits) + `x-ratelimit-*` headers, not the docs table.

**Verify it landed** (measured 2026-09-04, `live/config/groq_rail_probe.json`):

```
GET  https://api.groq.com/openai/v1/models            HTTP 200  n=14  has openai/gpt-oss-20b
POST https://api.groq.com/openai/v1/chat/completions  HTTP 200  response_model=openai/gpt-oss-20b
key_prefix=gsk_  last4 bound  value_emitted=false  expires=2027-09-01
```

`cosmos_groq_rail.py` satellite **GATE PASS** 2026-09-04 (`response_model=openai/gpt-oss-20b`, chat-create). Kernel attach still BACKLOG.

## OpenWork BYOK — Google + Vertex -- SATISFIED occupant (not a COSMOS config file)

**Put it here:** OpenWork Settings → **AI Providers** (occupant `OpenWork.exe`, grant `C:\Users\Papa\OpenWork Chat`). **Not** `live/config/`. **Not** git.

**Painted 2026-09-04** (Keith: *Key added to openwork, google and vertex providers added.*): workspace **COSMOS** shows **6 providers connected**. **Vertex** `google-vertex` **Your key**. **Google** `google` **Config**. GCP dialog in the same shot: key **`openwork-csm`** last4 **D6rQ** project **`252939746739`**. Occupant `GEMINI_API_KEY` / `GOOGLE_API_KEY` match that last4. Ranny AI Studio **`openw-cosmos`** last4 **9gXw** / `gen-lang-client-0877976774` is a **different** project — spare, not this bind. Never print. Never commit.

**Unblocks:** labeled OpenWork Google + Vertex draw on **`openwork-csm` / `252939746739`**. **Who:** OpenWork.exe file-work / A-tier supervisor. **Not** COSMOS Crucible / `gem-api` (that is **Joanna** Vertex). Does **not** Activate Ranny Cook GCP or Joanna. Usage table: `docs/ROUTING.md` Joanna vs Ranny. Bind: `docs/OPENWORK_BIND.md`.

**Verify it landed:** OpenWork AI Providers = Vertex **Your key** + Google **Config** + 6 connected. Occupant `google` last4 **D6rQ**. Quote those. Do not quote the secret.

## COSMOS Core bearer token -- SATISFIED

**Put it here:** `V:\A\Ai\COSMOS\live\config\api_token.txt`

**Shape:** a high-entropy secret minted by `cosmos install`  ·  **Get it:** minted by COSMOS itself -- `py -3.14 cosmos/cosmos.py install`

**Unblocks:**

* every authenticated call to COSMOS Core: KDash, the mobile client, voice

**Verify it landed:**

```
py -3.14 cosmos/cosmos.py status --root V:\A\Ai\COSMOS\live
expect:     "ok": true
```

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_service.py:410 -- refuses to serve rather than invent auth`
* `cosmos/cosmos_service.py:419 -- an EMPTY token file is an open door, also refused (this is why the manifest measures non-emptiness, not existence)`

**Evidence** (STATIC):

```
no probe artifact for this one; the consumers listed are the binding (each raises a typed refusal without it)
```

## Cursor COSMOS API key -- SATISFIED

**Put it here:** `V:\A\Ai\COSMOS\live\config\cursor_cosmos_key.txt`

**Shape:** crsr_...  ·  **Get it:** https://cursor.com/dashboard (Integrations -> API keys)

**Unblocks:**

* `cosmos_dispatch --kind cursor` -- the Cursor agent lane
* the watchdog's Cursor overflow route when the Grok lanes are loaded

**Verify it landed:**

```
py -3.14 cosmos/cosmos_cursor_rail.py --root V:\A\Ai\COSMOS\live --probe
expect:     "ok": true
expect NOT: NO_KEY
```

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_cursor_rail.py:48 -- KEY_NAME; read_key() raises NO_KEY`
* `cosmos/cosmos_dispatch.py:1996 -- DispatchError NO_KEY before job creation`
* `cosmos/cosmos_watchdog2.py:649 -- cursor_key_exists() gates the overflow lane`

**Evidence** (MEASURED, builds/probe/MESH_STATUS.json, measured 2026-08-30T21:18:47.285497-05:00):

```
cursor-api live apiKeyName=Cursor COSMOS 2 http=200 date=Mon, 31 Aug 2026 02:18:45 GMT key=crsr_…31ab
```

## ledger HMAC install key -- SATISFIED

**Put it here:** `V:\A\Ai\COSMOS\live\config\install_key.bin`

**Shape:** binary, minted by `cosmos install` -- never typed by a human  ·  **Get it:** minted by COSMOS itself -- `py -3.14 cosmos/cosmos.py install`

**Unblocks:**

* every ledger write, and therefore every spend-gated worker dispatch

**Verify it landed:**

```
py -3.14 cosmos/cosmos.py audit --root V:\A\Ai\COSMOS\live
expect:     "ok": true
```

**What refuses without it** (each is a typed refusal in the tree):

* `cosmos/cosmos_node_worker.py:401 -- WorkerError NO_KEY`
* `cosmos/cosmos_bucket_daemon.py:486 -- WorkerError NO_KEY`
* `cosmos/cosmos_node_bucket_worker.py:466 -- WorkerError NO_KEY`

**Evidence** (STATIC):

```
no probe artifact for this one; the consumers listed are the binding (each raises a typed refusal without it)
```

---

Regenerate: `py -3.14 builds\probe\credential_manifest.py --root <runtime-root> --write-md`
