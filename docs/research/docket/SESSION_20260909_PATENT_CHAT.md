# Session note — patent talk from Ara chat (2026-09-09)

**Source:** live Ara / Grok session, 2026-09-09.
**Status:** session capture only. Not a filing. Not claims. Not a novelty opinion.
**Assumption:** user said "parents"; this note treats that as **patents**. There was no family-parent discussion in the chat. P05 is already labeled FILE (parent) in the docket index — that is parent-*application*, not family.

---

## What already exists (confirmed against docket)

Zero USPTO filings. The docket is written-description packets, not applications.

| Slot | Packet | Docket status |
|---|---|---|
| P01 | MOTIF loop | FILE |
| P02 | Dual-lane BUILD | FILE |
| P03 | Porosity | FILE |
| P03b | Public tensor | TABLED (not a filing slot) |
| P04 | Runtime-bind | FILE |
| P05 | Adversarial engine | FILE (parent application) |
| P06 | Local free weights | FILE |
| P07 | Core ledger + fence + tokens | FILE |
| P08 | DOM-first rail | FILE |
| P09 | Spend gate | FILE |
| P10 | Resolver | FILE (narrow) |
| P11 | Signed session close / SEED | FILE (narrow) |
| P12 | Crucible seats | HOLD (PDJ triad granted in CN; claimed in US20260037351A1) |
| P13 | ThinkFast drop | FILE (takes the 12th slot while P12 is HOLD) |
| P14 | Patent attorney profile | NAMED 2026-09-09; not built; adversarial seat only |

Micro-entity provisional is $65. Eleven FILE packets ≈ $715 if all filed. CCr does not click USPTO. Legal + Keith dispose.

---

## Priority dates discussed in this chat

| Event | Date |
|---|---|
| bts-mesh public | 2026-08-16 |
| cosmos architecture public (fencing tokens, hash-chained ledger, fenced commit gateway, session-close manifests) | 2026-08-23 |
| CONTINUITY paper submitted | 2026-09-03 / posted 2026-09-04 |

CONTINUITY = arXiv 2609.05269, Zheng and Yang (ZAST). Research paper + MIT-licensed GitHub artifact. **No USPTO filing found.** It is prior art as a publication, not as a patent.

US grace period runs ~1 year from your own public disclosure (≈ through 2027-08-23 for the Aug 23 architecture). A working build helps enablement; it does not beat a later paper on priority by itself — the earlier *publication date* does. Absolute-novelty countries are already at risk for what GitHub enabled.

Docket already flagged CONTINUITY against P11.

---

## Combinations this chat treated as the live novelty (not isolated slogans)

These are the pieces the chat said survive after CONTINUITY crowded the bare "signed manifest" idea:

1. **Fencing tokens + hash-chained ledger + fail-closed refusal on a missing session-close manifest.** Manifest alone is crowded. The combination is the claim surface.
2. **Fenced commit gateway.** Workers execute in attempt-private workspaces. Publish only through a gateway that checks fencing token + expected input hashes. Typed, auditable refusals. Strongest "distributed systems, not vibes" angle from the chat.
3. **Backup as a verified scheduled job + bite-test methodology.** Hash-verified per file, scoped by irreplaceability, fail loud, rehearsed restore as a first-class job. Bite tests pin the predecessor failure before the fix. Prior art on backup verification is heavy; claim drafting has to stay on the AI-session / carry-over loop, not "we verify backups."

Orchestration-in-the-abstract was treated as weak (Yellow.ai, Salesforce, OpenAI, Wesco all sit there). Novelty has to live in the mechanisms above.

---

## New candidates raised in this chat (not already a named FILE packet)

### A. Typed refusal taxonomy as a machine-readable contract

Callers branch on `kind`. System refuses typed absence instead of silent fallback. Chat cited the live code surface (~160 modules, ~55 error classes, ~141 kinds, `(kind, detail)` shape, taxonomy generated from code). Distinct from P07 / P11 if claimed as the contract, not as "the system can error."

### B. Prompt-cache prefix rule as a routing primitive

