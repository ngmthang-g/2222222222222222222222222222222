"""S63 C07 original 1-second Auto tiler scheduling prerequisite.

Original binary proves _auto_tile_loop has a one-second cadence and runs
only while auto_tile_active=True. Exact first tick timing, mode transitions,
geometry and error handling are UNKNOWN. This is only a revocable Tk
scheduler for a future, fully verified real _auto_tile_windows operation.
It never moves game HWNDs, adds a UI, invokes game input or grants a license.
"""
from __future__ import annotations

AUTO_TILE_LOOP_INTERVAL_MS = 1000


class C07AutoTileClock:
    """Single Tk-after handle, epoch-cancelled; only test/verified caller may start.

    on_tick is an already authenticated real tiler operation supplied later.
    No default dummy callback is allowed. Fail-closed stop if callback errors.
    This safe error policy is local, NOT an upstream branch reconstruction.
    """

    def __init__(self, owner, *, on_tick, allowed):
        if not callable(on_tick) or not callable(allowed):
            raise TypeError("A real callable operation and authorization gate are required")
        self.owner = owner
        self.on_tick = on_tick
        self.allowed = allowed
        self.auto_tile_active = False
        self._auto_tile_id = None
        self._epoch = 0
        self._closed = False
        self.last_error = None
        self.tick_count = 0

    def start(self) -> bool:
        if self._closed or self.auto_tile_active or not self.allowed():
            return False
        self._epoch += 1
        self.auto_tile_active = True
        self.last_error = None
        self._schedule(self._epoch)
        return self.auto_tile_active

    def _schedule(self, epoch: int) -> None:
        if self._closed or not self.auto_tile_active or self._epoch != epoch:
            return
        try:
            self._auto_tile_id = self.owner.after(
                AUTO_TILE_LOOP_INTERVAL_MS, lambda: self._tick(epoch))
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            self.last_error = type(exc).__name__
            self.stop()

    def _tick(self, epoch: int) -> None:
        if self._closed or not self.auto_tile_active or self._epoch != epoch:
            return
        self._auto_tile_id = None
        if not self.allowed():
            self.stop()
            return
        try:
            self.on_tick()
        except Exception as exc:
            self.last_error = type(exc).__name__
            self.stop()
            return
        self.tick_count += 1
        if not self.allowed():
            self.stop()
            return
        if self._epoch == epoch and self.auto_tile_active and not self._closed:
            self._schedule(epoch)

    def stop(self) -> bool:
        was_active = self.auto_tile_active or self._auto_tile_id is not None
        self._epoch += 1
        self.auto_tile_active = False
        ident, self._auto_tile_id = self._auto_tile_id, None
        if ident is not None:
            try:
                self.owner.after_cancel(ident)
            except (RuntimeError, ValueError, TypeError, AttributeError):
                pass
        return was_active

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.stop()
