# cDeck - Motif stage-5 critique (oa-api)

## Verdict

**No — the supplied sample does not demonstrate delivery of the cDeck specification or the later Keith STAGE-5 requirements.** It establishes a plausible Tauri packaging/configuration skeleton and documents a subset of the v1 dashboard, but the actual Rust command implementation and all UI source are absent from the sample. Therefore the required functional-control surfaces cannot be verified and must be treated as **UNKNOWN**, not assumed present.

## HIGH

1. **Required control APIs are absent from the documented client contract**
   - **File/symbol:** `README.md` — “What it talks to” table
   - **Defect:** The table documents only:
     - GET status/health/spend/jobs/rails/makers/events
     - POST `/api/v1/command`
     
     It omits required SPEC APIs:
     - `GET /api/v1/audit`
     - `POST /api/v1/jobs {command, priority}`
     - `POST /api/v1/voice {transcript, session_id?, confirm_id?}`
   - **Impact:** The documented deck cannot provide the required Audit panel, functional Jukebox/job submission control, or integrated CVM control using the required dedicated endpoints.
   - **Status:** The actual implementation may contain these calls, but that is **UNKNOWN** because `src-tauri/src/*` and `ui/*` are not supplied. As written, the documented contract is materially incomplete versus `SPEC.md`.

2. **Keith-required STAGE-5 feature set is asserted but not evidenced**
   - **Files/symbols:** `FEATURES_KEITH.md`; `src-tauri/tauri.conf.json` → `bundle.longDescription`
   - **Defect:** Keith requires functional, not merely visual, support for:
     - per-rail/per-node budget setting and adjustment;
     - Jukebox controls;
     - draggable node topology;
     - batteries/health/quota indicators;
     - measured token caps and speed/latency per node/channel;
     - controls for nodes, channels, rails, and surfaces;
     - CVM control;
     - every KDash feature plus more.
     
     The bundle description claims these features exist, but the supplied implementation contains no UI source or backend command handlers to substantiate any of them.
   - **Impact:** This is a release-integrity defect: packaged-product metadata claims a feature set that cannot be reviewed or verified from the supplied code.
   - **Status:** **UNKNOWN** whether implemented elsewhere; not demonstrated by this sample.

3. **No evidence of the required Rust HTTP proxy command**
   - **Files/symbols:** `README.md` → `api_request`; expected backend implementation absent from sample
   - **Defect:** README says all COSMOS HTTP is proxied through a Rust `api_request` command with hard timeout. However, no `src-tauri/src/main.rs`, `src-tauri/src/lib.rs`, command registration, URL validation, timeout construction, authorization-header handling, or persistent-config implementation is supplied.
   - **Impact:** Core requirements depend on this: CORS isolation, 8-second down-server behavior, bearer token session handling, server-URL persistence, and every API panel.
   - **Status:** **UNKNOWN**, not a claim that it does not exist. The supplied material cannot establish that the app can contact COSMOS at all.

4. **No evidence of append-only event-feed correctness**
   - **Files/symbols:** `README.md` — `/api/v1/events?since_seq=N`; expected UI/event cursor implementation absent
   - **Defect:** The frozen-dashboard scar requirement is behavioral: preserve a monotonic cursor, request only later sequence numbers, avoid replaying old events, and reset only when the server changes. Documentation states this behavior, but no implementation is provided.
   - **Impact:** A standard polling implementation can easily duplicate, reorder, or refetch historical events; the requirement cannot be accepted based on prose alone.
   - **Status:** **UNKNOWN**.

## MEDIUM

1. **README feature inventory is stale/incomplete relative to the declared bundle**
   - **Files/symbols:** `README.md` opening description and API table; `src-tauri/tauri.conf.json` → `bundle.longDescription`
   - **Defect:** README describes Status, Health, Spend, Jobs, Rails, Makers/CREATE, command bar, and live feed. The bundle description additionally claims Spend control, Jobs/Jukebox, Audit, Tools, draggable node map, batteries, caps/speeds, and CVM voice.
   - **Impact:** Users and reviewers receive contradictory scope statements. The README is the primary operational documentation but omits major claimed functionality and required endpoints.
   - **Fix:** Make README’s panel/API/control inventory authoritative and consistent with the shipped product. Explicitly identify whether each control is backed by `/jobs`, `/command`, `/voice`, or another supported COSMOS API.

