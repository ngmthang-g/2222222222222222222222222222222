"""S09 background HWND/PID discovery and Tk Start cache-consumer lifecycle.

C01: ~3-second worker enumeration, ~2-second Start UI cache polling,
stop polling on leaving Start. C02: HWND/PID generation identity.
This module runs NO game commands, memory reads, mouse events, GUI construction,
server entitlement validation or fake window emulation in production.

The worker only publishes an immutable snapshot; the Tk thread alone invokes
registered view callbacks. The original exact threading implementation is not
available; cancellation/race safety here is a bounded reconstruction.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Callable

from start_windows import (
    GameWindow, NativeWin32Backend, WindowBackend,
    WindowDelta, WindowRegistry, discover_game_windows,
)

DISCOVERY_INTERVAL_SECONDS = 3.0
START_UI_POLL_MS = 2000


@dataclass(frozen=True)
class WindowSnapshot:
    revision: int = 0
    windows: tuple[GameWindow, ...] = ()
    valid: bool = False
    captured_at: float | None = None
    error: str | None = None


@dataclass(frozen=True)
class StartCacheEvent:
    snapshot: WindowSnapshot
    delta: WindowDelta


class StartWindowProducer:
    """At most one active native EnumWindows producer; never touch Tk.

    The Win32 backend is constructed IN the worker, not on Tk's UI thread.
    stop() is bounded: a timed Win32 call can finish later, but its result
    cannot publish after the epoch has been invalidated. A restart waits
    until any old worker finishes, preventing two competing native scans.
    """

    def __init__(
        self,
        backend_factory: Callable[[], WindowBackend] = NativeWin32Backend,
        *,
        interval_seconds: float = DISCOVERY_INTERVAL_SECONDS,
        join_timeout: float = 0.2,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if interval_seconds <= 0 or join_timeout < 0:
            raise ValueError("Positive discovery interval and nonnegative join timeout required")
        self._backend_factory = backend_factory
        self._interval = float(interval_seconds)
        self._join_timeout = float(join_timeout)
        self._clock = clock
        self._guard = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event | None = None
        self._epoch = 0
        self._active = False
        self._revision = 0
        self._snapshot = WindowSnapshot()

    def read_snapshot(self) -> WindowSnapshot:
        """Atomic O(1) cache copy; never scans windows and never waits on I/O."""
        with self._guard:
            return self._snapshot

    @property
    def active(self) -> bool:
        with self._guard:
            return self._active

    def start(self) -> bool:
        """Return True if active/started, False while stale worker still running."""
        with self._guard:
            if self._active:
                return True
            if self._thread is not None and self._thread.is_alive():
                return False
            self._epoch += 1
            epoch = self._epoch
            stop_event = threading.Event()
            self._stop_event = stop_event
            self._active = True
            self._revision += 1
            self._snapshot = WindowSnapshot(revision=self._revision)
            self._thread = threading.Thread(
                name="TLM-Start-ReadOnly-Windows",
                target=self._loop,
                args=(epoch, stop_event),
                daemon=True,
            )
            self._thread.start()
            return True

    def stop(self) -> None:
        """Idempotent bounded stop, revoke cached handles immediately."""
        with self._guard:
            self._epoch += 1
            self._active = False
            self._revision += 1
            self._snapshot = WindowSnapshot(revision=self._revision)
            stop_event, thread = self._stop_event, self._thread
            if stop_event is not None:
                stop_event.set()
        # Never indefinitely block the calling Tk thread.
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=self._join_timeout)

    def _publish(
        self,
        epoch: int,
        stop_event: threading.Event,
        windows: tuple[GameWindow, ...],
        error: str | None = None,
    ) -> None:
        with self._guard:
            if not self._active or epoch != self._epoch or stop_event.is_set():
                return
            self._revision += 1
            self._snapshot = WindowSnapshot(
                revision=self._revision,
                windows=windows if error is None else (),
                valid=(error is None),
                captured_at=self._clock(),
                error=error,
            )

    def _loop(self, epoch: int, stop_event: threading.Event) -> None:
        try:
            backend = self._backend_factory()
        except Exception as exc:
            self._publish(epoch, stop_event, (), f"BACKEND_ERROR:{type(exc).__name__}")
            with self._guard:
                if epoch == self._epoch and not stop_event.is_set():
                    self._active = False
            return
        while not stop_event.is_set():
            try:
                observed = discover_game_windows(backend)
                # The snapshot has only immutable GameWindow dataclasses.
                self._publish(epoch, stop_event, observed)
            except Exception as exc:
                # Never expose stale HWND/PID after an enumeration failure.
                self._publish(epoch, stop_event, (), f"ENUMERATION_ERROR:{type(exc).__name__}")
            if stop_event.wait(self._interval):
                break


class TkStartCachePoller:
    """Tk-only 2s cache reader compatible with TabLifecycle _start/_stop_refresh.

    The callback gets C02-safe HWND/PID deltas on the Tk thread. This is a
    callback/service seam, NOT a fabricated original Start page or tab grant.
    """

    def __init__(
        self,
        root: object,
        producer: StartWindowProducer,
        on_event: Callable[[StartCacheEvent], None],
        *,
        interval_ms: int = START_UI_POLL_MS,
    ) -> None:
        if interval_ms <= 0:
            raise ValueError("Positive Tk polling interval required")
        self.root = root
        self.producer = producer
        self.on_event = on_event
        self.interval_ms = int(interval_ms)
        self.registry = WindowRegistry()
        self._active = False
        self._closed = False
        self._generation = 0
        self._after_id: object | None = None
        self._last_revision: int | None = None

    @property
    def active(self) -> bool:
        return self._active

    def _start_refresh(self) -> None:
        if self._closed or self._active:
            return
        self._active = True
        self._generation += 1
        self._last_revision = None
        self.registry.update(())
        # A still-exiting worker is not a reason to block Tk; retry next tick.
        self.producer.start()
        self._schedule(0, self._generation)

    def _schedule(self, delay: int, generation: int) -> None:
        if not self._active or generation != self._generation:
            return
        try:
            self._after_id = self.root.after(delay, lambda: self._tick(generation))
        except Exception:
            # Root may have been destroyed; never schedule retry on it.
            self._stop_refresh()

    def _tick(self, generation: int) -> None:
        if not self._active or generation != self._generation or self._closed:
            return
        self._after_id = None
        if not self.producer.active:
            self.producer.start()
        snap = self.producer.read_snapshot()
        if snap.revision != self._last_revision:
            self._last_revision = snap.revision
            # A failed/unknown snapshot discards all previously bound HWNDs.
            delta = self.registry.update(snap.windows if snap.valid else ())
            self.on_event(StartCacheEvent(snapshot=snap, delta=delta))
        if self._active and generation == self._generation:
            self._schedule(self.interval_ms, generation)

    def _stop_refresh(self) -> None:
        if not self._active:
            return
        self._active = False
        self._generation += 1
        handle, self._after_id = self._after_id, None
        if handle is not None:
            try:
                self.root.after_cancel(handle)
            except Exception:
                # Tk root may already be gone; no more callbacks can be applied.
                pass
        self.registry.update(())
        self._last_revision = None
        self.producer.stop()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._stop_refresh()
        self._closed = True
