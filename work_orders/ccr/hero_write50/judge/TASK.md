Reply with exactly these ids, one per line: ID SEAT
SEAT is one of: glm, muse, or NONE.
Pick the retelling that adds nothing.

S-63 SOURCE: CoP was written off on a premise that expired — five days of a dead lane, and the "do not re-test" note was the thing keeping it dead
LESSON: 1. 🔴 A "DO NOT RE-TEST IT" NOTE INHERITS THE LIFESPAN OF THE FACT UNDERNEATH IT. BU.MD said
glm: I watched a CoP get written off against a premise that had already expired. Five days of a dead lane, and the thing holding it closed was a 'do not re-test' note nobody re-evaluated. I now treat every such note as inheriting the lifespan of the fact underneath it: when the underlying premise expires, the note expires with it, and I must check that link before trusting it.
muse: I learned that I wrote off CoP on a premise that later expired, and I left that lane dead for five days because my own do not re-test note kept it dead. I now see such a note inherits the lifespan of the fact underneath it, so I must re-check the premise before I let an old warning block me.

S-64 SOURCE: A launcher that prints "LAUNCHED" is not evidence anything launched — FANOUT_UI.bat v1: neither node ran
LESSON: 2. 🔴 A LAUNCHER THAT PRINTS "LAUNCHED" IS NOT EVIDENCE ANYTHING LAUNCHED. FANOUT_UI.bat v1
glm: I trusted a launcher's output once and got burned: FANOUT_UI.bat v1 printed its success word while neither node actually ran. I no longer treat a launcher that prints 'LAUNCHED' as evidence anything launched. Exit text is a claim, not a result. Now I verify the launched processes independently before I believe any summary the launcher itself produces about its own success.
muse: I learned that a launcher printing LAUNCHED proves nothing about whether anything actually launched, because I saw a first version where neither node ran despite the message. I now verify real process startup separately, and I treat console success text as decoration until I have confirmed independent evidence that work began.

S-65 SOURCE: setx PATH "%PATH%;…" is destructive — it truncates at 1024 chars, silently
LESSON: 3. 🔴 setx PATH "%PATH%;…" IS DESTRUCTIVE — never use it. It truncates at 1024 chars
glm: I learned the hard way that setx PATH '%PATH%;â¦' is destructive. It truncates at 1024 characters, silently, and takes the rest of the path with it. I never use it now. Any PATH change I make is done through a mechanism that preserves the full existing value, and I verify the resulting length before I let the change stand anywhere on a machine.
muse: I learned that using setx to append to PATH is destructive and I will never use it, because I saw it silently truncates the value at 1024 characters. I now treat that quiet truncation as data loss, so I avoid that command entirely and I look for a safe method that preserves the full existing value.

S-66 SOURCE: hv_judged was added to to_json and not to from_json — written to disk, quietly dropped on read
LESSON: 5. 🔴 ADDING ONE FIELD TOUCHES FOUR SERIALISATION POINTS, AND MISSING ONE IS SILENT.
glm: I added hv_judged to to_json and forgot from_json, so the field was faithfully written to disk and quietly dropped on every read. That taught me adding one field touches four serialisation points, and missing one is silent. Now I enumerate every write and read site for a schema before touching it, and I round-trip a record through disk to prove the field survives.
muse: I learned that I added hv_judged to to_json but not to from_json, so I wrote it to disk and then quietly dropped it on read. I now remember that adding one field touches four serialisation points, and missing one fails silently. I check every paired write and read path together before I consider the field done.

S-67 SOURCE: The RULING_COLUMNS append-only invariant was written wrong TWICE — both versions forbade the very thing append-only means
LESSON: 6. ⚠ DO NOT OVER-SPECIFY AN APPEND-ONLY INVARIANT. The RULING_COLUMNS guard was written
glm: I wrote the RULING_COLUMNS append-only invariant wrong twice, and both versions forbade the very thing append-only is supposed to allow. I over-specified the guard, turning it into a no-change rule instead of an additions-only rule. Now I keep append-only invariants minimal: state exactly what is permitted, name the allowed operation, and resist the urge to enumerate extra restrictions.
muse: I learned that I wrote my append-only invariant for RULING_COLUMNS wrong twice, and both versions forbade the very thing append-only means. I now avoid over-specifying that guard, so I keep the rule minimal and literal. I test that legitimate appends pass before I trust my own wording again.

