# Portfolio Studio architecture

## 1. PURPOSE

Keith sits down at Portfolio Studio to decide what each of seven products is trying to accomplish, see where every product actually is, inspect the evidence and cost of the work already running, and deliberately advance one product through the shared MOTIF method without losing sight of the other six. Portfolio Studio must therefore present Forge coding, Crucible legal, Diligence deals, Docket IP, UPS physics, Differentiator medical, and Website GC together while preserving each product's own pen, mailbox, hands, destination, occupancy, and refusal gates; it must bind every status, finding, estimate, and transition to a value returned by the live COSMOS Core. It must never start or advance MOTIF on its own, turn an empty or unavailable measurement into a reassuring zero, invent a run or stage from queue words, hide a RED health result, publish or write a product artifact on Keith's behalf, or create a second Core, scheduler, ledger writer, profile tree, or source of truth.

## 2. TOOLS NEEDED

### Contract boundary

Portfolio Studio is a projection client. COSMOS Core remains the only authority and the only service allowed to read authoritative runtime state, apply a stage decision, submit work, enforce spend, or write a ledger event. Client modules may retain selection, filters, expansion state, and the last successful response in memory; they may not infer authoritative stage, health, cost, occupancy, completion, or approval.

The current cache contains two distinct persistence contracts:

- `cosmos_profiles.py` backs `GET/POST /api/v1/profiles`. It owns seven profile-specific setup records and exposes the current nine-stage Core contract: `define`, `research`, `arch`, `consensus1`, `build`, `critics`, `consensus2`, `improve` (displayed as IMPLEMENT), `iterate`.
- `cosmos_studio.py` backs `GET/POST /api/v1/studio`. It owns one global Studio pack with `define`, `research`, `arch`, one `consensus`, `build`, `critics`, `implement`, and `iterate`.

Neither contract currently exposes authoritative live stage progression. The requested product-facing sequence — **DEFINE → RESEARCH → ITERATE → CONSENSUS → CRITICS → BUILD → IMPROVE → IMPLEMENT** — is therefore a target operator contract, not a fact the present client may claim. Core must expose the projection on existing routes while retaining the legacy nine-stage fields for existing panels:

| Portfolio stage | Existing persisted material | Important compatibility rule |
|---|---|---|
| DEFINE | profile `define`; Studio `define` | Preserve the on-disk key `define`; blank remains blank. |
| RESEARCH | profile `step_setup.research` and `stages.research`; Studio `research` | Research configuration is not a run. |
| ITERATE | profile `arch` and terminal `iterate` setup; Studio `arch` plus `iterate` policy | This combines architecture iteration and loop policy for the operator sequence; Core must identify the bound underlying step(s), never the client. |
| CONSENSUS | profile `consensus1`; Studio `consensus` | The current Studio pack has only one consensus object; do not fabricate a second result. |
| CRITICS | profile `critics`; Studio `critics` | A configured critic seat is not a returned criticism. |
| BUILD | profile `build`; Studio `build` | Reordering this after CRITICS is a target engine change, not a CSS/tab reorder. Legacy execution stays explicit until Core emits the new contract. |
| IMPROVE | profile `consensus2`; no independent Studio result today | Until Core binds a revised-artifact step, expose `UNMEASURED`, not the IMPLEMENT record. |
| IMPLEMENT | profile `improve`; Studio `implement` and `dest` | `improve` remains a legacy id; display is IMPLEMENT. Keith's approval is mandatory. |

### Exact inventory

“Failure mode” below is the behavior the page must render. A transport failure never authorizes a synthetic fallback value.

