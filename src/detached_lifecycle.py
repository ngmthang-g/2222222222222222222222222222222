"""S74 C14 owner-thread lifecycle of an EXPLICIT S73 detached scan.

Original C14 documents rebuilding on changes to the game window list,
independent of Start visibility. This internal controller composes the
existing verified S70 host, S72 observer and S73 on-demand reader.

It DOES NOT invent C14 scanning interval, detached tile positions, auto-open
policy, Tk user-facing controls, game inputs, role/HP memory or signed Info.
The caller is separately responsible for triggering scans and providing
evidence-backed native placements before invoking host.open/render.

No scan result can silently leave an obsolete S70 DWM host visible once a
new source identity list is *consumed*. Cleanup failure is a hard latch.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable

from detached_list_observer import C14DetachedListObserver
from detached_one_shot_scanner import C14DetachedOneShotScanner
from detached_host import C14DetachedHost


@dataclass(frozen=True)
class C14LifecycleResult:
    code: str
    identities: tuple[tuple[int, int], ...] = ()


class C14DetachedLifecycle:
    """Tk OWNER THREAD ONLY. No new Tk timers, control widgets or native APIs.

    Construction is side-effect free. The host is never opened/rendered here:
    only a verified existing host is CLOSED when S72 changes or revokes
    identities. Failed native cleanup latches FAIL_CLOSED until shutdown.
    """

    def __init__(
        self,
        scanner: C14DetachedOneShotScanner,
        host: C14DetachedHost,
    ) -> None:
        if not isinstance(scanner, C14DetachedOneShotScanner):
            raise TypeError("S73 independent scanner required")
        if not isinstance(host, C14DetachedHost):
            raise TypeError("S70 native detached host required")
        self._scanner = scanner
        self._host = host
        self._owner_thread = threading.get_ident()
        self._observer = C14DetachedListObserver(host.close)
        self._processed_revision: int | None = None
        self._closed = False
        self._faulted = False

    @property
    def identities(self) -> tuple[tuple[int, int], ...]:
        return self._observer.identities

    @property
    def faulted(self) -> bool:
        return self._faulted

    def _gate(self) -> str | None:
        if threading.get_ident() != self._owner_thread:
            return "WRONG_TK_THREAD"
        if self._closed:
            return "CLOSED"
        if self._faulted:
            return "NATIVE_CLEANUP_FAILED_LOCKED"
        return None

    @staticmethod
    def _authorized(allowed: Callable[[], bool]) -> bool:
        try:
            return callable(allowed) and allowed() is True
        except Exception:
            return False

    def _invalidate(self, code: str, *, stop_worker: bool) -> C14LifecycleResult:
        if stop_worker:
            self._scanner.revoke()
        self._processed_revision = None
        result = self._observer.reset()
        if result.code == "RENDERER_CLEANUP_FAILED":
            self._faulted = True
            return C14LifecycleResult("NATIVE_CLEANUP_FAILED_LOCKED")
        return C14LifecycleResult(code)

    def request_scan(
        self, *, max_windows: int, allowed: Callable[[], bool],
    ) -> C14LifecycleResult:
        gate = self._gate()
        if gate:
            return C14LifecycleResult(gate)
        if not self._authorized(allowed):
            return self._invalidate("PERMISSION_NOT_VERIFIED_OR_REVOKED", stop_worker=True)
        if type(max_windows) is not int or max_windows <= 0:
            return self._invalidate("NO_VERIFIED_WINDOW_LIMIT", stop_worker=True)
        result = self._scanner.request(max_windows=max_windows, allowed=allowed)
        if result in ("SCAN_STARTED", "SCAN_BUSY"):
            return C14LifecycleResult(result, self._observer.identities)
        # S73 may revoke on a permission race or failure.
        return self._invalidate(result, stop_worker=True)

    def consume_scan(
        self, *, max_windows: int, allowed: Callable[[], bool],
    ) -> C14LifecycleResult:
        gate = self._gate()
        if gate:
            return C14LifecycleResult(gate)
        if not self._authorized(allowed):
            return self._invalidate("PERMISSION_NOT_VERIFIED_OR_REVOKED", stop_worker=True)
        if type(max_windows) is not int or max_windows <= 0:
            return self._invalidate("NO_VERIFIED_WINDOW_LIMIT", stop_worker=True)
        state = self._scanner.read()
        if state.code in ("IDLE", "SCANNING"):
            return C14LifecycleResult(state.code, self._observer.identities)
        if state.code != "READY":
            return self._invalidate("SCAN_INVALIDATED_" + state.code, stop_worker=True)
        snap = state.snapshot
        # Recheck CURRENT verified entitlement cap, even for an identical
        # already-consumed scan revision. A reduced cap cannot preserve DWM.
        if not snap.valid or len(snap.windows) > max_windows:
            return self._invalidate("OVER_VERIFIED_LIMIT_OR_INVALID_CACHE", stop_worker=True)
        if self._processed_revision == snap.revision:
            return C14LifecycleResult("NO_NEW_SCAN", self._observer.identities)
        result = self._observer.observe(
            snap, max_windows=max_windows, allowed=allowed)
        if result.code == "RENDERER_CLEANUP_FAILED":
            self._faulted = True
            self._scanner.revoke()
            return C14LifecycleResult("NATIVE_CLEANUP_FAILED_LOCKED")
        if result.code in ("LIST_CHANGED", "UNCHANGED"):
            self._processed_revision = snap.revision
            return C14LifecycleResult(result.code, result.current)
        # Invalid/expired/unverified snapshots cannot retain old native DWM.
        self._scanner.revoke()
        self._processed_revision = None
        return C14LifecycleResult(result.code)

    def revoke(self) -> C14LifecycleResult:
        gate = self._gate()
        if gate:
            return C14LifecycleResult(gate)
        return self._invalidate("REVOKED", stop_worker=True)

    def shutdown(self) -> C14LifecycleResult:
        if threading.get_ident() != self._owner_thread:
            return C14LifecycleResult("WRONG_TK_THREAD")
        if self._closed:
            return C14LifecycleResult("CLOSED")
        self._closed = True
        self._scanner.shutdown()
        observed = self._observer.shutdown()
        # Host must be PERMANENTLY closed even if observer's temporary
        # host.close failed. Native errors remain explicit, not 'CLOSED'.
        try:
            ended = self._host.shutdown()
        except Exception:
            self._faulted = True
            return C14LifecycleResult("CLOSED_NATIVE_CLEANUP_FAILED")
        if (self._faulted or observed.code == "RENDERER_CLEANUP_FAILED"
                or "FAILED" in ended.code
                or ended.code == "WRONG_TK_THREAD"):
            self._faulted = True
            return C14LifecycleResult("CLOSED_NATIVE_CLEANUP_FAILED")
        return C14LifecycleResult("CLOSED")
