# OpenWork — bound on this machine (2026-09-04)

Keith: desktop already installed; public GitHub.

| | |
|---|---|
| Vendor | OpenWork Labs / `different-ai` |
| Repo | https://github.com/different-ai/openwork (public; MIT except `ee/` Den) |
| Install | `C:\Users\Papa\AppData\Local\Programs\@openworkdesktop\` |
| Exe | `OpenWork.exe` |
| Version | **0.18.42** (2026-09-03) |
| Grant | **`V:\Streams\openwork`** (`ws_12669390bcf4`) — **not** COSMOS root, **not** `V:\A`, **not** `V:\Ai`, **not** `C:\` (full). Keith 2026-09-04: off root, off Cosmos\\Ai. |
| Workspace name | **COSMOS** (display). Path is `V:\Streams\openwork`. Cloud org also **COSMOS**. Name collision with the repo is branding only — still no tree grant. |
| Old grant | `C:\Users\Papa\OpenWork Chat` — leftover. Pointer `MOVED.md`. Do not delete. Stop using as root. |
| State | `%AppData%\com.differentai.openwork\` |
| Pane | cDeck **main left**: OPEN focuses or launches `OpenWork.exe`; LIVE chip from loopback `/health` (port in `openwork-server-state.json`). Embed **UNMEASURED** — no HTML origin. Never iframe. Never persist a ui-control bearer. Headless web (`pnpm world up dev-headless`) is the later in-pane webview. |

COSMOS role (Keith 2026-09-05): **GFO** = Gem Flash OpenWork = **ORC seat**. Replaces Cowork. Brain **GF38** on **Joanna**. **Main left** of cDeck. Workspace root = this grant — file work + ORC **off** the OS live tree. **Runs on** live Core (`:8770`, code in `V:\A\Ai\COSMOS`). **Not CCr.** This TUI keeps the **write pen for CORE**. Do **not** add `V:\A\Ai\COSMOS` as authorized folder. Joint job: finish cDeck (she orchs the live deck; CCr writes). g43 shares Heavy — leave it. Memo: `docs/ORCH_SEAT.md`.

Local workspace on disk 2026-09-04 later: `openwork-workspaces.json` selected/active **`ws_12669390bcf4`**, **name/displayName=COSMOS**, path **`V:\Streams\openwork`**. Old path `C:\Users\Papa\OpenWork Chat` leftover. Loopback `/health` port **57383**.

**Cloud org ≠ repo tree (name collision).** Switcher 2026-09-04: signed in **keith.bbf@gmail.com**; active Cloud workspace **COSMOS** — *Creator plan · 1 member* · Owner. An earlier Billing shot showed footer **acme / Owner** (same billing numbers). That label is OpenWork Cloud branding, **not** `V:\A\Ai\COSMOS` and **not** a folder grant. Do not grant the COSMOS repo to this org because it is named COSMOS.

## Permissions (Keith 2026-09-04 — V:\ grant)

C:\ is the wrong disk. Workspace root **is** `V:\Streams\openwork` (created 2026-09-04; write-probed). OpenWork Settings → **Permissions**:

| | |
|---|---|
| Workspace root | **`V:\Streams\openwork`** |
| `cm\` | COSMOS orch mailbox (CCr harvests) |
| `legal\` | OpenWork legal **working** |
| Authorized folders | **none extra** — legal and cm are already inside the root |
| Pen | This folder only. Folder grant = pen. CCr writes CORE in the tree. |

**Do not add:** `V:\A\Ai\COSMOS`, `V:\A\Ai\COSMOS\live`, `V:\A`, `V:\Ai`, `P:\Legal\Abraxas`, Desktop, Downloads. Display name **COSMOS** is branding, not a tree grant. ORC **runs on** Core `:8770`; she does not file in the repo.

**Abraxas (encoded, empty stubs, no casefiles):** working archive `V:\legal\Abraxas`; main copy `P:\Legal\Abraxas`. **Not** in this grant. Do not point OpenWork at `P:\`. GrokBot LEGAL on `V:\Ai` stays a **third** surface — do not fuse.

## Billing (measured 2026-09-04, Keith screenshot Settings → Billing)

Vendor copy on the page: **OpenWork Web, team seats, and built-in AI model access are separate purchases.** Each plan billed separately. Cloud org **COSMOS** (Creator plan, 1 member). This TUI does **not** click Purchase.

| SKU | Shot | $/mo | Notes |
|---|---|---|---|
| **Team seats** | **Included** 1/5 | **$0** | “1 of 5 included users · nothing to pay yet” |
| **OpenWork Web** | **Off** | $0 now; **$50 / joined member** if bought | “Browser access for your organization.” Warning: *No OpenWork Web subscription is active.* Desktop `OpenWork.exe` does **not** need this. Do not buy for DT. |
| **AI model access** | **Active** | **$10.00** | “1 active member × $10.00 · billed for every member.” This **is** OpenWork Models. |
| **Expected monthly total** | — | **$10.00** | Models only. Web would add $50 if turned on. |

## OpenWork Models vs BYOK

Two provider lanes under **Models**. Do not conflate them.

| Lane | What it is | Wallet |
|---|---|---|
| **OpenWork Models** | Vendor-bundled catalog. **Active $10/mo** on Billing. Usage buckets shared across the org. | OpenWork Labs inference — not SuperGrok Heavy, not Cursor Ultra, not Vertex |
| **Bring your Own Keys** | Own provider keys beside the bundled models; switch whenever. Matches the COSMOS Fast pin. | **Draw-source labeled** — see below |

### Draw sources (Keith 2026-09-04)

Keith: *I will add the Ranny.bbf API token on OpenWork — that way we can monitor usage on the different accounts based on draw source.*

OpenWork BYOK keys are **named wallets**, not a silent pool. Each key is a **draw source**. Usage is read on **that account’s** vendor console (not mixed into SuperGrok Heavy). **Joanna = Keith’s OpenWork / Vertex. Ranny = Jack’s OpenWork only. A company $300 (unnamed) = coding/reasoning Vertex rail.** This TUI does **not** paste the token. Keith adds Joanna in OpenWork Settings if this seat should draw it. Never write it to `live/config/` unless a COSMOS rail is named.

| Draw source | Identity | Where it lives | Status |
|---|---|---|---|
| **keith.bbf** | `keith.bbf@gmail.com` (OpenWork Cloud sign-in; COSMOS org Owner). AI Studio 2026-09-04 **Free tier**. Keys: `openw-cos` last4 **cLGw** on **Default Gemini Project** `gen-lang-client-0129519884` (today); older last4 **jvmA** on **My First Project** `project-af3277c0-5279-4670-86c` (Jul 12). Usage shot (My First Project, 90d): July burst then quiet; **~300× 429** ~Jul 23. **Neither** Joanna `project-5a33f910` nor Ranny `project-5c0bf0ae`. | OpenWork BYOK (xAI grok-4.3 @ low is the Fast pin). Google/Gemini AI Studio is a Keith.bbf **Free-tier Developer API** draw, not Joanna Vertex, not Ranny $300, not a $580 GCloud overflow (that figure is Joanna+Ranny). | Bound as Cloud occupant. **Not** the Google/Vertex chips painted below. If a chat ever picks `openw-cos`, watch Usage on **Default Gemini Project**. **My First Project Free tier is rate-capped** (2026-09-04: Flash RPD over 20/day; 3.1 Flash Lite RPM 15/15). Do **not** click **Set up billing**. Vendor new-project path is the **Interactions API** ([overview](https://ai.google.dev/gemini-api/docs/interactions)) — pointer only; OpenWork may still call `generateContent`. Free store = **1 day**. |
| **openwork-csm (OpenWork Google + Vertex BYOK)** | Key last4 **D6rQ**, project number **`252939746739`**, name **`openwork-csm`**. Occupant `GEMINI_API_KEY` / `GOOGLE_API_KEY` + `~/.opencode/auth.json` `google` type=api. **Not** Joanna `project-5a33f910`. **Not** Ranny Cook GCP `249427005764`. **Not** proven equal to Ranny AI Studio Cosmos `gen-lang-client-0877976774`. | OpenWork Settings → AI Providers (workspace **COSMOS**). Watch Usage on **this** project number. | **PAINTED 2026-09-04** (Keith: *Key added to openwork, google and vertex providers added*). See provider table below. Do **not** click **Set up billing** / **Activate**. |
| **Ranny.bbf AI Studio** | **`ranny.bbf@gmail.com` — in Jack’s name** (Keith 2026-09-05). Key **`openw-cosmos`** last4 **9gXw**. | **Jack’s OpenWork only.** | Leave it. Do not swap into Keith’s OpenWork. Do **not** click **Set up billing**. |
| **Ranny Cook GCP Vertex** | `project-5c0bf0ae-c45a-4d2c-bab` / `249427005764`. Jack’s name. | **Jack’s OpenWork** Vertex / $300 trial. | **Leave for Jack.** Not Core `gem-api`. Not Keith’s OpenWork. Do **not** Activate. |
| **Company GCP spare** | **UNMEASURED** — “a couple more accounts with credits” + “a few more unactivated” (Keith 2026-09-05). | Spare. Not Kelly (coding). Not Joanna. Not Ranny/Jack. | Do not invent ids. Do **not** click Activate/Upgrade on unused trials. |
| **Joanna Vertex** | `Joanna.bbf@gmail.com` · `project-5a33f910-1251-4d6a-bf9` · FreeTrialUpgrade **$266 / 100%** through **2026-10-13**. **Payment Activated** (credits rolled). Key last4 **3fMQ**, prefix `AQ.` | **Keith’s OpenWork** GEM / Vertex. Key file written **2026-09-05** to grant `V:\Streams\openwork\.secrets\vertex_key.txt` (copy of `V:\Research4\.secrets\vertex_key.txt`; gitignored). Pointer: `VERTEX_JOANNA.md`. Keith points OpenWork Settings at that file. This TUI does **not** paste into the OpenWork UI. | **OpenWork.** Not COSMOS coding. Not Jack. |
| **Kelly — COSMOS / Crucible** | **`orders.ggn@gmail.com`** (console display **Kelly Gregory**) · `project-10b3a132-ec5b-41e9-a2c` · **$300** · expires **2026-12-04**. | **This TUI** Vertex `generateContent`. Agent Platform API key in `.secrets\vertex_coding_key.txt` last4 **Ko_A**. | **GATE PASS** `VERTEX_OK_20260905T103723` (re-prove) and `VERTEX_OK_20260905T015719` `gemini-2.5-flash` `tree_id=KMesh-COSMOS-live`. COSMOS GEM bucket + Crucible Vertex spend this wallet (`vertex-coding`). Joanna `gem-api` not used for these proves. |
| **OpenWork Models $10** | Org bundled catalog | OpenWork Labs inference | Active. Separate from BYOK draw sources. |

### AI Providers painted (Keith 2026-09-04)

Workspace **COSMOS** → Settings → **AI Providers**. Quote: *Key added to openwork, google and vertex providers added.* Same shot: GCP **API key details** `openwork-csm` · `projects/252939746739`. Toast: *opencode.jsonc updates applied* / *new models available*.

**6 providers connected:**

| Chip | npm id | Badge | What it draws |
|---|---|---|---|
| **Vertex** | `google-vertex` | **Your key** · Disconnect | OpenWork UI BYOK. Same session as `openwork-csm` / `252939746739`. **Not** Joanna `cosmos_vertex_rail`. |
| **Google** | `google` | **Config** · Disconnect | `opencode.jsonc` `provider.google` `@ai-sdk/google` + occupant `google` last4 **D6rQ**. AI Studio / Gemini API lane, not Agent Platform. |
| **xAI** | (existing) | Config | Fast pin **grok-4.3** @ low. SuperGrok Heavy vs Console — do not steal Heavy with `XAI_API_KEY`. |
| **OpenCode Zen** | (existing) | Config | OpenCode catalog. Not a COSMOS rail. |
| **GitLab Duo** | (existing) | Config | Duo Credits until **Sep 16**. Not `api.anthropic.com`. |
| **OpenWork Models COSMOS** | `openwork` | Config | **$10** bundled catalog. Cloud row: **OpenWork Models Connected**. |

Grant `opencode.jsonc` still names only `provider.google` (`@ai-sdk/google`). Vertex **Your key** lives in the OpenWork provider store, not as a `google-vertex` block in that jsonc. Occupant `~/.opencode/auth.json` has `google` (api, last4 **D6rQ**) and `google-oauth-client` (Ranny Cook GCP) — **no** `google-vertex` auth entry.

**GEM in this seat was DOWN on `openwork-csm` (Keith 2026-09-04).** Google + Vertex chips were connected to last4 **D6rQ** / project **`252939746739`** — not Joanna, not proven as Studio `AIza`. Ranny AI Studio **`openw-cosmos` last4 9gXw** stays Jack’s. **2026-09-05:** Joanna Agent Platform key last4 **3fMQ** is in the grant at `V:\Streams\openwork\.secrets\vertex_key.txt`. Keith points Settings at that file. A GEM call is still unproven until one returns. Do not fuse wallets.

### Seat pin (Keith 2026-09-04 — g43 while GEM is down)

This TUI (`grok-4.6` Build) **keeps the pen (CCr) and codes.** OpenWork is the **orch seat** (Cowork’s old role, no COSMOS grant). **For now (Keith 2026-09-05): GF38 / OpenWork as Orch** — Gemini 3.8 Flash on **Joanna** Vertex. Point Settings at `V:\Streams\openwork\.secrets\vertex_key.txt`. Memo: `docs/ORCH_SEAT.md`. PRC reasoning models are not the orch brain. Vertex Claude Sonnet 5 stays unenabled.

| Pick in OpenWork | Why | Watch |
|---|---|---|
| **g43 (`grok-4.3` @ low) on xAI** | **Running now** — troubleshooting seat while GEM is down. | May share SuperGrok Heavy with this TUI. Heavy **25% used** (Keith 2026-09-05). Last 2% reserve. Do not steal Heavy with `XAI_API_KEY`. |
| **Google / Vertex Gemini** | Connected in UI; **not working** | Do not treat as live. **Not** the Joanna Activate below. |
| **OpenWork Models GLM-5.2** | $10 supervisor | Separate from g43 and from GEM. |

**GCP Activate = Joanna (Keith 2026-09-04/05 Credits page).** Billing `010E47-824B53-7202F5` (same id `gcloud` already had on `joanna.bbf@gmail.com` / `project-5a33f910`). Two Free Trial rows, **do not add them**:

| Status | Remaining / original | Credit ID | Window |
|---|---|---|---|
| **Available 100%** | **$266.00 / $266.00** | `FreeTrialUpgrade:…:Credit-010E47-824B53-7202F5` | Sep 4 → **Oct 13, 2026** |
| **Expired** | $266.00 / $300.00 (leftover at expiry) | `FreeTrial:Credit-010E47-824B53-7202F5` | Jul 14 → Sep 4, 2026 |

Activate **did not wipe** the leftover: original `$300−$34=$266` rolled into **FreeTrialUpgrade**, still **100% / $266**, still ends **2026-10-13**. Pay-as-you-go only after this credit is $0 or that date. This TUI did not click Activate and does **not** walk Cloud Foundation. `do_not_activate` on `cosmos_vertex_rail` stays — no further upgrade/attach. Joanna is **Keith’s OpenWork**. Key file is in the grant (`VERTEX_JOANNA.md`); Keith points Settings at it. This TUI does **not** paste into the OpenWork UI. g43 stays the seat pin until a GEM call actually returns.

**What it looks like in the room:** this Grok 4.6 TUI orchestrates and writes COSMOS. OpenWork.exe (grant `V:\Streams\openwork`) is g43 file-work until GEM in that seat actually returns. Native Pulse/collector still poll.

**Who spends what (Keith 2026-09-05):** **You (COSMOS) = Kelly. OpenWork = Joanna. Jack = Ranny.** Payment may be on all three; Joanna is measured Activated. Kelly Upgrade was still on the home shot. This TUI does not click Upgrade. Spare company accounts PARKED. Chrome GEM is prepaid DOM. Full table: `docs/ROUTING.md`.

**Do not:** give Ranny to Keith’s COSMOS or Keith’s OpenWork; retarget `cosmos_vertex_rail` to Ranny or `252939746739`; walk Cloud Foundation; click AI Studio **Set up billing** on remaining Free projects; put tokens in the COSMOS ledger or git; treat Google + Vertex + Models + xAI as one fused meter. Joanna Activate is bound above ($266 FreeTrialUpgrade through Oct 13).

**OpenWork Models roster** (all 9; IDs as painted):

| Model | Best for (vendor) | Model ID |
|---|---|---|
| GLM-5.2 | Multi-step tasks | `z-ai/glm-5.2` |
| Kimi K2.7 Code | Spreadsheets & scripts | `moonshotai/kimi-k2.7-code` |
| Hy3 preview | Long documents | `tencent/hy3-preview` |
| Kimi K2.6 | Everyday drafting | `moonshotai/kimi-k2.6` |
| DeepSeek V4 Flash | Quick summaries | `deepseek/deepseek-v4-flash` |
| MiniMax M2.7 | Tools & integrations | `minimax/minimax-m2.7` |
| MiniMax-M3 | Images & screenshots | `minimax/minimax-m3` |
| GLM-5.1 | Balanced default | `z-ai/glm-5.1` |
| Kimi K3 | Research & synthesis | `moonshotai/kimi-k3` |

These are **not** COSMOS `dispatch()` rails. File-work default in the Chat grant is still **grok-4.3** @ low on official xAI via BYOK. The **$10 Active** seat is the cheap A-tier **background supervisor** fuel (not the left pane, not CCr).

## What the $10 seat can run (Keith 2026-09-04)

OpenWork **calls itself** an orchestration + harness layer. That is **their** agents/skills/MCP/files. It is **not** COSMOS Core, not cDeck, not CCr.

Three different products; do not collapse them:

| Thing | What it actually is | Wallet |
|---|---|---|
| **OpenWork desktop** (already installed 0.18.42) | Free harness: Chat grant, skills, MCP, Automations UI. Covered by **Team seats 1/5 Included $0**. | $0 |
| **AI model access / OpenWork Models** | Bundled inference. **Active $10/mo** (Billing 2026-09-04). 5h / weekly / monthly buckets. GLM/Kimi/Hy3/DeepSeek/MiniMax. | OpenWork Labs inference |
| **OpenWork Web** | Browser access for the org. **Off.** $50 / joined member / month if purchased. Not the desktop app. | Do not buy for DT |

**Can it run backend upkeep + cDeck services?** **No as the clock.** Pulse, collector, health, feed, runner, WD2 are native `pythonw` + schtasks. An LLM in that loop is the Claude-scheduler scar. Those stay OS CPU.

**Can it run a background agent *for* those?** **Yes as a labeled A-tier worker**, matching `docs/ROUTING.md` Supervisor: fires on typed gaps / incidents, **proposes** (P10 / `work_orders/`), does **not** write `cosmos/` or the ledger, does **not** sit in the left orch pane or the Flex/CCr pane. Fuel: **cheap reasoning alts** — OpenWork Models (GLM-5.2 / DeepSeek Flash / Kimi) **or** Groq `openai/gpt-oss-20b` / Qwen **or** BYOK grok-4.3. Not this TUI’s SuperGrok Build slice. Not CCr.

**Concurrency (vendor, 2026-09-04):**
- Interactive left pane = one conversation (split-screen = two windows). That is the **file-work occupant**, not the supervisor.
- **Automations** are separate threads with leases (`queued/claimed/running`). Desktop-created automations run on **this PC’s connected runner** (OpenWork.exe must be up; a due run with no runner is **missed**). Web-created automations run in OpenWork Cloud.
- Max automation runtime **10s–1h**. Not a 15s COSMOS poll.
- **Long-running / laptop-closed background** is still **Building** on the OpenWork roadmap. **Scheduled tasks = Partial.**
- Usage is **shared org buckets**, not a hard one-agent lock. Parallel runs burn the $10 pool faster; they do not become Core.

**Do not:** grant OpenWork `V:\A\Ai\COSMOS` (root or authorized). File work + ORC stay in this grant. ORC **runs on** Core `:8770`. Do not put Models in the left orch window; do not put Models in the Flex/CCr seat; do not purchase **OpenWork Web** ($50) for this desktop. Keith does money — this TUI does not click Purchase.

## Test drive (2026-09-04)

Grant files (not the COSMOS tree): `C:\Users\Papa\OpenWork Chat\`
- `opencode.jsonc` — default `openwork/z-ai/glm-5.2`, small `openwork/deepseek/deepseek-v4-flash`
- `AGENTS.md` — occupant rules + first smoke
- `TESTDRIVE.md` — picker + prompt

In workspace **COSMOS**: model group **openwork** → **GLM-5.2**. New chat: `Read AGENTS.md. Run the first smoke.` Expect `OPENWORK_READY glm-5.2`. Reload the workspace if the picker still shows no OpenWork Models. OpenWork may need a restart to pick up the display name.
