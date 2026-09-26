ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Do not emit a unified diff.

CRITIQUE the blueprint draft below. You did not write it — review it
independently. For each tab's proposed approach, answer:

1. Does the proposed approach actually fit existing conventions
   (IIFE-only, apiGet/apiPost, documented GET/POST surface, tab order)?
2. Does it invent anything — a GET/POST, a file not in the Files: list,
   an assumption not grounded in the live slices provided?
3. Is the suggested job breakdown realistic for the assigned seat
   (Luna / GLM+Ling / GF38), or does it actually need GF38/escalation
   when it was assigned to a cheaper seat?
4. Flag ANY point where you would revise the approach before it becomes
   a real job — be specific, cite the exact blueprint section.

If the blueprint is sound as written, say so explicitly per tab. Do not
invent a critique to fill space.

Live slices are the cached system block. Blueprint draft follows.
This seat is GPT-5.6 Terra (Rule B substitute). Do not call Claude.

--- BLUEPRINT (Query 5) ---
# Non-authoritative cDeck completion blueprint

This is a planning roadmap only. It is not a diff, CREW/OUT submission, CCr disposal candidate, lease request, or merge authorization.

## Scope classification

### Confirmed incomplete or materially nonfunctional
- Studio
- Runs
- Review
- Recents / Sessions
- Open
- Forge
- Crucible
- Diligence
- Docket
- UPS
- Differentiator
- Website

### Cross-cutting defects affecting tabs
- Browser-served `/cdeck/` asset closure
- Model Rater re-initialization
- Profiles re-initialization and mount bookkeeping
- System CVM-rule conflict and displaced `downBanner`
- Settings measurement-label violations

### Not yet eligible for an implementation blueprint
Surfaces, Voice, Tools, and Clock remain **UNMEASURED**, primarily because `app.js` was not supplied. Their next step should be evidence collection, not speculative implementation.

---

# Cross-cutting prerequisite A — JavaScript parse recovery

## GOAL

Make the shared Studio/Runs/Review module parse successfully and install its public initializers before any tab-specific behavior is evaluated.

## CURRENT STATE

`builds/cdeck/ui/deck_studio.js` contains an extra closing `};` immediately after:

```js
window.deckOpenResearchCall = window.openStudioResearchCall;
```

This prevents the IIFE from parsing and prevents `window.initDeckStudio` from being installed.

## GAP

