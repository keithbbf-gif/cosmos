"""Gate and learning-loop inbox."""

from __future__ import annotations

import hashlib
from dataclasses import fields, replace

import pytest

from cosmos_hermes import Refuse, secret_shape
from skills import (
    ALLOW_CAP,
    BODY_CAP,
    DESCRIPTION_CAP,
    GENESIS_FENCE,
    HARDLINE_MARKS,
    HARDLINE_NAMES,
    LIST_BUDGET,
    NAME_CAP,
    POLICY,
    PROPOSAL_CAP,
    SCHEMA,
    Caps,
    Proposal,
    Row,
    SkillCard,
    SkillInbox,
    rebuild,
)


def _doc(name: str, description: str, body: str = "Do the step.") -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n{body}"


def _inbox(
    allow: tuple[str, ...] | None = ("alpha",),
    flag: str | None = "flag-pen",
) -> SkillInbox:
    return SkillInbox(allow=allow, human_flag=flag)


def _only(rows: tuple[Row, ...]) -> Row:
    return rows[0]


def _only_proposal(items: tuple[Proposal, ...]) -> Proposal:
    return items[0]


def _only_active(items: tuple[SkillCard, ...]) -> SkillCard:
    return items[0]


def _flip(digest: str) -> str:
    replacement = "1" if digest[-1] == "0" else "0"
    return digest[:-1] + replacement


def _session_story() -> tuple[object, ...]:
    inbox = SkillInbox(allow=("session-note",), human_flag="flag-mina-card")
    note = _doc(
        "session-note",
        "Mina writes the session note on the card before the porch light",
        "Write the note on the card. Leave the light as it is.",
    )
    proposal = inbox.propose(note, at=1_720_000_000)
    drafted = inbox.propose_from_task(
        "File the session note on the card before the porch light",
        at=1_720_000_050,
    )
    mismatch = ""
    try:
        inbox.activate(proposal.sha, "ccr:mina", "flag-from-the-skill", at=1_720_000_080)
    except Refuse as exc:
        mismatch = exc.code
    load_code = ""
    try:
        inbox.load("session-note")
    except Refuse as exc:
        load_code = exc.code
    cards = inbox.list_skills()
    copy = rebuild(inbox.ledger(), allow=("session-note",), human_flag="flag-mina-card")
    assert proposal.state == "PROPOSED"
    assert drafted.state == "PROPOSED"
    assert drafted.name == "file-the-session-note-on-the-card-before-the-porch-light"
    assert mismatch == "FLAG_MISMATCH"
    assert load_code == "NOT_FOUND"
    assert cards == ()
    assert copy.ledger() == inbox.ledger()
    assert copy.list_skills() == ()
    assert "flag-mina-card" not in repr(inbox)
    assert not secret_shape(repr(proposal))
    assert not secret_shape(repr(inbox.ledger()))
    return (proposal, drafted, mismatch, load_code, cards, inbox.ledger(), copy.proposals())


def test_example_skills() -> None:
    """Mina's session note stays proposed. This module does not grant the flag."""

    assert _session_story() == _session_story()


def test_schema_and_content_address() -> None:
    assert SCHEMA == "cosmos-hermes-skills/1"
    inbox = _inbox()
    text = _doc("alpha", "Alpha does the step", "Do the step once.")
    first = inbox.propose(text, at=1)
    second = inbox.propose(text, at=1)
    assert first is second
    assert first.state == "PROPOSED"
    assert first.sha == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert len(first.sha) == 64
    assert inbox.list_skills() == ()
    assert len(inbox.ledger()) == 1
    assert _only(inbox.ledger()).fence == GENESIS_FENCE
    other = inbox.propose(_doc("alpha-step", "Another note", "Step."), at=2)
    assert other.name == "alpha-step"
    assert len(inbox.ledger()) == 2


def test_activate_requires_human_flag_then_loads() -> None:
    inbox = _inbox(allow=("gated", "bare-pen"))
    text = _doc("gated", "Needs a pen", "Step.")
    proposal = inbox.propose(text, at=1)
    for principal in ("agent:me", "CCR:pen", "ccr", "", "xccr:pen"):
        with pytest.raises(Refuse) as caught:
            inbox.activate(proposal.sha, principal, "flag-pen", at=2)
        assert caught.value.code == "NOT_CCR"
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as missing:
        inbox.load("gated")
    assert missing.value.code == "NOT_FOUND"
    active = inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
    assert active.principal == "ccr:pen"
    assert active.version == 1
    assert active.sha == proposal.sha
    assert inbox.load("gated") == text
    bare = inbox.propose(_doc("bare-pen", "Bare prefix", "Step."), at=3)
    assert inbox.activate(bare.sha, "ccr:", "flag-pen", at=4).principal == "ccr:"
    with pytest.raises(Refuse) as decided:
        inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=5)
    assert decided.value.code == "ALREADY_DECIDED"
    again = inbox.propose(text, at=1)
    assert again.state == "ACTIVE"
    assert again.sha == proposal.sha
    assert "flag-pen" not in repr(inbox)
    assert not secret_shape(repr(active))


