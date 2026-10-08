# Contract for every Hermes proposal

Read this file before writing code. The live COSMOS tree is read-only.
Write only inside `V:\streams\hermes\proposals/<your-slug>/`.

## What you are building

A review copy of one Hermes feature, rewritten for COSMOS. CCr may later land it.
You do not land it. You do not edit `V:\A\Ai\COSMOS`, `V:\streams\cosmos_code`,
`CONTRACT.md`, `FEATURES.md`, `cosmos_hermes`, or any other proposal.

Hermes documents describe the behavior. Do not clone
`NousResearch/hermes-agent` and do not paste its source. Re-express the behavior
in original code.

## Laws

- Fail closed. An unknown mode, an empty allowlist, a missing credential id, or an
  unclassified action refuses. There is no `off` and no `yolo`.
- The proposal performs no network, socket, subprocess, thread, sleep, or file write
  outside a path the test injects under `tmp_path`. Prefer pure functions.
- Do not call `exec`, `eval`, `compile` on attacker text, `pickle`, `subprocess`,
  `socket`, `urllib`, or `requests`.
- Do not spawn a scheduler, a cron thread, or a HTTP server. Return a descriptor
  a later COSMOS clock or service would execute.
- SQLite, if you use it, is a projection: `rebuild()` from caller-supplied records
  reproduces it. A missing index is the code `UNMEASURED`, not an empty success
  and not a new file created on read.
- Secrets: accept credential **ids**. Refuse raw key material (`sk-…`, `api_key=`,
  `Bearer …`). `repr` of every public object must stay free of those shapes.
  Compare tokens with `cosmos_hermes.const_eq`.
- Paths go through `cosmos_hermes.PathJail` when a path is accepted.
- Bound every string and byte string with `bound_text` / `bound_bytes` before use.
- Caps are policy. A caller who asks for a higher cap is ignored and the policy cap
  is recorded. Do not raise the cap.
- One confirming retry at most, and only for a named failure class. No retry loops.
- Deterministic: same inputs, same outputs. No clock reads except a timestamp the
  caller passes in.
- Type every function. Frozen dataclasses with slots for records. A module-level
  `SCHEMA = "cosmos-hermes-<slug>/1"` string.
- Public functions and classes go in `__all__`.
- Tests use only the standard library and `cosmos_hermes`. No network. Cover each
  refusal code at least once. Cover the success path. Cover the cap.

## Files you write

- `proposals/<slug>/MAP.md` — Hermes behavior, the live COSMOS module that already
  owns the seam (or "new seam"), the operations this proposal adds, where authority
  lives (ledger, projection, attempt workspace, or human), the refusal codes, and
  one short paragraph on how CCr would land it later.
- `proposals/<slug>/<slug>.py` — the implementation.
- `proposals/<slug>/test_<slug>.py` — pytest.

Extra modules may sit in the same directory and be imported by `<slug>.py`.
Import only `cosmos_hermes` and the standard library. Do not import a sibling proposal.

## 4C

From `V:\streams\hermes`, fix the slug until all four pass:

```
py -3.14 -m py_compile proposals/<slug>/<slug>.py proposals/<slug>/test_<slug>.py
py -3.14 -m ruff check proposals/<slug>
py -3.14 -m mypy --strict proposals/<slug>/<slug>.py proposals/<slug>/test_<slug>.py
py -3.14 -m pytest proposals/<slug>/test_<slug>.py -q -p no:cacheprovider --tb=short
```

`mypy --strict` must pass. A missing tool is reported as MISSING; do not pretend it passed.

## Style

Affirmative sentences in MAP.md. Short docstrings. No narration comments.
Line length is fine past 100; ruff ignores E501. Select E, F, I.
