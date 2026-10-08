"""Named-job descriptors, fail-closed batches, policy cap, and no upload."""

from __future__ import annotations

import ast
import shutil
import tempfile
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest

import batch
from batch import (
    POLICY_BYTES,
    POLICY_CAP,
    PROMPT_CAP,
    RETRY_FAILURE,
    SCHEMA,
    BatchDescriptor,
    JobDescriptor,
    Skip,
    attempt,
    confirm,
    rebuild,
    resume,
    upload,
)
from cosmos_hermes import Refuse


def _go(
    jobs: object,
    *,
    credential_id: object = "cred-mira",
    fence: object = "fence-mira",
    distribution: object = "default",
    requested_cap: object = None,
    now: object = 10,
    seen: object = (),
    grant: object = None,
) -> BatchDescriptor:
    return attempt(
        jobs,
        credential_id=credential_id,
        fence=fence,
        distribution=distribution,
        requested_cap=requested_cap,
        now=now,
        seen=seen,
        grant=grant,
    )


def _job(record: BatchDescriptor, index: int) -> JobDescriptor:
    return record.jobs[index]


def _skip(record: BatchDescriptor, index: int) -> Skip:
    return record.skipped[index]


def _expect(code: str, fn: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        fn()
    assert caught.value.code == code


def _cards() -> list[dict[str, str]]:
    return [
        {"name": "porch-card", "prompt": "Write Mira a short card for the porch light she fixed."},
        {"name": "session-note", "prompt": "File the evening note from Mira's workshop session."},
        {"name": "porch-light", "prompt": "List three checks before the porch lamp is switched on."},
    ]


def test_example_batch() -> None:
    def once() -> BatchDescriptor:
        return attempt(
            _cards(),
            credential_id="cred-mira-session",
            fence="fence-mira-session",
            now=1_700_000_000,
        )

    first = once()
    second = once()
    assert first == second
    assert SCHEMA == "cosmos-hermes-batch/1"
    assert first.schema == SCHEMA
    assert first.cap == POLICY_CAP == 100
    assert first.applied_cap == POLICY_CAP
    assert first.byte_budget == POLICY_BYTES
    assert [item.name for item in first.jobs] == ["porch-card", "session-note", "porch-light"]
    assert first.skipped == ()
    assert rebuild(first) == first
    assert rebuild(first) is not first


def test_three_named_jobs_are_a_descriptor_list() -> None:
    result = _go(_cards())
    assert isinstance(result.jobs, tuple)
    assert len(result.jobs) == 3
    row = _job(result, 0)
    assert row.index == 0
    assert row.attempt == 1
    assert row.toolsets == ("file", "terminal")
    assert row.prev_sha == "0" * 64
    assert row.cwd == ""
    assert row.image == ""
    assert "porch light" not in repr(result)
    assert _job(result, 1).prev_sha == row.sha


def test_one_bad_job_fails_the_batch_closed() -> None:
    jobs: list[dict[str, str]] = [
        {"name": "porch-card", "prompt": "Write the porch card."},
        {"name": "session-note", "prompt": "api_key=supersecretvalue"},
        {"name": "porch-light", "prompt": "Check the porch lamp."},
    ]

    def run() -> BatchDescriptor:
        return _go(jobs)

    with pytest.raises(Refuse) as caught:
        run()
    assert caught.value.code == "SECRET"
    assert caught.value.detail == ""
    assert "supersecretvalue" not in str(caught.value)
    assert "sk-" not in str(caught.value)


def test_budget_skips_without_dropping_later_jobs() -> None:
    jobs = [
        {"name": "huge-card", "prompt": "h" * 6_000},
        {"name": "mid-note", "prompt": "n" * 4_000},
        {"name": "wide-lamp", "prompt": "w" * 2_000},
        {"name": "small-lamp", "prompt": "s" * 500},
    ]
    result = _go(jobs)
    assert [item.name for item in result.jobs] == ["mid-note", "small-lamp"]
    assert [item.name for item in result.skipped] == ["huge-card", "wide-lamp"]
    assert _skip(result, 0).source == 0
    assert _skip(result, 0).reason == "BUDGET"
    assert _job(result, 0).index == 0
    assert _job(result, 1).index == 1
    assert rebuild(result) == result
    blob = repr(result)
    assert "hhhh" not in blob
    assert result.byte_budget == POLICY_BYTES


def test_policy_cap_is_recorded_and_not_raised() -> None:
    full = [{"name": f"job-{index}", "prompt": "note"} for index in range(100)]
    held = _go(full)
    assert len(held.jobs) == 100
    assert held.cap == 100
    assert held.applied_cap == 100

    def over() -> BatchDescriptor:
        return _go([{"name": f"job-{index}", "prompt": "note"} for index in range(101)])

    with pytest.raises(Refuse) as caught:
        over()
    assert caught.value.code == "BATCH_CAP"
    assert caught.value.detail == "100"

    raised = _go(_cards(), requested_cap=10_000)
    assert raised.cap == 100
    assert raised.applied_cap == 100
    assert raised.byte_budget == POLICY_BYTES

    tight = _go(_cards()[:2], requested_cap=2)
    assert tight.cap == 100
    assert tight.applied_cap == 2

    def too_many() -> BatchDescriptor:
        return _go(_cards(), requested_cap=2)

    with pytest.raises(Refuse) as limited:
        too_many()
    assert limited.value.code == "BATCH_CAP"
    assert limited.value.detail == "2"


def test_malformed_jobs() -> None:
    samples: tuple[tuple[object, str], ...] = (
        (None, "BAD_ITEMS"),
        ("one prompt", "BAD_ITEMS"),
        (b"one", "BAD_ITEMS"),
        (bytearray(b"one"), "BAD_ITEMS"),
        ({"name": "porch-card", "prompt": "Write the card."}, "BAD_ITEMS"),
        ([], "EMPTY"),
        ((), "EMPTY"),
        (["x"], "NOT_MAP"),
        ([{"prompt": "Write the card."}], "MISSING"),
        ([{"name": "porch-card"}], "MISSING"),
        ([{"name": "", "prompt": "Write the card."}], "EMPTY_NAME"),
        ([{"name": "Porch", "prompt": "Write the card."}], "BAD_NAME"),
        ([{"name": "porch-card", "prompt": ""}], "EMPTY_PROMPT"),
        ([{"name": "porch-card", "prompt": "   "}], "EMPTY_PROMPT"),
        ([{"name": "porch-card", "prompt": 4}], "NOT_TEXT"),
        ([{"name": "porch-card", "prompt": "a\x00b"}], "NULL_BYTE"),
        ([{"name": "porch-card", "prompt": "x" * (PROMPT_CAP + 1)}], "OVERSIZE"),
        ([{"name": "porch-card", "prompt": "sk-livekeyvalue"}], "SECRET"),
        ([{"name": "porch-card", "prompt": "Bearer abcdefghij"}], "SECRET"),
        ([{"name": "porch-card", "prompt": "api_key=abcdefghij"}], "SECRET"),
        (
            [
                {"name": "porch-card", "prompt": "Write the card."},
                {"name": "porch-card", "prompt": "Write another card."},
            ],
            "DUPLICATE",
        ),
        ([{"name": "porch-card", "prompt": "Write the card.", "tools": ["file"]}], "UNKNOWN_FIELD"),
        ([{"name": "porch-card", "prompt": "Write the card.", "image": ""}], "BAD_IMAGE"),
        ([{"name": "porch-card", "prompt": "Write the card.", "image": "Python"}], "BAD_IMAGE"),
        ([{"name": "porch-card", "prompt": "Write the card.", "image": ".."}], "BAD_IMAGE"),
        ([{"name": "porch-card", "prompt": "Write the card.", "completed": "yes"}], "NOT_BOOL"),
        ([{"name": "porch-card", "prompt": "Write the card.", "completed": True}], "UNVERIFIABLE"),
    )

    def check(jobs: object, code: str) -> None:
        def run() -> BatchDescriptor:
            return _go(jobs)

        _expect(code, run)

    for jobs, code in samples:
        check(jobs, code)

    tagged = _go([{"name": "porch-card", "prompt": "Write the card.", "completed": False, "image": "python:3.11"}])
    assert _job(tagged, 0).image == "python:3.11"
    pinned = _go([{"name": "porch-card", "prompt": "Write the card."}], distribution="eval")
    assert _job(pinned, 0).toolsets == ("file",)


def test_caller_fields_refuse() -> None:
    good = [{"name": "porch-card", "prompt": "Write the card."}]

    def check(code: str, fn: Callable[[], object]) -> None:
        _expect(code, fn)

    def cap_bool() -> BatchDescriptor:
        return _go(good, requested_cap=True)

    def cap_float() -> BatchDescriptor:
        return _go(good, requested_cap=1.5)

    def cap_text() -> BatchDescriptor:
        return _go(good, requested_cap="100")

    def cap_zero() -> BatchDescriptor:
        return _go(good, requested_cap=0)

    def cap_negative() -> BatchDescriptor:
        return _go(good, requested_cap=-3)

    def now_bool() -> BatchDescriptor:
        return _go(good, now=True)

    def now_negative() -> BatchDescriptor:
        return _go(good, now=-1)

    def now_none() -> BatchDescriptor:
        return _go(good, now=None)

    def fence_missing() -> BatchDescriptor:
        return _go(good, fence=None)

    def fence_empty() -> BatchDescriptor:
        return _go(good, fence="")

    def fence_bad() -> BatchDescriptor:
        return _go(good, fence="Bad Fence")

    def dist_missing() -> BatchDescriptor:
        return _go(good, distribution=None)

    def dist_empty() -> BatchDescriptor:
        return _go(good, distribution="")

    def dist_unknown() -> BatchDescriptor:
        return _go(good, distribution="random")

    def cred_missing() -> BatchDescriptor:
        return _go(good, credential_id=None)

    def cred_empty() -> BatchDescriptor:
        return _go(good, credential_id="")

    def cred_shape() -> BatchDescriptor:
        return _go(good, credential_id="Bad")

    def cred_secret() -> BatchDescriptor:
        return _go(good, credential_id="sk-livekeyvalue")

    def seen_text() -> BatchDescriptor:
        return _go(good, seen="fence-mira")

    def seen_replay() -> BatchDescriptor:
        return _go(good, seen=("fence-mira",))

    check("NOT_INT", cap_bool)
    check("NOT_INT", cap_float)
    check("NOT_INT", cap_text)
    check("OUT_OF_RANGE", cap_zero)
    check("OUT_OF_RANGE", cap_negative)
    check("NOT_INT", now_bool)
    check("OUT_OF_RANGE", now_negative)
    check("NOT_INT", now_none)
    check("MISSING", fence_missing)
    check("EMPTY", fence_empty)
    check("BAD_FENCE", fence_bad)
    check("MISSING", dist_missing)
    check("EMPTY", dist_empty)
    check("UNKNOWN", dist_unknown)
    check("MISSING_CRED", cred_missing)
    check("MISSING_CRED", cred_empty)
    check("MISSING_CRED", cred_shape)
    check("SECRET", cred_secret)
    check("NOT_LIST", seen_text)
    check("REPLAY", seen_replay)


def test_resume_chain_retry_and_rebuild() -> None:
    first = _go(
        [
            {"name": "porch-card", "prompt": "Write the porch card."},
            {"name": "session-note", "prompt": "File the session note."},
        ]
    )
    second = resume(
        first,
        [
            {"name": "porch-card", "prompt": "Write the porch card."},
            {"name": "porch-light", "prompt": "Check the porch lamp."},
        ],
        credential_id="cred-mira",
        fence="fence-mira-2",
        now=11,
    )
    assert [item.name for item in second.jobs] == ["porch-card", "session-note", "porch-light"]
    assert rebuild(second) == second

    copied = resume(
        first,
        [{"name": "copy-card", "prompt": "Write the porch card."}],
        credential_id="cred-mira",
        fence="fence-mira-3",
        now=12,
    )
    assert copied.jobs == first.jobs
    assert copied.chain != first.chain

    def mismatch() -> BatchDescriptor:
        return resume(
            first,
            [{"name": "porch-card", "prompt": "A different card."}],
            credential_id="cred-mira",
            fence="fence-mira-4",
            now=13,
        )

    def stale() -> BatchDescriptor:
        return resume(
            first,
            [{"name": "porch-light", "prompt": "Check the porch lamp."}],
            credential_id="cred-mira",
            fence="fence-mira-5",
            now=9,
        )

    def replay() -> BatchDescriptor:
        return resume(
            first,
            [{"name": "porch-light", "prompt": "Check the porch lamp."}],
            credential_id="cred-mira",
            fence="fence-mira",
            now=14,
        )

    def other_cred() -> BatchDescriptor:
        return resume(
            first,
            [{"name": "porch-light", "prompt": "Check the porch lamp."}],
            credential_id="cred-other",
            fence="fence-mira-6",
            now=14,
        )

    def other_dist() -> BatchDescriptor:
        return resume(
            first,
            [{"name": "porch-light", "prompt": "Check the porch lamp."}],
            credential_id="cred-mira",
            fence="fence-mira-7",
            now=14,
            distribution="eval",
        )

    def not_record() -> BatchDescriptor:
        return resume(
            object(),
            [{"name": "porch-light", "prompt": "Check the porch lamp."}],
            credential_id="cred-mira",
            fence="fence-mira-8",
            now=14,
        )

    _expect("MISMATCH", mismatch)
    _expect("STALE", stale)
    _expect("REPLAY", replay)
    _expect("MISMATCH", other_cred)
    _expect("MISMATCH", other_dist)
    _expect("BAD_RECORD", not_record)

    _expect("CHAIN", _rebuild_broken_sha(first))
    _expect("MISMATCH", _rebuild_broken_tools(first))
    _expect("EMPTY", _rebuild_blank(first))
    _expect("BAD_RECORD", _rebuild_schema(first))

    retried = confirm(first, "session-note", RETRY_FAILURE)
    assert _job(retried, 1).attempt == 2
    assert _job(retried, 0).attempt == 1
    assert rebuild(retried) == retried

    def again() -> BatchDescriptor:
        return confirm(retried, "session-note", RETRY_FAILURE)

    def wrong() -> BatchDescriptor:
        return confirm(first, "porch-card", "WORKER_FAIL")

    def missing() -> BatchDescriptor:
        return confirm(first, "missing-name", RETRY_FAILURE)

    def leaked() -> BatchDescriptor:
        return confirm(first, "porch-card", "sk-livekeyvalue")

    _expect("RETRY_CAP", again)
    _expect("NO_RETRY", wrong)
    _expect("UNKNOWN", missing)
    with pytest.raises(Refuse) as secret:
        leaked()
    assert secret.value.code == "SECRET"
    assert "sk-" not in str(secret.value)


def _broken_sha(record: BatchDescriptor) -> BatchDescriptor:
    job = replace(_job(record, 0), sha="0" * 64)
    return replace(record, jobs=(job,) + record.jobs[1:])


def _broken_tools(record: BatchDescriptor) -> BatchDescriptor:
    job = replace(_job(record, 0), toolsets=("file",))
    return replace(record, jobs=(job,) + record.jobs[1:])


def _rebuild_broken_sha(record: BatchDescriptor) -> Callable[[], object]:
    def run() -> BatchDescriptor:
        return rebuild(_broken_sha(record))

    return run


def _rebuild_broken_tools(record: BatchDescriptor) -> Callable[[], object]:
    def run() -> BatchDescriptor:
        return rebuild(_broken_tools(record))

    return run


def _rebuild_blank(record: BatchDescriptor) -> Callable[[], object]:
    def run() -> BatchDescriptor:
        return rebuild(replace(record, jobs=(), skipped=()))

    return run


def _rebuild_schema(record: BatchDescriptor) -> Callable[[], object]:
    def run() -> BatchDescriptor:
        return rebuild(replace(record, schema="cosmos-hermes-batch/2"))

    return run


def test_prior_skip_is_kept_and_upload_refuses() -> None:
    first = _go([{"name": "huge-card", "prompt": "h" * 6_000}])
    assert first.jobs == ()
    assert _skip(first, 0).name == "huge-card"
    second = resume(
        first,
        [{"name": "porch-light", "prompt": "Check the porch lamp."}],
        credential_id="cred-mira",
        fence="fence-next",
        now=11,
    )
    assert [item.name for item in second.jobs] == ["porch-light"]
    assert [item.name for item in second.skipped] == ["huge-card"]
    assert rebuild(second) == second

    def up() -> None:
        upload("data/run", token="sk-livekeyvalue")

    with pytest.raises(Refuse) as caught:
        up()
    assert caught.value.code == "NO_UPLOAD"
    assert "sk-" not in str(caught.value)


def test_cwd_stays_inside_the_grant() -> None:
    root = tempfile.mkdtemp(prefix="hermes-batch-")
    try:
        inside = str(Path(root) / "notes")
        held = _go(
            [{"name": "session-note", "prompt": "Read the evening note.", "cwd": inside}],
            grant=(root,),
        )
        assert _job(held, 0).cwd == str(Path(inside).resolve())
        again = _go(
            [{"name": "session-note", "prompt": "Read the evening note.", "cwd": inside}],
            grant=(root,),
        )
        assert again == held
        assert rebuild(held, grant=(root,)) == held

        def bare() -> BatchDescriptor:
            return _go([{"name": "session-note", "prompt": "Read the evening note.", "cwd": inside}])

        _expect("NO_GRANT", bare)

        outside = str(Path(root).parent / "hermes-batch-outside")
        cases: tuple[tuple[str, object, str], ...] = (
            ("notes", (root,), "RELATIVE_PATH"),
            (outside, (root,), "OUTSIDE_GRANT"),
            ("", (root,), "BAD_PATH"),
            (str(Path(root) / ".." / "leave"), (root,), "DOTDOT"),
            (str(Path(root) / "%2e%2e" / "leave"), (root,), "ENCODED_DOTDOT"),
            ("file:///tmp/note", (root,), "FILE_URL"),
            ("\\\\host\\share\\note", (root,), "UNC"),
            ("C:\\", (root,), "DRIVE_ROOT"),
            ("C:notes", (root,), "DRIVE_RELATIVE"),
            ("C:\\notes\\lamp:stream", (root,), "ALT_STREAM"),
            ("C:\\notes\\lamp.", (root,), "TRAILING_DOT"),
        )

        def check(cwd: str, grant: object, code: str) -> None:
            def run() -> BatchDescriptor:
                return _go(
                    [{"name": "session-note", "prompt": "Read the evening note.", "cwd": cwd}],
                    grant=grant,
                )

            _expect(code, run)

        for cwd, grant, code in cases:
            check(cwd, grant, code)

        def relative_grant() -> BatchDescriptor:
            return _go(
                [{"name": "session-note", "prompt": "Read the evening note.", "cwd": inside}],
                grant=("notes",),
            )

        _expect("RELATIVE_GRANT", relative_grant)
    finally:
        shutil.rmtree(root)


def test_records_are_frozen_and_module_stays_local() -> None:
    result = _go(_cards())
    with pytest.raises(AttributeError):
        setattr(result, "cap", 1)
    assert hasattr(JobDescriptor, "__slots__")
    assert hasattr(BatchDescriptor, "__slots__")
    assert hasattr(Skip, "__slots__")
    assert "status" not in BatchDescriptor.__slots__

    source_path = batch.__file__
    assert source_path is not None
    source = Path(source_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.append(node.module)
    assert "cosmos_hermes" in imported
    banned = (
        "threading",
        "concurrent",
        "multiprocessing",
        "socket",
        "subprocess",
        "urllib",
        "requests",
        "pickle",
        "asyncio",
        "http",
    )
    for name in imported:
        for prefix in banned:
            assert name != prefix and not name.startswith(prefix + ".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"exec", "eval", "compile", "__import__", "open"}
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"open", "system", "popen", "spawn"}
