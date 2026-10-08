# Browser

Hermes browser tools navigate, snapshot an accessibility tree, click, type, scroll, press, go back, and answer a dialog. Interactive elements carry ref ids such as `@e1`. A snapshot is text. The policy cap is 15000 characters and the minimum is 1000. Truncation keeps whole lines. A password entry is a human confirmation that names a credential id. Cloud browsers, CDP attach, console evaluation, and local Chromium launch stay in Hermes. This proposal returns a DOM descriptor and does not launch a browser.

The live seam is `cosmos/cosmos_dom.py`. `DomWorker.run_attempt` already owns one contained attempt: an injected `Driver`, an ephemeral profile, ledger evidence, and the typed failures `UNREACHABLE`, `SESSION_EXPIRED`, `AUTH_REQUIRED`, and `BROKE`. `cosmos/cosmos_browser.py` is the read-only dump-dom driver behind that protocol. This proposal does not import either module. The descriptor `session` is the job id a later attempt would pass in. `require_session` records the preflight flag and does not open a profile.

`open_page` returns a frozen `DomDescriptor` for an `http` or `https` URL. `file:` URLs refuse with `FILE_URL`. A URL that contains `..` or an encoded dot-dot refuses with `DOTDOT`. `click`, `snapshot`, `type_text`, `scroll`, `press`, `back`, and `dialog` return descriptors for the same session. `type_text` with `password=True` stores a credential id, leaves the text empty, and uses code `CONFIRM`. `pack_snapshot` keeps lines that fit the recorded cap and skips a line that does not fit, including when a later line does fit. `plan` freezes the descriptors. `rebuild` from those descriptors returns the same plan. `snapshot` and `plan` record a cap no higher than 15000. `retry` schedules one confirming retry after `UNREACHABLE`. `run` raises `NO_LAUNCH`.

Authority for a real attempt stays on the DOM worker and its ledger. The attempt workspace stays the worker's ephemeral profile. A password descriptor waits for a human. This module holds no session cookie, no credential material, and no projection.

## Ship

- operations: `MAX_ATTEMPT`, `MIN_SNAPSHOT`, `PAGE_CAP`, `PLAN_CAP`, `PROMPT_CAP`, `SCHEMA`, `SELECTOR_CAP`, `SNAPSHOT_CAP`, `TEXT_CAP`, `URL_CAP`, `BrowserPlan`, `DomDescriptor`, `SnapshotView`, `back`, `click`, `dialog`, `open_page`, `pack_snapshot`, `plan`, `press`, `rebuild`, `retry`, `run`, `scroll`, `snapshot`, `type_text`
- refusal codes: `FILE_URL`, `DOTDOT`, `BAD_URL`, `BAD_SELECTOR`, `BAD_TEXT`, `BAD_ID`, `BAD_JOB`, `BAD_CODE`, `BAD_CAP`, `BAD_ATTEMPT`, `BAD_KEY`, `BAD_DIRECTION`, `BAD_DIALOG`, `BAD_PLAN`, `DUPLICATE`, `SECRET`, `NOT_BOOL`, `NOT_TEXT`, `NOT_INT`, `NULL_BYTE`, `OVERSIZE`, `OUT_OF_RANGE`, `NO_RETRY`, `RETRY_CAP`, `NO_LAUNCH`. Descriptor codes are `READY` and `CONFIRM`.
- what this module still refuses to execute: a browser launch, CDP attach, a cloud session, JavaScript evaluation, a screenshot, a file download, a profile copy, and any `file:` or dot-dot URL. `run` does not start a driver.
- hot-path shape: one pass over the URL, then one pass over snapshot lines that skips any line which does not fit the remaining budget.

CCr would later pass an `open_page` descriptor to `DomWorker.run_attempt` and keep click, snapshot, type, scroll, press, back, and dialog as descriptors until a driver on the same `Driver` seam accepts them. `run` stays a refusal in this package. Password `CONFIRM` stays on the approval rail. The snapshot cap stays 15000.