| Status | Tool/module | Input | Output used by Portfolio Studio | Owner | Failure mode |
|---|---|---|---|---|---|
| EXISTING | `DeckStudio` in `deck_studio.js` | host and header API kit; active stage form | Studio pack, stage setup, jukebox heat | Client | Show the route error/refusal in the active module; retain last-good data as visibly stale. It must not call `/jobs` or a MOTIF start route from SAVE. |
| EXISTING | Runs painter in the alternate `deck_studio.js` revision (`paintRunsList`, `rowHtml`, `inspectHtml`) | jukebox response, filter, selected job id | runs list and selected run detail | Client | Empty filter result says explicit empty; malformed or unavailable queue says unavailable. The duplicate module identity is a collision, not a feature. |
| EXISTING | `DeckProfiles` / `ProfilesApp` in `deck_profiles.js` | profile id; base URL/token; setup form | seven profile records, skin tabs, destination catalogs | Client | Unknown profile is `BAD_INPUT`; `NO_SOURCE` is shown as not configured. Direct `fetch()` and the old empty `harvestPage()` are incompatible implementations. |
| EXISTING | `deck_more.html` extra-pane shell | tab activation | rail host and stage host | Client | Missing mount target is a composition failure; do not replace the page or remove existing panels. |
| EXISTING | `deck_tabs.js` | selected tab | mounts Studio/Profile/Run modules | Client | A labels-only tab map cannot claim a mounted module. Existing tabs and panels remain available. |
| EXISTING | header transport (`apiGet`, `apiPost`) | method, existing API path, JSON body | authenticated Core response | Client | `401`, network errors, and parse errors remain distinct visible failures. Pane code must use this transport rather than opening a second client stack. |
| EXISTING | `GET /api/v1/status` | none | `ready`, `tree_id`, ledger head `seq/event` | Core | Missing/unready is not healthy. A changed or absent `tree_id` blocks stage actions. |
| EXISTING, CURRENTLY BROKEN IN THIS CHECKOUT | `GET /api/v1/health` / `cosmos_health` | none | health verdict/rows and negative-control result | Core | The current handler imports a missing `snapshot`; return/render the actual error and RED. Never downgrade RED or reuse stale GREEN as current. |
| EXISTING, CONTRACT DRIFT | `GET /api/v1/jukebox` | none | jobs and exact queue states `QUEUED`, `RUNNING`, `BROKE`, `CLEAN`, `FINDINGS` | Core | The current panel can be uncomposed (`503`) and its flat shape does not satisfy all consumers. No `DONE`/`FAILED`, cancel, or retry action may be invented. |
| EXISTING | `GET /api/v1/jobs` | none | scheduler state keyed by `job_id` | Core | Empty object is an explicit empty scheduler; it does not supply command text, profile, stage, or findings by itself. |
| EXISTING | `POST /api/v1/jobs` | `{command, priority?}` | `201 {job_id}` | Core | `400 BAD_REQUEST`; queueing a job is not advancing or starting MOTIF. Submission belongs in existing run controls, not an automatic stage transition. |
| EXISTING | `GET /api/v1/spend` | none | rail caps, settled, reserved, headroom, expiry | Core | Missing rail or attribution is `UNMEASURED`; never render `$0`. |
| EXISTING | `GET/POST /api/v1/profiles` / `cosmos_profiles.py` | GET `?profile=<id>`; POST `{profile, define?, stages?, dest?, step_setup?}` | seven-product catalog, setup, destination, legacy stages, no-start/no-publish flags | Core | Unknown profile/destination is `BAD_INPUT`; overlong statement is `REFUSED`; missing file is `NO_SOURCE`. POST saves only and does not start MOTIF or publish. |
| EXISTING | `GET/POST /api/v1/studio` / `cosmos_studio.py` | GET none; POST a partial pack (`define`, `research`, `arch`, `consensus`, `build`, `critics`, `dest`, `implement`, `iterate`) | global MOTIF configuration and catalogs | Core | Missing pack is `NO_SOURCE`, `available:false`; limits return `BAD_INPUT` or `REFUSED`. POST saves only. |
| EXISTING | `GET /api/v1/gitur` | none | CCr lease, jobs, legs, panes, credential fold | Core | `BUSY`, `BROKE`, `UNMEASURED`, or queue unavailable stays explicit. Gitur is a gate for GitHub/GitLab destinations, not another writer. |
| EXISTING | `GET /api/v1/work_orders` | `id`, `state`, `limit` | rows/counts; one order and output head when `id` is present | Core | Missing store is `NO_SOURCE`; missing id is `NOT_FOUND`; absent product tag remains unassigned. |
| EXISTING | `GET /api/v1/review` | `window=day|week|month|90` | approvals, blockers, logins, catalog | Core | Optional sources may be `NO_SOURCE` or `UNMEASURED`; approval is present only when Core returns it. |
| EXISTING | `GET /api/v1/runs_ops` | none | watchdog, clocks, work orders, streams, Gitur, spend, products | Core | Child folds can be `BROKE`, `NO_SOURCE`, or `UNMEASURED`; one broken fold must not erase the others. |
| EXISTING | `GET /api/v1/model_rater` | filters/sort/search/limit | model catalog, seats, job estimate, costs, policy, porosity fold | Core | Empty/stale catalog and unmeasured model dimensions remain labeled; banned/refused choices cannot be silently substituted. |
| EXISTING | `POST /api/v1/model_rater/seat` | assign/add/remove action, profile, seat, model/via/effort/cap | updated seat set | Core | Banned model or rotator use is `REFUSED`; seat namespace is not automatically an occupancy profile id. |
| EXISTING | `POST /api/v1/model_rater/job_estimate` | `{tokens_in,tokens_out,override?}` or `{reset:true}` | estimate and per-job costs | Core | Bad tokens/override are `BAD_INPUT`; absent estimate is `UNMEASURED`, not free. |
| EXISTING | `GET /api/v1/recents` | list, or `open=1&id=<cow-id>` | recent sessions or opened text | Core | Missing source is `NO_SOURCE`; unknown/not permitted id is `404 NOT_IN_RECENTS`; omitted legal content is not reconstructed. |
| EXISTING | `GET /api/v1/surfaces` | none | reachability, capacity, age, qualification | Core | `reachable:null` is unmeasured; uncomposed route is `503`. |
| EXISTING | `GET /api/v1/tools` | none | tool-contract verification report | Core | `verified:null` means unknown, not failed or passed. |
| EXISTING | `GET /api/v1/makers` | `kind`, `tag`, `text` | maker catalog | Core | Empty match is empty; uncomposed route is `503`; bad filter is `BAD_INPUT`. |
| EXISTING | `GET /api/v1/porosity` | `profile`, comma-separated `agents` | pairs, tensor/complement, observation count | Core | No observation is `kind:UNMEASURED`; do not synthesize model quality. |
| EXISTING | `POST /api/v1/crucible` | `{sources[], critics?, priority?}` | `201 {job_id,outcome:QUEUED}` | Core | Empty sources are `400`; no runnable critics is `501 CRUCIBLE_NOT_RUNNABLE`. It is a Crucible round, not a general MOTIF start. |
| EXISTING | `POST /api/v1/command` | `{text}` | verb-specific commander result | Core | `UNKNOWN_COMMAND`, `REFUSED`, or kernel refusal is shown verbatim. It is not the Portfolio stage-control seam. |
| EXISTING | `POST /api/v1/orc` | `{stream}` for an existing ORC stream | boot/recovery result | Core | `BAD_STREAM`/boot refusal. ORC streams are not the seven product ids. |
| MISSING | Portfolio projection fold inside Core | existing `/profiles` and `/runs_ops` inputs | each product's measured active stage, state, stage binding, job ids, finding count, approval requirement, and measurement time | Core | Any field without tracker/ledger evidence is `UNMEASURED`; the whole fold reports `NO_SOURCE` or `BROKE` without contaminating other products. No new route is required. |
| MISSING | Explicit stage-transition contract on existing `POST /api/v1/profiles` | profile, expected current stage/version, requested next stage, Keith decision | accepted/refused transition plus ledger evidence and refreshed profile projection | Core | Stale version, skipped prerequisite, missing approval, RED health, wrong tree, or missing evidence is `REFUSED`; never queues a job as a side effect. |
| MISSING | Product attribution in the existing jobs/jukebox/spend folds | ledger and manifest product/stage tags | bound product/stage per run and measured per-product spend | Core | Untagged historic data remains `UNATTRIBUTED`/`UNMEASURED`; it is never assigned by text matching. |
| MISSING | `PortfolioStudio` composition/store module | responses from existing GETs; user selection | normalized immutable view model plus per-fold freshness/error | Client | Partial failure retains visibly stale last-good folds; no client inference fills missing authority fields. |
| MISSING | Portfolio board, eight-stage spine, product detail, findings feed, cost surface modules | normalized store only | the five regions specified below | Client | Each region owns its empty/error/refusal state and remains usable when a sibling region fails. |
| RETIRE AFTER REPLACEMENT | Duplicate Runs export from `deck_studio.js` | n/a | n/a | Client | Move Runs ownership to a dedicated module while preserving its DOM/test pins; do not delete the Runs panel. |
| RETIRE AFTER REPLACEMENT | labels-only `deck_tabs.js`, direct profile `fetch()`, `kitForTab() -> null`, and empty `harvestPage()` variants | n/a | n/a | Client | Remove only after the composed transport/mount/save contracts pass. |
| RETIRE | Jukebox command-word heat as a stage authority | queue command text | colored stage guess | Client | It may remain a diagnostic hint, but it must never set a product's stage or completion. |
| RETIRE | `IMPROVE` as an alias for current Core `improve` id | legacy display string | misleading label | Client | Keep the id for compatibility; current Core stage 8 displays IMPLEMENT. The new IMPROVE stage requires its own Core-bound meaning. |

