"""S199 read-only original TLM Reader for an ALREADY RUNNING game HWND/PID.

Unlike S196's independent Login own-launched Popen registry, original
Start/Party/Train discover pre-existing legitimate game windows. A
fresh S09 StartWindowProducer snapshot plus live S08 native window identity
and the user's exact selected game path form a fail-closed provenance
fence around S196–S198 original native Reader.

This is a diagnostic/provenance adapter, NOT verified character identity.
An original field layout and plausible name do not automatically grant
online status, Party membership, credentials, sender or gameplay rights.
Heavy real Win32 process reads + SHA256 MUST run in existing background
worker (never on Tk). No original TLM Info/permission/token/Proxy needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable

from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import (
    GameWindow, NativeWin32Backend, is_game_candidate, TITLE_TIMEOUT_MS,
)
from tlm_original_memory_reader_native import (
    TlmOriginalReadProbe, inspect_original_tlm_role_pointer,
)

MAX_START_SNAPSHOT_AGE_SECONDS = 7.0  # safety local, NOT original timer


@dataclass(frozen=True)
class ExistingTlmGameReaderReport:
    code: str
    hwnd: int | None = None
    pid: int | None = None
    revision: int | None = None
    native: TlmOriginalReadProbe | None = None
    role_name_confirmed_for_party: bool = False
    account_authenticated: bool = False
    gameplay_action_authorized: bool = False


class ExistingGameOriginalReader:
    """Background-only existing HWND/PID source gate, never arbitrary PID."""

    def __init__(self, start_producer: StartWindowProducer, *,
                 selected_game_exe: Callable[[], str | Path | None],
                 backend_factory=NativeWin32Backend,
                 clock: Callable[[], float] = time.monotonic):
        if (not isinstance(start_producer, StartWindowProducer)
                or not callable(selected_game_exe)
                or not callable(backend_factory)
                or not callable(clock)):
            raise ValueError("REAL_START_PRODUCER_AND_SELECTED_GAME_REQUIRED")
        self.producer = start_producer
        self.selected_game_exe = selected_game_exe
        self.backend_factory = backend_factory
        self.clock = clock

    def _snapshot(self, window: GameWindow) -> WindowSnapshot | None:
        snap = self.producer.read_snapshot()
        if (type(snap) is not WindowSnapshot or not snap.valid
                or type(snap.revision) is not int
                or snap.revision <= 0
                or type(snap.windows) is not tuple
                or not isinstance(snap.captured_at, (int, float))):
            return None
        # S09 Start periodic reader must be currently active; an old
        # cache copied while Start stopped must not authorize reads.
        if not self.producer.active:
            return None
        age = self.clock() - snap.captured_at
        if not 0 <= age <= MAX_START_SNAPSHOT_AGE_SECONDS:
            return None
        # Exactly ONE HWND/PID membership; arbitrary process PIDs cannot
        # join the reader by a guessed HWND/title.
        if (sum(x.hwnd == window.hwnd and x.pid == window.pid
                for x in snap.windows) != 1
                or len({w.hwnd for w in snap.windows}) != len(snap.windows)
                or len({w.pid for w in snap.windows}) != len(snap.windows)):
            return None
        return snap

    @staticmethod
    def _native_matches(window, native):
        try:
            return (
                type(window) is GameWindow
                and type(window.hwnd) is int and window.hwnd > 0
                and type(window.pid) is int and window.pid > 0
                and tuple(native.enumerate_top_level()).count(window.hwnd) == 1
                and native.is_window(window.hwnd)
                and native.is_visible(window.hwnd)
                and native.process_id(window.hwnd) == window.pid
                and is_game_candidate(
                    native.process_executable(window.pid),
                    native.window_class(window.hwnd),
                    native.title_with_timeout(window.hwnd, TITLE_TIMEOUT_MS))
                and native.is_window(window.hwnd)
                and native.process_id(window.hwnd) == window.pid
            )
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
            return False

    def inspect(self, window: GameWindow) -> ExistingTlmGameReaderReport:
        """Source-only native diagnostic; no Party/Train source promotion."""
        if (type(window) is not GameWindow
                or type(window.hwnd) is not int or window.hwnd <= 0
                or type(window.pid) is not int or window.pid <= 0):
            return ExistingTlmGameReaderReport("INVALID_GAME_WINDOW")
        hwnd, pid = window.hwnd, window.pid

        def report(code, revision=None, result=None):
            return ExistingTlmGameReaderReport(
                code, hwnd, pid, revision, result)

        try:
            first = self._snapshot(window)
            if first is None:
                return report("START_CACHE_MISSING_STALE_OR_AMBIGUOUS")
            exe = self.selected_game_exe()
            if not isinstance(exe, (str, Path)):
                return report("USER_SELECTED_GAME_EXE_REQUIRED", first.revision)
            selected = Path(exe)
            native = self.backend_factory()
            if not self._native_matches(window, native):
                return report("NATIVE_HWND_PID_NOT_VERIFIED", first.revision)

            # The actual original Reader only reads process memory after
            # frozen 2-file SHA256, current process image, module/PE and
            # pointer/session checks. The source is S196–S198, not mock.
            observation = inspect_original_tlm_role_pointer(
                window, selected, backend=native)

            after = self._snapshot(window)
            # C01 refresh creates a new revision every ~3s even when
            # the exact same immutable HWND/PID window set is unchanged.
            # Reject removal/replacement, NOT a no-op cache refresh.
            # Live HWND/PID and source EXE are also re-verified below.
            if (after is None or after.revision < first.revision
                    or after.windows != first.windows):
                return report("START_GAME_WINDOW_SET_CHANGED_DURING_READ")
            selected_after = self.selected_game_exe()
            if (not isinstance(selected_after, (str, Path))
                    or Path(selected_after) != selected):
                return report("GAME_DIRECTORY_CHANGED_DURING_READ")
            if not self._native_matches(window, native):
                return report("NATIVE_HWND_PID_CHANGED_AFTER_READ")
            if observation.status != (
                    "ORIGINAL_ROLE_UTF16_CANDIDATE_NOT_RUNTIME_VERIFIED"):
                return report("ORIGINAL_READER_" + observation.status,
                              first.revision, observation)
            # Important: structurally plausible RoleName string is a
            # diagnostic candidate until real owner Win64/game acceptance.
            # NEVER emit RoleReading to Party by default.
            return report(
                "ORIGINAL_READONLY_CHARACTER_CANDIDATE_UNVERIFIED",
                first.revision, observation)
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError):
            return report("EXISTING_GAME_READ_DIAGNOSTIC_UNAVAILABLE")
