// One fixture pin: session.open against a stand-in Core.
//
//     node --experimental-strip-types builds/session-plugin/test/test_tool_session_open.ts

import { fakeCore, fileEnv, run } from "./_harness.ts";

const { server, url } = await fakeCore();
try {
  const open = await run("session.open", { id: "cow-abc" }, { ...fileEnv, COSMOS_CORE_URL: url });
  const ok =
    open.ok &&
    String(open.gate.text).includes("hello from plumbing") &&
    open.gate.opencode_id === "ses_cow_001";
  console.log(ok ? "PASS session.open fixture" : "FAIL session.open fixture");
  console.log(ok ? "1/1" : "0/1");
  process.exitCode = ok ? 0 : 1;
} finally {
  server.close();
}
