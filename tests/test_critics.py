#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: THE LIVE CRUCIBLE CRITIC SET (three families, three vendors).

NO LIVE VENDOR IS REQUIRED AND NO KEY IS HELD. The grok CLI is a fake binary this
test writes onto PATH (so the environment withholding is proven through a REAL
subprocess, not a mock); the Vertex transport and the OpenAI rail are injected.
What is asserted:

  * XAI_API_KEY is withheld from the grok child environment - the parent has it,
    the child does not, and the read-back guard refuses to start the CLI if a
    strip ever silently fails.
  * grok-sgh is PREFERRED over sgh-api, and the two never appear together: one
    family per vendor.
  * claude-cli is never attached - not when a `claude` binary is on PATH, not when
    ANTHROPIC_API_KEY is in the environment, and asking for it is OFF_ROUTE.
  * llama/bedrock are DEFERRED, not composed: no Meta API is minted, and a
    Bedrock-shaped environment adds no fourth family.
  * an empty compose attaches NOTHING, so the served crucible still answers 501
    CRUCIBLE_NOT_RUNNABLE.
  * the vertex and oa rails are INJECTABLE, and a full three-family round runs
    over HTTP with returns landing on disk.
"""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_service import Service
from cosmos_spend import SpendGate, SpendError
from cosmos_ledger import Ledger
import cosmos_critics as CC
from cosmos_critics import (CriticError, GrokSghCritic, attach_critics,
                            compose_critics, assert_routable, pool_summary,
                            OA_MODEL, OA_TIER, SGH_ENV_WITHHELD)
from cosmos_vertex_rail import (MODEL_PIN, VERTEX_ACCOUNT, VERTEX_PROJECT,
                                VertexExpressRail, VertexRailError,
                                resolve_model)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


FINDINGS = '```json\n[{"id": "%s-1", "topic": "shared-defect"}]\n```\nprose\n'


# ---------------- fakes (no vendor, no key, no spend) ----------------
def _which(*present):
    """A recording shutil.which: only the named binaries exist."""
    asked = []

    def which(name):
        asked.append(name)
        return f"/fake/bin/{name}" if name in present else None
    which.asked = asked
    return which


def _grok_runner(text=FINDINGS % "grok-sgh", rc=0, timed_out=False):
    """A fake cosmos_platform.run_tree_killed: records argv + env, returns the
    CLI's json envelope."""
    seen = {}

    def runner(argv, timeout_s=None, env=None, cwd=None):
        seen["argv"] = list(argv)
        seen["env"] = dict(env or {})
        seen["timeout_s"] = timeout_s
        return {"rc": rc, "out": json.dumps({"text": text, "stopReason": "end_turn",
                                             "total_cost_usd": 0.0}),
                "err": "", "timed_out": timed_out, "kill_result": None,
                "elapsed_s": 0.1}
    runner.seen = seen
    return runner


def _vertex_transport(text=FINDINGS % "gem-api", raises=None):
    seen = {}

    def transport(url, body, headers, timeout_s):
        seen["url"], seen["headers"] = url, dict(headers)
        seen["body"] = json.loads(body.decode("utf-8"))
        seen["timeout_s"] = timeout_s
        if raises is not None:
            raise raises
        return json.dumps({"candidates": [{"content": {"parts": [{"text": text}]}}],
                           "usageMetadata": {"totalTokenCount": 1234}})
    transport.seen = seen
    return transport


class FakeRail:
    """Any injected rail: probe/dispatch, recording what it was asked."""
    kind = "API"

    def __init__(self, text="ok", live=True, ok=True, model=None, boom=None):
        self.text, self.live, self.ok, self.model, self.boom = text, live, ok, model, boom
        self.calls = []
        self.metered_usd = 0.05

    def probe(self):
        return (True, "fake rail live") if self.live else (False, "UNREACHABLE: fake")

    def dispatch(self, payload):
        self.calls.append(payload)
        if self.boom:
            raise self.boom
        return {"ok": self.ok, "kind": "API" if self.ok else "BROKE",
                "text": self.text, "usd": 0.01, "node": "fake",
                "model": self.model, "detail": "" if self.ok else "fake rail down"}