- Remove the unmatched closure.
- Add deterministic JavaScript syntax validation.
- Add a runtime smoke check for exported window initializers.
- Re-test all three tabs after the parser defect is corrected; their apparent implementation has not yet been proven in a browser.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_studio.js`
- Existing cDeck test files; exact suitable test file is **ASSUMPTION** until the live test layout is inspected.

Implementation outline:

1. Correct only the unmatched closure.
2. Add a deterministic check equivalent to:
   - `node --check builds/cdeck/ui/deck_studio.js`
3. Load the pane markup and scripts in a browser harness and assert:
   - `typeof window.initDeckStudio === "function"`
   - Studio, Runs, and Review can each be selected without a console exception.
4. Do not refactor the large module during this recovery job.

No new endpoint is needed.

## RISK NOTES

- A broad cleanup would make it difficult to distinguish parser recovery from behavioral changes.
- Existing occupancy string tests can pass while the JavaScript remains syntactically invalid.
- Studio, Runs, and Review should remain one cDeck product change, separate from any COSMOS Core Crucible change.

## SUGGESTED JOB BREAKDOWN

1. **Parser correction and syntax gate** — small — Luna.
2. **Browser initialization smoke test** — medium — GLM+Ling pair.
3. **Post-recovery UI correctness check** — medium — GF38.

---

# Cross-cutting prerequisite B — browser `/cdeck/` asset closure

## GOAL

Ensure browser-served `/cdeck/` can load the same tab shell and pane modules required by the native frontend.

## CURRENT STATE

`cosmos/cosmos_service.py::_CDECK_UI_NAMES` and `_CDECK_ROUTES` expose only five cDeck files. The attached `header.js` dynamically loads `deck_more.html`, `deck_tabs.js`, and multiple pane scripts that are not served by the allowlist.

## GAP

- Inventory every static asset referenced by `index.html`, CSS, service worker, and dynamic script insertion.
- Extend the exact-match static allowlist without introducing path-derived filesystem access.
- Confirm content types.
- Confirm that no data or bearer material is exposed.
- Verify browser mode separately from Tauri mode.

Several required files were unavailable in the deep dive:

- `builds/cdeck/ui/index.html`
- `builds/cdeck/ui/app.js`
- `builds/cdeck/ui/app.css`
- `builds/cdeck/ui/sw.js`

## PROPOSED APPROACH

Files likely involved:

- `cosmos/cosmos_service.py`
- Existing service/static-route tests
- Possibly cDeck browser smoke tests

Implementation outline:

1. Build an explicit asset manifest from the live frontend.
2. Add each required filename to `_CDECK_UI_NAMES`.
3. Add exact routes under `/cdeck/`; never derive a disk path from request text.
4. Include local audio, image, CSS, and module assets only if the live frontend references them.
5. Test:
   - every declared route returns 200 and the expected content type;
   - an undeclared path returns 404;
   - traversal attempts remain refused;
   - `/cdeck/` reaches the tab shell without asset 404s.

No new API endpoint is needed. This is static-shell completion.

## RISK NOTES

- This is a COSMOS Core PR and must not be mixed with cDeck product fixes.
- The service worker may maintain a second asset list; it must be inspected rather than guessed.
- Wildcard static serving would violate the exact-match security architecture.

## SUGGESTED JOB BREAKDOWN

1. **Live asset inventory** — small investigation — Luna.
2. **Exact-route Core implementation and tests** — medium/hard Python — GF38.
3. **Browser-mode smoke verification** — medium — GLM+Ling pair.

---

# 1. Studio

## GOAL

Provide a functioning nine-stage MOTIF configuration workspace whose reads, saves, research calls, and graph interactions execute without parser or transport failures.

## CURRENT STATE

The markup and intended implementation include the MOTIF graph, persistent stage forms, centralized API calls, research-call FILE/INGEST, and Crucible controls. The entire initializer is currently blocked by the `deck_studio.js` syntax failure.

## GAP

- Complete prerequisite A.
- Verify each GET painter against real response bodies.
- Verify every SAVE preserves operator edits across polling.
- Verify drag/drop graph persistence.
- Decouple Studio’s Crucible button from the invalid synchronous Core execution path.
- Add browser tests for tab initialization, stage switching, save success, and visible refusal handling.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_studio.js`
- `builds/cdeck/ui/deck_more.html`
- Existing cDeck UI tests

After parser recovery:

1. Exercise Studio with fixture responses for `/studio`, `/model_rater`, `/rails`, and `/research_call`.
2. Confirm polling does not replace focused inputs or discard dirty drafts.
3. Keep API access through the central transport supplied by `header.js`.
4. Change the Crucible UI expectation to submission/queued status once the Core handler is corrected; do not wait synchronously for a completed round.
5. Display Core-returned refusal kinds without relabeling them as success.

No new endpoint is needed for the existing Studio functions.

## RISK NOTES

- Studio is large; split recovery, behavioral fixes, and UI polish.
- Crucible Core changes belong in a separate COSMOS PR.
- Do not allow Studio to execute or dispose crew output directly.
- A SAVE remains configuration only and must not silently start MOTIF.

## SUGGESTED JOB BREAKDOWN

1. **Studio post-parser fixture harness** — medium — GLM+Ling.
2. **Dirty-form and polling preservation fixes** — medium — Luna.
3. **Graph interaction/browser correctness** — medium — GF38.
4. **Crucible queued-status UI adaptation** — small, after Core contract is settled — Luna.

---

# 2. Runs

## GOAL

Deliver a live, navigable queue and operations view with accurate status, stale reporting, job inspection, and explicit new-job filing.

