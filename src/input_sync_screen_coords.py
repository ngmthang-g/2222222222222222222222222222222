"""S143: C19 original-supported Win32 master SCREEN -> CLIENT point.

Original C19 names WindowFromPoint, GetAncestor, ScreenToClient, GetClientRect
before size-aware scaling. This implements only that real OS geometry stage.
The original slave DLL, native input sender, key packing and listeners remain
UNKNOWN and DISABLED. No game action or permission grant is created.
"""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Callable
from input_sync_core import InputSyncModel, ClientSize, NativeClientRectReader
from start_windows import NativeWin32Backend


@dataclass(frozen=True)
class VerifiedMasterClientPoint:
    hwnd: int
    pid: int
    x: int
    y: int
    width: int
    height: int


class NativeC19MasterPointReader:
    """Actual Windows point identity and geometry, NO INPUT SENDER.

    WindowFromPoint may return a child; GetAncestor(GA_ROOT=2) must
    exactly equal the selected verified top-level master HWND.
    """
    def __init__(self, *, identity_backend=None, size_reader=None):
        if os.name != "nt":
            raise OSError("S143_C19_WINDOWS_ONLY")
        import ctypes
        from ctypes import wintypes
        self._ctypes=ctypes
        self._w=wintypes
        self._identity=(identity_backend if identity_backend is not None
                        else NativeWin32Backend())
        self._sizes=(size_reader if size_reader is not None
                     else NativeClientRectReader())
        u=ctypes.WinDLL("user32",use_last_error=True)
        self._window_from_point=u.WindowFromPoint
        self._window_from_point.argtypes=[wintypes.POINT]
        self._window_from_point.restype=wintypes.HWND
        self._ancestor=u.GetAncestor
        self._ancestor.argtypes=[wintypes.HWND,wintypes.UINT]
        self._ancestor.restype=wintypes.HWND
        self._screen_to_client=u.ScreenToClient
        self._screen_to_client.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.POINT)]
        self._screen_to_client.restype=wintypes.BOOL

    def _alive(self,hwnd:int,pid:int)->bool:
        try:
            return (self._identity.is_window(hwnd) and
                    self._identity.process_id(hwnd)==pid)
        except Exception:
            return False

    def capture(self,hwnd:int,pid:int,screen_x:int,screen_y:int)->VerifiedMasterClientPoint:
        if (type(hwnd) is not int or hwnd<=0 or
            type(pid) is not int or pid<=0 or
            type(screen_x) is not int or type(screen_y) is not int or
            not -(2**31)<=screen_x<2**31 or
            not -(2**31)<=screen_y<2**31):
            raise ValueError("INVALID_MASTER_SCREEN_POINT")
        if not self._alive(hwnd,pid):
            raise ValueError("STALE_MASTER_HWND_PID")
        point=self._w.POINT(screen_x,screen_y)
        underlying=int(self._window_from_point(point) or 0)
        if not underlying or int(self._ancestor(underlying,2) or 0)!=hwnd:
            raise ValueError("SCREEN_POINT_NOT_ON_MASTER")
        if not self._screen_to_client(hwnd,self._ctypes.byref(point)):
            raise ValueError("SCREEN_TO_CLIENT_FAILED")
        size=self._sizes.size(hwnd,pid)
        if not isinstance(size,ClientSize):
            raise ValueError("UNVERIFIED_CLIENT_SIZE")
        if not (0<=point.x<size.width and 0<=point.y<size.height):
            raise ValueError("SCREEN_POINT_OUTSIDE_MASTER_CLIENT")
        if not self._alive(hwnd,pid):
            raise ValueError("MASTER_RECYCLED_DURING_CAPTURE")
        return VerifiedMasterClientPoint(
            hwnd,pid,point.x,point.y,size.width,size.height)


def queue_verified_screen_mouse(
    model:InputSyncModel,screen_x:int,screen_y:int,*,
    button:str,pressed:bool,now:float,
    allowed:Callable[[],bool],
    live_identity:Callable[[int,int],bool],
    point_reader:NativeC19MasterPointReader|None=None,
    size_reader:NativeClientRectReader|None=None,
)->int:
    """C19 real master screen location -> original S19 size-scaled FIFO.

    Caller must supply live separately authenticated permission and HWND/PID
    checks. Does NOT send, block, unlock or inject native mouse events.
    Returns 0 without queuing anything on invalid/revoked/incomplete data.
    """
    if (not isinstance(model,InputSyncModel) or
        not callable(allowed) or not callable(live_identity)):
        return 0
    if not model.active or model.master is None or not model.slaves:
        return 0
    identities=(model.master,)+model.slaves
    try:
        if allowed() is not True or not all(
            live_identity(hwnd,pid) is True for hwnd,pid in identities
        ):
            return 0
        capture_reader=(point_reader if point_reader is not None
                        else NativeC19MasterPointReader())
        sizes_reader=(size_reader if size_reader is not None
                      else NativeClientRectReader())
        point=capture_reader.capture(*model.master,screen_x,screen_y)
        if (point.hwnd,point.pid)!=model.master:
            return 0
        sizes={model.master:ClientSize(point.width,point.height)}
        for hwnd,pid in model.slaves:
            sizes[(hwnd,pid)]=sizes_reader.size(hwnd,pid)
        if allowed() is not True or not all(
            live_identity(hwnd,pid) is True for hwnd,pid in identities
        ):
            return 0
        return model.queue_mouse(
            point.x,point.y,button=button,pressed=pressed,
            sizes=sizes,now=now)
    except (OSError,ValueError,TypeError,OverflowError,AttributeError,KeyError):
        return 0
