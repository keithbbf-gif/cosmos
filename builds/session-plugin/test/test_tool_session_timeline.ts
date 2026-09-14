// One fixture pin: session.timeline against rolled-event fixtures.
//
//     node --experimental-strip-types builds/session-plugin/test/test_tool_session_timeline.ts

import { fileEnv, run } from "./_harness.ts";

const tl = await run("session.timeline", { id: "cow-abc" }, fileEnv);
const ok =
  tl.ok &&
  tl.gate.n_events === 2 &&
  (tl.gate.entries as Array<{ seq: number }>).map((e) => e.seq).join(",") === "1,2";

console.log(ok ? "PASS session.timeline fixture" : "FAIL session.timeline fixture");
console.log(ok ? "1/1" : "0/1");
process.exitCode = ok ? 0 : 1;