## CURRENT STATE

The intended implementation includes `/jukebox`, `/jobs`, `/runs_ops`, state and sort chips, keyboard navigation, dynamic operation panes, and two-click new-job filing. It is inert because `deck_studio.js` does not parse.

`panel-events` also depends on the unavailable `app.js`.

## GAP

- Complete prerequisite A.
- Verify `/jukebox` and `/jobs` fallback behavior with fixture and live bodies.
- Verify dynamic `run-op-*` panes do not duplicate across polls.
- Verify scroll and selection persistence.
- Inspect and test `panel-events` after obtaining `app.js`.
- Confirm new-job POST receipts and failures remain visible.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_studio.js`
- `builds/cdeck/ui/app.js` after supplied
- Existing cDeck UI tests

Implementation outline:

1. Add fixture cases for unread queue, empty queue, active rows, stale rows, and last-good-read state.
2. Assert no cancel/retry/hold control is introduced.
3. Exercise keyboard navigation and “show more.”
4. Assert the first click only arms new-job creation and the second files it.
5. Verify operation panes update existing elements rather than accumulating duplicates.

No new endpoint is needed.

## RISK NOTES

- `/jobs` does not contain the richer `/jukebox` fields; missing data must remain `UNMEASURED`.
- A stale job is reported, never automatically retried.
- Events behavior cannot be changed until `app.js` is reviewed.

## SUGGESTED JOB BREAKDOWN

1. **Runs fixture and initialization tests** — medium — GLM+Ling.
2. **Dynamic-pane and polling correctness** — medium — Luna.
3. **Keyboard/scroll/browser UI verification** — medium — GF38.
4. **Events subpane follow-up** — size unknown — hold until `app.js` is supplied.

---

# 3. Review

## GOAL

Provide a functioning read-only HITL dashboard for spending refusals, blockers, required logins, and work-product review.

## CURRENT STATE

The intended `paintReview()` reads `/review`, supports time-window chips, renders four review areas, and links relevant jobs to Runs. It is inert because the shared script does not parse.

## GAP

- Complete prerequisite A.
- Verify all four response sections against Core fixture bodies.
- Make observational scope explicit: the pane does not possess an annotation or approval POST.
- Test window switching and Runs navigation.
- Test partial and failed reads without displaying false-empty states.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_studio.js`
- `builds/cdeck/ui/deck_more.html`
- Existing cDeck UI tests

Implementation outline:

1. Add fixtures for pending spend widen, FINDINGS, stale work, required login, and empty catalog.
2. Keep actions as navigation to existing surfaces.
3. Add concise UI text explaining that disposition occurs through CCr/Gitur, not through a hidden Review write.
4. Preserve legal-file exclusion.

No new endpoint is currently justified.

## RISK NOTES

- Do not invent an annotation queue or approval POST.
- “No rows” must be distinguished from “GET failed.”
- Review must not become a second disposal path.

## SUGGESTED JOB BREAKDOWN

1. **Review painter fixture tests** — small/medium — Luna.
2. **Error/empty-state and navigation verification** — medium — GLM+Ling.
3. **Final pane correctness review** — small — GF38.

---

# 4. Recents / Sessions

## GOAL

Provide a reliable Sessions workspace whose list, transcript, session tools, and Session Kit preserve edits and use only measured session sources.

## CURRENT STATE

`deck_session_kit.js` implements `/session_kit`. The session list, transcript, stripper, and suite functions are owned by unavailable `app.js`.

Before the first successful GET, `kit()` returns a new default object on every call. COS checkbox changes can therefore mutate a temporary object that is not later posted.

The markup also includes `navSessFilter`, which conflicts with the no-hunt-box rule.

## GAP

