# PR #37 — cDeck P7 Gemini side panel (harvest)

- **When:** 2026-09-04
- **Cursor:** `bc-c4a1bf91-52cf-4663-b52e-8c1a75c57ffe` FINISHED
- **PR:** https://github.com/keithbbf-gif/cosmos/pull/37
- **P10:** propose only. Two files: `proposals/cdeck-p7-gemini-side-panel.md` + `.json`.
- **Do not merge.**

## CCr disposition

**Accept as research/arch** for P7. **Do not apply as a live patch this pass** (no UI symbols; clone could not see `builds/cdeck/`).

Keep: Chrome owns Alt+G; GEM is a toggle (`TOGGLE_NOT_OBSERVABLE`); no iframe / no web-app `window.open`; CDP structurally refused; no RegisterHotKey; AUTH click not automated; browser-served `NOT_ADDRESSABLE` + copy query.

Refine: live Tauri `cdeck.exe` **has** a native host — Option A SendInput is available on DT. Next BUILD reads live `ORCH_HOME_SPEC.md` + `src-tauri` + `ui/`, not GitHub `main` 14addfc.

Core `GET /api/v1/gem/preflight` stays queued (read-only additive). No new clock.
