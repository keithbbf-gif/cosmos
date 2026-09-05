# Grayson — federated install card (Keith 2026-09-04)

**Status:** named peer, **not installed**. `host=None`. Do not invent an address.
**Where:** **his own PC** (Keith 2026-09-04). Not SRV1, not T7, not Keith’s COSMOS box.
A PC is a host *class*, not an address — still `NO_HOST` until Keith names the
machine (hostname / Tailscale name / LAN IP).
**Mesh ID:** **UNASSIGNED.** `cosmos/cosmos_identity.py`: Grant and Grayson are both
unassigned because an identity two people could answer to resolves to the wrong node
(GMesh scar). Keith assigns the ID. Until then he is the person **Grayson**, not a
constant.

## What he runs

**Keith 2026-09-04: he mostly needs Crucible.** Crucible is the **application**.
**COSMOS is the OS** that runs it (Carry-Over State Mesh Operating System).
Thin Core on his PC so `POST /api/v1/crucible` can run. He does **not** need
Cm self-build, MOTIF house, or this OpenWork+TUI orch home.

**Updates + comms** come from a service Keith can run on **T7 (T7920) or SRV1**
— not from this Cm TUI, not from his PC as the hub. Spec:
`docs/federation/UPDATE_SERVICE.md`. Hub host still unnamed.

| Piece | On his machine | Not |
|---|---|---|
| **CRUCIBLE** | **Primary.** `cosmos_crucible` rounds; his critic keys | A writer of Keith’s mesh. Not COW |
| **COSMOS Core** | **Substrate only** — `install` + `serve`, own root/sentinel/`tree_id` | Full Cm stream. Not `KMesh-COSMOS-live` |
| **Stream** | **One.** Work may be Legal; the tool is Crucible | Cm, plumbing, Keith’s CCr |
| **Product / profile / skin** | **Crucible** product → his profile → **Crucible cDeck skin** | Cm profile or Cm skin. Medical differentiator is a *different* product/profile/skin |
| **OpenWork** | Optional local orch if he wants it | Why he is federated |
| **CCr** | Only if his Core tree must change; one lease, **his** tree | A second CCr on Keith’s tree |

Mailbox + one versioned API + lease **before** any write that touches Keith’s install.
If the work is Legal, his root ≠ GrokBot `V:\Ai` Legal.

## Blockers (count the list; do not remember)

1. **Mesh ID** — Keith assigns. Do not use `GMesh`.
2. **Host** — his **own PC**. Keith names that PC’s address when he has it.
   `probe_lan_node` / F-56 stay `NO_HOST`. Do not put him in `LAN_NODES` as SRV1/T7.
3. **Stream confirm** — one stream. Product = **Crucible**. Legal is the likely
   *subject matter*, not a second product.
4. **Credentials** — his SuperGrok / API / Cursor / GitLab, not Keith’s files.
5. **Wire / meeting point** — Keith’s **update+comms service** on T7 **or** SRV1
   (not chosen; both `NO_HOST`). `cosmos_mail` schema exists; transport does not
   until that service has a host and a live tick.

## Cold-machine path (when 1–2 are named)

```
cosmos.py install   → new root, sentinel, tree_id, one stream
cosmos.py serve     → his Core (host for Crucible)
critics             → HIS rails/keys (GEM / OA / Grok / …) so a round is runnable
cDeck Crucible skin → POST /api/v1/crucible; 501 CRUCIBLE_NOT_RUNNABLE is honest
                    until `cosmos.py serve` attaches critics (`cosmos_crucible_critics`:
                    grok-sgh SuperGrok, gem-api, oa-api). His keys, not Keith’s.
OpenWork            → optional; not required to use Crucible
```

Installable by a peer on a cold machine is already COSMOS canon. Folder name says
**COSMOS**, not `Ai` (`docs/COSMOS_PIPELINE.md`).

## This install (Keith)

Does **not** take a CCr lease for him. Does **not** share `V:\A`. Drops to mailbox when
the host exists. HOLD on this Cm window is unrelated: naming Grayson does not clear it.
