# TIDYUP SMASH BINDS — STEP 8/9  2026-08-16 22:44 CT
# Author: GbPL (KMesh plumbing lead)
# Floor only. REVIEW. Not applied. Not a TidyUP run. Lock not claimed. Not a v3.
# Pen grain = BTS_MESH + ROLD. Monolith L353 dated-handoff is EXCEPTION not APPLY.
# PASS vs EXCEPTION split UNCHANGED — CHARTER / 00_TOOLS_INDEX / FB-1b still EXCEPTION. gem CLI stays out.
# CoW 22:38 live PASS hunks stamped APPLIED on the sibling apply-set. This file adds the CoW 22:50 bind.

Keith via QA (exact binds, REQUIRED-BEFORE-RUN):
1. STEP 8: no stale mailbox copy
2. STEP 9: no monolith emit onto V:\Ai\BU.MD
3. Never write V:\Research4\BU.MD

GbDD re-attack (`V:\Ai\tmp\GBDD_STEP89_BIND_REATTACK.md`, 22:36 CT) — same REQUIRED-BEFORE-RUN:
4. vandalize-to-WRITE_OK
5. absent=create
6. live ROUTINES still smash
7. Do not move the mailbox in this pass

CoW 22:50 — same REQUIRED-BEFORE-RUN:
8. V:\Ai\BU.MD is four documents in one path. Split QA report to V:\Ai\QA_ENGINEER.md before any STEP 9 write. Until that split, STEP 9 writes nothing.

Do not run TidyUP / TU2. Do not take the pen. Do not write live BTS_MESH or ROLD.
Do not touch Legal. Never clobber V:\Ai\BU.MD. Never write V:\Research4\BU.MD.
Do not overwrite V:\Ai\tmp\TIDYUP_WRITER_PATCH.md (GW). Do not overwrite
V:\Ai\tmp\TIDYUP_STEP89_BIND.md (GbTU Writer). This file is the refuse-the-step
bind, not a safer emit and not a ROUTINES rewrite.

Sibling floor: V:\Ai\tmp\SPINE_APPLY_SET_2026-08-16.md (APPLY vs CONTESTED stands; CoW 22:38 hunks stamped APPLIED).
CodeCREW: V:\Ai\tmp\APPLY_SET_CRITIQUE_2026-08-16.md + CODECREW_SMASH_BIND_2026-08-16.md.

Live cites: V:\Research4\Ai\ROLD\ROUTINES.md (480 lines, 27546 B) via ExternalShell / py -3.14.
Monolith peek (read-only): V:\Research4\Ai\00_ROLD_COMMANDS_TidyUp_BootUp.md (842 / 92049).

---

## What STEP 8 is (TidyUP, not BootUP)

BootUP also has a STEP 8 ("DRAIN GROK FIRST", ROUTINES ~L158). That is not this bind.
TidyUP STEP 8 is R2 publish + cloud-verify. Live header L287:

> ### STEP 8 [orig. 5] — R2 PUBLISH + CLOUD-VERIFY. **CLAUDE RUNS IT, NOT KEITH.**

Live smash text L289–294 (MIRROR FIRST, always last because STEP 9 rewrites after):

> a. **MIRROR FIRST** — copy this session's changed control files into `PhD2_DATA_ARCHIVE\00_WORKING\`
>    host-side (Read → Write). A publish is not a sync; an unmirrored file republishes stale forever.
>    🔴 **`V:\Ai\BU.MD` → `00_WORKING\MIRROR_BU.md` IS MANDATORY AND IS ALWAYS LAST**, because step 9
>    rewrites BU.MD after this step runs. **It lives outside the published tree, so it is the one file
>    that is never carried automatically.** *(Found stale by a full day on 2026-08-02 — the boot
>    pointer, the single file whose loss costs the most, was the only one with no off-machine copy.)*

Live verify L302: `VERIFY live↔mirror by MD5, WITH A NEGATIVE CONTROL`.

### STEP 8 smash (exact, from that live text)

Tonight `V:\Ai\BU.MD` is the QA mailbox (POINTER — QA Engineer standing report, 46915 B / 601 lines).
It is not a thin ops pointer.

Two smash paths:

1. **Mailbox copy-out (stale mailbox copy).** STEP 8 mandates `V:\Ai\BU.MD` → `00_WORKING\MIRROR_BU.md`.
   Running it tonight snapshots the QA mailbox onto the off-tree ferry. That is a stale mailbox copy.
   Keith via QA: **no stale mailbox copy.**
