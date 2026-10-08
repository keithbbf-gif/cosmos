# Federation improvements

Base: `V:\A\Ai\COSMOS` main `501fdee2`. Package `federation\` already passes
its package 4C. These are reviewable diffs. They are not applied.

`rehearse.py` is not touched. The unused type ignore stays for the other
agent. `docs/CREDENTIALS_NEEDED.md` stays DENY: `shipset` pins that
over-wide prefix as a measured gap, and narrowing it is a classifier edit,
not this pass.

## 1. `federation/proposals/secrets/secrets.py` — `write_files` will store a vendor key

`mint` refuses a bearer that matches `secret_shape`. `write_files` is a
second entry and does not. A caller can pass an `sk-` or `xai-` string and
the writer stores it as `config/api_token.txt`. `rehearse` only passes a
minted bearer, so the story does not change. `secret_shape` is already
imported.

```diff
--- a/federation/proposals/secrets/secrets.py
+++ b/federation/proposals/secrets/secrets.py
@@ -142,6 +142,8 @@ def write_files(jail: PathJail, token: str, key: bytes) -> None:
         raise Refuse("BLANK_TOKEN", "empty token is an open door")
     cleaned = bound_text(token, limit=_TOKEN_LIMIT, name="token").strip()
+    if secret_shape(cleaned):
+        raise Refuse("SECRET_SHAPE", "bearer looked like vendor key material")
     if not isinstance(key, bytes) or len(key) != _KEY_BYTES:
         raise Refuse("BAD_KEY", "install key must be 32 bytes")
```

## 2. `federation/cosmos_federation/jail.py` — device names and streams resolve inside the root

`contain` rejects `..`, a drive, and a URL, then `resolve`s. On Windows,
`NUL`, `CON`, `PRN`, `AUX`, `COM1`–`COM9`, `LPT1`–`LPT9`, and the same
names with an extension open a device, not a file under the jail. A colon
in a part is an alternate data stream of a file that is still under the
root. `config/api_token.txt` has neither, so `write_files` and `rehearse`
stay on the same paths. Refuse before `resolve`.

```diff
--- a/federation/cosmos_federation/jail.py
+++ b/federation/cosmos_federation/jail.py
@@ -6,6 +6,22 @@ from pathlib import Path
 
 from cosmos_federation.errors import Refuse
 
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
+def _blocked(part: str) -> bool:
+    if ":" in part:
+        return True
+    stem = part.split(".", 1)[0].rstrip(" .").lower()
+    return stem in _DEVICES
+
 
 class PathJail:
@@ -36,6 +52,8 @@ class PathJail:
         parts = [part for part in norm.split("/") if part not in ("", ".")]
         if not parts or any(part == ".." for part in parts):
             raise Refuse("PATH", "dotdot")
+        if any(_blocked(part) for part in parts):
+            raise Refuse("PATH", "device or stream")
         out = self._root.joinpath(*parts).resolve()
```

## 3. `federation/proposals/chatwindow/chatwindow.py` — a short nonce returns before the compare

`redeem` says a wrong presentation is always `NONCE`, so length is not a
separate code. The condition still returns on length before `const_eq`.
A presentation of the wrong size is a faster reject than a wrong code of
the right size. Compare the stored code either way. Do not hash a
caller string whose length already failed. Remote is still refused first.

```diff
--- a/federation/proposals/chatwindow/chatwindow.py
+++ b/federation/proposals/chatwindow/chatwindow.py
@@ -128,12 +128,13 @@ def redeem(nonce: Nonce, presented: str, now: int, remote: bool) -> Cookie:
     if not isinstance(remote, bool) or remote:
         raise Refuse("REMOTE", "loopback only")
     if not isinstance(nonce, Nonce):
         raise Refuse("NONCE", "mismatch")
-    if (
-        not isinstance(presented, str)
-        or len(presented) != _NONCE_BYTES * 2
-        or not const_eq(nonce.code, presented)
-    ):
+    if not isinstance(presented, str):
+        raise Refuse("NONCE", "mismatch")
+    same = len(presented) == len(nonce.code)
+    # Wrong length still runs a compare, against the stored code only.
+    if not const_eq(nonce.code, presented if same else nonce.code) or not same:
         raise Refuse("NONCE", "mismatch")
     if nonce._use.spent:
         raise Refuse("NONCE_USED", "replay")
```

The refusal code does not change. Existing mismatch tests stay valid.