`JACK'S MESH`, Signal Core, `kdash_native.js`, all existing cDeck panels, and every existing deep link are outside the replacement boundary and remain mounted.

## 3. LAYOUT CONCEPTION

The page is an operator workbench, not a dashboard collage. Selection flows from portfolio to stage; evidence flows back from Core. No region is decorative, and no region may determine another region's authority by scraping rendered text.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ EXISTING cDeck shell / JACK'S MESH / Signal Core / existing panels          │
├──────────────────────────────────────────────────────────────────────────────┤
│ PORTFOLIO BOARD                                                             │
│ ┌ Forge ┐ ┌ Crucible ┐ ┌ Diligence ┐ ┌ Docket ┐ ┌ UPS ┐ ┌ Diff. ┐ ┌ Web ┐ │
│ │stage  │ │stage     │ │stage      │ │stage   │ │stage│ │stage  │ │stage│ │
│ │state  │ │state     │ │state      │ │state   │ │state│ │state  │ │state│ │
│ │run/$  │ │run/$     │ │run/$      │ │run/$   │ │run/$│ │run/$ │ │run/$│ │
│ └───────┘ └──────────┘ └───────────┘ └────────┘ └─────┘ └───────┘ └─────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ SELECTED PRODUCT: <measured identity>       CORE: tree / seq / health        │
│ DEFINE → RESEARCH → ITERATE → CONSENSUS → CRITICS → BUILD → IMPROVE →       │
│ IMPLEMENT                                                                   │
│ [state and approval marker on each stage; selection is not advancement]     │
├───────────────────────────────────────┬──────────────────────────────────────┤
│ PER-PRODUCT STAGE DETAIL              │ RUNS / FINDINGS FEED                 │
│ purpose + frozen input                │ exact word state + job id            │
│ setup / seats / evidence / output     │ product/stage binding or UNATTRIBUTED│
│ destination + refusal                 │ FINDINGS/BROKE/stale evidence        │
│ [SAVE SETUP] [REQUEST ADVANCE]        │ selected-run inspection              │
├───────────────────────────────────────┴──────────────────────────────────────┤
│ COST / ESTIMATE                                                           │
│ measured rail spend | product attribution | selected-job estimate | cap     │
│ every absent measure says UNMEASURED; estimate is never labeled spend       │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Region contracts