Stable prefix + append-only tail. Exact byte match. Measured `cached_tokens`, never assumed. Thin prior-art discussion in-chat; cheap to file if it stays a method, not a slogan.

### C. Designated drive-letter access matrix + OS-level restricted tokens

Started as two-pen folder grants (GrokBot writes `V:\Ai`, Grok Code writes `V:\A`, OpenWork writes `V:\Streams\openwork`). Strengthened in-session to:

- each agent gets a **designated** read / write / deny matrix across host drive letters (not one-writer-one-drive only);
- Windows: restricted token + job object at spawn; NTFS ACLs on the assigned letters;
- Linux: mount namespaces or Landlock;
- kernel-enforced, not application-enforced;
- no separate Windows user login per agent;
- daemon must have enough privilege to mint restricted tokens (typically a service);
- typed refusal when the agent crosses the matrix.

**Not implemented yet.** Folder-grant convention is what AGENT_BOUNDARIES currently documents. Restricted tokens themselves are old Windows plumbing and are already used by other agent harnesses. The open angle discussed: multi-vendor mesh + per-agent designated matrix across host drive letters + fail-closed typed refusals.

Write the description down before filing. A provisional needs the matrix + kernel-enforcement story in text, not working code.

### D. Capability / porosity tensor as a selection standard

Pairwise overlap tensor. Axes = themes (security-context, enablement, prior-art proximity, claim breadth, error type, data domain). Cells = porosity + orthogonality scores between two agents' outputs. Use: pick contraposed models by tensor distance (least overlapping failure modes), not by reputation.

Related existing packet: P03 Porosity (FILE) and P03_PUBLIC_TENSOR (TABLED).

### E. On-chain publication of the tensor

Public, append-only, tamper-evident contribution layer so the tensor can become a shared standard. Chat consensus with Perplexity: **do not bundle this with the mechanism patents.** Tensor = measurement method. Chain = distribution / consensus layer. Two provisionals, cross-reference. Practical split: hashes on-chain, vectors off-chain, batched updates.

---

## Filing strategy stated in this chat

- Patent the **mechanism**. Publish the **interface** as a standard.
- Split tensor vs chain. Split mechanism vs standard.
- Do not wait on implementation of C before a provisional — written description is enough — but the description must exist in dated text first.
- Do not post public articles / X / LinkedIn / arXiv on these until provisionals are filed (already in docket README).
- Adversarial loop already running (Ara, Perplexity, others). P14 names the missing attorney-profile seat. Independence rule borrowed from Crucible: that seat should not see the other agents' reasoning before it submits.

---

## Prior-art names the chat actually used

Treat as a working list for Docket attackers, not a clearance:

- CONTINUITY / arXiv 2609.05269 (signed provenance + context manifests, typed releases, effect-bound permits, verifier refuses unwitnessed effects)
- OpenAI shared-workspace patent (docket already marks US12,405,822 B1 as anti-shape for P02)
- Salesforce multi-agent routing; Yellow.ai; Wesco
- Microsoft isolated-agents; Sandlock; Vercel per-user sandboxes
- DeepSeek harness / OpenAI Codex sandbox using restricted tokens
- Microsoft US12524210B2 and Google US20240311405A1 (already in VETTING.md for P06)
- US11943344B2 (already closest patent note on P07)
- CN grant + US20260037351A1 on PDJ (P12 HOLD)
- Backup-verification literature generally (heavy)

---

## Out of scope for this note

The same chat also covered the Anthropic wipe / ban / demand-letter thread and a Dario / SLAC biography check. Those are not patent subject matter. Do not fold them into packets.

---

## Suggested next Docket moves (from the chat, not ordered by Legal)

1. Write C (drive-letter matrix + restricted token) as a dated spec, then a packet.
2. Decide whether A and B get their own packets or fold into P07 / P09 / P11.
3. Keep D with P03; keep E split and tabled until the measurement rubric is operational.
4. Feed CONTINUITY as the new baseline into the P11 / P07 adversarial pass, not as a footnote.
5. Leave filing to Legal + Keith. This note does not click USPTO.
