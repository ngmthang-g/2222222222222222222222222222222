"""S11: original-backed, read-only DWM thumbnail service for Start.

C03 proves DWM registration/overlay lifecycle; exact Tk pixel parity and
fVisible/fSourceClientAreaOnly Boolean expressions were NOT recovered.
This bounded adaptation uses an opaque top-level tool-window destination,
never registers with a Tk child, never sends mouse/keyboard/game commands,
and validates source HWND+PID before each create/update.

All native window operations run on the Tk OWNER thread (not S09 worker).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence

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
        for hwnd in tuple(self._slots):
            self._remove(hwnd)

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
    """Real Windows user32+dwmapi ctypes calls, with NO input handlers.

    Destination uses the original 'ThlDwmThumbDst' class name but its WndProc
    deliberately has *no* original click-to-activate actions in S11.
    Original opacity=255 is proven; visible/client-only True are S11 choices.
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
            # No game activation/mouse interception in S11.
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

    def create_destination(self, owner: int, x: int, y: int, width: int, height: int) -> int:
        # Tk winfo_id can refer to its drawing child, not the native top-level.
        # DWM requires a real top-level owner. GA_ROOT=2 preserves ownership.
        owner_root = self._ancestor(owner, 2)
        if not owner_root or not self._is_window(owner_root):
            raise OSError("Owner HWND missing")
        ext = (self.WS_EX_LAYERED | self.WS_EX_TOOLWINDOW
               | self.WS_EX_NOACTIVATE | self.WS_EX_TRANSPARENT)
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
            self._destroy(destination)
