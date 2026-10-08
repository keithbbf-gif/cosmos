# Duplex voice improvements

Base: `V:\A\Ai\COSMOS` main `501fdee2`. Package `voice_duplex\` already
passes 4C. These are reviewable diffs. They are not applied. Voice refine
stays TABLED. No WebSocket, no second ledger, no spend file.

`CeilingSpend` stays a caller-supplied ceiling. It does not grow a meter.

## 1. `voice_duplex/cosmos_voice_duplex/confirm.py` — punctuation hides the verb

`first_word` is `parts[0].lower()`. `cosmos_voice` strips
`string.punctuation` before the same compare. Here `delete,` is not in
`DESTRUCTIVE`, and `submit,` is not in `CONSEQUENTIAL`, so the line is
`pass` and the host can run it. The accept set is unchanged: `do it` and
`go ahead` stay whole-utterance matches, and `yes,` stays a cancel.
Widening `YES` to a first-word `yes` would confirm `yes please ...` and
is not part of this diff.

```diff
--- a/voice_duplex/cosmos_voice_duplex/confirm.py
+++ b/voice_duplex/cosmos_voice_duplex/confirm.py
@@ -12,6 +12,7 @@ plus the confirm id, which is what ``VoiceMode.handle`` binds the nonce to.
 
 from __future__ import annotations
 
+import string
 from dataclasses import dataclass
 from typing import Protocol
@@ -72,8 +73,10 @@ class GateResult:
 
 
 def first_word(text: str) -> str:
     parts = text.split()
-    return parts[0].lower() if parts else ""
+    if not parts:
+        return ""
+    return parts[0].strip(string.punctuation).lower()
```

`delete,` and `submit,` then take the same branch as `delete` and
`submit`. Existing tests use unpunctuated words.

## 2. `voice_duplex/cosmos_voice_duplex/session.py` — cancel still calls the host

`on_user` is the accepted-turn callback. `pass` calls it. `cancel` calls
it too, with the line that failed the yes-set. A pending `submit` followed
by `ok submit it` is a cancel (first word is not `submit`), and the host
still receives `ok submit it`. Captions already stored the line. `refuse`
does not call `on_user`. Cancel should match refuse.

```diff
--- a/voice_duplex/cosmos_voice_duplex/session.py
+++ b/voice_duplex/cosmos_voice_duplex/session.py
@@ -220,10 +220,8 @@ class DuplexSession:
             self._apply(self.rail.force_say(result.spoken))
             return
         if result.action == "cancel":
             self._apply(self.rail.force_say(result.spoken or "Cancelled."))
-            if result.transcript and self.on_user is not None:
-                self.on_user(result.transcript)
             return
         if result.action == "confirm" and result.tool_name:
             output = self.tools.call(result.tool_name, result.tool_args, confirmed=True)
```

The `confirmed=True` argument belongs to the next diff. Apply them together.

## 3. `voice_duplex/cosmos_voice_duplex/tools.py` — `confirm=True` is a comment

`ToolRegistry.call` runs the handler for every known name. `propose` is
`confirm=True`, and only `DuplexSession._on_tool` remembers to hold it.
Any other caller, including the plugin host, runs the handler with no
spoken yes. `status` and `check` are `confirm=False`, so
`tests/test_plugin.py` keeps working. The session's confirm arm is the
only caller that may pass `confirmed=True`.

```diff
--- a/voice_duplex/cosmos_voice_duplex/tools.py
+++ b/voice_duplex/cosmos_voice_duplex/tools.py
@@ -41,8 +41,10 @@ class ToolRegistry:
     def schemas(self) -> list[dict[str, object]]:
         return [*self.server_tools, *[tool.schema() for tool in self.tools.values()]]
 
-    def call(self, name: str, arguments: str) -> str:
+    def call(self, name: str, arguments: str, *, confirmed: bool = False) -> str:
         tool = self.tools.get(name)
         if tool is None:
             return json.dumps({"ok": False, "error": f"unknown tool {name}"})
+        if tool.confirm and not confirmed:
+            return json.dumps({"ok": False, "error": "confirm required"})
         try:
             payload = json.loads(arguments) if arguments else {}
```

The unconfirmed tool arm in `session.py` (`self.tools.call(ev.name, ev.arguments)`)
stays positional. It only runs when `tool.confirm` is false, so the new
guard does not change it.
