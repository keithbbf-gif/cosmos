# gbridge - Motif stage-5 critique (gem-api)

As a DIFFERENT-family reviewer, I've conducted a Motif STAGE-5 critique of the `gbridge` application, focusing on adherence to specifications, design, and implementation quality.

Overall, the `gbridge` app for T1 slice 1 *substantially delivers its stated specification*. The design for synchronous `ask()`, typed refusals, injected transports, and fail-closed validation is well-articulated and largely implemented as described. The use of `Path` objects, atomic file operations, and SHA256 validation demonstrates a commitment to robustness. The self-test suite is comprehensive for this slice, explicitly testing all expected refusal kinds.

However, a STAGE-5 critique aims to uncover even subtle issues. Below is a list of defects, categorized by severity.

---

### Defects

**HIGH Severity**
*(Issues that could lead to data loss, security vulnerabilities, or complete failure of critical functionality under specific, non-trivial conditions.)*

1.  **File/Symbol:** `gbridge.py`, `MailboxTransport.poll`
    *   **Defect:** **Race Condition (Missing `os.replace` for reply files):** The `MailboxTransport.poll` method checks `p.exists()` and then attempts to read and parse the file. If the "bot" is writing the reply file directly (rather than atomically via `os.replace`), it's possible for `poll` to read a partially written or corrupted file before the bot completes its write. While `TORN_REPLY` catches hash mismatches, it doesn't prevent reading a malformed JSON file *before* a valid one is fully written, potentially leading to transient `TORN_REPLY` errors or other parsing failures during normal operation where the bot is genuinely trying to write a valid reply. The spec for `MailboxTransport.send` explicitly uses `os.replace` for robustness, but there's no mention or enforcement of this for the *bot's* reply writing. This means the *external system* (the bot) is implicitly relied upon to write atomically, which is not guaranteed by the `gbridge` contract for the bot itself.
    *   **Impact:** Increased likelihood of `TORN_REPLY` in scenarios where the bot is mid-write, even for valid replies. Potential for transient errors causing unnecessary retries or failed attempts to collect answers.
    *   **Spec Delivery:** Partially adheres. The `gbridge` side handles a torn reply gracefully, but the architecture implicitly assumes the external writer (the "bot") writes atomically, which isn't enforced by `gbridge` or the `MailboxTransport` API for incoming messages, unlike outgoing ones. This could make `gbridge` appear less robust than intended.
    *   **Concrete:** The `test_gbridge.py::TornBot` writes directly: `reply.write_text(json.dumps(...))`. A real bot might do the same. If `gbridge`'s `poll` reads this mid-write, it could raise `json.decoder.JSONDecodeError` or `KeyError` *before* the `final` flag, leading to `None` and unnecessary retries, or even `TORN_REPLY` if it reads a valid but *incomplete* JSON that happens to pass initial checks before the hash mismatch.

**MEDIUM Severity**
*(Issues that could cause functional bugs, degraded performance, or user experience problems under common conditions, but are not immediately critical.)*

1.  **File/Symbol:** `gbridge.py`, `GBridgeError`
    *   **Defect:** **Untyped Refusal Kinds:** The `kind` attribute of `GBridgeError` is a `str`, and its possible values are documented in the class docstring. However, this is not enforced by an `Enum` or a `Literal` type hint.
    *   **Impact:** A typo in a `kind` string could lead to incorrect error handling by callers, making it harder to programmatically react to specific error types. It's a common source of bugs in dynamically typed languages.
    *   **Spec Delivery:** Partially adheres. The spec states "typed refusal," which implies programmatic distinguishability. While the class is typed, the `kind` field itself is a loose string.
    *   **Concrete:** If a developer types `GBridgeError("TIME_OUT", ...)` instead of `GBridgeError("TIMEOUT", ...)`, it would pass type checking but fail comparison for callers expecting `"TIMEOUT"`.

2.  **File/Symbol:** `gbridge.py`, `GBridge.ask`
    *   **Defect:** **Duplicate `_validated` Calls:** The `ask` method calls `self.transport.poll(ask, final=True)` and then immediately `return self._validated(ans, rid)` if `ans` is not `None`. However, `_validated` is *also* called inside the loop for non-final polls.
    *   **Impact:** Redundant validation logic and potential for slight performance overhead. More importantly, it creates a subtle difference in error reporting between inside the loop and after the loop. If an `ans` becomes non-`None` *just* after the loop, it's validated once. If it becomes non-`None` *inside* the loop, it's validated, returned, and then implicitly *not* validated again. This is likely benign, but it's an inconsistent code path.
    *   **Spec Delivery:** Adheres. The functionality is correct. This is a code quality issue.
    *   **Concrete:** The logic `ans = self.transport.poll(ask, final=True); if ans is not None: return self._validated(ans, rid)` is reachable only if `ans` was `None` *during the very last iteration* of the loop, but then became available on the `final=True` poll. `_validated` is correctly applied. The redundancy is minor.

