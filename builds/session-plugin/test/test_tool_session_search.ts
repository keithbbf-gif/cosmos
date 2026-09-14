// One fixture pin: session.search against transcript fixtures.
//
//     node --experimental-strip-types builds/session-plugin/test/test_tool_session_search.ts

import { fileEnv, run } from "./_harness.ts";

const hit = await run("session.search", { query: "plumbing" }, fileEnv);
const ok =
  hit.ok &&
  hit.gate.n_hits === 1 &&
  (hit.gate.hits as Array<{ id: string; excerpt: string }>)[0].id === "cow-abc" &&
  (hit.gate.hits as Array<{ excerpt: string }>)[0].excerpt.includes("hello from plumbing");

console.log(ok ? "PASS session.search fixture" : "FAIL session.search fixture");
console.log(ok ? "1/1" : "0/1");
process.exitCode = ok ? 0 : 1;
