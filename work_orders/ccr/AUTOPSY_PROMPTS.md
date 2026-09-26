# Autopsy — why Output was empty (all 157 prompts)

Looked at `_prompt` / `Task` / `_argv` on every `live/state/work_orders/failed/*.json`.
JSONL: `CREW/OUT/TRANSFER/FAILED_AUTOPSY.jsonl` (157 rows). **None fulfill as-is** — as-is re-fires the same death.

## Why empty

| n | Why (from the prompt/argv, not the rc) | Fulfill? |
|---|---|---|
| **112** | Same prompt clone: `Drive the MOTIF route from WISHLIST/BACKLOG. Drop work in the box…` Agent `prepaid-orch`. `_argv` = `grok --single <that>`. Extra **grok.exe**. No Output file. | **No as-is.** One MOTIF-driver WO is enough; 111 are corpses of the same spawn. WD2 already drives MOTIF. Dispose `superseded_wd2`. Token leak. |
| **5** | P10 propose / runtime-binding parts 1–3. Grok-4.6, empty Output. | **Modify-retry** via Gitur/GAC, not grok.exe. Check LiT first (binding may already be on unique HEAD). |
| **1** | “You are JUDGE…” grok spawn, empty. | **No as-is.** Judge is WRAP+daemon, not grok.exe. |
| **35** | `NO_CONTEXT` — prompt never ran. Context source was `SOP.md` missing **or** one concatenated ` · ` string. | **Modify-retry** with **list** CTX. Salvage Task. GAC. attempt 2. |
| **3** | Unreadable JSON in bucket. | **Discard** corrupt. |
| **1** | Gemini empty Output. | **Modify-retry** GAC. |

## Partners / judge (again)

118 failed had **no partner**. 24 failed with a live partner — **never judged** (prompts never asked for a pair ballot). Judge wasn’t in `_argv`.

## Token economy

112× prepaid grok MOTIF-driver is the pile. **Do not retry those 112.** Daemon already does MOTIF every 15s. Keep **one** definition if WD2 is down; else close all 112 as `superseded_wd2` after JSONL rows.

Zero of 157 can be fulfilled **as-is**.