| Region | What it paints | Existing GET source(s) |
|---|---|---|
| Portfolio board | Exactly seven cards in the Core profile catalog order; label/status, measured current Portfolio stage and state, bound running/finding counts, occupancy/CCr gate, measured product spend, freshness | Primary: `/api/v1/profiles?profile=<id>` and `/api/v1/runs_ops`; supporting: `/api/v1/status`, `/api/v1/jobs`, `/api/v1/gitur`, `/api/v1/work_orders`, `/api/v1/spend`. Until Core adds binding/attribution, those cells say `UNMEASURED`. |
| MOTIF stage spine | The exact eight operator stages; selected stage; Core-returned state; evidence/refusal/approval marker; compatibility disclosure when legacy nine-stage execution is active | `/api/v1/profiles?profile=<selected>`; `/api/v1/studio` only for the current global pack; measured progression from the new projection fields on those existing GETs. |
| Per-product stage detail | Product purpose/define text, selected-stage setup, role/seat assignments, source/evidence pointers, output pointers, destination, saved time, current refusal, and Keith decision control | `/api/v1/profiles?profile=<selected>`, `/api/v1/studio`, `/api/v1/model_rater`, `/api/v1/work_orders?id=<bound-id>`, `/api/v1/review`, `/api/v1/porosity`. Product-specific actions such as Crucible remain explicitly product-specific. |
| Runs/findings feed | Scheduler/job identity, exact Core state word, product and stage binding, age/freshness, findings/refusal summary, output head on explicit inspect | `/api/v1/jobs`, `/api/v1/jukebox`, `/api/v1/runs_ops`, `/api/v1/review`, `/api/v1/work_orders`; `/api/v1/gitur` for Gitur-bound work. |
| Cost/estimate surface | Core spend by rail, measured product attribution, reservation/headroom/expiry, selected-job token estimate and rate-card result, seat cap | `/api/v1/spend`, `/api/v1/model_rater`, `/api/v1/runs_ops`; estimates are changed only through existing `POST /api/v1/model_rater/job_estimate`. |

