# cDm

cDm is the Android dashboard under `builds/cdm`. It is a phone client of the COSMOS HTTP API. It is not VMC, not cDeck, and not Core. This page is a reading map of that tree. COSMOS is not finished. A debug APK, a unit-test run, or a green log is not a finished product, and this page does not claim one.

The app id is `com.cosmos.cdm`. `versionName` is `0.1.0`. Debug builds append `.debug` to the application id and `-debug` to the version name. Kotlin and Jetpack Compose. `minSdk` 26, `compileSdk` and `targetSdk` 34, Java and Kotlin target 17. The longer product note is `builds/cdm/SPEC.md`. The README in that folder still describes an older default port. Where this page and that README disagree, the Kotlin and the stage-6 probe below are the code.

## What it is

Four tabs, in `ui/CdmApp.kt`: Dashboard, Command, CREATE, Settings.

| Screen | What it does |
| --- | --- |
| Dashboard | Status, health, spend, jobs, rails, audit, tools, control, and the `/events` feed. Each card keeps a last-measured age. Cached `/api/*` is not treated as live. |
| Command | Text to `POST /api/v1/command`. A job post goes to `POST /api/v1/jobs`. |
| CREATE | Maker map from `GET /api/v1/makers`, register with `POST /api/v1/makers`. |
| Settings | Server URL, pause, and human-posted Claude/Grok pool notes. Those pools are UI-only. Posting one does not spend and does not call a model. |

CONTROL on the dashboard can post kill and resume. Kill does not send the bearer. An optional kill token stays in session memory.

`MouthDrop` can post `action=drop` on `/api/v1/voice_loop` with mouth `android`. That is a remote drop into the voice-loop seam Core already accepts. It is not the VMC voice app, and it does not keep a second copy of the work-order rules. Voice Drop (SGH to GitHub) does not call it.

Package layout under `app/src/main/java/com/cosmos/cdm/`:

| Path | Role |
| --- | --- |
| `data/CosmosApi.kt` | Paths, major version, fit. |
| `data/CosmosClient.kt` | OkHttp. Bearer on the wire when one was pasted. |
| `data/ConnLogic.kt` | Per-response kind and the connection headline. |
| `data/SettingsStore.kt` | URL, client id, human pools. Not the bearer. |
| `data/Idempotency.kt` | Client-side claim of a `request_id`. |
| `ui/` | Tabs, view model, panels. |
| `reference/CosmosClient.kt` | Older envelope pattern. Not the transport this app runs. |

`builds/cdm/reference/` holds that pattern file. The running client is `app/src/main/.../data/CosmosClient.kt`.

## The contract it speaks

`CosmosApi` is the only place that names the prefix. `MAJOR` is `1`. `PREFIX` is `/api/v1`. The client sends `X-Cdm-Api: 1` and `Accept: application/json`. A request id, when present, is `X-Request-Id`.

Paths that object builds: `status`, `health`, `spend`, `jobs`, `audit`, `rails`, `tools`, `command`, `voice_loop`, `kill`, `control/resume`, `makers` (optional `kind`), `events?since_seq=`, and `control` (optional `client_id`).

A v1 kernel often omits `api_version`. Absence is **Compatible**. This client is the v1 consumer. That absence is not a mismatch and it is not offline.

Fit is decided in `CosmosApi.classify`:

| Signal | Fit |
| --- | --- |
| HTTP 410 | Breaking |
| Body `error` is `API_MISMATCH` | Breaking |
| No declared major (missing, null, or not a number or version string) | Compatible |
| Declared major is `1` (`1`, `1.0.0`, `v1.4` — the integer before `.` or `-`) | Compatible |
| Declared major is anything else | Breaking |

The declared major is read from `api_version`, then `apiVersion`, then `version`. A JSON object or array in those fields is not a major. It does not by itself make the fit Breaking.

On a Breaking fit the client stamps `api_fit` `breaking` and sets `error` to `API_MISMATCH`, unless the error is already `API_MISMATCH` or `UNAUTHORIZED`. It does not parse that body as live v1 panels. The panel stores the mismatch detail and leaves the last parsed data in place, with its age. The foreign envelope is not the new live reading.

## Mismatch is not offline

Offline is a transport failure. Connect timeout is 8 seconds. A failed call becomes `{error: "offline", http_status: 0}`. GET retries that status-0 failure once. POST is never retried. OkHttp is capped at 8 requests so the poll loop does not fill `Dispatchers.IO`. `retryOnConnectionFailure` is off.

`ConnLogic.classify` checks in this order:

1. `http_status` 0, or `error` `offline` → `Offline`.
2. HTTP 401, or `error` `UNAUTHORIZED` → `Unauthorized`.
3. `error` `API_MISMATCH`, or `api_fit` `breaking`, or `CosmosApi` fit Breaking → `Mismatch`.
4. Any other non-2xx → `HttpError`.
5. Otherwise `Ok`.

A server that answers HTTP 200 with `api_version` `2.0` is `Mismatch`. A server that answers HTTP 410 is `Mismatch`. Neither case is `Offline`. Offline means the server did not answer. Mismatch means it answered and the contract is not `/api/v1`.

