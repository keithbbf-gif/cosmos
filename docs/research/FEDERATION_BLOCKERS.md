# Five federation blockers — fix or defer (2026-09-19)

Counted from `cosmos_identity.federation_blockers()`, not prose. `federation_ready()` is True iff the list is empty.

| # | Blocker (from the function) | Fix or deferral |
|---|---|---|
| 1 | no live peer (JMesh not installed; LAN nodes declared, not installed) | **Defer.** Do not fake a peer. Install JMesh only when Keith names a second machine. |
| 2 | no meeting point (LAN NAS does not exist; G: was USB wearing a NAS label) | **Defer.** Meeting point is a named NAS with sentinel content, not a drive letter. |
| 3 | no wire protocol (cosmos_mail schema exists; no transport between machines) | **Defer.** Schema stays; transport is a later Gitur bite after a live peer exists. |
| 4 | no trust model (peer identity is a name, not a verified credential) | **Defer.** Do not treat a hostname as a principal. |
| 5 | no notarization of control files across peers (tree_lock is local; cross-peer TOCTOU remains) | **Defer.** Local hash-chain stays. Cross-peer notarization after 1–4. |

**Ready:** no. Do not declare federation live. Do not invent a peer to empty the list.