The board does not replace the current Profiles pages, Runs panel, Orders, Review, Gitur, Models, Recents, Surfaces, Tools, Makers, Porosity, or system panels. It composes their Core data into one decision surface and keeps their deep inspection paths.

## 4. HOW THE MODULES ACTUALLY WORK

### Shared data store and refresh discipline

1. Mount triggers parallel `GET /api/v1/status`, `/api/v1/runs_ops`, `/api/v1/jobs`, `/api/v1/jukebox`, `/api/v1/spend`, `/api/v1/gitur`, `/api/v1/work_orders`, and one `/api/v1/profiles?profile=<id>` for each of the seven ids returned by the first profile response. The client does not maintain a hard-coded eighth product.
2. Every response is stored as its own fold with `loading | fresh | stale | empty | unmeasured | refused | broke`, its Core measurement time, receipt time, and error. A successful response updates only its fold.
3. Operational folds refresh every 10 seconds, matching the existing cDeck poll cadence: status, runs operations, jobs, jukebox, and Gitur. Spend and work orders refresh every 30 seconds and immediately after a related accepted POST. Profile setup refreshes on product selection, on tab visibility return, and immediately after a save/transition response. Model Rater, Review, Porosity, and a selected work-order detail load on demand.
4. Refreshes are coalesced: one in-flight request per route/query. A slower old response cannot overwrite a newer response. Hiding Portfolio Studio stops client polling; remount performs a fresh read.
5. A failed refresh retains last-good bytes only with a visible STALE age and the current error. No action that requires current tree, health, stage version, or approval remains enabled against stale authority.

### Portfolio board

- **Trigger:** initial mount; operational refresh; accepted profile/stage/job/seat/estimate action.
- **GETs:** the board joins only Core-provided identifiers. `profile`/`product` tags are the join key; command text is never parsed to assign a run.
- **State:** selected product is client state. Card stage/state/run/cost are Core state. Changing selection never POSTs and never advances anything.
- **Empty/UNMEASURED:** seven catalog profiles with `NO_SOURCE` paint “not configured”; no bound jobs paints explicit “no active runs”; missing stage binding or product cost paints `UNMEASURED`; UPS remains `needs_keith` when Core says so.
- **Refusals:** RED/broken health, wrong `tree_id`, unavailable stage projection, or busy/missing CCr state is shown on the affected card and blocks stage action, not inspection.

### MOTIF stage spine

- **Trigger:** product selection, profile refresh, or an accepted transition.
- **GET:** `/api/v1/profiles?profile=<id>` supplies legacy setup and the target Core-supplied `portfolio_stages` projection. `/api/v1/studio` supplies global pack configuration where still applicable.
- **State:** each of the eight stages has a Core-returned status such as `UNMEASURED`, `NOT_CONFIGURED`, `READY_FOR_KEITH`, `ACTIVE`, `FINDINGS`, `REFUSED`, or `IMPLEMENTED`. These words must be defined and emitted by Core; the client does not derive them from timestamps, filled forms, job counts, or jukebox heat.
- **Refresh:** no independent polling; it repaints when the selected profile fold changes.
- **Empty/UNMEASURED:** before the new projection exists, show the exact legacy nine-stage contract and an `UNMEASURED — no live progression binding` notice. Do not present the target eight-stage order as live.
- **Refusal:** selecting a blocked stage opens its evidence/refusal detail. It does not offer “skip”.

