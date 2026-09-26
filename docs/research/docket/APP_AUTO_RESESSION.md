# Appendix — AUTO resession and fail-closed carry-over (measured 2026-09-10)

**Kind:** How-it-works appendix. Attach at filing with `HOW_IT_WORKS.pdf` / `APP_OS.md`.
**Maps to packets:** **P11** (SEED / OPEN_CONTEXT / auto-resession), **P07** (Layer A spawn grant ≠ Layer B fencing token), **P02** (peeking ban; no ballot writer), **P04** (live-emit vs green-log), **P03** / **P06** (UNMEASURED until observed).
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY.
**Not** claims. **Not** a novelty opinion. **Not** legal advice. Counsel drafts claims. USPTO click is **Keith + Legal**. This TUI does not write `V:\Ai` and does not click Patent Center.
**37 CFR 1.53(c):** no technical add-after a filing date. Duplicate this appendix into each FILE provisional that needs it. No claim of benefit of a sister.

Source tree: COSMOS live tree `V:\A\Ai\COSMOS`. Runtime root `live/` (`tree_id=KMesh-COSMOS-live`). Embodiment code: `cosmos/cosmos_session.py`, `cosmos/cosmos_validate.py`, `cosmos/cosmos_resession.py`, `cosmos/cosmos_spawn_grant.py`, `cosmos/cosmos_lock.py`, `cosmos/cosmos_ccr.py`. Spawn script: `work_orders/ccr/_spawn_ccr_successor.ps1`. SOP: `docs/RESESSION_SOP.md`.

---

## 1. Field

[0001] This appendix discloses a method and system for **fail-closed carry-over of an AI operating-system session across a vendor context boundary**, including: (a) a signed close manifest; (b) a two-step spawn of a **fresh** vendor session that is not a replay of the dying transcript; (c) a resume gate whose default is motion; (d) a spawn-time folder grant that is a different object from a commit-time fencing token.

## 2. Background / measured scars

[0002] Vendor `--continue` / `-c` of a dying window replays the same transcript. That is the failure auto-resession exists to close. A satellite that only mints a `--session-id` and never attaches a visible TUI leaves an injected session with no operator surface (`f5132f97`, inject-only). A TUI opened on a new id without the inject step is empty (`4ecfbb83`). `cmd /c start "title" grok.exe …` died on title-quoting. Compaction of a chat is not TidyUP and is not a signed close.

[0003] A write primitive that returns length and hash of the **intended buffer** after a raw write will **seal a truncated or mid-copy-mutated file**. The next session then injects a lie, or a matching sidecar hides a short body.

[0004] A spawn capability (what a worker process may touch on disk) collapsed into a commit fencing token (whether the holder still owns the lease) is a second measured hole: sandbox path ≠ execution grant.

## 3. Definitions

[0005] **SEED** — signed context manifest at close (`SEED.json` plus `SEED.decl.json`: declared length, SHA, install-key HMAC). Authority for carry-over. Not vendor memory.

[0006] **BUcr / BUCm** — lightweight session pointers beside the SEED. One truth. Never a competing second handoff. Trust `[next]` over stale SEED prose when HMAC still binds old keys.

[0007] **5a inject** — `grok --cwd <repo> --session-id <uuid> --prompt-file <BOOTUP_PASTE> --always-approve`. Writes the new vendor conversation and **exits**. That exit is correct.

[0008] **5b TUI** — WMI `Win32_Process.Create` of `grok.exe --cwd <repo> --fullscreen -r <same uuid>`. Same argv as a live Chief Coder TUI. Not `-c` of the dying window. Not `cmd /c start`. Not `cmd /k`.

[0009] **AUTO resession** — native clock plus satellite that, after a proper signed close, performs **5a then 5b** on a **newly minted** uuid. Default motion. HOLD never self-clears.

[0010] **VERIFY_MISMATCH** — typed refusal when bytes on disk after write or copy are not the declared body. Close must not append `SESSION_SEED_WRITTEN` over a lie.

[0011] **Spawn grant (Layer A)** — folder pen issued at worker spawn. Writes outside the granted root refuse (`GRANT_DENIED`). A lock fencing token (integer) is **not** a spawn grant (`NOT_A_GRANT`). Presenting a spawn grant as a fencing token is `LAYER_COLLAPSE`.

[0012] **Fencing token (Layer B)** — monotonic token on a lease (`cosmos_lock.Lease.token`). Stale token at publish is `STALE_TOKEN` / `NO_LEASE`. Distinct type from Layer A.

[0013] **Resume gate** — after BootUP injects SEED: Resume all · pick a subset · hold. No affirmative selection → auto-resume on the native 15-second clock. Default is MOTION.

[0014] **Live emit** — a value only the running Core (`:8770`) can produce. CI exit 0 is a projection, never DONE.

[0015] **UNMEASURED** — honest empty observation (`n_obs=0`, `n_pairs=0`). Not a score. Not a fabricated pair.

## 4. Drawings in prose

