"""S199 independent app-shared Win32 discovery source lifetime.

Original Start tab has a 3s native producer and 2s Tk consumer. In the
independent product Party/Train/Login ALSO depend on the SAME real HWND/PID
snapshots. Source review found original TkStartCachePoller._stop_refresh()
calls producer.stop() on leaving Start, invalidating Party's cache.

Keep the original Start tab's Tk/UI lifecycle, but in NEW independent
entrypoint hold a whole-app lease on the single native discovery producer.
This is NOT a game bridge/RoleName reader or original TLM auth bypass.
No patches to historical StartWindowProducer/TkStartCachePoller/Start GUI.
"""
from __future__ import annotations

from start_polling import StartWindowProducer


class IndependentSharedWindowProducer(StartWindowProducer):
    """One independent-program-wide real native HWND/PID cache.

    The stop method is a tab-lease release (no-op), because Start calls
    it when its UI is hidden. Shutdown is the real native-worker stop and
    is called by the independent entrypoint even on app exceptions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shutdown_complete = False

    def start(self) -> bool:
        if self._shutdown_complete:
            return False
        return super().start()

    def stop(self) -> None:
        # Shared native game-window source is leased across independent
        # Party, Login, Train etc. Tk refresh still stops on tab change.
        return None

    def shutdown(self) -> None:
        if self._shutdown_complete:
            return
        self._shutdown_complete = True
        super().stop()
