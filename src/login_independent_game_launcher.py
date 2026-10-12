"""S188: independent user-click Windows game EXE launcher, no TLM licensing.

Original F04/F05 support selecting the exact "Thần Long  Mobile.exe",
serializing one launch, and PID->HWND handoff. Unlike the original's
suspend+inject and optional proxy path, this deliberately attempts a
NORMAL OS launch with only Windows essential environment variables,
NO original DLL injection, no token/license check, and no F06 login.

Process started != game ready != game authenticated. Source-only until
owner's deferred consolidated native Windows/game acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from queue import Empty, Queue
import subprocess
import threading
import time
from typing import Callable

from login_path import EXE_NAME
from login_pid_window import find_main_window_by_pid
from login_running_process_capacity import count_current_game_processes
from login_safe_env import WINDOWS_ESSENTIAL_CANDIDATES
from login_independent_window_activation import (
    IndependentActivationResult, activate_verified_launched_game,
)

LOCAL_HWND_TIMEOUT_SECONDS = 25.0
LOCAL_POLL_QUANTUM_SECONDS = 0.25


@dataclass(frozen=True)
class IndependentLaunchResult:
    code: str
    pid: int | None = None
    hwnd: int | None = None
    running_game_count_before: int | None = None

    @property
    def process_was_started(self):
        return self.pid is not None and self.code in (
            "WINDOW_VERIFIED", "STARTED_NO_WINDOW_YET",
            "PROCESS_EXITED_BEFORE_WINDOW", "CANCELLED_AFTER_START",
            "HWND_CHECK_FAILED")


def _game_exe(path: str | Path) -> Path:
    if not isinstance(path, (str, Path)):
        raise ValueError("GAME_EXE_PATH_REQUIRED")
    p = Path(path)
    if (p.name != EXE_NAME or not p.is_file() or p.is_symlink()
            or p.parent.is_symlink()):
        raise ValueError("EXACT_SELECTED_GAME_EXE_REQUIRED")
    # Use the user-selected file, not PATH lookup and no shell argument.
    return p.resolve(strict=True)


def local_windows_game_env(source=None):
    """Conservative Windows essentials; not a claimed original F05 whitelist.

    In particular never inherit Python, Conda, inherited proxy hooks, DLL
    injector variables or service tokens, and never fabricate TLM_PROFILE
    without a user-verified original profile value.
    """
    env = os.environ if source is None else source
    if not hasattr(env, "items"):
        raise ValueError("UNSAFE_WINDOWS_ENV_SOURCE")
    result = {}
    seen = set()
    for key, value in env.items():
        if (type(key) is not str or type(value) is not str
                or not key or "\0" in key or "=" in key or "\0" in value):
            raise ValueError("UNSAFE_WINDOWS_ENV_ENTRY")
        folded = key.upper()
        if folded in seen:
            raise ValueError("AMBIGUOUS_WINDOWS_ENV_KEYS")
        seen.add(folded)
        if folded in WINDOWS_ESSENTIAL_CANDIDATES:
            result[key] = value
    if not any(k.upper() == "SYSTEMROOT" for k in result):
        raise ValueError("MISSING_WINDOWS_SYSTEMROOT")
    if not any(k.upper() == "PATH" for k in result):
        raise ValueError("MISSING_WINDOWS_PATH")
    return result


class IndependentGameLaunchController:
    """One normal game EXE launch per click, only one worker in flight.

    Background worker *never touches Tk*. Results are posted through queue.
    Shutdown cancels further polling but NEVER kills a user-created game.
    """

    def __init__(
        self, *, hwnd_finder: Callable[[int], int | None] = find_main_window_by_pid,
        clock: Callable[[], float] = time.monotonic,
    ):
        if not callable(hwnd_finder) or not callable(clock):
            raise ValueError("INVALID_INDEPENDENT_LAUNCH_SERVICES")
        self._find_hwnd = hwnd_finder
        self._clock = clock
        self._stop = threading.Event()
        self._closed = False
        self._lock = threading.Lock()
        self._worker: threading.Thread | None = None
        self._results: Queue[IndependentLaunchResult] = Queue(maxsize=8)
        # Retain actual Popen handle; a naked PID/HWND is insufficient proof
        # after a process exits and Windows recycles numeric identifiers.
        self._owned_process = None
        self._owned_verified_hwnd = None

    def start(self, executable: str | Path) -> bool:
        if os.name != "nt":
            self._post(IndependentLaunchResult("WINDOWS_ONLY"))
            return False
        with self._lock:
            if self._closed or (self._worker is not None and self._worker.is_alive()):
                return False
            try:
                game = _game_exe(executable)
                env = local_windows_game_env()
            except (ValueError, OSError):
                self._post(IndependentLaunchResult("INVALID_GAME_OR_ENV"))
                return False
            self._stop.clear()
            self._owned_process = None
            self._owned_verified_hwnd = None
            self._worker = threading.Thread(
                target=self._launch_once, args=(game, env),
                name="TLM-Independent-Explicit-Game-Start", daemon=True,
            )
            try:
                self._worker.start()
            except (RuntimeError, OSError):
                self._worker = None
                self._post(IndependentLaunchResult("WORKER_START_FAILED"))
                return False
            return True

    def _post(self, result: IndependentLaunchResult):
        try:
            self._results.put_nowait(result)
        except Exception:  # Full queue should not leak process/error reports.
            try:
                self._results.get_nowait()
                self._results.put_nowait(result)
            except Empty:
                pass

    def _launch_once(self, exe: Path, env: dict[str, str]):
        if self._stop.is_set():
            self._post(IndependentLaunchResult("CANCELLED_BEFORE_START"))
            return
        observed = count_current_game_processes()
        if observed.code != "PROCESS_SNAPSHOT_OK":
            self._post(IndependentLaunchResult("PROCESS_SNAPSHOT_UNAVAILABLE"))
            return
        count = observed.running_exe
        if self._stop.is_set():
            self._post(IndependentLaunchResult(
                "CANCELLED_BEFORE_START", running_game_count_before=count))
            return
        # Actual user-click Windows app execution. This does NOT inject,
        # steal credentials, click other windows or perform game login.
        try:
            process = subprocess.Popen(
                [str(exe)], cwd=str(exe.parent), env=env,
                shell=False, close_fds=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, ValueError):
            self._post(IndependentLaunchResult(
                "OS_PROCESS_CREATE_FAILED", running_game_count_before=count))
            return
        pid = process.pid
        if type(pid) is not int or pid <= 0:
            self._post(IndependentLaunchResult(
                "INVALID_CREATED_PID", running_game_count_before=count))
            return
        with self._lock:
            if not self._closed:
                self._owned_process = process
        deadline = self._clock() + LOCAL_HWND_TIMEOUT_SECONDS
        while not self._stop.is_set():
            if process.poll() is not None:
                self._post(IndependentLaunchResult(
                    "PROCESS_EXITED_BEFORE_WINDOW", pid,
                    running_game_count_before=count))
                return
            try:
                hwnd = self._find_hwnd(pid)
            except (OSError, RuntimeError, ValueError, TypeError):
                hwnd = None
            if type(hwnd) is int and hwnd > 0:
                # Keep the genuine live process handle with its observed
                # hwnd. This does NOT establish game login or RoleName.
                with self._lock:
                    if (not self._closed and not self._stop.is_set()
                            and self._owned_process is process
                            and process.poll() is None):
                        self._owned_verified_hwnd = hwnd
                self._post(IndependentLaunchResult(
                    "WINDOW_VERIFIED", pid, hwnd,
                    running_game_count_before=count))
                return
            remaining = deadline - self._clock()
            if remaining <= 0:
                self._post(IndependentLaunchResult(
                    "STARTED_NO_WINDOW_YET", pid,
                    running_game_count_before=count))
                return
            self._stop.wait(min(LOCAL_POLL_QUANTUM_SECONDS, remaining))
        self._post(IndependentLaunchResult(
            "CANCELLED_AFTER_START", pid, running_game_count_before=count))

    @property
    def can_activate_last_window(self) -> bool:
        with self._lock:
            proc = self._owned_process
            hwnd = self._owned_verified_hwnd
            if self._closed or proc is None or hwnd is None:
                return False
        try:
            return proc.poll() is None
        except (OSError, RuntimeError, ValueError):
            return False

    def activate_last_window(self) -> IndependentActivationResult:
        """A user-click-only real native C03 action; never auto-focus."""
        with self._lock:
            proc = self._owned_process
            hwnd = self._owned_verified_hwnd
            if self._closed or proc is None or hwnd is None:
                return IndependentActivationResult(
                    "NO_VERIFIED_LAUNCHED_WINDOW")
        result = activate_verified_launched_game(proc, hwnd)
        if result.code in (
                "LAUNCHED_PROCESS_EXITED", "WINDOW_NOT_CURRENT_GAME",
                "WINDOW_CHANGED_AFTER_ACTIVATE", "LAUNCHED_PROCESS_UNVERIFIED"):
            with self._lock:
                if self._owned_process is proc and self._owned_verified_hwnd == hwnd:
                    self._owned_verified_hwnd = None
        return result

    @property
    def busy(self):
        with self._lock:
            return self._worker is not None and self._worker.is_alive()

    def drain(self) -> tuple[IndependentLaunchResult, ...]:
        rows = []
        try:
            while True:
                rows.append(self._results.get_nowait())
        except Empty:
            pass
        return tuple(rows)

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._stop.set()
            # Closing references is NOT terminating/killing the game.
            self._owned_process = None
            self._owned_verified_hwnd = None
        # No join/block of Tk and importantly NO process.kill/terminate.
