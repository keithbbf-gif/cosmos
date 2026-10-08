# Hermes improvements

Base: `V:\A\Ai\COSMOS` main `501fdee2`. Package `hermes\` already passes 4C.
These are reviewable diffs. They are not applied. Credential-pool install
stays TABLED. Nothing here reads a key file, opens a socket, or starts a pool.

The 69 proposal modules were sampled (`credential_pools`, `agent_loop`,
`code_execution`, `workspace_guard`, `plugins`, `hooks`, `api_server`,
`tool_gateway`). They already fail closed, cap the caller, and compare with
`const_eq`. No third change. A style pass would only add code.

## 1. `hermes/cosmos_hermes/redact.py` — pasted xAI key is not a secret

`secret_shape` refuses `sk-`, `Bearer`, and `api_key=` assignments.
Federation and voice also refuse an `xai-` token of eight or more characters.
This kernel does not. `CredentialPool.add` stores any id that passes
`secret_shape`, so a pasted xAI key becomes a credential id. `xai-main`,
the short id already used in tests, stays an id: the suffix is under eight
characters. This is a pure function. It does not install a pool.

```diff
--- a/hermes/cosmos_hermes/redact.py
+++ b/hermes/cosmos_hermes/redact.py
@@ -11,6 +11,7 @@ _BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{8,}")
 _ASSIGN = re.compile(
     r"(?i)\b(api_key|apikey|token|secret|password|authorization)\b\s*[:=]\s*\S+"
 )
+_XAI = re.compile(r"(?i)(?<![A-Za-z0-9])xai-[A-Za-z0-9_\-]{8,}")
 
 
 def secret_shape(text: str) -> bool:
     """True when `text` carries a key-shaped substring."""
     if not isinstance(text, str):
         return False
-    return bool(_SK.search(text) or _BEARER.search(text) or _ASSIGN.search(text))
+    return bool(
+        _SK.search(text) or _BEARER.search(text) or _ASSIGN.search(text) or _XAI.search(text)
+    )
 
 
 def redact(text: str) -> str:
     """Replace key-shaped substrings. The input is otherwise unchanged."""
     if not isinstance(text, str):
         return ""
     out = _ASSIGN.sub("[redacted-assignment]", text)
     out = _BEARER.sub("[redacted-bearer]", out)
     out = _SK.sub("[redacted-key]", out)
+    out = _XAI.sub("[redacted-key]", out)
     return out
```

`hermes/tests/test_kernel.py` should assert `secret_shape("xai-" + "a" * 8)`
and `not secret_shape("xai-main")`, and that redact removes the long form.
No other call site changes.

## 2. `hermes/cosmos_hermes/jail.py` — `NUL` and `CON` sit inside the grant

`_shape` refuses `..`, a colon stream, and a trailing dot. It does not
refuse a Windows device name. `contain` then returns `grant\NUL` or
`grant\nul.txt`. `open` on that path writes the NUL device, not a file
inside the grant. The same is true for `CON`, `PRN`, `AUX`, `COM1`–`COM9`,
and `LPT1`–`LPT9`. Refuse the stem before `Path.resolve` so the device is
never opened.

```diff
--- a/hermes/cosmos_hermes/jail.py
+++ b/hermes/cosmos_hermes/jail.py
@@ -19,6 +19,18 @@ _DRIVE_RELATIVE = re.compile(r"^[A-Za-z]:([^/\\]|$)")
 _DRIVE_ROOT = re.compile(r"^[A-Za-z]:[/\\]?$")
 _FILE_URL = re.compile(r"^file:", re.IGNORECASE)
 _DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
+_DEVICES = frozenset(
+    {
+        "con",
+        "prn",
+        "aux",
+        "nul",
+        *(f"com{n}" for n in range(1, 10)),
+        *(f"lpt{n}" for n in range(1, 10)),
+    }
+)
+
+
+def _device(raw: str) -> bool:
+    for part in re.split(r"[/\\]", raw):
+        if part in ("", ".", ".."):
+            continue
+        stem = part.split(".", 1)[0].split(":")[0].rstrip(" .").lower()
+        if stem in _DEVICES:
+            return True
+    return False
 
 
 def _shape(raw: str) -> None:
@@ -47,6 +59,8 @@ def _shape(raw: str) -> None:
             continue
         if part.endswith(".") or part.endswith(" "):
             raise Refuse("TRAILING_DOT")
+    if _device(raw):
+        raise Refuse("DEVICE_PATH")
```

Add `str(grant / "NUL")` to the escape list in `hermes/tests/test_kernel.py`
and expect `DEVICE_PATH`. Colon streams stay `ALT_STREAM`.
