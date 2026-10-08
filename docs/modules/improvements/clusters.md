# Clusters improvements

Base: `V:\A\Ai\COSMOS` main `501fdee2`. Package `clusters\` passes under
`grade.py` mypy flags. These are reviewable diffs. They are not applied.
The strict-mypy backlog (hundreds of errors) is not a fix. No second ledger.

`spend.py` stays a projection of caller-stamped observations.

## 1. `clusters/clusters/policy.py` — a routine prefix allows the rest of the line

`ROUTINE` includes `git status`, `pytest`, `dir`, and `ls`. `_listed`
allows the command when it equals the phrase or starts with
`phrase + " "`. Hard refusals run first, but they only match a fixed
needle list. `git status && <anything else>` does not contain `rm -rf`
or `git push`, so the prefix matches and the decision is `OK`. Turbo is
already ignored. A chained line is not a routine command. Send it to
`APPROVAL` after the hard checks, so a destructive chain is still
`DESTRUCTIVE` and an extra deny such as `curl` still wins.

```diff
--- a/clusters/clusters/policy.py
+++ b/clusters/clusters/policy.py
@@ -9,6 +9,16 @@ from clusters.models import ROUTINE
 from clusters.refuse import Refuse, forbidden_flag, is_destructive, is_protected_push
 from clusters.store import Store
 
 
+_CHAIN_MARKS = ("&&", "||", ";", "|", "&", "`", "$(")
+
+
+def _chained(command: str) -> bool:
+    """True when a shell would run more than the allowlisted prefix."""
+    return any(mark in command for mark in _CHAIN_MARKS)
+
+
 def check_command(
     store: Store,
@@ -33,6 +43,8 @@ def check_command(
     denied = _denied(text, extra_deny)
     if denied:
         return _decision("refuse", "DENY", denied)
+    if _chained(text):
+        return _decision("needs_approval", "APPROVAL", "shell chain")
     if _listed(text, [*ROUTINE, *extra_allow]):
         return _decision("allow", "OK", "")
     # Turbo allowlist and hard refusals: turbo does not widen this; code is APPROVAL. Records no claim.
```

`py -3.14 -m pytest` and the other `ROUTINE` rows contain none of the marks.

## 2. `clusters/clusters/refuse.py` — protected push only sees the literal tokens

`is_protected_push` requires the substring `git push` and then an exact
token `main`, `master`, `origin/main`, or `origin/master`. Both of these
fall through to `APPROVAL` instead of `PROTECTED`:

- `git -C <repo> push origin main` has no `git push` substring.
- `git push origin HEAD:main` and `git push origin refs/heads/main` do
  not contain the token `main`.

A commit message that merely contains those words must stay approval,
not a false protected push. Look at the arguments of the `push`
subcommand only.

```diff
--- a/clusters/clusters/refuse.py
+++ b/clusters/clusters/refuse.py
@@ -79,17 +79,42 @@ def is_destructive(command: str) -> bool:
     return any(item in text for item in needles)
 
 
+def _push_args(tokens: list[str]) -> list[str] | None:
+    """Arguments of a git push subcommand, or None when this is not one."""
+    if "git" not in tokens:
+        return None
+    index = tokens.index("git") + 1
+    while index < len(tokens):
+        token = tokens[index]
+        if token == "push":
+            return tokens[index + 1 :]
+        if token in {"-c", "-C"} and index + 1 < len(tokens):
+            index += 2
+            continue
+        if token.startswith("-"):
+            index += 1
+            continue
+        return None
+    return None
+
+
 def is_protected_push(command: str, branch: str = "") -> bool:
     text = " ".join(command.lower().split())
     named = branch.strip().lower()
-    if named in PROTECTED_BRANCHES and "push" in text:
+    tokens = text.split()
+    if named in PROTECTED_BRANCHES and "push" in tokens:
         return True
-    if "git push" not in text and not text.startswith("git push"):
-        return False
-    for item in PROTECTED_BRANCHES:
-        if item in text.split():
+    args = _push_args(tokens)
+    if args is None:
+        return False
+    for token in args:
+        if token.startswith("-"):
+            continue
+        dest = token.rsplit(":", 1)[-1]
+        if dest.startswith("+"):
+            dest = dest[1:]
+        if dest in PROTECTED_BRANCHES:
             return True
+        bare = dest.rsplit("/", 1)[-1]
+        if bare in {"main", "master"} and (dest == bare or "/heads/" in dest):
+            return True
     return False
```

`test_protected_push_refuses` still passes: `git push origin main` and
`git push` with `branch="main"` are unchanged. `git commit -m ...` does
not become `PROTECTED`.

## 3. `clusters/clusters/refuse.py` and `policy.py` — `live/ledger` is not the live root

`guard_path` refuses a path that ends with `/live` or contains
`/cosmos/live`. `Store` then `mkdir`s whatever got through. `live` and
`live/ledger` do neither, so a relative root named `live` is created.
`_live_hit` has the same gap: `type live\state` is not `LIVE_TREE`.
The architecture line is that this package does not write `live/`.
A path segment whose name is `live` is that tree, including its children.
The word `live` with no slash stays allowed (`git log --grep live`).

```diff
--- a/clusters/clusters/refuse.py
+++ b/clusters/clusters/refuse.py
@@ -44,9 +44,14 @@ def guard_path(text: str) -> str:
         raise Refuse("PATH", "rejected")
     parts = Path(text).parts
     if ".." in parts:
         raise Refuse("PATH", "rejected")
     folded = text.replace("\\", "/").rstrip("/").lower()
-    if folded.endswith(("/live", ":live")) or "/cosmos/live" in folded:
+    segments = [part for part in folded.split("/") if part not in ("", ".")]
+    if folded.endswith(":live") or any(
+        part == "live" or part.endswith(":live") for part in segments
+    ):
         raise Refuse("LIVE_TREE", text)
     return text
```

```diff
--- a/clusters/clusters/policy.py
+++ b/clusters/clusters/policy.py
@@ -114,14 +114,16 @@ def _listed(command: str, phrases: list[str]) -> bool:
 def _live_hit(command: str) -> str:
     lowered = command.lower()
     if "cosmos/live" in lowered:
         return "cosmos/live"
     if "cosmos\\live" in lowered:
         return "cosmos\\live"
     for token in command.split():
         if "/" not in token and "\\" not in token:
             continue
         folded = token.replace("\\", "/").rstrip("/").lower()
-        if folded.lower().endswith("/live"):
+        parts = [part for part in folded.split("/") if part not in ("", ".")]
+        if any(part == "live" for part in parts):
             return token
     return ""
```

`folded` is already lowercased, so the old `.lower()` on it was redundant.
Existing live-path tests name `...\live` or `cosmos/live` and still refuse.
