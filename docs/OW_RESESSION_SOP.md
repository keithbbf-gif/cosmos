# RESESSION SOP — OpenWork ORC (measured 2026-09-23)

**This is the OpenWork path.** Do not use grok 5a/5b for an OpenWork pen.
Do not SQLite-inject (`_ow_post.py` / `OW_POST.off`).

Measured success: TidyUP + TU2 + **BUorc.toml** + `session.create` in the
**same workspace** (`cosmos-2` / `ws_f38522284048`) with BootUP pointers in
the first prompt. Successor started. Lease then passed by
`cosmos_ccr.release` (old sid) + `cosmos_ccr.acquire` (new sid). Dying
session prints END OF SESSION and stops. No extra `grok.exe`.

## Watermark
- **65% persistent warn** — Grok window **200k**; warn at **130000** tokens. Writes `live/state/control/RESESSION_WARN.flag`. **Never self-clears.** Does not pack. Does not spawn.
- **~70% / fat fork** — pack only. Do not close. Do not spawn.
- **Keith says resession / write BUorc** — full SOP below.

## Full close (order is the design)

1. **TidyUP pack** — `live/state/session_saves/<stamp>/TIDYUP.md`
   (what closed, what is live, what not to do). Do **not** run
   `cosmos.py session close` unless Keith wants the kernel SEED path
   (that also releases the lease).
2. **TidyUP2** — `tu2_adversarial.json`: what the pack claimed that disk
   contradicts. Mitigation = **BUorc `[next]`**, not a fake-green HMAC.
3. **Write BUorc** — `V:\A\Ai\COSMOS\BUorc.toml`. `[read_order]`, `[next]`,
   prefork/fork sids. Point BUCm `[next]` at BUorc so old seats do not win.
4. **Paste** — `live/state/BOOTUP_PASTE.md` pointers only (BUorc, pack).
   Not a dump.
5. **Spawn ONE new OpenWork session in the same workspace**
   `session.create` `{ workspaceId: ws_f38522284048, sessions: [{
     title, prompt: BOOTUP pointers, model: xai / grok-4.6 }] }`
   - Skip create → no successor.
   - Inject-only into a dead grok uuid → vanish scar (`f5132f97`).
   - `session.create` **starts** the session (`started: true`). Do not also
     5b `grok.exe -r`.
6. **Pass the pen** — `release(sid=old_lease_sid)` then
   `acquire(sid=new_openwork_sid)`. Quote round-trip. Update BUorc
   `successor_id`.
7. **Inject this SOP** into the new session (`session.send`, not SQLite).
8. **Dying chair** prints END OF SESSION ×3 and stops. It cannot archive
   itself mid-turn.

## New session first acts
1. Read `BUorc.toml` then the pack.
2. Confirm `CCR.lease.sid` is **this** OpenWork session.
3. Resume-gate: Resume all · pick · hold. Default KEEP hold until Keith.
4. Continue BUorc `[next]`.

## Improper
- `_ow_post.py` fake user TICK into the hottest tab (preempts the pen).
- grok `--prompt-file` without a TUI, or TUI without inject.
- Hand-editing `CCR.lease` JSON.
- Chasing `time_updated DESC LIMIT 1` as the sit target.

## Measured this close (2026-09-23 ORC)
- Pack: `live/state/session_saves/20260923T123500`
- BUorc: `V:\A\Ai\COSMOS\BUorc.toml`
- Successor: `ses_f30942bf1ffeEp1wWbmMtErG4z` (cosmos-2, grok-4.6)
- Prefork lease sid: `ses_f3375edd5ffevQBjUDw27RZMpg`
- Dying fork: `ses_f30e84716ffeWYozBjZ2P3Rw3s`
- OW_POST.off stays. PAUSE hold stays. XTalk tabled.
