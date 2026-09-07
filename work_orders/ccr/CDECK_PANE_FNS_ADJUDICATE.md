# Adjudication — extra-pane functions (MOTIF CONSENSUS)

**DEFINE:** `DEFINE_CDECK_PANE_FNS.md`
**Takes:** Cursor draft PR #31 body; GEM 3.1 Pro critic; OpenRouter `z-ai/glm-5.3-flash` critic.
**Adjudicator:** CCr (Grok 4.6). 2026-09-07.

## Comparison

| Finding | Cursor | GEM 3.1 Pro | GLM 5.3 Flash | CCr |
|---|---|---|---|---|
| Gitur never called Core (`api.get`) | claims fix | real | real | **ACCEPT** |
| Fleet/nodemap `runtimeRoot` gate | claims fix | real | real (plus Core 503 was separate) | **ACCEPT** |
| Forge writes swallow REFUSED | one write path | real | all four POSTs need the wrapper | **ACCEPT** GLM: all four |
| Recents vs coding history / OPENED off-screen | claims fix | real | real; must *stop* writing `#nav-session-list` | **ACCEPT** |
| Talk mic → Voice state | claims fix | real | real; confirm not in `kdash_native.js` | **ACCEPT** |
| Surfaces canon UNMEASURED rows | claims fix | (not named) | unverifiable without `/surfaces` n | **ACCEPT** shape |
| FINDINGS missing on Runs | — | missed | — | **VERIFY** — `JOB_ORDER` already has FINDINGS; painter must not drop it |
| Motif lane_a/lane_b on Forge | — | missed | — | **HOLD** — DEFINE puts MOTIF seats on Studio, not Forge |
| Gitur filter hides the 6 jobs | — | "destructive filter" | show kept/dropped counts | **ACCEPT** GLM |
| WORK IN FLIGHT: BROKE as in-flight | gap-fill | — | BROKE must not render as in-flight | **ACCEPT** |
| 503 must print `CDECK_PANEL_NOT_COMPOSED` | — | — | verbatim | **ACCEPT** |
| Critic input was PR JSON not a `.diff` | — | used the body | called the scar | **ACCEPT** as process: DEFINE + real diff next pass |

## Discussion

GEM and GLM agree on the five client defects Cursor named. That is not suspicious:
the PR body stated them. Disagreement is the leftovers. GEM wanted MOTIF lanes on
Forge — that fights DEFINE (Forge = CCr + adversarial; Studio = MOTIF seats).
GLM wanted kept/dropped counts on Gitur and BROKE out of in-flight — that honors
live emit (`jobs_n=6`, BROKE 8). GLM also caught a missing DEFINE: the critic
prompt was not a frozen feature file and the "diff" was PowerShell UTF-16 JSON.

## Accept (apply on PR #31 / next IMPROVE)

1. Gitur: `api(path)` not `api.get`; last-good on fail; kept/dropped counts.
2. Fleet/nodemap: HTTP 200 without `runtimeRoot`; 503 prints `CDECK_PANEL_NOT_COMPOSED`.
3. Forge: one wrapper on **all four** writes; locked CCr refusal visible.
4. Recents: coding history off `#nav-session-list`; OPENED card on Recents.
5. Talk mic state on Talk.
6. Surfaces: five canon rows, UNMEASURED if absent.
7. Runs: FINDINGS chip/filter if Core sends FINDINGS (verify, do not invent).
8. WORK IN FLIGHT: not BROKE.
9. Health RED x1 stays red.

## Hold

- Motif seats on the Forge tab.
- Auto-MOTIF. Second Core. PR lists. cancel/retry.

## Apply

Cursor still RUNNING on draft #31. CCr does not merge a draft. Next IMPROVE:
retarget #31 onto `main` (gitur branch already merged), apply Accept 1–9,
then merge when CI is green. DEFINE file is the verbatim Task for that pass.