def _fake_grok_binary(dirpath: Path, record: Path) -> Path:
    """A REAL executable on PATH that records the environment and argv it was
    started with, then answers like `grok --single ... --output-format json`."""
    dirpath.mkdir(parents=True, exist_ok=True)
    exe = dirpath / "grok"
    exe.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        f"open({str(record)!r}, 'w', encoding='utf-8').write(json.dumps(\n"
        "    {'argv': sys.argv[1:], 'env': dict(os.environ)}))\n"
        "print(json.dumps({'text': " + repr(FINDINGS % "grok-sgh") + ",\n"
        "                  'stopReason': 'end_turn'}))\n",
        encoding="utf-8")
    exe.chmod(0o755)
    return exe


def _http(port, method, path, obj=None, token=""):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    req.add_header("Authorization", "Bearer " + token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_critics_"))
    PARENT_ENV = {"PATH": "/usr/bin", "HOME": "/home/keith",
                  "XAI_API_KEY": "xai-SECRET-should-never-reach-the-child",
                  "ANTHROPIC_API_KEY": "sk-ant-off-the-route",
                  "VERTEX_EXPRESS_API_KEY": "express-KEY-not-real",
                  "GOOGLE_API_KEY": "keith-paid-studio-key",
                  "GOOGLE_APPLICATION_CREDENTIALS": "/home/keith/adc.json",
                  "AWS_REGION": "us-east-1", "AWS_BEARER_TOKEN_BEDROCK": "unbound"}

    # ================= 1. THE GROK ENVIRONMENT =================
    runner = _grok_runner()
    gc = GrokSghCritic(binary="/fake/bin/grok", env=PARENT_ENV, runner=runner)
    env = gc.child_env()
    check("grok-sgh: XAI_API_KEY is WITHHELD from the child env (the parent has it)",
          lambda: "XAI_API_KEY" in PARENT_ENV and "XAI_API_KEY" not in env)
    check("grok-sgh: the rest of the environment survives (HOME/PATH intact - a "
          "strip, not a scrub)",
          lambda: env["HOME"] == "/home/keith" and env["PATH"] == "/usr/bin"
          and len(env) == len(PARENT_ENV) - len(SGH_ENV_WITHHELD))
    out = gc("# PACKET BODY\n")
    check("grok-sgh: argv is `grok --single <prompt>` with the prompt as the flag's "
          "value (headless mode does not read stdin)",
          lambda: runner.seen["argv"][0] == "/fake/bin/grok"
          and runner.seen["argv"][1] == "--single"
          and "# PACKET BODY" in runner.seen["argv"][2]
          and "--output-format" in runner.seen["argv"])
    check("grok-sgh: the argv also denies Bash/Edit/Write (a critic judges, it does "
          "not touch the tree it reviews)",
          lambda: runner.seen["argv"].count("--deny") == 3
          and {"Bash", "Edit", "Write"} <= set(runner.seen["argv"]))
    check("grok-sgh: the env handed to the RUNNER carries no XAI_API_KEY",
          lambda: "XAI_API_KEY" not in runner.seen["env"])
    check("grok-sgh: the return is the CLI's json text, with a provenance header",
          lambda: "shared-defect" in out and "family=grok-sgh" in out)
    check("grok-sgh: never metered per call - the weekly pool is already paid",
          lambda: gc.metered_usd == 0.0
          and "weekly pool" in gc.describe())

    class LeakyGrok(GrokSghCritic):
        def _strip(self, base):                 # a strip that silently did nothing
            return dict(base)

    leaky = LeakyGrok(binary="grok", env=PARENT_ENV, runner=_grok_runner())
    check("grok-sgh: a failed strip is caught by READ-BACK -> ENV_WITHHOLD_FAILED, "
          "the CLI never starts",
          expect(CriticError, "ENV_WITHHOLD_FAILED")(lambda: leaky.child_env()))
    check("...and the leaky critic refuses the whole call, rather than billing the "
          "prepaid API credit",
          expect(CriticError, "ENV_WITHHOLD_FAILED")(lambda: leaky("packet")))

    # non-zero exit and a timeout are FINDINGS, not silent empties
    check("grok-sgh: rc!=0 raises (a dead critic is a recorded finding)",
          expect(CriticError, "CLI_FAILED")(
              lambda: GrokSghCritic(binary="grok", env=PARENT_ENV,
                                    runner=_grok_runner(rc=1))("p")))
    check("grok-sgh: a timeout raises TIMEOUT with the kill outcome",
          expect(CriticError, "TIMEOUT")(
              lambda: GrokSghCritic(binary="grok", env=PARENT_ENV,
                                    runner=_grok_runner(timed_out=True))("p")))

    # ---- the same withholding through a REAL subprocess ----
    if os.name == "nt":
        check("grok-sgh: real-subprocess env withholding [SKIPPED-NON-NATIVE: needs a "
              "POSIX shebang]", lambda: True)
    else:
        bindir = td / "bin"
        bindir.mkdir(parents=True, exist_ok=True)
        record = td / "grok_saw.json"
        exe = _fake_grok_binary(bindir, record)
        live_env = dict(os.environ, XAI_API_KEY="xai-SECRET-live-parent")
        real = GrokSghCritic(binary=str(exe), env=live_env)
        real_out = real("# REAL SUBPROCESS PACKET\n")
        saw = json.loads(record.read_text(encoding="utf-8"))
        check("grok-sgh REAL SUBPROCESS: the CLI process saw NO XAI_API_KEY while "
              "the parent had one (measured, not mocked)",
              lambda: "XAI_API_KEY" in live_env
              and "XAI_API_KEY" not in saw["env"])
        check("grok-sgh REAL SUBPROCESS: --single carried the packet and the json "
              "envelope was parsed",
              lambda: saw["argv"][0] == "--single"
              and "# REAL SUBPROCESS PACKET" in saw["argv"][1]
              and "shared-defect" in real_out)

    # ================= 2. VENDOR-PLURAL PREFERENCE =================
    led = Ledger(td / "c.jsonl", b"k", "core")
    spend = SpendGate(led)
    w_grok = _which("grok")
    critics, absent = compose_critics(env=PARENT_ENV, which=w_grok, spend=spend,
                                      grok_runner=_grok_runner(),
                                      vertex_transport=_vertex_transport(),
                                      oa_rail=FakeRail(text=FINDINGS % "oa-api"))
    check("compose: grok CLI present -> grok-sgh is the xAI family",
          lambda: "grok-sgh" in critics)
    check("compose: sgh-api is NOT composed beside it (same vendor, and the pool "
          "already covers it)",
          lambda: "sgh-api" not in critics and "SAME VENDOR" in absent["sgh-api"])
    check("compose: three families, three DISTINCT vendors",
          lambda: sorted(critics) == ["gem-api", "grok-sgh", "oa-api"]
          and sorted({CC.FAMILY_VENDOR[f] for f in critics})
          == ["google", "openai", "xai"])
    check("compose: `which` was asked about grok ONLY - no claude, no codex binary "
          "was ever looked for",
          lambda: w_grok.asked == ["grok"])
    check("compose: the metered families get a budget; grok-sgh gets none because "
          "the weekly pool is not per-call money",
          lambda: {"gem-api", "oa-api"} <= set(spend.audit()["rails"])
          and "grok-sgh" not in spend.audit()["rails"])

    critics2, absent2 = compose_critics(
        env=PARENT_ENV, which=_which(), spend=SpendGate(led),
        sgh_rail=FakeRail(text=FINDINGS % "sgh-api"),
        vertex_transport=_vertex_transport(),
        oa_rail=FakeRail(text=FINDINGS % "oa-api"))
    check("compose: grok CLI ABSENT -> sgh-api is the xAI family (the documented "
          "fallback, and only then)",
          lambda: "sgh-api" in critics2 and "grok-sgh" not in critics2
          and "not on PATH" in absent2["grok-sgh"])
    check("compose: still exactly one xAI member",
          lambda: sum(1 for f in critics2 if CC.FAMILY_VENDOR[f] == "xai") == 1)
    check("compose: the vendor-plural rule is STRUCTURAL - if a second family ever "
          "mapped to a vendor already in the pool, compose REFUSES "
          "(VENDOR_DOUBLE_COUNT)",
          expect(CriticError, "VENDOR_DOUBLE_COUNT")(
              lambda: _double_count(led)))

    # ================= 3. ANTHROPIC IS OFF THE ROUTE =================
    w_claude = _which("grok", "claude", "claude-code")
    critics3, _ = compose_critics(env=PARENT_ENV, which=w_claude, spend=SpendGate(led),
                                  grok_runner=_grok_runner(),
                                  vertex_transport=_vertex_transport(),
                                  oa_rail=FakeRail())
    check("claude-cli is NEVER attached - a `claude` binary on PATH and an "
          "ANTHROPIC_API_KEY in the env change nothing",
          lambda: not any("claude" in f for f in critics3)
          and "anthropic" not in {CC.FAMILY_VENDOR[f] for f in critics3}
          and "ANTHROPIC_API_KEY" in PARENT_ENV)
    check("asking for claude-cli is a typed OFF_ROUTE refusal",
          expect(CriticError, "OFF_ROUTE")(lambda: assert_routable("claude-cli")))
    check("asking for claude-bedrock is OFF_ROUTE too (Anthropic off-route AND the "
          "account unbound)",
          expect(CriticError, "OFF_ROUTE")(lambda: assert_routable("claude-bedrock")))
    check("an invented family name is UNKNOWN_FAMILY, never composed",
          expect(CriticError, "UNKNOWN_FAMILY")(lambda: assert_routable("gpt-oss-cli")))

    # ================= 4. LLAMA IS NOT A FOURTH FAMILY =================
    check("llama is DEFERRED_FAMILY (Keith adds it later, or taps it on Bedrock)",
          expect(CriticError, "DEFERRED_FAMILY")(lambda: assert_routable("llama")))
    check("bedrock is DEFERRED_FAMILY: the account is opening/unbound - no region, "
          "no keys",
          expect(CriticError, "DEFERRED_FAMILY")(lambda: assert_routable("bedrock")))
    check("a Bedrock-shaped environment adds NO fourth family and mints no Meta API",
          lambda: "AWS_REGION" in PARENT_ENV
          and len(critics3) == 3 and "llama" not in critics3
          and not any("bedrock" in f for f in critics3))
    check("the deferral is declared, not silent (attach reports it)",
          lambda: "llama" in CC.DEFERRED and "llama" in
          attach_critics(Kernel(_root(td, "def"), worker="core"),
                         env={}, which=_which(), spend=None)["deferred"])

    # ================= 5. EMPTY COMPOSE -> STILL 501 =================
    # a breaker IS composed here, so every absence is about LIVENESS, not budget
    critics4, absent4 = compose_critics(env={}, which=_which(),
                                        spend=SpendGate(Ledger(td / "e.jsonl", b"k", "c")),
                                        sgh_rail=FakeRail(live=False),
                                        oa_rail=FakeRail(live=False))
    check("empty compose: nothing measured live -> NO critics, and every family "
          "carries its measured reason",
          lambda: critics4 == {}
          and {"grok-sgh", "sgh-api", "gem-api", "oa-api"} == set(absent4))
    check("empty compose: the gem absence names the missing express key, never a "
          "fallback to Keith's paid key",
          lambda: "VERTEX_EXPRESS_API_KEY" in absent4["gem-api"])
    check("empty compose: the summary line says the crucible is not runnable",
          lambda: "501" in pool_summary({"attached": {}, "vendors": [],
                                         "absent": absent4}))

    root501 = _root(td, "empty")
    k501 = Kernel(root501, worker="core")
    check("a bare Kernel() has NO critic pool (attachment is not a kernel verb)",
          lambda: getattr(k501, "crucible_critics", None) is None)
    rep501 = attach_critics(k501, env={}, which=_which(),
                            sgh_rail=FakeRail(live=False), oa_rail=FakeRail(live=False))
    check("attach_critics with an empty pool attaches NOTHING (the attribute stays "
          "unset - no empty dict, no stub)",
          lambda: rep501["attached"] == {}
          and getattr(k501, "crucible_critics", None) is None)
    check("...and the absence is ledgered as CRUCIBLE_CRITICS_ABSENT",
          lambda: any(e["event"] == "CRUCIBLE_CRITICS_ABSENT"
                      and "501" in e["payload"]["effect"]
                      for e in k501.ledger.verify()))
    svc501 = Service(k501, host="127.0.0.1", port=0)
    svc501.serve_background()
    (k501.paths.role("docs") / "p.md").write_text("# p\n", encoding="utf-8")
    code, body = _http(svc501.port, "POST", "/api/v1/crucible",
                       {"sources": ["p.md"]}, token=svc501.token)
    check("POST /crucible after an EMPTY attach -> 501 CRUCIBLE_NOT_RUNNABLE "
          "(Kernel+Service without critics still refuses)",
          lambda: code == 501 and body.get("error") == "CRUCIBLE_NOT_RUNNABLE")
    svc501.shutdown()

    # ================= 6. THE VERTEX RAIL (gem-api) =================
    check("vertex: the model is PINNED to gemini-2.5-flash with no live gate",
          lambda: resolve_model()[0] == MODEL_PIN == "gemini-2.5-flash"
          and "PINNED" in resolve_model()[1])
    check("vertex: a live gate returning 3.8 UNPINS it",
          lambda: resolve_model(lambda: "gemini-3.8-flash")[0] == "gemini-3.8-flash")
    check("vertex: a gate returning anything else keeps the pin",
          lambda: resolve_model(lambda: "gemini-3.0-pro")[0] == MODEL_PIN
          and "not gemini-3.8" in resolve_model(lambda: "gemini-3.0-pro")[1])
    check("vertex: a gate that RAISES keeps the pin (a broken gate is not a version "
          "bump)",
          lambda: resolve_model(_boom)[0] == MODEL_PIN)
    check("vertex: do_not_activate=False is ACTIVATE_REFUSED - Activate destroys the "
          "free credit",
          expect(VertexRailError, "ACTIVATE_REFUSED")(
              lambda: VertexExpressRail(do_not_activate=False)))
    check("vertex: a billing_project is BILLING_REFUSED - never Keith GCloud billing",
          expect(VertexRailError, "BILLING_REFUSED")(
              lambda: VertexExpressRail(billing_project="keith-prod")))
    check("vertex: an ungated model argument is MODEL_NOT_GATED",
          expect(VertexRailError, "MODEL_NOT_GATED")(
              lambda: VertexExpressRail(model="gemini-9-ultra")))

    tp = _vertex_transport()
    vr = VertexExpressRail(env=PARENT_ENV, transport=tp)
    ok, detail = vr.probe()
    r = vr.dispatch({"prompt": "review this"})
    check("vertex: probe is live on the express key and NAMES the account/project/pin",
          lambda: ok and VERTEX_ACCOUNT in detail and VERTEX_PROJECT in detail
          and MODEL_PIN in detail and "do_not_activate=True" in detail)
    check("vertex: probe says out loud which auth vars it IGNORES (no account "
          "collapse onto keith.bbf's paid key or ADC)",
          lambda: "IGNORED on purpose" in detail
          and "GOOGLE_API_KEY" in detail
          and "GOOGLE_APPLICATION_CREDENTIALS" in detail)
    check("vertex: the request goes to the PINNED model's express endpoint",
          lambda: tp.seen["url"].endswith(
              f"models/{MODEL_PIN}:generateContent"))
    check("vertex: the key travels in the x-goog-api-key HEADER, never in the URL "
          "(a URL lands in logs)",
          lambda: tp.seen["headers"]["x-goog-api-key"]
          == PARENT_ENV["VERTEX_EXPRESS_API_KEY"]
          and PARENT_ENV["VERTEX_EXPRESS_API_KEY"] not in tp.seen["url"])
    check("vertex: the return carries text, the account, the project and the pin's "
          "provenance, and prices the free credit as UNPRICED (never zero)",
          lambda: r["ok"] and "shared-defect" in r["text"]
          and r["account"] == VERTEX_ACCOUNT and r["project"] == VERTEX_PROJECT
          and r["model"] == MODEL_PIN and r["usd"] is None
          and "PINNED" in r["model_provenance"])

    leak = _vertex_transport(raises=RuntimeError(
        "401 for key " + PARENT_ENV["VERTEX_EXPRESS_API_KEY"]))
    rleak = VertexExpressRail(env=PARENT_ENV, transport=leak).dispatch({"prompt": "x"})
    check("vertex: a vendor error that ECHOES THE KEY is redacted before it can "
          "reach a ledger or a RETURN file",
          lambda: not rleak["ok"]
          and PARENT_ENV["VERTEX_EXPRESS_API_KEY"] not in rleak["detail"]
          and "[REDACTED]" in rleak["detail"])

    nokey = VertexExpressRail(env={"GOOGLE_API_KEY": "keith-paid",
                                   "GOOGLE_APPLICATION_CREDENTIALS": "/adc.json"},
                              transport=_vertex_transport())
    nok, nodetail = nokey.probe()
    check("vertex: with no express key, GOOGLE_API_KEY/ADC do NOT stand in - probe "
          "is UNREACHABLE and dispatch is typed, never fabricated",
          lambda: not nok and "UNREACHABLE" in nodetail
          and nokey.dispatch({"prompt": "x"})["kind"] == "UNREACHABLE")

    # gem-api's budget carries the credit's real expiry
    led_g = Ledger(td / "g.jsonl", b"k", "core")
    spend_g = SpendGate(led_g)
    compose_critics(env=PARENT_ENV, which=_which(), spend=spend_g,
                    sgh_rail=FakeRail(live=False), oa_rail=FakeRail(live=False),
                    vertex_transport=_vertex_transport())
    audit = spend_g.audit()["rails"]
    check("gem-api: the budget is the $300 credit AND its expiry (an expired credit "
          "is not money)",
          lambda: audit["gem-api"]["cap_usd"] == 300.0
          and audit["gem-api"]["expires_in_days"] is not None)

    # ================= 7. THE OA RAIL (oa-api) =================
    oa = FakeRail(text=FINDINGS % "oa-api")
    led_o = Ledger(td / "o.jsonl", b"k", "core")
    spend_o = SpendGate(led_o)
    critics5, _absent5 = compose_critics(env=PARENT_ENV, which=_which("grok"),
                                         spend=spend_o, grok_runner=_grok_runner(),
                                         vertex_transport=_vertex_transport(),
                                         oa_rail=oa)
    oa_out = critics5["oa-api"]("# packet\n")
    check("oa-api: the injected rail is asked for tier terra (gpt-5.6-terra) - the "
          "API, not Codex and not a ChatGPT plan",
          lambda: oa.calls[0]["kwargs"]["model"] == OA_MODEL == "gpt-5.6-terra"
          and OA_TIER == "terra"
          and "not Codex" in critics5["oa-api"].describe())
    check("oa-api: the return lands with its provenance header",
          lambda: "family=oa-api" in oa_out and "shared-defect" in oa_out)
    check("oa-api: the metered call went through the breaker (SPEND_SETTLED)",
          lambda: any(e["event"] == "SPEND_SETTLED"
                      and e["payload"]["rail"] == "oa-api"
                      for e in led_o.verify()))

    _, absent_nb = compose_critics(env=PARENT_ENV, which=_which("grok"), spend=None,
                                   grok_runner=_grok_runner(),
                                   vertex_transport=_vertex_transport(),
                                   oa_rail=FakeRail())
    check("oa-api: NO breaker -> NOT composed. Auto-reload does not self-limit, so "
          "an unbudgeted OpenAI rail has no ceiling at all",
          lambda: "no SpendGate composed" in absent_nb["oa-api"]
          and "auto-reload" in absent_nb["oa-api"])
    check("...and the same refusal applies to the metered gem/sgh rails",
          lambda: "no SpendGate composed" in absent_nb["gem-api"])

    oa2 = FakeRail()
    led_d = Ledger(td / "d.jsonl", b"k", "core")
    spend_d = SpendGate(led_d)
    critics6, _ = compose_critics(env=PARENT_ENV, which=_which("grok"), spend=spend_d,
                                  grok_runner=_grok_runner(),
                                  vertex_transport=_vertex_transport(), oa_rail=oa2)
    spend_d.set_budget("oa-api", 0.001)          # smaller than one worst case
    check("oa-api: an exhausted cap DENIES before the call - the fake rail is never "
          "reached (the breaker is in the caller)",
          lambda: _denied(critics6["oa-api"]) and oa2.calls == [])

    dead = FakeRail(ok=False)
    critics7, _ = compose_critics(env=PARENT_ENV, which=_which("grok"),
                                  spend=SpendGate(Ledger(td / "x.jsonl", b"k", "c")),
                                  grok_runner=_grok_runner(),
                                  vertex_transport=_vertex_transport(), oa_rail=dead)
    check("a family that answers BROKE raises out of the critic, so the crucible "
          "records it as a FINDING rather than an absence",
          expect(CriticError, "BROKE")(lambda: critics7["oa-api"]("p")))

    # ================= 8. ATTACHMENT LIVES ONLY IN cosmos.py serve() ==============
    import cosmos_service as _svcmod
    cos_dir = Path(_svcmod.__file__).resolve().parent
    cos_src = (cos_dir / "cosmos.py").read_text(encoding="utf-8")
    serve_block = cos_src.split('if a.cmd == "serve":')[1].split('if a.cmd ==')[0]
    check("cosmos.py serve() attaches the pool after Kernel()",
          lambda: "attach_critics(k)" in serve_block
          and "pool_summary" in serve_block)
    check("neither the Kernel nor the Service composes a critic - so an un-attached "
          "kernel keeps its honest 501",
          lambda: "cosmos_critics" not in
          (cos_dir / "cosmos_kernel.py").read_text(encoding="utf-8")
          and "cosmos_critics" not in
          (cos_dir / "cosmos_service.py").read_text(encoding="utf-8"))
    check("attachment happens in serve() and nowhere else in the tree",
          lambda: [p.name for p in sorted(cos_dir.glob("*.py"))
                   if "attach_critics(" in p.read_text(encoding="utf-8")]
          == ["cosmos.py", "cosmos_critics.py"])

    # ---- live: `cosmos.py serve` composes grok-sgh from PATH and runs a round ----
    if os.name == "nt":
        check("live serve round [SKIPPED-NON-NATIVE]", lambda: True)
    else:
        root = _root(td, "serve")
        rec = td / "serve_grok_saw.json"
        _fake_grok_binary(td / "bin", rec)
        senv = dict(os.environ)
        senv["PATH"] = str(td / "bin") + os.pathsep + senv.get("PATH", "")
        senv["XAI_API_KEY"] = "xai-SECRET-parent-of-serve"
        senv["PYTHONPATH"] = os.pathsep.join(
            [str(cos_dir)] + ([senv["PYTHONPATH"]] if senv.get("PYTHONPATH") else []))
        proc = subprocess.Popen(
            [sys.executable, str(cos_dir / "cosmos.py"), "serve",
             "--root", str(root), "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=senv)
        try:
            summary, port = "", None
            deadline = time.time() + 60
            while time.time() < deadline and summary == "":
                line = proc.stdout.readline()
                if not line:
                    break
                if line.startswith("COSMOS API serving"):
                    m = re.search(r"127\.0\.0\.1:(\d+)", line)
                    port = int(m.group(1)) if m else None
                elif line.startswith("crucible critics:"):
                    summary = line.strip()
            check("live serve: the banner names the composed pool - grok-sgh on xAI",
                  lambda: "grok-sgh" in summary and "xai" in summary
                  and "NONE" not in summary)
            k_live = Kernel(root, worker="probe", read_only=True)
            token = k_live.paths.config("api_token.txt").read_text(
                encoding="utf-8").strip()
            k_live.paths.role("docs", "packet.md").write_text(
                "# LIVE PACKET\nthe artifact under review\n", encoding="utf-8")
            code, body = _http(port, "POST", "/api/v1/crucible",
                               {"sources": ["packet.md"], "critics": ["grok-sgh"]},
                               token=token)
            check("live serve: POST /crucible -> 201 and the grok-sgh return LANDS "
                  "ON DISK (the CLI ran, the packet went in on --single)",
                  lambda: code == 201
                  and "grok-sgh" in (body.get("returned") or {})
                  and Path(body["returned"]["grok-sgh"]).exists()
                  and "shared-defect" in Path(
                      body["returned"]["grok-sgh"]).read_text(encoding="utf-8"))
            saw2 = json.loads(rec.read_text(encoding="utf-8"))
            check("live serve: the CLI the SERVER started also saw no XAI_API_KEY, "
                  "and the served packet reached it",
                  lambda: "XAI_API_KEY" not in saw2["env"]
                  and "the artifact under review" in saw2["argv"][1])
            check("live serve: the attach is ledgered with families + vendors and no "
                  "key material",
                  lambda: any(
                      e["event"] == "CRUCIBLE_CRITICS_ATTACHED"
                      and e["payload"]["families"] == ["grok-sgh"]
                      and e["payload"]["vendors"] == ["xai"]
                      and "SECRET" not in json.dumps(e["payload"])
                      for e in k_live.ledger.verify()))
            check("live serve: a single-family round is FLAGGED, not celebrated",
                  lambda: any(
                      e["event"] == "CRUCIBLE_CRITICS_ATTACHED"
                      and e["payload"]["single_family_warning"]
                      for e in k_live.ledger.verify())
                  and "SINGLE FAMILY" in summary)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:                          # pragma: no cover
                proc.kill()

    # ================= 9. THE THREE-FAMILY ROUND, OVER HTTP =================
    root3 = _root(td, "round3")
    k3 = Kernel(root3, worker="core")
    rep3 = attach_critics(k3, env=PARENT_ENV, which=_which("grok"),
                          grok_runner=_grok_runner(),
                          vertex_transport=_vertex_transport(),
                          oa_rail=FakeRail(text=FINDINGS % "oa-api"))
    check("attach: three families attached, three vendors, no single-family warning",
          lambda: sorted(rep3["attached"]) == ["gem-api", "grok-sgh", "oa-api"]
          and rep3["vendors"] == ["google", "openai", "xai"]
          and sorted(k3.crucible_critics) == ["gem-api", "grok-sgh", "oa-api"])
    svc3 = Service(k3, host="127.0.0.1", port=0)
    svc3.serve_background()
    (k3.paths.role("docs") / "packet.md").write_text(
        "# ARTIFACT\nthe thing being judged\n", encoding="utf-8")
    code3, body3 = _http(svc3.port, "POST", "/api/v1/crucible",
                         {"sources": ["packet.md"]}, token=svc3.token)
    check("three-family round: 201, every family's return on disk",
          lambda: code3 == 201
          and sorted(body3["returned"]) == ["gem-api", "grok-sgh", "oa-api"]
          and all(Path(p).exists() and Path(p).stat().st_size > 0
                  for p in body3["returned"].values()))
    merge = Path(body3["merge"]).read_text(encoding="utf-8") if code3 == 201 else ""
    check("three-family round: the merge separates the shared finding as UNANIMOUS "
          "across all three",
          lambda: "shared-defect" in merge.split("## MAJORITY")[0]
          and "gem-api" in merge and "grok-sgh" in merge and "oa-api" in merge)
    check("three-family round: no family failed and the job closed CLEAN",
          lambda: not body3.get("failed") and body3.get("outcome") == "CLEAN")
    svc3.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (three families, three vendors; XAI_API_KEY "
          "withheld; anthropic off-route; llama deferred; empty compose still 501)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _root(td: Path, name: str) -> Path:
    root = td / name
    install(root, tree_id=f"critics-{name}")
    return root


def _boom():
    raise RuntimeError("gate unreachable")


def _double_count(led):
    """Drive the REAL guard in compose_critics: re-badge the openai family as xAI
    for one call, so the composed pool would carry two members of one vendor."""
    saved = CC.FAMILY_VENDOR["oa-api"]
    CC.FAMILY_VENDOR["oa-api"] = "xai"
    try:
        compose_critics(env={"VERTEX_EXPRESS_API_KEY": "k"}, which=_which("grok"),
                        spend=SpendGate(led), grok_runner=_grok_runner(),
                        vertex_transport=_vertex_transport(), oa_rail=FakeRail())
    finally:
        CC.FAMILY_VENDOR["oa-api"] = saved


def _denied(critic):
    try:
        critic("packet")
    except SpendError as e:
        return e.kind == "DENIED"
    return False


def test_critics():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
