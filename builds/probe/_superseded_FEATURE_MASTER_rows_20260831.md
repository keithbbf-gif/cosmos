# SUPERSEDED TEXT — `docs/FEATURE_MASTER.md`, 2026-08-31 (F-63 re-audit)

Never-delete record. `docs/FEATURE_MASTER.md` is **untracked by git** (`git ls-files
--error-unmatch` → *"did not match any file(s) known to git"*), so git preserves no
prior version. Two passages were REPLACED rather than appended to; both are recorded
here verbatim. Everything else changed in that file was additive (F-60 row, rank 10, §5
bullet — original wording still present, amended in place).

Staged inside the assignment fence (`builds/backup/`, `builds/probe/`, `docs/`) because
`_delme/` is outside it. Move to `_delme/predispose_FEATURE_MASTER_20260831/` at COW's
discretion.

---

## 1. Row F-63 — Status + Evidence columns, as they read before

> | F-63 | **Session-transcript mining** — flag unaddressed questions/requests | `BACKLOG.md:49-58` | **ABSENT** | `cosmos_context_pull.py` can tail a session transcript, but grepping `context_pull` across `cosmos/` returns **2 files** and **WD2 is not one of them**. Nothing flags an unanswered ask from a transcript. *(This document is the manual substitute, and it is not a daemon.)* | High | M |

**Why superseded:** the ABSENT verdict was correct when written and is no longer.
`builds/probe/cosmos_askmine.py` now does exactly this and has been run (862 + 534
transcripts). The row is now PARTIAL — the tool is a probe prototype, not promoted to
`cosmos/`, not in `CLOCKS`, and **the grep fact quoted above is still true**: WD2 still
does not reference `context_pull`, and now does not reference `askmine` either.

## 2. Rank 13 — the "Why" cell, as it read before

> | 13 | **F-63 — session-transcript mining** | The only reason this document had to be written by hand. WD2 already has the parser shape and `cosmos_context_pull` already tails transcripts; nothing joins them | `cosmos/` | M |

**Why superseded:** "nothing joins them" is no longer accurate — the join now exists in
`builds/probe/`. The first sentence is retained verbatim in the new cell. Effort M → S
because the remaining work is promotion, not construction.

---

Both replacements are argued from artifacts listed in
`docs/UNANSWERED_ASKS_2026-08-31.md` and reproduced in
`docs/CHANGELOG_2026-08-30_CC_AUDIT.md` (entry *2026-08-31 · F-63 SESSION-TRANSCRIPT
MINING*).