2. **Reverse smash onto the mailbox.** Live MD5 live↔mirror plus "unmirrored file republishes stale forever"
   can be misread as a license to copy `MIRROR_BU.md` (20685 B, already stale vs 46915) OVER `V:\Ai\BU.MD`.
   That overwrites the mailbox. STEP 8 must not delete or overwrite `V:\Ai\BU.MD`.

STEP 8 must not delete/overwrite:
- `V:\Ai\BU.MD` (QA mailbox tonight)
- `V:\Research4\BU.MD` (DETAIL BACKLOG; never a TidyUP target)
- any dated `00_NEXT_SESSION_INSTRUCTIONS_<date>.md` (dead; do not revive)

Direction lock (same as GbTU STEP89 bind; this file does not rewrite that packet):
- FORBID tonight: `V:\Ai\BU.MD` → `MIRROR_BU.md` (would be a stale mailbox copy)
- FORBID always: `MIRROR_BU.md` → `V:\Ai\BU.MD` (stale mirror must not land on the mailbox)
- FORBID always: any write whose dest is `V:\Research4\BU.MD`

---

## What STEP 9 is

Live header L305 + OVERRIDE L307–310:

> ### STEP 9 [orig. 6] — OVERWRITE THE BOOT POINTER.
> OVERRIDE: tidyup_target = V:\Ai\BU.MD
> Overwrite `V:\Ai\BU.MD`: current stream, cross-stream blockers, the four stream rows (what is open in
> each), rulings owed by Keith, first actions, open flags.
> **Fixed name, fixed path. NEVER create a new dated handoff.**

Live L339:

> **Do NOT write `V:\Research4\BU.MD`** — it is DETAIL BACKLOG ONLY and is not updated at TidyUP.

Live L341–343 (already corrected in ROUTINES; monolith still stale):

