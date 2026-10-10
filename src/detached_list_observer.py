"""S72 C14 detached HWND/PID list-change observer, no fabricated timer/UI.

Original C14 proves detached preview maintenance on game-window list change,
independent of Start tab visibility. Exact C14 cadence, order comparison,
tile rectangles and auto-open lifecycle remain UNKNOWN.

This observes separately SUPPLIED S09 immutable snapshots on their owner
thread. It neither owns nor starts the Start-only 2s Tk poller/3s producer.
An independent authorized source must publish those snapshots. A change,
revocation or invalid cache requests fail-closed release of old previews.
It NEVER rebuilds/renders without a separately authenticated placement.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable

from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

Identity = tuple[int, int]


@dataclass(frozen=True)
class DetachedObservation:
    code: str
    current: tuple[Identity, ...] = ()
    previous: tuple[Identity, ...] = ()
    changed: bool = False


class C14DetachedListObserver:
    """Tk-owner-thread C14 change gate; never schedules a Tk timer itself.

    invalidate_preview must clear DWM/session or close the detached host on
    the SAME Tk thread, before a new list can be accepted. A native cleanup
    exception or reported *_FAILED result explicitly prevents acceptance.
    Comparisons use ordered HWND/PID tuples as a conservative S72 policy,
    NOT claimed original Python list equality semantics.
    """

    def __init__(self, invalidate_preview: Callable[[], object]):
        if not callable(invalidate_preview):
            raise TypeError("Native preview invalidation callback required")
        self._invalidate_preview = invalidate_preview
        self._owner_thread = threading.get_ident()
        self._current: tuple[Identity, ...] | None = None
        self._revision: int | None = None
        self._closed = False

    @property
    def identities(self) -> tuple[Identity, ...]:
        return self._current or ()

    @property
    def closed(self) -> bool:
        return self._closed

    def _clear(self, code: str, *, reset_revision: bool = False) -> DetachedObservation:
        previous = self._current or ()
        self._current = None
        if reset_revision:
            self._revision = None
        try:
            outcome = self._invalidate_preview()
            outcome_code = getattr(outcome, "code", "")
            if isinstance(outcome_code, str) and (
                "FAILED" in outcome_code or outcome_code == "WRONG_TK_THREAD"
            ):
                return DetachedObservation("RENDERER_CLEANUP_FAILED", previous=previous)
        except Exception:
            return DetachedObservation("RENDERER_CLEANUP_FAILED", previous=previous)
        return DetachedObservation(code, previous=previous)

    def observe(
        self, snapshot: WindowSnapshot, *,
        max_windows: int,
        allowed: Callable[[], bool],
    ) -> DetachedObservation:
        if threading.get_ident() != self._owner_thread:
            return DetachedObservation("WRONG_TK_THREAD")
        if self._closed:
            return DetachedObservation("CLOSED")
        if not callable(allowed):
            return self._clear("PERMISSION_NOT_VERIFIED")
        try:
            if not allowed():
                return self._clear("PERMISSION_REVOKED")
        except Exception:
            return self._clear("PERMISSION_NOT_VERIFIED")

        if type(max_windows) is not int or max_windows <= 0:
            return self._clear("NO_VERIFIED_WINDOW_LIMIT")
        if (not isinstance(snapshot, WindowSnapshot) or not snapshot.valid
                or type(snapshot.revision) is not int
                or snapshot.revision < 0):
            return self._clear("INVALID_CACHE")
        if self._revision is not None and snapshot.revision < self._revision:
            # No stale producer epoch may resurrect a DWM destination.
            return self._clear("STALE_REVISION")
        if len(snapshot.windows) > max_windows:
            return self._clear("OVER_VERIFIED_LIMIT")

        current = []
        seen: set[int] = set()
        for window in snapshot.windows:
            if (not isinstance(window, GameWindow)
                    or type(window.hwnd) is not int or window.hwnd <= 0
                    or type(window.pid) is not int or window.pid <= 0
                    or window.hwnd in seen
                    or not is_game_candidate(
                        window.process_name, window.class_name, window.title)):
                return self._clear("INVALID_OR_AMBIGUOUS_CACHE")
            seen.add(window.hwnd)
            current.append((window.hwnd, window.pid))
        identities = tuple(current)
        if self._revision == snapshot.revision and self._current is not None:
            if identities != self._current:
                return self._clear("REVISION_IDENTITY_CONFLICT")
        if identities == self._current:
            self._revision = snapshot.revision
            return DetachedObservation("UNCHANGED", current=identities)
        # ALWAYS remove stale registrations before observing new HWND/PID.
        previous = self._current or ()
        cleared = self._clear("RENDERER_INVALIDATED")
        if cleared.code != "RENDERER_INVALIDATED":
            return cleared
        try:
            if not allowed():
                return DetachedObservation("PERMISSION_REVOKED", previous=previous)
        except Exception:
            return DetachedObservation("PERMISSION_NOT_VERIFIED", previous=previous)
        self._current = identities
        self._revision = snapshot.revision
        return DetachedObservation("LIST_CHANGED", identities, previous, True)

    def reset(self) -> DetachedObservation:
        """Explicit producer lifetime reset; never infer a new epoch from ticks."""
        if threading.get_ident() != self._owner_thread:
            return DetachedObservation("WRONG_TK_THREAD")
        if self._closed:
            return DetachedObservation("CLOSED")
        return self._clear("RESET", reset_revision=True)

    def shutdown(self) -> DetachedObservation:
        if threading.get_ident() != self._owner_thread:
            return DetachedObservation("WRONG_TK_THREAD")
        if self._closed:
            return DetachedObservation("CLOSED")
        self._closed = True
        return self._clear("CLOSED", reset_revision=True)
