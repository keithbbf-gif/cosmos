# SOP — Broken token / dead rail (general)

**Scope:** any API lane (Vertex accounts, OpenRouter, OpenAI, Groq, Cursor,
Grok). A lane is GREEN when a single-token round trip succeeds, RED when it
fails. The meter shows the battery (budget/credit); the rail shows health.

**Canon:** `work_orders/ccr/vertex_ping.py` (Vertex) · `cosmos_kb.py query
"SELECT account, lane, status, key_file FROM keys"` (registry) ·
`docs/SOP_BROKEN_TOKEN.md` (this file).

## Detection (the ping)

Every lane gets a minimal round trip — one token out, one token back:

```
py -3.14 work_orders/ccr/vertex_ping.py
```

| Result | Meaning | Display |
|---|---|---|
| GREEN (HTTP 200 + candidate) | key works, rail live | rail **green** |
| RED (HTTP 401/403) | key bad / wrong scope / wrong project | rail **red** |
| RED (HTTP 429) | quota exhausted | rail **red**, meter shows battery |
| RED (HTTP 400) | endpoint/project wrong | rail **red** |
| NO KEY FILE | key never saved | rail **red**, "no key" |

## Display (cDeck)

- **Rail strip:** green dot = round trip OK; red dot = broken. Clicking a red
  dot opens the fix popup.
- **Meter (battery):** budget/credit remaining per lane. Red when near/over
  limit (e.g. OpenRouter 95% ALERT). The meter is the *battery*; the rail is
  the *health* — a lane can be GREEN with a low battery (works, nearly out) or
  RED with a full battery (broken key, plenty of credit).

## Fix popup (what it shows)

1. **What broke** — the measured error (401/403/429/400, from the ping).
2. **How to fix** — the corrective for that lane (below).
3. **Links** — the account page(s) for that lane.

## Fixes by lane

### Vertex (AaaAQ. keys)
| Symptom | Fix | Link |
|---|---|---|
| 403 on aiplatform | key lacks access to that project; check IAM / API key restrictions | https://console.cloud.google.com/apis/credentials |
| 403 on generativelanguage | Vertex keys need the project-scoped aiplatform endpoint — set the project id in the wallet config | https://console.cloud.google.com/vertex-ai |
| 401 | key wrong/revoked — re-save from the account | https://console.cloud.google.com/apis/credentials |
| 429 | quota/credit exhausted — check billing | https://console.cloud.google.com/billing |
| credit expired | credit_expiry passed — top up or new credit | https://console.cloud.google.com/billing |

### OpenRouter
| Symptom | Fix | Link |
|---|---|---|
| 401 | key wrong — re-save | https://openrouter.ai/settings/keys |
| 402/insufficient | balance low — top up | https://openrouter.ai/settings/credits |

### OpenAI (oa-api)
| Symptom | Fix | Link |
|---|---|---|
| 401 | key wrong/revoked | https://platform.openai.com/api-keys |
| 429/insufficient_quota | balance low | https://platform.openai.com/settings/organization/billing |

### Groq / Cursor / Grok / GitLab
| Lane | Fix | Link |
|---|---|---|
| Groq | re-mint key | https://console.groq.com/keys |
| Cursor | re-auth in Cursor | https://cursor.com/settings |
| Grok | re-mint token | https://console.x.ai |
| GitLab | re-mint PAT | https://gitlab.com/-/user_settings/personal_access_tokens |

## Rules

1. **Never print a key.** The ping reads from the vault; output shows
   GREEN/RED + error class only.
2. **UNMEASURED, never 0.** A lane that cannot be pinged (no project id, no
   key file) reports UNMEASURED, not GREEN.
3. **The popup links, it does not fix.** Keith does money and credentials; the
   popup takes him to the exact page.
4. **After a fix, re-ping.** The same command re-verifies; do not claim GREEN
   without a fresh round trip.
5. **Record the scar.** A lane that broke and was fixed gets a scar entry in
   the KB (scope=model or system, kind=BROKEN_TOKEN) with the corrective.

## Where this lives

- Ping: `work_orders/ccr/vertex_ping.py` (extend for non-Vertex lanes)
- Registry: `COSMOS_KB.json` → `keys` (the ORC's always-find map)
- This SOP: `docs/SOP_BROKEN_TOKEN.md`
- WO: `WO-20260920-003` (usage tracker + this SOP)