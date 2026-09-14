// One fixture pin: session.list against a stand-in Core.
//
//     node --experimental-strip-types builds/session-plugin/test/test_tool_session_list.ts

import { fakeCore, fileEnv, run } from "./_harness.ts";

const { server, url } = await fakeCore();
try {
  const list = await run("session.list", {}, { ...fileEnv, COSMOS_CORE_URL: url });
  const ok =
    list.ok &&
    list.kind === "OK" &&
    (list.gate.rows as unknown[]).length === 2 &&
    list.legal_omitted === 1;
  console.log(ok ? "PASS session.list fixture" : "FAIL session.list fixture");
  console.log(ok ? "1/1" : "0/1");
  process.exitCode = ok ? 0 : 1;
} finally {
  server.close();
}
