"""S125 H12/H03: bounded, read-only Train character sample worker.

The original H12 background worker reads RoleName/MapID and Site-10 occupied
bag slots before Tk-main-thread apply. Actual game memory addresses and a
verified Info-backed native reader are NOT available. Production therefore
has NO character reader by default and never invents a value.

A future independently verified read-only adapter may implement read(window)
returning a TrainCharacterSample. CI uses an explicitly test-only callback.
No Tk method is called from worker. Generation + HWND/PID prevent stale
samples from a previous window/refresh cycle from crossing into new rows.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import threading
from typing import Callable, Protocol, Sequence

from start_windows import GameWindow

_HTML_TAGS = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class TrainCharacterSample:
    hwnd: int
    pid: int
    role_name: str | None = None
    map_id: int | None = None
    bag_slots: int | None = None
    bound_money: int | None = None
    exp: int | None = None


class ReadOnlyTrainCharacterReader(Protocol):
    """Future signed-Info-approved reader; deliberately NO native default."""
    def read(self, window: GameWindow) -> TrainCharacterSample | None: ...


def sanitized_role_name(name: str | None) -> str | None:
    if name is None:
        return None
    if type(name) is not str:
        raise ValueError("INVALID_ROLE_NAME")
    value = _HTML_TAGS.sub("", name).strip()
    return value if value else None


def validated_sample(sample: TrainCharacterSample,
                     window: GameWindow) -> TrainCharacterSample:
    """Original RoleName/MapID/Site10 semantic gate; no fabricated 0."""
    if type(sample) is not TrainCharacterSample or type(window) is not GameWindow:
        raise ValueError("S125_SAMPLE_NOT_VERIFIED_SHAPE")
    if (type(sample.hwnd) is not int or type(sample.pid) is not int
            or sample.hwnd != window.hwnd or sample.pid != window.pid
            or sample.hwnd <= 0 or sample.pid <= 0):
        raise ValueError("STALE_OR_WRONG_HWND_PID_SAMPLE")
    for value in (sample.map_id, sample.bag_slots,
                  sample.bound_money, sample.exp):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("INVALID_REAL_CHARACTER_NUMERIC")
    return TrainCharacterSample(
        hwnd=sample.hwnd, pid=sample.pid,
        role_name=sanitized_role_name(sample.role_name),
        map_id=sample.map_id, bag_slots=sample.bag_slots,
        bound_money=sample.bound_money, exp=sample.exp)


class TrainCharacterSampler:
    """Single bounded background worker; mailbox drained on Tk owner only.

    An absent reader means no work and no data; an exception or None sample
    preserves all previously accepted row values. close() invalidates any
    in-flight generation, so stale responses cannot publish later.
    """

    def __init__(self, reader: ReadOnlyTrainCharacterReader | None = None):
        self.reader = reader
        self._lock = threading.Lock()
        self._epoch = 0
        self._worker: threading.Thread | None = None
        self._pending: tuple[TrainCharacterSample, ...] = ()
        self._closed = False

    @property
    def enabled(self) -> bool:
        return self.reader is not None and not self._closed

    def request(self, windows: Sequence[GameWindow]) -> bool:
        """Called by Tk thread AFTER an authoritative permission/HWND gate."""
        if not self.enabled:
            return False
        if not isinstance(windows, (tuple, list)) or any(
                type(w) is not GameWindow or type(w.hwnd) is not int
                or type(w.pid) is not int or w.hwnd <= 0 or w.pid <= 0
                for w in windows):
            return False
        if not windows:
            return False
        with self._lock:
            if self._closed or (self._worker is not None
                                and self._worker.is_alive()):
                return False
            self._epoch += 1
            epoch = self._epoch
            target = tuple(windows)
            self._pending = ()
            thread = threading.Thread(
                target=self._work, args=(epoch, target),
                name="TLM-Train-H12-ReadOnly-Character-Sampler", daemon=True)
            self._worker = thread
            thread.start()
            return True

    def _work(self, epoch: int, windows: tuple[GameWindow, ...]) -> None:
        accepted = []
        for window in windows:
            with self._lock:
                if self._closed or epoch != self._epoch:
                    return
            try:
                sample = self.reader.read(window)
                if sample is not None:
                    accepted.append(validated_sample(sample, window))
            except Exception:
                # A failed read is UNKNOWN; never pretend zero slots/map/EXP.
                continue
        with self._lock:
            if not self._closed and epoch == self._epoch:
                self._pending = tuple(accepted)

    def drain(self) -> tuple[TrainCharacterSample, ...]:
        """Read one mailbox batch. Caller MUST be the Tk owner/main thread."""
        with self._lock:
            result, self._pending = self._pending, ()
            return result if not self._closed else ()

    def invalidate(self) -> None:
        """Disallow all in-flight responses after PID reuse/permission loss."""
        with self._lock:
            self._epoch += 1
            self._pending = ()

    def shutdown(self) -> None:
        with self._lock:
            self._closed = True
            self._epoch += 1
            self._pending = ()
