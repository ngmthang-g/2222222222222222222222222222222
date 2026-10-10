"""S11/S78: original-backed live DWM thumbnails and verified source activation.

C03 proves DWM registration/overlay lifecycle; exact Tk pixel parity and
fVisible/fSourceClientAreaOnly Boolean expressions were NOT recovered.
This bounded adaptation uses an opaque top-level tool-window destination,
never registers with a Tk child and validates source HWND+PID before
each create/update. S78 adds C03's authentic overlay left-click -> source
restore/show/foreground action, only while a verified DWM slot is owned.

All native window operations run on the Tk OWNER thread (not S09 worker).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence

# Original C03 _dwm_dst_click_targets: mapping lives only as long as native
# destination popup HWNDs. Each entry preserves the validated source PID.
_DWM_CLICK_TARGETS: dict[int, tuple[object, int, int]] = {}
_DWM_LEFT_MESSAGES = (0x0201, 0x0202, 0x0203)  # C03 exact 513/514/515


def _dispatch_dwm_click(destination: int, message: int) -> bool:
    """C03 target mapping: dispatch only original left-button HWND messages.

    Returns True if destination was bound and the message consumed, even if
    stale or OS foreground policy refuses activation. Revalidates HWND/PID
    at the LAST Win32 boundary; never reads game memory or generates input.
    """
    if message not in _DWM_LEFT_MESSAGES:
        return False
    target = _DWM_CLICK_TARGETS.get(destination)
    if target is None:
        return False
    backend, source, pid = target
    try:
        if backend.source_matches(source, pid):
            backend.activate_source(source)
    except Exception:
        # Never unwind into native unmanaged Win32 WndProc.
        pass
    return True


THUMB_WIDTH = 197
THUMB_HEIGHT = 110
ITEM_WIDTH = 205
ITEM_HEIGHT = 137


@dataclass(frozen=True)
class PreviewPlacement:
    hwnd: int
    pid: int
    owner_hwnd: int
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class PreviewResult:
    rendered: tuple[int, ...] = ()
    errors: tuple[tuple[int, str], ...] = ()


class DwmBackend(Protocol):
    def source_matches(self, hwnd: int, pid: int) -> bool: ...
    def activate_source(self, hwnd: int) -> bool: ...
    def bind_click_target(self, destination: int, hwnd: int, pid: int) -> None: ...
    def create_destination(self, owner: int, x: int, y: int, width: int, height: int) -> int: ...
    def register(self, destination: int, source: int) -> int: ...
    def reposition(self, destination: int, thumbnail: int, x: int, y: int,
                   width: int, height: int) -> None: ...
    def unregister(self, thumbnail: int) -> None: ...
    def destroy_destination(self, destination: int) -> None: ...


@dataclass
class _PreviewSlot:
    pid: int
    owner_hwnd: int
    destination: int
    thumbnail: int


class ReadOnlyDwmPreviews:
    """Stateful HWND+PID guard and deterministic cleanup around DWM.

    Creation is all-or-nothing. HWND numeric reuse always tears down the prior
    DWM thumbnail BEFORE considering a new PID. Failed scans and empty input
    drop everything rather than leaving a stale game image visible.
    """

    def __init__(self, backend: DwmBackend):
        self.backend = backend
        self._slots: dict[int, _PreviewSlot] = {}
        self._closed = False

    @property
    def active_hwnds(self) -> tuple[int, ...]:
        return tuple(self._slots)

    def _remove(self, hwnd: int) -> None:
        slot = self._slots.pop(hwnd, None)
        if slot is None:
            return
        try:
            self.backend.unregister(slot.thumbnail)
        finally:
            self.backend.destroy_destination(slot.destination)

    def clear(self) -> None:
        # S71: one native DWM unregister/destroy failure must NOT prevent
        # the remaining slots being released. Propagate the FIRST failure
        # after every slot was attempted; never report full cleanup success.
        first_failure = None
        for hwnd in tuple(self._slots):
            try:
                self._remove(hwnd)
            except Exception as exc:
                if first_failure is None:
                    first_failure = exc
        if first_failure is not None:
            raise first_failure

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.clear()

    def sync(self, placements: Sequence[PreviewPlacement]) -> PreviewResult:
        if self._closed:
            return PreviewResult(errors=tuple((x.hwnd, "CLOSED") for x in placements))
        requested: dict[int, PreviewPlacement] = {}
        for item in placements:
            if item.hwnd in requested:
                raise ValueError("Repeated HWND in DWM preview input")
            requested[item.hwnd] = item

        # Teardown precedes any construction, even when an HWND was reused.
        for hwnd, slot in tuple(self._slots.items()):
            item = requested.get(hwnd)
            if (item is None or item.pid != slot.pid
                    or item.owner_hwnd != slot.owner_hwnd):
                self._remove(hwnd)

        rendered = []
        errors = []
        for hwnd, item in requested.items():
            if (min(item.hwnd, item.pid, item.owner_hwnd,
                    item.width, item.height) <= 0):
                self._remove(hwnd)
                errors.append((hwnd, "INVALID_RECT_OR_ID"))
                continue
            try:
                if not self.backend.source_matches(item.hwnd, item.pid):
                    self._remove(hwnd)
                    errors.append((hwnd, "STALE_CLOSED_OR_HUNG_SOURCE"))
                    continue

                slot = self._slots.get(hwnd)
                if slot is None:
                    destination = 0
                    thumbnail = 0
                    try:
                        destination = self.backend.create_destination(
                            item.owner_hwnd, item.x, item.y,
                            item.width, item.height)
                        if not destination:
                            raise OSError("DWM_DESTINATION_NOT_CREATED")
                        # Revalidate after Win32 window creation: HWND could be reused.
                        if not self.backend.source_matches(item.hwnd, item.pid):
                            raise OSError("HWND_PID_CHANGED_BEFORE_REGISTER")
                        thumbnail = self.backend.register(destination, hwnd)
                        if not thumbnail:
                            raise OSError("DWM_REGISTER_RETURNED_NULL")
                        # C03 destination click handler is bound ONLY after
                        # a real DWM source+PID registration is verified.
                        bind = getattr(self.backend, "bind_click_target", None)
                        if callable(bind):
                            bind(destination, hwnd, item.pid)
                        slot = _PreviewSlot(item.pid, item.owner_hwnd, destination, thumbnail)
                        self._slots[hwnd] = slot
                    except Exception:
                        if thumbnail:
                            self.backend.unregister(thumbnail)
                        if destination:
                            self.backend.destroy_destination(destination)
                        raise
                # Revalidate directly before property change as well.
                if not self.backend.source_matches(hwnd, item.pid):
                    self._remove(hwnd)
                    errors.append((hwnd, "HWND_PID_CHANGED_BEFORE_UPDATE"))
                    continue
                self.backend.reposition(
                    slot.destination, slot.thumbnail,
                    item.x, item.y, item.width, item.height)
                rendered.append(hwnd)
            except Exception as exc:
                self._remove(hwnd)
                errors.append((hwnd, f"{type(exc).__name__}:{exc}"))
        return PreviewResult(tuple(rendered), tuple(errors))


class NativeDwmBackend:
    """Real Windows user32+dwmapi and C03 click-to-activate WndProc.

    C03 recovers WM_LBUTTONDOWN/UP/DBLCLK, mapping destination HWND to a
    source HWND, IsIconic/ShowWindow SW_RESTORE/SW_SHOW, SetForegroundWindow.
    The exact original click event return values and restore branch remain
    unknown. This bounded S78 implementation checks live HWND+PID and hung
    state again before a native foreground attempt, and does NOT synthesize
    any game mouse/keyboard events or grant account permissions.
    """

    CLASS_NAME = "ThlDwmThumbDst"
    WS_POPUP = 0x80000000
    WS_VISIBLE = 0x10000000
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TRANSPARENT = 0x00000020
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    DWM_TNP_RECTDESTINATION = 0x00000001
    DWM_TNP_OPACITY = 0x00000004
    DWM_TNP_VISIBLE = 0x00000008
    DWM_TNP_SOURCECLIENTAREAONLY = 0x00000010
    _class_atom: int | None = None
    _wndproc_keepalive = None

    def __init__(self):
        if os.name != "nt":
            raise OSError("Native DWM previews require Windows")
        import ctypes
        from ctypes import wintypes as w
        self.ctypes = ctypes
        self.w = w
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.dwm = ctypes.WinDLL("dwmapi", use_last_error=True)

        class Rect(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

        class Properties(ctypes.Structure):
            _fields_ = [("dwFlags", w.DWORD),
                        ("rcDestination", Rect), ("rcSource", Rect),
                        ("opacity", ctypes.c_ubyte), ("fVisible", w.BOOL),
                        ("fSourceClientAreaOnly", w.BOOL)]

        self.Rect = Rect
        self.Properties = Properties
        self._is_window = self.user32.IsWindow
        self._is_window.argtypes = [w.HWND]
        self._is_window.restype = w.BOOL
        self._hung = self.user32.IsHungAppWindow
        self._hung.argtypes = [w.HWND]
        self._hung.restype = w.BOOL
        self._get_pid = self.user32.GetWindowThreadProcessId
        self._get_pid.argtypes = [w.HWND, ctypes.POINTER(w.DWORD)]
        self._get_pid.restype = w.DWORD

        self._ancestor = self.user32.GetAncestor
        self._ancestor.argtypes = [w.HWND, w.UINT]
        self._ancestor.restype = w.HWND

        self._create = self.user32.CreateWindowExW
        self._create.argtypes = [w.DWORD, w.LPCWSTR, w.LPCWSTR, w.DWORD,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 w.HWND, w.HMENU, w.HINSTANCE, ctypes.c_void_p]
        self._create.restype = w.HWND
        self._destroy = self.user32.DestroyWindow
        self._destroy.argtypes = [w.HWND]
        self._destroy.restype = w.BOOL
        self._set_pos = self.user32.SetWindowPos
        self._set_pos.argtypes = [w.HWND, w.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, w.UINT]
        self._set_pos.restype = w.BOOL

        self._register = self.dwm.DwmRegisterThumbnail
        self._register.argtypes = [w.HWND, w.HWND, ctypes.POINTER(w.HANDLE)]
        self._register.restype = ctypes.c_long
        self._update = self.dwm.DwmUpdateThumbnailProperties
        self._update.argtypes = [w.HANDLE, ctypes.POINTER(Properties)]
        self._update.restype = ctypes.c_long
        self._unregister = self.dwm.DwmUnregisterThumbnail
        self._unregister.argtypes = [w.HANDLE]
        self._unregister.restype = ctypes.c_long
        self._show = self.user32.ShowWindow
        self._show.argtypes = [w.HWND, ctypes.c_int]
        self._show.restype = w.BOOL
        self._is_iconic = self.user32.IsIconic
        self._is_iconic.argtypes = [w.HWND]
        self._is_iconic.restype = w.BOOL
        self._foreground = self.user32.SetForegroundWindow
        self._foreground.argtypes = [w.HWND]
        self._foreground.restype = w.BOOL
        self._hinstance = self.kernel32.GetModuleHandleW
        self._hinstance.argtypes = [w.LPCWSTR]
        self._hinstance.restype = w.HMODULE
        self._ensure_class()

    def _ensure_class(self) -> None:
        cls = type(self)
        if cls._class_atom is not None:
            return
        ctypes, w = self.ctypes, self.w
        proc_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, w.HWND, w.UINT,
                                       w.WPARAM, w.LPARAM)
        default_proc = self.user32.DefWindowProcW
        default_proc.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
        default_proc.restype = ctypes.c_ssize_t

        @proc_type
        def wndproc(hwnd, msg, wp, lp):
            if _dispatch_dwm_click(int(hwnd), int(msg)):
                return 0
            return default_proc(hwnd, msg, wp, lp)

        class WindowClass(ctypes.Structure):
            _fields_ = [
                ("cbSize", w.UINT), ("style", w.UINT),
                ("lpfnWndProc", ctypes.c_void_p),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", w.HINSTANCE), ("hIcon", w.HICON),
                ("hCursor", w.HANDLE), ("hbrBackground", w.HBRUSH),
                ("lpszMenuName", w.LPCWSTR), ("lpszClassName", w.LPCWSTR),
                ("hIconSm", w.HICON),
            ]

        register = self.user32.RegisterClassExW
        register.argtypes = [ctypes.POINTER(WindowClass)]
        register.restype = ctypes.c_ushort
        wc = WindowClass()
        wc.cbSize = ctypes.sizeof(WindowClass)
        wc.lpfnWndProc = ctypes.cast(wndproc, ctypes.c_void_p).value
        wc.hInstance = self._hinstance(None)
        wc.lpszClassName = self.CLASS_NAME
        atom = int(register(ctypes.byref(wc)))
        if not atom:
            error = ctypes.get_last_error()
            if error != 1410:  # ERROR_CLASS_ALREADY_EXISTS
                raise OSError(error, "RegisterClassExW failed")
            atom = 1
        # Keep callback alive while any overlay uses the registered class.
        cls._wndproc_keepalive = wndproc
        cls._class_atom = atom

    def source_matches(self, hwnd: int, pid: int) -> bool:
        if not self._is_window(hwnd) or self._hung(hwnd):
            return False
        current = self.w.DWORD(0)
        self._get_pid(hwnd, self.ctypes.byref(current))
        return int(current.value) == pid and pid > 0

    def activate_source(self, hwnd: int) -> bool:
        """C03 real native restore/show and foreground attempt (no game input).

        Win32 foreground restrictions may reject SetForegroundWindow even
        when the source HWND/PID is current. Never misreport an attempt as
        proof of focus in another process.
        """
        if not self._is_window(hwnd) or self._hung(hwnd):
            return False
        self._show(hwnd, 9 if self._is_iconic(hwnd) else 5)  # SW_RESTORE / SW_SHOW
        return bool(self._foreground(hwnd))

    def bind_click_target(self, destination: int, hwnd: int, pid: int) -> None:
        if (not self._is_window(destination)
                or not self.source_matches(hwnd, pid)):
            raise OSError("C03_CLICK_SOURCE_NOT_CURRENT")
        _DWM_CLICK_TARGETS[destination] = (self, hwnd, pid)

    def create_destination(self, owner: int, x: int, y: int, width: int, height: int) -> int:
        # Tk winfo_id can refer to its drawing child, not the native top-level.
        # DWM requires a real top-level owner. GA_ROOT=2 preserves ownership.
        owner_root = self._ancestor(owner, 2)
        if not owner_root or not self._is_window(owner_root):
            raise OSError("Owner HWND missing")
        # C03's real destination WndProc handles left clicks. S11's
        # local WS_EX_TRANSPARENT click-through choice would bypass that
        # destination hit-test path; the original class marker does not
        # recover WS_EX_TRANSPARENT as a required style.
        ext = (self.WS_EX_LAYERED | self.WS_EX_TOOLWINDOW
               | self.WS_EX_NOACTIVATE)
        h = self._create(ext, self.CLASS_NAME, "", self.WS_POPUP | self.WS_VISIBLE,
                         x, y, width, height, owner_root, None, self._hinstance(None), None)
        if not h:
            raise OSError(self.ctypes.get_last_error(), "CreateWindowExW failed")
        return int(h)

    def register(self, destination: int, source: int) -> int:
        thumb = self.w.HANDLE()
        hr = self._register(destination, source, self.ctypes.byref(thumb))
        if hr != 0 or not thumb.value:
            raise OSError(f"DwmRegisterThumbnail HRESULT=0x{hr & 0xffffffff:08X}")
        return int(thumb.value)

    def reposition(self, destination: int, thumbnail: int, x: int, y: int,
                   width: int, height: int) -> None:
        if not self._set_pos(destination, 0, x, y, width, height,
                             self.SWP_NOACTIVATE | self.SWP_SHOWWINDOW):
            raise OSError(self.ctypes.get_last_error(), "SetWindowPos failed")
        props = self.Properties()
        props.dwFlags = (self.DWM_TNP_RECTDESTINATION | self.DWM_TNP_OPACITY
                         | self.DWM_TNP_VISIBLE | self.DWM_TNP_SOURCECLIENTAREAONLY)
        props.rcDestination = self.Rect(0, 0, max(1, width), max(1, height))
        props.opacity = 255
        props.fVisible = True
        props.fSourceClientAreaOnly = True
        hr = self._update(thumbnail, self.ctypes.byref(props))
        if hr != 0:
            raise OSError(f"DwmUpdateThumbnailProperties HRESULT=0x{hr & 0xffffffff:08X}")

    def unregister(self, thumbnail: int) -> None:
        if thumbnail:
            self._unregister(thumbnail)

    def destroy_destination(self, destination: int) -> None:
        if destination:
            # Original C03 _destroy_dwm_dst_hwnd removes click mapping
            # before destroying the popup HWND. No stale click targets.
            _DWM_CLICK_TARGETS.pop(destination, None)
            self._destroy(destination)
