# web_dashboard

Hermes serves a local management page on `127.0.0.1:9119`. The page reads status, sessions, config, keys, logs, analytics, cron, profiles, skills, MCP, webhooks, pairing, channels, and system state. A bind to any other host turns on an auth gate and refuses to start when no auth provider is configured. The old insecure flag does not turn that gate off. Writes (config, env, sessions, cron, skills, gateway, hooks, chat launch) change the installation. Plugin widgets are display ids, not imported modules. Chat on that page starts a terminal. This proposal does none of those side effects.

The live seam is projection panels. `cosmos/cosmos_kdash.py` paints read-only cards and is not authority. `cosmos/cosmos_service.py` is the only listener: a remote bind refuses open access. This proposal does not import either module.

## Operations

`panels()` and `panel(name)` return frozen page records. They take no nonce.

`Dashboard.rebuild(rows)` replaces the projection from caller-supplied `Reading` values. `read(name)` returns rows for one panel and profile. It takes no nonce. Before the first rebuild the read and `records()` are `UNMEASURED`. An empty rebuild is measured and may return no rows. A failed rebuild leaves the previous rows in place. Text that is secret-shaped is refused and is not stored. `records()` returns the admitted rows in rebuild order. Rebuilding a fresh dashboard from those records reproduces each panel view.

`spend`, `queue`, and `leases` are projection panels for caller records (a card, a note, an amount, a session). They are not the spend authority, not the queue, and not a lease manager. `panel("pty")` and `panel("shell")` raise `BAD_PANEL`. `screen(body)` accepts display text and does not keep the body. An import of `pty`, `shell`, or `subprocess`, a `from os import system` or `popen`, or a call such as `pty.spawn`, `shell(...)`, `os.system`, or `subprocess.Popen` is `BAD_PANEL`. An identifier that only contains those letters, such as `empty` or `eggshell`, stays display text.

`grant(action, nonce)` records a human nonce for one closed action name. `mutate(action, nonce)` returns an `APPROVED` descriptor. An empty nonce raises `NEED_APPROVAL`. The nonce is hashed once and compared with `const_eq` on that sha256. The raw nonce is not stored. A spent nonce is `REPLAY`, including when a later grant is still open, and that replay does not consume the confirming retry. A well-formed mismatch is the single confirming retry (`BAD_NONCE`); the next mismatch is `RETRY_CAP`.

`check_bind(host, public_grant=False)` returns a listen descriptor. The only loopback host is `127.0.0.1`. Any other host raises `PUBLIC_BIND` unless `public_grant` is true or a credential id. An empty credential id is `BAD_GRANT`. A public plan still sets `auth_required`. `insecure=True` is recorded and ignored. The default port is 9119. No listener is opened.

`add_widget(name)` keeps a display id that matches `^[a-z0-9-]{1,32}$`. Any other name is `BAD_WIDGET`.

The row cap is 20. The widget cap is 8. A requested widget cap or row limit above policy is ignored, and the record stores the ask plus the applied cap. A lower positive widget cap is honored. The policy cap stays 8 on the policy record.

## Authority

Panel rows are a projection. They are not authority. The human nonce is the authority for a mutation, and the human public grant is the authority for a non-loopback descriptor. This module does not listen, does not write config or env, and does not start a chat terminal. A later service would apply an `APPROVED` descriptor. The ledger would store the nonce sha, not the nonce.

## Refusal codes

`NEED_APPROVAL`, `PUBLIC_BIND`, `BAD_WIDGET`, `UNKNOWN_PANEL`, `BAD_PANEL`, `BAD_ACTION`, `UNCLASSIFIED`, `SECRET`, `BAD_NONCE`, `UNGRANTED`, `RETRY_CAP`, `REPLAY`, `BAD_GRANT`, `BAD_HOST`, `NOT_BOOL`, `AT_CAP`, `ALREADY`, `BAD_ROW`, `BAD_KEY`, `BAD_PROFILE`, `BAD_SCHEMA`, `BAD_CODE`, `BAD_LIMIT`, `UNMEASURED`. Bounds also raise `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, and `OUT_OF_RANGE`. There is no `off` and no `yolo`. The confirming retry class is `BAD_NONCE` only.

## Landing

CCr would later fill these panel rows from the projection the service already serves, leave reads without a nonce, and require this nonce before any config, env, session, cron, skill, or gateway write. `check_bind` stays in front of the service listen: only `127.0.0.1` without a public grant, and a public grant still means auth is required. Widget names stay on the same shape. This package never becomes a second listener. `spend`, `queue`, and `leases` stay caller-supplied projections. A pty or shell panel stays refused.

## Ship

- operations: `ACTION_CAP`, `APPROVED`, `BODY_CAP`, `DEFAULT_PORT`, `DISPLAY`, `HOST_CAP`, `LOOPBACK`, `NONCE_CAP`, `PANELS`, `RETRY_FAILURE`, `ROW_CAP`, `SCAN_CAP`, `SCHEMA`, `VALUE_CAP`, `WIDGET_CAP`, `BindPlan`, `Dashboard`, `Display`, `Grant`, `Mutation`, `Panel`, `PanelView`, `Policy`, `Projection`, `Reading`, `Widget`, `add_widget`, `check_bind`, `grant`, `mutate`, `panel`, `panels`, `policy`, `read`, `rebuild`, `records`, `reset`, `screen`, `widgets`. `Dashboard` exposes `policy`, `rebuild`, `records`, `read`, `add_widget`, `widgets`, `grant`, and `mutate`.
- refusal codes: `NEED_APPROVAL`, `PUBLIC_BIND`, `BAD_WIDGET`, `UNKNOWN_PANEL`, `BAD_PANEL`, `BAD_ACTION`, `UNCLASSIFIED`, `SECRET`, `BAD_NONCE`, `UNGRANTED`, `RETRY_CAP`, `REPLAY`, `BAD_GRANT`, `BAD_HOST`, `NOT_BOOL`, `AT_CAP`, `ALREADY`, `BAD_ROW`, `BAD_KEY`, `BAD_PROFILE`, `BAD_SCHEMA`, `BAD_CODE`, `BAD_LIMIT`, `UNMEASURED`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`
- what this module still refuses to execute: a listen socket, an HTTP server, a PTY, a shell, a chat terminal, a config or env write, a cron run, a gateway restart, and a plugin import. `mutate` returns an `APPROVED` descriptor and does not apply it. `check_bind` returns a descriptor and does not bind. `screen` does not exec, eval, or compile the body. `insecure=True` does not turn the auth gate off. There is no `off` and no `yolo`. The only confirming retry is `BAD_NONCE`.
- hot-path shape: one pass at rebuild groups rows in a dict keyed by panel and profile; a read is that lookup plus a prefix that stops when the applied row window is full, so a later panel is not dropped when another panel is already full. Widget ids and panel keys are sets. A nonce is hashed once per grant or mutate, then compared with `const_eq` on the digest.
