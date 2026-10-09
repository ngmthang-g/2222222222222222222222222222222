"""S23 / E06: scoped stdout/stderr tee into append-only log/tlmtool.log.

Original evidence (E06): debug_logger.setup, _TeeWriter, tlmtool.log,
appending Start/End session markers, stdout+stderr tee, atexit restore,
and oldest-content trimming when MAX_SIZE/KEEP_SIZE are known.

NOT recovered: numerical trim bounds, partial-line timestamp algorithm,
original writer lock/queue, exact session marker timestamp formatting.
S23 LOCAL SAFETY POLICIES are labeled; production disables automatic
trimming until original numeric thresholds have credible evidence.
No extra Python logging framework, no auth change, no game commands.
"""
from __future__ import annotations

import atexit
from datetime import datetime
import os
from pathlib import Path
import sys
import threading
from typing import TextIO

LOG_BASENAME = "tlmtool.log"
LOG_SUBDIR = "log"
SESSION_SEPARATOR = "=" * 60
ORIGINAL_MAX_SIZE = "UNKNOWN"
ORIGINAL_KEEP_SIZE = "UNKNOWN"
ORIGINAL_PARTIAL_LINE_TIMESTAMP = "UNKNOWN"
ORIGINAL_WRITER_SERIALIZATION = "UNKNOWN_S23_LOCAL_MUTEX_FOR_SAFETY"
TRIM_NOTICE = ">>> log trimmed (oldest removed) <<<"


class SessionLogError(RuntimeError):
    """Failed to safely prepare or operate the session log."""


def central_log_path(folder: str | Path | None = None, *,
                     executable: str | Path | None = None,
                     frozen: bool | None = None) -> Path:
    """Original frozen executable directory/log/tlmtool.log; source fallback local."""
    if folder is not None:
        return Path(folder) / LOG_SUBDIR / LOG_BASENAME
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))
    if frozen:
        exe = Path(executable if executable is not None else sys.executable)
        return exe.parent / LOG_SUBDIR / LOG_BASENAME
    # Non-frozen test/development fallback, not a recovered original path.
    return Path(__file__).resolve().parents[1] / LOG_SUBDIR / LOG_BASENAME


def trim_if_needed(path: str | Path, *, max_size: int | None = None,
                   keep_size: int | None = None) -> bool:
    """Explicit test-only trimming; never guess production MAX_SIZE/KEEP_SIZE.

    Original behavior retains newest content, drops oldest lines and records
    TRIM_NOTICE. Thresholds default to None -> disabled, not fake parity.
    """
    if max_size is None and keep_size is None:
        return False
    if (type(max_size) is not int or type(keep_size) is not int
            or max_size <= 0 or not 0 < keep_size < max_size):
        raise ValueError("UNVERIFIED_LOG_TRIM_LIMITS")
    file_path = Path(path)
    if not file_path.exists() or file_path.stat().st_size <= max_size:
        return False
    source = file_path.read_bytes()
    tail = source[-keep_size:]
    # Drop fragment of oldest partial line: prefer full recent lines.
    index = tail.find(b"\n")
    if index >= 0:
        tail = tail[index + 1:]
    # Retain valid UTF-8 records; original decoding handling UNKNOWN.
    trimmed = tail.decode("utf-8", errors="replace")
    tmp = file_path.with_name(file_path.name + ".s23tmp")
    try:
        with tmp.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(TRIM_NOTICE + "\n")
            handle.write(trimmed)
        os.replace(tmp, file_path)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
    return True


class _TeeWriter:
    """Original output stream plus same session file; no native input."""

    def __init__(self, original: TextIO, log_file: TextIO,
                 mutex: threading.RLock):
        self.original = original
        self.file = log_file
        self._mutex = mutex

    @property
    def encoding(self) -> str:
        return getattr(self.original, "encoding", None) or "utf-8"

    @property
    def errors(self):
        return getattr(self.original, "errors", None)

    def write(self, value: str) -> int:
        if not isinstance(value, str):
            raise TypeError("TEE_WRITES_TEXT_ONLY")
        with self._mutex:
            self.original.write(value)
            self.file.write(value)
            return len(value)

    def flush(self) -> None:
        with self._mutex:
            self.original.flush()
            self.file.flush()

    def isatty(self) -> bool:
        return bool(getattr(self.original, "isatty", lambda: False)())

    def writable(self) -> bool:
        return True

    def fileno(self) -> int:
        return self.original.fileno()