### Per-product stage detail

- **Trigger:** selected product or selected stage changes.
- **GETs:** profile and Studio setup immediately; model seats/estimate, review, porosity, and bound work-order detail on demand.
- **POST save:** `POST /api/v1/profiles` saves profile setup; global fields still owned by the Studio pack use `POST /api/v1/studio`. Both responses replace the submitted fold only after Core accepts them. Copy states plainly: **SAVE DOES NOT START OR ADVANCE MOTIF**.
- **Product POSTs:** `POST /api/v1/crucible` remains a clearly labeled Crucible run action and returns `QUEUED` or `CRUCIBLE_NOT_RUNNABLE`. Existing `/jobs`, `/command`, and `/orc` actions remain in their current panels; Portfolio Studio does not repurpose them as stage transitions.
- **Empty/UNMEASURED:** blank purpose stays blank; absent artifacts, findings, estimates, or porosity say `UNMEASURED`/`NO_SOURCE`. No sample roles, fake sources, or fake history are generated.
- **Refusal:** validation and Core refusal details remain attached to the relevant field/action. A failed POST does not optimistically mutate authoritative state.

### Product stage movement and Keith approval

Stage movement is a two-step human operation:

1. **Prepare:** Keith edits and saves setup/evidence. Core returns the saved version and reevaluates readiness. This does not start work and does not move the stage.
2. **Approve transition:** only when Core returns `READY_FOR_KEITH`, the detail module exposes **REQUEST ADVANCE** with the current product, from-stage, proposed to-stage, stage/version token, evidence summary, health/tree binding, cost state, and destination. Keith confirms that exact packet. The client POSTs it to the extended existing `POST /api/v1/profiles` contract.

Core then checks the expected version, legal product transition, required evidence, health/tree binding, spend gate, product-specific gates, occupancy/CCr lease, and Keith decision. It writes the authoritative transition event through the single ledger writer and returns either the new projection plus evidence sequence or a typed refusal. It does **not** submit a job, start the next stage, publish, implement, retry, or cancel as a side effect. Starting stage work remains a separate explicit existing product/run action after the transition is accepted.

Every transition in the target sequence requires Keith's explicit approval. IMPLEMENT additionally requires destination confirmation; Website GC `publish` remains a separate Keith click, GitHub/GitLab remains Gitur-first, Differentiator requires the anonymization gate, Docket filing remains Legal + Keith, UPS may remain blocked on Keith, and Crucible may return 501 when critics are unavailable.

### Runs/findings feed

- **Trigger:** mount, 10-second operational refresh, selected product/stage/filter change, or accepted job submission in an existing panel.
- **GETs:** `/jobs` is scheduler state; `/jukebox` supplies exact queue words and details after its contract is normalized; `/runs_ops` supplies operational folds; `/review` supplies blockers/approvals; `/work_orders?id=` opens explicit evidence.
- **State:** filters and selected run are client-only and survive refresh. Run state, product/stage binding, finding, output, and age are Core fields.
- **Empty/UNMEASURED:** no matching run is explicit empty. Historic untagged work is `UNATTRIBUTED`; absent output is `NO_SOURCE`; absent freshness is `UNMEASURED`.
- **Refusal paths:** `BROKE` and `FINDINGS` remain findings, `CLEAN` remains the only clean terminal word in this vocabulary, and no `DONE`, `FAILED`, retry, or cancel affordance is manufactured.

### Cost/estimate surface

- **Trigger:** mount/30-second spend refresh; product/run/seat change; explicit estimate calculation.
- **GETs:** `/spend` for authoritative rail accounting; `/model_rater` for rate-card estimates and seats; `/runs_ops` for any measured product token fold.
- **POST:** explicit calculate/reset uses `/model_rater/job_estimate`. Seat edits use `/model_rater/seat`. Spend-cap mutation remains in its existing gated panel and is not silently performed here.
- **State:** settled/reserved/headroom are spend; token/rate-card output is an estimate. They are labeled and stored separately.
- **Empty/UNMEASURED:** missing product attribution, tokens, model price, or rail is `UNMEASURED`. Only a measured numeric zero may display `0`.
- **Refusal:** banned/rotator seat refusals, bad estimate input, expired rails, RED breaker, and cap refusal remain visible and block the dependent action.

