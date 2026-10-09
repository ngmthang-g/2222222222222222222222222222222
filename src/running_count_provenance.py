"""S30: E04/S29 non-authoritative, freshness-aware process/HWND provenance.

STATIC original emulator audit P01..P06 does not establish which Windows
emulator image(s), clones or ADB serials count as one licensed account.
Never guess image names, treat game-window rows as game-process count, infer
zero emulator count, or convert these observations into launch permission.

This adds two independent process snapshots *around* the existing S08
visible game HWND enumeration to expose churn and observation age.
No Win32 API duplication: uses S29 Toolhelp and S08 EnumWindows readers.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Callable

from login_path import EXE_NAME
from running_count_evidence import (
    NativeWin32ProcessBackend, ProcessSnapshotBackend, find_named_process_pids,
)
from start_windows import (
    GameWindow, NativeWin32Backend, WindowBackend, discover_game_windows,
)

DEFAULT_DIAGNOSTIC_MAX_AGE_SECONDS = 2.0
DEFAULT_DIAGNOSTIC_MAX_SPAN_SECONDS = 2.0


@dataclass(frozen=True)
class RunningSnapshotProvenance:
    """Read-only double Toolhelp + one HWND snapshot, never signed authority."""

    started_at: float
    completed_at: float
    process_pids_before: tuple[int, ...] | None
    visible_windows: tuple[GameWindow, ...] | None
    process_pids_after: tuple[int, ...] | None
    status: str
    error_stage: str | None = None

    @property
    def game_process_count(self) -> int | None:
        if (self.status == "OBSERVATION_CONSISTENT"
                and self.process_pids_after is not None):
            return len(self.process_pids_after)
        return None

    @property
    def visible_game_hwnd_count(self) -> int | None:
        return len(self.visible_windows) if self.visible_windows is not None else None

    @property
    def visible_game_pid_count(self) -> int | None:
        return (len({w.pid for w in self.visible_windows})
                if self.visible_windows is not None else None)

    @property
    def emulator_count(self) -> None:
        return None

    @property
    def combined_running_count(self) -> None:
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False

    def diagnostic_freshness(
        self, now: float, *,
        max_age_seconds: float = DEFAULT_DIAGNOSTIC_MAX_AGE_SECONDS,
        max_span_seconds: float = DEFAULT_DIAGNOSTIC_MAX_SPAN_SECONDS,
    ) -> str:
        """Local TTL policy for evidence display, NEVER a licensing grant.

        A strictly monotonic clock must be used by the producer and consumer.
        The original E04 snapshot age threshold was not recovered.
        """
        if (type(now) not in (int, float) or not math.isfinite(now)
                or type(max_age_seconds) not in (int, float)
                or not math.isfinite(max_age_seconds) or max_age_seconds < 0
                or type(max_span_seconds) not in (int, float)
                or not math.isfinite(max_span_seconds) or max_span_seconds < 0):
            raise ValueError("Finite non-negative diagnostic timing required")
        if (not math.isfinite(self.started_at)
                or not math.isfinite(self.completed_at)
                or self.completed_at < self.started_at
                or now < self.completed_at):
            return "CLOCK_INVALID_OR_REGRESSED"
        if self.status != "OBSERVATION_CONSISTENT":
            return "INCOMPLETE_OR_CHANGING"
        if self.completed_at - self.started_at > max_span_seconds:
            return "OBSERVATION_SPAN_TOO_WIDE"
        if now - self.completed_at > max_age_seconds:
            return "STALE_DIAGNOSTIC"
        return "FRESH_DIAGNOSTIC_ONLY"


def observe_running_provenance(
    *,
    processes: ProcessSnapshotBackend | None = None,
    windows: WindowBackend | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> RunningSnapshotProvenance:
    """Read process→HWND→process; no atomicity guarantee, no emulator count.

    Process snapshots may change and stale HWNDs can be reused. Both are
    explicitly exposed rather than silently treating mismatches as a valid
    total. A stable double scan is only DIAGNOSTIC consistency evidence.
    """
    started = clock()
    process_backend = processes
    window_backend = windows
    before: tuple[int, ...] | None = None
    after: tuple[int, ...] | None = None
    visible: tuple[GameWindow, ...] | None = None
    failed_stage: str | None = None
    try:
        if process_backend is None:
            process_backend = NativeWin32ProcessBackend()
        before = find_named_process_pids(process_backend, EXE_NAME)
    except (OSError, RuntimeError, ValueError, TypeError):
        failed_stage = "PROCESS_BEFORE"
    try:
        if window_backend is None:
            window_backend = NativeWin32Backend()
        visible = discover_game_windows(window_backend)
    except (OSError, RuntimeError, ValueError, TypeError):
        if failed_stage is None:
            failed_stage = "WINDOWS"
    try:
        # A failed first scan does not turn an independent second scan into
        # a valid count; both must succeed and agree to be even diagnostic.
        if process_backend is None:
            process_backend = NativeWin32ProcessBackend()
        after = find_named_process_pids(process_backend, EXE_NAME)
    except (OSError, RuntimeError, ValueError, TypeError):
        if failed_stage is None:
            failed_stage = "PROCESS_AFTER"
    ended = clock()
    if ended < started or not math.isfinite(started) or not math.isfinite(ended):
        code = "CLOCK_INVALID_OR_REGRESSED"
    elif failed_stage is not None:
        code = "SCAN_FAILED"
    elif before != after:
        code = "GAME_PROCESS_SET_CHANGED"
    elif not {w.pid for w in visible or ()}.issubset(set(after or ())):
        code = "HWND_PID_ABSENT_FROM_PROCESS_SNAPSHOT"
    else:
        code = "OBSERVATION_CONSISTENT"
    return RunningSnapshotProvenance(
        started, ended, before, visible, after, code, failed_stage,
    )
