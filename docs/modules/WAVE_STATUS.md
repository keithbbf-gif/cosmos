# Wave status

NOT DONE. This page does not close the tree.

Poll of `C:\Users\Papa\AppData\Local\Temp\c4-*-result.md` at 2026-10-08 13:58:52. Grades are the exits printed in those receipts. This judge did not re-run the suites, did not edit product code, and did not commit or stage.

SpendGate stays unbound. Jury chair in `docs/modules/JURY_SPENDGATE.md` is DO_NOT_BIND (BIND_NOW 1, BIND_READ_ONLY 1, DO_NOT_BIND 3). `c4-h19-result.md` records the same chair call: no merge of `credits_face_usd` and `meter.db`. The rails2 checkers do not bind it.

Dispatch stays locked. `c4-code-result.md` says `Provider.prepare_call` still raises `DISPATCH_LOCKED` and `propose` still returns `"done": False`. No provider was added.

Named receipts: `c4-rails2-result.md`, `c4-cdeck2-result.md`, `c4-fedclu-result.md`, and `c4-code-result.md` were all present. None of those four were absent.

OPEN is only a missing receipt. No row below is OPEN.

| work item | receipt file | exit | grade |
| --- | --- | --- | --- |
| rails2 | `c4-rails2-result.md` | 0 | PASS |
| cdeck2 | `c4-cdeck2-result.md` | pytest 5 failed, 33 passed; `node --check` 0 | FAIL |
| fedclu | `c4-fedclu-result.md` | 0 | PASS |
| code | `c4-code-result.md` | 0 | PASS |
| cdeck | `c4-cdeck-result.md` | pytest 1; ruff 1; py_compile 0 | FAIL |
| clone | `c4-clone-result.md` | integer not printed; banner 8 passed | PASS |
| core | `c4-core-result.md` | ruff 1; `test_rail_base.py` 5; py_compile 0; mypy 0 | FAIL |
| core2 | `c4-core2-result.md` | 0 on ruff, py_compile, mypy, pytest, rail script; hermes-features script 1 | FAIL |
| h11 | `c4-h11-result.md` | 0 | PASS |
| h12 | `c4-h12-result.md` | 0 | PASS |
| h13 | `c4-h13-result.md` | 0 | PASS |
| h15 | `c4-h15-result.md` | py_compile 0; selftest 0; ruff 1 | FAIL |
| h16 | `c4-h16-result.md` | 0 | PASS |
| h17 | `c4-h17-result.md` | 0 | PASS |
| h18 | `c4-h18-result.md` | none | PASS |
| h19 | `c4-h19-result.md` | none | PASS |
| h20 | `c4-h20-result.md` | none | PASS |
| hermes | `c4-hermes-result.md` | 0 | PASS |
| meter | `c4-meter-result.md` | integer not printed; banner 7 passed | PASS |
| orc | `c4-orc-result.md` | 0 | PASS |
| orc2 | `c4-orc2-result.md` | py_compile 0; pytest banner 1 passed | PASS |
| pkt | `c4-pkt-result.md` | integer not printed; banner 11 passed | PASS |
| resession | `c4-resession-result.md` | 0 | PASS |
| seed | `c4-seed-result.md` | py_compile 0; pytest banner 30 passed | PASS |
| sessions | `c4-sessions-result.md` | py_compile 0; pytest 29 passed, 0 failed | PASS |
| small | `c4-small-result.md` | 0 after the clusters edit (before line was 1) | PASS |
| tokenctr | `c4-tokenctr-result.md` | 0 | PASS |
| voice | `c4-voice-result.md` | 0 | PASS |

## What a PASS row is not

- rails2 and tokenctr PASS are package checkers. They are not a SpendGate bind.
- code PASS leaves dispatch locked.
- hermes PASS is not a credential-pool install. The receipt says no key file was read.
- voice PASS says voice refine was not built.
- resession and h12 PASS are dry plans (`execute` false). The resession receipt says `spawn_auto_resession` still launches grok when `execute=True`.
- h17 PASS is 6 passed and 1 skipped. `cosmos_packets` was not created.
- h18, h19, and h20 PASS means the receipt is a doc write with no failing command. h18 says core 4C is not a blanket PASS. h19 says the resale desk is not finished and section 3 stays open. h20 does not claim cdeck passed. h20 also says sessions-page 4C was NOT_RUN; the later `c4-h13-result.md` prints `EXIT:0` (68/68) and is a separate row.
- orc2 did not run ruff. h16 later ran `tests/test_pilot_womb_http.py` at exit 0.
- clone, meter, and pkt print a pass banner and no fail line. The process integer is not in those three files.
- No `c4-h14-result.md` was in the poll. It is not one of the four named receipts, so it is not graded OPEN.

## FAIL rows

- cdeck and cdeck2: probe pytest still 5 failed, 33 passed. cdeck2 says those probes were not regenerated and were not run against the live server. `node --check` on `ui\header.js` was 0. The strip folds rows already on the page; the receipt does not claim the full ledger was read.
- core: ruff exit 1 on the listed modules except xtalk, and `tests/test_rail_base.py` exit 5.
- core2: checkers and the 50-test pytest are exit 0. `tests/test_hermes_features.py` as a script is exit 1 (50/51, SK6 text slice).
- h15: `stage6_gate.py` py_compile and selftest are exit 0. ruff `--select E,F,I` is exit 1 (10 E501). Pytest was not run.