[0016] **FIG. A — two-step AUTO resession.** Dying session writes HMAC SEED and BUcr, releases the CCr lease, prints END OF SESSION. Satellite or operator script **mints uuid U**. Step 5a: grok `--session-id U --prompt-file BOOTUP_PASTE.md` runs to completion and **exits**. Step 5b: WMI creates `grok --cwd --fullscreen -r U`. The new TUI is not `-c` of the dying pid. Skip 5a → empty TUI. Skip 5b → session dies after inject.

[0017] **FIG. B — fail-closed SEED write.** `write_declared` writes, fsyncs, **re-reads**. Disk bytes are the declaration. Truncation or mid-copy mutation refuses `VERIFY_MISMATCH`. Dated archive of the prior SEED is hash-compared. `start_session` still refuses `NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH`.

[0018] **FIG. C — Layer A vs Layer B.** Worker spawn issues `SpawnGrant(root, sid)`. Commit gateway still demands `Lease.token`. The two objects are not interchangeable. Folder grant = pen. No IAM / Active Directory required for this embodiment.

[0019] Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## 5. Detailed description — AUTO resession (P11)

[0020] Close (`TidyUP`) writes `live/state/SEED.json` and `SEED.decl.json` under declared length and HMAC. It copies the CCr lease into the session-save pack, then **releases** the live lease. Adversarial TidyUP2 re-runs occupancy and live-emit and records what the close claimed that the disk contradicts (stale inherit is usual). Mitigation is BUcr `[next]`, not a fake-green HMAC.

[0021] A pointer paste (`live/state/BOOTUP_PASTE.md`) names files to read, not a dump of unfiled packet prose and not a 407,383-byte patent preload.

[0022] Spawn of the next Chief Coder (or Layer-B orchestrator) is **two steps, one new uuid**:

1. **5a.** `grok --cwd V:\A\Ai\COSMOS --session-id <uuid> --prompt-file live\state\BOOTUP_PASTE.md --always-approve` — injects and **exits**.
2. **5b.** WMI `Win32_Process.Create`: `C:\Users\Papa\.grok\bin\grok.exe --cwd V:\A\Ai\COSMOS --fullscreen -r <uuid>`.

[0023] The uuid is minted **new** for each BootUP. Reusing the dying window's id (`-c`) is refused on the proper-close path. `-r` in 5b attaches the visible TUI to the session **5a just created**; it is not replay of the predecessor transcript.

[0024] Embodiment script: `work_orders/ccr/_spawn_ccr_successor.ps1` (mints uuid unless `-Uuid` is passed). Satellite embodiment: `cosmos/cosmos_resession.py` `spawn_inject_argv` + `spawn_tui_argv` + `spawn_auto_resession`; `--spawn` is opt-in so a one-minute clock cannot open windows by surprise. Dry path records 5a+5b argv without creating a process.

[0025] Measured 2026-09-10: inject pid 43076 **exited**; TUI pid **60372** argv was `grok.exe --cwd V:\A\Ai\COSMOS --fullscreen -r a8f31c04-6e2b-4d91-9c7e-2b1e0d4a7c55`. One CCr. Lease sid matches that uuid.

[0026] After 5b, BootUP runs `cosmos.py session start <stream>`, quotes inherit, and presents the resume gate. Default MOTION. HOLD never self-clears.

[0027] Headless `--single` dispatch (worker jobs) is a **different** argv set and must not be combined with `--prompt-file` on the same invocation.

## 6. Detailed description — fail-closed SEED write (P11)

[0028] Predecessor: `write_declared` returned `len`/`sha` of the in-memory buffer after a raw write. Truncating the file after that return left a matching declaration. Close could still append `SESSION_SEED_WRITTEN`.

