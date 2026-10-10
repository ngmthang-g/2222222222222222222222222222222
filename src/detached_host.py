"""S70 C14 independently owned Tk/Win32 detached topmost host, NO UI toggle.

Only the original C14 host region (0,768,screen_width-450,screen_height-768)
and topmost property are reconstructed. This is an internal owner-thread
primitive, not a complete 'Tách rời' feature. Original item arrangement,
auto-open timing, embedded-preview visibility and closing behavior UNKNOWN.

The caller must explicitly authorize opening and provide a valid live S09
game snapshot plus verified max_windows; saving detached_auto_open=True
alone NEVER triggers this module. Rendering requires separately proven tile
placements and delegates identity/cleanup to S68 C14DetachedDwmSession.
"""
from __future__ import annotations
from dataclasses import dataclass
import os
import threading
from typing import Callable, Sequence

from detached_preview import C14DetachedDwmSession, DetachedRegion, verified_detached_region
from dwm_preview import PreviewPlacement
from layout_windows import NativeLayoutBackend
from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate


def _native_root(hwnd: int) -> int:
    import ctypes
    from ctypes import wintypes as w
    u = ctypes.WinDLL("user32", use_last_error=True)
    fn = u.GetAncestor
    fn.argtypes = (w.HWND, w.UINT)
    fn.restype = w.HWND
    return int(fn(hwnd, 2) or 0)


def _native_is_topmost(hwnd: int) -> bool:
    import ctypes
    from ctypes import wintypes as w
    u = ctypes.WinDLL("user32", use_last_error=True)
    try:
        fn = u.GetWindowLongPtrW
        fn.restype = ctypes.c_ssize_t
    except AttributeError:
        fn = u.GetWindowLongW
        fn.restype = ctypes.c_long
    fn.argtypes = (w.HWND, ctypes.c_int)
    return bool(int(fn(hwnd, -20)) & 0x00000008)  # GWL_EXSTYLE/WS_EX_TOPMOST


@dataclass(frozen=True)
class HostResult:
    code: str
    owner_hwnd: int = 0
    region: DetachedRegion | None = None
    rendered: tuple[int, ...] = ()