## 5. WO BREAKDOWN

Each work order is additive, keeps all existing panels, and must land green independently. The cDeck commands are run from `builds/cdeck`; where a Core module changes, its focused self-test is run before the two required cDeck suites. No work order is appearance-only.

| ID | Suggested agent | Size | One-sentence goal | Files touched | Contracts to keep | Test command | Done when |
|---|---|---:|---|---|---|---|---|
| PS-01 | gpt-5.6-sol | M | Freeze the Portfolio Studio response, stage-projection, typed-state, and transition schemas as executable contract tests on existing routes. | `cosmos/cosmos_profiles.py`, `tests/test_profiles.py`, `builds/cdeck/test_kdash_working.py`, `builds/cdeck/test_deck_features.py` | Legacy `profiles[]`, nine `stages[]`, `engine`, `does_not_start_motif`, and `does_not_publish` remain byte/meaning compatible; no new route. | `py -3.14 cosmos/cosmos_profiles.py --selftest && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Existing clients still receive the legacy fields and tests prove all new unbound live fields emit `UNMEASURED`, never inferred values. |
| PS-02 | gpt-5.6-sol | M | Restore the health snapshot called by the existing health route so Portfolio Studio can bind actions to an honest current verdict. | `cosmos/cosmos_health.py`, `cosmos/cosmos_service.py`, focused health tests | One Core, 10-second Core cache if retained, negative control stays RED, GET does not mutate. | `py -3.14 -m unittest tests.test_health && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | `GET /health` returns the measured HealthBoard fold and every error/RED survives unchanged to the client contract. |
| PS-03 | composer-2.5 | M | Normalize the existing jukebox fold around scheduler truth and its five legal state words while retaining compatibility aliases for current consumers. | `builds/cdeck/cosmos_jukebox_panel.py`, `cosmos/cosmos_service.py`, jukebox tests | `QUEUED/RUNNING/BROKE/CLEAN/FINDINGS`; report-never-retry; no cancel; existing `/jobs`; GET no mutation. | `py -3.14 -m unittest tests.test_jukebox && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | `/jukebox` exposes one documented jobs/counts shape, uncomposed state stays 503, and Gitur/Review/Runs consumers pass without text-derived stage guesses. |
| PS-04 | gpt-5.6-sol | L | Add the seven-product live projection to existing profile and runs-ops GETs by joining only tracker, ledger, scheduler, lease, and work-order evidence. | `cosmos/cosmos_profiles.py`, `cosmos/cosmos_runs_ops.py`, `cosmos/cosmos_service.py`, focused Core tests | Seven canonical ids; legacy nine-stage contract; one occupant/profile; untagged is `UNATTRIBUTED`; absent is `UNMEASURED`; no second store. | `py -3.14 cosmos/cosmos_profiles.py --selftest && py -3.14 -m unittest tests.test_runs_ops && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Each product returns a measured/bound stage fold or a typed non-measurement, with source sequence/time sufficient for the client to refuse inference. |
| PS-05 | gpt-5.6-sol | L | Implement optimistic, Keith-approved stage transitions as an extension of `POST /profiles`, with ledger evidence and no job-start side effect. | `cosmos/cosmos_profiles.py`, `cosmos/cosmos_service.py`, ledger/event schema, `tests/test_profiles.py`, stage-transition tests | Existing profile saves; no auto-MOTIF; Core-only writer; fencing/version check; health/tree/spend/product gates; Website no-publish. | `py -3.14 cosmos/cosmos_profiles.py --selftest && py -3.14 -m unittest tests.test_profiles tests.test_portfolio_transitions && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Legal adjacent transitions require an explicit Keith decision and emit ledger-bound evidence; stale, skipped, RED, unmeasured, or ungated requests refuse without queueing work. |
| PS-06 | grok-4.5 | L | Add product/stage attribution to new job, work-order, spend, and porosity evidence while leaving historic untagged records explicitly unattributed. | scheduler manifest/ledger modules, `cosmos/cosmos_spend.py`, `cosmos/cosmos_runs_ops.py`, `cosmos/cosmos_porosity.py`, related tests | Append-only ledger; existing job ids/states; rail spend authority; no command-text classification; old records remain readable. | `py -3.14 -m unittest tests.test_spend tests.test_runs_ops tests.test_porosity && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | New evidence carries validated canonical product/stage tags end-to-end and all unavailable product totals are `UNMEASURED`, not zero. |
| PS-07 | composer-2.5 | M | Introduce one client transport/store that independently refreshes and normalizes existing Portfolio GET folds without becoming an authority. | `builds/cdeck/ui/deck_portfolio_store.js`, `builds/cdeck/ui/header.js`, `builds/cdeck/ui/deck_more.html`, cDeck feature tests | Header `apiGet/apiPost`; bearer/Tauri behavior; existing tab hosts/panels/deep links; no direct pane `fetch`; partial failures isolated. | `cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Tests prove per-route freshness, stale last-good labeling, out-of-order response rejection, poll stop on unmount, and no synthesized authoritative field. |
| PS-08 | composer-2.5 | M | Build the seven-card portfolio board from the normalized store and wire selection without POST or stage movement. | `builds/cdeck/ui/deck_portfolio.js`, `builds/cdeck/ui/deck_tabs.js`, `builds/cdeck/ui/deck_more.html`, cDeck tests | All old panels remain; canonical catalog order; health RED; `NO_SOURCE`/`UNMEASURED`; profile selection is client-only. | `cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Exactly seven Core-catalog cards paint measured stage/run/cost data or explicit non-measurements, and selecting each card only changes detail context. |
| PS-09 | gpt-5.6-sol | L | Implement the eight-stage operator spine and per-stage detail against Core's explicit projection, including the legacy-nine disclosure and separate save/advance actions. | `builds/cdeck/ui/deck_portfolio_stages.js`, `builds/cdeck/ui/deck_profiles.js`, `builds/cdeck/ui/deck_studio.js`, cDeck tests | Exact eight target labels/order; legacy ids retained; SAVE never starts; no stage inference; current panels and Profile saves preserved. | `cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Bound projection paints eight stages; absent projection truthfully paints legacy nine plus `UNMEASURED`; only a fresh `READY_FOR_KEITH` response enables the confirmed advance packet. |
| PS-10 | composer-2.5 | M | Separate Runs ownership from the colliding Studio module and compose the bound runs/findings feed without losing filters, selection, polling, or exact state words. | `builds/cdeck/ui/deck_runs.js`, `builds/cdeck/ui/deck_studio.js`, `builds/cdeck/ui/deck_tabs.js`, `builds/cdeck/ui/deck_more.html`, cDeck tests | `paintRunsList`, row inspection, 10-second poll, filter/selection persistence, FINDINGS handling, no retry/cancel, existing Runs panel. | `cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Studio and Runs have distinct module identities, all old Runs pins pass, and untagged/no-output/error rows remain explicit. |
| PS-11 | composer-2.5 | M | Compose measured spend, product attribution, estimate, and seat controls into one cost surface without conflating estimates with ledger spend. | `builds/cdeck/ui/deck_portfolio_cost.js`, existing model-rater client module, `builds/cdeck/ui/deck_more.html`, cDeck tests | `/spend` authority; existing estimate/seat POSTs; caps/refusals; `UNMEASURED` never `$0`; existing Model Rater panel. | `cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | Measured spend, attribution, estimates, and caps remain separately labeled and every missing dimension/refusal is represented without fallback arithmetic. |
| PS-12 | grok-4.5 | L | Add cross-module contract coverage proving Portfolio Studio is additive, Core-bound, refusal-preserving, and incapable of auto-MOTIF. | `builds/cdeck/test_kdash_working.py`, `builds/cdeck/test_deck_features.py`, focused Core integration tests, contract fixtures | STUDIO pins; PROFILES pins; occupancy pins; all existing panels; off-limits modules untouched; no invented routes/history/states. | `py -3.14 -m unittest tests.test_profiles tests.test_portfolio_transitions tests.test_runs_ops && cd builds/cdeck && py -3.14 test_kdash_working.py && py -3.14 test_deck_features.py` | A full fixture with partial outages, RED health, unmeasured cost, refusal, findings, and one Keith-approved transition passes while asserting zero implicit job submits, transitions, retries, cancels, publishes, or second-Core calls. |
