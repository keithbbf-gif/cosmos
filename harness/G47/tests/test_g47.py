"""G47 binding tests. No vendor process is started."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from g47.contracts import Legend, OutputContract
from g47.doors import get_door
from g47.grade import grade
from g47.pack import project
from g47.refuse import Refuse
from g47.scars import classify
from g47.size import compute
from g47.summon import execute, materialize, plan


def legend(**kw: object) -> Legend:
    base: dict[str, object] = dict(
        role="CODER",
        model="inclusionai/ling-3.0-flash",
        window=1_000_000,
        task="Say the contract.",
    )
    base.update(kw)
    return Legend(**base)  # type: ignore[arg-type]


def test_max_formula_and_refuse():
    sized = compute(1000, cached_tokens=100, prompt_tokens=100, optimum=50)
    assert sized.margin == 200
    assert sized.max_tokens == 600
    assert sized.optimum == 50
    with pytest.raises(Refuse) as exc:
        compute(100, 80, 10)
    assert exc.value.reason == "MAX_LE_ZERO"


def test_optimum_float_and_clamp():
    sized = compute(1000, 0, 100, optimum="float")
    assert sized.optimum == "float"
    sized = compute(1000, 0, 100, optimum=5000)
    assert sized.optimum == sized.max_tokens


def test_keep_under_grok():
    with pytest.raises(Refuse) as exc:
        plan(legend(role="CODER", model="grok-4.6", window=2_000_000, task="x" * 900_000), "grok")
    assert exc.value.reason == "KEEP_UNDER"


def test_none_first_text_and_python_and_ping():
    text = grade("NONE\nok\n", OutputContract("CODER", "text"))
    assert text.mouth_ok and text.applied and text.reason == "TEXT_OK"
    bad = grade("def f():\n    pass\n", OutputContract("CODER", "text"))
    assert not bad.mouth_ok and bad.reason == "FIRST_LINE"
    py = grade("def f():\n    pass\n", OutputContract("CODER", "python"), door_grade="filed_text")
    assert py.applied and py.reason == "PYTHON_OK"
    ping = grade("NONE\nHERO_OK ling\n", OutputContract("CODER", "text", ping=True))
    assert ping.applied and ping.reason == "PING_OK" and ping.task_pass is False
    spaced = grade("NONE \nok\n", OutputContract("CODER", "text"))
    assert spaced.reason == "TEXT_OK"
    fence = grade("```\nNONE\n", OutputContract("CODER", "python"))
    assert fence.reason == "FENCE"
    unbound = grade(
        "NONE\n",
        OutputContract("CODER", "text"),
        served_model="",
        expected_model="nex-agi/nex-n2.5-mini:free",
    )
    assert unbound.mouth_ok and not unbound.applied and unbound.reason == "SKU_UNBOUND"
    prefill = grade("NONE\n", OutputContract("CODER", "text"), prefill_injected=True)
    assert prefill.reason == "PREFILL_ONLY"


def test_worktree_mouth_is_not_applied():
    result = grade("NONE\n", OutputContract("CODER", "text"), door_grade="worktree")
    assert result.mouth_ok and not result.applied and result.reason == "NEED_WORKTREE"
    result = grade("NONE\n", OutputContract("CODER", "text"), door_grade="worktree", worktree_obeyed=True)
    assert result.applied


def test_strong_pack_is_thin_and_weak_style_is_not_system():
    strong = project(legend(wrap="ROLE WRAP\n", style="be terse\n"), get_door("opencode"))
    assert strong.system == ""
    assert "ROLE WRAP" not in strong.user
    assert "AGENTS.md" in strong.files
    assert "CONTRACT" in strong.user
    weak = project(legend(wrap="ROLE WRAP\n", style="be terse\n"), get_door("openrouter"))
    assert weak.system == "ROLE WRAP"
    assert "be terse" in weak.user
    assert "be terse" not in weak.system


def test_opencode_and_claude_argv():
    built = plan(legend(where=r"V:\tmp\attempt"), "opencode")
    assert built.argv[:2] == ["opencode.cmd", "run"]
    assert "--dir" in built.argv
    assert "-m" in built.argv
    assert "openrouter/inclusionai/ling-3.0-flash" in built.argv
    assert "--fallback-model" not in built.argv
    claude = plan(legend(model="claude-sonnet-4-6", where=r"V:\tmp\attempt"), "claude")
    assert claude.seated is False
    assert "--bare" in claude.argv
    assert "--fallback-model" not in claude.argv
    assert "--max-turns" in claude.argv
    assert "--print" not in claude.argv  # short flag is -p
    assert "-p" in claude.argv


def test_orc_and_context_and_hermes():
    with pytest.raises(Refuse) as exc:
        plan(legend(role="ORC", model="gpt"), "codex")
    assert exc.value.reason == "ORC_NO_CODING"
    with pytest.raises(Refuse) as exc:
        plan(legend(context=("a · b",)), "opencode")
    assert exc.value.reason == "NO_CONTEXT"
    hermes = plan(legend(model="hermes-pool"), "hermes")
    assert hermes.seated is False
    deep = plan(legend(model="deepseek-v4"), "deepseek")
    assert deep.door == "dsh"
    assert deep.argv[:3] == ["dsh.cmd", "--profile", "headless"]


def test_materialize_skips_existing_agents_and_refuses_live(tmp_path: Path):
    built = plan(legend(wrap="NEW\n", where=str(tmp_path)), "opencode")
    (tmp_path / "AGENTS.md").write_text("OLD\n", encoding="utf-8")
    materialize(built, tmp_path)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "OLD\n"
    assert (tmp_path / "TASK.md").is_file()
    with pytest.raises(Refuse) as exc:
        materialize(built, tmp_path / "live")
    assert exc.value.reason == "LIVE_TREE"


def test_codex_write_flag_and_forbid():
    house = dict(model="gpt-5.6-luna", wrap="role = CODER\npen = none\n")
    built = plan(legend(**house), "codex", write=True)
    assert "--approve-for-me" in built.argv
    assert "--sandbox" not in built.argv
    assert "--ignore-user-config" not in built.argv
    assert "--full-auto" not in built.argv
    assert "--ephemeral" in built.argv
    judge = plan(legend(role="JUDGE", model="gpt-5.6-luna", what="text", wrap="role = JUDGE\n"), "codex")
    assert "--approve-for-me" not in judge.argv
    assert judge.argv[judge.argv.index("--sandbox") + 1] == "read-only"
    graded = grade("KEEP\n", OutputContract("JUDGE", "text"))
    assert graded.applied
    with pytest.raises(Refuse) as exc:
        plan(legend(model="gpt-5.6-luna"), "codex")
    assert exc.value.reason == "EMPTY_HOUSE"


def test_slug_classes_and_no_retry():
    with pytest.raises(Refuse) as exc:
        plan(legend(model="qwen/qwen:free:floor"), "openrouter")
    assert exc.value.reason == "FLOOR_ON_FREE"
    with pytest.raises(Refuse) as exc:
        plan(legend(model="thinkingmachines/inkling:free"), "openrouter")
    assert exc.value.reason == "HARNESS_GATE"
    with pytest.raises(Refuse) as exc:
        plan(legend(model="openai/gpt-6-luna:floor"), "openrouter")
    assert exc.value.reason == "WRONG_VIA"
    with pytest.raises(Refuse) as exc:
        plan(legend(model="z-ai/glm-5.3-flash"), "openrouter")
    assert exc.value.reason == "MIXED_VIA"
    # A named deepseek pin on the rail is not the dsh binary. Do not block it here.
    rail = plan(legend(model="deepseek/deepseek-v4.1-flash"), "openrouter")
    assert rail.argv == []
    assert rail.rail is not None
    assert rail.rail["routing"] == "off"
    assert rail.rail["allow_fallbacks"] is False
    assert rail.rail["max_tokens"] != 2048
    row = classify(http=429, detail="upstream_provider_shared_pool")
    assert row["class"] == "UPSTREAM_POOL" and row["retry_same"] is False
    down = classify(http=502, detail="Upstream error from Nvidia: Internal server error")
    assert down["class"] == "UPSTREAM" and down["retry_same"] is False
    pin = classify(http=None, detail="not a pinned OpenRouter id 'liquid/lfm-2.5-2.6b:free'")
    assert pin["class"] == "PIN_GATE" and pin["retry_same"] is False


def test_named_shape_is_one_call_and_the_latch_stays():
    """A provider sentence names one new body. The SOP is not cleared for a third call."""
    from g47.loop import Attempt, action_for, run

    pcm = "Unsupported value: 'audio.format' does not support 'wav'. Supported values are: 'pcm16'."
    audio = Attempt("openai/gpt-audio", "openrouter", "audio")
    named = action_for(audio, "REJECTED", pcm)
    assert named.sop == "audio_pcm16" and named.shape == "pcm16" and named.again
    held = action_for(
        Attempt("openai/gpt-audio", "openrouter", "audio", applied=("audio_pcm16",)),
        "REJECTED",
        pcm,
    )
    assert held.again is False

    batch = action_for(
        Attempt("anthropic/claude-opus-5.5:batch", "openrouter", "text"),
        "SLUG_DEAD",
        "cannot be used with the chat/completions endpoint (adapter AnthropicBatchAdapter).",
    )
    assert batch.sop == "batch_endpoint" and batch.shape == "batch"
    think = action_for(
        Attempt("anthropic/claude-opus-5.5", "openrouter", "text"),
        "REJECTED",
        "Reasoning is mandatory for this endpoint and cannot be disabled.",
    )
    assert think.sop == "reasoning_on"
    empty = action_for(Attempt("anthropic/claude-fable-5", "openrouter", "text"), "EMPTY", "")
    assert empty.sop == "reasoning_on" and empty.again
    image = action_for(
        Attempt("google/gemini-3-pro-image", "openrouter", "image", catalog_form="image"),
        "FORM_MISS",
        "",
    )
    assert image.sop == "image_endpoint" and image.shape == "images"
    relace = action_for(
        Attempt("relace/relace-apply-3", "openrouter", "text"),
        "REJECTED",
        "Provider returned error",
    )
    assert relace.sop == "apply_xml"
    lyria = action_for(
        Attempt("google/lyria-3-pro-preview", "openrouter", "audio"),
        "EMPTY",
        "Internal error encountered.",
    )
    assert lyria.again is False and "music" in lyria.reason.lower()
    kat = action_for(
        Attempt("kwaipilot/kat-coder-pro-v2.5", "openrouter", "text"),
        "REJECTED",
        "Provider returned error",
    )
    assert kat.again is False

    seen: list[str] = []

    def call(attempt: Attempt) -> dict[str, object]:
        seen.append(attempt.shape)
        return {"http": 400, "detail": pcm, "mouth": "", "served": attempt.pin, "scar": "REJECTED"}

    out = run(audio, call)
    assert seen == ["", "pcm16"]
    assert out["turns"] == 2 and out["seated"] is False and out["shape"] == "pcm16"


def test_october_scars_name_one_sop():
    """The 2026-10-01 pass. Each scar has one SOP. None of them stamps a seat."""
    from g47.loop import Attempt, action_for
    from g47.scars import same_pin

    assert same_pin("anthropic/claude-sonnet-5.5:batch", "anthropic/claude-sonnet-5.5:batch")
    assert same_pin("anthropic/claude-opus-5.5:batch", "anthropic/claude-opus-5.5")
    assert not same_pin("openrouter/auto-beta", "openai/gpt-5.6-sol")
    assert not same_pin("openrouter/bodybuilder", "google/gemini-2.5-flash")
    assert not same_pin("openrouter/auto-beta", "")
    assert not same_pin("anthropic/claude-opus-5.5", "anthropic/claude-opus-5.5-20260921")

    refused = classify(
        http=200,
        detail="The provided model 'gpt-6.1-sol' is not supported by the Batch API. (line 1)",
    )
    assert refused["class"] == "BATCH_UNSUPPORTED" and refused["retry_same"] is False
    failed = classify(http=200, detail="failed batch_id=batch-1790817770-vdGHQZ7LsL7QI8m1Bs0z")
    assert failed["class"] == "BATCH_UNSUPPORTED"
    waiting = classify(http=200, detail="in_progress batch_id=batch-1790818271-Def65LfNlMJNTTabjiru")
    assert waiting["class"] == "BATCH_OPEN" and "completed" in str(waiting["next"])
    door = classify(
        http=404,
        detail="cannot be used with the chat/completions endpoint (adapter OpenAIBatchAdapter).",
    )
    assert door["class"] == "BATCH_DOOR"
    foreign = classify(detail="json_code reused a mouth served as openai/gpt-5.6-sol")
    assert foreign["class"] == "MOUTH_FOREIGN"
    routed = classify(detail="calls served google/gemini-2.5-flash; host did not pass")
    assert routed["class"] == "MOUTH_FOREIGN"
    asked = classify(http=200, detail="Understood. What is the task?\n", mouth="What is the task?")
    assert asked["class"] == "TASK_ASK"
    unnamed = classify(http=400, detail='{"code":400,"msg":"bad request","request_id":"5721adc9"}')
    assert unnamed["class"] == "NO_SHAPE"
    safe = classify(http=200, mouth="User Safety: safe", served_model="nvidia/nemotron-3.5-content-safety")
    assert safe["class"] == "NOT_CODE"
    guard = classify(http=200, mouth="unsafe\nS14", served_model="meta-llama/llama-guard-4-12b")
    assert guard["class"] == "NOT_CODE"
    pool = classify(http=429, detail="Provider returned error")
    assert pool["class"] == "UPSTREAM_POOL" and "45" in str(pool["next"])
    dead = classify(http=404, detail="Provider returned error")
    assert dead["class"] == "SLUG_DEAD"

    opus = action_for(
        Attempt("anthropic/claude-opus-5.5", "openrouter", "text"),
        "EMPTY",
        "empty keys=content,reasoning,refusal,role",
    )
    assert opus.sop == "effort_low" and opus.shape == "effort_low" and opus.again
    assert "effort none" in opus.reason.lower()
    spent = action_for(
        Attempt("anthropic/claude-opus-5.5", "openrouter", "text", applied=("effort_low",)),
        "EMPTY",
        "empty keys=content,reasoning,refusal,role",
    )
    assert spent.again is False
    already = action_for(
        Attempt("anthropic/claude-opus-5.5", "openrouter", "text", applied=("reasoning_on",)),
        "EMPTY",
        "empty keys=content,reasoning,refusal,role",
    )
    assert already.again is False

    still = action_for(
        Attempt("anthropic/claude-opus-5.5:batch", "openrouter", "text"),
        "SLUG_DEAD",
        "in_progress batch_id=batch-1790818271-Def65LfNlMJNTTabjiru",
    )
    assert still.sop == "batch_open" and still.again is False
    gone = action_for(
        Attempt("openai/gpt-6.1-sol:batch", "openrouter", "text"),
        "SLUG_DEAD",
        "failed batch_id=batch-1790817770-vdGHQZ7LsL7QI8m1Bs0z",
    )
    assert gone.sop == "batch_unsupported" and gone.again is False
    kat = action_for(
        Attempt("kwaipilot/kat-coder-pro-v2.5", "openrouter", "text"),
        "NO_SHAPE",
        '{"code":400,"msg":"bad request"}',
    )
    assert kat.sop == "no_shape" and kat.again is False
    stolen = action_for(
        Attempt("openrouter/auto-beta", "openrouter", "text"),
        "MOUTH_FOREIGN",
        "json_code reused a mouth served as openai/gpt-5.6-sol",
    )
    assert stolen.sop == "foreign_mouth" and stolen.again is False
    label = action_for(
        Attempt("nvidia/nemotron-3.5-content-safety", "openrouter", "text"),
        "NOT_CODE",
        "",
    )
    assert label.sop == "not_code" and label.again is False
    missing = action_for(Attempt("minimax/minimax-m1", "openrouter", "text"), "HOST_FAIL", "")
    assert missing.sop == "unemitted" and missing.again is False
    inkling = action_for(
        Attempt("thinkingmachines/inkling:free", "opencode", "text"),
        "TASK_ASK",
        "What is the task?",
    )
    assert inkling.sop == "task_ask" and inkling.again is False
    gemma = action_for(
        Attempt("google/gemma-4-31b-it:free", "openrouter", "text"),
        "UPSTREAM_POOL",
        "Provider returned error",
    )
    assert gemma.sop == "pool_hold" and gemma.again is False
    nvidia = action_for(
        Attempt("nvidia/nemotron-3-ultra-550b-a55b:free", "openrouter", "text"),
        "UPSTREAM",
        "Upstream error from Nvidia: Internal server error",
    )
    assert nvidia.sop == "upstream" and nvidia.again is False


def test_door_catalog_resolves_a_tree_without_downloading(tmp_path: Path):
    from g47.locate import probe

    tree = tmp_path / "deepseek-harness" / "docs"
    tree.mkdir(parents=True)
    (tree / "architecture.md").write_text("x\n", encoding="utf-8")
    rows = probe(
        [{
            "id": "dsh",
            "binary": "dsh.cmd",
            "local_name": "deepseek-harness",
            "obtain": "git clone https://github.com/deepseek-ai/deepseek-harness",
            "wire_api": "",
        }],
        which=lambda _name: None,
        roots=(tmp_path,),
    )
    assert rows[0]["state"] == "found"
    assert rows[0]["local"].endswith("deepseek-harness")
    assert rows[0]["binary_found"] == ""
    missing = probe(
        [{"id": "codex", "binary": "codex", "local_name": "", "obtain": "npm install -g @openai/codex"}],
        which=lambda _name: None,
        roots=(tmp_path,),
    )
    assert missing[0]["state"] == "missing"


def test_prepare_keeps_the_caller_door():
    """Vendor doors stay choosable. prepare does not move the seat onto them."""
    from g47.loop import Attempt, action_for, prepare

    luna = prepare(Attempt("openai/gpt-6-luna:floor", "openrouter", "text"))
    assert luna.door == "openrouter"
    assert "native_door" not in luna.applied
    foreign = action_for(luna, "MOUTH_FOREIGN", "reused a mouth")
    assert foreign.sop == "foreign_mouth" and foreign.again is False
    routed = action_for(luna, "WRONG_VIA", "")
    assert routed.again is False and routed.door == "openrouter"
    glm = prepare(Attempt("z-ai/glm-5.3-flash", "cosmos-harness", "text"))
    assert glm.door == "cosmos-harness" and "native_door" not in glm.applied
    assert action_for(glm, "MIXED_VIA", "").again is False
    ink = prepare(Attempt("thinkingmachines/inkling:free", "cosmos-harness", "text"))
    assert ink.door == "cosmos-harness" and "agentic_door" not in ink.applied
    gate = action_for(ink, "HARNESS_GATE", "")
    assert gate.again is False and gate.door == "cosmos-harness"
    chosen = prepare(Attempt("thinkingmachines/inkling:free", "opencode", "text"))
    assert chosen.door == "opencode"


def test_a_claimed_seat_needs_the_served_id(tmp_path: Path):
    """The seated flag is ignored unless the served id is this pin."""
    import json

    from g47.loop import Attempt, run
    from g47.summon import process_observation, served_model

    journal = tmp_path / "seat.jsonl"
    calls: list[str] = []

    def foreign(attempt: Attempt) -> dict[str, object]:
        calls.append(attempt.pin)
        return {"seated": True, "served": "other", "mouth": "HOLD", "http": 200}

    out = run(Attempt("openai/gpt-6-luna:floor", "codex", "text"), foreign, journal=journal)
    assert calls == ["openai/gpt-6-luna:floor"]
    assert out["seated"] is False
    assert out["scar"] == "MOUTH_FOREIGN"
    assert out["sop"] == "foreign_mouth"
    assert out["turns"] == 1
    row = json.loads(journal.read_text(encoding="utf-8").splitlines()[0])
    assert row["seated"] is False
    assert row["sop"] == "foreign_mouth"

    def unbound(attempt: Attempt) -> dict[str, object]:
        calls.append("unbound")
        return {"seated": True, "served": "", "mouth": "", "http": 200}

    empty = run(Attempt("openai/gpt-6-luna:floor", "codex", "text"), unbound)
    assert empty["seated"] is False
    assert empty["scar"] == "SKU_UNBOUND"
    assert empty["turns"] == 1
    assert calls == ["openai/gpt-6-luna:floor", "unbound"]

    def matched(attempt: Attempt) -> dict[str, object]:
        calls.append("matched")
        return {"seated": True, "served": "openai/gpt-6-luna", "mouth": "HOLD", "http": 200}

    seated = run(Attempt("openai/gpt-6-luna:floor", "codex", "text"), matched)
    assert seated["seated"] is True
    assert seated["served"] == "openai/gpt-6-luna"
    assert calls == ["openai/gpt-6-luna:floor", "unbound", "matched"]

    assert served_model('{"model":"openai/gpt-6-luna"}') == "openai/gpt-6-luna"
    events = (
        '{"type":"thread.started","thread_id":"abc"}\n'
        '{"type":"turn.completed","usage":{"input_tokens":1}}\n'
    )
    assert served_model(events) == ""
    assert served_model('{"model": null}') == ""
    assert served_model('{"model": "has space"}') == ""
    assert served_model('{"model":"openai/gpt-6-luna"}\n{"model":"other"}\n') == ""
    hidden = '{"item":{"aggregated_output":"the model is openai/gpt-6-luna"}}'
    assert served_model(hidden) == ""
    observed = process_observation('{"model":"openai/gpt-6-luna"}', 0)
    assert observed["seated"] is False
    assert observed["served"] == "openai/gpt-6-luna"


def test_long_tail_stays_in_the_file_and_grok_does_not_spawn(tmp_path: Path):
    built = plan(legend(task="y" * 2000, where=str(tmp_path)), "opencode")
    assert "y" * 2000 not in " ".join(built.argv)
    assert "Complete TASK.md" in " ".join(built.argv)
    assert "yyyy" in built.files["TASK.md"]
    pi = plan(legend(model="glm-5.3-flash", wrap="role = CODER\n"), "pi")
    assert pi.argv[:6] == ["pi.cmd", "-p", "--provider", "zai", "--model", "glm-5.3-flash"]
    assert "--no-session" in pi.argv
    assert "--system-prompt" in pi.argv
    grok = plan(legend(role="CODER", model="grok-4.6", window=100_000, task="short"), "grok")
    with pytest.raises(Refuse) as exc:
        execute(grok, tmp_path)
    assert exc.value.reason == "GROK_NOT_A_WORKER"
    with pytest.raises(Refuse) as exc:
        plan(legend(task="see docs/HARNESS.md"), "opencode")
    assert exc.value.reason == "POINTER_IN_TASK"