S-68 SOURCE: GEM reported its prototype "compiles and runs flawlessly (Exit Code: 0)" having executed only py_compile
LESSON: 7. ⚠ A PARSE CHECK IS NOT A RUN — including when a NODE claims otherwise. GEM reported its
glm: GEM reported its prototype 'compiles and runs flawlessly (Exit Code: 0)' when the only thing executed was py_compile. A parse check is not a run, and I no longer accept a node's claim otherwise. Exit code zero from a compiler means syntax only. Before I believe anything about behaviour, I require evidence of actual execution with output inspected, not a compile badge.
muse: I learned that a prototype was reported as compiling and running flawlessly with Exit Code zero when only py_compile had executed. I now treat a parse check as never equivalent to a run, even when another node claims otherwise. I require actual execution evidence before I accept that anything ran flawlessly.

S-69 SOURCE: Bare python on this box is 3.13 with no pytest — and _pyver_probe.log had already recorded it on 07-27
LESSON: - (Also recorded, environment-specific:) bare python on this box is 3.13 and has no
glm: I rediscovered something my own logs already knew: bare python on this box is 3.13 with no pytest available, and _pyver_probe.log had already recorded exactly that on 07-27. I re-derived an environment fact from scratch because I did not consult the record first. Now I check prior probe logs before assuming anything about interpreter versions or installed packages.
muse: I learned that bare python on this box is version 3.13 with no pytest available, and I had already recorded that fact on July 27. I now check my earlier environment notes before assuming tooling exists. I verify the interpreter version and test runner first so I do not waste time on a missing setup.

S-70 SOURCE: 55 LF-only line endings and 12 non-ASCII bytes in this project's .bat files produced measured mojibake
LESSON: 1. RUN_TESTS.bat failed tests\test_launchers.py — 55 LF-only line endings and 12
glm: I ran RUN_TESTS.bat and it failed tests\test_launchers.py because of 55 LF-only line endings and 12 non-ASCII bytes in this project's .bat files, producing measured mojibake. Encoding defects in batch files are real test failures, not cosmetic noise. Now I audit line endings and byte content of .bat files directly, and I treat any non-ASCII byte in them as a bug to fix immediately.
muse: I learned that fifty-five LF-only line endings and twelve non-ASCII bytes in this project's batch files produced measured mojibake for me. I now take line endings and encoding seriously because small invisible differences break execution. I normalize and verify those bytes before I assume my scripts will run cleanly.

S-71 SOURCE: srdata.nist.gov returns HTTP 200 for EVERY path including nonsense — the 401-vs-404 endpoint test is useless against it
LESSON: And srdata.nist.gov returns HTTP 200 for EVERY path including
glm: I designed an endpoint test against srdata.nist.gov and then found it returns HTTP 200 for every path, including complete nonsense. The 401-versus-404 distinction I was probing simply does not exist there, so the test is useless against it. Before I build any probe on status codes, I first send a deliberately invalid request and confirm the server actually discriminates.
muse: I learned that srdata.nist.gov returns HTTP 200 for every path including nonsense, so my 401-versus-404 endpoint test is useless against it. I now avoid relying on status codes alone for that host. I design a content-based check instead, because I need positive evidence that I reached a real intended resource.

S-72 SOURCE: A session ran four streams in one context and degraded badly by the end
LESSON: A session that touches rails, physics, tooling and prompt-discipline in one context degrades
glm: (missing)
muse: I learned that running four streams in one context degraded badly by the end, when I touched rails, physics, tooling, and prompt-discipline together. I now keep sessions narrowly scoped instead of mixing unrelated work. I split complex efforts early, because I focus better and I avoid the slowdown that overloaded context creates.
