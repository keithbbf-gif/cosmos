# L6 — Final Auditor Tool Matrix

| Tool | Permission | Scope |
|---|---|---|
| Read, Glob, Grep | ALLOWED | diffs, orders, judge scores, baselines |
| Bash | READ-ONLY | `git diff --check`, py_compile, AST inspect |
| Write/Edit | RESTRICTED | verdict batch JSON to `live/queue/audit_verdicts/` ONLY |
| Git push, live-tree write, `grok.exe` spawn | FORBIDDEN | — |
