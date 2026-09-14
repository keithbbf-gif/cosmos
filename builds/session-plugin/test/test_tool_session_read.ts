// One fixture pin: session.read against transcript fixtures.
//
//     node --experimental-strip-types builds/session-plugin/test/test_tool_session_read.ts

import { readVerified } from "../src/transcript.ts";
import { fileEnv, run, TRANSCRIPTS } from "./_harness.ts";

const read = await run("session.read", { id: "cow-abc" }, fileEnv);
const ok =
  read.ok &&
  (read.gate.head as { schema: string }).schema === "cosmos-transcript/1" &&
  read.gate.sha === readVerified(TRANSCRIPTS, "cow-abc").sha;

console.log(ok ? "PASS session.read fixture" : "FAIL session.read fixture");
console.log(ok ? "1/1" : "0/1");
process.exitCode = ok ? 0 : 1;
