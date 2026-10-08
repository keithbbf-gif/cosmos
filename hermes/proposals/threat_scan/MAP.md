# threat_scan

A defensive classifier. It pairs with approval and does not approve, publish, or run anything. `scan` returns a frozen `Scan` with a code, a category, a label, and span offsets. `HARDLINE` covers force-publish, approval-bypass, pipe-to-interpreter, and destructive-wipe. `SECRET` covers secret-shaped text, including text that is otherwise ambiguous. `CLEAN` is only text that matches none of those. Empty text refuses. A hardline classification stays hardline.

Seam: `cosmos_approval.py`. A hardline classification stays hardline. This package does not import the live gate and does not replace it.

Labels are short operator intents: `git push --force`, `git push --force-with-lease`, `git push -f`, `disable approval`, `--yolo`, `/yolo`, `HERMES_YOLO_MODE`, `invoke-expression`, `curl |`, `rm -rf`, and `rm -fr`. Secret-shaped text is labeled `secret-shaped`. The raw key is not stored. `repr` of a scan stays free of `sk-`, `Bearer`, and `api_key=` shapes.

`TEXT_CAP` is 8000. A caller who asks for a higher cap is ignored. The applied cap and the asked cap are both recorded on `Policy`. A lower ask is kept. There is no retry loop.

## Ship

- operations: `APPROVAL_BYPASS`, `ASK_MAX`, `CATEGORIES`, `CLEAN`, `DESTRUCTIVE_WIPE`, `FORCE_PUBLISH`, `Finding`, `HARDLINE`, `LABELS`, `PIPE_TO_INTERPRETER`, `Policy`, `SECRET`, `SECRET_SHAPED`, `SCHEMA`, `Scan`, `TEXT_CAP`, `resolve_cap`, `scan`
- refusal codes: `EMPTY`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `BAD_CODE`, `BAD_SCAN`, `BAD_HIT`, `BAD_POLICY`
- what this module still refuses to execute: a push, a delete, a pipe, an approval change, a shell, or a network call. It does not rewrite the text, does not mint a grant, and does not turn a label into a bypass.
- hot-path shape: one operator pass over a module-level expression; category and label lookup is a dict; `secret_shape` runs once; secret spans are collected only after that match; a higher text cap is ignored

CCr would land this later by calling `scan` from the approval gate before a command is classified, keeping `cosmos_approval.py` as the only writer. A `HARDLINE` or `SECRET` scan stays a deny. This copy does not widen that gate.
