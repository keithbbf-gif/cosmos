---
name: final-audit-vet
description: Final quality-gate audit of Gitur candidate patches before Scribe. Not for writing code.
---
# Final Audit Vetting Protocol

1. 4Cs integrity: py_compile clean, ruff zero, mypy intact, pytest no regressions.
2. Estate sync: clean apply on V:\, GitHub Actions, GitLab CI (CRLF/LF, no hardcoded `V:\` in generic modules).
3. Scribe handoff: staging manifest with files + target hashes for atomic commit/sync/ledger under the 75% context ceiling.
