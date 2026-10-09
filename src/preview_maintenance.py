"""S13: bounded Tk cache-only C04 embedded preview maintenance scheduler.

The original TLM has adaptive 800/2000ms maintenance cadence and threshold 6.
Its exact equality comparison at 6 is *not* recovered. Here 6 uses 2000ms
as an explicitly chosen conservative S13 policy, not claimed original parity.

NO video frame polling/FPS, EnumWindows, game-process memory, Tk worker access,
server authority, feature control, detached mode, or Proxy functionality.
"""
from __future__ import annotations

from typing import Callable
from start_polling import WindowSnapshot

SHORT_MAINTENANCE_MS = 800
LONG_MAINTENANCE_MS = 2000
ORIGINAL_SWITCH_CONSTANT = 6
BOUNDARY_AT_SIX = "S13_CONSERVATIVE_LONG_NOT_ORIGINAL_PROVEN"


def maintenance_delay_ms(account_count: int) -> int:
    """Adapt Tk housekeeping, NOT DWM compositor FPS.

    C04 proves threshold literal 6, but NOT whether original used < or <=.
    Choosing >=6 as long mode favors bounded UI work in ambiguity.
    """
    if not isinstance(account_count, int) or isinstance(account_count, bool) or account_count < 0:
        raise ValueError("nonnegative integer window count required")
    return SHORT_MAINTENANCE_MS if account_count < ORIGINAL_SWITCH_CONSTANT else LONG_MAINTENANCE_MS


class TkPreviewMaintenance:
    """A cancelable, selected-tab-only Tk scheduler reading existing S09 cache.

    Exact cache comparison/time-to-refresh and original HP extraction are out
    of scope until source/game evidence exists. The callback receives only
    immutable worker-produced snapshot data, never an inferred game window.
    """

    def __init__(self, root, producer, on_tick: Callable[[WindowSnapshot], None]):
        self.root = root
        self.producer = producer
        self.on_tick = on_tick
        self._active = False
        self._closed = False
        self._generation = 0
        self._after_id = None
        self.cycles = 0
        self.last_delay_ms = None

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> None:
        if self._active or self._closed:
            return
        self._active = True
        self._generation += 1
        # Native preview is already triggered by S09 poll/60ms geometry events.
        # Start housekeeping at the next real maintenance cadence, not 0ms.
        self._schedule(SHORT_MAINTENANCE_MS, self._generation)

    def _schedule(self, delay: int, generation: int) -> None:
        if not self._active or self._closed or generation != self._generation:
            return
        self.last_delay_ms = delay
        try:
            self._after_id = self.root.after(delay, lambda: self._tick(generation))
        except Exception:
            # Destroyed Tk tree: never resume callbacks in the background.
            self.stop()

    def _tick(self, generation: int) -> None:
        if not self._active or self._closed or generation != self._generation:
            return
        self._after_id = None
        count = 0
        try:
            snap = self.producer.read_snapshot()  # O(1), no EnumWindows on Tk
            if not isinstance(snap, WindowSnapshot):
                raise TypeError("Producer returned non-WindowSnapshot")
            self.cycles += 1
            self.on_tick(snap)
            count = len(snap.windows) if snap.valid else 0
        except Exception:
            # A broken snapshot/callback must not retain an indefinitely stale
            # window list or create a tight retry loop. S09 handles discovery.
            self.stop()
            return
        if self._active and generation == self._generation:
            self._schedule(maintenance_delay_ms(count), generation)

    def stop(self) -> None:
        if not self._active:
            return
        self._active = False
        self._generation += 1
        token, self._after_id = self._after_id, None
        if token is not None:
            try:
                self.root.after_cancel(token)
            except Exception:
                pass
        self.last_delay_ms = None

    def shutdown(self) -> None:
        self.stop()
        self._closed = True
