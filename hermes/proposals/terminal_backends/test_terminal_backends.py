"""Refusal, cap, proof, and descriptor coverage for terminal_backends."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from cosmos_hermes import PathJail, Refuse, secret_shape
from terminal_backends import (
    ARG_CAP,
    ARGV_CAP,
    BACKENDS,
    DAYTONA_DISK_MB,
    ENV_BUDGET,
    ENV_LIST_CAP,
    ENV_NAME_CAP,
    PLAN_CAP,
    POLICY_DISK_MB,
    POLICY_TIMEOUT_S,
    PROOF_SCHEMA,
    SCHEMA,
    BackendSpec,
    Catalog,
    EnvName,
    TerminalOrder,
    TerminalPlan,
    WipeProof,
    execute,
    issue_proof,
    plan,
    proof_digest,
    rebuild,
    snapshot,
    spec,
)

_STAMP = "2026-10-01T00:00:00Z"
_ARGV = ["tool-not-spawned", "arg"]


@contextmanager
def _workspace() -> Iterator[tuple[PathJail, Path, Path]]:
    root = Path(tempfile.mkdtemp(prefix="terminal_backends_"))
    try:
        grant = root / "grant"
        grant.mkdir()
        yield PathJail([str(grant)]), grant, root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def refused(exc: object) -> Refuse:
    assert isinstance(exc, Refuse)
    assert secret_shape(str(exc)) is False
    assert secret_shape(repr(exc)) is False
    return exc


def _pair(fn: Callable[[], None]) -> tuple[str, str]:
    try:
        fn()
    except Refuse as err:
        clean = refused(err)
        return clean.code, clean.detail
    raise AssertionError("expected Refuse")


def _plan_at(rows: tuple[TerminalPlan, ...], index: int) -> TerminalPlan:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing")
    return rows[index]


def _env_at(rows: tuple[EnvName, ...], index: int) -> EnvName:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing")
    return rows[index]


def _env_token(prefix: str, width: int) -> str:
    if len(prefix) > width:
        raise AssertionError("prefix")
    return prefix + ("X" * (width - len(prefix)))


def _cred(name: str) -> str:
    if name in ("ssh", "modal", "daytona", "vercel"):
        return name + "-cred-1"
    return ""


def _plan_ready(name: str, argv: list[str]) -> TerminalPlan:
    cred = _cred(name)
    if name == "ssh":
        return plan(
            name,
            argv,
            host="shell.example.com",
            user="builder",
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
        )
    if cred != "":
        return plan(
            name,
            argv,
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
        )
    return plan(name, argv, timestamp=_STAMP, task_id="row." + name)


def _execute_ready(name: str, argv: list[str]) -> None:
    cred = _cred(name)
    if name == "ssh":
        execute(
            name,
            argv,
            host="shell.example.com",
            user="builder",
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
        )
        return
    if cred != "":
        execute(
            name,
            argv,
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
        )
        return
    execute(name, argv, timestamp=_STAMP, task_id="row." + name)


def _proven(name: str) -> TerminalOrder:
    cred = _cred(name)
    proof = issue_proof(
        backend=name,
        credential_id=cred,
        proof_id="proof-" + name,
        stamp=_STAMP,
    )
    if name == "ssh":
        return execute(
            name,
            ["tool-not-spawned"],
            host="shell.example.com",
            user="builder",
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
            proof=proof,
        )
    if cred != "":
        return execute(
            name,
            ["tool-not-spawned"],
            credential_id=cred,
            expected_credential_id=cred,
            timestamp=_STAMP,
            task_id="row." + name,
            proof=proof,
        )
    return execute(
        name,
        ["tool-not-spawned"],
        timestamp=_STAMP,
        task_id="row." + name,
        proof=proof,
    )


@dataclass(frozen=True, slots=True)
class _Lookalike:
    schema: str
    backend: str
    credential_id: str
    proof_id: str
    stamp: str
    digest: str


@dataclass(frozen=True, slots=True)
class _Story:
    local_class: str
    local_timeout: int
    local_requested: int
    local_clamped: tuple[str, ...]
    local_code: str
    local_detail: str
    docker_code: str
    docker_detail: str
    order: TerminalOrder
    catalog: Catalog
    rebuilt: Catalog


def _story() -> _Story:
    argv = ["note", "light the porch", "card-porch-light"]

    def _run_local() -> None:
        execute(
            "local",
            argv,
            task_id="porch-session",
            timestamp=_STAMP,
            timeout_s=600,
        )

    def _run_docker() -> None:
        execute(
            "docker",
            argv,
            task_id="porch-docker",
            timestamp=_STAMP,
            image="python:3.11-slim",
        )

    local = plan(
        "local",
        argv,
        task_id="porch-session",
        timestamp=_STAMP,
        timeout_s=600,
    )
    local_code, local_detail = _pair(_run_local)
    docker_code, docker_detail = _pair(_run_docker)
    proof = issue_proof(backend="docker", proof_id="proof-porch-light", stamp=_STAMP)
    order = execute(
        "docker",
        argv,
        task_id="porch-docker",
        timestamp=_STAMP,
        image="python:3.11-slim",
        proof=proof,
    )
    catalog = snapshot((local, order.plan))
    return _Story(
        local_class=local.classification,
        local_timeout=local.spec.timeout_s,
        local_requested=local.spec.requested_timeout_s,
        local_clamped=local.spec.clamped,
        local_code=local_code,
        local_detail=local_detail,
        docker_code=docker_code,
        docker_detail=docker_detail,
        order=order,
        catalog=catalog,
        rebuilt=rebuild(catalog),
    )


def test_example_terminal_backends() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.local_class == "UNSANDBOXED"
    assert first.local_code == "UNSANDBOXED"
    assert first.local_detail == "local"
    assert first.docker_code == "UNSANDBOXED"
    assert first.docker_detail == "docker"
    assert first.local_timeout == POLICY_TIMEOUT_S
    assert first.local_requested == 600
    assert first.local_clamped == ("timeout_s",)
    assert first.order.classification == "SANDBOXED"
    assert first.order.plan.spec.name == "docker"
    assert first.order.plan.classification == "UNPROVEN"
    assert first.order.plan.spec.policy_only is True
    assert first.order.proof_id == "proof-porch-light"
    assert first.rebuilt == first.catalog
    local = _plan_at(first.catalog.plans, 0)
    assert local.classification == "UNSANDBOXED"
    assert local.task_id == "porch-session"
    assert local.argv == ("note", "light the porch", "card-porch-light")
    assert secret_shape(repr(first.order)) is False
    assert secret_shape(repr(first.catalog)) is False
    assert secret_shape(repr(local)) is False


def test_schema_and_seven_names() -> None:
    assert SCHEMA == "cosmos-hermes-terminal_backends/1"
    assert PROOF_SCHEMA == "cosmos-hermes-terminal_backends-wipe/1"
    assert BACKENDS == (
        "local",
        "docker",
        "ssh",
        "singularity",
        "modal",
        "daytona",
        "vercel",
    )
    assert len(BACKENDS) == 7
    assert ENV_BUDGET == 64
    assert PLAN_CAP == 32


@pytest.mark.parametrize("name", BACKENDS)
def test_spec_is_policy_only(name: str) -> None:
    row = spec(name)
    assert row == spec(name)
    assert isinstance(row, BackendSpec)
    assert row.schema == SCHEMA
    assert row.name == name
    assert row.policy_only is True
    assert row.remote is (name in ("ssh", "modal", "daytona", "vercel"))
    assert row.needs_credential is row.remote
    assert row.isolation == {
        "local": "none",
        "docker": "container",
        "ssh": "remote",
        "singularity": "namespace",
        "modal": "container",
        "daytona": "container",
        "vercel": "microvm",
    }[name]
    assert row.classification == ("UNSANDBOXED" if name == "local" else "UNPROVEN")
    assert row.timeout_s == POLICY_TIMEOUT_S
    assert row.requested_timeout_s == POLICY_TIMEOUT_S
    assert row.clamped == ()
    assert secret_shape(repr(row)) is False
    with pytest.raises(AttributeError):
        setattr(row, "policy_only", False)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "Docker",
        "vercel_sandbox",
        "managed_modal",
        "job_object",
        "e2b",
        "podman",
        "local ",
        "off",
        "yolo",
    ],
)
def test_unknown_backend(name: str) -> None:
    with pytest.raises(Refuse) as info:
        spec(name)
    assert refused(info.value).code == "UNKNOWN_BACKEND"
    with pytest.raises(Refuse) as planned:
        plan(name, ["tool-not-spawned"])
    assert refused(planned.value).code == "UNKNOWN_BACKEND"


def test_caps_are_policy() -> None:
    assert POLICY_TIMEOUT_S == 180
    assert POLICY_DISK_MB == 51_200
    assert DAYTONA_DISK_MB == 10_240
    high = spec("docker", timeout_s=10_000, disk_mb=90_000)
    assert high.timeout_s == POLICY_TIMEOUT_S
    assert high.requested_timeout_s == 10_000
    assert high.disk_mb == POLICY_DISK_MB
    assert high.requested_disk_mb == 90_000
    assert high.clamped == ("timeout_s", "disk_mb")
    assert high.policy_only is True
    assert high.classification == "UNPROVEN"
    low = spec("docker", timeout_s=12, disk_mb=256)
    assert low.timeout_s == 12
    assert low.requested_timeout_s == 12
    assert low.disk_mb == 256
    assert low.requested_disk_mb == 256
    assert low.clamped == ()
    floor = spec("modal", timeout_s=1, disk_mb=1)
    assert floor.timeout_s == 1
    assert floor.disk_mb == 1
    day = spec("daytona", disk_mb=20_000)
    assert day.disk_mb == DAYTONA_DISK_MB
    assert day.requested_disk_mb == 20_000
    assert day.clamped == ("disk_mb",)
    edge = spec("daytona", disk_mb=DAYTONA_DISK_MB)
    assert edge.disk_mb == DAYTONA_DISK_MB
    assert edge.clamped == ()
    vercel = spec("vercel")
    assert vercel.disk_mb == POLICY_DISK_MB
    assert vercel.requested_disk_mb == POLICY_DISK_MB
    same = spec("vercel", disk_mb=POLICY_DISK_MB)
    assert same.disk_mb == POLICY_DISK_MB
    assert spec("local").disk_mb == 0
    assert spec("ssh").disk_mb == 0
    assert spec("singularity").disk_mb == 0
    held = plan(
        "docker",
        ["tool-not-spawned"],
        timeout_s=5_000,
        disk_mb=60_000,
        timestamp=_STAMP,
    )
    assert held.spec.timeout_s == POLICY_TIMEOUT_S
    assert held.spec.requested_timeout_s == 5_000
    assert held.spec.disk_mb == POLICY_DISK_MB
    assert held.spec.clamped == ("timeout_s", "disk_mb")
    assert held.classification == "UNPROVEN"


def test_cap_refusals() -> None:
    with pytest.raises(Refuse) as zero:
        spec("local", timeout_s=0)
    assert refused(zero.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        spec("docker", timeout_s=-5)
    assert refused(negative.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as huge:
        spec("docker", timeout_s=1_000_000_001)
    assert refused(huge.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flag:
        spec("local", timeout_s=True)
    assert refused(flag.value).code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        spec("local", timeout_s="180")
    assert refused(text.value).code == "NOT_INT"
    with pytest.raises(Refuse) as disk_flag:
        spec("docker", disk_mb=True)
    assert refused(disk_flag.value).code == "NOT_INT"
    with pytest.raises(Refuse) as disk_zero:
        spec("docker", disk_mb=0)
    assert refused(disk_zero.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as local_disk:
        spec("local", disk_mb=1)
    assert refused(local_disk.value).code == "DISK_UNSUPPORTED"
    with pytest.raises(Refuse) as ssh_disk:
        spec("ssh", disk_mb=POLICY_DISK_MB)
    assert refused(ssh_disk.value).code == "DISK_UNSUPPORTED"
    with pytest.raises(Refuse) as sif_disk:
        spec("singularity", disk_mb=1)
    assert refused(sif_disk.value).code == "DISK_UNSUPPORTED"
    with pytest.raises(Refuse) as vercel_disk:
        spec("vercel", disk_mb=1_024)
    assert refused(vercel_disk.value).code == "DISK_UNSUPPORTED"
    with pytest.raises(Refuse) as vercel_type:
        spec("vercel", disk_mb="51200")
    assert refused(vercel_type.value).code == "NOT_INT"


@pytest.mark.parametrize("name", BACKENDS)
def test_plan_succeeds_and_execute_refuses(name: str) -> None:
    held = _plan_ready(name, list(_ARGV))
    assert held.argv == ("tool-not-spawned", "arg")
    assert held.spec.policy_only is True
    assert held.spec.name == name
    assert held.schema == SCHEMA
    assert held.classification == ("UNSANDBOXED" if name == "local" else "UNPROVEN")
    assert secret_shape(repr(held)) is False
    again = _plan_ready(name, list(_ARGV))
    assert again == held
    with pytest.raises(Refuse) as info:
        _execute_ready(name, list(_ARGV))
    err = refused(info.value)
    assert err.code == "UNSANDBOXED"
    assert err.detail == name
    assert _ARGV == ["tool-not-spawned", "arg"]


@pytest.mark.parametrize("name", ["docker", "ssh", "singularity", "modal", "daytona", "vercel"])
def test_execute_with_proof_returns_descriptor(name: str) -> None:
    order = _proven(name)
    assert order == _proven(name)
    assert order.classification == "SANDBOXED"
    assert order.plan.classification == "UNPROVEN"
    assert order.plan.spec.name == name
    assert order.schema == SCHEMA
    assert secret_shape(repr(order)) is False
    digest = proof_digest(name, _cred(name), "proof-" + name, _STAMP)
    proof = issue_proof(
        backend=name,
        credential_id=_cred(name),
        proof_id="proof-" + name,
        stamp=_STAMP,
    )
    assert proof.digest == digest
    assert proof.schema == PROOF_SCHEMA


def test_shell_string_and_argv_shape() -> None:
    with pytest.raises(Refuse) as shell:
        execute("local", "echo hi")
    assert refused(shell.value).code == "SHELL_STRING"
    with pytest.raises(Refuse) as planned:
        plan("docker", "ls -la")
    assert refused(planned.value).code == "SHELL_STRING"
    with pytest.raises(Refuse) as secret:
        plan("local", "sk-abcdefghij")
    assert refused(secret.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as blob:
        plan("local", b"echo")
    assert refused(blob.value).code == "BAD_ARGV"
    with pytest.raises(Refuse) as pair:
        plan("local", ("tool-not-spawned",))
    assert refused(pair.value).code == "BAD_ARGV"
    with pytest.raises(Refuse) as empty:
        plan("local", [])
    assert refused(empty.value).code == "EMPTY_ARGV"
    with pytest.raises(Refuse) as blank:
        plan("local", ["tool-not-spawned", ""])
    assert refused(blank.value).code == "EMPTY_ARG"
    with pytest.raises(Refuse) as count:
        plan("local", ["tool-not-spawned"] * (ARGV_CAP + 1))
    assert refused(count.value).code == "ARGV_COUNT"
    assert refused(count.value).detail == str(ARGV_CAP)
    with pytest.raises(Refuse) as huge:
        plan("local", ["x" * (ARG_CAP + 1)])
    assert refused(huge.value).code == "OVERSIZE"
    with pytest.raises(Refuse) as nul:
        plan("local", ["ok\x00"])
    assert refused(nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as nested:
        plan("local", [["nope"]])
    assert refused(nested.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as split:
        plan("local", ["api_key", "=abcdef"])
    assert refused(split.value).code == "SECRET_SHAPE"
    held = plan("local", ["tool-not-spawned", "hello;world"], timestamp=_STAMP)
    assert held.argv == ("tool-not-spawned", "hello;world")
    assert held.classification == "UNSANDBOXED"


def test_ssh_host_and_user() -> None:
    host = "a" * 253
    held = plan(
        "ssh",
        ["tool-not-spawned"],
        host=host,
        user="a" * 32,
        credential_id="ssh-cred-1",
        expected_credential_id="ssh-cred-1",
        timestamp=_STAMP,
    )
    assert held.host == host
    assert held.user == "a" * 32
    dotted = plan(
        "ssh",
        ["tool-not-spawned"],
        host="A1.example-host.com",
        user="builder_1",
        credential_id="ssh-cred-1",
        timestamp=_STAMP,
    )
    assert dotted.host == "A1.example-host.com"
    with pytest.raises(Refuse) as long_host:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="a" * 254,
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(long_host.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as spaced:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="bad host",
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(spaced.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as under:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="bad_host",
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(under.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as shell_host:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="host;rm",
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(shell_host.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as missing:
        plan("ssh", ["tool-not-spawned"], user="builder", credential_id="ssh-cred-1")
    assert refused(missing.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as local_host:
        plan("local", ["tool-not-spawned"], host="shell.example.com")
    assert refused(local_host.value).code == "BAD_HOST"
    with pytest.raises(Refuse) as bad_user:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="shell.example.com",
            user="builder;id",
            credential_id="ssh-cred-1",
        )
    assert refused(bad_user.value).code == "BAD_USER"
    with pytest.raises(Refuse) as long_user:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="shell.example.com",
            user="a" * 33,
            credential_id="ssh-cred-1",
        )
    assert refused(long_user.value).code == "BAD_USER"
    with pytest.raises(Refuse) as no_user:
        plan("ssh", ["tool-not-spawned"], host="shell.example.com", credential_id="ssh-cred-1")
    assert refused(no_user.value).code == "BAD_USER"
    with pytest.raises(Refuse) as local_user:
        plan("docker", ["tool-not-spawned"], user="builder")
    assert refused(local_user.value).code == "BAD_USER"
    with pytest.raises(Refuse) as host_type:
        plan("ssh", ["tool-not-spawned"], host=22, user="builder", credential_id="ssh-cred-1")
    assert refused(host_type.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as host_nul:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="good.com\x00",
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(host_nul.value).code == "NULL_BYTE"
    with pytest.raises(Refuse) as host_secret:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="sk-abcdefgh.example.com",
            user="builder",
            credential_id="ssh-cred-1",
        )
    assert refused(host_secret.value).code == "SECRET_SHAPE"


def test_credentials() -> None:
    held = plan(
        "modal",
        ["tool-not-spawned"],
        credential_id="modal-cred-1",
        expected_credential_id="modal-cred-1",
        timestamp=_STAMP,
    )
    assert held.credential_id == "modal-cred-1"
    assert secret_shape(repr(held)) is False
    with pytest.raises(Refuse) as missing:
        plan("daytona", ["tool-not-spawned"])
    assert refused(missing.value).code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as mismatch:
        plan(
            "vercel",
            ["tool-not-spawned"],
            credential_id="vercel-cred-1",
            expected_credential_id="vercel-cred-2",
        )
    assert refused(mismatch.value).code == "CREDENTIAL_MISMATCH"
    with pytest.raises(Refuse) as refused_cred:
        plan("local", ["tool-not-spawned"], credential_id="local-cred-1")
    assert refused(refused_cred.value).code == "CREDENTIAL_REFUSED"
    with pytest.raises(Refuse) as expected_only:
        plan("docker", ["tool-not-spawned"], expected_credential_id="docker-cred-1")
    assert refused(expected_only.value).code == "CREDENTIAL_REFUSED"
    with pytest.raises(Refuse) as shaped:
        plan(
            "ssh",
            ["tool-not-spawned"],
            host="shell.example.com",
            user="builder",
            credential_id="api_key=abcdef",
        )
    assert refused(shaped.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as bearer:
        plan(
            "modal",
            ["tool-not-spawned"],
            credential_id="modal-cred-1",
            expected_credential_id="Bearer abcdefgh",
        )
    assert refused(bearer.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as bad:
        plan("modal", ["tool-not-spawned"], credential_id="-modal")
    assert refused(bad.value).code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as spaced:
        plan("modal", ["tool-not-spawned"], credential_id="modal cred")
    assert refused(spaced.value).code == "BAD_CREDENTIAL"
    open_id = plan(
        "ssh",
        ["tool-not-spawned"],
        host="shell.example.com",
        user="builder",
        credential_id="ssh-cred-1",
        timestamp=_STAMP,
    )
    assert open_id.credential_id == "ssh-cred-1"


def test_images_and_paths() -> None:
    with _workspace() as (jail, grant, root):
        local = plan(
            "local",
            ["tool-not-spawned"],
            work_dir=str(grant),
            jail=jail,
            timestamp=_STAMP,
        )
        assert local.work_dir == str(grant.resolve())
        assert local.image == ""
        with pytest.raises(Refuse) as still:
            execute(
                "local",
                ["tool-not-spawned"],
                work_dir=str(grant),
                jail=jail,
                timestamp=_STAMP,
            )
        assert refused(still.value).code == "UNSANDBOXED"
        sif = grant / "env.sif"
        singular = plan(
            "singularity",
            ["tool-not-spawned"],
            image=str(sif),
            jail=jail,
            timestamp=_STAMP,
        )
        assert singular.image == str(sif.resolve())
        custom = plan(
            "singularity",
            ["tool-not-spawned"],
            image="docker://python:3.11-slim",
            timestamp=_STAMP,
        )
        assert custom.image == "docker://python:3.11-slim"
        docker = plan("docker", ["tool-not-spawned"], image="python:3.11-slim", timestamp=_STAMP)
        assert docker.image == "python:3.11-slim"
        assert plan("docker", ["tool-not-spawned"], timestamp=_STAMP).image == (
            "nousresearch/hermes-sandbox:desktop"
        )
        assert plan(
            "modal",
            ["tool-not-spawned"],
            credential_id="modal-cred-1",
            timestamp=_STAMP,
        ).image == "nousresearch/hermes-sandbox:desktop"
        assert plan(
            "vercel",
            ["tool-not-spawned"],
            credential_id="vercel-cred-1",
            timestamp=_STAMP,
        ).image == "vercel/sandbox/universal:latest"
        with pytest.raises(Refuse) as host_path:
            plan(
                "ssh",
                ["tool-not-spawned"],
                host="shell.example.com",
                user="builder",
                credential_id="ssh-cred-1",
                work_dir=str(grant),
                jail=jail,
            )
        assert refused(host_path.value).code == "HOST_PATH"
        with pytest.raises(Refuse) as no_jail:
            plan("local", ["tool-not-spawned"], work_dir=str(grant), jail=None)
        assert refused(no_jail.value).code == "BAD_JAIL"
        with pytest.raises(Refuse) as bad_jail:
            plan("singularity", ["tool-not-spawned"], image=str(sif), jail=object())
        assert refused(bad_jail.value).code == "BAD_JAIL"
        with pytest.raises(Refuse) as local_image:
            plan("local", ["tool-not-spawned"], image="python:3.11")
        assert refused(local_image.value).code == "BAD_IMAGE"
        with pytest.raises(Refuse) as messy:
            plan("docker", ["tool-not-spawned"], image="not an image")
        assert refused(messy.value).code == "BAD_IMAGE"
        with pytest.raises(Refuse) as docker_url:
            plan("docker", ["tool-not-spawned"], image="docker://python:3.11")
        assert refused(docker_url.value).code == "BAD_IMAGE"
        with pytest.raises(Refuse) as docker_path:
            plan("docker", ["tool-not-spawned"], image=str(sif))
        assert refused(docker_path.value).code == "BAD_IMAGE"
        with pytest.raises(Refuse) as outside:
            plan("local", ["tool-not-spawned"], work_dir=str(root / "other"), jail=jail)
        assert refused(outside.value).code == "OUTSIDE_GRANT"
        with pytest.raises(Refuse) as relative:
            plan("local", ["tool-not-spawned"], work_dir="relative/tool", jail=jail)
        assert refused(relative.value).code == "RELATIVE_PATH"
        with pytest.raises(Refuse) as dotdot:
            plan(
                "local",
                ["tool-not-spawned"],
                work_dir=str(grant) + "\\..\\outside",
                jail=jail,
            )
        assert refused(dotdot.value).code == "DOTDOT"
        with pytest.raises(Refuse) as encoded:
            plan(
                "local",
                ["tool-not-spawned"],
                work_dir=str(grant) + "\\%2e%2e\\outside",
                jail=jail,
            )
        assert refused(encoded.value).code == "ENCODED_DOTDOT"
        with pytest.raises(Refuse) as unc:
            plan("local", ["tool-not-spawned"], work_dir="\\\\server\\share", jail=jail)
        assert refused(unc.value).code == "UNC"
        with pytest.raises(Refuse) as file_url:
            plan("local", ["tool-not-spawned"], work_dir="file:///C:/Windows", jail=jail)
        assert refused(file_url.value).code == "FILE_URL"
        with pytest.raises(Refuse) as drive_root:
            plan("local", ["tool-not-spawned"], work_dir="C:\\", jail=jail)
        assert refused(drive_root.value).code == "DRIVE_ROOT"
        with pytest.raises(Refuse) as drive_rel:
            plan("local", ["tool-not-spawned"], work_dir="C:foo", jail=jail)
        assert refused(drive_rel.value).code == "DRIVE_RELATIVE"
        with pytest.raises(Refuse) as stream:
            plan("local", ["tool-not-spawned"], work_dir=str(grant) + ":stream", jail=jail)
        assert refused(stream.value).code == "ALT_STREAM"
        with pytest.raises(Refuse) as trailing:
            plan("local", ["tool-not-spawned"], work_dir=str(grant / "leaf."), jail=jail)
        assert refused(trailing.value).code == "TRAILING_DOT"


def test_text_bounds_and_stamp() -> None:
    with pytest.raises(Refuse) as missing:
        spec(None)
    assert refused(missing.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as oversized:
        spec("n" * 65)
    assert refused(oversized.value).code == "OVERSIZE"
    with pytest.raises(Refuse) as named:
        spec("sk-abcdefgh")
    assert refused(named.value).code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as stamp:
        plan("local", ["tool-not-spawned"], timestamp="now")
    assert refused(stamp.value).code == "BAD_STAMP"
    with pytest.raises(Refuse) as empty_type:
        plan("local", ["tool-not-spawned"], timestamp=None)
    assert refused(empty_type.value).code == "NOT_TEXT"
    with pytest.raises(Refuse) as bad_task:
        plan("local", ["tool-not-spawned"], task_id="porch session")
    assert refused(bad_task.value).code == "BAD_TASK"
    held = plan("local", ["tool-not-spawned"], timestamp="")
    assert held.timestamp == ""
    assert held == plan("local", ["tool-not-spawned"], timestamp="")


def test_proof_refusals_and_flags() -> None:
    proof = issue_proof(backend="docker", proof_id="proof-porch-light", stamp=_STAMP)
    with pytest.raises(Refuse) as local_proof:
        execute(
            "local",
            ["note"],
            timestamp=_STAMP,
            proof=proof,
        )
    assert refused(local_proof.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as flag:
        execute("docker", ["note"], timestamp=_STAMP, proof=True)
    assert refused(flag.value).code == "UNSANDBOXED"
    look = _Lookalike(PROOF_SCHEMA, "docker", "", "proof-porch-light", _STAMP, proof.digest)
    with pytest.raises(Refuse) as alike:
        execute("docker", ["note"], timestamp=_STAMP, proof=look)
    assert refused(alike.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as crossed:
        execute(
            "modal",
            ["note"],
            credential_id="modal-cred-1",
            timestamp=_STAMP,
            proof=proof,
        )
    assert refused(crossed.value).code == "BAD_PROOF"
    with pytest.raises(Refuse) as stale:
        execute("docker", ["note"], timestamp="2026-10-02T00:00:00Z", proof=proof)
    assert refused(stale.value).code == "STALE"
    with pytest.raises(Refuse) as blank_stamp:
        execute("docker", ["note"], timestamp="", proof=proof)
    assert refused(blank_stamp.value).code == "STALE"
    with pytest.raises(Refuse) as pty:
        execute("docker", ["note"], timestamp=_STAMP, proof=proof, pty=True)
    assert refused(pty.value).code == "PTY"
    with pytest.raises(Refuse) as background:
        execute("docker", ["note"], timestamp=_STAMP, proof=proof, background=True)
    assert refused(background.value).code == "BACKGROUND"
    with pytest.raises(Refuse) as bad_flag:
        plan("docker", ["note"], pty="yes")
    assert refused(bad_flag.value).code == "NOT_BOOL"
    with pytest.raises(Refuse) as local_issue:
        issue_proof(backend="local", proof_id="proof-local", stamp=_STAMP)
    assert refused(local_issue.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as docker_cred:
        issue_proof(
            backend="docker",
            credential_id="docker-cred-1",
            proof_id="proof-docker",
            stamp=_STAMP,
        )
    assert refused(docker_cred.value).code == "CREDENTIAL_REFUSED"
    with pytest.raises(Refuse) as ssh_missing:
        issue_proof(backend="ssh", proof_id="proof-ssh", stamp=_STAMP)
    assert refused(ssh_missing.value).code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as bad_id:
        issue_proof(backend="docker", proof_id="-proof", stamp=_STAMP)
    assert refused(bad_id.value).code == "BAD_PROOF"
    with pytest.raises(Refuse) as bad_when:
        issue_proof(backend="docker", proof_id="proof-docker", stamp="now")
    assert refused(bad_when.value).code == "BAD_STAMP"
    with pytest.raises(Refuse) as chain:
        WipeProof(
            schema=PROOF_SCHEMA,
            backend="docker",
            credential_id="",
            proof_id="proof-docker",
            stamp=_STAMP,
            digest="a" * 64,
        )
    assert refused(chain.value).code == "BROKEN_CHAIN"
    other = issue_proof(
        backend="ssh",
        credential_id="ssh-cred-2",
        proof_id="proof-ssh-2",
        stamp=_STAMP,
    )
    with pytest.raises(Refuse) as creds:
        execute(
            "ssh",
            ["note"],
            host="shell.example.com",
            user="builder",
            credential_id="ssh-cred-1",
            timestamp=_STAMP,
            proof=other,
        )
    assert refused(creds.value).code == "CREDENTIAL_MISMATCH"


def test_env_budget_skips_and_keeps_later() -> None:
    porch = _env_token("PORCH", 30)
    card = _env_token("CARD", 30)
    note = _env_token("NOTE", 30)
    names = [porch, card, note, "LAMP", "LIGHT"]
    held = plan("docker", ["note"], env_names=names, timestamp=_STAMP, task_id="porch-env")
    assert _env_at(held.env, 0).admitted is True
    assert _env_at(held.env, 1).admitted is True
    assert _env_at(held.env, 2).name == note
    assert _env_at(held.env, 2).admitted is False
    assert _env_at(held.env, 3).name == "LAMP"
    assert _env_at(held.env, 3).admitted is True
    assert _env_at(held.env, 4).name == "LIGHT"
    assert _env_at(held.env, 4).admitted is False
    admitted = tuple(row.name for row in held.env if row.admitted)
    assert admitted == (porch, card, "LAMP")
    assert sum(len(name) for name in admitted) == ENV_BUDGET
    catalog = snapshot((held,))
    assert rebuild(catalog) == catalog
    with pytest.raises(Refuse) as dup:
        plan("docker", ["note"], env_names=["CARD", "CARD"])
    assert refused(dup.value).code == "DUPLICATE"
    with pytest.raises(Refuse) as bad:
        plan("docker", ["note"], env_names=["card-porch"])
    assert refused(bad.value).code == "BAD_ENV"
    with pytest.raises(Refuse) as count:
        plan("docker", ["note"], env_names=[f"N{i}" for i in range(ENV_LIST_CAP + 1)])
    assert refused(count.value).code == "ENV_COUNT"
    with pytest.raises(Refuse) as unsupported:
        plan("local", ["note"], env_names=["CARD"])
    assert refused(unsupported.value).code == "ENV_UNSUPPORTED"
    with pytest.raises(Refuse) as huge:
        plan("docker", ["note"], env_names=["N" * (ENV_NAME_CAP + 1)])
    assert refused(huge.value).code == "OVERSIZE"
    with pytest.raises(Refuse) as secret:
        plan("docker", ["note"], env_names=["sk-abcdefgh"])
    assert refused(secret.value).code == "SECRET_SHAPE"
    tweaked = (replace(_env_at(held.env, 0), admitted=False),) + held.env[1:]
    with pytest.raises(Refuse) as broken:
        replace(held, env=tweaked)
    assert refused(broken.value).code == "BROKEN_CHAIN"


def test_catalog_and_forged_records() -> None:
    local = plan("local", ["note"], task_id="card-porch", timestamp=_STAMP)
    other = plan("docker", ["note"], task_id="card-lamp", timestamp=_STAMP)
    sealed = snapshot((local, other))
    assert rebuild(sealed) == sealed
    assert _plan_at(sealed.plans, 1).spec.name == "docker"
    with pytest.raises(Refuse) as empty:
        snapshot(())
    assert refused(empty.value).code == "EMPTY"
    with pytest.raises(Refuse) as bad:
        snapshot(["nope"])
    assert refused(bad.value).code == "BAD_PLAN"
    with pytest.raises(Refuse) as dup:
        snapshot((local, replace(other, task_id="card-porch")))
    assert refused(dup.value).code == "DUPLICATE"
    many = tuple(
        plan("local", ["note", str(index)], task_id=f"card-{index}", timestamp=_STAMP)
        for index in range(PLAN_CAP + 1)
    )
    with pytest.raises(Refuse) as count:
        snapshot(many)
    assert refused(count.value).code == "PLAN_COUNT"
    with pytest.raises(Refuse) as chain:
        Catalog(schema=SCHEMA, plans=(local,), chain="f" * 64)
    assert refused(chain.value).code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as wrong:
        rebuild(local)
    assert refused(wrong.value).code == "UNCLASSIFIED"
    base = spec("local")
    with pytest.raises(Refuse) as claimed:
        replace(base, classification="SANDBOXED")
    assert refused(claimed.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as policy:
        replace(base, policy_only=False)
    assert refused(policy.value).code == "UNSANDBOXED"
    with pytest.raises(Refuse) as schema:
        replace(base, schema="cosmos-hermes-terminal_backends/2")
    assert refused(schema.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as remote:
        replace(base, remote=True)
    assert refused(remote.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as raised:
        replace(base, timeout_s=999, requested_timeout_s=999)
    assert refused(raised.value).code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flags:
        replace(base, requested_timeout_s=10_000, clamped=())
    assert refused(flags.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as klass:
        replace(local, classification="UNPROVEN")
    assert refused(klass.value).code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as order:
        TerminalOrder(
            schema=SCHEMA,
            plan=local,
            proof_id="proof-local",
            classification="SANDBOXED",
        )
    assert refused(order.value).code == "UNSANDBOXED"


def test_source_does_not_spawn() -> None:
    text = Path(__file__).with_name("terminal_backends.py").read_text(encoding="utf-8")
    assert "subprocess" not in text
    assert "import pty" not in text
    assert "Popen" not in text
    assert "os.system" not in text
    assert "import socket" not in text
    assert "urllib" not in text
    assert "requests" not in text
    assert "pickle" not in text
    assert "# type: ignore" not in text