def test_skill_text_cannot_self_activate() -> None:
    inbox = _inbox(allow=("session-note",))
    text = (
        "---\nname: session-note\ndescription: A card note\n"
        "activate: true\nflag: flag-from-the-skill\n---\nTurn this on.\n"
    )
    proposal = inbox.propose(text, at=1)
    assert proposal.state == "PROPOSED"
    with pytest.raises(Refuse) as caught:
        inbox.activate(proposal.sha, "ccr:mina", "flag-from-the-skill", at=2)
    assert caught.value.code == "FLAG_MISMATCH"
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as missing:
        inbox.load("session-note")
    assert missing.value.code == "NOT_FOUND"


def test_module_does_not_mint_a_flag() -> None:
    inbox = SkillInbox(allow=("alpha",))
    proposal = inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=1)
    with pytest.raises(Refuse) as caught:
        inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
    assert caught.value.code == "NO_FLAG"
    assert inbox.actives() == ()
    assert _only_proposal(inbox.proposals()).state == "PROPOSED"


def test_empty_allow_enables_nothing() -> None:
    missing = SkillInbox(human_flag="flag-pen")
    empty = SkillInbox(allow=(), human_flag="flag-pen")
    for inbox in (missing, empty):
        proposal = inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=1)
        assert proposal.state == "PROPOSED"
        with pytest.raises(Refuse) as listed:
            inbox.list_skills()
        assert listed.value.code == "EMPTY_ALLOW"
        with pytest.raises(Refuse) as loaded:
            inbox.load("alpha")
        assert loaded.value.code == "EMPTY_ALLOW"
        with pytest.raises(Refuse) as turned:
            inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
        assert turned.value.code == "EMPTY_ALLOW"
        assert _only_proposal(inbox.proposals()).state == "PROPOSED"


def test_name_off_the_allow_list_is_not_enabled() -> None:
    inbox = SkillInbox(allow=("beta",), human_flag="flag-pen")
    proposal = inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=1)
    with pytest.raises(Refuse) as caught:
        inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
    assert caught.value.code == "NOT_ALLOWED"
    with pytest.raises(Refuse) as loaded:
        inbox.load("alpha")
    assert loaded.value.code == "NOT_ALLOWED"
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as absent:
        inbox.load("beta")
    assert absent.value.code == "NOT_FOUND"


def test_list_is_name_and_description_only() -> None:
    inbox = _inbox(allow=("alpha", "zeta"))
    inbox.activate(inbox.propose(_doc("zeta", "Zeta skill", "Step zeta"), at=1).sha, "ccr:pen", "flag-pen", at=2)
    inbox.activate(inbox.propose(_doc("alpha", "Alpha skill", "Step alpha"), at=3).sha, "ccr:pen", "flag-pen", at=4)
    cards = inbox.list_skills()
    assert cards == (
        SkillCard("alpha", "Alpha skill"),
        SkillCard("zeta", "Zeta skill"),
    )
    shown = _only_active(cards)
    assert {item.name for item in fields(shown)} == {"name", "description"}
    assert "Step zeta" not in repr(cards)
    assert not secret_shape(repr(cards))
    assert not secret_shape(repr(inbox.caps))
    assert inbox.actives()[0].name == "alpha"


def test_list_skips_a_card_that_does_not_fit() -> None:
    inbox = SkillInbox(
        allow=("alpha", "mid-card", "zeta"),
        human_flag="flag-pen",
        list_budget=20,
    )
    specs = (("alpha", "short"), ("mid-card", "m" * 30), ("zeta", "z"))
    moment = 1
    for name, description in specs:
        proposal = inbox.propose(_doc(name, description, "Step."), at=moment)
        moment += 1
        inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=moment)
        moment += 1
    assert inbox.list_budget == 20
    assert inbox.requested_list_budget == 20
    expected = (SkillCard("alpha", "short"), SkillCard("zeta", "z"))
    assert inbox.list_skills() == expected
    assert inbox.list_skills(budget=10_000) == expected
    assert inbox.list_skills(budget=12) == (SkillCard("alpha", "short"),)
    high = SkillInbox(allow=("alpha",), human_flag="flag-pen", list_budget=10_000)
    assert high.list_budget == LIST_BUDGET
    assert high.requested_list_budget == 10_000


