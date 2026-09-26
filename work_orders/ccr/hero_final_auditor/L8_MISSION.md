# L8 — Final Auditor Mission & Output Contract

Grade 30 judged keeps: confirm Judge legitimacy (no co-failure), 4Cs green,
no governance/security breach. Per item ACCEPT or REJECT.

```json
{"schema": "cosmos-final-audit/1", "audit_batch_id": "audit-20260923T...",
 "auditor_model": "grok-4.7", "auditor_family": "xai", "batch_count": 30,
 "verdicts": [
  {"order_id": "wo-…", "decision": "ACCEPT",
   "rationale": "4Cs green. AST verified. Zero boundary leaks.",
   "forward_to": "scribe", "staging_path": "live/work/orders/wo-…/patch.diff"},
  {"order_id": "wo-…", "decision": "REJECT",
   "rationale": "Unescaped Windows path breaks POSIX CI.",
   "forward_to": "wombat_autopsy", "autopsy_code": "PATH_SYNTAX_REGRESSION"}]}
```