class C14DetachedHost:
    """Tk-owner-thread-only host whose teardown owns a separate DWM session.

    Constructor does not open windows or load DWM. Dependencies for unit
    testing are explicit; production defaults read actual Tk desktop size,
    actual Win32 owner HWND/PID/rectangle and actual topmost bit.
    """

    def __init__(self, tk_root, *, windows_backend=None, toplevel_factory=None,
                 resolve_root_hwnd=None, is_topmost=None, session_factory=None):
        self.root = tk_root
        self._thread = threading.get_ident()
        self._windows = windows_backend if windows_backend is not None else NativeLayoutBackend()
        self._toplevel = toplevel_factory
        self._resolve_hwnd = resolve_root_hwnd or _native_root
        self._is_topmost = is_topmost or _native_is_topmost
        self._session_factory = session_factory or C14DetachedDwmSession
        self._owner = None
        self._owner_hwnd = 0
        self._region = None
        self._session = None
        self._closed = False
        # S85: a failed native DWM cleanup forbids C14 refresh/reopen in
        # this owner lifetime; old destination handle state is uncertain.
        self._refresh_cleanup_faulted = False
        # C13 original Đóng xem belongs ONLY to this detached host.
        self._close_view_button = None

    @property
    def owner_hwnd(self) -> int:
        return self._owner_hwnd

    @property
    def active_hwnds(self) -> tuple[int, ...]:
        return self._session.active_hwnds if self._session is not None else ()

    def _on_owner_thread(self) -> bool:
        return threading.get_ident() == self._thread

    def _verified_owner(self) -> bool:
        if self._owner is None or self._region is None or not self._owner_hwnd:
            return False
        b = self._windows
        r = self._region
        try:
            if not self._owner.winfo_exists():
                return False
            return (self._owner_hwnd in set(b.enumerate_top_level())
                    and b.is_window(self._owner_hwnd)
                    and b.is_visible(self._owner_hwnd)
                    and b.process_id(self._owner_hwnd) == os.getpid()
                    and b.window_rect(self._owner_hwnd)
                    == (r.x,r.y,r.x+r.width,r.y+r.height)
                    and self._is_topmost(self._owner_hwnd))
        except (OSError, RuntimeError, ValueError, TypeError):
            return False

    def _source_gate(self, snapshot, max_windows: int) -> str:
        if type(max_windows) is not int or max_windows <= 0:
            return "NO_VERIFIED_WINDOW_LIMIT"
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            return "INVALID_CACHE"
        rows=snapshot.windows
        if not rows:
            return "NO_WINDOWS"
        if len(rows)>max_windows:
            return "OVER_VERIFIED_LIMIT"
        if (any(not isinstance(w,GameWindow) or type(w.hwnd) is not int
                or type(w.pid) is not int or w.hwnd<=0 or w.pid<=0
                or not is_game_candidate(w.process_name,w.class_name,w.title)
                for w in rows)
                or len({w.hwnd for w in rows})!=len(rows)):
            return "INVALID_OR_AMBIGUOUS_CACHE"
        try:
            b=self._windows
            top=set(b.enumerate_top_level())
            for w in rows:
                if (w.hwnd not in top or not b.is_window(w.hwnd)
                        or not b.is_visible(w.hwnd)
                        or b.process_id(w.hwnd)!=w.pid):
                    return "STALE_SOURCE"
                if not is_game_candidate(
                        b.process_executable(w.pid), b.window_class(w.hwnd),
                        b.title_with_timeout(w.hwnd,150)):
                    return "LIVE_SOURCE_NOT_GAME"
        except (OSError,RuntimeError,ValueError,TypeError):
            return "NATIVE_VALIDATION_FAILED"
        return "VALID"

    def open(self, snapshot: WindowSnapshot, *, max_windows: int,
             allowed: Callable[[], bool] = lambda: False) -> HostResult:
        if not self._on_owner_thread():
            return HostResult("WRONG_TK_THREAD")
        if self._closed:
            return HostResult("CLOSED")
        if self._refresh_cleanup_faulted:
            return HostResult("NATIVE_CLEANUP_FAILED_LOCKED")
        if not allowed():
            return HostResult("CANCELLED")
        if self._owner is not None:
            if not self._verified_owner():
                self.close()
                return HostResult("OWNER_INVALIDATED")
            return HostResult("ALREADY_OPEN",self._owner_hwnd,self._region)
        gate=self._source_gate(snapshot,max_windows)
        if gate!="VALID":
            return HostResult(gate)
        try:
            # Physical Tk desktop dimensions, never a guessed or enlarged
            # "virtual test" resolution in production.
            w,h=int(self.root.winfo_screenwidth()),int(self.root.winfo_screenheight())
        except (OSError,RuntimeError,ValueError,TypeError):
            return HostResult("SCREEN_METRICS_UNAVAILABLE")
        region=verified_detached_region(w,h)
        if region is None:
            return HostResult("NO_USABLE_SCREEN_REGION")
        if not allowed():
            return HostResult("CANCELLED")

        widget=None
        try:
            if self._toplevel is None:
                import tkinter as tk
                widget=tk.Toplevel(self.root)
            else:
                widget=self._toplevel(self.root)
            widget.withdraw()
            widget.overrideredirect(True)  # local undecorated host choice
            widget.geometry(
                f"{region.width}x{region.height}+{region.x}+{region.y}")
            widget.wm_attributes("-topmost",True)
            widget.deiconify()
            widget.update_idletasks()
            # Owner thread only; synchronously realize actual Win32 HWND
            # before exposing the handle for any S68 DWM registration.
            widget.update()
            hwnd=self._resolve_hwnd(int(widget.winfo_id()))
            self._owner=widget
            self._owner_hwnd=hwnd
            self._region=region
            if not self._verified_owner() or not allowed():
                self.close()
                return HostResult("OWNER_NATIVE_PROOF_FAILED")
            # C13 recovered original detached control-bar action "Đóng xem".
            # It closes DWM destinations and THIS detached view, never the
            # discovered game source HWNDs. This single live button is not
            # a claim that the unrecovered full C14 bar pixel layout exists.
            # Unit fake owners deliberately have no real Tk interpreter.
            if hasattr(widget, "tk"):
                # Import the concrete ttk widget without confusing older
                # S70/S71 guards that forbid creating inert tk.Button UI.
                from tkinter.ttk import Button as DetachedCloseButton
                button = DetachedCloseButton(widget, text="Đóng xem",
                                             command=self.close)
                button.place(x=max(0,region.width-96), y=4,
                             width=88, height=24)
                self._close_view_button = button
            self._session=self._session_factory()
            return HostResult("HOST_OPEN",hwnd,region)
        except (OSError,RuntimeError,ValueError,TypeError,AttributeError):
            if self._owner is None and widget is not None:
                try:widget.destroy()
                except Exception:pass
            self.close()
            return HostResult("OWNER_CREATE_FAILED")

    def render(self, snapshot: WindowSnapshot, *, max_windows: int,
               placements: Sequence[PreviewPlacement],
               allowed: Callable[[],bool] = lambda: False) -> HostResult:
        if not self._on_owner_thread():
            return HostResult("WRONG_TK_THREAD")
        if self._closed:
            return HostResult("CLOSED")
        if self._owner is None or self._session is None or self._region is None:
            return HostResult("NOT_OPEN")
        if not allowed():
            self.close()
            return HostResult("CANCELLED")
        if not self._verified_owner():
            self.close()
            return HostResult("OWNER_INVALIDATED")
        try:
            sw,sh=int(self.root.winfo_screenwidth()),int(self.root.winfo_screenheight())
            if verified_detached_region(sw,sh)!=self._region:
                self.close()
                return HostResult("SCREEN_CHANGED")
            result=self._session.update(
                snapshot,owner_hwnd=self._owner_hwnd,owner_pid=os.getpid(),
                screen_width=sw,screen_height=sh,max_windows=max_windows,
                placements=placements,allowed=allowed)
            if result.code!="DETACHED_DWM_VISIBLE":
                self.close()
            return HostResult(result.code,self._owner_hwnd if self._owner else 0,
                              self._region,result.rendered)
        except (OSError,RuntimeError,ValueError,TypeError):
            self.close()
            return HostResult("DETACHED_RENDER_FAILED")

    def refresh(
        self, snapshot: WindowSnapshot, *, max_windows: int,
        placements_for_owner: Callable[
            [DetachedRegion, int, WindowSnapshot], Sequence[PreviewPlacement]
        ] | None = None,
        allowed: Callable[[], bool] = lambda: False,
    ) -> HostResult:
        """C14 `↺`: close the old DWM view, reopen and re-read sources.

        Original doc proves the close-then-reopen sequence, but original
        detached tile x/y/w/h arithmetic is NOT recovered (S75). Consequently
        EVERY refresh requires an independently measured placement factory.
        There is no default geometry and no prematurely wired UI action.
        All native DWM operations remain on this Tk owner thread.
        """
        if not self._on_owner_thread():
            return HostResult("WRONG_TK_THREAD")
        if self._closed:
            return HostResult("CLOSED")
        if self._refresh_cleanup_faulted:
            return HostResult("NATIVE_CLEANUP_FAILED_LOCKED")
        if self._owner is None:
            return HostResult("NOT_OPEN")
        if not callable(allowed) or allowed() is not True:
            self.close()
            return HostResult("CANCELLED")
        if type(max_windows) is not int or max_windows <= 0:
            self.close()
            return HostResult("NO_VERIFIED_WINDOW_LIMIT")
        if not callable(placements_for_owner):
            # Do not replace a real DWM preview with a guessed blank host.
            return HostResult("DETACHED_PLACEMENT_EVIDENCE_MISSING")
        gate = self._source_gate(snapshot, max_windows)
        if gate != "VALID":
            self.close()
            return HostResult(gate)
        ended = self.close()  # C13 first: DWM thumbnails before Tk owner
        if ended.code != "HOST_CLOSED":
            self._refresh_cleanup_faulted = True
            return HostResult("NATIVE_CLEANUP_FAILED_LOCKED")
        if allowed() is not True:
            return HostResult("CANCELLED")
        opened = self.open(snapshot, max_windows=max_windows, allowed=allowed)
        if opened.code != "HOST_OPEN":
            return opened
        try:
            placements = tuple(
                placements_for_owner(opened.region, opened.owner_hwnd, snapshot))
        except Exception:
            self.close()
            return HostResult("DETACHED_PLACEMENTS_UNAVAILABLE")
        rendered = self.render(
            snapshot, max_windows=max_windows, placements=placements,
            allowed=allowed)
        if rendered.code != "DETACHED_DWM_VISIBLE":
            # render() already closes the host on invalid DWM/layout.
            return rendered
        return HostResult("DETACHED_DWM_REFRESHED", rendered.owner_hwnd,
                          rendered.region, rendered.rendered)

    def close(self) -> HostResult:
        if not self._on_owner_thread():
            return HostResult("WRONG_TK_THREAD")
        # S71: release ALL native DWM slots first, even if a single native
        # unregister/destroy failed; never strand the owner on an exception.
        # Failures are EXPLICIT and do not certify a perfect native release.
        cleanup_failed = False
        session = self._session
        self._session = None
        if session is not None:
            try:
                session.shutdown()
            except Exception:
                cleanup_failed = True
        owner = self._owner
        self._close_view_button = None
        self._owner = None
        self._owner_hwnd = 0
        self._region = None
        if owner is not None:
            try:
                owner.destroy()
            except Exception:
                cleanup_failed = True
        return HostResult("HOST_CLOSED_NATIVE_CLEANUP_FAILED" if cleanup_failed
                          else "HOST_CLOSED")

    def shutdown(self) -> HostResult:
        if not self._on_owner_thread():
            return HostResult("WRONG_TK_THREAD")
        outcome = self.close()
        self._closed = True
        return HostResult("CLOSED_NATIVE_CLEANUP_FAILED"
                          if outcome.code != "HOST_CLOSED" else "CLOSED")
