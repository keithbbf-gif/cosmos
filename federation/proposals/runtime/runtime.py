"""Day-one interpreter plan. It does not start a process or use the network.

The Windows embeddable zip is packed into the installer before the
person's clock starts. Expanding that zip is local file work. Fetching
CPython during the two minutes would spend the clock on the network,
so a machine with neither an embed zip nor CPython 3.14 refuses.
Day one does not pip-install a compiler and does not run npm or cargo:
those tools do not fit SOFTWARE_BUDGET_S, and the kernel is the
standard library plus the files the installer already holds.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation.bounds import bound_int, bound_text
from cosmos_federation.errors import Refuse
from cosmos_federation.product import SOFTWARE_BUDGET_S

SCHEMA = "cosmos-federation-runtime/1"

# Filename of the Windows embeddable package (64-bit) listed on
# python.org/downloads/windows for CPython 3.14.8 (2026-09-30).
# Recorded here so the plan names the member. The bytes are not fetched.
EMBED_ZIP = "python-3.14.8-embed-amd64.zip"

_WINDOWS = frozenset({"windows", "win32", "nt"})

# A step whose text names one of these is a plan this slot must not emit.
_BANNED = (
    "download",
    "pip",
    "npm",
    "cargo",
    "compiler",
    "winget",
    "curl",
    "wget",
    "http://",
    "https://",
    "msiexec",
    "rustc",
    "git clone",
    "py install",
    "ensurepip",
)


@dataclass(frozen=True, slots=True)
class Facts:
    """What the installer already observed. Versions are caller data."""

    os_name: str
    py_major: int | None
    py_minor: int | None
    launcher: bool
    embed_present: bool


@dataclass(frozen=True, slots=True)
class Step:
    """One local action and the seconds it is allowed to take."""

    name: str
    seconds: int
    detail: str


def _windows(os_name: str) -> None:
    # The packed artifact is the Windows amd64 embeddable zip.
    # Another OS cannot run that file, and this slot does not fetch a substitute.
    if os_name.strip().lower() not in _WINDOWS:
        raise Refuse("OS_REFUSED", "day-one runtime is the Windows embeddable package")


def _version(major: int | None, minor: int | None) -> tuple[int, int] | None:
    if major is None and minor is None:
        return None
    if major is None or minor is None:
        raise Refuse("BOUND", "py_version")
    return (
        bound_int(major, lo=0, hi=99, name="py_major"),
        bound_int(minor, lo=0, hi=99, name="py_minor"),
    )


def _step(name: str, seconds: int, detail: str) -> Step:
    kept_name = bound_text(name, limit=40, name="step")
    kept_detail = bound_text(detail, limit=200, name="detail")
    kept_seconds = bound_int(seconds, lo=1, hi=SOFTWARE_BUDGET_S, name="seconds")
    blob = f"{kept_name} {kept_detail}".lower()
    if any(token in blob for token in _BANNED):
        raise Refuse("RUNTIME_PLAN", "step is outside the day-one clock")
    return Step(kept_name, kept_seconds, kept_detail)


def _finish(steps: tuple[Step, ...]) -> tuple[Step, ...]:
    # The contract caps the embed path at the software budget. The same
    # cap applies to every plan so the installed-interpreter path cannot
    # grow into a compile either. Key paste sits outside this sum.
    total = sum(step.seconds for step in steps)
    if total > SOFTWARE_BUDGET_S:
        raise Refuse("RUNTIME_BUDGET", "software steps exceed the clock")
    return steps


def _embed_plan() -> tuple[Step, ...]:
    # Unpack only. The zip was sealed into the installer before the
    # clock started, so none of these steps contact python.org.
    return _finish((
        _step(
            "unpack_embed",
            8,
            f"expand packed {EMBED_ZIP} into runtime/python; the zip is already in the installer",
        ),
        _step(
            "pin_pth",
            1,
            "point python314._pth at the unpacked stdlib and the app tree and leave site disabled",
        ),
        _step(
            "probe",
            2,
            "runtime/python/python.exe reports CPython 3.14",
        ),
    ))


def _installed_plan(launcher: bool) -> tuple[Step, ...]:
    # `py -3.14` selects an interpreter that is already installed.
    # It is not `py install`, which would download.
    if launcher:
        how = "select the installed interpreter with py -3.14"
    else:
        how = "select the installed python.exe that is already 3.14"
    return _finish((
        _step("use_installed", 1, how),
        _step("probe", 2, "confirm the selected interpreter is CPython 3.14 or newer"),
    ))


def plan(facts: Facts) -> tuple[Step, ...]:
    """Ordered local steps with integer seconds.

    When the embed zip is already in the installer, the plan unpacks
    that known file and stays at or under SOFTWARE_BUDGET_S. No step
    downloads. When Python was not reported and the zip is absent,
    raise RUNTIME_MISSING instead of fetching an interpreter. A plan
    never pip-installs a compiler and never runs npm or cargo.
    """
    if not isinstance(facts, Facts):
        raise Refuse("BOUND", "facts")
    os_name = bound_text(facts.os_name, limit=32, name="os_name")
    if not isinstance(facts.launcher, bool) or not isinstance(facts.embed_present, bool):
        raise Refuse("BOUND", "facts")
    _windows(os_name)
    version = _version(facts.py_major, facts.py_minor)
    if facts.embed_present:
        # Prefer the packed zip even when a system 3.14 is also present.
        # The zip is one build, named by EMBED_ZIP. A system install may
        # be an older patch, and day one should not depend on it when
        # the installer already carries the runtime.
        return _embed_plan()
    if version is None:
        raise Refuse(
            "RUNTIME_MISSING",
            "no CPython version was reported and the embed zip is not packed",
        )
    major, minor = version
    if major == 3 and minor >= 14:
        return _installed_plan(facts.launcher)
    if major == 3 and minor < 14:
        raise Refuse(
            "RUNTIME_TOO_OLD",
            "installed CPython is below 3.14 and the embed zip is not packed",
        )
    raise Refuse(
        "RUNTIME_UNSUPPORTED",
        "installed CPython is outside the 3.14 line and the embed zip is not packed",
    )


__all__ = [
    "EMBED_ZIP",
    "SCHEMA",
    "Facts",
    "Step",
    "plan",
]