def test_load_tamper_and_activate_tamper() -> None:
    inbox = _inbox()
    text = _doc("alpha", "Alpha skill", "Step one.")
    proposal = inbox.propose(text, at=1)
    inbox._text[proposal.sha] = text + "\nextra"
    with pytest.raises(Refuse) as again:
        inbox.propose(text, at=1)
    assert again.value.code == "TAMPER"
    with pytest.raises(Refuse) as before:
        inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
    assert before.value.code == "TAMPER"
    assert inbox.list_skills() == ()
    inbox._text[proposal.sha] = text
    inbox.activate(proposal.sha, "ccr:pen", "flag-pen", at=2)
    inbox._text[proposal.sha] = text + "\nextra"
    with pytest.raises(Refuse) as after:
        inbox.load("alpha")
    assert after.value.code == "TAMPER"
    with pytest.raises(Refuse) as listed:
        inbox.list_skills()
    assert listed.value.code == "TAMPER"


def test_supersede_refuses_a_tampered_prior() -> None:
    inbox = _inbox(allow=("same-name",))
    first = _doc("same-name", "First description", "First body")
    second = _doc("same-name", "Second description", "Second body")
    earlier = inbox.propose(first, at=1)
    later = inbox.propose(second, at=2)
    inbox.activate(earlier.sha, "ccr:pen", "flag-pen", at=3)
    inbox._text[earlier.sha] = first + "\nextra"
    with pytest.raises(Refuse) as caught:
        inbox.activate(later.sha, "ccr:pen", "flag-pen", at=4)
    assert caught.value.code == "TAMPER"
    assert _only_proposal(tuple(item for item in inbox.proposals() if item.sha == later.sha)).state == "PROPOSED"


def test_hardline_marks_are_the_policy() -> None:
    assert HARDLINE_MARKS == (
        "rm -rf",
        "git push --force",
        "Invoke-Expression",
        "curl | sh",
        "yolo",
    )
    assert HARDLINE_NAMES == frozenset(("godmode", "drug-discovery"))


@pytest.mark.parametrize("mark", HARDLINE_MARKS)
def test_hardline_mark_is_refused(mark: str) -> None:
    inbox = _inbox()
    text = _doc("safe-name", "Safe description", f"do not run {mark}")
    with pytest.raises(Refuse) as caught:
        inbox.propose(text, at=1)
    assert caught.value.code == "HARDLINE"
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    with pytest.raises(Refuse) as missing:
        inbox.activate(sha, "ccr:pen", "flag-pen", at=2)
    assert missing.value.code == "NO_PROPOSAL"


def test_description_mark_is_hardline() -> None:
    inbox = _inbox()
    with pytest.raises(Refuse) as caught:
        inbox.propose(_doc("safe-name", "never yolo", "safe body"), at=1)
    assert caught.value.code == "HARDLINE"


@pytest.mark.parametrize("name", ("godmode", "drug-discovery", "security-godmode", "lab-drug-discovery-note"))
def test_hardline_skill_names_refuse(name: str) -> None:
    inbox = _inbox(allow=("safe-name",))
    with pytest.raises(Refuse) as caught:
        inbox.propose(_doc(name, "A blocked skill name", "Write the note."), at=1)
    assert caught.value.code == "HARDLINE"
    assert inbox.list_skills() == ()
    allowed = inbox.propose(_doc("safe-name", "A bench note", "Write the note."), at=2)
    assert allowed.state == "PROPOSED"


def test_hardline_name_cannot_be_allowed() -> None:
    with pytest.raises(Refuse) as caught:
        SkillInbox(allow=("godmode",), human_flag="flag-pen")
    assert caught.value.code == "HARDLINE"
    with pytest.raises(Refuse) as lesson:
        _inbox().propose_from_task("drug-discovery", at=1)
    assert lesson.value.code == "HARDLINE"


