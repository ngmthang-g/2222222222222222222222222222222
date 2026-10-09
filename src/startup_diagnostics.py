"""S22 E01 bounded early Python startup diagnostics; NO auth/GUI grant.

Original E01 fingerprints: debug_logger.setup, faulthandler.enable,
crash_fault.log and threading.excepthook. The original logger's formatting,
file location and startup ordering are UNKNOWN. S22 local policy: create
a private writable crash_fault.log under LOCALAPPDATA/TLMTool, or use a
TEST-OWNED explicitly supplied path. Never fabricate debug_logger source,
send reports to a server, or invoke os._exit.

faulthandler and threading.excepthook are process-global. This context
restores the prior thread hook and only disables faulthandler if it was not
already active before entering. A pre-existing faulthandler destination is
left untouched, not silently overwritten.
"""
from __future__ import annotations

import faulthandler
import os
from pathlib import Path
import sys
import threading
import traceback
from types import TracebackType

ORIGINAL_CRASH_LOG_BASENAME = "crash_fault.log"
ORIGINAL_DEBUG_LOGGER_SETUP = "RECOVERED_CONSTANT_ONLY_NOT_REBUILT"
ORIGINAL_LOG_FORMAT = "UNKNOWN"
ORIGINAL_LOG_DIRECTORY = "UNKNOWN_S22_LOCALAPPDATA_POLICY"


class DiagnosticSetupError(RuntimeError):
    """Crash diagnostics cannot be prepared; caller must fail closed."""


def crash_log_path(base: str | Path | None = None) -> Path:
    """Reconstructed local path policy, NOT verified original directory."""
    if base is not None:
        return Path(base) / ORIGINAL_CRASH_LOG_BASENAME
    home = os.environ.get("LOCALAPPDATA")
    if not home:
        home = str(Path.home())
    return Path(home) / "TLMTool" / ORIGINAL_CRASH_LOG_BASENAME


class StartupDiagnostics:
    """Opt-in, balanced early diagnostics lifecycle, no global on import.

    This is intended around the real authorized Start GUI lifecycle, inside
    the already-held S21 instance mutex. It never changes Info permissions.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else crash_log_path()
        self._file = None
        self._old_thread_hook = None
        self._installed_hook = None
        self._owns_fault_handler = False
        self._active = False
        self._lock = threading.RLock()

    @property
    def active(self) -> bool:
        with self._lock:
            return self._active

    def _thread_exception(self, args) -> None:
        with self._lock:
            target = self._file
            if target is not None and not target.closed:
                try:
                    print("S22 THREAD_EXCEPTION", file=target)
                    traceback.print_exception(
                        args.exc_type, args.exc_value,
                        args.exc_traceback, file=target)
                    target.flush()
                except Exception:
                    pass
            previous = self._old_thread_hook
        # Do not silently suppress user/application's previous hook.
        if previous is not None:
            previous(args)

    def record_exception(self, exc: BaseException) -> None:
        """Record exception raised by the startup path, then re-raise it."""
        with self._lock:
            if not self._active or self._file is None:
                return
            print("S22 STARTUP_EXCEPTION", file=self._file)
            traceback.print_exception(
                type(exc), exc, exc.__traceback__, file=self._file)
            self._file.flush()

    def start(self) -> "StartupDiagnostics":
        with self._lock:
            if self._active:
                return self
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                # Opening the actual file also proves writability before
                # installing process-global hooks.
                self._file = self.path.open("a", encoding="utf-8")
                self._file.flush()
                if not faulthandler.is_enabled():
                    faulthandler.enable(file=self._file, all_threads=True)
                    self._owns_fault_handler = True
                self._old_thread_hook = threading.excepthook
                self._installed_hook = self._thread_exception
                threading.excepthook = self._installed_hook
                self._active = True
                return self
            except Exception as exc:
                # No stale global hook/file is allowed on partial setup.
                if self._installed_hook is not None and (
                        threading.excepthook is self._installed_hook):
                    threading.excepthook = self._old_thread_hook
                if self._owns_fault_handler:
                    faulthandler.disable()
                    self._owns_fault_handler = False
                if self._file is not None:
                    self._file.close()
                    self._file = None
                self._installed_hook = None
                self._old_thread_hook = None
                raise DiagnosticSetupError("STARTUP_DIAGNOSTICS_UNAVAILABLE") from exc

    def close(self) -> None:
        with self._lock:
            if not self._active:
                return
            # Only restore the hook when we are still the owner. A later
            # independently installed hook must never be clobbered.
            if threading.excepthook is self._installed_hook:
                threading.excepthook = self._old_thread_hook
            self._installed_hook = None
            self._old_thread_hook = None
            if self._owns_fault_handler:
                faulthandler.disable()
                self._owns_fault_handler = False
            if self._file is not None:
                try:
                    self._file.flush()
                finally:
                    self._file.close()
                    self._file = None
            self._active = False

    def __enter__(self) -> "StartupDiagnostics":
        return self.start()

    def __exit__(self, kind: type[BaseException] | None,
                 value: BaseException | None,
                 tb: TracebackType | None) -> None:
        if value is not None:
            self.record_exception(value)
        self.close()
