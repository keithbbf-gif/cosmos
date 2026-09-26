# WO-20260920-003 — Vertex AI usage tracker (Cloud Monitoring)

**Grading pile entry.** Scored by JUDGE (not yet seated) with all other outputs.
**Prompt xfer (honest chain):** initial prompt = Keith 2026-09-20 directive:
*"track your real-time usage before it even registers on your billing statement"*
+ the pasted google-cloud-monitoring draft. Context included: the corrected
script (`work_orders/ccr/vertex_usage.py`), the key registry (6 Vertex
accounts), and the measured auth blockers.

---

## This job (initial prompt — verbatim)

> Here is a Python script using the google-cloud-monitoring library to fetch
> your exact Vertex AI token consumption metrics over a specified period. This
> allows you to track your real-time usage before it even registers on your
> billing statement.

## Measured state (what the coder must work from)

**Script ready:** `work_orders/ccr/vertex_usage.py` — valid metric types
(`aiplatform.googleapis.com/consumed_input_tokens` / `consumed_output_tokens`),
cumulative→delta alignment, per-model breakdown. Runs with a working credential.

**Auth blockers (measured 2026-09-20):**
- `V:\Research4\.secrets\gcp_billing_token.json` — expired 2026-07-16, refresh
  token dead (HTTP 400 on refresh attempt)
- `gcp_billing_oauth.json` — installed-app OAuth, scope
  `cloud-billing.readonly` only (no monitoring)
- Vertex API keys (`AaaAQ.` format) — inference only, cannot call Cloud
  Monitoring

**Accounts (from the KB key registry):**
| Account | Project | Key |
|---|---|---|
| joanna.bbf@gmail.com | project-5a33f910-1251-4d6a-bf9 | SAVED |
| orders.ggn@gmail.com | project-10b3a132-ec5b-41e9-a2c | SAVED |
| fruitaholics.com@gmail.com | **UNMEASURED** | SAVED |
| medicineman.mme@gmail.com | **UNMEASURED** | SAVED |
| patriotfuelstop.com@gmail.com | **UNMEASURED** | SAVED |
| ranny.bbf@gmail.com | UNMEASURED | RESERVED (Jack) |

## Deliverables (closed-form)

1. **Auth path** — propose ONE of:
   - Service account key(s) with `roles/monitoring.viewer` per project (best for
     automation), stored in `V:\Research4\.secrets\` as
     `vertex_monitoring_<account>.json`, wired via
     `GOOGLE_APPLICATION_CREDENTIALS`; OR
   - Re-run OAuth consent with `monitoring.read-only` scope (interactive).
   Do NOT invent credentials. Do NOT use the inference API keys for Monitoring.
2. **Project IDs** — obtain the UNMEASURED project ids for fruitaholics,
   medicineman, patriotfuelstop (from Keith or the GCP console). Record in the
   wallet configs + KB key registry.
3. **Run** — `py -3.14 work_orders/ccr/vertex_usage.py --project <id> --days 7
   --per-model` for each measured project. Output to
   `live/state/vertex_usage/<account>.json` (never under live/ unless named).
4. **Record** — write the token totals into the KB (new `usage` facet or a
   `live/state/vertex_usage/` projection) so the ORC can read usage down the
   columns like the rest of the KB.
5. **Broken-token SOP** — `docs/SOP_BROKEN_TOKEN.md` (already drafted): rail
   green/red from the ping, meter = battery, fix popup with account-page links,
   per-lane fix table, never-print-a-key rule. Wire the cDeck rail strip +
   meter to the ping results and the popup.

## Contracts (first and last)

- **First line:** NONE or `diff --git`. Propose only. No merge. No grok.exe.
- **Never:** print a key/token value, commit a credential, use an inference API
  key for Monitoring, invent a project id, claim usage measured without a
  successful API call.
- **UNMEASURED, never 0.** A project without a working credential reports
  UNMEASURED, not 0 tokens.
- **DONE** = at least one project returns a real token total from the API, and
  the auth path is documented for the rest.

## Verification

```
py -3.14 work_orders/ccr/vertex_usage.py --project project-5a33f910-1251-4d6a-bf9 --days 7
  → INPUT tokens: N | OUTPUT tokens: M   (real API values, not 0/UNMEASURED)
```

---

**Derivation chain:** Keith directive + pasted draft → corrected script +
measured auth blockers → this WO. Judge scores this entry against the same bar
as the singles.