[0029] Embodiment (GitHub `keithbbf-gif/cosmos` PR **#128**, merged `83cd762`): after write, fsync and `read_verified` against intended length and SHA. Mismatch is `ValidateError VERIFY_MISMATCH`. `close_session` maps that to `SessionError VERIFY_MISMATCH` and hash-compares the dated archive copy of the prior SEED. Start of a truncated body remains `BAD_SEED`.

[0030] Pin: `cosmos/_fail_p11_seed_against_old.py` (old primitive still seals). Lock: `cosmos/_bite_p11_seed.py` `all_bite:true`. Isolated tests: `tests/test_p11_seed_bite.py`. Existing `tests/test_session.py` refusals by kind remain.

## 7. Detailed description — Layer A vs Layer B (P07)

[0031] Layer B already exists: monotonic fencing tokens and four-phase fenced commit (`cosmos_lock.py`). Stale token REJECTED. Dashboards are projections.

[0032] Layer A in this embodiment is **not** Windows IAM, not Active Directory, not extra logins. It is a **folder grant** issued at spawn (`SpawnGrant`: granted root + sid). `assert_granted` refuses a path outside the root (`GRANT_DENIED`) and refuses an integer fencing token used as a grant (`NOT_A_GRANT`). `refuse_as_fencing_token` refuses a `SpawnGrant` presented to the lock (`LAYER_COLLAPSE`).

[0033] `prepare_grok_workspace` attaches `spawn_grant` on the attempt-private clone. The CCr occupancy lease (`CCR.lease`: sid, pid, stream, tree_id, taken_at) is the **writer** token, not the spawn grant and not the lock fencing token.

[0034] Embodiment: GitHub PR **#130**, merged `42cfc48`. Pin `cosmos/_fail_p07_layer_ab_against_old.py`. Lock `cosmos/_bite_p07_layer_ab.py` `all_bite:true`. `tests/test_dispatch_workspace.py` still 41/41.

## 8. Dual-lane, live-emit, measurement (P02 / P04 / P03 / P06)

[0035] Dual-lane BUILD: two private workspaces; peeking ban until compare; **one disposer** (CCr). Occupancy: dual-lane BUILD has **no ballot writer**. A row that would invent `obs.jsonl` pairs to un-UNMEASURED is refused.

[0036] Runtime binding (P04): DONE requires a value only Core `:8770` emits. Embodiment pin `tests/test_live_emit.py` (status 200 `tree_id=KMesh-COSMOS-live`; porosity `kind=UNMEASURED` `n_obs=0`; PWA leftover 404; GET `/forge` and GET `/crucible` 404 occupancy-correct). Occupancy pin `builds/cdeck/test_kdash_working.py` **154/154**. Green log is not this gate.

[0037] Porosity GET never mkdir. `n_obs=0` stays UNMEASURED until real JSONL rows exist. Public digest/chain (`P03_PUBLIC_TENSOR`) remains **TABLED**. P12 Crucible PDJ triad remains **HOLD**.

## 9. Best mode (in-tree, this date)

[0038] Proper close: TidyUP → TidyUP2 → BUcr.toml → BOOTUP_PASTE.md → `_spawn_ccr_successor.ps1` (5a+5b) → successor reads BUcr then `SUCCESSOR_ROADMAP.md` → `session start` → resume-gate Resume all.

[0039] Gitur BUILD: one job, one branch `ccr/<job>`, one PR, blob from GitHub `main`. Do not `git pull origin/main` onto unique local HEAD. Parked leftovers stay parked (cdeck 6/16/17/68/102/108; cosmos 30/32/36/37/38/40/41/43/44).

[0040] Two pens: CCr `V:\A`; GrokBot `V:\Ai`. One CCr at a time (`CCR.lease`). ANTHROPIC_OFF on COSMOS dispatch.

## 10. Further embodiments (build sequence, not extra packets)

These are **embodiments of FILE packets already named**. They are not a 14th or 15th $65 slot. P14 precache is SOP (`CACHE_RULE`), not a new packet.

| Phase | Packets | Embodiment to code / bind | Refusal / live emit |
|---|---|---|---|
| **A — done this session** | P11, P07 | Fail-closed SEED write; Layer A grant ≠ Layer B fence; AUTO resession 5a+5b | `VERIFY_MISMATCH`; `GRANT_DENIED` / `LAYER_COLLAPSE`; skip-5a empty TUI |
| **B** | P02, P04, P05 | Peeking ban in farm spawn (no shared scratch). Extend live-emit: DONE needs `:8770` value | `PEEKING_VIOLATION`; missing emit refuses DONE. **No ballot writer** |
| **C** | P03, P06 | JSONL authority; GET never mkdir; COMPARE box$/token$ only after real `obs.jsonl` rows | Delete SQLite → GET rebuilds from JSONL; `n_obs=0` stays UNMEASURED |
| **D** | P08, P09, P10 | Confirm-to-widen occupancy; resolver identity mismatch; TESS/PPS is Keith+Legal | `409 WIDEN_REQUIRES_CONFIRM`; `IDENTITY_MISMATCH`. No USPTO click from a coder TUI |
| **E** | P13, P14 SOP, P01 | Voice Drop ingest live; prefix byte-stable; MOTIF DEFINE-first gates precache | Measure `cached_tokens`. Fabricated cache hit is refused |

[0041] P12 stays HOLD (CN119168059B / PDJ triad art). Do not revive `P03_PUBLIC_TENSOR`. Do not invent coverage scores while `n_obs=0`.

## 11. What this disclosure is not

[0042] Not ChatGPT / vendor memory. Not `-continue` of a full window. Not a second Core. Not a blockchain ledger. Not IAM. Not a ballot that writes observations. Not a 15th packet. Not a novelty opinion. Not an IDS.

## 12. Disclosure clock (already public)

[0043] Architecture ratification and AD-10 (signed close) **2026-08-23** (`cosmos` GitHub `created_at` 2026-08-23T06:42:12Z). Private-now does not rewind that clock. AUTO resession two-step argv and SEED round-trip are **2026-09-10** embodiments in the source tree and, once merged, on `keithbbf-gif/cosmos` (`#128`, `#130`; AUTO resession satellite PR `#131`).

## 13. Attach to

P11 (primary), P07, P02, P04, P03, and `APP_OS.md` / `HOW_IT_WORKS.pdf`. Duplicate at filing.

## 14. Handoff

GrokBot copies this file into Legal. CCr keeps coding on `V:\A`. Counsel completes inventor name and claims. Keith files or does not file.