## Later than this poll

The table above is the 13:58:52 poll. It was not rewritten. These receipts arrived after it, or the FAIL note needs the house bar next to it.

| work item | receipt | what it printed | grade on that print |
| --- | --- | --- | --- |
| h07 stagehand | `c4-h07-result.md` | py_compile 0, ruff 0, mypy 0, pytest 11 passed | PASS |
| h25 rails | `c4-h25-result.md` | pytest 10 passed, ruff 0 | PASS |
| h27 kdash | `c4-h27-result.md` | doc only, no HTML edit | PASS |
| H21 | `docs/modules/JUDGE_H21.md` | seven pytest suites exit 0 | NOT DONE |
| H22 | `docs/modules/JUDGE_H22.md` | voice 118 passed, duplex 66 passed | not a phone client |
| H23 | `docs/modules/JUDGE_H23.md` | ruff 0 and py_compile 0 on fourteen modules | PASS for that lint |

h07 fixed six stagehand holes: case-folded scheduler and READ destinations, HTML rejected in nested strings, extract schema required before `tools/call`, a non-string `expect` returns `BROKE`, a padded `file:` URL is refused, and the action cache returns copies. Unchecked property types, the constant `authority_ledger_written` flag, and observe-on-non-list were left as graded.

h25 adds rail `google` and unset Bedrock, OpenRouter, and Azure. Both stay off RunPod. The earlier rails2 row remains the 8-passed receipt.

House ruff ignores E501. The h15 exit 1 is ten line-length findings and no F or I finding. The selftest is exit 0. That row is not a behavior fail.

core2's hermes-features script line is the older 50/51 receipt. The skills GET branch in `cosmos_service.py` now contains the words `Never mkdir` and `UNMEASURED`. A run after that comment printed 51/51. This page did not re-run it. The core row's ruff exit 1 is the pre-`cosmos/ruff.toml` pass. core2 ruff on the fourteen modules is exit 0.

cdeck2 stays FAIL on the five stale probe files. Those probes were not run against port 8770.

h14 Open Sessions arrived while this section was being written. `c4-h14-result.md`: py_compile 0, script harness 5/5 exit 0, pytest exit 5 because the functions are named `t_*` (NO_TESTS). `open` on a missing projection now exits 2. It used to exit 0 because `NO_SOURCE` sets `ok` for an empty list. Legal id `cow-law` exits 2 and the transcript body is absent. The 666 sessions were not re-ingested. PASS on that script. Pytest exit 5 is not a product failure.

h01 nlcron is in. `c4-h01-result.md`: py_compile 0, ruff 0, mypy 0, pytest 12 passed. `daily 07:30` is no longer labeled COSMOS Backup. That label is an exact listed hour at `HH:00` only. `every 24 hours` and `every 1440 minutes` are `DAILY` with no `/st`. `every 25 hours`, `every 1441 minutes`, and a non-finite unit scale are `UNRECOGNIZED` instead of an illegal `schtasks` modifier or an `OverflowError`.