- Persist one default Session Kit object in state.
- Harvest all checkbox values before POST as defensive synchronization.
- Inspect the remaining session implementation in `app.js`.
- Decide how to replace or explicitly approve the session search box.
- Add tests for pre-GET edits, failed GET, successful GET, and SAVE.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_session_kit.js`
- `builds/cdeck/ui/deck_more.html`
- `builds/cdeck/ui/app.js` after supplied

Implementation outline:

1. Initialize `state.kit` once instead of constructing disposable defaults.
2. On SAVE, read COS checkbox state from the DOM before building the POST body.
3. Test edits made before GET resolution and after GET failure.
4. For the session filter:
   - preferred rule-compliant option: use chips derived from `/recents` locations and bounded recent rows;
   - **ASSUMPTION:** a text filter may still be operationally necessary for a large session corpus. If Keith approves that exception, document and test it rather than silently retaining it.
5. Review transcript and suite actions only after `app.js` is available.

No new endpoint is needed.

## RISK NOTES

- Removing a useful session filter without a replacement could make large histories unusable.
- Do not scrape AppData or invent an OpenWork port.
- Session-tools expansion must stay within the documented `/session_tools` contract.

## SUGGESTED JOB BREAKDOWN

1. **Session Kit state-loss fix and unit test** — small — Luna.
2. **Recents owner-code review after `app.js` supply** — medium — GLM+Ling.
3. **Search-control rule disposition and UI verification** — medium — GF38.

---

# 5. Open

## GOAL

Make Open consistently focus an existing OpenWork instance without spawning one when none is live.

## CURRENT STATE

The Rust commands focus and snap an existing process, but `open_openwork()` and `open_orc()` launch `OpenWork.exe` when no process exists. This conflicts with the absolute no-spawn rule.

Some Open-tab binding logic remains unavailable in `app.js`.

## GAP

- Reconcile implementation with the binding rule.
- Replace launch behavior with a typed refusal/status response.
- Remove or bound synchronous retry sleeps where practical.
- Verify browser and native messages.
- Inspect `app.js` bindings.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/src-tauri/src/lib.rs`
- `builds/cdeck/ui/header.js`
- `builds/cdeck/ui/app.js` after supplied
- Rust tests

Implementation outline:

1. When no `OpenWork.exe` PID exists, return a structured `refused` or `idle` record; do not launch.
2. Preserve focus and snap behavior for a live process.
3. Update UI wording to distinguish:
   - focused;
   - live but focus failed;
   - no live OpenWork, launch refused.
4. Review the 20×150 ms snap retry loop. If asynchronous waiting is unavailable, reduce blocking or move the operation off the UI-sensitive path.
5. Add Rust tests that the no-PID decision refuses rather than launches.

No new endpoint is needed.

## RISK NOTES

- This changes behavior users may currently rely on, so Keith should explicitly approve enforcement of the absolute rule.
- Do not replace native focus with an iframe or web launch.
- Tauri changes remain a cDeck product PR.

## SUGGESTED JOB BREAKDOWN

1. **No-spawn decision and Rust tests** — medium — GLM+Ling.
2. **Header/Open status messaging** — small — Luna.
3. **Native responsiveness verification** — medium — GF38.

---

# 6. Forge

## GOAL

Make Forge an accurate control and visibility surface for the approved crew pipeline without becoming a second executor or live-tree writer.

## CURRENT STATE

Forge supports the CCr seat, adversarial seat configuration, vias, model assignments, and token estimates. It does not demonstrate dispatch into CREW/OUT, deterministic gating, aggregation, or CCr disposal.

Its sample/default models also reflect older Grok/Composer configurations rather than the package’s Luna, GLM+Ling, and GF38 ladder.

## GAP

- Inspect the native coding/session behavior in `app.js`.
- Separate generic profile configuration from the package-specific crew roster.
- Determine whether Forge should only display pipeline state or submit existing work-order commands.
- Add status visibility for candidate output, gate verdict, and CCr disposition if those facts already exist in current GET bodies.
- Do not invent pipeline APIs.

## PROPOSED APPROACH

Files likely involved:

- `builds/cdeck/ui/deck_forge.js`
- `builds/cdeck/ui/deck_more.html`
- `builds/cdeck/ui/app.js` after supplied

Implementation outline:

