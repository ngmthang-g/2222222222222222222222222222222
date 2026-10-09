"""S21 / E01: one-instance Windows named mutex lifecycle guard.

E01 original EXE evidence: CreateMutexW, GetLastError and exact
"TLMTool_SingleInstance" name. Original duplicate-instance message and
the exact compiled numeric error comparison remain UNKNOWN.

S21 uses documented Win32 ERROR_ALREADY_EXISTS=183 (LOCAL implementation),
bInitialOwner=False and CloseHandle for lifecycle. A duplicate process
closes its *own newly created handle* immediately, never takes ownership
of, releases, or terminates the first process. This is not authentication.
"""
from __future__ import annotations

import os
from threading import RLock
from typing import Protocol

ORIGINAL_MUTEX_NAME = "TLMTool_SingleInstance"
ERROR_ALREADY_EXISTS = 183  # official Win32 code; original compare UNKNOWN
ORIGINAL_COLLISION_MESSAGE = "UNKNOWN"
ORIGINAL_COMPARISON_NUMBER = "UNKNOWN_STATIC_NOT_RECOVERED"


class InstanceAlreadyRunning(RuntimeError):
    """Another process already holds the single-instance registration."""


class MutexUnavailable(RuntimeError):
    """OS mutex acquisition failed; fail closed instead of allowing two UIs."""


class MutexBackend(Protocol):
    def create(self, name: str) -> tuple[int, int]: ...
    def close(self, handle: int) -> bool: ...


class Win32MutexBackend:
    """Real kernel32 CreateMutexW/GetLastError/CloseHandle; Windows only."""

    def __init__(self):
        if os.name != "nt":
            raise OSError("Win32 named mutex requires Windows")
        import ctypes
        from ctypes import wintypes
        self._ctypes = ctypes
        self._kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create = self._kernel.CreateMutexW
        self._create.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self._create.restype = wintypes.HANDLE
        self._close = self._kernel.CloseHandle
        self._close.argtypes = [wintypes.HANDLE]
        self._close.restype = wintypes.BOOL

    def create(self, name: str) -> tuple[int, int]:
        # ctypes.get_last_error() returns the captured GetLastError result
        # immediately after CreateMutexW (use_last_error=True).
        handle = self._create(None, False, name)
        error = self._ctypes.get_last_error()
        return int(handle or 0), int(error)

    def close(self, handle: int) -> bool:
        return bool(self._close(handle))


class SingleInstanceMutex:
    """One live handle per guard, explicit idempotent close on every path.

    The default name matches the original EXE. Unit and native Windows
    process tests MUST inject a unique test-only name instead.
    """

    def __init__(self, name: str = ORIGINAL_MUTEX_NAME,
                 backend: MutexBackend | None = None):
        if not isinstance(name, str) or not name.strip() or "\x00" in name:
            raise ValueError("INVALID_MUTEX_NAME")
        self.name = name
        self._backend = backend
        self._handle = 0
        self._lock = RLock()

    @property
    def acquired(self) -> bool:
        with self._lock:
            return bool(self._handle)

    def acquire(self) -> bool:
        """True only when registration is newly won.

        Duplicate -> close this process's duplicate handle and raise.
        Any other failure -> close residual handle and fail closed.
        Repeated acquire on the SAME object is idempotent.
        """
        with self._lock:
            if self._handle:
                return True
            if self._backend is None:
                self._backend = Win32MutexBackend()
            try:
                handle, error = self._backend.create(self.name)
            except Exception as exc:
                raise MutexUnavailable("MUTEX_CREATE_FAILED") from exc

            if handle <= 0 or error not in (0, ERROR_ALREADY_EXISTS):
                if handle:
                    try:
                        self._backend.close(handle)
                    except Exception:
                        pass
                raise MutexUnavailable("MUTEX_UNAVAILABLE")
            if error == ERROR_ALREADY_EXISTS:
                try:
                    closed = self._backend.close(handle)
                except Exception as exc:
                    raise MutexUnavailable("DUPLICATE_HANDLE_CLOSE_FAILED") from exc
                if not closed:
                    raise MutexUnavailable("DUPLICATE_HANDLE_CLOSE_FAILED")
                raise InstanceAlreadyRunning("INSTANCE_ALREADY_RUNNING")

            self._handle = handle
            return True

    def close(self) -> None:
        with self._lock:
            handle = self._handle
            if not handle:
                return
            # Do not silently re-mark a failed release as clean.
            if not self._backend.close(handle):
                raise MutexUnavailable("MUTEX_HANDLE_CLOSE_FAILED")
            self._handle = 0

    def __enter__(self) -> SingleInstanceMutex:
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