@pytest.mark.parametrize(
    "payload",
    (
        "sk-livekeyvalue",
        "Authorization: Bearer abcdefghijk",
        "api_key=supersecret",
    ),
)
def test_secret_shape_is_hardline(payload: str) -> None:
    inbox = _inbox()
    text = _doc("safe-name", "Safe description", f"prefix {payload} suffix")
    with pytest.raises(Refuse) as caught:
        inbox.propose(text, at=1)
    assert caught.value.code == "HARDLINE"
    assert payload not in str(caught.value)
    assert not secret_shape(str(caught.value))
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    with pytest.raises(Refuse) as missing:
        inbox.activate(sha, "ccr:pen", "flag-pen", at=2)
    assert missing.value.code == "NO_PROPOSAL"


def test_secret_principal_and_flag_are_hardline() -> None:
    inbox = _inbox()
    proposal = inbox.propose(_doc("alpha", "Safe description", "Step."), at=1)
    with pytest.raises(Refuse) as caught:
        inbox.activate(proposal.sha, "ccr:sk-livekeyvalue", "flag-pen", at=2)
    assert caught.value.code == "HARDLINE"
    assert "sk-livekeyvalue" not in str(caught.value)
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as flagged:
        SkillInbox(allow=("alpha",), human_flag="sk-livekeyvalue")
    assert flagged.value.code == "HARDLINE"


def test_bad_skill_shapes() -> None:
    inbox = _inbox()
    samples = (
        "no fence here",
        "---\nname: ab\ndescription: hi\n",
        _doc("Bad", "Upper name", "x"),
        _doc("a--b", "Double hyphen", "x"),
        _doc("-leading", "Leading hyphen", "x"),
        "---\nname: dup\nname: dup\ndescription: Twice\n---\nBody\n",
        "---\nname: nest\ndescription: Nested\nmeta:\n  child: no\n---\nBody\n",
        "---\nname: missing-desc\n---\nBody\n",
        '---\nname: quoted\ndescription: ""\n---\nBody\n',
        "---\nname: ab\nnot-a-pair\ndescription: hi\n---\nBody\n",
    )
    moment = 1
    for text in samples:
        with pytest.raises(Refuse) as caught:
            inbox.propose(text, at=moment)
        assert caught.value.code == "BAD_SKILL"
        moment += 1
    quoted = '---\nname: "quoted-name"\ndescription: "Says hello"\n---\nBody\n'
    parsed = inbox.propose(quoted, at=moment)
    assert parsed.name == "quoted-name"
    assert parsed.description == "Says hello"
    crlf = "---\r\nname: crlf-name\r\ndescription: Windows lines\r\n---\r\nDo the step.\r\n"
    assert inbox.propose(crlf, at=moment + 1).name == "crlf-name"
    commented = "---\n# comment\nname: commented\n\ndescription: Has a comment\n---\nBody\n"
    assert inbox.propose(commented, at=moment + 2).name == "commented"


def test_not_text_null_bad_sha_and_missing() -> None:
    inbox = _inbox()
    with pytest.raises(Refuse) as kind:
        inbox.propose(b"---", at=1)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        inbox.propose("ab\x00", at=1)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as surrogate:
        inbox.propose("\ud800", at=1)
    assert surrogate.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as principal:
        inbox.activate("ab" * 32, None, "flag-pen", at=1)
    assert principal.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as bad:
        inbox.activate("abcd", "ccr:pen", "flag-pen", at=1)
    assert bad.value.code == "BAD_SHA"
    with pytest.raises(Refuse) as upper:
        inbox.activate("AB" * 32, "ccr:pen", "flag-pen", at=1)
    assert upper.value.code == "BAD_SHA"
    with pytest.raises(Refuse) as missing:
        inbox.activate("ab" * 32, "ccr:pen", "flag-pen", at=1)
    assert missing.value.code == "NO_PROPOSAL"
    with pytest.raises(Refuse) as denied:
        inbox.activate("nope", "agent:other", None, None)
    assert denied.value.code == "NOT_CCR"
    with pytest.raises(Refuse) as flag:
        inbox.activate("ab" * 32, "ccr:pen", "Not A Flag", at=1)
    assert flag.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as shaped:
        SkillInbox(allow=("alpha",), human_flag="")
    assert shaped.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as allow:
        SkillInbox(allow="alpha", human_flag="flag-pen")
    assert allow.value.code == "NOT_LIST"
    with pytest.raises(Refuse) as blank:
        SkillInbox(allow=("",), human_flag="flag-pen")
    assert blank.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as clock:
        inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=True)
    assert clock.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=-1)
    assert low.value.code == "OUT_OF_RANGE"


