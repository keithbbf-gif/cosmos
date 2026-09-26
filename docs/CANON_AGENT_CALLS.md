# CANON: how we call agents (all seats read this)

**Authority (measured, not remembered):** `work_orders/ccr/_crew_tab_teams.py`,
`work_orders/ccr/_cdeck_code_seat.py`, `work_orders/ccr/_code_or_seat.py`,
`cosmos/cosmos_openrouter_rail.py`, `cosmos/cosmos_codex_rail.py`,
`cosmos/cosmos_route_variant.py`, `cosmos/cosmos_spawn.py`,
`cosmos/cosmos_resession.py`, `cosmos/cosmos_dispatch.py`.
**Companion:** `docs/CANON_4C_JUDGE.md` (reply formatting + verdicts).

One seat = one call shape. Wrong shape = refused or unscored. No seat invents
its own invocation.

---

## 1. Farm coder seats (pairs) — the only spawner

`_crew_tab_teams.py` via `spawn_detached` (WMI/`pythonw`, detached, logged):

```
pythonw <seat_py> --seat <a> --pack <fat|house> --item <ITEMs/<tab>.md>
        --out <CREW/OUT/TEAM_TABS/<tab>/<seat>-NNN.json>
        --timeout 900 --max-tokens 8192
```

- Seat file: seats in `VX_WINDOW` → `_cdeck_code_seat.py`; all others →
  `_code_or_seat.py` (`_py()` in `_crew_tab_teams.py`).
- `--pack fat` only where the seat window holds it; else `--pack house`
  (refuse: fat patent pack on small-context seats).
- Pairs share one ITEM, no shared context between a/b (blind by construction).
- Called ONLY from the factory cycle when NOT paused. Direct invocation during
  `PAUSE hold` must self-refuse (see `_crew_tab_teams.py` pause gate).

## 2. Model rails (no processes — API calls)

| Rail | Call | Notes |
|---|---|---|
| OpenRouter (GLM/DS/Qwen/Ling/Muse/OSS/Solar/…) | `rail.dispatch({"model": "<id>", "text": "<prompt>"})` → `POST https://openrouter.ai/api/v1/chat/completions` | `request_model()` appends `:floor` by default; key file `live/config/openrouter_api_key.txt`, never printed |
| Vertex (Gemini Flash) | `rail.dispatch({"prompt": "…", "model": "gemini-2.5-flash"})` | Kelly project wallet; thinking medium, never HIGH |
| Codex CODER | `codex exec --sandbox workspace-write --skip-git-repo-check` | Opt-in only; never from probe/`--gate` |
| Codex VETTER | `codex exec --sandbox read-only --output-schema <schema>` | Diff on stdin |
| Codex JUDGE / WOMBAT (Luna, OpenRouter-keyed) | isolated `CODEX_HOME` + `codex exec` **without** `--ignore-user-config` + `-m <id>:floor` | Codex **0.147**: `--ignore-user-config` skips `config.toml` but **auth still uses CODEX_HOME** → ChatGPT/OpenAI Responses 401. `-p name` layers `$CODEX_HOME/<name>.config.toml` on the *user* config. Fix: seat-private `CODEX_HOME` with `config.toml` `model_provider=openrouter`, `wire_api=responses` (0.147 refuses `chat`), PowerShell `auth` command (not only `env_key`). Never write Keith’s `~\.codex\config.toml`. Key from `live/config/openrouter_api_key.txt`, never printed. MAX = `model_reasoning_effort="max"`; FLEX = `:floor`. Templates: `CALL_WOMBAT_LUNA.cmd`, `CALL_LUNA_G6_OR.cmd`. |
| Cursor Gitur BUILD | Cloud Agent `autoCreatePR`, one job / one branch / one PR from `origin/main` | Gitur PRs ONLY. Cursor credits are NOT used for CCrew, WOMBAT, Judge, Scribe, or Final Auditor. |

## 3. Grok CLI — allowed shapes only

- WO worker: `grok --single <task> -m <model>` is **REFUSED**
  (`cosmos_spawn.py` refuse; `cosmos_work_order_run.py` warn3 `GROK_EXE_SCAR`).
- **Audit carve-out (Final Auditor ONLY):** `grok --single --prompt-file <batch>.md
  -m grok-4.7 --output-format json --always-approve` — bucket-full-only (>= 30),
  verdicts to `live/queue/audit_verdicts/`. Audit is not a WO worker; exactly
  ONE grok.exe; never a second grok writer on the tree.
- Resession 5a (new session): `grok --cwd <dir> --session-id <uuid>` (new-only).
- Resession 5b (resume TUI): `grok --cwd <dir> --fullscreen -r <uuid>`.
- `--session-id` on an existing session is rejected by the binary — never retry,
  use `-r`.
- Prompt caching: legend PREFIX bytes stable across a batch's calls, packets in
  the tail (cache hits; churned legend = full re-bill).

## 4. Bucket/daemon workers (clocks, not agents)

```
py -3.14 cosmos\cosmos_<node>_worker.py --root <live> --once|--loop|--standup|--status
```

`--once` for probes; `--loop` only under schtasks; `--standup` registers the
task; `--status` reads heartbeats. Workers never call models directly.

## 5. What a call must carry (every dispatch)

`{model, text/prompt, seat, pack, item, out, timeout}` — missing `out` (write
path) = no harvest = silent death (see the 422 manifests with 2 returns).
First-line + 4Cs + verdict formatting per `docs/CANON_4C_JUDGE.md`.