2. **Spend-control requirement lacks a documented write/control contract**
   - **Files/symbols:** `FEATURES_KEITH.md` → “Spend control”; `SPEC.md` API list; `README.md` API table
   - **Defect:** Requirements demand adjustable per-rail/per-node budgets, caps, thresholds, and headroom. The documented spend API is read-only (`GET /api/v1/spend`), and no mutation endpoint or command grammar is documented for changing spend policy.
   - **Impact:** A display of spend/headroom does not satisfy “ability to set/adjust them.” The implementation might route changes through POST `/command`, but no such mapping, validation, confirmation behavior, or response handling is documented.
   - **Status:** Functional implementation is **UNKNOWN**; the interface contract/documentation is insufficient.

3. **“Every panel shows measured age” is not verifiable, especially for new required panels**
   - **Files/symbols:** `SPEC.md` → Panels/non-negotiables; `README.md` → “Every panel shows measured age”
   - **Defect:** The initial seven panels are named, but the later claimed/required Audit, Tools, Node Map, Batteries, Caps & Speeds, Jukebox, and CVM surfaces are not covered by an age/data-freshness contract.
   - **Impact:** New panels may regress the explicit anti-frozen-dashboard requirement while the original panels comply.
   - **Status:** **UNKNOWN** absent UI/source.

4. **No documented honest handling for subscription-pool spend data**
   - **Files/symbols:** `FEATURES_KEITH.md` → Spend control note
   - **Defect:** Keith specifically requires Claude/Grok subscription pools to be represented as “UI-only / human-posted” honestly. Neither `README.md` nor `SPEC.md` explains labeling, source attribution, edit workflow, freshness, or distinction from measured COSMOS spend.
   - **Impact:** The deck could present manually entered subscription estimates as live measured telemetry, directly violating the requirement.
   - **Status:** Implementation behavior is **UNKNOWN**; required data semantics are undocumented.

## LOW

1. **Product metadata overclaims functionality**
   - **File/symbol:** `src-tauri/tauri.conf.json` → `bundle.longDescription`
   - **Defect:** The installer description presents advanced features as fact: “Spend control, Jobs/Jukebox, Rails, Makers, CREATE, Audit, Tools, a draggable node map, batteries, caps and speeds, CVM voice…”
   - **Impact:** This is user-visible during installation and is stronger than the evidence supplied. It should not claim unverified/nonfunctional controls.
   - **Fix:** Either provide the corresponding implementation/tests or change wording to only shipped and verified functionality.

2. **No evidence that CI proves installable artifacts**
   - **Files/symbols:** `README.md` → GitHub Actions claims; referenced `.github/workflows/build.yml` not supplied
   - **Defect:** README claims CI builds MSI/NSIS artifacts and uploads them, but the workflow itself and any CI result are not part of the sample.
   - **Impact:** Build/install compliance with the SPEC CI requirement cannot be assessed.
   - **Status:** **UNKNOWN**; not evidence that CI is absent or failing.

3. **No supplied evidence of API-shape compatibility**
   - **Files/symbols:** `SPEC.md` → “read `cosmos_service.py` for exact shapes”; expected API parsing code absent
   - **Defect:** The spec requires integration against exact COSMOS response/request shapes. No parsers, request DTOs, response handling, or fixtures are supplied.
   - **Impact:** Endpoint names alone do not establish compatibility, particularly for jobs, audit, events sequencing, voice sessions/confirmation, rails probes, and maker kinds.
   - **Status:** **UNKNOWN**.

## What is positively evidenced

- Tauri 2 project configuration exists.
- Windows MSI and NSIS bundle targets are configured.
- A static frontend directory is configured as `frontendDist`.
- The intended architecture is Rust-proxied COSMOS HTTP rather than browser-side direct calls.
- The intended server URL, optional bearer handling, measured-age display, and graceful-down-server behavior are documented.

Those are useful foundations, but they are not evidence that the required dashboard/control behavior has been implemented.

## Acceptance conclusion

**Reject as demonstrated-complete.** The sample supports acceptance only of the project/configuration scaffold and stated intent. To assess delivery, provide at minimum:

1. `src-tauri/src/lib.rs` / `main.rs` and all IPC command handlers;
2. all `ui/` HTML/JS/CSS;
3. the CI workflow and a successful Windows build artifact/result;
4. tests or runnable evidence for event cursor monotonicity, timeout/down-server handling, URL persistence/token non-persistence, and each POST control path;
5. a feature-to-control/API matrix covering every Keith requirement and KDash-parity item.