1. First inventory the existing `/work_orders`, `/runs_ops`, `/gitur`, and `/model_rater` fields that can evidence the pipeline.
2. Render only facts those routes already provide.
3. Update configurable examples to the approved coding ladder where appropriate:
   - Luna for routine work;
   - GLM and Ling always represented as a pair;
   - GF38 escalation;
   - Terra excluded from coding.
4. Keep CCr as the only disposal actor.
5. If no current route exposes local gate verdicts, explicitly leave that visibility `UNMEASURED`.

**Explicit endpoint recommendation:** none at this stage. A new gate-status endpoint may eventually be useful, but it is not justified until existing `/work_orders`, `/runs_ops`, and `/gitur` bodies are inspected.

## RISK NOTES

- Do not turn blueprint text directly into a Forge job.
- Do not add a client-side dispatch path that bypasses CREW/OUT or the local gate.
- Package-specific roster changes must not accidentally rewrite global product defaults without approval.
- Profiles re-initialization can displace mounted Forge panels and should be fixed first.

## SUGGESTED JOB BREAKDOWN

1. **Forge evidence-surface inventory** — investigation — Luna.
2. **Roster and paired-seat correctness** — medium — GLM+Ling.
3. **Pipeline visibility UI using existing routes** — medium/large — GF38.
4. **Native session controls follow-up** — hold until `app.js` is supplied.

---

# 7. Crucible

## GOAL

Make Crucible submit a critic-round job that is claimed and executed only by the runner pool, with the UI observing its eventual result.

## CURRENT STATE

The profile UI posts to the documented `/crucible` route. The Core handler currently submits, calls `kernel.sched.claim_next()`, and executes `Crucible.run_round()` inside the HTTP request.

It may execute without claiming the submitted job and may claim a different queued job.

## GAP

- Remove HTTP-side claiming.
- Remove critic execution from the request thread.
- Define a runner-recognized Crucible job command using the existing scheduler.
- Ensure only the pool claims it.
- Return a queued job ID promptly.
- Ensure the runner writes a result artifact and finishes the correct job.
- Update UI status expectations and tests.

## PROPOSED APPROACH

This requires separate product boundaries.

### COSMOS Core files likely involved

- `cosmos/cosmos_service.py`
- `cosmos/cosmos_runner.py` or an existing command adapter, exact location **ASSUMPTION**
- `cosmos/cosmos_crucible.py`
- Scheduler/runner tests

Core sequence:

1. Validate sources and composed critic availability.
2. Submit one typed existing-format job on the Crucible lane.
3. Return `201` with `job_id` and queued state.
4. Let the pool’s normal `claim_next()` path claim it.
5. Execute the round through a runner adapter.
6. Finish the same claimed job as CLEAN, FINDINGS, or BROKE.
7. Persist output under the established work role.

### cDeck files likely involved

- `builds/cdeck/ui/deck_profiles.js`
- `builds/cdeck/ui/deck_studio.js`

UI sequence:

1. Display the returned job ID.
2. Offer “open Runs.”
3. Do not imply completion from the initial POST.

No new HTTP endpoint is needed.

## RISK NOTES

- Core and cDeck changes must be separate PRs.
- This touches scheduling and concurrency; GF38 escalation is appropriate.
- Do not run `cosmos_run.py` beside the pool.
- The runner must verify that it completes only a job it claimed under its own worker identity.
- Client timeout increases would hide the architectural defect and are not the solution.

## SUGGESTED JOB BREAKDOWN

1. **Core design/job-envelope specification** — design review — GF38.
2. **Pool-only Crucible runner implementation and concurrency tests** — large/hard Python — GF38, maximum two attempts.
3. **Core HTTP submit-only handler** — medium — GLM+Ling pair.
4. **cDeck queued-result UI adaptation** — small — Luna.
5. **End-to-end submit/claim/result verification** — medium — GF38.

---

# 8. Diligence

## GOAL

Provide an operational deal-diligence workflow that ingests named evidence, runs independent Bull/Bear/Risk analysis, and produces a measured review artifact.

