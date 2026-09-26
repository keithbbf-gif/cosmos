import { mcpListTools, runTool } from "../src/tools.ts";
import type { FetchLike } from "../src/core.ts";

function mockFetch(status: number, body: unknown): FetchLike {
  return async () => ({
    status,
    json: async () => body,
  });
}

const env = { COSMOS_CORE_URL: "http://127.0.0.1:8770" };

let failed = 0;
function check(label: string, ok: boolean) {
  console.log(ok ? "PASS" : "FAIL", label);
  if (!ok) failed += 1;
}

const listed = mcpListTools();
check("lists xtalk_get / xtalk_send / xtalk_roles",
  listed.map((t) => t.name).join(",") === "xtalk_get,xtalk_send,xtalk_roles");

const get = await runTool("xtalk.get", {}, {
  env,
  fetchImpl: mockFetch(200, { schema: "cosmos-xtalk/1", kind: "UNMEASURED", n: 0, roles: {} }),
});
check("get UNMEASURED is ok envelope", get.ok === true && get.kind === "UNMEASURED");

const sendA = await runTool("xtalk.send", { to: "crew", body: "hi" }, {
  env,
  fetchImpl: mockFetch(200, { kind: "DRY_RUN", transport: "A", inject: false, harness: "opencode" }),
});
check("send Transport A is DRY_RUN not a fake inject",
  sendA.ok === true && sendA.kind === "DRY_RUN");
const sendInj = await runTool("xtalk.send", { to: "crew", body: "hi", inject: "true" }, {
  env,
  fetchImpl: mockFetch(501, { error: "NOT_COMPOSED", detail: "no inject" }),
});
check("inject:true is NOT_COMPOSED",
  sendInj.ok === false && sendInj.kind === "NOT_COMPOSED");

const sendB = await runTool("xtalk.send", { to: "orc", body: "hello" }, {
  env,
  fetchImpl: mockFetch(200, { kind: "ACCEPTED", transport: "B", seq: 1 }),
});
check("send Transport B ACCEPTED", sendB.ok === true && sendB.kind === "ACCEPTED");

const offbox = await runTool("xtalk.get", {}, {
  env: { COSMOS_CORE_URL: "http://example.invalid:8770" },
  fetchImpl: mockFetch(200, { kind: "MEASURED" }),
});
check("non-loopback without token is NO_TOKEN before fetch",
  offbox.ok === false && offbox.kind === "NO_TOKEN");

console.log("xtalk-plugin", failed ? "FAIL" : "PASS", `${3 + 1 - failed + 1}/4+`);
if (failed) process.exit(1);
