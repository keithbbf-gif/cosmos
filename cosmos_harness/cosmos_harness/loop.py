"""The attempt loop. Same inputs, same halt.

A turn is one model sample plus the hands that sample named. The sample is
the unbound step. Everything around it is a hook:

- turn cap is 8
- a refused hand sets the latch
- an edit whose old text is already gone, after a patch landed, asks once
  for a closing line and does not latch
- a repeated read, glob, or grep returns the short "already returned" line
- the latch is not cleared on the next turn, on a token-budget continuation,
  or after a stop
- a seating SOP that already fired does not fire again
- the pin on the sample must be the stack pin
- tool debt is the calls in this sample; each one is answered or the turn
  halts with ``ORPHANED_DEBT``
- a provider scar that also carries tool calls is debt, not a dropped sample
- after an act-mode sample returns no hands, the oracle must be green and
  the four checkers must be PASS
- a plan-mode sample with no hands closes on a legal first line. Plan
  cannot edit, so that review is a verdict, not a coding bundle

There is no ``while true``. The range is ``range(1, TURN_CAP + 1)``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from cosmos_harness.bundle import DoneBundle, make
from cosmos_harness.hooks import (
    done,
    post_tool,
    pre_tool,
    prompt_bound,
    prompt_in,
    seat_scar,
    stop,
    verify,
)
from cosmos_harness.layers import TURN_CAP, Stack, bind
from cosmos_harness.learn import step as seat_step
from cosmos_harness.oracle import Oracle
from cosmos_harness.refuse import Refuse
from cosmos_harness.tools import Hands, execute


@dataclass(frozen=True)
class ToolCall:
    """One hand the sample asked for. ``args`` is a JSON object, not a shell line."""

    call_id: str
    name: str
    args: dict[str, object]


@dataclass(frozen=True)
class Sample:
    """One model response. ``model`` must equal the pin. The text is not done."""

    model: str
    text: str
    calls: tuple[ToolCall, ...] = ()
    provider_detail: str = ""
    provider_http: int | None = None


class Driver:
    """The only place a model is asked to speak. Tests pass a script."""

    def sample(self, messages: tuple[str, ...]) -> Sample:
        raise Refuse("NO_DRIVER", "sample")


@dataclass(frozen=True)
class Halt:
    """The terminal record. Two runs with the same script produce equal halts."""

    state: str
    turns: int
    reason: str
    trace: tuple[str, ...]
    latch: bool
    bundle: dict[str, str] | None


def _trace(trace: list[str], hook: str, reason: str) -> None:
    trace.append(f"{hook}:{reason}")


def _verdict_line(text: str, allowed: tuple[str, ...] = ()) -> str:
    """The first non-empty line, with one matching pair of backticks removed.

    A legal token glued to its sentence still counts, including a period
    or colon glued on. Longer tokens are tried first, so ``diff --git``
    is kept ahead of a shorter prefix.
    """
    line = ""
    for raw in (text or "").splitlines():
        candidate = raw.strip()
        if len(candidate) >= 2 and candidate[0] == candidate[-1] == "`":
            candidate = candidate[1:-1].strip()
        if candidate.startswith(("- ", "* ")):
            candidate = candidate[2:].strip()
        if candidate.startswith("**"):
            end = candidate.find("**", 2)
            if end != -1:
                inner = candidate[2:end].strip()
                tail = candidate[end + 2:].lstrip(" \t")
                if inner:
                    candidate = inner if not tail else inner + " " + tail
        if candidate:
            line = candidate
            break
    if not line or line in allowed:
        return line
    for token in sorted(allowed, key=len, reverse=True):
        if line.startswith(token) and (
            len(line) == len(token) or line[len(token)] in " \t.,:;"
        ):
            return token
    return line


def run(
    stack: Stack,
    driver: Driver,
    oracle: Oracle,
    hands: Hands,
    *,
    pack_dir,
    checks: tuple[str, ...] | None = None,
    grade=None,
) -> Halt:
    """Drive one attempt to a terminal state.

    ``grade``, when passed, replaces the checker runner. The default runner
    is ``checks.grade``. A test passes four ``PASS`` rows. A missing checker
    is still ``UNAVAILABLE`` on the default path.
    """
    from g47.contracts import FIRST_LINE
    from g47.scars import same_pin

    from cosmos_harness.checks import grade as grade_python

    trace: list[str] = []
    try:
        stack = bind(stack)
    except Refuse as exc:
        _trace(trace, "prompt_bound", exc.reason)
        return Halt(exc.reason, 0, exc.reason, tuple(trace), True, None)
    if hands.jail.root != stack.where or hands.mode != stack.mode:
        _trace(trace, "prompt_bound", "HAND_BINDING")
        return Halt("HAND_BINDING", 0, "HAND_BINDING", tuple(trace), True, None)
    door = prompt_in(stack)
    _trace(trace, door.hook, door.reason)
    if not door.allow:
        return Halt(door.reason, 0, door.reason, tuple(trace), True, None)
    bound = prompt_bound(stack)
    _trace(trace, bound.hook, bound.reason)
    if not bound.allow:
        return Halt(bound.reason, 0, bound.reason, tuple(trace), True, None)

    try:
        oracle.prove_red()
    except Refuse as exc:
        _trace(trace, "verify", exc.reason)
        return Halt(exc.reason, 0, exc.reason, tuple(trace), True, None)
    hands.oracle_red = True
    messages: list[str] = [stack.wrap, stack.contract_line(), stack.task]
    latch = False
    latch_reason = ""
    turns = 0
    held_sop = ""
    mouth = ""
    journal = pack_dir / "seat.jsonl"
    repeated: set[str] = set()
    reminded = 0

    for turn in range(1, TURN_CAP + 1):
        turns = turn
        if latch:
            break
        sample = driver.sample(tuple(messages))
        mouth = sample.text
        messages.append(sample.text)
        if sample.provider_detail or sample.provider_http is not None:
            if sample.calls:
                # The scar and the calls are one sample. Dropping the calls
                # would hide debt. Running them would edit under a scar.
                gate = stop(debt=len(sample.calls), latch=False, sop_applied=False)
                _trace(trace, gate.hook, gate.reason)
                return Halt(gate.reason, turns, gate.reason, tuple(trace), True, None)
            # One scar, one journal line, then at most one confirming sample.
            # An empty error model stays on this path so it is classified
            # before the pin check.
            taken = seat_step(
                stack.model,
                http=sample.provider_http,
                detail=sample.provider_detail,
                mouth=sample.text,
                served=sample.model or None,
                applied=(held_sop,) if held_sop else (),
                door=stack.door,
                journal=journal,
            )
            decision = seat_scar(again=taken.again, sop=taken.sop)
            _trace(trace, decision.hook, decision.reason)
            if not decision.allow or held_sop:
                return Halt(taken.sop or decision.reason, turns, taken.reason, tuple(trace), not decision.allow, None)
            held_sop = taken.sop
            messages.append(f"SOP {taken.sop} shape {taken.shape}")
            continue
        if not same_pin(stack.model, sample.model):
            _trace(trace, "stop", "PIN_SWAP")
            return Halt("PIN_SWAP", turns, "PIN_SWAP", tuple(trace), True, None)
        if not sample.calls:
            gate = stop(debt=0, latch=latch, sop_applied=False)
            _trace(trace, gate.hook, gate.reason)
            break
        for call in sample.calls:
            decision = pre_tool(call.name, mode=hands.mode, oracle_red=hands.oracle_red)
            _trace(trace, decision.hook, decision.reason)
            if not decision.allow:
                latch = True
                latch_reason = decision.reason
                messages.append(f"{call.call_id} {decision.reason}")
                break
            signature = call.name + "\n" + json.dumps(call.args, sort_keys=True, default=str)
            if call.name in {"read", "glob", "grep"} and signature in repeated:
                _trace(trace, "post_tool", "already_returned")
                messages.append(f"{call.call_id} already returned. Do not repeat this call.")
                continue
            try:
                result = execute(hands, call.name, call.args)
            except Refuse as exc:
                # The old text is gone because an earlier edit landed.
                # One reminder, then the model can close. A second miss latches.
                if exc.reason == "EDIT_NOT_UNIQUE" and exc.detail == "0" and hands.patches and reminded < 2:
                    reminded += 1
                    _trace(trace, "post_tool", "already_applied")
                    messages.append(
                        f"{call.call_id} already applied. Next reply first line NONE. Do not call a tool."
                    )
                    continue
                held = post_tool(False, exc.reason)
                _trace(trace, held.hook, held.reason)
                latch = True
                latch_reason = exc.reason
                messages.append(f"{call.call_id} {exc.reason}")
                break
            repeated.add(signature)
            recorded = post_tool(result.ok, result.name)
            _trace(trace, recorded.hook, recorded.reason)
            messages.append(f"{call.call_id} {result.text}")
        else:
            continue
        break
    else:
        gate = stop(debt=0, latch=False, sop_applied=False)
        _trace(trace, gate.hook, "HALT_MAX_TURNS")
        return Halt("HALT_MAX_TURNS", turns, "HALT_MAX_TURNS", tuple(trace), False, None)

    if latch and not hands.patches:
        # A refused hand that never changed the tree stops here.
        # A refused hand after a landed edit still gets graded below.
        gate = stop(debt=0, latch=True, sop_applied=False)
        _trace(trace, gate.hook, gate.reason)
        return Halt("HALT_GUARD_HELD", turns, latch_reason, tuple(trace), True, None)

    if stack.mode == "plan":
        # Plan cannot edit, so the coding oracle cannot turn green. The
        # review closes on the role's first line. It is not a DONE bundle.
        allowed = FIRST_LINE.get(stack.role, ())
        line = _verdict_line(mouth, allowed)
        if line not in allowed:
            _trace(trace, "done", "FIRST_LINE")
            return Halt("FIRST_LINE", turns, line or "EMPTY", tuple(trace), True, None)
        _trace(trace, "done", line)
        return Halt("VERDICT", turns, line, tuple(trace), False, None)

    try:
        green = oracle.prove_green()
    except Refuse as exc:
        _trace(trace, "verify", exc.reason)
        return Halt("GATE_FAILED", turns, exc.reason, tuple(trace), True, None)
    if checks is None:
        rows = grade(stack.where) if grade is not None else grade_python(stack.where)
        checks = tuple(row["status"] for row in rows)
    verdict = verify(oracle_green=green.ok, checks=checks)
    _trace(trace, verdict.hook, verdict.reason)
    if not verdict.allow:
        return Halt("GATE_FAILED", turns, verdict.reason, tuple(trace), True, None)
    bundle: DoneBundle = make(
        patches=list(hands.patches),
        oracle_argv=oracle.argv,
        oracle_log_hash=green.log_hash,
        pack_dir=pack_dir,
    )
    final = done(bundle.as_dict())
    _trace(trace, final.hook, final.reason)
    if not final.allow:
        return Halt("INCOMPLETE_BUNDLE", turns, final.reason, tuple(trace), True, None)
    return Halt("DONE", turns, "bundle", tuple(trace), False, bundle.as_dict())
