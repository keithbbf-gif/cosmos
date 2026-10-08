# Hermes proposals for COSMOS

Applied 2026-10-07 from `V:\streams\hermes`. This folder is the copy on the COSMOS tree.

The live seams stay the authority: `cosmos_approval`, `cosmos_delegate`, `cosmos_recall`, `cosmos_skills`, `cosmos_nlcron`, `cosmos_sandbox`, `cosmos_mcp_client`, `cosmos_cred_kit`, `cosmos_dom`, `cosmos_spend`, and `cosmos_sched`. These modules do not replace them. A proposal still refuses the action it was written to refuse.

Source of behavior: the public docs for **NousResearch/hermes-agent**
(https://github.com/NousResearch/hermes-agent and
https://hermes-agent.nousresearch.com/docs/user-guide/features/overview).
This is not `rkchoudary/hermes`. That other repo is the action-chain / separation-of-duties
idea already landed as `cosmos_action_chain.py`.

Each feature is original Python under `proposals/<slug>/`. It follows COSMOS law:
one ledger when something becomes authority, projections rebuild, no `yolo`, no `off`,
no in-process cron, no self-activating skill, no second spend gate, no second scheduler.
Paths stay inside a grant. Secrets are ids, never stored or printed.

The 4C checkers are `py_compile`, `ruff`, `mypy`, and `pytest`.
Run them from this folder:

```
py -3.14 check4.py
```

A missing checker is MISSING. A failed checker blocks. Pytest exit 5 is NO_TESTS.