## CURRENT STATE

The tab supplies named seat cards, a research-call jump, generic MOTIF forms, and `/profiles` configuration save. Seat clicks insert labels into a roles field.

No domain execution or result artifact is evident.

## GAP

- Define evidence inputs and output artifact schema.
- Define how Bull, Bear, and Independent Risk seats map to approved model/via assignments.
- Define execution, disagreement handling, and completion evidence.
- Add result/history UI.
- Add tests around safety, missing evidence, and contested output.

## PROPOSED APPROACH

Phase 1 should remain within existing surfaces:

1. Use `/profiles` for saved setup.
2. Use `/research_call` for FILE/INGEST envelopes.
3. Use `/jobs` only if an existing runner command can execute the workflow.
4. Display returned artifacts through existing work-order or review surfaces.

**Explicit endpoint recommendation:** a new diligence endpoint is not approved by this blueprint. If no existing job command can execute the domain workflow, prepare a separate architecture proposal defining the minimum command/runner contract before requesting any endpoint.

## RISK NOTES

- **ASSUMPTION:** Keith wants execution rather than a configuration-only skin.
- Evidence sources and legal/corporate boundaries must be specified before coding.
- Do not invent scores or mark risk analysis complete without an emitted artifact.
- Keep independent lanes isolated until adjudication.

## SUGGESTED JOB BREAKDOWN

1. **Domain contract and artifact schema** — design job — GF38.
2. **Existing-route feasibility spike** — medium — GLM+Ling.
3. **Profile UI/result presentation** — medium — Luna.
4. **Execution adapter, only after contract approval** — large — GF38.

---

# 9. Docket

## GOAL

Provide a safe IP-analysis workflow that produces prior-art and claim-analysis artifacts without performing USPTO filing actions.

## CURRENT STATE

The tab contains Applicant, Examiner, and Prior Art roles, LEGAL_OMITTED/USPTO warnings, research-call navigation, and generic profile setup.

No IP-specific execution or result is implemented.

## GAP

- Define allowed corpus and evidence sources.
- Define prior-art result and claim-chart artifact formats.
- Define Applicant/Examiner disagreement workflow.
- Add result display and measured completion state.
- Preserve the prohibition on filing and USPTO clicks.

## PROPOSED APPROACH

1. Keep `/profiles` for setup.
2. Use `/research_call` for explicitly named source envelopes.
3. Use existing work-order/job infrastructure only after an approved IP artifact contract exists.
4. Surface outputs through Review or work-order detail rather than inventing a Docket-specific GET.

**Explicit endpoint recommendation:** none now. Any proposed Docket API requires separate architectural approval and evidence that generic jobs/work orders are insufficient.

## RISK NOTES

- Legal material remains LEGAL_OMITTED from this package.
- Do not imply legal advice, filing completion, or verified prior art without source-bound evidence.
- USPTO remains Keith’s action.
- **ASSUMPTION:** claim charts and office-action analysis are desired outputs; Keith must confirm.

## SUGGESTED JOB BREAKDOWN

1. **Allowed-scope and artifact specification** — design — GF38.
2. **Research-call handoff validation** — small/medium — Luna.
3. **Applicant/Examiner/Prior-Art UI workflow** — medium — GLM+Ling.
4. **Execution adapter after approval** — large — GF38.

---

# 10. UPS

## GOAL

Provide an operational physics-analysis workflow with measured spectra inputs and an explicitly bound UPS-JUDGE adjudication artifact.

## CURRENT STATE

The tab names Spectra and UPS-JUDGE, provides generic MOTIF configuration, and links to research-call FILE/INGEST. The code explicitly says the physics rebuild is not yet implemented.

## GAP

- Define accepted spectra/input formats.
- Identify the real UPS-JUDGE callable or keep it NAMED.
- Define analysis and adjudication artifacts.
- Add input validation, execution, and result display.
- Add runtime-binding evidence for the model/tool that actually performed judging.

## PROPOSED APPROACH

