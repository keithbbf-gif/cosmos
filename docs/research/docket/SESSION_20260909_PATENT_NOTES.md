# Session note — patent talk (2026-09-09)

**Source:** Ara / Grok 4.6 voice session, 2026-09-09.
**Status:** Session notes only. Not a USPTO filing. Not claims. Not a novelty opinion.
**Assumption:** User said "parents"; treated as **patents** (voice). No parent/family IP discussion in this chat.

---

## What already exists in the Docket

Zero applications filed. Packets are written-description outlines.

From `docs/research/docket/README.md` as of this session:

- **FILE:** P01 MOTIF, P02 Dual-lane, P03 Porosity, P04 Runtime-bind, P05 Adversarial engine, P06 Local free weights, P07 Core ledger + fence, P08 DOM-first, P09 Spend gate, P10 Resolver (narrow), P11 SEED / signed session close (narrow), P13 Thinkfast drop (takes the 12th slot).
- **HOLD:** P12 Crucible (PDJ triad already claimed elsewhere).
- **TABLED:** P03 Public Tensor — not a filing slot this BUILD.
- **NAMED this session:** P14 Patent attorney profile — adversarial seat inside Docket vetting. Not built. Does not click USPTO.

Micro-entity provisional cited in-session: **$65** each. Eleven FILE packets ≈ **$715** if all filed.

---

## Priority and prior art (this session)

| Event | Date | Kind |
|---|---|---|
| `bts-mesh` public GitHub | 2026-08-16 | Working build / publication |
| `cosmos` public GitHub + ratified architecture | 2026-08-23 | Working build / publication |
| CONTINUITY paper (Zheng & Yang, ZAST) | submitted 2026-09-03, dated 2026-09-04 | Research paper + MIT code. **No USPTO filing found.** arXiv 2609.05269 |

US grace period from own disclosure: about **one year from 2026-08-23**, not "file tomorrow."

A public GitHub build is a publication date, not a patent filing. It does **not** stop CONTINUITY authors from filing a provisional tomorrow with a 2026-09-04 priority. It does stop them from claiming you copied them.

A working build helps **enablement**. For **priority**, paper and build are equal publications. The earlier date is still the build.

CONTINUITY is close on: signed root grants, signed provenance/context manifests, typed releases, effect-bound permits, verifier that refuses effects without a valid witness.

**What is not in that paper (session view):** fencing tokens + hash-chained ledger + fail-closed refusal on missing manifest + bite-test methodology that pins predecessor failure before the fix. Treat 2026-09-04 as the new baseline, not a footnote.

---

## Combinations this session ranked as strongest

Already overlapping P07 / P11 / backup work. Novelty lives in the **combination**, not "multi-agent orchestration" or "a signed manifest" alone.

1. **Signed context manifest at session close** — inherited facts, active leases, open watchers, handoff recipient; refuse to close without a valid one. Tie to fencing tokens + hash-chained ledger + fail-closed missing manifest.
2. **Fenced commit gateway** — attempt-private workspaces; publish only after fencing token + expected input hashes. Typed, auditable refusals. Strongest against Alice-style concurrent writers.
3. **Backup verification loop + bite tests** — hash-verified per file, scoped by irreplaceability, fail loud, rehearsed restore as a scheduled job. "Backup is a scheduled job with verification or it is not a backup." Prior art on backup verification is heavy; claims need care.

Weaker alone: generic orchestration / routing. Yellow.ai, Salesforce, OpenAI, Wesco already occupy that space.

---

## New candidates surfaced this session (not already a packet)

These were searched from the repo in-session. Not drafted as packets yet.

1. **Typed refusal taxonomy as a machine-readable contract.** ~160 modules, ~55 error classes, ~141 kinds, each `(kind, detail)`. Taxonomy generated from code. Callers branch on `kind`. Fail-closed typed absence instead of silent fallback. Distinct from P07 / P11 if claimed as the contract, not the ledger.
2. **Prompt-cache prefix rule as a routing primitive.** Stable prefix + append-only tail, exact byte match, measured `cached_tokens` never assumed. Thin prior art. Cheap to file.
3. **Designated access matrix / two-pen split, OS-enforced.** Started as folder grants (GrokBot `V:\Ai`, Grok Code `V:\A`, OpenWork `V:\Streams\openwork`). Strengthened in-session to:
   - each agent gets a **designated** read / write / deny matrix across **drive letters** (or Linux mounts),
   - kernel-enforced (Windows restricted token + job object at spawn; Linux mount namespace / Landlock),
   - no separate Windows user logins — daemon spawns the child under the restricted token,
   - typed refusal when the agent crosses the matrix.
   **Not implemented yet.** Idea predates this chat (drive letters thought earlier). Restricted tokens themselves are old Windows plumbing and used by other agent sandboxes. The open angle is the **per-agent designated matrix across host drive letters in a multi-vendor mesh, with fail-closed typed refusals.**
   Claim must describe matrix + kernel enforcement, not folder convention.

---

## Capability tensor (today's extra idea)

Pairwise overlap tensor. Axes = themes (novelty, enablement, prior-art proximity, claim breadth, error type, domain). Cells = porosity + orthogonality between two agents' outputs.

Use: pick contraposed models by **tensor distance** (least overlapping failure modes), not reputation.

Publication path discussed: hashes on-chain, vectors off-chain, anyone can append a row → living standard.

**Split filings (Perplexity, agreed in-session):**

- Tensor / measurement method = one provisional.
- Chain distribution / consensus = a different provisional.
- Do **not** bundle with the fencing-ledger-manifest mechanism patents.

P03 Public Tensor is already **TABLED**. Do not promote it back into the same application as P07 / P11.

Strategy stated: **patent the mechanism, standard the interface.** Own the core; open the edges.

---

## Process notes from this chat

- Adversarial review is already the loop (Ara, Perplexity, others). P14 is the attorney-profile seat: claim drafting, enablement, prosecution risk. Independence rule borrowed from Crucible — seat must not see other agents' reasoning first.
- Ideas that live only in CCr / Grokbot session memory are **not** a publication date. Write them down (repo or Drive) before filing.
- A provisional needs a written description, not working code. File the restricted-token matrix as description first if the date matters; implement after.
- Mesh has been running since June/July 2026; that helps enablement narrative, not priority over the August GitHub dates.

---

## Out of scope for this note

Anthropic wipe / ban / lawsuit discussion in the same session is **not** patent subject matter. Do not mix it into packets.

---

## Suggested next Docket steps

1. Write a short spec for the designated access matrix (drive letters + spawn-time restricted token + typed refusal) so the idea has a dated text.
2. Decide whether refusal-taxonomy and cache-prefix get their own thin packets or fold into P07 / P11 / P04.
3. Keep tensor + chain as separate TABLED / later provisionals.
4. Run P14 seat against CONTINUITY as the new baseline before any FILE packet is sent to USPTO.
5. Filing stays Legal + Keith. This note does not click USPTO.