3.  **File/Symbol:** `gbridge.py`, `MailboxTransport.send`
    *   **Defect:** **`_sha256` on `ask.text` vs. `payload["text"]` for read-back:** The `_sha256` function is called on `ask.text` when creating the `payload`, but then the read-back verification uses `back["body_sha256"] != payload["body_sha256"]`. This is fine as `payload["body_sha256"]` would contain the hash of `ask.text`. However, the name `body_sha256` is potentially confusing as it is literally a hash of `ask.text`, not the entire JSON body. A future extension might add other fields to the "body" or introduce different hashing strategies. While technically correct *for now*, it's slightly imprecise.
    *   **Impact:** Minor clarity issue. Could lead to confusion or subtle bugs if the definition of "body" for hashing changes in future wire protocol versions without careful review.
    *   **Spec Delivery:** Adheres. The current implementation works as intended.
    *   **Concrete:** `payload = {"...text": ask.text, "body_sha256": _sha256(ask.text)}`. This means `body_sha256` refers specifically to the hash of the `text` field, not a general hash of the entire "body" of the message (which would typically imply more than one field).

**LOW Severity**
*(Minor issues impacting code style, readability, or very specific edge cases that are unlikely to occur.)*

1.  **File/Symbol:** `gbridge.py`, `_now`
    *   **Defect:** **Local Timezone Offset Calculation Flaw:** The `_now` function calculates `off = -time.timezone + (3600 if local.tm_isdst else 0)`. While this is a common approach for *current* offset, it's not robust across all historical time changes or for future-dated timestamps. `time.timezone` and `time.altzone` are seconds west of UTC, and `time.localtime` can be platform-dependent for `tm_isdst`. A more robust way to get the *current* UTC offset would be to use `datetime.now().astimezone().utcoffset().total_seconds()`.
    *   **Impact:** For the very narrow use case of recording `epoch` and `utc_offset_s` for an immediate request, this is likely sufficient and accurate enough for *current* time. However, it's a known source of subtle bugs in time-sensitive applications. Given this is *logging* the offset, not performing time arithmetic, the impact is minimal.
    *   **Spec Delivery:** Adheres for the practical intent. The current implementation likely yields correct values for "now."
    *   **Concrete:** Consider a system configured with a non-standard `TZ` environment variable, or in a region that changes DST rules. `time.timezone` might not always reflect the full picture.

2.  **File/Symbol:** `test_gbridge.py`, `RESULTS.append`
    *   **Defect:** **Bare `except Exception as e`:** The `check` helper in `test_gbridge.py` uses a bare `except Exception as e`.
    *   **Impact:** While generally discouraged in production code (it can catch SystemExit, KeyboardInterrupt, etc.), in a self-test utility designed to catch *any* failure and report it, this is acceptable and arguably desirable to ensure no test case silently fails due to an unexpected exception type. It's a style guideline rather than a functional bug in this context.
    *   **Spec Delivery:** Not relevant to app spec, but to test code quality. The test suite correctly identifies issues.

3.  **File/Symbol:** `gbridge.py`, `_sha256`
    *   **Defect:** **Encoding Assumption:** The `_sha256` function assumes `utf-8` encoding for `s.encode("utf-8")`. While `utf-8` is a common and good default, the `text` and `context` fields in `Ask` are `str` which can contain any Unicode characters. If a specific different encoding was mandated by an external system or protocol, this would be an implicit assumption.
    *   **Impact:** Extremely low, as `utf-8` is the standard for text data. However, for a wire protocol, being explicit about text encoding is crucial.
    *   **Spec Delivery:** Adheres, as there is no specific encoding mentioned. `utf-8` is a reasonable default.

---
**Summary of Spec Delivery:**

The `gbridge` app for T1 slice 1 **delivers its spec substantially**. The core contract points are met:
*   **Synchronous `ask()` with typed refusals:** Yes, `GBridge.ask` is blocking and raises `GBridgeError` with `kind`s.
*   **Injected Transports:** Yes, the `GBridge` class takes a `Transport` instance.
*   **MailboxTransport as primary, XaiApiTransport as fallback (refusing):** Yes, this is correctly implemented.
*   **Python 3.14 stdlib only, no third-party deps:** Verified, only standard library modules are imported.
*   **Wire shape versioned, validation fail-closed, TORN_REPLY/TIMEOUT:** Yes, `WIRE_VERSION` is checked, hash validation is in place, and `TORN_REPLY`/`TIMEOUT` are correctly raised. Request files are left for collectibility.
*   **Root handed in, no path resolution by module:** Yes, `mail_root` is passed to `MailboxTransport`.
*   **Missing endpoint is THE PHONE IS DEAD:** Yes, `ROOT_MISSING` is raised if `to_dir` or `from_dir` are not found.

The defects identified are primarily about edge cases, robustness of external interactions (the bot's write behavior), consistency, or minor clarity/implementation details. None invalidate the core functionality or the design principles outlined in the spec for this slice. The `MailboxTransport.poll` race condition is the most significant, as it impacts the robustness of the primary transport's reply reception.