1. Keep UPS-JUDGE displayed as NAMED until a live callable is proven.
2. Use `/profiles` and `/research_call` only for configuration and evidence intake.
3. Prepare a domain contract for spectra analysis before adding execution.
4. If an existing tool under `/tools_kit` proves callable, route through the approved job runner rather than a direct pane invocation.

**Explicit endpoint recommendation:** none until the physics tool is identified. Do not invent `/ups` or `/ups_judge`.

## RISK NOTES

- The deep dive explicitly confirms the runtime is absent; UI polish cannot make this complete.
- Do not relabel DOI or citation verification as physics judging.
- **ASSUMPTION:** spectra files can be represented through existing named-file ingestion; blob handling was not verified.

## SUGGESTED JOB BREAKDOWN

1. **Physics input/output contract** — design — GF38.
2. **Callable inventory against `/tools_kit`** — investigation — GLM+Ling.
3. **Safe intake/result UI** — medium — Luna.
4. **Execution adapter only after callable proof** — large — GF38.

---

# 11. Differentiator

## GOAL

Provide a gated clinical-opinion workflow in which anonymization is enforced before independent lanes receive data.

## CURRENT STATE

The tab names Clinical A, Clinical B, and Anonymize. These are currently cards and generic configuration fields. There is no anonymization implementation, clinical execution, result artifact, or research-call jump.

## GAP

- Define a non-PHI test input format.
- Implement or bind a proven anonymization gate.
- Prevent clinical dispatch unless the gate emits success.
- Define two independent opinion artifacts and adjudication behavior.
- Add evidence/result display.
- Add a safe research/evidence intake path if approved.

## PROPOSED APPROACH

1. Treat Anonymize as a mandatory gate, never as a model seat.
2. Keep all early development on synthetic, non-PHI fixtures.
3. Reuse `/profiles` for configuration.
4. Use existing job/work-order machinery only after a gate artifact contract exists.
5. Add a research-call jump only if Keith confirms it is appropriate for this profile.

**Explicit endpoint recommendation:** no clinical endpoint should be added without a dedicated privacy/security design review. If existing jobs cannot express gate-dependent execution, stop and submit a design question.

## RISK NOTES

- Highest privacy risk among the profile tabs.
- No PHI should enter fixtures, logs, prompts, or screenshots.
- Client-side gating alone is insufficient; enforcement must occur in the executor.
- Model independence must be real, not two labels pointing to one family.

## SUGGESTED JOB BREAKDOWN

1. **Privacy and gate contract** — blocking design job — GF38.
2. **Synthetic fixture and refusal tests** — medium — GLM+Ling.
3. **Profile UI and gate-state presentation** — medium — Luna.
4. **Executor enforcement** — hard Python, after approval — GF38.

---

# 12. Website

## GOAL

Produce a staged, owned website artifact with preview and accessibility evidence while never publishing automatically.

## CURRENT STATE

The tab provides Copy/Layout/a11y seats, hosting and WordPress stack cards, generic MOTIF setup, research-call navigation, destination selection, and `/profiles` SAVE. Selecting publish is safely converted back to staged.

No site generation, staging upload, preview, accessibility run, or artifact harvest is present.

The stack cards use `data-stack`, while the shared click handler reads `data-seat`, so their clicks provide only visual selection.

## GAP

- Fix stack-card selection semantics.
- Define the staged website artifact and destination contract.
- Add generation through an approved job/tool path.
- Add preview and accessibility-result presentation.
- Preserve `publish:false` and Keith-only publication.
- Verify WordPress/cPanel support rather than assuming credentials or APIs.

## PROPOSED APPROACH

1. Correct stack-card handling so `data-stack` is processed independently from seat cards.
2. Save selected stack configuration through the existing `/profiles` engine if its schema supports it; otherwise prepare a schema proposal rather than silently dropping it.
3. Identify a real site generator or existing tool through `/tools_kit`.
4. Generate only into a staged destination.
5. Present:
   - artifact path;
   - preview location;
   - accessibility result;
   - explicit “not published” state.