h26 spend/pay fence is in. `c4-h26-result.md`: pytest 2 passed, ruff 0. The test parses source with `ast` and does not import either package. No file under `cosmos\` imports `cosmos_pay`. No file under `tokenctr\` imports `cosmos_spend`. Product code was not changed. Jury chair stays DO_NOT_BIND.

h28 discover is in. `c4-h28-result.md`: pytest 3 passed, ruff 0, py_compile 0. The tests cover `inventory_hands` on a temp directory and the two argv planners. They do not call `probe_http`, `bind`, `poll_once`, `install_task`, `standup`, `write_heartbeat`, or `main`. `cosmos_discover.py` was not edited.

h03 sandbox is in. `c4-h03-result.md`: py_compile 0, ruff 0, mypy 0, pytest 14 passed. `\\.\V:\`, `\\localhost\V$\`, and `\\?\C:\Users\Papa\OneDrive` now refuse as `BACKEND_ISOLATION`. A pasted Daytona or E2B key raises `UNMEASURED` and does not open a socket or host-spawn. A child byte `0xFF` is captured with `errors="replace"` instead of a false `ok` and an empty stdout. No key still raises `UNCONFIGURED`.

h09 delegation module is in. `c4-h09-result.md`: py_compile 0, ruff 0, mypy 0, pytest 4 passed, and 7/7 delegation checks in `tests/test_hermes_features.py`. A bad iteration or a caps iterable that raises now fails before `DELEGATION_RESERVED`, so the slot does not stay open. A parent that is no longer `RUNNING` under the lock gets `BAD_PARENT` and no child. `sweep_stale` marks only delegation children, not the parent. `cosmos_service.py` was not edited.

h02 porosity is in. `c4-h02-result.md`: py_compile pass, ruff pass, mypy pass, pytest 4 passed, selftest 37/37. The Opus T formula and schema `/5` were not changed. NaN and non-numeric `error_mag` are refused. A missing rescue falls back to magnitude instead of scoring 0. The best co-variable cell is kept. Compare filters match the stored axis and the 80-character judge. SQLite counts `disagree="yes"` the same way the fold does. Hit-vector writes are all-or-nothing. `hook_trial` records each named model once. The observation lock covers the SQLite rebuild.

h04 spawn is in. `c4-h04-result.md`: py_compile 0, ruff 0, mypy 0, pytest 1 passed. Eight proved bugs are fixed. A partial `params` object no longer drops the style layer. A style name cannot walk out of `STYLES`. A blank role becomes `CODER`. An empty model is not recorded as filled, and it still does not refuse, because `apply(SpawnSpec())` is the landed selftest. A string argv containing `grok.exe` is refused. `grok.cmd --single` and `grok.bat --single` are refused. Whitespace-only tool names take the default list. `fail_xfer` writes the corpse after `archive` is attached. `grok.exe` was not started.

h05 recall is in. `c4-h05-result.md`: py_compile 0, ruff 0, mypy 0, pytest 4 passed. The feature script printed 56/56 on the run before an import-order split in that same test file. Search before refresh stays `UNMEASURED` and does not create `state\recall`. A ledger shorter than the checkpoint makes `search()` and `state_sha()` raise `TRUNCATED`. `indexed_sessions` counts stored rows only. A non-dict `CONVO_TURN` is skipped and the checkpoint still advances. `cosmos_service.py` was not edited.

h10 xtalk is in. `c4-h10-result.md`: py_compile 0, ruff 0, mypy 0, pytest 4 passed, `node --check` on `xtalk.js` 0. A `null` line is no longer skipped. A broken tail refuses append with `CHAIN` instead of `KeyError`, and that snapshot head is `UNMEASURED`. A non-object role row is `BAD_ROLE`. The selftest no longer marks absent OpenWork checks PASS. The page keeps `#xtEmpty`, and `DRY_RUN` is a notice. `builds/cdeck` and `cosmos_service.py` were not edited.

h29 cDeck strip is in. `c4-h29-result.md`: `node builds\cdeck\tests\header_meter_fold.js` exit 0, `assertions 102 passed`, `checks 7 passed, 0 failed`. `ui\header.js` was not changed. Empty windows stay the string `UNMEASURED`. A carried 0 stays 0. A row with no price does not invent dollars. A bad count throws `BAD_ROW` and the strip stays `UNMEASURED`. `settled_usd` from `GET /api/v1/spend` is not an input. The old probe pytest list was not re-run. cdeck2 stays 5 failed, 33 passed on those stale probes. The deck is not finished.

h08 session procedures are in. `c4-h08-result.md`: py_compile 0, ruff 0, mypy 0, pytest 3 passed. The 190000 close constant and the 200000 window were not changed. `cosmos_resession.py` was not edited. A padded hold and an unknown pause mode now fail closed. A bad token count no longer drops a usable context percent, and a boolean percent cannot force a close. Compaction at 190000 tokens closes. A quiet beat does not move `last_act_epoch`. Autosave redacts a secret-shaped rail in `running.toml`. One HARDLINE inbox skill no longer aborts the rest of the batch.

h06 approval is in. `c4-h06-result.md`: py_compile 0, ruff 0, mypy 0 on the approval module and two test files, pytest 6 passed, feature script 56/56. Rule matching uses NFKC text with format characters removed. The raw action is still what the scan and the action hash use. `rm -r -f`, `rm -f -r`, `Invoke-Expression (Invoke-RestMethod ...)`, `curl | sudo sh`, and `git -c ... push --force` stay HARDLINE. A plain `git push`, including `git -c ... push`, stays CONFIRM. `CONSUMED` and `DENIED` stick. `grant` and `deny` decide inside `append_guarded`. A zero-width lookalike cannot self-approve. `consume` refuses a ledgered HARDLINE grant and records `APPROVAL_REFUSED`. `cosmos_service.py` was not edited. `rm -f` alone, `rm -r` alone, and a path that lexically names the staging directory stay off those rules.

Every receipt this board was waiting on has arrived. That is not a finish. SpendGate stays unbound. Dispatch stays locked. cDeck pytest stays 5 failed, 33 passed on stale probes that were not run against port 8770. Token Center is not a live multi-provider sale. Seats stay HTTP 501. Resession plans stay `execute: false`. The 190000 close and the 200000 window were not changed. Nothing in this wave was committed. The live service on port 8770 was not restarted.

## Recheck after the writers returned

`C:\Users\Papa\AppData\Local\Temp\c4-wave-verify-result.md` is a read-only re-run. Nothing was edited.

- pytest on the 13 wave files: exit 0, `74 passed in 13.73s`
- `tests\test_hermes_features.py` as a script: exit 0, `56/56 passed`
- `node builds\cdeck\tests\header_meter_fold.js`: exit 0, `assertions 102 passed`, `checks 7 passed, 0 failed`

The cDeck probe list was not part of this recheck. This recheck does not bind SpendGate, unlock dispatch, or finish the tree.
