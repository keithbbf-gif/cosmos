# MOTIF public pack (Keith 2026-09-07)

Four pieces, one argument. **Keith 2026-09-07: don't publish anything yet.**
Drafts stay on disk. This TUI does not click X, LinkedIn, arXiv, or USPTO.

Posting any of them later is **another public disclosure** on top of GitHub
(`bts-mesh` 2026-08-16, `cosmos` 2026-08-23). Legal files provisionals.

| File | Channel | Form |
|---|---|---|
| `MOTIF_WHITEPAPER.md` + `MOTIF_WHITEPAPER.pdf` | Site, partners, deck | Long form (~2,200–2,800 w). SOP lives here. Pointer table is the proof box. |
| `MOTIF_X.md` | X.com | **Article** (paste into X Articles; ~1,000–1,500 w, subheads) plus optional **6–8 post** thread (excerpts, not a chop). |
| `MOTIF_LINKEDIN.md` | LinkedIn | Native article (title + body ~1,200–1,600 w) plus share commentary (~140–210 chars) at the top of the file. |
| `arxiv/motif_swiss_cheese.tex` | [arXiv.org](https://arxiv.org) (Cornell) | Submit the **.tex**. Preview PDF is `arxiv/motif_swiss_cheese.pdf`. Suggested: `cs.SE` primary, `cs.AI` cross-list. Research article of an implemented system. |

`_preview/` is local raster of the PDFs (layout check). Do not post those PNGs.

**Do not** paste live ledger, keys, or local paths into posts.

## What this TUI will not do

- Click X / LinkedIn / arXiv / USPTO
- Invent a controlled benchmark
- Claim the combination is a granted patent

## arXiv note (CS category, Oct 2025+)

Review articles and *position papers* in arXiv CS generally need prior
journal/conference acceptance. The `.tex` is a **research article** of an
implemented OS and the method used to modify it while it stays up. Moderators
may still reclassify or bounce it. Compile with `pdflatex motif_swiss_cheese.tex`
(twice) if you want a LaTeX PDF; this machine had no `pdflatex`, so the preview
PDF is reportlab. Do not run the PDF builder from BUILD; CCr does.

Rebuild PDFs: `py -3 docs/publish/_build_pdfs.py`
