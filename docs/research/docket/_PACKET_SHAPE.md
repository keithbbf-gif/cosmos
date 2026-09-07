# Provisional packet shape (Legal, not USPTO)

Each `Pxx_*.md` is a **complete written description** for a US provisional,
arranged for later citation by a court or examiner. Not a filed application.
Not claims. Not a novelty opinion. Keith + Legal file.

Form: `SPEC_FORM.md`. Printer: `_print_specs.py`. PDFs: `specs/`.

## Arrangement (37 CFR 1.77, adapted)

1. Cover / caption (docket, title, status, legend, inventor blank)
2. Cross-reference (sisters named; **no** claim of benefit)
3. Field of the invention
4. Background (problem / scar; related art as information known to applicant)
5. Brief summary
6. Definitions
7. Brief description of the drawings (drawings-in-prose)
8. Detailed description (enablement; numbered paragraphs `[0001]`)
9. Best mode (the in-tree embodiment)
10. Further embodiments
11. Disclosure clock (already public)
12. Information concerning related art (not an IDS; not a novelty opinion)
13. What this disclosure is not
14. Statement of invention (**not claims** — counsel drafts claims)
15. Appendix to attach at filing (`HOW_IT_WORKS.pdf`)

## Court-form PDF

Letter, 1-inch margins, Times 12/16, line numbers, page n of m, docket
header. FILE packets: `NOT FILED — FOR COUNSEL`. P12: red `HOLD`.

Each FILE packet is **standalone**. Duplicate the how-it-works appendix
into each filing. Do not add technical matter after a filing date
(37 CFR 1.53(c)).
