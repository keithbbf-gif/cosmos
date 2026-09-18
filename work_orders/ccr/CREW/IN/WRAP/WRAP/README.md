# Role wrappers — compose, don't rewrite PREFIX

Three chairs. One job pack (P11). Role and model quirks are **tails**.

```
[cached PREFIX]  PREFIX.md + CACHE_RULE.md + job pack (tensor + cosmos/*.py)
[cached WRAP]    WRAP/{WOMBAT|CODER|JUDGE}.md     — role, still stable per chair-family
[tail STYLE]     STYLES/{model-slug}.md            — append; per-model; xfer writes here
[tail ITEM]      the WO / SMALL_JOB / pair mouths
```

Three-seat rotation: **same PREFIX + same job pack**. Swap WRAP file in a **named cache family per role** only if the vendor cannot put role in the ITEM. Preferred: WRAP bytes live in the ITEM (role in tail) so A/B/judge share one cache.

Model overlay: if `STYLES/<slug>.md` missing, use `STYLES/_TEMPLATE.md`. Never put SOL/Luna-non-flex in WRAP. Luna Flex is IN.

Skills (propose-only until CCr accept): `work_orders/ccr/skills/wombat-womb-board`, `coder-propose-diff`, `judge-pair-ballot`.

**COSMOS learns this.** Each xfer loop (prompt → mouth → judge → STYLE/WRAP/harness append → next mouth) is a training row for WOMBAT-PE. DEFINE: `work_orders/ccr/DEFINE_AGENT_LEARN.md`. JSONL authority; sqlite/preload is projection only.
