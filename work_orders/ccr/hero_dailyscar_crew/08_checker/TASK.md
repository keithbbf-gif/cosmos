First line is ten picks, one per line, form: S-0N WINNER one short reason.
WINNER is GLM or DS. Pick the note that stays with the scar and does not add a fact.

Item 01
GLM: On 2026-07-05 the Chrome bridge denied my requests three times, and I almost read it as refusal. It was not refusal; the operator was simply away. Now I note the denial, queue the bridge work, and move on instead of retry-spamming the same call over and over while nobody is at the keyboard to approve anything.
DS: I logged three Chrome-bridge denials on 2026-07-05. They were not the operator refusing: the operator was simply away. When the operator is away and a request is denied, I should note it and queue the bridge work instead of retry-spamming. Three denials meant the operator was away, not refusing.

Item 02
GLM: On 2026-07-06 I lost the ROLD commands file to disk truncation and had to reconstruct it from Doping-session context, guided by the .bak_2026-07-06- files left behind. What I have now is the canonical current version. After every edit I run wc -c and do a tail check, because I never want to lose that file silently again.
DS: The ROLD commands file was lost to disk truncation and I had to reconstruct it from Doping-session context. It is the canonical current version now. After every edit of this file I follow the integrity rule: run wc -c and a tail-check to confirm the file is intact. The .bak_2026-07-06 files hold the backup.

Item 03
GLM: On 2026-07-06 a mixed permission dialog confused me, and the wrong scope got answered instead of the primary per-site ask. The good news is that a mis-click deny is recoverable in the same session by re-granting. Now I pause and make sure the primary ask is the one I respond to, not some broader-scope option.
DS: On 2026-07-06 I learned a lesson about mixed permission dialogs. The operator must answer the PRIMARY per-site ask, not a broader-scope option inside a mixed dialog. A mis-click deny is recoverable in the same session by re-granting. I now read the dialog scope carefully before answering.

Item 04
GLM: During the 2026-07-10/11 mesh and dashboard session with GDX, I told the operator I could write, and my Drive write silently failed on stale connector auth. I had to walk back my earlier yes. The operator re-authed, the round-trip proved out, and the lesson stuck: never trust an agent's self-report about a working write.
DS: On 2026-07-10 and 11, during the mesh dashboard and GDX session, a GDX write silently failed on stale connector auth. The node claimed it could write, but my Drive write failed. The operator re-authenticated and fixed it, and the round-trip proved out. Lesson: do not trust an agent's self-report.

Item 05
GLM: On 2026-07-12 I hit a mount problem with jack_command.html. It was served pinned at a truncated 63,824 bytes while the host copy ran 1,146 lines, so what I read through the mount was not what sat on disk. I learned that day to compare what the mount serves against the host before I trust any file I read through it.
DS: On 2026-07-12 I hit a truncation issue: jack_command.html was served pinned at a truncated 63,824 bytes. The host file had 1,146 lines. I noticed the served file did not match the source size, a known truncation class I need to watch for when working through the mount.

Item 06
GLM: That same 2026-07-12 mount also corrupted bts_gdx.py at the character level: a single colon was missing on read, which produced a completely false SyntaxError. The file was fine on disk; the mount was the liar. I stopped blaming the code and started verifying reads through the mount before accepting any parse failure at face value.
DS: On 2026-07-12 I saw character-level corruption: bts_gdx.py read back through the mount was missing a colon, which produced a FALSE SyntaxError. The file was fine on disk. I learned to verify the read-back against the on-disk truth rather than trusting the apparent parse error.

Item 07
GLM: The same 2026-07-12 corruption class hit my JSON reads too. dash.json gave me a bogus Unterminated string error at line 255, a line I knew was valid on disk. Between the truncated HTML and the missing colon, I concluded the mount itself was unreliable, and that decoding errors through it need disk-level confirmation.
DS: The same corruption hit dash.json on 2026-07-12: a bogus Unterminated string error at line 255, a line that is perfectly valid on disk. sgh_spend.json also gave bogus JSON decode errors. I now disregard JSON decode errors on read-through unless the on-disk file confirms a real problem.

Item 08
GLM: I have seen what silent truncation costs. On 2026-07-12, 26 of Chapter 4's 36 references were eaten, and the list simply ended at the letter G with no error raised. Nothing complained, so nothing looked wrong until I counted. Since then I count list lengths against expectations rather than trusting that a read returning cleanly is complete.
DS: This is the same failure class that silently ate 26 of Chapter 4's 36 references. The list truncated at the letter G, so a large portion vanished without warning. I treat silent truncation of long lists as a recurring danger and check lengths before relying on any reference list that came through the mount.

Item 09
GLM: On 2026-07-12 the BootUP took only V:\Research4 and then stalled twice mid-session: once for the Desktop to fix the launcher, once for GDX. That is exactly the stall the up-front mount step exists to prevent. Now I ask for the whole set of mounts in one block before any work starts, so the session never pauses halfway.
DS: On 2026-07-12 the BootUP took only one mount, the research drive, and then had to stop twice mid-session: once for the Desktop to fix the launcher, and once for GDX. That is exactly the stall this step exists to prevent. I ask for the whole set in one up-front block before any work starts.

Item 10
GLM: The 2026-07-12 root cause I never want to regress: the Desktop launcher was starting python -m http.server 8765, the plain static server. It served the page, but it had no /api routes, so <TEST> could not run the python probe, since a browser cannot execute python. Every panel silently went stale while looking perfectly alive.
DS: The 2026-07-12 root cause: the Desktop launcher started python -m http.server 8765, the plain static server. It serves the page but has no /api routes, so my probe could not run the python check because a browser cannot execute python. I must not regress this; the launcher has to start the real server.
