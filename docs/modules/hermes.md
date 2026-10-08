# Hermes

## What it is

Review copies of NousResearch/hermes-agent features, rewritten as original Python for COSMOS. Each slug under `proposals/<slug>/` is one feature: a module, a `MAP.md`, and a pytest. Shared law is `cosmos_hermes`. Live seams stay the authority: `cosmos_approval`, `cosmos_delegate`, `cosmos_recall`, `cosmos_skills`, `cosmos_nlcron`, `cosmos_sandbox`, `cosmos_mcp_client`, `cosmos_cred_kit`, `cosmos_dom`, `cosmos_spend`, and `cosmos_sched`. A proposal still refuses the action it was written to refuse. The feature table is `hermes/FEATURES.md`. Behavior source is the public NousResearch hermes-agent docs, not a paste of that repo.

## Where it lives

Repo path: `V:\A\Ai\COSMOS\hermes`. Applied 2026-10-07 from `V:\streams\hermes`. The streams original stays in place. Package name: `cosmos-hermes-proposals`.

## Entry points

Checker, from this folder: `py -3.14 check4.py` (`check4.main`). It runs `py_compile`, `ruff`, `mypy --strict`, and `pytest`. A missing checker is `MISSING` (exit 127). Pytest exit 5 is `NO_TESTS` and blocks.

Shared public names: `PathJail`, `Refuse`, `bound_bytes`, `bound_int`, `bound_text`, `const_eq`, `redact`, `secret_shape`.

Each proposal exports its own `__all__`. The credential-pool review module is `CredentialPool` (`add`, `next_id`, `report`, `status`, `change_provider`, `reveal`, `records`), plus `rebuild` and `reveal`. `reveal` always refuses. Setup-portal names are `plan`, `persist`, `open_port`, and `confirm`. There is no installer CLI.

## What it refuses

The live tree, `CCR.lease`, and a second ledger. Proposals perform no network, socket, subprocess, or file write outside a path a test injects. No `yolo`, no `off`, no in-process cron, no self-activating skill, no second spend gate, no second scheduler. Unknown mode, empty allowlist, missing credential id, and an unclassified action refuse. Secrets are ids. Raw key shapes refuse (`SECRET` / `PLAINTEXT`). Caps are policy; a higher request is ignored. SQLite, if used, is a projection: `rebuild` from caller records, and a missing index is `UNMEASURED`.

Credential-pool install onto the live tree is TABLED. This package does not install keys.

## What it is not

Not `rkchoudary/hermes`. That idea already landed as `cosmos_action_chain.py`. Not a clone of NousResearch/hermes-agent. Not a replacement for the live seams. Not a running gateway, cron, or key vault. `CredentialPool` is an in-memory id ledger for one provider. It does not reveal secrets, change provider, or fall back to another provider.

## Grade

On main `501fdee2` (2026-10-08), the package 4C passed `py_compile`, `ruff`, `mypy`, and `pytest`. That is the recorded grade. It was not re-run for this note.