6. Leave cPanel/WordPress deployment as a staged or Keith-click operation.

**Explicit endpoint recommendation:** none initially. If artifact staging cannot be represented through jobs/work orders and existing profile destinations, submit a separate minimal API proposal.

## RISK NOTES

- Do not turn informational vendor cards into claims of live integration.
- Do not store credentials in profile state.
- Do not publish.
- NameCheap and CloudFlare are not interchangeable with a site deployment target.
- **ASSUMPTION:** a static staged artifact is an acceptable first functional milestone.

## SUGGESTED JOB BREAKDOWN

1. **Stack-card interaction fix** — small — Luna.
2. **Website artifact/destination contract** — design — GF38.
3. **Existing tool inventory and generation spike** — medium — GLM+Ling.
4. **Staged preview and a11y UI** — medium/large — GF38.
5. **No-publish regression tests** — small — Luna.

---

# Important supporting remediation tracks

These are not separate incomplete tabs in every case, but they block reliable completion.

## Model Rater idempotent initialization

- **Goal:** one listener per control regardless of repeated `initModelRater()` calls.
- **Approach:** move closure state to a persistent module-level object or add a one-time binding guard while allowing explicit reloads.
- **Proposed test:** initialize three times, click once, observe one POST.
- **Suggested job:** medium, Luna; cross-check GLM+Ling.

## Profiles mount bookkeeping

- **Goal:** preserve one shared `park` map and safely return mounted panels.
- **Approach:** make initialization idempotent and store mount placeholders in persistent module state.
- **Proposed test:** initialize, mount Forge, initialize again, leave Profiles, and assert every element returns to its original placeholder.
- **Suggested job:** medium, GF38 due to DOM ownership complexity.

## System rule cleanup

- **Goal:** resolve the prohibited CVM surface and keep `downBanner` visible.
- **Approach:** Keith must first decide whether CVM is removed, staged elsewhere, or the binding rule is revised. Assign `downBanner` outside the tab sweep or to a persistent shell location.
- **Suggested jobs:** decision first; then small/medium cDeck job, Luna.
- No new endpoint is needed.

## Settings measurement corrections

- **Goal:** display only measured identity and label Core uptime as uptime, not subscription hours.
- **Approach:** replace hardcoded Account with `UNMEASURED` unless Core supplies identity; remove uptime from subscription length or label it “Core uptime.”
- **Suggested job:** small, Luna.
- **Proposed test:** missing fields remain `UNMEASURED`.

---

# Evidence-collection jobs for UNMEASURED tabs

Before planning Surfaces, Voice, Tools, or Clock implementation:

1. Supply and inspect:
   - `builds/cdeck/ui/app.js`
   - `builds/cdeck/ui/index.html`
   - `builds/cdeck/ui/app.css`
   - `builds/cdeck/ui/sw.js`
   - `builds/cdeck/src-tauri/src/main.rs`
   - `builds/cdeck/src-tauri/Cargo.toml`
2. Run deterministic JavaScript syntax checks.
3. Capture representative live GET bodies.
4. Run the occupancy test and record its actual result.
5. Execute a browser/Tauri tab smoke test.

Suggested as one investigation package for **GF38**, with no code change unless a specific evidence-bound defect is found.

---

# Recommended sequencing if Keith approves items

1. Parser recovery for Studio/Runs/Review.
2. Profiles and Model Rater initialization fixes.
3. Recents Session Kit state-loss fix.
4. Open no-spawn decision and implementation.
5. Crucible Core submit-only architecture, in a separate COSMOS PR.
6. Crucible cDeck queued-status adaptation.
7. Browser `/cdeck/` exact asset closure, in a separate COSMOS PR.
8. Supply missing files and reclassify UNMEASURED tabs.
9. Approve domain contracts individually for Diligence, Docket, UPS, Differentiator, and Website.
10. Convert only approved pieces into normal CREW/OUT job specifications.

No blueprint text should itself enter the gate, receive a lease, or be submitted as a code job.