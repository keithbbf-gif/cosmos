# Appendix — How CRUCIBLE works

**Kind:** written description for Legal to attach to US provisionals.
**Status:** not a USPTO filing. **P12 (role-triad as the invention) remains HOLD.**
This appendix describes the **occupancy engine applied to a legal packet** (a skin of
P05), not “AI plaintiff / defense / judge” as a claim.
**In-tree:** `POST /api/v1/crucible`; 501 `CRUCIBLE_NOT_RUNNABLE` when no critic
dispatchers are composed. Seats in `model_rater`: `crucible.plaintiff`,
`crucible.defense`, `crucible.judge`. Product profile: `docs/PROFILES.md`.
Federated embodiment: Grayson runs Crucible as the **app** on **his** Core
(`docs/federation/GRAYSON.md`); host still `NO_HOST` until Keith names it.

## What it is

Crucible is a **product** on the COSMOS OS. A case (or other legal packet) is
evaluated by **named seats** that run **independently first**, then argue. One
**disposer** holds the write path. Spend is gated. Critics are a **different
family** from the builders and judge the *decision*, not style.

The same occupancy is reused as other skins by changing the **packet**, not by
cloning the stack:

| Skin | Packet | Seats (embodiments) |
|---|---|---|
| Forge | code / work order | CCr + N adversarial coders |
| Crucible | legal casefile | plaintiff / defense / judge **as seats**, not as the claimed invention |
| Diligence | data room / 10-K / deck | bull / bear / independent risk |
| Differentiator | anonymized clinical case | independent opinions, then argue |
| Docket | IP packet | applicant / examiner / prior-art |

Roles are **embodiments**. The method is: isolate proposers, different-family
critics, one disposer, runtime-bind, ledger the round.

## How a round runs (enabling)

1. Operator (or federated peer) presents a packet and named seats. Each seat is a
   model id from the local catalog / occupancy file, not a hard-coded vendor.
2. **Independent first.** Each proposer receives the packet and the task. They do
   **not** share a transcript mid-pass. No “second agent based on the first.”
3. Artifacts land as proposals (files / job results), not as a merged chat.
4. **Argue.** A later stage may exchange the isolated first takes. Disagreement is
   the signal, not a defect.
5. **Critics** (different family) compare the round to the **decided** rubric.
6. **One disposer** accepts or refuses. Core ledgers the round. cDeck Review pane
   paints FINDINGS; it does not invent an approve/reject verb the OS lacks.
7. `POST /api/v1/crucible` without composed critics is **501** — an honest refusal,
   not a stub job. Fail-closed.

## Federation (shape, not a live peer)

COSMOS is the OS. Crucible is the application a peer can run. Grayson: thin Core
on **his** PC, **his** keys, **his** tree. Updates/comms from a hub Keith names
later (T7 or SRV1 — both `NO_HOST` today). Mailbox + one versioned API + lease
**before** any write that touches Keith’s install. Do not share `V:\A`. Do not
invent a hostname.

cDeck parallel instances (Forge window + Crucible window) are two **clients** of
one API, the same sit as Grok.com + OpenWork today. Not two Cores.

## What not to claim

Do **not** claim “AI plaintiff, defense, and judge” as the invention. That triad
is crowded: SimuCourt/AgentsCourt arXiv:2403.02959; AgentCourt arXiv:2408.08089;
**CN119168059B granted** 2025-07-15; **US20260037351A1** claim 21; jury-side
US20250148558A1. File Crucible only as **P05 occupancy applied to a legal
packet**. Else fold into P05 and spend the 12th slot on UPS-JUDGE with Keith’s
July pack.

Name collisions (not TESS): CrucibleTech RN 8043152; Star Lab CRUCIBLE RN 5023199;
Crucible Discovery; Destiny PvP fame.

## Already public (clock)

GitHub `bts-mesh` **About** text names “CRUCIBLE method” as of 2026-08-16T10:21:14Z.
Tracked files in that repo: **zero** hits for CRUCIBLE. Public date is a **name**,
not a method disclosure in code. US grace for that string is thin.

## Attach to

P05 (parent occupancy) at minimum. P12 only if Legal files occupancy-not-roles.
Do not attach this appendix as if it cured a PDJ claim.