def test_clock_and_duplicate_allow() -> None:
    inbox = _inbox()
    inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=5)
    with pytest.raises(Refuse) as caught:
        inbox.propose(_doc("alpha-step", "Next note", "Step."), at=5)
    assert caught.value.code == "CLOCK"
    assert len(inbox.ledger()) == 1
    with pytest.raises(Refuse) as duplicate:
        SkillInbox(allow=("alpha", "alpha"), human_flag="flag-pen")
    assert duplicate.value.code == "DUPLICATE"


def test_caps_are_policy() -> None:
    inbox = SkillInbox(
        allow=("a", "ok-name", "abcd"),
        human_flag="flag-pen",
        name_cap=10_000,
        description_cap=50_000,
        body_cap=9_000_000,
    )
    assert inbox.caps == Caps(NAME_CAP, DESCRIPTION_CAP, BODY_CAP, 10_000, 50_000, 9_000_000)
    assert inbox.caps.name == NAME_CAP
    assert inbox.caps.requested_body == 9_000_000
    with pytest.raises(Refuse) as name:
        inbox.propose(_doc("n" * (NAME_CAP + 1), "ok", "x"), at=1)
    assert name.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as desc:
        inbox.propose(_doc("ok-name", "d" * (DESCRIPTION_CAP + 1), "x"), at=1)
    assert desc.value.code == "BAD_SKILL"
    prefix = _doc("a", "b", "")
    exact = _doc("a", "b", "x" * (BODY_CAP - len(prefix)))
    assert len(exact) == BODY_CAP
    stored = inbox.propose(exact, at=1)
    assert stored.sha == hashlib.sha256(exact.encode("utf-8")).hexdigest()
    with pytest.raises(Refuse) as body:
        inbox.propose(exact + "y", at=2)
    assert body.value.code == "OVERSIZE"
    tight = SkillInbox(allow=("abcd",), human_flag="flag-pen", name_cap=4, description_cap=8, body_cap=80)
    assert (tight.caps.name, tight.caps.description, tight.caps.body) == (4, 8, 80)
    assert tight.propose(_doc("abcd", "ok", "x"), at=1).name == "abcd"
    with pytest.raises(Refuse) as tight_name:
        tight.propose(_doc("abcde", "ok", "x"), at=2)
    assert tight_name.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as tight_desc:
        tight.propose(_doc("abcd", "123456789", "x"), at=2)
    assert tight_desc.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as tight_body:
        tight.propose(_doc("abcd", "ok", "y" * 80), at=2)
    assert tight_body.value.code == "OVERSIZE"
    names = tuple(f"n{index}" for index in range(ALLOW_CAP + 1))
    with pytest.raises(Refuse) as wide:
        SkillInbox(allow=names, human_flag="flag-pen")
    assert wide.value.code == "OVERSIZE"
    assert POLICY.name == NAME_CAP
    assert POLICY.requested_name == NAME_CAP


def test_bad_limit() -> None:
    with pytest.raises(Refuse) as zero:
        SkillInbox(allow=("alpha",), name_cap=0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flag:
        SkillInbox(allow=("alpha",), body_cap=True)
    assert flag.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as fraction:
        SkillInbox(allow=("alpha",), description_cap=1.5)
    assert fraction.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as budget:
        SkillInbox(allow=("alpha",), human_flag="flag-pen", list_budget=True)
    assert budget.value.code == "BAD_LIMIT"
    inbox = _inbox()
    inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=1)
    inbox.activate(inbox.proposals()[0].sha, "ccr:pen", "flag-pen", at=2)
    with pytest.raises(Refuse) as listed:
        inbox.list_skills(budget=0)
    assert listed.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as direct:
        Caps(0, 1, 1, 0, 1, 1)
    assert direct.value.code == "BAD_LIMIT"


def test_proposal_cap() -> None:
    inbox = SkillInbox(allow=("n0",), human_flag="flag-pen")
    for index in range(PROPOSAL_CAP):
        inbox.propose(_doc(f"n{index}", "Note", "Step."), at=index + 1)
    with pytest.raises(Refuse) as caught:
        inbox.propose(_doc("overflow", "Note", "Step."), at=PROPOSAL_CAP + 1)
    assert caught.value.code == "FULL"
    again = inbox.propose(_doc("n0", "Note", "Step."), at=1)
    assert again.name == "n0"
    assert len(inbox.ledger()) == PROPOSAL_CAP


