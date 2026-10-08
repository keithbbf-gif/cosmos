"""Refusal and success coverage for file_terminal."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from cosmos_hermes import PathJail, Refuse, secret_shape
from file_terminal import (
    ARGV_CAP,
    POLICY_TIMEOUT_S,
    READ_CAP,
    SCHEMA,
    WIPE_BACKENDS,
    ExecuteHold,
    PatchResult,
    ReadText,
    TerminalRequest,
    WipeProof,
    execute,
    patch,
    read_text,
    terminal,
)


@contextmanager
def _root() -> Iterator[Path]:
    folder = Path(tempfile.mkdtemp(prefix="file_terminal_"))
    try:
        yield folder
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def refused(exc: object) -> Refuse:
    assert isinstance(exc, Refuse)
    assert secret_shape(str(exc)) is False
    assert secret_shape(repr(exc)) is False
    return exc


def _code(run: Callable[[], object]) -> str:
    try:
        run()
    except Refuse as exc:
        refused(exc)
        return exc.code
    raise AssertionError("expected Refuse")


def _jail(folder: Path) -> tuple[PathJail, Path]:
    grant = folder / "grant"
    grant.mkdir()
    return PathJail([str(grant)]), grant


def _abs_note(folder: Path) -> str:
    return str((folder / "lamp-card.txt").resolve())


def test_read_patch_and_terminal_success() -> None:
    with _root() as folder:
        jail, grant = _jail(folder)
        target = grant / "note.txt"
        raw = b"alpha beta alpha\r\n"
        target.write_bytes(raw)
        loaded = read_text(jail, str(target))
        assert loaded == read_text(jail, str(target))
        assert loaded.text == "alpha beta alpha\r\n"
        assert loaded.byte_len == len(raw)
        assert loaded.cap == READ_CAP
        assert loaded.policy_cap == READ_CAP
        assert loaded.schema == SCHEMA
        assert loaded.path == str(target.resolve())
        assert secret_shape(repr(loaded)) is False
        edited = patch(loaded.text, "beta", "gamma")
        assert edited.text == "alpha gamma alpha\r\n"
        assert edited.replacements == 1
        assert edited.schema == SCHEMA
        assert target.read_bytes() == raw
        assert patch("only", "only", "").text == ""
        assert patch("zza-end", "zz", "b").text == "ba-end"
        assert secret_shape(repr(edited)) is False
        request = terminal(["missing-binary-not-run", "arg"])
        assert request.code == "NEED_APPROVAL"
        assert request.argv == ("missing-binary-not-run", "arg")
        assert request.schema == SCHEMA
        assert secret_shape(repr(request)) is False
        again = terminal(["missing-binary-not-run", "arg"])
        assert again == request
        with pytest.raises(AttributeError):
            setattr(request, "code", "RUN")
        empty = grant / "empty.txt"
        empty.write_bytes(b"")
        blank = read_text(jail, str(empty))
        assert blank.text == ""
        assert blank.byte_len == 0


def test_read_cap_policy() -> None:
    with _root() as folder:
        jail, grant = _jail(folder)
        target = grant / "capped.txt"
        target.write_bytes(b"a" * READ_CAP)
        held = read_text(jail, str(target), 10**18)
        assert held.byte_len == READ_CAP
        assert held.cap == READ_CAP
        assert held.policy_cap == READ_CAP
        assert held.text == "a" * READ_CAP
        target.write_bytes(b"b" * (READ_CAP + 1))
        with pytest.raises(Refuse) as over:
            read_text(jail, str(target), 10**18)
        assert refused(over.value).code == "OVERSIZE"
        assert refused(over.value).detail == str(READ_CAP)
        target.write_bytes("é".encode("utf-8") + b"ok")
        small = read_text(jail, str(target), 4)
        assert small.cap == 4
        assert small.policy_cap == READ_CAP
        assert small.byte_len == 4
        assert small.text == "éok"
        target.write_bytes(b"abcdef")
        with pytest.raises(Refuse) as tight:
            read_text(jail, str(target), 5)
        assert refused(tight.value).code == "OVERSIZE"
        assert refused(tight.value).detail == "5"


def test_read_refusals(monkeypatch: pytest.MonkeyPatch) -> None:
    with _root() as folder:
        jail, grant = _jail(folder)
        with pytest.raises(Refuse) as bad_jail:
            read_text(object(), str(grant / "x"), None)
        assert refused(bad_jail.value).code == "BAD_JAIL"
        with pytest.raises(Refuse) as bad_cap:
            read_text(jail, str(grant / "x"), True)
        assert refused(bad_cap.value).code == "BAD_LIMIT"
        with pytest.raises(Refuse) as zero_cap:
            read_text(jail, str(grant / "x"), 0)
        assert refused(zero_cap.value).code == "BAD_LIMIT"
        with pytest.raises(Refuse) as text_cap:
            read_text(jail, str(grant / "x"), "9")
        assert refused(text_cap.value).code == "BAD_LIMIT"
        with pytest.raises(Refuse) as missing:
            read_text(jail, str(grant / "missing.txt"))
        assert refused(missing.value).code == "MISSING"
        nested = grant / "dir"
        nested.mkdir()
        with pytest.raises(Refuse) as not_file:
            read_text(jail, str(nested))
        assert refused(not_file.value).code == "NOT_FILE"
        binary = grant / "bin.dat"
        binary.write_bytes(b"\xff\xfe")
        with pytest.raises(Refuse) as not_utf8:
            read_text(jail, str(binary))
        assert refused(not_utf8.value).code == "NOT_UTF8"
        nul = grant / "zero.txt"
        nul.write_bytes(b"a\x00b")
        with pytest.raises(Refuse) as nul_hit:
            read_text(jail, str(nul))
        assert refused(nul_hit.value).code == "NULL_BYTE"
        with pytest.raises(Refuse) as not_text:
            read_text(jail, 12)
        assert refused(not_text.value).code == "NOT_TEXT"
        outside = folder / "outside.txt"
        outside.write_bytes(b"nope")
        with pytest.raises(Refuse) as escaped:
            read_text(jail, str(outside))
        assert refused(escaped.value).code == "OUTSIDE_GRANT"
        with pytest.raises(Refuse) as dotted:
            read_text(jail, str(grant / ".." / "out.txt"))
        assert refused(dotted.value).code == "DOTDOT"
        with pytest.raises(Refuse) as relative:
            read_text(jail, "note.txt")
        assert refused(relative.value).code == "RELATIVE_PATH"
        secret = grant / "secret.txt"
        secret.write_bytes(b"sk-livekey1")
        with pytest.raises(Refuse) as secret_hit:
            read_text(jail, str(secret))
        assert refused(secret_hit.value).code == "SECRET"
        assert "livekey1" not in str(secret_hit.value)
        secret_path = str(grant / "sk-livekey1.txt")
        with pytest.raises(Refuse) as secret_name:
            read_text(jail, secret_path)
        assert refused(secret_name.value).code == "SECRET"
        assert "livekey1" not in str(secret_name.value)
        readable = grant / "ok.txt"
        readable.write_bytes(b"ok")

        def _boom(*_args: object, **_kwargs: object) -> object:
            raise OSError("denied")

        monkeypatch.setattr(Path, "open", _boom)
        with pytest.raises(Refuse) as unread:
            read_text(jail, str(readable))
        assert refused(unread.value).code == "UNREADABLE"
        assert "denied" not in str(unread.value)

        def _stat_denied(self: Path, **_kwargs: object) -> object:
            raise PermissionError("denied")

        monkeypatch.setattr(Path, "stat", _stat_denied)
        with pytest.raises(Refuse) as stat_hit:
            read_text(jail, str(readable))
        assert refused(stat_hit.value).code == "UNREADABLE"


def test_patch_refusals() -> None:
    with pytest.raises(Refuse) as miss:
        patch("alpha", "beta", "gamma")
    assert refused(miss.value).code == "EDIT_MISS"
    with pytest.raises(Refuse) as many:
        patch("alpha alpha", "alpha", "beta")
    assert refused(many.value).code == "EDIT_NOT_UNIQUE"
    with pytest.raises(Refuse) as overlap:
        patch("aaa", "aa", "b")
    assert refused(overlap.value).code == "EDIT_NOT_UNIQUE"
    with pytest.raises(Refuse) as empty:
        patch("alpha", "", "beta")
    assert refused(empty.value).code == "EMPTY_OLD"
    with pytest.raises(Refuse) as nul:
        patch("a\x00b", "a", "c")
    assert refused(nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as not_text:
        patch(None, "a", "b")
    assert refused(not_text.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as formed:
        patch("sk-XXXX", "XXXX", "livekey1")
    assert refused(formed.value).code == "SECRET"
    assert "livekey1" not in str(formed.value)
    with pytest.raises(Refuse) as source_secret:
        patch("sk-abcdefghij", "sk-abcdefghij", "hello")
    assert refused(source_secret.value).code == "SECRET"
    assert "abcdefghij" not in str(source_secret.value)
    with pytest.raises(Refuse) as surrogate:
        patch("\ud800", "a", "b")
    assert refused(surrogate.value).code == "NOT_UTF8"
    with pytest.raises(Refuse) as bad_result:
        PatchResult(text="ok", replacements=0, schema=SCHEMA)
    assert refused(bad_result.value).code == "BAD_RESULT"
    with pytest.raises(Refuse) as bad_schema:
        PatchResult(text="ok", replacements=1, schema="other")
    assert refused(bad_schema.value).code == "BAD_SCHEMA"


def test_terminal_refusals() -> None:
    with pytest.raises(Refuse) as shell:
        terminal("echo hi")
    assert refused(shell.value).code == "SHELL_STRING"
    with pytest.raises(Refuse) as secret_shell:
        terminal("sk-livekey1")
    assert refused(secret_shell.value).code == "SECRET"
    assert "livekey1" not in str(secret_shell.value)
    with pytest.raises(Refuse) as bad:
        terminal(("py", "-c"))
    assert refused(bad.value).code == "BAD_ARGV"
    with pytest.raises(Refuse) as empty:
        terminal([])
    assert refused(empty.value).code == "EMPTY_ARGV"
    with pytest.raises(Refuse) as blank:
        terminal(["py", ""])
    assert refused(blank.value).code == "EMPTY_ARG"
    with pytest.raises(Refuse) as count:
        terminal(["py"] * (ARGV_CAP + 1))
    assert refused(count.value).code == "ARGV_COUNT"
    with pytest.raises(Refuse) as piece:
        terminal(["py", 1])
    assert refused(piece.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as split:
        terminal(["sk-", "abcdefgh"])
    assert refused(split.value).code == "SECRET"
    with pytest.raises(Refuse) as bearer:
        terminal(["Bearer", "abcdefgh"])
    assert refused(bearer.value).code == "SECRET"
    with pytest.raises(Refuse) as bad_code:
        TerminalRequest(argv=("py",), code="RUN", schema=SCHEMA)
    assert refused(bad_code.value).code == "BAD_CODE"
    with pytest.raises(Refuse) as bad_schema:
        TerminalRequest(argv=("py",), code="NEED_APPROVAL", schema="other")
    assert refused(bad_schema.value).code == "BAD_SCHEMA"
    with _root() as folder:
        with pytest.raises(Refuse) as bad_read:
            ReadText(
                path=_abs_note(folder),
                text="t",
                byte_len=1,
                cap=1,
                policy_cap=READ_CAP,
                schema="nope",
            )
        assert refused(bad_read.value).code == "BAD_SCHEMA"
        with pytest.raises(Refuse) as relative_record:
            ReadText(path="p", text="t", byte_len=1, cap=1, policy_cap=READ_CAP, schema=SCHEMA)
        assert refused(relative_record.value).code == "RELATIVE_PATH"
        with pytest.raises(Refuse) as dotted_record:
            ReadText(
                path=str(Path(_abs_note(folder)).parent / ".." / "x.txt"),
                text="t",
                byte_len=1,
                cap=1,
                policy_cap=READ_CAP,
                schema=SCHEMA,
            )
        assert refused(dotted_record.value).code == "DOTDOT"
        with pytest.raises(Refuse) as surrogate_record:
            ReadText(
                path=_abs_note(folder),
                text="\ud800",
                byte_len=1,
                cap=1,
                policy_cap=READ_CAP,
                schema=SCHEMA,
            )
        assert refused(surrogate_record.value).code == "NOT_UTF8"


def test_execute_requires_wipe_proof() -> None:
    argv = ["missing-binary-not-run", "lamp-card.txt"]
    with pytest.raises(Refuse) as missing_proof:
        execute(argv)
    assert refused(missing_proof.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as wrong_type:
        execute(argv, {"wipe_proof": True, "backend": "job_object"})
    assert refused(wrong_type.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as false_proof:
        WipeProof(False, "job_object")
    assert refused(false_proof.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as numbered:
        WipeProof(1, "job_object")  # type: ignore[arg-type]
    assert refused(numbered.value).code == "UNSANDBOXED"
    for name in ("local", "platform", "policy_only", "docker", "ssh", "modal", "vercel"):
        with pytest.raises(Refuse) as denied:
            WipeProof(True, name)
        assert refused(denied.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as unknown:
        WipeProof(True, "custom-box")
    assert refused(unknown.value).code == "UNKNOWN_BACKEND"
    with pytest.raises(Refuse) as empty_backend:
        WipeProof(True, "")
    assert refused(empty_backend.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as secret_backend:
        WipeProof(True, "sk-livekey1")
    assert refused(secret_backend.value).code == "SECRET"
    assert "livekey1" not in str(secret_backend.value)
    with pytest.raises(Refuse) as shell:
        execute("echo hi", WipeProof(True, "job_object"))
    assert refused(shell.value).code == "SHELL_STRING"
    proof = WipeProof(True, "job_object")
    assert proof.wipe_proof is True
    assert proof.backend in WIPE_BACKENDS
    assert secret_shape(repr(proof)) is False
    with pytest.raises(AttributeError):
        setattr(proof, "wipe_proof", False)


def test_execute_hold_cap_and_credentials() -> None:
    with _root() as folder:
        jail, grant = _jail(folder)
        card = grant / "lamp-card.txt"
        raw = b"Lamp card for Ada: dim the hall lamp.\r\n"
        card.write_bytes(raw)
        proof = WipeProof(True, "job_object")
        held = execute(
            ["missing-binary-not-run", str(card)],
            proof,
            cwd=str(grant),
            jail=jail,
            timeout_s=10**9,
            timestamp="2026-10-01T00:00:00Z",
        )
        assert held.code == "HELD"
        assert held.backend == "job_object"
        assert held.credential_id == ""
        assert held.work_dir == str(grant.resolve())
        assert held.timeout_s == POLICY_TIMEOUT_S
        assert held.requested_timeout_s == 10**9
        assert held.policy_timeout_s == POLICY_TIMEOUT_S
        assert held.schema == SCHEMA
        assert not hasattr(held, "pid")
        assert card.read_bytes() == raw
        assert secret_shape(repr(held)) is False
        low = execute(["rg", "-n", "lamp"], proof, timeout_s=15, timestamp="")
        assert low.timeout_s == 15
        assert low.requested_timeout_s == 15
        assert low.work_dir == ""
        other = execute(["rg", "-n", "lamp"], WipeProof(True, "posix_subprocess"))
        assert other.backend == "posix_subprocess"
        assert other == execute(["rg", "-n", "lamp"], WipeProof(True, "posix_subprocess"))
        with pytest.raises(Refuse) as timed:
            execute(["rg", "lamp"], proof, timeout_s=True)
        assert refused(timed.value).code == "NOT_INT"
        with pytest.raises(Refuse) as zero:
            execute(["rg", "lamp"], proof, timeout_s=0)
        assert refused(zero.value).code == "OUT_OF_RANGE"
        with pytest.raises(Refuse) as stamp:
            execute(["rg", "lamp"], proof, timestamp=None)
        assert refused(stamp.value).code == "NOT_TEXT"
        with pytest.raises(Refuse) as no_jail:
            execute(["rg", "lamp"], proof, cwd=str(grant), jail=object())
        assert refused(no_jail.value).code == "BAD_JAIL"
        with pytest.raises(Refuse) as dotted:
            execute(["rg", "lamp"], proof, cwd=str(grant / ".." / "out"), jail=jail)
        assert refused(dotted.value).code == "DOTDOT"
        outside = folder / "outside.txt"
        outside.write_bytes(b"nope")
        with pytest.raises(Refuse) as escaped:
            execute(["rg", "lamp"], proof, cwd=str(outside.parent), jail=jail)
        assert refused(escaped.value).code == "OUTSIDE_GRANT"
        with pytest.raises(Refuse) as local_cred:
            execute(
                ["rg", "lamp"],
                proof,
                credential_id="ada-sandbox",
                confirm_id="ada-sandbox",
            )
        assert refused(local_cred.value).code == "CREDENTIAL_REFUSED"
        remote = WipeProof(True, "daytona")
        for name in ("daytona", "e2b"):
            with pytest.raises(Refuse) as missing_cred:
                execute(["rg", "lamp"], WipeProof(True, name))
            assert refused(missing_cred.value).code == "MISSING_CREDENTIAL"
        with pytest.raises(Refuse) as mismatch:
            execute(
                ["rg", "lamp"],
                remote,
                credential_id="ada-sandbox",
                confirm_id="ada-other",
            )
        assert refused(mismatch.value).code == "CREDENTIAL_MISMATCH"
        assert "ada-sandbox" not in str(mismatch.value)
        with pytest.raises(Refuse) as bad_id:
            execute(
                ["rg", "lamp"],
                remote,
                credential_id="ada sandbox",
                confirm_id="ada sandbox",
            )
        assert refused(bad_id.value).code == "BAD_CREDENTIAL"
        with pytest.raises(Refuse) as secret_id:
            execute(
                ["rg", "lamp"],
                remote,
                credential_id="sk-livekey1",
                confirm_id="sk-livekey1",
            )
        assert refused(secret_id.value).code == "SECRET"
        assert "livekey1" not in str(secret_id.value)
        remote_hold = execute(
            ["rg", "-n", "lamp"],
            remote,
            credential_id="ada-sandbox",
            confirm_id="ada-sandbox",
            timestamp="2026-10-01T00:00:00Z",
        )
        assert remote_hold.credential_id == "ada-sandbox"
        assert remote_hold.backend == "daytona"
        assert card.read_bytes() == raw
        assert secret_shape(repr(remote_hold)) is False
        with pytest.raises(Refuse) as bad_code:
            ExecuteHold(
                argv=("rg",),
                backend="job_object",
                credential_id="",
                work_dir="",
                code="RUN",
                schema=SCHEMA,
                timeout_s=POLICY_TIMEOUT_S,
                requested_timeout_s=POLICY_TIMEOUT_S,
                policy_timeout_s=POLICY_TIMEOUT_S,
                timestamp="",
            )
        assert refused(bad_code.value).code == "BAD_CODE"
        with pytest.raises(Refuse) as raised:
            ExecuteHold(
                argv=("rg",),
                backend="job_object",
                credential_id="",
                work_dir="",
                code="HELD",
                schema=SCHEMA,
                timeout_s=1,
                requested_timeout_s=10**9,
                policy_timeout_s=POLICY_TIMEOUT_S,
                timestamp="",
            )
        assert refused(raised.value).code == "BAD_LIMIT"
        with pytest.raises(AttributeError):
            setattr(held, "code", "RUN")


def _story(root: Path) -> tuple[ReadText, PatchResult, TerminalRequest, str, str, ExecuteHold, bytes]:
    session = root / "north-session"
    session.mkdir(exist_ok=True)
    jail = PathJail([str(session)])
    card = session / "lamp-card.txt"
    raw = b"Lamp card for Ada: dim the hall lamp.\r\n"
    card.write_bytes(raw)
    loaded = read_text(jail, str(card))
    assert loaded.path == str(card.resolve())
    assert ".." not in Path(loaded.path).parts
    assert session.resolve() in Path(loaded.path).parents
    edited = patch(loaded.text, "dim", "lit")
    request = terminal(["rg", "-n", "lit", loaded.path])

    def _dotdot() -> ReadText:
        return read_text(jail, str(session / ".." / "other.txt"))

    def _bare() -> ExecuteHold:
        return execute(["rg", "-n", "lit", loaded.path], cwd=str(session), jail=jail)

    proof = WipeProof(True, "job_object")
    held = execute(
        ["rg", "-n", "lit", loaded.path],
        proof,
        cwd=str(session),
        jail=jail,
        timeout_s=10**6,
        timestamp="2026-10-01T12:00:00Z",
    )
    assert card.read_bytes() == raw
    assert held.code == "HELD"
    assert not hasattr(held, "pid")
    return (loaded, edited, request, _code(_dotdot), _code(_bare), held, card.read_bytes())


def test_example_file_terminal() -> None:
    with _root() as folder:
        first = _story(folder)
        second = _story(folder)
        assert first == second
        loaded, edited, request, dotdot, bare, held, raw = first
        assert loaded.text == "Lamp card for Ada: dim the hall lamp.\r\n"
        assert edited.text == "Lamp card for Ada: lit the hall lamp.\r\n"
        assert edited.replacements == 1
        assert request.code == "NEED_APPROVAL"
        assert request.argv[0] == "rg"
        assert dotdot == "DOTDOT"
        assert bare == "UNSANDBOXED"
        assert held.code == "HELD"
        assert held.backend == "job_object"
        assert held.timeout_s == POLICY_TIMEOUT_S
        assert held.requested_timeout_s == 10**6
        assert held.policy_timeout_s == POLICY_TIMEOUT_S
        assert raw == b"Lamp card for Ada: dim the hall lamp.\r\n"
        assert secret_shape(repr(loaded)) is False
        assert secret_shape(repr(held)) is False
