# SESSIONS APP — ARCH (stage-2), skeleton slice

**Wish (Keith):** the Sessions product becomes its own **standalone app**. Today it is
three pieces inside two other products: the cDeck RECENTS pane + `ui/deck_session_kit.js`
(cDeck repo), the verb suite in `builds/session-tools/`, and the list/open CLI in
`builds/open_sessions/`. This file is the plan the skeleton implements.

**Additive by construction.** cDeck keeps rendering the same Core data. Nothing under
`cosmos/` changes, `builds/cdeck` is not touched, `builds/session-tools/` is not moved.
The standalone app is a **second reader** of one authority, never a second authority.

## Files

| Path | Role |
|---|---|
| `builds/sessions-app/sessions_app.py` | App shell — CLI (`list · open · verbs · verb · timeline · serve`) + its own-origin HTTP shell |
| `builds/sessions-app/sessions_core.py` | Read-only client of Core `GET /api/v1/recents` (+ `?open=1&id=`). Typed `CORE_UNREACHABLE` / `CORE_REFUSED`. |
| `builds/sessions-app/sessions_recents.py` | `cdeck-recents/1` → `sessions-app-list/1`. id-stable `cow-<session_id>`; legal **counted, not opened**. |
| `builds/sessions-app/sessions_verbs.py` | The verb set (scan load convert migrate diff check anonymize strip) with per-verb bind status. `scan` is BOUND to `builds/session-tools`. |
| `builds/sessions-app/sessions_timeline.py` | `rolled-event/1` milestone feed → `sessions-app-timeline/1` projection (`t · seat · kind · title · ref`). |
| `builds/sessions-app/sessions_refusals.py` | `SessionsAppRefusal` — a kind, not a traceback (same contract as session-tools). |
| `builds/sessions-app/ui/{index.html,app.css,app.js}` | Three-pane deck-skin shell: SESSIONS · VERBS · TIMELINE. |
| `tests/test_sessions_app.py` | Focused suite, incl. the "cDeck Sessions tab still routed" guard. |

Module names carry the `sessions_` prefix on purpose: `builds/session-tools/` is imported
with its own directory on `sys.path` and owns the bare names `verbs`, `schema`,
`refusals`. A `verbs.py` in this app would **shadow** the suite's own module.

## Architecture

```
Core :8770  ── GET /api/v1/recents ─┬─→ cDeck RECENTS pane        (unchanged)
(one authority,                     ├─→ builds/open_sessions CLI  (unchanged)
 single ledger writer)              └─→ sessions-app  ──→ its own shell :8785
                                            │              /sessions/  (ui/)
live/state/rolled/feed.jsonl ───────────────┤              /api/sessions
(rolled-event/1, append-only)               │              /api/verbs
                                            │              /api/timeline
builds/session-tools/ (verbs) ──────────────┘
```

- **Its own origin, its own port.** The app serves its shell *and* its JSON from one
  origin, so the browser is never cross-origin to anything (PARITY_AUDIT K-2). Core is
  read **server-side**, so no Core route, no CORS header, and no Core edit is required.
- **Exact-match static allowlist.** `/sessions/…` is a dict key, never concatenated onto
  a filesystem path — the cDeck-shell pattern, no traversal surface.
- **Loopback by default; a non-loopback bind refuses** (`REMOTE_OPEN_ACCESS`) because the
  shell carries no bearer. Remote reach stays `cosmos up`.
- **No browser-supplied filesystem path.** `--store` / `--root` are operator-declared at
  `serve` time; `/api/verbs/scan` scans that declared store or returns `NO_STORE`.
- **Projections only.** The app writes nothing under the runtime root and appends nothing
  to the ledger.

## Typed states (the two that get faked)

- **UNMEASURED is `null`, never `0`.** Core down, feed absent, or a count the upstream did
  not report → `n_shown: null` / `n: null` + a `kind`. A measured empty feed *is* `0`.
- **Legal is counted, not opened.** `omission = {reason, counted, opened: 0}`; `counted`
  is `null` when Core did not report it. `open` of an omitted id returns `LEGAL_OMITTED`.
- **No fake ids.** A blank or duplicated row id is `ID_UNSTABLE`, not a minted `cow-<seq>`.
- **Fail-closed feed.** One malformed `rolled-event/1` line refuses the whole projection
  (`UNPARSEABLE`, naming the line) rather than silently dropping a milestone.

## Compatibility risks

1. **`builds/cdeck` is a gitlink (mode 160000) with no `.gitmodules`.** The cDeck UI —
   `ui/app.css`, `ui/deck_session_kit.js` — is **not in this repo**, so the deck skin
   cannot be imported. This app mirrors the in-repo skin tokens (`kdash/index.html`
   `:root`) instead of copying cDeck CSS. Same reason `tests/test_cdeck_shell.py` and the
   cdeck panel routes cannot execute in a cosmos-only checkout.
2. **`sys.path` shadowing** of `session-tools`' bare module names — handled by the
   `sessions_` prefix; a test asserts the app declares none of those names.
3. **Core loopback is open** (DT auto-connect), so the app reads recents with no bearer on
   `127.0.0.1`; a tailnet Core needs `--core-token` / `live/config/api_token.txt`.
4. **Port.** `8785`, chosen away from Core `8770` and the cDeck/trylive `8791` footgun.
5. **Two surfaces, one projection.** cDeck and this app can disagree only by being read at
   different times; neither computes recents itself.

## Not in this slice

The seven DECLARED verbs (`load convert migrate diff check anonymize strip`) refuse with
`VERB_NOT_BOUND` until each is bound with its own gate — `session-tools` implements six of
them at CLI level, but a route is not a proof, and `strip` does not exist yet anywhere.
Timeline has no writer in this slice: it projects a feed some other seat appends.