def test_propose_from_task_never_activates() -> None:
    inbox = _inbox(allow=("check-the-ledger-before-writing",))
    proposal = inbox.propose_from_task("  Check the ledger before writing  ", at=1)
    assert proposal.state == "PROPOSED"
    assert proposal.name == "check-the-ledger-before-writing"
    assert proposal.description == "Check the ledger before writing"
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as missing:
        inbox.load(proposal.name)
    assert missing.value.code == "NOT_FOUND"
    again = inbox.propose_from_task("Check the ledger before writing", at=1)
    assert again is proposal
    active = inbox.activate(proposal.sha, "ccr:reviewer", "flag-pen", at=2)
    assert active.version == 1
    loaded = inbox.load(proposal.name)
    assert proposal.sha == hashlib.sha256(loaded.encode("utf-8")).hexdigest()
    assert "Check the ledger before writing" in loaded
    assert not secret_shape(repr(proposal))
    assert not secret_shape(repr(active))


def test_propose_from_task_refuses_bad_lessons() -> None:
    inbox = _inbox()
    with pytest.raises(Refuse) as blank:
        inbox.propose_from_task("   ", at=1)
    assert blank.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as broken:
        inbox.propose_from_task("line\nmore", at=1)
    assert broken.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as unnamed:
        inbox.propose_from_task("???", at=1)
    assert unnamed.value.code == "BAD_SKILL"
    with pytest.raises(Refuse) as hardline:
        inbox.propose_from_task("please yolo the deploy", at=1)
    assert hardline.value.code == "HARDLINE"
    assert inbox.list_skills() == ()
    with pytest.raises(Refuse) as kind:
        inbox.propose_from_task(12, at=1)
    assert kind.value.code == "NOT_TEXT"
    tiny = SkillInbox(allow=("alpha",), human_flag="flag-pen", body_cap=20, description_cap=100)
    with pytest.raises(Refuse) as over:
        tiny.propose_from_task("Check ledger", at=1)
    assert over.value.code == "OVERSIZE"


def test_supersede_bumps_version_and_rebuilds() -> None:
    allow = ("same-name",)
    flag = "flag-pen"
    inbox = SkillInbox(allow=allow, human_flag=flag)
    first = _doc("same-name", "First description", "First body")
    second = _doc("same-name", "Second description", "Second body")
    earlier = inbox.propose(first, at=1)
    later = inbox.propose(second, at=2)
    one = inbox.activate(earlier.sha, "ccr:pen", flag, at=3)
    two = inbox.activate(later.sha, "ccr:pen", flag, at=4)
    assert one.version == 1
    assert two.version == 2
    assert inbox.load("same-name") == second
    assert inbox.list_skills() == (SkillCard("same-name", "Second description"),)
    with pytest.raises(Refuse) as caught:
        inbox.activate(earlier.sha, "ccr:pen", flag, at=5)
    assert caught.value.code == "ALREADY_DECIDED"
    copy = rebuild(inbox.ledger(), allow=allow, human_flag=flag)
    assert copy.ledger() == inbox.ledger()
    assert copy.load("same-name") == second
    assert copy.list_skills() == inbox.list_skills()
    assert {item.state for item in copy.proposals()} == {"ACTIVE", "SUPERSEDED"}
    assert copy.actives()[0].version == 2
    with pytest.raises(Refuse) as replayed:
        copy.activate(earlier.sha, "ccr:pen", flag, at=5)
    assert replayed.value.code == "ALREADY_DECIDED"


def test_chain_refuses_stale_duplicate_and_broken_rows() -> None:
    inbox = _inbox()
    inbox.propose(_doc("alpha", "Alpha skill", "Step."), at=10)
    good = _only(inbox.ledger())
    stale = replace(good, fence="f" * 64)
    with pytest.raises(Refuse) as fence:
        rebuild((stale,), allow=("alpha",), human_flag="flag-pen")
    assert fence.value.code == "STALE_FENCE"
    broken = replace(good, digest=_flip(good.digest))
    with pytest.raises(Refuse) as chain:
        rebuild((broken,), allow=("alpha",), human_flag="flag-pen")
    assert chain.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as duplicate:
        rebuild((good, replace(good, seq=2)), allow=("alpha",), human_flag="flag-pen")
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as gap:
        rebuild((replace(good, seq=2),), allow=("alpha",), human_flag="flag-pen")
    assert gap.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as record:
        rebuild(("x",), allow=("alpha",), human_flag="flag-pen")
    assert record.value.code == "BAD_RECORD"
    blob = (good,) * (PROPOSAL_CAP * 2 + 1)
    with pytest.raises(Refuse) as over:
        rebuild(blob, allow=("alpha",), human_flag="flag-pen")
    assert over.value.code == "OVERSIZE"
