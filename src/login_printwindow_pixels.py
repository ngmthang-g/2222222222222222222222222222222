"""S145 F06 original PrintWindow and single-frame login multipixel read-only.

Original F06 proves PrintWindow and checks both login.login1/login.login2
from ONE complete capture before F06 credentials. The real game's RGB,
coordinates, color tolerance and render flags were NOT recovered.
No default/login-color template is invented. Only explicit caller-supplied
reference points can be compared; exact RGB equality is a LOCAL test policy.

No clicks, typing, launching, DLL, credential handling, Proxy, or Info grant.
Not wired to product Login while original signed Info/F05 remain unknown.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable, Mapping, Protocol, Sequence

from start_polling import WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate

LOGIN_REFERENCES = ("login.login1", "login.login2")
MAX_CAPTURE_WIDTH = 2560    # local allocation safety cap, NOT original
MAX_CAPTURE_HEIGHT = 1600   # local allocation safety cap, NOT original
MAX_POINTS_PER_REFERENCE = 32  # local cap, NOT original


@dataclass(frozen=True)
class RgbSample:
    x: int
    y: int
    red: int
    green: int
    blue: int


@dataclass(frozen=True)
class CapturedBgra:
    width: int
    height: int
    bgra: bytes

    def rgb_at(self, x: int, y: int) -> tuple[int, int, int]:
        if (type(x) is not int or type(y) is not int or
                x < 0 or y < 0 or x >= self.width or y >= self.height):
            raise ValueError("PIXEL_OUTSIDE_CAPTURE")
        i = (y*self.width+x)*4
        b,g,r = self.bgra[i:i+3]
        return r,g,b


@dataclass(frozen=True)
class LoginPixelResult:
    code: str
    matched: tuple[str,...] = ()
    observed_one_full_frame: bool = False


class FrameProvider(Protocol):
    def capture(self, hwnd:int)->CapturedBgra: ...


def _valid_reference(reference:object)->bool:
    if not isinstance(reference, (tuple,list)) or (
            not 1 <= len(reference) <= MAX_POINTS_PER_REFERENCE):
        return False
    return all(isinstance(p,RgbSample) and
        type(p.x) is int and type(p.y) is int and p.x >= 0 and p.y >= 0
        and all(type(v) is int and 0 <= v <= 255
                for v in (p.red,p.green,p.blue))
        for p in reference)


def compare_reference(frame:CapturedBgra,
                      samples:Sequence[RgbSample])->bool:
    if not isinstance(frame,CapturedBgra) or not _valid_reference(samples):
        return False
    if (type(frame.width) is not int or type(frame.height) is not int
            or not 1 <= frame.width <= MAX_CAPTURE_WIDTH
            or not 1 <= frame.height <= MAX_CAPTURE_HEIGHT
            or len(frame.bgra) != frame.width*frame.height*4):
        return False
    if any(p.x >= frame.width or p.y >= frame.height for p in samples):
        return False
    return all(frame.rgb_at(p.x,p.y)==(p.red,p.green,p.blue)
               for p in samples)


class NativePrintWindowFrame:
    """Actual background PrintWindow to a compatible DIB readback.

    Uses the full WINDOW rectangle as original PrintWindow evidence describes,
    not the physical desktop capture or foreground mouse. Non-ready native
    windows and Win32 failures produce no screenshot data or match result.
    PrintWindow may still hang if its target cannot paint synchronously;
    this primitive must not run on Tk main thread in real product.
    """

    def __init__(self, *, printwindow_flags: int = 0):
        if os.name!="nt":
            raise OSError("S145_WINDOWS_REQUIRED")
        # S203: original compiled pixel.py's batch captures request
        # PrintWindow flag=2. Preserve S145's original default flag=0.
        if type(printwindow_flags) is not int or printwindow_flags not in (0, 2):
            raise ValueError("PRINTWINDOW_UNSUPPORTED_FLAGS")
        self._printwindow_flags = printwindow_flags
        import ctypes
        from ctypes import wintypes as w
        self._ctypes=ctypes
        self._w=w
        self._u=ctypes.WinDLL("user32",use_last_error=True)
        self._g=ctypes.WinDLL("gdi32",use_last_error=True)
        self._u.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
        self._u.GetWindowRect.restype=w.BOOL
        self._u.GetWindowDC.argtypes=[w.HWND]
        self._u.GetWindowDC.restype=w.HDC
        self._u.ReleaseDC.argtypes=[w.HWND,w.HDC]
        self._u.ReleaseDC.restype=ctypes.c_int
        self._u.PrintWindow.argtypes=[w.HWND,w.HDC,w.UINT]
        self._u.PrintWindow.restype=w.BOOL
        self._g.CreateCompatibleDC.argtypes=[w.HDC]
        self._g.CreateCompatibleDC.restype=w.HDC
        self._g.CreateCompatibleBitmap.argtypes=[w.HDC,ctypes.c_int,ctypes.c_int]
        self._g.CreateCompatibleBitmap.restype=w.HBITMAP
        self._g.SelectObject.argtypes=[w.HDC,w.HGDIOBJ]
        self._g.SelectObject.restype=w.HGDIOBJ
        self._g.GetDIBits.argtypes=[w.HDC,w.HBITMAP,w.UINT,w.UINT,
                                  ctypes.c_void_p,ctypes.c_void_p,w.UINT]
        self._g.GetDIBits.restype=ctypes.c_int
        self._g.DeleteObject.argtypes=[w.HGDIOBJ]
        self._g.DeleteObject.restype=w.BOOL
        self._g.DeleteDC.argtypes=[w.HDC]
        self._g.DeleteDC.restype=w.BOOL

    def capture(self,hwnd:int)->CapturedBgra:
        if type(hwnd) is not int or hwnd<=0:
            raise ValueError("INVALID_CAPTURE_HWND")
        ct=self._ctypes
        w=self._w
        rect=w.RECT()
        if not self._u.GetWindowRect(hwnd,ct.byref(rect)):
            raise OSError("PRINTWINDOW_RECT_UNAVAILABLE")
        width,height=rect.right-rect.left,rect.bottom-rect.top
        if not (1<=width<=MAX_CAPTURE_WIDTH and
                1<=height<=MAX_CAPTURE_HEIGHT):
            raise ValueError("INVALID_CAPTURE_DIMENSIONS")
        window_dc=self._u.GetWindowDC(hwnd)
        if not window_dc:
            raise OSError("PRINTWINDOW_GET_DC_FAILED")
        memory_dc=0
        bitmap=0
        prior=0
        try:
            memory_dc=self._g.CreateCompatibleDC(window_dc)
            if not memory_dc:
                raise OSError("PRINTWINDOW_MEMORY_DC_FAILED")
            bitmap=self._g.CreateCompatibleBitmap(window_dc,width,height)
            if not bitmap:
                raise OSError("PRINTWINDOW_BITMAP_FAILED")
            prior=self._g.SelectObject(memory_dc,bitmap)
            if not prior:
                raise OSError("PRINTWINDOW_SELECT_FAILED")
            if not self._u.PrintWindow(hwnd,memory_dc,self._printwindow_flags):
                raise OSError("PRINTWINDOW_FAILED")
            # BITMAPINFOHEADER + RGBQUAD zero; negative height = top-down.
            # Explicit layout uses DWORD (4), LONG (4), WORD (2), WORD (2).
            class Info(ct.Structure):
                _fields_=[
                    ("biSize",ct.c_uint32),("biWidth",ct.c_int32),
                    ("biHeight",ct.c_int32),("biPlanes",ct.c_uint16),
                    ("biBitCount",ct.c_uint16),("biCompression",ct.c_uint32),
                    ("biSizeImage",ct.c_uint32),("biXPelsPerMeter",ct.c_int32),
                    ("biYPelsPerMeter",ct.c_int32),("biClrUsed",ct.c_uint32),
                    ("biClrImportant",ct.c_uint32)]
            info=Info()
            info.biSize=ct.sizeof(Info)
            info.biWidth=width
            info.biHeight=-height
            info.biPlanes=1
            info.biBitCount=32
            info.biCompression=0
            pixels=(ct.c_ubyte*(width*height*4))()
            count=self._g.GetDIBits(memory_dc,bitmap,0,height,
                                    ct.cast(pixels,ct.c_void_p),
                                    ct.byref(info),0)
            if count!=height:
                raise OSError("PRINTWINDOW_DIB_READ_FAILED")
            return CapturedBgra(width,height,bytes(pixels))
        finally:
            if prior and memory_dc:
                self._g.SelectObject(memory_dc,prior)
            if bitmap:
                self._g.DeleteObject(bitmap)
            if memory_dc:
                self._g.DeleteDC(memory_dc)
            self._u.ReleaseDC(hwnd,window_dc)


def observe_login_screen(
    window:GameWindow, *,
    snapshot:WindowSnapshot,
    max_windows:int,
    allowed:Callable[[],bool],
    references:Mapping[str,Sequence[RgbSample]]|None,
    backend=None,
    provider:FrameProvider|None=None,
)->LoginPixelResult:
    """Only explicit F06 original reference specs, never synthetic defaults.

    One native full-window PrintWindow frame for BOTH login1+login2.
    If original reference points aren't known, return NO_REFERENCE_DATA
    WITHOUT capturing or reporting ready. Real game authorization is
    independent, never inferred from a screenshot alone.
    """
    if (not isinstance(references,Mapping) or
        set(references)!=set(LOGIN_REFERENCES) or
        not all(_valid_reference(references[k]) for k in LOGIN_REFERENCES)):
        return LoginPixelResult("NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE")
    if (not isinstance(window,GameWindow)
        or not isinstance(snapshot,WindowSnapshot) or not snapshot.valid
        or type(max_windows) is not int or max_windows<=0
        or not 1<=len(snapshot.windows)<=max_windows
        or window not in snapshot.windows
        or not is_game_candidate(window.process_name,window.class_name,window.title)
        or not callable(allowed)):
        return LoginPixelResult("UNVERIFIED_TARGET")
    native=backend if backend is not None else NativeWin32Backend()

    def current()->bool:
        try:
            return (allowed() is True and
                tuple(native.enumerate_top_level()).count(window.hwnd)==1
                and native.is_window(window.hwnd)
                and native.is_visible(window.hwnd)
                and native.process_id(window.hwnd)==window.pid
                and is_game_candidate(
                    native.process_executable(window.pid),
                    native.window_class(window.hwnd),
                    native.title_with_timeout(window.hwnd,150))
                and native.is_window(window.hwnd)
                and native.process_id(window.hwnd)==window.pid)
        except Exception:
            return False

    if not current():
        return LoginPixelResult("STALE_OR_UNAUTHORIZED_TARGET")
    frame_provider=provider if provider is not None else NativePrintWindowFrame()
    try:
        frame=frame_provider.capture(window.hwnd)
    except (OSError,ValueError,TypeError,OverflowError):
        return LoginPixelResult("PRINTWINDOW_CAPTURE_FAILED")
    if not current():
        return LoginPixelResult("STALE_OR_UNAUTHORIZED_AFTER_CAPTURE")
    if not isinstance(frame,CapturedBgra):
        return LoginPixelResult("INVALID_CAPTURE")
    if (not 1<=frame.width<=MAX_CAPTURE_WIDTH
        or not 1<=frame.height<=MAX_CAPTURE_HEIGHT
        or len(frame.bgra)!=frame.width*frame.height*4):
        return LoginPixelResult("INVALID_CAPTURE")
    # Exact RGB is a conservative S145 local comparator, not proven to be
    # original pixel tolerance. No actual login coordinates are embedded.
    found=tuple(k for k in LOGIN_REFERENCES
                if compare_reference(frame,references[k]))
    return LoginPixelResult(
        "BOTH_EXPLICIT_REFERENCES_MATCH_TEST_ONLY" if len(found)==2
        else "LOGIN_REFERENCE_MISMATCH",
        found,True)