The headline in `summarize` checks the nine panel kinds in this order: status, health, spend, jobs, makers, rails, audit, tools, control. Unauthorized wins over mismatch. Mismatch wins over partial, degraded, and offline. One mismatched panel makes the headline `ConnKind.Mismatch` even when the others are ok. The top bar prints **API**, not **OFFLINE**. The message is the `CosmosApi` mismatch line: this cDm speaks `/api/v1`; the server is not that contract.

The other headlines, when nothing is unauthorized or mismatched:

| Condition | Headline |
| --- | --- |
| No panel ok, and at least one offline | `offline — COSMOS is not answering` |
| No panel ok, and none offline | `SERVER DOWN` |
| Status and health both ok, and nothing else failing | connected, with URL and rtt |
| Status and health both ok, something else failing | `PARTIAL` |
| Something ok, but status or health is not | `DEGRADED` |

One lucky panel is never LIVE. Command and event posts use the same classifier. A mismatch there is the label `API_MISMATCH`, not `OFFLINE`.

Cleartext is scoped. `res/xml/network_security_config.xml` allows HTTP only for `192.168.1.10`, `100.103.9.112`, `127.0.0.1`, `localhost`, and `10.0.2.2`. Any other host must be TLS. A cleartext refusal on an unlisted host is an I/O failure, so the client names it **offline**. That is still not an API-version mismatch. The phone never reached a contract check.

## Where it dials

Presets live in `SettingsStore`. They are host strings, not credentials, and not proof that a server is up.

| Constant | Value in code |
| --- | --- |
| `DEFAULT_URL` | `http://100.103.9.112:8770` |
| `TAILSCALE_URL` | the same Tailscale host and port |
| `LAN_URL` | `http://192.168.1.10:8770` |

Kernel `serve` defaults to port **8770**. Settings has a PORT 8770 rewrite for a URL that still names another port. `builds/cdm/README.md` and `SPEC.md` still say base port **8791**. That is the older deck note. The Kotlin presets do not use 8791.

SharedPreferences name `cdm_settings` may store the URL, a minted `cdm-` client id, and the human pool notes. Those prefs may be backed up. The bearer and the kill token are session memory only. They are not written to disk, so they cannot appear in a backup. This page does not contain a token. Leave the bearer blank only when that kernel was started with `--no-auth`.

Polling pauses while the process is in the background, and when Settings says pause. A URL change bumps a generation counter. A response that belongs to the previous URL is dropped. It does not paint the new connection.

`POST /api/v1/command` on the kernel reads `text`. `request_id` is forwarded and not honoured there yet. The phone ledger claims each id once. A second claim is `DUPLICATE_REQUEST_ID` and does not POST again. That is a client guard, not server idempotency.

## Build and the stage-6 gate

From `builds/cdm`, with JDK 17 and an Android SDK:

```text
gradlew.bat assembleDebug
gradlew.bat testDebugUnitTest
```

The debug APK path the gate expects is `app/build/outputs/apk/debug/app-debug.apk`. Unit tests cover parsers, version fit, the idempotency ledger, OkHttp against a mock server, and `ConnLogic` (including a v2 envelope as mismatch, and mismatch beating partial). This page does not report a pass count. The README names a GitHub Actions workflow. That workflow file is not in this repository's `.github` tree. Do not treat the README sentence as CI on this clone.

Stage 6 is not the unit tests. From `builds/cdm`:

```text
py -3.14 stage6_gate.py selftest
py -3.14 stage6_gate.py gate --live-root <runtime root>
```

`selftest` checks that `CosmosApi.kt` still declares major `1` and the same paths. Its own note says a green log is not stage 6.

`gate` takes the runtime root as an argument. It does not walk parents and it does not infer a root from the working directory. It reads the sentinel, hashes the APK, and GETs `/api/v1/status` with `X-Cdm-Api: 1`. If `config/api_token.txt` is present it sends that bearer. The proof redacts it. Do not paste the token or the proof file into docs or chat.

Default bases, in order: `http://127.0.0.1:8770`, `http://127.0.0.1:8791`, `http://100.103.9.112:8791`, `http://100.103.9.112:8770`. Repeat `--base` to replace that list.

The probe remembers an API mismatch and keeps trying the next base. A later base may be the v1 kernel. If some base answers v1 but the `tree_id` is wrong, the gate is `TREE_MISMATCH`. If the only answer is a foreign contract, the gate is `API_MISMATCH` ("kernel is not /api/v1"). It does not call that `KERNEL_OFFLINE`. `KERNEL_OFFLINE` is the case where no base produced ok, unauthorized, a tree mismatch, or a stored API mismatch. Unauthorized is its own refusal. A missing ledger sequence is `NO_LEDGER_HEAD`. A status body with no `served_at` is `NO_SERVED_AT`.

The proof file is `builds/cdm/STAGE6_GATE.json` unless `--proof` names another path. The gate's own record says `rc=0` is not the gate. The proof is `emitted` / `live_value`: tree id, ledger sequence, `served_at`, and the APK sha256. Those values have to come from the live tree. This page does not copy a proof.

cDm does not write the COSMOS ledger, does not take `CCR.lease`, and does not start Core. It is one client. Shipping the phone app does not finish COSMOS.