class SessionTee:
    """Scoped debug_logger.setup replacement; restores streams on any exit.

    Startup order is bounded S23 POLICY: after single-instance mutex and
    before S22 startup diagnostics. Original exact micro-order UNKNOWN.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else central_log_path()
        self._mutex = threading.RLock()
        self._old_out = None
        self._old_err = None
        self._old_backup_out = None
        self._old_backup_err = None
        self._had_backup_out = False
        self._had_backup_err = False
        self._file = None
        self._out = None
        self._err = None
        self._active = False
        self._registered = False

    @property
    def active(self) -> bool:
        with self._mutex:
            return self._active

    def start(self) -> "SessionTee":
        with self._mutex:
            if self._active:
                return self
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self._file = self.path.open("a", encoding="utf-8")
                # Refuse to stack process-global stdout hooks from another
                # active SessionTee: ownership must be unambiguous.
                if isinstance(sys.stdout, _TeeWriter) or isinstance(sys.stderr, _TeeWriter):
                    raise SessionLogError("TEE_ALREADY_INSTALLED")
                self._old_out, self._old_err = sys.stdout, sys.stderr
                self._had_backup_out = hasattr(sys, "_fl_tee_out")
                self._had_backup_err = hasattr(sys, "_fl_tee_err")
                self._old_backup_out = getattr(sys, "_fl_tee_out", None)
                self._old_backup_err = getattr(sys, "_fl_tee_err", None)
                self._out = _TeeWriter(self._old_out, self._file, self._mutex)
                self._err = _TeeWriter(self._old_err, self._file, self._mutex)
                self._file.write(SESSION_SEPARATOR + "\n")
                self._file.write("=== Start " +
                                 datetime.now().isoformat(timespec="seconds") +
                                 " ===\n")
                self._file.write("exe: " + str(sys.executable) + "\n")
                self._file.write("python: " + sys.version.split("\n")[0] + "\n")
                self._file.flush()
                # Register failure must never install partially owned streams.
                atexit.register(self.close)
                self._registered = True
                sys._fl_tee_out = self._old_out
                sys._fl_tee_err = self._old_err
                sys.stdout, sys.stderr = self._out, self._err
                self._active = True
                return self
            except Exception as exc:
                if sys.stdout is self._out:
                    sys.stdout = self._old_out
                if sys.stderr is self._err:
                    sys.stderr = self._old_err
                self._restore_backup_attributes()
                if self._registered:
                    atexit.unregister(self.close)
                    self._registered = False
                if self._file is not None:
                    self._file.close()
                    self._file = None
                self._out = self._err = None
                self._old_out = self._old_err = None
                raise SessionLogError("TEE_SETUP_FAILED") from exc

    def _restore_backup_attributes(self) -> None:
        if self._had_backup_out:
            sys._fl_tee_out = self._old_backup_out
        elif hasattr(sys, "_fl_tee_out"):
            delattr(sys, "_fl_tee_out")
        if self._had_backup_err:
            sys._fl_tee_err = self._old_backup_err
        elif hasattr(sys, "_fl_tee_err"):
            delattr(sys, "_fl_tee_err")

    def close(self) -> None:
        with self._mutex:
            if not self._active:
                return
            # Own streams only; do not overwrite another component's later
            # stdout/stderr replacement. Still append normal End marker.
            if sys.stdout is self._out:
                sys.stdout = self._old_out
            if sys.stderr is self._err:
                sys.stderr = self._old_err
            self._restore_backup_attributes()
            self._active = False
            try:
                self._out.flush()
                self._err.flush()
                self._file.write("=== End " +
                                 datetime.now().isoformat(timespec="seconds") +
                                 " ===\n")
                self._file.write(SESSION_SEPARATOR + "\n")
                self._file.flush()
            finally:
                if self._registered:
                    atexit.unregister(self.close)
                    self._registered = False
                self._file.close()
                self._file = None
                self._out = self._err = None

    def __enter__(self) -> "SessionTee":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
