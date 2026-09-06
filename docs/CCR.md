# CCr — Chief Coder (Keith 2026-09-04)

**One writer of the COSMOS live tree. One at a time.** Orchestrator does not need that pen.
Cowork already proved orch-without-pen: folder grants were the lock. OpenWork should work
the same way. Full addendum: `docs/AGENT_BOUNDARIES.md` items 12–14. Principles P9/P10.

## Occupant (Keith 2026-09-04, this session)

| | |
|---|---|
| **Who** | **Grok 4.6 Build** (this TUI) |
| **Pen** | **`V:\A`** (including `V:\A\Ai\COSMOS`) |
| **CCr** | **This session is the current CCr** |
| **Lease** | `live/state/control/CCR.lease` sid `39d083c1-caa1-4fd0-9881-fecfadbfcceb` stream `Cm` |

An empty lease file is not “no pen.” CCr **takes** the lease. A second CCr REFUSES. GrokBot still does not write `V:\A`. OpenWork still does not write COSMOS.

**Keith 2026-09-05:** Captain = Keith. ORC = wheel and rudder. OpenWork = wheelhouse. This TUI = designer / engineer / builder. **This tree is the engine room.** CCr writes CORE here. ORC does not.

## Roles

| Role | Pen | Writes |
|---|---|---|
| **ORC = GFO** (Gem Flash OpenWork, cDeck left) | **None** on COSMOS. Files in `V:\Streams\openwork` | Talk, mailbox `cm\`, WOs, SSA. **Runs on** live Core (`:8770` — the tree’s code). CORE changes queued for CCr. Replaces Cowork. |
| **CCr** (this TUI, Grok 4.6 Build) | **Write pen for live COSMOS CORE** (`V:\A`, `cosmos/`, lease) | Writes CORE in the tree. `builds/cdeck`, tests Core runs, live ledger/registry/config. **Exactly one** lease. |
| **OpenWork grant** | Workspace **`V:\Streams\openwork` only** | File work + orch mailbox. **Off** the OS live tree. No COSMOS folder grant. |
| **Other streams** | **Own root only** | LEGAL, plumbing, UPS, … each have a tree. **No two streams share a root.** Mailbox before any shared write (BTS two-writer scar). |

**Keith 2026-09-04 (this TUI, verbatim intent):** *you don't code — you write work
orders, you run github/cursor/gitlab, you review/refine the code and write to
the COSMOS live tree.* **Gitur (Keith 2026-09-05) = GitHub + GitLab + Cursor.**
That triad is what CCr **runs**. Coding = GitHub Copilot / Cursor Cloud Agent
(Opus 5 / Sonnet, never Composer 2.5) / GitLab Duo + dropped Grok 4.6 work-order
sessions. Dispose = CCr after review. P10 still: Gitur PROPOSE; CCr writes.
Gitur is not a pen and not a fourth writer. Map: `docs/ROUTING.md`.

**Keith 2026-09-05:** the **entire COSMOS build** runs **through Gitur** so we get **branched trees**. That includes **side jobs / products**, not only CORE kernel: **Open Sessions** (`builds/open_sessions/`), **cowork_to_openwork**, session-tools, cDeck occupancy chrome. Stage-4 BUILD lands on a GitHub/GitLab branch + PR (Cursor lane and/or Grok CLI `--cwd` that branch/worktree). CCr **reviews** then disposes onto the live tree. Do **not** author `builds/` / `cosmos/` / product CLIs straight onto `main` in this TUI as the default path. Open Sessions stays LIVE — iterate on a branch; do not rebuild it in place. `cowork_to_openwork` is not ORC recode; if CCr changes it, that is still a Gitur branch.

**Keep it organized (Keith 2026-09-05):** **one job, one branch, one PR.** Do not mix products (session-tools / Open Sessions / cowork_to_openwork / cDeck) with occupancy canon, CLOCKS, or harvest notes. Named branches: `ccr/<job>`. Side jobs do not share a PR.

**Keith 2026-09-05 (this chair):** keep COSMOS **ticking**, **finish features**, and optimize for **elegance, simplicity, and token economy**. This TUI stays sparse (decisions + dispose). Volume BUILD is Gitur. Improvement-not-bloat: subtract as well as add. Do not merge PRs #30 #32 #36 #37 #38. Do not force-push local unique history (apk blob).

**The cycle:** native **system clock** (WD2 / Pulse / runner) **and Gitur** execute MOTIF in the background. **This TUI reviews and applies** (CCr dispose). Wishlist and needed features **must** exist as **work orders** (`work_orders/drop/`, six-field SOP) so the clock and Gitur can run them. This TUI does not in-band the BUILD. One job, one WO, one Gitur branch.

GrokBot still does not write `V:\A`. OpenWork does not write COSMOS Core. **This Grok 4.6 Build session does** — it is CCr, pen `V:\A`, under the lease.

## Why a social rule is not enough

A new session will not know CCr and will Write anyway. Hidden folders do not help: the session
that must use the tree has to see it; the session that must not will find hidden files.

## Simple protection (do not silent-overwrite)

**Do not** keep a hidden “real copy” that **overwrites** the public COSMOS tree on CCr close.
That is the two-writer **deletion** scar: work vanishes with no ledger event.

**Do** the Cowork trick, plus one lease:

1. **Folder grant = pen.** OpenWork **workspace root** stays `V:\Streams\openwork`.
   File work + ORC **off** the OS live tree — **no** COSMOS authorized folder.
   GFO **runs on** the live Core (tree code at `:8770`). CCr is the only CORE writer.
2. **`live/state/control/CCR.lease`** — sid, pid, fencing token, `taken_at`. A second CCr
   **REFUSES**. No lease → fenced commit gateway **REFUSES** live-tree writes. Orch still
   drops `work_orders/drop/` and `work_orders/ccr/`.
3. **CCr close** = TidyUP + lease drop. Queued CORE changes from orch/OW wait for the
   **next** CCr. Publish is fenced commit, not robocopy-over-main.
4. If public tree is dirty from a rogue: **stage unexpected paths to `_delme\ccr-quarantine\<sid>\`**,
   ledger it, then CCr promote. Never silent clobber.

Optional later (same user on Windows, so NTFS deny-Everyone is useless): Grok **agent profile**
for orch denies `Edit`/`Write` under `cosmos/`, `tests/`, `live/ledger`. CCr profile allows.
That is a permission file, not a hidden directory.

## Queue for next Cm

Path: `work_orders/ccr/` (plus existing `work_orders/drop/`).
Payload: P10 proposal (`target_path`, diff or full content, rationale).
CCr `--accept` applies through the fenced gateway. Core stays the ledger writer.

## Federation (Keith 2026-09-04)

**Grayson soon:** **his own PC**, his accounts. **He mostly needs Crucible** (the
**application**). **COSMOS is the OS** that runs it. Thin Core on his PC.
**Update + comms** = a service Keith can run on **T7 (T7920) or SRV1** (not
chosen; `NO_HOST`). Spec `docs/federation/UPDATE_SERVICE.md`. Not a Cm self-build.
OpenWork optional. Own tree. Mailbox before any write this way. Do not invent a host.

**Jack’s OpenWork (Keith 2026-09-05):** Ranny Cook GCP `$300` / `249427005764` is
**saved for Jack’s OpenWork**, not Keith’s COSMOS and not Keith’s OpenWork grant
(`V:\Streams\openwork`). Do not invent Jack’s tree or grant path. Joanna stays
Keith’s. Coding/reasoning Vertex gets a **separate company $300** when pasted.

**One stream per federated install (Keith 2026-09-04).** Grayson: Crucible as the
product (Legal as likely subject). No Cm on his box, no CCr on Keith’s COSMOS tree.
**Different cDeck is allowed:** Grayson gets a **Crucible skin** (run a round, packet,
returns) vs this Cm OpenWork+TUI home. Same Core API; UI may deploy separately;
authority may not (decision 7). Do not fork Core. His tree is not `V:\Ai\Legal`.

## Lease is not wired this file

This file is the contract. `CCR.lease` + grant split are the build. Until they exist, the
rule is still binding on sessions that have read it; **protection against a session that
has not** is the grant + lease work, not a backup overwrite.
