# Specification form — court-admissible written descriptions

**Keith 2026-09-07:** make the packets complete; format so a patent court
will admit and appreciate them.

These are **attorney work-product written descriptions** for counsel.
They are **not** filed applications. This TUI does not click USPTO.
Counsel drafts claims. Inventor legal name is a blank for counsel.
No novelty opinion.

## Why this form

A later court or PTAB cites a provisional by **paragraph number**, not by
a heading in a lab note. 35 U.S.C. 112(a) asks whether the disclosure
shows possession and enables a person of ordinary skill to make and use
the invention. 37 CFR 1.77 prefers a stable order. 37 CFR 1.52 prefers
letter paper, margins, and a legible 12-point proportional font.

Informal outline packets (the 2026-09-07 first pass) are not that
instrument. This pass is.

## Arrangement (37 CFR 1.77, adapted for a provisional)

Each FILE packet is a **standalone** specification. A provisional cannot
claim the benefit of a sister provisional. Duplicate the how-it-works
appendix into **each** filing. Do not add technical matter after a filing
date (37 CFR 1.53(c)). No IDS on a provisional.

1. Cover / caption (docket, title, status, legend)
2. Cross-reference (sisters named; **no** claim of benefit)
3. Field of the invention
4. Background (problem / scar; related art as information known to applicant)
5. Brief summary
6. Definitions
7. Brief description of the drawings (drawings-in-prose; sheet drawings optional)
8. Detailed description (enablement; numbered paragraphs)
9. Best mode (the in-tree embodiment)
10. Further embodiments
11. Disclosure clock (already public)
12. Information concerning related art (not an IDS; not a novelty opinion)
13. What this disclosure is not
14. Statement of invention (**not claims** — counsel drafts claims)
15. Appendix to attach at filing

## Typography the PDF must keep

| Rule | Value |
|---|---|
| Paper | Letter 8.5 x 11 in |
| Margins | 1.00 in all sides (left 1.00 in satisfies 2.5 cm) |
| Body | Times-Roman 12 pt, leading 16 pt (1.5 line) |
| Paragraph numbers | `[0001]` hanging indent; sequential through the spec |
| Line numbers | left margin, every line, court-style |
| Header | docket id + ATTORNEY WORK PRODUCT — NOT A FILED APPLICATION |
| Footer | Page n of m |
| Color | black text; HOLD packet may carry a red legend |
| Encoding | PDF with Title/Author/Subject metadata |

## What a court can cite

- Caption and docket (`COSMOS-P01` … `COSMOS-P13`)
- Paragraph `[0042]`
- `FIG. 1` as described in prose
- Best-mode embodiment as the live tree (`tree_id=KMesh-COSMOS-live`)
- Disclosure clock table (GitHub dates)

## What this TUI will not

Sign as inventor. Invent a legal name. Draft a numbered claim set.
Click Patent Center. Write `V:\Ai`. Post the pack. File P12 as a
plaintiff–defense–judge independent invention.

## Packets

FILE: P01–P11 and **P13** (12th $65 slot). **P12 HOLD.**
Appendix volume: `HOW_IT_WORKS.pdf` (SCAR, ROLD, carry-over, Core,
Crucible as skin, BTS-MESH). Duplicate into each FILE.

Printer: `docs/research/docket/_print_specs.py`.
Output: `docs/research/docket/specs/`.