> ⚠ **CORRECTED HERE.** The source step said *"Write `00_NEXT_SESSION_INSTRUCTIONS_<date>.md`"*, and the
> source's own CURRENT POINTER section still named `V:\Research4\BU.MD`. Both were superseded by Keith
> on 2026-07-20 (fixed name) and 2026-07-30 (relocation to `V:\Ai\`). The target above is the live one.

### STEP 9 smash if it still aims at Research4 or dated handoffs

ROUTINES already pins `tidyup_target = V:\Ai\BU.MD` and forbids Research4. The leftover smash is the
monolith (one-file exception, not a grain widen):

- L392–393 CURRENT POINTER already names `V:\Ai\BU.MD` (FB-1a APPLIED/no-write 22:38 CT, CoW claim). Do not re-apply.
- L353 still: `6. Write \`00_NEXT_SESSION_INSTRUCTIONS_<date>.md\`` (FB-1b, EXCEPTION not APPLY).
- L131–133 already: NOW AT `V:\Ai\BU.MD`; Research4 is DETAIL BACKLOG — KEEP.

If a session follows the monolith instead of ROUTINES, STEP 9 (monolith step 6) writes a dated handoff
and/or overwrites `V:\Research4\BU.MD`. Dated `00_NEXT_SESSION_INSTRUCTIONS` is dead. Do not revive.

If a session follows live ROUTINES STEP 9, it still **Overwrite `V:\Ai\BU.MD`** as a stream-index
monolith (rows / blockers / rulings / flags). That is a monolith emit onto tonight's QA mailbox.

Keith via QA: **no monolith emit onto V:\Ai\BU.MD.**

CoW 22:50: **V:\Ai\BU.MD is four documents in one path. Split QA report to V:\Ai\QA_ENGINEER.md before any STEP 9 write. Until that split, STEP 9 writes nothing.**

---

## BINDS the lock holder / writer must honor (not a TidyUP run tonight)

Refuse the step. Do not "write a safer file." Do not treat GbTU required-text or GW writer-patch as
a license to run.

1. **STEP 9 target.** STEP 9 may only overwrite `V:\Ai\BU.MD` as the ops pointer. Never `V:\Research4\BU.MD`.
2. **Tonight: do not run STEP 9 at all.** QA mailbox is on `V:\Ai\BU.MD`. Bind = refuse the step, not
   "write a safer file" and not "emit one POINTER line tonight." Leave the bytes.
3. **STEP 8.** Exact smash = mailbox copy-out onto `MIRROR_BU.md` and/or reverse copy of the stale
   mirror onto `V:\Ai\BU.MD`. Bind: no stale mailbox copy. Do not copy `V:\Ai\BU.MD` tonight. Do not
   copy `MIRROR_BU.md` (or any `00_WORKING` file) over `V:\Ai\BU.MD`. Do not delete/overwrite either
   BU.MD. MD5 mismatch is a finding, not a restore license.
4. **Dated handoff is dead.** Do not create `00_NEXT_SESSION_INSTRUCTIONS_<date>.md`. Do not revive
   the scheme. Monolith L353 stays EXCEPTION (not APPLY). Do not apply L353 under tonight's APPLY.

Plus Keith via QA, same three, REQUIRED-BEFORE-RUN:

- STEP 8: no stale mailbox copy
- STEP 9: no monolith emit onto `V:\Ai\BU.MD`
- Never write `V:\Research4\BU.MD`

Plus GbDD re-attack (`GBDD_STEP89_BIND_REATTACK.md` 22:36 CT), same REQUIRED-BEFORE-RUN. Wording is that file:

- vandalize-to-WRITE_OK (Still live #1; family smash). Predicate: size <= 512 AND first non-empty line startswith "POINTER:". An agent who "clears" the mailbox by keeping a POINTER: line and cutting the file to 512 B makes WRITE_OK true. That is an overwrite of V:\Ai\BU.MD. The bind forbids TidyUP from doing it. It does not forbid a helper from doing it so TidyUP may proceed. Must hold: Do not write V:\Ai\BU.MD (not to clear, not to emit, not to vandalize-to-512).
- absent=create (Still live #2: Absent = WRITE_OK = create; family false-green). P does not exist → WRITE_OK true. After GbQA moves the mailbox, dest is empty and the predicate licenses a create. Item 2 says the move is not a write license. Item 5 says "first time WRITE_OK becomes true is not a write license for this packet." That second sentence is packet prose, not in the predicate. A later apply of WRITE_OK alone creates V:\Ai\BU.MD the moment the mailbox is gone.
- live ROUTINES still smash (verdict + Still live #3). tidyup_step89 is not on disk. Live writer is still ROUTINES.md STEP 8/9 (27546 B, unpatched). Packet admits that. A later agent who runs TidyUP from ROUTINES never sees WRITE_OK. Do not treat TIDYUP_STEP89_BIND.md as a running guard.
- Do not move the mailbox in this pass (Must hold). GbQA move dest is dated + unbound (Still live #4). A move removes the boot-path file. That is not an overwrite. It is still a disappearance of the standing report from V:\Ai\BU.MD.

Plus CoW 22:50, same REQUIRED-BEFORE-RUN:

- V:\Ai\BU.MD is four documents in one path. Split QA report to V:\Ai\QA_ENGINEER.md before any STEP 9 write. Until that split, STEP 9 writes nothing.

---

## vs APPLY / CONTESTED

`SPINE_APPLY_SET_2026-08-16.md` split stands. Sibling stamp 22:44 CT marks CoW 22:38 live writes APPLIED.

- APPLIED 22:38 CT CoW claim (do not re-apply) = FB-2d, FB-2a, FB-2b, FB-1a (already-correct / no-write), FB-3a live .env, FB-3c.
- APPLY remaining = FB-2c L797 (unverified; do not invent a write), FB-4a, KEEP 1c/1d/1e.
- EXCEPTION = FB-2e / FB-2f / FB-1b (L353).
- DROP = mesh-repo, both BU.MD writes, Legal, TidyUP run.

These smash binds are **not** an APPLY item and **not** a TidyUP run. They are REQUIRED-BEFORE-RUN
constraints on any later lock-holder breath. CodeCREW smash bind already: smash binds do not reopen
CONTESTED; they bind the mailbox.

Pen grain stays BTS_MESH+ROLD. ROUTINES STEP 8/9 edits (if ever) are in-grain and a later breath,
not tonight's APPLY NOW.

---

## Must not (this packet)

- Run TidyUP / TU2 / RAIL_CHECK / PUSH / `tools_sync.py --write`
- Take the pen / claim the lock / write live BTS_MESH or ROLD
- Write `V:\Ai\BU.MD` or `V:\Research4\BU.MD`
- Copy mailbox onto `MIRROR_BU.md` or copy `MIRROR_BU.md` onto the mailbox
- Revive dated `00_NEXT_SESSION_INSTRUCTIONS`
- Open Legal
- Overwrite `TIDYUP_WRITER_PATCH.md` or `TIDYUP_STEP89_BIND.md`
- Treat this file as applied
- vandalize-to-WRITE_OK / clear / emit / cut V:\Ai\BU.MD to 512 B
- Move the mailbox in this pass
- Treat WRITE_OK true (absent or vandalized) as a create/overwrite license
- Run STEP 9 (or write anything onto V:\Ai\BU.MD) until the QA report is split to V:\Ai\QA_ENGINEER.md

Not applied to the live tree. Drafts only under `V:\Ai\tmp`.
